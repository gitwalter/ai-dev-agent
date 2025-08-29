"""
Automated Testing Pipeline - US-002 Implementation

This module provides a fully automated testing pipeline with zero manual intervention,
following strict test-driven development principles.

Components:
- AutomatedTestingPipeline: Main orchestrator for automated testing
- CoverageTracker: Tracks and enforces test coverage requirements  
- CommitHookManager: Manages Git hooks for automated test execution
- TestReporter: Generates reports and sends notifications
- DeploymentBlocker: Blocks deployments when quality gates fail
"""

from .pipeline_manager import AutomatedTestingPipeline
from .coverage_tracker import CoverageTracker  
from .commit_hooks import CommitHookManager
from .test_reporter import AutomatedTestReporter
from .deployment_blocker import DeploymentBlocker

__all__ = [
    'AutomatedTestingPipeline',
    'CoverageTracker', 
    'CommitHookManager',
    'AutomatedTestReporter',
    'DeploymentBlocker'
]
