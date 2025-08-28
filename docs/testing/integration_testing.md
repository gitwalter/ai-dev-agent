# Integration Tests

This directory contains integration tests for the AI Development Agent system. Integration tests focus on testing the interactions between different components and ensuring they work together correctly.

## 🔗 Integration Testing Overview

Integration tests verify that multiple components work together correctly, testing the interfaces and interactions between different parts of the system.

### Test Organization

```
tests/integration/
├── agents/                 # Agent integration tests
│   ├── test_agent_workflows.py
│   ├── test_agent_communication.py
│   └── test_agent_state_flow.py
├── workflow/               # Workflow integration tests
│   ├── test_workflow_execution.py
│   ├── test_workflow_state_management.py
│   └── test_workflow_error_handling.py
├── models/                 # Model integration tests
│   ├── test_config_integration.py
│   ├── test_state_integration.py
│   └── test_response_integration.py
├── utils/                  # Utility integration tests
│   ├── test_parser_integration.py
│   ├── test_file_manager_integration.py
│   └── test_prompt_manager_integration.py
├── apps/                   # Application integration tests
│   ├── test_app_integration.py
│   └── test_streamlit_integration.py
└── end_to_end/            # End-to-end integration tests
    ├── test_complete_workflow.py
    ├── test_agent_chain.py
    └── test_system_integration.py
```

## 🎯 Testing Standards

### Test Structure

Each integration test should follow this structure:

```python
import pytest
from unittest.mock import Mock, patch
from agents.requirements_analyst import RequirementsAnalyst
from agents.architecture_designer import ArchitectureDesigner
from workflow.workflow_manager import WorkflowManager

class TestAgentWorkflowIntegration:
    """Test integration between agents and workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.workflow_manager = WorkflowManager()
        self.requirements_analyst = RequirementsAnalyst()
        self.architecture_designer = ArchitectureDesigner()
    
    def test_requirements_to_architecture_flow(self):
        """Test complete flow from requirements to architecture."""
        # Arrange
        project_description = "Create a REST API for user management"
        expected_requirements_count = 10
        
        # Act
        requirements_result = self.requirements_analyst.execute({
            "project_description": project_description
        })
        
        architecture_result = self.architecture_designer.execute({
            "requirements": requirements_result,
            "project_description": project_description
        })
        
        # Assert
        assert len(requirements_result["functional_requirements"]) >= expected_requirements_count
        assert "system_architecture" in architecture_result
        assert "technology_stack" in architecture_result
```

### Testing Principles

1. **Component Interaction**: Test how components interact with each other
2. **Data Flow**: Verify data flows correctly between components
3. **State Management**: Test state transitions and persistence
4. **Error Propagation**: Test how errors propagate between components
5. **Performance**: Test performance of component interactions

### Test Categories

#### 1. **Agent Integration Tests**
- Test interactions between different agents
- Verify data flow between agents
- Test agent handoff and state transfer
- Test agent communication patterns

#### 2. **Workflow Integration Tests**
- Test complete workflow execution
- Verify workflow state management
- Test workflow error handling and recovery
- Test workflow performance and scalability

#### 3. **Model Integration Tests**
- Test configuration integration across components
- Verify state management integration
- Test response model integration
- Test data validation and transformation

#### 4. **Utility Integration Tests**
- Test utility integration with other components
- Verify utility performance in integrated scenarios
- Test utility error handling in context
- Test utility resource management

#### 5. **Application Integration Tests**
- Test application integration with backend components
- Verify user interface integration
- Test application error handling
- Test application performance

## 🔧 Test Configuration

### Integration Test Configuration

```python
# conftest.py - Integration test fixtures
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm_integration():
    """Mock LLM for integration testing."""
    mock = Mock()
    mock.invoke.side_effect = [
        "Requirements response",
        "Architecture response",
        "Code response"
    ]
    return mock

@pytest.fixture
def sample_workflow_state():
    """Sample workflow state for integration testing."""
    return {
        "project_name": "integration-test-project",
        "project_description": "Test project for integration testing",
        "requirements": {
            "functional_requirements": [
                {"id": "REQ-001", "title": "User Registration"}
            ],
            "non_functional_requirements": [
                {"id": "NFR-001", "title": "Response Time"}
            ]
        },
        "architecture": {},
        "code": {},
        "tests": {},
        "review": {},
        "security": {},
        "documentation": {},
        "metadata": {}
    }
```

### Test Environment Setup

```python
# test_integration_setup.py
import pytest
import tempfile
import os

@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment for integration tests."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Set up test configuration
    test_config = {
        "output_dir": temp_dir,
        "enable_logging": False,
        "test_mode": True
    }
    
    yield test_config
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
```

## 🚀 Running Integration Tests

### Run All Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run with verbose output
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html
```

### Run Specific Integration Test Categories

```bash
# Run agent integration tests
pytest tests/integration/agents/

# Run workflow integration tests
pytest tests/integration/workflow/

# Run end-to-end tests
pytest tests/integration/end_to_end/

# Run specific integration test
pytest tests/integration/agents/test_agent_workflows.py
```

### Run Integration Tests with Markers

```bash
# Run slow integration tests
pytest tests/integration/ -m slow

# Run fast integration tests
pytest tests/integration/ -m "not slow"

