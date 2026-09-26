"""Machine Learning experimentation and training routes for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
import numpy as np
import pandas as pd

from api.models.schemas import ApiResponse, TrainRequest
from api.services.session_store import session_manager
from api.utils.serialization import sanitize_for_json
from src.evaluator import get_metric_definitions
from src.model_selector import get_model_descriptions
from src.model_trainer import train_supervised_models, train_unsupervised_models
from src.problem_detector import detect_problem_type

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/train")
def train_pipeline(req: TrainRequest):
    """Runs split-first training, cross-validation, and model benchmarking."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    df = session.active_df
    target_col = req.target_col or session.target_col

    # Check if target is required
    is_unsupervised = (
        req.problem_type == "Unsupervised Analysis"
        or (not target_col and not session.target_col)
    )

    if not is_unsupervised and not target_col:
        return ApiResponse(
            success=False,
            error={
                "code": "MISSING_TARGET",
                "message": "A target column must be selected for supervised model training.",
            },
        )

    try:
        if is_unsupervised:
            res = train_unsupervised_models(df, random_state=42)
            session.ml_results = res
            session.best_model_obj = res.get("fitted_kmeans")
            session.problem_type = "Unsupervised Analysis"

            # Prepare elbow table & cluster counts
            elbow_records = res["elbow_df"].to_dict(orient="records") if "elbow_df" in res else []
            pca_data = []
            if "pca_coords" in res:
                coords = res["pca_coords"]
                labels = res["cluster_labels"]
                for i in range(min(500, len(coords))):
                    pca_data.append({
                        "pca_1": round(float(coords[i, 0]), 4),
                        "pca_2": round(float(coords[i, 1]), 4),
                        "cluster": f"Cluster {labels[i]}",
                    })

            data = {
                "problem_type": "Unsupervised Analysis",
                "best_k": res["best_k"],
                "elbow_table": elbow_records,
                "pca_variance": res.get("pca_variance", []),
                "pca_points": pca_data,
                "features_used": res.get("features_used", []),
            }
            return ApiResponse(success=True, data=sanitize_for_json(data))

        # Supervised Training
        problem_type = req.problem_type or session.problem_type or detect_problem_type(df, target_col)
        session.problem_type = problem_type
        session.target_col = target_col

        train_res = train_supervised_models(
            df=df,
            target_col=target_col,
            problem_type=problem_type,
            test_size=req.test_size,
            cv_folds=req.cv_folds,
            random_state=42,
        )

        session.ml_results = train_res
        session.best_model_obj = train_res["best_model_pipeline"]

        # Parse results dataframe
        results_df = train_res["results_df"]
        leaderboard = results_df.to_dict(orient="records") if isinstance(results_df, pd.DataFrame) else []

        best_model_name = train_res["best_model_name"]
        feature_importances = train_res.get("feature_importances", {})
        top_features = feature_importances.get(best_model_name, {})
        top_attributions = train_res.get("feature_attributions", {}).get(best_model_name, [])

        n_train = train_res.get(
            "n_train",
            train_res.get("train_rows", 0),
        )

        n_test = train_res.get(
            "n_test",
            train_res.get("test_rows", 0),
        )

        # Reliability Assessment
        reliability_warning = None
        if n_test < 25:
            reliability_warning = (
                f"Small evaluation set: hold-out test metrics are computed on only {n_test} observations. "
                "Treat test performance as an initial estimate rather than a definitive guarantee of generalization."
            )

        data = {
            "target_col": target_col,
            "problem_type": problem_type,
            "best_model_name": best_model_name,
            "leaderboard": leaderboard,
            "feature_importance": [
                {
                    **item,
                    "importance": item["value"],
                }
                for item in top_attributions
            ] if top_attributions else [
                {"feature": k, "importance": v} for k, v in top_features.items()
            ],
            "feature_attributions": top_attributions,
            "all_feature_importances": feature_importances,
            "all_feature_attributions": train_res.get("feature_attributions", {}),
            "n_train": n_train,
            "n_test": n_test,
            "test_size": req.test_size,
            "cv_folds": req.cv_folds,
            "reliability_warning": reliability_warning,
            "metric_definitions": get_metric_definitions(),
            "model_descriptions": get_model_descriptions(),
        }

        return ApiResponse(success=True, data=sanitize_for_json(data))

    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "TRAINING_FAILED", "message": f"ML training failed: {str(e)}"},
        )


@router.get("/results/{session_id}")
def get_ml_results(session_id: str):
    """Retrieves cached benchmark and model results for active session."""
    session = session_manager.get_session(session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    if not session.ml_results:
        return ApiResponse(
            success=False,
            error={"code": "NO_MODELS_TRAINED", "message": "No machine learning benchmark has been run yet."},
        )

    res = session.ml_results
    if "best_k" in res:  # Unsupervised
        elbow_records = res["elbow_df"].to_dict(orient="records") if "elbow_df" in res else []
        return ApiResponse(
            success=True,
            data=sanitize_for_json({
                "problem_type": "Unsupervised Analysis",
                "best_k": res["best_k"],
                "elbow_table": elbow_records,
                "pca_variance": res.get("pca_variance", []),
                "features_used": res.get("features_used", []),
            }),
        )

    results_df = res["results_df"]
    leaderboard = results_df.to_dict(orient="records") if isinstance(results_df, pd.DataFrame) else []
    best_model_name = res["best_model_name"]
    top_features = res.get("feature_importances", {}).get(best_model_name, {})
    top_attributions = res.get("feature_attributions", {}).get(best_model_name, [])

    n_train = res.get(
    "n_train",
    res.get("train_rows", 0),
    )

    n_test = res.get(
         "n_test",
         res.get("test_rows", 0),
    )

    reliability_warning = None
    if n_test < 25:
        reliability_warning = (
            f"Small evaluation set: hold-out test metrics are computed on only {n_test} observations. "
            "Treat test performance as an initial estimate rather than a definitive guarantee of generalization."
        )

    data = {
        "target_col": session.target_col,
        "problem_type": session.problem_type,
        "best_model_name": best_model_name,
        "leaderboard": leaderboard,
        "feature_importance": [
            {
                **item,
                "importance": item["value"],
            }
            for item in top_attributions
        ] if top_attributions else [
            {"feature": k, "importance": v} for k, v in top_features.items()
        ],
        "feature_attributions": top_attributions,
        "n_train": n_train,
        "n_test": n_test,
        "reliability_warning": reliability_warning,
        "metric_definitions": get_metric_definitions(),
    }
    return ApiResponse(success=True, data=sanitize_for_json(data))
