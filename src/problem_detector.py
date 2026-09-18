"""Problem Type Detection Engine for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def detect_problem_type(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Any]:
    """Infers machine learning problem formulation (Classification, Regression, Unsupervised)."""
    if not target_col or target_col not in df.columns:
        return {
            "problem_type": "Unsupervised Analysis",
            "subtype": "Clustering & Dimensionality Reduction",
            "target_column": None,
            "description": "No target variable designated. Automatic transition to unsupervised pattern discovery.",
            "recommended_metrics": ["Silhouette Score", "Davies-Bouldin Index", "Inertia (Elbow)"],
            "classes": [],
            "class_counts": {},
            "class_proportions": {},
            "is_imbalanced": False,
        }

    series = df[target_col].dropna()
    total_valid = len(series)
    if total_valid == 0:
        return {
            "problem_type": "Invalid",
            "subtype": "All-Missing Target",
            "target_column": target_col,
            "description": f"Target column '{target_col}' has 100% missing values.",
            "recommended_metrics": [],
        }

    n_unique = int(series.nunique())

    if n_unique == 1:
        return {
            "problem_type": "Invalid",
            "subtype": "Single-Class Target",
            "target_column": target_col,
            "description": f"Target column '{target_col}' has only 1 unique value. Machine learning requires variance.",
            "recommended_metrics": [],
        }

    is_numeric = pd.api.types.is_numeric_dtype(series)

    # 1. Binary Classification
    if n_unique == 2:
        val_counts = series.value_counts()
        proportions = (val_counts / total_valid).to_dict()
        min_prop = min(proportions.values())
        is_imbalanced = min_prop < 0.20

        return {
            "problem_type": "Binary Classification",
            "subtype": "Binary",
            "target_column": target_col,
            "n_classes": 2,
            "classes": [str(k) for k in val_counts.index],
            "class_counts": {str(k): int(v) for k, v in val_counts.items()},
            "class_proportions": {str(k): round(float(v), 3) for k, v in proportions.items()},
            "is_imbalanced": is_imbalanced,
            "description": f"Binary target with classes {list(val_counts.index)}. {'Class imbalance detected.' if is_imbalanced else 'Balanced classes.'}",
            "recommended_metrics": ["Accuracy", "F1-Score", "ROC-AUC", "Precision", "Recall"],
        }

    # 2. Multiclass Classification
    if not is_numeric or n_unique <= 15:
        val_counts = series.value_counts()
        proportions = (val_counts / total_valid).to_dict()
        min_prop = min(proportions.values())

        return {
            "problem_type": "Multiclass Classification",
            "subtype": "Multiclass",
            "target_column": target_col,
            "n_classes": n_unique,
            "classes": [str(k) for k in val_counts.index],
            "class_counts": {str(k): int(v) for k, v in val_counts.items()},
            "class_proportions": {str(k): round(float(v), 3) for k, v in proportions.items()},
            "is_imbalanced": min_prop < (1.0 / (n_unique * 2)),
            "description": f"Categorical target with {n_unique} distinct classes.",
            "recommended_metrics": ["Accuracy", "Macro F1", "Weighted F1", "Precision", "Recall"],
        }

    # 3. Continuous Regression
    return {
        "problem_type": "Regression",
        "subtype": "Continuous",
        "target_column": target_col,
        "n_unique": n_unique,
        "mean": round(float(series.mean()), 4),
        "std": round(float(series.std()), 4),
        "min": round(float(series.min()), 4),
        "max": round(float(series.max()), 4),
        "description": f"Continuous numeric target ranging from {round(float(series.min()), 2)} to {round(float(series.max()), 2)}.",
        "recommended_metrics": ["MAE", "MSE", "RMSE", "R²", "Adjusted R²"],
    }
