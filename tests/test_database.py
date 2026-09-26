"""Unit tests for SQLite prediction history database."""

import os
import sqlite3
import pytest
from src.database import init_db, log_prediction, get_prediction_history, clear_prediction_history


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_datapilot.db"
    return str(db_file)


def test_database_lifecycle(temp_db):
    init_db(temp_db)
    assert os.path.exists(temp_db)

    # Insert log
    rec_id = log_prediction(
        dataset_name="unit_test_dataset",
        target_col="Churn",
        problem_type="Binary Classification",
        model_name="Random Forest",
        input_data={"tenure": 24, "charges": 75.5},
        prediction_result="Yes",
        confidence=0.88,
        db_path=temp_db,
    )
    assert rec_id > 0

    # Fetch logs
    hist_df = get_prediction_history(limit=10, db_path=temp_db)
    assert len(hist_df) == 1
    assert hist_df.iloc[0]["dataset_name"] == "unit_test_dataset"
    assert hist_df.iloc[0]["prediction_result"] == "Yes"

    # Clear logs
    deleted = clear_prediction_history(temp_db)
    assert deleted == 1
    assert len(get_prediction_history(db_path=temp_db)) == 0


def test_prediction_history_is_scoped_by_session(temp_db):
    for session_id, dataset_name in (
        ("session-A", "dataset_a"),
        ("session-B", "dataset_b"),
    ):
        log_prediction(
            dataset_name=dataset_name,
            target_col="target",
            problem_type="Classification",
            model_name="Test Model",
            input_data={"feature": session_id},
            prediction_result=session_id,
            session_id=session_id,
            db_path=temp_db,
        )

    session_a = get_prediction_history(session_id="session-A", db_path=temp_db)
    session_b = get_prediction_history(session_id="session-B", db_path=temp_db)
    global_history = get_prediction_history(session_id=None, db_path=temp_db)

    assert session_a["prediction_result"].tolist() == ["session-A"]
    assert session_b["prediction_result"].tolist() == ["session-B"]
    assert set(global_history["prediction_result"]) == {"session-A", "session-B"}
    assert "session_id" in global_history.columns


def test_legacy_prediction_history_database_is_migrated(tmp_path):
    db_file = str(tmp_path / "legacy_datapilot.db")
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            dataset_name TEXT NOT NULL,
            target_col TEXT,
            problem_type TEXT NOT NULL,
            model_name TEXT NOT NULL,
            input_data TEXT NOT NULL,
            prediction_result TEXT NOT NULL,
            confidence REAL
        )
        """
    )
    conn.execute(
        """INSERT INTO prediction_history (
            timestamp, dataset_name, target_col, problem_type, model_name,
            input_data, prediction_result, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ("2025-01-01 00:00:00", "legacy", "target", "Classification", "Model", "{}", "yes", 0.9),
    )
    conn.commit()
    conn.close()

    init_db(db_file)
    init_db(db_file)

    conn = sqlite3.connect(db_file)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(prediction_history)")]
    conn.close()

    assert columns.count("session_id") == 1
    history = get_prediction_history(db_path=db_file)
    assert len(history) == 1
    assert history.iloc[0]["prediction_result"] == "yes"
    assert history.iloc[0]["session_id"] is None
