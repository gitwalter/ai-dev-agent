#!/usr/bin/env python3
"""
Workflow Graph Module for AI Development Agent.
Provides workflow orchestration and state management.
"""

import logging
from typing import Dict, Any, List
from models.config import AgentConfig

logger = logging.getLogger("workflow.graph")

def create_workflow_graph(config: AgentConfig, agents: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a workflow graph for the AI Development Agent system.
    
    Args:
        config: Agent configuration
        agents: Dictionary of available agents
        
    Returns:
        Workflow graph configuration
    """
    logger.info("Creating workflow graph")
    
    # Define the workflow steps
    workflow_steps = [
        {
            "name": "requirements_analysis",
            "agent": "requirements_analyst",
            "description": "Analyze project requirements",
            "dependencies": []
        },
        {
            "name": "architecture_design",
            "agent": "architecture_designer", 
            "description": "Design system architecture",
            "dependencies": ["requirements_analysis"]
        },
        {
            "name": "code_generation",
            "agent": "code_generator",
            "description": "Generate application code",
            "dependencies": ["architecture_design"]
        },
        {
            "name": "test_generation",
            "agent": "test_generator",
            "description": "Generate test suites",
            "dependencies": ["code_generation"]
        },
        {
            "name": "code_review",
            "agent": "code_reviewer",
            "description": "Review code quality",
            "dependencies": ["code_generation"]
        },
        {
            "name": "security_analysis",
            "agent": "security_analyst",
            "description": "Analyze security vulnerabilities",
            "dependencies": ["code_generation"]
        },
        {
            "name": "documentation_generation",
            "agent": "documentation_generator",
            "description": "Generate project documentation",
            "dependencies": ["code_generation", "test_generation"]
        }
    ]
    
    # Create workflow graph
    workflow_graph = {
        "steps": workflow_steps,
        "agents": agents,
        "config": config,
        "state": {}
    }
    
    logger.info(f"Created workflow graph with {len(workflow_steps)} steps")
    return workflow_graph

def execute_workflow_step(workflow_graph: Dict[str, Any], step_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single workflow step.
    
    Args:
        workflow_graph: The workflow graph configuration
        step_name: Name of the step to execute
        state: Current workflow state
        
    Returns:
        Updated state
    """
    logger.info(f"Executing workflow step: {step_name}")
    
    # Find the step configuration
    step_config = None
    for step in workflow_graph["steps"]:
        if step["name"] == step_name:
            step_config = step
            break
    
    if not step_config:
        raise ValueError(f"Step '{step_name}' not found in workflow")
    
    # Get the agent for this step
    agent_name = step_config["agent"]
    agent = workflow_graph["agents"].get(agent_name)
    
    if not agent:
        raise ValueError(f"Agent '{agent_name}' not found")
    
    # Execute the agent
    try:
        # This would normally call the agent's execute method
        # For now, we'll just log the execution
        logger.info(f"Executing {agent_name} for step {step_name}")
        
        # Update state with step completion
        state["completed_steps"] = state.get("completed_steps", [])
        state["completed_steps"].append(step_name)
        state["current_step"] = step_name
        state["step_results"] = state.get("step_results", {})
        state["step_results"][step_name] = {
            "status": "completed",
            "agent": agent_name,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        logger.info(f"Step {step_name} completed successfully")
        
    except Exception as e:
        logger.error(f"Step {step_name} failed: {e}")
        state["step_results"] = state.get("step_results", {})
        state["step_results"][step_name] = {
            "status": "failed",
            "agent": agent_name,
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        raise
    
    return state

def get_next_steps(workflow_graph: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    """
    Get the next steps that can be executed based on current state.
    
    Args:
        workflow_graph: The workflow graph configuration
        state: Current workflow state
        
    Returns:
        List of step names that can be executed next
    """
    completed_steps = set(state.get("completed_steps", []))
    available_steps = []
    
    for step in workflow_graph["steps"]:
        step_name = step["name"]
        dependencies = set(step["dependencies"])
        
        # Check if all dependencies are completed
        if dependencies.issubset(completed_steps) and step_name not in completed_steps:
            available_steps.append(step_name)
    
    return available_steps

def is_workflow_complete(workflow_graph: Dict[str, Any], state: Dict[str, Any]) -> bool:
    """
    Check if the workflow is complete.
    
    Args:
        workflow_graph: The workflow graph configuration
        state: Current workflow state
        
    Returns:
        True if workflow is complete, False otherwise
    """
    completed_steps = set(state.get("completed_steps", []))
    total_steps = {step["name"] for step in workflow_graph["steps"]}
    
    return completed_steps == total_steps
