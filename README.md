# Yarnnn Agent Deployment Service

**Production deployment service for Yarnnn autonomous agents**

This repository contains the production deployment infrastructure for running autonomous agents that integrate with the Yarnnn platform. It provides HTTP endpoints that the Yarnnn main service calls to trigger agent tasks.

## Architecture

```
┌──────────────────────┐
│  Yarnnn Main Service │
│  (Platform/UI)       │
└──────────────────────┘
          │
          │ HTTP API calls
          v
┌──────────────────────────────────┐
│  This Repo: Agent Deployment API │
│  - FastAPI web service           │
│  - Agent endpoints               │
│  - Configuration management      │
└──────────────────────────────────┘
          │
          │ depends on
          v
┌──────────────────────────────────┐
│  Claude Agent SDK (Open Source)  │
│  - Agent framework               │
│  - Archetypes                    │
│  - Provider integrations         │
│  github.com/Kvkthecreator/       │
│    claude-agentsdk-opensource    │
└──────────────────────────────────┘
```

## What's In This Repo

- **`api/`** - FastAPI web service with agent endpoints
- **`agents/`** - Agent configurations (YAML)
- **`config/`** - Environment configurations
- **`deployment/`** - Docker and Render deployment files
- **`tests/`** - Integration tests

## What's NOT In This Repo

