"""Reporting agent API endpoints."""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ReportingTaskRequest(BaseModel):
    """Request model for reporting tasks (placeholder)."""
    task_type: str
    report_format: str = "pdf"


class ReportingTaskResponse(BaseModel):
    """Response model for reporting tasks (placeholder)."""
    status: str
    message: str


@router.post("/run", response_model=ReportingTaskResponse)
async def run_reporting_task(request: ReportingTaskRequest):
    """Trigger reporting agent task.

    This endpoint is called by Yarnnn main service to trigger report generation.

    NOTE: This is a placeholder. Configure after ResearchAgent is validated.

    Args:
        request: Reporting task request

    Returns:
        Task execution result
    """
    logger.warning("Reporting agent endpoint called but not yet implemented")

    raise HTTPException(
        status_code=501,
        detail="Reporting agent not yet configured. "
               "Wire up ResearchAgent first, then add ReportingAgent."
    )


@router.get("/status")
async def get_reporting_agent_status():
    """Get reporting agent status.

    Returns:
        Agent status information
    """
    return {
        "status": "not_configured",
        "message": "Reporting agent not yet configured. Coming soon after ResearchAgent validation."
    }
