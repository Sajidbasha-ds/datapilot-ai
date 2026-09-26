"""End-to-end pipeline integration verification for DataPilot AI."""

import os
import pandas as pd
from src.data_loader import load_dataset
from src.profiler import profile_dataset
from src.cleaner import analyze_data_quality, clean_dataset
from src.statistics import compute_descriptive_stats, compute_pairwise_correlation_with_pvalues, run_hypothesis_test
from src.target_detector import detect_target_column
from src.problem_detector import detect_problem_type
from src.model_trainer import train_supervised_models, train_unsupervised_models
from src.predictor import predict_single, predict_batch
from src.insights import generate_automated_insights, answer_datapilot_query
from src.database import get_prediction_history
from src.report_generator import generate_pdf_report


def test_complete_e2e_lifecycle(tmp_path):
    # 1. Ingestion
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "customer_churn.csv")
    df, summary = load_dataset(sample_path, "customer_churn.csv")
    assert len(df) == 50
    assert summary["rows"] == 50

    # 2. Profiling
    prof = profile_dataset(df)
    assert prof["overview"]["rows"] == 50
    assert prof["overview"]["columns"] == 9

    # 3. Quality & Cleaning
    qual = analyze_data_quality(df, target_col="Churn")
    cleaned_df, logs = clean_dataset(df, drop_duplicates=True, drop_constant_cols=True, impute_missing=True)
    assert len(cleaned_df) == 50

    # 4. Statistics
    desc = compute_descriptive_stats(cleaned_df)
    assert not desc.empty
    corr_res = compute_pairwise_correlation_with_pvalues(cleaned_df, "Tenure_Months", "MonthlyCharges")
    assert "pearson" in corr_res

    # 5. Target & Problem Detection
    tgt_info = detect_target_column(cleaned_df)
    assert tgt_info["suggested_target"] == "Churn"
    prob_info = detect_problem_type(cleaned_df, target_col="Churn")
    assert prob_info["problem_type"] == "Binary Classification"

    # 6. Model Training & Benchmarks
    ml_res = train_supervised_models(
        df=cleaned_df,
        target_col="Churn",
        problem_type=prob_info["problem_type"],
        test_size=0.20,
        cv_folds=2,
    )
    assert ml_res["best_model_name"] in ml_res["all_pipelines"]
    assert not ml_res["results_df"].empty

    # 7. Single Inference
    sample_rec = {
        "Age": 45,
        "Tenure_Months": 15,
        "MonthlyCharges": 75.0,
        "TotalCharges": 1125.0,
        "Contract_Type": "Month-to-month",
        "InternetService": "Fiber optic",
        "TechSupport": "No",
    }
    single_res = predict_single(
        pipeline=ml_res["best_model_pipeline"],
        input_dict=sample_rec,
        problem_type=prob_info["problem_type"],
        target_col="Churn",
    )
    assert single_res["prediction"] in ["Yes", "No"]
    assert single_res["confidence"] is not None

    # 8. Batch Inference
    batch_df = pd.DataFrame([sample_rec, sample_rec])
    scored_df, batch_sum = predict_batch(
        pipeline=ml_res["best_model_pipeline"],
        batch_df=batch_df,
        required_features=ml_res["raw_features_used"],
        problem_type=prob_info["problem_type"],
        target_col="Churn",
    )
    assert "Predicted_Churn" in scored_df.columns
    assert batch_sum["total_rows_scored"] == 2

    # 9. AI Insights & QA
    insights = generate_automated_insights(prof, qual, ml_res)
    assert len(insights["executive_insights"]) > 0
    assert len(insights["technical_insights"]) > 0

    qa_reply = answer_datapilot_query("What are the most important columns?", prof, qual, ml_res)
    assert "tree feature-importance value" in qa_reply

    # 10. PDF Report Generation
    test_pdf = str(tmp_path / "e2e_report.pdf")
    pdf_path = generate_pdf_report(
        filename_or_path=test_pdf,
        dataset_name="Customer Churn Benchmark",
        profile_data=prof,
        quality_data=qual,
        ml_results=ml_res,
        insights_data=insights,
    )
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000

    # 11. Unsupervised Mode
    num_sub = cleaned_df[["Tenure_Months", "MonthlyCharges", "TotalCharges"]]
    unsup_res = train_unsupervised_models(num_sub, k_range=(2, 3))
    assert unsup_res["best_k"] in [2, 3]
    assert len(unsup_res["cluster_labels"]) == 50

    print("END-TO-END PIPELINE VALIDATED SUCCESSFULLY!")


if __name__ == "__main__":
    import tempfile
    import pathlib
    with tempfile.TemporaryDirectory() as td:
        test_complete_e2e_lifecycle(pathlib.Path(td))
