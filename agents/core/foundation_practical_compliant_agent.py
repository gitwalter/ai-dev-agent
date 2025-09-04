#!/usr/bin/env python3
"""
Foundation-Practical Compliant Agent

Enhanced agent base class that integrates with the complete Foundation-Practical
Onion Architecture system, ensuring validation through both foundational principles
and practical engineering excellence.

This agent replaces the previous formal system compliant agent with the improved
foundation-practical separation for clearer validation and better organization.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentConfig, AgentState
from utils.validation.foundation_practical_onion_system import (
    FoundationPracticalOnionArchitecture,
    Operation,
    FoundationLayer,
    PracticalLayer,
    CompleteValidationResult
)


class FoundationPracticalViolation(Exception):
    """Exception raised when an operation violates foundation or practical standards."""
    pass


@dataclass
class FoundationPracticalAgentConfig(AgentConfig):
    """Extended configuration for foundation-practical compliant agents."""
    enable_foundation_validation: bool = True
    enable_practical_validation: bool = True
    validation_strict_mode: bool = True
    performance_threshold_ms: float = 100.0
    confidence_threshold: float = 0.8
    foundation_layer: Optional[FoundationLayer] = FoundationLayer.UNIVERSAL_FOUNDATION
    practical_layer: Optional[PracticalLayer] = PracticalLayer.SOFTWARE_ARCHITECTURE


@dataclass 
class FoundationPracticalAgentState(AgentState):
    """Extended state tracking for foundation-practical compliant agents."""
    foundation_validations_performed: int = 0
    foundation_validations_passed: int = 0
    foundation_validations_failed: int = 0
    practical_validations_performed: int = 0
    practical_validations_passed: int = 0
    practical_validations_failed: int = 0
    average_validation_time_ms: float = 0.0
    total_validation_time_ms: float = 0.0
    foundation_score_average: float = 0.0
    practical_score_average: float = 0.0
    overall_compliance_score: float = 0.0


class FoundationPracticalCompliantAgent(BaseAgent):
    """
    ENHANCED agent base class with Foundation-Practical Onion Architecture validation.
    
    Ensures operations are validated through:
    - Foundation Layers: Universal (Divine+Scientific+Ethical) + Philosophical
    - Practical Layers: Architecture + Development + Operations + Quality + UX + Data
    
    This provides clear separation between foundational principles and practical
    engineering excellence while maintaining comprehensive validation.
    """
    
    def __init__(self, config: FoundationPracticalAgentConfig, gemini_client=None):
        # Initialize base agent
        super().__init__(config, gemini_client)
        
        # Override state with foundation-practical state
        self.state = FoundationPracticalAgentState(agent_id=config.agent_id)
        self.config = config  # Type hint clarification
        
        # Initialize foundation-practical architecture
        self.onion_architecture = FoundationPracticalOnionArchitecture()
        
        # Initialize compliance tracking
        self.foundation_practical_compliance_required = True
        self.validation_history: List[CompleteValidationResult] = []
        
        # Enhanced logging
        self.logger = logging.getLogger(f"foundation_practical_agent.{config.agent_id}")
        self.logger.info(f"Initialized foundation-practical compliant agent: {config.agent_id}")
    
    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced run method with foundation-practical validation.
        
        Validates through both foundation layers (philosophical) and practical layers
        (software engineering) to ensure comprehensive compliance.
        """
        try:
            # Pre-execution validation
            operation = self._create_operation_from_task(task, "agent_run")
            
            if self.config.enable_foundation_validation or self.config.enable_practical_validation:
                pre_validation = await self._validate_foundation_practical_compliance(operation)
                if not pre_validation.overall_system_ready:
                    raise FoundationPracticalViolation(
                        f"Pre-execution validation failed for {self.config.agent_id}: "
                        f"Operation {operation.operation_id} violates foundation-practical standards. "
                        f"Foundation errors: {pre_validation.foundation_details.error_messages} "
                        f"Practical errors: {pre_validation.practical_details.error_messages}"
                    )
            
            # Execute with monitoring
            result = await self._execute_with_onion_monitoring(task)
            
            # Post-execution validation
            if self.config.enable_foundation_validation or self.config.enable_practical_validation:
                post_operation = self._create_operation_from_task(result, "agent_completion")
                post_validation = await self._validate_foundation_practical_compliance(post_operation)
                
                if not post_validation.overall_system_ready:
                    raise FoundationPracticalViolation(
                        f"Post-execution validation failed for {self.config.agent_id}: "
                        f"Result violates foundation-practical standards. "
                        f"Foundation errors: {post_validation.foundation_details.error_messages} "
                        f"Practical errors: {post_validation.practical_details.error_messages}"
                    )
            
            # Verify system integrity
            self._verify_foundation_practical_integrity()
            
            return result
            
        except FoundationPracticalViolation:
            # Foundation-practical violations are critical and should not be retried
            self.state.status = 'error'
            self.state.error_count += 1
            raise
        except Exception as e:
            # Other exceptions can use normal retry logic
            return await super().run(task)
    
    async def _execute_with_onion_monitoring(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with foundation-practical onion architecture monitoring."""
        start_time = time.time()
        
        try:
            # Call base class run method (which calls execute)
            result = await super().run(task)
            
            # Update validation metrics
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_onion_performance_metrics(execution_time_ms, True)
            
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_onion_performance_metrics(execution_time_ms, False)
            raise
    
    async def _validate_foundation_practical_compliance(self, operation: Operation) -> CompleteValidationResult:
        """
        Validate operation against foundation-practical onion architecture.
        
        Comprehensive validation through all foundation and practical layers.
        """
        try:
            # Perform complete validation through onion architecture
            validation_result = self.onion_architecture.validate_complete_system(operation)
            
            # Store validation result
            self.validation_history.append(validation_result)
            
            # Update state metrics
            self.state.foundation_validations_performed += 1
            self.state.practical_validations_performed += 1
            self.state.total_validation_time_ms += validation_result.total_validation_time_ms
            
            if validation_result.foundation_valid:
                self.state.foundation_validations_passed += 1
            else:
                self.state.foundation_validations_failed += 1
            
            if validation_result.practical_excellent:
                self.state.practical_validations_passed += 1
            else:
                self.state.practical_validations_failed += 1
            
            # Update average validation time
            total_validations = self.state.foundation_validations_performed
            self.state.average_validation_time_ms = (
                self.state.total_validation_time_ms / total_validations
            )
            
            # Update score averages
            self._update_validation_score_averages()
            
            # Check performance threshold
            if (self.config.validation_strict_mode and 
                validation_result.total_validation_time_ms > self.config.performance_threshold_ms):
                self.logger.warning(
                    f"Foundation-practical validation exceeded performance threshold: "
                    f"{validation_result.total_validation_time_ms:.1f}ms > {self.config.performance_threshold_ms}ms"
                )
            
            # Check confidence threshold
            if (self.config.validation_strict_mode and 
                validation_result.confidence_score < self.config.confidence_threshold):
                self.logger.warning(
                    f"Foundation-practical validation confidence below threshold: "
                    f"{validation_result.confidence_score:.3f} < {self.config.confidence_threshold}"
                )
            
            # Log validation result
            log_level = logging.INFO if validation_result.overall_system_ready else logging.ERROR
            self.logger.log(
                log_level,
                f"Foundation-practical validation: {operation.operation_id} - "
                f"Ready: {validation_result.overall_system_ready}, "
                f"Foundation: {validation_result.foundation_details.foundation_score:.3f}, "
                f"Practical: {validation_result.practical_details.practical_excellence_score:.3f}, "
                f"Time: {validation_result.total_validation_time_ms:.1f}ms"
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Foundation-practical validation failed with exception: {e}")
            # Return failed validation result
            from utils.validation.foundation_practical_onion_system import (
                CompleteValidationResult, FoundationValidationResult, PracticalValidationResult
            )
            return CompleteValidationResult(
                foundation_valid=False,
                practical_excellent=False,
                overall_system_ready=False,
                foundation_details=FoundationValidationResult(
                    divinely_aligned=False, scientifically_sound=False, ethically_compliant=False,
                    ontologically_coherent=False, epistemologically_valid=False, logically_consistent=False,
                    foundation_score=0.0, validation_time_ms=0.0, error_messages=[f"Validation exception: {str(e)}"]
                ),
                practical_details=PracticalValidationResult(
                    architecturally_sound=False, development_excellent=False, operationally_robust=False,
                    quality_assured=False, user_centered=False, data_intelligent=False,
                    practical_excellence_score=0.0, validation_time_ms=0.0, error_messages=[f"Validation exception: {str(e)}"]
                ),
                total_validation_time_ms=0.0,
                confidence_score=0.0
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
            "foundation_layer": self.config.foundation_layer.name if self.config.foundation_layer else None,
            "practical_layer": self.config.practical_layer.name if self.config.practical_layer else None
        }
        
        return Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            parameters=parameters,
            context=context,
            timestamp=datetime.now(),
            foundation_layer=self.config.foundation_layer,
            practical_layer=self.config.practical_layer
        )
    
    def _update_validation_score_averages(self):
        """Update validation score averages based on recent history."""
        if not self.validation_history:
            return
        
        recent_validations = self.validation_history[-100:]  # Last 100 validations
        
        foundation_scores = [v.foundation_details.foundation_score for v in recent_validations]
        practical_scores = [v.practical_details.practical_excellence_score for v in recent_validations]
        
        self.state.foundation_score_average = sum(foundation_scores) / len(foundation_scores)
        self.state.practical_score_average = sum(practical_scores) / len(practical_scores)
        
        # Calculate overall compliance score
        self.state.overall_compliance_score = (
            self.state.foundation_score_average * 0.5 +
            self.state.practical_score_average * 0.5
        )
    
    def _update_onion_performance_metrics(self, execution_time_ms: float, success: bool):
        """Update onion architecture performance metrics."""
        # Update base performance metrics
        self.performance_metrics.setdefault('onion_validations', 0)
        self.performance_metrics['onion_validations'] += 1
        
        if success:
            self.performance_metrics.setdefault('onion_validations_successful', 0)
            self.performance_metrics['onion_validations_successful'] += 1
        
        # Update execution time tracking
        self.performance_metrics.setdefault('total_onion_execution_time_ms', 0.0)
        self.performance_metrics['total_onion_execution_time_ms'] += execution_time_ms
        
        self.performance_metrics['average_onion_execution_time_ms'] = (
            self.performance_metrics['total_onion_execution_time_ms'] / 
            self.performance_metrics['onion_validations']
        )
    
    def _verify_foundation_practical_integrity(self):
        """Verify that foundation-practical system integrity is maintained."""
        try:
            # Check onion architecture system status
            system_status = self.onion_architecture.get_system_status()
            
            # Verify foundation compliance
            if system_status.get('total_validations', 0) > 0:
                foundation_success_rate = system_status.get('average_foundation_score', 0.0)
                if foundation_success_rate < 0.8:  # 80% threshold for foundation
                    self.logger.warning(
                        f"Foundation validation average below threshold: {foundation_success_rate:.3f}"
                    )
                
                practical_success_rate = system_status.get('average_practical_score', 0.0)
                if practical_success_rate < 0.8:  # 80% threshold for practical
                    self.logger.warning(
                        f"Practical validation average below threshold: {practical_success_rate:.3f}"
                    )
            
            # Verify agent compliance
            if self.state.foundation_validations_performed > 10:  # Only check after enough data
                if self.state.overall_compliance_score < 0.8:  # 80% compliance threshold
                    self.logger.warning(
                        f"Overall compliance score below threshold: "
                        f"{self.state.overall_compliance_score:.3f}"
                    )
            
            # Keep validation history manageable
            if len(self.validation_history) > 500:
                self.validation_history = self.validation_history[-250:]
            
        except Exception as e:
            self.logger.error(f"Foundation-practical integrity verification failed: {e}")
    
    def get_foundation_practical_status(self) -> Dict[str, Any]:
        """
        Get comprehensive foundation-practical status for monitoring.
        
        Returns:
            Dictionary containing all foundation-practical metrics and status
        """
        return {
            "agent_id": self.config.agent_id,
            "foundation_practical_compliance_required": self.foundation_practical_compliance_required,
            "foundation_validation_enabled": self.config.enable_foundation_validation,
            "practical_validation_enabled": self.config.enable_practical_validation,
            "strict_mode": self.config.validation_strict_mode,
            "foundation_layer": self.config.foundation_layer.name if self.config.foundation_layer else None,
            "practical_layer": self.config.practical_layer.name if self.config.practical_layer else None,
            
            # Foundation metrics
            "foundation_validations_performed": self.state.foundation_validations_performed,
            "foundation_validations_passed": self.state.foundation_validations_passed,
            "foundation_validations_failed": self.state.foundation_validations_failed,
            "foundation_success_rate": (
                self.state.foundation_validations_passed / max(1, self.state.foundation_validations_performed)
            ),
            "foundation_score_average": self.state.foundation_score_average,
            
            # Practical metrics
            "practical_validations_performed": self.state.practical_validations_performed,
            "practical_validations_passed": self.state.practical_validations_passed,
            "practical_validations_failed": self.state.practical_validations_failed,
            "practical_success_rate": (
                self.state.practical_validations_passed / max(1, self.state.practical_validations_performed)
            ),
            "practical_score_average": self.state.practical_score_average,
            
            # Performance metrics
            "average_validation_time_ms": self.state.average_validation_time_ms,
            "total_validation_time_ms": self.state.total_validation_time_ms,
            
            # Overall compliance
            "overall_compliance_score": self.state.overall_compliance_score,
            
            # System status
            "onion_architecture_status": self.onion_architecture.get_system_status(),
            
            # Recent validation history
            "recent_validations": len(self.validation_history),
            "recent_validation_results": [
                {
                    "overall_ready": v.overall_system_ready,
                    "foundation_score": v.foundation_details.foundation_score,
                    "practical_score": v.practical_details.practical_excellence_score,
                    "confidence_score": v.confidence_score,
                    "validation_time_ms": v.total_validation_time_ms
                }
                for v in self.validation_history[-10:]  # Last 10 validations
            ]
        }
    
    def validate_foundation_practical_compliance_sync(self, operation_id: str, operation_type: str, 
                                                     parameters: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """
        Synchronous validation for non-async contexts.
        
        Args:
            operation_id: Unique operation identifier
            operation_type: Type of operation
            parameters: Operation parameters
            context: Optional context
            
        Returns:
            True if operation passes all foundation-practical validations
        """
        operation = Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            parameters=parameters,
            context=context or {},
            timestamp=datetime.now(),
            foundation_layer=self.config.foundation_layer,
            practical_layer=self.config.practical_layer
        )
        
        validation_result = self.onion_architecture.validate_complete_system(operation)
        
        if not validation_result.overall_system_ready:
            self.logger.error(
                f"Foundation-practical compliance validation failed for {operation_id}: "
                f"Foundation errors: {validation_result.foundation_details.error_messages} "
                f"Practical errors: {validation_result.practical_details.error_messages}"
            )
        
        return validation_result.overall_system_ready


# Utility function for creating foundation-practical compliant agents
def create_foundation_practical_compliant_agent(agent_id: str, agent_type: str, 
                                               foundation_layer: FoundationLayer = FoundationLayer.UNIVERSAL_FOUNDATION,
                                               practical_layer: PracticalLayer = PracticalLayer.SOFTWARE_ARCHITECTURE,
                                               **kwargs) -> FoundationPracticalAgentConfig:
    """
    Utility function for creating foundation-practical compliant agent configurations.
    
    Args:
        agent_id: Unique agent identifier
        agent_type: Type of agent
        foundation_layer: Foundation layer for validation
        practical_layer: Practical layer for validation
        **kwargs: Additional configuration parameters
        
    Returns:
        FoundationPracticalAgentConfig instance
    """
    return FoundationPracticalAgentConfig(
        agent_id=agent_id,
        agent_type=agent_type,
        prompt_template_id=f"{agent_type}_template",
        foundation_layer=foundation_layer,
        practical_layer=practical_layer,
        **kwargs
    )


if __name__ == "__main__":
    # Example usage and testing
    import asyncio
    
    async def test_foundation_practical_compliant_agent():
        """Test the foundation-practical compliant agent."""
        # Create test configuration
        config = create_foundation_practical_compliant_agent(
            agent_id="test_foundation_practical_agent",
            agent_type="testing_agent",
            foundation_layer=FoundationLayer.UNIVERSAL_FOUNDATION,
            practical_layer=PracticalLayer.SOFTWARE_ARCHITECTURE
        )
        
        # Create concrete test agent class
        class TestFoundationPracticalAgent(FoundationPracticalCompliantAgent):
            async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "result": "test_completed", 
                    "task": task,
                    "approach": "clean architecture with TDD",
                    "purpose": "help users"
                }
            
            def validate_task(self, task: Dict[str, Any]) -> bool:
                return isinstance(task, dict) and "test_type" in task
        
        # Test agent
        agent = TestFoundationPracticalAgent(config)
        
        test_task = {
            "test_type": "foundation_practical_validation",
            "description": "Test foundation-practical validation system",
            "goal": "improve system quality",
            "method": "test-driven development",
            "approach": "user-centered design"
        }
        
        try:
            result = await agent.run(test_task)
            print("✅ Test passed - Agent executed with foundation-practical validation")
            print(f"Result: {result}")
            
            # Get status
            status = agent.get_foundation_practical_status()
            print(f"Foundation Score: {status['foundation_score_average']:.3f}")
            print(f"Practical Score: {status['practical_score_average']:.3f}")
            print(f"Overall Compliance: {status['overall_compliance_score']:.3f}")
            
        except FoundationPracticalViolation as e:
            print(f"❌ Foundation-practical violation: {e}")
        except Exception as e:
            print(f"❌ Execution error: {e}")
    
    # Run test
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_foundation_practical_compliant_agent())

