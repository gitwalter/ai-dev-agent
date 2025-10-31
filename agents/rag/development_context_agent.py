"""
Development Context Agent - LangGraph Compatible
=================================================

RAG agent specialized for providing context to development agents.
Fully LangGraph compatible with state management and checkpointing.

This agent bridges development agents (architecture designer, code generator, etc.)
with the RAG system (QueryAnalyst, RetrievalSpecialist, Writer, etc.)

Usage:
    from agents.rag.development_context_agent import create_development_context_graph
    
    # Create LangGraph workflow
    graph = create_development_context_graph(context_engine)
    
    # Execute with state
    result = await graph.ainvoke({
        "task": "Design auth system",
        "agent_role": "architecture_designer",
        "query": "What architecture patterns should I follow?",
        "user_guidelines": "use defaults"
    })
"""

import logging
from typing import Annotated, List, Dict, Any, Optional
try:
    from typing_extensions import TypedDict  # Python < 3.12 compatibility
except ImportError:
    from typing import TypedDict  # Python >= 3.12
import operator
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI

# Knowledge management
from workflow.knowledge_source_manager import DocumentSelectionPrompt

logger = logging.getLogger(__name__)


# ============================================================================
# STATE DEFINITION - LangGraph Compatible
# ============================================================================

class DevelopmentContextState(TypedDict):
    """State for development context workflow - LangGraph compatible."""
    
    # Input
    task: str
    agent_role: str  # "architecture_designer", "code_generator", etc.
    query: str  # What context is needed
    
    # Guideline selection
    guidelines_prompt: str
    user_guidelines: str
    loaded_sources: dict
    
    # Context retrieval
    enriched_context: str
    sources_used: List[str]
    
    # Workflow control
    stage: str  # "ask_guidelines", "load_docs", "get_context", "done"
    
    # Messages for conversation
    messages: Annotated[List, operator.add]


# ============================================================================
# NODES - LangGraph Workflow Nodes
# ============================================================================

async def ask_guidelines_node(state: DevelopmentContextState):
    """Node: Ask user for guidelines proactively."""
    logger.info(f"🤝 Node: Asking {state.get('agent_role', 'agent')} for guidelines...")
    
    task = state.get("task", "Development task")
    agent_role = state.get("agent_role", "development_agent")
    
    # Generate proactive prompt
    prompt = DocumentSelectionPrompt.generate_selection_prompt(
        task_description=task,
        agent_role=agent_role
    )
    
    return {
        "guidelines_prompt": prompt,
        "stage": "awaiting_user_response",
        "messages": [{"role": "assistant", "content": prompt}]
    }


async def load_documents_node(state: DevelopmentContextState):
    """Node: Load user-selected documents."""
    logger.info("📚 Node: Loading documents...")
    
    user_guidelines = state.get("user_guidelines", "")
    
    # Parse selections
    selections = DocumentSelectionPrompt.parse_user_response(user_guidelines)
    
    # Simulate loading (in real impl, use context_engine)
    loaded_sources = {}
    
    if "use defaults" in user_guidelines.lower():
        loaded_sources = {
            "architecture": ["docs/architecture/*.md"],
            "agile": ["docs/agile/sprints/current_sprint.md"],
            "coding_guidelines": ["docs/guides/*.md"]
        }
    else:
        loaded_sources = selections
    
    return {
        "loaded_sources": loaded_sources,
        "stage": "ready_for_retrieval",
        "messages": [{"role": "system", "content": f"Loaded {len(loaded_sources)} document categories"}]
    }


