"""Research agent API endpoints."""
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from api.dependencies import create_research_agent

logger = logging.getLogger(__name__)

router = APIRouter()


class ResearchTaskRequest(BaseModel):
    """Request model for research tasks."""
    task_type: str = Field(..., description="Type of research task (monitor, deep_dive)")
    topic: Optional[str] = Field(None, description="Topic for deep dive research")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")


class ResearchTaskResponse(BaseModel):
    """Response model for research tasks."""
    status: str
    task_id: Optional[str] = None
    message: str
    result: Optional[Dict[str, Any]] = None


@router.post("/run", response_model=ResearchTaskResponse)
async def run_research_task(request: ResearchTaskRequest):
    """Trigger research agent task.

    This endpoint is called by Yarnnn main service to trigger research tasks.

    Supported task types:
    - monitor: Run monitoring across configured domains
    - deep_dive: Deep research on specific topic

    Args:
        request: Research task request

    Returns:
        Task execution result
    """
    logger.info(f"Received research task: {request.task_type}")

    try:
        # Create agent instance
        agent = create_research_agent()

        # Execute based on task type
        if request.task_type == "monitor":
            logger.info("Running research monitoring")
            result = await agent.monitor()

            return ResearchTaskResponse(
                status="completed",
                message="Monitoring completed successfully",
                result=result
            )

        elif request.task_type == "deep_dive":
            if not request.topic:
                raise HTTPException(
                    status_code=400,
                    detail="Topic required for deep_dive tasks"
                )

            logger.info(f"Running deep dive research on: {request.topic}")
            result = await agent.deep_dive(request.topic)

            return ResearchTaskResponse(
                status="completed",
                message=f"Deep dive completed for topic: {request.topic}",
                result=result
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task type: {request.task_type}. "
                       f"Supported: monitor, deep_dive"
            )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

    except Exception as e:
        logger.error(f"Error executing research task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")


@router.get("/status")
async def get_research_agent_status():
    """Get research agent status and configuration.

    Returns:
        Agent status information
    """
    try:
        # Verify agent can be created
        agent = create_research_agent()

        return {
            "status": "ready",
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "message": "Research agent is configured and ready"
        }

    except Exception as e:
        logger.error(f"Error checking agent status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
