# Yarnnn Service Integration Guide

**For Yarnnn Core Service Development**

This document describes what the Yarnnn core service needs to implement to integrate with this agent deployment service.

---

## Overview

```
┌─────────────────────────────────────┐
│  Yarnnn Core Service (Your Work)   │
│  - User creates research request    │
│  - UI triggers agent execution      │
│  - Stores results in baskets        │
└─────────────────────────────────────┘
            ↓ HTTP POST
┌─────────────────────────────────────┐
│  Agent Deployment Service (This)    │
│  URL: https://your-service.onrender.com
│  - Receives trigger requests        │
│  - Creates agent instances          │
│  - Executes agent tasks             │
└─────────────────────────────────────┘
            ↓ HTTP calls back
┌─────────────────────────────────────┐
│  Yarnnn Core Service API            │
│  - Provides memory (baskets)        │
│  - Handles governance (proposals)   │
│  - Returns results                  │
└─────────────────────────────────────┘
```

---

## Agent Deployment Service Endpoints

This service (after deployed to Render) exposes these endpoints:

### 1. Health Check

```http
GET https://your-service.onrender.com/health

Response:
{
  "status": "healthy",
  "service": "yarnnn-agents"
}
```

**Use**: Monitoring, verify service is running

---

### 2. Research Agent - Run Task

```http
POST https://your-service.onrender.com/agents/research/run
Content-Type: application/json

Request Body:
{
  "task_type": "monitor",     // or "deep_dive"
  "topic": "AI agents",       // required for deep_dive, optional for monitor
  "parameters": {             // optional additional parameters
    "custom_param": "value"
  }
}

Response (Success):
{
  "status": "completed",
  "message": "Monitoring completed successfully",
  "result": {
    "session_id": "session_abc123",
    "findings": [...],
    "proposals": [...],
    // ... agent-specific results
  }
}

Response (Error):
{
  "error": "Internal server error",
  "detail": "Configuration error: RESEARCH_BASKET_ID not set"
}
```

**Task Types:**
- `monitor` - Run continuous monitoring across configured domains
- `deep_dive` - Deep research on a specific topic

---

### 3. Research Agent - Status

```http
GET https://your-service.onrender.com/agents/research/status

Response:
{
  "status": "ready",              // or "error"
  "agent_id": "yarnnn_research_agent",
  "agent_type": "research",
  "message": "Research agent is configured and ready"
}
```

**Use**: Check if agent is configured before triggering

---

### 4. Content Agent (Placeholder)

```http
POST https://your-service.onrender.com/agents/content/run

Response:
{
  "error": "Not Implemented",
  "detail": "Content agent not yet configured..."
}
Status: 501
```

### 5. Reporting Agent (Placeholder)

```http
POST https://your-service.onrender.com/agents/reporting/run

Response:
{
  "error": "Not Implemented",
  "detail": "Reporting agent not yet configured..."
}
Status: 501
```

---

## What Yarnnn Core Service Needs to Implement

### Phase 1: Basic Integration (ResearchAgent)

#### 1. API Client for Agent Service

Create a client in Yarnnn service to call agent deployment endpoints:

```python
# yarnnn-core-service/services/agent_client.py

import httpx
from typing import Dict, Any

class AgentDeploymentClient:
    """Client for calling agent deployment service."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout

    async def trigger_research_monitor(self) -> Dict[str, Any]:
        """Trigger research monitoring task."""
        response = await self.client.post(
            f"{self.base_url}/agents/research/run",
            json={"task_type": "monitor"}
        )
        response.raise_for_status()
        return response.json()

    async def trigger_research_deep_dive(self, topic: str) -> Dict[str, Any]:
        """Trigger deep dive research on topic."""
        response = await self.client.post(
            f"{self.base_url}/agents/research/run",
            json={
                "task_type": "deep_dive",
                "topic": topic
            }
        )
        response.raise_for_status()
        return response.json()

    async def check_research_agent_status(self) -> Dict[str, Any]:
        """Check if research agent is ready."""
        response = await self.client.get(
            f"{self.base_url}/agents/research/status"
        )
        response.raise_for_status()
        return response.json()
```

#### 2. UI Integration Points

**Where users trigger agents in Yarnnn UI:**

**Option A: Basket-level "Research" Button**
```
Basket View
┌────────────────────────────────┐
│ Research Basket                │
│                                │
│ [🔍 Run Research Monitor]      │ ← Triggers agent
│                                │
│ Recent Yarns:                  │
│ - Finding 1                    │
│ - Finding 2                    │
└────────────────────────────────┘
```

