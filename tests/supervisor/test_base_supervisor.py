#!/usr/bin/env python3
"""
Tests for base supervisor classes.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from agents.supervisor.base_supervisor import BaseSupervisor, SupervisorConfig

# Mock the ChatGoogleGenerativeAI class for testing
class ChatGoogleGenerativeAI:
    """Mock class for testing."""
    pass


class TestSupervisorConfig:
    """Tests for SupervisorConfig."""
    
    def test_supervisor_config_creation(self):
        """Test creating a supervisor config."""
        config = SupervisorConfig(
            quality_thresholds={
                "requirements": 0.8,
                "architecture": 0.8,
                "code": 0.7
            }
        )
        
        assert config.quality_thresholds["requirements"] == 0.8
        assert config.quality_thresholds["architecture"] == 0.8
        assert config.quality_thresholds["code"] == 0.7
        assert config.max_retries == 3
        assert config.escalation_threshold == 0.7
        assert config.enable_parallel_execution is True
    
    def test_supervisor_config_custom_values(self):
        """Test creating a supervisor config with custom values."""
        config = SupervisorConfig(
            quality_thresholds={"test": 0.9},
            max_retries=5,
            escalation_threshold=0.8,
            enable_parallel_execution=False
        )
        
        assert config.quality_thresholds["test"] == 0.9
        assert config.max_retries == 5
        assert config.escalation_threshold == 0.8
        assert config.enable_parallel_execution is False
    
    def test_supervisor_config_validation(self):
        """Test supervisor config validation."""
        # Should not raise an exception
        config = SupervisorConfig(quality_thresholds={})
        assert isinstance(config, SupervisorConfig)


class ConcreteSupervisor(BaseSupervisor):
    """Concrete implementation for testing."""
    
    async def make_decision(self, context: dict) -> dict:
        """Make a test decision."""
        return {
            "action": "test_action",
            "result": "test_result",
            "context": context
        }


class TestBaseSupervisor:
    """Tests for BaseSupervisor."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def supervisor_config(self):
        """Create a supervisor config."""
        return SupervisorConfig(
            quality_thresholds={
                "requirements": 0.8,
                "architecture": 0.8,
                "code": 0.7
            }
        )
    
    @pytest.fixture
    def concrete_supervisor(self, mock_llm, supervisor_config):
        """Create a concrete supervisor instance."""
        return ConcreteSupervisor(mock_llm, supervisor_config)
    
    def test_supervisor_initialization(self, concrete_supervisor, mock_llm, supervisor_config):
        """Test supervisor initialization."""
        assert concrete_supervisor.llm == mock_llm
        assert concrete_supervisor.config == supervisor_config
        assert concrete_supervisor.decision_history == []
        assert concrete_supervisor.logger is not None
    
    def test_log_decision(self, concrete_supervisor):
        """Test logging a decision."""
        decision = {"action": "test", "result": "success"}
        context = {"input": "test_input"}
        
        decision_record = concrete_supervisor.log_decision(decision, context)
        
        assert len(concrete_supervisor.decision_history) == 1
        assert decision_record["decision"] == decision
        assert decision_record["context"] == context
        assert "timestamp" in decision_record
        assert isinstance(decision_record["timestamp"], str)
    
    def test_get_decision_history(self, concrete_supervisor):
        """Test getting decision history."""
        # Add some decisions
        concrete_supervisor.log_decision({"action": "test1"}, {"context": "test1"})
        concrete_supervisor.log_decision({"action": "test2"}, {"context": "test2"})
        
        history = concrete_supervisor.get_decision_history()
        
        assert len(history) == 2
        assert history[0]["decision"]["action"] == "test1"
        assert history[1]["decision"]["action"] == "test2"
    
    def test_clear_decision_history(self, concrete_supervisor):
        """Test clearing decision history."""
        # Add some decisions
        concrete_supervisor.log_decision({"action": "test"}, {"context": "test"})
        assert len(concrete_supervisor.decision_history) == 1
        
        # Clear history
        concrete_supervisor.clear_decision_history()
        assert len(concrete_supervisor.decision_history) == 0
    
    def test_get_recent_decisions(self, concrete_supervisor):
        """Test getting recent decisions."""
        # Add multiple decisions
        for i in range(5):
            concrete_supervisor.log_decision(
                {"action": f"test{i}"}, 
                {"context": f"test{i}"}
            )
        
        # Get recent decisions with limit
        recent = concrete_supervisor.get_recent_decisions(limit=3)
        assert len(recent) == 3
        assert recent[0]["decision"]["action"] == "test2"
        assert recent[1]["decision"]["action"] == "test3"
        assert recent[2]["decision"]["action"] == "test4"
    
    def test_get_recent_decisions_empty_history(self, concrete_supervisor):
        """Test getting recent decisions from empty history."""
        recent = concrete_supervisor.get_recent_decisions(limit=5)
        assert recent == []
    
    def test_get_recent_decisions_limit_exceeds_history(self, concrete_supervisor):
        """Test getting recent decisions when limit exceeds history size."""
        # Add one decision
        concrete_supervisor.log_decision({"action": "test"}, {"context": "test"})
        
        # Request more than available
        recent = concrete_supervisor.get_recent_decisions(limit=5)
        assert len(recent) == 1
        assert recent[0]["decision"]["action"] == "test"
    
    @pytest.mark.asyncio
    async def test_make_decision_implementation(self, concrete_supervisor):
        """Test the make_decision implementation."""
        context = {"input": "test_input", "data": "test_data"}
        
        result = await concrete_supervisor.make_decision(context)
        
        assert result["action"] == "test_action"
        assert result["result"] == "test_result"
        assert result["context"] == context
    
    def test_decision_history_timestamp_format(self, concrete_supervisor):
        """Test that decision timestamps are in ISO format."""
        concrete_supervisor.log_decision({"action": "test"}, {"context": "test"})
        
        decision_record = concrete_supervisor.decision_history[0]
        timestamp = decision_record["timestamp"]
        
        # Should be ISO format string
        assert isinstance(timestamp, str)
        # Should be parseable as datetime
        parsed_timestamp = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_timestamp, datetime)
    
    def test_multiple_decisions_ordering(self, concrete_supervisor):
        """Test that multiple decisions are stored in correct order."""
        decisions = []
        for i in range(3):
            decision = {"action": f"action{i}", "id": i}
            context = {"context": f"context{i}"}
            concrete_supervisor.log_decision(decision, context)
            decisions.append((decision, context))
        
        history = concrete_supervisor.get_decision_history()
        
        assert len(history) == 3
        for i, record in enumerate(history):
            assert record["decision"] == decisions[i][0]
            assert record["context"] == decisions[i][1]


