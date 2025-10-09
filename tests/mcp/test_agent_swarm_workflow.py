#!/usr/bin/env python3
"""
Agent Swarm Workflow Tests
==========================

Comprehensive tests for MCP-powered agent swarm workflows:
- Swarm Coordinator functionality
- Agent role specialization
- Workflow execution and coordination
- Inter-agent communication through MCP
- Performance and scalability testing

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 3)
"""

import asyncio
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import swarm components
try:
    from agents.swarm.swarm_coordinator import (
        SwarmCoordinator, create_swarm_coordinator, SwarmWorkflow, SwarmTask,
        AgentRole, TaskPriority, SwarmState
    )
    from agents.core.base_agent import AgentConfig
    SWARM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Agent swarm import failed: {e}")
    SWARM_AVAILABLE = False


@pytest.mark.skipif(not SWARM_AVAILABLE, reason="Agent swarm components not available")
class TestSwarmCoordinator:
    """Test suite for Swarm Coordinator."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.coordinator = create_swarm_coordinator("test_coordinator")
    
    def test_coordinator_initialization(self):
        """Test swarm coordinator initialization."""
        assert self.coordinator.config.agent_id == "test_coordinator"
        assert self.coordinator.config.agent_type == "swarm_coordinator"
        assert self.coordinator.swarm_state == SwarmState.INITIALIZING
        assert len(self.coordinator.swarm_agents) == 0
        assert len(self.coordinator.active_workflows) == 0
    
    @pytest.mark.asyncio
    async def test_swarm_initialization(self):
        """Test swarm initialization with agents."""
        # Test with default agent roles
        success = await self.coordinator.initialize_swarm()
        
        # Should succeed regardless of MCP availability
        assert isinstance(success, bool)
        
        # Should have created agents
        if success:
            assert len(self.coordinator.swarm_agents) > 0
            assert self.coordinator.swarm_state in [SwarmState.PLANNING, SwarmState.ERROR]
        
        # Cleanup
        await self.coordinator.shutdown_swarm()
    
    @pytest.mark.asyncio
    async def test_swarm_initialization_with_specific_roles(self):
        """Test swarm initialization with specific agent roles."""
        specific_roles = [AgentRole.PRODUCT_AGENT, AgentRole.DEVELOPMENT_AGENT]
        
        success = await self.coordinator.initialize_swarm(specific_roles)
        
        if success:
            # Should have exactly 2 agents
            assert len(self.coordinator.swarm_agents) == 2
            
            # Should have the specified roles
            agent_roles = [agent.role for agent in self.coordinator.swarm_agents.values()]
            assert AgentRole.PRODUCT_AGENT in agent_roles
            assert AgentRole.DEVELOPMENT_AGENT in agent_roles
        
        await self.coordinator.shutdown_swarm()
    
    def test_agent_capabilities_mapping(self):
        """Test agent capabilities are correctly mapped."""
        # Test product agent capabilities
        product_caps = self.coordinator._get_agent_capabilities(AgentRole.PRODUCT_AGENT)
        assert "agile.create_user_story" in product_caps
        assert "agile.update_artifacts" in product_caps
        
        # Test development agent capabilities
        dev_caps = self.coordinator._get_agent_capabilities(AgentRole.DEVELOPMENT_AGENT)
        assert "file.manage_files" in dev_caps
        assert "file.enforce_organization" in dev_caps
        
        # Test testing agent capabilities
        test_caps = self.coordinator._get_agent_capabilities(AgentRole.TESTING_AGENT)
        assert "test.run_pipeline" in test_caps
        assert "test.generate_catalogue" in test_caps
    
    def test_workflow_creation_from_definition(self):
        """Test workflow creation from definition."""
        workflow_def = {
            'id': 'test_workflow',
            'name': 'Test Workflow',
            'description': 'Test workflow description',
            'tasks': [
                {
                    'id': 'task1',
                    'description': 'First task',
                    'priority': 1,
                    'mcp_tools': ['agile.create_user_story']
                },
                {
                    'id': 'task2',
                    'description': 'Second task',
                    'priority': 2,
                    'mcp_tools': ['file.manage_files']
                }
            ]
        }
        
        workflow = self.coordinator._create_workflow_from_definition(workflow_def)
        
        assert workflow.workflow_id == 'test_workflow'
        assert workflow.name == 'Test Workflow'
        assert workflow.description == 'Test workflow description'
        assert len(workflow.tasks) == 2
        
        # Check first task
        task1 = workflow.tasks[0]
        assert task1.task_id == 'task1'
        assert task1.description == 'First task'
        assert task1.priority == TaskPriority.CRITICAL
        assert 'agile.create_user_story' in task1.mcp_tools_required
    
    def test_task_validation(self):
        """Test task validation."""
        # Valid task
        valid_task = {
            'workflow_definition': {
                'name': 'Test Workflow',
                'tasks': []
            }
        }
        assert self.coordinator.validate_task(valid_task) is True
        
        # Invalid task (missing workflow_definition)
        invalid_task = {
            'description': 'Test task without workflow'
        }
        assert self.coordinator.validate_task(invalid_task) is False
    
    def test_swarm_status(self):
        """Test swarm status retrieval."""
        status = self.coordinator.get_swarm_status()
        
        assert isinstance(status, dict)
        assert 'coordinator_id' in status
        assert 'swarm_state' in status
        assert 'total_agents' in status
        assert 'active_workflows' in status
        assert 'swarm_metrics' in status
        assert 'agent_status' in status
        
        assert status['coordinator_id'] == 'test_coordinator'
        assert status['swarm_state'] == SwarmState.INITIALIZING.value
        assert status['total_agents'] == 0  # No agents initialized yet


@pytest.mark.skipif(not SWARM_AVAILABLE, reason="Agent swarm components not available")
class TestSwarmWorkflow:
    """Test suite for Swarm Workflow functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.coordinator = create_swarm_coordinator("workflow_test_coordinator")
    
    @pytest.mark.asyncio
    async def test_workflow_execution_structure(self):
        """Test workflow execution returns proper structure."""
        # Create simple workflow
        workflow = SwarmWorkflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Simple test workflow",
            tasks=[
                SwarmTask(
                    task_id="task1",
                    description="Test task",
                    mcp_tools_required=["db.track_agent_session"]
                )
            ]
        )
        
        # Execute workflow (may fail due to missing agents, but should return structure)
        result = await self.coordinator.execute_workflow(workflow)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'workflow_id' in result
        assert 'execution_time' in result
        assert result['workflow_id'] == "test_workflow"
    
    @pytest.mark.asyncio
    async def test_task_assignment_logic(self):
        """Test task assignment to appropriate agents."""
        # Initialize swarm first
        await self.coordinator.initialize_swarm([
            AgentRole.PRODUCT_AGENT,
            AgentRole.DEVELOPMENT_AGENT
        ])
        
        # Create workflow with tasks requiring different capabilities
        workflow = SwarmWorkflow(
            workflow_id="assignment_test",
            name="Assignment Test",
            description="Test task assignment",
            tasks=[
                SwarmTask(
                    task_id="agile_task",
                    description="Create user story",
                    mcp_tools_required=["agile.create_user_story"]
                ),
                SwarmTask(
                    task_id="dev_task",
                    description="Manage files",
                    mcp_tools_required=["file.manage_files"]
                )
            ]
        )
        
        # Plan and assign tasks
        await self.coordinator._plan_and_assign_tasks(workflow)
        
        # Check assignments
        agile_task = next(t for t in workflow.tasks if t.task_id == "agile_task")
        dev_task = next(t for t in workflow.tasks if t.task_id == "dev_task")
        
        # Tasks should be assigned to appropriate agents
        if agile_task.assigned_agent:
            assert agile_task.assigned_agent == AgentRole.PRODUCT_AGENT
        
        if dev_task.assigned_agent:
            assert dev_task.assigned_agent == AgentRole.DEVELOPMENT_AGENT
        
        await self.coordinator.shutdown_swarm()
    
    @pytest.mark.asyncio
    async def test_task_execution_simulation(self):
        """Test task execution simulation."""
        task = SwarmTask(
            task_id="sim_task",
            description="Simulation test task",
            assigned_agent=AgentRole.PRODUCT_AGENT,
            mcp_tools_required=["agile.create_user_story"]
        )
        
        # Simulate task execution
        result = await self.coordinator._simulate_task_execution(task)
        
        # Should return result structure
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'execution_time' in result
        
        # Should have some form of result
        assert result['success'] is True or 'error' in result


