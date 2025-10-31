"""
Status Query Node for Studio Graphs

Adds a status query node that can be called to get current agent status.
This node can be added to any Studio graph for status querying.
"""

from typing import Dict, Any
from datetime import datetime
from utils.agent_status_query import format_status_report


def publish_status_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Status publish node that generates and returns formatted status information.
    
    This node can be called from Studio to get agent status.
    It reads the current state and returns a formatted status report.
    
    Usage in Studio:
        1. Add this node to your graph: workflow.add_node("publish_status", publish_status_node)
        2. Add a conditional edge that routes to this node when state includes "action": "publish_status"
        3. Or call directly: Update state with {"action": "publish_status"} and route to this node
    
    Args:
        state: Current graph state
        
    Returns:
        Dict with status information including formatted report in status_summary field
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Detect agent name from state fields or use default
    agent_name = "unknown"
    
    # Detect agent by checking state fields
    if "project_complexity" in state or "context_confidence" in state:
        agent_name = "complexity_analyzer"
    elif "selected_agents" in state or "selection_confidence" in state:
        agent_name = "agent_selector"
    elif "requirements_analysis" in state or "analysis_confidence" in state:
        agent_name = "requirements_analyst"
    elif "architecture_design" in state or "design_confidence" in state:
        agent_name = "architecture_designer"
    elif "code_files" in state or "generation_confidence" in state:
        agent_name = "code_generator"
    
    logger.info(f"📊 Publishing status for agent: {agent_name}")
    
    # Build status from current state
    status = {
        "agent": agent_name,
        "current_step": state.get("current_step", "unknown"),
        "is_complete": state.get("current_step") == "completed",
        "is_interrupted": state.get("current_step") in ["context_review", "selection_review", 
                                                         "requirements_review", "architecture_review", 
                                                         "code_review"],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add agent-specific fields
    if agent_name == "complexity_analyzer":
        status.update({
            "context_detected": bool(state.get("project_domain")),
            "confidence": state.get("context_confidence", 0.0),
            "needs_more_info": state.get("needs_more_info", False),
            "iteration_count": state.get("iteration_count", 0),
            "project_domain": state.get("project_domain", ""),
            "project_intent": state.get("project_intent", ""),
            "project_complexity": state.get("project_complexity", ""),
            "detected_entities": state.get("detected_entities", [])
        })
    elif agent_name == "agent_selector":
        status.update({
            "agents_selected": len(state.get("selected_agents", [])),
            "selected_agents": state.get("selected_agents", []),
            "confidence": state.get("selection_confidence", 0.0),
            "iteration_count": state.get("iteration_count", 0)
        })
    elif agent_name == "requirements_analyst":
        status.update({
            "requirements_analyzed": bool(state.get("requirements_analysis")),
            "functional_requirements_count": len(state.get("functional_requirements", [])),
            "non_functional_requirements_count": len(state.get("non_functional_requirements", [])),
            "confidence": state.get("analysis_confidence", 0.0),
            "iteration_count": state.get("iteration_count", 0)
        })
    elif agent_name == "architecture_designer":
        status.update({
            "architecture_designed": bool(state.get("architecture_design")),
            "components_count": len(state.get("components", [])),
            "architecture_pattern": state.get("architecture_pattern", ""),
            "confidence": state.get("design_confidence", 0.0),
            "iteration_count": state.get("iteration_count", 0)
        })
    elif agent_name == "code_generator":
        status.update({
            "code_generated": bool(state.get("code_files")),
            "files_count": len(state.get("code_files", {})),
            "files_list": list(state.get("code_files", {}).keys())[:10],  # First 10 files
            "confidence": state.get("generation_confidence", 0.0),
            "iteration_count": state.get("iteration_count", 0)
        })
    
    # Add human feedback if present
    if state.get("human_approval"):
        status["human_approval"] = state.get("human_approval")
        status["human_feedback"] = state.get("human_feedback", "")
    
    # Add errors if any
    errors = state.get("errors", [])
    if errors:
        status["errors"] = errors
    
    # Generate formatted report
    formatted_report = format_status_report(status)
    
    logger.info(f"✅ Status published for {agent_name}: {status.get('current_step')}")
    
    # Return status update - store in status_summary field for visibility in Studio
    return {
        "status_summary": formatted_report,  # Human-readable report
        "status_data": status,  # Machine-readable data
        "current_step": state.get("current_step", "unknown")
    }

