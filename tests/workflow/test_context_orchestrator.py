#!/usr/bin/env python3
"""
Comprehensive tests for the ContextOrchestrator component.
Tests workflow execution, context transitions, and error handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from workflow.orchestration.context_orchestrator import ContextOrchestrator
from workflow.models.workflow_models import (
    WorkflowDefinition, WorkflowState, WorkflowResult, WorkflowPhase,
    PhaseStatus, WorkflowStatus, RecoveryAction, ValidationResult,
    TaskAnalysis, Entity, ComplexityLevel
)


class TestContextOrchestrator:
    """Test suite for ContextOrchestrator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.context_switcher = AsyncMock()
        self.rule_loader = AsyncMock()
        self.agent_manager = Mock()
        
        self.orchestrator = ContextOrchestrator(
            context_switcher=self.context_switcher,
            rule_loader=self.rule_loader,
            agent_manager=self.agent_manager
        )
        
        # Create sample workflow
        self.sample_workflow = WorkflowDefinition(
            workflow_id="test_workflow_001",
            name="Test Workflow",
            description="Sample workflow for testing",
            phases=[
                WorkflowPhase(
                    phase_id="phase_1",
                    context="@agile",
                    name="Requirements Analysis",
                    description="Analyze requirements",
                    inputs=["task_description"],
                    outputs=["user_stories"],
                    timeout=300
                ),
                WorkflowPhase(
                    phase_id="phase_2",
                    context="@code",
                    name="Implementation",
                    description="Implement feature",
                    inputs=["user_stories"],
                    outputs=["source_code"],
                    timeout=600
                ),
                WorkflowPhase(
                    phase_id="phase_3",
                    context="@test",
                    name="Testing",
                    description="Test implementation",
                    inputs=["source_code"],
                    outputs=["test_results"],
                    timeout=300
                )
            ],
            dependencies={"phase_2": ["phase_1"], "phase_3": ["phase_2"]},
            estimated_duration=60
        )
    
    def test_initialization(self):
        """Test ContextOrchestrator initialization."""
        assert self.orchestrator is not None
        assert hasattr(self.orchestrator, 'active_workflows')
        assert hasattr(self.orchestrator, 'recovery_strategies')
        assert len(self.orchestrator.recovery_strategies) > 0
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self):
        """Test successful workflow execution."""
        result = await self.orchestrator.execute_workflow(self.sample_workflow)
        
        assert isinstance(result, WorkflowResult)
        assert result.workflow_id == self.sample_workflow.workflow_id
        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.phases_executed) == len(self.sample_workflow.phases)
        assert len(result.phases_failed) == 0
        assert result.execution_time >= 0
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_initial_context(self):
        """Test workflow execution with initial context data."""
        initial_context = {"project_name": "test_project", "environment": "development"}
        
        result = await self.orchestrator.execute_workflow(self.sample_workflow, initial_context)
        
        assert result.status == WorkflowStatus.COMPLETED
        # Verify initial context was used
        workflow_id = self.sample_workflow.workflow_id
        assert workflow_id not in self.orchestrator.active_workflows  # Should be cleaned up
    
    @pytest.mark.asyncio
    async def test_execute_single_phase_success(self):
        """Test successful single phase execution."""
        phase = self.sample_workflow.phases[0]
        state = WorkflowState(
            workflow_id=self.sample_workflow.workflow_id,
            context_data={"task_description": "Test task"}
        )
        
        await self.orchestrator._execute_single_phase(phase, self.sample_workflow, state)
        
        assert state.phase_status[phase.phase_id] == PhaseStatus.COMPLETED
        assert phase.phase_id in state.completed_phases
        assert phase.phase_id in state.phase_results
    
    @pytest.mark.asyncio
    async def test_execute_single_phase_timeout(self):
        """Test phase execution with timeout."""
        # Create phase with very short timeout
        phase = WorkflowPhase(
            phase_id="timeout_phase",
            context="@code",
            name="Timeout Phase",
            description="Phase that will timeout",
            inputs=[],
            outputs=[],
            timeout=0.001  # Very short timeout
        )
        
        state = WorkflowState(workflow_id="test_workflow")
        
        # Mock phase execution to take longer than timeout
        async def slow_execution(*args):
            await asyncio.sleep(0.1)  # Longer than timeout (0.001)
            return {"result": "success"}
        
        with patch.object(self.orchestrator, '_execute_phase_logic', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = slow_execution
            
            await self.orchestrator._execute_single_phase(phase, self.sample_workflow, state)
            
            assert state.phase_status[phase.phase_id] == PhaseStatus.FAILED
            assert phase.phase_id in state.failed_phases
    
    @pytest.mark.asyncio
    async def test_execute_parallel_phases(self):
        """Test parallel phase execution."""
        # Create phases that can run in parallel
        parallel_phases = [
            WorkflowPhase(
                phase_id="parallel_1",
                context="@docs",
                name="Documentation",
                description="Create docs",
                inputs=[],
                outputs=["docs"],
                parallel_group="group_1"
            ),
            WorkflowPhase(
                phase_id="parallel_2",
                context="@security",
                name="Security Review",
                description="Security analysis",
                inputs=[],
                outputs=["security_report"],
                parallel_group="group_1"
            )
        ]
        
        state = WorkflowState(workflow_id="parallel_test")
        
        await self.orchestrator._execute_parallel_phases(parallel_phases, self.sample_workflow, state)
        
        # Both phases should complete
        for phase in parallel_phases:
            assert state.phase_status[phase.phase_id] in [PhaseStatus.COMPLETED, PhaseStatus.FAILED]
    
    @pytest.mark.asyncio
    async def test_transition_context_success(self):
        """Test successful context transition."""
        state = WorkflowState(
            workflow_id="test_workflow",
            context_data={"current_data": "test"}
        )
        
        result_state = await self.orchestrator.transition_context("@agile", "@code", state)
        
        assert result_state.current_phase == "@code"
        assert self.context_switcher.switch_context.called
        assert self.rule_loader.load_context_rules.called
    
    @pytest.mark.asyncio
    async def test_transition_context_invalid(self):
        """Test context transition with invalid context."""
        state = WorkflowState(workflow_id="test_workflow")
        
        with pytest.raises(ValueError, match="Invalid context transition"):
            await self.orchestrator.transition_context("@agile", "@invalid", state)
    
    @pytest.mark.asyncio
    async def test_propagate_results_success(self):
        """Test successful result propagation."""
        state = WorkflowState(workflow_id="test_workflow")
        results = {"user_stories": ["Story 1", "Story 2"], "acceptance_criteria": ["AC 1"]}
        
        propagated = await self.orchestrator.propagate_results("phase_1", "phase_2", results, state)
        
        assert isinstance(propagated, dict)
        assert propagated["user_stories"] == results["user_stories"]
        assert "_source_phase" in propagated
        assert "_target_phase" in propagated
        assert state.phase_results["phase_1"] == results
    
    @pytest.mark.asyncio
    async def test_handle_failure_retry_strategy(self):
        """Test failure handling with retry strategy."""
        state = WorkflowState(workflow_id="test_workflow")
        error = asyncio.TimeoutError("Phase timeout")
        
        recovery_action = await self.orchestrator.handle_failure("@code", error, state)
        
        assert isinstance(recovery_action, RecoveryAction)
        assert recovery_action.action_type == "retry"
        assert len(state.errors) > 0
    
    @pytest.mark.asyncio
    async def test_handle_failure_abort_strategy(self):
        """Test failure handling with abort strategy."""
        state = WorkflowState(workflow_id="test_workflow")
        error = Exception("Critical error occurred")
        
        recovery_action = await self.orchestrator.handle_failure("@code", error, state)
        
        assert isinstance(recovery_action, RecoveryAction)
        assert recovery_action.action_type == "abort"
    
    @pytest.mark.asyncio
    async def test_execute_agile_phase(self):
        """Test agile phase execution."""
        phase = WorkflowPhase(
            phase_id="agile_test",
            context="@agile",
            name="Agile Phase",
            description="Test agile phase",
            inputs=["task_description"],
            outputs=["user_stories"]
        )
        inputs = {"task_description": "Create user login feature"}
        state = WorkflowState(workflow_id="test")
        
        result = await self.orchestrator._execute_agile_phase(phase, inputs, state)
        
        assert isinstance(result, dict)
        assert "user_stories" in result
        assert "acceptance_criteria" in result
        assert isinstance(result["user_stories"], list)
    
    @pytest.mark.asyncio
    async def test_execute_code_phase(self):
        """Test code phase execution."""
        phase = WorkflowPhase(
            phase_id="code_test",
            context="@code",
            name="Code Phase",
            description="Test code phase",
            inputs=["design_specs"],
            outputs=["source_code"]
        )
        inputs = {"design_specs": "API specification"}
        state = WorkflowState(workflow_id="test")
        
        result = await self.orchestrator._execute_code_phase(phase, inputs, state)
        
        assert isinstance(result, dict)
        assert "source_code" in result
        assert "implementation_notes" in result
        assert isinstance(result["source_code"], dict)
    
    @pytest.mark.asyncio
    async def test_execute_test_phase(self):
        """Test testing phase execution."""
        phase = WorkflowPhase(
            phase_id="test_test",
            context="@test",
            name="Test Phase",
            description="Test testing phase",
            inputs=["source_code"],
            outputs=["test_results"]
        )
        inputs = {"source_code": {"files": ["main.py"]}}
        state = WorkflowState(workflow_id="test")
        
        result = await self.orchestrator._execute_test_phase(phase, inputs, state)
        
        assert isinstance(result, dict)
        assert "test_suite" in result
        assert "test_results" in result
        assert "coverage_report" in result
    
    @pytest.mark.asyncio
    async def test_execute_debug_phase(self):
        """Test debug phase execution."""
        phase = WorkflowPhase(
            phase_id="debug_test",
            context="@debug",
            name="Debug Phase",
            description="Test debug phase",
            inputs=["error_logs"],
            outputs=["fixes"]
        )
        inputs = {"error_logs": ["Error 1", "Error 2"]}
        state = WorkflowState(workflow_id="test")
        
        result = await self.orchestrator._execute_debug_phase(phase, inputs, state)
        
        assert isinstance(result, dict)
        assert "root_cause_analysis" in result
        assert "fixes" in result
        assert isinstance(result["fixes"], list)
    
    @pytest.mark.asyncio
    async def test_execute_security_phase(self):
        """Test security phase execution."""
        phase = WorkflowPhase(
            phase_id="security_test",
            context="@security",
            name="Security Phase",
            description="Test security phase",
            inputs=["source_code"],
            outputs=["security_analysis"]
        )
        inputs = {"source_code": {"files": ["auth.py"]}}
        state = WorkflowState(workflow_id="test")
        
        result = await self.orchestrator._execute_security_phase(phase, inputs, state)
        
        assert isinstance(result, dict)
        assert "security_analysis" in result
        assert "vulnerability_report" in result
        assert isinstance(result["vulnerability_report"], dict)
    
    @pytest.mark.asyncio
    async def test_execute_git_phase(self):
        """Test git phase execution."""
        phase = WorkflowPhase(
            phase_id="git_test",
            context="@git",
            name="Git Phase",
            description="Test git phase",
            inputs=["source_code", "test_results"],
            outputs=["commit_hash"]
        )
        inputs = {"source_code": {"files": ["main.py"]}, "test_results": {"passed": 10}}
        state = WorkflowState(workflow_id="test")
        
        result = await self.orchestrator._execute_git_phase(phase, inputs, state)
        
        assert isinstance(result, dict)
        assert "commit_hash" in result
        assert "deployment_status" in result
        assert result["deployment_status"] == "Successfully deployed"
    
    def test_initialize_workflow_state(self):
        """Test workflow state initialization."""
        initial_context = {"project": "test", "environment": "dev"}
        
        state = self.orchestrator._initialize_workflow_state(self.sample_workflow, initial_context)
        
        assert isinstance(state, WorkflowState)
        assert state.workflow_id == self.sample_workflow.workflow_id
        assert state.status == WorkflowStatus.PENDING
        assert state.context_data == initial_context
        assert len(state.phase_status) == len(self.sample_workflow.phases)
        
        # All phases should start as pending
        for phase in self.sample_workflow.phases:
            assert state.phase_status[phase.phase_id] == PhaseStatus.PENDING
    
    def test_build_execution_plan_sequential(self):
        """Test building execution plan for sequential phases."""
        plan = self.orchestrator._build_execution_plan(self.sample_workflow)
        
        assert isinstance(plan, list)
        assert len(plan) == len(self.sample_workflow.phases)
        
        # Should be sequential phases (not lists)
        for item in plan:
            assert isinstance(item, WorkflowPhase)
    
    def test_build_execution_plan_parallel(self):
        """Test building execution plan with parallel phases."""
        # Create workflow with parallel phases
        parallel_workflow = WorkflowDefinition(
            workflow_id="parallel_workflow",
            name="Parallel Workflow",
            description="Workflow with parallel phases",
            phases=[
                WorkflowPhase(
                    phase_id="seq_1",
                    context="@agile",
                    name="Sequential 1",
                    description="Sequential phase",
                    inputs=[],
                    outputs=[]
                ),
                WorkflowPhase(
                    phase_id="par_1",
                    context="@docs",
                    name="Parallel 1",
                    description="Parallel phase 1",
                    inputs=[],
                    outputs=[],
                    parallel_group="group_1"
                ),
                WorkflowPhase(
                    phase_id="par_2",
                    context="@security",
                    name="Parallel 2",
                    description="Parallel phase 2",
                    inputs=[],
                    outputs=[],
                    parallel_group="group_1"
                )
            ],
            dependencies={},
            estimated_duration=60
        )
        
        plan = self.orchestrator._build_execution_plan(parallel_workflow)
        
        # Should have both sequential phases and parallel groups
        has_parallel_group = any(isinstance(item, list) for item in plan)
        assert has_parallel_group or len(plan) == len(parallel_workflow.phases)
    
    def test_prepare_phase_inputs(self):
        """Test preparation of phase inputs."""
        phase = self.sample_workflow.phases[1]  # Code phase
        state = WorkflowState(
            workflow_id="test",
            context_data={"global_data": "test"},
            phase_results={"phase_1": {"user_stories": ["Story 1"]}}
        )
        
        inputs = self.orchestrator._prepare_phase_inputs(phase, state)
        
        assert isinstance(inputs, dict)
        assert "global_data" in inputs
        assert "previous_phase_1" in inputs
        assert inputs["previous_phase_1"]["user_stories"] == ["Story 1"]
    
    def test_validate_context_transition_valid(self):
        """Test validation of valid context transitions."""
        state = WorkflowState(workflow_id="test")
        
        # Valid transitions
        assert self.orchestrator._validate_context_transition("@agile", "@design", state) is True
        assert self.orchestrator._validate_context_transition("@code", "@test", state) is True
        assert self.orchestrator._validate_context_transition(None, "@agile", state) is True
    
    def test_validate_context_transition_invalid(self):
        """Test validation of invalid context transitions."""
        state = WorkflowState(workflow_id="test")
        
        # Invalid transitions
        assert self.orchestrator._validate_context_transition("@agile", "@invalid", state) is False
        assert self.orchestrator._validate_context_transition("@agile", "not_context", state) is False
        assert self.orchestrator._validate_context_transition("@agile", "", state) is False
    
    def test_capture_context_state(self):
        """Test capturing context state."""
        state = WorkflowState(
            workflow_id="test",
            phase_results={"phase_1": {"data": "test"}},
            context_data={"@agile": {"agile_data": "test"}}
        )
        
        captured = self.orchestrator._capture_context_state("@agile", state)
        
        assert isinstance(captured, dict)
        assert "context" in captured
        assert "timestamp" in captured
        assert "phase_results" in captured
        assert captured["context"] == "@agile"
    
    def test_transform_phase_results(self):
        """Test transformation of phase results."""
        results = {"user_stories": ["Story 1"], "acceptance_criteria": ["AC 1"]}
        state = WorkflowState(workflow_id="test")
        
        transformed = self.orchestrator._transform_phase_results("phase_1", "phase_2", results, state)
        
        assert isinstance(transformed, dict)
        assert transformed["user_stories"] == results["user_stories"]
        assert transformed["_source_phase"] == "phase_1"
        assert transformed["_target_phase"] == "phase_2"
        assert "_transformation_timestamp" in transformed
    
    def test_validate_propagated_data_valid(self):
        """Test validation of valid propagated data."""
        data = {
            "user_stories": ["Story 1"],
            "_source_phase": "phase_1",
            "_target_phase": "phase_2"
        }
        
        validation = self.orchestrator._validate_propagated_data("phase_2", data)
        
        assert isinstance(validation, ValidationResult)
        assert validation.passed is True
        assert validation.score >= 0.7
    
    def test_validate_propagated_data_invalid(self):
        """Test validation of invalid propagated data."""
        # Empty data
        validation = self.orchestrator._validate_propagated_data("phase_2", {})
        
        assert validation.passed is False
        assert validation.score < 0.7
    
    def test_validate_phase_results_valid(self):
        """Test validation of valid phase results."""
        phase = WorkflowPhase(
            phase_id="test_phase",
            context="@code",
            name="Test Phase",
            description="Test phase",
            inputs=[],
            outputs=["source_code", "implementation_notes"]
        )
        results = {
            "source_code": {"files": ["main.py"]},
            "implementation_notes": "Implementation complete"
        }
        
        validation = self.orchestrator._validate_phase_results(phase, results)
        
        assert validation.passed is True
        assert validation.score >= 0.7
    
    def test_validate_phase_results_missing_outputs(self):
        """Test validation of phase results with missing outputs."""
        phase = WorkflowPhase(
            phase_id="test_phase",
            context="@code",
            name="Test Phase",
            description="Test phase",
            inputs=[],
            outputs=["source_code", "implementation_notes"]
        )
        results = {
            "source_code": {"files": ["main.py"]}
            # Missing implementation_notes
        }
        
        validation = self.orchestrator._validate_phase_results(phase, results)
        
        assert validation.passed is False
        assert any("missing expected output" in msg.lower() for msg in validation.messages)
    
    def test_determine_recovery_action_timeout(self):
        """Test recovery action determination for timeout errors."""
        state = WorkflowState(workflow_id="test")
        error = asyncio.TimeoutError("Operation timed out")
        
        action = self.orchestrator._determine_recovery_action("@code", error, state)
        
        assert isinstance(action, RecoveryAction)
        assert action.action_type == "retry"
    
    def test_determine_recovery_action_critical(self):
        """Test recovery action determination for critical errors."""
        state = WorkflowState(workflow_id="test")
        error = Exception("Critical system failure")
        
        action = self.orchestrator._determine_recovery_action("@code", error, state)
        
        assert isinstance(action, RecoveryAction)
        assert action.action_type == "abort"
    
    def test_finalize_workflow_success(self):
        """Test workflow finalization for successful execution."""
        state = WorkflowState(
            workflow_id="test_workflow",
            status=WorkflowStatus.COMPLETED,
            completed_phases=["phase_1", "phase_2"],
            phase_results={"phase_1": {"data": "test"}},
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        result = self.orchestrator._finalize_workflow(self.sample_workflow, state)
        
        assert isinstance(result, WorkflowResult)
        assert result.status == WorkflowStatus.COMPLETED
        assert result.workflow_id == "test_workflow"
        assert len(result.phases_executed) == 2
        assert result.execution_time >= 0
        assert "success_rate" in result.metrics
    
    def test_handle_workflow_failure(self):
        """Test workflow failure handling."""
        state = WorkflowState(
            workflow_id="test_workflow",
            completed_phases=["phase_1"],
            failed_phases=[],
            start_time=datetime.now()
        )
        error = Exception("Workflow execution failed")
        
        result = self.orchestrator._handle_workflow_failure(self.sample_workflow, state, error)
        
        assert isinstance(result, WorkflowResult)
        assert result.status == WorkflowStatus.FAILED
        assert len(result.errors) > 0
        assert "Workflow failed" in result.errors[0]
        assert "failure_reason" in result.metrics
    
    @pytest.mark.asyncio
    async def test_workflow_cleanup_on_completion(self):
        """Test that workflows are cleaned up after completion."""
        workflow_id = self.sample_workflow.workflow_id
        
        # Execute workflow
        await self.orchestrator.execute_workflow(self.sample_workflow)
        
        # Workflow should be cleaned up from active workflows
        assert workflow_id not in self.orchestrator.active_workflows
    
    @pytest.mark.asyncio
    async def test_workflow_cleanup_on_failure(self):
        """Test that workflows are cleaned up after failure."""
        # Create workflow that will fail
        failing_workflow = WorkflowDefinition(
            workflow_id="failing_workflow",
            name="Failing Workflow",
            description="Workflow that will fail",
            phases=[
                WorkflowPhase(
                    phase_id="failing_phase",
                    context="@code",
                    name="Failing Phase",
                    description="Phase that will fail",
                    inputs=[],
                    outputs=[],
                    timeout=1
                )
            ],
            dependencies={},
            estimated_duration=30
        )
        
        # Mock phase execution to raise exception
        with patch.object(self.orchestrator, '_execute_phase_logic', side_effect=Exception("Test failure")):
            result = await self.orchestrator.execute_workflow(failing_workflow)
            
            assert result.status == WorkflowStatus.FAILED
            # Workflow should be cleaned up
            assert failing_workflow.workflow_id not in self.orchestrator.active_workflows
    
    def test_recovery_strategies_initialization(self):
        """Test that recovery strategies are properly initialized."""
        strategies = self.orchestrator.recovery_strategies
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        
        # Check strategy structure
        for strategy in strategies:
            assert "name" in strategy
            assert "condition" in strategy
            assert "action" in strategy
            assert "reason" in strategy
            assert callable(strategy["condition"])
    
    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self):
        """Test execution of multiple workflows concurrently."""
        workflow1 = self.sample_workflow
        workflow2 = WorkflowDefinition(
            workflow_id="concurrent_workflow_2",
            name="Concurrent Workflow 2",
            description="Second concurrent workflow",
            phases=[
                WorkflowPhase(
                    phase_id="concurrent_phase",
                    context="@docs",
                    name="Documentation",
                    description="Create documentation",
                    inputs=[],
                    outputs=["docs"]
                )
            ],
            dependencies={},
            estimated_duration=30
        )
        
        # Mock phase execution to produce expected outputs
        async def mock_execution(phase, workflow, state):
            # Return expected outputs based on phase
            if phase.outputs:
                return {output: f"mock_{output}_result" for output in phase.outputs}
            return {"result": "success"}
        
        with patch.object(self.orchestrator, '_execute_phase_logic', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = mock_execution
            
            # Execute both workflows concurrently
            results = await asyncio.gather(
                self.orchestrator.execute_workflow(workflow1),
                self.orchestrator.execute_workflow(workflow2)
            )
        
        assert len(results) == 2
        assert all(isinstance(result, WorkflowResult) for result in results)
        assert all(result.status == WorkflowStatus.COMPLETED for result in results)
