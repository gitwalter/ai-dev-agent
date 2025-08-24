"""
LangGraph workflow graph for the AI Development Agent system.
Defines the workflow structure and agent interactions.
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.state import AgentState
from models.config import SystemConfig
from agents import (
    RequirementsAnalyst,
    ArchitectureDesigner,
    CodeGenerator,
    TestGenerator,
    CodeReviewer,
    SecurityAnalyst,
    DocumentationGenerator
)


def create_workflow_graph(config: SystemConfig, agents: Dict[str, Any]) -> StateGraph:
    """
    Create the LangGraph workflow for the development agent system.
    
    Args:
        config: System configuration
        agents: Dictionary of initialized agents
        
    Returns:
        Compiled LangGraph workflow
    """
    
    logger = logging.getLogger("workflow.graph")
    logger.info("Creating workflow graph...")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("requirements_analysis", agents["requirements_analyst"].execute_with_retry)
    workflow.add_node("architecture_design", agents["architecture_designer"].execute_with_retry)
    workflow.add_node("code_generation", agents["code_generator"].execute_with_retry)
    workflow.add_node("test_generation", agents["test_generator"].execute_with_retry)
    workflow.add_node("code_review", agents["code_reviewer"].execute_with_retry)
    workflow.add_node("security_analysis", agents["security_analyst"].execute_with_retry)
    workflow.add_node("documentation_generation", agents["documentation_generator"].execute_with_retry)
    
    # Add conditional nodes for human approval
    if config.workflow.enable_human_approval:
        workflow.add_node("check_approval_needed", check_approval_needed)
        workflow.add_node("wait_for_approval", wait_for_human_approval)
        workflow.add_node("handle_approval_response", handle_approval_response)
    
    # Add error handling nodes
    workflow.add_node("handle_error", handle_workflow_error)
    workflow.add_node("retry_task", retry_failed_task)
    
    # Define the main workflow edges
    if config.workflow.enable_human_approval:
        # Add conditional edges for human approval
        # After requirements analysis (no approval needed)
        workflow.add_edge("requirements_analysis", "architecture_design")
        
        # After architecture design
        workflow.add_conditional_edges(
            "architecture_design",
            check_approval_needed,
            {
                "approval_needed": "wait_for_approval",
                "no_approval_needed": "code_generation"
            }
        )
        
        # After code generation (no approval needed)
        workflow.add_edge("code_generation", "test_generation")
        
        # After test generation (no approval needed)
        workflow.add_edge("test_generation", "code_review")
        
        # After code review (no approval needed)
        workflow.add_edge("code_review", "security_analysis")
        
        # After security analysis
        workflow.add_conditional_edges(
            "security_analysis",
            check_approval_needed,
            {
                "approval_needed": "wait_for_approval",
                "no_approval_needed": "documentation_generation"
            }
        )
        
        # Handle approval responses
        workflow.add_conditional_edges(
            "wait_for_approval",
            handle_approval_response,
            {
                "approved": "code_generation",  # Continue to next step after approval
                "rejected": "handle_error",
                "modified": "retry_task"
            }
        )
    else:
        # Linear flow without human approval
        logger.info("Adding linear workflow edges...")
        workflow.add_edge("requirements_analysis", "architecture_design")
        workflow.add_edge("architecture_design", "code_generation")
        workflow.add_edge("code_generation", "test_generation")
        workflow.add_edge("test_generation", "code_review")
        workflow.add_edge("code_review", "security_analysis")
        workflow.add_edge("security_analysis", "documentation_generation")
        logger.info("Linear workflow edges added successfully")
    
    # Final edge to end
    workflow.add_edge("documentation_generation", END)
    
    # Add retry logic
    workflow.add_edge("retry_task", "requirements_analysis")
    workflow.add_edge("handle_error", END)
    
    # Set the entry point
    workflow.set_entry_point("requirements_analysis")
    
    # Compile the workflow with memory saver for checkpointing
    memory = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=memory)
    
    logger.info("Workflow graph created successfully")
    logger.info(f"Workflow nodes: {list(workflow.nodes.keys())}")
    logger.info(f"Workflow edges: {list(workflow.edges)}")
    
    return compiled_workflow


def check_approval_needed(state: AgentState) -> str:
    """
    Check if human approval is needed for the current task.
    
    Args:
        state: Current workflow state
        
    Returns:
        "approval_needed" or "no_approval_needed"
    """
    current_task = state.get("current_task", "")
    approval_required_tasks = [
        "architecture_design",
        "security_analysis",
        "deployment"
    ]
    
    if current_task in approval_required_tasks:
        return "approval_needed"
    else:
        return "no_approval_needed"


def wait_for_human_approval(state: AgentState) -> AgentState:
    """
    Wait for human approval of the current task.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    # In a real implementation, this would:
    # 1. Send notification to human
    # 2. Wait for response
    # 3. Update state with approval decision
    
    # For now, we'll simulate approval
    from models.state import add_approval_request
    
    state = add_approval_request(
        state=state,
        task_name=state.get("current_task", ""),
        agent_name=state.get("current_agent", ""),
        description=f"Please review the {state.get('current_task', '')} results",
        data_to_review=state.get("agent_outputs", {}),
        options=["approve", "reject", "modify"]
    )
    
    return state


