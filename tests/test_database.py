"""Unit tests for SQLite prediction history database."""

import os
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
