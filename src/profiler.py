"""Automated data profiling engine for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from scipy import stats


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Performs deep profiling of the dataset at dataset-level and column-level."""
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())
    total_cells = total_rows * total_cols
    total_missing = int(df.isna().sum().sum())
    missing_ratio = (total_missing / total_cells) if total_cells > 0 else 0.0

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols and c not in dt_cols]

    columns_profile: List[Dict[str, Any]] = []
    suspicious_columns: List[Dict[str, Any]] = []
    constant_columns: List[str] = []

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        n_unique = int(series.nunique(dropna=True))
        cardinality_ratio = round((n_unique / total_rows), 4) if total_rows > 0 else 0.0

        col_info: Dict[str, Any] = {
            "name": col,
            "dtype": str(series.dtype),
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": n_unique,
            "cardinality_ratio": cardinality_ratio,
        }

        # Check for constant / near-constant
        if n_unique <= 1:
            constant_columns.append(col)
            suspicious_columns.append({
                "column": col,
                "reason": "Constant Column",
                "detail": "Contains only 1 unique value across all rows. Provides zero predictive signal.",
                "severity": "high",
            })
        elif total_rows > 10:
            top_freq = series.value_counts(dropna=True).iloc[0] if n_unique > 0 else 0
            if (top_freq / total_rows) >= 0.99:
                suspicious_columns.append({
                    "column": col,
                    "reason": "Near-Constant Column",
                    "detail": f"{round((top_freq / total_rows) * 100, 1)}% of rows contain the same single value.",
                    "severity": "medium",
                })

        # Check for ID columns
        col_lower = str(col).lower()
        is_id_name = any(k in col_lower for k in ["_id", "id_", "identifier", "uuid", "guid"]) or col_lower in ["id", "index"]
        if is_id_name or (n_unique == total_rows and total_rows > 30 and (col in num_cols or col in cat_cols)):
            suspicious_columns.append({
                "column": col,
                "reason": "Potential ID / Key Column",
                "detail": "100% unique or matches standard ID naming patterns. Likely an identifier rather than a genuine feature.",
                "severity": "high" if is_id_name else "medium",
            })

        # Check high cardinality categorical
        if col in cat_cols and n_unique > 50 and cardinality_ratio > 0.3:
            suspicious_columns.append({
                "column": col,
                "reason": "High-Cardinality Categorical",
                "detail": f"Contains {n_unique} unique categories ({round(cardinality_ratio*100, 1)}% of rows). One-hot encoding may cause dimensionality explosion.",
                "severity": "medium",
            })

        # Numerical specific statistics
        if col in num_cols:
            col_info["type_category"] = "numerical"
            clean_series = series.dropna()
            if not clean_series.empty:
                col_info["mean"] = round(float(clean_series.mean()), 4)
                col_info["std"] = round(float(clean_series.std()), 4) if len(clean_series) > 1 else 0.0
                col_info["median"] = round(float(clean_series.median()), 4)
                col_info["min"] = round(float(clean_series.min()), 4)
                col_info["max"] = round(float(clean_series.max()), 4)
                col_info["q25"] = round(float(clean_series.quantile(0.25)), 4)
                col_info["q75"] = round(float(clean_series.quantile(0.75)), 4)
                col_info["iqr"] = round(col_info["q75"] - col_info["q25"], 4)
                col_info["zeros_count"] = int((clean_series == 0).sum())
                try:
                    col_info["skewness"] = round(float(stats.skew(clean_series, nan_policy="omit")), 3)
                    col_info["kurtosis"] = round(float(stats.kurtosis(clean_series, nan_policy="omit")), 3)
                except Exception:
                    col_info["skewness"] = 0.0
                    col_info["kurtosis"] = 0.0
            else:
                col_info.update({k: None for k in ["mean", "std", "median", "min", "max", "q25", "q75", "iqr", "skewness", "kurtosis", "zeros_count"]})
        elif col in dt_cols:
            col_info["type_category"] = "datetime"
            clean_dt = series.dropna()
            if not clean_dt.empty:
                col_info["min_date"] = str(clean_dt.min())
                col_info["max_date"] = str(clean_dt.max())
            else:
                col_info["min_date"] = None
                col_info["max_date"] = None
        else:
            col_info["type_category"] = "categorical"
            top_vals = series.value_counts(dropna=True).head(5).to_dict()
            col_info["top_categories"] = {str(k): int(v) for k, v in top_vals.items()}
            if len(top_vals) > 0:
                top_item = next(iter(top_vals.items()))
                col_info["most_frequent_value"] = str(top_item[0])
                col_info["most_frequent_count"] = int(top_item[1])
                col_info["most_frequent_pct"] = round((top_item[1] / total_rows) * 100, 2) if total_rows > 0 else 0.0
            else:
                col_info["most_frequent_value"] = None
                col_info["most_frequent_count"] = 0
                col_info["most_frequent_pct"] = 0.0

        columns_profile.append(col_info)

    overview = {
        "rows": total_rows,
        "columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0,
        "total_cells": total_cells,
        "total_missing": total_missing,
        "missing_pct": round(missing_ratio * 100, 2),
        "numerical_columns_count": len(num_cols),
        "categorical_columns_count": len(cat_cols),
        "datetime_columns_count": len(dt_cols),
        "constant_columns": constant_columns,
        "constant_columns_count": len(constant_columns),
        "suspicious_columns": suspicious_columns,
        "suspicious_count": len(suspicious_columns),
    }

    return {
        "overview": overview,
        "columns": columns_profile,
        "numerical_cols": num_cols,
        "categorical_cols": cat_cols,
        "datetime_cols": dt_cols,
    }
