#!/usr/bin/env python3
"""
Tests for Project Manager Supervisor.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from agents.supervisor.project_manager_supervisor import ProjectManagerSupervisor
from agents.supervisor.base_supervisor import SupervisorConfig
from models.supervisor_state import Task, TaskResult, Escalation


class TestProjectManagerSupervisor:
    """Tests for ProjectManagerSupervisor."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock = Mock()
        mock.ainvoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def supervisor_config(self):
        """Create a supervisor config."""
        return SupervisorConfig(
            quality_thresholds={
                "requirements": 0.8,
                "architecture": 0.8,
                "code": 0.7,
                "tests": 0.7,
                "review": 0.8,
                "security": 0.9,
                "documentation": 0.7
            }
        )
    
    @pytest.fixture
    def project_manager(self, mock_llm, supervisor_config):
        """Create a project manager supervisor instance."""
        return ProjectManagerSupervisor(mock_llm, supervisor_config)
    
    def test_project_manager_initialization(self, project_manager, mock_llm, supervisor_config):
        """Test project manager initialization."""
        assert project_manager.llm == mock_llm
        assert project_manager.config == supervisor_config
        assert project_manager.worker_agents == {}
        assert project_manager.task_queue == []
        assert project_manager.active_tasks == {}
        assert project_manager.logger is not None
    
    @pytest.mark.asyncio
    async def test_initialize_project_state(self, project_manager):
        """Test project state initialization."""
        project_context = "Create a web application"
        
        state = await project_manager._initialize_project_state(project_context)
        
        assert state["project_context"] == project_context
        assert state["project_name"].startswith("project_")
        assert state["session_id"].startswith("session_")
        assert state["current_phase"] == "started"
        assert state["requirements"] == []
        assert state["architecture"] == {}
        assert state["supervisor_decisions"] == []
    
    @pytest.mark.asyncio
    async def test_create_default_tasks(self, project_manager):
        """Test default task creation."""
        project_context = "Create a web application"
        
        tasks = project_manager._create_default_tasks(project_context)
        
        assert len(tasks) == 7
        
        # Check task types
        task_types = [task.task_name for task in tasks]
        expected_types = [
            "requirements_analysis", "architecture_design", "code_generation",
            "test_generation", "code_review", "security_analysis", "documentation_generation"
        ]
        assert task_types == expected_types
        
        # Check task properties
        for task in tasks:
            assert task.task_id.startswith("task_")
            assert len(task.description) > 0
            assert task.priority in ["low", "medium", "high", "critical"]
            assert task.estimated_complexity in ["simple", "moderate", "complex"]
            assert isinstance(task.quality_criteria, dict)
    
    @pytest.mark.asyncio
    async def test_prioritize_tasks(self, project_manager):
        """Test task prioritization."""
        tasks = [
            Task(
                task_id="task_1",
                task_name="requirements_analysis",
                description="Test task 1",
                priority="low",
                dependencies=[]
            ),
            Task(
                task_id="task_2",
                task_name="architecture_design",
                description="Test task 2",
                priority="high",
                dependencies=[]
            ),
            Task(
                task_id="task_3",
                task_name="code_generation",
                description="Test task 3",
                priority="critical",
                dependencies=[]
            )
        ]
        
        prioritized = await project_manager._prioritize_tasks(tasks)
        
        # Critical should come first, then high, then low
        assert prioritized[0].priority == "critical"
        assert prioritized[1].priority == "high"
        assert prioritized[2].priority == "low"
    
    @pytest.mark.asyncio
    async def test_select_worker_for_task(self, project_manager):
        """Test worker selection for tasks."""
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task"
        )
        
        worker = await project_manager._select_worker_for_task(task)
        assert worker == "requirements_analyst"
        
        # Test unknown task type
        task.task_name = "unknown_task"
        worker = await project_manager._select_worker_for_task(task)
        assert worker == "general_worker"
    
    @pytest.mark.asyncio
    async def test_create_task_prompt(self, project_manager):
        """Test task prompt creation."""
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Analyze requirements",
            priority="high",
            estimated_complexity="moderate",
            requirements={"framework": "flask"},
            quality_criteria={"completeness": 0.8}
        )
        
        prompt = await project_manager._create_task_prompt(task, "requirements_analyst")
        
        assert "Analyze requirements" in prompt
        assert "requirements_analysis" in prompt
        assert "high" in prompt
        assert "moderate" in prompt
        assert "requirements_analyst" in prompt
    
    @pytest.mark.asyncio
    async def test_execute_task(self, project_manager):
        """Test task execution."""
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task"
        )
        
        result = await project_manager._execute_task(task, "requirements_analyst", "test prompt")
        
        assert result["task_id"] == "task_1"
        assert result["worker"] == "requirements_analyst"
        assert "Mock result for requirements_analysis" in result["result"]
        assert result["status"] == "completed"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_delegate_task_success(self, project_manager):
        """Test successful task delegation."""
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task"
        )
        
        result = await project_manager.delegate_task(task, "requirements_analyst")
        
        assert isinstance(result, TaskResult)
        assert result.task_id == "task_1"
        assert result.success == True
        assert result.result_data != {}
        assert len(project_manager.decision_history) == 1
        assert project_manager.decision_history[0]["decision"]["action"] == "task_delegation"
    
    @pytest.mark.asyncio
    async def test_delegate_task_failure(self, project_manager):
        """Test task delegation failure."""
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task"
        )
        
        # Mock task execution to fail
        with patch.object(project_manager, '_execute_task', side_effect=Exception("Task failed")):
            result = await project_manager.delegate_task(task, "requirements_analyst")
        
        assert result.success == False
        assert result.error_message is not None
        assert "Task failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_update_state_with_task_result(self, project_manager):
        """Test state update with task result."""
        from models.supervisor_state import create_initial_supervisor_swarm_state
        
        state = create_initial_supervisor_swarm_state("Test project", "test_project", "test_session")
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task"
        )
        result = TaskResult(
            task_id="task_1",
            success=True,
            result_data={"requirements": [{"id": "req1", "description": "User authentication"}]},
            execution_time=5.2
        )
        
        updated_state = project_manager._update_state_with_task_result(state, task, result)
        
        # Check execution history
        assert len(updated_state["execution_history"]) == 1
        assert updated_state["execution_history"][0]["step"] == "requirements_analysis"
        assert updated_state["execution_history"][0]["agent"] == "requirements_analyst"
        
        # Check agent outputs
        assert "requirements_analyst" in updated_state["agent_outputs"]
        
        # Check requirements
        assert len(updated_state["requirements"]) == 1
        assert updated_state["requirements"][0]["id"] == "req1"
    
    @pytest.mark.asyncio
    async def test_analyze_escalation_success(self, project_manager, mock_llm):
        """Test successful escalation analysis."""
        escalation = Escalation(
            escalation_id="esc_1",
            task_id="task_1",
            reason="Unclear requirements",
            level="high"
        )
        
        mock_llm.ainvoke.return_value = "Analysis: Requirements are unclear"
        
        analysis = await project_manager._analyze_escalation(escalation)
        
        assert "analysis" in analysis
        assert "Analysis: Requirements are unclear" in analysis["analysis"]
        assert analysis["escalation_id"] == "esc_1"
        assert "timestamp" in analysis
    
    @pytest.mark.asyncio
    async def test_analyze_escalation_failure(self, project_manager, mock_llm):
        """Test escalation analysis failure."""
        escalation = Escalation(
            escalation_id="esc_1",
            task_id="task_1",
            reason="Unclear requirements",
            level="high"
        )
        
        mock_llm.ainvoke.side_effect = Exception("LLM failed")
        
        analysis = await project_manager._analyze_escalation(escalation)
        
        assert analysis["analysis"] == "Unable to analyze escalation"
        assert "error" in analysis
        assert "LLM failed" in analysis["error"]
    
    @pytest.mark.asyncio
    async def test_determine_resolution_strategy_success(self, project_manager, mock_llm):
        """Test successful resolution strategy determination."""
        analysis = {
            "analysis": "Root cause: unclear requirements",
            "escalation_id": "esc_1"
        }
        
        mock_llm.ainvoke.return_value = "Strategy: Clarify requirements"
        
        strategy = await project_manager._determine_resolution_strategy(analysis)
        
        assert "strategy" in strategy
        assert "Strategy: Clarify requirements" in strategy["strategy"]
        assert strategy["analysis_id"] == "esc_1"
        assert "timestamp" in strategy
    
    @pytest.mark.asyncio
    async def test_determine_resolution_strategy_failure(self, project_manager, mock_llm):
        """Test resolution strategy determination failure."""
        analysis = {
            "analysis": "Root cause: unclear requirements",
            "escalation_id": "esc_1"
        }
        
        mock_llm.ainvoke.side_effect = Exception("LLM failed")
        
        strategy = await project_manager._determine_resolution_strategy(analysis)
        
        assert strategy["strategy"] == "Standard escalation resolution"
        assert "error" in strategy
        assert "LLM failed" in strategy["error"]
    
    @pytest.mark.asyncio
    async def test_execute_resolution(self, project_manager):
        """Test resolution execution."""
        resolution = {
            "strategy": "Clarify requirements",
            "analysis_id": "esc_1"
        }
        
        result = await project_manager._execute_resolution(resolution)
        
        assert result["status"] == "resolved"
        assert result["resolution"] == resolution
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_handle_escalation_success(self, project_manager, mock_llm):
        """Test successful escalation handling."""
        escalation = Escalation(
            escalation_id="esc_1",
            task_id="task_1",
            reason="Unclear requirements",
            level="high"
        )
        
        mock_llm.ainvoke.side_effect = [
            "Analysis: Requirements are unclear",
            "Strategy: Clarify requirements"
        ]
        
        result = await project_manager.handle_escalation(escalation)
        
        assert result["status"] == "resolved"
        assert "resolution" in result
        assert len(project_manager.decision_history) == 1
        assert project_manager.decision_history[0]["decision"]["action"] == "escalation_handling"
    
    @pytest.mark.asyncio
    async def test_handle_escalation_failure(self, project_manager, mock_llm):
        """Test escalation handling failure."""
        escalation = Escalation(
            escalation_id="esc_1",
            task_id="task_1",
            reason="Unclear requirements",
            level="high"
        )
        
        mock_llm.ainvoke.side_effect = Exception("LLM failed")
        
        result = await project_manager.handle_escalation(escalation)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert "LLM failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_task_breakdown_success(self, project_manager, mock_llm):
        """Test successful task breakdown creation."""
        project_context = "Create a web application"
        
        mock_llm.ainvoke.return_value = "Task breakdown response"
        
        tasks = await project_manager._create_task_breakdown(project_context)
        
        assert len(tasks) == 7  # Should return default tasks
        assert all(isinstance(task, Task) for task in tasks)
    
    @pytest.mark.asyncio
    async def test_create_task_breakdown_failure(self, project_manager, mock_llm):
        """Test task breakdown creation failure."""
        project_context = "Create a web application"
        
        mock_llm.ainvoke.side_effect = Exception("LLM failed")
        
        tasks = await project_manager._create_task_breakdown(project_context)
        
        assert len(tasks) == 7  # Should return default tasks as fallback
        assert all(isinstance(task, Task) for task in tasks)
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, project_manager):
        """Test successful workflow execution."""
        from models.supervisor_state import create_initial_supervisor_swarm_state
        
        # Create test tasks
        tasks = [
            Task(
                task_id="task_1",
                task_name="requirements_analysis",
                description="Test task 1",
                priority="high"
            ),
            Task(
                task_id="task_2",
                task_name="architecture_design",
                description="Test task 2",
                priority="high"
            )
        ]
        project_manager.task_queue = tasks
        
        initial_state = create_initial_supervisor_swarm_state("Test project", "test_project", "test_session")
        
        result = await project_manager._execute_workflow(initial_state)
        
        assert result["status"] == "completed"
        assert result["tasks_executed"] == 2
        assert "timestamp" in result
        assert "state" in result
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_failure(self, project_manager):
        """Test workflow execution with task failure."""
        from models.supervisor_state import create_initial_supervisor_swarm_state
        
        # Create test task that will fail
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task",
            priority="high"
        )
        project_manager.task_queue = [task]
        
        # Mock delegate_task to return failed result
        failed_result = TaskResult(
            task_id="task_1",
            success=False,
            result_data={"error": "Task failed"},
            error_message="Task failed"
        )
        
        with patch.object(project_manager, 'delegate_task', return_value=failed_result):
            with patch.object(project_manager, 'handle_escalation') as mock_handle:
                initial_state = create_initial_supervisor_swarm_state("Test project", "test_project", "test_session")
                result = await project_manager._execute_workflow(initial_state)
        
        assert result["status"] == "completed"  # Workflow completes even with failures
        assert mock_handle.called  # Escalation should be handled
    
    @pytest.mark.asyncio
    async def test_execute_workflow_exception(self, project_manager):
        """Test workflow execution with exception."""
        from models.supervisor_state import create_initial_supervisor_swarm_state
        
        # Create test task so the workflow has something to execute
        task = Task(
            task_id="task_1",
            task_name="requirements_analysis",
            description="Test task",
            priority="high"
        )
        project_manager.task_queue = [task]
        
        initial_state = create_initial_supervisor_swarm_state("Test project", "test_project", "test_session")
        
        # Mock delegate_task to raise exception
        with patch.object(project_manager, 'delegate_task', side_effect=Exception("Workflow failed")):
            result = await project_manager._execute_workflow(initial_state)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert "Workflow failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_orchestrate_workflow_success(self, project_manager):
        """Test successful workflow orchestration."""
        project_context = "Create a web application"
        
        # Mock internal methods
        with patch.object(project_manager, '_initialize_project_state') as mock_init:
            with patch.object(project_manager, '_create_task_breakdown') as mock_breakdown:
                with patch.object(project_manager, '_prioritize_tasks') as mock_prioritize:
                    with patch.object(project_manager, '_execute_workflow') as mock_execute:
                        
                        mock_init.return_value = {"project_context": project_context}
                        mock_breakdown.return_value = [Task(task_id="task_1", task_name="test", description="test")]
                        mock_prioritize.return_value = [Task(task_id="task_1", task_name="test", description="test")]
                        mock_execute.return_value = {"status": "completed"}
                        
                        result = await project_manager.orchestrate_workflow(project_context)
        
        assert result["status"] == "completed"
        assert mock_init.called
        assert mock_breakdown.called
        assert mock_prioritize.called
        assert mock_execute.called
    
    @pytest.mark.asyncio
    async def test_orchestrate_workflow_failure(self, project_manager):
        """Test workflow orchestration failure."""
        project_context = "Create a web application"
        
        # Mock internal method to raise exception
        with patch.object(project_manager, '_initialize_project_state', side_effect=Exception("Orchestration failed")):
            result = await project_manager.orchestrate_workflow(project_context)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert "Orchestration failed" in result["error"]


