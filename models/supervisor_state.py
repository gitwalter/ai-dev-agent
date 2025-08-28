#!/usr/bin/env python3
"""
Enhanced state management for supervisor-swarm hybrid system.
"""

from typing import TypedDict, Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


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
    current_task: str  # Current task being executed
    
    # Agent outputs
    requirements: List[Dict[str, Any]]
    architecture: Dict[str, Any]
    code_files: Dict[str, Any]
    tests: Dict[str, Any]
    documentation: Dict[str, Any]
    diagrams: Dict[str, Any]
    
    # Agent management
    agent_outputs: Dict[str, Any]
    agent_status: Dict[str, str]  # 'available', 'busy', 'completed', 'failed'
    agent_assignments: Dict[str, str]  # task -> agent mapping
    
    # Handoff system
    handoff_queue: List[Dict[str, Any]]  # Pending handoffs
    handoff_history: List[Dict[str, Any]]  # Completed handoffs
    handoff_rules: Dict[str, Any]  # Handoff validation rules
    
    # Quality control
    quality_gates: Dict[str, bool]  # Quality gate status
    quality_metrics: Dict[str, float]  # Quality scores
    validation_results: List[Dict[str, Any]]  # Validation outcomes
    
    # Error handling
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    approval_requests: List[Dict[str, Any]]
    
    # Execution tracking
    current_step: str
    execution_history: List[Dict[str, Any]]
    workflow_history: List[Dict[str, Any]]
    
    # Performance monitoring
    performance_metrics: Dict[str, float]
    execution_times: Dict[str, float]
    resource_usage: Dict[str, Any]


class HandoffRequest(BaseModel):
    """Handoff request between agents."""
    from_agent: str
    to_agent: str
    task_id: str
    task_type: str
    priority: str = "normal"  # low, normal, high, critical
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending"  # pending, approved, rejected, completed
    validation_rules: List[str] = []
    quality_requirements: Dict[str, Any] = {}


class QualityGate(BaseModel):
    """Quality gate for handoff validation."""
    gate_id: str
    gate_name: str
    gate_type: str  # 'validation', 'review', 'approval'
    required_score: float
    current_score: float = 0.0
    passed: bool = False
    validation_rules: List[str] = []
    approver: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentStatus(BaseModel):
    """Agent status and capabilities."""
    agent_id: str
    agent_name: str
    status: str  # 'available', 'busy', 'completed', 'failed'
    current_task: Optional[str] = None
    capabilities: List[str] = []
    performance_metrics: Dict[str, float] = {}
    last_activity: datetime = Field(default_factory=datetime.now)
    workload: float = 0.0  # 0.0 to 1.0


class HandoffRule(BaseModel):
    """Rule for handoff validation."""
    rule_id: str
    rule_name: str
    rule_type: str  # 'validation', 'quality', 'approval'
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int = 1
    enabled: bool = True


