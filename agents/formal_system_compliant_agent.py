"""
Formal System Compliant Agent - Mathematically Validated Agent Base Class

This module provides the MANDATORY base class for all agents in the system that ensures
mathematical and philosophical consistency according to our formal organization rules.

All agents MUST inherit from FormalSystemCompliantAgent to ensure compliance with:
- Divine mathematical constants
- Scientific method validation
- Ethical formalization (Asimov + Kant)
- Harmonic integration across all layers
- Formal verification and proof generation

Based on:
- docs/mathematics/formal_system_mathematics.md
- docs/rules/core/formal_organization_rules.md
- .cursor/rules/core/formal_system_enforcement.mdc
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from agents.base_agent import BaseAgent, AgentConfig, AgentState
from utils.validation.mathematical_system_foundation import (
    MathematicalSystemFoundation,
    Operation,
    LayerIndex,
    MathematicalValidationResult
)


class FormalSystemViolation(Exception):
    """Exception raised when an operation violates formal system rules."""
    pass


@dataclass
class FormalSystemCompliantAgentConfig(AgentConfig):
    """Extended configuration for formal system compliant agents."""
    enable_mathematical_validation: bool = True
    mathematical_validation_strict_mode: bool = True
    performance_threshold_ms: float = 100.0
    confidence_threshold: float = 0.8
    layer: LayerIndex = LayerIndex.DEVELOPMENT_CORE


@dataclass 
class FormalSystemCompliantAgentState(AgentState):
    """Extended state tracking for formal system compliant agents."""
    mathematical_validations_performed: int = 0
    mathematical_validations_passed: int = 0
    mathematical_validations_failed: int = 0
    average_validation_time_ms: float = 0.0
    total_validation_time_ms: float = 0.0
    divine_validation_success_rate: float = 0.0
    ethical_validation_success_rate: float = 0.0
    harmonic_validation_success_rate: float = 0.0
    formal_system_compliance_score: float = 0.0


class FormalSystemCompliantAgent(BaseAgent):
    """
    MANDATORY base class for all agents in the system.
    
    Ensures mathematical and philosophical consistency according to our formal
    organization rules. All operations are validated against:
    
    - Divine mathematical constants (love, wisdom, beauty, justice, mercy, power, unity)
    - Scientific method principles (empirical basis, reproducibility)
    - Ethical formalization (Asimov's Laws + Kant's Categorical Imperative)
    - Harmonic integration across all 12 layers
    - Formal verification and proof generation
    
    CRITICAL: All agents in the system MUST inherit from this class.
    Agents that do not use this base class violate formal system rules.
    """
    
    def __init__(self, config: FormalSystemCompliantAgentConfig, gemini_client=None):
        # Initialize base agent
        super().__init__(config, gemini_client)
        
        # Override state with formal system compliant state
        self.state = FormalSystemCompliantAgentState(agent_id=config.agent_id)
        self.config = config  # Type hint clarification
        
        # Initialize mathematical foundation system
        self.mathematical_foundation = MathematicalSystemFoundation()
        
        # Initialize formal system compliance tracking
        self.formal_compliance_required = True
        self.validation_history: List[MathematicalValidationResult] = []
        
        # Enhanced logging with formal system context
        self.logger = logging.getLogger(f"formal_agent.{config.agent_id}")
        self.logger.info(f"Initialized formal system compliant agent: {config.agent_id}")
    
    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced run method with mathematical validation.
        
        MANDATORY: All operations must validate formal compliance before execution.
        """
        try:
            # Pre-execution validation
            operation = self._create_operation_from_task(task, "agent_run")
            
            if self.config.enable_mathematical_validation:
                pre_validation = await self._validate_formal_system_compliance(operation)
                if not pre_validation.mathematically_sound:
                    raise FormalSystemViolation(
                        f"Pre-execution validation failed for {self.config.agent_id}: "
                        f"Operation {operation.operation_id} violates formal system rules. "
                        f"Errors: {pre_validation.error_messages}"
                    )
            
            # Execute with monitoring
            result = await self._execute_with_mathematical_monitoring(task)
            
            # Post-execution validation
            if self.config.enable_mathematical_validation:
                post_operation = self._create_operation_from_task(result, "agent_completion")
                post_validation = await self._validate_formal_system_compliance(post_operation)
                
                if not post_validation.mathematically_sound:
                    raise FormalSystemViolation(
                        f"Post-execution validation failed for {self.config.agent_id}: "
                        f"Result violates formal system rules. "
                        f"Errors: {post_validation.error_messages}"
                    )
            
            # Verify formal system integrity
            self._verify_formal_system_integrity()
            
            return result
            
        except FormalSystemViolation:
            # Formal system violations are critical and should not be retried
            self.state.status = 'error'
            self.state.error_count += 1
            raise
        except Exception as e:
            # Other exceptions can use normal retry logic
            return await super().run(task)
    
    async def _execute_with_mathematical_monitoring(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the base agent logic with mathematical monitoring."""
        start_time = time.time()
        
        try:
            # Call base class run method (which calls execute)
            result = await super().run(task)
            
            # Update mathematical validation metrics
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_mathematical_performance_metrics(execution_time_ms, True)
            
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_mathematical_performance_metrics(execution_time_ms, False)
            raise
    
    async def _validate_formal_system_compliance(self, operation: Operation) -> MathematicalValidationResult:
        """
        Validate operation against formal system rules.
        
        MANDATORY: All operations must pass this validation.
        """
        try:
            # Perform mathematical validation
            validation_result = self.mathematical_foundation.validate_operation_mathematically(operation)
            
            # Store validation result
            self.validation_history.append(validation_result)
            
            # Update state metrics
            self.state.mathematical_validations_performed += 1
            self.state.total_validation_time_ms += validation_result.validation_time_ms
            
            if validation_result.mathematically_sound:
                self.state.mathematical_validations_passed += 1
            else:
                self.state.mathematical_validations_failed += 1
            
            # Update average validation time
            self.state.average_validation_time_ms = (
                self.state.total_validation_time_ms / self.state.mathematical_validations_performed
            )
            
            # Update success rates
            self._update_validation_success_rates()
            
            # Check performance threshold
            if (self.config.mathematical_validation_strict_mode and 
                validation_result.validation_time_ms > self.config.performance_threshold_ms):
                self.logger.warning(
                    f"Mathematical validation exceeded performance threshold: "
                    f"{validation_result.validation_time_ms:.1f}ms > {self.config.performance_threshold_ms}ms"
                )
            
            # Check confidence threshold
            if (self.config.mathematical_validation_strict_mode and 
                validation_result.confidence_score < self.config.confidence_threshold):
                self.logger.warning(
                    f"Mathematical validation confidence below threshold: "
                    f"{validation_result.confidence_score:.3f} < {self.config.confidence_threshold}"
                )
            
            # Log validation result
            log_level = logging.INFO if validation_result.mathematically_sound else logging.ERROR
            self.logger.log(
                log_level,
                f"Mathematical validation: {operation.operation_id} - "
                f"Sound: {validation_result.mathematically_sound}, "
                f"Confidence: {validation_result.confidence_score:.3f}, "
                f"Time: {validation_result.validation_time_ms:.1f}ms"
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Mathematical validation failed with exception: {e}")
            # Create failed validation result
            return MathematicalValidationResult(
                divine_mathematics_valid=False,
                scientific_mathematics_valid=False,
                ethical_mathematics_valid=False,
                harmonic_integration_valid=False,
                formal_proof_complete=False,
                mathematically_sound=False,
                validation_time_ms=0.0,
                error_messages=[f"Validation exception: {str(e)}"],
                confidence_score=0.0,
                layer_validations={}
            )
    
    def _create_operation_from_task(self, task: Dict[str, Any], operation_type: str) -> Operation:
        """Create Operation object from task for validation."""
        operation_id = f"{self.config.agent_id}_{operation_type}_{int(time.time() * 1000)}"
        
        # Extract parameters safely
        parameters = {}
        if isinstance(task, dict):
            parameters = {k: v for k, v in task.items() if isinstance(v, (str, int, float, bool, list))}
        
        # Create context
        context = {
            "agent_id": self.config.agent_id,
            "agent_type": self.config.agent_type,
            "operation_type": operation_type,
            "layer": self.config.layer.name
        }
        
        return Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            parameters=parameters,
            context=context,
            timestamp=datetime.now(),
            layer=self.config.layer
        )
    
    def _update_validation_success_rates(self):
        """Update validation success rates based on recent history."""
        if not self.validation_history:
            return
        
        recent_validations = self.validation_history[-100:]  # Last 100 validations
        
        divine_successes = sum(1 for v in recent_validations if v.divine_mathematics_valid)
        ethical_successes = sum(1 for v in recent_validations if v.ethical_mathematics_valid)
        harmonic_successes = sum(1 for v in recent_validations if v.harmonic_integration_valid)
        
        total = len(recent_validations)
        
        self.state.divine_validation_success_rate = divine_successes / total
        self.state.ethical_validation_success_rate = ethical_successes / total
        self.state.harmonic_validation_success_rate = harmonic_successes / total
        
        # Calculate overall compliance score
        self.state.formal_system_compliance_score = (
            self.state.divine_validation_success_rate * 0.4 +
            self.state.ethical_validation_success_rate * 0.3 +
            self.state.harmonic_validation_success_rate * 0.3
        )
    
    def _update_mathematical_performance_metrics(self, execution_time_ms: float, success: bool):
        """Update mathematical performance metrics."""
        # Update base performance metrics
        self.performance_metrics.setdefault('mathematical_validations', 0)
        self.performance_metrics['mathematical_validations'] += 1
        
        if success:
            self.performance_metrics.setdefault('mathematical_validations_successful', 0)
            self.performance_metrics['mathematical_validations_successful'] += 1
        
        # Update execution time tracking
        self.performance_metrics.setdefault('total_mathematical_execution_time_ms', 0.0)
        self.performance_metrics['total_mathematical_execution_time_ms'] += execution_time_ms
        
        self.performance_metrics['average_mathematical_execution_time_ms'] = (
            self.performance_metrics['total_mathematical_execution_time_ms'] / 
            self.performance_metrics['mathematical_validations']
        )
    
    def _verify_formal_system_integrity(self):
        """
        Verify that the formal system integrity is maintained.
        
        MANDATORY: This check ensures no corruption of formal system principles.
        """
        try:
            # Check mathematical foundation integrity
            foundation_metrics = self.mathematical_foundation.get_performance_metrics()
            
            # Verify divine constants are preserved
            if foundation_metrics.get('total_validations', 0) > 0:
                divine_success_rate = foundation_metrics.get('divine_validation_success_rate', 0.0)
                if divine_success_rate < 0.9:  # 90% threshold for divine validation
                    self.logger.warning(
                        f"Divine validation success rate below threshold: {divine_success_rate:.3f}"
                    )
            
            # Verify agent compliance
            if self.state.mathematical_validations_performed > 10:  # Only check after enough data
                if self.state.formal_system_compliance_score < 0.8:  # 80% compliance threshold
                    self.logger.warning(
                        f"Formal system compliance score below threshold: "
                        f"{self.state.formal_system_compliance_score:.3f}"
                    )
            
            # Keep validation history manageable
            if len(self.validation_history) > 500:
                self.validation_history = self.validation_history[-250:]
            
        except Exception as e:
            self.logger.error(f"Formal system integrity verification failed: {e}")
    
    def get_formal_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive formal system status for monitoring.
        
        Returns:
            Dictionary containing all formal system metrics and status
        """
        return {
            "agent_id": self.config.agent_id,
            "formal_compliance_required": self.formal_compliance_required,
            "mathematical_validation_enabled": self.config.enable_mathematical_validation,
            "strict_mode": self.config.mathematical_validation_strict_mode,
            "layer": self.config.layer.name,
            
            # Validation metrics
            "validations_performed": self.state.mathematical_validations_performed,
            "validations_passed": self.state.mathematical_validations_passed,
            "validations_failed": self.state.mathematical_validations_failed,
            "validation_success_rate": (
                self.state.mathematical_validations_passed / max(1, self.state.mathematical_validations_performed)
            ),
            
            # Performance metrics
            "average_validation_time_ms": self.state.average_validation_time_ms,
            "total_validation_time_ms": self.state.total_validation_time_ms,
            
            # Success rates by category
            "divine_validation_success_rate": self.state.divine_validation_success_rate,
            "ethical_validation_success_rate": self.state.ethical_validation_success_rate,
            "harmonic_validation_success_rate": self.state.harmonic_validation_success_rate,
            
            # Overall compliance
            "formal_system_compliance_score": self.state.formal_system_compliance_score,
            
            # Mathematical foundation metrics
            "foundation_metrics": self.mathematical_foundation.get_performance_metrics(),
            
            # Recent validation history
            "recent_validations": len(self.validation_history),
            "recent_validation_results": [
                {
                    "mathematically_sound": v.mathematically_sound,
                    "confidence_score": v.confidence_score,
                    "validation_time_ms": v.validation_time_ms,
                    "error_count": len(v.error_messages)
                }
                for v in self.validation_history[-10:]  # Last 10 validations
            ]
        }
    
    def validate_formal_system_compliance_sync(self, operation_id: str, operation_type: str, 
                                              parameters: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """
        Synchronous validation for non-async contexts.
        
        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation
            parameters: Operation parameters
            context: Optional context
            
        Returns:
            True if operation passes all formal system validations
        """
        operation = Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            parameters=parameters,
            context=context or {},
            timestamp=datetime.now(),
            layer=self.config.layer
        )
        
        validation_result = self.mathematical_foundation.validate_operation_mathematically(operation)
        
        if not validation_result.mathematically_sound:
            self.logger.error(
                f"Formal system compliance validation failed for {operation_id}: "
                f"{validation_result.error_messages}"
            )
        
        return validation_result.mathematically_sound


# Utility function for creating formal system compliant agents
def create_formal_system_compliant_agent(agent_id: str, agent_type: str, 
                                        layer: LayerIndex = LayerIndex.DEVELOPMENT_CORE,
                                        **kwargs) -> FormalSystemCompliantAgentConfig:
    """
    Utility function for creating formal system compliant agent configurations.
    
    Args:
        agent_id: Unique agent identifier
        agent_type: Type of agent
        layer: Layer in the onion architecture
        **kwargs: Additional configuration parameters
        
    Returns:
        FormalSystemCompliantAgentConfig instance
    """
    return FormalSystemCompliantAgentConfig(
        agent_id=agent_id,
        agent_type=agent_type,
        prompt_template_id=f"{agent_type}_template",
        layer=layer,
        **kwargs
    )


if __name__ == "__main__":
    # Example usage and testing
    import asyncio
    
    async def test_formal_system_compliant_agent():
        """Test the formal system compliant agent."""
        # Create test configuration
        config = create_formal_system_compliant_agent(
            agent_id="test_formal_agent",
            agent_type="testing_agent",
            layer=LayerIndex.TESTING_CORE
        )
        
        # Create concrete test agent class
        class TestFormalAgent(FormalSystemCompliantAgent):
            async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "test_completed", "task": task}
            
            def validate_task(self, task: Dict[str, Any]) -> bool:
                return isinstance(task, dict) and "test_type" in task
        
        # Test agent
        agent = TestFormalAgent(config)
        
        test_task = {
            "test_type": "formal_validation",
            "description": "Test mathematical validation system",
            "goal": "improve system quality"
        }
        
        try:
            result = await agent.run(test_task)
            print("✅ Test passed - Agent executed with formal validation")
            print(f"Result: {result}")
            
            # Get status
            status = agent.get_formal_system_status()
            print(f"Compliance Score: {status['formal_system_compliance_score']:.3f}")
            
        except FormalSystemViolation as e:
            print(f"❌ Formal system violation: {e}")
        except Exception as e:
            print(f"❌ Execution error: {e}")
    
    # Run test
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_formal_system_compliant_agent())
