"""
Test Agent System

Comprehensive tests for the agent system including base agent, factory,
manager, and specialized agents.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

from agents import (
    BaseAgent, AgentConfig, AgentFactory, AgentManager,
    RequirementsAnalyst, get_agent_manager, execute_task,
    analyze_requirements, get_system_status
)
from agents.core.agent_manager import AgentPerformanceMonitor, AgentConfigManager
from models.state import AgentState

class TestAgentConfig:
    """Test AgentConfig dataclass."""
    
    def test_agent_config_creation(self):
        """Test creating an AgentConfig instance."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        assert config.agent_id == "test_agent"
        assert config.agent_type == "test_type"
        assert config.prompt_template_id == "test_template"
        assert config.optimization_enabled is True
        assert config.performance_monitoring is True
        assert config.max_retries == 3
        assert config.timeout_seconds == 30

class TestAgentState:
    """Test AgentState dataclass."""
    
    def test_agent_state_creation(self):
        """Test creating an AgentState instance."""
        from datetime import datetime
        
        state = AgentState(
            project_context="test context",
            project_name="test project",
            requirements=[],
            user_stories=[],
            architecture={},
            tech_stack={},
            database_schema={},
            code_files={},
            tests={},
            documentation={},
            configuration_files={},
            current_task="test_task",
            current_agent="test_agent",
            agent_outputs={},
            workflow_history=[],
            human_approval_needed=False,
            approval_requests=[],
            human_feedback={},
            errors=[],
            warnings=[],
            retry_count=0,
            memory_context="",
            memory_query="",
            memory_timestamp="",
            recall_memories=[],
            knowledge_triples=[],
            memory_stats={},
            handoff_queue=[],
            handoff_history=[],
            agent_availability={},
            collaboration_context={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            session_id="test_session"
        )
        
        assert state["current_agent"] == "test_agent"
        assert state["current_task"] == "test_task"
        assert state["project_name"] == "test project"
        assert state["human_approval_needed"] is False

class TestAgentFactory:
    """Test AgentFactory class."""
    
    def test_factory_initialization(self):
        """Test factory initialization."""
        factory = AgentFactory()
        
        assert factory.agent_registry == {}
        assert factory.active_agents == {}
    
    def test_register_agent_type(self):
        """Test registering an agent type."""
        factory = AgentFactory()
        
        class TestAgent(BaseAgent):
            async def execute(self, task):
                return {"success": True}
            
            def validate_task(self, task):
                return True
        
        factory.register_agent_type("test_type", TestAgent)
        
        assert "test_type" in factory.agent_registry
        assert factory.agent_registry["test_type"] == TestAgent
    
    def test_create_agent(self):
        """Test creating an agent instance."""
        factory = AgentFactory()
        
        class TestAgent(BaseAgent):
            async def execute(self, task):
                return {"success": True}
            
            def validate_task(self, task):
                return True
        
        factory.register_agent_type("test_type", TestAgent)
        
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        agent = factory.create_agent("test_type", config)
        
        assert isinstance(agent, TestAgent)
        assert agent.config.agent_id == "test_agent"
        assert "test_agent" in factory.active_agents
    
    def test_create_unknown_agent_type(self):
        """Test creating an agent with unknown type."""
        factory = AgentFactory()
        
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="unknown_type",
            prompt_template_id="test_template"
        )
        
        with pytest.raises(ValueError, match="Unknown agent type"):
            factory.create_agent("unknown_type", config)
    
    def test_get_agent(self):
        """Test getting an agent by ID."""
        factory = AgentFactory()
        
        class TestAgent(BaseAgent):
            async def execute(self, task):
                return {"success": True}
            
            def validate_task(self, task):
                return True
        
        factory.register_agent_type("test_type", TestAgent)
        
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        created_agent = factory.create_agent("test_type", config)
        retrieved_agent = factory.get_agent("test_agent")
        
        assert retrieved_agent is created_agent
    
    def test_list_agents(self):
        """Test listing active agents."""
        factory = AgentFactory()
        
        class TestAgent(BaseAgent):
            async def execute(self, task):
                return {"success": True}
            
            def validate_task(self, task):
                return True
        
        factory.register_agent_type("test_type", TestAgent)
        
        config1 = AgentConfig(
            agent_id="agent1",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        config2 = AgentConfig(
            agent_id="agent2",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        factory.create_agent("test_type", config1)
        factory.create_agent("test_type", config2)
        
        agent_list = factory.list_agents()
        
        assert "agent1" in agent_list
        assert "agent2" in agent_list
        assert len(agent_list) == 2
    
    def test_shutdown_agent(self):
        """Test shutting down an agent."""
        factory = AgentFactory()
        
        class TestAgent(BaseAgent):
            async def execute(self, task):
                return {"success": True}
            
            def validate_task(self, task):
                return True
        
        factory.register_agent_type("test_type", TestAgent)
        
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        factory.create_agent("test_type", config)
        
        assert "test_agent" in factory.active_agents
        
        result = factory.shutdown_agent("test_agent")
        
        assert result is True
        assert "test_agent" not in factory.active_agents

class TestAgentManager:
    """Test AgentManager class."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = AgentManager()
        
        assert isinstance(manager.factory, AgentFactory)
        assert isinstance(manager.performance_monitor, AgentPerformanceMonitor)
        assert isinstance(manager.config_manager, AgentConfigManager)
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        manager = AgentManager()
        
        config = manager.config_manager.get_default_config("requirements_analysis")
        
        assert config.agent_type == "requirements_analysis"
        assert config.model_name == "gemini-2.5-flash"
        assert config.temperature == 0.1
        assert config.max_retries == 3
        assert config.timeout_seconds == 30
    
    def test_list_available_agent_types(self):
        """Test listing available agent types."""
        manager = AgentManager()
        
        # Initially no agent types registered
        agent_types = manager.list_available_agent_types()
        assert len(agent_types) == 0
        
        # Register an agent type
        class TestAgent(BaseAgent):
            async def execute(self, task):
                return {"success": True}
            
            def validate_task(self, task):
                return True
        
        manager.factory.register_agent_type("test_type", TestAgent)
        
        agent_types = manager.list_available_agent_types()
        assert "test_type" in agent_types

class TestRequirementsAnalyst:
    """Test RequirementsAnalyst class."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="requirements_analysis",
            prompt_template_id="requirements_template"
        )
        
        agent = RequirementsAnalyst(config)
        
        assert agent.config.agent_id == "test_agent"
        assert agent.config.agent_type == "requirements_analysis"
        assert agent.state.status == "idle"
    
    def test_validate_task(self):
        """Test task validation."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="requirements_analysis",
            prompt_template_id="requirements_template"
        )
        
        agent = RequirementsAnalyst(config)
        
        # Valid task
        valid_task = {
            'description': 'Test description',
            'context': 'Test context'
        }
        assert agent.validate_task(valid_task) is True
        
        # Invalid task - missing description
        invalid_task = {
            'context': 'Test context'
        }
        assert agent.validate_task(invalid_task) is False
        
        # Invalid task - missing context
        invalid_task = {
            'description': 'Test description'
        }
        assert agent.validate_task(invalid_task) is False
    
    @pytest.mark.asyncio
    async def test_execute_task_fallback(self):
        """Test task execution with fallback analysis."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="requirements_analysis",
            prompt_template_id="requirements_template"
        )
        
        agent = RequirementsAnalyst(config)
        
        task = {
            'description': 'Create a user authentication system',
            'context': 'Web application with user management',
            'requirements': ['Secure login', 'Password reset'],
            'constraints': ['Must use OAuth2'],
            'stakeholders': ['End users', 'Administrators']
        }
        
        # Mock LLM model to None to trigger fallback
        agent.llm_model = None
        
        result = await agent.execute(task)
        
        assert result['success'] is True
        assert 'analysis' in result
        assert 'user_stories' in result['analysis']
        assert 'technical_requirements' in result['analysis']
        assert result['confidence'] > 0
        assert result['quality_score'] > 0
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="requirements_analysis",
            prompt_template_id="requirements_template"
        )
        
        agent = RequirementsAnalyst(config)
        
        text = "Create a web API with database security and cloud scalability"
        keywords = agent._extract_keywords(text)
        
        assert 'api' in keywords
        assert 'database' in keywords
        assert 'security' in keywords
        assert 'cloud' in keywords
        assert 'scalability' in keywords
    
    def test_generate_basic_user_stories(self):
        """Test basic user story generation."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="requirements_analysis",
            prompt_template_id="requirements_template"
        )
        
        agent = RequirementsAnalyst(config)
        
        description = "User can login and reset password"
        keywords = ['api', 'security']
        
        stories = agent._generate_basic_user_stories(description, keywords)
        
        assert len(stories) > 0
        assert all('id' in story for story in stories)
        assert all('title' in story for story in stories)
        assert all('description' in story for story in stories)
        assert all('acceptance_criteria' in story for story in stories)
    
    def test_generate_technical_requirements(self):
        """Test technical requirements generation."""
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="requirements_analysis",
            prompt_template_id="requirements_template"
        )
        
        agent = RequirementsAnalyst(config)
        
        description = "Create a secure API with database"
        keywords = ['api', 'database', 'security']
        
        requirements = agent._generate_technical_requirements(description, keywords)
        
        assert len(requirements) > 0
        assert any(req['category'] == 'API' for req in requirements)
        assert any(req['category'] == 'Database' for req in requirements)
        assert any(req['category'] == 'Security' for req in requirements)

class TestAgentSystemIntegration:
    """Test agent system integration."""
    
    def test_get_agent_manager(self):
        """Test getting the global agent manager."""
        manager1 = get_agent_manager()
        manager2 = get_agent_manager()
        
        # Should return the same instance
        assert manager1 is manager2
    
    @pytest.mark.asyncio
    async def test_analyze_requirements(self):
        """Test requirements analysis convenience function."""
        description = "Create a user authentication system"
        context = "Web application with user management"
        requirements = ["Secure login", "Password reset"]
        constraints = ["Must use OAuth2"]
        stakeholders = ["End users", "Administrators"]
        
        # Mock the agent manager to avoid LLM dependencies
        with patch('agents.get_agent_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.execute_task = AsyncMock(return_value={
                'success': True,
                'analysis': {
                    'user_stories': [],
                    'technical_requirements': []
                },
                'confidence': 0.85,
                'quality_score': 0.9
            })
            mock_get_manager.return_value = mock_manager
            
            result = await analyze_requirements(
                description, context, requirements, constraints, stakeholders
            )
            
            assert result['success'] is True
            assert 'analysis' in result
            assert result['confidence'] > 0
    
    def test_get_system_status(self):
        """Test getting system status."""
        status = get_system_status()
        
        assert 'active_agents' in status
        assert 'available_agent_types' in status
        assert 'performance_summary' in status
        assert 'agent_statuses' in status
        assert isinstance(status['active_agents'], int)
        assert isinstance(status['available_agent_types'], list)
        assert isinstance(status['performance_summary'], dict)
        assert isinstance(status['agent_statuses'], dict)

class TestAgentPerformance:
    """Test agent performance monitoring."""
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization."""
        from agents.core.agent_manager import AgentPerformanceMonitor
        
        monitor = AgentPerformanceMonitor()
        
        assert monitor.execution_history == []
    
    def test_record_execution(self):
        """Test recording agent execution."""
        from agents.core.agent_manager import AgentPerformanceMonitor
        
        monitor = AgentPerformanceMonitor()
        
        # Create a mock agent
        config = AgentConfig(
            agent_id="test_agent",
            agent_type="test_type",
            prompt_template_id="test_template"
        )
        
        agent = Mock()
        agent.config = config
        agent.state.status = "completed"
        agent.performance_metrics = {
            'execution_time': 1.5,
            'result_quality': 0.9
        }
        agent.state.error_count = 0
        agent.state.current_task = "Test task"
        
        result = {"success": True, "data": "test"}
        
        monitor.record_execution(agent, result)
        
        assert len(monitor.execution_history) == 1
        record = monitor.execution_history[0]
        
        assert record['agent_id'] == "test_agent"
        assert record['agent_type'] == "test_type"
        assert record['success'] is True
        assert record['execution_time'] == 1.5
        assert record['result_quality'] == 0.9
    
    def test_get_summary(self):
        """Test getting performance summary."""
        from agents.core.agent_manager import AgentPerformanceMonitor
        
        monitor = AgentPerformanceMonitor()
        
        # Add some test records
        monitor.execution_history = [
            {
                'agent_id': 'agent1',
                'agent_type': 'test_type',
                'timestamp': '2024-01-01T00:00:00',
                'execution_time': 1.0,
                'success': True,
                'result_quality': 0.9,
                'error_count': 0,
                'task_summary': 'Task 1'
            },
            {
                'agent_id': 'agent2',
                'agent_type': 'test_type',
                'timestamp': '2024-01-01T00:01:00',
                'execution_time': 2.0,
                'success': False,
                'result_quality': 0.5,
                'error_count': 1,
                'task_summary': 'Task 2'
            }
        ]
        
        summary = monitor.get_summary()
        
        assert summary['total_executions'] == 2
        assert summary['successful_executions'] == 1
        assert summary['success_rate'] == 0.5
        assert summary['avg_execution_time'] == 1.5
        assert len(summary['recent_executions']) == 2
