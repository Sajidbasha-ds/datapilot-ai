"""DataPilot AI - Autonomous AI Data Scientist Streamlit Dashboard."""

from __future__ import annotations

import io
import os
import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.cleaner import analyze_data_quality, clean_dataset
from src.data_loader import DataLoaderError, load_dataset
from src.database import clear_prediction_history, get_prediction_history
from src.eda import (
    plot_categorical_frequency,
    plot_correlation_heatmap,
    plot_numerical_distribution,
    plot_scatter_relationship,
    plot_timeseries_trend,
)
from src.evaluator import get_metric_definitions
from src.insights import answer_datapilot_query, generate_automated_insights
from src.model_selector import get_model_descriptions
from src.model_trainer import train_supervised_models, train_unsupervised_models
from src.predictor import predict_batch, predict_single
from src.problem_detector import detect_problem_type
from src.profiler import profile_dataset
from src.report_generator import generate_pdf_report
from src.statistics import (
    compute_descriptive_stats,
    compute_pairwise_correlation_with_pvalues,
    run_hypothesis_test,
)
from src.target_detector import detect_target_column

# Configure Streamlit page
st.set_page_config(
    page_title="DataPilot AI | Autonomous AI Data Scientist",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End Styling CSS
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(2, 6, 23, 1) 90%);
        color: #F8FAFC;
    }
    
    /* Top Brand Banner */
    .brand-container {
        padding: 1.25rem 1.5rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
    }
    
    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #60A5FA 0%, #38BDF8 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .brand-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    
    /* Card Component */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    /* Pill Badges */
    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4); }
    .badge-green { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-amber { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-rose { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.4); }
    
    /* Workflow step node */
    .flow-step {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
        font-size: 0.85rem;
        font-weight: 600;
        color: #CBD5E1;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Session State
def init_session():
    defaults = {
        "df": None,
        "cleaned_df": None,
        "filename": None,
        "profile_data": None,
        "quality_data": None,
        "target_info": None,
        "target_col": None,
        "problem_type": None,
        "ml_results": None,
        "insights_data": None,
        "chat_messages": [
            {
                "role": "assistant",
                "content": "Hello! I am your Autonomous AI Data Scientist. Upload a dataset or load a sample to inspect profiling, train machine learning pipelines, and ask questions!",
            }
        ],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session()


# Sidebar Navigation
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <h2 style="margin: 0; color: #60A5FA; font-weight: 800; font-size: 1.5rem;">DATAPILOT AI</h2>
        <span style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Autonomous AI Data Scientist</span>
    </div>
    """,
    unsafe_allow_html=True,
)

NAV_OPTIONS = [
    "1. Home",
    "2. Upload Dataset",
    "3. Data Overview",
    "4. Data Quality",
    "5. EDA",
    "6. Statistics",
    "7. ML Lab",
    "8. Predictions",
    "9. AI Insights & Chat",
    "10. Reports",
]

selected_page = st.sidebar.radio("Navigation Flow", NAV_OPTIONS, index=0)

# Quick dataset indicator in sidebar
if st.session_state.df is not None:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Active File:** `{st.session_state.filename}`")
    st.sidebar.markdown(f"**Dimensions:** `{len(st.session_state.df):,} rows × {len(st.session_state.df.columns)} cols`")
    if st.session_state.target_col:
        st.sidebar.markdown(f"**Target:** `{st.session_state.target_col}`")
    if st.session_state.ml_results:
        st.sidebar.markdown(f"**Winning Model:** `{st.session_state.ml_results.get('best_model_name')}`")
# Target Detection Summary
if st.session_state.df is not None and st.session_state.target_info:
    target_info = st.session_state.target_info
    suggested_target = target_info.get("suggested_target")
    confidence = target_info.get("confidence", 0.0)
    reason = target_info.get("reason", "No reason provided")

    st.subheader("🎯 Automatic Target Detection")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Suggested Target", suggested_target or "None")

    with col2:
        st.metric("Detection Confidence", f"{confidence * 100:.1f}%")

    st.caption(f"Reason: {reason}")

# Helper to recompute profiling
def update_dataset(df: pd.DataFrame, filename: str):
    st.session_state.df = df
    st.session_state.filename = filename
    with st.spinner("Profiling dataset & calculating statistical distributions..."):
        prof = profile_dataset(df)
        st.session_state.profile_data = prof

        target_info = detect_target_column(df)
        st.session_state.target_col = target_info.get("suggested_target")
        st.session_state.target_info = target_info
        # Show automatic target-detection details
        if target_info.get("suggested_target"):
            confidence = target_info.get("confidence", 0.0)
            reason = target_info.get("reason", "No reason provided")

            if confidence < 0.25:
                st.warning(
                    f"Target suggestion: `{target_info['suggested_target']}` "
                    f"(low confidence: {confidence * 100:.1f}%)"
                )
            else:
                st.info(
                    f"Suggested target: `{target_info['suggested_target']}` "
                    f"— confidence: {confidence * 100:.1f}%"
                )

            st.caption(f"Reason: {reason}")
        qual = analyze_data_quality(df, target_col=st.session_state.target_col)
        st.session_state.quality_data = qual

        prob_info = detect_problem_type(df, target_col=st.session_state.target_col)
        st.session_state.problem_type = prob_info.get("problem_type")

        # Reset ML state when new data is loaded
        st.session_state.ml_results = None
        st.session_state.cleaned_df = None
        st.session_state.insights_data = generate_automated_insights(prof, qual, None)


# -------------------------------------------------------------
# PAGE 1: HOME
# -------------------------------------------------------------
if selected_page == "1. Home":
    st.markdown(
        """
        <div class="brand-container">
            <h1 class="brand-title">DATAPILOT AI</h1>
            <p class="brand-subtitle">Autonomous End-to-End AI Data Scientist — Transform raw datasets into cleaned representations, statistical analyses, verified ML models, and publication-ready PDF reports.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🔄 Complete Autonomous Lifecycle")
    cols = st.columns(6)
    steps = [
        ("1. Ingestion", "Upload CSV/XLSX with schema validation"),
        ("2. Profiling", "Zero-variance, ID & missingness checks"),
        ("3. Quality & EDA", "Tukey IQR outliers & Plotly charts"),
        ("4. Hypothesis", "Welch's t-test, Mann-Whitney & ANOVA"),
        ("5. ML Engine", "Training-split preprocessing & CV"),
        ("6. Inference", "Dynamic forms, batch CSV & PDF report"),
    ]
    for c, (title, desc) in zip(cols, steps):
        with c:
            st.markdown(
                f"""
                <div class="flow-step">
                    <div style="color: #60A5FA; margin-bottom: 0.2rem;">{title}</div>
                    <div style="font-size: 0.72rem; color: #94A3B8; font-weight: normal;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 0.8])
    with col_left:
        st.markdown("#### 🚀 Why DataPilot AI?")
        st.markdown(
            """
            - **No Hallucinations**: Core statistical analyses and model metrics are computed via deterministic Scikit-Learn and SciPy routines.
            - **Leakage-Risk Controls**: The pipeline splits before screening features and fits preprocessing on training data. These checks reduce specific risks but cannot establish that every leakage source is absent.
            - **100% Free & Open**: Operates natively on local hardware without mandatory paid API subscriptions.
            - **Production & College Ready**: Built according to industry standards for student viva defense, portfolio review, and hackathons.
            """
        )
        if st.button("Get Started → Upload a Dataset", type="primary"):
            st.session_state.page = "2. Upload Dataset"
            st.rerun()

    with col_right:
        st.markdown("#### ⚡ Quick Launch Demo Mode")
        st.markdown("Select a pre-bundled synthetic benchmark dataset to run the pipeline instantly:")
        demo_choice = st.selectbox(
            "Choose Benchmark Dataset",
            [
                "Select one...",
                "Customer Churn (Classification - 50 rows)",
                "House Prices (Regression - 40 rows)",
                "Student Performance (Multiclass - 30 rows)",
            ],
        )
        if st.button("Load Selected Benchmark", use_container_width=True):
            if "Customer Churn" in demo_choice:
                sample_path = os.path.join(os.path.dirname(__file__), "data", "sample", "customer_churn.csv")
                df, _ = load_dataset(sample_path, "customer_churn.csv")
                update_dataset(df, "customer_churn.csv")
                st.success("Loaded Customer Churn benchmark! Proceed to **Data Overview** or **ML Lab**.")
            elif "House Prices" in demo_choice:
                sample_path = os.path.join(os.path.dirname(__file__), "data", "sample", "house_prices.csv")
                df, _ = load_dataset(sample_path, "house_prices.csv")
                update_dataset(df, "house_prices.csv")
                st.success("Loaded House Prices benchmark! Proceed to **Data Overview** or **ML Lab**.")
            elif "Student Performance" in demo_choice:
                sample_path = os.path.join(os.path.dirname(__file__), "data", "sample", "student_performance.csv")
                df, _ = load_dataset(sample_path, "student_performance.csv")
                update_dataset(df, "student_performance.csv")
                st.success("Loaded Student Performance benchmark! Proceed to **Data Overview** or **ML Lab**.")
            else:
                st.warning("Please choose one of the sample benchmarks above.")


# -------------------------------------------------------------
# PAGE 2: UPLOAD DATASET
# -------------------------------------------------------------
elif selected_page == "2. Upload Dataset":
    st.markdown("## 📥 Ingest & Validate Dataset")
    st.markdown("Upload your structured CSV or Excel workbook. DataPilot AI validates schema, size, and encoding.")

    uploaded_file = st.file_uploader("Upload CSV or XLSX file", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df, summary = load_dataset(uploaded_file, uploaded_file.name)
            update_dataset(df, uploaded_file.name)
            st.success(f"Successfully loaded '{uploaded_file.name}' ({summary['rows']:,} rows, {summary['columns']} columns)!")
        except DataLoaderError as e:
            st.error(f"Validation Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected file error: {str(e)}")

    if st.session_state.df is not None:
        st.markdown("---")
        st.markdown("### 📋 Dataset Metadata")
        ov = st.session_state.profile_data.get("overview", {}) if st.session_state.profile_data else {}

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Total Observations</div>
                    <div class="metric-value">{len(st.session_state.df):,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Feature Columns</div>
                    <div class="metric-value">{len(st.session_state.df.columns)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Numerical Features</div>
                    <div class="metric-value">{ov.get('numerical_columns_count', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Categorical Features</div>
                    <div class="metric-value">{ov.get('categorical_columns_count', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### Preview Ingested Table")
        st.dataframe(st.session_state.df.head(10), use_container_width=True)


# -------------------------------------------------------------
# PAGE 3: DATA OVERVIEW & PROFILING
# -------------------------------------------------------------
elif selected_page == "3. Data Overview":
    if st.session_state.df is None:
        st.warning("Please upload a dataset or load a benchmark from the **Upload Dataset** tab.")
    else:
        st.markdown("## 🔍 Deep Data Profiling")
        prof = st.session_state.profile_data
        ov = prof.get("overview", {})

        # Overview Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", f"{ov.get('rows', 0):,}")
        c2.metric("Missing Values", f"{ov.get('total_missing', 0):,} ({ov.get('missing_pct', 0)}%)")
        c3.metric("Duplicate Rows", f"{ov.get('duplicate_rows', 0):,} ({ov.get('duplicate_pct', 0)}%)")
        c4.metric("Constant Columns", f"{ov.get('constant_columns_count', 0)}")

        # Suspicious Column Flags
        suspicious = ov.get("suspicious_columns", [])
        if suspicious:
            st.markdown("### ⚠️ Suspicious Feature Flags")
            for s in suspicious:
                severity_color = "red" if s["severity"] == "high" else "orange"
                st.warning(f"**{s['column']}** ({s['reason']}): {s['detail']}")

        # Column-by-column breakdown table
        st.markdown("### 📊 Column-Level Characteristics")
        col_records = []
        for c in prof.get("columns", []):
            rec = {
                "Column": c["name"],
                "Type": c.get("type_category", "unknown"),
                "Dtype": c["dtype"],
                "Missing %": c["missing_pct"],
                "Unique Values": c["unique_count"],
                "Mean": c.get("mean"),
                "Median": c.get("median"),
                "Std Dev": c.get("std"),
                "Min": c.get("min"),
                "Max": c.get("max"),
                "Skewness": c.get("skewness"),
            }
            col_records.append(rec)

        st.dataframe(pd.DataFrame(col_records), use_container_width=True)


# -------------------------------------------------------------
# PAGE 4: DATA QUALITY ENGINE
# -------------------------------------------------------------
elif selected_page == "4. Data Quality":
    if st.session_state.df is None:
        st.warning("Please upload a dataset or load a benchmark first.")
    else:
        st.markdown("## 🛡️ Data Quality & Automated Cleaner")
        qual = st.session_state.quality_data
        issues = qual.get("issues", [])

        st.markdown(f"**Total Quality Diagnostic Signals:** `{len(issues)}`")

        if issues:
            for iss in issues:
                st.info(f"**[{iss.get('type')}]** {iss.get('title')} — {iss.get('description')}")

        st.markdown("---")
        st.markdown("### 🧹 Apply Cleaning Transformations")
        st.caption("DataPilot maintains an immutable copy of your original dataset. Cleaning creates a separate `cleaned_df` object.")

        c1, c2, c3 = st.columns(3)
        with c1:
            do_dedup = st.checkbox("Deduplicate identical rows", value=True)
            do_drop_const = st.checkbox("Drop zero-variance constant columns", value=True)
        with c2:
            do_impute = st.checkbox("Impute missing values (median/mode)", value=True)
            do_cap_outliers = st.checkbox("Cap extreme IQR outliers (Winsorization)", value=False)
        with c3:
            num_cols = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()
            selected_outlier_cols = st.multiselect("Columns for outlier capping", options=num_cols)

        if st.button("Generate Cleaned Dataset", type="primary"):
            cleaned, logs = clean_dataset(
                st.session_state.df,
                drop_duplicates=do_dedup,
                drop_constant_cols=do_drop_const,
                impute_missing=do_impute,
                cap_outliers=do_cap_outliers,
                outlier_cols=selected_outlier_cols,
            )
            st.session_state.cleaned_df = cleaned
            st.success(f"Cleaned dataset created ({len(cleaned):,} rows, {len(cleaned.columns)} columns)!")
            for l in logs:
                st.write(f"✓ {l}")

        if st.session_state.cleaned_df is not None:
            st.markdown("#### Cleaned Dataset Preview")
            st.dataframe(st.session_state.cleaned_df.head(10), use_container_width=True)

            csv_buffer = st.session_state.cleaned_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Cleaned CSV",
                data=csv_buffer,
                file_name=f"cleaned_{st.session_state.filename or 'dataset.csv'}",
                mime="text/csv",
            )


# -------------------------------------------------------------
# PAGE 5: EXPLORATORY DATA ANALYSIS (EDA)
# -------------------------------------------------------------
elif selected_page == "5. EDA":
    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
    else:
        st.markdown("## 📈 Exploratory Data Analysis")
        df_to_plot = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else st.session_state.df

        tab1, tab2, tab3, tab4 = st.tabs(["Distributions", "Categorical Frequencies", "Correlation Heatmap", "Bivariate Scatters"])

        with tab1:
            num_cols = df_to_plot.select_dtypes(include=[np.number]).columns.tolist()
            if num_cols:
                sel_num = st.selectbox("Select Numerical Feature", num_cols, key="eda_num")
                fig_dist = plot_numerical_distribution(df_to_plot, sel_num)
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("No numerical features available.")

        with tab2:
            cat_cols = [c for c in df_to_plot.columns if c not in num_cols]
            if cat_cols:
                sel_cat = st.selectbox("Select Categorical Feature", cat_cols, key="eda_cat")
                fig_cat = plot_categorical_frequency(df_to_plot, sel_cat)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No categorical features available.")

        with tab3:
            fig_corr = plot_correlation_heatmap(df_to_plot)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("At least 2 numerical features are required for correlation analysis.")

        with tab4:
            if len(num_cols) >= 2:
                c1, c2, c3 = st.columns(3)
                with c1:
                    x_axis = st.selectbox("X-Axis Feature", num_cols, index=0)
                with c2:
                    y_axis = st.selectbox("Y-Axis Feature", num_cols, index=1 if len(num_cols) > 1 else 0)
                with c3:
                    hue_col = st.selectbox("Color Hue (Optional)", [None] + list(df_to_plot.columns))
                fig_scat = plot_scatter_relationship(df_to_plot, x_axis, y_axis, color_col=hue_col)
                st.plotly_chart(fig_scat, use_container_width=True)
            else:
                st.info("Need at least 2 numerical features for scatter plots.")


# -------------------------------------------------------------
# PAGE 6: STATISTICAL ANALYSIS
# -------------------------------------------------------------
elif selected_page == "6. Statistics":
    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
    else:
        st.markdown("## 📐 Rigorous Statistical Analysis")
        df_stat = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else st.session_state.df

        tab_desc, tab_corr, tab_hyp = st.tabs(["Descriptive Statistics", "Correlation & P-Values", "Hypothesis Testing"])

        with tab_desc:
            st.markdown("### Parametric & Non-Parametric Descriptives")
            desc_table = compute_descriptive_stats(df_stat)
            if not desc_table.empty:
                st.dataframe(desc_table, use_container_width=True)
            else:
                st.info("No numerical features available.")

        with tab_corr:
            num_cols = df_stat.select_dtypes(include=[np.number]).columns.tolist()
            if len(num_cols) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    col_x = st.selectbox("Feature 1", num_cols, index=0, key="stat_col_x")
                with c2:
                    col_y = st.selectbox("Feature 2", num_cols, index=1 if len(num_cols) > 1 else 0, key="stat_col_y")

                if col_x and col_y and col_x != col_y:
                    pair_res = compute_pairwise_correlation_with_pvalues(df_stat, col_x, col_y)
                    if "error" in pair_res:
                        st.error(pair_res["error"])
                    else:
                        c_p, c_s = st.columns(2)
                        with c_p:
                            p_info = pair_res["pearson"]
                            st.metric("Pearson r", f"{p_info['coefficient']:.4f}")
                            st.caption(f"p-value: `{p_info['p_value']:.4e}` | Significant: `{p_info['statistically_significant']}`")
                            st.write(p_info["interpretation"])
                        with c_s:
                            s_info = pair_res["spearman"]
                            st.metric("Spearman Rank ρ", f"{s_info['rho']:.4f}")
                            st.caption(f"p-value: `{s_info['p_value']:.4e}` | Significant: `{s_info['statistically_significant']}`")
                            st.write(s_info["interpretation"])

                        st.info(f"⚠️ {pair_res['scientific_disclaimer']}")
            else:
                st.info("At least two numerical columns required.")

        with tab_hyp:
            st.markdown("### Inferential Hypothesis Testing Engine")
            test_type = st.selectbox(
                "Select Hypothesis Test",
                ["Two-Sample T-Test", "Mann-Whitney U Test", "Chi-Square Test"],
            )

            if test_type in ["Two-Sample T-Test", "Mann-Whitney U Test"]:
                num_cols = df_stat.select_dtypes(include=[np.number]).columns.tolist()
                cat_cols = [c for c in df_stat.columns if c not in num_cols]
                if num_cols and cat_cols:
                    c1, c2 = st.columns(2)
                    with c1:
                        num_var = st.selectbox("Numerical Metric Variable", num_cols)
                    with c2:
                        group_var = st.selectbox("Categorical Grouping Variable", cat_cols)

                    if st.button(f"Run {test_type}", type="primary"):
                        test_res = run_hypothesis_test(df_stat, test_type, num_var, group_var)
                        if "error" in test_res:
                            st.error(test_res["error"])
                        else:
                            st.success(test_res["conclusion"])
                            st.json(test_res)
                else:
                    st.info("Requires at least one numerical and one categorical variable.")

            elif test_type == "Chi-Square Test":
                cat_cols = [c for c in df_stat.columns if not pd.api.types.is_numeric_dtype(df_stat[c])]
                if len(cat_cols) >= 2:
                    c1, c2 = st.columns(2)
                    with c1:
                        c_var1 = st.selectbox("Categorical Feature 1", cat_cols, index=0)
                    with c2:
                        c_var2 = st.selectbox("Categorical Feature 2", cat_cols, index=1)
                    if st.button("Run Chi-Square Test", type="primary"):
                        chi_res = run_hypothesis_test(df_stat, "Chi-Square Test", c_var1, c_var2)
                        if "error" in chi_res:
                            st.error(chi_res["error"])
                        else:
                            st.success(chi_res["conclusion"])
                            st.json(chi_res)
                else:
                    st.info("Requires at least 2 categorical variables for Chi-Square test.")


# -------------------------------------------------------------
# PAGE 7: ML LAB & MODEL BENCHMARKING
# -------------------------------------------------------------
elif selected_page == "7. ML Lab":
    if st.session_state.df is None:
        st.warning("Please upload a dataset or load a sample first.")
    else:
        st.markdown("## 🧪 Autonomous Machine Learning Lab")
        df_ml = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else st.session_state.df

        # Target Selection & Problem Detection
        col_tgt1, col_tgt2 = st.columns([1.2, 0.8])
        with col_tgt1:
            all_cols = ["None (Unsupervised Mode)"] + list(df_ml.columns)
            default_tgt = st.session_state.target_col if st.session_state.target_col in df_ml.columns else all_cols[0]
            selected_target = st.selectbox("Designate Target Column", all_cols, index=all_cols.index(default_tgt))

        with col_tgt2:
            if selected_target != "None (Unsupervised Mode)":
                prob_info = detect_problem_type(df_ml, target_col=selected_target)
                detected_prob = prob_info["problem_type"]
                st.markdown(f"**Detected Formulation:** <span class='badge-pill badge-blue'>{detected_prob}</span>", unsafe_allow_html=True)
                st.caption(prob_info.get("description", ""))
            else:
                detected_prob = "Unsupervised Analysis"
                st.markdown("**Detected Formulation:** <span class='badge-pill badge-amber'>Unsupervised Analysis</span>", unsafe_allow_html=True)

        st.session_state.target_col = None if selected_target == "None (Unsupervised Mode)" else selected_target
        if st.session_state.target_col is not None:
            st.session_state.quality_data = analyze_data_quality(
                df_ml,
                target_col=st.session_state.target_col
    )
        st.session_state.problem_type = detected_prob

        # Model Training Trigger
        st.markdown("---")
        c_split, c_cv = st.columns(2)
        with c_split:
            test_size = st.slider("Test Hold-Out Ratio", 0.15, 0.35, 0.20, 0.05)
        with c_cv:
            cv_folds = st.slider("Cross-Validation Folds", 2, 5, 3, 1)

        if st.button("🚀 Run Automated Model Training Pipeline", type="primary", use_container_width=True):
            prog_bar = st.progress(0.0)
            status_text = st.empty()

            def progress_cb(pct: float, msg: str):
                prog_bar.progress(pct)
                status_text.write(f"⚡ {msg}")

            try:
                if st.session_state.problem_type == "Unsupervised Analysis":
                    results = train_unsupervised_models(df_ml)
                    st.session_state.ml_results = results
                    st.success("Unsupervised K-Means clustering and PCA projections completed!")
                else:
                    results = train_supervised_models(
                        df=df_ml,
                        target_col=st.session_state.target_col,
                        problem_type=st.session_state.problem_type,
                        test_size=test_size,
                        cv_folds=cv_folds,
                        progress_callback=progress_cb,
                    )
                    st.session_state.ml_results = results
                    st.session_state.insights_data = generate_automated_insights(
                        st.session_state.profile_data,
                        st.session_state.quality_data,
                        results,
                    )
                    st.success(f"Automated benchmarking complete! Top Performer: **{results['best_model_name']}**")
            except Exception as e:
                st.error(f"Training failed: {str(e)}")

        # Display ML Results
        if st.session_state.ml_results:
            ml_res = st.session_state.ml_results

            if ml_res.get("problem_type") == "Unsupervised Analysis":
                st.markdown("### 🧬 Unsupervised Clustering & PCA Projection")
                c_k, c_pca = st.columns(2)
                with c_k:
                    st.markdown("#### Optimal Clusters (Elbow Curve)")
                    st.dataframe(ml_res["elbow_df"], use_container_width=True)
                with c_pca:
                    st.markdown("#### 2D PCA Cluster Distribution")
                    pca_coords = ml_res["pca_coords"]
                    labels = ml_res["cluster_labels"]
                    fig_pca = px.scatter(
                        x=pca_coords[:, 0],
                        y=pca_coords[:, 1],
                        color=[f"Cluster {l}" for l in labels],
                        title="PCA Projection (2 Dimensions)",
                        labels={"x": f"PC 1 ({ml_res['pca_variance'][0]}%)", "y": f"PC 2 ({ml_res['pca_variance'][1]}%)"},
                    )
                    st.plotly_chart(fig_pca, use_container_width=True)
            else:
                st.markdown("### 🏆 Model Comparison Leaderboard")
                results_df = ml_res["results_df"]
                display_cols = [c for c in results_df.columns if c not in ["confusion_matrix", "classes"]]
                st.dataframe(results_df[display_cols], use_container_width=True)

                # Leaderboard Bar Chart
                metric_to_plot = "F1-Score (Macro)" if "Classification" in ml_res["problem_type"] else "R²"
                fig_comp = px.bar(
                    results_df,
                    x="Model",
                    y=metric_to_plot,
                    color=metric_to_plot,
                    color_continuous_scale="Blues",
                    title=f"Algorithm Comparison ({metric_to_plot})",
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                # Model-specific feature attribution chart
                best_name = ml_res["best_model_name"]
                importances = ml_res.get("feature_importances", {}).get(best_name, {})
                if importances:
                    attributions = ml_res.get("feature_attributions", {}).get(best_name, [])
                    is_logistic = "Logistic" in best_name
                    is_coefficient = (
                        (bool(attributions) and attributions[0].get("method") == "coefficient")
                        or any(model_name in best_name for model_name in ("Logistic", "Ridge", "Linear"))
                    )
                    metric_name = (
                        "Absolute Model Coefficient Magnitude"
                        if is_coefficient
                        else "Tree Feature Importance"
                    )
                    st.markdown(f"### Model Feature Attribution ({best_name})")
                    if attributions:
                        imp_df = pd.DataFrame([
                            {
                                "Feature": item["feature"],
                                metric_name: item["value"],
                                "Coefficient": item.get("coefficient"),
                                "Direction": item.get("direction"),
                            }
                            for item in attributions
                        ]).sort_values(by=metric_name, ascending=True)
                        if is_logistic and is_coefficient:
                            st.caption("Binary coefficient sign indicates direction on the model decision score/log-odds for the positive class; this is not causal evidence.")
                    else:
                        imp_df = pd.DataFrame(list(importances.items()), columns=["Feature", metric_name]).sort_values(by=metric_name, ascending=True)
                    fig_imp = px.bar(
                        imp_df,
                        x=metric_name,
                        y="Feature",
                        orientation="h",
                        color=metric_name,
                        color_continuous_scale="Viridis",
                        title=f"{metric_name} for {best_name}",
                    )
                    st.plotly_chart(fig_imp, use_container_width=True)


# -------------------------------------------------------------
# PAGE 8: PREDICTIONS
# -------------------------------------------------------------
elif selected_page == "8. Predictions":
    if not st.session_state.ml_results or "best_model_pipeline" not in st.session_state.ml_results:
        st.warning("Please train models in the **ML Lab** tab first before generating predictions.")
    else:
        st.markdown("## 🔮 Inference & Prediction Engine")
        ml_res = st.session_state.ml_results
        pipeline = ml_res["best_model_pipeline"]
        best_model_name = ml_res["best_model_name"]
        raw_features = ml_res["raw_features_used"]
        prob_type = ml_res["problem_type"]
        target_col = ml_res["target_col"]

        st.info(f"Using winning model: **{best_model_name}** | Problem Formulation: **{prob_type}**")

        tab_single, tab_batch, tab_hist = st.tabs(["Single Prediction", "Batch Prediction (CSV)", "Prediction History (SQLite)"])

        with tab_single:
            st.markdown("### 📝 Dynamic Schema Input Form")
            st.caption("Enter feature values to compute instantaneous model inference:")

            input_dict = {}
            df_src = st.session_state.df

            # Generate dynamic UI widgets based on data dtypes
            cols_per_row = 3
            chunks = [raw_features[i : i + cols_per_row] for i in range(0, len(raw_features), cols_per_row)]

            for chunk in chunks:
                ui_cols = st.columns(len(chunk))
                for c_ui, feat_name in zip(ui_cols, chunk):
                    series = df_src[feat_name].dropna()
                    with c_ui:
                        if pd.api.types.is_numeric_dtype(series):
                            min_val = float(series.min())
                            max_val = float(series.max())
                            mean_val = float(series.mean())
                            step = (max_val - min_val) / 100.0 if max_val > min_val else 1.0
                            input_dict[feat_name] = st.number_input(
                                f"{feat_name}",
                                value=mean_val,
                                min_value=min_val - (abs(min_val) * 0.5),
                                max_value=max_val + (abs(max_val) * 0.5),
                                step=step,
                            )
                        else:
                            options = list(series.astype(str).unique())[:30]
                            input_dict[feat_name] = st.selectbox(f"{feat_name}", options)

            if st.button("🔮 Predict Single Outcome", type="primary"):
                try:
                    pred_res = predict_single(
                        pipeline=pipeline,
                        input_dict=input_dict,
                        problem_type=prob_type,
                        dataset_name=st.session_state.filename or "dataset",
                        target_col=target_col,
                        model_name=best_model_name,
                    )
                    st.success(f"**Prediction Result ({target_col}):** `{pred_res['prediction']}`")
                    if pred_res.get("confidence"):
                        st.metric("Model Confidence", f"{pred_res['confidence']*100:.1f}%")
                    if pred_res.get("probabilities"):
                        st.json(pred_res["probabilities"])
                except Exception as e:
                    st.error(f"Inference error: {str(e)}")

        with tab_batch:
            st.markdown("### 📂 Batch Prediction Upload")
            st.caption("Upload a CSV file with matching feature schema to score all rows simultaneously.")

            batch_file = st.file_uploader("Upload Batch CSV", type=["csv"], key="batch_uploader")
            if batch_file:
                try:
                    batch_df, _ = load_dataset(batch_file, batch_file.name)
                    st.write(f"Loaded batch file with {len(batch_df):,} records.")
                    if st.button("Run Batch Inference", type="primary"):
                        scored_df, summary = predict_batch(
                            pipeline=pipeline,
                            batch_df=batch_df,
                            required_features=raw_features,
                            problem_type=prob_type,
                            dataset_name=batch_file.name,
                            target_col=target_col,
                            model_name=best_model_name,
                        )
                        st.success(f"Scored {summary['total_rows_scored']:,} records successfully!")
                        st.dataframe(scored_df.head(10), use_container_width=True)

                        out_csv = scored_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "📥 Download Scored Batch CSV",
                            data=out_csv,
                            file_name=f"scored_{batch_file.name}",
                            mime="text/csv",
                        )
                except Exception as e:
                    st.error(f"Batch prediction error: {str(e)}")

        with tab_hist:
            st.markdown("### 📜 SQLite Prediction Audit Trail")
            hist_df = get_prediction_history(limit=50)
            if not hist_df.empty:
                st.dataframe(hist_df, use_container_width=True)
                if st.button("Clear Prediction Audit Trail"):
                    clear_prediction_history()
                    st.success("Audit trail cleared.")
                    st.rerun()
            else:
                st.info("No predictions logged in SQLite database yet.")


# -------------------------------------------------------------
# PAGE 9: AI INSIGHTS & CHATBOT
# -------------------------------------------------------------
elif selected_page == "9. AI Insights & Chat":
    st.markdown("## 🧠 AI Insights & Autonomous Data Scientist Chat")

    tab_insights, tab_chat = st.tabs(["Automated Insights", "Ask DataPilot AI (Chatbot)"])

    with tab_insights:
        if not st.session_state.insights_data:
            st.info("Upload and profile a dataset to generate automated insights.")
        else:
            ins = st.session_state.insights_data
            c_exec, c_tech = st.columns(2)

            with c_exec:
                st.markdown("### 👔 Executive Summary (Non-Technical)")
                for pt in ins.get("executive_insights", []):
                    st.markdown(f"- {pt}")

            with c_tech:
                st.markdown("### 🔬 Technical Insights (Data Science)")
                for pt in ins.get("technical_insights", []):
                    st.markdown(f"- {pt}")

    with tab_chat:
        st.markdown("### 💬 Ask DataPilot AI")
        st.caption("Ask questions about feature distributions, missingness, model performance, or statistical interpretations:")

        # Render message history
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ask about this dataset or ML models (e.g. 'What are the top features?')")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # Generate grounded response
            bot_reply = answer_datapilot_query(
                user_query=user_input,
                profile_data=st.session_state.profile_data,
                quality_data=st.session_state.quality_data,
                ml_results=st.session_state.ml_results,
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.write(bot_reply)


# -------------------------------------------------------------
# PAGE 10: REPORTS
# -------------------------------------------------------------
elif selected_page == "10. Reports":
    if st.session_state.df is None:
        st.warning("Please upload a dataset or load a sample first.")
    else:
        st.markdown("## 📄 Automated PDF Executive Report")
        st.markdown(
            "Generate a multi-page PDF summary compiling dataset profiles, quality flags, "
            "model benchmarking leaderboards, top feature importances, and statistical disclaimers."
        )

        report_filename = f"datapilot_report_{int(time.time())}.pdf"
        report_path = os.path.join(os.path.dirname(__file__), "reports", report_filename)

        if st.button("📄 Generate Comprehensive PDF Report", type="primary"):
            with st.spinner("Compiling ReportLab PDF document..."):
                try:
                    pdf_file = generate_pdf_report(
                        filename_or_path=report_path,
                        dataset_name=st.session_state.filename or "Uploaded Dataset",
                        profile_data=st.session_state.profile_data,
                        quality_data=st.session_state.quality_data,
                        ml_results=st.session_state.ml_results,
                        insights_data=st.session_state.insights_data,
                    )
                    st.success("PDF Report successfully compiled!")

                    with open(pdf_file, "rb") as f:
                        pdf_bytes = f.read()

                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=report_filename,
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"Failed to compile PDF report: {str(e)}")
