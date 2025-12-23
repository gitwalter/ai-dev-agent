# User Story: US-DEEPAGENTS-002 - Specialized Subagents + Coordinator Routing

**Epic**: EPIC-2: Software Development Agents  
**Sprint**: Sprint 8  
**Story Points**: 8  
**Priority**: High  
**Status**: Not started  
**Created**: 2025-12-23  
**Assignee**: AI Team  
**Dependencies**: US-DEEPAGENTS-001, US-MCP-002  

## Story Overview

**As a** user of the agent system  
**I want** a coordinator agent that can delegate to specialized subagents (finance/news/weather)  
**So that** tasks can be routed to the best tool set and the final answer is synthesized from specialist outputs

## Acceptance Criteria

- [ ] Define at least 2 specialist subagents with limited, domain-specific MCP tools
- [ ] Define a coordinator agent with delegation tools (one per specialist)
- [ ] Coordinator synthesizes results into a single response and indicates which specialist handled what
- [ ] Demonstrate a multi-domain query that triggers at least 2 specialists

## Notes

- Reference patterns: `tests/deep_agents/deep_agents_mcp.ipynb` (specialized servers + delegation tools)