# Run specific marker tests
pytest tests/integration/ -m "agent_integration"
```

## 📊 Test Coverage

### Integration Coverage Requirements

- **Component Interaction**: 100% coverage of component interfaces
- **Data Flow**: 100% coverage of data flow paths
- **Error Scenarios**: 100% coverage of error propagation
- **State Transitions**: 100% coverage of state transitions

### Coverage Reporting

```bash
# Generate integration test coverage
pytest tests/integration/ --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

## 🛡️ Mocking and Stubbing

### Mocking External Dependencies

```python
class TestAgentWorkflowIntegration:
    @patch('agents.base_agent.ChatGoogleGenerativeAI')
    @patch('workflow.workflow_manager.FileManager')
    def test_complete_workflow_integration(self, mock_file_manager, mock_llm_class):
        """Test complete workflow integration with mocked dependencies."""
        # Arrange
        mock_llm = Mock()
        mock_llm.invoke.side_effect = [
            "Requirements response",
            "Architecture response",
            "Code response"
        ]
        mock_llm_class.return_value = mock_llm
        
        mock_file_manager.return_value.create_project_structure.return_value = True
        
        workflow_manager = WorkflowManager()
        
        # Act
        result = workflow_manager.execute_workflow({
            "project_description": "Test project"
        })
        
        # Assert
        assert result["status"] == "completed"
        assert mock_llm.invoke.call_count == 3
        mock_file_manager.return_value.create_project_structure.assert_called_once()
```

### Mocking Database Operations

```python
@patch('utils.prompt_manager.sqlite3.connect')
def test_prompt_manager_integration(self, mock_db_connect):
    """Test prompt manager integration with mocked database."""
    # Arrange
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = ("Test prompt",)
    mock_db_connect.return_value.cursor.return_value = mock_cursor
    
    prompt_manager = PromptManager()
    
    # Act
    prompt = prompt_manager.get_prompt("requirements_analyst", "main")
    
    # Assert
    assert prompt == "Test prompt"
    mock_cursor.execute.assert_called_once()
```

## 🔍 Test Debugging

### Debugging Integration Tests

```bash
# Run with debug output
pytest tests/integration/ -v -s

# Run specific failing test with debug
pytest tests/integration/test_specific.py::test_method -v -s --pdb

# Run with maximum verbosity
pytest tests/integration/ -vvv
```

### Common Integration Test Issues

1. **State Pollution**: Tests affecting each other's state
2. **Resource Conflicts**: Tests competing for shared resources
3. **Timing Issues**: Race conditions in concurrent operations
4. **Mock Configuration**: Incorrect mock setup for integration scenarios

### Debugging Techniques

```python
# Add debugging to integration tests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_debug_integration():
    """Test with debugging output."""
    logger.debug("Starting integration test")
    
    # Test steps with logging
    logger.debug("Step 1: Initialize components")
    component1 = Component1()
    component2 = Component2()
    
    logger.debug("Step 2: Execute integration")
    result = component1.integrate_with(component2)
    
    logger.debug(f"Step 3: Verify result: {result}")
    assert result is not None
```

## 📈 Performance Testing

### Integration Performance Requirements

- **Response Time**: Integration operations should complete within 5 seconds
- **Memory Usage**: Integration tests should not exceed memory limits
- **Resource Cleanup**: Tests should clean up resources properly
- **Concurrency**: Tests should handle concurrent operations correctly

### Performance Testing Examples

```python
import time
import pytest

def test_integration_performance():
    """Test integration performance."""
    start_time = time.time()
    
    # Act - Execute integration test
    workflow_manager = WorkflowManager()
    result = workflow_manager.execute_workflow({
        "project_description": "Performance test project"
    })
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Assert
    assert execution_time < 5.0  # Should complete within 5 seconds
    assert result["status"] == "completed"
```

## 🧹 Test Maintenance

### Integration Test Maintenance

1. **Keep Tests Updated**: Update tests when component interfaces change
2. **Monitor Performance**: Track integration test performance over time
3. **Review Dependencies**: Regularly review and update test dependencies
4. **Clean Up Resources**: Ensure proper cleanup of test resources

### Integration Test Review Checklist

- [ ] Tests verify component interactions correctly
- [ ] Tests cover all integration paths
- [ ] Tests handle error scenarios properly
- [ ] Tests are performant and efficient
- [ ] Tests clean up resources properly
- [ ] Tests are maintainable and readable
- [ ] Tests provide good coverage of integration scenarios

## 📚 Related Documentation

- **Unit Tests**: See `tests/unit/` for unit tests
- **System Tests**: See `tests/system/` for system tests
- **Test Configuration**: See `pytest.ini` for test configuration
- **Test Utilities**: See `conftest.py` for test fixtures and utilities
- **Testing Standards**: See `TEST_ORGANIZATION_RULES.md` for testing standards

## 🤝 Contributing

### Adding New Integration Tests

1. **Follow Patterns**: Adhere to established integration test patterns
2. **Test Interactions**: Focus on component interactions and data flow
3. **Mock Appropriately**: Mock external dependencies but test real component interactions
4. **Test Error Scenarios**: Include error propagation and recovery tests
5. **Maintain Performance**: Ensure tests are performant and efficient

### Integration Test Standards

- **Interaction Focus**: Tests should focus on component interactions
- **Realistic Scenarios**: Tests should reflect real-world usage scenarios
- **Error Handling**: Tests should verify error propagation and recovery
- **Performance**: Tests should be performant and efficient
- **Maintainability**: Tests should be easy to maintain and update

---

**Last Updated**: Current session  
**Version**: 1.0  
**Maintainer**: Development Team
