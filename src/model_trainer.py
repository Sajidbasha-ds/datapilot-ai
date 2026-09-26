"""End-to-End Machine Learning Training Pipeline for DataPilot AI."""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    KFold,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline

from src.evaluator import (
    evaluate_classification_model,
    evaluate_clustering_model,
    evaluate_regression_model,
)
from src.feature_engineering import (
    build_preprocessing_pipeline,
    engineer_datetime_features,
    filter_suspicious_features,
    get_feature_names,
)
from src.model_selector import get_candidate_models


def _extract_feature_attributions(
    pipeline: Pipeline,
    model_name: str,
    limit: int = 15,
) -> List[Dict[str, Any]]:
    """Return model-appropriate attribution using fitted transformed names."""
    fitted_model = pipeline.named_steps.get("model")
    preprocessor = pipeline.named_steps.get("preprocessor")
    if fitted_model is None or preprocessor is None:
        return []

    try:
        feature_names = list(preprocessor.get_feature_names_out())
    except (AttributeError, ValueError, TypeError):
        return []

    records: List[Dict[str, Any]] = []

    if hasattr(fitted_model, "feature_importances_"):
        values = np.asarray(fitted_model.feature_importances_).reshape(-1)
        if len(values) != len(feature_names):
            return []
        records = [
            {
                "feature": feature,
                "value": float(value),
                "method": "tree_feature_importance",
                "model_type": model_name,
            }
            for feature, value in zip(feature_names, values)
        ]
    elif hasattr(fitted_model, "coef_"):
        coefficients = np.asarray(fitted_model.coef_)
        if coefficients.ndim == 1:
            coefficients = coefficients.reshape(1, -1)
        if coefficients.ndim != 2 or coefficients.shape[1] != len(feature_names):
            return []

        classes = list(getattr(fitted_model, "classes_", []))
        is_logistic = isinstance(fitted_model, LogisticRegression)
        for index, feature in enumerate(feature_names):
            feature_coefficients = coefficients[:, index]
            strength = float(np.max(np.abs(feature_coefficients)))
            record: Dict[str, Any] = {
                "feature": feature,
                "value": strength,
                "method": "coefficient",
                "model_type": model_name,
                "coefficient_strength": strength,
            }

            if is_logistic and coefficients.shape[0] == 1:
                coefficient = float(feature_coefficients[0])
                record["coefficient"] = coefficient
                record["direction"] = (
                    "positive" if coefficient > 0 else
                    "negative" if coefficient < 0 else
                    "zero"
                )
                if len(classes) == 2:
                    record["decision_class"] = str(classes[1])
            elif is_logistic:
                record["class_coefficients"] = [
                    {
                        "class": str(classes[row]) if row < len(classes) else str(row),
                        "coefficient": float(coefficients[row, index]),
                    }
                    for row in range(coefficients.shape[0])
                ]

            records.append(record)

    records.sort(key=lambda item: item["value"], reverse=True)
    return records[:limit]


