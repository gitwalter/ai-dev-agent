#!/usr/bin/env python3
"""
Comprehensive test suite for the Intelligent Rule Loader

Tests the distinction between checking rule applicability and selective application.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.rule_system.intelligent_rule_loader import (
    IntelligentRuleLoader, 
    TaskType, 
    TaskComplexity, 
    TaskContext,
    RuleSelection
)

class TestIntelligentRuleLoader:
    """Test suite for intelligent rule selection system."""
    
    @pytest.fixture
    def loader(self):
        """Create a fresh rule loader for each test."""
        return IntelligentRuleLoader()
    
    @pytest.fixture
    def simple_file_context(self):
        """Simple file operation context."""
        return TaskContext(
            task_type=TaskType.FILE_OPERATION,
            complexity=TaskComplexity.SIMPLE,
            time_pressure=0.3,
            quality_requirements=0.7
        )
    
    @pytest.fixture
    def complex_code_context(self):
        """Complex code implementation context."""
        return TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.COMPLEX,
            time_pressure=0.8,
            quality_requirements=0.9,
            security_requirements=0.8
        )
    
    @pytest.fixture
    def security_context(self):
        """Security-focused context."""
        return TaskContext(
            task_type=TaskType.SECURITY,
            complexity=TaskComplexity.MODERATE,
            security_requirements=0.9,
            quality_requirements=0.8
        )

    def test_always_check_applicability_but_selective_application(self, loader):
        """Test that rules are always checked but selectively applied."""
        
        # Test with a simple file operation
        task_description = "Move files to organize project structure"
        context = TaskContext(
            task_type=TaskType.FILE_OPERATION,
            complexity=TaskComplexity.SIMPLE
        )
        
        selection = loader.select_rules_for_task(task_description, context)
        
        # Verify that critical rules are always included
        critical_rules = [
            "SAFETY FIRST PRINCIPLE",
            "Context Awareness and Excellence Rule", 
            "No Premature Victory Declaration Rule"
        ]
        
        for rule in critical_rules:
            assert rule in selection.selected_rules, f"Critical rule {rule} should always be included"
        
        # Verify that file-specific rules are selected
        file_rules = [
            "File Organization Rule",
            "Clean Repository Focus Rule"
        ]
        
        selected_file_rules = [rule for rule in file_rules if rule in selection.selected_rules]
        assert len(selected_file_rules) > 0, "File operation rules should be selected for file tasks"
        
        # Verify that irrelevant rules are excluded
        code_rules = [
            "Test-Driven Development Rule",
            "Object-Oriented Programming Rule"
        ]
        
        excluded_code_rules = [rule for rule in code_rules if rule in selection.excluded_rules]
        assert len(excluded_code_rules) > 0, "Code rules should be excluded for file operations"
        
        # Verify token savings
        assert selection.estimated_token_savings > 0, "Should achieve token savings through selective application"
        
        # Verify reasoning is provided
        assert len(selection.selection_reasoning) > 0, "Should provide reasoning for selections"

    def test_critical_rules_always_included(self, loader):
        """Test that critical foundation rules are always included regardless of context."""
        
        contexts = [
            TaskContext(TaskType.FILE_OPERATION, TaskComplexity.TRIVIAL),
            TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.COMPLEX),
            TaskContext(TaskType.SECURITY, TaskComplexity.CRITICAL),
            TaskContext(TaskType.DOCUMENTATION, TaskComplexity.SIMPLE)
        ]
        
        critical_rules = [
            "SAFETY FIRST PRINCIPLE",
            "Context Awareness and Excellence Rule", 
            "No Premature Victory Declaration Rule"
        ]
        
        for context in contexts:
            selection = loader.select_rules_for_task("Test task", context)
            
            for rule in critical_rules:
                assert rule in selection.selected_rules, f"Critical rule {rule} should be included for {context.task_type}"

    def test_task_type_specific_selection(self, loader):
        """Test that rules are selected based on task type."""
        
        test_cases = [
            {
                "task_type": TaskType.CODE_IMPLEMENTATION,
                "task_description": "Implement a new function with proper testing",
                "expected_rules": ["Test-Driven Development Rule", "Best Practices and Standard Libraries Rule"],
                "unexpected_rules": ["File Organization Rule"]
            },
            {
                "task_type": TaskType.DOCUMENTATION,
                "task_description": "Update README and add comprehensive documentation",
                "expected_rules": ["Live Documentation Updates Rule", "Clear Documentation Rule"],
                "unexpected_rules": ["Object-Oriented Programming Rule"]
            },
            {
                "task_type": TaskType.SECURITY,
                "task_description": "Implement secure API key management",
                "expected_rules": ["Streamlit Secrets Management Rule"],
                "unexpected_rules": ["Keep It Small and Simple (KISS) Rule"]
            }
        ]
        
        for test_case in test_cases:
            context = TaskContext(
                task_type=test_case["task_type"],
                complexity=TaskComplexity.MODERATE
            )
            
            selection = loader.select_rules_for_task(test_case["task_description"], context)
            
            # Check expected rules are selected
            for expected_rule in test_case["expected_rules"]:
                if expected_rule in loader.rule_definitions:  # Only check if rule exists
                    assert expected_rule in selection.selected_rules, f"Expected rule {expected_rule} should be selected for {test_case['task_type']}"
            
            # Check unexpected rules are excluded
            for unexpected_rule in test_case["unexpected_rules"]:
                if unexpected_rule in loader.rule_definitions:  # Only check if rule exists
                    assert unexpected_rule in selection.excluded_rules, f"Unexpected rule {unexpected_rule} should be excluded for {test_case['task_type']}"

    def test_complexity_based_selection(self, loader):
        """Test that rule selection considers task complexity."""
        
        # Simple task should exclude complex rules
        simple_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.SIMPLE
        )
        
        simple_selection = loader.select_rules_for_task("Create a simple utility function", simple_context)
        
        # Complex task should include more sophisticated rules
        complex_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.COMPLEX
        )
        
        complex_selection = loader.select_rules_for_task("Design and implement a complex system architecture", complex_context)
        
        # Complex tasks should generally have more rules selected
        assert len(complex_selection.selected_rules) >= len(simple_selection.selected_rules), "Complex tasks should select more rules"

    def test_quality_requirements_affect_selection(self, loader):
        """Test that quality requirements affect rule selection."""
        
        # Low quality requirements
        low_quality_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            quality_requirements=0.3
        )
        
        low_quality_selection = loader.select_rules_for_task("Quick implementation", low_quality_context)
        
        # High quality requirements
        high_quality_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            quality_requirements=0.9
        )
        
        high_quality_selection = loader.select_rules_for_task("Production-ready implementation", high_quality_context)
        
        # Higher quality requirements should select more rules
        assert len(high_quality_selection.selected_rules) >= len(low_quality_selection.selected_rules), "Higher quality requirements should select more rules"

    def test_time_pressure_affects_selection(self, loader):
        """Test that time pressure affects rule selection."""
        
        # Low time pressure
        low_pressure_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            time_pressure=0.2
        )
        
        low_pressure_selection = loader.select_rules_for_task("Take time to implement properly", low_pressure_context)
        
        # High time pressure
        high_pressure_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            time_pressure=0.9
        )
        
        high_pressure_selection = loader.select_rules_for_task("Urgent implementation needed", high_pressure_context)
        
        # Higher time pressure should select fewer rules (higher threshold)
        assert len(high_pressure_selection.selected_rules) <= len(low_pressure_selection.selected_rules), "Higher time pressure should select fewer rules"

    def test_keyword_based_relevance(self, loader):
        """Test that keyword matching affects rule selection."""
        
        # Task with testing keywords
        testing_task = "Write comprehensive unit tests and integration tests for the new module"
        testing_context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        testing_selection = loader.select_rules_for_task(testing_task, testing_context)
        
        # Task without testing keywords
        non_testing_task = "Create a simple configuration file"
        non_testing_context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        non_testing_selection = loader.select_rules_for_task(non_testing_task, non_testing_context)
        
        # Testing task should be more likely to include testing rules
        testing_rules = ["Test-Driven Development Rule"]
        for rule in testing_rules:
            if rule in loader.rule_definitions:
                testing_included = rule in testing_selection.selected_rules
                non_testing_included = rule in non_testing_selection.selected_rules
                
                # Testing task should be more likely to include testing rules
                if testing_included and not non_testing_included:
                    break  # This is the expected behavior
                elif non_testing_included and not testing_included:
                    pytest.fail(f"Testing rule {rule} should be more likely for testing tasks")

    def test_security_requirements_affect_selection(self, loader):
        """Test that security requirements affect rule selection."""
        
        # Low security requirements
        low_security_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            security_requirements=0.2
        )
        
        low_security_selection = loader.select_rules_for_task("Internal utility function", low_security_context)
        
        # High security requirements
        high_security_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            security_requirements=0.9
        )
        
        high_security_selection = loader.select_rules_for_task("Secure authentication system", high_security_context)
        
        # High security context should be more likely to include security rules
        security_rules = ["Streamlit Secrets Management Rule", "No Silent Errors and Mock Fallbacks Rule"]
        for rule in security_rules:
            if rule in loader.rule_definitions:
                high_security_included = rule in high_security_selection.selected_rules
                low_security_included = rule in low_security_selection.selected_rules
                
                # High security should be more likely to include security rules
                if high_security_included and not low_security_included:
                    break  # Expected behavior
                elif low_security_included and not high_security_included:
                    pytest.fail(f"Security rule {rule} should be more likely for high security contexts")

    def test_confidence_score_calculation(self, loader):
        """Test that confidence scores are calculated correctly."""
        
        # Task with clear keywords and intent
        clear_task = "Implement comprehensive unit tests for the authentication module with proper error handling"
        clear_context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        clear_selection = loader.select_rules_for_task(clear_task, clear_context)
        
        # Task with vague description
        vague_task = "Do something"
        vague_context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        vague_selection = loader.select_rules_for_task(vague_task, vague_context)
        
        # Clear task should have higher confidence
        assert clear_selection.confidence_score >= vague_selection.confidence_score, "Clear tasks should have higher confidence scores"

    def test_token_savings_calculation(self, loader):
        """Test that token savings are calculated correctly."""
        
        context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        selection = loader.select_rules_for_task("Test task", context)
        
        # Should always have some token savings (not all rules selected)
        assert selection.estimated_token_savings > 0, "Should achieve token savings through selective application"
        
        # Token savings should be reasonable (not negative)
        assert selection.estimated_token_savings < 10000, "Token savings should be reasonable"

    def test_selection_reasoning(self, loader):
        """Test that selection reasoning is provided for all rules."""
        
        context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        selection = loader.select_rules_for_task("Test task", context)
        
        # All selected rules should have reasoning
        for rule in selection.selected_rules:
            assert rule in selection.selection_reasoning, f"Selected rule {rule} should have reasoning"
            assert selection.selection_reasoning[rule], f"Selected rule {rule} should have non-empty reasoning"
        
        # All excluded rules should have reasoning
        for rule in selection.excluded_rules:
            assert rule in selection.selection_reasoning, f"Excluded rule {rule} should have reasoning"
            assert selection.selection_reasoning[rule], f"Excluded rule {rule} should have non-empty reasoning"

    def test_selection_history_tracking(self, loader):
        """Test that rule selections are tracked in history."""
        
        initial_history_count = len(loader.selection_history)
        
        context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        selection = loader.select_rules_for_task("Test task", context)
        
        # History should be updated
        assert len(loader.selection_history) == initial_history_count + 1, "Selection should be recorded in history"
        
        # Get summary
        summary = loader.get_selection_summary()
        assert summary["total_selections"] > 0, "Should have selection history"

    def test_edge_cases(self, loader):
        """Test edge cases and boundary conditions."""
        
        # Empty task description
        context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
        selection = loader.select_rules_for_task("", context)
        
        # Should still include critical rules
        critical_rules = ["SAFETY FIRST PRINCIPLE", "Context Awareness and Excellence Rule", "No Premature Victory Declaration Rule"]
        for rule in critical_rules:
            assert rule in selection.selected_rules, f"Critical rule {rule} should be included even with empty description"
        
        # Very long task description
        long_description = "This is a very long task description " * 50
        selection = loader.select_rules_for_task(long_description, context)
        
        # Should still work and provide reasonable results
        assert len(selection.selected_rules) > 0, "Should select rules even with very long description"
        assert selection.confidence_score > 0, "Should have positive confidence score"

    def test_performance_requirements_affect_selection(self, loader):
        """Test that performance requirements affect rule selection."""
        
        # Low performance requirements
        low_perf_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            performance_requirements=0.2
        )
        
        low_perf_selection = loader.select_rules_for_task("Simple utility function", low_perf_context)
        
        # High performance requirements
        high_perf_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            performance_requirements=0.9
        )
        
        high_perf_selection = loader.select_rules_for_task("High-performance algorithm implementation", high_perf_context)
        
        # High performance context should be more likely to include performance-related rules
        performance_rules = ["Keep It Small and Simple (KISS) Rule"]
        for rule in performance_rules:
            if rule in loader.rule_definitions:
                high_perf_included = rule in high_perf_selection.selected_rules
                low_perf_included = rule in low_perf_selection.selected_rules
                
                # High performance should be more likely to include performance rules
                if high_perf_included and not low_perf_included:
                    break  # Expected behavior
                elif low_perf_included and not high_perf_included:
                    pytest.fail(f"Performance rule {rule} should be more likely for high performance contexts")

    def test_domain_specific_selection(self, loader):
        """Test that domain affects rule selection."""
        
        # Web development domain
        web_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            domain="web_development"
        )
        
        web_selection = loader.select_rules_for_task("Create a web API endpoint", web_context)
        
        # Data science domain
        data_context = TaskContext(
            task_type=TaskType.CODE_IMPLEMENTATION,
            complexity=TaskComplexity.MODERATE,
            domain="data_science"
        )
        
        data_selection = loader.select_rules_for_task("Implement a machine learning model", data_context)
        
        # Different domains might select different rules (though current implementation is simplified)
        # This test ensures the system handles different domains gracefully
        assert len(web_selection.selected_rules) > 0, "Web domain should select rules"
        assert len(data_selection.selected_rules) > 0, "Data science domain should select rules"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
