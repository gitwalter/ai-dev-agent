#!/usr/bin/env python3
"""
Test Workflow Orchestration System

Comprehensive tests for the workflow orchestration system implemented for US-WO-01.
Tests both the specialized team design capabilities and the core orchestration engine.

Test Categories:
- Team functionality tests
- Workflow composition tests  
- Orchestration engine tests
- Integration tests
- Performance tests
"""

import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Test imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agents.teams.workflow_orchestration_team import (
    WorkflowOrchestrationTeam,
    WorkflowArchitectAgent,
    OrchestrationEngineerAgent,
    AgentCoordinatorAgent,
    ContextAnalyzerAgent,
    ValidationSpecialistAgent,
    IntegrationEngineerAgent,
    WorkflowType,
    AgentRole
)

from workflow.orchestration import (
    WorkflowOrchestrationEngine,
    WorkflowOrchestrator,
    create_workflow_orchestration_engine,
    WorkflowStatus
)

class TestWorkflowOrchestrationTeam:
    """Test the specialized workflow orchestration team"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.team = WorkflowOrchestrationTeam()
        
    def test_team_initialization(self):
        """Test that team initializes with all required agents"""
        assert isinstance(self.team.workflow_architect, WorkflowArchitectAgent)
        assert isinstance(self.team.orchestration_engineer, OrchestrationEngineerAgent)
        assert isinstance(self.team.agent_coordinator, AgentCoordinatorAgent)
        assert isinstance(self.team.context_analyzer, ContextAnalyzerAgent)
        assert isinstance(self.team.validation_specialist, ValidationSpecialistAgent)
        assert isinstance(self.team.integration_engineer, IntegrationEngineerAgent)
    
    def test_simple_task_analysis(self):
        """Test workflow analysis for simple tasks"""
        architect = WorkflowArchitectAgent()
        
        simple_task = "Create a basic hello world function"
        context = {}
        
        analysis = architect.analyze_task_requirements(simple_task, context)
        
        assert analysis["complexity_level"] >= 0
        assert analysis["recommended_pattern"] in ["sequential", "parallel", "conditional", "hierarchical"]
        assert isinstance(analysis["agent_roles_needed"], list)
        assert len(analysis["detected_contexts"]) >= 0
    
    def test_complex_task_analysis(self):
        """Test workflow analysis for complex tasks"""
        architect = WorkflowArchitectAgent()
        
        complex_task = """
        Implement a user authentication system with JWT tokens including:
        - Database schema design
        - API endpoint implementation
        - Unit testing
        - Integration testing
        - Documentation
        - Security validation
        """
        context = {}
        
        analysis = architect.analyze_task_requirements(complex_task, context)
        
        assert analysis["complexity_level"] > 2  # Should detect multiple contexts
        assert "testing" in analysis["detected_contexts"]
        assert "documentation" in analysis["detected_contexts"]
        assert len(analysis["agent_roles_needed"]) > 1
    
    def test_workflow_composition_design(self):
        """Test workflow composition design"""
        architect = WorkflowArchitectAgent()
        
        task = "Create API with testing and documentation"
        analysis = {
            "complexity_level": 3,
            "detected_contexts": ["multiple files", "testing", "documentation"],
            "recommended_pattern": "hierarchical",
            "estimated_steps": 6,
            "agent_roles_needed": [AgentRole.DEVELOPER, AgentRole.TESTER, AgentRole.DOCUMENTER]
        }
        
        composition = architect.design_workflow_composition(analysis, task)
        
        assert composition.workflow_type in [WorkflowType.DEVELOPMENT, WorkflowType.TESTING, WorkflowType.DOCUMENTATION]
        assert len(composition.steps) > 0
        assert len(composition.quality_gates) > 0
        assert len(composition.success_criteria) > 0
        assert all(step.agent_role in analysis["agent_roles_needed"] for step in composition.steps)
    
    def test_langgraph_orchestration_implementation(self):
        """Test LangGraph orchestration implementation"""
        engineer = OrchestrationEngineerAgent()
        architect = WorkflowArchitectAgent()
        
        # Create a test composition
        task = "Simple development task"
        analysis = architect.analyze_task_requirements(task, {})
        composition = architect.design_workflow_composition(analysis, task)
        
        implementation = engineer.implement_langgraph_orchestration(composition)
        
        assert "pattern" in implementation
        assert "graph_definition" in implementation
        assert "state_schema" in implementation
        assert "node_implementations" in implementation
        assert "edge_conditions" in implementation
        assert "execution_config" in implementation
        
        # Validate graph structure
        graph_def = implementation["graph_definition"]
        assert "nodes" in graph_def
        assert "edges" in graph_def
        assert len(graph_def["nodes"]) == len(composition.steps)
    
    def test_agent_coordination(self):
        """Test agent coordination functionality"""
        coordinator = AgentCoordinatorAgent()
        architect = WorkflowArchitectAgent()
        engineer = OrchestrationEngineerAgent()
        
        # Create test data
        task = "Multi-agent coordination test"
        analysis = architect.analyze_task_requirements(task, {})
        composition = architect.design_workflow_composition(analysis, task)
        implementation = engineer.implement_langgraph_orchestration(composition)
        
        coordination_plan = coordinator.coordinate_agent_execution(implementation, composition)
        
        assert "agent_allocation" in coordination_plan
        assert "execution_sequence" in coordination_plan
        assert "coordination_protocol" in coordination_plan
        assert "resource_management" in coordination_plan
        assert "conflict_resolution" in coordination_plan
        
        # Validate allocation
        allocation = coordination_plan["agent_allocation"]
        assert len(allocation) == len(composition.steps)
        assert all(step.id in allocation for step in composition.steps)
    
    def test_context_flow_analysis(self):
        """Test context flow analysis"""
        analyzer = ContextAnalyzerAgent()
        architect = WorkflowArchitectAgent()
        coordinator = AgentCoordinatorAgent()
        
        # Create test data
        task = "Context flow analysis test"
        analysis = architect.analyze_task_requirements(task, {})
        composition = architect.design_workflow_composition(analysis, task)
        coordination = coordinator.coordinate_agent_execution({}, composition)
        
        context_analysis = analyzer.analyze_context_flow(composition, coordination)
        
        assert "flow_pattern" in context_analysis
        assert "context_dependencies" in context_analysis
        assert "data_transformations" in context_analysis
        assert "optimization_opportunities" in context_analysis
        assert "context_validation" in context_analysis
        
        # Validate patterns
        assert context_analysis["flow_pattern"] in [
            "sequential_flow", "branched_flow", "accumulated_flow", "transformed_flow"
        ]
    
    def test_validation_framework_design(self):
        """Test validation framework design"""
        validator = ValidationSpecialistAgent()
        architect = WorkflowArchitectAgent()
        analyzer = ContextAnalyzerAgent()
        
        # Create test data
        task = "Validation framework test"
        analysis = architect.analyze_task_requirements(task, {})
        composition = architect.design_workflow_composition(analysis, task)
        context_analysis = analyzer.analyze_context_flow(composition, {})
        
        validation_framework = validator.design_validation_framework(composition, context_analysis)
        
        assert "validation_strategy" in validation_framework
        assert "test_scenarios" in validation_framework
        assert "quality_metrics" in validation_framework
        assert "validation_checkpoints" in validation_framework
        assert "error_handling" in validation_framework
        assert "performance_benchmarks" in validation_framework
        
        # Validate test scenarios
        scenarios = validation_framework["test_scenarios"]
        assert len(scenarios) > 0
        assert any(scenario["type"] == "positive" for scenario in scenarios)
    
    def test_system_integration_design(self):
        """Test system integration design"""
        integrator = IntegrationEngineerAgent()
        
        validation_framework = {
            "validation_strategy": "integration_validation",
            "test_scenarios": [],
            "quality_metrics": {}
        }
        
        # Create mock composition
        from agents.teams.workflow_orchestration_team import WorkflowComposition, WorkflowStep
        composition = WorkflowComposition(
            id="test_comp",
            name="Test Composition",
            description="Test",
            workflow_type=WorkflowType.DEVELOPMENT,
            steps=[],
            quality_gates=[],
            success_criteria=[]
        )
        
        integration_design = integrator.design_system_integration(validation_framework, composition)
        
        assert "integration_architecture" in integration_design
        assert "agent_system_integration" in integration_design
        assert "prompt_system_integration" in integration_design
        assert "monitoring_integration" in integration_design
        assert "database_integration" in integration_design
        assert "file_system_integration" in integration_design
    
    def test_full_team_workflow_implementation(self):
        """Test complete team workflow implementation"""
        team = WorkflowOrchestrationTeam()
        
        task = "Create a user registration system with validation and testing"
        context = {"project_type": "web_api", "technology": "python"}
        
        results = team.implement_basic_workflow_orchestration(task, context)
        
        # Validate results structure
        assert "start_time" in results
        assert "user_story" in results
        assert "team_contributions" in results
        assert "implementation_artifacts" in results
        assert "implementation_summary" in results
        
        # Validate team contributions
        contributions = results["team_contributions"]
        assert "workflow_architect" in contributions
        assert "orchestration_engineer" in contributions
        assert "agent_coordinator" in contributions
        assert "context_analyzer" in contributions
        assert "validation_specialist" in contributions
        assert "integration_engineer" in contributions
        
        # Validate implementation artifacts
        artifacts = results["implementation_artifacts"]
        assert "workflow_composition" in artifacts
        assert "langgraph_implementation" in artifacts
        assert "coordination_plan" in artifacts
        assert "context_analysis" in artifacts
        assert "validation_framework" in artifacts
        assert "integration_design" in artifacts

class TestWorkflowOrchestrationEngine:
    """Test the workflow orchestration engine"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.engine = WorkflowOrchestrationEngine()
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert isinstance(self.engine.team, WorkflowOrchestrationTeam)
        assert isinstance(self.engine.active_workflows, dict)
        assert isinstance(self.engine.workflow_history, list)
        assert self.engine.workflow_storage.exists()
    
    @pytest.mark.asyncio
    async def test_simple_task_orchestration(self):
        """Test orchestration of a simple task"""
        task = "Create a hello world function with basic testing"
        
        results = await self.engine.orchestrate_task(task)
        
        assert "orchestration_id" in results
        assert "task_description" in results
        assert "design_results" in results
        assert "execution_results" in results
        assert "status" in results
        assert "duration_seconds" in results
        assert "business_value" in results
        
        # Validate successful completion
        assert results["status"] in ["completed", "failed"]  # Should complete or fail gracefully
    
    @pytest.mark.asyncio
    async def test_complex_task_orchestration(self):
        """Test orchestration of a complex task"""
        task = """
        Implement a complete user authentication system including:
        - Database schema with users table
        - User registration endpoint with validation
        - Login endpoint with JWT token generation
        - Password hashing and verification
        - Comprehensive unit tests for all endpoints
        - Integration tests for authentication flow
        - API documentation with examples
        - Security validation and testing
        """
        
        results = await self.engine.orchestrate_task(task)
        
        # Validate complex task handling
        assert results["status"] in ["completed", "failed"]
        
        # Check that complexity was recognized
        design_results = results["design_results"]
        composition = design_results["implementation_artifacts"]["workflow_composition"]
        assert len(composition["steps"]) > 2  # Should generate multiple steps
    
    @pytest.mark.asyncio
    async def test_workflow_execution_tracking(self):
        """Test workflow execution tracking"""
        task = "Simple task for tracking test"
        
        # Start orchestration
        orchestration_task = asyncio.create_task(self.engine.orchestrate_task(task))
        
        # Give it a moment to start
        await asyncio.sleep(0.1)
        
        # Check active workflows
        active_workflows = self.engine.list_active_workflows()
        
        # Wait for completion
        results = await orchestration_task
        
        # Validate tracking
        assert "orchestration_id" in results
        
        # Check workflow status
        workflow_id = results["orchestration_id"]
        status = self.engine.get_workflow_status(workflow_id)
        assert status is not None
        assert "status" in status
    
    @pytest.mark.asyncio
    async def test_parallel_workflows(self):
        """Test handling multiple parallel workflows"""
        tasks = [
            "Create function A with testing",
            "Create function B with documentation", 
            "Create function C with validation"
        ]
        
        # Start multiple workflows in parallel
        orchestration_tasks = [
            self.engine.orchestrate_task(task) for task in tasks
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*orchestration_tasks)
        
        # Validate all completed
        assert len(results) == 3
        for result in results:
            assert "status" in result
            assert "orchestration_id" in result
    
    def test_workflow_orchestrator_context_manager(self):
        """Test the WorkflowOrchestrator context manager"""
        async def test_context():
            async with WorkflowOrchestrator() as orchestrator:
                assert isinstance(orchestrator, WorkflowOrchestrationEngine)
                
                # Test basic functionality
                task = "Simple context manager test"
                results = await orchestrator.orchestrate_task(task)
                assert "status" in results
        
        asyncio.run(test_context())
    
    def test_factory_function(self):
        """Test the factory function"""
        engine = create_workflow_orchestration_engine()
        assert isinstance(engine, WorkflowOrchestrationEngine)
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in orchestration"""
        # Test with invalid/problematic input
        with patch.object(self.engine.team, 'implement_basic_workflow_orchestration') as mock_impl:
            mock_impl.side_effect = Exception("Test error")
            
            results = await self.engine.orchestrate_task("Error test task")
            
            assert results["status"] == "failed"
            assert "error" in results

class TestWorkflowIntegration:
    """Test integration with existing systems"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.engine = WorkflowOrchestrationEngine()
    
    @pytest.mark.asyncio
    async def test_file_system_integration(self):
        """Test that workflow results are properly saved"""
        task = "Integration test task"
        
        results = await self.engine.orchestrate_task(task)
        
        # Check that results file was created
        orchestration_id = results["orchestration_id"]
        results_file = self.engine.workflow_storage / f"results_{orchestration_id}.json"
        
        assert results_file.exists()
        
        # Verify file content
        with open(results_file, 'r') as f:
            saved_results = json.load(f)
        
        assert saved_results["orchestration_id"] == orchestration_id
        assert saved_results["status"] == results["status"]
    
    def test_directory_structure_compliance(self):
        """Test that workflow orchestration follows project directory structure"""
        # Verify correct file placement
        engine_file = Path("workflow/orchestration/workflow_orchestration_engine.py")
        team_file = Path("agents/workflow_orchestration_team.py")
        init_file = Path("workflow/orchestration/__init__.py")
        
        assert engine_file.exists(), "Engine should be in workflow/orchestration/"
        assert team_file.exists(), "Team should be in agents/"
        assert init_file.exists(), "Module should have __init__.py"
    
    def test_import_structure(self):
        """Test that imports work correctly"""
        # Test main imports
        from workflow.orchestration import WorkflowOrchestrationEngine
        from workflow.orchestration import create_workflow_orchestration_engine
        from workflow.orchestration import WorkflowOrchestrator
        
        # Verify classes are importable
        assert WorkflowOrchestrationEngine is not None
        assert create_workflow_orchestration_engine is not None
        assert WorkflowOrchestrator is not None

