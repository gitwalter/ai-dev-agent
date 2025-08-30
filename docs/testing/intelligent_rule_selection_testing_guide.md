# Intelligent Rule Selection Testing Guide

## Overview

The Intelligent Rule Selection system implements the crucial distinction between **checking rule applicability** and **selective application**. This guide explains how to test this system correctly.

## Key Concepts

### 1. Always Check Applicability
- **Every rule is evaluated** for relevance to the current task
- **All rules are analyzed** against task context, keywords, and requirements
- **No rules are ignored** - the system considers all available rules

### 2. Selective Application
- **Only the most relevant rules** are selected for actual application
- **Token savings** are achieved by excluding irrelevant rules
- **Context-aware selection** based on task type, complexity, and requirements

## Testing Approach

### 1. Unit Testing

#### Test Structure
```python
def test_rule_selection_behavior():
    """Test that rules are checked but selectively applied."""
    
    # Setup
    loader = IntelligentRuleLoader()
    context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
    
    # Execute
    selection = loader.select_rules_for_task("Implement secure authentication", context)
    
    # Verify
    assert len(selection.selected_rules) > 0, "Should select some rules"
    assert len(selection.excluded_rules) > 0, "Should exclude irrelevant rules"
    assert selection.estimated_token_savings > 0, "Should achieve token savings"
```

#### Critical Tests

**Test 1: Critical Rules Always Included**
```python
def test_critical_rules_always_included():
    """Verify critical foundation rules are always selected."""
    
    critical_rules = [
        "SAFETY FIRST PRINCIPLE",
        "Context Awareness and Excellence Rule", 
        "No Premature Victory Declaration Rule"
    ]
    
    # Test across different contexts
    contexts = [
        TaskContext(TaskType.FILE_OPERATION, TaskComplexity.TRIVIAL),
        TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.COMPLEX),
        TaskContext(TaskType.SECURITY, TaskComplexity.CRITICAL)
    ]
    
    for context in contexts:
        selection = loader.select_rules_for_task("Test task", context)
        
        for rule in critical_rules:
            assert rule in selection.selected_rules, f"Critical rule {rule} should always be included"
```

**Test 2: Task-Specific Selection**
```python
def test_task_type_specific_selection():
    """Verify rules are selected based on task type."""
    
    test_cases = [
        {
            "task_type": TaskType.CODE_IMPLEMENTATION,
            "expected_rules": ["Test-Driven Development Rule"],
            "unexpected_rules": ["File Organization Rule"]
        },
        {
            "task_type": TaskType.DOCUMENTATION,
            "expected_rules": ["Live Documentation Updates Rule"],
            "unexpected_rules": ["Object-Oriented Programming Rule"]
        }
    ]
    
    for test_case in test_cases:
        context = TaskContext(test_case["task_type"], TaskComplexity.MODERATE)
        selection = loader.select_rules_for_task("Test task", context)
        
        # Check expected rules are selected
        for expected_rule in test_case["expected_rules"]:
            if expected_rule in loader.rule_definitions:
                assert expected_rule in selection.selected_rules
```

**Test 3: Context-Aware Selection**
```python
def test_context_affects_selection():
    """Verify that context affects rule selection."""
    
    # Same task, different contexts
    task_description = "Create a new function"
    
    # Low quality, high time pressure
    low_quality_context = TaskContext(
        task_type=TaskType.CODE_IMPLEMENTATION,
        complexity=TaskComplexity.SIMPLE,
        time_pressure=0.9,
        quality_requirements=0.3
    )
    
    # High quality, low time pressure
    high_quality_context = TaskContext(
        task_type=TaskType.CODE_IMPLEMENTATION,
        complexity=TaskComplexity.SIMPLE,
        time_pressure=0.2,
        quality_requirements=0.9
    )
    
    low_quality_selection = loader.select_rules_for_task(task_description, low_quality_context)
    high_quality_selection = loader.select_rules_for_task(task_description, high_quality_context)
    
    # High quality should select more rules
    assert len(high_quality_selection.selected_rules) >= len(low_quality_selection.selected_rules)
```

