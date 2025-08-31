# Unit Tests

This directory contains unit tests for individual components of the AI Development Agent system.

## Quick Reference

For comprehensive unit testing documentation, see **[docs/testing/unit_testing.md](../../docs/testing/unit_testing.md)**.

## Test Structure

```
tests/unit/
├── agents/
│   ├── test_agent_system.py         # Agent system testing
│   ├── test_test_generator.py       # Test generator unit tests
│   └── test_workflow_extraction.py  # Workflow extraction tests
├── prompts/
│   ├── test_advanced_prompt_optimization.py  # Prompt optimization
│   ├── test_prompt_engineering_system.py     # Prompt engineering
│   ├── test_prompt_interface_imports.py      # Prompt interface tests
│   └── test_prompt_management_infrastructure.py # Prompt infrastructure
├── test_base_agent.py               # Base agent testing
├── test_fast_utils.py               # Fast utility testing
├── test_intelligent_rule_loader.py  # Rule loader testing
├── test_quality_assurance.py        # QA system testing
├── test_strategic_rule_selector.py  # Rule selector testing
└── test_utils.py                    # General utility testing
```

## Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=src

# Run specific test
pytest tests/unit/test_output_parsers.py -v
```

## Key Testing Principles

1. **Isolation**: Each test is independent and isolated
2. **Single Responsibility**: Each test tests one specific behavior  
3. **Clear Naming**: Test names clearly describe what's being tested
4. **Arrange-Act-Assert**: Follow AAA pattern for test structure
5. **Mocking**: Use mocks to isolate the unit under test

## Coverage Requirements

- **Minimum Coverage**: 80% for unit tests
- **Critical Paths**: 100% coverage for critical business logic
- **Error Handling**: Complete coverage for error scenarios

---

**📖 For complete unit testing guidelines, best practices, and detailed examples, see [docs/testing/unit_testing.md](../../docs/testing/unit_testing.md)**

**🔗 For all testing documentation, see [docs/testing/](../../docs/testing/README.md)**