"""
Development MCP Server: dev_research (FastMCP)
==============================================

Internet research tools for development agents.

Transport:
- streamable-http (HTTP) at /mcp

Port:
- 8105

Tools (wrapping existing MCP research swarm tools):
- research.plan_research
- research.quick_search
- research.web_search
- research.get_stats
"""

from __future__ import annotations

from fastmcp import FastMCP


mcp = FastMCP("dev_research")


def _coordinator():
    from utils.mcp.tools.research_swarm_tools import get_research_swarm_coordinator

    return get_research_swarm_coordinator()


@mcp.tool(name="research.plan_research")
async def research_plan_research(query: str, depth: str = "standard") -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "Research swarm coordinator not available"}

    plan = await coordinator.query_planner.plan_research(query, depth)
    return {"success": True, "query": query, "plan": plan}


@mcp.tool(name="research.web_search")
async def research_web_search(query: str, max_sources: int = 10, research_depth: str = "standard") -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "Research swarm coordinator not available"}

    result = await coordinator.research(query=query, max_sources=max_sources, research_depth=research_depth)
    return {
        "success": bool(result.get("success", False)),
        "query": query,
        "synthesis": result.get("synthesis", {}),
        "verification_report": result.get("verification_report", {}),
        "research_plan": result.get("research_plan", {}),
        "stages_completed": result.get("stages_completed", []),
        "metrics": result.get("metrics", {}),
    }


@mcp.tool(name="research.quick_search")
async def research_quick_search(query: str, max_sources: int = 5) -> dict:
    return await research_web_search(query=query, max_sources=max_sources, research_depth="quick")


@mcp.tool(name="research.get_stats")
async def research_get_stats() -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "Research swarm coordinator not available"}

    # Keep this minimal and robust (no LLM calls required)
    return {
        "success": True,
        "swarm_initialized": True,
        "capabilities": {"planning": True, "web_search": True, "verification": True, "synthesis": True},
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8105)


