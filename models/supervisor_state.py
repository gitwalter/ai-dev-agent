#!/usr/bin/env python3
"""
Enhanced state management for supervisor-swarm hybrid system.
"""

from typing import TypedDict, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SupervisorSwarmState(TypedDict):
    """Enhanced state for supervisor-swarm hybrid system."""
    # Project context
    project_context: str
    project_name: str
    session_id: str
    
    # Workflow state
    current_phase: str  # 'planning', 'execution', 'review', 'completion'
    current_supervisor_task: Optional[str]
    active_agent: Optional[str]
    
    # Agent outputs
    requirements: List[Dict[str, Any]]
    architecture: Dict[str, Any]
    code_files: Dict[str, Any]
    tests: Dict[str, Any]
    documentation: Dict[str, Any]
    agent_outputs: Dict[str, Any]
    
    # Supervisor oversight
    supervisor_decisions: List[Dict[str, Any]]
    quality_validations: List[Dict[str, Any]]
    task_delegations: List[Dict[str, Any]]
    escalations: List[Dict[str, Any]]
    
    # Swarm coordination
    handoff_history: List[Dict[str, Any]]
    agent_collaborations: List[Dict[str, Any]]
    current_collaboration: Optional[Dict[str, Any]]
    
    # Error handling
    errors: List[str]
    warnings: List[str]
    retry_count: int
    
    # Performance tracking
    execution_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, Dict[str, Any]]