class SupervisorSwarmStateManager:
    """Manager for supervisor-swarm state operations."""
    
    def __init__(self):
        self.state: SupervisorSwarmState = {}
    
    def initialize_state(self, project_context: str, project_name: str, session_id: str) -> SupervisorSwarmState:
        """Initialize a new supervisor-swarm state."""
        self.state = {
            "project_context": project_context,
            "project_name": project_name,
            "session_id": session_id,
            "current_phase": "planning",
            "current_supervisor_task": None,
            "active_agent": None,
            "current_task": "initialization",
            "requirements": [],
            "architecture": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "agent_status": {},
            "agent_assignments": {},
            "handoff_queue": [],
            "handoff_history": [],
            "handoff_rules": {},
            "quality_gates": {},
            "quality_metrics": {},
            "validation_results": [],
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "started",
            "execution_history": [],
            "workflow_history": [],
            "performance_metrics": {},
            "execution_times": {},
            "resource_usage": {}
        }
        return self.state
    
    def add_handoff_request(self, handoff: HandoffRequest) -> None:
        """Add a handoff request to the queue."""
        self.state["handoff_queue"].append(handoff.dict())
    
    def process_handoff(self, handoff_id: str, action: str, approver: str = None) -> bool:
        """Process a handoff request."""
        for handoff in self.state["handoff_queue"]:
            if handoff.get("task_id") == handoff_id:
                handoff["status"] = action
                if approver:
                    handoff["approver"] = approver
                handoff["processed_at"] = datetime.now().isoformat()
                
                # Move to history
                self.state["handoff_history"].append(handoff)
                self.state["handoff_queue"].remove(handoff)
                return True
        return False
    
    def add_quality_gate(self, gate: QualityGate) -> None:
        """Add a quality gate."""
        self.state["quality_gates"][gate.gate_id] = gate.dict()
    
    def update_quality_gate(self, gate_id: str, score: float, passed: bool) -> bool:
        """Update a quality gate."""
        if gate_id in self.state["quality_gates"]:
            self.state["quality_gates"][gate_id]["current_score"] = score
            self.state["quality_gates"][gate_id]["passed"] = passed
            self.state["quality_gates"][gate_id]["timestamp"] = datetime.now().isoformat()
            return True
        return False
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get agent status."""
        if agent_id in self.state["agent_status"]:
            return AgentStatus(**self.state["agent_status"][agent_id])
        return None
    
    def update_agent_status(self, agent_id: str, status: str, task: str = None) -> None:
        """Update agent status."""
        if agent_id not in self.state["agent_status"]:
            self.state["agent_status"][agent_id] = {
                "agent_id": agent_id,
                "agent_name": agent_id,
                "status": status,
                "current_task": task,
                "capabilities": [],
                "performance_metrics": {},
                "last_activity": datetime.now().isoformat(),
                "workload": 0.0
            }
        else:
            self.state["agent_status"][agent_id]["status"] = status
            if task:
                self.state["agent_status"][agent_id]["current_task"] = task
            self.state["agent_status"][agent_id]["last_activity"] = datetime.now().isoformat()
    
    def assign_task_to_agent(self, task_id: str, agent_id: str) -> None:
        """Assign a task to an agent."""
        self.state["agent_assignments"][task_id] = agent_id
        self.update_agent_status(agent_id, "busy", task_id)
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents."""
        available = []
        for agent_id, status in self.state["agent_status"].items():
            if status.get("status") == "available":
                available.append(agent_id)
        return available
    
    def add_error(self, error: Dict[str, Any]) -> None:
        """Add an error to the state."""
        error["timestamp"] = datetime.now().isoformat()
        self.state["errors"].append(error)
    
    def add_warning(self, warning: Dict[str, Any]) -> None:
        """Add a warning to the state."""
        warning["timestamp"] = datetime.now().isoformat()
        self.state["warnings"].append(warning)
    
    def add_approval_request(self, request: Dict[str, Any]) -> None:
        """Add an approval request."""
        request["timestamp"] = datetime.now().isoformat()
        request["status"] = "pending"
        self.state["approval_requests"].append(request)
    
    def get_state(self) -> SupervisorSwarmState:
        """Get the current state."""
        return self.state
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update the state with new values."""
        self.state.update(updates)


# Missing classes and functions needed by tests

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Task model for supervisor tasks."""
    task_id: str
    task_name: str
    description: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    dependencies: List[str] = []
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = {}


class TaskResult(BaseModel):
    """Result of a completed task."""
    task_id: str
    success: bool
    result_data: Dict[str, Any] = {}
    error_message: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    quality_score: float = 0.0


