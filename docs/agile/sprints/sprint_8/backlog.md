# Sprint 8 Backlog

**Sprint Goal**: Build a reliable foundation for agents built with the DeepAgents framework and MCP tools, aligned with `tests/deep_agents/deep_agents_mcp.ipynb`.  
**Sprint Duration**: 2025-12-23 - 2026-01-06  
**Team Capacity**: 34 story points  
**Scrum Master**: AI Development Agent  
**Product Owner**: Project Stakeholders  

## Sprint Overview

### Success Criteria
- [ ] Development MCP server suite can be started via a simple runbook and is reachable from a client
- [ ] Baseline DeepAgent can load MCP tools and successfully call at least 2 tools end-to-end
- [ ] Coordinator can delegate to specialists and synthesize a unified response
- [ ] Agent can perform research and retrieval:
  - web search via MCP (with sources)
  - RAG retrieval via MCP (with citations/metadata)

## User Stories

### Priority 1 - Must Have
| Story ID | Title | Story Points | Assignee | Status |
|----------|-------|--------------|----------|--------|
| US-MCP-002 | Development MCP Tool Server Suite + Client Configuration | 8 | AI Team | Not started |
| US-DEEPAGENTS-001 | DeepAgents Baseline Agent with MCP Tools + Memory | 13 | AI Team | Not started |

### Priority 2 - Should Have
| Story ID | Title | Story Points | Assignee | Status |
|----------|-------|--------------|----------|--------|
| US-DEEPAGENTS-002 | Specialized Subagents + Coordinator Routing | 8 | AI Team | Not started |

### Priority 3 - Could Have
| Story ID | Title | Story Points | Assignee | Status |
|----------|-------|--------------|----------|--------|
| US-DEEPAGENTS-003 | HITL + Safety for Sensitive Operations | 5 | AI Team | Not started |

## Sprint Tasks (High-Level)

### Development Tasks
- [ ] Define canonical development MCP server config (ports, endpoints) and a runbook
- [ ] Implement baseline DeepAgent entrypoint (tools + memory) consistent with notebook patterns
- [ ] Implement coordinator + delegation tools to call specialist agents

### Testing Tasks
- [ ] Add smoke tests or scripts that validate tool discovery and tool invocation

### Documentation Tasks
- [ ] Document how to start MCP servers and how to connect from a client


