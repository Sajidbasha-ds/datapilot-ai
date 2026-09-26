"""End-to-End Machine Learning Training Pipeline for DataPilot AI."""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score, train_test_split
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


def train_supervised_models(
    df: pd.DataFrame,
    target_col: str,
    problem_type: str,
    test_size: float = 0.20,
    random_state: int = 42,
    cv_folds: int = 3,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Dict[str, Any]:
    """Executes leakage-free split, preprocessing, model training, cross-validation, and evaluation."""
    # 1. Clean missing targets if any
    working_df = df.dropna(subset=[target_col]).copy()
    if len(working_df) < 15:
        raise ValueError(f"Dataset has only {len(working_df)} valid rows. At least 15 rows required for training.")

    # 2. Extract Datetime features
    if progress_callback:
        progress_callback(0.1, "Engineering datetime features...")
    working_df, dt_logs = engineer_datetime_features(working_df)

    # 3. Separate features X and target y
    y_raw = working_df[target_col]
    X_raw = working_df.drop(columns=[target_col])

    # 4. Filter suspicious columns (IDs, constant, obvious leakage)
    if progress_callback:
        progress_callback(0.15, "Filtering non-predictive identifiers & leakage...")
    X_filtered, filter_logs = filter_suspicious_features(X_raw, y=y_raw if "Regression" in problem_type else None)

    if X_filtered.empty or len(X_filtered.columns) == 0:
        raise ValueError("No valid predictive features remaining after filtering constant/ID columns.")

    # 5. Stratified or Standard Train/Test Split (Prevent data leakage)
    is_classification = "Classification" in problem_type
    stratify = y_raw if (is_classification and y_raw.value_counts().min() >= 2) else None

    X_train, X_test, y_train, y_test = train_test_split(
        X_filtered,
        y_raw,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )

    # 6. Build Preprocessing Pipeline (FITTED STRICTLY ON X_train)
    if progress_callback:
        progress_callback(0.25, "Fitting preprocessing pipeline on training fold...")
    preprocessor, num_cols, cat_cols = build_preprocessing_pipeline(X_train)
    preprocessor.fit(X_train)

    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)
    feature_names = get_feature_names(preprocessor, num_cols, cat_cols)

    # 7. Candidate Models Selection
    candidates = get_candidate_models(problem_type, dataset_size=len(working_df), random_state=random_state)
    model_results: List[Dict[str, Any]] = []
    trained_pipelines: Dict[str, Pipeline] = {}
    feature_importances: Dict[str, Dict[str, float]] = {}

    total_models = len(candidates)
    cv_strategy = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state) if is_classification else KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    for idx, (name, model) in enumerate(candidates.items()):
        if progress_callback:
            pct = 0.3 + (idx / total_models) * 0.6
            progress_callback(pct, f"Training & Cross-Validating {name}...")

        # Full pipeline combining preprocessor + estimator
        full_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        try:
            # Cross-validation score (evaluated on X_train to prevent leakage)
            scoring_metric = "f1_macro" if is_classification else "r2"
            cv_scores = cross_val_score(full_pipeline, X_train, y_train, cv=cv_strategy, scoring=scoring_metric, n_jobs=1)
            cv_mean = float(np.mean(cv_scores))
            cv_std = float(np.std(cv_scores))
        except Exception as e:
            cv_mean = np.nan
            cv_std = np.nan
            print(f"WARNING: Cross-validation failed for {name}: {e}")

        # Fit the complete pipeline on the training set
        full_pipeline.fit(X_train, y_train)

        # Predict using the fitted complete pipeline
        y_pred = full_pipeline.predict(X_test)

        # Store the fitted pipeline for future predictions
        trained_pipelines[name] = full_pipeline
        # Model evaluation on held-out test fold
        if is_classification:
            y_prob = None
            if hasattr(model, "predict_proba"):
                try:
                    y_prob = model.predict_proba(X_test_trans)
                except Exception:
                    y_prob = None
            eval_metrics = evaluate_classification_model(
                y_true=y_test.values if hasattr(y_test, "values") else np.array(y_test),
                y_pred=y_pred,
                y_prob=y_prob,
                classes=model.classes_ if hasattr(model, "classes_") else None,
            )
            eval_metrics["Model"] = name
            eval_metrics["CV F1 (Train)"] = round(cv_mean, 4)
            eval_metrics["CV Std"] = round(cv_std, 4)
            model_results.append(eval_metrics)
        else:
            eval_metrics = evaluate_regression_model(
                y_true=y_test.values if hasattr(y_test, "values") else np.array(y_test),
                y_pred=y_pred,
                n_features=X_train_trans.shape[1],
            )
            eval_metrics["Model"] = name
            eval_metrics["CV R² (Train)"] = round(cv_mean, 4)
            eval_metrics["CV Std"] = round(cv_std, 4)
            model_results.append(eval_metrics)

        # Extract Feature Importances / Coefficients
        importances: Dict[str, float] = {}
        if hasattr(model, "feature_importances_"):
            raw_imp = model.feature_importances_
            if len(raw_imp) == len(feature_names):
                for f_name, imp in zip(feature_names, raw_imp):
                    importances[f_name] = round(float(imp), 4)
        elif hasattr(model, "coef_"):
            raw_coef = model.coef_
            if raw_coef.ndim > 1:
                raw_coef = np.mean(np.abs(raw_coef), axis=0)
            else:
                raw_coef = np.abs(raw_coef)
            if len(raw_coef) == len(feature_names):
                for f_name, imp in zip(feature_names, raw_coef):
                    importances[f_name] = round(float(imp), 4)

        if importances:
            # Sort top 15 descending
            sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True)[:15])
            feature_importances[name] = sorted_imp

    # 8. Comparison Table & Best Model Selection
    results_df = pd.DataFrame(model_results)
    best_model_name: str

    if is_classification:
        # Select the model using cross-validation on the training data.
        # The held-out test set must NOT be used to choose the winner.
        results_df.sort_values(
            by=["CV F1 (Train)", "CV Std"],
            ascending=[False, True],
            inplace=True,
            na_position="last",
        )
        best_model_name = results_df.iloc[0]["Model"]

    else:
        # Select the regression model using cross-validation R².
        results_df.sort_values(
            by=["CV R² (Train)", "CV Std"],
            ascending=[False, True],
            inplace=True,
            na_position="last",
        )
        best_model_name = results_df.iloc[0]["Model"]    

    if progress_callback:
        progress_callback(1.0, f"Training complete! Best performer: {best_model_name}")

    return {
        "problem_type": problem_type,
        "target_col": target_col,
        "results_df": results_df,
        "best_model_name": best_model_name,
        "best_model_pipeline": trained_pipelines[best_model_name],
        "all_pipelines": trained_pipelines,
        "feature_importances": feature_importances,
        "feature_names": feature_names,
        "raw_features_used": X_filtered.columns.tolist(),
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
    """Performs K-Means clustering across candidate cluster counts and PCA 2D projection."""
    working_df, _ = engineer_datetime_features(df.copy())
    X_filtered, _ = filter_suspicious_features(working_df, drop_leakage=False)

    preprocessor, num_cols, cat_cols = build_preprocessing_pipeline(X_filtered)
    X_trans = preprocessor.fit_transform(X_filtered)

    # Evaluate multiple k values
    elbow_data: List[Dict[str, Any]] = []
    best_k = 3
    best_sil = -1.0

    for k in range(k_range[0], min(k_range[1] + 1, len(X_trans))):
        km = KMeans(n_clusters=k, n_init=10, random_state=random_state)
        labels = km.fit_predict(X_trans)
        eval_dict = evaluate_clustering_model(X_trans, labels)
        inertia = float(km.inertia_)

        sil_score = eval_dict.get("Silhouette Score", 0.0)
        elbow_data.append({
            "k": k,
            "Inertia": round(inertia, 2),
            "Silhouette Score": sil_score,
            "Davies-Bouldin": eval_dict.get("Davies-Bouldin Index", 0.0),
        })
        if sil_score > best_sil:
            best_sil = sil_score
            best_k = k

    # Train optimal model
    optimal_kmeans = KMeans(n_clusters=best_k, n_init=10, random_state=random_state)
    optimal_labels = optimal_kmeans.fit_predict(X_trans)

    # 2D PCA projection for visualization
    pca_2d = PCA(n_components=2, random_state=random_state)
    pca_coords = pca_2d.fit_transform(X_trans)
    explained_var = [round(float(v) * 100, 1) for v in pca_2d.explained_variance_ratio_]

    cluster_summary_df = pd.DataFrame(X_filtered)
    cluster_summary_df["Cluster"] = [f"Cluster {lbl}" for lbl in optimal_labels]

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
