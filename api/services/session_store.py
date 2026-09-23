"""Session store for caching active dataset sessions in DataPilot AI."""

from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional
import pandas as pd


class SessionData:
    def __init__(self, session_id: str, df: pd.DataFrame, filename: str):
        self.session_id: str = session_id
        self.raw_df: pd.DataFrame = df
        self.cleaned_df: Optional[pd.DataFrame] = None
        self.filename: str = filename
        self.profile_data: Optional[Dict[str, Any]] = None
        self.quality_data: Optional[Dict[str, Any]] = None
        self.target_info: Optional[Dict[str, Any]] = None
        self.target_col: Optional[str] = None
        self.problem_type: Optional[str] = None
        self.ml_results: Optional[Dict[str, Any]] = None
        self.best_model_obj: Any = None
        self.insights_data: Optional[Dict[str, Any]] = None
        self.chat_messages: list = [
            {
                "role": "assistant",
                "content": "Hello! I am your Autonomous AI Data Scientist. I can answer questions about data quality, distributions, model performance, or business recommendations.",
            }
        ]
        self.created_at: float = time.time()
        self.updated_at: float = time.time()

    @property
    def active_df(self) -> pd.DataFrame:
        """Returns the cleaned dataframe if available, otherwise raw dataframe."""
        return self.cleaned_df if self.cleaned_df is not None else self.raw_df


class SessionManager:
    """Manages active dataset sessions in memory."""

    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def create_session(self, df: pd.DataFrame, filename: str, session_id: Optional[str] = None) -> SessionData:
        sid = session_id or str(uuid.uuid4())
        session = SessionData(session_id=sid, df=df, filename=filename)
        self._sessions[sid] = session
        # Keep maximum 20 recent sessions in memory to prevent memory leaks
        if len(self._sessions) > 20:
            oldest_sid = min(self._sessions.keys(), key=lambda k: self._sessions[k].updated_at)
            del self._sessions[oldest_sid]
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        session = self._sessions.get(session_id)
        if session:
            session.updated_at = time.time()
        return session

    def get_or_create_default(self) -> Optional[SessionData]:
        """Returns the most recently updated session if exists."""
        if not self._sessions:
            return None
        latest_sid = max(self._sessions.keys(), key=lambda k: self._sessions[k].updated_at)
        return self._sessions[latest_sid]


# Singleton instance
session_manager = SessionManager()
