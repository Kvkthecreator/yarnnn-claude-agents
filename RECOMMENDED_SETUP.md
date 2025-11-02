# Recommended Setup: Git Dependency Workflow

## Decision

**Use Option 2 (Git Dependency)** for production-ready deployment with rapid iteration capability.

## Why This Approach

### Your Situation
- Solo founder managing 3 repositories
- 90% of development in open source library
- 10% deployment/infrastructure in this repo
- Need production stability + development speed
- Want genuine open source (not just internal tool)

### Option 2 Benefits
- ✅ Production-ready (pinned versions)
- ✅ Fast iteration (tag + reinstall)
- ✅ No PyPI overhead during development
- ✅ Works in Docker/K8s
- ✅ Easy rollback to previous versions
- ✅ Clear version tracking

### Migration Path
- **Now → v0.9.x**: Git dependency (rapid development)
- **v1.0.0+**: Move to PyPI (stable public release)

## Implementation

### Step 1: Restructure This Repo

**Remove library code (it becomes a dependency):**

```bash
cd ~/yarnnn-claude-agents

# Create new structure
mkdir -p agents/{research,content,reporting}
mkdir -p deployment/{docker,kubernetes,serverless}
mkdir -p config
mkdir -p orchestration
mkdir -p monitoring

# Remove library code (comes from dependency now)
git rm -r claude_agent_sdk/
git rm -r tests/
git rm -r examples/  # Keep if you want deployment examples
```

**Update pyproject.toml:**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "yarnnn-agent-deployment"
version = "1.0.0"
description = "Production deployment for Yarnnn autonomous agents"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    # Library dependency (from open source)
    "claude-agent-sdk @ git+https://github.com/Kvkthecreator/claude-agentsdk-opensource.git@v0.1.0",

    # Production dependencies
    "apscheduler>=3.10.0",     # Scheduling
    "celery>=5.3.0",           # Task queue (optional)
    "redis>=5.0.0",            # Celery backend (optional)
    "prometheus-client>=0.19.0", # Metrics
    "sentry-sdk>=1.40.0",      # Error tracking
    "python-dotenv>=1.0.0",    # Environment management
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

### Step 2: Create Production Agent Configurations

**agents/research/config.yaml:**
```yaml
agent:
  id: yarnnn_research_agent
  type: research

yarnnn:
  basket_id: ${RESEARCH_BASKET_ID}
  api_url: ${YARNNN_API_URL}
  api_key: ${YARNNN_API_KEY}
  workspace_id: ${YARNNN_WORKSPACE_ID}

research:
  monitoring_domains:
    - competitors
    - market_trends
    - ai_agents
  monitoring_frequency: daily
  signal_threshold: 0.7
  synthesis_mode: insights

schedule:
  # Daily at 6am UTC
  cron: "0 6 * * *"
```

