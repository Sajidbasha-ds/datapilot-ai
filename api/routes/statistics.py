"""Statistical analysis routes for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
import numpy as np
import pandas as pd

from api.models.schemas import ApiResponse, HypothesisTestRequest
from api.services.session_store import session_manager
from api.utils.serialization import sanitize_for_json
from src.statistics import (
    compute_descriptive_stats,
    compute_pairwise_correlation_with_pvalues,
    run_hypothesis_test,
)

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/descriptive/{session_id}")
def get_descriptive_statistics(session_id: str):
    """Calculates comprehensive descriptive statistics for all numerical features."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    try:
        stats_df = compute_descriptive_stats(df)
        records = stats_df.to_dict(orient="records") if not stats_df.empty else []
        return ApiResponse(success=True, data=sanitize_for_json(records))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "STATS_FAILED", "message": f"Failed to compute descriptive statistics: {str(e)}"},
        )


@router.get("/pairwise/{session_id}")
def get_pairwise_correlation(
    session_id: str,
    col_x: str = Query(...),
    col_y: str = Query(...),
):
    """Calculates Pearson and Spearman correlation with p-values and scientific interpretations."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    if col_x not in df.columns or col_y not in df.columns:
        return ApiResponse(
            success=False,
            error={"code": "INVALID_COLUMNS", "message": "One or both selected columns not in dataset."},
        )

    try:
        res = compute_pairwise_correlation_with_pvalues(df, col_x=col_x, col_y=col_y)
        if "error" in res:
            return ApiResponse(success=False, error={"code": "INSUFFICIENT_DATA", "message": res["error"]})
        return ApiResponse(success=True, data=sanitize_for_json(res))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "CORRELATION_ERROR", "message": f"Failed to compute pairwise correlation: {str(e)}"},
        )


@router.post("/hypothesis")
def execute_hypothesis_test(req: HypothesisTestRequest):
    """Executes parametric and non-parametric hypothesis tests."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    if req.col1 not in df.columns or req.col2 not in df.columns:
        return ApiResponse(
            success=False,
            error={"code": "INVALID_COLUMNS", "message": "Selected columns do not exist."},
        )

    test_type = req.test_type or "auto"
    col1_numeric = pd.api.types.is_numeric_dtype(df[req.col1])
    col2_numeric = pd.api.types.is_numeric_dtype(df[req.col2])

    # Determine automatic test type if requested
    if test_type == "auto":
        if col1_numeric and not col2_numeric and df[req.col2].nunique() == 2:
            test_type = "Two-Sample T-Test"
        elif col1_numeric and not col2_numeric and df[req.col2].nunique() > 2:
            test_type = "One-Way ANOVA"
        elif not col1_numeric and not col2_numeric:
            test_type = "Chi-Square Test of Independence"
        elif col1_numeric and col2_numeric:
            test_type = "Pearson Correlation Test"
        else:
            test_type = "Two-Sample T-Test"

    try:
        res = run_hypothesis_test(df, test_type=test_type, var1=req.col1, var2=req.col2)
        if "error" in res:
            return ApiResponse(success=False, error={"code": "TEST_ERROR", "message": res["error"]})
        return ApiResponse(success=True, data=sanitize_for_json(res))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "TEST_FAILED", "message": f"Hypothesis test failed: {str(e)}"},
        )
