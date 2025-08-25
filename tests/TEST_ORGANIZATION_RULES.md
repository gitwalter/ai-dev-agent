# Test Organization Rules

## Overview

This document outlines the rules and guidelines for organizing tests in the AI Development Agent project. All tests must follow these rules to maintain consistency and ensure proper test discovery.

## Core Rules

### 1. All Tests Must Be in the `tests/` Directory

**Rule**: All test files must be located in the `tests/` directory or its subdirectories.

**Allowed Locations**:
- `tests/` (root test directory)
- `tests/unit/` (unit tests)
- `tests/integration/` (integration tests)
- `tests/system/` (system tests)
- `tests/performance/` (performance tests)
- `tests/security/` (security tests)

**Forbidden Locations**:
- Root project directory
- Any source code directory (`agents/`, `models/`, `utils/`, etc.)
- Any other location outside the `tests/` directory

### 2. Test File Naming Conventions

**Rule**: Test files must follow specific naming patterns to be discovered by pytest.

**Required Patterns**:
- `test_*.py` - Files starting with "test_"
- `*_test.py` - Files ending with "_test.py"

**Examples**:
- ✅ `test_agent_execution.py`
- ✅ `test_base_agent.py`
- ✅ `agent_test.py`
- ✅ `workflow_test.py`
- ❌ `agent_tests.py` (no underscore)
- ❌ `testagent.py` (no underscore)

### 3. Test Function Naming

**Rule**: Test functions must start with "test_".

**Examples**:
- ✅ `def test_agent_initialization():`
- ✅ `def test_workflow_execution():`
- ❌ `def testagent():` (no underscore)
- ❌ `def agent_test():` (wrong order)

### 4. Test Class Naming

**Rule**: Test classes must start with "Test".

**Examples**:
- ✅ `class TestAgentExecution:`
- ✅ `class TestWorkflowManager:`
- ❌ `class AgentTest:` (wrong order)
- ❌ `class test_agent:` (lowercase)

## Directory Structure

### Recommended Structure

```
tests/
├── __init__.py                 # Package initialization
├── conftest.py                 # Shared pytest fixtures
├── test_utils.py               # Common test utilities
├── TEST_ORGANIZATION_RULES.md  # This file
├── TEST_INDEX.md               # Auto-generated test index
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/                # Integration tests
│   ├── __init__.py
│   ├── test_workflow.py
│   └── test_api.py
├── system/                     # System tests
│   ├── __init__.py
│   └── test_end_to_end.py
├── performance/                # Performance tests
│   ├── __init__.py
│   └── test_workflow_performance.py
├── security/                   # Security tests
│   ├── __init__.py
│   └── test_security_analysis.py
├── fixtures/                   # Test fixtures and data
│   ├── __init__.py
│   └── sample_data.py
└── mocks/                      # Mock objects
    ├── __init__.py
    └── mock_responses.py
```

### Category Guidelines

#### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Use mocks for external dependencies
- Fast execution (< 1 second per test)
- High coverage of business logic

#### Integration Tests (`tests/integration/`)
- Test component interactions
- May use real external services
- Moderate execution time (1-10 seconds per test)
- Focus on data flow between components

#### System Tests (`tests/system/`)
- Test complete workflows
- End-to-end scenarios
- Longer execution time (10+ seconds per test)
- Real external dependencies

#### Performance Tests (`tests/performance/`)
- Measure execution time and resource usage
- Load testing scenarios
- Benchmark comparisons
- Marked with `@pytest.mark.performance`

#### Security Tests (`tests/security/`)
- Test security vulnerabilities
- Input validation testing
- Authentication and authorization
- Marked with `@pytest.mark.security`

## Test Markers

### Required Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_agent_initialization():
    """Unit test for agent initialization."""
    pass

@pytest.mark.integration
def test_workflow_execution():
    """Integration test for workflow execution."""
    pass

