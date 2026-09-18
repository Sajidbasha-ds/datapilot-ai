"""Data Quality and Cleaning Engine for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def analyze_data_quality(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Any]:
    """Inspects dataset for quality issues: missingness, duplicates, outliers, collinearity, leakage."""
    total_rows = len(df)
    issues: List[Dict[str, Any]] = []
    missing_strategy_recommendations: Dict[str, Dict[str, Any]] = {}
    outlier_summary: Dict[str, Dict[str, Any]] = {}

    # 1. Duplicate rows
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        dup_pct = round((dup_count / total_rows) * 100, 2)
        issues.append({
            "type": "Duplicates",
            "title": f"{dup_count} Duplicate Rows ({dup_pct}%)",
            "description": "Identical rows can bias model training and inflate validation performance.",
            "severity": "high" if dup_pct > 5 else "medium",
            "action": "Deduplicate",
        })

    # 2. Missing Values & Strategies
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols]

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            null_pct = round((null_count / total_rows) * 100, 2)
            if col in num_cols:
                series = df[col].dropna()
                skew = abs(float(stats.skew(series))) if len(series) > 2 else 0.0
                rec = "median" if skew > 1.0 else "mean"
                reason = "Skewed distribution detected (median is outlier-resistant)" if skew > 1.0 else "Relatively symmetric distribution"
            else:
                rec = "mode" if null_pct < 10 else "Unknown"
                reason = "Low missing percentage (impute most frequent category)" if null_pct < 10 else "High missing percentage (treat missing as explicit 'Unknown' class)"

            missing_strategy_recommendations[col] = {
                "missing_count": null_count,
                "missing_pct": null_pct,
                "recommended_strategy": rec,
                "reason": reason,
                "is_numerical": col in num_cols,
            }

            severity = "high" if null_pct > 40 else ("medium" if null_pct > 10 else "low")
            issues.append({
                "type": "Missing Values",
                "title": f"Column '{col}' is {null_pct}% missing ({null_count} rows)",
                "description": f"Recommended action: Impute with {rec} ({reason}).",
                "severity": severity,
                "column": col,
            })

    # 3. Outlier Analysis (Tukey IQR & Z-score)
    for col in num_cols:
        series = df[col].dropna()
        if len(series) >= 10 and series.nunique() > 5:
            q25 = float(series.quantile(0.25))
            q75 = float(series.quantile(0.75))
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            iqr_outliers = int(((series < lower_bound) | (series > upper_bound)).sum())

            # Z-score (|z| > 3)
            std_val = float(series.std())
            z_outliers = 0
            if std_val > 0:
                z_scores = np.abs((series - float(series.mean())) / std_val)
                z_outliers = int((z_scores > 3).sum())

            if iqr_outliers > 0:
                outlier_pct = round((iqr_outliers / len(series)) * 100, 2)
                outlier_summary[col] = {
                    "iqr_count": iqr_outliers,
                    "iqr_pct": outlier_pct,
                    "z_count": z_outliers,
                    "lower_bound": round(lower_bound, 4),
                    "upper_bound": round(upper_bound, 4),
                }
                if outlier_pct > 2.0:
                    issues.append({
                        "type": "Outliers",
                        "title": f"Column '{col}' has {iqr_outliers} IQR outliers ({outlier_pct}%)",
                        "description": f"Values outside [{round(lower_bound, 2)}, {round(upper_bound, 2)}] can disproportionately pull linear models.",
                        "severity": "medium" if outlier_pct > 5.0 else "low",
                        "column": col,
                    })

    # 4. Constant / Zero-Variance Features
    for col in df.columns:
        if df[col].nunique(dropna=False) <= 1:
            issues.append({
                "type": "Constant Feature",
                "title": f"Column '{col}' has zero variance (constant)",
                "description": "Carries no statistical entropy. Should be removed to reduce dimension.",
                "severity": "high",
                "column": col,
            })

    # 5. Multicollinearity & Potential Target Leakage
    high_corr_pairs: List[Dict[str, Any]] = []
    leakage_candidates: List[Dict[str, Any]] = []

    if len(num_cols) >= 2:
        corr_matrix = df[num_cols].corr(method="pearson").abs()
        cols = corr_matrix.columns
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                col_a, col_b = cols[i], cols[j]
                val = float(corr_matrix.iloc[i, j])
                if not np.isnan(val) and val >= 0.85:
                    high_corr_pairs.append({
                        "col1": col_a,
                        "col2": col_b,
                        "correlation": round(val, 4),
                    })
                    issues.append({
                        "type": "High Collinearity",
                        "title": f"Collinear pair: '{col_a}' & '{col_b}' (|r| = {round(val, 2)})",
                        "description": "Redundant information causes instability in linear model coefficients.",
                        "severity": "medium",
                    })

                # Check potential target leakage
                if target_col and (col_a == target_col or col_b == target_col):
                    other = col_b if col_a == target_col else col_a
                    if not np.isnan(val) and val >= 0.95:
                        leakage_candidates.append({"feature": other, "target": target_col, "correlation": round(val, 4)})
                        issues.append({
                            "type": "Target Leakage Candidate",
                            "title": f"Potential target leakage in '{other}' (|r| = {round(val, 3)} with '{target_col}')",
                            "description": "Near-perfect correlation with target usually signals a downstream artifact or duplicate target.",
                            "severity": "high",
                            "column": other,
                        })

    return {
        "total_issues": len(issues),
        "issues": issues,
        "duplicate_count": dup_count,
        "missing_recommendations": missing_strategy_recommendations,
        "outlier_summary": outlier_summary,
        "high_corr_pairs": high_corr_pairs,
        "leakage_candidates": leakage_candidates,
    }


def clean_dataset(
    df: pd.DataFrame,
    drop_duplicates: bool = True,
    drop_constant_cols: bool = True,
    impute_missing: bool = True,
    custom_imputations: Optional[Dict[str, str]] = None,
    cap_outliers: bool = False,
    outlier_cols: Optional[List[str]] = None,
    drop_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """Creates a cleaned copy of the dataset based on user-approved operations.
    Original dataframe is NEVER mutated in place.
    """
    cleaned = df.copy(deep=True)
    logs: List[str] = []

    # 1. Drop user-specified columns
    if drop_cols:
        valid_drops = [c for c in drop_cols if c in cleaned.columns]
        if valid_drops:
            cleaned.drop(columns=valid_drops, inplace=True)
            logs.append(f"Dropped {len(valid_drops)} designated columns: {', '.join(valid_drops)}")

    # 2. Deduplicate
    if drop_duplicates:
        initial_rows = len(cleaned)
        cleaned.drop_duplicates(inplace=True)
        dropped_dups = initial_rows - len(cleaned)
        if dropped_dups > 0:
            logs.append(f"Removed {dropped_dups} duplicate rows.")

    # 3. Drop constant columns
    if drop_constant_cols:
        const_cols = [c for c in cleaned.columns if cleaned[c].nunique(dropna=False) <= 1]
        if const_cols:
            cleaned.drop(columns=const_cols, inplace=True)
            logs.append(f"Removed {len(const_cols)} constant column(s): {', '.join(const_cols)}")

    # 4. Impute missing values
    if impute_missing:
        num_cols = cleaned.select_dtypes(include=[np.number]).columns.tolist()
        for col in cleaned.columns:
            if cleaned[col].isna().sum() > 0:
                # Custom strategy or heuristic
                strat = (custom_imputations or {}).get(col)
                if not strat:
                    strat = "median" if col in num_cols else "Unknown"

                if strat == "median" and col in num_cols:
                    fill_val = cleaned[col].median()
                    cleaned[col] = cleaned[col].fillna(fill_val)
                    logs.append(f"Imputed '{col}' nulls with median ({round(fill_val, 4) if isinstance(fill_val, float) else fill_val})")
                elif strat == "mean" and col in num_cols:
                    fill_val = cleaned[col].mean()
                    cleaned[col] = cleaned[col].fillna(fill_val)
                    logs.append(f"Imputed '{col}' nulls with mean ({round(fill_val, 4)})")
                elif strat == "zero" and col in num_cols:
                    cleaned[col] = cleaned[col].fillna(0)
                    logs.append(f"Imputed '{col}' nulls with 0")
                elif strat == "mode":
                    mode_val = cleaned[col].mode(dropna=True)
                    fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
                    cleaned[col] = cleaned[col].fillna(fill_val)
                    logs.append(f"Imputed '{col}' nulls with mode ('{fill_val}')")
                else:  # 'Unknown' or fallback
                    cleaned[col] = cleaned[col].fillna("Unknown")
                    logs.append(f"Imputed '{col}' nulls with literal 'Unknown'")

    # 5. Cap Outliers via IQR Winsorization
    if cap_outliers and outlier_cols:
        for col in outlier_cols:
            if col in cleaned.columns and pd.api.types.is_numeric_dtype(cleaned[col]):
                q25 = cleaned[col].quantile(0.25)
                q75 = cleaned[col].quantile(0.75)
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                outliers_capped = ((cleaned[col] < lower_bound) | (cleaned[col] > upper_bound)).sum()
                if outliers_capped > 0:
                    cleaned[col] = cleaned[col].clip(lower=lower_bound, upper=upper_bound)
                    logs.append(f"Capped {outliers_capped} outliers in '{col}' to range [{round(lower_bound, 2)}, {round(upper_bound, 2)}]")

    return cleaned, logs
