# User Story: US-MCP-002 - FastMCP Tool Server Suite + Client Configuration

**Epic**: EPIC-2: Software Development Agents  
**Sprint**: Sprint 8  
**Story Points**: 8  
**Priority**: High  
**Status**: Not started  
**Created**: 2025-12-23  
**Assignee**: AI Team  

## Story Overview

**As a** developer building agents with MCP tools  
**I want** a clear, repeatable way to run local FastMCP servers and connect to them from a client  
**So that** DeepAgents-based agents can reliably discover and call MCP tools during development and demos

## Acceptance Criteria

- [ ] Define and document canonical local MCP server ports/endpoints for:
  - weather (8000), finance (8001), news (8002), calculator (8003)
- [ ] Provide a runbook for starting all servers locally (separate terminals)
- [ ] Provide a simple client-side connectivity check (tool discovery and one tool call per server)
- [ ] Failure modes documented (server down, wrong port, missing env var such as NEWS_API_KEY)

## Notes

- Reference implementation patterns: `tests/deep_agents/deep_agents_mcp.ipynb`
- Local server code lives in: `utils/mcp/fastmcp/`


