"""
Response models for the AI Development Agent system.
100% Pydantic V2 and LangChain compatible.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(BaseModel):
    """Result of a single task execution - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    task_id: str = Field(description="Unique identifier for the task")
    status: TaskStatus = Field(description="Current status of the task")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task execution result")
    message: str = Field(description="Status message or description")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the result")


class WorkflowResult(BaseModel):
    """Result of a complete workflow execution - LangChain compatible."""
    model_config = ConfigDict(
        extra="allow",  # Allow extra fields for workflow flexibility
        validate_assignment=True
    )
    
    # Core workflow fields
    workflow_id: str = Field(description="Unique identifier for the workflow")
    status: str = Field(description="Overall workflow status")
    tasks: List[TaskResult] = Field(default_factory=list, description="Results of individual tasks")
    start_time: datetime = Field(default_factory=datetime.now, description="Workflow start time")
    
    # Extended workflow fields (previously missing)
    session_id: Optional[str] = Field(None, description="Session identifier")
    project_name: Optional[str] = Field(None, description="Project name")
    project_context: Optional[str] = Field(None, description="Project context description")
    agent_results: Dict[str, Any] = Field(default_factory=dict, description="Agent execution results")
    generated_files: Dict[str, Any] = Field(default_factory=dict, description="Generated file data")
    code_files: Dict[str, Any] = Field(default_factory=dict, description="Generated code files")
    test_files: Dict[str, Any] = Field(default_factory=dict, description="Generated test files")
    documentation_files: Dict[str, Any] = Field(default_factory=dict, description="Generated documentation files")
    configuration_files: Dict[str, Any] = Field(default_factory=dict, description="Generated configuration files")
    diagram_files: Dict[str, Any] = Field(default_factory=dict, description="Generated diagram files")
    total_execution_time: Optional[float] = Field(None, description="Total execution time in seconds")
    end_time: Optional[datetime] = Field(None, description="Workflow end time")
    human_approvals: List[str] = Field(default_factory=list, description="Human approval requests")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    raw_state: Optional[Dict[str, Any]] = Field(None, description="Raw workflow state for enhanced display")


class AgentResponse(BaseModel):
    """Response from an individual agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="allow",  # Allow extra fields for agent flexibility
        validate_assignment=True
    )
    
    # Core agent response fields
    agent_name: str = Field(description="Name of the responding agent")
    content: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response content")
    status: Optional[TaskStatus] = Field(None, description="Response status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    # Extended agent response fields (previously missing)
    task_name: Optional[str] = Field(None, description="Task name")
    output: Dict[str, Any] = Field(default_factory=dict, description="Agent output data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Agent metadata")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if any")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    documentation: Dict[str, Any] = Field(default_factory=dict, description="Generated documentation")
    logs: List[str] = Field(default_factory=list, description="Agent log messages")
    decisions: List[str] = Field(default_factory=list, description="Agent decisions made")
    artifacts: List[str] = Field(default_factory=list, description="Generated artifacts")


class RequirementsAnalysisResponse(BaseModel):
    """Response from requirements analysis agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    functional_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="List of functional requirements")
    non_functional_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="List of non-functional requirements")
    business_rules: List[Dict[str, Any]] = Field(default_factory=list, description="List of business rules")
    constraints: List[Dict[str, Any]] = Field(default_factory=list, description="List of constraints")
    assumptions: List[Dict[str, Any]] = Field(default_factory=list, description="List of assumptions")
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="List of dependencies")
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="List of identified risks")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Analysis summary")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


class ArchitectureDesignResponse(BaseModel):
    """Response from architecture design agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    architecture_overview: Dict[str, Any] = Field(default_factory=dict, description="Overall architecture description")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="System components")
    data_flow: Dict[str, Any] = Field(default_factory=dict, description="Data flow design")
    technology_stack: Dict[str, Any] = Field(default_factory=dict, description="Technology stack")
    patterns: List[str] = Field(default_factory=list, description="Design patterns used")
    scalability: Dict[str, Any] = Field(default_factory=dict, description="Scalability considerations")
    security: Dict[str, Any] = Field(default_factory=dict, description="Security design")
    timestamp: datetime = Field(default_factory=datetime.now, description="Design timestamp")


class CodeGenerationResponse(BaseModel):
    """Response from code generation agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    generated_code: Dict[str, str] = Field(default_factory=dict, description="Generated code files")
    file_structure: Dict[str, Any] = Field(default_factory=dict, description="Project file structure")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    setup_instructions: List[str] = Field(default_factory=list, description="Setup instructions")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Code quality metrics")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")


class TestGenerationResponse(BaseModel):
    """Response from test generation agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    test_files: Dict[str, str] = Field(default_factory=dict, description="Generated test files")
    test_coverage: float = Field(ge=0, le=100, description="Test coverage percentage")
    test_strategy: str = Field(description="Testing strategy")
    frameworks: List[str] = Field(default_factory=list, description="Test frameworks used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")


class CodeReviewResponse(BaseModel):
    """Response from code review agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    review_summary: Dict[str, Any] = Field(default_factory=dict, description="Review summary")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Code issues found")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Improvement recommendations")
    quality_score: float = Field(ge=0, le=100, description="Code quality score")
    timestamp: datetime = Field(default_factory=datetime.now, description="Review timestamp")


class SecurityAnalysisResponse(BaseModel):
    """Response from security analysis agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    security_summary: Dict[str, Any] = Field(default_factory=dict, description="Security analysis summary")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Security vulnerabilities")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Security recommendations")
    compliance: Dict[str, Any] = Field(default_factory=dict, description="Compliance status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


class DocumentationResponse(BaseModel):
    """Response from documentation generation agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    documentation_files: Dict[str, str] = Field(default_factory=dict, description="Generated documentation files")
    api_docs: Dict[str, Any] = Field(default_factory=dict, description="API documentation")
    user_guides: Dict[str, str] = Field(default_factory=dict, description="User guides")
    technical_docs: Dict[str, str] = Field(default_factory=dict, description="Technical documentation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")


class AgentResult(BaseModel):
    """Generic agent result - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    status: str = Field(description="Result status")
    message: str = Field(description="Result message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Result timestamp")


class AgentStatus(str, Enum):
    """Status of an agent."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"
