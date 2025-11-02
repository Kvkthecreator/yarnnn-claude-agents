# Development Workflow: Managing Library and Application

## Current Setup (Temporary)

Both repositories are currently identical. This is intentional for initial development.

## Recommended Workflow

### For Active Development (Current)

**Use Development Mode** - Changes in library immediately available:

```bash
# Directory structure
~/projects/
  ├── claude-agentsdk-opensource/   # Library development
  └── yarnnn-claude-agents/         # This repo (deployment)

# One-time setup
cd ~/projects/yarnnn-claude-agents
pip install -e ../claude-agentsdk-opensource

# Or if repos are elsewhere
pip install -e /path/to/claude-agentsdk-opensource
```

**Daily workflow:**

```bash
# Scenario: Adding new agent capability
# =====================================

# 1. Develop in open source
cd ~/claude-agentsdk-opensource
# Make changes to archetypes, tools, etc.
pytest  # Test
git commit -m "Add MonitoringAgent archetype"

# 2. Test in production context (changes already available!)
cd ~/yarnnn-claude-agents
# Create production config for new agent
# Test deployment
# Commit deployment configs
git commit -m "Add MonitoringAgent deployment config"

# 3. Push both
cd ~/claude-agentsdk-opensource
git push

cd ~/yarnnn-claude-agents
git push
```

**Benefits:**
- ✅ Zero friction - changes immediately available
- ✅ Fast iteration
- ✅ Can test library and deployment together
- ✅ Perfect for solo development

### For Production Deployment (Future)

**Switch to Git Dependency** when deploying:

```toml
# yarnnn-claude-agents/pyproject.toml
[project]
name = "yarnnn-agent-deployment"
dependencies = [
    "claude-agent-sdk @ git+https://github.com/Kvkthecreator/claude-agentsdk-opensource.git@v0.1.0"
]
```

**Deployment workflow:**

```bash
# 1. Release library version
cd ~/claude-agentsdk-opensource
git tag v0.1.0
git push --tags

# 2. Update deployment to use release
cd ~/yarnnn-claude-agents
# Edit pyproject.toml to pin version
pip install --upgrade --force-reinstall claude-agent-sdk

# 3. Deploy
docker build -t yarnnn-agents:latest .
# Deploy to production
```

## Key Principles

### Where to Develop

**Open Source (claude-agentsdk-opensource):**
- ✅ Agent framework (BaseAgent, interfaces)
- ✅ Archetypes (Research, Content, Reporting, new ones)
- ✅ Tools and skills
- ✅ Integrations (including Yarnnn)
- ✅ Tests for framework

**This Repo (yarnnn-claude-agents):**
- ✅ Production agent configurations
- ✅ Deployment infrastructure (Docker, K8s)
- ✅ Environment configs (.env files)
- ✅ Orchestration (schedulers, queues)
- ✅ Monitoring dashboards
- ✅ Integration tests (end-to-end)

### Decision Framework

Ask: **"Would another developer using a different backend need this?"**
- YES → Open source
- NO → This repo

### Examples

| Change | Where | Why |
|--------|-------|-----|
| Add AnalyticsAgent archetype | Open source | Generic capability |
| Fix bug in YarnnnMemory | Open source | Benefits everyone |
| Add web scraping tool | Open source | Generic tool |
| Update K8s deployment YAML | This repo | Infrastructure-specific |
| Add production monitoring | This repo | Deployment-specific |
| Configure APScheduler | This repo | Orchestration-specific |
| Improve BaseAgent.reason() | Open source | Framework improvement |
| Add staging environment config | This repo | Environment-specific |

## Handling Updates

### Library Update → Deployment

```bash
# 1. Develop in open source
cd ~/claude-agentsdk-opensource
# Add new feature
git commit && git push

# 2. Already available in dev mode!
cd ~/yarnnn-claude-agents
# No reinstall needed - changes are live
# Just update configs/deployment if needed
git commit && git push
```

### Deployment-Only Update

```bash
# Change only affects this repo
cd ~/yarnnn-claude-agents
# Update infrastructure
git commit && git push

# No need to touch open source repo
```

## Version Management

### During Development
- Keep both repos on `main` branch
- Use development mode (`pip install -e`)
- Commit frequently to both

### For Releases
- Tag versions in open source
- Pin versions in deployment
- Follow semantic versioning

```bash
# Open source versioning
v0.1.0 - Initial release
v0.2.0 - Add new archetypes (minor - backward compatible)
v1.0.0 - Stable API (major)
v1.1.0 - Add features (minor)
v1.1.1 - Bug fixes (patch)
```

## Common Scenarios

### Scenario 1: Testing New Agent Locally

```bash
# Develop and test together
cd ~/claude-agentsdk-opensource
# Edit ResearchAgent
cd ~/yarnnn-claude-agents
python agents/research/run.py  # Uses latest immediately
```

### Scenario 2: Deploying to Production

```bash
# 1. Finalize open source
cd ~/claude-agentsdk-opensource
git tag v0.1.0
git push --tags

# 2. Pin version for production
cd ~/yarnnn-claude-agents
# Update pyproject.toml to pin v0.1.0
pip install --upgrade claude-agent-sdk

# 3. Deploy
docker-compose up --build
```

### Scenario 3: Hotfix in Library

```bash
# 1. Fix in open source
cd ~/claude-agentsdk-opensource
# Fix critical bug
git commit -m "Fix memory leak in YarnnnMemory"
git tag v0.1.1
git push --tags

# 2. Update deployment
cd ~/yarnnn-claude-agents
pip install --upgrade claude-agent-sdk
# Restart production services
```

## Current State Action Items

**Right now:**
- ✅ Both repos are identical (this is OK!)
- ✅ Keep developing in open source primarily
- ✅ Test deployment scenarios in this repo
- ⏳ When ready, set up development mode linking

**Don't split yet** - wait until:
- Library is stable enough for v0.1.0
- You've tested in production
- Clear separation of concerns is established

## Questions?

- "Where does this code go?" → See Decision Framework above
- "How do I test changes?" → Development mode gives instant access
- "When do I split repos?" → When library is stable and you need different release cycles
- "What about dependencies?" → Library dependencies in open source, deployment dependencies here

---

**Remember:** This is a dependency relationship, not a fork. The open source repo is the source of truth for agent capabilities, this repo just uses them.
