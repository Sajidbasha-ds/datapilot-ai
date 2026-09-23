"""AI Insights and dataset grounded conversational chatbot routes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
import pandas as pd

from api.models.schemas import ApiResponse, ChatRequest
from api.services.session_store import session_manager
from api.utils.serialization import sanitize_for_json
from src.insights import answer_datapilot_query, generate_automated_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/generate/{session_id}")
def get_automated_insights(session_id: str):
    """Generates executive, technical, and data quality insights grounded in real calculations."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    profile_data = session.profile_data or {}
    quality_data = session.quality_data or {}
    ml_results = session.ml_results

    try:
        insights = generate_automated_insights(
            profile_data=profile_data,
            quality_data=quality_data,
            ml_results=ml_results,
        )
        session.insights_data = insights
        return ApiResponse(success=True, data=sanitize_for_json(insights))
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "INSIGHTS_FAILED", "message": f"Failed to generate insights: {str(e)}"},
        )


@router.post("/chat")
def chat_with_datapilot(req: ChatRequest):
    """Answers conversational questions about the active dataset, quality, and models."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    # Record user message
    session.chat_messages.append({"role": "user", "content": req.message})

    try:
        reply = answer_datapilot_query(
            user_query=req.message,
            profile_data=session.profile_data or {},
            quality_data=session.quality_data or {},
            ml_results=session.ml_results,
        )
        session.chat_messages.append({"role": "assistant", "content": reply})

        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "role": "assistant",
                "content": reply,
                "history": session.chat_messages,
            }),
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "CHAT_FAILED", "message": f"Failed to answer query: {str(e)}"},
        )


@router.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    """Returns conversation history for the session."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    return ApiResponse(success=True, data=session.chat_messages)
