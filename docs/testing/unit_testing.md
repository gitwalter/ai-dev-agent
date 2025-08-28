# Unit Tests

This directory contains unit tests for individual components of the AI Development Agent system. Unit tests focus on testing individual functions, methods, and classes in isolation.

## 🧪 Unit Testing Overview

Unit tests are designed to test individual components in isolation, ensuring that each piece of functionality works correctly independently of other components.

### Test Organization

```
tests/unit/
├── agents/                 # Agent unit tests
│   ├── test_base_agent.py
│   ├── test_requirements_analyst.py
│   ├── test_architecture_designer.py
│   ├── test_code_generator.py
│   ├── test_test_generator.py
│   ├── test_code_reviewer.py
│   ├── test_security_analyst.py
│   └── test_documentation_generator.py
├── workflow/               # Workflow unit tests
│   ├── test_workflow_manager.py
│   ├── test_workflow_graph.py
│   ├── test_error_handler.py
│   └── test_human_approval.py
├── models/                 # Model unit tests
│   ├── test_config.py
│   ├── test_state.py
│   ├── test_responses.py
│   └── test_supervisor_state.py
├── utils/                  # Utility unit tests
│   ├── test_output_parsers.py
│   ├── test_file_manager.py
│   ├── test_prompt_manager.py
│   └── test_rag_processor.py
└── apps/                   # Application unit tests
    ├── test_main.py
    └── test_streamlit_app.py
```

## 🎯 Testing Standards

### Test Structure

Each unit test should follow this structure:

```python
import pytest
from unittest.mock import Mock, patch
from your_module import YourClass

class TestYourClass:
    """Test suite for YourClass."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = YourClass()
    
    def test_method_name_success_case(self):
        """Test successful execution of method_name."""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_output"
        
        # Act
        result = self.instance.method_name(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_method_name_error_case(self):
        """Test error handling in method_name."""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid input"):
            self.instance.method_name(invalid_input)
```

### Testing Principles

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Single Responsibility**: Each test should test one specific behavior
3. **Clear Naming**: Test names should clearly describe what is being tested
4. **Arrange-Act-Assert**: Follow the AAA pattern for test structure
5. **Mocking**: Use mocks to isolate the unit under test

### Test Categories

#### 1. **Success Tests**
- Test normal operation with valid inputs
- Verify expected outputs
- Test edge cases within valid ranges

#### 2. **Error Tests**
- Test error handling with invalid inputs
- Verify appropriate exceptions are raised
- Test error messages and types

#### 3. **Boundary Tests**
- Test boundary conditions
- Test minimum and maximum values
- Test empty/null inputs

#### 4. **Integration Tests**
- Test interactions between methods within the same class
- Test state changes and side effects
- Test method chaining

## 🔧 Test Configuration

### Pytest Configuration

The project uses pytest for unit testing with the following configuration:

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    system: System tests
    slow: Slow running tests
```

### Test Fixtures

Common test fixtures are defined in `conftest.py`:

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = Mock()
    mock.invoke.return_value = "Mock response"
    return mock

@pytest.fixture
def sample_state():
    """Sample workflow state for testing."""
    return {
        "project_name": "test-project",
        "project_description": "Test project description",
        "requirements": {},
        "architecture": {},
        "code": {},
        "tests": {},
        "review": {},
        "security": {},
        "documentation": {},
        "metadata": {}
    }
```

## 🚀 Running Unit Tests

### Run All Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run with verbose output
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Run agent tests only
pytest tests/unit/agents/

# Run workflow tests only
pytest tests/unit/workflow/

# Run model tests only
pytest tests/unit/models/

# Run utility tests only
pytest tests/unit/utils/
```

### Run Specific Test Files

```bash
# Run specific test file
pytest tests/unit/agents/test_requirements_analyst.py

# Run specific test class
pytest tests/unit/agents/test_requirements_analyst.py::TestRequirementsAnalyst

