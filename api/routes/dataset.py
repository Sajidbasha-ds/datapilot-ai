"""Dataset management, profiling, quality, and cleaning routes."""

from __future__ import annotations

import io
import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import pandas as pd

from api.models.schemas import ApiResponse, CleanRequest, TargetUpdateRequest
from api.services.session_store import session_manager
from api.utils.serialization import sanitize_for_json
from src.cleaner import analyze_data_quality, clean_dataset
from src.data_loader import load_dataset
from src.problem_detector import detect_problem_type
from src.profiler import profile_dataset
from src.target_detector import detect_target_column

router = APIRouter(prefix="/dataset", tags=["dataset"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE_DIR = os.path.join(BASE_DIR, "data", "sample")


def _process_dataset(df: pd.DataFrame, filename: str, session_id: Optional[str] = None):
    """Processes DataFrame: profiles, detects quality, detects target and problem type."""
    prof = profile_dataset(df)
    target_info = detect_target_column(df)
    suggested_target = target_info.get("suggested_target")

    problem_type_info = None
    problem_type_str = None
    if suggested_target and suggested_target in df.columns:
        problem_type_info = detect_problem_type(df, suggested_target)
        problem_type_str = problem_type_info.get("problem_type")
    else:
        problem_type_str = "Unsupervised Analysis"

    quality_data = analyze_data_quality(df, target_col=suggested_target)

    session = session_manager.create_session(df=df, filename=filename, session_id=session_id)
    session.profile_data = prof
    session.quality_data = quality_data
    session.target_info = target_info
    session.target_col = suggested_target
    session.problem_type = problem_type_str
    session.problem_type_info = problem_type_info

    preview_rows = df.head(50).to_dict(orient="records")

    return {
        "session_id": session.session_id,
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "profile": prof,
        "quality": quality_data,
        "target_info": target_info,
        "target_col": suggested_target,
        "problem_type": problem_type_str,
        "problem_type_info": problem_type_info,
        "preview": preview_rows,
    }


@router.get("/samples")
def get_sample_datasets():
    """Lists available sample datasets."""
    samples = [
        {
            "id": "customer_churn",
            "name": "Customer Churn",
            "description": "Telco customer churn dataset with demographics, account info, and services. Ideal for binary classification.",
            "target": "Churn",
            "task": "Binary Classification",
            "filename": "customer_churn.csv",
        },
        {
            "id": "house_prices",
            "name": "House Prices",
            "description": "Residential home sale prices with physical property features and square footage. Ideal for regression.",
            "target": "SalePrice",
            "task": "Regression",
            "filename": "house_prices.csv",
        },
        {
            "id": "student_performance",
            "name": "Student Performance",
            "description": "Student academic performance dataset with demographics and study hours. Ideal for multi-class classification or regression.",
            "target": "GradeClass",
            "task": "Multi-Class Classification",
            "filename": "student_performance.csv",
        },
    ]
    return ApiResponse(success=True, data=samples)


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Uploads CSV or XLSX dataset, runs automated profiling and quality audit."""
    allowed_exts = [".csv", ".xlsx", ".xls"]
    filename = file.filename or "uploaded_dataset.csv"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_exts:
        return ApiResponse(
            success=False,
            error={
                "code": "INVALID_FILE_TYPE",
                "message": f"Unsupported file extension '{ext}'. Please upload a .csv or .xlsx file.",
            },
        )

    try:
        content = await file.read()
        file_bytes = io.BytesIO(content)
        df, meta = load_dataset(file_bytes, filename=filename)

        if df.empty or len(df) == 0:
            return ApiResponse(
                success=False,
                error={"code": "EMPTY_DATASET", "message": "The uploaded dataset contains zero rows."},
            )

        data = _process_dataset(df, filename=filename)
        return ApiResponse(success=True, data=sanitize_for_json(data))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "UPLOAD_FAILED", "message": f"Failed to process dataset: {str(e)}"},
        )


@router.get("/sample/{sample_id}")
def load_sample_dataset(sample_id: str):
    """Loads one of the pre-configured sample datasets."""
    sample_files = {
        "customer_churn": "customer_churn.csv",
        "house_prices": "house_prices.csv",
        "student_performance": "student_performance.csv",
    }

    filename = sample_files.get(sample_id)
    if not filename:
        return ApiResponse(
            success=False,
            error={"code": "SAMPLE_NOT_FOUND", "message": f"Sample dataset '{sample_id}' not found."},
        )

    file_path = os.path.join(SAMPLE_DIR, filename)
    if not os.path.exists(file_path):
        return ApiResponse(
            success=False,
            error={"code": "FILE_NOT_FOUND", "message": f"Sample file '{filename}' is missing on server."},
        )

    try:
        df, meta = load_dataset(file_path, filename=filename)
        data = _process_dataset(df, filename=filename)
        return ApiResponse(success=True, data=sanitize_for_json(data))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "LOAD_FAILED", "message": f"Failed to load sample dataset: {str(e)}"},
        )


@router.get("/summary/{session_id}")
def get_dataset_summary(session_id: str):
    """Fetches summary, profiling, and quality details of the active session."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(
            success=False,
            error={"code": "SESSION_NOT_FOUND", "message": "Session expired or dataset not found."},
        )

    df = session.active_df
    preview_rows = df.head(50).to_dict(orient="records")

    data = {
        "session_id": session.session_id,
        "filename": session.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "profile": session.profile_data,
        "quality": session.quality_data,
        "target_info": session.target_info,
        "target_col": session.target_col,
        "problem_type": session.problem_type,
        "is_cleaned": session.cleaned_df is not None,
        "preview": preview_rows,
    }
    return ApiResponse(success=True, data=sanitize_for_json(data))


@router.post("/target")
def update_target(req: TargetUpdateRequest):
    """Updates target column and re-evaluates problem type and data quality."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(
            success=False,
            error={"code": "SESSION_NOT_FOUND", "message": "Session expired or dataset not found."},
        )

    df = session.active_df
    if req.target_col and req.target_col not in df.columns:
        return ApiResponse(
            success=False,
            error={"code": "INVALID_TARGET", "message": f"Column '{req.target_col}' not found in dataset."},
        )

    session.target_col = req.target_col
    if req.target_col:
        prob_info = detect_problem_type(df, req.target_col)
        session.problem_type = req.problem_type or prob_info.get("problem_type")
        session.problem_type_info = prob_info
    else:
        session.problem_type = "Unsupervised Analysis"
        session.problem_type_info = {"problem_type": "Unsupervised Analysis"}

    # Recalculate quality analysis with new target (for leakage candidates)
    session.quality_data = analyze_data_quality(df, target_col=session.target_col)

    # Invalidate stale ML results when target changes
    session.ml_results = None
    session.best_model_obj = None

    return ApiResponse(
        success=True,
        data=sanitize_for_json({
            "target_col": session.target_col,
            "problem_type": session.problem_type,
            "quality": session.quality_data,
        }),
    )


@router.post("/clean")
def run_clean_pipeline(req: CleanRequest):
    """Executes non-destructive data cleaning based on requested parameters."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(
            success=False,
            error={"code": "SESSION_NOT_FOUND", "message": "Session expired or dataset not found."},
        )

    try:
        cleaned_df, logs = clean_dataset(
            df=session.raw_df,
            drop_duplicates=req.drop_duplicates,
            drop_constant_cols=req.remove_constant,
            impute_missing=req.impute_missing,
        )

        session.cleaned_df = cleaned_df
        session.profile_data = profile_dataset(cleaned_df)
        session.quality_data = analyze_data_quality(cleaned_df, target_col=session.target_col)

        # Invalidate stale models
        session.ml_results = None
        session.best_model_obj = None

        preview_rows = cleaned_df.head(50).to_dict(orient="records")

        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "logs": logs,
                "rows": len(cleaned_df),
                "columns": len(cleaned_df.columns),
                "profile": session.profile_data,
                "quality": session.quality_data,
                "preview": preview_rows,
            }),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "CLEANING_FAILED", "message": f"Cleaning failed: {str(e)}"},
        )
