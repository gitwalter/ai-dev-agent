"""
Specialized team agents module.

This module contains specialized team agents that handle specific domains
or complex coordinated tasks requiring multiple agent collaboration.
"""

from .specialized_subagent_team import SpecializedSubagentTeam
from .workflow_orchestration_team import WorkflowOrchestrationTeam

__all__ = [
    'SpecializedSubagentTeam',
    'WorkflowOrchestrationTeam'
]
