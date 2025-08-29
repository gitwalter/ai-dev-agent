#!/usr/bin/env python3
"""
Mock LangGraph Workflow - for compatibility with outdated tests.
"""

from typing import Dict, Any, List, Optional, TypedDict
from unittest.mock import MagicMock
from pydantic import BaseModel


class WorkflowState(TypedDict):
    """Mock workflow state."""
    current_step: str
    agents: List[str]
    results: Dict[str, Any]
    status: str


class LangGraphWorkflowManager:
    """Mock LangGraph Workflow Manager for backwards compatibility."""

    def __init__(self, llm_config=None):
        self.llm_config = llm_config
        self.workflow = MagicMock()
        self.agents = []

    def add_agent(self, agent: Any) -> None:
        """Add an agent to the workflow."""
        self.agents.append(agent)

    def create_workflow(self, config: Dict[str, Any]) -> MagicMock:
        """Create a workflow with given config."""
        return self.workflow

    async def execute_workflow(self, state: WorkflowState) -> WorkflowState:
        """Execute the workflow with given state."""
        # Mock successful execution with all expected fields
        state["current_step"] = "completed"
        state["status"] = "completed"
        state["results"] = {"success": True}
        
        # Mock agent outputs
        state["requirements"] = [
            {"id": "REQ-001", "title": "User Authentication", "description": "System must support login"}
        ]
        state["architecture"] = {
            "pattern": "microservices",
            "components": ["auth_service", "user_service"]
        }
        state["code_files"] = {
            "main.py": {"content": "# Mock main file", "language": "python"}
        }
        state["tests"] = {
            "test_main.py": {"content": "# Mock test file", "test_type": "unit"}
        }
        state["agent_outputs"] = {
            "requirements_analyst": {"status": "completed"},
            "architecture_designer": {"status": "completed"},
            "code_generator": {"status": "completed"},
            "test_generator": {"status": "completed"}
        }
        state["execution_history"] = [
            {"step": "requirements_analysis", "status": "completed"},
            {"step": "architecture_design", "status": "completed"},
            {"step": "code_generation", "status": "completed"},
            {"step": "test_generation", "status": "completed"}
        ]
        
        return state

    def get_workflow_status(self) -> str:
        """Get current workflow status."""
        return "completed"


# Create global instance for compatibility
workflow_manager = LangGraphWorkflowManager()
