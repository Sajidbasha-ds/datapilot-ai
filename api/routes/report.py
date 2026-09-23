"""PDF Report generation and download routes."""

from __future__ import annotations

import os
import tempfile
from fastapi import APIRouter
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from api.models.schemas import ApiResponse
from api.services.session_store import session_manager
from src.insights import generate_automated_insights
from src.report_generator import generate_pdf_report

router = APIRouter(prefix="/report", tags=["report"])


class ReportRequest(BaseModel):
    session_id: str


@router.post("/generate")
def create_report(req: ReportRequest):
    """Generates the comprehensive PDF report and returns metadata."""
    session = session_manager.get_session(req.session_id)
    if not session:
        return ApiResponse(success=False, error={"code": "SESSION_NOT_FOUND", "message": "Session expired."})

    profile_data = session.profile_data or {}
    quality_data = session.quality_data or {}
    ml_results = session.ml_results

    try:
        insights = session.insights_data or generate_automated_insights(
            profile_data=profile_data,
            quality_data=quality_data,
            ml_results=ml_results,
        )

        # Temporary path for report output
        temp_dir = tempfile.gettempdir()
        report_filename = f"DataPilot_Executive_Report_{session.filename.replace('.', '_')}.pdf"
        report_path = os.path.join(temp_dir, report_filename)

        generated_path = generate_pdf_report(
            filename_or_path=report_path,
            dataset_name=session.filename,
            profile_data=profile_data,
            quality_data=quality_data,
            ml_results=ml_results,
            insights_data=insights,
        )

        return ApiResponse(
            success=True,
            data={
                "report_filename": report_filename,
                "file_size": os.path.getsize(generated_path),
                "generated_at": session.updated_at,
            },
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error={"code": "REPORT_GEN_FAILED", "message": f"Failed to generate PDF report: {str(e)}"},
        )


@router.get("/download/{session_id}")
def download_report(session_id: str):
    """Streams the generated PDF report directly to the browser for download."""
    session = session_manager.get_session(session_id)
    if not session:
        return Response(content="Session expired", status_code=404)

    temp_dir = tempfile.gettempdir()
    report_filename = f"DataPilot_Executive_Report_{session.filename.replace('.', '_')}.pdf"
    report_path = os.path.join(temp_dir, report_filename)

    # If not already generated, generate now
    if not os.path.exists(report_path):
        profile_data = session.profile_data or {}
        quality_data = session.quality_data or {}
        ml_results = session.ml_results
        insights = session.insights_data or generate_automated_insights(
            profile_data=profile_data,
            quality_data=quality_data,
            ml_results=ml_results,
        )
        report_path = generate_pdf_report(
            filename_or_path=report_path,
            dataset_name=session.filename,
            profile_data=profile_data,
            quality_data=quality_data,
            ml_results=ml_results,
            insights_data=insights,
        )

    with open(report_path, "rb") as f:
        pdf_bytes = f.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{report_filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )
