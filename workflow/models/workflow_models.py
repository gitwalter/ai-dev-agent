#!/usr/bin/env python3
"""
Data models for the Workflow Composition Engine.
Defines core data structures for workflow automation and context orchestration.
"""

from typing import Dict, List, Any, Optional, Literal, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ComplexityLevel(str, Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class PhaseStatus(str, Enum):
    """Individual phase execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Entity(BaseModel):
    """Extracted entity from task description."""
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (feature, bug, component, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")


class TaskAnalysis(BaseModel):
    """Analysis results for a task description."""
    task_id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Original task description")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    complexity: ComplexityLevel = Field(..., description="Task complexity level")
    required_contexts: List[str] = Field(default_factory=list, description="Required @keyword contexts")
    estimated_duration: int = Field(..., gt=0, description="Estimated duration in minutes")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    created_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    @validator('required_contexts')
    def validate_contexts(cls, v):
        """Validate that contexts are valid @keywords."""
        valid_contexts = {
            '@code', '@debug', '@agile', '@git', '@test', '@design', 
            '@docs', '@optimize', '@security', '@research', '@default'
        }
        for context in v:
            if context not in valid_contexts:
                raise ValueError(f"Invalid context: {context}")
        return v


class WorkflowPhase(BaseModel):
    """Individual phase in a workflow."""
    phase_id: str = Field(..., description="Unique phase identifier")
    context: str = Field(..., description="@keyword context for this phase")
    name: str = Field(..., description="Human-readable phase name")
    description: str = Field(..., description="Phase description")
    inputs: List[str] = Field(default_factory=list, description="Required input parameters")
    outputs: List[str] = Field(default_factory=list, description="Expected output parameters")
    condition: Optional[str] = Field(None, description="Conditional execution logic")
    timeout: int = Field(300, gt=0, description="Phase timeout in seconds")
    retry_count: int = Field(3, ge=0, description="Number of retry attempts")
    quality_gates: List[str] = Field(default_factory=list, description="Quality validation requirements")
    parallel_group: Optional[str] = Field(None, description="Parallel execution group")
    
    @validator('context')
    def validate_context(cls, v):
        """Validate context is a valid @keyword."""
        valid_contexts = {
            '@code', '@debug', '@agile', '@git', '@test', '@design', 
            '@docs', '@optimize', '@security', '@research', '@default'
        }
        if v not in valid_contexts:
            raise ValueError(f"Invalid context: {v}")
        return v


class WorkflowDefinition(BaseModel):
    """Complete workflow definition."""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    phases: List[WorkflowPhase] = Field(..., description="Workflow phases")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Phase dependencies")
    estimated_duration: int = Field(..., gt=0, description="Estimated total duration in minutes")
    quality_gates: List[str] = Field(default_factory=list, description="Global quality gates")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    @validator('phases')
    def validate_phases_not_empty(cls, v):
        """Ensure workflow has at least one phase."""
        if not v:
            raise ValueError("Workflow must have at least one phase")
        return v


class WorkflowState(BaseModel):
    """Current state of workflow execution."""
    workflow_id: str = Field(..., description="Workflow identifier")
    status: WorkflowStatus = Field(WorkflowStatus.PENDING, description="Current workflow status")
    current_phase: Optional[str] = Field(None, description="Currently executing phase")
    completed_phases: List[str] = Field(default_factory=list, description="Completed phase IDs")
    failed_phases: List[str] = Field(default_factory=list, description="Failed phase IDs")
    phase_results: Dict[str, Any] = Field(default_factory=dict, description="Results from each phase")
    phase_status: Dict[str, PhaseStatus] = Field(default_factory=dict, description="Status of each phase")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Context-specific data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    start_time: Optional[datetime] = Field(None, description="Workflow start time")
    end_time: Optional[datetime] = Field(None, description="Workflow end time")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    def get_execution_time(self) -> Optional[int]:
        """Get execution time in seconds."""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        elif self.start_time:
            return int((datetime.now() - self.start_time).total_seconds())
        return None


class WorkflowResult(BaseModel):
    """Complete workflow execution result."""
    workflow_id: str = Field(..., description="Workflow identifier")
    status: WorkflowStatus = Field(..., description="Final workflow status")
    results: Dict[str, Any] = Field(default_factory=dict, description="Workflow outputs")
    execution_time: int = Field(..., ge=0, description="Total execution time in seconds")
    phases_executed: List[str] = Field(default_factory=list, description="Successfully executed phases")
    phases_failed: List[str] = Field(default_factory=list, description="Failed phases")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall quality score")
    completed_at: datetime = Field(default_factory=datetime.now, description="Completion timestamp")


class WorkflowTemplate(BaseModel):
    """Reusable workflow template."""
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    phases: List[WorkflowPhase] = Field(..., description="Template phases")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")
    usage_count: int = Field(0, ge=0, description="Number of times used")
    success_rate: float = Field(0.0, ge=0.0, le=1.0, description="Success rate")
    average_duration: Optional[int] = Field(None, description="Average execution time in minutes")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class ExecutionMetrics(BaseModel):
    """Metrics for workflow execution monitoring."""
    workflow_id: str = Field(..., description="Workflow identifier")
    phase_id: Optional[str] = Field(None, description="Phase identifier")
    metric_type: str = Field(..., description="Type of metric")
    value: Union[int, float, str] = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metric timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ValidationResult(BaseModel):
    """Result of quality validation."""
    passed: bool = Field(..., description="Whether validation passed")
    score: float = Field(..., ge=0.0, le=1.0, description="Validation score")
    messages: List[str] = Field(default_factory=list, description="Validation messages")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed validation results")
    timestamp: datetime = Field(default_factory=datetime.now, description="Validation timestamp")


class RecoveryAction(BaseModel):
    """Recovery action for error handling."""
    action_type: Literal["retry", "skip", "rollback", "escalate", "abort"] = Field(..., description="Recovery action type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    reason: str = Field(..., description="Reason for recovery action")
    timestamp: datetime = Field(default_factory=datetime.now, description="Action timestamp")


class Bottleneck(BaseModel):
    """Performance bottleneck identification."""
    bottleneck_id: str = Field(..., description="Unique bottleneck identifier")
    workflow_id: str = Field(..., description="Affected workflow")
    phase_id: Optional[str] = Field(None, description="Affected phase")
    type: str = Field(..., description="Bottleneck type")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Bottleneck severity")
    description: str = Field(..., description="Bottleneck description")
    impact: str = Field(..., description="Performance impact")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    detected_at: datetime = Field(default_factory=datetime.now, description="Detection timestamp")


class Optimization(BaseModel):
    """Workflow optimization recommendation."""
    optimization_id: str = Field(..., description="Unique optimization identifier")
    workflow_id: str = Field(..., description="Target workflow")
    type: str = Field(..., description="Optimization type")
    description: str = Field(..., description="Optimization description")
    expected_improvement: str = Field(..., description="Expected improvement")
    implementation_effort: Literal["low", "medium", "high"] = Field(..., description="Implementation effort")
    priority: Literal["low", "medium", "high", "critical"] = Field(..., description="Optimization priority")
    recommendations: List[str] = Field(default_factory=list, description="Implementation recommendations")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class AnalyticsReport(BaseModel):
    """Comprehensive analytics report."""
    report_id: str = Field(..., description="Unique report identifier")
    timeframe: str = Field(..., description="Report timeframe")
    total_workflows: int = Field(..., ge=0, description="Total workflows executed")
    successful_workflows: int = Field(..., ge=0, description="Successfully completed workflows")
    failed_workflows: int = Field(..., ge=0, description="Failed workflows")
    average_execution_time: float = Field(..., ge=0.0, description="Average execution time in minutes")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Overall success rate")
    most_used_contexts: List[str] = Field(default_factory=list, description="Most frequently used contexts")
    bottlenecks: List[Bottleneck] = Field(default_factory=list, description="Identified bottlenecks")
    optimizations: List[Optimization] = Field(default_factory=list, description="Optimization recommendations")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional metrics")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")


# Utility functions for model validation and conversion

def validate_workflow_definition(workflow: WorkflowDefinition) -> ValidationResult:
    """
    Validate a workflow definition for completeness and correctness.
    
    Args:
        workflow: Workflow definition to validate
        
    Returns:
        Validation result with details
    """
    messages = []
    score = 1.0
    
    # Check for circular dependencies
    if has_circular_dependencies(workflow.dependencies):
        messages.append("Circular dependencies detected in workflow")
        score -= 0.3
    
    # Check phase connectivity
    if not is_workflow_connected(workflow):
        messages.append("Workflow phases are not properly connected")
        score -= 0.2
    
    # Validate phase inputs/outputs
    for phase in workflow.phases:
        if not phase.outputs and phase != workflow.phases[-1]:
            messages.append(f"Phase {phase.name} has no outputs")
            score -= 0.1
    
    return ValidationResult(
        passed=score >= 0.7,
        score=max(0.0, score),
        messages=messages,
        details={"validation_type": "workflow_definition"}
    )


def has_circular_dependencies(dependencies: Dict[str, List[str]]) -> bool:
    """Check for circular dependencies in workflow."""
    visited = set()
    rec_stack = set()
    
    def has_cycle(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in dependencies:
        if node not in visited:
            if has_cycle(node):
                return True
    
    return False


def is_workflow_connected(workflow: WorkflowDefinition) -> bool:
    """Check if workflow phases are properly connected."""
    if not workflow.phases:
        return False
    
    if len(workflow.phases) == 1:
        return True
    
    # Build adjacency list
    graph = {}
    for phase in workflow.phases:
        graph[phase.phase_id] = []
    
    for phase_id, deps in workflow.dependencies.items():
        for dep in deps:
            if dep in graph:
                graph[dep].append(phase_id)
    
    # Check if all phases are reachable from first phase
    visited = set()
    
    def dfs(node: str):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
    
    dfs(workflow.phases[0].phase_id)
    
    return len(visited) == len(workflow.phases)