def train_supervised_models(
    df: pd.DataFrame,
    target_col: str,
    problem_type: str,
    test_size: float = 0.20,
    random_state: int = 42,
    cv_folds: int = 3,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Dict[str, Any]:
    """Execute split-first feature screening, preprocessing, model training,
    cross-validation, evaluation, and model selection.
    """

    # 1. Remove rows with missing target values
    working_df = df.dropna(subset=[target_col]).copy()

    if len(working_df) < 15:
        raise ValueError(
            f"Dataset has only {len(working_df)} valid rows. "
            "At least 15 rows required for training."
        )

    # 2. Engineer datetime features
    if progress_callback:
        progress_callback(0.10, "Engineering datetime features...")

    working_df, dt_logs = engineer_datetime_features(working_df)

    # 3. Separate features and target
    y_raw = working_df[target_col]
    X_raw = working_df.drop(columns=[target_col])

    # 4. Train/Test Split BEFORE target-dependent feature filtering
    is_classification = "Classification" in problem_type

    stratify = (
        y_raw
        if (
            is_classification
            and y_raw.value_counts().min() >= 2
        )
        else None
    )

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw,
        y_raw,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )

    # 5. Filter features using training data only
    if progress_callback:
        progress_callback(
            0.15,
            "Screening training features for constants, ID-like columns, and applicable numeric target correlation...",
        )

    X_train, filter_logs = filter_suspicious_features(
        X_train_raw,
        y=y_train if "Regression" in problem_type else None,
    )

    # Apply exactly the same selected feature columns to the
    # untouched test set.
    X_test = X_test_raw[X_train.columns]

    if X_train.empty or len(X_train.columns) == 0:
        raise ValueError(
            "No valid predictive features remaining after "
            "filtering constant/ID columns."
        )

    # 6. Build preprocessing pipeline using training data only
    if progress_callback:
        progress_callback(
            0.25,
            "Fitting preprocessing pipeline on training data...",
        )

    preprocessor, num_cols, cat_cols = build_preprocessing_pipeline(
        X_train
    )

    preprocessor.fit(X_train)

    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    feature_names = get_feature_names(
        preprocessor,
        num_cols,
        cat_cols,
    )

    # 7. Candidate model selection
    candidates = get_candidate_models(
        problem_type,
        dataset_size=len(working_df),
        random_state=random_state,
    )

    model_results: List[Dict[str, Any]] = []
    trained_pipelines: Dict[str, Pipeline] = {}
    feature_importances: Dict[str, Dict[str, float]] = {}
    feature_attributions: Dict[str, List[Dict[str, Any]]] = {}

    total_models = len(candidates)

    if is_classification:
        cv_strategy = StratifiedKFold(
            n_splits=cv_folds,
            shuffle=True,
            random_state=random_state,
        )
    else:
        cv_strategy = KFold(
            n_splits=cv_folds,
            shuffle=True,
            random_state=random_state,
        )

    for idx, (name, model) in enumerate(candidates.items()):

        if progress_callback:
            pct = 0.30 + (idx / total_models) * 0.60
            progress_callback(
                pct,
                f"Training & Cross-Validating {name}...",
            )

        # Complete preprocessing + model pipeline.
        # Cross-validation fits preprocessing separately inside
        # every training fold.
        full_pipeline = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

        # 7a. Cross-validation on TRAINING data only
        try:
            scoring_metric = (
                "f1_macro"
                if is_classification
                else "r2"
            )

            cv_scores = cross_val_score(
                full_pipeline,
                X_train,
                y_train,
                cv=cv_strategy,
                scoring=scoring_metric,
                n_jobs=1,
            )

            cv_mean = float(np.mean(cv_scores))
            cv_std = float(np.std(cv_scores))

        except Exception as e:
            cv_mean = np.nan
            cv_std = np.nan
            print(
                f"WARNING: Cross-validation failed for "
                f"{name}: {e}"
            )

        # 7b. Fit final pipeline on the complete training set
        full_pipeline.fit(X_train, y_train)

        # 7c. Predict ONLY on held-out test data
        y_pred = full_pipeline.predict(X_test)

        # Store fitted pipeline for future predictions
        trained_pipelines[name] = full_pipeline

        fitted_model = full_pipeline.named_steps["model"]        

        # 7d. Evaluate on held-out test set
        if is_classification:

            y_prob = None

            

            if hasattr(fitted_model, "predict_proba"):
                try:
                    y_prob = full_pipeline.predict_proba(
                        X_test
                    )
                except Exception:
                    y_prob = None

            eval_metrics = evaluate_classification_model(
                y_true=(
                    y_test.values
                    if hasattr(y_test, "values")
                    else np.array(y_test)
                ),
                y_pred=y_pred,
                y_prob=y_prob,
                classes=(
                    fitted_model.classes_
                    if hasattr(fitted_model, "classes_")
                    else None
                ),
            )

            eval_metrics["Model"] = name
            eval_metrics["CV F1 (Train)"] = round(
                cv_mean,
                4,
            )
            eval_metrics["CV Std"] = round(
                cv_std,
                4,
            )

            model_results.append(eval_metrics)

        else:

            eval_metrics = evaluate_regression_model(
                y_true=(
                    y_test.values
                    if hasattr(y_test, "values")
                    else np.array(y_test)
                ),
                y_pred=y_pred,
                n_features=X_train_trans.shape[1],
            )

            eval_metrics["Model"] = name
            eval_metrics["CV R² (Train)"] = round(
                cv_mean,
                4,
            )
            eval_metrics["CV Std"] = round(
                cv_std,
                4,
            )

            model_results.append(eval_metrics)

        # 7e. Extract model-appropriate attribution in transformed space.
        attributions = _extract_feature_attributions(full_pipeline, name)
        if attributions:
            feature_attributions[name] = attributions
            feature_importances[name] = {
                item["feature"]: round(float(item["value"]), 4)
                for item in attributions
            }

    # 8. Comparison Table & Best Model Selection
    results_df = pd.DataFrame(model_results)

    if results_df.empty:
        raise ValueError(
            "No model evaluation results were produced."
        )

    if is_classification:

        # Select model using CV performance on TRAINING data.
        # The held-out test set is NOT used to select the model.
        results_df.sort_values(
            by=["CV F1 (Train)", "CV Std"],
            ascending=[False, True],
            inplace=True,
            na_position="last",
        )

    else:

        # Select regression model using CV R² on TRAINING data.
        results_df.sort_values(
            by=["CV R² (Train)", "CV Std"],
            ascending=[False, True],
            inplace=True,
            na_position="last",
        )

    best_model_name = results_df.iloc[0]["Model"]

    if progress_callback:
        progress_callback(
            1.0,
            f"Training complete! Selected model: {best_model_name}",
        )

    return {
        "problem_type": problem_type,
        "target_col": target_col,
        "results_df": results_df,
        "best_model_name": best_model_name,
        "best_model_pipeline": trained_pipelines[
            best_model_name
        ],
        "all_pipelines": trained_pipelines,
        "feature_importances": feature_importances,
        "feature_attributions": feature_attributions,
        "feature_names": feature_names,
        "raw_features_used": X_train.columns.tolist(),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "X_test": X_test,
        "y_test": y_test,
        "logs": dt_logs + filter_logs,
    }


