#!/usr/bin/env python3
"""
Tests for supervisor state management.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from models.supervisor_state import (
    SupervisorSwarmState, Task, TaskResult, Escalation, ValidationResult,
    SupervisorDecision, HandoffRecord, PerformanceMetrics,
    create_initial_supervisor_swarm_state, update_supervisor_swarm_state,
    add_supervisor_decision, add_quality_validation, add_handoff_record,
    add_error, add_warning, increment_retry_count, add_execution_history_entry,
    add_performance_metric
)


class TestTask:
    """Tests for Task model."""
    
    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        task = Task(
            id="task_1",
            type="requirements_analysis",
            description="Analyze project requirements"
        )
        
        assert task.id == "task_1"
        assert task.type == "requirements_analysis"
        assert task.description == "Analyze project requirements"
        assert task.priority == "medium"
        assert task.estimated_complexity == "moderate"
        assert task.status == "pending"
        assert task.assigned_to is None
        assert isinstance(task.created_at, datetime)
    
    def test_task_creation_full(self):
        """Test creating a task with all fields."""
        task = Task(
            id="task_2",
            type="architecture_design",
            description="Design system architecture",
            requirements={"framework": "flask", "database": "postgresql"},
            priority="high",
            estimated_complexity="complex",
            dependencies=["task_1"],
            quality_criteria={"scalability": 0.8, "security": 0.9},
            assigned_to="architecture_designer",
            status="in_progress"
        )
        
        assert task.id == "task_2"
        assert task.type == "architecture_design"
        assert task.description == "Design system architecture"
        assert task.requirements["framework"] == "flask"
        assert task.priority == "high"
        assert task.estimated_complexity == "complex"
        assert task.dependencies == ["task_1"]
        assert task.quality_criteria["scalability"] == 0.8
        assert task.assigned_to == "architecture_designer"
        assert task.status == "in_progress"
    
    def test_task_validation_error(self):
        """Test task validation error handling."""
        with pytest.raises(ValidationError):
            Task(
                id="",  # Empty ID should fail
                type="",  # Empty type should also fail
                description=""  # Empty description should also fail
            )


class TestTaskResult:
    """Tests for TaskResult model."""
    
    def test_task_result_creation(self):
        """Test creating a task result."""
        result = TaskResult(
            task_id="task_1",
            worker="requirements_analyst",
            result={"requirements": ["req1", "req2"]}
        )
        
        assert result.task_id == "task_1"
        assert result.worker == "requirements_analyst"
        assert result.result["requirements"] == ["req1", "req2"]
        assert result.status == "completed"
        assert result.validation is None
        assert isinstance(result.timestamp, datetime)
    
    def test_task_result_with_validation(self):
        """Test creating a task result with validation."""
        validation = {"score": 0.85, "approved": True}
        result = TaskResult(
            task_id="task_1",
            worker="requirements_analyst",
            result={"requirements": ["req1"]},
            validation=validation,
            execution_time=5.2,
            status="validated"
        )
        
        assert result.validation == validation
        assert result.execution_time == 5.2
        assert result.status == "validated"


class TestEscalation:
    """Tests for Escalation model."""
    
    def test_escalation_creation(self):
        """Test creating an escalation."""
        escalation = Escalation(
            id="esc_1",
            from_agent="requirements_analyst",
            issue="Unclear project requirements"
        )
        
        assert escalation.id == "esc_1"
        assert escalation.from_agent == "requirements_analyst"
        assert escalation.issue == "Unclear project requirements"
        assert escalation.severity == "medium"
        assert escalation.status == "pending"
        assert isinstance(escalation.timestamp, datetime)
    
    def test_escalation_with_context(self):
        """Test creating an escalation with context."""
        context = {"attempts": 3, "last_error": "Invalid input"}
        escalation = Escalation(
            id="esc_2",
            from_agent="code_generator",
            issue="Complex algorithm implementation",
            severity="high",
            context=context
        )
        
        assert escalation.severity == "high"
        assert escalation.context["attempts"] == 3
        assert escalation.context["last_error"] == "Invalid input"


class TestValidationResult:
    """Tests for ValidationResult model."""
    
    def test_validation_result_creation(self):
        """Test creating a validation result."""
        validation = ValidationResult(
            task_type="requirements_analysis",
            overall_score=0.85,
            is_approved=True,
            criteria_scores={"completeness": 0.9, "clarity": 0.8},
            feedback="Good requirements analysis"
        )
        
        assert validation.task_type == "requirements_analysis"
        assert validation.overall_score == 0.85
        assert validation.is_approved is True
        assert validation.criteria_scores["completeness"] == 0.9
        assert validation.feedback == "Good requirements analysis"
        assert validation.validator == "quality_control_supervisor"
    
    def test_validation_result_custom_validator(self):
        """Test creating a validation result with custom validator."""
        validation = ValidationResult(
            task_type="code_review",
            overall_score=0.7,
            is_approved=False,
            criteria_scores={"readability": 0.6, "efficiency": 0.8},
            feedback="Code needs improvement",
            validator="senior_developer"
        )
        
        assert validation.validator == "senior_developer"
        assert validation.is_approved is False


class TestSupervisorDecision:
    """Tests for SupervisorDecision model."""
    
    def test_supervisor_decision_creation(self):
        """Test creating a supervisor decision."""
        decision = SupervisorDecision(
            decision_type="task_delegation",
            action="assign_to_requirements_analyst",
            reasoning="Task requires requirements analysis expertise",
            supervisor_id="project_manager"
        )
        
        assert decision.decision_type == "task_delegation"
        assert decision.action == "assign_to_requirements_analyst"
        assert decision.reasoning == "Task requires requirements analysis expertise"
        assert decision.supervisor_id == "project_manager"
        assert isinstance(decision.timestamp, datetime)


class TestHandoffRecord:
    """Tests for HandoffRecord model."""
    
    def test_handoff_record_creation(self):
        """Test creating a handoff record."""
        handoff = HandoffRecord(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            reason="Architecture-related questions"
        )
        
        assert handoff.from_agent == "requirements_analyst"
        assert handoff.to_agent == "architecture_designer"
        assert handoff.reason == "Architecture-related questions"
        assert handoff.status == "completed"
        assert isinstance(handoff.timestamp, datetime)


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics model."""
    
    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        metric = PerformanceMetrics(
            agent_id="requirements_analyst",
            metric_type="execution_time",
            value=5.2,
            unit="seconds"
        )
        
        assert metric.agent_id == "requirements_analyst"
        assert metric.metric_type == "execution_time"
        assert metric.value == 5.2
        assert metric.unit == "seconds"
        assert isinstance(metric.timestamp, datetime)