### 2. Integration Testing

#### Test Rule Selection in Workflow
```python
def test_rule_selection_in_workflow():
    """Test rule selection integrated with actual workflow."""
    
    # Simulate a real development task
    workflow = DevelopmentWorkflow()
    
    # File operation task
    file_task = {
        "description": "Organize project files and clean up temporary files",
        "context": TaskContext(TaskType.FILE_OPERATION, TaskComplexity.SIMPLE)
    }
    
    # Code implementation task
    code_task = {
        "description": "Implement secure authentication with comprehensive testing",
        "context": TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.COMPLEX)
    }
    
    # Verify different rule selections
    file_selection = workflow.select_rules(file_task)
    code_selection = workflow.select_rules(code_task)
    
    # File task should include file-specific rules
    assert "File Organization Rule" in file_selection.selected_rules
    
    # Code task should include code-specific rules
    assert "Test-Driven Development Rule" in code_selection.selected_rules
    
    # Code task should exclude file-specific rules
    assert "File Organization Rule" in code_selection.excluded_rules
```

### 3. Performance Testing

#### Test Token Savings
```python
def test_token_savings():
    """Verify that intelligent selection achieves token savings."""
    
    loader = IntelligentRuleLoader()
    
    # Test multiple task types
    test_tasks = [
        ("File organization", TaskContext(TaskType.FILE_OPERATION, TaskComplexity.SIMPLE)),
        ("Code implementation", TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)),
        ("Documentation update", TaskContext(TaskType.DOCUMENTATION, TaskComplexity.SIMPLE))
    ]
    
    total_savings = 0
    for task_desc, context in test_tasks:
        selection = loader.select_rules_for_task(task_desc, context)
        total_savings += selection.estimated_token_savings
        
        # Each task should achieve some savings
        assert selection.estimated_token_savings > 0
    
    # Should achieve significant total savings
    assert total_savings > 1000, "Should achieve significant token savings"
```

#### Test Selection Efficiency
```python
def test_selection_efficiency():
    """Verify selection process is efficient."""
    
    import time
    
    loader = IntelligentRuleLoader()
    context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
    
    # Measure selection time
    start_time = time.time()
    selection = loader.select_rules_for_task("Test task", context)
    end_time = time.time()
    
    selection_time = end_time - start_time
    
    # Selection should be fast (under 100ms)
    assert selection_time < 0.1, f"Selection took {selection_time:.3f}s, should be under 0.1s"
```

### 4. Edge Case Testing

#### Test Boundary Conditions
```python
def test_edge_cases():
    """Test edge cases and boundary conditions."""
    
    loader = IntelligentRuleLoader()
    
    # Empty task description
    context = TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)
    selection = loader.select_rules_for_task("", context)
    
    # Should still include critical rules
    critical_rules = ["SAFETY FIRST PRINCIPLE", "Context Awareness and Excellence Rule"]
    for rule in critical_rules:
        assert rule in selection.selected_rules
    
    # Very long task description
    long_description = "This is a very long task description " * 50
    selection = loader.select_rules_for_task(long_description, context)
    
    # Should still work and provide reasonable results
    assert len(selection.selected_rules) > 0
    assert selection.confidence_score > 0
```

#### Test Invalid Contexts
```python
def test_invalid_contexts():
    """Test behavior with invalid or extreme context values."""
    
    loader = IntelligentRuleLoader()
    
    # Extreme values
    extreme_context = TaskContext(
        task_type=TaskType.CODE_IMPLEMENTATION,
        complexity=TaskComplexity.CRITICAL,
        time_pressure=1.0,  # Maximum pressure
        quality_requirements=0.0,  # Minimum quality
        security_requirements=1.0  # Maximum security
    )
    
    selection = loader.select_rules_for_task("Test task", extreme_context)
    
    # Should still provide valid results
    assert len(selection.selected_rules) > 0
    assert len(selection.excluded_rules) > 0
    assert selection.confidence_score > 0
```

