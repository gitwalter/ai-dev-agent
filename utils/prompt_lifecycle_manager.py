"""
Prompt Lifecycle Manager - Task 3.2 Implementation

This module implements the comprehensive prompt lifecycle manager that orchestrates the complete workflow.
Following our systematic approach and rules for reliable, testable, and optimized prompt management.

Key Features:
- Complete prompt lifecycle orchestration
- Automated workflow management
- Quality gates and validation
- Performance monitoring and analytics
- Integration with all frameworks (testing, optimization, MCP)
- Advanced reporting and insights
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

from .prompt_engineering_framework import (
    PromptTestingFramework, 
    WorkflowMode, 
    OptimizedPrompt,
    PromptTestResults
)
from .prompt_optimizer import (
    PromptOptimizer,
    OptimizationResult,
    OptimizationConfig
)
from .mcp_prompt_manager import (
    MCPPromptManager,
    MCPPrompt,
    PromptStatus,
    PromptVersion
)

# Configure logging
logger = logging.getLogger(__name__)

class LifecycleStage(Enum):
    """Lifecycle stages"""
    CREATION = "creation"
    TESTING = "testing"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    APPROVAL = "approval"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"

class QualityGate(Enum):
    """Quality gates"""
    SYNTAX_VALIDATION = "syntax_validation"
    FUNCTIONAL_TESTING = "functional_testing"
    PERFORMANCE_TESTING = "performance_testing"
    OPTIMIZATION_VALIDATION = "optimization_validation"
    INTEGRATION_TESTING = "integration_testing"
    APPROVAL_REVIEW = "approval_review"
    DEPLOYMENT_READINESS = "deployment_readiness"

@dataclass
class LifecycleEvent:
    """Lifecycle event record"""
    event_id: str
    prompt_id: str
    stage: LifecycleStage
    timestamp: datetime
    user: str
    details: Dict[str, Any]
    status: str = "completed"
    duration: Optional[float] = None

@dataclass
class QualityGateResult:
    """Quality gate result"""
    gate: QualityGate
    passed: bool
    score: float
    details: Dict[str, Any]
    timestamp: datetime
    duration: float

@dataclass
class LifecycleMetrics:
    """Lifecycle performance metrics"""
    total_duration: float
    stage_durations: Dict[LifecycleStage, float]
    quality_gate_results: List[QualityGateResult]
    performance_improvements: List[float]
    error_count: int
    success_rate: float

class PromptLifecycleManager:
    """
    Comprehensive prompt lifecycle manager
    
    Implements complete workflow orchestration:
    - Complete prompt lifecycle orchestration
    - Automated workflow management
    - Quality gates and validation
    - Performance monitoring and analytics
    - Integration with all frameworks
    - Advanced reporting and insights
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.testing_framework = PromptTestingFramework()
        self.optimizer = PromptOptimizer()
        self.mcp_manager = MCPPromptManager()
        
        # Lifecycle tracking
        self.active_lifecycles: Dict[str, Dict[str, Any]] = {}
        self.lifecycle_events: List[LifecycleEvent] = []
        self.quality_gate_results: List[QualityGateResult] = []
        
        logger.info("PromptLifecycleManager initialized with all frameworks")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'enable_automated_optimization': True,
            'enable_quality_gates': True,
            'enable_performance_monitoring': True,
            'quality_threshold': 0.8,
            'max_optimization_iterations': 5,
            'automated_approval': False,
            'enable_rollback': True,
            'monitoring_duration_days': 30
        }
    
    async def start_lifecycle(
        self,
        prompt: str,
        agent_type: str,
        mode: WorkflowMode,
        created_by: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        target_metrics: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Start a new prompt lifecycle
        
        Args:
            prompt: The prompt content
            agent_type: Type of agent
            mode: Workflow mode
            created_by: Creator identifier
            description: Prompt description
            tags: Prompt tags
            target_metrics: Target performance metrics
            
        Returns:
            str: Lifecycle ID
        """
        logger.info(f"Starting new prompt lifecycle for {agent_type} in {mode.value} mode")
        
        try:
            # Generate lifecycle ID
            lifecycle_id = str(uuid.uuid4())
            
            # Create MCP prompt
            mcp_prompt = await self.mcp_manager.create_prompt(
                prompt, agent_type, mode, created_by, description, tags
            )
            
            # Initialize lifecycle tracking
            self.active_lifecycles[lifecycle_id] = {
                'prompt_id': mcp_prompt.metadata.prompt_id,
                'stage': LifecycleStage.CREATION,
                'start_time': time.time(),
                'target_metrics': target_metrics,
                'quality_gates_passed': [],
                'current_iteration': 0
            }
            
            # Record lifecycle event
            await self._record_lifecycle_event(
                lifecycle_id, mcp_prompt.metadata.prompt_id,
                LifecycleStage.CREATION, created_by,
                {'prompt_length': len(prompt), 'agent_type': agent_type, 'mode': mode.value}
            )
            
            logger.info(f"Lifecycle started successfully. ID: {lifecycle_id}")
            return lifecycle_id
            
        except Exception as e:
            logger.error(f"Failed to start lifecycle: {e}")
            raise
    
    async def execute_lifecycle(self, lifecycle_id: str, user: str) -> MCPPrompt:
        """
        Execute the complete prompt lifecycle
        
        Args:
            lifecycle_id: Lifecycle identifier
            user: User executing the lifecycle
            
        Returns:
            MCPPrompt: Final deployed prompt
        """
        logger.info(f"Executing lifecycle: {lifecycle_id}")
        
        try:
            lifecycle_info = self.active_lifecycles.get(lifecycle_id)
            if not lifecycle_info:
                raise ValueError(f"Lifecycle not found: {lifecycle_id}")
            
            prompt_id = lifecycle_info['prompt_id']
            target_metrics = lifecycle_info.get('target_metrics')
            
            # Stage 1: Testing
            await self._execute_testing_stage(lifecycle_id, prompt_id, user)
            
            # Stage 2: Optimization
            if self.config['enable_automated_optimization']:
                await self._execute_optimization_stage(lifecycle_id, prompt_id, user, target_metrics)
            
            # Stage 3: Validation
            if self.config['enable_quality_gates']:
                await self._execute_validation_stage(lifecycle_id, prompt_id, user)
            
            # Stage 4: Approval
            await self._execute_approval_stage(lifecycle_id, prompt_id, user)
            
            # Stage 5: Deployment
            final_prompt = await self._execute_deployment_stage(lifecycle_id, prompt_id, user)
            
            # Stage 6: Monitoring
            if self.config['enable_performance_monitoring']:
                await self._execute_monitoring_stage(lifecycle_id, prompt_id, user)
            
            logger.info(f"Lifecycle completed successfully: {lifecycle_id}")
            return final_prompt
            
        except Exception as e:
            logger.error(f"Lifecycle execution failed: {e}")
            await self._handle_lifecycle_failure(lifecycle_id, user, str(e))
            raise
    
    async def _execute_testing_stage(self, lifecycle_id: str, prompt_id: str, user: str):
        """Execute testing stage"""
        logger.info(f"Executing testing stage for lifecycle: {lifecycle_id}")
        
        start_time = time.time()
        
        try:
            # Update lifecycle stage
            self.active_lifecycles[lifecycle_id]['stage'] = LifecycleStage.TESTING
            
            # Run comprehensive testing
            test_results = await self.mcp_manager.test_prompt(prompt_id)
            
            # Quality gate: Functional testing
            quality_result = QualityGateResult(
                gate=QualityGate.FUNCTIONAL_TESTING,
                passed=test_results.all_tests_passed,
                score=test_results.overall_score,
                details={'test_results': test_results.__dict__},
                timestamp=datetime.now(),
                duration=time.time() - start_time
            )
            
            self.quality_gate_results.append(quality_result)
            self.active_lifecycles[lifecycle_id]['quality_gates_passed'].append(QualityGate.FUNCTIONAL_TESTING)
            
            # Record event
            await self._record_lifecycle_event(
                lifecycle_id, prompt_id, LifecycleStage.TESTING, user,
                {'test_score': test_results.overall_score, 'all_tests_passed': test_results.all_tests_passed}
            )
            
            logger.info(f"Testing stage completed. Score: {test_results.overall_score:.3f}")
            
        except Exception as e:
            logger.error(f"Testing stage failed: {e}")
            raise
    
    async def _execute_optimization_stage(self, lifecycle_id: str, prompt_id: str, user: str, target_metrics: Optional[Dict[str, float]] = None):
        """Execute optimization stage"""
        logger.info(f"Executing optimization stage for lifecycle: {lifecycle_id}")
        
        start_time = time.time()
        
        try:
            # Update lifecycle stage
            self.active_lifecycles[lifecycle_id]['stage'] = LifecycleStage.OPTIMIZATION
            
            # Run optimization
            optimization_result = await self.mcp_manager.optimize_prompt(prompt_id, target_metrics)
            
            # Quality gate: Optimization validation
            quality_result = QualityGateResult(
                gate=QualityGate.OPTIMIZATION_VALIDATION,
                passed=optimization_result.performance_improvement > 0,
                score=optimization_result.confidence_score,
                details={'optimization_result': optimization_result.__dict__},
                timestamp=datetime.now(),
                duration=time.time() - start_time
            )
            
            self.quality_gate_results.append(quality_result)
            self.active_lifecycles[lifecycle_id]['quality_gates_passed'].append(QualityGate.OPTIMIZATION_VALIDATION)
            
            # Record event
            await self._record_lifecycle_event(
                lifecycle_id, prompt_id, LifecycleStage.OPTIMIZATION, user,
                {'improvement': optimization_result.performance_improvement, 'confidence': optimization_result.confidence_score}
            )
            
            logger.info(f"Optimization stage completed. Improvement: {optimization_result.performance_improvement:.3f}")
            
        except Exception as e:
            logger.error(f"Optimization stage failed: {e}")
            raise
    
    async def _execute_validation_stage(self, lifecycle_id: str, prompt_id: str, user: str):
        """Execute validation stage"""
        logger.info(f"Executing validation stage for lifecycle: {lifecycle_id}")
        
        start_time = time.time()
        
        try:
            # Update lifecycle stage
            self.active_lifecycles[lifecycle_id]['stage'] = LifecycleStage.VALIDATION
            
            # Get current prompt
            mcp_prompt = await self.mcp_manager.get_prompt(prompt_id)
            if not mcp_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Run additional validation tests
            validation_results = await self._run_validation_tests(mcp_prompt)
            
            # Quality gate: Performance testing
            quality_result = QualityGateResult(
                gate=QualityGate.PERFORMANCE_TESTING,
                passed=validation_results['performance_score'] >= self.config['quality_threshold'],
                score=validation_results['performance_score'],
                details=validation_results,
                timestamp=datetime.now(),
                duration=time.time() - start_time
            )
            
            self.quality_gate_results.append(quality_result)
            self.active_lifecycles[lifecycle_id]['quality_gates_passed'].append(QualityGate.PERFORMANCE_TESTING)
            
            # Record event
            await self._record_lifecycle_event(
                lifecycle_id, prompt_id, LifecycleStage.VALIDATION, user,
                validation_results
            )
            
            logger.info(f"Validation stage completed. Performance score: {validation_results['performance_score']:.3f}")
            
        except Exception as e:
            logger.error(f"Validation stage failed: {e}")
            raise
    
    async def _execute_approval_stage(self, lifecycle_id: str, prompt_id: str, user: str):
        """Execute approval stage"""
        logger.info(f"Executing approval stage for lifecycle: {lifecycle_id}")
        
        start_time = time.time()
        
        try:
            # Update lifecycle stage
            self.active_lifecycles[lifecycle_id]['stage'] = LifecycleStage.APPROVAL
            
            # Check if automated approval is enabled
            if self.config['automated_approval']:
                # Auto-approve if all quality gates passed
                quality_gates_passed = self.active_lifecycles[lifecycle_id]['quality_gates_passed']
                if len(quality_gates_passed) >= 3:  # Minimum required gates
                    await self.mcp_manager.approve_prompt(prompt_id, user)
                    approval_status = "automated"
                else:
                    approval_status = "manual_required"
            else:
                # Manual approval required
                approval_status = "manual_required"
            
            # Quality gate: Approval review
            quality_result = QualityGateResult(
                gate=QualityGate.APPROVAL_REVIEW,
                passed=approval_status == "automated",
                score=1.0 if approval_status == "automated" else 0.0,
                details={'approval_status': approval_status},
                timestamp=datetime.now(),
                duration=time.time() - start_time
            )
            
            self.quality_gate_results.append(quality_result)
            
            # Record event
            await self._record_lifecycle_event(
                lifecycle_id, prompt_id, LifecycleStage.APPROVAL, user,
                {'approval_status': approval_status}
            )
            
            logger.info(f"Approval stage completed. Status: {approval_status}")
            
        except Exception as e:
            logger.error(f"Approval stage failed: {e}")
            raise
    
    async def _execute_deployment_stage(self, lifecycle_id: str, prompt_id: str, user: str) -> MCPPrompt:
        """Execute deployment stage"""
        logger.info(f"Executing deployment stage for lifecycle: {lifecycle_id}")
        
        start_time = time.time()
        
        try:
            # Update lifecycle stage
            self.active_lifecycles[lifecycle_id]['stage'] = LifecycleStage.DEPLOYMENT
            
            # Deploy prompt
            deployed_prompt = await self.mcp_manager.deploy_prompt(prompt_id, user)
            
            # Quality gate: Deployment readiness
            quality_result = QualityGateResult(
                gate=QualityGate.DEPLOYMENT_READINESS,
                passed=deployed_prompt.metadata.status == PromptStatus.DEPLOYED,
                score=1.0 if deployed_prompt.metadata.status == PromptStatus.DEPLOYED else 0.0,
                details={'deployment_status': deployed_prompt.metadata.status.value},
                timestamp=datetime.now(),
                duration=time.time() - start_time
            )
            
            self.quality_gate_results.append(quality_result)
            self.active_lifecycles[lifecycle_id]['quality_gates_passed'].append(QualityGate.DEPLOYMENT_READINESS)
            
            # Record event
            await self._record_lifecycle_event(
                lifecycle_id, prompt_id, LifecycleStage.DEPLOYMENT, user,
                {'deployment_status': deployed_prompt.metadata.status.value}
            )
            
            logger.info(f"Deployment stage completed successfully")
            return deployed_prompt
            
        except Exception as e:
            logger.error(f"Deployment stage failed: {e}")
            raise
    
    async def _execute_monitoring_stage(self, lifecycle_id: str, prompt_id: str, user: str):
        """Execute monitoring stage"""
        logger.info(f"Executing monitoring stage for lifecycle: {lifecycle_id}")
        
        start_time = time.time()
        
        try:
            # Update lifecycle stage
            self.active_lifecycles[lifecycle_id]['stage'] = LifecycleStage.MONITORING
            
            # Get analytics
            analytics = await self.mcp_manager.get_prompt_analytics(prompt_id, self.config['monitoring_duration_days'])
            
            # Record event
            await self._record_lifecycle_event(
                lifecycle_id, prompt_id, LifecycleStage.MONITORING, user,
                {'analytics_summary': self._summarize_analytics(analytics)}
            )
            
            logger.info(f"Monitoring stage completed")
            
        except Exception as e:
            logger.error(f"Monitoring stage failed: {e}")
            raise
    
    async def _run_validation_tests(self, mcp_prompt: MCPPrompt) -> Dict[str, Any]:
        """Run additional validation tests"""
        try:
            # Run comprehensive testing again
            test_results = await self.testing_framework.comprehensive_test_prompt(
                mcp_prompt.prompt,
                mcp_prompt.metadata.agent_type,
                mcp_prompt.metadata.mode
            )
            
            # Calculate performance score
            performance_score = test_results.overall_score
            
            # Additional validation checks
            validation_results = {
                'performance_score': performance_score,
                'test_results': test_results.__dict__,
                'prompt_length': len(mcp_prompt.prompt),
                'version': mcp_prompt.metadata.version,
                'optimization_count': len(mcp_prompt.metadata.optimization_history)
            }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation tests failed: {e}")
            return {'performance_score': 0.0, 'error': str(e)}
    
    def _summarize_analytics(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize analytics data"""
        try:
            summary = {
                'total_metrics': 0,
                'metric_types': [],
                'average_performance': 0.0
            }
            
            for metric_type, data in analytics.items():
                if isinstance(data, list) and data:
                    summary['total_metrics'] += len(data)
                    summary['metric_types'].append(metric_type)
                    
                    # Calculate average for performance metrics
                    if 'performance' in metric_type.lower():
                        values = [item['value'] for item in data if 'value' in item]
                        if values:
                            summary['average_performance'] = sum(values) / len(values)
            
            return summary
            
        except Exception as e:
            logger.error(f"Analytics summarization failed: {e}")
            return {'error': str(e)}
    
    async def _record_lifecycle_event(
        self,
        lifecycle_id: str,
        prompt_id: str,
        stage: LifecycleStage,
        user: str,
        details: Dict[str, Any]
    ):
        """Record lifecycle event"""
        event = LifecycleEvent(
            event_id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            stage=stage,
            timestamp=datetime.now(),
            user=user,
            details=details
        )
        
        self.lifecycle_events.append(event)
    
    async def _handle_lifecycle_failure(self, lifecycle_id: str, user: str, error_message: str):
        """Handle lifecycle failure"""
        logger.error(f"Lifecycle {lifecycle_id} failed: {error_message}")
        
        # Record failure event
        await self._record_lifecycle_event(
            lifecycle_id, "", LifecycleStage.MONITORING, user,
            {'error': error_message, 'status': 'failed'}
        )
        
        # Update lifecycle status
        if lifecycle_id in self.active_lifecycles:
            self.active_lifecycles[lifecycle_id]['status'] = 'failed'
            self.active_lifecycles[lifecycle_id]['error'] = error_message
    
    async def get_lifecycle_metrics(self, lifecycle_id: str) -> Optional[LifecycleMetrics]:
        """Get lifecycle performance metrics"""
        try:
            lifecycle_info = self.active_lifecycles.get(lifecycle_id)
            if not lifecycle_info:
                return None
            
            # Calculate metrics
            start_time = lifecycle_info['start_time']
            total_duration = time.time() - start_time
            
            # Calculate stage durations
            stage_durations = {}
            events = [e for e in self.lifecycle_events if e.prompt_id == lifecycle_info['prompt_id']]
            
            for i, event in enumerate(events):
                if i > 0:
                    duration = (event.timestamp - events[i-1].timestamp).total_seconds()
                    stage_durations[event.stage] = duration
            
            # Get quality gate results
            quality_results = [q for q in self.quality_gate_results if q.timestamp >= datetime.fromtimestamp(start_time)]
            
            # Calculate success rate
            success_count = sum(1 for event in events if event.status == 'completed')
            success_rate = success_count / len(events) if events else 0.0
            
            # Calculate performance improvements
            performance_improvements = []
            for result in quality_results:
                if result.gate == QualityGate.OPTIMIZATION_VALIDATION:
                    performance_improvements.append(result.score)
            
            metrics = LifecycleMetrics(
                total_duration=total_duration,
                stage_durations=stage_durations,
                quality_gate_results=quality_results,
                performance_improvements=performance_improvements,
                error_count=sum(1 for event in events if event.status == 'failed'),
                success_rate=success_rate
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle metrics: {e}")
            return None
    
    async def get_lifecycle_report(self, lifecycle_id: str) -> Dict[str, Any]:
        """Generate comprehensive lifecycle report"""
        try:
            lifecycle_info = self.active_lifecycles.get(lifecycle_id)
            if not lifecycle_info:
                return {'error': 'Lifecycle not found'}
            
            # Get metrics
            metrics = await self.get_lifecycle_metrics(lifecycle_id)
            
            # Get prompt details
            prompt = await self.mcp_manager.get_prompt(lifecycle_info['prompt_id'])
            
            # Generate report
            report = {
                'lifecycle_id': lifecycle_id,
                'prompt_id': lifecycle_info['prompt_id'],
                'status': lifecycle_info.get('status', 'active'),
                'current_stage': lifecycle_info['stage'].value,
                'start_time': datetime.fromtimestamp(lifecycle_info['start_time']).isoformat(),
                'total_duration': metrics.total_duration if metrics else 0.0,
                'success_rate': metrics.success_rate if metrics else 0.0,
                'quality_gates_passed': len(lifecycle_info['quality_gates_passed']),
                'prompt_details': {
                    'agent_type': prompt.metadata.agent_type if prompt else 'unknown',
                    'mode': prompt.metadata.mode.value if prompt else 'unknown',
                    'version': prompt.metadata.version if prompt else 'unknown',
                    'status': prompt.metadata.status.value if prompt else 'unknown'
                },
                'stage_durations': metrics.stage_durations if metrics else {},
                'quality_gate_results': [q.__dict__ for q in metrics.quality_gate_results] if metrics else [],
                'performance_improvements': metrics.performance_improvements if metrics else [],
                'events': [e.__dict__ for e in self.lifecycle_events if e.prompt_id == lifecycle_info['prompt_id']]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate lifecycle report: {e}")
            return {'error': str(e)}

# Main function for testing
async def main():
    """Test the prompt lifecycle manager"""
    logger.info("Testing Prompt Lifecycle Manager")
    
    # Initialize manager
    manager = PromptLifecycleManager()
    
    # Test prompt
    test_prompt = """
    You are a requirements analyst. Your task is to analyze the following requirements and extract functional and non-functional requirements.
    
    Output Format:
    - Functional Requirements: List of functional requirements
    - Non-Functional Requirements: List of non-functional requirements
    - Constraints: List of constraints
    
    Requirements: {requirements}
    """
    
    # Start lifecycle
    lifecycle_id = await manager.start_lifecycle(
        test_prompt,
        "requirements_analyst",
        WorkflowMode.WATERFALL,
        "test_user",
        "Test requirements analysis prompt lifecycle",
        ["requirements", "analysis", "lifecycle"]
    )
    
    logger.info(f"Started lifecycle with ID: {lifecycle_id}")
    
    # Execute lifecycle
    final_prompt = await manager.execute_lifecycle(lifecycle_id, "test_user")
    
    logger.info(f"Lifecycle completed. Final status: {final_prompt.metadata.status.value}")
    
    # Get report
    report = await manager.get_lifecycle_report(lifecycle_id)
    logger.info(f"Lifecycle report generated. Success rate: {report.get('success_rate', 0):.2f}")

if __name__ == "__main__":
    asyncio.run(main())
