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

    def __init__(self):
        self.workflow = MagicMock()
        self.agents = []

    def add_agent(self, agent: Any) -> None:
        """Add an agent to the workflow."""
        self.agents.append(agent)

    def create_workflow(self, config: Dict[str, Any]) -> MagicMock:
        """Create a workflow with given config."""
        return self.workflow

    def execute_workflow(self, state: WorkflowState) -> WorkflowState:
        """Execute the workflow with given state."""
        # Mock successful execution
        state["status"] = "completed"
        state["results"] = {"success": True}
        return state

    def get_workflow_status(self) -> str:
        """Get current workflow status."""
        return "completed"


# Create global instance for compatibility
workflow_manager = LangGraphWorkflowManager()
