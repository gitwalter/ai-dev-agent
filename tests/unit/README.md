# Unit Tests

This directory contains unit tests for individual components of the AI Development Agent system.

## Quick Reference

For comprehensive unit testing documentation, see **[docs/testing/unit_testing.md](../../docs/testing/unit_testing.md)**.

## Test Structure

```
tests/unit/
├── test_config.py                    # Configuration testing
├── test_output_parsers.py            # Output parser testing
├── test_prompt_manager.py            # Prompt management testing
├── test_structured_outputs.py       # Structured output testing
└── test_workflow_manager.py          # Workflow testing
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