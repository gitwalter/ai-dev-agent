"""
RAG-Enhanced Architecture Workflow for LangGraph Studio
========================================================

LangGraph-compatible workflow for testing RAG-enhanced architecture design
in LangGraph Studio.

Workflow:
1. ask_guidelines: Agent asks user for guidelines proactively
2. load_documents: Load selected documents into RAG
3. design_architecture: Generate architecture using RAG
4. human_review: Human reviews and approves/refines
"""

import logging
from typing import TypedDict, Annotated, List
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from workflow.knowledge_source_manager import (
    create_knowledge_source_manager,
    DocumentSelectionPrompt
)

logger = logging.getLogger(__name__)


# State definition
class ArchitectureWorkflowState(TypedDict):
    """State for RAG-enhanced architecture workflow."""
    task_description: str
    user_story_id: str
    
    # Guideline selection
    guidelines_prompt: str
    user_guidelines: str
    loaded_sources: dict
    
    # Architecture design
    architecture_proposal: str
    sources_used: List[str]
    guidelines_context: str
    
    # Human review
    human_decision: str  # "approve", "refine", "consult_more"
    human_feedback: str
    
    # Iteration
    iteration_count: int
    
    # Messages for conversation
    messages: Annotated[List, operator.add]


async def ask_guidelines_node(state: ArchitectureWorkflowState):
    """Node 1: Agent asks user for guidelines proactively."""
    logger.info("🤝 Node: Asking user for guidelines...")
    
    task = state.get("task_description", "Design system architecture")
    
    # Generate proactive guideline request
    prompt = DocumentSelectionPrompt.generate_selection_prompt(
        task_description=task,
        agent_role="architecture_designer"
    )
    
    return {
        "guidelines_prompt": prompt,
        "messages": [{"role": "assistant", "content": prompt}]
    }


async def load_documents_node(state: ArchitectureWorkflowState):
    """Node 2: Load documents based on user's response."""
    logger.info("📚 Node: Loading documents...")
    
    user_guidelines = state.get("user_guidelines", "")
    
    # Parse user response
    selections = DocumentSelectionPrompt.parse_user_response(user_guidelines)
    
    # Simulate loading (in real impl, use KnowledgeSourceManager)
    loaded_sources = {}
    
    if "use defaults" in user_guidelines.lower():
        loaded_sources = {
            "architecture": ["docs/architecture/*.md"],
            "agile": ["docs/agile/sprints/current_sprint.md"],
            "coding_guidelines": ["docs/guides/*.md"]
        }
    else:
        # Use parsed selections
        for category, sources in selections.items():
            loaded_sources[category] = sources
    
    return {
        "loaded_sources": loaded_sources,
        "messages": [{"role": "system", "content": f"Loaded {len(loaded_sources)} document categories"}]
    }


async def design_architecture_node(state: ArchitectureWorkflowState):
    """Node 3: Design architecture using RAG."""
    logger.info("🏗️ Node: Designing architecture with RAG...")
    
    task = state.get("task_description", "")
    loaded_sources = state.get("loaded_sources", {})
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    
    # Simulate RAG retrieval context
    guidelines_context = f"""
Retrieved from project documents:

Architecture Guidelines (docs/architecture/):
- Follow Onion Architecture pattern
- Separate concerns: Domain → Application → Infrastructure
- Domain entities at core, infrastructure at edges

Coding Standards (docs/guides/):
- Use type hints for all functions
- Follow PEP 8 style guide
- Comprehensive docstrings required

Security Guidelines (docs/guides/security_guidelines.md):
- Use stateless authentication (JWT)
- Implement RBAC for access control
- Audit all security events
"""
    
    # Generate architecture with context
    prompt = f"""You are an expert Architecture Designer.

TASK: Design architecture for: {task}

PROJECT GUIDELINES (from RAG retrieval):
{guidelines_context}

LOADED SOURCES:
{', '.join([f"{cat}: {len(srcs)} docs" for cat, srcs in loaded_sources.items()])}

Based on the guidelines above, design a comprehensive architecture that:
1. Follows the project's patterns (Onion Architecture)
2. Satisfies the requirements
3. Includes clear component breakdown
4. Cites specific guidelines used

Provide a detailed architecture proposal with rationale.
"""
    
    try:
        response = await llm.ainvoke([{"role": "user", "content": prompt}])
        architecture_proposal = response.content
        
        sources_used = [
            "docs/architecture/onion_architecture.md",
            "docs/guides/python_standards.md",
            "docs/guides/security_guidelines.md"
        ]
        
        return {
            "architecture_proposal": architecture_proposal,
            "sources_used": sources_used,
            "guidelines_context": guidelines_context,
            "messages": [{"role": "assistant", "content": f"Architecture Proposal:\n\n{architecture_proposal}"}]
        }
    except Exception as e:
        logger.error(f"❌ Architecture generation failed: {e}")
        return {
            "architecture_proposal": f"Error: {e}",
            "messages": [{"role": "assistant", "content": f"Error generating architecture: {e}"}]
        }


