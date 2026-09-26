"""Unit tests for ML pipelines, training, evaluation, predictions, and clustering."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
import src.model_trainer as model_trainer
from src.feature_engineering import build_preprocessing_pipeline, filter_suspicious_features
from src.model_trainer import _extract_feature_attributions, train_supervised_models, train_unsupervised_models
from src.predictor import predict_single, predict_batch
from src.evaluator import evaluate_classification_model, evaluate_regression_model


@pytest.fixture
def classification_df():
    np.random.seed(42)
    n = 60
    return pd.DataFrame({
        "Feature_A": np.random.normal(10, 2, n),
        "Feature_B": np.random.exponential(1, n),
        "Category_C": np.random.choice(["Alpha", "Beta"], n),
        "Target_Class": np.random.choice(["Active", "Churned"], n),
    })


@pytest.fixture
def regression_df():
    np.random.seed(42)
    n = 60
    x1 = np.random.uniform(10, 50, n)
    x2 = np.random.normal(5, 1, n)
    y = 3.5 * x1 - 2.0 * x2 + np.random.normal(0, 1, n)
    return pd.DataFrame({
        "Feature_1": x1,
        "Feature_2": x2,
        "Target_Continuous": y,
    })


def test_classification_pipeline(classification_df):
    results = train_supervised_models(
        df=classification_df,
        target_col="Target_Class",
        problem_type="Binary Classification",
        test_size=0.25,
        cv_folds=2,
    )
    assert results["best_model_name"] in results["all_pipelines"]
    assert not results["results_df"].empty
    assert "Accuracy" in results["results_df"].columns
    assert "F1-Score (Macro)" in results["results_df"].columns

    # Test single prediction
    pipeline = results["best_model_pipeline"]
    sample_input = {"Feature_A": 11.2, "Feature_B": 0.8, "Category_C": "Alpha"}
    pred_res = predict_single(
        pipeline=pipeline,
        input_dict=sample_input,
        problem_type="Binary Classification",
        target_col="Target_Class",
    )
    assert pred_res["prediction"] in ["Active", "Churned"]

    # Test batch prediction
    batch_df = pd.DataFrame([sample_input, {"Feature_A": 8.5, "Feature_B": 1.5, "Category_C": "Beta"}])
    scored_df, summary = predict_batch(
        pipeline=pipeline,
        batch_df=batch_df,
        required_features=["Feature_A", "Feature_B", "Category_C"],
        problem_type="Binary Classification",
        target_col="Target_Class",
    )
    assert "Predicted_Target_Class" in scored_df.columns
    assert summary["total_rows_scored"] == 2


def test_regression_pipeline(regression_df):
    results = train_supervised_models(
        df=regression_df,
        target_col="Target_Continuous",
        problem_type="Regression",
        test_size=0.25,
        cv_folds=2,
    )
    assert not results["results_df"].empty
    assert "RMSE" in results["results_df"].columns
    assert "R²" in results["results_df"].columns


def test_unsupervised_pipeline(classification_df):
    unsup_results = train_unsupervised_models(
        df=classification_df[["Feature_A", "Feature_B"]],
        k_range=(2, 4),
    )
    assert "elbow_df" in unsup_results
    assert not unsup_results["elbow_df"].empty
    assert "pca_coords" in unsup_results
    assert len(unsup_results["cluster_labels"]) == len(classification_df)


def _fit_attribution_pipeline(X, y, model):
    preprocessor, _, _ = build_preprocessing_pipeline(X)
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])
    pipeline.fit(X, y)
    return pipeline


def test_logistic_attributions_keep_transformed_names_and_signed_coefficients():
    X = pd.DataFrame({
        "amount": np.linspace(-3, 3, 90),
        "segment": ["north", "south", "west"] * 30,
    })
    y = np.where(X["amount"] + X["segment"].map({"north": 1.0, "south": -0.8, "west": 0.2}) > 0, "yes", "no")
    pipeline = _fit_attribution_pipeline(X, y, LogisticRegression(max_iter=1000))

    records = _extract_feature_attributions(pipeline, "Logistic Regression")
    names = set(pipeline.named_steps["preprocessor"].get_feature_names_out())
    coefficient_by_name = dict(zip(
        pipeline.named_steps["preprocessor"].get_feature_names_out(),
        pipeline.named_steps["model"].coef_[0],
    ))

    assert {record["feature"] for record in records} == names
    assert any(name.startswith("cat__segment_") for name in names)
    assert all(record["method"] == "coefficient" for record in records)
    for record in records:
        expected = float(coefficient_by_name[record["feature"]])
        assert record["coefficient"] == pytest.approx(expected)
        assert record["value"] == pytest.approx(abs(expected))
        assert record["direction"] == ("positive" if expected > 0 else "negative" if expected < 0 else "zero")
        assert "Gini" not in record and "gain" not in record


def test_tree_attributions_keep_tree_importances():
    X = pd.DataFrame({"signal": np.arange(30), "noise": np.tile([0, 1, 2], 10)})
    y = np.where(X["signal"] > 14, "high", "low")
    pipeline = _fit_attribution_pipeline(X, y, DecisionTreeClassifier(max_depth=2, random_state=0))

    records = _extract_feature_attributions(pipeline, "Decision Tree")
    expected = dict(zip(
        pipeline.named_steps["preprocessor"].get_feature_names_out(),
        pipeline.named_steps["model"].feature_importances_,
    ))

    assert {record["method"] for record in records} == {"tree_feature_importance"}
    assert {record["feature"]: record["value"] for record in records} == pytest.approx(expected)


def test_knn_has_no_fabricated_attribution():
    X = pd.DataFrame({"signal": np.arange(30), "noise": np.tile([0, 1, 2], 10)})
    y = np.where(X["signal"] > 14, "high", "low")
    pipeline = _fit_attribution_pipeline(X, y, KNeighborsClassifier(n_neighbors=3))

    assert _extract_feature_attributions(pipeline, "K-Nearest Neighbors") == []


def test_multiclass_logistic_attribution_is_class_specific():
    X = pd.DataFrame({
        "x": np.tile(np.arange(3), 30),
        "y": np.repeat(np.arange(3), 30),
    })
    target = np.array(["a", "b", "c"] * 30)
    pipeline = _fit_attribution_pipeline(X, target, LogisticRegression(max_iter=1000))

    records = _extract_feature_attributions(pipeline, "Logistic Regression")

    assert records
    assert all("coefficient" not in record for record in records)
    assert all("direction" not in record for record in records)
    assert all(len(record["class_coefficients"]) == 3 for record in records)


def test_feature_screening_only_removes_implemented_suspicious_columns():
    target = pd.Series(np.arange(30, dtype=float), name="target")
    frame = pd.DataFrame({
        "numeric_target_copy": target,
        "record_id": [f"row-{idx}" for idx in range(30)],
        "constant": [1] * 30,
        "noise": np.random.default_rng(2).normal(size=30),
    })

    filtered, logs = filter_suspicious_features(frame, y=target)
    filtered_without_target, _ = filter_suspicious_features(frame)

    assert "numeric_target_copy" not in filtered.columns
    assert "record_id" not in filtered.columns
    assert "constant" not in filtered.columns
    assert "numeric_target_copy" in filtered_without_target.columns
    assert any("target leakage suspect" in item for item in logs)


def test_training_split_precedes_filter_and_cv_scores_select_model(monkeypatch):
    rng = np.random.default_rng(17)
    target = pd.Series(np.arange(60, dtype=float), name="target")
    frame = pd.DataFrame({
        "target_copy": target,
        "record_id": [f"key-{idx}" for idx in range(60)],
        "noise": rng.normal(size=60),
        "constant": 1,
        "target": target,
    })
    events = []
    observed = {}
    original_split = model_trainer.train_test_split
    original_filter = model_trainer.filter_suspicious_features

    def split_spy(*args, **kwargs):
        split = original_split(*args, **kwargs)
        observed["outer_train_index"] = split[0].index
        observed["outer_test_index"] = split[1].index
        observed["outer_train_y_index"] = split[2].index
        events.append("split")
        return split

    def filter_spy(features, y=None, **kwargs):
        events.append("filter")
        observed["filter_y_index"] = y.index if y is not None else None
        filtered, logs = original_filter(features, y=y, **kwargs)
        observed["screened_columns"] = set(filtered.columns)
        return filtered, logs

    def cv_spy(estimator, X, y, **kwargs):
        observed.setdefault("cv_indices", []).append(X.index)
        depth = estimator.named_steps["model"].max_depth
        return np.array([0.9, 0.9]) if depth == 1 else np.array([0.1, 0.1])

    holdout_scores = iter([
        {"R²": 0.01, "Adjusted R²": 0.01, "RMSE": 10.0},
        {"R²": 0.99, "Adjusted R²": 0.99, "RMSE": 0.1},
    ])

    monkeypatch.setattr(model_trainer, "train_test_split", split_spy)
    monkeypatch.setattr(model_trainer, "filter_suspicious_features", filter_spy)
    monkeypatch.setattr(model_trainer, "get_candidate_models", lambda *args, **kwargs: {
        "CV selected": DecisionTreeRegressor(max_depth=1, random_state=1),
        "Holdout scorer": DecisionTreeRegressor(max_depth=2, random_state=2),
    })
    monkeypatch.setattr(model_trainer, "cross_val_score", cv_spy)
    monkeypatch.setattr(model_trainer, "evaluate_regression_model", lambda **kwargs: next(holdout_scores))

    result = model_trainer.train_supervised_models(
        df=frame,
        target_col="target",
        problem_type="Regression",
        test_size=0.2,
        cv_folds=2,
        random_state=19,
    )

    assert events == ["split", "filter"]
    assert observed["filter_y_index"].equals(observed["outer_train_y_index"])
    assert set(observed["outer_train_index"]).isdisjoint(observed["outer_test_index"])
    assert observed["screened_columns"] == {"noise"}
    assert all(set(index).issubset(observed["outer_train_index"]) for index in observed["cv_indices"])
    assert result["best_model_name"] == "CV selected"
