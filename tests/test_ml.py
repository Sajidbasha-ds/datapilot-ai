"""Unit tests for ML pipelines, training, evaluation, predictions, and clustering."""

import numpy as np
import pandas as pd
import pytest
from src.model_trainer import train_supervised_models, train_unsupervised_models
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