**agents/research/run.py:**
```python
"""Production research agent instance."""
import os
import asyncio
from pathlib import Path
import yaml
from dotenv import load_dotenv

from claude_agent_sdk.archetypes import ResearchAgent
from claude_agent_sdk.integrations.yarnnn import YarnnnMemory, YarnnnGovernance

# Load environment
load_dotenv()

# Load config
config_path = Path(__file__).parent / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

def create_agent() -> ResearchAgent:
    """Create configured research agent instance."""

    # Environment variables
    env_vars = {
        "RESEARCH_BASKET_ID": os.getenv("RESEARCH_BASKET_ID"),
        "YARNNN_API_URL": os.getenv("YARNNN_API_URL"),
        "YARNNN_API_KEY": os.getenv("YARNNN_API_KEY"),
        "YARNNN_WORKSPACE_ID": os.getenv("YARNNN_WORKSPACE_ID"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }

    # Validate
    missing = [k for k, v in env_vars.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

    # Create providers
    memory = YarnnnMemory(
        basket_id=env_vars["RESEARCH_BASKET_ID"],
        api_key=env_vars["YARNNN_API_KEY"],
        workspace_id=env_vars["YARNNN_WORKSPACE_ID"],
        api_url=env_vars["YARNNN_API_URL"]
    )

    governance = YarnnnGovernance(
        basket_id=env_vars["RESEARCH_BASKET_ID"],
        api_key=env_vars["YARNNN_API_KEY"],
        workspace_id=env_vars["YARNNN_WORKSPACE_ID"],
        api_url=env_vars["YARNNN_API_URL"]
    )

    # Create agent from config
    return ResearchAgent(
        agent_id=config["agent"]["id"],
        memory=memory,
        governance=governance,
        anthropic_api_key=env_vars["ANTHROPIC_API_KEY"],
        monitoring_domains=config["research"]["monitoring_domains"],
        monitoring_frequency=config["research"]["monitoring_frequency"],
        signal_threshold=config["research"]["signal_threshold"],
        synthesis_mode=config["research"]["synthesis_mode"]
    )

async def run_monitoring():
    """Run monitoring task."""
    agent = create_agent()
    print(f"Starting monitoring for agent: {agent.agent_id}")

    try:
        result = await agent.monitor()
        print(f"Monitoring completed successfully")
        return result
    except Exception as e:
        print(f"Monitoring failed: {e}")
        # Sentry reporting here
        raise

if __name__ == "__main__":
    asyncio.run(run_monitoring())
```

### Step 3: Set Up Deployment

**deployment/docker/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy agent configurations
COPY agents/ /app/agents/
COPY config/ /app/config/
COPY orchestration/ /app/orchestration/

# Default command (can override)
CMD ["python", "-m", "orchestration.scheduler"]
```

**deployment/docker/docker-compose.yml:**
```yaml
version: '3.8'

services:
  research-agent:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    environment:
      - YARNNN_API_URL=${YARNNN_API_URL}
      - YARNNN_API_KEY=${YARNNN_API_KEY}
      - YARNNN_WORKSPACE_ID=${YARNNN_WORKSPACE_ID}
      - RESEARCH_BASKET_ID=${RESEARCH_BASKET_ID}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python agents/research/run.py
    restart: unless-stopped

  scheduler:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    environment:
      - YARNNN_API_URL=${YARNNN_API_URL}
      - YARNNN_API_KEY=${YARNNN_API_KEY}
      - YARNNN_WORKSPACE_ID=${YARNNN_WORKSPACE_ID}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python -m orchestration.scheduler
    restart: unless-stopped
```

### Step 4: Environment Configuration

**config/production.env:**
```bash
# Yarnnn Configuration
YARNNN_API_URL=https://api.yarnnn.com
YARNNN_API_KEY=ynk_prod_...
YARNNN_WORKSPACE_ID=ws_prod_...

# Agent Baskets
RESEARCH_BASKET_ID=basket_research_prod
CONTENT_BASKET_ID=basket_content_prod
REPORTING_BASKET_ID=basket_reporting_prod

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Monitoring
SENTRY_DSN=https://...
PROMETHEUS_PORT=9090
```

**config/staging.env:**
```bash
# Staging environment (same structure, different values)
YARNNN_API_URL=https://staging-api.yarnnn.com
YARNNN_API_KEY=ynk_staging_...
# ...
```

### Step 5: Orchestration

**orchestration/scheduler.py:**
```python
"""Production scheduler for all agents."""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from agents.research.run import run_monitoring as research_monitor
# Import other agents as needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_scheduler():
    """Create and configure scheduler."""
    scheduler = AsyncIOScheduler()

    # Research agent - daily at 6am UTC
    scheduler.add_job(
        research_monitor,
        CronTrigger(hour=6, minute=0),
        id='research_monitor',
        name='Research Agent Monitoring',
        replace_existing=True
    )

    # Add other scheduled agents here
    # scheduler.add_job(content_agent, ...)
    # scheduler.add_job(reporting_agent, ...)

    return scheduler

async def main():
    """Main scheduler loop."""
    scheduler = create_scheduler()

    logger.info("Starting agent scheduler")
    scheduler.start()

    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Workflow

