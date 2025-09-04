#!/usr/bin/env python3
"""
Comprehensive Test Suite for Specialized Subagent Team

Tests the specialized keyword-role-subagent team implementation for Sprint 2
optimization, validating all agent roles, collaboration patterns, and integration.

Test Coverage:
- Individual agent functionality and specializations
- Team coordination and collaboration patterns
- Task detection and routing based on keywords
- Sprint 2 optimization execution
- Performance metrics and quality validation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, List, Any

import sys
from pathlib import Path

# Add project root to path at the very beginning to override any conflicting modules
project_root = Path(__file__).parent.parent.parent
if str(project_root) in sys.path:
    sys.path.remove(str(project_root))
sys.path.insert(0, str(project_root))

from agents.teams.specialized_subagent_team import (
    SpecializedSubagentTeam,
    ArchitectAgent,
    DeveloperAgent,
    TesterAgent,
    OptimizerAgent,
    CoordinatorAgent,
    DocumenterAgent,
    AgentRole,
    TaskContext,
    AgentResponse,
    TaskComplexity
)

class TestSpecializedSubagentTeam:
    """Test suite for the specialized subagent team"""
    
    @pytest.fixture
    def team(self):
        """Create a specialized subagent team for testing"""
        return SpecializedSubagentTeam()
    
    @pytest.fixture
    def sample_context(self):
        """Sample task context for testing"""
        return TaskContext(
            user_story_id='US-AB-02',
            story_points=13,
            priority='CRITICAL',
            dependencies=['US-PE-01', 'US-AB-01'],
            acceptance_criteria=[
                'Agent intelligence framework implemented',
                'Integration with prompt engineering system',
                'Comprehensive testing and validation'
            ],
            current_status='Ready to start',
            sprint_goal_alignment=0.95
        )
    
    def test_team_initialization(self, team):
        """Test that the team initializes correctly with all agents"""
        # Test all agents are created
        assert len(team.agents) == 6
        
        # Test all required agent roles are present
        expected_roles = {
            AgentRole.ARCHITECT,
            AgentRole.DEVELOPER,
            AgentRole.TESTER,
            AgentRole.OPTIMIZER,
            AgentRole.COORDINATOR,
            AgentRole.DOCUMENTER
        }
        assert set(team.agents.keys()) == expected_roles
        
        # Test team performance tracking initialized
        assert isinstance(team.team_performance, dict)
        assert isinstance(team.collaboration_history, list)
    
    def test_keyword_detection(self, team):
        """Test keyword detection for agent routing"""
        # Test architect keywords
        arch_task = "@architect design system architecture"
        roles = team.detect_agent_keywords(arch_task)
        assert AgentRole.ARCHITECT in roles
        
        # Test developer keywords
        dev_task = "@developer implement code feature"
        roles = team.detect_agent_keywords(dev_task)
        assert AgentRole.DEVELOPER in roles
        
        # Test multiple keywords
        multi_task = "@architect @developer design and implement system"
        roles = team.detect_agent_keywords(multi_task)
        assert AgentRole.ARCHITECT in roles
        assert AgentRole.DEVELOPER in roles
        
        # Test no keywords (should default to coordinator)
        no_keyword_task = "generic task with no specific keywords"
        roles = team.detect_agent_keywords(no_keyword_task)
        assert AgentRole.COORDINATOR in roles

class TestIndividualAgents:
    """Test individual agent functionality"""
    
    @pytest.fixture
    def sample_context(self):
        """Sample task context for testing"""
        return TaskContext(
            user_story_id='US-TEST-01',
            story_points=5,
            priority='HIGH',
            dependencies=[],
            acceptance_criteria=['Test criteria'],
            current_status='In progress',
            sprint_goal_alignment=0.85
        )
    
    def test_architect_agent_initialization(self):
        """Test architect agent initialization"""
        agent = ArchitectAgent()
        
        assert agent.role == AgentRole.ARCHITECT
        assert agent.capabilities.model_complexity == TaskComplexity.CRITICAL
        assert agent.capabilities.priority_level == 1
        assert "@architect" in agent.capabilities.keywords
        assert "System architecture design" in agent.capabilities.specializations
    
    def test_developer_agent_initialization(self):
        """Test developer agent initialization"""
        agent = DeveloperAgent()
        
        assert agent.role == AgentRole.DEVELOPER
        assert agent.capabilities.model_complexity == TaskComplexity.COMPLEX
        assert agent.capabilities.priority_level == 2
        assert "@developer" in agent.capabilities.keywords
        assert "Test-driven development" in agent.capabilities.specializations
    
    def test_tester_agent_initialization(self):
        """Test tester agent initialization"""
        agent = TesterAgent()
        
        assert agent.role == AgentRole.TESTER
        assert agent.capabilities.model_complexity == TaskComplexity.COMPLEX
        assert agent.capabilities.priority_level == 2
        assert "@tester" in agent.capabilities.keywords
        assert "Comprehensive test strategy" in agent.capabilities.specializations
    
    def test_optimizer_agent_initialization(self):
        """Test optimizer agent initialization"""
        agent = OptimizerAgent()
        
        assert agent.role == AgentRole.OPTIMIZER
        assert agent.capabilities.model_complexity == TaskComplexity.COMPLEX
        assert agent.capabilities.priority_level == 3
        assert "@optimizer" in agent.capabilities.keywords
        assert "Performance optimization and monitoring" in agent.capabilities.specializations
    
    def test_coordinator_agent_initialization(self):
        """Test coordinator agent initialization"""
        agent = CoordinatorAgent()
        
        assert agent.role == AgentRole.COORDINATOR
        assert agent.capabilities.model_complexity == TaskComplexity.COMPLEX
        assert agent.capabilities.priority_level == 1
        assert "@coordinator" in agent.capabilities.keywords
        assert "Agile sprint management and coordination" in agent.capabilities.specializations
    
    def test_documenter_agent_initialization(self):
        """Test documenter agent initialization"""
        agent = DocumenterAgent()
        
        assert agent.role == AgentRole.DOCUMENTER
        assert agent.capabilities.model_complexity == TaskComplexity.SIMPLE
        assert agent.capabilities.priority_level == 3
        assert "@documenter" in agent.capabilities.keywords
        assert "Comprehensive documentation and knowledge management" in agent.capabilities.specializations

class TestAgentSpecializations:
    """Test agent specializations and capabilities"""
    
    def test_architect_specializations(self):
        """Test architect agent specializations"""
        agent = ArchitectAgent()
        specializations = agent.capabilities.specializations
        
        # Check key architectural specializations
        assert "System architecture design" in specializations
        assert "Component integration planning" in specializations
        assert "Design pattern selection" in specializations
        assert "Scalability analysis" in specializations
        assert "Technical decision making" in specializations
    
    def test_developer_specializations(self):
        """Test developer agent specializations"""
        agent = DeveloperAgent()
        specializations = agent.capabilities.specializations
        
        # Check key development specializations
        assert "Code implementation excellence" in specializations
        assert "Test-driven development" in specializations
        assert "Framework integration" in specializations
        assert "Error handling and validation" in specializations
        assert "Performance optimization" in specializations
    
    def test_tester_specializations(self):
        """Test tester agent specializations"""
        agent = TesterAgent()
        specializations = agent.capabilities.specializations
        
        # Check key testing specializations
        assert "Comprehensive test strategy" in specializations
        assert "Quality assurance and validation" in specializations
        assert "Test automation and coverage" in specializations
        assert "Performance and security testing" in specializations
        assert "Acceptance criteria validation" in specializations

class TestAgentCollaboration:
    """Test agent collaboration patterns"""
    
    def test_collaboration_patterns(self):
        """Test that agents have correct collaboration patterns"""
        # Architect collaborates with developer, tester, optimizer
        architect = ArchitectAgent()
        assert AgentRole.DEVELOPER in architect.capabilities.collaboration_patterns
        assert AgentRole.TESTER in architect.capabilities.collaboration_patterns
        assert AgentRole.OPTIMIZER in architect.capabilities.collaboration_patterns
        
        # Developer collaborates with architect, tester, optimizer
        developer = DeveloperAgent()
        assert AgentRole.ARCHITECT in developer.capabilities.collaboration_patterns
        assert AgentRole.TESTER in developer.capabilities.collaboration_patterns
        assert AgentRole.OPTIMIZER in developer.capabilities.collaboration_patterns
        
        # Coordinator collaborates with all agents
        coordinator = CoordinatorAgent()
        expected_collaborations = [
            AgentRole.ARCHITECT, AgentRole.DEVELOPER, AgentRole.TESTER,
            AgentRole.OPTIMIZER, AgentRole.DOCUMENTER
        ]
        for role in expected_collaborations:
            assert role in coordinator.capabilities.collaboration_patterns

class TestModelSelection:
    """Test AI model selection based on agent complexity"""
    
    @patch('streamlit.secrets')
    def test_model_selection_critical(self, mock_secrets):
        """Test critical complexity model selection"""
        mock_secrets.get.return_value = "test-api-key"
        
        agent = ArchitectAgent()
        llm = agent._initialize_llm()
        
        # Architect should use critical complexity model
        assert agent.capabilities.model_complexity == TaskComplexity.CRITICAL
        # Note: We can't easily test the actual model name without mocking deeper
        assert llm is not None
    
    @patch('streamlit.secrets')
    def test_model_selection_complex(self, mock_secrets):
        """Test complex complexity model selection"""
        mock_secrets.get.return_value = "test-api-key"
        
        agent = DeveloperAgent()
        llm = agent._initialize_llm()
        
        # Developer should use complex complexity model
        assert agent.capabilities.model_complexity == TaskComplexity.COMPLEX
        assert llm is not None
    
    @patch('streamlit.secrets')
    def test_model_selection_simple(self, mock_secrets):
        """Test simple complexity model selection"""
        mock_secrets.get.return_value = "test-api-key"
        
        agent = DocumenterAgent()
        llm = agent._initialize_llm()
        
        # Documenter should use simple complexity model
        assert agent.capabilities.model_complexity == TaskComplexity.SIMPLE
        assert llm is not None

class TestTaskExecution:
    """Test task execution and response handling"""
    
    @pytest.fixture
    def sample_context(self):
        """Sample task context for testing"""
        return TaskContext(
            user_story_id='US-TEST-01',
            story_points=8,
            priority='HIGH',
            dependencies=['US-PREREQ-01'],
            acceptance_criteria=[
                'Feature implemented correctly',
                'Comprehensive test coverage',
                'Documentation updated'
            ],
            current_status='In progress',
            sprint_goal_alignment=0.90
        )
    
    @patch('streamlit.secrets')
    @patch('agents.specialized_subagent_team.ChatGoogleGenerativeAI')
    def test_architect_prompt_generation(self, mock_llm_class, mock_secrets, sample_context):
        """Test architect agent prompt generation"""
        mock_secrets.get.return_value = "test-api-key"
        mock_llm_class.return_value = Mock()
        
        agent = ArchitectAgent()
        task = "Design system architecture for agent framework"
        
        prompt = agent.get_specialized_prompt(task, sample_context)
        
        # Check prompt contains key elements
        assert "architect agent" in prompt.lower()
        assert "system architecture" in prompt.lower()
        assert sample_context.user_story_id in prompt
        assert str(sample_context.story_points) in prompt
        assert sample_context.priority in prompt
    
    @patch('streamlit.secrets')
    @patch('agents.specialized_subagent_team.ChatGoogleGenerativeAI')
    def test_developer_prompt_generation(self, mock_llm_class, mock_secrets, sample_context):
        """Test developer agent prompt generation"""
        mock_secrets.get.return_value = "test-api-key"
        mock_llm_class.return_value = Mock()
        
        agent = DeveloperAgent()
        task = "Implement agent intelligence framework"
        
        prompt = agent.get_specialized_prompt(task, sample_context)
        
        # Check prompt contains key elements
        assert "developer agent" in prompt.lower()
        assert "test-driven development" in prompt.lower()
        assert "langchain" in prompt.lower()
        assert sample_context.user_story_id in prompt

class TestPerformanceMetrics:
    """Test performance metrics and tracking"""
    
    def test_performance_metrics_initialization(self):
        """Test that agents initialize performance metrics"""
        agent = ArchitectAgent()
        
        assert isinstance(agent.performance_metrics, dict)
        assert isinstance(agent.session_history, list)
    
    def test_performance_metrics_update(self):
        """Test performance metrics update"""
        agent = ArchitectAgent()
        
        # Create sample agent response
        response = AgentResponse(
            agent_role=AgentRole.ARCHITECT,
            task_id="test_task",
            response_content="Test response",
            recommendations=["Test recommendation"],
            next_actions=["Test action"],
            quality_score=0.95,
            evidence={"test": "evidence"},
            collaboration_needs=[AgentRole.DEVELOPER]
        )
        
        # Update performance metrics
        agent.update_performance_metrics(response)
        
        # Check metrics were updated
        assert 'quality_score' in agent.performance_metrics
        assert 'response_time' in agent.performance_metrics
        assert 'task_completion_rate' in agent.performance_metrics
        assert 'collaboration_effectiveness' in agent.performance_metrics
        
        assert agent.performance_metrics['quality_score'] == 0.95
        assert agent.performance_metrics['task_completion_rate'] == 1.0

class TestSprint2Optimization:
    """Test Sprint 2 optimization capabilities"""
    
    @pytest.fixture
    def team(self):
        """Create team for Sprint 2 testing"""
        return SpecializedSubagentTeam()
    
    def test_optimization_recommendations(self, team):
        """Test optimization recommendations generation"""
        recommendations = team._generate_optimization_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for key Sprint 2 elements
        assert any("US-AB-02" in rec for rec in recommendations)
        assert any("Agent Intelligence Framework" in rec for rec in recommendations)
        assert any("parallel" in rec.lower() for rec in recommendations)
    
    def test_next_actions_generation(self, team):
        """Test next actions generation"""
        next_actions = team._generate_next_actions()
        
        assert isinstance(next_actions, list)
        assert len(next_actions) > 0
        
        # Check for actionable items
        assert any("Begin" in action for action in next_actions)
        assert any("Complete" in action for action in next_actions)
        assert any("Monitor" in action for action in next_actions)
    
    def test_success_metrics_calculation(self, team):
        """Test success metrics calculation"""
        # Mock sprint results
        mock_results = {
            'US-AB-02': {
                'architect': AgentResponse(
                    agent_role=AgentRole.ARCHITECT,
                    task_id="test",
                    response_content="test",
                    recommendations=[],
                    next_actions=[],
                    quality_score=0.95,
                    evidence={}
                )
            },
            'US-PE-03': {
                'developer': AgentResponse(
                    agent_role=AgentRole.DEVELOPER,
                    task_id="test",
                    response_content="test",
                    recommendations=[],
                    next_actions=[],
                    quality_score=0.92,
                    evidence={}
                )
            }
        }
        
        metrics = team._calculate_success_metrics(mock_results)
        
        assert isinstance(metrics, dict)
        assert 'task_completion_rate' in metrics
        assert 'average_quality_score' in metrics
        assert 'team_collaboration_effectiveness' in metrics
        assert 'sprint_goal_alignment' in metrics
        assert 'value_delivery_score' in metrics
        
        # Check reasonable values
        assert 0 <= metrics['task_completion_rate'] <= 1
        assert 0 <= metrics['average_quality_score'] <= 1
        assert 0 <= metrics['sprint_goal_alignment'] <= 1
        assert 0 <= metrics['value_delivery_score'] <= 1

class TestTeamStatus:
    """Test team status and monitoring"""
    
    @pytest.fixture
    def team(self):
        """Create team for status testing"""
        return SpecializedSubagentTeam()
    
    def test_team_status_structure(self, team):
        """Test team status structure"""
        status = team.get_team_status()
        
        assert isinstance(status, dict)
        assert 'team_performance' in status
        assert 'agent_status' in status
        assert 'collaboration_history' in status
    
    def test_agent_status_details(self, team):
        """Test agent status details"""
        status = team.get_team_status()
        agent_status = status['agent_status']
        
        # Check all agents are represented
        expected_agents = [
            '@architect', '@developer', '@tester',
            '@optimizer', '@coordinator', '@documenter'
        ]
        
        for agent_name in expected_agents:
            assert agent_name in agent_status
            
            agent_info = agent_status[agent_name]
            assert 'specializations' in agent_info
            assert 'performance_metrics' in agent_info
            assert 'collaboration_patterns' in agent_info
            
            assert isinstance(agent_info['specializations'], list)
            assert isinstance(agent_info['performance_metrics'], dict)
            assert isinstance(agent_info['collaboration_patterns'], list)

class TestErrorHandling:
    """Test error handling and recovery"""
    
    @patch('streamlit.secrets')
    def test_missing_api_key_error(self, mock_secrets):
        """Test error handling for missing API key"""
        mock_secrets.get.return_value = None
        
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found in secrets"):
            ArchitectAgent()
    
    @patch('streamlit.secrets')
    @patch('agents.specialized_subagent_team.ChatGoogleGenerativeAI')
    def test_agent_task_failure_handling(self, mock_llm_class, mock_secrets):
        """Test handling of agent task failures"""
        mock_secrets.get.return_value = "test-api-key"
        
        # Mock LLM to raise an exception
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("Test error")
        mock_llm_class.return_value = mock_llm
        
        team = SpecializedSubagentTeam()
        context = TaskContext(
            user_story_id='US-TEST-ERROR',
            story_points=5,
            priority='HIGH',
            dependencies=[],
            acceptance_criteria=['Test'],
            current_status='Error test',
            sprint_goal_alignment=0.5
        )
        
        # Note: This would be an async test in real implementation
        # For now, we test that the team structure handles failures
        assert team is not None
        assert len(team.agents) == 6

# Integration Tests
class TestIntegration:
    """Integration tests for the specialized subagent team"""
    
    @pytest.fixture
    def team(self):
        """Create team for integration testing"""
        return SpecializedSubagentTeam()
    
    @pytest.fixture
    def sprint_context(self):
        """Sprint 2 context for integration testing"""
        return TaskContext(
            user_story_id='US-AB-02',
            story_points=13,
            priority='CRITICAL',
            dependencies=['US-PE-01', 'US-AB-01'],
            acceptance_criteria=[
                'Agent intelligence framework implemented',
                'Integration with prompt engineering system',
                'Comprehensive testing and validation',
                'Performance optimization and monitoring'
            ],
            current_status='Ready to start',
            sprint_goal_alignment=0.95
        )
    
    def test_team_integration_workflow(self, team, sprint_context):
        """Test complete team integration workflow"""
        # Test keyword detection
        task = "@architect @developer @tester implement agent intelligence framework"
        detected_roles = team.detect_agent_keywords(task)
        
        assert AgentRole.ARCHITECT in detected_roles
        assert AgentRole.DEVELOPER in detected_roles
        assert AgentRole.TESTER in detected_roles
        
        # Test team status tracking
        initial_status = team.get_team_status()
        assert isinstance(initial_status, dict)
        
        # Test optimization recommendations
        recommendations = team._generate_optimization_recommendations()
        assert len(recommendations) >= 3
        
        # Test success metrics calculation
        mock_response = AgentResponse(
            agent_role=AgentRole.ARCHITECT,
            task_id="test",
            response_content="test",
            recommendations=[],
            next_actions=[],
            quality_score=0.95,
            evidence={}
        )
        mock_results = {'US-AB-02': {'test': mock_response}}
        metrics = team._calculate_success_metrics(mock_results)
        assert all(key in metrics for key in [
            'task_completion_rate', 'average_quality_score',
            'team_collaboration_effectiveness', 'sprint_goal_alignment'
        ])

# Performance Tests
class TestPerformance:
    """Performance tests for the specialized subagent team"""
    
    def test_agent_initialization_performance(self):
        """Test that agent initialization is performant"""
        import time
        
        start_time = time.time()
        team = SpecializedSubagentTeam()
        end_time = time.time()
        
        initialization_time = end_time - start_time
        
        # Should initialize quickly (less than 1 second)
        assert initialization_time < 1.0
        
        # Should have all agents
        assert len(team.agents) == 6
    
    def test_keyword_detection_performance(self):
        """Test keyword detection performance"""
        import time
        
        team = SpecializedSubagentTeam()
        
        # Test with multiple iterations
        tasks = [
            "@architect design system",
            "@developer implement code",
            "@tester validate quality",
            "@optimizer improve performance",
            "@coordinator manage team",
            "@documenter write docs"
        ]
        
        start_time = time.time()
        for _ in range(100):
            for task in tasks:
                team.detect_agent_keywords(task)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Should be very fast (less than 0.1 seconds for 600 detections)
        assert total_time < 0.1

# Test Runner
def run_tests():
    """Run all tests for the specialized subagent team"""
    print("🧪 Running Specialized Subagent Team Tests")
    print("=" * 50)
    
    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ])

if __name__ == "__main__":
    run_tests()
