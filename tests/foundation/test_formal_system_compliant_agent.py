#!/usr/bin/env python3
"""
Comprehensive Test Suite for Formal System Compliant Agent

This test suite validates that the FormalSystemCompliantAgent properly integrates
mathematical validation into agent operations and maintains formal system compliance.

Tests cover:
- Agent initialization with mathematical validation
- Pre and post execution validation
- Formal system violation handling
- Performance metrics tracking
- Integration with base agent functionality
- Configuration and state management
"""

import pytest
import asyncio
import time
from datetime import datetime
from typing import Dict, Any
import logging

from agents.formal_system_compliant_agent import (
    FormalSystemCompliantAgent,
    FormalSystemCompliantAgentConfig,
    FormalSystemCompliantAgentState,
    FormalSystemViolation,
    create_formal_system_compliant_agent
)
from agents.base_agent import AgentConfig
from utils.validation.mathematical_system_foundation import LayerIndex


class TestFormalSystemCompliantAgent(FormalSystemCompliantAgent):
    """Concrete test implementation of FormalSystemCompliantAgent."""
    
    def __init__(self, config: FormalSystemCompliantAgentConfig, should_pass_validation: bool = True):
        super().__init__(config)
        self.should_pass_validation = should_pass_validation
        self.execution_count = 0
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Test implementation of execute method."""
        self.execution_count += 1
        
        # Simulate different behaviors based on task
        if self.should_pass_validation:
            return {
                "result": "success",
                "task_id": task.get("task_id", "unknown"),
                "action": "help users",
                "goal": "improve system",
                "execution_count": self.execution_count
            }
        else:
            return {
                "result": "harmful_action",
                "task_id": task.get("task_id", "unknown"),  
                "action": "harm users",
                "goal": "damage system",
                "execution_count": self.execution_count
            }
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Test implementation of validate_task method."""
        return isinstance(task, dict) and "task_type" in task


class TestFormalSystemCompliantAgentInitialization:
    """Test agent initialization and configuration."""
    
    def test_agent_initialization_success(self):
        """Test successful agent initialization."""
        config = FormalSystemCompliantAgentConfig(
            agent_id="test_agent_001",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE
        )
        
        agent = TestFormalSystemCompliantAgent(config)
        
        assert agent.config.agent_id == "test_agent_001"
        assert agent.config.agent_type == "testing_agent"
        assert agent.config.layer == LayerIndex.TESTING_CORE
        assert agent.config.enable_mathematical_validation == True
        assert agent.formal_compliance_required == True
        assert isinstance(agent.state, FormalSystemCompliantAgentState)
        assert agent.mathematical_foundation is not None
    
    def test_agent_initialization_with_custom_config(self):
        """Test agent initialization with custom configuration."""
        config = FormalSystemCompliantAgentConfig(
            agent_id="test_agent_002",
            agent_type="custom_agent",
            prompt_template_id="custom_template",
            layer=LayerIndex.SOFTWARE_ARCHITECTURE_CORE,
            enable_mathematical_validation=False,
            mathematical_validation_strict_mode=False,
            performance_threshold_ms=200.0,
            confidence_threshold=0.9
        )
        
        agent = TestFormalSystemCompliantAgent(config)
        
        assert agent.config.enable_mathematical_validation == False
        assert agent.config.mathematical_validation_strict_mode == False
        assert agent.config.performance_threshold_ms == 200.0
        assert agent.config.confidence_threshold == 0.9
    
    def test_create_formal_system_compliant_agent_utility(self):
        """Test the utility function for creating agent configurations."""
        config = create_formal_system_compliant_agent(
            agent_id="utility_test_001",
            agent_type="utility_agent",
            layer=LayerIndex.DEVELOPMENT_CORE,
            enable_mathematical_validation=True
        )
        
        assert isinstance(config, FormalSystemCompliantAgentConfig)
        assert config.agent_id == "utility_test_001"
        assert config.agent_type == "utility_agent"
        assert config.layer == LayerIndex.DEVELOPMENT_CORE
        assert config.enable_mathematical_validation == True


