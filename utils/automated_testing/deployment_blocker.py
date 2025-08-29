#!/usr/bin/env python3
"""
DeploymentBlocker - Deployment blocking based on quality gates

This class blocks deployments when tests fail or quality gates are not met
for US-002: Fully Automated Testing Pipeline.

TDD Implementation: Minimal viable code to pass the comprehensive test suite.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeploymentReadinessResult:
    """Result object for deployment readiness check."""
    deployment_allowed: bool = False
    blocking_reason: Optional[str] = None
    failed_tests: List[str] = None
    current_coverage: float = 0.0
    quality_gates_passed: bool = False

    def __post_init__(self):
        if self.failed_tests is None:
            self.failed_tests = []


class DeploymentBlocker:
    """
    Blocks deployments when quality gates fail or tests don't pass.
    
    Enforces quality gates including test success, coverage requirements,
    and performance validation before allowing deployments.
    """

    def __init__(self, min_coverage: float = 90.0, max_response_time_ms: int = 200):
        """
        Initialize the deployment blocker.
        
        Args:
            min_coverage: Minimum required test coverage percentage
            max_response_time_ms: Maximum allowed response time in milliseconds
        """
        self.min_coverage = min_coverage
        self.max_response_time_ms = max_response_time_ms
        
        logger.info(f"DeploymentBlocker initialized (coverage: {min_coverage}%, response: {max_response_time_ms}ms)")

    def check_deployment_readiness(self, test_results: Dict[str, Any]) -> DeploymentReadinessResult:
        """
        Check if deployment should be allowed based on test results and quality gates.
        
        Args:
            test_results: Dictionary containing test execution results
            
        Returns:
            DeploymentReadinessResult with deployment decision
        """
        result = DeploymentReadinessResult()
        
        # Extract test results
        test_success = test_results.get('success', False)
        failed_tests = test_results.get('failed_tests', [])
        coverage = test_results.get('coverage', 0.0)
        
        result.failed_tests = failed_tests
        result.current_coverage = coverage
        
        # Check test success
        if not test_success or len(failed_tests) > 0:
            result.deployment_allowed = False
            result.blocking_reason = f"Test failures detected: {len(failed_tests)} tests failed"
            return result
        
        # Check coverage requirement
        if coverage < self.min_coverage:
            result.deployment_allowed = False
            result.blocking_reason = f"Coverage {coverage}% below minimum {self.min_coverage}%"
            return result
        
        # Check performance if provided
        performance_metrics = test_results.get('performance_metrics', {})
        if performance_metrics:
            max_response = performance_metrics.get('max_response_time', 0)
            if max_response > self.max_response_time_ms:
                result.deployment_allowed = False
                result.blocking_reason = f"Performance issue: {max_response}ms > {self.max_response_time_ms}ms"
                return result
        
        # All quality gates passed
        result.deployment_allowed = True
        result.blocking_reason = None
        result.quality_gates_passed = True
        
        logger.info("All quality gates passed - deployment allowed")
        return result

    def get_quality_gates_status(self, test_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed status of all quality gates.
        
        Args:
            test_results: Test execution results
            
        Returns:
            Dictionary with detailed quality gate status
        """
        gates_status = {}
        
        # Test success gate
        test_success = test_results.get('success', False)
        failed_tests = test_results.get('failed_tests', [])
        gates_status['test_success'] = {
            'passed': test_success and len(failed_tests) == 0,
            'details': f"{len(failed_tests)} failed tests" if failed_tests else "All tests passed",
            'blocking': not test_success or len(failed_tests) > 0
        }
        
        # Coverage gate
        coverage = test_results.get('coverage', 0.0)
        gates_status['coverage'] = {
            'passed': coverage >= self.min_coverage,
            'details': f"Coverage {coverage}% (required: {self.min_coverage}%)",
            'blocking': coverage < self.min_coverage
        }
        
        # Performance gate
        performance_metrics = test_results.get('performance_metrics', {})
        if performance_metrics:
            max_response = performance_metrics.get('max_response_time', 0)
            gates_status['performance'] = {
                'passed': max_response <= self.max_response_time_ms,
                'details': f"Max response {max_response}ms (limit: {self.max_response_time_ms}ms)",
                'blocking': max_response > self.max_response_time_ms
            }
        
        return gates_status

    def block_deployment(self, reason: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Explicitly block deployment with a specific reason.
        
        Args:
            reason: Reason for blocking deployment
            details: Additional details about the blocking
            
        Returns:
            True if deployment was blocked
        """
        logger.warning(f"Deployment blocked: {reason}")
        if details:
            logger.warning(f"Blocking details: {details}")
        
        # In a real implementation, this would integrate with CI/CD systems
        # to actually prevent deployment (e.g., exit with error code,
        # update deployment status, send notifications, etc.)
        
        return True

    def allow_deployment(self, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Allow deployment after all quality gates pass.
        
        Args:
            details: Details about the successful validation
            
        Returns:
            True if deployment is allowed
        """
        logger.info("Deployment allowed - all quality gates passed")
        if details:
            logger.info(f"Deployment details: {details}")
        
        # In a real implementation, this would integrate with CI/CD systems
        # to proceed with deployment
        
        return True

    def get_blocking_summary(self, test_results: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of what's blocking deployment.
        
        Args:
            test_results: Test execution results
            
        Returns:
            Summary string of blocking issues
        """
        readiness = self.check_deployment_readiness(test_results)
        
        if readiness.deployment_allowed:
            return "✅ No blocking issues - deployment ready"
        
        blocking_issues = []
        
        # Check each quality gate
        gates_status = self.get_quality_gates_status(test_results)
        
        for gate_name, gate_info in gates_status.items():
            if gate_info['blocking']:
                blocking_issues.append(f"❌ {gate_name.title()}: {gate_info['details']}")
        
        if not blocking_issues:
            blocking_issues.append(f"❌ {readiness.blocking_reason}")
        
        return "🚫 Deployment blocked:\n" + "\n".join(blocking_issues)
