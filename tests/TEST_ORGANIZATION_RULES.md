# Test Organization Rules

## Overview

This document outlines the rules and guidelines for organizing tests in the AI Development Agent project. All tests must follow these rules to maintain consistency and ensure proper test discovery. This document aligns with the cursor rule for test organization and structure.

## Core Rules

### 1. All Tests Must Be in the `tests/` Directory

**Rule**: All test files must be located in the `tests/` directory or its subdirectories.

**Allowed Locations**:
- `tests/` (root test directory)
- `tests/unit/` (unit tests)
- `tests/integration/` (integration tests)
- `tests/system/` (system tests)
- `tests/langgraph/` (LangGraph-specific tests)
- `tests/isolated/` (isolated agent tests)
- `tests/supervisor/` (supervisor tests)
- `tests/performance/` (performance tests)
- `tests/security/` (security tests)
- `tests/fixtures/` (test fixtures and data)
- `tests/mocks/` (mock objects)

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

### Actual Project Structure

```
tests/
├── __init__.py                 # Package initialization
├── conftest.py                 # Shared pytest fixtures
├── test_utils.py               # Common test utilities
├── setup_test_environment.py   # Test environment setup
├── organize_tests.py           # Test organization script
├── TEST_ORGANIZATION_RULES.md  # This file
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── agents/                 # Agent unit tests
│   ├── models/                 # Model unit tests
│   ├── utils/                  # Utility function tests
│   └── test_base_agent.py
├── integration/                # Integration tests
│   ├── __init__.py
│   ├── agent_workflows/        # Multi-agent workflow tests
│   ├── test_agent_execution.py
│   ├── test_agents_simple.py
│   ├── test_api_key_validation.py
│   ├── test_gemini_integration.py
│   └── test_real_llm_integration.py
├── system/                     # System tests
│   ├── __init__.py
│   ├── complete_workflow/      # Full workflow tests
│   └── test_complete_workflow.py
├── langgraph/                  # LangGraph-specific tests
│   ├── __init__.py
│   ├── integration/            # LangGraph integration tests
│   ├── unit/                   # LangGraph unit tests
│   ├── test_basic_workflow.py
│   ├── test_simple_integration.py
│   ├── test_langgraph_workflow_integration.py
│   ├── test_workflow_manager.py
│   └── TEST_DEVELOPMENT_PLAN.md
├── isolated/                   # Isolated agent tests
│   ├── __init__.py
│   ├── test_problematic_agents.py
│   ├── test_code_reviewer_only.py
│   ├── debug_agent_factory.py
│   └── simple_agent_test.py
├── supervisor/                 # Supervisor tests
│   ├── __init__.py
│   ├── test_base_supervisor.py
│   ├── test_project_manager_supervisor.py
│   └── test_supervisor_state.py
├── performance/                # Performance tests
│   ├── __init__.py
│   └── README.md
├── security/                   # Security tests
│   ├── __init__.py
│   └── README.md
├── fixtures/                   # Test fixtures and data
│   ├── __init__.py
│   └── README.md
└── mocks/                      # Mock objects
    ├── __init__.py
    └── README.md
```

### Category Guidelines

#### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Use mocks for external dependencies
- Fast execution (< 1 second per test)
- High coverage of business logic
- Organized by component type (agents/, models/, utils/)

#### Integration Tests (`tests/integration/`)
- Test component interactions
- May use real external services
- Moderate execution time (1-10 seconds per test)
- Focus on data flow between components
- Include agent workflow tests

#### System Tests (`tests/system/`)
- Test complete workflows
- End-to-end scenarios
- Longer execution time (10+ seconds per test)
- Real external dependencies
- Complete workflow testing

#### LangGraph Tests (`tests/langgraph/`)
- Test LangGraph-specific functionality
- Individual node execution
- Workflow orchestration
- State management
- Graph validation
- Integration with LangChain components

#### Isolated Tests (`tests/isolated/`)
- Test problematic agents in isolation
- Debug agent-specific issues
- Mock inputs for parsing error resolution
- Agent factory debugging
- Simple agent testing scenarios

#### Supervisor Tests (`tests/supervisor/`)
- Test supervisor components
- Base supervisor functionality
- Project manager supervisor
- Supervisor state management
- Supervisor-agent interactions

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

@pytest.mark.langgraph
def test_langgraph_workflow():
    """LangGraph test for workflow orchestration."""
    pass

@pytest.mark.isolated
def test_agent_parsing():
    """Isolated test for agent parsing issues."""
    pass

@pytest.mark.supervisor
def test_supervisor_management():
    """Supervisor test for management functionality."""
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
- `@pytest.mark.langgraph` - LangGraph tests
- `@pytest.mark.isolated` - Isolated agent tests
- `@pytest.mark.supervisor` - Supervisor tests
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
import sys
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

## Test File Creation Rules

### When Creating New Tests
1. **Identify Test Type**: Determine if it's unit, integration, system, LangGraph, isolated, or supervisor test
2. **Choose Correct Directory**: Place in appropriate subfolder
3. **Follow Naming Convention**: Use required naming pattern
4. **Import Correctly**: Import from project root, not relative paths
5. **Use Proper Fixtures**: Leverage shared fixtures from `conftest.py`

### Required Test File Template
```python
#!/usr/bin/env python3
"""
Test file for <component_name>.

<Brief description of what this test file covers>
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import components to test
from <component_path> import <ComponentName>

class Test<ComponentName>:
    """Test cases for <ComponentName>."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pass
        
    def teardown_method(self):
        """Clean up after tests."""
        pass
        
    def test_<specific_functionality>(self):
        """Test <specific functionality description>."""
        # Test implementation
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

### 6. Parsing Error Resolution

- Use isolated tests for parsing error debugging
- Mock inputs to isolate parsing issues
- Test different parser types systematically
- Document successful parser-prompt combinations

## Troubleshooting

### Common Issues

1. **Test not discovered**: Check naming convention
2. **Import errors**: Use absolute imports from project root
3. **Fixture not found**: Check `conftest.py` and import statements
4. **Slow tests**: Use appropriate markers and consider optimization
5. **Parsing errors**: Use isolated tests with mocked inputs

### Getting Help

1. Check this document for rules and guidelines
2. Run validation script to identify issues
3. Review existing test files for examples
4. Consult the test utilities for common patterns
5. Use isolated tests for debugging specific issues

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
- [ ] Test is in correct subfolder based on type

## Updates and Maintenance

This document should be updated when:

- New test categories are added
- Naming conventions change
- Directory structure is modified
- New tools or scripts are added
- Best practices evolve
- Parsing error resolution patterns change

Keep this document synchronized with the actual test organization implementation and cursor rules.

## Alignment with Cursor Rules

This test organization aligns with the cursor rule for test organization and structure, ensuring:

- **Consistent Structure**: All tests follow the same organizational patterns
- **Proper Isolation**: Isolated tests for debugging specific issues
- **LangGraph Integration**: Dedicated tests for LangGraph functionality
- **Supervisor Testing**: Comprehensive supervisor component testing
- **Parsing Error Resolution**: Isolated tests for systematic parsing issue debugging
- **Performance and Security**: Dedicated test categories for specialized testing

## Benefits

- **Consistency**: Standardized test organization across the project
- **Maintainability**: Easy to find and update tests
- **Scalability**: Clear structure for adding new tests
- **Collaboration**: Team members can easily understand test organization
- **CI/CD Integration**: Clear test execution patterns for automation
- **Debugging**: Isolated tests for efficient issue resolution
- **Framework Support**: Dedicated support for LangGraph and supervisor components
