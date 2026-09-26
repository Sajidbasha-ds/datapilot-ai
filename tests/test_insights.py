"""Tests for model-aware feature attribution wording in generated insights."""

import pandas as pd

from src.insights import answer_datapilot_query, generate_automated_insights


def _logistic_results():
    return {
        "problem_type": "Binary Classification",
        "best_model_name": "Logistic Regression",
        "results_df": pd.DataFrame([{
            "Model": "Logistic Regression",
            "Accuracy": 0.9,
            "F1-Score (Macro)": 0.9,
        }]),
        "feature_importances": {"Logistic Regression": {"num__amount": 0.7}},
        "feature_attributions": {
            "Logistic Regression": [{
                "feature": "num__amount",
                "value": 0.7,
                "coefficient": -0.7,
                "coefficient_strength": 0.7,
                "direction": "negative",
                "decision_class": "yes",
                "method": "coefficient",
                "model_type": "Logistic Regression",
            }]
        },
    }


def test_logistic_insights_use_coefficient_and_noncausal_language():
    insights = generate_automated_insights(
        profile_data={"overview": {"rows": 20, "columns": 2}},
        quality_data={},
        ml_results=_logistic_results(),
    )
    text = " ".join(insights["executive_insights"] + insights["technical_insights"])

    assert "largest absolute model coefficient" in text
    assert "β = -0.7000" in text
    assert "decreases the Logistic Regression decision score/log-odds" in text
    assert "not evidence of causation" in text
    assert "driver" not in text.lower()
    assert "gini" not in text.lower()
    assert "gain" not in text.lower()


def test_logistic_feature_question_does_not_call_coefficients_importance_or_drivers():
    response = answer_datapilot_query(
        "Which features have the largest coefficients?",
        profile_data={"overview": {"rows": 20, "columns": 2}},
        quality_data={},
        ml_results=_logistic_results(),
    )

    assert "β = -0.7000" in response
    assert "not causal evidence" in response
    assert "driver" not in response.lower()
    assert "gini" not in response.lower()
    assert "gain" not in response.lower()