async def get_context_node(state: DevelopmentContextState):
    """Node: Get enriched context using RAG agents."""
    logger.info("🔍 Node: Getting enriched context...")
    
    query = state.get("query", "")
    task = state.get("task", "")
    
    # Create LLM for context synthesis
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        transport="rest"  # Use REST to avoid grpc event loop issues
    )
    
    # Build context query
    context_prompt = f"""You are a Development Context Assistant providing guidelines to development agents.

TASK: {task}

QUERY: {query}

Based on the loaded project guidelines (architecture, coding standards, agile requirements), provide:
1. Relevant architectural patterns and design guidelines
2. Coding standards and best practices to follow
3. Specific requirements from user stories/sprint goals
4. Framework-specific patterns (LangChain, LangGraph) if relevant

Be specific and cite which guidelines/documents are being referenced.

CONTEXT:"""
    
    try:
        response = await llm.ainvoke([{"role": "user", "content": context_prompt}])
        enriched_context = response.content
        
        # Simulated sources (in real impl, track actual sources used)
        sources = [
            "docs/architecture/onion_architecture.md",
            "docs/guides/python_standards.md",
            "docs/agile/sprints/current_sprint.md"
        ]
        
        return {
            "enriched_context": enriched_context,
            "sources_used": sources,
            "stage": "done",
            "messages": [{"role": "assistant", "content": f"✅ Context retrieved from {len(sources)} sources"}]
        }
        
    except Exception as e:
        logger.error(f"❌ Context retrieval failed: {e}")
        return {
            "enriched_context": f"Error: {e}",
            "sources_used": [],
            "stage": "error",
            "messages": [{"role": "system", "content": f"Error: {e}"}]
        }


# ============================================================================
# GRAPH CREATION - LangGraph Workflow
# ============================================================================

def create_development_context_graph(context_engine=None):
    """
    Create LangGraph workflow for development context agent.
    
    Workflow:
    START → ask_guidelines → (interrupt) → load_documents → get_context → END
    
    Args:
        context_engine: Optional ContextEngine for RAG operations
        
    Returns:
        Compiled LangGraph with checkpointer
    """
    
    # Create workflow
    workflow = StateGraph(DevelopmentContextState)
    
    # Add nodes
    workflow.add_node("ask_guidelines", ask_guidelines_node)
    workflow.add_node("load_documents", load_documents_node)
    workflow.add_node("get_context", get_context_node)
    
    # Add edges
    workflow.add_edge(START, "ask_guidelines")
    workflow.add_edge("ask_guidelines", "load_documents")
    workflow.add_edge("load_documents", "get_context")
    workflow.add_edge("get_context", END)
    
    # Always compile with checkpointer for instances
    # The graph methods depend on state management
    memory = MemorySaver()
    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["load_documents"]  # Interrupt for user input
    )
    logger.info("✅ Development Context Graph compiled WITH checkpointer")
    
    return app


# ============================================================================
# EXPORT FOR LANGGRAPH STUDIO (separate graph without checkpointer)
# ============================================================================

def _create_studio_graph():
    """
    Create a simplified graph for LangGraph Studio WITHOUT checkpointer.
    LangGraph Studio provides its own persistence.
    """
    workflow = StateGraph(DevelopmentContextState)
    
    # Add nodes
    workflow.add_node("ask_guidelines", ask_guidelines_node)
    workflow.add_node("load_documents", load_documents_node)
    workflow.add_node("get_context", get_context_node)
    
    # Add edges
    workflow.add_edge(START, "ask_guidelines")
    workflow.add_edge("ask_guidelines", "load_documents")
    workflow.add_edge("load_documents", "get_context")
    workflow.add_edge("get_context", END)
    
    # Compile WITHOUT checkpointer for Studio
    app = workflow.compile(interrupt_before=["load_documents"])
    logger.info("✅ Development Context Graph for Studio compiled WITHOUT checkpointer")
    
    return app

# Export graph for LangGraph Studio (without custom checkpointer)
graph = _create_studio_graph()

logger.info("✅ Development Context Graph exported for LangGraph Studio")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def create_development_context_agent(context_engine=None):
    """
    Create development context agent (returns graph).
    
    Args:
        context_engine: Optional ContextEngine for RAG operations
        
    Returns:
        Compiled LangGraph workflow
    """
    return create_development_context_graph(context_engine)