@pytest.mark.system
def test_end_to_end_workflow():
    """System test for complete workflow."""
    pass

@pytest.mark.performance
def test_workflow_performance():
    """Performance test for workflow execution."""
    pass

@pytest.mark.security
def test_input_validation():
    """Security test for input validation."""
    pass
```

### Available Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.system` - System tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.api` - Tests requiring API access
- `@pytest.mark.mock` - Tests using mocks
- `@pytest.mark.real` - Tests using real services

## Test Organization Script

### Automatic Organization

Use the test organization script to automatically move test files:

```bash
# Move test files to tests directory
python tests/organize_tests.py

# Dry run to see what would be moved
python tests/organize_tests.py --dry-run

# Create recommended directory structure
python tests/organize_tests.py --create-structure

# Validate test structure
python tests/organize_tests.py --validate

# Generate test index
python tests/organize_tests.py --generate-index
```

### Manual Organization

If automatic organization fails, manually move test files:

1. Identify test files outside `tests/` directory
2. Move them to appropriate subdirectory in `tests/`
3. Update imports if necessary
4. Run validation to ensure compliance

## Import Rules

### Test Imports

**Rule**: Tests should import from the project root, not relative paths.

**Correct**:
```python
from models.config import SystemConfig
from agents.base_agent import BaseAgent
from utils.logging_config import setup_logging
```

**Incorrect**:
```python
import sys
sys.path.append('../')
from models.config import SystemConfig
```

### Test Utilities

**Rule**: Use shared test utilities from `tests/test_utils.py` and fixtures from `tests/conftest.py`.

**Examples**:
```python
from tests.test_utils import TestConfig, MockGeminiClient
from tests.test_utils import create_mock_agent_response

def test_agent_execution(test_config, mock_gemini_client):
    """Test agent execution with shared utilities."""
    pass
```

## Validation and Enforcement

### Automated Validation

The test organization script validates compliance:

```bash
python tests/organize_tests.py --validate
```

### CI/CD Integration

Add validation to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Validate Test Organization
  run: python tests/organize_tests.py --validate
```

### Pre-commit Hooks

Add pre-commit hook to enforce rules:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: test-organization
      name: Test Organization
      entry: python tests/organize_tests.py --validate
      language: system
      files: ^tests/
```

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Use fixtures for setup and teardown
- Avoid shared state between tests

### 2. Descriptive Names

- Use descriptive test names
- Include the scenario being tested
- Make failures easy to understand

### 3. Documentation

- Document complex test scenarios
- Explain test data and fixtures
- Include examples in docstrings

### 4. Performance

- Keep unit tests fast (< 1 second)
- Use appropriate markers for slow tests
- Consider parallel execution for integration tests

### 5. Coverage

- Aim for high test coverage
- Focus on critical business logic
- Test edge cases and error conditions

## Troubleshooting

### Common Issues

1. **Test not discovered**: Check naming convention
2. **Import errors**: Use absolute imports from project root
3. **Fixture not found**: Check `conftest.py` and import statements
4. **Slow tests**: Use appropriate markers and consider optimization

### Getting Help

1. Check this document for rules and guidelines
2. Run validation script to identify issues
3. Review existing test files for examples
4. Consult the test utilities for common patterns

## Compliance Checklist

Before committing test files, ensure:

- [ ] Test file is in `tests/` directory
- [ ] Test file follows naming convention
- [ ] Test functions start with "test_"
- [ ] Test classes start with "Test"
- [ ] Appropriate pytest markers are used
- [ ] Imports use absolute paths from project root
- [ ] Test uses shared utilities and fixtures
- [ ] Test is properly documented
- [ ] Test follows isolation principles
- [ ] Validation script passes

## Updates and Maintenance

This document should be updated when:

- New test categories are added
- Naming conventions change
- Directory structure is modified
- New tools or scripts are added
- Best practices evolve

Keep this document synchronized with the actual test organization implementation.
