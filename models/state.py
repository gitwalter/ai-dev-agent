"""
State management models for the AI Development Agent system.
Defines the state structure used throughout the LangGraph workflow.
"""

from typing import TypedDict, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


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
    
    # Memory system fields (Phase 2 enhancement)
    memory_context: str
    memory_query: str
    memory_timestamp: str
    recall_memories: List[Dict[str, Any]]
    knowledge_triples: List[Dict[str, Any]]
    memory_stats: Dict[str, Any]
    
    # Handoff system fields (Phase 2 enhancement)
    handoff_queue: List[Dict[str, Any]]
    handoff_history: List[Dict[str, Any]]
    agent_availability: Dict[str, bool]
    collaboration_context: Dict[str, Any]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    session_id: str


class TaskResult(BaseModel):
    """Result of a single agent task - LangChain compatible."""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    task_name: str
    agent_name: str
    status: str = Field(..., description="success, failed, pending, approved, rejected")
    output: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: float = 0.0
    error_message: Optional[str] = None


class WorkflowStep(BaseModel):
    """Represents a single step in the workflow - LangChain compatible."""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
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
    """Represents a request for human approval - LangChain compatible."""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
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
    """Detailed error information - LangChain compatible."""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    error_id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: str = "error"  # error, warning, info
    recoverable: bool = True
    retry_count: int = 0


class MemoryInfo(BaseModel):
    """Memory information for state tracking."""
    
    memory_id: str
    content: str
    context: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = "agent"


class KnowledgeTriple(BaseModel):
    """Structured knowledge triple for memory."""
    
    triple_id: str
    subject: str
    predicate: str
    object: str
    context: str
    confidence: float = 1.0
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = "agent"
    user_id: str = "default"


class HandoffRequest(BaseModel):
    """Represents a handoff request between agents."""
    
    handoff_id: str
    from_agent: str
    to_agent: str
    task_description: str
    data_to_transfer: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, urgent
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, failed


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
        # Memory system fields
        memory_context="",
        memory_query="",
        memory_timestamp="",
        recall_memories=[],
        knowledge_triples=[],
        memory_stats={},
        # Handoff system fields
        handoff_queue=[],
        handoff_history=[],
        agent_availability={
            "requirements_analyst": True,
            "architecture_designer": True,
            "code_generator": True,
            "test_generator": True,
            "code_reviewer": True,
            "security_analyst": True,
            "documentation_generator": True
        },
        collaboration_context={},
        # Metadata
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
    
    state["workflow_history"].append(step.model_dump())
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
        state["errors"].append(error.model_dump())
    else:
        state["warnings"].append(error.model_dump())
    
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
    
    state["approval_requests"].append(request.model_dump())
    state["human_approval_needed"] = True
    
    return update_state_timestamp(state)


def add_memory_to_state(
    state: AgentState,
    memory_content: str,
    memory_context: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    relevance_score: float = 0.0
) -> AgentState:
    """Add a memory to the state."""
    
    memory = MemoryInfo(
        memory_id=f"memory_{len(state['recall_memories'])}",
        content=memory_content,
        context=memory_context,
        metadata=metadata or {},
        relevance_score=relevance_score
    )
    
    state["recall_memories"].append(memory.model_dump())
    return update_state_timestamp(state)


def add_knowledge_triple_to_state(
    state: AgentState,
    subject: str,
    predicate: str,
    obj: str,
    context: str = "",
    confidence: float = 1.0,
    source: str = "agent"
) -> AgentState:
    """Add a knowledge triple to the state."""
    
    triple = KnowledgeTriple(
        triple_id=f"triple_{len(state['knowledge_triples'])}",
        subject=subject,
        predicate=predicate,
        object=obj,
        context=context,
        confidence=confidence,
        source=source
    )
    
    # Add triple to state
    state["knowledge_triples"].append(triple.model_dump())
    return update_state_timestamp(state)


def add_handoff_request(
    state: AgentState,
    from_agent: str,
    to_agent: str,
    task_description: str,
    data_to_transfer: Dict[str, Any],
    priority: str = "normal",
    context: Optional[Dict[str, Any]] = None
) -> AgentState:
    """Add a handoff request to the state."""
    
    handoff = HandoffRequest(
        handoff_id=f"handoff_{len(state['handoff_queue'])}",
        from_agent=from_agent,
        to_agent=to_agent,
        task_description=task_description,
        data_to_transfer=data_to_transfer,
        priority=priority,
        context=context or {}
    )
    
    # Add handoff to state
    state["handoff_queue"].append(handoff.model_dump())
    return update_state_timestamp(state)


def update_agent_availability(
    state: AgentState,
    agent_name: str,
    available: bool
) -> AgentState:
    """Update agent availability status."""
    
    if agent_name in state["agent_availability"]:
        state["agent_availability"][agent_name] = available
    
    return update_state_timestamp(state)


def update_memory_context(
    state: AgentState,
    memory_context: str,
    memory_query: str = ""
) -> AgentState:
    """Update memory context in the state."""
    
    state["memory_context"] = memory_context
    state["memory_query"] = memory_query
    state["memory_timestamp"] = datetime.now().isoformat()
    
    return update_state_timestamp(state)


def update_memory_stats(
    state: AgentState,
    stats: Dict[str, Any]
) -> AgentState:
    """Update memory statistics in the state."""
    
    state["memory_stats"] = stats
    return update_state_timestamp(state)
