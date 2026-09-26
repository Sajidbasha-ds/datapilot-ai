"""Inference and prediction routes for single and batch predictions."""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse
import numpy as np
import pandas as pd

from api.models.schemas import ApiResponse, SinglePredictRequest
from api.services.session_store import session_manager
from api.utils.serialization import sanitize_for_json
from src.database import get_prediction_history
from src.predictor import predict_batch, predict_single

router = APIRouter(prefix="/predict", tags=["predict"])


@router.get("/schema/{session_id}")
def get_prediction_schema(session_id: str):
    """Inspects the winning trained pipeline to build dynamic input forms."""
    session = session_manager.get_session(session_id)
    if not session or not session.best_model_obj:
        return ApiResponse(
            success=False,
            error={"code": "NO_MODEL", "message": "Train a model in the ML Lab first before predicting."},
        )

    pipeline = session.best_model_obj
    df = session.active_df
    target_col = session.target_col

    fields = []
    # Identify expected features
    feature_cols = [c for c in df.columns if c != target_col]
    if hasattr(pipeline, "feature_names_in_"):
        feature_cols = list(pipeline.feature_names_in_)

    for col in feature_cols:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        is_num = pd.api.types.is_numeric_dtype(series)

        if is_num:
            fields.append({
                "name": col,
                "type": "number",
                "default": float(series.median()) if not series.empty else 0.0,
                "min": float(series.min()) if not series.empty else 0.0,
                "max": float(series.max()) if not series.empty else 100.0,
            })
        else:
            categories = series.astype(str).unique().tolist()[:25]
            default_cat = series.mode().iloc[0] if not series.empty else (categories[0] if categories else "")
            fields.append({
                "name": col,
                "type": "select",
                "default": str(default_cat),
                "options": categories,
            })

    best_name = session.ml_results.get("best_model_name", "Winning Model") if session.ml_results else "Model"

    return ApiResponse(
        success=True,
        data=sanitize_for_json({
            "model_name": best_name,
            "target_col": target_col,
            "problem_type": session.problem_type,
            "fields": fields,
        }),
    )


@router.post("/single")
def run_single_prediction(req: SinglePredictRequest):
    """Scores a single record and logs prediction to the audit trail."""
    session = session_manager.get_session(req.session_id)
    if not session or not session.best_model_obj:
        return ApiResponse(
            success=False,
            error={"code": "NO_MODEL", "message": "Train a model in the ML Lab first before predicting."},
        )

    try:
        best_name = session.ml_results.get("best_model_name", "Winning Model") if session.ml_results else "Model"
        pred_res = predict_single(
            pipeline=session.best_model_obj,
            input_dict=req.features,
            problem_type=session.problem_type or "Classification",
            dataset_name=session.filename,
            target_col=session.target_col,
            model_name=best_name,
            session_id=req.session_id,
        )
        return ApiResponse(success=True, data=sanitize_for_json(pred_res))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "PREDICTION_FAILED", "message": f"Prediction failed: {str(e)}"},
        )


@router.post("/batch")
async def run_batch_prediction(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Executes batch predictions on uploaded CSV and returns preview + download token."""
    session = session_manager.get_session(session_id)
    if not session or not session.best_model_obj:
        return ApiResponse(
            success=False,
            error={"code": "NO_MODEL", "message": "Train a model in the ML Lab first before predicting."},
        )

    pipeline = session.best_model_obj
    target_col = session.target_col
    expected_features = [c for c in session.active_df.columns if c != target_col]
    if hasattr(pipeline, "feature_names_in_"):
        expected_features = list(pipeline.feature_names_in_)

    try:
        content = await file.read()
        batch_df = pd.read_csv(io.BytesIO(content))

        # Check required columns
        missing = [c for c in expected_features if c not in batch_df.columns]
        if missing:
            return ApiResponse(
                success=False,
                error={
                    "code": "MISSING_COLUMNS",
                    "message": f"Uploaded batch file is missing required columns: {', '.join(missing[:5])}",
                },
            )

        best_name = session.ml_results.get("best_model_name", "Winning Model") if session.ml_results else "Model"
        scored_df, metrics = predict_batch(
            pipeline=pipeline,
            batch_df=batch_df,
            required_features=expected_features,
            problem_type=session.problem_type or "Classification",
            dataset_name=session.filename,
            target_col=target_col,
            model_name=best_name,
            session_id=session_id,
        )        

        preview_rows = scored_df.head(50).to_dict(orient="records")
        csv_str = scored_df.to_csv(index=False)

        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "total_rows": len(batch_df),
                "summary": metrics,
                "preview": preview_rows,
                "csv_data": csv_str,
            }),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "BATCH_FAILED", "message": f"Batch prediction failed: {str(e)}"},
        )


@router.get("/history")
def get_history(
    limit: int = 50,
    session_id: Optional[str] = None,
):
    """Fetches recent prediction audit records from database."""
    try:
        df = get_prediction_history(
           limit=limit,
           session_id=session_id,
   )
        records = df.to_dict(orient="records") if not df.empty else []
        return ApiResponse(success=True, data=sanitize_for_json(records))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "HISTORY_FAILED", "message": f"Failed to retrieve history: {str(e)}"},
        )
