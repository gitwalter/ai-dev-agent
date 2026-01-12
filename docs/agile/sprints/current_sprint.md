# Current Sprint: Sprint 8 - DeepAgents + MCP Tooling Foundation

**Sprint Number**: 8  
**Sprint Name**: DeepAgents + MCP Agent-Building Sprint  
**Duration**: 2 weeks (14 days)  
**Start Date**: 2025-12-23  
**End Date**: 2026-01-06  
**Current Date**: 2025-12-23 (Day 1)  
**Status**: **ACTIVE - WEEK 1**

---

## Sprint Goal

Build a reliable foundation for **DeepAgents-based agents** that use **MCP tools** (local FastMCP servers + remote MCP servers), aligned with the proven patterns in `tests/deep_agents/deep_agents_mcp.ipynb`.

---

## Quick Status

**Current Phase**: Week 1 - MCP Tooling + DeepAgents Baseline  
**Sprint Day**: Day 1 of 14  
**Points Completed**: 0 / 34 (0%)  
**Points In Progress**: 0  
**Points Remaining**: 34  
**Sprint Health**: **GREEN** - Clear scope and concrete implementation plan

---

## Active User Stories

### In Progress (Week 1)

#### US-MCP-002: Development MCP Tool Server Suite + Client Configuration (8 points)
**Priority**: High  
**Status**: Not started

**Scope**:
- Define and standardize a **development MCP server suite** (repo inspection, search, tests, git, docs)
- Provide a single place for MCP server endpoints/ports
- Add a quick connectivity check and example client usage

**Current Focus**: Define the canonical server config and runbook

---

#### US-DEEPAGENTS-001: DeepAgents Baseline Agent with MCP Tools + Memory (13 points)
**Priority**: Critical  
**Status**: Not started

**Scope**:
- Implement a runnable DeepAgent wrapper that loads MCP tools via `MultiServerMCPClient`
- Provide thread-scoped memory via checkpointer
- Provide a small "RAG-like" internal tool (optional) plus MCP tools
- Demonstrate usage in a script (and keep it consistent with the notebook)

**Current Focus**: Build a minimal, reliable agent entrypoint that can call tools

---

#### US-DEEPAGENTS-002: Specialized Subagents + Coordinator Routing (8 points)
**Priority**: High  
**Status**: Not started

**Scope**:
- Create 2-3 specialized subagents (e.g., finance/news/weather) using MCP tools
- Create a coordinator agent that delegates via tools and synthesizes results

**Current Focus**: Define subagent prompts and delegation tools

---

### Backlog (Week 2)

#### US-DEEPAGENTS-003: HITL + Safety for Sensitive Operations (5 points)
**Priority**: High  
**Planned**: Week 2

**Scope**:
- Require approval for file writes/edits and spawning subagents (where applicable)
- Document the recommended HITL policy and example resume flow

---

### Future (Sprint 8)

#### US-RAG-010: Dynamic Graph Composition (21 points)
**Priority**: Medium  
**Planned**: Sprint 8

**Scope**:
- Self-building agent workflows
- Task analysis with LLM
- Dynamic agent composition
- Self-optimization

---

## Sprint Documentation

For complete sprint information, see:
- **Sprint Overview**: `docs/agile/sprints/sprint_8/README.md`
- **Sprint Backlog**: `docs/agile/sprints/sprint_8/backlog.md`
- **User Stories**: `docs/agile/sprints/sprint_8/user_stories/`
- **Reference Notebook**: `tests/deep_agents/deep_agents_mcp.ipynb`

---

## Previous Sprint

**Sprint 7**: Scope pivoted. RAG/HITL artifacts remain in `docs/agile/sprints/sprint_7/` for reference.

---

## This Week's Focus (Week 1)

### Tuesday (Today) - December 23
1. Create Sprint 8 folder and backlog
2. Add Sprint 8 user stories for DeepAgents + MCP
3. Provide a concrete runbook for local FastMCP servers and ports
4. Regenerate catalogs (user story catalog + task catalog) via automation

### Rest of Week 1
- Implement and validate US-MCP-002 and US-DEEPAGENTS-001 foundations
- Ensure local FastMCP servers are easy to run and tools are discoverable

**Week 1 Goal**: Complete US-MCP-002 and begin US-DEEPAGENTS-001 (baseline agent entrypoint)

---

## Sprint 8 Key Features

### 1. DeepAgents as the core agent framework
- Standard deep agent creation, memory via checkpointer, optional persistent memory patterns

### 2. MCP tools as the core integration surface
- Development MCP server suite (repo/search/tests/git/docs) for agent building
- Configurable remote MCP servers (optional)

### 3. Optional multi-agent delegation
- Coordinator agent delegates to specialist subagents and synthesizes results

### 4. Safety and HITL for sensitive operations
- Approval for file writes/edits and spawning subagents (policy-driven)

### 5. Memory patterns
- Thread-scoped memory for multi-turn interactions, with an optional path to persistent memory

---

## Success Metrics

### Performance Targets
- Fast local MCP tool calls (local network)
- Clear failure modes and actionable errors when MCP servers are down

### Quality Targets
- Deep agent reliably loads tools from MCP servers
- Subagent delegation produces correct tool usage and summaries

### Week 1 Milestones
- Sprint 8 backlog and stories created
- Local MCP servers + client configuration documented and validated
- DeepAgents baseline agent can call MCP tools end-to-end

---

## Upcoming Ceremonies

**Daily Standup**: Daily (time set by team)  
**Sprint Review**: 2026-01-06  
**Sprint Retrospective**: 2026-01-06

---

## Sprint Schedule

### Week 1 (2025-12-23 - 2025-12-29)
**Focus**: MCP server runbook + DeepAgents baseline

- US-MCP-002
- US-DEEPAGENTS-001

---

### Week 2 (2025-12-30 - 2026-01-06)
**Focus**: Subagents + HITL policy

- US-DEEPAGENTS-002
- US-DEEPAGENTS-003

---

## Last Updated

**Last Updated**: 2025-12-23 (Sprint 8 Day 1)  
**Sprint Status**: ACTIVE - Week 1 MCP + DeepAgents Foundation
