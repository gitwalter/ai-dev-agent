"""
Workflow Orchestration Module

Provides intelligent workflow orchestration capabilities for the AI-Dev-Agent system.
Implements automated task analysis, workflow composition, and agent coordination.

Main Components:
- WorkflowOrchestrationEngine: Core orchestration engine
- WorkflowOrchestrationTeam: Specialized team for workflow design
- Integration interfaces for existing agent systems

Usage:
    from workflow.orchestration import create_workflow_orchestration_engine
    
    async with WorkflowOrchestrator() as orchestrator:
        results = await orchestrator.orchestrate_task("Implement user auth system")
        print(f"Status: {results['status']}")
"""

from .workflow_orchestration_engine import (
    WorkflowOrchestrationEngine,
    WorkflowOrchestrator,
    create_workflow_orchestration_engine,
    WorkflowStatus,
    WorkflowExecution
)

__all__ = [
    'WorkflowOrchestrationEngine',
    'WorkflowOrchestrator', 
    'create_workflow_orchestration_engine',
    'WorkflowStatus',
    'WorkflowExecution'
]

# Version info
__version__ = "1.0.0"
__author__ = "AI-Dev-Agent Workflow Orchestration Team"
