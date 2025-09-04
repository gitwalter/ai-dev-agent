#!/usr/bin/env python3
"""
Comprehensive validation and testing for context-aware rule system.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path at the very beginning to override any conflicting modules
project_root = Path(__file__).parent.parent.parent
if str(project_root) in sys.path:
    sys.path.remove(str(project_root))
sys.path.insert(0, str(project_root))

from utils import ReliableContextIntegration
from utils.reliable_context_integration import auto_switch_context_reliable

class TestContextSystemValidation:
    """Comprehensive validation tests for context system."""
    
    def setup_method(self):
        """Setup for each test."""
        self.integration = ReliableContextIntegration()
        self.cursor_rules_file = Path(".cursor-rules")
    
    def test_context_detection_accuracy(self):
        """Test context detection accuracy for all keywords."""
        test_cases = [
            ("@docs Update documentation", "DOCUMENTATION"),
            ("@code Implement features", "CODING"),
            ("@debug Fix issues", "DEBUGGING"),
            ("@test Run validation", "TESTING"),
            ("@agile Sprint planning", "AGILE"),
            ("@git Commit changes", "GIT_OPERATIONS"),
            ("@optimize Performance", "PERFORMANCE"),
            ("@security Audit system", "SECURITY"),
            ("General development work", "DEFAULT")
        ]
        
        correct_detections = 0
        total_tests = len(test_cases)
        
        for message, expected_context in test_cases:
            result = auto_switch_context_reliable(message)
            if result.get('context') == expected_context:
                correct_detections += 1
            else:
                print(f"Failed: '{message}' -> Expected: {expected_context}, Got: {result.get('context')}")
        
        accuracy = (correct_detections / total_tests) * 100
        assert accuracy >= 90, f"Context detection accuracy {accuracy}% below 90% threshold"
    
    def test_rule_count_reduction(self):
        """Test that rule count is significantly reduced per context."""
        contexts_to_test = [
            "@docs test",
            "@code test", 
            "@debug test",
            "@test test"
        ]
        
        for context_message in contexts_to_test:
            result = auto_switch_context_reliable(context_message)
            rule_count = result.get('new_rule_count', 0)
            
            # Should be between 6-10 rules per context (significant reduction from 33+)
            assert 6 <= rule_count <= 10, f"Rule count {rule_count} not in expected range 6-10 for {context_message}"
    
    def test_file_generation_and_reload(self):
        """Test that .cursor-rules file is generated and reload works."""
        # Test file generation
        result = auto_switch_context_reliable("@docs test file generation")
        
        assert result.get('success', True), f"Context switch failed: {result.get('error')}"
        assert self.cursor_rules_file.exists(), ".cursor-rules file not generated"
        assert result.get('reload_success', False), "File reload mechanism failed"
        assert result.get('file_changed', False), "File change not detected"
    
    def test_context_verification(self):
        """Test context verification functionality."""
        # Switch to known context
        result = auto_switch_context_reliable("@docs verification test")
        expected_context = result.get('context')
        
        # Verify context is active
        verification = self.integration.verify_context_active(expected_context)
        
        assert verification.get('verified', False), f"Context verification failed: {verification.get('reason')}"
        assert verification.get('context_found', False), "Context not found in .cursor-rules file"
        assert verification.get('rule_count', 0) > 0, "No rules found in verification"
    
    def test_error_handling_robustness(self):
        """Test error handling and fallback mechanisms."""
        # Test with invalid context
        result = auto_switch_context_reliable("@invalid_context test")
        
        # Should fallback to DEFAULT context
        assert result.get('context') == 'DEFAULT', "Invalid context should fallback to DEFAULT"
        
        # Test verification with non-existent file
        if self.cursor_rules_file.exists():
            self.cursor_rules_file.unlink()
        
        verification = self.integration.verify_context_active("TEST")
        assert not verification.get('verified', True), "Should fail verification when file missing"
        assert 'fallback' in verification, "Should provide fallback suggestion"
    
    def test_performance_benchmarks(self):
        """Test performance of context switching."""
        import time
        
        test_messages = [
            "@docs performance test",
            "@code performance test", 
            "@debug performance test"
        ]
        
        total_time = 0
        iterations = len(test_messages)
        
        for message in test_messages:
            start_time = time.time()
            result = auto_switch_context_reliable(message)
            end_time = time.time()
            
            switch_time = end_time - start_time
            total_time += switch_time
            
            # Each context switch should complete within 2 seconds
            assert switch_time < 2.0, f"Context switch too slow: {switch_time:.2f}s for {message}"
        
        avg_time = total_time / iterations
        assert avg_time < 1.0, f"Average context switch time {avg_time:.2f}s exceeds 1.0s threshold"
    
    def test_system_status_reporting(self):
        """Test system status and monitoring."""
        # Perform some context switches using the same integration instance
        self.integration.switch_context_with_reload("@docs status test")
        self.integration.switch_context_with_reload("@code status test")
        
        status = self.integration.get_system_status()
        
        assert status.get('cursor_rules_exists', False), "System should report .cursor-rules exists"
        assert status.get('cursor_rules_size', 0) > 0, "Rules file should have content"
        assert len(status.get('recent_contexts', [])) > 0, "Should track recent contexts"
        assert status.get('last_context') is not None, "Should track last context"
    
    def test_context_history_tracking(self):
        """Test context history and tracking functionality."""
        # Perform multiple context switches using the same integration instance
        contexts = ["@docs", "@code", "@debug", "@docs"]
        
        for context in contexts:
            self.integration.switch_context_with_reload(f"{context} history test")
        
        status = self.integration.get_system_status()
        recent_contexts = status.get('recent_contexts', [])
        
        # Should track recent context switches
        assert len(recent_contexts) > 0, "Should track context history"
        assert 'DOCUMENTATION' in recent_contexts, "Should track DOCUMENTATION context"
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up test artifacts but preserve working .cursor-rules
        pass

def run_validation_suite():
    """Run the complete validation suite."""
    print("Running Context System Validation Suite...")
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("✅ All validation tests passed")
    else:
        print("❌ Some validation tests failed")
    
    return exit_code

if __name__ == "__main__":
    run_validation_suite()
