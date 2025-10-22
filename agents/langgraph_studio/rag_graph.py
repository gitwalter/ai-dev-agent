"""
RAG Pipeline Graph for LangGraph Studio.

This module provides a compiled LangGraph workflow for the RAG pipeline.
"""

from context.context_engine import ContextEngine
from agents.rag.rag_swarm_langgraph import RAGSwarmCoordinator
from models.config import ContextConfig

# Initialize context engine with default config
config = ContextConfig(
    enable_codebase_indexing=True,
    enable_semantic_search=True,
    vector_db_path="./context_db"
)
context_engine = ContextEngine(config)

# Create RAG coordinator and get compiled graph
coordinator = RAGSwarmCoordinator(context_engine)

# Export the compiled graph for LangGraph Studio
graph = coordinator.app

