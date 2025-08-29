"""
Agile Artifacts Automation System

This module provides automated updating of agile artifacts when stories are completed,
implementing the Live Documentation Updates Rule.
"""

from .artifacts_automation import (
    AgileArtifactsAutomator,
    StoryCompletion,
    ArtifactUpdateResult,
    ArtifactValidationResult
)

__all__ = [
    'AgileArtifactsAutomator',
    'StoryCompletion',
    'ArtifactUpdateResult', 
    'ArtifactValidationResult'
]
