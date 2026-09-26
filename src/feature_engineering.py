"""Training-partition preprocessing and feature engineering for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def engineer_datetime_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Expands datetime columns into cyclical and calendar numeric components."""
    transformed = df.copy()
    dt_cols = transformed.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    logs: List[str] = []

    # Also detect object columns that parse as dates
    for col in transformed.columns:
        if col not in dt_cols and transformed[col].dtype == "object":
            sample = transformed[col].dropna().head(10)
            if not sample.empty and sample.astype(str).str.contains(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", regex=True).all():
                try:
                    transformed[col] = pd.to_datetime(transformed[col], errors="coerce")
                    dt_cols.append(col)
                except Exception:
                    pass

    for col in dt_cols:
        series = transformed[col]
        prefix = str(col)
        transformed[f"{prefix}_year"] = series.dt.year.fillna(-1).astype(int)
        transformed[f"{prefix}_month"] = series.dt.month.fillna(-1).astype(int)
        transformed[f"{prefix}_day"] = series.dt.day.fillna(-1).astype(int)
        transformed[f"{prefix}_dayofweek"] = series.dt.dayofweek.fillna(-1).astype(int)

        # Include hour if varying
        if series.dt.hour.nunique() > 1:
            transformed[f"{prefix}_hour"] = series.dt.hour.fillna(-1).astype(int)

        transformed.drop(columns=[col], inplace=True)
        logs.append(f"Engineered calendar features from datetime column '{col}' (year, month, day, dayofweek).")

    return transformed, logs


def filter_suspicious_features(
    X: pd.DataFrame,
    y: Optional[pd.Series] = None,
    drop_ids: bool = True,
    drop_constants: bool = True,
    drop_leakage: bool = True,
) -> Tuple[pd.DataFrame, List[str]]:
    """Remove constants and heuristic IDs; screen numeric target correlation when y is supplied."""
    filtered_X = X.copy()
    dropped_logs: List[str] = []
    n_rows = len(filtered_X)

    cols_to_drop: List[str] = []

    for col in filtered_X.columns:
        series = filtered_X[col]
        n_unique = series.nunique(dropna=True)

        # 1. Constant columns
        if drop_constants and n_unique <= 1:
            cols_to_drop.append(col)
            dropped_logs.append(f"Dropped constant feature '{col}' (0 variance).")
            continue

        # 2. Obvious ID columns
        col_lower = str(col).lower()
        is_id_name = (
            any(k in col_lower for k in ["_id", "id_", "identifier", "uuid", "guid", "code"])
            or col_lower.endswith("id")
            or col_lower.startswith("id")
            or col_lower in ["id", "index"]
        )
        is_discrete_or_text = not pd.api.types.is_float_dtype(series)
        if drop_ids and is_id_name and is_discrete_or_text and (n_unique > n_rows * 0.85):
            cols_to_drop.append(col)
            dropped_logs.append(f"Dropped identifier feature '{col}' (non-predictive key).")
            continue

        # 3. Target leakage (if y is numerical continuous and |corr| > 0.98)
        if drop_leakage and y is not None and pd.api.types.is_numeric_dtype(series) and pd.api.types.is_numeric_dtype(y):
            try:
                corr = abs(float(series.corr(y)))
                if corr >= 0.98:
                    cols_to_drop.append(col)
                    dropped_logs.append(f"Dropped target leakage suspect '{col}' (|r| = {round(corr, 3)} with target).")
            except Exception:
                pass

    if cols_to_drop:
        filtered_X.drop(columns=cols_to_drop, inplace=True)

    return filtered_X, dropped_logs


def build_preprocessing_pipeline(
    X_train: pd.DataFrame,
    numerical_strategy: str = "median",
    scale_numeric: bool = True,
) -> Tuple[ColumnTransformer, List[str], List[str]]:
    """Construct a ColumnTransformer from the training partition's feature columns."""
    num_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X_train.columns if c not in num_cols]
    logs: List[str] = []

    transformers = []

    if num_cols:
        num_steps = [("imputer", SimpleImputer(strategy=numerical_strategy))]
        if scale_numeric:
            num_steps.append(("scaler", StandardScaler()))
            logs.append(f"Numerical Pipeline: SimpleImputer({numerical_strategy}) + StandardScaler on {len(num_cols)} features.")
        else:
            logs.append(f"Numerical Pipeline: SimpleImputer({numerical_strategy}) on {len(num_cols)} features.")
        transformers.append(("num", Pipeline(num_steps), num_cols))

    if cat_cols:
        cat_steps = [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
        logs.append(f"Categorical Pipeline: Imputer('Unknown') + OneHotEncoder on {len(cat_cols)} features.")
        transformers.append(("cat", Pipeline(cat_steps), cat_cols))

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    return preprocessor, num_cols, cat_cols


def get_feature_names(preprocessor: ColumnTransformer, num_cols: List[str], cat_cols: List[str]) -> List[str]:
    """Extracts post-transformation feature names for transparent model explainability."""
    feature_names: List[str] = []

    if num_cols:
        feature_names.extend(num_cols)

    if cat_cols:
        try:
            cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
            ohe_names = cat_encoder.get_feature_names_out(cat_cols)
            feature_names.extend(list(ohe_names))
        except Exception:
            for c in cat_cols:
                feature_names.append(f"{c}_encoded")

    return feature_names
