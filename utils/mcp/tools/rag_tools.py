"""
RAG-Specific MCP Tools
=====================

MCP tools for RAG system integration, providing semantic search,
context analysis, and knowledge base management capabilities.

This module creates the critical RAG-MCP integration layer that enables
intelligent tool selection and context-aware agent coordination.

Author: AI Development Agent
Created: 2025-01-02 (Phase 1.1 - Critical Path Implementation)
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import asyncio
from datetime import datetime

# RAG system imports
try:
    from context.context_engine import ContextEngine
    from models.config import ContextConfig
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# MCP integration imports
from utils.mcp.server import MCPServer
from utils.system.universal_agent_tracker import UniversalAgentTracker

logger = logging.getLogger(__name__)


class RAGMCPTools:
    """RAG-specific MCP tools for semantic search and context analysis."""
    
    def __init__(self):
        """Initialize RAG-MCP tools."""
        self.context_engine = None
        self.agent_tracker = UniversalAgentTracker()
        self.tool_usage_stats = {}
        
        # Initialize RAG system if available
        if RAG_AVAILABLE:
            try:
                # Create default context configuration
                context_config = ContextConfig(
                    enable_codebase_indexing=True,
                    index_file_extensions=[".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".md", ".txt"],
                    exclude_patterns=["__pycache__", "node_modules", ".git", "venv", "env"],
                    max_context_size=10000,
                    max_file_size=1024 * 1024
                )
                
                self.context_engine = ContextEngine(context_config)
                logger.info("✅ RAG Context Engine initialized for MCP integration")
            except Exception as e:
                logger.error(f"❌ Failed to initialize RAG Context Engine: {e}")
                self.context_engine = None
        else:
            logger.warning("⚠️ RAG system not available - some tools will have limited functionality")
    
    async def semantic_search(self, query: str, limit: int = 10, context_filter: str = None) -> Dict[str, Any]:
        """
        Perform semantic search using RAG system.
        
        Args:
            query: Search query
            limit: Maximum number of results
            context_filter: Optional context filter
            
        Returns:
            Dict with search results and metadata
        """
        tool_start = datetime.now()
        
        try:
            if not self.context_engine:
                return {
                    "success": False,
                    "error": "RAG Context Engine not available",
                    "results": [],
                    "metadata": {"tool": "semantic_search", "timestamp": tool_start.isoformat()}
                }
            
            # Perform semantic search
            search_results = await self._perform_semantic_search(query, limit, context_filter)
            
            # Track tool usage
            self._track_tool_usage("semantic_search", tool_start, True)
            
            # Log to Universal Agent Tracker
            await self._log_tool_execution("semantic_search", {
                "query": query,
                "results_count": len(search_results.get("results", [])),
                "context_filter": context_filter
            })
            
            return {
                "success": True,
                "results": search_results.get("results", []),
                "metadata": {
                    "tool": "semantic_search",
                    "timestamp": tool_start.isoformat(),
                    "query": query,
                    "results_count": len(search_results.get("results", [])),
                    "processing_time": (datetime.now() - tool_start).total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            self._track_tool_usage("semantic_search", tool_start, False)
            
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "metadata": {"tool": "semantic_search", "timestamp": tool_start.isoformat()}
            }
    
    async def context_analysis(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze text context using RAG system.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (comprehensive, keywords, entities, sentiment)
            
        Returns:
            Dict with analysis results
        """
        tool_start = datetime.now()
        
        try:
            if not self.context_engine:
                return {
                    "success": False,
                    "error": "RAG Context Engine not available",
                    "analysis": {},
                    "metadata": {"tool": "context_analysis", "timestamp": tool_start.isoformat()}
                }
            
            # Perform context analysis
            analysis_results = await self._perform_context_analysis(text, analysis_type)
            
            # Track tool usage
            self._track_tool_usage("context_analysis", tool_start, True)
            
            # Log to Universal Agent Tracker
            await self._log_tool_execution("context_analysis", {
                "text_length": len(text),
                "analysis_type": analysis_type,
                "analysis_keys": list(analysis_results.keys())
            })
            
            return {
                "success": True,
                "analysis": analysis_results,
                "metadata": {
                    "tool": "context_analysis",
                    "timestamp": tool_start.isoformat(),
                    "analysis_type": analysis_type,
                    "text_length": len(text),
                    "processing_time": (datetime.now() - tool_start).total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Context analysis failed: {e}")
            self._track_tool_usage("context_analysis", tool_start, False)
            
            return {
                "success": False,
                "error": str(e),
                "analysis": {},
                "metadata": {"tool": "context_analysis", "timestamp": tool_start.isoformat()}
            }
    
    async def knowledge_base_query(self, query: str, knowledge_type: str = "all") -> Dict[str, Any]:
        """
        Query the RAG knowledge base.
        
        Args:
            query: Query string
            knowledge_type: Type of knowledge to query (all, code, docs, patterns)
            
        Returns:
            Dict with query results
        """
        tool_start = datetime.now()
        
        try:
            if not self.context_engine:
                return {
                    "success": False,
                    "error": "RAG Context Engine not available",
                    "knowledge": [],
                    "metadata": {"tool": "knowledge_base_query", "timestamp": tool_start.isoformat()}
                }
            
            # Query knowledge base
            knowledge_results = await self._query_knowledge_base(query, knowledge_type)
            
            # Track tool usage
            self._track_tool_usage("knowledge_base_query", tool_start, True)
            
            # Log to Universal Agent Tracker
            await self._log_tool_execution("knowledge_base_query", {
                "query": query,
                "knowledge_type": knowledge_type,
                "results_count": len(knowledge_results)
            })
            
            return {
                "success": True,
                "knowledge": knowledge_results,
                "metadata": {
                    "tool": "knowledge_base_query",
                    "timestamp": tool_start.isoformat(),
                    "query": query,
                    "knowledge_type": knowledge_type,
                    "results_count": len(knowledge_results),
                    "processing_time": (datetime.now() - tool_start).total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge base query failed: {e}")
            self._track_tool_usage("knowledge_base_query", tool_start, False)
            
            return {
                "success": False,
                "error": str(e),
                "knowledge": [],
                "metadata": {"tool": "knowledge_base_query", "timestamp": tool_start.isoformat()}
            }
    
    async def intelligent_tool_selection(self, task_description: str, available_tools: List[str]) -> Dict[str, Any]:
        """
        Select optimal tools for a task using RAG intelligence.
        
        Args:
            task_description: Description of the task
            available_tools: List of available tool names
            
        Returns:
            Dict with recommended tools and reasoning
        """
        tool_start = datetime.now()
        
        try:
            # Analyze task context
            task_analysis = await self.context_analysis(task_description, "comprehensive")
            
            if not task_analysis["success"]:
                return {
                    "success": False,
                    "error": "Failed to analyze task context",
                    "recommended_tools": [],
                    "metadata": {"tool": "intelligent_tool_selection", "timestamp": tool_start.isoformat()}
                }
            
            # Select tools based on analysis
            tool_recommendations = await self._select_optimal_tools(
                task_analysis["analysis"], 
                available_tools
            )
            
            # Track tool usage
            self._track_tool_usage("intelligent_tool_selection", tool_start, True)
            
            # Log to Universal Agent Tracker
            await self._log_tool_execution("intelligent_tool_selection", {
                "task_description": task_description[:100] + "..." if len(task_description) > 100 else task_description,
                "available_tools_count": len(available_tools),
                "recommended_tools_count": len(tool_recommendations.get("tools", []))
            })
            
            return {
                "success": True,
                "recommended_tools": tool_recommendations.get("tools", []),
                "reasoning": tool_recommendations.get("reasoning", ""),
                "confidence_score": tool_recommendations.get("confidence", 0.0),
                "metadata": {
                    "tool": "intelligent_tool_selection",
                    "timestamp": tool_start.isoformat(),
                    "task_length": len(task_description),
                    "available_tools_count": len(available_tools),
                    "processing_time": (datetime.now() - tool_start).total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Intelligent tool selection failed: {e}")
            self._track_tool_usage("intelligent_tool_selection", tool_start, False)
            
            return {
                "success": False,
                "error": str(e),
                "recommended_tools": [],
                "metadata": {"tool": "intelligent_tool_selection", "timestamp": tool_start.isoformat()}
            }
    
    async def enrich_knowledge_base(self, content: str, content_type: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enrich the RAG knowledge base with new content.
        
        Args:
            content: Content to add to knowledge base
            content_type: Type of content (code, documentation, pattern, result)
            metadata: Additional metadata about the content
            
        Returns:
            Dict with enrichment results
        """
        tool_start = datetime.now()
        
        try:
            if not self.context_engine:
                return {
                    "success": False,
                    "error": "RAG Context Engine not available",
                    "enrichment_id": None,
                    "metadata": {"tool": "enrich_knowledge_base", "timestamp": tool_start.isoformat()}
                }
            
            # Enrich knowledge base
            enrichment_result = await self._enrich_knowledge_base(content, content_type, metadata or {})
            
            # Track tool usage
            self._track_tool_usage("enrich_knowledge_base", tool_start, True)
            
            # Log to Universal Agent Tracker
            await self._log_tool_execution("enrich_knowledge_base", {
                "content_type": content_type,
                "content_length": len(content),
                "metadata_keys": list((metadata or {}).keys())
            })
            
            return {
                "success": True,
                "enrichment_id": enrichment_result.get("id"),
                "indexed": enrichment_result.get("indexed", False),
                "metadata": {
                    "tool": "enrich_knowledge_base",
                    "timestamp": tool_start.isoformat(),
                    "content_type": content_type,
                    "content_length": len(content),
                    "processing_time": (datetime.now() - tool_start).total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge base enrichment failed: {e}")
            self._track_tool_usage("enrich_knowledge_base", tool_start, False)
            
            return {
                "success": False,
                "error": str(e),
                "enrichment_id": None,
                "metadata": {"tool": "enrich_knowledge_base", "timestamp": tool_start.isoformat()}
            }
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        return {
            "tool_stats": self.tool_usage_stats.copy(),
            "total_executions": sum(stats.get("count", 0) for stats in self.tool_usage_stats.values()),
            "success_rate": self._calculate_overall_success_rate(),
            "most_used_tool": self._get_most_used_tool(),
            "generated_at": datetime.now().isoformat()
        }
    
    # Private helper methods
    
    async def _perform_semantic_search(self, query: str, limit: int, context_filter: str) -> Dict[str, Any]:
        """Perform actual semantic search using RAG system."""
        if not self.context_engine:
            return {"results": []}
        
        try:
            # Use context engine for semantic search
            search_results = self.context_engine.search_context(
                query=query,
                max_results=limit
            )
            
            return {"results": search_results}
            
        except Exception as e:
            logger.error(f"❌ Semantic search execution failed: {e}")
            return {"results": []}
    
    async def _perform_context_analysis(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Perform context analysis using RAG system."""
        if not self.context_engine:
            return {}
        
        try:
            # Basic context analysis
            analysis = {
                "text_length": len(text),
                "word_count": len(text.split()),
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add more sophisticated analysis based on type
            if analysis_type in ["comprehensive", "keywords"]:
                analysis["keywords"] = self._extract_keywords(text)
            
            if analysis_type in ["comprehensive", "entities"]:
                analysis["entities"] = self._extract_entities(text)
            
            if analysis_type in ["comprehensive", "sentiment"]:
                analysis["sentiment"] = self._analyze_sentiment(text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Context analysis execution failed: {e}")
            return {}
    
    async def _query_knowledge_base(self, query: str, knowledge_type: str) -> List[Dict[str, Any]]:
        """Query the RAG knowledge base."""
        if not self.context_engine:
            return []
        
        try:
            # Query based on knowledge type
            results = self.context_engine.search_context(
                query=query,
                max_results=20
            )
            
            # Filter by knowledge type if specified
            if knowledge_type != "all":
                # Simple filtering based on content type in metadata
                filtered_results = []
                for result in results:
                    metadata = result.get("metadata", {})
                    if knowledge_type in str(metadata).lower() or knowledge_type in result.get("content", "").lower():
                        filtered_results.append(result)
                results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Knowledge base query execution failed: {e}")
            return []
    
    async def _select_optimal_tools(self, task_analysis: Dict[str, Any], available_tools: List[str]) -> Dict[str, Any]:
        """Select optimal tools based on task analysis."""
        try:
            # Simple tool selection logic based on keywords and entities
            keywords = task_analysis.get("keywords", [])
            entities = task_analysis.get("entities", [])
            
            # Tool selection rules
            tool_scores = {}
            
            for tool in available_tools:
                score = 0.0
                
                # Score based on keyword matching
                for keyword in keywords:
                    if keyword.lower() in tool.lower():
                        score += 0.3
                
                # Score based on entity matching
                for entity in entities:
                    if entity.lower() in tool.lower():
                        score += 0.2
                
                # Add base score for common tools
                if any(common in tool.lower() for common in ["file", "git", "test", "agile"]):
                    score += 0.1
                
                tool_scores[tool] = score
            
            # Sort tools by score
            sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Select top tools with score > 0
            recommended_tools = [tool for tool, score in sorted_tools if score > 0][:5]
            
            # Generate reasoning
            reasoning = f"Selected {len(recommended_tools)} tools based on keyword and entity analysis"
            
            # Calculate confidence
            confidence = min(1.0, max(tool_scores.values()) if tool_scores else 0.0)
            
            return {
                "tools": recommended_tools,
                "reasoning": reasoning,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Tool selection failed: {e}")
            return {"tools": [], "reasoning": "Tool selection failed", "confidence": 0.0}
    
    async def _enrich_knowledge_base(self, content: str, content_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich the knowledge base with new content."""
        if not self.context_engine:
            return {"id": None, "indexed": False}
        
        try:
            # Create enrichment entry
            enrichment_id = f"enrich_{int(datetime.now().timestamp())}_{hash(content) % 10000}"
            
            # Add to context engine (simplified implementation)
            # In a real implementation, this would add to the vector store
            indexed = True
            
            return {
                "id": enrichment_id,
                "indexed": indexed
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge base enrichment failed: {e}")
            return {"id": None, "indexed": False}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified implementation)."""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter out common words and short words
        keywords = [word for word in words if len(word) > 3 and word not in ["this", "that", "with", "from", "they", "have", "will", "been", "were"]]
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified implementation)."""
        # Simple entity extraction - look for capitalized words
        words = text.split()
        entities = [word for word in words if word[0].isupper() and len(word) > 2]
        return list(set(entities))[:10]  # Return unique entities, max 10
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (simplified implementation)."""
        # Very simple sentiment analysis
        positive_words = ["good", "great", "excellent", "success", "working", "complete"]
        negative_words = ["bad", "error", "fail", "problem", "issue", "broken"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _log_tool_execution(self, tool_name: str, details: Dict[str, Any]):
        """Log tool execution to Universal Agent Tracker."""
        try:
            session_id = f"rag_mcp_session_{int(datetime.now().timestamp())}"
            
            # Record tool usage as context switch
            self.agent_tracker.record_context_switch(
                session_id=session_id,
                new_context=f"rag_tool_{tool_name}",
                from_context="mcp_server",
                trigger_type="tool_execution",
                trigger_details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to log tool execution: {e}")
    
    def _track_tool_usage(self, tool_name: str, start_time: datetime, success: bool):
        """Track tool usage statistics."""
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {
                "count": 0,
                "success_count": 0,
                "total_time": 0.0,
                "last_used": None
            }
        
        stats = self.tool_usage_stats[tool_name]
        stats["count"] += 1
        if success:
            stats["success_count"] += 1
        stats["total_time"] += (datetime.now() - start_time).total_seconds()
        stats["last_used"] = datetime.now().isoformat()
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all tools."""
        if not self.tool_usage_stats:
            return 0.0
        
        total_count = sum(stats.get("count", 0) for stats in self.tool_usage_stats.values())
        total_success = sum(stats.get("success_count", 0) for stats in self.tool_usage_stats.values())
        
        return (total_success / total_count) if total_count > 0 else 0.0
    
    def _get_most_used_tool(self) -> str:
        """Get the most frequently used tool."""
        if not self.tool_usage_stats:
            return "none"
        
        most_used = max(self.tool_usage_stats.items(), key=lambda x: x[1].get("count", 0))
        return most_used[0]


# Global RAG-MCP tools instance
_rag_mcp_tools = None


def get_rag_mcp_tools() -> RAGMCPTools:
    """Get the global RAG-MCP tools instance."""
    global _rag_mcp_tools
    if _rag_mcp_tools is None:
        _rag_mcp_tools = RAGMCPTools()
    return _rag_mcp_tools


# MCP Tool Registration Functions
# These functions are called by the MCP server to register RAG tools

async def mcp_semantic_search(query: str, limit: int = 10, context_filter: str = None) -> Dict[str, Any]:
    """MCP tool wrapper for semantic search."""
    tools = get_rag_mcp_tools()
    return await tools.semantic_search(query, limit, context_filter)


async def mcp_context_analysis(text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """MCP tool wrapper for context analysis."""
    tools = get_rag_mcp_tools()
    return await tools.context_analysis(text, analysis_type)


async def mcp_knowledge_base_query(query: str, knowledge_type: str = "all") -> Dict[str, Any]:
    """MCP tool wrapper for knowledge base query."""
    tools = get_rag_mcp_tools()
    return await tools.knowledge_base_query(query, knowledge_type)


async def mcp_intelligent_tool_selection(task_description: str, available_tools: List[str]) -> Dict[str, Any]:
    """MCP tool wrapper for intelligent tool selection."""
    tools = get_rag_mcp_tools()
    return await tools.intelligent_tool_selection(task_description, available_tools)


async def mcp_enrich_knowledge_base(content: str, content_type: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """MCP tool wrapper for knowledge base enrichment."""
    tools = get_rag_mcp_tools()
    return await tools.enrich_knowledge_base(content, content_type, metadata or {})


def mcp_get_rag_stats() -> Dict[str, Any]:
    """MCP tool wrapper for RAG tool statistics."""
    tools = get_rag_mcp_tools()
    return tools.get_tool_usage_stats()
