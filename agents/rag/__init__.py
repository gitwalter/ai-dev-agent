"""
RAG Agent Swarm Package

Specialized agents for Retrieval Augmented Generation operations.
All agents use LangGraph for proper tracing and agent handover.

For Development Agents:
    Use DevelopmentContextAgent to get RAG-enhanced context.
    This agent delegates to the RAG swarm and returns enriched context.
"""

# Phase 1 & 2: Official LangChain RAG implementations
from agents.rag.simple_rag import SimpleRAG, create_simple_rag
from agents.rag.agentic_rag import AgenticRAG, create_agentic_rag

# Keep these for reference - may be used as enhancements later
from agents.rag.query_analyst_agent import QueryAnalystAgent
from agents.rag.retrieval_specialist_agent import RetrievalSpecialistAgent
from agents.rag.re_ranker_agent import ReRankerAgent
from agents.rag.quality_assurance_agent import QualityAssuranceAgent
from agents.rag.writer_agent import WriterAgent

# Keep coordinator for reference only - don't use directly
from agents.rag.rag_swarm_coordinator import RAGSwarmCoordinator

# Development context agent (uses RAG)
from agents.rag.development_context_agent import create_development_context_agent, create_development_context_graph

__all__ = [
    # Phase 1 & 2: Official LangChain RAG (ACTIVE)
    'SimpleRAG',
    'create_simple_rag',
    'AgenticRAG',
    'create_agentic_rag',
    # Reference agents (for future enhancements)
    'QueryAnalystAgent',
    'RetrievalSpecialistAgent',
    'ReRankerAgent',
    'QualityAssuranceAgent',
    'WriterAgent',
    'RAGSwarmCoordinator',
    # Development context
    'create_development_context_agent',
    'create_development_context_graph',
]

