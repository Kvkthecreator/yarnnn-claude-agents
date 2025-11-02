# Refactoring Plan: Split Library from Application

## Goal
Transform this repository from a copy of the library into a pure deployment/application repository that depends on the open source library.

## Current State
- ✅ Repository cloned from open source
- ✅ Contains all library code (claude_agent_sdk/)
- ✅ Contains deployment examples

## Target State
- ❌ Remove library code (becomes dependency)
- ✅ Keep only deployment/infrastructure code
- ✅ Depend on open source via pip

## Step-by-Step Refactoring

### Phase 1: Prepare (Do First)

1. **Ensure open source repo is accessible**
   - Published to PyPI (public), OR
   - Published to private PyPI server, OR
   - Installable from Git URL

2. **Test library installation from open source**
   ```bash
   # Option A: From PyPI (when published)
   pip install claude-agent-sdk

   # Option B: From Git (works now)
   pip install git+https://github.com/Kvkthecreator/claude-agentsdk-opensource.git

   # Option C: Development mode (local)
   pip install -e /path/to/claude-agentsdk-opensource
   ```

### Phase 2: Restructure This Repo

1. **Create new directory structure**
   ```
   yarnnn-claude-agents/
   ├── pyproject.toml          # NEW: Application config (not library)
   ├── agents/                 # NEW: Production agent instances
   │   ├── research/
   │   │   ├── config.yaml
   │   │   └── run.py
   │   ├── content/
   │   └── reporting/
   ├── deployment/             # NEW: Infrastructure
   │   ├── docker/
   │   │   ├── Dockerfile
   │   │   └── docker-compose.yml
   │   ├── kubernetes/
   │   │   ├── deployments/
   │   │   └── cronjobs/
   │   └── serverless/
   │       └── serverless.yml
   ├── config/                 # NEW: Environment configs
   │   ├── production.env
   │   ├── staging.env
   │   └── local.env
   ├── orchestration/          # NEW: Schedulers
   │   ├── scheduler.py
   │   └── tasks.py
   └── monitoring/             # NEW: Observability
       ├── dashboards/
       └── alerts/
   ```

2. **Replace pyproject.toml**
   ```toml
   [project]
   name = "yarnnn-agent-deployment"  # NOT a library
   version = "1.0.0"
   dependencies = [
       # The library this repo depends on
       "claude-agent-sdk>=0.1.0",  # From open source!

       # Production-specific dependencies
       "apscheduler>=3.10.0",
       "celery>=5.3.0",
       "redis>=5.0.0",
       "prometheus-client>=0.19.0",
       "sentry-sdk>=1.40.0",
   ]
   ```

3. **Remove library code**
   ```bash
   # Remove these (they come from dependency now)
   rm -rf claude_agent_sdk/
   rm -rf tests/
   rm -rf examples/

   # Keep only deployment-specific files
   # (Move current files to new structure above)
   ```

### Phase 3: Migration

1. **Move existing files**
   ```bash
   # Move Docker setup
   mkdir -p deployment/docker
   mv Dockerfile deployment/docker/
   mv docker-compose.yml deployment/docker/

   # Move examples to production agents
   mkdir -p agents/research
   # Adapt examples to production configs
   ```

2. **Create production agent configurations**
   ```python
   # agents/research/run.py
   from claude_agent_sdk.archetypes import ResearchAgent
   from claude_agent_sdk.integrations.yarnnn import YarnnnMemory, YarnnnGovernance
   import os

   # Production agent instance
   def create_agent():
       memory = YarnnnMemory(
           basket_id=os.getenv("RESEARCH_BASKET_ID"),
           api_key=os.getenv("YARNNN_API_KEY"),
           workspace_id=os.getenv("YARNNN_WORKSPACE_ID"),
           api_url=os.getenv("YARNNN_API_URL")
       )

       governance = YarnnnGovernance(
           basket_id=os.getenv("RESEARCH_BASKET_ID"),
           api_key=os.getenv("YARNNN_API_KEY"),
           workspace_id=os.getenv("YARNNN_WORKSPACE_ID")
       )

       return ResearchAgent(
           agent_id="yarnnn_research_agent",
           memory=memory,
           governance=governance,
           anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
           monitoring_domains=["competitors", "market_trends"],
           monitoring_frequency="daily"
       )

   if __name__ == "__main__":
       agent = create_agent()
       # Run monitoring
       import asyncio
       asyncio.run(agent.monitor())
   ```

3. **Set up orchestration**
   ```python
   # orchestration/scheduler.py
   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   from agents.research.run import create_agent as create_research_agent

   scheduler = AsyncIOScheduler()

   # Schedule research agent to run daily at 6am
   @scheduler.scheduled_job('cron', hour=6, minute=0)
   async def run_research_monitor():
       agent = create_research_agent()
       await agent.monitor()

   if __name__ == "__main__":
       scheduler.start()
       # Keep running
       import asyncio
       asyncio.get_event_loop().run_forever()
   ```

## Timeline

**Don't do this yet!** Wait until:
- [ ] Open source repo is stable
- [ ] You've tested agents in production with current setup
- [ ] You're ready to publish open source to PyPI or Git
- [ ] You need to make deployment changes that don't affect library

**Estimated effort:** 4-8 hours of refactoring

## Rollback Plan

If something goes wrong:
1. Keep a backup branch before refactoring
2. Can always reinstall from local copy
3. Development mode (`pip install -e`) allows local testing

---

**Note:** This is a future refactoring. Current identical repos are fine for now!