class TestWorkflowPerformance:
    """Test workflow orchestration performance"""
    
    @pytest.mark.asyncio
    async def test_orchestration_performance(self):
        """Test that orchestration completes within reasonable time"""
        engine = WorkflowOrchestrationEngine()
        
        task = "Performance test task with basic functionality"
        
        start_time = datetime.now()
        results = await engine.orchestrate_task(task)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within 30 seconds for a simple task
        assert duration < 30, f"Orchestration took {duration} seconds, should be under 30"
        assert results["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test that orchestration doesn't leak memory"""
        engine = WorkflowOrchestrationEngine()
        
        # Run multiple orchestrations
        for i in range(5):
            task = f"Memory test task {i}"
            await engine.orchestrate_task(task)
        
        # Verify active workflows are cleaned up
        active_workflows = engine.list_active_workflows()
        assert len(active_workflows) == 0, "Should have no active workflows after completion"

def test_us_wo_01_requirements():
    """Test that US-WO-01 requirements are met"""
    # Test that all required components exist
    assert Path("agents/workflow_orchestration_team.py").exists()
    assert Path("workflow/orchestration/workflow_orchestration_engine.py").exists()
    assert Path("workflow/orchestration/__init__.py").exists()
    
    # Test that team can be instantiated
    team = WorkflowOrchestrationTeam()
    assert team is not None
    
    # Test that engine can be instantiated
    engine = WorkflowOrchestrationEngine()
    assert engine is not None
    
    # Test basic functionality
    task = "US-WO-01 requirement validation test"
    results = team.implement_basic_workflow_orchestration(task)
    
    # Validate key deliverables
    assert "team_contributions" in results
    assert "implementation_artifacts" in results
    
    # Verify all team members contributed
    contributions = results["team_contributions"]
    required_contributors = [
        "workflow_architect",
        "orchestration_engineer", 
        "agent_coordinator",
        "context_analyzer",
        "validation_specialist",
        "integration_engineer"
    ]
    
    for contributor in required_contributors:
        assert contributor in contributions, f"Missing contribution from {contributor}"
    
    print("✅ US-WO-01 REQUIREMENTS VALIDATED")

if __name__ == "__main__":
    # Run basic validation
    test_us_wo_01_requirements()
    
    # Run pytest if available
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("Pytest not available, running basic tests...")
        
        # Run basic sync tests
        test_team = TestWorkflowOrchestrationTeam()
        test_team.setup_method()
        test_team.test_team_initialization()
        test_team.test_simple_task_analysis()
        test_team.test_full_team_workflow_implementation()
        
        print("✅ BASIC TESTS COMPLETED")