class TestStateManagement:
    """Tests for state management functions."""
    
    def test_create_initial_supervisor_swarm_state(self):
        """Test creating initial supervisor-swarm state."""
        state = create_initial_supervisor_swarm_state(
            project_context="Create a web application",
            project_name="test_project",
            session_id="session_123"
        )
        
        assert state["project_context"] == "Create a web application"
        assert state["project_name"] == "test_project"
        assert state["session_id"] == "session_123"
        assert state["current_phase"] == "started"
        assert state["current_supervisor_task"] is None
        assert state["active_agent"] is None
        assert state["requirements"] == []
        assert state["architecture"] == {}
        assert state["supervisor_decisions"] == []
        assert state["quality_validations"] == []
        assert state["errors"] == []
        assert state["warnings"] == []
        assert state["retry_count"] == 0
    
    def test_update_supervisor_swarm_state(self):
        """Test updating supervisor-swarm state."""
        initial_state = create_initial_supervisor_swarm_state("Test project")
        
        updates = {
            "current_phase": "execution",
            "active_agent": "requirements_analyst",
            "requirements": [{"id": "req1", "description": "User authentication"}]
        }
        
        updated_state = update_supervisor_swarm_state(initial_state, updates)
        
        assert updated_state["current_phase"] == "execution"
        assert updated_state["active_agent"] == "requirements_analyst"
        assert len(updated_state["requirements"]) == 1
        assert updated_state["requirements"][0]["id"] == "req1"
        
        # Original state should remain unchanged
        assert initial_state["current_phase"] == "started"
        assert initial_state["active_agent"] is None
        assert initial_state["requirements"] == []
    
    def test_add_supervisor_decision(self):
        """Test adding a supervisor decision."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        decision = SupervisorDecision(
            decision_type="task_delegation",
            action="assign_task",
            reasoning="Task requires specialized expertise",
            supervisor_id="project_manager"
        )
        
        updated_state = add_supervisor_decision(state, decision)
        
        assert len(updated_state["supervisor_decisions"]) == 1
        assert updated_state["supervisor_decisions"][0]["decision_type"] == "task_delegation"
        assert updated_state["supervisor_decisions"][0]["action"] == "assign_task"
        
        # Original state should remain unchanged
        assert len(state["supervisor_decisions"]) == 0
    
    def test_add_quality_validation(self):
        """Test adding a quality validation."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        validation = ValidationResult(
            task_type="requirements_analysis",
            overall_score=0.85,
            is_approved=True,
            criteria_scores={"completeness": 0.9, "clarity": 0.8},
            feedback="Good requirements analysis"
        )
        
        updated_state = add_quality_validation(state, validation)
        
        assert len(updated_state["quality_validations"]) == 1
        assert updated_state["quality_validations"][0]["task_type"] == "requirements_analysis"
        assert updated_state["quality_validations"][0]["overall_score"] == 0.85
        assert updated_state["current_validation"]["task_type"] == "requirements_analysis"
        
        # Original state should remain unchanged
        assert len(state["quality_validations"]) == 0
        assert state.get("current_validation") is None
    
    def test_add_handoff_record(self):
        """Test adding a handoff record."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        handoff = HandoffRecord(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            reason="Architecture questions"
        )
        
        updated_state = add_handoff_record(state, handoff)
        
        assert len(updated_state["handoff_history"]) == 1
        assert updated_state["handoff_history"][0]["from_agent"] == "requirements_analyst"
        assert updated_state["handoff_history"][0]["to_agent"] == "architecture_designer"
        
        # Original state should remain unchanged
        assert len(state["handoff_history"]) == 0
    
    def test_add_error(self):
        """Test adding an error."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        updated_state = add_error(state, "Task execution failed")
        
        assert len(updated_state["errors"]) == 1
        assert updated_state["errors"][0] == "Task execution failed"
        
        # Original state should remain unchanged
        assert len(state["errors"]) == 0
    
    def test_add_warning(self):
        """Test adding a warning."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        updated_state = add_warning(state, "Performance degradation detected")
        
        assert len(updated_state["warnings"]) == 1
        assert updated_state["warnings"][0] == "Performance degradation detected"
        
        # Original state should remain unchanged
        assert len(state["warnings"]) == 0
    
    def test_increment_retry_count(self):
        """Test incrementing retry count."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        updated_state = increment_retry_count(state)
        assert updated_state["retry_count"] == 1
        
        updated_state = increment_retry_count(updated_state)
        assert updated_state["retry_count"] == 2
        
        # Original state should remain unchanged
        assert state["retry_count"] == 0
    
    def test_add_execution_history_entry(self):
        """Test adding execution history entry."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        entry = {
            "step": "requirements_analysis",
            "agent": "requirements_analyst",
            "duration": 5.2
        }
        
        updated_state = add_execution_history_entry(state, entry)
        
        assert len(updated_state["execution_history"]) == 1
        assert updated_state["execution_history"][0]["step"] == "requirements_analysis"
        assert updated_state["execution_history"][0]["agent"] == "requirements_analyst"
        assert updated_state["execution_history"][0]["duration"] == 5.2
        assert "timestamp" in updated_state["execution_history"][0]
        
        # Original state should remain unchanged
        assert len(state["execution_history"]) == 0
    
    def test_add_performance_metric(self):
        """Test adding performance metric."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        metric = PerformanceMetrics(
            agent_id="requirements_analyst",
            metric_type="execution_time",
            value=5.2,
            unit="seconds"
        )
        
        updated_state = add_performance_metric(state, metric)
        
        assert "requirements_analyst" in updated_state["performance_metrics"]
        assert "execution_time" in updated_state["performance_metrics"]["requirements_analyst"]
        assert updated_state["performance_metrics"]["requirements_analyst"]["execution_time"]["value"] == 5.2
        
        # Original state should remain unchanged
        assert len(state["performance_metrics"]) == 0


