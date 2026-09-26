"""Regression tests for appropriately scoped leakage explanations."""

import pandas as pd

from src import report_generator
from src.insights import answer_datapilot_query, generate_automated_insights
from src.cleaner import analyze_data_quality


def _leakage_results():
    return {
        "problem_type": "Regression",
        "best_model_name": "Random Forest",
        "results_df": pd.DataFrame(),
    }


def test_generated_insight_describes_checks_without_guaranteeing_absence():
    insights = generate_automated_insights(
        profile_data={"overview": {"rows": 100, "columns": 4}},
        quality_data={},
        ml_results=_leakage_results(),
    )
    text = " ".join(insights["technical_insights"]).lower()

    assert "splits data before feature screening" in text
    assert "absolute pearson r >= 0.98" in text
    assert "full dataset for review" in text
    assert "does not remove features" in text
    assert "not repeated inside each cv fold" in text
    assert "do not establish that all leakage is absent" in text
    assert "leakage-free" not in text
    assert "guarantee zero" not in text


def test_chat_leakage_questions_receive_scoped_answer():
    questions = [
        "Is my dataset free from leakage?",
        "Did you prevent leakage?",
        "Is leakage handled?",
        "Can I trust this model?",
        "Are the features safe?",
        "Was the test set protected?",
    ]

    for question in questions:
        answer = answer_datapilot_query(
            question,
            profile_data={"overview": {"rows": 100, "columns": 4}},
            quality_data={},
            ml_results=_leakage_results(),
        ).lower()
        assert "do not establish that all leakage is absent" in answer
        assert "cv scores may be optimistic" in answer
        assert "temporal leakage" in answer
        assert "leakage-free" not in answer


def test_report_distinguishes_checks_from_coverage_limits(tmp_path, monkeypatch):
    captured = {}

    class CapturingDocument:
        def __init__(self, *args, **kwargs):
            pass

        def build(self, story):
            captured["story"] = story

    monkeypatch.setattr(report_generator, "SimpleDocTemplate", CapturingDocument)
    report_generator.generate_pdf_report(
        filename_or_path=str(tmp_path / "leakage_scope.pdf"),
        dataset_name="Leakage Scope Test",
        profile_data={"overview": {"rows": 50, "columns": 3}},
        quality_data={},
        ml_results={
            "problem_type": "Regression",
            "best_model_name": "Random Forest",
            "results_df": pd.DataFrame([{"Model": "Random Forest", "R²": 0.8}]),
        },
    )
    paragraphs = " ".join(
        item.getPlainText()
        for item in captured["story"]
        if hasattr(item, "getPlainText")
    ).lower()

    assert "supervised leakage checks implemented" in paragraphs
    assert "absolute pearson r >= 0.98" in paragraphs
    assert "across the full dataset for review" in paragraphs
    assert "does not remove those features" in paragraphs
    assert "scope and limitations" in paragraphs
    assert "cv scores may be optimistic" in paragraphs
    assert "do not establish that all leakage is absent" in paragraphs
    assert "leakage-free" not in paragraphs
    assert "guarantee zero" not in paragraphs


def test_quality_analysis_flags_numeric_target_correlation_for_review():
    target = pd.Series(range(30), dtype=float)
    frame = pd.DataFrame({
        "target": target,
        "numeric_copy": target * 2,
        "other": range(30, 60),
    })

    result = analyze_data_quality(frame, target_col="target")

    assert any(
        candidate["feature"] == "numeric_copy"
        and candidate["target"] == "target"
        for candidate in result["leakage_candidates"]
    )


def test_unsupervised_chat_does_not_claim_supervised_split_controls():
    answer = answer_datapilot_query(
        "Is this dataset free from leakage?",
        profile_data={"overview": {"rows": 50, "columns": 3}},
        quality_data={},
        ml_results={"problem_type": "Unsupervised Analysis"},
    ).lower()

    assert "unsupervised workflow does not create a supervised train/test split" in answer
    assert "holdout" not in answer
    assert "cannot establish that all leakage is absent" in answer