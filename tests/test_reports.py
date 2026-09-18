"""Unit tests for automated ReportLab PDF generation."""

import os
import pandas as pd
import pytest
from src.report_generator import generate_pdf_report


def test_generate_pdf_report(tmp_path):
    output_pdf = str(tmp_path / "test_report.pdf")

    profile_data = {
        "overview": {
            "rows": 50,
            "columns": 5,
            "total_missing": 2,
            "missing_pct": 0.8,
            "duplicate_rows": 0,
            "duplicate_pct": 0.0,
            "numerical_columns_count": 3,
            "categorical_columns_count": 2,
            "datetime_columns_count": 0,
            "suspicious_count": 0,
        }
    }
    quality_data = {
        "issues": [
            {"type": "Missingness", "title": "2 missing entries in Feature B", "description": "Imputed via median."}
        ]
    }
    ml_results = {
        "problem_type": "Binary Classification",
        "target_col": "Outcome",
        "best_model_name": "Random Forest",
        "results_df": pd.DataFrame([
            {"Model": "Random Forest", "Accuracy": 0.92, "F1-Score (Macro)": 0.91, "Precision (Macro)": 0.90, "Recall (Macro)": 0.92},
            {"Model": "Logistic Regression", "Accuracy": 0.86, "F1-Score (Macro)": 0.84, "Precision (Macro)": 0.85, "Recall (Macro)": 0.83},
        ]),
        "feature_importances": {
            "Random Forest": {"Feature A": 0.65, "Feature B": 0.35}
        },
    }
    insights_data = {
        "executive_insights": ["Executive summary statement"],
        "technical_insights": ["Technical specification statement"],
    }

    res_path = generate_pdf_report(
        filename_or_path=output_pdf,
        dataset_name="Test Bench",
        profile_data=profile_data,
        quality_data=quality_data,
        ml_results=ml_results,
        insights_data=insights_data,
    )

    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 1000
