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


class TaskResult(BaseModel):
    """Result of a single task execution - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    task_id: str = Field(description="Unique identifier for the task")
    status: TaskStatus = Field(description="Current status of the task")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task execution result")
    message: str = Field(description="Status message or description")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the result")


class WorkflowResult(BaseModel):
    """Result of a complete workflow execution - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    workflow_id: str = Field(description="Unique identifier for the workflow")
    status: str = Field(description="Overall workflow status")
    tasks: List[TaskResult] = Field(default_factory=list, description="Results of individual tasks")
    start_time: datetime = Field(default_factory=datetime.now, description="Workflow start time")


class AgentResponse(BaseModel):
    """Response from an individual agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    agent_name: str = Field(description="Name of the responding agent")
    content: Dict[str, Any] = Field(description="Response content")
    status: TaskStatus = Field(description="Response status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
