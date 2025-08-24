"""
Human Approval Node for AI Development Agent.
Handles human-in-the-loop approval workflows.
"""

import logging
from typing import Dict, Any
from models.state import AgentState


class HumanApprovalNode:
    """
    Node for handling human approval in the workflow.
    """
    
    def __init__(self):
        """Initialize the human approval node."""
        self.logger = logging.getLogger("human_approval")
        
    def check_approval_needed(self, state: AgentState) -> AgentState:
        """
        Check if human approval is needed for the current state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        # Check if approval is needed based on configuration or state
        approval_needed = state.get("human_approval_needed", False)
        
        if approval_needed:
            self.logger.info("Human approval required")
            state["current_task"] = "wait_for_approval"
        else:
            self.logger.info("No human approval required")
            state["current_task"] = "continue_workflow"
            
        return state
    
    def wait_for_human_approval(self, state: AgentState) -> AgentState:
        """
        Wait for human approval input.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        # In a real implementation, this would wait for user input
        # For now, we'll simulate approval
        self.logger.info("Waiting for human approval...")
        
        # Simulate approval (in real implementation, this would be user input)
        state["human_feedback"] = {
            "approved": True,
            "comments": "Auto-approved for demonstration",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return state
    
    def handle_approval_response(self, state: AgentState) -> AgentState:
        """
        Handle the human approval response.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        feedback = state.get("human_feedback", {})
        approved = feedback.get("approved", False)
        
        if approved:
            self.logger.info("Human approval granted")
            state["human_approval_needed"] = False
            state["current_task"] = "continue_workflow"
        else:
            self.logger.info("Human approval denied")
            state["current_task"] = "handle_rejection"
            
        return state
    
    def create_approval_request(self, state: AgentState, approval_type: str, details: Dict[str, Any]) -> AgentState:
        """
        Create an approval request.
        
        Args:
            state: Current workflow state
            approval_type: Type of approval needed
            details: Details of what needs approval
            
        Returns:
            Updated state
        """
        approval_request = {
            "id": f"approval_{len(state.get('approval_requests', [])) + 1}",
            "type": approval_type,
            "details": details,
            "status": "pending",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        if "approval_requests" not in state:
            state["approval_requests"] = []
            
        state["approval_requests"].append(approval_request)
        state["human_approval_needed"] = True
        
        self.logger.info(f"Created approval request: {approval_request['id']}")
        
        return state
