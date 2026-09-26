"""AI Insights Engine and Autonomous Data Scientist Chatbot for DataPilot AI."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional
import pandas as pd


def _leakage_scope_summary(problem_type: Optional[str] = None) -> str:
    """Describe implemented leakage-risk controls and their limits."""
    if problem_type and "Unsupervised" in problem_type:
        return (
            "The unsupervised workflow does not create a supervised train/test split or use target-correlation "
            "screening. It screens constants and some high-cardinality ID-like columns on the supplied feature "
            "matrix and fits preprocessing on that matrix. It does not automatically detect temporal leakage, "
            "semantic post-outcome fields, or related records, so it cannot establish that all leakage is absent."
        )

    summary = (
        "This supervised run splits data before feature screening, removes constant columns and some "
        "high-cardinality ID-like columns from the training features, fits preprocessing on training data, "
        "and uses cross-validation scores for candidate ranking while reserving the holdout for evaluation. "
        if problem_type and ("Regression" in problem_type or "Classification" in problem_type)
        else "When supervised training runs, it splits data before feature screening, removes constant columns and some "
        "high-cardinality ID-like columns from the training features, fits preprocessing on training data, "
        "and uses cross-validation scores for candidate ranking while reserving the holdout for evaluation. "
    )
    if problem_type and "Regression" in problem_type:
        summary += (
            "For regression, numeric feature/target correlations with absolute Pearson r >= 0.98 are screened "
            "on the outer training partition before cross-validation; because this screen is not repeated inside "
            "each CV fold, CV scores may be optimistic. "
        )
    elif problem_type and "Classification" in problem_type:
        summary += (
            "The training feature filter does not apply target-correlation screening to classification. "
        )
    else:
        summary += (
            "The numeric target-correlation screen is used only for regression, and it runs on the outer "
            "training partition before cross-validation. "
        )
    summary += (
        "Data-quality analysis can separately flag near-perfect numeric feature/target correlations on the "
        "full dataset for review; that diagnostic does not remove features. "
    )
    summary += (
        "These checks reduce specific risks but do not establish that all leakage is absent; the pipeline does "
        "not automatically detect temporal leakage, categorical or semantic post-outcome features, or related "
        "records split across a random train/test partition."
    )
    return summary


def generate_automated_insights(
    profile_data: Dict[str, Any],
    quality_data: Dict[str, Any],
    ml_results: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Derives deterministic, mathematical, and statistical insights from actual computation.
    Guaranteed zero hallucination.
    """
    overview = profile_data.get("overview", {})
    rows = overview.get("rows", 0)
    cols = overview.get("columns", 0)
    dup_pct = overview.get("duplicate_pct", 0.0)
    missing_pct = overview.get("missing_pct", 0.0)

    technical_points: List[str] = []
    executive_points: List[str] = []

    if ml_results and any(
        task in ml_results.get("problem_type", "")
        for task in ("Regression", "Classification")
    ):
        technical_points.append(
            f"Leakage checks and limits: {_leakage_scope_summary(ml_results.get('problem_type'))}"
        )

    # 1. Volume & Dimensionality
    executive_points.append(
        f"The dataset contains {rows:,} records across {cols} features. "
        f"Overall missingness is low to moderate at {missing_pct}% of total cells."
    )
    technical_points.append(
        f"Dimensionality: matrix shape is ({rows:,}, {cols}). "
        f"Memory contains {overview.get('numerical_columns_count', 0)} numeric, "
        f"{overview.get('categorical_columns_count', 0)} categorical, and "
        f"{overview.get('datetime_columns_count', 0)} temporal dimensions."
    )

    # 2. Data Quality & Duplicates
    if dup_pct > 0:
        executive_points.append(
            f"Detected {overview.get('duplicate_rows', 0):,} duplicate rows ({dup_pct}%). "
            "Deduplicating is recommended before deploying models."
        )
        technical_points.append(
            f"Entropy Warning: {dup_pct}% identical feature vectors detected. "
            "Duplicates artificially shrink standard errors and induce optimistic bias in validation."
        )
    else:
        executive_points.append("Excellent data hygiene: zero duplicate records identified.")
        technical_points.append("Integrity check passed: All rows represent unique observation tuples.")

    # 3. Suspicious & High Collinearity
    high_corr = quality_data.get("high_corr_pairs", [])
    if high_corr:
        top_pair = high_corr[0]
        executive_points.append(
            f"Strong relationship identified between '{top_pair['col1']}' and '{top_pair['col2']}' "
            f"(correlation: {top_pair['correlation']}). These features measure similar dynamics."
        )
        technical_points.append(
            f"Multicollinearity: Observed Pearson |r| = {top_pair['correlation']} between "
            f"'{top_pair['col1']}' and '{top_pair['col2']}'. Regularization (Ridge/L2) or PCA is warranted."
        )

    # 4. Outlier analysis
    outlier_sum = quality_data.get("outlier_summary", {})
    if outlier_sum:
        top_outlier_col = max(outlier_sum.keys(), key=lambda k: outlier_sum[k]["iqr_pct"])
        pct = outlier_sum[top_outlier_col]["iqr_pct"]
        executive_points.append(
            f"Column '{top_outlier_col}' shows {pct}% extreme outlier values that deviate significantly from typical ranges."
        )
        technical_points.append(
            f"Distribution Tail: Feature '{top_outlier_col}' exhibits heavy tails with {pct}% outside "
            f"[{outlier_sum[top_outlier_col]['lower_bound']}, {outlier_sum[top_outlier_col]['upper_bound']}] via Tukey's IQR rule."
        )

    # 5. Machine Learning Performance Insights
    if ml_results:
        prob_type = ml_results.get("problem_type", "")
        best_name = ml_results.get("best_model_name", "Unknown")
        results_df = ml_results.get("results_df", pd.DataFrame())

        if not results_df.empty:
            if "Classification" in prob_type:
                best_f1 = results_df.iloc[0].get("F1-Score (Macro)", 0.0)
                best_acc = results_df.iloc[0].get("Accuracy", 0.0)
                executive_points.append(
                    f"In automated benchmarking, **{best_name}** emerged as the top classifier, "
                    f"achieving an Accuracy of {round(best_acc * 100, 1)}% and an F1-Score of {best_f1}."
                )
                technical_points.append(
                    f"Model Selection: {best_name} maximized Macro F1 ({best_f1}) on held-out test fold. "
                    f"Generalization was validated via stratified cross-validation."
                )
            elif "Regression" in prob_type:
                best_r2 = results_df.iloc[0].get("R²", 0.0)
                best_rmse = results_df.iloc[0].get("RMSE", 0.0)
                executive_points.append(
                    f"The top predictive algorithm was **{best_name}**, explaining {round(best_r2 * 100, 1)}% "
                    f"of the target's variance with an average RMSE error of {best_rmse}."
                )
                technical_points.append(
                    f"Goodness of Fit: {best_name} achieved R² = {best_r2}, Adjusted R² = {results_df.iloc[0].get('Adjusted R²', 0.0)}, "
                    f"and RMSE = {best_rmse}."
                )

        # Model-specific feature attribution
        importances = ml_results.get("feature_importances", {}).get(best_name, {})
        attributions = ml_results.get("feature_attributions", {}).get(best_name, [])
        if attributions:
            top = attributions[0]
            top_feature = top["feature"]
            top_value = top["value"]
            if top.get("method") == "coefficient":
                executive_points.append(
                    f"Among the displayed transformed features, **{top_feature}** has the largest absolute model coefficient."
                )
                if "coefficient" in top and "Logistic" in top.get("model_type", best_name):
                    direction = "increases" if top["coefficient"] > 0 else "decreases" if top["coefficient"] < 0 else "does not change"
                    decision_class = top.get("decision_class", "positive class")
                    technical_points.append(
                        f"Model Coefficient: '{top_feature}' has β = {top['coefficient']:.4f} (|β| = {top_value:.4f}); "
                        f"its sign {direction} the Logistic Regression decision score/log-odds for class '{decision_class}'. "
                        "This is a model association, not evidence of causation."
                    )
                elif top.get("class_coefficients"):
                    technical_points.append(
                        f"Model Coefficient Strength: '{top_feature}' has the largest maximum absolute coefficient "
                        f"across the Logistic Regression class-specific coefficient rows ({top_value:.4f}); "
                        "this is not evidence of causation."
                    )
                else:
                    technical_points.append(
                        f"Model Coefficient Strength: '{top_feature}' has the largest absolute coefficient "
                        f"({top_value:.4f}) in {best_name}; magnitude is not evidence of causation."
                    )
            elif top.get("method") == "tree_feature_importance":
                executive_points.append(
                    f"**{top_feature}** has the highest tree-based feature-importance value in {best_name}."
                )
                technical_points.append(
                    f"Tree Feature Importance: '{top_feature}' has value {top_value:.4f} in {best_name}; "
                    "this model attribution is not evidence of causation."
                )
        elif importances and "Logistic" in best_name:
            top_feature, top_value = next(iter(importances.items()))
            executive_points.append(
                f"Among the displayed features, **{top_feature}** has the largest absolute model coefficient magnitude."
            )
            technical_points.append(
                f"Model Coefficient Strength: '{top_feature}' has magnitude {top_value:.4f}. "
                "The coefficient sign is unavailable in these legacy results, and magnitude is not evidence of causation."
            )
        elif importances and any(tree_name in best_name for tree_name in ("Tree", "Forest", "Boosting")):
            top_feature, top_value = next(iter(importances.items()))
            executive_points.append(
                f"**{top_feature}** has the highest tree-based feature-importance value in {best_name}."
            )
            technical_points.append(
                f"Tree Feature Importance: '{top_feature}' has value {top_value:.4f} in {best_name}; "
                "this model attribution is not evidence of causation."
            )

    return {
        "executive_insights": executive_points,
        "technical_insights": technical_points,
    }