class TestFormalSystemCompliantAgentExecution:
    """Test agent execution with mathematical validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = FormalSystemCompliantAgentConfig(
            agent_id="execution_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE,
            enable_mathematical_validation=True,
            mathematical_validation_strict_mode=True
        )
    
    @pytest.mark.asyncio
    async def test_successful_execution_with_validation(self):
        """Test successful execution with mathematical validation."""
        agent = TestFormalSystemCompliantAgent(self.config, should_pass_validation=True)
        
        task = {
            "task_type": "beneficial_task",
            "task_id": "test_001",
            "description": "Help users improve their experience",
            "goal": "create positive impact"
        }
        
        result = await agent.run(task)
        
        assert result["result"] == "success"
        assert result["task_id"] == "test_001"
        assert agent.execution_count == 1
        
        # Check validation metrics
        assert agent.state.mathematical_validations_performed >= 2  # Pre and post validation
        assert agent.state.mathematical_validations_passed >= 2
        assert agent.state.mathematical_validations_failed == 0
        
        # Check formal system status
        status = agent.get_formal_system_status()
        assert status["validation_success_rate"] == 1.0
        assert status["formal_system_compliance_score"] > 0.8
    
    @pytest.mark.asyncio
    async def test_execution_with_validation_failure(self):
        """Test execution that fails mathematical validation."""
        agent = TestFormalSystemCompliantAgent(self.config, should_pass_validation=False)
        
        harmful_task = {
            "task_type": "harmful_task",
            "task_id": "test_002",
            "description": "Damage the system",
            "goal": "harm users"
        }
        
        with pytest.raises(FormalSystemViolation) as exc_info:
            await agent.run(harmful_task)
        
        assert "violates formal system rules" in str(exc_info.value)
        assert agent.state.mathematical_validations_failed > 0
    
    @pytest.mark.asyncio
    async def test_execution_with_validation_disabled(self):
        """Test execution with mathematical validation disabled."""
        config = FormalSystemCompliantAgentConfig(
            agent_id="no_validation_agent",
            agent_type="testing_agent", 
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE,
            enable_mathematical_validation=False
        )
        
        agent = TestFormalSystemCompliantAgent(config, should_pass_validation=False)
        
        task = {
            "task_type": "any_task",
            "task_id": "test_003",
            "description": "Any description"
        }
        
        # Should complete without validation errors
        result = await agent.run(task)
        assert result["result"] == "harmful_action"  # Would normally fail validation
        assert agent.state.mathematical_validations_performed == 0
    
    @pytest.mark.asyncio 
    async def test_performance_threshold_monitoring(self):
        """Test performance threshold monitoring."""
        config = FormalSystemCompliantAgentConfig(
            agent_id="performance_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template", 
            layer=LayerIndex.TESTING_CORE,
            performance_threshold_ms=1.0,  # Very low threshold to trigger warning
            mathematical_validation_strict_mode=True
        )
        
        agent = TestFormalSystemCompliantAgent(config, should_pass_validation=True)
        
        # Capture log output
        with pytest.warns(None) as warning_list:
            task = {
                "task_type": "slow_task",
                "task_id": "perf_001",
                "description": "Task that might trigger performance warning"
            }
            
            result = await agent.run(task)
            assert result["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_monitoring(self):
        """Test confidence threshold monitoring.""" 
        config = FormalSystemCompliantAgentConfig(
            agent_id="confidence_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE,
            confidence_threshold=0.99,  # Very high threshold
            mathematical_validation_strict_mode=True
        )
        
        agent = TestFormalSystemCompliantAgent(config, should_pass_validation=True)
        
        task = {
            "task_type": "neutral_task",
            "task_id": "conf_001", 
            "description": "Neutral task that might have lower confidence"
        }
        
        result = await agent.run(task)
        assert result["result"] == "success"


class TestFormalSystemCompliantAgentState:
    """Test agent state management and metrics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = FormalSystemCompliantAgentConfig(
            agent_id="state_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE
        )
        self.agent = TestFormalSystemCompliantAgent(self.config)
    
    def test_initial_state(self):
        """Test initial agent state."""
        state = self.agent.state
        
        assert state.mathematical_validations_performed == 0
        assert state.mathematical_validations_passed == 0
        assert state.mathematical_validations_failed == 0
        assert state.average_validation_time_ms == 0.0
        assert state.total_validation_time_ms == 0.0
        assert state.divine_validation_success_rate == 0.0
        assert state.ethical_validation_success_rate == 0.0
        assert state.harmonic_validation_success_rate == 0.0
        assert state.formal_system_compliance_score == 0.0
    
    @pytest.mark.asyncio
    async def test_state_updates_after_execution(self):
        """Test that state is properly updated after execution."""
        task = {
            "task_type": "state_test",
            "task_id": "state_001",
            "description": "Test state updates"
        }
        
        initial_validations = self.agent.state.mathematical_validations_performed
        
        await self.agent.run(task)
        
        # Check that validations were performed
        assert self.agent.state.mathematical_validations_performed > initial_validations
        assert self.agent.state.mathematical_validations_passed > 0
        assert self.agent.state.average_validation_time_ms > 0
        assert self.agent.state.total_validation_time_ms > 0
    
    def test_formal_system_status_report(self):
        """Test formal system status reporting."""
        status = self.agent.get_formal_system_status()
        
        required_fields = [
            "agent_id", "formal_compliance_required", "mathematical_validation_enabled",
            "strict_mode", "layer", "validations_performed", "validations_passed", 
            "validations_failed", "validation_success_rate", "average_validation_time_ms",
            "divine_validation_success_rate", "ethical_validation_success_rate",
            "harmonic_validation_success_rate", "formal_system_compliance_score",
            "foundation_metrics", "recent_validations", "recent_validation_results"
        ]
        
        for field in required_fields:
            assert field in status, f"Status should contain field: {field}"
        
        assert status["agent_id"] == self.config.agent_id
        assert status["layer"] == self.config.layer.name
        assert isinstance(status["foundation_metrics"], dict)
        assert isinstance(status["recent_validation_results"], list)


