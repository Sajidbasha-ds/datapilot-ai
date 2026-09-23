"""FastAPI application entrypoint for DataPilot AI.
Serves REST API routes for both local development and Vercel serverless deployment.
"""

from __future__ import annotations

import os
import sys

# Ensure root workspace directory is in python search path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import dataset, eda, insights, ml, predict, report, statistics

app = FastAPI(
    title="DataPilot AI API",
    description="Autonomous AI Data Scientist REST API Engine",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to format errors cleanly as JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "type": exc.__class__.__name__,
            },
        },
    )

# Mount modular routers under /api prefix
app.include_router(dataset.router, prefix="/api")
app.include_router(eda.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(ml.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/api")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DataPilot AI Engine",
        "version": "2.0.0",
        "capabilities": [
            "profiling",
            "quality_audit",
            "eda",
            "statistics",
            "automl_benchmark",
            "predictions",
            "insights",
            "pdf_reports",
        ],
    }