async def human_review_node(state: ArchitectureWorkflowState):
    """Node 4: Human reviews architecture (interrupt point)."""
    logger.info("👤 Node: Human review (interrupt point)")
    
    # This node just passes through - the interrupt happens at graph level
    return {
        "messages": [{"role": "system", "content": "Awaiting human review..."}]
    }


async def refine_architecture_node(state: ArchitectureWorkflowState):
    """Node 5: Refine architecture based on human feedback."""
    logger.info("🔄 Node: Refining architecture...")
    
    current_architecture = state.get("architecture_proposal", "")
    human_feedback = state.get("human_feedback", "")
    iteration = state.get("iteration_count", 0)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    
    prompt = f"""You are an expert Architecture Designer.

CURRENT ARCHITECTURE:
{current_architecture}

HUMAN FEEDBACK:
{human_feedback}

Please refine the architecture based on the feedback above. Address the concerns while maintaining good design.

REFINED ARCHITECTURE:
"""
    
    try:
        response = await llm.ainvoke([{"role": "user", "content": prompt}])
        refined_proposal = response.content
        
        return {
            "architecture_proposal": refined_proposal,
            "iteration_count": iteration + 1,
            "messages": [{"role": "assistant", "content": f"Refined Architecture:\n\n{refined_proposal}"}]
        }
    except Exception as e:
        logger.error(f"❌ Refinement failed: {e}")
        return {
            "messages": [{"role": "assistant", "content": f"Error refining: {e}"}]
        }


def route_after_review(state: ArchitectureWorkflowState) -> str:
    """Route based on human decision."""
    decision = state.get("human_decision", "approve")
    
    if decision == "approve":
        return "end"
    elif decision == "refine":
        return "refine"
    elif decision == "consult_more":
        return "ask_guidelines"
    else:
        return "end"


def create_rag_architecture_workflow():
    """Create LangGraph workflow for RAG-enhanced architecture design."""
    
    # Create graph
    workflow = StateGraph(ArchitectureWorkflowState)
    
    # Add nodes
    workflow.add_node("ask_guidelines", ask_guidelines_node)
    workflow.add_node("load_documents", load_documents_node)
    workflow.add_node("design_architecture", design_architecture_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("refine_architecture", refine_architecture_node)
    
    # Add edges
    workflow.add_edge(START, "ask_guidelines")
    workflow.add_edge("ask_guidelines", "load_documents")
    workflow.add_edge("load_documents", "design_architecture")
    workflow.add_edge("design_architecture", "human_review")
    
    # Conditional routing after human review
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "end": END,
            "refine": "refine_architecture",
            "ask_guidelines": "ask_guidelines"
        }
    )
    
    # After refinement, go back to review
    workflow.add_edge("refine_architecture", "human_review")
    
    # Compile with memory for interrupts
    memory = MemorySaver()
    app = workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]  # Interrupt for human input
    )
    
    logger.info("✅ RAG Architecture Workflow compiled")
    return app


# Export for LangGraph Studio
graph = create_rag_architecture_workflow()

logger.info("✅ RAG Architecture Workflow graph exported for LangGraph Studio")

