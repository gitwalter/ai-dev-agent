#!/usr/bin/env python3
"""
Test suite for the Handoff Management System.

Tests dynamic agent assignment, handoff validation, and handoff processing.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.handoff_manager import (
    HandoffManager, HandoffValidationResult, HandoffPriority, HandoffStatus,
    validate_handoff, suggest_agents, create_handoff, process_handoffs
)
from models.state import AgentState, HandoffRequest, create_initial_state


class TestHandoffManager:
    """Test cases for HandoffManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handoff_manager = HandoffManager()
        self.initial_state = create_initial_state(
            project_context="Test project for handoff system",
            project_name="handoff_test",
            session_id="test_session_handoff"
        )
    
    def test_handoff_manager_initialization(self):
        """Test handoff manager initialization."""
        assert self.handoff_manager is not None
        assert hasattr(self.handoff_manager, 'agent_capabilities')
        assert len(self.handoff_manager.agent_capabilities) > 0
        
        # Check that all expected agents are present
        expected_agents = [
            "requirements_analyst", "architecture_designer", "code_generator",
            "test_generator", "code_reviewer", "security_analyst", "documentation_generator"
        ]
        for agent in expected_agents:
            assert agent in self.handoff_manager.agent_capabilities
    
    def test_agent_capabilities_structure(self):
        """Test that agent capabilities have the correct structure."""
        for agent_name, capabilities in self.handoff_manager.agent_capabilities.items():
            assert "primary_tasks" in capabilities
            assert "secondary_tasks" in capabilities
            assert "expertise" in capabilities
            
            assert isinstance(capabilities["primary_tasks"], list)
            assert isinstance(capabilities["secondary_tasks"], list)
            assert isinstance(capabilities["expertise"], list)
    
    def test_validate_handoff_request_valid(self):
        """Test validation of a valid handoff request."""
        handoff = HandoffRequest(
            handoff_id="test_handoff_1",
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design system architecture based on requirements",
            data_to_transfer={
                "requirements": [{"id": 1, "description": "User authentication"}],
                "project_context": "Web application for user management"
            },
            priority="normal"
        )
        
        result = self.handoff_manager.validate_handoff_request(handoff, self.initial_state)
        
        assert result.is_valid is True
        assert "valid" in result.reason.lower()
        assert len(result.suggestions) == 0
    
    def test_validate_handoff_request_invalid_agent(self):
        """Test validation with invalid agent names."""
        handoff = HandoffRequest(
            handoff_id="test_handoff_2",
            from_agent="invalid_agent",
            to_agent="architecture_designer",
            task_description="Design system architecture",
            data_to_transfer={"requirements": []},
            priority="normal"
        )
        
        result = self.handoff_manager.validate_handoff_request(handoff, self.initial_state)
        
        assert result.is_valid is False
        assert "does not exist" in result.reason
        assert len(result.suggestions) > 0
    
    def test_validate_handoff_request_incompatible_task(self):
        """Test validation with incompatible task."""
        handoff = HandoffRequest(
            handoff_id="test_handoff_3",
            from_agent="requirements_analyst",
            to_agent="test_generator",
            task_description="Cook dinner and wash dishes",  # Incompatible task
            data_to_transfer={"requirements": []},
            priority="normal"
        )
        
        result = self.handoff_manager.validate_handoff_request(handoff, self.initial_state)
        
        assert result.is_valid is False
        assert "not compatible" in result.reason
        assert len(result.suggestions) > 0
    
    def test_validate_handoff_request_missing_data(self):
        """Test validation with missing required data."""
        handoff = HandoffRequest(
            handoff_id="test_handoff_4",
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design system architecture",
            data_to_transfer={},  # Missing required data
            priority="normal"
        )
        
        result = self.handoff_manager.validate_handoff_request(handoff, self.initial_state)
        
        assert result.is_valid is False
        assert "Missing required data types" in result.reason
        assert len(result.suggestions) > 0
    
    def test_suggest_alternative_agents(self):
        """Test agent suggestion functionality."""
        task_description = "Design system architecture and select technology stack"
        
        suggestions = self.handoff_manager.suggest_alternative_agents(task_description)
        
        assert len(suggestions) > 0
        assert all(isinstance(suggestion, tuple) for suggestion in suggestions)
        assert all(len(suggestion) == 2 for suggestion in suggestions)
        assert all(isinstance(suggestion[0], str) for suggestion in suggestions)
        assert all(isinstance(suggestion[1], float) for suggestion in suggestions)
        
        # Check that suggestions are sorted by score (highest first)
        scores = [suggestion[1] for suggestion in suggestions]
        assert scores == sorted(scores, reverse=True)
        
        # Check that architecture_designer is highly ranked for this task
        agent_names = [suggestion[0] for suggestion in suggestions]
        assert "architecture_designer" in agent_names[:3]  # Should be in top 3
    
    def test_suggest_alternative_agents_with_exclusion(self):
        """Test agent suggestion with exclusion list."""
        task_description = "Generate comprehensive test cases"
        exclude_agents = ["test_generator"]  # Exclude the most suitable agent
        
        suggestions = self.handoff_manager.suggest_alternative_agents(task_description, exclude_agents)
        
        assert len(suggestions) > 0
        agent_names = [suggestion[0] for suggestion in suggestions]
        assert "test_generator" not in agent_names
    
    def test_create_handoff_request(self):
        """Test handoff request creation."""
        handoff = self.handoff_manager.create_handoff_request(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design system architecture",
            data_to_transfer={"requirements": []},
            priority="high",
            context={"reason": "Complex requirements need architectural review"}
        )
        
        assert isinstance(handoff, HandoffRequest)
        assert handoff.from_agent == "requirements_analyst"
        assert handoff.to_agent == "architecture_designer"
        assert handoff.task_description == "Design system architecture"
        assert handoff.priority == "high"
        assert handoff.status == "pending"
        assert "handoff_requirements_analyst_architecture_designer_" in handoff.handoff_id
        assert handoff.context["reason"] == "Complex requirements need architectural review"
    
    def test_calculate_task_compatibility_score(self):
        """Test task compatibility score calculation."""
        # Test high compatibility
        capabilities = {
            "primary_tasks": ["architecture_design", "system_design"],
            "secondary_tasks": ["technology_selection"],
            "expertise": ["system_architecture", "design_patterns"]
        }
        
        score = self.handoff_manager._calculate_task_compatibility_score(
            "Design system architecture and select technology stack",
            capabilities
        )
        
        assert score > 0.5  # Should be high compatibility
        
        # Test low compatibility
        score = self.handoff_manager._calculate_task_compatibility_score(
            "Cook dinner and wash dishes",
            capabilities
        )
        
        assert score < 0.3  # Should be low compatibility
    
    def test_get_required_data_types(self):
        """Test required data types for different agents."""
        # Test architecture designer
        required = self.handoff_manager._get_required_data_types("architecture_designer")
        assert "requirements" in required
        assert "project_context" in required
        
        # Test code generator
        required = self.handoff_manager._get_required_data_types("code_generator")
        assert "requirements" in required
        assert "architecture" in required
        assert "tech_stack" in required
        
        # Test unknown agent
        required = self.handoff_manager._get_required_data_types("unknown_agent")
        assert required == []


