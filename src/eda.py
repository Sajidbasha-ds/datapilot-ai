"""Exploratory Data Analysis (EDA) visualization module using Plotly for DataPilot AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

# Modern, sleek color palette tokens
PRIMARY_COLOR = "#3B82F6"      # Indigo / Blue
SECONDARY_COLOR = "#10B981"    # Emerald Green
ACCENT_COLOR = "#F59E0B"       # Amber
DANGER_COLOR = "#EF4444"       # Rose / Red
PURPLE_COLOR = "#8B5CF6"       # Purple
BACKGROUND_DARK = "#0F172A"    # Slate 900
SURFACE_DARK = "#1E293B"       # Slate 800
TEXT_COLOR = "#F8FAFC"         # Slate 50


def get_plot_template() -> Dict[str, Any]:
    """Provides a consistent, modern dark-mode Plotly layout styling."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Roboto, sans-serif", color="#CBD5E1", size=12),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#475569"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#475569"),
    )


def sample_for_plotting(df: pd.DataFrame, max_rows: int = 5000) -> pd.DataFrame:
    """Downsamples high-volume datasets to maintain fluid 60fps browser interactions."""
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42)
    return df


def plot_numerical_distribution(df: pd.DataFrame, column: str) -> go.Figure:
    """Generates an interactive histogram with KDE/box marginal for numerical features."""
    sampled_df = sample_for_plotting(df)
    clean_series = sampled_df[column].dropna()

    fig = px.histogram(
        sampled_df,
        x=column,
        marginal="box",
        nbins=min(40, max(15, int(clean_series.nunique() / 2))),
        color_discrete_sequence=[PRIMARY_COLOR],
        title=f"Distribution & Spread: <b>{column}</b>",
        opacity=0.85,
    )
    fig.update_layout(**get_plot_template())
    fig.update_layout(bargap=0.05)
    return fig


def plot_categorical_frequency(df: pd.DataFrame, column: str, max_categories: int = 15) -> go.Figure:
    """Generates an interactive frequency bar chart for categorical variables."""
    sampled_df = sample_for_plotting(df)
    val_counts = sampled_df[column].astype(str).value_counts(dropna=False).head(max_categories).reset_index()
    val_counts.columns = ["Category", "Count"]

    total = val_counts["Count"].sum()
    val_counts["Percentage"] = ((val_counts["Count"] / total) * 100).round(1)

    fig = px.bar(
        val_counts,
        x="Category",
        y="Count",
        text=val_counts["Percentage"].astype(str) + "%",
        color="Count",
        color_continuous_scale="Blues",
        title=f"Category Breakdown: <b>{column}</b> (Top {len(val_counts)})",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(**get_plot_template())
    fig.update_layout(coloraxis_showscale=False)
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, max_cols: int = 20) -> Optional[go.Figure]:
    """Generates an annotated correlation heatmap for numerical attributes."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return None

    # Pick top columns by variance if there are too many columns
    if len(num_cols) > max_cols:
        variances = df[num_cols].var().sort_values(ascending=False)
        num_cols = variances.head(max_cols).index.tolist()

    corr_df = df[num_cols].corr(method="pearson").round(2)
    z_values = corr_df.values
    x_labels = corr_df.columns.tolist()
    y_labels = corr_df.index.tolist()

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=x_labels,
            y=y_labels,
            colorscale="RdBu",
            zmin=-1.0,
            zmax=1.0,
            colorbar=dict(title="Pearson r", thickness=15),
            text=np.around(z_values, 2),
            texttemplate="%{text}",
            textfont=dict(size=10),
            hoverongaps=False,
        )
    )
    fig.update_layout(
        title=f"Feature Correlation Matrix ({len(num_cols)} Numerical Features)",
        **get_plot_template(),
    )
    return fig


def plot_scatter_relationship(
    df: pd.DataFrame,
    col_x: str,
    col_y: str,
    color_col: Optional[str] = None,
    trendline: bool = True,
) -> go.Figure:
    """Generates a bivariate scatter plot with optional trendline and category hue."""
    sampled_df = sample_for_plotting(df)
    valid_color = color_col if (color_col and color_col in sampled_df.columns) else None

    # Trendline requires statsmodels; if not present, omit trendline gracefully
    trend = "ols" if trendline and pd.api.types.is_numeric_dtype(sampled_df[col_x]) and pd.api.types.is_numeric_dtype(sampled_df[col_y]) else None

    try:
        fig = px.scatter(
            sampled_df,
            x=col_x,
            y=col_y,
            color=valid_color,
            color_discrete_sequence=px.colors.qualitative.Prism,
            trendline=trend,
            title=f"Bivariate Analysis: <b>{col_x}</b> vs <b>{col_y}</b>",
            opacity=0.75,
        )
    except Exception:
        # Fallback without trendline if statsmodels isn't installed
        fig = px.scatter(
            sampled_df,
            x=col_x,
            y=col_y,
            color=valid_color,
            color_discrete_sequence=px.colors.qualitative.Prism,
            title=f"Bivariate Analysis: <b>{col_x}</b> vs <b>{col_y}</b>",
            opacity=0.75,
        )

    fig.update_layout(**get_plot_template())
    return fig


def plot_timeseries_trend(df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
    """Generates chronological trendline with 7-period rolling moving average."""
    sub_df = df[[date_col, value_col]].dropna().copy()
    sub_df[date_col] = pd.to_datetime(sub_df[date_col], errors="coerce")
    sub_df = sub_df.dropna().sort_values(by=date_col)

    # Compute rolling average
    sub_df["rolling_avg"] = sub_df[value_col].rolling(window=min(7, len(sub_df)), min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sub_df[date_col],
            y=sub_df[value_col],
            mode="lines+markers",
            name="Observed Value",
            line=dict(color=PRIMARY_COLOR, width=1.5),
            marker=dict(size=4),
            opacity=0.6,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sub_df[date_col],
            y=sub_df["rolling_avg"],
            mode="lines",
            name="Trend (Rolling Avg)",
            line=dict(color=ACCENT_COLOR, width=3),
        )
    )
    fig.update_layout(
        title=f"Time Series Dynamic: <b>{value_col}</b> over <b>{date_col}</b>",
        **get_plot_template(),
    )
    return fig