class TestProjectManagerIntegration:
    """Integration tests for ProjectManagerSupervisor."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock = Mock()
        mock.ainvoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def supervisor_config(self):
        """Create a supervisor config."""
        return SupervisorConfig(
            quality_thresholds={
                "requirements": 0.8,
                "architecture": 0.8,
                "code": 0.7,
                "tests": 0.7,
                "review": 0.8,
                "security": 0.9,
                "documentation": 0.7
            }
        )
    
    @pytest.fixture
    def project_manager(self, mock_llm, supervisor_config):
        """Create a project manager supervisor instance."""
        return ProjectManagerSupervisor(mock_llm, supervisor_config)
    
    @pytest.mark.asyncio
    async def test_complete_workflow_orchestration(self, project_manager, mock_llm):
        """Test complete workflow orchestration."""
        project_context = "Create a simple web application with user authentication"
        
        # Mock LLM responses
        mock_llm.ainvoke.side_effect = [
            "Analysis: Requirements are clear",
            "Strategy: Proceed with development"
        ]
        
        result = await project_manager.orchestrate_workflow(project_context)
        
        assert result["status"] == "completed"
        assert "tasks_executed" in result
        assert result["tasks_executed"] > 0
        assert "state" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_decision_logging_integration(self, project_manager):
        """Test that decisions are properly logged throughout the workflow."""
        project_context = "Create a web application"
        
        # Execute a simple workflow
        result = await project_manager.orchestrate_workflow(project_context)
        
        # Check that decisions were logged
        assert len(project_manager.decision_history) > 0
        
        # Check decision structure
        for decision in project_manager.decision_history:
            assert "timestamp" in decision
            assert "decision" in decision
            assert "context" in decision
            assert "action" in decision["decision"]
    
    @pytest.mark.asyncio
    async def test_state_management_integration(self, project_manager):
        """Test that state is properly managed throughout the workflow."""
        project_context = "Create a web application"
        
        result = await project_manager.orchestrate_workflow(project_context)
        
        state = result["state"]
        
        # Check that state was properly updated
        assert state["project_context"] == project_context
        assert len(state["execution_history"]) > 0
        assert len(state["agent_outputs"]) > 0
        
        # Check execution history structure
        for entry in state["execution_history"]:
            assert "step" in entry
            assert "agent" in entry
            assert "timestamp" in entry
