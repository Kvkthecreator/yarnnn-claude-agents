"""Content creator agent API endpoints."""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ContentTaskRequest(BaseModel):
    """Request model for content tasks (placeholder)."""
    task_type: str
    platform: str = "twitter"
    topic: str


class ContentTaskResponse(BaseModel):
    """Response model for content tasks (placeholder)."""
    status: str
    message: str


@router.post("/run", response_model=ContentTaskResponse)
async def run_content_task(request: ContentTaskRequest):
    """Trigger content creator agent task.

    This endpoint is called by Yarnnn main service to trigger content creation.

    NOTE: This is a placeholder. Configure after ResearchAgent is validated.

    Args:
        request: Content task request

    Returns:
        Task execution result
    """
    logger.warning("Content agent endpoint called but not yet implemented")

    raise HTTPException(
        status_code=501,
        detail="Content agent not yet configured. "
               "Wire up ResearchAgent first, then add ContentCreatorAgent."
    )


@router.get("/status")
async def get_content_agent_status():
    """Get content agent status.

    Returns:
        Agent status information
    """
    return {
        "status": "not_configured",
        "message": "Content agent not yet configured. Coming soon after ResearchAgent validation."
    }
