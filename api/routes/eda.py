"""Exploratory Data Analysis (EDA) routes."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
import numpy as np
import pandas as pd

from api.models.schemas import ApiResponse, EdaDistributionRequest, EdaScatterRequest
from api.services.session_store import session_manager
from api.utils.serialization import sanitize_for_json
from src.eda import (
    plot_categorical_frequency,
    plot_correlation_heatmap,
    plot_numerical_distribution,
    plot_scatter_relationship,
)

router = APIRouter(prefix="/eda", tags=["eda"])


@router.get("/options/{session_id}")
def get_eda_options(session_id: str):
    """Returns available numerical, categorical, and target columns for chart selectors."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols and c not in dt_cols]

    return ApiResponse(
        success=True,
        data={
            "numerical_columns": num_cols,
            "categorical_columns": cat_cols,
            "datetime_columns": dt_cols,
            "all_columns": list(df.columns),
            "target_col": session.target_col,
            "problem_type": session.problem_type,
        },
    )


@router.post("/distribution")
def get_distribution(req: EdaDistributionRequest):
    """Generates distribution data and Plotly figure for a column."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    if req.column not in df.columns:
        return ApiResponse(
            success=False,
            error={"code": "COLUMN_NOT_FOUND", "message": f"Column '{req.column}' does not exist."},
        )

    is_numeric = pd.api.types.is_numeric_dtype(df[req.column])
    try:
        if is_numeric:
            fig = plot_numerical_distribution(df, req.column)
            # Generate summary metrics
            clean_series = df[req.column].dropna()
            summary = {
                "mean": round(float(clean_series.mean()), 3) if not clean_series.empty else None,
                "median": round(float(clean_series.median()), 3) if not clean_series.empty else None,
                "std": round(float(clean_series.std()), 3) if len(clean_series) > 1 else None,
                "min": round(float(clean_series.min()), 3) if not clean_series.empty else None,
                "max": round(float(clean_series.max()), 3) if not clean_series.empty else None,
            }
        else:
            fig = plot_categorical_frequency(df, req.column)
            counts = df[req.column].astype(str).value_counts().head(10).to_dict()
            summary = {"top_categories": counts, "unique_count": int(df[req.column].nunique())}

        plotly_spec = json.loads(fig.to_json())
        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "column": req.column,
                "is_numeric": is_numeric,
                "summary": summary,
                "plotly": plotly_spec,
            }),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "DISTRIBUTION_FAILED", "message": f"Failed to plot distribution: {str(e)}"},
        )


@router.get("/correlation/{session_id}")
def get_correlation(session_id: str):
    """Computes correlation heatmap figure and matrix data."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(num_cols) < 2:
        return ApiResponse(
            success=False,
            error={
                "code": "INSUFFICIENT_NUMERICAL_COLS",
                "message": "At least 2 numerical columns are required for a correlation matrix.",
            },
        )

    try:
        corr_matrix = df[num_cols].corr().round(3)
        fig = plot_correlation_heatmap(df)
        plotly_spec = json.loads(fig.to_json()) if fig else None

        # Format matrix for UI table
        matrix_data = []
        for col1 in num_cols:
            row = {"feature": col1}
            for col2 in num_cols:
                row[col2] = float(corr_matrix.loc[col1, col2]) if not pd.isna(corr_matrix.loc[col1, col2]) else 0.0
            matrix_data.append(row)

        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "columns": num_cols,
                "matrix": matrix_data,
                "plotly": plotly_spec,
            }),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "CORRELATION_FAILED", "message": f"Failed to compute correlation: {str(e)}"},
        )


@router.post("/scatter")
def get_scatter(req: EdaScatterRequest):
    """Generates scatter relationship plot and data between two features."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    if req.x_col not in df.columns or req.y_col not in df.columns:
        return ApiResponse(
            success=False,
            error={"code": "INVALID_COLUMNS", "message": "Specified columns do not exist in dataset."},
        )

    color_col = req.color_col if (req.color_col and req.color_col in df.columns) else session.target_col
    try:
        fig = plot_scatter_relationship(df, x_col=req.x_col, y_col=req.y_col, color_col=color_col)
        plotly_spec = json.loads(fig.to_json())
        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "x_col": req.x_col,
                "y_col": req.y_col,
                "color_col": color_col,
                "plotly": plotly_spec,
            }),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "SCATTER_FAILED", "message": f"Failed to generate scatter plot: {str(e)}"},
        )
