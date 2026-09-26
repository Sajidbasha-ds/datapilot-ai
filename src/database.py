"""SQLite Database Layer for Prediction Audit Logs in DataPilot AI."""

from __future__ import annotations

from datetime import datetime
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd

def _resolve_default_db_path() -> str:
    """Resolves DB path, using /tmp on serverless environments like Vercel/Lambda if needed."""
    if os.environ.get("DATAPILOT_DB_PATH"):
        return os.environ["DATAPILOT_DB_PATH"]
    # Check if running in Vercel or AWS Lambda environment where filesystem is read-only
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "/tmp/datapilot.db"
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "datapilot.db")

DEFAULT_DB_PATH = _resolve_default_db_path()


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Opens a connection to the SQLite database and ensures directories exist with fallback."""
    try:
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(db_path)
    except (OSError, sqlite3.OperationalError):
        # Fallback to /tmp or in-memory on restricted filesystems
        fallback_path = "/tmp/datapilot.db" if os.path.exists("/tmp") else ":memory:"
        conn = sqlite3.connect(fallback_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes the prediction audit trail table if not existing."""

    conn = get_db_connection(db_path)

    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                target_col TEXT,
                problem_type TEXT NOT NULL,
                model_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                prediction_result TEXT NOT NULL,
                confidence REAL,
                session_id TEXT
            )
        """)

        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(prediction_history)"
            ).fetchall()
        }

        if "session_id" not in columns:
            conn.execute(
                "ALTER TABLE prediction_history ADD COLUMN session_id TEXT"
            )

    conn.close()


def log_prediction(
    dataset_name: str,
    target_col: Optional[str],
    problem_type: str,
    model_name: str,
    input_data: Dict[str, Any],
    prediction_result: Any,
    confidence: Optional[float] = None,
    db_path: str = DEFAULT_DB_PATH,
    session_id: Optional[str] = None,
) -> int:
    """Appends an individual inference event into the SQLite audit trail."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    input_json = json.dumps(input_data, default=str)
    pred_str = str(prediction_result)

    with conn:
        cursor = conn.execute(
            """
            INSERT INTO prediction_history (
                timestamp, dataset_name, target_col, problem_type,
                model_name, input_data, prediction_result, confidence, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                dataset_name,
                target_col or "N/A",
                problem_type,
                model_name,
                input_json,
                pred_str,
                confidence,
                session_id,
            ),
        )
        record_id = cursor.lastrowid
    conn.close()
    return int(record_id) if record_id else 0


def get_prediction_history(
    limit: int = 100,
    dataset_name: Optional[str] = None,
    session_id: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Fetches recent prediction records into a structured Pandas DataFrame."""
    init_db(db_path)
    conn = get_db_connection(db_path)

    query = """
    SELECT id, timestamp, dataset_name, target_col, problem_type,
           model_name, input_data, prediction_result, confidence, session_id
    FROM prediction_history
    """
    params: List[Any] = []

    conditions = []

    if dataset_name:
        conditions.append("dataset_name = ?")
        params.append(dataset_name)

    if session_id is not None:
        conditions.append("session_id = ?")
        params.append(session_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


def clear_prediction_history(db_path: str = DEFAULT_DB_PATH) -> int:
    """Purges all records from the prediction audit trail."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    with conn:
        cursor = conn.execute("DELETE FROM prediction_history")
        deleted = cursor.rowcount
    conn.close()
    return int(deleted)