class Task(BaseModel):
    """Structured task definition for delegation."""
    id: str = Field(..., min_length=1, description="Unique task identifier")
    type: str = Field(..., min_length=1, description="Task type (requirements_analysis, architecture_design, etc.)")
    description: str = Field(..., min_length=1, description="Task description")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Task requirements")
    priority: str = Field(default="medium", description="Task priority (low/medium/high/critical)")
    estimated_complexity: str = Field(default="moderate", description="Estimated complexity (simple/moderate/complex)")
    dependencies: List[str] = Field(default_factory=list, description="List of task dependencies")
    quality_criteria: Dict[str, Any] = Field(default_factory=dict, description="Quality criteria for the task")
    created_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    assigned_to: Optional[str] = Field(default=None, description="Agent assigned to the task")
    status: str = Field(default="pending", description="Task status (pending/in_progress/completed/failed)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_id: str = Field(..., description="ID of the executed task")
    worker: str = Field(..., description="Worker agent that executed the task")
    result: Dict[str, Any] = Field(..., description="Task execution result")
    validation: Optional[Dict[str, Any]] = Field(default=None, description="Validation result")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    status: str = Field(default="completed", description="Execution status")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Escalation(BaseModel):
    """Escalation from worker agent to supervisor."""
    id: str = Field(..., description="Unique escalation identifier")
    from_agent: str = Field(..., description="Agent that created the escalation")
    issue: str = Field(..., description="Description of the issue")
    severity: str = Field(default="medium", description="Issue severity (low/medium/high/critical)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Escalation context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Escalation timestamp")
    status: str = Field(default="pending", description="Escalation status (pending/in_progress/resolved)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationResult(BaseModel):
    """Result of quality validation."""
    task_type: str = Field(..., description="Type of task being validated")
    overall_score: float = Field(..., description="Overall validation score (0.0-1.0)")
    is_approved: bool = Field(..., description="Whether the output is approved")
    criteria_scores: Dict[str, float] = Field(..., description="Scores for individual criteria")
    feedback: str = Field(..., description="Validation feedback")
    timestamp: datetime = Field(default_factory=datetime.now, description="Validation timestamp")
    validator: str = Field(default="quality_control_supervisor", description="Validator that performed the validation")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SupervisorDecision(BaseModel):
    """A decision made by a supervisor."""
    decision_type: str = Field(..., description="Type of decision")
    action: str = Field(..., description="Action taken")
    reasoning: str = Field(..., description="Reasoning for the decision")
    context: Dict[str, Any] = Field(default_factory=dict, description="Decision context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Decision timestamp")
    supervisor_id: str = Field(..., description="ID of the supervisor that made the decision")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HandoffRecord(BaseModel):
    """Record of a handoff between agents."""
    from_agent: str = Field(..., description="Agent that initiated the handoff")
    to_agent: str = Field(..., description="Agent that received the handoff")
    reason: str = Field(..., description="Reason for the handoff")
    context: Dict[str, Any] = Field(default_factory=dict, description="Handoff context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Handoff timestamp")
    status: str = Field(default="completed", description="Handoff status")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PerformanceMetrics(BaseModel):
    """Performance metrics for agents and workflows."""
    agent_id: str = Field(..., description="Agent identifier")
    metric_type: str = Field(..., description="Type of metric")
    value: float = Field(..., description="Metric value")
    unit: str = Field(default="", description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metric timestamp")
    context: Dict[str, Any] = Field(default_factory=dict, description="Metric context")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def create_initial_supervisor_swarm_state(
    project_context: str,
    project_name: str = "",
    session_id: str = ""
) -> SupervisorSwarmState:
    """Create an initial supervisor-swarm state."""
    return SupervisorSwarmState(
        project_context=project_context,
        project_name=project_name,
        session_id=session_id,
        current_phase="started",
        current_supervisor_task=None,
        active_agent=None,
        requirements=[],
        architecture={},
        code_files={},
        tests={},
        documentation={},
        agent_outputs={},
        supervisor_decisions=[],
        quality_validations=[],
        task_delegations=[],
        escalations=[],
        handoff_history=[],
        agent_collaborations=[],
        current_collaboration=None,
        errors=[],
        warnings=[],
        retry_count=0,
        execution_history=[],
        performance_metrics={}
    )


def update_supervisor_swarm_state(
    state: SupervisorSwarmState,
    updates: Dict[str, Any]
) -> SupervisorSwarmState:
    """Update a supervisor-swarm state with new values."""
    return SupervisorSwarmState(**{**state, **updates})


def add_supervisor_decision(
    state: SupervisorSwarmState,
    decision: SupervisorDecision
) -> SupervisorSwarmState:
    """Add a supervisor decision to the state."""
    decisions = state["supervisor_decisions"].copy()
    decisions.append(decision.model_dump())
    
    return update_supervisor_swarm_state(state, {
        "supervisor_decisions": decisions
    })


def add_quality_validation(
    state: SupervisorSwarmState,
    validation: ValidationResult
) -> SupervisorSwarmState:
    """Add a quality validation to the state."""
    validations = state["quality_validations"].copy()
    validations.append(validation.model_dump())
    
    return update_supervisor_swarm_state(state, {
        "quality_validations": validations,
        "current_validation": validation.model_dump()
    })


def add_handoff_record(
    state: SupervisorSwarmState,
    handoff: HandoffRecord
) -> SupervisorSwarmState:
    """Add a handoff record to the state."""
    handoffs = state["handoff_history"].copy()
    handoffs.append(handoff.model_dump())
    
    return update_supervisor_swarm_state(state, {
        "handoff_history": handoffs
    })


def add_error(
    state: SupervisorSwarmState,
    error: str
) -> SupervisorSwarmState:
    """Add an error to the state."""
    errors = state["errors"].copy()
    errors.append(error)
    
    return update_supervisor_swarm_state(state, {
        "errors": errors
    })


def add_warning(
    state: SupervisorSwarmState,
    warning: str
) -> SupervisorSwarmState:
    """Add a warning to the state."""
    warnings = state["warnings"].copy()
    warnings.append(warning)
    
    return update_supervisor_swarm_state(state, {
        "warnings": warnings
    })


def increment_retry_count(state: SupervisorSwarmState) -> SupervisorSwarmState:
    """Increment the retry count."""
    return update_supervisor_swarm_state(state, {
        "retry_count": state["retry_count"] + 1
    })


def add_execution_history_entry(
    state: SupervisorSwarmState,
    entry: Dict[str, Any]
) -> SupervisorSwarmState:
    """Add an execution history entry."""
    history = state["execution_history"].copy()
    entry_with_timestamp = {
        **entry,
        "timestamp": datetime.now().isoformat()
    }
    history.append(entry_with_timestamp)
    
    return update_supervisor_swarm_state(state, {
        "execution_history": history
    })


def add_performance_metric(
    state: SupervisorSwarmState,
    metric: PerformanceMetrics
) -> SupervisorSwarmState:
    """Add a performance metric to the state."""
    metrics = state["performance_metrics"].copy()
    agent_metrics = metrics.get(metric.agent_id, {})
    agent_metrics[metric.metric_type] = metric.model_dump()
    metrics[metric.agent_id] = agent_metrics
    
    return update_supervisor_swarm_state(state, {
        "performance_metrics": metrics
    })
