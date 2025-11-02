"""Dependency injection for agents.

Factory functions to create configured agent instances.
"""
import os
from pathlib import Path
from typing import Optional
import yaml

from claude_agent_sdk.archetypes import ResearchAgent, ContentCreatorAgent, ReportingAgent
from claude_agent_sdk.integrations.yarnnn import YarnnnMemory, YarnnnGovernance


def load_agent_config(agent_type: str) -> dict:
    """Load agent configuration from YAML file.

    Args:
        agent_type: Type of agent (research, content, reporting)

    Returns:
        Configuration dictionary
    """
    config_path = Path(__file__).parent.parent / "agents" / agent_type / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def get_yarnnn_providers(basket_id: str):
    """Create Yarnnn memory and governance providers.

    Args:
        basket_id: Yarnnn basket ID for this agent

    Returns:
        Tuple of (YarnnnMemory, YarnnnGovernance)
    """
    # Get credentials from environment
    api_key = os.getenv("YARNNN_API_KEY")
    workspace_id = os.getenv("YARNNN_WORKSPACE_ID")
    api_url = os.getenv("YARNNN_API_URL")

    if not all([api_key, workspace_id, api_url]):
        raise ValueError(
            "Missing required environment variables: "
            "YARNNN_API_KEY, YARNNN_WORKSPACE_ID, YARNNN_API_URL"
        )

    memory = YarnnnMemory(
        basket_id=basket_id,
        api_key=api_key,
        workspace_id=workspace_id,
        api_url=api_url
    )

    governance = YarnnnGovernance(
        basket_id=basket_id,
        api_key=api_key,
        workspace_id=workspace_id,
        api_url=api_url
    )

    return memory, governance


def create_research_agent() -> ResearchAgent:
    """Create configured research agent instance.

    Returns:
        Configured ResearchAgent
    """
    config = load_agent_config("research")

    # Get Yarnnn providers
    basket_id = os.getenv("RESEARCH_BASKET_ID")
    if not basket_id:
        raise ValueError("RESEARCH_BASKET_ID environment variable required")

    memory, governance = get_yarnnn_providers(basket_id)

    # Get Anthropic API key
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable required")

    # Create agent
    return ResearchAgent(
        agent_id=config["agent"]["id"],
        memory=memory,
        governance=governance,
        anthropic_api_key=anthropic_api_key,
        monitoring_domains=config["research"]["monitoring_domains"],
        monitoring_frequency=config["research"]["monitoring_frequency"],
        signal_threshold=config["research"]["signal_threshold"],
        synthesis_mode=config["research"]["synthesis_mode"]
    )


def create_content_agent() -> ContentCreatorAgent:
    """Create configured content creator agent instance.

    Returns:
        Configured ContentCreatorAgent

    Raises:
        NotImplementedError: Endpoint not yet configured
    """
    # TODO: Implement after research agent is validated
    raise NotImplementedError("Content agent not yet configured")


def create_reporting_agent() -> ReportingAgent:
    """Create configured reporting agent instance.

    Returns:
        Configured ReportingAgent

    Raises:
        NotImplementedError: Endpoint not yet configured
    """
    # TODO: Implement after research agent is validated
    raise NotImplementedError("Reporting agent not yet configured")
