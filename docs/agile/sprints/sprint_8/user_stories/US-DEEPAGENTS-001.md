# User Story: US-DEEPAGENTS-001 - DeepAgents Baseline Agent with MCP Tools + Memory

**Epic**: EPIC-2: Software Development Agents  
**Sprint**: Sprint 8  
**Story Points**: 13  
**Priority**: CRITICAL  
**Status**: Not started  
**Created**: 2025-12-23  
**Assignee**: AI Team  
**Dependencies**: US-MCP-002  

## Story Overview

**As a** developer building agents in this repo  
**I want** a baseline DeepAgents agent that can load MCP tools and keep thread-scoped memory  
**So that** we can build more capable agents on top of a stable, testable foundation (matching `tests/deep_agents/deep_agents_mcp.ipynb`)

## Acceptance Criteria

- [ ] Baseline agent can connect to one or more MCP servers via `MultiServerMCPClient`
- [ ] Baseline agent can call at least 2 MCP tools end-to-end (happy path)
- [ ] Agent uses a checkpointer for thread-scoped memory continuity (same thread_id retains context)
- [ ] Example usage is provided (script or module entrypoint), consistent with notebook patterns

## Notes

- This story focuses on DeepAgents + MCP wiring and runtime reliability (not product UX).


