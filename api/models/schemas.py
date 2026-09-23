"""Pydantic schemas and typed models for DataPilot AI API."""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[str] = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ApiError] = None


class TargetUpdateRequest(BaseModel):
    session_id: str
    target_col: Optional[str] = None
    problem_type: Optional[str] = None


class CleanRequest(BaseModel):
    session_id: str
    drop_duplicates: bool = True
    impute_missing: bool = True
    numeric_strategy: str = "median"
    categorical_strategy: str = "mode"
    remove_constant: bool = True


class EdaDistributionRequest(BaseModel):
    session_id: str
    column: str


class EdaScatterRequest(BaseModel):
    session_id: str
    x_col: str
    y_col: str
    color_col: Optional[str] = None


class HypothesisTestRequest(BaseModel):
    session_id: str
    col1: str
    col2: str
    test_type: Optional[str] = "auto"


class TrainRequest(BaseModel):
    session_id: str
    target_col: Optional[str] = None
    problem_type: Optional[str] = None
    test_size: float = 0.20
    cv_folds: int = 3


class SinglePredictRequest(BaseModel):
    session_id: str
    features: Dict[str, Any]


class ChatRequest(BaseModel):
    session_id: str
    message: str