class TestFormalSystemCompliantAgentSyncValidation:
    """Test synchronous validation capabilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = FormalSystemCompliantAgentConfig(
            agent_id="sync_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE
        )
        self.agent = TestFormalSystemCompliantAgent(self.config)
    
    def test_sync_validation_success(self):
        """Test synchronous validation of compliant operation."""
        is_valid = self.agent.validate_formal_system_compliance_sync(
            operation_id="sync_test_001",
            operation_type="beneficial_operation",
            parameters={"action": "help users", "goal": "improve system"},
            context={"purpose": "positive impact"}
        )
        
        assert is_valid == True
    
    def test_sync_validation_failure(self):
        """Test synchronous validation of non-compliant operation."""
        is_valid = self.agent.validate_formal_system_compliance_sync(
            operation_id="sync_test_002", 
            operation_type="harmful_operation",
            parameters={"action": "harm users", "goal": "damage system"},
            context={"purpose": "negative impact"}
        )
        
        assert is_valid == False


class TestFormalSystemCompliantAgentIntegration:
    """Test integration with base agent functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = FormalSystemCompliantAgentConfig(
            agent_id="integration_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE,
            max_retries=2
        )
    
    @pytest.mark.asyncio
    async def test_base_agent_functionality_preserved(self):
        """Test that base agent functionality is preserved."""
        agent = TestFormalSystemCompliantAgent(self.config)
        
        # Test task validation
        valid_task = {"task_type": "valid", "description": "test"}
        invalid_task = {"invalid": "no task_type"}
        
        assert agent.validate_task(valid_task) == True
        assert agent.validate_task(invalid_task) == False
        
        # Test execution with valid task
        result = await agent.run(valid_task)
        assert result["result"] == "success"
        
        # Test state updates
        assert agent.state.status == "completed"
        assert agent.state.success_count == 1
        assert agent.state.total_executions == 1
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling integration."""
        # Create agent that will cause validation failure
        agent = TestFormalSystemCompliantAgent(self.config, should_pass_validation=False)
        
        harmful_task = {
            "task_type": "harmful",
            "description": "This will fail validation"
        }
        
        with pytest.raises(FormalSystemViolation):
            await agent.run(harmful_task)
        
        # Check that error state is properly managed
        assert agent.state.status == "error"
        assert agent.state.error_count > 0
    
    def test_configuration_inheritance(self):
        """Test that configuration properly inherits from base agent config."""
        config = FormalSystemCompliantAgentConfig(
            agent_id="inheritance_test",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            optimization_enabled=False,
            performance_monitoring=False,
            max_retries=5,
            timeout_seconds=60,
            model_name="custom-model",
            temperature=0.5,
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        agent = TestFormalSystemCompliantAgent(config)
        
        # Check base config properties
        assert agent.config.optimization_enabled == False
        assert agent.config.performance_monitoring == False
        assert agent.config.max_retries == 5
        assert agent.config.timeout_seconds == 60
        assert agent.config.model_name == "custom-model"
        assert agent.config.temperature == 0.5
        
        # Check extended config properties
        assert agent.config.layer == LayerIndex.DEVELOPMENT_CORE
        assert agent.config.enable_mathematical_validation == True  # Default


class TestFormalSystemCompliantAgentPerformance:
    """Test performance characteristics of formal system compliant agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = FormalSystemCompliantAgentConfig(
            agent_id="performance_test_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE
        )
    
    @pytest.mark.asyncio
    async def test_validation_performance_overhead(self):
        """Test that validation adds minimal performance overhead."""
        # Test with validation enabled
        agent_with_validation = TestFormalSystemCompliantAgent(self.config)
        
        # Test without validation  
        config_no_validation = FormalSystemCompliantAgentConfig(
            agent_id="no_validation_agent",
            agent_type="testing_agent",
            prompt_template_id="test_template",
            layer=LayerIndex.TESTING_CORE,
            enable_mathematical_validation=False
        )
        agent_without_validation = TestFormalSystemCompliantAgent(config_no_validation)
        
        task = {
            "task_type": "performance_test",
            "task_id": "perf_001",
            "description": "Performance comparison test"
        }
        
        # Time execution with validation
        start_with = time.time()
        await agent_with_validation.run(task)
        time_with_validation = time.time() - start_with
        
        # Time execution without validation
        start_without = time.time()
        await agent_without_validation.run(task)
        time_without_validation = time.time() - start_without
        
        # Validation overhead should be reasonable (less than 10x slower)
        overhead_ratio = time_with_validation / time_without_validation
        assert overhead_ratio < 10.0, f"Validation overhead too high: {overhead_ratio:.2f}x"
        
        print(f"Performance comparison:")
        print(f"With validation: {time_with_validation:.3f}s")
        print(f"Without validation: {time_without_validation:.3f}s") 
        print(f"Overhead ratio: {overhead_ratio:.2f}x")
    
    @pytest.mark.asyncio
    async def test_multiple_executions_performance(self):
        """Test performance over multiple executions."""
        agent = TestFormalSystemCompliantAgent(self.config)
        
        tasks = [
            {
                "task_type": "batch_test",
                "task_id": f"batch_{i:03d}",
                "description": f"Batch test task {i}"
            }
            for i in range(10)
        ]
        
        start_time = time.time()
        
        for task in tasks:
            await agent.run(task)
        
        total_time = time.time() - start_time
        avg_time_per_task = total_time / len(tasks)
        
        print(f"Batch execution performance:")
        print(f"Total tasks: {len(tasks)}")
        print(f"Total time: {total_time:.3f}s")
        print(f"Average time per task: {avg_time_per_task:.3f}s")
        
        # Each task should complete in reasonable time
        assert avg_time_per_task < 1.0, f"Average task time too high: {avg_time_per_task:.3f}s"
        
        # Check final state
        status = agent.get_formal_system_status()
        assert status["validations_performed"] >= len(tasks) * 2  # Pre and post validation
        assert status["validation_success_rate"] == 1.0


if __name__ == "__main__":
    # Run tests with verbose output
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v", "--tb=short"])