def handle_approval_response(state: AgentState) -> str:
    """
    Handle the human approval response.
    
    Args:
        state: Current workflow state
        
    Returns:
        "approved", "rejected", or "modified"
    """
    # In a real implementation, this would check the actual approval response
    # For now, we'll simulate approval
    return "approved"


def check_for_errors(state: AgentState) -> str:
    """
    Check if there are any errors in the current state.
    
    Args:
        state: Current workflow state
        
    Returns:
        "error" or "success"
    """
    errors = state.get("errors", [])
    if errors:
        return "error"
    else:
        return "success"


def handle_workflow_error(state: AgentState) -> AgentState:
    """
    Handle workflow errors.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    logger = logging.getLogger("workflow.error_handler")
    
    errors = state.get("errors", [])
    if errors:
        latest_error = errors[-1]
        logger.error(f"Workflow error: {latest_error.get('error_message', 'Unknown error')}")
        
        # Add error handling logic here
        # For example, send notifications, log to external systems, etc.
        
        # Update state to indicate workflow failure
        state["current_task"] = "error_handling"
        
    return state


def retry_failed_task(state: AgentState) -> AgentState:
    """
    Retry a failed task.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    logger = logging.getLogger("workflow.retry")
    
    # Reset error state
    state["errors"] = []
    state["retry_count"] = state.get("retry_count", 0) + 1
    
    logger.info(f"Retrying task. Attempt {state['retry_count']}")
    
    return state


def create_parallel_workflow_graph(config: SystemConfig, agents: Dict[str, Any]) -> StateGraph:
    """
    Create a parallel workflow graph for concurrent agent execution.
    
    Args:
        config: System configuration
        agents: Dictionary of initialized agents
        
    Returns:
        Compiled LangGraph workflow with parallel execution
    """
    
    logger = logging.getLogger("workflow.parallel_graph")
    logger.info("Creating parallel workflow graph...")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("requirements_analysis", agents["requirements_analyst"].execute_with_retry)
    workflow.add_node("architecture_design", agents["architecture_designer"].execute_with_retry)
    workflow.add_node("code_generation", agents["code_generator"].execute_with_retry)
    workflow.add_node("test_generation", agents["test_generator"].execute_with_retry)
    workflow.add_node("code_review", agents["code_reviewer"].execute_with_retry)
    workflow.add_node("security_analysis", agents["security_analyst"].execute_with_retry)
    workflow.add_node("documentation_generation", agents["documentation_generator"].execute_with_retry)
    
    # Add parallel execution nodes
    workflow.add_node("parallel_code_generation", parallel_code_generation)
    workflow.add_node("parallel_test_generation", parallel_test_generation)
    workflow.add_node("parallel_review", parallel_review)
    
    # Define parallel workflow edges
    workflow.add_edge("requirements_analysis", "architecture_design")
    workflow.add_edge("architecture_design", "parallel_code_generation")
    
    # Parallel code generation and test generation
    workflow.add_edge("parallel_code_generation", "parallel_test_generation")
    workflow.add_edge("parallel_test_generation", "parallel_review")
    workflow.add_edge("parallel_review", "security_analysis")
    workflow.add_edge("security_analysis", "documentation_generation")
    workflow.add_edge("documentation_generation", END)
    
    # Set the entry point
    workflow.set_entry_point("requirements_analysis")
    
    # Compile the workflow
    memory = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=memory)
    
    logger.info("Parallel workflow graph created successfully")
    return compiled_workflow


def parallel_code_generation(state: AgentState) -> AgentState:
    """
    Execute code generation in parallel with other tasks.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    # This would implement parallel execution logic
    # For now, just return the state
    return state


def parallel_test_generation(state: AgentState) -> AgentState:
    """
    Execute test generation in parallel with other tasks.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    # This would implement parallel execution logic
    # For now, just return the state
    return state


def parallel_review(state: AgentState) -> AgentState:
    """
    Execute code review in parallel with other tasks.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    # This would implement parallel execution logic
    # For now, just return the state
    return state
