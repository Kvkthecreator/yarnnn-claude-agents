# Architecture Decision: Library vs Application Separation

**Date:** 2025-01-02
**Status:** Proposed
**Decision Maker:** Sole contributor (Yarnnn maintainer)

## Context

This repository (`yarnnn-claude-agents`) was cloned from the open source repository (`claude-agentsdk-opensource`). They are currently identical. We need to clarify the separation of concerns between:

1. **Open Source Library** - Generic agent framework
2. **This Repository** - Production deployment for Yarnnn service
3. **Yarnnn Main Service** - The platform itself

## Decision

### Repository Roles

#### Open Source (claude-agentsdk-opensource)
**Purpose:** Generic agent framework library
**Development Focus:**
- Agent framework architecture (BaseAgent, interfaces)
- Archetypes (ResearchAgent, ContentCreator, ReportingAgent, future ones)
- Tool and skill development
- Subagent patterns
- Provider interfaces and example implementations
- Documentation for developers

**Publishing:** PyPI as `claude-agent-sdk`

#### This Repository (yarnnn-claude-agents)
**Purpose:** Production deployment and hosting
**Development Focus:**
- Production agent configurations
- Deployment infrastructure (Docker, K8s, serverless)
- Environment management
- Orchestration (scheduling, task queues)
- Monitoring and observability
- Yarnnn-specific production tweaks
- Infrastructure as code

**Dependency:** `pip install claude-agent-sdk` (from open source)

#### Yarnnn Main Service
**Purpose:** Platform (baskets, proposals, governance API)
**Development Focus:**
- Core platform features
- API endpoints
- User interface
- Data persistence

## Implementation Strategy

### Phase 1: Immediate (Current State)
Keep repositories identical while we:
- Develop and stabilize agent framework
- Test Yarnnn integration
- Validate architecture decisions

### Phase 2: Split (After Initial Production)
1. **Open Source Actions:**
   - Keep: Core framework, archetypes, integrations (including Yarnnn)
   - Remove: Production-specific configs, deployment manifests
   - Publish to PyPI

2. **This Repository Actions:**
   - Keep: Deployment infrastructure, production configs
   - Remove: Core framework code (becomes a dependency)
   - Add: `pyproject.toml` with dependency on `claude-agent-sdk`
   - Add: Production-specific orchestration

3. **Dependency Setup:**
   ```toml
   # This repo's pyproject.toml
   [project]
   name = "yarnnn-agent-deployment"
   dependencies = [
       "claude-agent-sdk>=0.1.0",  # From open source
       # Production dependencies
       "apscheduler",
       "celery",
       "prometheus-client"
   ]
   ```

### Phase 3: Continuous (Ongoing)
- **New agent features, archetypes, tools** → Develop in open source
- **Production deployment updates** → Develop in this repo
- **Integration improvements** → Develop in open source
- **Infrastructure changes** → Develop in this repo

## Development Workflow

### Developing New Agent Capabilities

```bash
# Work in open source repo
cd claude-agentsdk-opensource
# Develop new archetype, tool, or feature
# Test, commit, release new version

# Update production deployment
cd yarnnn-claude-agents
# Update dependency version
pip install --upgrade claude-agent-sdk
# Update configs if needed
# Deploy
```

### Deploying Production Changes

```bash
# Work in this repo
cd yarnnn-claude-agents
# Update deployment configs, infrastructure
# Test in staging
# Deploy to production
```

## Yarnnn Integration Placement

**Decision:** Keep Yarnnn integration in open source

**Rationale:**
- Positions Yarnnn as a serious platform (like Stripe, Notion, etc.)
- Allows community to build on Yarnnn
- No proprietary logic exposed (just HTTP API calls)
- Good for marketing and adoption
- This repo just uses the integration, doesn't own it

## Migration Checklist

### When Ready to Split:

**Open Source Repo:**
- [ ] Remove deployment/ directory
- [ ] Remove config/ (production.env, staging.env)
- [ ] Remove orchestration/ (schedulers, task queues)
- [ ] Remove monitoring/ (dashboards)
- [ ] Keep only: claude_agent_sdk/, examples/, tests/, docs/
- [ ] Set up PyPI publishing
- [ ] Create release workflow

**This Repo:**
- [ ] Remove claude_agent_sdk/ (becomes dependency)
- [ ] Remove tests/ (or keep integration tests only)
- [ ] Keep only: deployment/, config/, orchestration/, monitoring/
- [ ] Add pyproject.toml with claude-agent-sdk dependency
- [ ] Add agents/ directory with production instances
- [ ] Update README to focus on deployment

## Benefits

1. **Clear Separation:** Library development vs production deployment
2. **Reusability:** Open source framework can be used by others
3. **Maintainability:** Changes in framework don't affect deployment, vice versa
4. **Versioning:** Can version library independently from deployment
5. **Testing:** Can test library in isolation
6. **Community:** Open source enables contributions to framework

## Risks & Mitigations

**Risk:** Tight coupling between library and deployment
**Mitigation:** Well-defined interfaces, semantic versioning

**Risk:** Breaking changes in library break production
**Mitigation:** Pin library versions, test before upgrading

**Risk:** Duplication of Yarnnn-specific code
**Mitigation:** Keep all Yarnnn integration in library, this repo just configures

## Review & Updates

This decision should be reviewed:
- After first production deployment
- When adding first external contributor
- Before any major refactoring

---

**Next Actions:**
1. Continue current development with identical repos
2. When ready for production (after testing), execute split
3. Set up dependency management
4. Establish development workflow