**Option B: Dedicated "Agents" Section**
```
Workspace Dashboard
┌────────────────────────────────┐
│ My Agents                      │
│                                │
│ Research Agent                 │
│ Status: Ready                  │
│ [▶ Run Monitor] [🔍 Deep Dive] │
│                                │
│ Content Agent (Coming Soon)    │
│ Reporting Agent (Coming Soon)  │
└────────────────────────────────┘
```

**Option C: Task Queue / Scheduled Jobs**
```
Settings > Automations
┌────────────────────────────────┐
│ Scheduled Research             │
│                                │
│ ✓ Daily monitoring at 6am      │
│ Domains: AI agents, competitors│
│                                │
│ [Edit Schedule] [Run Now]      │
└────────────────────────────────┘
```

#### 3. Backend API Endpoints (Yarnnn Service)

Add these to your Yarnnn service API:

```python
# yarnnn-core-service/api/routes/agents.py

from fastapi import APIRouter, BackgroundTasks
from services.agent_client import AgentDeploymentClient

router = APIRouter()
agent_client = AgentDeploymentClient(
    base_url=os.getenv("AGENT_DEPLOYMENT_URL")
)

@router.post("/api/agents/research/trigger-monitor")
async def trigger_research_monitor(background_tasks: BackgroundTasks):
    """Trigger research monitoring (called from UI)."""

    # Option 1: Synchronous (blocks until complete)
    # result = await agent_client.trigger_research_monitor()
    # return result

    # Option 2: Background task (returns immediately)
    background_tasks.add_task(
        run_research_monitor_background,
        user_id=current_user.id
    )
    return {
        "status": "started",
        "message": "Research monitoring started in background"
    }

@router.post("/api/agents/research/deep-dive")
async def trigger_deep_dive(request: DeepDiveRequest):
    """Trigger deep dive research on topic."""
    result = await agent_client.trigger_research_deep_dive(
        topic=request.topic
    )
    return result

async def run_research_monitor_background(user_id: str):
    """Background task to run research and store results."""
    try:
        result = await agent_client.trigger_research_monitor()

        # Store results in user's research basket
        # (Agents already store via YarnnnMemory, but you might
        #  want to create a "task completed" notification)

        await create_notification(
            user_id=user_id,
            message=f"Research monitoring completed",
            result=result
        )
    except Exception as e:
        await create_notification(
            user_id=user_id,
            message=f"Research monitoring failed: {e}",
            error=True
        )
```

#### 4. Environment Configuration

Add to Yarnnn service environment:

```bash
# .env (Yarnnn core service)

# Agent Deployment Service URL
AGENT_DEPLOYMENT_URL=https://your-service.onrender.com

# Or for local testing
AGENT_DEPLOYMENT_URL=http://localhost:8000
```

#### 5. Database Schema (Optional)

If you want to track agent executions in Yarnnn DB:

```sql
-- Agent execution history
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    workspace_id UUID REFERENCES workspaces(id),
    basket_id UUID REFERENCES baskets(id),
    agent_type VARCHAR(50) NOT NULL,  -- 'research', 'content', etc.
    task_type VARCHAR(50),            -- 'monitor', 'deep_dive', etc.
    status VARCHAR(20) NOT NULL,      -- 'running', 'completed', 'failed'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    result JSONB,                     -- Store agent response
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for user queries
CREATE INDEX idx_agent_executions_user ON agent_executions(user_id, created_at DESC);
```

---

### Phase 2: Governance Integration (Later)

When agents create proposals (via YarnnnGovernance), Yarnnn UI needs to show them:

#### Proposal Approval UI

```
Pending Approvals
┌────────────────────────────────────────┐
│ Research Agent Proposal                │
│ Created: 2 minutes ago                 │
│                                        │
│ Wants to add:                          │
│ "New insight about AI agent trends"   │
│                                        │
│ Confidence: 85%                        │
│ Reasoning: "High-quality source..."   │
│                                        │
│ [✓ Approve] [✗ Reject] [View Details] │
└────────────────────────────────────────┘
```

**Backend endpoints needed:**

```python
# Already have these from YARNNN_INTEGRATION.md
POST /api/proposals          # Create proposal (agents call this)
GET  /api/proposals/{id}     # Get proposal details
POST /api/proposals/{id}/approve   # User approves
POST /api/proposals/{id}/reject    # User rejects
```

