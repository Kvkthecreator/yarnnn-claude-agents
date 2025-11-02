"""FastAPI application for Yarnnn agent deployment service.

This service exposes HTTP endpoints that Yarnnn main service calls to trigger agents.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import research, content, reporting

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    logger.info("Starting Yarnnn Agent Deployment Service")
    yield
    logger.info("Shutting down Yarnnn Agent Deployment Service")


# Create FastAPI app
app = FastAPI(
    title="Yarnnn Agent Deployment Service",
    description="HTTP API for triggering autonomous agents from Yarnnn main service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research.router, prefix="/agents/research", tags=["research"])
app.include_router(content.router, prefix="/agents/content", tags=["content"])
app.include_router(reporting.router, prefix="/agents/reporting", tags=["reporting"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Yarnnn Agent Deployment Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render and monitoring."""
    return {
        "status": "healthy",
        "service": "yarnnn-agents"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
