"""Data cleaning and JSON serialization utilities."""

from __future__ import annotations

import math
from typing import Any
import numpy as np
import pandas as pd


def sanitize_for_json(obj: Any) -> Any:
    """Recursively converts NaN, Infinity, numpy types, and pandas types to JSON-safe Python primitives."""
    if obj is None:
        return None
    if isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or np.isnan(obj):
            return None
        if math.isinf(obj) or np.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (np.ndarray, pd.Series)):
        return [sanitize_for_json(item) for item in obj.tolist()]
    if isinstance(obj, pd.DataFrame):
        return [sanitize_for_json(row) for row in obj.to_dict(orient="records")]
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(item) for item in obj]
    return str(obj) if not isinstance(obj, (str, int, float, bool)) else obj