class TestSupervisorIntegration:
    """Integration tests for supervisor functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
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
            },
            max_retries=3,
            escalation_threshold=0.7,
            enable_parallel_execution=True
        )
    
    @pytest.fixture
    def supervisor(self, mock_llm, supervisor_config):
        """Create a supervisor instance."""
        return ConcreteSupervisor(mock_llm, supervisor_config)
    
    def test_supervisor_config_integration(self, supervisor):
        """Test that supervisor uses config correctly."""
        assert supervisor.config.quality_thresholds["requirements"] == 0.8
        assert supervisor.config.max_retries == 3
        assert supervisor.config.enable_parallel_execution is True
    
    def test_supervisor_llm_integration(self, supervisor, mock_llm):
        """Test that supervisor has access to LLM."""
        assert supervisor.llm == mock_llm
        assert hasattr(supervisor.llm, 'invoke')
    
    @pytest.mark.asyncio
    async def test_supervisor_decision_workflow(self, supervisor):
        """Test complete decision workflow."""
        # Make a decision
        context = {"task": "requirements_analysis", "data": "test_data"}
        decision = await supervisor.make_decision(context)
        
        # Log the decision
        decision_record = supervisor.log_decision(decision, context)
        
        # Verify the decision was logged
        history = supervisor.get_decision_history()
        assert len(history) == 1
        assert history[0]["decision"] == decision
        assert history[0]["context"] == context
        
        # Verify the decision record
        assert decision_record["decision"] == decision
        assert decision_record["context"] == context
        assert "timestamp" in decision_record
    
    def test_supervisor_logger_integration(self, supervisor):
        """Test that supervisor has proper logging setup."""
        assert supervisor.logger is not None
        assert supervisor.logger.name == "ConcreteSupervisor"
        
        # Test that logging works
        decision = {"action": "test_logging"}
        context = {"test": "data"}
        
        # This should not raise an exception
        supervisor.log_decision(decision, context)
        
        # Verify the decision was logged
        history = supervisor.get_decision_history()
        assert len(history) == 1
        assert history[0]["decision"] == decision
