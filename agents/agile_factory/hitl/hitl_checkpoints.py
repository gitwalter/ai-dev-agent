"""
Human-in-the-loop checkpoint implementations.

Provides structured HITL checkpoints between workflow stages.
"""

import logging
from typing import Dict, Any
from agents.agile_factory.state.agile_state import AgileFactoryState

logger = logging.getLogger(__name__)


def create_checkpoint_summary(state: AgileFactoryState, checkpoint_name: str) -> Dict[str, Any]:
    """
    Create structured summary for human review at checkpoint.
    
    Args:
        state: Current workflow state
        checkpoint_name: Name of checkpoint
        
    Returns:
        Structured summary dictionary
    """
    summary = {
        "checkpoint": checkpoint_name,
        "timestamp": None,  # Will be set by caller if needed
        "status": state.get("status", "processing")
    }
    
    if checkpoint_name == "story_review":
        summary.update({
            "what": "User Story Input",
            "content": state.get("user_story", ""),
            "project_type": state.get("project_type", "website")
        })
    
    elif checkpoint_name == "requirements_review":
        requirements = state.get("requirements", {})
        summary.update({
            "what": "Requirements Analysis",
            "summary": requirements.get("summary", ""),
            "functional_count": len(requirements.get("functional_requirements", [])),
            "non_functional_count": len(requirements.get("non_functional_requirements", []))
        })
    
    elif checkpoint_name == "architecture_review":
        architecture = state.get("architecture", {})
        summary.update({
            "what": "Architecture Design",
            "system_overview": architecture.get("system_overview", "")[:500],
            "architecture_pattern": architecture.get("architecture_pattern", ""),
            "components_count": len(architecture.get("components", [])),
            "tech_stack": architecture.get("technology_stack", {})
        })
    
    elif checkpoint_name == "code_generation_review":
        code_files = state.get("code_files", {})
        summary.update({
            "what": "Code Generation",
            "files_generated": len(code_files),
            "file_list": list(code_files.keys())[:10],  # First 10 files
            "total_size": sum(len(content) for content in code_files.values())
        })
    
    elif checkpoint_name == "final_review":
        summary.update({
            "what": "Final Project Review",
            "requirements_complete": bool(state.get("requirements")),
            "architecture_complete": bool(state.get("architecture")),
            "code_complete": bool(state.get("code_files")),
            "tests_complete": bool(state.get("test_results")),
            "docs_complete": bool(state.get("documentation_files"))
        })
    
    return summary


def print_summary(summary: Dict[str, Any]) -> None:
    """
    Print checkpoint summary to console.
    
    Args:
        summary: Summary dictionary
    """
    print(f"\n{summary.get('what', 'Checkpoint')}:")
    print("-" * 60)
    
    for key, value in summary.items():
        if key not in ["checkpoint", "what", "timestamp"]:
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            elif isinstance(value, list):
                print(f"{key}: {len(value)} items")
                if value and len(value) <= 5:
                    for item in value:
                        print(f"  - {item}")
            else:
                print(f"{key}: {value}")


def hitl_checkpoint_node(state: AgileFactoryState, checkpoint_name: str) -> dict:
    """
    Generic HITL checkpoint node.
    
    This node presents a checkpoint summary to the human reviewer and
    collects their decision (approve/reject/edit).
    
    Args:
        state: Current workflow state
        checkpoint_name: Name of checkpoint
        
    Returns:
        Updates dict with HITL feedback (LangGraph will merge with state)
    """
    # Create structured summary
    summary = create_checkpoint_summary(state, checkpoint_name)
    
    # Present to human (console for MVP, Streamlit UI later)
    print("\n" + "="*60)
    print(f"HITL CHECKPOINT: {checkpoint_name.upper().replace('_', ' ')}")
    print("="*60)
    print_summary(summary)
    print("\nOptions:")
    print("  [a]pprove - Continue to next step")
    print("  [r]eject - Restart from beginning")
    print("  [e]dit - Provide feedback for revision")
    print("  [s]kip - Skip this checkpoint (not recommended)")
    
    # Get human input
    # For LangGraph Studio, this will be handled via interrupt
    # For now, we'll set a default and let Studio handle the interrupt
    feedback = "approve"  # Default for automated testing
    
    # In LangGraph Studio, this will be an interrupt point
    # The human will provide feedback through Studio UI
    
    # Build updates dict (correct LangGraph pattern - return only updates)
    # Merge with existing hitl_approvals and hitl_feedback from state
    existing_approvals = state.get("hitl_approvals", {}).copy()
    existing_feedback = state.get("hitl_feedback", {}).copy()
    
    existing_approvals[checkpoint_name] = feedback == "approve"
    existing_feedback[checkpoint_name] = feedback
    
    updates = {
        "current_checkpoint": checkpoint_name,
        "hitl_approvals": existing_approvals,
        "hitl_feedback": existing_feedback
    }
    
    if feedback == "approve":
        updates["status"] = "approved"
    elif feedback == "reject":
        updates["status"] = "rejected"
    elif feedback == "edit":
        updates["status"] = "needs_revision"
    
    logger.info("HITL checkpoint %s: %s", checkpoint_name, feedback)
    
    return updates

