"""Inference Engine for Single and Batch Predictions in DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.database import log_prediction


def predict_single(
    pipeline: Pipeline,
    input_dict: Dict[str, Any],
    problem_type: str,
    dataset_name: str = "custom",
    target_col: Optional[str] = None,
    model_name: str = "Model",
) -> Dict[str, Any]:
    """Generates a prediction for a single user-input record and logs to SQLite."""
    # Convert input dictionary to 1-row DataFrame
    input_df = pd.DataFrame([input_dict])
    if hasattr(pipeline, "feature_names_in_"):
        expected = list(pipeline.feature_names_in_)
        for col in expected:
            if col not in input_df.columns:
                input_df[col] = np.nan
        input_df = input_df[expected]

    try:
        raw_pred = pipeline.predict(input_df)[0]
    except Exception as e:
        raise ValueError(f"Inference error on input sample: {str(e)}")

    confidence = None
    prob_dict = {}

    is_classification = "Classification" in problem_type
    if is_classification and hasattr(pipeline.named_steps.get("model", pipeline), "predict_proba"):
        try:
            model = pipeline.named_steps["model"]
            probabilities = pipeline.predict_proba(input_df)[0]
            classes = model.classes_
            for cls_name, prob in zip(classes, probabilities):
                prob_dict[str(cls_name)] = round(float(prob), 4)
            confidence = round(float(np.max(probabilities)), 4)
        except Exception:
            confidence = None

    # Format output
    if isinstance(raw_pred, (np.floating, float)):
        result = round(float(raw_pred), 4)
    elif isinstance(raw_pred, (np.integer, int)):
        result = int(raw_pred)
    else:
        result = str(raw_pred)

    # Log to SQLite audit trail
    log_id = log_prediction(
        dataset_name=dataset_name,
        target_col=target_col,
        problem_type=problem_type,
        model_name=model_name,
        input_data=input_dict,
        prediction_result=result,
        confidence=confidence,
    )

    return {
        "prediction": result,
        "confidence": confidence,
        "probabilities": prob_dict,
        "log_id": log_id,
    }


def predict_batch(
    pipeline: Pipeline,
    batch_df: pd.DataFrame,
    required_features: List[str],
    problem_type: str,
    dataset_name: str = "batch_upload",
    target_col: Optional[str] = None,
    model_name: str = "Model",
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Scores a batch DataFrame, appends prediction columns, and logs to database."""
    # Verify feature columns exist in uploaded batch
    missing_cols = [col for col in required_features if col not in batch_df.columns]
    if missing_cols:
        raise ValueError(f"Batch dataset is missing required features: {missing_cols}")

    working_batch = batch_df[required_features].copy()

    try:
        predictions = pipeline.predict(working_batch)
    except Exception as e:
        raise ValueError(f"Failed to execute batch predictions: {str(e)}")

    output_df = batch_df.copy()
    pred_col_name = f"Predicted_{target_col or 'Outcome'}"
    output_df[pred_col_name] = predictions

    confidences = None
    is_classification = "Classification" in problem_type
    if is_classification and hasattr(pipeline.named_steps.get("model", pipeline), "predict_proba"):
        try:
            probs = pipeline.predict_proba(working_batch)
            confidences = np.max(probs, axis=1)
            output_df["Prediction_Confidence"] = np.round(confidences, 4)
        except Exception:
            pass

    # Log batch summary to SQLite (first row as sample)
    if len(output_df) > 0:
        sample_input = working_batch.iloc[0].to_dict()
        sample_pred = predictions[0]
        sample_conf = float(confidences[0]) if confidences is not None else None
        log_prediction(
            dataset_name=f"{dataset_name} (Batch: {len(output_df)} rows)",
            target_col=target_col,
            problem_type=problem_type,
            model_name=model_name,
            input_data=sample_input,
            prediction_result=f"Batch generated ({len(output_df)} records)",
            confidence=sample_conf,
        )

    summary = {
        "total_rows_scored": len(output_df),
        "prediction_column": pred_col_name,
        "has_confidence": confidences is not None,
    }

    return output_df, summary