# Run specific test method
pytest tests/unit/agents/test_requirements_analyst.py::TestRequirementsAnalyst::test_parse_response
```

## 📊 Test Coverage

### Coverage Requirements

- **Minimum Coverage**: 90% code coverage for all components
- **Critical Paths**: 100% coverage for critical business logic
- **Error Handling**: 100% coverage for error handling code
- **Public APIs**: 100% coverage for public API methods

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

## 🛡️ Mocking and Stubbing

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

class TestAgent:
    @patch('agents.base_agent.ChatGoogleGenerativeAI')
    def test_execute_with_mock_llm(self, mock_llm_class):
        """Test agent execution with mocked LLM."""
        # Arrange
        mock_llm = Mock()
        mock_llm.invoke.return_value = "Mock response"
        mock_llm_class.return_value = mock_llm
        
        agent = BaseAgent()
        
        # Act
        result = agent.execute({"input": "test"})
        
        # Assert
        assert result is not None
        mock_llm.invoke.assert_called_once()
```

### Mocking File Operations

```python
@patch('builtins.open', mock_open(read_data='test content'))
def test_file_reading(self):
    """Test file reading with mocked file operations."""
    # Arrange
    file_manager = FileManager()
    
    # Act
    content = file_manager.read_file("test.txt")
    
    # Assert
    assert content == "test content"
```

## 🔍 Test Debugging

### Debugging Failed Tests

```bash
# Run with debug output
pytest tests/unit/ -v -s

# Run specific failing test with debug
pytest tests/unit/test_specific.py::test_method -v -s --pdb

# Run with maximum verbosity
pytest tests/unit/ -vvv
```

### Common Debugging Techniques

1. **Print Statements**: Add print statements to understand test flow
2. **Pytest Debugger**: Use `--pdb` flag for interactive debugging
3. **Mock Inspection**: Inspect mock calls and arguments
4. **State Inspection**: Check object state during test execution

## 📈 Performance Testing

### Test Performance Requirements

- **Execution Time**: Unit tests should complete within 1 second
- **Memory Usage**: Tests should not exceed reasonable memory limits
- **Resource Cleanup**: Tests should clean up resources properly

### Performance Testing Examples

```python
import time
import pytest

def test_performance():
    """Test that operation completes within time limit."""
    start_time = time.time()
    
    # Act
    result = perform_operation()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Assert
    assert execution_time < 1.0  # Should complete within 1 second
    assert result is not None
```

## 🧹 Test Maintenance

### Test Maintenance Guidelines

1. **Keep Tests Updated**: Update tests when code changes
2. **Remove Obsolete Tests**: Remove tests for removed functionality
3. **Refactor Tests**: Refactor tests to improve maintainability
4. **Review Test Quality**: Regularly review test quality and coverage

### Test Review Checklist

- [ ] Tests are independent and isolated
- [ ] Tests have clear, descriptive names
- [ ] Tests follow AAA pattern
- [ ] Tests use appropriate mocks and stubs
- [ ] Tests cover success and error cases
- [ ] Tests have good coverage
- [ ] Tests are maintainable and readable

## 📚 Related Documentation

- **Integration Tests**: See `tests/integration/` for integration tests
- **System Tests**: See `tests/system/` for system tests
- **Test Configuration**: See `pytest.ini` for test configuration
- **Test Utilities**: See `conftest.py` for test fixtures and utilities
- **Testing Standards**: See `TEST_ORGANIZATION_RULES.md` for testing standards

## 🤝 Contributing

### Adding New Unit Tests

1. **Follow Patterns**: Adhere to established test patterns
2. **Use Fixtures**: Use existing fixtures or create new ones
3. **Mock Dependencies**: Mock external dependencies appropriately
4. **Test Edge Cases**: Include boundary and error case tests
5. **Maintain Coverage**: Ensure good test coverage

### Unit Test Standards

- **Isolation**: Each test should be completely independent
- **Clarity**: Tests should be clear and easy to understand
- **Completeness**: Tests should cover all important scenarios
- **Performance**: Tests should be fast and efficient
- **Maintainability**: Tests should be easy to maintain and update

---

**Last Updated**: Current session  
**Version**: 1.0  
**Maintainer**: Development Team
