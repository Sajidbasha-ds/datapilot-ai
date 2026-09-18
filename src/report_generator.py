"""Automated PDF Executive Report Generator using ReportLab for DataPilot AI."""

from __future__ import annotations

from datetime import datetime
import os
from typing import Any, Dict, List, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(
    filename_or_path: str,
    dataset_name: str,
    profile_data: Dict[str, Any],
    quality_data: Dict[str, Any],
    ml_results: Optional[Dict[str, Any]] = None,
    insights_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Creates a publication-quality multi-page PDF summary of the complete Data Science lifecycle."""
    report_dir = os.path.dirname(filename_or_path)
    if report_dir and not os.path.exists(report_dir):
        os.makedirs(report_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        filename_or_path,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom Clean Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E293B"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#3B82F6"),
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    bullet_style = ParagraphStyle(
        "BulletPoint",
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=4,
    )

    story: List[Any] = []

    # 1. Header Banner
    story.append(Paragraph("DATAPILOT AI", subtitle_style))
    story.append(Paragraph("Autonomous Data Science & ML Executive Report", title_style))
    story.append(Spacer(1, 4))
    gen_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    story.append(Paragraph(f"<b>Dataset:</b> {dataset_name} &nbsp;|&nbsp; <b>Generated:</b> {gen_time}", body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=14))

    # 2. Executive Overview Table
    story.append(Paragraph("1. Dataset Ingestion & Profiling Overview", section_style))
    ov = profile_data.get("overview", {})

    overview_table_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Rows", f"{ov.get('rows', 0):,}", "Total Columns", str(ov.get("columns", 0))],
        ["Missing Cells", f"{ov.get('total_missing', 0):,} ({ov.get('missing_pct', 0)}%)", "Duplicate Rows", f"{ov.get('duplicate_rows', 0):,} ({ov.get('duplicate_pct', 0)}%)"],
        ["Numerical Features", str(ov.get("numerical_columns_count", 0)), "Categorical Features", str(ov.get("categorical_columns_count", 0))],
        ["Datetime Features", str(ov.get("datetime_columns_count", 0)), "Suspicious Columns", str(ov.get("suspicious_count", 0))],
    ]

    t_overview = Table(overview_table_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch])
    t_overview.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 14))

    # 3. Data Quality Engine Findings
    story.append(Paragraph("2. Data Quality Audit & Hygiene", section_style))
    issues = quality_data.get("issues", [])
    if not issues:
        story.append(Paragraph("No critical data quality issues identified. Dataset is clean and balanced.", body_style))
    else:
        for iss in issues[:5]:
            story.append(Paragraph(f"• <b>{iss.get('type')}:</b> {iss.get('title')} - {iss.get('description')}", bullet_style))
    story.append(Spacer(1, 12))

    # 4. Machine Learning Benchmarks & Comparison
    if ml_results and "results_df" in ml_results:
        prob_type = ml_results.get("problem_type", "Supervised Learning")
        target_col = ml_results.get("target_col", "Target")
        best_model = ml_results.get("best_model_name", "Top Model")
        results_df: pd.DataFrame = ml_results["results_df"]

        story.append(Paragraph(f"3. Machine Learning Model Leaderboard ({prob_type})", section_style))
        story.append(Paragraph(f"Target Column: <b>{target_col}</b> &nbsp;|&nbsp; Top Performer: <b>{best_model}</b>", body_style))
        story.append(Spacer(1, 6))

        # Format comparison table
        display_df = results_df.copy().head(5)
        # Select numeric columns to format
        header_cols = [c for c in display_df.columns if c not in ["confusion_matrix", "classes"]]
        table_rows = [header_cols]
        for _, r in display_df[header_cols].iterrows():
            row_vals = []
            for h in header_cols:
                v = r[h]
                row_vals.append(str(v) if not isinstance(v, float) else f"{v:.4f}")
            table_rows.append(row_vals)

        col_w = (7.2 * inch) / len(header_cols)
        t_models = Table(table_rows, colWidths=[col_w] * len(header_cols))
        t_models.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_models)
        story.append(Spacer(1, 14))

        # Top Features
        importances = ml_results.get("feature_importances", {}).get(best_model, {})
        if importances:
            story.append(Paragraph("4. Key Predictive Feature Drivers", section_style))
            feat_table_data = [["Rank", "Feature Name", "Importance Score"]]
            for rank, (fname, fscore) in enumerate(list(importances.items())[:6], 1):
                feat_table_data.append([str(rank), fname, f"{fscore:.4f}"])

            t_feat = Table(feat_table_data, colWidths=[1.0 * inch, 4.2 * inch, 2.0 * inch])
            t_feat.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(t_feat)
            story.append(Spacer(1, 14))

    # 5. Automated AI Insights & Explanations
    story.append(Paragraph("5. AI-Synthesized Insights & Recommendations", section_style))
    if insights_data:
        for pt in insights_data.get("executive_insights", [])[:4]:
            story.append(Paragraph(f"• <b>Executive Insight:</b> {pt}", bullet_style))
        for pt in insights_data.get("technical_insights", [])[:3]:
            story.append(Paragraph(f"• <b>Technical Detail:</b> {pt}", bullet_style))
    else:
        story.append(Paragraph("No automated insights configured for this run.", body_style))
    story.append(Spacer(1, 14))

    # 6. Scientific Limitations & Disclaimers
    story.append(Paragraph("6. Statistical Assumptions & Methodological Disclaimers", section_style))
    disclaimer_text = (
        "This autonomous report is algorithmically compiled by DataPilot AI. All preprocessing was isolated to training partitions "
        "to prevent data leakage. Statistical tests assume independence of observations and appropriate distributional traits. "
        "Correlations reflect mathematical associations and MUST NOT be construed as empirical causal relationships."
    )
    story.append(Paragraph(disclaimer_text, body_style))

    # Build PDF document
    doc.build(story)
    return filename_or_path
