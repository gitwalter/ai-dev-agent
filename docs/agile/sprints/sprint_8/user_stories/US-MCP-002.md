# User Story: US-MCP-002 - Development MCP Tool Server Suite + Client Configuration

**Epic**: EPIC-2: Software Development Agents  
**Sprint**: Sprint 8  
**Story Points**: 8  
**Priority**: High  
**Status**: Not started  
**Created**: 2025-12-23  
**Assignee**: AI Team  

## Story Overview

**As a** developer building agents with MCP tools  
**I want** a clear, repeatable way to run development-focused MCP servers and connect to them from a client  
**So that** DeepAgents-based agents can reliably discover and call the tools needed for real software development workflows (repo inspection, search, tests, git, docs)

## Acceptance Criteria

- [ ] Define and document canonical local MCP server ports/endpoints for a **development server suite**:
  - **dev_repo** (repo inspection: list/read) on **8100**
  - **dev_search** (code search: grep/semantic-ish search) on **8101**
  - **dev_tests** (test runner: pytest/targeted commands, allowlisted) on **8102**
  - **github** (official GitHub MCP server; remote; uses `GITHUB_TOKEN`) on **(remote)**
  - **dev_docs** (link scan/validate + docs navigation helpers) on **8104**
  - **dev_research** (internet research: web search + source capture) on **8105**
  - **dev_knowledge** (RAG retrieval + knowledge base maintenance) on **8106**
- [ ] Provide a runbook for starting the suite locally (separate terminals) and verifying the ports are reachable
- [ ] Provide a minimal client-side connectivity check:
  - tool discovery per server
  - one safe read-only tool call per server (happy path)
- [ ] Document failure modes and mitigations:
  - server down / wrong port
  - missing optional dependencies (pytest, git)
  - missing env vars for optional integrations
  - permission errors (workspace path not accessible)
- [ ] Define a safety policy for development MCP tools:
  - **Default read-only**
  - **Any write/exec/git-push requires HITL approval** (handled by US-DEEPAGENTS-003)

## Proposed Tool Map (v1)

These tool IDs are the *capabilities* we want available to the DeepAgent. Implementation can reuse existing tool functions where they already exist (see Notes).

- **dev_repo** (read-only)
  - `file.list_directory`
  - `file.read`
  - `file.search_content`
  - `file.get_info`
  - `file.exists`
- **dev_docs** (read-only by default; healing is gated)
  - `link.scan_all`
  - `link.validate`
  - `link.generate_report`
  - `link.heal` (RESTRICTED; requires HITL approval)
- **dev_search** (read-only)
  - `file.search_content` (baseline)
  - (future) fast code search across the repo with file-type filters
- **dev_tests** (execution; allowlisted commands only; can be HITL-gated)
  - run `pytest` for a specific path/test id
  - parse failures into a structured summary
- **github** (remote; read-only by default; any write ops are gated)
  - Use the official GitHub MCP server at `https://api.githubcopilot.com/mcp/`
  - Auth: `Authorization: Bearer $GITHUB_TOKEN`
  - Prefer read-only operations for v1 (search, read, list); gate write operations via HITL
- **dev_research** (network access; read-only)
  - `research.plan_research` (query decomposition)
  - `research.quick_search` (fast web research)
  - `research.web_search` (full research swarm with verification/synthesis)
  - `research.get_stats` (capabilities + diagnostics)
- **dev_knowledge** (RAG + knowledge base)
  - `rag_swarm.query` (end-to-end: retrieval + response + metrics)
  - `rag_swarm.semantic_search` (retrieval only)
  - `rag_swarm.analyze_query` (query analysis/rewrites)
  - `rag_swarm.get_stats` (capabilities + diagnostics)
  - (future) software catalog / anti-duplication:
    - `software_catalog.build_comprehensive_catalog`
    - `software_catalog.search_catalog_semantic`

## Notes

- Reference implementation patterns: `tests/deep_agents/deep_agents_mcp.ipynb`
- Existing FastMCP demo servers live in: `utils/mcp/fastmcp/` (weather/finance/news/calculator). Keep them for demos, but Sprint 8 focuses on development tooling.
- Existing internal MCP tool registry exists under `utils/mcp/server.py` and `utils/mcp/tools/`; we should reuse tool implementations where possible instead of re-inventing them.
- Existing MCP research and RAG tools already exist:
  - `utils/mcp/tools/research_swarm_tools.py` (web research swarm)
  - `utils/mcp/tools/rag_swarm_tools.py` (RAG swarm over ContextEngine/Qdrant)