### Daily Development (90% of time)

**Work in open source repo:**
```bash
cd ~/claude-agentsdk-opensource

# Develop new features
# - Add new archetype
# - Fix bugs in integrations
# - Add new tools

# Test
pytest

# Commit
git add .
git commit -m "Add AnalyticsAgent archetype"
git push
```

### Releasing Library Updates

**When feature is ready:**
```bash
cd ~/claude-agentsdk-opensource

# Tag new version
git tag v0.2.0
git push --tags

# No need to publish to PyPI yet!
```

### Updating Production Deployment (10% of time)

**Update this repo to use new library version:**
```bash
cd ~/yarnnn-claude-agents

# Option A: Update to specific tag
# Edit pyproject.toml:
# "claude-agent-sdk @ git+...@v0.2.0"

# Option B: Update to latest main (faster iteration)
# "claude-agent-sdk @ git+...@main"

# Reinstall
pip install --upgrade --force-reinstall claude-agent-sdk

# Test locally
python agents/research/run.py

# Update deployment configs if needed
# Edit agents/research/config.yaml

# Commit and deploy
git add .
git commit -m "Update to claude-agent-sdk v0.2.0"
git push

# Deploy
docker-compose up --build
```

### Quick Iteration During Active Development

**If you need to iterate quickly:**
```bash
# In open source
cd ~/claude-agentsdk-opensource
# Make changes
git commit && git push

# In deployment (if pinned to @main)
cd ~/yarnnn-claude-agents
pip install --upgrade --force-reinstall claude-agent-sdk
# Changes immediately available
```

## Version Management Strategy

### Development Phase (Now - v0.9.x)

**Open source repo:**
- Use semantic versioning
- Tag frequently (v0.1.0, v0.2.0, etc.)
- Don't worry about breaking changes yet

**This repo:**
- Pin to tags for production
- Can use @main for staging/testing
- Update when features are needed

### Stable Release (v1.0.0+)

**Move to Option 3 (PyPI):**
```bash
# In open source
cd ~/claude-agentsdk-opensource
python -m build
python -m twine upload dist/*

# In this repo
# Update pyproject.toml to use PyPI:
# "claude-agent-sdk>=1.0.0,<2.0.0"
```

## Migration Checklist

### Phase 1: Restructure (Do Soon)
- [ ] Create new directory structure in this repo
- [ ] Remove library code (`claude_agent_sdk/`)
- [ ] Update `pyproject.toml` with Git dependency
- [ ] Create agent configurations
- [ ] Set up Docker deployment
- [ ] Test installation from Git

### Phase 2: Production Deploy (After Testing)
- [ ] Set up production environment configs
- [ ] Deploy to staging
- [ ] Test scheduled execution
- [ ] Deploy to production
- [ ] Set up monitoring

### Phase 3: Stabilize (Ongoing)
- [ ] Tag library versions as features mature
- [ ] Update deployment to use stable tags
- [ ] Document version compatibility

### Phase 4: Public Release (When Ready)
- [ ] Clean up open source repo
- [ ] Write comprehensive docs
- [ ] Publish to PyPI
- [ ] Update this repo to use PyPI version
- [ ] Announce open source release

## Benefits for Your Situation

1. **Fast iteration**: 90% of work in open source, easy to update
2. **Production ready**: Pinned versions, reproducible builds
3. **No PyPI overhead**: Skip publishing during rapid development
4. **Clear separation**: Library vs deployment concerns
5. **Scalable**: Can move to PyPI when ready
6. **Genuine open source**: Git dependency works for external users too

## Rollback Strategy

**If something breaks:**
```bash
# Rollback to previous tag
# Edit pyproject.toml:
# "claude-agent-sdk @ git+...@v0.1.0"  # Previous working version

pip install --force-reinstall claude-agent-sdk

# Or pin to specific commit
# "claude-agent-sdk @ git+...@abc123def"
```

---

**Next Step:** Execute Phase 1 (Restructure) when ready to split repos.
