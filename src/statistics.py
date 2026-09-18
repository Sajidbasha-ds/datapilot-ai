"""Statistical Analysis Engine for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats


def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Computes comprehensive numerical descriptive statistics including skewness and kurtosis."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        return pd.DataFrame()

    records: List[Dict[str, Any]] = []
    for col in num_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        n = len(series)
        mean_val = float(series.mean())
        std_val = float(series.std()) if n > 1 else 0.0
        var_val = float(series.var()) if n > 1 else 0.0
        median_val = float(series.median())
        min_val = float(series.min())
        max_val = float(series.max())
        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr_val = q75 - q25

        try:
            skew_val = float(stats.skew(series))
            kurt_val = float(stats.kurtosis(series))
        except Exception:
            skew_val = 0.0
            kurt_val = 0.0

        records.append({
            "Feature": col,
            "Count": n,
            "Mean": round(mean_val, 4),
            "Std Dev": round(std_val, 4),
            "Variance": round(var_val, 4),
            "Median": round(median_val, 4),
            "Min": round(min_val, 4),
            "25%": round(q25, 4),
            "75%": round(q75, 4),
            "Max": round(max_val, 4),
            "IQR": round(iqr_val, 4),
            "Skewness": round(skew_val, 3),
            "Kurtosis": round(kurt_val, 3),
        })

    return pd.DataFrame(records)


def compute_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Computes correlation matrix for numerical features using Pearson or Spearman."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return pd.DataFrame()
    return df[num_cols].corr(method=method).round(4)


def compute_covariance_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Computes covariance matrix for numerical features."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return pd.DataFrame()
    return df[num_cols].cov().round(4)


def compute_pairwise_correlation_with_pvalues(
    df: pd.DataFrame,
    col_x: str,
    col_y: str,
) -> Dict[str, Any]:
    """Calculates both Pearson and Spearman correlations along with p-values."""
    sub_df = df[[col_x, col_y]].dropna()
    if len(sub_df) < 5:
        return {"error": "Insufficient non-null rows (minimum 5 required for hypothesis testing)."}

    x = sub_df[col_x]
    y = sub_df[col_y]

    pearson_r, pearson_p = stats.pearsonr(x, y)
    spearman_rho, spearman_p = stats.spearmanr(x, y)

    return {
        "feature_x": col_x,
        "feature_y": col_y,
        "sample_size": len(sub_df),
        "pearson": {
            "coefficient": round(float(pearson_r), 4),
            "p_value": float(pearson_p),
            "statistically_significant": bool(pearson_p < 0.05),
            "interpretation": _interpret_correlation(pearson_r),
        },
        "spearman": {
            "rho": round(float(spearman_rho), 4),
            "p_value": float(spearman_p),
            "statistically_significant": bool(spearman_p < 0.05),
            "interpretation": _interpret_correlation(spearman_rho),
        },
        "scientific_disclaimer": (
            "CRITICAL NOTE: Correlation measures statistical association only, NOT causation. "
            "Latent confounding factors, selection bias, or reverse causality may explain high correlations."
        ),
    }


def run_hypothesis_test(
    df: pd.DataFrame,
    test_type: str,
    var1: str,
    var2: str,
    group_val1: Optional[str] = None,
    group_val2: Optional[str] = None,
) -> Dict[str, Any]:
    """Executes parametric and non-parametric hypothesis tests with assumption disclaimers."""
    clean_df = df.dropna(subset=[var1, var2]).copy()
    if len(clean_df) < 10:
        return {"error": "Sample size is too small (<10 observations) for reliable inference."}

    if test_type == "Two-Sample T-Test":
        # var1: numerical target, var2: binary group
        groups = clean_df[var2].unique()
        if len(groups) < 2:
            return {"error": f"Group variable '{var2}' must have at least 2 distinct categories."}
        g1_val = group_val1 if group_val1 in groups else groups[0]
        g2_val = group_val2 if group_val2 in groups else groups[1]

        data1 = clean_df[clean_df[var2] == g1_val][var1]
        data2 = clean_df[clean_df[var2] == g2_val][var1]

        if len(data1) < 3 or len(data2) < 3:
            return {"error": "One or both groups have fewer than 3 samples."}

        # Welch's t-test (does not assume equal variance)
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False)

        return {
            "test_name": "Two-Sample Welch's t-Test",
            "numerical_var": var1,
            "grouping_var": var2,
            "group_1": {"name": str(g1_val), "mean": round(float(data1.mean()), 4), "n": len(data1)},
            "group_2": {"name": str(g2_val), "mean": round(float(data2.mean()), 4), "n": len(data2)},
            "statistic": round(float(t_stat), 4),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05),
            "null_hypothesis": f"Mean {var1} for {g1_val} is EQUAL to Mean {var1} for {g2_val}.",
            "conclusion": (
                f"Reject Null Hypothesis (p={p_val:.4e} < 0.05): Statistically significant difference in means."
                if p_val < 0.05
                else f"Fail to Reject Null (p={p_val:.4f} >= 0.05): Insufficient statistical evidence of difference."
            ),
            "assumptions": "Assumes data is approximately normally distributed or sample size is large (Central Limit Theorem).",
        }

    elif test_type == "Mann-Whitney U Test":
        # Non-parametric equivalent of two-sample t-test
        groups = clean_df[var2].unique()
        if len(groups) < 2:
            return {"error": f"Group variable '{var2}' must have at least 2 distinct categories."}
        g1_val = group_val1 if group_val1 in groups else groups[0]
        g2_val = group_val2 if group_val2 in groups else groups[1]

        data1 = clean_df[clean_df[var2] == g1_val][var1]
        data2 = clean_df[clean_df[var2] == g2_val][var1]

        u_stat, p_val = stats.mannwhitneyu(data1, data2, alternative="two-sided")
        return {
            "test_name": "Mann-Whitney U Test (Non-Parametric)",
            "numerical_var": var1,
            "grouping_var": var2,
            "statistic": round(float(u_stat), 4),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05),
            "null_hypothesis": f"Distributions of {var1} across {g1_val} and {g2_val} are stochastically equal.",
            "conclusion": (
                f"Reject Null Hypothesis (p={p_val:.4e} < 0.05): Significant rank-sum difference between groups."
                if p_val < 0.05
                else f"Fail to Reject Null (p={p_val:.4f} >= 0.05): No statistically significant distributional shift."
            ),
            "assumptions": "Non-parametric; robust to severe outliers and non-normal distributions.",
        }

    elif test_type == "Chi-Square Test":
        # Contingency table of var1 vs var2
        contingency_table = pd.crosstab(clean_df[var1], clean_df[var2])
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

        return {
            "test_name": "Chi-Square Test of Independence",
            "feature_1": var1,
            "feature_2": var2,
            "chi2_statistic": round(float(chi2), 4),
            "degrees_of_freedom": int(dof),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05),
            "null_hypothesis": f"'{var1}' and '{var2}' are independent categorical variables.",
            "conclusion": (
                f"Reject Null Hypothesis (p={p_val:.4e} < 0.05): Significant statistical dependence detected between '{var1}' and '{var2}'."
                if p_val < 0.05
                else f"Fail to Reject Null (p={p_val:.4f} >= 0.05): No evidence of association between '{var1}' and '{var2}'."
            ),
            "assumptions": "Assumes expected frequency in at least 80% of contingency table cells is >= 5.",
        }

    return {"error": f"Unknown test type: {test_type}"}


def _interpret_correlation(r: float) -> str:
    abs_r = abs(r)
    direction = "positive" if r > 0 else "negative"
    if abs_r < 0.2:
        return f"Negligible {direction} linear relationship"
    elif abs_r < 0.4:
        return f"Weak {direction} linear association"
    elif abs_r < 0.7:
        return f"Moderate {direction} linear correlation"
    elif abs_r < 0.9:
        return f"Strong {direction} linear association"
    else:
        return f"Very strong {direction} correlation (check for redundancy or leakage)"
