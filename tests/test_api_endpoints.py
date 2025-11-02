"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Yarnnn Agent Deployment Service"
    assert data["status"] == "running"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "yarnnn-agents"


def test_research_status_endpoint():
    """Test research agent status endpoint."""
    response = client.get("/agents/research/status")
    assert response.status_code == 200
    data = response.json()
    # Agent might be in error state if not configured, that's OK
    assert "status" in data


def test_content_status_endpoint():
    """Test content agent status endpoint (not yet configured)."""
    response = client.get("/agents/content/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_configured"


def test_reporting_status_endpoint():
    """Test reporting agent status endpoint (not yet configured)."""
    response = client.get("/agents/reporting/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_configured"


def test_content_agent_not_implemented():
    """Test that content agent returns 501 (not implemented)."""
    response = client.post(
        "/agents/content/run",
        json={"task_type": "create", "platform": "twitter", "topic": "test"}
    )
    assert response.status_code == 501


def test_reporting_agent_not_implemented():
    """Test that reporting agent returns 501 (not implemented)."""
    response = client.post(
        "/agents/reporting/run",
        json={"task_type": "generate", "report_format": "pdf"}
    )
    assert response.status_code == 501


# NOTE: Full research agent tests require valid configuration
# These would be added after wiring up with Yarnnn service
#
# @pytest.mark.integration
# def test_research_monitor_task():
#     """Test research monitoring task (requires configuration)."""
#     response = client.post(
#         "/agents/research/run",
#         json={"task_type": "monitor"}
#     )
#     assert response.status_code == 200