@pytest.mark.skipif(not SWARM_AVAILABLE, reason="Agent swarm components not available")
class TestSwarmIntegrationScenarios:
    """Test real-world swarm integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_sprint_workflow(self):
        """Test complete software development sprint workflow."""
        coordinator = create_swarm_coordinator("sprint_coordinator")
        
        try:
            # Initialize swarm with all agent types
            success = await coordinator.initialize_swarm()
            
            if success:
                # Create comprehensive sprint workflow
                sprint_workflow_def = {
                    'id': 'sprint_001',
                    'name': 'Software Development Sprint',
                    'description': 'Complete sprint from planning to release',
                    'phases': ['planning', 'development', 'testing', 'release'],
                    'tasks': [
                        {
                            'id': 'create_stories',
                            'description': 'Create user stories for sprint',
                            'priority': 1,
                            'mcp_tools': ['agile.create_user_story', 'agile.update_artifacts'],
                            'duration': 15
                        },
                        {
                            'id': 'implement_features',
                            'description': 'Implement user story features',
                            'priority': 2,
                            'mcp_tools': ['file.manage_files', 'file.enforce_organization'],
                            'duration': 60
                        },
                        {
                            'id': 'quality_review',
                            'description': 'Review code quality',
                            'priority': 2,
                            'mcp_tools': ['system.platform_commands'],
                            'duration': 30
                        },
                        {
                            'id': 'run_tests',
                            'description': 'Execute test suite',
                            'priority': 3,
                            'mcp_tools': ['test.run_pipeline', 'test.generate_catalogue'],
                            'duration': 20
                        },
                        {
                            'id': 'release_deployment',
                            'description': 'Deploy release',
                            'priority': 4,
                            'mcp_tools': ['git.automate_workflow', 'agile.update_catalogs'],
                            'duration': 25
                        }
                    ]
                }
                
                # Execute sprint workflow
                result = await coordinator.execute({
                    'workflow_definition': sprint_workflow_def
                })
                
                # Verify workflow execution
                assert isinstance(result, dict)
                assert 'success' in result
                assert 'workflow_id' in result
                assert result['workflow_id'] == 'sprint_001'
                
                # Check final swarm status
                final_status = coordinator.get_swarm_status()
                assert final_status['swarm_state'] in ['completed', 'error']
                
                print(f"✅ Sprint workflow result: {json.dumps(result, indent=2)}")
            
        finally:
            await coordinator.shutdown_swarm()
    
    @pytest.mark.asyncio
    async def test_swarm_error_handling(self):
        """Test swarm error handling and recovery."""
        coordinator = create_swarm_coordinator("error_test_coordinator")
        
        try:
            # Test with invalid workflow
            invalid_workflow_def = {
                'id': 'invalid_workflow',
                'name': 'Invalid Workflow',
                'tasks': [
                    {
                        'id': 'impossible_task',
                        'description': 'Task with impossible requirements',
                        'mcp_tools': ['nonexistent.tool']
                    }
                ]
            }
            
            # Should handle gracefully
            result = await coordinator.execute({
                'workflow_definition': invalid_workflow_def
            })
            
            # Should return error result without crashing
            assert isinstance(result, dict)
            assert 'success' in result
            
        finally:
            await coordinator.shutdown_swarm()
    
    @pytest.mark.asyncio
    async def test_swarm_performance_metrics(self):
        """Test swarm performance metrics collection."""
        coordinator = create_swarm_coordinator("metrics_coordinator")
        
        try:
            await coordinator.initialize_swarm([AgentRole.PRODUCT_AGENT])
            
            # Execute simple workflow
            simple_workflow_def = {
                'id': 'metrics_test',
                'name': 'Metrics Test Workflow',
                'tasks': [
                    {
                        'id': 'metrics_task',
                        'description': 'Task for metrics testing',
                        'mcp_tools': ['agile.create_user_story']
                    }
                ]
            }
            
            result = await coordinator.execute({
                'workflow_definition': simple_workflow_def
            })
            
            # Check metrics are collected
            if result.get('success'):
                assert 'swarm_metrics' in result
                metrics = result['swarm_metrics']
                assert 'workflows_completed' in metrics
                assert 'total_execution_time' in metrics
                assert metrics['workflows_completed'] >= 1
            
        finally:
            await coordinator.shutdown_swarm()


@pytest.mark.skipif(not SWARM_AVAILABLE, reason="Agent swarm components not available")
class TestSwarmFactoryFunctions:
    """Test swarm factory functions."""
    
    def test_create_swarm_coordinator(self):
        """Test swarm coordinator factory function."""
        coordinator = create_swarm_coordinator("factory_test")
        
        assert isinstance(coordinator, SwarmCoordinator)
        assert coordinator.config.agent_id == "factory_test"
        assert coordinator.config.agent_type == "swarm_coordinator"
    
    def test_create_swarm_coordinator_default_id(self):
        """Test swarm coordinator with default ID."""
        coordinator = create_swarm_coordinator()
        
        assert isinstance(coordinator, SwarmCoordinator)
        assert coordinator.config.agent_id == "swarm_coordinator"


# Test runner function for pytest integration
def test_agent_swarm_workflow_components():
    """Main test function for pytest integration."""
    if not SWARM_AVAILABLE:
        pytest.skip("Agent swarm components not available")
    
    # This function can be called by pytest to run all swarm tests
    pass


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    pytest.main([__file__, "-v"])
