"""Integration tests for DataPilot AI FastAPI backend endpoints."""

import pytest
from starlette.testclient import TestClient

from api.index import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "capabilities" in data


def test_sample_datasets_list():
    response = client.get("/api/dataset/samples")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    samples = res["data"]
    assert len(samples) >= 3
    sample_ids = [s["id"] for s in samples]
    assert "customer_churn" in sample_ids
    assert "house_prices" in sample_ids
    assert "student_performance" in sample_ids


def test_automatic_pearson_correlation_hypothesis_test():
    load_res = client.get("/api/dataset/sample/customer_churn")
    assert load_res.status_code == 200
    session_id = load_res.json()["data"]["session_id"]

    response = client.post(
        "/api/statistics/hypothesis",
        json={
            "session_id": session_id,
            "col1": "Age",
            "col2": "MonthlyCharges",
            "test_type": "auto",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["test_name"] == "Pearson Correlation Test"
    assert -1.0 <= data["data"]["statistic"] <= 1.0
    assert "p_value" in data["data"]


def test_automatic_chi_square_hypothesis_test():
    load_res = client.get("/api/dataset/sample/customer_churn")
    assert load_res.status_code == 200
    session_id = load_res.json()["data"]["session_id"]

    response = client.post(
        "/api/statistics/hypothesis",
        json={
            "session_id": session_id,
            "col1": "Contract_Type",
            "col2": "InternetService",
            "test_type": "auto",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["test_name"] == "Chi-Square Test of Independence"
    assert "chi2_statistic" in data["data"]
    assert "p_value" in data["data"]


def test_full_api_workflow_lifecycle():
    # 1. Load customer churn sample
    load_res = client.get("/api/dataset/sample/customer_churn")
    assert load_res.status_code == 200
    load_data = load_res.json()
    assert load_data["success"] is True
    session_id = load_data["data"]["session_id"]
    assert session_id is not None
    assert load_data["data"]["rows"] > 0
    assert "profile" in load_data["data"]
    assert "quality" in load_data["data"]

    # 2. Check summary
    sum_res = client.get(f"/api/dataset/summary/{session_id}")
    assert sum_res.status_code == 200
    assert sum_res.json()["success"] is True

    # 3. Update target
    target_res = client.post("/api/dataset/target", json={"session_id": session_id, "target_col": "Churn"})
    assert target_res.status_code == 200
    assert target_res.json()["success"] is True
    assert "Classification" in target_res.json()["data"]["problem_type"]

    # 4. EDA distribution
    dist_res = client.post("/api/eda/distribution", json={"session_id": session_id, "column": "MonthlyCharges"})
    assert dist_res.status_code == 200
    assert dist_res.json()["success"] is True
    assert dist_res.json()["data"]["is_numeric"] is True

    # 5. Statistics descriptive
    stats_res = client.get(f"/api/statistics/descriptive/{session_id}")
    assert stats_res.status_code == 200
    assert stats_res.json()["success"] is True
    assert len(stats_res.json()["data"]) > 0

    # 6. Train Supervised Models
    train_res = client.post(
        "/api/ml/train",
        json={
            "session_id": session_id,
            "target_col": "Churn",
            "test_size": 0.20,
            "cv_folds": 2,
        },
    )
    assert train_res.status_code == 200
    t_data = train_res.json()
    assert t_data["success"] is True
    assert "leaderboard" in t_data["data"]
    assert len(t_data["data"]["leaderboard"]) > 0
    assert t_data["data"]["best_model_name"] is not None
    assert "feature_attributions" in t_data["data"]
    assert all(
        "feature" in item and "importance" in item
        for item in t_data["data"]["feature_importance"]
    )

    # 7. Single Prediction
    schema_res = client.get(f"/api/predict/schema/{session_id}")
    assert schema_res.status_code == 200
    schema_data = schema_res.json()["data"]
    fields = schema_data["fields"]
    sample_input = {f["name"]: f.get("default", 0) for f in fields}

    pred_res = client.post(
        "/api/predict/single",
        json={"session_id": session_id, "features": sample_input},
    )
    assert pred_res.status_code == 200
    assert pred_res.json()["success"] is True
    assert "prediction" in pred_res.json()["data"]

    # 8. AI Insights & Chat
    insights_res = client.get(f"/api/insights/generate/{session_id}")
    assert insights_res.status_code == 200
    assert insights_res.json()["success"] is True
    assert "executive_insights" in insights_res.json()["data"]

    chat_res = client.post(
        "/api/insights/chat",
        json={"session_id": session_id, "message": "Which model performed best?"},
    )
    assert chat_res.status_code == 200
    assert chat_res.json()["success"] is True
    assert len(chat_res.json()["data"]["content"]) > 0

    # 9. PDF Report Generation & Download
    rep_res = client.post("/api/report/generate", json={"session_id": session_id})
    assert rep_res.status_code == 200
    assert rep_res.json()["success"] is True

    down_res = client.get(f"/api/report/download/{session_id}")
    assert down_res.status_code == 200
    assert down_res.headers["content-type"] == "application/pdf"
    assert len(down_res.content) > 1000