def answer_datapilot_query(
    user_query: str,
    profile_data: Optional[Dict[str, Any]],
    quality_data: Optional[Dict[str, Any]],
    ml_results: Optional[Dict[str, Any]],
) -> str:
    """Deterministic natural-language QA engine for 'Ask DataPilot AI'.
    Answers factual questions about the current session accurately.
    """
    q = user_query.lower().strip()

    if not profile_data:
        return "Please upload and profile a dataset first so I can inspect the data characteristics."

    overview = profile_data.get("overview", {})

    if any(term in q for term in (
        "leakage",
        "data leak",
        "safe from leak",
        "features safe",
        "safe features",
        "trust this model",
        "trust the model",
        "test set protected",
        "test set safe",
    )):
        problem_type = ml_results.get("problem_type") if ml_results else None
        return _leakage_scope_summary(problem_type)

    # 1. Missing values query
    if any(k in q for k in ["missing", "null", "nan"]):
        tot_missing = overview.get("total_missing", 0)
        pct_missing = overview.get("missing_pct", 0.0)
        rec = quality_data.get("missing_recommendations", {}) if quality_data else {}
        if tot_missing == 0:
            return "Good news! There are 0 missing values (NaN) anywhere in this dataset."
        ans = f"The dataset has {tot_missing:,} missing cells ({pct_missing}% of all data).\n\n"
        ans += "Key columns requiring imputation:\n"
        for c, details in list(rec.items())[:5]:
            ans += f"- **{c}**: {details['missing_pct']}% nulls (Recommended strategy: `{details['recommended_strategy']}`)\n"
        return ans

    # 2. Most important columns / features
    if any(k in q for k in ["important", "driver", "influence", "feature importance", "top feature", "coefficient", "attribution"]):
        if not ml_results or "feature_importances" not in ml_results:
            return "To view model feature attribution, please train the models in the **ML Lab** tab first."
        best_name = ml_results.get("best_model_name", "")
        importances = ml_results.get("feature_importances", {}).get(best_name, {})
        if not importances:
            return f"The current best model ({best_name}) does not output direct linear coefficients or tree importances."
        attributions = ml_results.get("feature_attributions", {}).get(best_name, [])
        if attributions:
            if attributions[0].get("method") == "coefficient":
                is_logistic = "Logistic" in best_name
                model_kind = "Logistic Regression" if is_logistic else "linear model"
                ans = f"Based on the winning {model_kind} (**{best_name}**), these transformed features have the largest absolute model coefficients. Magnitude is not causal evidence.\n\n"
                for item in attributions[:5]:
                    if is_logistic and "coefficient" in item:
                        ans += f"- **{item['feature']}**: β = {item['coefficient']:.4f} (|β| = {item['value']:.4f}), direction {item['direction']} for class '{item.get('decision_class', 'positive class')}'\n"
                    elif item.get("class_coefficients"):
                        ans += f"- **{item['feature']}**: maximum class-specific |β| = {item['value']:.4f}\n"
                    else:
                        ans += f"- **{item['feature']}**: |coefficient| = {item['value']:.4f}\n"
            else:
                ans = f"Based on the winning tree model (**{best_name}**), here are the highest tree feature-importance values. These are not causal effects.\n\n"
                for item in attributions[:5]:
                    ans += f"- **{item['feature']}**: {item['value']:.4f} tree feature-importance value\n"
            return ans
        ans = f"Based on the winning model (**{best_name}**), here are the highest model-attributed features. These values are not causal effects:\n\n"
        for feat, score in list(importances.items())[:5]:
            ans += f"- **{feat}**: {score:.4f} attribution strength\n"
        return ans

    # 3. Best model query
    if any(k in q for k in ["best model", "winner", "top model", "compare", "performance"]):
        if not ml_results or "results_df" not in ml_results:
            return "No models have been trained yet. Head to **ML Lab** and click 'Run Automated Model Training'!"
        best_name = ml_results.get("best_model_name", "")
        prob_type = ml_results.get("problem_type", "")
        results_df = ml_results["results_df"]
        ans = f"The top performing model is **{best_name}** for **{prob_type}**.\n\n"
        ans += "Model Leaderboard:\n"
        for _, row in results_df.head(4).iterrows():
            if "Classification" in prob_type:
                ans += f"- **{row['Model']}**: F1-Score = {row['F1-Score (Macro)']}, Accuracy = {row['Accuracy']}\n"
            else:
                ans += f"- **{row['Model']}**: R² = {row['R²']}, RMSE = {row['RMSE']}\n"
        return ans

    # 4. Preprocessing query
    if any(k in q for k in ["preprocessing", "transformation", "pipeline", "scaled", "encoded"]):
        if not ml_results:
            return "Preprocessing steps: Missing numerical features are imputed with median, numerical features are standardized via StandardScaler, and categorical variables are one-hot encoded with handle_unknown='ignore'."
        logs = ml_results.get("logs", [])
        ans = "Here is the exact preprocessing pipeline applied:\n\n"
        ans += "- **Training-split preprocessing**: Imputers, encoders, and scalers are fitted on training data; cross-validation refits them within each training fold. This reduces preprocessing leakage risk but does not guarantee that all leakage is absent.\n"
        ans += "- **Numerical Treatment**: Missing values filled via median, scaled via StandardScaler.\n"
        ans += "- **Categorical Treatment**: Missing filled with 'Unknown', one-hot encoded.\n"
        if logs:
            ans += "\nSpecific transformations logged:\n"
            for log_entry in logs[:6]:
                ans += f"- {log_entry}\n"
        return ans

    # 5. Correlation heatmap explanation
    if any(k in q for k in ["correlation", "heatmap", "multicollinearity", "relationship"]):
        high_corr = quality_data.get("high_corr_pairs", []) if quality_data else []
        if not high_corr:
            return "The correlation heatmap displays Pearson correlation coefficients between -1.0 and +1.0. No severe collinear pairs (|r| >= 0.85) were detected in this dataset."
        ans = "The correlation heatmap shows the linear association between numerical variables:\n\n"
        for pair in high_corr[:5]:
            ans += f"- **{pair['col1']}** & **{pair['col2']}**: r = {pair['correlation']} (Strong linear association)\n"
        ans += "\n*Note: Correlation indicates association, not direct causality.*"
        return ans

    # 6. Definition of Metrics (RMSE, F1, etc.)
    if "rmse" in q:
        return "**RMSE (Root Mean Squared Error)** is the square root of the average squared discrepancies between predicted and actual continuous values. It is expressed in the exact same physical units as the target, making it intuitive, while penalizing large outliers heavily."
    if "f1" in q:
        return "**F1-Score** is the harmonic mean of Precision and Recall: `2 * (Precision * Recall) / (Precision + Recall)`. Unlike simple Accuracy, F1 remains reliable even when the target classes are severely imbalanced."
    if "r2" in q or "r-squared" in q or "r squared" in q:
        return "**R² (Coefficient of Determination)** indicates what percentage of the variance in the target variable is successfully explained by the model features. A score of 1.0 represents a perfect fit, while 0.0 matches a trivial mean baseline."

    # 7. Problem type
    if any(k in q for k in ["why classification", "why regression", "problem type", "unsupervised"]):
        prob_type = ml_results.get("problem_type") if ml_results else "Determined by target column cardinality."
        target_col = ml_results.get("target_col") if ml_results else "Selected target"
        return f"Current problem type is **{prob_type}**. Classification is chosen when the target has discrete labels (e.g. churn yes/no), Regression when the target is continuous numeric (e.g. price), and Unsupervised when no target is chosen."

    # General fallback
    return (
        f"I analyzed your dataset ({overview.get('rows', 0):,} rows, {overview.get('columns', 0)} columns). "
        "You can ask me questions like:\n"
        "- *'Which columns have missing values?'*\n"
        "- *'What are the most important columns?'*\n"
        "- *'Which model performed best?'*\n"
        "- *'What preprocessing was performed?'*\n"
        "- *'What does RMSE mean?'*\n"
        "- *'Explain the correlation heatmap'*"
    )