---

## Testing Integration

### Local Testing (Before Deployment)

**Terminal 1: Run Agent Service Locally**
```bash
cd yarnnn-claude-agents
cp config/local.env.example config/local.env
# Edit config/local.env with credentials
uvicorn api.main:app --reload --port 8000
```

**Terminal 2: Run Yarnnn Core Service**
```bash
cd yarnnn-core-service
# Set AGENT_DEPLOYMENT_URL=http://localhost:8000
npm run dev  # or your start command
```

**Terminal 3: Test Integration**
```bash
# Test agent service is running
curl http://localhost:8000/health

# Test from Yarnnn service (or via UI)
curl -X POST http://localhost:8000/agents/research/run \
  -H "Content-Type: application/json" \
  -d '{"task_type": "monitor"}'
```

### Production Testing (After Deployment)

1. **Deploy agent service to Render**
   - Get URL: `https://yarnnn-agents.onrender.com`

2. **Update Yarnnn service environment**
   - Set `AGENT_DEPLOYMENT_URL=https://yarnnn-agents.onrender.com`

3. **Test from Yarnnn UI**
   - Click "Run Research Monitor" button
   - Should trigger agent on Render
   - Agent calls back to Yarnnn API for baskets/proposals

---

## API Contracts

### Agent Service → Yarnnn Service

When agents execute, they call back to Yarnnn service for:

**1. Memory Operations (Baskets)**
```http
POST https://api.yarnnn.com/api/baskets/{basket_id}/yarns
Authorization: Bearer {YARNNN_API_KEY}

{
  "content": "Research finding...",
  "metadata": {
    "agent_id": "yarnnn_research_agent",
    "session_id": "session_123",
    "confidence": 0.85
  }
}
```

**2. Governance Operations (Proposals)**
```http
POST https://api.yarnnn.com/api/proposals
Authorization: Bearer {YARNNN_API_KEY}

{
  "basket_id": "basket_research",
  "changes": [...],
  "confidence": 0.85,
  "reasoning": "Found high-quality insight..."
}
```

**What Yarnnn API Needs:**
- ✅ Basket CRUD endpoints (probably already have)
- ✅ Yarn create/search endpoints (probably already have)
- ⏳ Proposal endpoints (see governance integration)
- ⏳ API key authentication

---

## Checklist for Yarnnn Service

### Immediate (For ResearchAgent)

- [ ] **Add agent deployment URL to environment**
  - Local: `http://localhost:8000`
  - Prod: `https://yarnnn-agents.onrender.com`

- [ ] **Create agent client**
  - File: `services/agent_client.py`
  - Methods: `trigger_research_monitor()`, `trigger_research_deep_dive()`

- [ ] **Add API endpoints**
  - `POST /api/agents/research/trigger-monitor`
  - `POST /api/agents/research/deep-dive`
  - (These call the agent deployment service)

- [ ] **Add UI trigger points**
  - Button in basket view, or
  - Dedicated agents section, or
  - Scheduled automation settings

- [ ] **Verify basket API works**
  - Agents will call `POST /api/baskets/{id}/yarns`
  - Agents will call `GET /api/baskets/{id}/yarns?search=...`
  - Test authentication with API keys

### Later (For Governance)

- [ ] **Add proposal endpoints**
  - `POST /api/proposals`
  - `GET /api/proposals/{id}`
  - `POST /api/proposals/{id}/approve`
  - `POST /api/proposals/{id}/reject`

- [ ] **Add proposal UI**
  - List pending proposals
  - Approve/reject interface
  - Notification when agents create proposals

- [ ] **Add agent execution history** (optional)
  - Database table
  - UI to view past runs
  - Metrics/analytics

### Future (Other Agents)

- [ ] **Content Agent integration**
  - Same pattern as research agent
  - Additional endpoints for content creation

- [ ] **Reporting Agent integration**
  - Report generation triggers
  - Template management

---

## Error Handling

### Agent Service Errors

**Configuration Errors:**
```json
{
  "error": "Configuration error",
  "detail": "RESEARCH_BASKET_ID environment variable required"
}
```
**Action**: Check Render environment variables

**Agent Execution Errors:**
```json
{
  "error": "Task execution failed",
  "detail": "Anthropic API rate limit exceeded"
}
```
**Action**: Retry with exponential backoff, or show error to user

