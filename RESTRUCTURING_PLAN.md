# Restructuring Execution Plan

## Context
- **Deployment target**: Render (cloud platform)
- **Trigger mechanism**: Yarnnn API calls (POST to agent endpoints)
- **Agent scope**: Structure for all 3, configure ResearchAgent initially
- **Environments**: Production (Render) + Local dev
- **Open source**: Accessible at github.com/Kvkthecreator/claude-agentsdk-opensource

## Architecture

### This Repo Structure (After Restructuring)
```
yarnnn-claude-agents/
├── pyproject.toml              # Depends on claude-agent-sdk@v0.1.0
├── requirements.txt            # Generated from pyproject.toml
├── runtime.txt                 # Python version for Render
├── README.md                   # Deployment guide
├──
├── api/                        # FastAPI web service
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── routes/                 # Agent endpoints
│   │   ├── __init__.py
│   │   ├── research.py         # POST /agents/research/run
│   │   ├── content.py          # POST /agents/content/run
│   │   └── reporting.py        # POST /agents/reporting/run
│   └── dependencies.py         # Agent factory functions
│
├── agents/                     # Agent configurations
│   ├── research/
│   │   ├── config.yaml
│   │   └── agent.py            # ResearchAgent setup
│   ├── content/
│   │   └── config.yaml         # Placeholder
│   └── reporting/
│       └── config.yaml         # Placeholder
│
├── config/                     # Environment configs
│   ├── production.env.example
│   └── local.env.example
│
├── deployment/                 # Deployment files
│   ├── render.yaml            # Render config
│   └── docker/
│       ├── Dockerfile
│       └── docker-compose.yml  # Local development
│
├── tests/                      # Integration tests
│   └── test_api_endpoints.py
│
└── docs/                       # Keep existing docs
    ├── ARCHITECTURE_DECISION.md
    ├── DEVELOPMENT_WORKFLOW.md
    ├── REFACTORING_PLAN.md
    └── YARNNN_INTEGRATION.md
```

### Key Components

**1. FastAPI Web Service**
- Exposes HTTP endpoints for Yarnnn to trigger agents
- POST /agents/research/run - Trigger research monitoring
- POST /agents/content/run - Trigger content creation
- POST /agents/reporting/run - Trigger report generation
- GET /health - Health check

**2. Agent Configurations**
- YAML configs for each agent type
- Agent factory functions create instances
- Environment-based configuration

**3. Render Deployment**
- render.yaml defines services
- Web service runs FastAPI
- Optional: Cron jobs for scheduled tasks

## Execution Steps

### Step 1: Tag Open Source Repo
Tag claude-agentsdk-opensource as v0.1.0

### Step 2: Remove Library Code
Remove claude_agent_sdk/, tests/, examples/ from this repo

### Step 3: Create New Structure
Set up directory structure above

### Step 4: Update Dependencies
Update pyproject.toml to depend on git+...@v0.1.0

### Step 5: Create FastAPI Service
Web service for agent triggers

### Step 6: Configure ResearchAgent
Full configuration for initial agent

### Step 7: Create Render Config
render.yaml for deployment

### Step 8: Update Documentation
README for deployment guide

### Step 9: Test Locally
Verify structure and installation

## Next Actions After Restructuring
(Post-stabilization, one by one)

1. Wire up ResearchAgent with Yarnnn service
2. Test end-to-end flow
3. Deploy to Render
4. Add ContentCreatorAgent
5. Add ReportingAgent
6. Add monitoring/observability
7. Add staging environment (if needed)

---

Proceeding with execution...
