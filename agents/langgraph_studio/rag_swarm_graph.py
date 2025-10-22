"""
RAG Swarm Graph for LangGraph Studio.

Complete RAG pipeline with 5 specialized agents:
- QueryAnalyst
- RetrievalSpecialist  
- ReRanker
- QualityAssurance
- Writer
"""

from context.context_engine import ContextEngine
from agents.rag.rag_swarm_langgraph import RAGSwarmCoordinator
from models.config import ContextConfig

# Initialize context engine
config = ContextConfig(
    enable_codebase_indexing=True,
    enable_semantic_search=True,
    vector_db_path="./context_db"
)
context_engine = ContextEngine(config)

# Create RAG coordinator
coordinator = RAGSwarmCoordinator(context_engine)

# Export for Studio
graph = coordinator.app

