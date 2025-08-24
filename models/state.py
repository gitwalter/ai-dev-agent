"""
State management models for the AI Development Agent system.
Defines the state structure used throughout the LangGraph workflow.
"""

from typing import TypedDict, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    """Main state structure for the LangGraph workflow."""
    
    # Project context and requirements
    project_context: str
    project_name: str
    requirements: List[Dict[str, Any]]
    user_stories: List[Dict[str, Any]]
    
    # Architecture and design
    architecture: Dict[str, Any]
    tech_stack: Dict[str, Any]
    database_schema: Dict[str, Any]
    
    # Generated artifacts
    code_files: Dict[str, str]
    tests: Dict[str, str]
    documentation: Dict[str, str]
    configuration_files: Dict[str, str]
    
    # Workflow state
    current_task: str
    current_agent: str
    agent_outputs: Dict[str, Any]
    workflow_history: List[Dict[str, Any]]
    
    # Human interaction
    human_approval_needed: bool
    approval_requests: List[Dict[str, Any]]
    human_feedback: Dict[str, Any]
    
    # Error handling
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    retry_count: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    session_id: str


class TaskResult(BaseModel):
    """Result of a single agent task."""
    
    task_name: str
    agent_name: str
    status: str = Field(..., description="success, failed, pending, approved, rejected")
    output: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: float = 0.0
    error_message: Optional[str] = None


class WorkflowStep(BaseModel):
    """Represents a single step in the workflow."""
    
    step_id: str
    step_name: str
    agent_name: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ApprovalRequest(BaseModel):
    """Represents a request for human approval."""
    
    request_id: str
    task_name: str
    agent_name: str
    description: str
    data_to_review: Dict[str, Any]
    options: List[str] = Field(default_factory=list)
    required: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    decision: Optional[str] = None
    comments: Optional[str] = None


class ErrorInfo(BaseModel):
    """Detailed error information."""
    
    error_id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: str = "error"  # error, warning, info
    recoverable: bool = True
    retry_count: int = 0


def create_initial_state(
    project_context: str,
    project_name: str,
    session_id: str
) -> AgentState:
    """Create an initial state for the workflow."""
    
    return AgentState(
        project_context=project_context,
        project_name=project_name,
        requirements=[],
        user_stories=[],
        architecture={},
        tech_stack={},
        database_schema={},
        code_files={},
        tests={},
        documentation={},
        configuration_files={},
        current_task="requirements_analysis",
        current_agent="requirements_analyst",
        agent_outputs={},
        workflow_history=[],
        human_approval_needed=False,
        approval_requests=[],
        human_feedback={},
        errors=[],
        warnings=[],
        retry_count=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        session_id=session_id
    )


def update_state_timestamp(state: AgentState) -> AgentState:
    """Update the timestamp of the state."""
    state["updated_at"] = datetime.now()
    return state


def add_workflow_step(
    state: AgentState,
    step_name: str,
    agent_name: str,
    input_data: Dict[str, Any],
    output_data: Optional[Dict[str, Any]] = None,
    status: str = "completed"
) -> AgentState:
    """Add a workflow step to the history."""
    
    step = WorkflowStep(
        step_id=f"{agent_name}_{step_name}_{len(state['workflow_history'])}",
        step_name=step_name,
        agent_name=agent_name,
        input_data=input_data,
        output_data=output_data,
        status=status,
        completed_at=datetime.now() if status == "completed" else None
    )
    
    state["workflow_history"].append(step.dict())
    return update_state_timestamp(state)


def add_error(
    state: AgentState,
    error_type: str,
    error_message: str,
    context: Optional[Dict[str, Any]] = None,
    severity: str = "error"
) -> AgentState:
    """Add an error to the state."""
    
    error = ErrorInfo(
        error_id=f"error_{len(state['errors'])}",
        error_type=error_type,
        error_message=error_message,
        context=context or {},
        severity=severity
    )
    
    if severity == "error":
        state["errors"].append(error.dict())
    else:
        state["warnings"].append(error.dict())
    
    return update_state_timestamp(state)


def add_approval_request(
    state: AgentState,
    task_name: str,
    agent_name: str,
    description: str,
    data_to_review: Dict[str, Any],
    options: Optional[List[str]] = None,
    required: bool = True
) -> AgentState:
    """Add an approval request to the state."""
    
    request = ApprovalRequest(
        request_id=f"approval_{len(state['approval_requests'])}",
        task_name=task_name,
        agent_name=agent_name,
        description=description,
        data_to_review=data_to_review,
        options=options or ["approve", "reject", "modify"],
        required=required
    )
    
    state["approval_requests"].append(request.dict())
    state["human_approval_needed"] = True
    
    return update_state_timestamp(state)