**Network Errors:**
```
Connection timeout / Service unavailable
```
**Action**:
- Check if Render service is running
- Verify health endpoint
- Implement retry logic in Yarnnn service

### Yarnnn Service → Agent Service

**Implement retry logic:**
```python
async def trigger_agent_with_retry(task_type: str, max_retries: int = 3):
    """Trigger agent with retry logic."""
    for attempt in range(max_retries):
        try:
            return await agent_client.trigger_research_monitor()
        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                # Server error, retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            raise
```

---

## Security Considerations

### Authentication

**Agent Service → Yarnnn Service:**
- Agents use `YARNNN_API_KEY` to authenticate
- Set via environment variable on Render
- Yarnnn API validates this key

**Yarnnn Service → Agent Service:**
- Currently no auth (internal service)
- If exposed publicly, add API key or JWT
- Render can restrict access by IP if needed

### Environment Variables

**Never commit:**
- `ANTHROPIC_API_KEY`
- `YARNNN_API_KEY`
- `YARNNN_WORKSPACE_ID`

**Add to:**
- Render dashboard (for agent service)
- Yarnnn deployment environment (for core service)

---

## Monitoring & Observability

### Agent Service Health

**Endpoint**: `GET https://yarnnn-agents.onrender.com/health`

**Set up monitoring:**
- Render built-in health checks (already configured)
- UptimeRobot or similar for external monitoring
- Sentry for error tracking (add `SENTRY_DSN` when ready)

### Logging

**Agent service logs:**
- View in Render dashboard: Logs tab
- Filter by service name
- Search for errors: `status_code >= 400`

**What to monitor:**
- Agent execution times
- Success/failure rates
- API call volumes
- Error types

---

## Quick Reference

### URLs

**Local Development:**
- Agent Service: `http://localhost:8000`
- Yarnnn Service: `http://localhost:3000` (or your port)

**Production:**
- Agent Service: `https://yarnnn-agents.onrender.com` (after deploy)
- Yarnnn Service: `https://api.yarnnn.com` (your production)

### Key Environment Variables

**Agent Service (Render):**
```
ANTHROPIC_API_KEY=sk-ant-...
YARNNN_API_URL=https://api.yarnnn.com
YARNNN_API_KEY=ynk_...
YARNNN_WORKSPACE_ID=ws_...
RESEARCH_BASKET_ID=basket_research_prod
```

**Yarnnn Service:**
```
AGENT_DEPLOYMENT_URL=https://yarnnn-agents.onrender.com
```

### Testing Commands

```bash
# Health check
curl https://yarnnn-agents.onrender.com/health

# Check agent status
curl https://yarnnn-agents.onrender.com/agents/research/status

# Trigger monitoring
curl -X POST https://yarnnn-agents.onrender.com/agents/research/run \
  -H "Content-Type: application/json" \
  -d '{"task_type": "monitor"}'

# Trigger deep dive
curl -X POST https://yarnnn-agents.onrender.com/agents/research/run \
  -H "Content-Type: application/json" \
  -d '{"task_type": "deep_dive", "topic": "AI agent trends"}'
```

---

## Next Session Goals (Yarnnn Service)

When you work on Yarnnn core service, implement:

1. **Agent Client** (`services/agent_client.py`)
   - HTTP client to call agent deployment service
   - Methods for each agent type

2. **API Endpoints** (in your API routes)
   - Endpoints that UI calls to trigger agents
   - Background task support for long-running agents

3. **UI Integration**
   - Button/form to trigger research monitoring
   - Display for agent results
   - (Optional) Agent execution history

4. **Test Integration**
   - Local: Agent service on :8000, Yarnnn on :3000
   - Verify end-to-end flow
   - Check baskets receive agent findings

---

## Questions to Clarify (Yarnnn Service Side)

1. **Basket Structure**
   - Do baskets for agents already exist?
   - Should agents auto-create baskets if missing?
   - What metadata fields do baskets support?

2. **API Authentication**
   - Do you have API key authentication implemented?
   - What format: Bearer token, API key header, query param?
   - How to generate/manage keys?

3. **Proposal/Governance**
   - Do proposal endpoints exist yet?
   - What's the approval workflow?
   - Who can approve (workspace owner, specific roles)?

4. **User Experience**
   - Should agent execution be synchronous (waits for result)?
   - Or async (returns immediately, notify when done)?
   - Where in UI should agent controls live?

---

**This document provides everything needed to integrate Yarnnn core service with the agent deployment service.**

Save it for your next session working on Yarnnn!
