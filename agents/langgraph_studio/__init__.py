"""
LangGraph Studio Integration for AI-Dev-Agent
==============================================

This module provides LangGraph Studio compatibility for our agent system,
enabling visual debugging, human-in-the-loop interaction, and step-by-step
execution of agent workflows.

Key Features:
- Visual graph visualization in LangGraph Studio
- Step-by-step debugging with pause/resume
- State inspection and manipulation
- Human review checkpoints
- Performance monitoring

Available Graphs:
- RAGSwarmCoordinator: Document retrieval and synthesis pipeline
- WebResearchSwarmCoordinator: Web research pipeline
- DevelopmentPipelineGraph: Complete software development workflow (coming soon)

Usage:
    # LangGraph Studio automatically discovers graphs via langgraph.json
    # Just open the project in LangGraph Studio desktop app

For more information:
- See: docs/agile/sprints/sprint_6/analysis/LANGGRAPH_STUDIO_INTEGRATION_DESIGN.md
- LangGraph Studio: https://blog.langchain.com/langgraph-studio-the-first-agent-ide/
"""

__version__ = "0.1.0"
__all__ = []

# Note: Graph wrappers will be added in future sprints
# Current Sprint 6 focus: RAG and MCP integration
# LangGraph Studio integration: Sprint 7 candidate