class TestHandoffValidationResult:
    """Test cases for HandoffValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test HandoffValidationResult creation."""
        result = HandoffValidationResult(
            is_valid=True,
            reason="Handoff is valid",
            suggestions=["Proceed with handoff"]
        )
        
        assert result.is_valid is True
        assert result.reason == "Handoff is valid"
        assert result.suggestions == ["Proceed with handoff"]
    
    def test_validation_result_default_suggestions(self):
        """Test HandoffValidationResult with default suggestions."""
        result = HandoffValidationResult(
            is_valid=False,
            reason="Invalid handoff"
        )
        
        assert result.is_valid is False
        assert result.reason == "Invalid handoff"
        assert result.suggestions == []


class TestHandoffIntegration:
    """Integration tests for handoff system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.initial_state = create_initial_state(
            project_context="Integration test project",
            project_name="handoff_integration_test",
            session_id="test_session_integration"
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_handoff_workflow(self):
        """Test complete handoff workflow."""
        # Step 1: Create a valid handoff request
        handoff = create_handoff(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design system architecture based on requirements",
            data_to_transfer={
                "requirements": [
                    {"id": 1, "description": "User authentication system"},
                    {"id": 2, "description": "User profile management"}
                ],
                "project_context": "Web application for user management"
            },
            priority="high",
            context={"reason": "Complex requirements need architectural design"}
        )
        
        # Step 2: Validate the handoff
        validation = validate_handoff(handoff, self.initial_state)
        assert validation.is_valid is True
        
        # Step 3: Add handoff to queue
        self.initial_state["handoff_queue"].append(handoff.model_dump())
        
        # Step 4: Process handoffs
        updated_state = process_handoffs(self.initial_state)
        
        # Step 5: Verify handoff was processed
        assert len(updated_state["handoff_queue"]) == 0
        assert len(updated_state["handoff_history"]) == 1
        
        # Verify handoff history entry
        handoff_history_entry = updated_state["handoff_history"][0]
        assert handoff_history_entry["from_agent"] == "requirements_analyst"
        assert handoff_history_entry["to_agent"] == "architecture_designer"
        assert handoff_history_entry["status"] == "completed"
        
        # Verify state was updated
        assert updated_state["current_agent"] == "architecture_designer"
        assert "requirements" in updated_state
        assert "project_context" in updated_state
        
        # Verify collaboration context
        assert "collaboration_context" in updated_state
        assert len(updated_state["collaboration_context"]) > 0
    
    @pytest.mark.asyncio
    async def test_handoff_with_alternative_suggestions(self):
        """Test handoff with alternative agent suggestions."""
        # Create handoff with incompatible task
        handoff = create_handoff(
            from_agent="requirements_analyst",
            to_agent="test_generator",
            task_description="Design system architecture",  # Incompatible with test_generator
            data_to_transfer={"requirements": []},
            priority="normal"
        )
        
        # Validate handoff (should fail)
        validation = validate_handoff(handoff, self.initial_state)
        assert validation.is_valid is False
        
        # Get alternative suggestions
        suggestions = suggest_agents("Design system architecture", ["test_generator"])
        assert len(suggestions) > 0
        
        # Check that architecture_designer is suggested
        suggested_agents = [s[0] for s in suggestions]
        assert "architecture_designer" in suggested_agents
    
    @pytest.mark.asyncio
    async def test_multiple_handoffs_processing(self):
        """Test processing multiple handoffs in queue."""
        # Create multiple handoff requests
        handoff1 = create_handoff(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design architecture",
            data_to_transfer={"requirements": [], "project_context": "Test project"},
            priority="high"
        )
        
        handoff2 = create_handoff(
            from_agent="architecture_designer",
            to_agent="code_generator",
            task_description="Generate code",
            data_to_transfer={"architecture": {}, "requirements": [], "tech_stack": ["python", "fastapi"]},
            priority="normal"
        )
        
        # Add both to queue
        self.initial_state["handoff_queue"].extend([handoff1.model_dump(), handoff2.model_dump()])
        
        # Process handoffs
        updated_state = process_handoffs(self.initial_state)
        
        # Verify both were processed
        assert len(updated_state["handoff_queue"]) == 0
        assert len(updated_state["handoff_history"]) == 2
        
        # Verify final agent is code_generator (last handoff)
        assert updated_state["current_agent"] == "code_generator"


class TestHandoffErrorHandling:
    """Test error handling in handoff system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.initial_state = create_initial_state(
            project_context="Error handling test project",
            project_name="handoff_error_test",
            session_id="test_session_error"
        )
    
    def test_handoff_with_invalid_data_structure(self):
        """Test handoff with invalid data structure."""
        # Create handoff with invalid data
        handoff = create_handoff(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design architecture",
            data_to_transfer={"invalid_key": "invalid_value"},  # Missing required data
            priority="normal"
        )
        
        # Validate handoff
        validation = validate_handoff(handoff, self.initial_state)
        assert validation.is_valid is False
        assert "Missing required data types" in validation.reason
    
    def test_handoff_with_unavailable_agent(self):
        """Test handoff with unavailable agent."""
        # Set agent as unavailable
        self.initial_state["agent_availability"]["architecture_designer"] = False
        
        handoff = create_handoff(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design architecture",
            data_to_transfer={"requirements": []},
            priority="normal"
        )
        
        # Validate handoff
        validation = validate_handoff(handoff, self.initial_state)
        assert validation.is_valid is False
        assert "not available" in validation.reason


if __name__ == "__main__":
    pytest.main([__file__])
