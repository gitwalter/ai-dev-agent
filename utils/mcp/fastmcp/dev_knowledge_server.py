"""
Development MCP Server: dev_knowledge (FastMCP)
===============================================

RAG / knowledge-base retrieval tools for development agents.

Transport:
- streamable-http (HTTP) at /mcp

Port:
- 8106

Tools (wrapping existing RAG swarm coordinator):
- rag_swarm.query
- rag_swarm.semantic_search
- rag_swarm.analyze_query
- rag_swarm.get_stats
"""

from __future__ import annotations

from fastmcp import FastMCP


mcp = FastMCP("dev_knowledge")


def _coordinator():
    from utils.mcp.tools.rag_swarm_tools import get_rag_swarm_coordinator

    return get_rag_swarm_coordinator()


@mcp.tool(name="rag_swarm.analyze_query")
async def rag_swarm_analyze_query(query: str) -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "RAG swarm coordinator not available"}

    analysis = await coordinator.query_analyst.analyze_query(query)
    return {"success": True, "query": query, "analysis": analysis}


@mcp.tool(name="rag_swarm.semantic_search")
async def rag_swarm_semantic_search(query: str, max_results: int = 10, search_strategy: str = "focused") -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "RAG swarm coordinator not available"}

    results = await coordinator.retrieval_specialist.retrieve(query=query, strategy=search_strategy, max_results=max_results)
    return {
        "success": True,
        "query": query,
        "results": results,
        "total_results": len(results) if isinstance(results, list) else None,
        "strategy_used": search_strategy,
    }


@mcp.tool(name="rag_swarm.query")
async def rag_swarm_query(query: str, max_results: int = 10, quality_threshold: float = 0.7, enable_re_retrieval: bool = True) -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "RAG swarm coordinator not available"}

    result = await coordinator.query(
        query=query,
        max_results=max_results,
        quality_threshold=quality_threshold,
        enable_re_retrieval=enable_re_retrieval,
    )
    return {
        "success": True,
        "query": query,
        "response": result.get("final_response", {}),
        "quality_report": result.get("quality_report", {}),
        "metrics": result.get("metrics", {}),
        "stages_completed": result.get("stages_completed", []),
    }


@mcp.tool(name="rag_swarm.get_stats")
async def rag_swarm_get_stats() -> dict:
    coordinator = _coordinator()
    if not coordinator:
        return {"success": False, "error": "RAG swarm coordinator not available"}

    # Keep this minimal and robust (no LLM calls required)
    return {"success": True, "swarm_initialized": True}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8106)


