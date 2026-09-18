"""Evaluation Engine for Machine Learning Models in DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    davies_bouldin_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)


def evaluate_classification_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    classes: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Computes comprehensive classification metrics with robust handling of multiclass and edge cases."""
    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    prec_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    cm_list = cm.tolist()

    # ROC AUC computation where probabilities exist
    roc_auc = None
    if y_prob is not None:
        try:
            n_classes = len(np.unique(y_true))
            if n_classes == 2:
                # Binary: y_prob could be 1D or 2D
                prob_vec = y_prob[:, 1] if y_prob.ndim == 2 else y_prob
                roc_auc = float(roc_auc_score(y_true, prob_vec))
            elif n_classes > 2 and y_prob.ndim == 2:
                roc_auc = float(roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro"))
        except Exception:
            roc_auc = None

    metrics = {
        "Accuracy": round(acc, 4),
        "Precision (Macro)": round(prec_macro, 4),
        "Recall (Macro)": round(rec_macro, 4),
        "F1-Score (Macro)": round(f1_macro, 4),
        "Precision (Weighted)": round(prec_weighted, 4),
        "Recall (Weighted)": round(rec_weighted, 4),
        "F1-Score (Weighted)": round(f1_weighted, 4),
        "ROC-AUC": round(roc_auc, 4) if roc_auc is not None else None,
        "confusion_matrix": cm_list,
        "classes": [str(c) for c in classes] if classes is not None else [str(c) for c in np.unique(y_true)],
    }

    return metrics


def evaluate_regression_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_features: int = 1,
) -> Dict[str, Any]:
    """Computes regression metrics: MAE, MSE, RMSE, R2, and Adjusted R2."""
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))

    # Adjusted R-squared: 1 - [(1 - R2) * (n - 1) / (n - k - 1)]
    n = len(y_true)
    k = n_features
    if n - k - 1 > 0:
        adj_r2 = float(1.0 - (1.0 - r2) * (n - 1) / (n - k - 1))
    else:
        adj_r2 = r2

    metrics = {
        "MAE": round(mae, 4),
        "MSE": round(mse, 4),
        "RMSE": round(rmse, 4),
        "R²": round(r2, 4),
        "Adjusted R²": round(adj_r2, 4),
    }

    return metrics


def evaluate_clustering_model(X: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
    """Evaluates unsupervised clustering quality using Silhouette and Davies-Bouldin metrics."""
    n_clusters = len(np.unique(labels))
    if n_clusters <= 1 or n_clusters >= len(X):
        return {"error": "Silhouette score is undefined for <2 clusters or singleton clusters."}

    # Sample if X is very large to compute silhouette within 1 second
    sample_size = min(3000, len(X))
    sil = float(silhouette_score(X, labels, sample_size=sample_size, random_state=42))
    db = float(davies_bouldin_score(X, labels))

    return {
        "Silhouette Score": round(sil, 4),
        "Davies-Bouldin Index": round(db, 4),
        "n_clusters": n_clusters,
    }


def get_metric_definitions() -> Dict[str, str]:
    """Student-friendly explanations of all evaluation metrics."""
    return {
        "Accuracy": "Ratio of correct predictions to total cases. Can be misleading in heavily imbalanced classes.",
        "Precision": "Out of all instances predicted as positive, how many were actually positive? Focuses on minimizing False Positives.",
        "Recall": "Out of all actual positive instances, how many did the model capture? Focuses on minimizing False Negatives.",
        "F1-Score": "Harmonic mean of Precision and Recall. The gold standard for balanced model ranking under class imbalance.",
        "ROC-AUC": "Area Under the ROC Curve. Measures discriminatory ranking ability across all possible classification thresholds.",
        "MAE": "Mean Absolute Error: Average absolute difference between predicted and actual values. Intuitive and robust to extreme outliers.",
        "RMSE": "Root Mean Squared Error: Square root of average squared errors. Heavily penalizes large prediction errors.",
        "R²": "Coefficient of Determination: Proportion of variance in target explained by input features (1.0 is a perfect fit).",
        "Silhouette Score": "Measures how similar an observation is to its own cluster compared to neighboring clusters (-1 to +1).",
    }
