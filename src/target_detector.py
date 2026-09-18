"""Intelligent Target Column Detection Engine for DataPilot AI."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import pandas as pd


TARGET_KEYWORD_PATTERNS = [
    (r"\btarget\b", 1.0),
    (r"\blabel\b", 0.95),
    (r"\bclass\b", 0.90),
    (r"\bchurn\b", 0.95),
    (r"\bsurvived\b", 0.95),
    (r"\boutcome\b", 0.90),
    (r"\bstatus\b", 0.75),
    (r"\bdiagnosis\b", 0.90),
    (r"\bprice\b", 0.85),
    (r"\bsales\b", 0.85),
    (r"\brevenue\b", 0.85),
    (r"\bdefault\b", 0.90),
    (r"\bfraud\b", 0.90),
    (r"\brating\b", 0.75),
    (r"\bcategory\b", 0.70),
    (r"\bscore\b", 0.75),
    (r"\bsalary\b", 0.80),
    (r"\bincome\b", 0.80),
    (r"\bcost\b", 0.75),
]


def detect_target_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyzes column naming, position, and cardinality to rank target candidates."""
    if df.empty or len(df.columns) == 0:
        return {"suggested_target": None, "confidence": 0.0, "reason": "Empty dataset", "ranked_candidates": []}

    candidates: List[Dict[str, Any]] = []
    total_cols = len(df.columns)
    total_rows = len(df)

    for idx, col in enumerate(df.columns):
        score = 0.0
        reasons: List[str] = []
        col_str = str(col).lower().strip()

        # 1. Semantic keyword matching
        for pattern, weight in TARGET_KEYWORD_PATTERNS:
            if re.search(pattern, col_str):
                score += weight * 0.50
                reasons.append(f"Name matches standard target pattern '{pattern.strip(chr(92)+'b')}'")
                break

        # 2. Position bias (last column is very frequently target in tabular ML benchmarks)
        if idx == total_cols - 1:
            score += 0.25
            reasons.append("Located at final column index")
        elif idx == total_cols - 2:
            score += 0.10

        # 3. Cardinality properties
        n_unique = df[col].nunique(dropna=True)
        if n_unique == 2:
            score += 0.20
            reasons.append("Binary cardinality (exactly 2 unique classes)")
        elif 3 <= n_unique <= 10:
            score += 0.10
            reasons.append(f"Low distinct classes ({n_unique} unique values)")

        # Penalize obvious ID or constant columns
        if n_unique <= 1:
            score = 0.0
            reasons = ["Zero variance constant column"]
        elif n_unique == total_rows and total_rows > 30 and ("id" in col_str or "uuid" in col_str):
            score = 0.0
            reasons = ["Identified as unique identifier key"]

        score = min(1.0, round(score, 2))
        candidates.append({
            "column": col,
            "score": score,
            "reasons": reasons,
            "unique_values": n_unique,
            "dtype": str(df[col].dtype),
        })

    # Sort descending by score
    candidates.sort(key=lambda x: x["score"], reverse=True)

    best = candidates[0] if candidates else None
    if best and best["score"] >= 0.25:
        suggested_target = best["column"]
        confidence = best["score"]
        reason = "; ".join(best["reasons"])
    else:
        # Fallback to last column if no candidate triggered keywords
        suggested_target = df.columns[-1]
        confidence = 0.20
        reason = "Heuristic fallback to the dataset's final column"

    return {
        "suggested_target": suggested_target,
        "confidence": confidence,
        "reason": reason,
        "ranked_candidates": candidates,
    }
