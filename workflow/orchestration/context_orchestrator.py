#!/usr/bin/env python3
"""
Context Orchestrator for the Workflow Composition Engine.
Manages execution across multiple @keyword contexts with seamless transitions.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
import traceback

from workflow.models.workflow_models import (
    WorkflowDefinition, WorkflowState, WorkflowResult, WorkflowPhase,
    PhaseStatus, WorkflowStatus, RecoveryAction, ExecutionMetrics, ValidationResult
)

logger = logging.getLogger(__name__)


class ContextOrchestrator:
    """
    Manages execution across multiple @keyword contexts with state management.
    
    This class handles:
    1. Sequential and parallel phase execution
    2. Context transitions and state management
    3. Result propagation between phases
    4. Error recovery and rollback
    5. Integration with context-aware rule system
    """
    
    def __init__(self, context_switcher=None, rule_loader=None, agent_manager=None):
        """
        Initialize the context orchestrator.
        
        Args:
            context_switcher: Context switching implementation
            rule_loader: Rule loading system
            agent_manager: Agent management system
        """
        self.context_switcher = context_switcher
        self.rule_loader = rule_loader
        self.agent_manager = agent_manager
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.execution_callbacks: Dict[str, List[Callable]] = {}
        self.recovery_strategies = self._build_recovery_strategies()
        
    async def execute_workflow(self, workflow: WorkflowDefinition, initial_context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        Execute complete workflow with context orchestration.
        
        Args:
            workflow: Workflow definition to execute
            initial_context: Initial context data
            
        Returns:
            Complete workflow execution results
        """
        logger.info(f"Starting workflow execution: {workflow.workflow_id}")
        
        # Initialize workflow state
        state = self._initialize_workflow_state(workflow, initial_context or {})
        self.active_workflows[workflow.workflow_id] = state
        
        try:
            # Execute workflow phases
            await self._execute_workflow_phases(workflow, state)
            
            # Finalize workflow
            result = self._finalize_workflow(workflow, state)
            
            logger.info(f"Workflow completed successfully: {workflow.workflow_id}")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {workflow.workflow_id}, error: {e}")
            return self._handle_workflow_failure(workflow, state, e)
        
        finally:
            # Cleanup
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
    
    async def transition_context(self, from_context: str, to_context: str, state: WorkflowState) -> WorkflowState:
        """
        Handle smooth transition between contexts.
        
        Args:
            from_context: Source @keyword context
            to_context: Target @keyword context
            state: Current workflow state
            
        Returns:
            Updated workflow state after transition
        """
        logger.info(f"Transitioning context: {from_context} -> {to_context}")
        
        try:
            # Validate transition
            if not self._validate_context_transition(from_context, to_context, state):
                raise ValueError(f"Invalid context transition: {from_context} -> {to_context}")
            
            # Save current context state
            if from_context:
                state.context_data[from_context] = self._capture_context_state(from_context, state)
            
            # Switch to new context
            if self.context_switcher:
                await self.context_switcher.switch_context(to_context, state)
            
            # Load context-specific rules
            if self.rule_loader:
                rules = await self.rule_loader.load_context_rules(to_context)
                state.context_data[f"{to_context}_rules"] = rules
            
            # Update state
            state.current_phase = to_context
            state.last_updated = datetime.now()
            
            logger.info(f"Context transition completed: {to_context}")
            return state
            
        except Exception as e:
            logger.error(f"Context transition failed: {from_context} -> {to_context}, error: {e}")
            raise
    
    async def propagate_results(self, from_phase: str, to_phase: str, results: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """
        Propagate outputs from one phase as inputs to the next.
        
        Args:
            from_phase: Source phase ID
            to_phase: Target phase ID
            results: Results from source phase
            state: Current workflow state
            
        Returns:
            Processed inputs for target phase
        """
        logger.debug(f"Propagating results: {from_phase} -> {to_phase}")
        
        try:
            # Store results from source phase
            state.phase_results[from_phase] = results
            
            # Transform results for target phase
            transformed_results = self._transform_phase_results(from_phase, to_phase, results, state)
            
            # Validate propagated data
            validation = self._validate_propagated_data(to_phase, transformed_results)
            if not validation.passed:
                logger.warning(f"Data propagation validation issues: {validation.messages}")
            
            logger.debug(f"Results propagated successfully: {len(transformed_results)} items")
            return transformed_results
            
        except Exception as e:
            logger.error(f"Result propagation failed: {from_phase} -> {to_phase}, error: {e}")
            return {}
    
    async def handle_failure(self, context: str, error: Exception, state: WorkflowState) -> RecoveryAction:
        """
        Handle failures with graceful recovery.
        
        Args:
            context: Context where failure occurred
            error: Exception that occurred
            state: Current workflow state
            
        Returns:
            Recovery action to take
        """
        logger.error(f"Handling failure in context {context}: {error}")
        
        # Determine recovery strategy
        recovery_action = self._determine_recovery_action(context, error, state)
        
        # Execute recovery action
        await self._execute_recovery_action(recovery_action, context, state)
        
        # Update state
        state.errors.append(f"Context {context}: {str(error)}")
        state.last_updated = datetime.now()
        
        logger.info(f"Recovery action executed: {recovery_action.action_type}")
        return recovery_action
    
    async def _execute_workflow_phases(self, workflow: WorkflowDefinition, state: WorkflowState) -> None:
        """Execute all workflow phases in the correct order."""
        state.status = WorkflowStatus.RUNNING
        state.start_time = datetime.now()
        
        # Build execution plan
        execution_plan = self._build_execution_plan(workflow)
        
        # Execute phases according to plan
        for phase_group in execution_plan:
            if isinstance(phase_group, list):
                # Parallel execution
                await self._execute_parallel_phases(phase_group, workflow, state)
            else:
                # Sequential execution
                await self._execute_single_phase(phase_group, workflow, state)
            
            # Check for early termination
            if state.status in [WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                break
        
        # Update final status
        if state.status == WorkflowStatus.RUNNING:
            state.status = WorkflowStatus.COMPLETED
        
        state.end_time = datetime.now()
    
    async def _execute_single_phase(self, phase: WorkflowPhase, workflow: WorkflowDefinition, state: WorkflowState) -> None:
        """Execute a single workflow phase."""
        logger.info(f"Executing phase: {phase.name} ({phase.context})")
        
        try:
            # Update phase status
            state.phase_status[phase.phase_id] = PhaseStatus.RUNNING
            state.current_phase = phase.phase_id
            
            # Prepare phase inputs
            phase_inputs = self._prepare_phase_inputs(phase, state)
            
            # Transition to phase context
            previous_context = getattr(state, 'previous_context', None)
            await self.transition_context(previous_context, phase.context, state)
            state.previous_context = phase.context
            
            # Execute phase with timeout
            phase_results = await asyncio.wait_for(
                self._execute_phase_logic(phase, phase_inputs, state),
                timeout=phase.timeout
            )
            
            # Validate phase results
            validation = self._validate_phase_results(phase, phase_results)
            if not validation.passed:
                raise ValueError(f"Phase validation failed: {validation.messages}")
            
            # Store results
            state.phase_results[phase.phase_id] = phase_results
            state.phase_status[phase.phase_id] = PhaseStatus.COMPLETED
            state.completed_phases.append(phase.phase_id)
            
            # Record metrics
            await self._record_phase_metrics(phase, phase_results, state)
            
            logger.info(f"Phase completed successfully: {phase.name}")
            
        except asyncio.TimeoutError:
            logger.error(f"Phase timeout: {phase.name}")
            state.phase_status[phase.phase_id] = PhaseStatus.FAILED
            state.failed_phases.append(phase.phase_id)
            await self._handle_phase_timeout(phase, state)
            
        except Exception as e:
            logger.error(f"Phase execution failed: {phase.name}, error: {e}")
            state.phase_status[phase.phase_id] = PhaseStatus.FAILED
            state.failed_phases.append(phase.phase_id)
            
            # Attempt recovery
            recovery_action = await self.handle_failure(phase.context, e, state)
            
            if recovery_action.action_type == "abort":
                state.status = WorkflowStatus.FAILED
                raise
            elif recovery_action.action_type == "skip":
                state.phase_status[phase.phase_id] = PhaseStatus.SKIPPED
                logger.info(f"Phase skipped due to recovery: {phase.name}")
    
    async def _execute_parallel_phases(self, phases: List[WorkflowPhase], workflow: WorkflowDefinition, state: WorkflowState) -> None:
        """Execute multiple phases in parallel."""
        logger.info(f"Executing {len(phases)} phases in parallel")
        
        # Create tasks for parallel execution
        tasks = []
        for phase in phases:
            task = asyncio.create_task(self._execute_single_phase(phase, workflow, state))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Parallel phase failed: {phases[i].name}, error: {result}")
    
    async def _execute_phase_logic(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute the actual phase logic."""
        # This is where we would integrate with the actual execution engines
        # For now, simulate phase execution
        
        logger.debug(f"Executing phase logic: {phase.name}")
        
        # Simulate context-specific execution
        if phase.context == '@agile':
            return await self._execute_agile_phase(phase, inputs, state)
        elif phase.context == '@design':
            return await self._execute_design_phase(phase, inputs, state)
        elif phase.context == '@code':
            return await self._execute_code_phase(phase, inputs, state)
        elif phase.context == '@test':
            return await self._execute_test_phase(phase, inputs, state)
        elif phase.context == '@debug':
            return await self._execute_debug_phase(phase, inputs, state)
        elif phase.context == '@docs':
            return await self._execute_docs_phase(phase, inputs, state)
        elif phase.context == '@security':
            return await self._execute_security_phase(phase, inputs, state)
        elif phase.context == '@optimize':
            return await self._execute_optimize_phase(phase, inputs, state)
        elif phase.context == '@git':
            return await self._execute_git_phase(phase, inputs, state)
        else:
            return await self._execute_generic_phase(phase, inputs, state)
    
    async def _execute_agile_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute agile/requirements analysis phase."""
        # Simulate agile analysis
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'user_stories': ['As a user, I want to...', 'As an admin, I need to...'],
            'acceptance_criteria': ['Criteria 1', 'Criteria 2'],
            'sprint_planning': {'story_points': 8, 'sprint_capacity': 40},
            'requirements_analysis': 'Detailed requirements analysis completed'
        }
    
    async def _execute_design_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute design/architecture phase."""
        await asyncio.sleep(0.1)
        
        return {
            'design_specifications': 'System architecture designed',
            'architecture_diagrams': ['component_diagram.png', 'sequence_diagram.png'],
            'api_contracts': {'endpoints': ['/api/users', '/api/auth']},
            'design_decisions': 'Key architectural decisions documented'
        }
    
    async def _execute_code_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute code implementation phase."""
        await asyncio.sleep(0.2)
        
        return {
            'source_code': {'files': ['main.py', 'models.py', 'views.py']},
            'implementation_notes': 'Implementation completed following design specs',
            'code_metrics': {'lines_of_code': 500, 'complexity': 'medium'},
            'unit_tests': 'Basic unit tests implemented'
        }
    
    async def _execute_test_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute testing phase."""
        await asyncio.sleep(0.15)
        
        return {
            'test_suite': {'unit_tests': 25, 'integration_tests': 10},
            'test_results': {'passed': 33, 'failed': 2, 'coverage': 85},
            'coverage_report': 'Test coverage report generated',
            'quality_metrics': {'test_quality': 'good', 'coverage_adequate': True}
        }
    
    async def _execute_debug_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute debugging phase."""
        await asyncio.sleep(0.1)
        
        return {
            'root_cause_analysis': 'Issues identified and analyzed',
            'fixes': ['Fix 1: Null pointer exception', 'Fix 2: Logic error'],
            'resolution_notes': 'All critical issues resolved',
            'regression_tests': 'Regression tests passed'
        }
    
    async def _execute_docs_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute documentation phase."""
        await asyncio.sleep(0.1)
        
        return {
            'documentation': {'api_docs': 'API documentation updated', 'user_guide': 'User guide created'},
            'user_guides': ['Installation Guide', 'Usage Guide'],
            'technical_docs': 'Technical documentation completed',
            'documentation_coverage': 'All public APIs documented'
        }
    
    async def _execute_security_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute security analysis phase."""
        await asyncio.sleep(0.1)
        
        return {
            'security_analysis': 'Security review completed',
            'vulnerability_report': {'high': 0, 'medium': 1, 'low': 3},
            'security_recommendations': ['Enable HTTPS', 'Add input validation'],
            'compliance_status': 'Meets security requirements'
        }
    
    async def _execute_optimize_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute performance optimization phase."""
        await asyncio.sleep(0.1)
        
        return {
            'optimized_code': 'Performance optimizations applied',
            'performance_metrics': {'response_time': '200ms', 'throughput': '1000 rps'},
            'benchmark_results': 'Performance targets met',
            'optimization_report': 'Optimization summary completed'
        }
    
    async def _execute_git_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute git/deployment phase."""
        await asyncio.sleep(0.1)
        
        return {
            'commit_hash': 'abc123def456',
            'deployment_status': 'Successfully deployed',
            'pull_request': 'PR #123 created',
            'deployment_notes': 'Deployment completed successfully'
        }
    
    async def _execute_generic_phase(self, phase: WorkflowPhase, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute generic phase."""
        await asyncio.sleep(0.1)
        
        return {
            'phase_results': f'Phase {phase.name} completed',
            'execution_status': 'success',
            'outputs': phase.outputs,
            'metadata': {'phase_id': phase.phase_id, 'context': phase.context}
        }
    
    def _initialize_workflow_state(self, workflow: WorkflowDefinition, initial_context: Dict[str, Any]) -> WorkflowState:
        """Initialize workflow state."""
        return WorkflowState(
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.PENDING,
            context_data=initial_context.copy(),
            phase_status={phase.phase_id: PhaseStatus.PENDING for phase in workflow.phases}
        )
    
    def _build_execution_plan(self, workflow: WorkflowDefinition) -> List[Any]:
        """Build execution plan considering dependencies and parallel groups."""
        # Simple execution plan - sequential by default
        # Could be enhanced with more sophisticated dependency resolution
        
        plan = []
        processed_phases = set()
        
        # Group phases by parallel groups
        parallel_groups = {}
        sequential_phases = []
        
        for phase in workflow.phases:
            if hasattr(phase, 'parallel_group') and phase.parallel_group:
                if phase.parallel_group not in parallel_groups:
                    parallel_groups[phase.parallel_group] = []
                parallel_groups[phase.parallel_group].append(phase)
            else:
                sequential_phases.append(phase)
        
        # Add sequential phases
        plan.extend(sequential_phases)
        
        # Add parallel groups
        for group_phases in parallel_groups.values():
            if len(group_phases) > 1:
                plan.append(group_phases)  # List indicates parallel execution
            else:
                plan.extend(group_phases)
        
        return plan
    
    def _prepare_phase_inputs(self, phase: WorkflowPhase, state: WorkflowState) -> Dict[str, Any]:
        """Prepare inputs for phase execution."""
        inputs = {}
        
        # Add context data
        inputs.update(state.context_data)
        
        # Add results from previous phases
        for phase_id, results in state.phase_results.items():
            inputs[f"previous_{phase_id}"] = results
        
        # Add phase-specific inputs
        for input_name in phase.inputs:
            if input_name in state.context_data:
                inputs[input_name] = state.context_data[input_name]
        
        return inputs
    
    def _validate_context_transition(self, from_context: str, to_context: str, state: WorkflowState) -> bool:
        """Validate context transition is allowed."""
        # Basic validation - could be enhanced with more sophisticated rules
        if not to_context or not to_context.startswith('@'):
            return False
        
        valid_contexts = {
            '@code', '@debug', '@agile', '@git', '@test', '@design', 
            '@docs', '@optimize', '@security', '@research', '@default'
        }
        
        return to_context in valid_contexts
    
    def _capture_context_state(self, context: str, state: WorkflowState) -> Dict[str, Any]:
        """Capture current context state for later restoration."""
        return {
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'phase_results': state.phase_results.copy(),
            'context_data': state.context_data.get(context, {})
        }
    
    def _transform_phase_results(self, from_phase: str, to_phase: str, results: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Transform results from one phase for use in another."""
        # Simple pass-through transformation
        # Could be enhanced with sophisticated data mapping
        transformed = results.copy()
        
        # Add metadata
        transformed['_source_phase'] = from_phase
        transformed['_target_phase'] = to_phase
        transformed['_transformation_timestamp'] = datetime.now().isoformat()
        
        return transformed
    
    def _validate_propagated_data(self, phase_id: str, data: Dict[str, Any]) -> ValidationResult:
        """Validate data being propagated to a phase."""
        messages = []
        score = 1.0
        
        # Basic validation
        if not data:
            messages.append("No data provided for phase")
            score = 0.5
        
        # Check for required fields (could be enhanced)
        if '_source_phase' not in data:
            messages.append("Missing source phase information")
            score -= 0.1
        
        return ValidationResult(
            passed=score >= 0.7,
            score=score,
            messages=messages,
            details={'phase_id': phase_id, 'data_keys': list(data.keys())}
        )
    
    def _validate_phase_results(self, phase: WorkflowPhase, results: Dict[str, Any]) -> ValidationResult:
        """Validate phase execution results."""
        messages = []
        score = 1.0
        
        # Check if expected outputs are present
        missing_outputs = []
        for expected_output in phase.outputs:
            if expected_output not in results:
                missing_outputs.append(expected_output)
                messages.append(f"Missing expected output: {expected_output}")
                score -= 0.2
        
        # Check for errors in results
        has_errors = 'error' in results or 'errors' in results
        if has_errors:
            messages.append("Phase results contain errors")
            score -= 0.3
        
        # Validation fails if any required outputs are missing or there are errors
        passed = len(missing_outputs) == 0 and not has_errors
        
        return ValidationResult(
            passed=passed,
            score=score,
            messages=messages,
            details={'phase_id': phase.phase_id, 'results_keys': list(results.keys())}
        )
    
    async def _record_phase_metrics(self, phase: WorkflowPhase, results: Dict[str, Any], state: WorkflowState) -> None:
        """Record metrics for phase execution."""
        # Simple metrics recording
        # Could be enhanced with more sophisticated metrics collection
        pass
    
    async def _handle_phase_timeout(self, phase: WorkflowPhase, state: WorkflowState) -> None:
        """Handle phase timeout."""
        state.errors.append(f"Phase timeout: {phase.name} exceeded {phase.timeout}s")
        state.warnings.append(f"Consider increasing timeout for phase: {phase.name}")
    
    def _determine_recovery_action(self, context: str, error: Exception, state: WorkflowState) -> RecoveryAction:
        """Determine appropriate recovery action for an error."""
        error_type = type(error).__name__
        
        # Use recovery strategies
        for strategy in self.recovery_strategies:
            if strategy['condition'](context, error, state):
                return RecoveryAction(
                    action_type=strategy['action'],
                    parameters=strategy.get('parameters', {}),
                    reason=strategy['reason']
                )
        
        # Default recovery action
        return RecoveryAction(
            action_type="abort",
            reason=f"No recovery strategy found for {error_type} in {context}"
        )
    
    async def _execute_recovery_action(self, action: RecoveryAction, context: str, state: WorkflowState) -> None:
        """Execute a recovery action."""
        logger.info(f"Executing recovery action: {action.action_type}")
        
        if action.action_type == "retry":
            # Retry logic would be implemented here
            pass
        elif action.action_type == "skip":
            # Skip logic would be implemented here
            pass
        elif action.action_type == "rollback":
            # Rollback logic would be implemented here
            pass
        # Other recovery actions...
    
    def _build_recovery_strategies(self) -> List[Dict[str, Any]]:
        """Build recovery strategies for different error types."""
        return [
            {
                'name': 'timeout_retry',
                'condition': lambda ctx, err, state: isinstance(err, asyncio.TimeoutError),
                'action': 'retry',
                'parameters': {'max_retries': 2, 'backoff': 1.5},
                'reason': 'Retry on timeout with backoff'
            },
            {
                'name': 'validation_fail',
                'condition': lambda ctx, err, state: 'validation' in str(err).lower(),
                'action': 'abort',
                'reason': 'Fail phase on validation error'
            },
            {
                'name': 'critical_abort',
                'condition': lambda ctx, err, state: 'critical' in str(err).lower(),
                'action': 'abort',
                'reason': 'Abort on critical error'
            }
        ]
    
    def _finalize_workflow(self, workflow: WorkflowDefinition, state: WorkflowState) -> WorkflowResult:
        """Finalize workflow execution and create result."""
        execution_time = state.get_execution_time() or 0
        
        return WorkflowResult(
            workflow_id=state.workflow_id,
            status=state.status,
            results=state.phase_results,
            execution_time=execution_time,
            phases_executed=state.completed_phases,
            phases_failed=state.failed_phases,
            errors=state.errors,
            warnings=state.warnings,
            metrics={
                'total_phases': len(workflow.phases),
                'completed_phases': len(state.completed_phases),
                'failed_phases': len(state.failed_phases),
                'success_rate': len(state.completed_phases) / len(workflow.phases) if workflow.phases else 0
            }
        )
    
    def _handle_workflow_failure(self, workflow: WorkflowDefinition, state: WorkflowState, error: Exception) -> WorkflowResult:
        """Handle workflow failure and create error result."""
        state.status = WorkflowStatus.FAILED
        state.end_time = datetime.now()
        state.errors.append(f"Workflow failed: {str(error)}")
        
        execution_time = state.get_execution_time() or 0
        
        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.FAILED,
            results=state.phase_results,
            execution_time=execution_time,
            phases_executed=state.completed_phases,
            phases_failed=state.failed_phases + [state.current_phase] if state.current_phase else state.failed_phases,
            errors=state.errors,
            warnings=state.warnings,
            metrics={
                'total_phases': len(workflow.phases),
                'completed_phases': len(state.completed_phases),
                'failed_phases': len(state.failed_phases),
                'success_rate': len(state.completed_phases) / len(workflow.phases) if workflow.phases else 0,
                'failure_reason': str(error)
            }
        )
