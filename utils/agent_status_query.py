"""
Agent Status Query Utility for LangGraph Studio Graphs

This utility provides status querying capabilities for all Studio graphs.
Allows querying agent status, current state, and workflow progress.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def query_agent_status(
    graph: Any,
    thread_id: str,
    agent_name: str
) -> Dict[str, Any]:
    """
    Query the current status of an agent graph.
    
    Args:
        graph: LangGraph compiled graph instance
        thread_id: Thread ID for state lookup
        agent_name: Name of the agent (for reporting)
        
    Returns:
        Dict with status information including:
        - current_step: Current workflow step
        - state_summary: Summary of state fields
        - next_nodes: Next nodes to execute (if any)
        - is_complete: Whether workflow is complete
        - is_interrupted: Whether workflow is paused at HITL checkpoint
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get state snapshot
        state_snapshot = graph.get_state(config)
        
        if not state_snapshot:
            return {
                "agent": agent_name,
                "status": "not_started",
                "message": f"No state found for thread_id: {thread_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract state values
        state_values = state_snapshot.values if state_snapshot.values else {}
        
        # Determine status
        current_step = state_values.get("current_step", "unknown")
        next_nodes = state_snapshot.next if state_snapshot.next else []
        is_complete = len(next_nodes) == 0 and current_step in ["completed", "end"]
        is_interrupted = len(next_nodes) > 0
        
        # Build status summary
        status_summary = {
            "agent": agent_name,
            "status": "complete" if is_complete else ("interrupted" if is_interrupted else "in_progress"),
            "current_step": current_step,
            "next_nodes": next_nodes,
            "is_complete": is_complete,
            "is_interrupted": is_interrupted,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add agent-specific status fields
        if agent_name == "complexity_analyzer":
            status_summary.update({
                "context_detected": bool(state_values.get("project_domain")),
                "confidence": state_values.get("context_confidence", 0.0),
                "needs_more_info": state_values.get("needs_more_info", False),
                "iteration_count": state_values.get("iteration_count", 0)
            })
        elif agent_name == "agent_selector":
            status_summary.update({
                "agents_selected": len(state_values.get("selected_agents", [])),
                "selected_agents": state_values.get("selected_agents", []),
                "confidence": state_values.get("selection_confidence", 0.0),
                "iteration_count": state_values.get("iteration_count", 0)
            })
        elif agent_name == "requirements_analyst":
            status_summary.update({
                "requirements_analyzed": bool(state_values.get("requirements_analysis")),
                "functional_requirements_count": len(state_values.get("functional_requirements", [])),
                "confidence": state_values.get("analysis_confidence", 0.0),
                "iteration_count": state_values.get("iteration_count", 0)
            })
        elif agent_name == "architecture_designer":
            status_summary.update({
                "architecture_designed": bool(state_values.get("architecture_design")),
                "components_count": len(state_values.get("components", [])),
                "confidence": state_values.get("design_confidence", 0.0),
                "iteration_count": state_values.get("iteration_count", 0)
            })
        elif agent_name == "code_generator":
            status_summary.update({
                "code_generated": bool(state_values.get("code_files")),
                "files_count": len(state_values.get("code_files", {})),
                "confidence": state_values.get("generation_confidence", 0.0),
                "iteration_count": state_values.get("iteration_count", 0)
            })
        
        # Add human feedback status if present
        human_approval = state_values.get("human_approval", "")
        if human_approval:
            status_summary["human_approval"] = human_approval
            status_summary["human_feedback"] = state_values.get("human_feedback", "")
        
        # Add errors if any
        errors = state_values.get("errors", [])
        if errors:
            status_summary["errors"] = errors
        
        return status_summary
        
    except Exception as e:
        logger.error(f"Failed to query status for {agent_name}: {e}")
        return {
            "agent": agent_name,
            "status": "error",
            "message": f"Failed to query status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def query_all_agents_status(
    graphs: Dict[str, Any],
    thread_id: str
) -> Dict[str, Dict[str, Any]]:
    """
    Query status of all agents.
    
    Args:
        graphs: Dict mapping agent names to graph instances
        thread_id: Thread ID for state lookup
        
    Returns:
        Dict mapping agent names to their status
    """
    all_status = {}
    
    for agent_name, graph in graphs.items():
        try:
            status = query_agent_status(graph, thread_id, agent_name)
            all_status[agent_name] = status
        except Exception as e:
            logger.error(f"Failed to query status for {agent_name}: {e}")
            all_status[agent_name] = {
                "agent": agent_name,
                "status": "error",
                "message": str(e)
            }
    
    return all_status


def format_status_report(status: Dict[str, Any]) -> str:
    """
    Format status information as a human-readable report.
    
    Args:
        status: Status dict from query_agent_status
        
    Returns:
        Formatted status report string
    """
    lines = [
        f"# Agent Status Report: {status.get('agent', 'Unknown')}",
        f"",
        f"**Status**: {status.get('status', 'unknown').upper()}",
        f"**Current Step**: {status.get('current_step', 'unknown')}",
        f"**Timestamp**: {status.get('timestamp', 'unknown')}",
        f""
    ]
    
    # Add next nodes if interrupted
    if status.get('is_interrupted'):
        next_nodes = status.get('next_nodes', [])
        if next_nodes:
            lines.append(f"**Next Nodes**: {', '.join(next_nodes)}")
            lines.append("**Workflow**: ⏸️ Paused (HITL checkpoint)")
        lines.append("")
    
    # Add agent-specific fields
    if 'confidence' in status:
        lines.append(f"**Confidence**: {status['confidence']:.0%}")
    
    if 'iteration_count' in status:
        lines.append(f"**Iterations**: {status['iteration_count']}/3")
    
    # Add progress indicators
    if status.get('agent') == 'complexity_analyzer':
        if status.get('context_detected'):
            lines.append("**Context**: ✅ Detected")
        if status.get('needs_more_info'):
            lines.append("**Info Needed**: ⚠️ Yes")
    
    elif status.get('agent') == 'agent_selector':
        agents_selected = status.get('selected_agents', [])
        if agents_selected:
            lines.append(f"**Selected Agents**: {', '.join(agents_selected)}")
    
    elif status.get('agent') == 'requirements_analyst':
        req_count = status.get('functional_requirements_count', 0)
        if req_count > 0:
            lines.append(f"**Functional Requirements**: {req_count}")
    
    elif status.get('agent') == 'architecture_designer':
        comp_count = status.get('components_count', 0)
        if comp_count > 0:
            lines.append(f"**Components**: {comp_count}")
    
    elif status.get('agent') == 'code_generator':
        files_count = status.get('files_count', 0)
        if files_count > 0:
            lines.append(f"**Files Generated**: {files_count}")
    
    # Add human feedback if present
    if 'human_approval' in status:
        lines.append("")
        lines.append(f"**Human Approval**: {status['human_approval']}")
        if status.get('human_feedback'):
            lines.append(f"**Feedback**: {status['human_feedback'][:100]}...")
    
    # Add errors if any
    if 'errors' in status and status['errors']:
        lines.append("")
        lines.append("**Errors**:")
        for error in status['errors']:
            lines.append(f"- {error}")
    
    # Add completion status
    lines.append("")
    if status.get('is_complete'):
        lines.append("✅ **Workflow Complete**")
    elif status.get('is_interrupted'):
        lines.append("⏸️ **Workflow Paused** (awaiting human input)")
    else:
        lines.append("🔄 **Workflow In Progress**")
    
    return "\n".join(lines)

