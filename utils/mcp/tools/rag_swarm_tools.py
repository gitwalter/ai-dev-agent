#!/usr/bin/env python3
"""
RAG Swarm MCP Tools
===================

MCP tools for RAG Agent Swarm integration, providing high-quality semantic
search and context-aware retrieval using 5 specialized agents.

Tools expose the RAG Swarm (QueryAnalyst, RetrievalSpecialist, ReRanker,
QualityAssurance, Writer) for use by other agents and systems.

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

# RAG Swarm imports
try:
    from agents.rag.rag_swarm_langgraph import RAGSwarmCoordinator
    from context.context_engine import ContextEngine
    from models.config import ContextConfig
    RAG_SWARM_AVAILABLE = True
except ImportError:
    RAG_SWARM_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global RAG swarm instance (lazy initialization)
_rag_swarm_coordinator = None


def get_rag_swarm_coordinator() -> Optional['RAGSwarmCoordinator']:
    """Get or create RAG swarm coordinator instance."""
    global _rag_swarm_coordinator
    
    if _rag_swarm_coordinator is None and RAG_SWARM_AVAILABLE:
        try:
            # Initialize Context Engine
            context_config = ContextConfig(
                enable_codebase_indexing=True,
                index_file_extensions=[".py", ".js", ".ts", ".md", ".txt"],
                exclude_patterns=["__pycache__", "node_modules", ".git", "venv"],
                max_context_size=10000
            )
            context_engine = ContextEngine(context_config)
            
            # Initialize RAG Swarm
            _rag_swarm_coordinator = RAGSwarmCoordinator(context_engine)
            logger.info("✅ RAG Swarm Coordinator initialized for MCP tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Swarm: {e}")
            return None
    
    return _rag_swarm_coordinator


# ============================================================================
# MCP Tools - RAG Swarm
# ============================================================================

if MCP_AVAILABLE:
    
    @mcp_tool(
        "rag_swarm.query",
        "Query RAG swarm for high-quality semantic search and response generation",
        AccessLevel.UNRESTRICTED,
        ToolCategory.RAG
    )
    def rag_swarm_query_mcp(
        query: str,
        max_results: int = 10,
        quality_threshold: float = 0.7,
        enable_re_retrieval: bool = True
    ) -> Dict[str, Any]:
        """
        Query RAG Agent Swarm for high-quality semantic search and response.
        
        Uses 5 specialized agents:
        - QueryAnalyst: Analyzes and rewrites queries
        - RetrievalSpecialist: Multi-strategy retrieval
        - ReRanker: Intelligent ranking and deduplication
        - QualityAssurance: Quality validation and re-retrieval
        - Writer: Response synthesis with citations
        
        Args:
            query: Search query
            max_results: Maximum results to retrieve
            quality_threshold: Minimum quality score (0-1)
            enable_re_retrieval: Allow re-retrieval if quality low
            
        Returns:
            RAG swarm response with generated text, sources, and metrics
        """
        if not RAG_SWARM_AVAILABLE:
            return {
                "error": "RAG Swarm not available",
                "message": "Install required dependencies: langchain, langgraph"
            }
        
        coordinator = get_rag_swarm_coordinator()
        if not coordinator:
            return {"error": "Failed to initialize RAG Swarm coordinator"}
        
        try:
            # Execute RAG swarm workflow
            result = asyncio.run(
                coordinator.query(
                    query=query,
                    max_results=max_results,
                    quality_threshold=quality_threshold,
                    enable_re_retrieval=enable_re_retrieval
                )
            )
            
            return {
                "success": True,
                "query": query,
                "response": result.get("final_response", {}),
                "quality_report": result.get("quality_report", {}),
                "metrics": result.get("metrics", {}),
                "stages_completed": result.get("stages_completed", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG swarm query failed: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "rag_swarm.semantic_search",
        "Perform semantic search using RAG swarm retrieval specialist",
        AccessLevel.UNRESTRICTED,
        ToolCategory.RAG
    )
    def rag_swarm_semantic_search_mcp(
        query: str,
        max_results: int = 10,
        search_strategy: str = "focused"
    ) -> Dict[str, Any]:
        """
        Semantic search using RAG Swarm's RetrievalSpecialist.
        
        Args:
            query: Search query
            max_results: Maximum results
            search_strategy: Search strategy (focused, broad, multi-stage)
            
        Returns:
            Search results with relevance scores
        """
        if not RAG_SWARM_AVAILABLE:
            return {"error": "RAG Swarm not available"}
        
        coordinator = get_rag_swarm_coordinator()
        if not coordinator:
            return {"error": "Failed to initialize RAG Swarm"}
        
        try:
            # Use retrieval specialist directly
            results = asyncio.run(
                coordinator.retrieval_specialist.retrieve(
                    query=query,
                    strategy=search_strategy,
                    max_results=max_results
                )
            )
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results),
                "strategy_used": search_strategy,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "rag_swarm.analyze_query",
        "Analyze query using RAG swarm query analyst",
        AccessLevel.UNRESTRICTED,
        ToolCategory.RAG
    )
    def rag_swarm_analyze_query_mcp(query: str) -> Dict[str, Any]:
        """
        Analyze query intent and generate variations using QueryAnalyst.
        
        Args:
            query: Query to analyze
            
        Returns:
            Query analysis with intent, rewrites, and key concepts
        """
        if not RAG_SWARM_AVAILABLE:
            return {"error": "RAG Swarm not available"}
        
        coordinator = get_rag_swarm_coordinator()
        if not coordinator:
            return {"error": "Failed to initialize RAG Swarm"}
        
        try:
            # Use query analyst directly
            analysis = asyncio.run(
                coordinator.query_analyst.analyze_query(query)
            )
            
            return {
                "success": True,
                "query": query,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "rag_swarm.get_stats",
        "Get RAG swarm usage statistics and performance metrics",
        AccessLevel.UNRESTRICTED,
        ToolCategory.RAG
    )
    def rag_swarm_get_stats_mcp() -> Dict[str, Any]:
        """
        Get RAG swarm statistics.
        
        Returns:
            Usage statistics and performance metrics
        """
        if not RAG_SWARM_AVAILABLE:
            return {"error": "RAG Swarm not available"}
        
        coordinator = get_rag_swarm_coordinator()
        if not coordinator:
            return {"error": "RAG Swarm not initialized"}
        
        try:
            # Get statistics from context engine
            context_engine = coordinator.context_engine
            
            stats = {
                "success": True,
                "swarm_initialized": True,
                "agents": {
                    "query_analyst": "QueryAnalystAgent",
                    "retrieval_specialist": "RetrievalSpecialistAgent",
                    "re_ranker": "ReRankerAgent",
                    "quality_assurance": "QualityAssuranceAgent",
                    "writer": "WriterAgent"
                },
                "context_engine": {
                    "semantic_search_enabled": hasattr(context_engine, 'embeddings'),
                    "indexed_files": len(getattr(context_engine, 'indexed_files', [])),
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get RAG swarm stats: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test RAG swarm tools
    print("🧪 Testing RAG Swarm MCP Tools\n")
    
    # Test query
    print("1. Testing rag_swarm.query...")
    result = rag_swarm_query_mcp(
        query="How do I create a context-aware agent?",
        max_results=5
    )
    print(f"   Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"   Response length: {len(str(result.get('response', {})))}")
    
    # Test semantic search
    print("\n2. Testing rag_swarm.semantic_search...")
    result = rag_swarm_semantic_search_mcp(
        query="agent swarm architecture",
        max_results=3
    )
    print(f"   Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"   Found: {result.get('total_results', 0)} results")
    
    # Test stats
    print("\n3. Testing rag_swarm.get_stats...")
    result = rag_swarm_get_stats_mcp()
    print(f"   Result: {result.get('success', False)}")
    if result.get('success'):
        print(f"   Agents: {len(result.get('agents', {}))}")
    
    print("\n✅ RAG Swarm MCP tools test complete!")