class TestStateIntegration:
    """Integration tests for state management."""
    
    def test_complete_workflow_state_updates(self):
        """Test a complete workflow with multiple state updates."""
        # Create initial state
        state = create_initial_supervisor_swarm_state("Create web application")
        
        # Add supervisor decision
        decision = SupervisorDecision(
            decision_type="task_delegation",
            action="assign_to_requirements_analyst",
            reasoning="Start with requirements analysis",
            supervisor_id="project_manager"
        )
        state = add_supervisor_decision(state, decision)
        
        # Add execution history
        state = add_execution_history_entry(state, {
            "step": "requirements_analysis",
            "agent": "requirements_analyst",
            "duration": 5.2
        })
        
        # Add performance metric
        metric = PerformanceMetrics(
            agent_id="requirements_analyst",
            metric_type="execution_time",
            value=5.2,
            unit="seconds"
        )
        state = add_performance_metric(state, metric)
        
        # Add quality validation
        validation = ValidationResult(
            task_type="requirements_analysis",
            overall_score=0.85,
            is_approved=True,
            criteria_scores={"completeness": 0.9, "clarity": 0.8},
            feedback="Good requirements analysis"
        )
        state = add_quality_validation(state, validation)
        
        # Add handoff record
        handoff = HandoffRecord(
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            reason="Architecture questions"
        )
        state = add_handoff_record(state, handoff)
        
        # Verify final state
        assert len(state["supervisor_decisions"]) == 1
        assert len(state["execution_history"]) == 1
        assert len(state["quality_validations"]) == 1
        assert len(state["handoff_history"]) == 1
        assert "requirements_analyst" in state["performance_metrics"]
        assert state["current_validation"]["task_type"] == "requirements_analysis"
        assert state["current_validation"]["is_approved"] is True
    
    def test_error_handling_workflow(self):
        """Test error handling workflow."""
        state = create_initial_supervisor_swarm_state("Test project")
        
        # Add warning
        state = add_warning(state, "Performance degradation detected")
        
        # Add error
        state = add_error(state, "Task execution failed")
        
        # Increment retry count
        state = increment_retry_count(state)
        state = increment_retry_count(state)
        
        # Verify error handling state
        assert len(state["warnings"]) == 1
        assert len(state["errors"]) == 1
        assert state["retry_count"] == 2
        assert state["warnings"][0] == "Performance degradation detected"
        assert state["errors"][0] == "Task execution failed"
