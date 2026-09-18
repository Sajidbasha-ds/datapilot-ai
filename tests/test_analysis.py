"""Unit tests for profiling, cleaning, eda, and statistics."""

import numpy as np
import pandas as pd
import pytest
from src.profiler import profile_dataset
from src.cleaner import analyze_data_quality, clean_dataset
from src.statistics import compute_descriptive_stats, compute_pairwise_correlation_with_pvalues, run_hypothesis_test
from src.target_detector import detect_target_column
from src.problem_detector import detect_problem_type


@pytest.fixture
def sample_df():
    np.random.seed(42)
    return pd.DataFrame({
        "id": range(1, 101),
        "constant_col": [42] * 100,
        "age": np.random.randint(20, 60, size=100),
        "income": np.random.normal(50000, 15000, size=100),
        "department": np.random.choice(["HR", "Engineering", "Marketing"], size=100),
        "churn": np.random.choice(["Yes", "No"], size=100, p=[0.3, 0.7]),
    })


def test_profiler(sample_df):
    prof = profile_dataset(sample_df)
    assert prof["overview"]["rows"] == 100
    assert prof["overview"]["columns"] == 6
    assert "constant_col" in prof["overview"]["constant_columns"]
    suspicious_cols = [s["column"] for s in prof["overview"]["suspicious_columns"]]
    assert "id" in suspicious_cols or "constant_col" in suspicious_cols


def test_cleaner_analysis_and_cleaning(sample_df):
    # Introduce duplicate and null
    sample_df.iloc[0, 2] = np.nan
    sample_df = pd.concat([sample_df, sample_df.iloc[[1]]], ignore_index=True)

    quality = analyze_data_quality(sample_df, target_col="churn")
    assert quality["duplicate_count"] == 1
    assert "age" in quality["missing_recommendations"]

    cleaned, logs = clean_dataset(sample_df, drop_duplicates=True, drop_constant_cols=True, impute_missing=True)
    assert len(cleaned) == 100
    assert "constant_col" not in cleaned.columns
    assert cleaned["age"].isna().sum() == 0


def test_statistics(sample_df):
    desc = compute_descriptive_stats(sample_df)
    assert not desc.empty
    assert "income" in desc["Feature"].values

    corr_res = compute_pairwise_correlation_with_pvalues(sample_df, "age", "income")
    assert "pearson" in corr_res
    assert -1.0 <= corr_res["pearson"]["coefficient"] <= 1.0

    t_res = run_hypothesis_test(sample_df, "Two-Sample T-Test", "income", "churn")
    assert "p_value" in t_res


def test_target_and_problem_detection(sample_df):
    target_res = detect_target_column(sample_df)
    assert target_res["suggested_target"] == "churn"

    prob_res = detect_problem_type(sample_df, target_col="churn")
    assert prob_res["problem_type"] == "Binary Classification"

    prob_reg = detect_problem_type(sample_df, target_col="income")
    assert prob_reg["problem_type"] == "Regression"