- **Agent framework code** - Lives in [claude-agentsdk-opensource](https://github.com/Kvkthecreator/claude-agentsdk-opensource)
- **Yarnnn platform code** - Separate private repository
- **Library development** - Happens in open source repo

## Quick Start

### Prerequisites

- Python 3.10+
- Docker (for local development)
- Yarnnn account with API access
- Anthropic API key

### Local Development

1. **Clone repository**
   ```bash
   git clone https://github.com/Kvkthecreator/yarnnn-claude-agents.git
   cd yarnnn-claude-agents
   ```

2. **Set up environment**
   ```bash
   cp config/local.env.example config/local.env
   # Edit config/local.env with your credentials
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**
   ```bash
   uvicorn api.main:app --reload
   ```

5. **Test endpoints**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/agents/research/status
   ```

### Docker Development

```bash
cd deployment/docker
cp ../../config/local.env.example ../../config/local.env
# Edit local.env with your credentials

docker-compose up --build
```

Service will be available at `http://localhost:8000`

## Deployment

### Render (Recommended)

1. **Connect repository to Render**
   - Create new Web Service
   - Connect this GitHub repository
   - Render will auto-detect `render.yaml`

2. **Configure environment variables**
   Add via Render dashboard:
   - `ANTHROPIC_API_KEY` - Your Claude API key
   - `YARNNN_API_URL` - Yarnnn service endpoint
   - `YARNNN_API_KEY` - Service-level API key for Yarnnn

   **Note:** `workspace_id` and `basket_id` are now passed per-request (see API section below)

3. **Deploy**
   - Render will automatically deploy
   - Health check: `https://your-service.onrender.com/health`

### Manual Deployment

```bash
# Build
docker build -f deployment/docker/Dockerfile -t yarnnn-agents .

# Run
docker run -p 8000:8000 --env-file config/production.env yarnnn-agents
```

## API Endpoints

### Health & Status

- **GET /**
  Service information

- **GET /health**
  Health check (for monitoring)

### Research Agent

- **POST /agents/research/run**
  Trigger research task
  ```json
  {
    "task_type": "monitor",         // or "deep_dive"
    "workspace_id": "ws_abc123",    // Yarnnn workspace ID
    "basket_id": "basket_xyz789",   // Basket to store results
    "topic": "AI agents"            // required for deep_dive only
  }
  ```

- **GET /agents/research/status**
  Get agent status

### Content Agent (Coming Soon)

- **POST /agents/content/run** - Not yet configured
- **GET /agents/content/status** - Returns "not_configured"

### Reporting Agent (Coming Soon)

- **POST /agents/reporting/run** - Not yet configured
- **GET /agents/reporting/status** - Returns "not_configured"

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `ANTHROPIC_API_KEY` - Claude API key
- `YARNNN_API_URL` - Yarnnn service endpoint
- `YARNNN_API_KEY` - Service-level API authentication key

**Per-Request Parameters (not environment variables):**
- `workspace_id` - Passed in each API request body
- `basket_id` - Passed in each API request body

This design allows the service to handle multiple users/workspaces without reconfiguration.

**Optional:**
- `LOG_LEVEL` - Logging level (default: INFO)
- `SENTRY_DSN` - Error tracking
- `ENABLE_RESEARCH_AGENT` - Feature flag (default: true)

### Agent Configuration

Agents are configured via YAML files in `agents/{agent_type}/config.yaml`

Example (`agents/research/config.yaml`):
```yaml
agent:
  id: yarnnn_research_agent
  type: research

research:
  monitoring_domains:
    - "ai_agents"
    - "market_trends"
  monitoring_frequency: "daily"
  signal_threshold: 0.7
  synthesis_mode: "insights"
```

## Development Workflow

### Adding New Agent Capabilities

New agent features, archetypes, and tools are developed in the **open source repository**:

1. **Develop in open source repo**
   ```bash
   cd ../claude-agentsdk-opensource
   # Add new archetype, tool, or feature
   git commit && git push
   git tag v0.2.0 && git push --tags
   ```

2. **Update this deployment repo**
   ```bash
   cd ../yarnnn-claude-agents
   # Update pyproject.toml to new version:
   # "claude-agent-sdk @ git+...@v0.2.0"

   pip install --upgrade --force-reinstall claude-agent-sdk
   # Update configs if needed
   git commit && git push
   ```

3. **Deploy**
   - Render will auto-deploy on push
   - Or manually: `docker-compose up --build`

### Wire Up New Agent

To add ContentCreatorAgent or ReportingAgent:

1. **Update agent config** - Edit `agents/{agent_type}/config.yaml`
2. **Implement factory function** - Update `api/dependencies.py`
3. **Enable endpoint** - Update `api/routes/{agent_type}.py`
4. **Set environment variables** - Add basket ID, enable flag
5. **Test** - Call `/agents/{agent_type}/status`
6. **Deploy**

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
# Requires running service
pytest tests/ -v --integration
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Research agent status
curl http://localhost:8000/agents/research/status

# Trigger research monitoring
curl -X POST http://localhost:8000/agents/research/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "monitor",
    "workspace_id": "ws_your_workspace_id",
    "basket_id": "basket_your_basket_id"
  }'
```

## Project Structure

```
yarnnn-claude-agents/
├── api/                        # FastAPI application
│   ├── main.py                 # App entry point
│   ├── dependencies.py         # Agent factories
│   └── routes/                 # Endpoint handlers
│       ├── research.py
│       ├── content.py
│       └── reporting.py
├── agents/                     # Agent configs
│   ├── research/
│   │   └── config.yaml
│   ├── content/
│   │   └── config.yaml
│   └── reporting/
│       └── config.yaml
├── config/                     # Environment configs
│   ├── production.env.example
│   └── local.env.example
├── deployment/                 # Deployment files
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── render/
├── tests/                      # Integration tests
├── pyproject.toml              # Dependencies (incl. SDK)
├── requirements.txt            # Pip requirements
├── render.yaml                 # Render config
└── README.md                   # This file
```

## Troubleshooting

### "Configuration error" when calling endpoints

- Verify all required environment variables are set
- Check `.env` file is loaded correctly
- Verify Yarnnn service is accessible

### "Agent not ready" status

- Check Yarnnn API credentials
- Verify basket IDs exist in Yarnnn
- Check logs: `docker-compose logs -f`

### Installation fails

- Ensure Git is installed (needed for GitHub dependency)
- Check network access to GitHub
- Try: `pip install --upgrade --force-reinstall claude-agent-sdk`

## Documentation

- **Architecture Decision**: [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md)
- **Development Workflow**: [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)
- **Yarnnn Integration**: [YARNNN_INTEGRATION.md](YARNNN_INTEGRATION.md)
- **Refactoring Plan**: [REFACTORING_PLAN.md](REFACTORING_PLAN.md)
- **Library README**: [README_LIBRARY.md](README_LIBRARY.md) (original agent SDK docs)

## Related Repositories

- **Agent SDK (Open Source)**: [claude-agentsdk-opensource](https://github.com/Kvkthecreator/claude-agentsdk-opensource)
- **Yarnnn Main Service**: Private repository

## Support

For issues with:
- **Agent framework/features**: Open issue in [claude-agentsdk-opensource](https://github.com/Kvkthecreator/claude-agentsdk-opensource/issues)
- **Deployment/infrastructure**: Open issue in this repository
- **Yarnnn platform**: Contact Yarnnn support

## Next Steps (Post-Restructuring)

1. ✅ **Tag open source repo** - See [OPEN_SOURCE_TAGGING.md](OPEN_SOURCE_TAGGING.md)
2. ⏳ **Configure Yarnnn connection** - Add credentials to environment
3. ⏳ **Wire up ResearchAgent** - Test end-to-end with Yarnnn
4. ⏳ **Deploy to Render** - Production deployment
5. ⏳ **Add monitoring** - Sentry, metrics
6. ⏳ **Wire up other agents** - Content, Reporting (one by one)

## License

MIT License - see [LICENSE](LICENSE) file

---

**Built with Claude Agent SDK + Yarnnn Integration**