def train_unsupervised_models(
    df: pd.DataFrame,
    k_range: Tuple[int, int] = (2, 6),
    random_state: int = 42,
) -> Dict[str, Any]:
    """Perform K-Means clustering across candidate cluster counts
    and PCA 2D projection.
    """

    working_df, _ = engineer_datetime_features(df.copy())

    X_filtered, _ = filter_suspicious_features(
        working_df,
        drop_leakage=False,
    )

    preprocessor, num_cols, cat_cols = (
        build_preprocessing_pipeline(X_filtered)
    )

    X_trans = preprocessor.fit_transform(X_filtered)

    # Evaluate multiple k values
    elbow_data: List[Dict[str, Any]] = []

    best_k = 3
    best_sil = -1.0

    max_k = min(
        k_range[1] + 1,
        len(X_trans),
    )

    for k in range(
        k_range[0],
        max_k,
    ):

        km = KMeans(
            n_clusters=k,
            n_init=10,
            random_state=random_state,
        )

        labels = km.fit_predict(X_trans)

        eval_dict = evaluate_clustering_model(
            X_trans,
            labels,
        )

        inertia = float(km.inertia_)

        sil_score = eval_dict.get(
            "Silhouette Score",
            0.0,
        )

        elbow_data.append(
            {
                "k": k,
                "Inertia": round(inertia, 2),
                "Silhouette Score": sil_score,
                "Davies-Bouldin": eval_dict.get(
                    "Davies-Bouldin Index",
                    0.0,
                ),
            }
        )

        if sil_score > best_sil:
            best_sil = sil_score
            best_k = k

    # Train optimal model
    optimal_kmeans = KMeans(
        n_clusters=best_k,
        n_init=10,
        random_state=random_state,
    )

    optimal_labels = optimal_kmeans.fit_predict(
        X_trans
    )

    # 2D PCA projection for visualization
    pca_2d = PCA(
        n_components=2,
        random_state=random_state,
    )

    pca_coords = pca_2d.fit_transform(X_trans)

    explained_var = [
        round(float(v) * 100, 1)
        for v in pca_2d.explained_variance_ratio_
    ]

    cluster_summary_df = pd.DataFrame(X_filtered)

    cluster_summary_df["Cluster"] = [
        f"Cluster {lbl}"
        for lbl in optimal_labels
    ]

    return {
        "problem_type": "Unsupervised Analysis",
        "best_k": best_k,
        "elbow_df": pd.DataFrame(elbow_data),
        "pca_coords": pca_coords,
        "pca_variance": explained_var,
        "cluster_labels": optimal_labels,
        "cluster_df": cluster_summary_df,
        "fitted_preprocessor": preprocessor,
        "fitted_kmeans": optimal_kmeans,
        "features_used": X_filtered.columns.tolist(),
    }