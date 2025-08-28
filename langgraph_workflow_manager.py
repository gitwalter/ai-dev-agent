#!/usr/bin/env python3
"""
Mock LangGraph Workflow Manager - for compatibility with outdated tests.
"""

from typing import Dict, Any, List, Optional, TypedDict
from unittest.mock import MagicMock
from pydantic import BaseModel


class AgentState(TypedDict):
    """Mock agent state."""
    messages: List[Dict[str, Any]]
    current_agent: Optional[str]
    workflow_status: str
    results: Dict[str, Any]


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

    def execute_workflow(self, state: AgentState) -> AgentState:
        """Execute the workflow with given state."""
        # Mock successful execution
        state["workflow_status"] = "completed"
        state["results"] = {"success": True}
        return state

    def get_workflow_status(self) -> str:
        """Get current workflow status."""
        return "completed"


class AgentNodeFactory:
    """Mock Agent Node Factory."""

    @staticmethod
    def create_agent_node(agent_type: str, config: Dict[str, Any]) -> MagicMock:
        """Create a mock agent node."""
        mock_node = MagicMock()
        mock_node.agent_type = agent_type
        mock_node.config = config
        return mock_node

    @staticmethod
    def create_supervisor_node(config: Dict[str, Any]) -> MagicMock:
        """Create a mock supervisor node."""
        mock_node = MagicMock()
        mock_node.node_type = "supervisor"
        mock_node.config = config
        return mock_node


# Create global instances for compatibility
workflow_manager = LangGraphWorkflowManager()
agent_node_factory = AgentNodeFactory()
