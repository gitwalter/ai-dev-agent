#!/usr/bin/env python3
"""
Web Research Swarm MCP Tools
=============================

MCP tools for Web Research Agent Swarm integration, providing comprehensive
web research capabilities using 5 specialized agents with LangChain parsing.

Tools expose the Research Swarm (QueryPlanner, WebSearch, ContentParser,
Verification, Synthesis) for web-based research and information gathering.

Created: 2025-10-10
Sprint: US-RAG-001 Enhancement
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

# MCP Tool Integration
try:
    from utils.mcp.mcp_tool import mcp_tool, AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Research Swarm imports
try:
    from agents.research.web_research_swarm import WebResearchSwarmCoordinator
    RESEARCH_SWARM_AVAILABLE = True
except ImportError:
    RESEARCH_SWARM_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global research swarm instance (lazy initialization)
_research_swarm_coordinator = None


def get_research_swarm_coordinator() -> Optional['WebResearchSwarmCoordinator']:
    """Get or create research swarm coordinator instance."""
    global _research_swarm_coordinator
    
    if _research_swarm_coordinator is None and RESEARCH_SWARM_AVAILABLE:
        try:
            _research_swarm_coordinator = WebResearchSwarmCoordinator()
            logger.info("✅ Research Swarm Coordinator initialized for MCP tools")
        except Exception as e:
            logger.error(f"Failed to initialize Research Swarm: {e}")
            return None
    
    return _research_swarm_coordinator


# ============================================================================
# MCP Tools - Research Swarm
# ============================================================================

if MCP_AVAILABLE:
    
    @mcp_tool(
        "research.web_search",
        "Conduct comprehensive web research using 5-agent swarm",
        AccessLevel.UNRESTRICTED,
        ToolCategory.WEB_RESEARCH
    )
    def research_web_search_mcp(
        query: str,
        max_sources: int = 10,
        research_depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Comprehensive web research using Research Agent Swarm.
        
        Uses 5 specialized agents:
        - QueryPlanner: Plans research strategy
        - WebSearch: Executes web searches
        - ContentParser: Parses and extracts content (LangChain)
        - Verification: Verifies quality and credibility
        - Synthesis: Creates comprehensive report
        
        Args:
            query: Research question or topic
            max_sources: Maximum sources to analyze (default: 10)
            research_depth: Depth (quick, standard, comprehensive, exhaustive)
            
        Returns:
            Comprehensive research report with synthesis, sources, and metrics
        """
        if not RESEARCH_SWARM_AVAILABLE:
            return {
                "error": "Research Swarm not available",
                "message": "Install required dependencies: langgraph, langchain"
            }
        
        coordinator = get_research_swarm_coordinator()
        if not coordinator:
            return {"error": "Failed to initialize Research Swarm coordinator"}
        
        try:
            # Execute research swarm workflow
            result = asyncio.run(
                coordinator.research(
                    query=query,
                    max_sources=max_sources,
                    research_depth=research_depth
                )
            )
            
            return {
                "success": result.get("success", False),
                "query": query,
                "synthesis": result.get("synthesis", {}),
                "verification_report": result.get("verification_report", {}),
                "research_plan": result.get("research_plan", {}),
                "stages_completed": result.get("stages_completed", []),
                "metrics": result.get("metrics", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Research swarm failed: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "research.quick_search",
        "Quick web search for simple queries (faster, less comprehensive)",
        AccessLevel.UNRESTRICTED,
        ToolCategory.WEB_RESEARCH
    )
    def research_quick_search_mcp(
        query: str,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Quick web research for simple queries.
        
        Args:
            query: Simple research question
            max_sources: Maximum sources (default: 5)
            
        Returns:
            Quick research summary
        """
        return research_web_search_mcp(
            query=query,
            max_sources=max_sources,
            research_depth="quick"
        )
    
    
    @mcp_tool(
        "research.deep_dive",
        "Comprehensive deep-dive research (slower, very thorough)",
        AccessLevel.UNRESTRICTED,
        ToolCategory.WEB_RESEARCH
    )
    def research_deep_dive_mcp(
        query: str,
        max_sources: int = 20
    ) -> Dict[str, Any]:
        """
        Comprehensive deep-dive research.
        
        Args:
            query: Complex research question
            max_sources: Maximum sources (default: 20)
            
        Returns:
            Comprehensive research report
        """
        return research_web_search_mcp(
            query=query,
            max_sources=max_sources,
            research_depth="comprehensive"
        )
    
    
    @mcp_tool(
        "research.plan_research",
        "Plan research strategy without executing search",
        AccessLevel.UNRESTRICTED,
        ToolCategory.WEB_RESEARCH
    )
    def research_plan_mcp(
        query: str,
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Plan research strategy using QueryPlannerAgent.
        
        Args:
            query: Research question
            depth: Research depth
            
        Returns:
            Research plan with sub-queries, key concepts, search terms
        """
        if not RESEARCH_SWARM_AVAILABLE:
            return {"error": "Research Swarm not available"}
        
        coordinator = get_research_swarm_coordinator()
        if not coordinator:
            return {"error": "Failed to initialize Research Swarm"}
        
        try:
            # Use query planner directly
            plan = asyncio.run(
                coordinator.query_planner.plan_research(query, depth)
            )
            
            return {
                "success": True,
                "query": query,
                "plan": plan,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Research planning failed: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "research.get_stats",
        "Get research swarm statistics and capabilities",
        AccessLevel.UNRESTRICTED,
        ToolCategory.WEB_RESEARCH
    )
    def research_get_stats_mcp() -> Dict[str, Any]:
        """
        Get research swarm statistics.
        
        Returns:
            Swarm capabilities and status
        """
        if not RESEARCH_SWARM_AVAILABLE:
            return {"error": "Research Swarm not available"}
        
        coordinator = get_research_swarm_coordinator()
        if not coordinator:
            return {"error": "Research Swarm not initialized"}
        
        try:
            stats = {
                "success": True,
                "swarm_initialized": True,
                "agents": {
                    "query_planner": "QueryPlannerAgent (Gemini 2.0 Flash)",
                    "web_search": "WebSearchAgent (Search APIs)",
                    "content_parser": "ContentParserAgent (LangChain parsing)",
                    "verification": "VerificationAgent (Gemini 2.0 Flash)",
                    "synthesis": "SynthesisAgent (Gemini 2.0 Flash)"
                },
                "capabilities": {
                    "langchain_parsing": True,
                    "async_loading": True,
                    "quality_verification": True,
                    "re_search": True,
                    "langgraph_orchestration": True
                },
                "research_depths": ["quick", "standard", "comprehensive", "exhaustive"],
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get research swarm stats: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test research swarm tools
    print("🧪 Testing Research Swarm MCP Tools\n")
    
    # Test research planning
    print("1. Testing research.plan_research...")
    result = research_plan_mcp(
        query="What are best practices for API integration?",
        depth="standard"
    )
    print(f"   Result: {result.get('success', False)}")
    if result.get('success'):
        plan = result.get('plan', {})
        print(f"   Strategy: {plan.get('strategy')}")
        print(f"   Sub-queries: {len(plan.get('sub_queries', []))}")
    
    # Test quick search
    print("\n2. Testing research.quick_search...")
    result = research_quick_search_mcp(
        query="Google Drive API authentication",
        max_sources=3
    )
    print(f"   Result: {result.get('success', False)}")
    if result.get('success'):
        synthesis = result.get('synthesis', {})
        print(f"   Sources: {synthesis.get('sources_used', 0)}")
    
    # Test stats
    print("\n3. Testing research.get_stats...")
    result = research_get_stats_mcp()
    print(f"   Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"   Agents: {len(result.get('agents', {}))}")
        print(f"   LangChain parsing: {result.get('capabilities', {}).get('langchain_parsing')}")
    
    print("\n✅ Research Swarm MCP tools test complete!")