## Running the Tests

### 1. Run All Tests
```bash
# Run all intelligent rule selection tests
python -m pytest tests/unit/test_intelligent_rule_loader.py -v

# Run with coverage
python -m pytest tests/unit/test_intelligent_rule_loader.py --cov=utils.rule_system.intelligent_rule_loader -v
```

### 2. Run Specific Test Categories
```bash
# Run only critical rule tests
python -m pytest tests/unit/test_intelligent_rule_loader.py -k "critical" -v

# Run only context tests
python -m pytest tests/unit/test_intelligent_rule_loader.py -k "context" -v

# Run only performance tests
python -m pytest tests/unit/test_intelligent_rule_loader.py -k "performance" -v
```

### 3. Run Demo Script
```bash
# Run the demonstration script
python scripts/demo_intelligent_rule_selection.py
```

## Expected Test Results

### 1. Selection Metrics
- **File Operations**: 5-7 rules selected, 10-12 rules excluded
- **Code Implementation**: 12-16 rules selected, 1-5 rules excluded
- **Documentation**: 6-8 rules selected, 9-11 rules excluded
- **Security**: 5-7 rules selected, 10-12 rules excluded

### 2. Token Savings
- **Simple tasks**: 1500-2500 tokens saved
- **Complex tasks**: 500-1500 tokens saved
- **Average savings**: 1000-2000 tokens per task

### 3. Confidence Scores
- **Clear tasks**: 0.8-1.0 confidence
- **Vague tasks**: 0.6-0.8 confidence
- **Critical rules**: Always included (confidence boost)

## Validation Checklist

### Before Running Tests
- [ ] All rule definitions are properly configured
- [ ] Task types and complexity levels are defined
- [ ] Keyword patterns are comprehensive
- [ ] Relevance thresholds are appropriate

### During Testing
- [ ] Critical rules are always included
- [ ] Task-specific rules are selected appropriately
- [ ] Context affects selection as expected
- [ ] Token savings are achieved
- [ ] Reasoning is provided for all decisions

### After Testing
- [ ] All tests pass
- [ ] Performance is acceptable
- [ ] Edge cases are handled
- [ ] Documentation is updated

## Troubleshooting

### Common Issues

**Issue**: Tests failing because expected rules are not selected
**Solution**: Check relevance thresholds and keyword matching logic

**Issue**: No token savings achieved
**Solution**: Verify rule definitions have proper token costs

**Issue**: Critical rules missing
**Solution**: Check `_get_critical_foundation_rules()` method

**Issue**: Poor performance
**Solution**: Optimize keyword matching and relevance calculation

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run tests with debug output
python -m pytest tests/unit/test_intelligent_rule_loader.py -v -s
```

## Best Practices

### 1. Test Design
- Test both positive and negative cases
- Verify edge cases and boundary conditions
- Test performance and efficiency
- Validate reasoning and metrics

### 2. Test Maintenance
- Update tests when rule definitions change
- Add tests for new task types or complexity levels
- Monitor test performance over time
- Keep tests focused and specific

### 3. Continuous Improvement
- Collect metrics on rule selection effectiveness
- Analyze which rules are frequently excluded
- Optimize relevance calculation algorithms
- Refine keyword patterns based on usage

## Conclusion

The intelligent rule selection system successfully implements the distinction between checking applicability and selective application. The comprehensive test suite ensures that:

1. **All rules are checked** for relevance to every task
2. **Only the most relevant rules** are selected for application
3. **Critical foundation rules** are always included
4. **Significant token savings** are achieved
5. **Context-aware selection** works correctly
6. **Reasoning is provided** for all decisions

This system dramatically improves efficiency while maintaining excellence standards through intelligent, context-aware rule selection.