class EscalationLevel(str, Enum):
    """Escalation level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Escalation(BaseModel):
    """Escalation for failed tasks."""
    escalation_id: str
    task_id: str
    level: EscalationLevel = EscalationLevel.MEDIUM
    reason: str
    suggested_actions: List[str] = []
    escalated_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    status: str = "pending"


class ValidationResult(BaseModel):
    """Result of validation."""
    validation_id: str
    task_id: str
    validator: str
    score: float
    passed: bool
    feedback: str = ""
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class SupervisorDecision(BaseModel):
    """Decision made by supervisor."""
    decision_id: str
    task_id: str
    decision_type: str  # 'assign', 'escalate', 'retry', 'cancel'
    decision: str
    reasoning: str
    confidence: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}


class HandoffRecord(BaseModel):
    """Record of agent handoff."""
    handoff_id: str
    from_agent: str
    to_agent: str
    task_id: str
    reason: str
    data_transferred: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "completed"


class PerformanceMetrics(BaseModel):
    """Performance metrics for agents/tasks."""
    entity_id: str
    entity_type: str  # 'agent', 'task', 'supervisor'
    metrics: Dict[str, float] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    period: str = "hourly"  # 'hourly', 'daily', 'weekly'


# Utility functions

def create_initial_supervisor_swarm_state(project_context: str, project_name: str, session_id: str) -> SupervisorSwarmState:
    """Create initial supervisor swarm state."""
    manager = SupervisorSwarmStateManager()
    return manager.initialize_state(project_context, project_name, session_id)


def update_supervisor_swarm_state(state: SupervisorSwarmState, updates: Dict[str, Any]) -> SupervisorSwarmState:
    """Update supervisor swarm state."""
    state.update(updates)
    return state


def add_supervisor_decision(state: SupervisorSwarmState, decision: SupervisorDecision) -> SupervisorSwarmState:
    """Add supervisor decision to state."""
    if "supervisor_decisions" not in state:
        state["supervisor_decisions"] = []
    state["supervisor_decisions"].append(decision.dict())
    return state


def add_quality_validation(state: SupervisorSwarmState, validation: ValidationResult) -> SupervisorSwarmState:
    """Add quality validation to state."""
    if "quality_validations" not in state:
        state["quality_validations"] = []
    state["quality_validations"].append(validation.dict())
    return state


def add_handoff_record(state: SupervisorSwarmState, handoff: HandoffRecord) -> SupervisorSwarmState:
    """Add handoff record to state."""
    if "handoff_records" not in state:
        state["handoff_records"] = []
    state["handoff_records"].append(handoff.dict())
    return state


def add_error(state: SupervisorSwarmState, error: Dict[str, Any]) -> SupervisorSwarmState:
    """Add error to state."""
    if "errors" not in state:
        state["errors"] = []
    error["timestamp"] = datetime.now().isoformat()
    state["errors"].append(error)
    return state


def add_warning(state: SupervisorSwarmState, warning: Dict[str, Any]) -> SupervisorSwarmState:
    """Add warning to state."""
    if "warnings" not in state:
        state["warnings"] = []
    warning["timestamp"] = datetime.now().isoformat()
    state["warnings"].append(warning)
    return state


def increment_retry_count(state: SupervisorSwarmState, task_id: str) -> SupervisorSwarmState:
    """Increment retry count for a task."""
    if "retry_counts" not in state:
        state["retry_counts"] = {}
    if task_id not in state["retry_counts"]:
        state["retry_counts"][task_id] = 0
    state["retry_counts"][task_id] += 1
    return state


def add_execution_history_entry(state: SupervisorSwarmState, entry: Dict[str, Any]) -> SupervisorSwarmState:
    """Add execution history entry."""
    if "execution_history" not in state:
        state["execution_history"] = []
    entry["timestamp"] = datetime.now().isoformat()
    state["execution_history"].append(entry)
    return state


def add_performance_metric(state: SupervisorSwarmState, metric: PerformanceMetrics) -> SupervisorSwarmState:
    """Add performance metric."""
    if "performance_metrics" not in state:
        state["performance_metrics"] = []
    state["performance_metrics"].append(metric.dict())
    return state
