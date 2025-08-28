"""
Pytest configuration and fixtures for configurable testing

Supports both MOCK and REAL test execution modes with automatic provider selection.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add the tests directory to the path so we can import mock modules
sys.path.insert(0, str(Path(__file__).parent))

# Import test configuration system
try:
    from tests.config.test_config import (
        pytest_configure as config_pytest_configure,
        pytest_addoption as config_pytest_addoption,
        pytest_collection_modifyitems as config_pytest_collection_modifyitems,
        get_test_config,
        is_mock_mode
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Mock the problematic imports at the module level
mock_modules = [
    'utils.structured_outputs',
    'utils.output_parsers',
    'agents.requirements_analyst',
    'agents.architecture_designer',
    'agents.code_generator',
    'agents.test_generator',
    'agents.code_reviewer',
    'agents.security_analyst',
    'agents.documentation_generator',
    'langgraph_workflow_manager',
    'langgraph_workflow'
]

def pytest_addoption(parser):
    """Add pytest command-line options."""
    if CONFIG_AVAILABLE:
        config_pytest_addoption(parser)


def pytest_configure(config):
    """Configure pytest with test mode support."""
    if CONFIG_AVAILABLE:
        config_pytest_configure(config)


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on current mode."""
    if CONFIG_AVAILABLE:
        config_pytest_collection_modifyitems(config, items)


@pytest.fixture(autouse=True, scope='session')
def mock_structured_outputs():
    """Mock all structured output imports in MOCK mode only"""
    
    # Only apply mocks in MOCK mode or when config not available
    if CONFIG_AVAILABLE and not is_mock_mode():
        print("🔄 Running in REAL mode - skipping mock initialization")
        yield
        return
    
    print("🔄 Running in MOCK mode - initializing mocks")
    # Import our mock module
    from tests.mock_structured_outputs import (
        RequirementsAnalysisOutput,
        ArchitectureDesignOutput,
        CodeGenerationOutput,
        TestGenerationOutput,
        CodeReviewOutput,
        SecurityAnalysisOutput,
        DocumentationGenerationOutput,
        ProjectPlanOutput,
        CodeQualityScore,
        Issue,
        Recommendation
    )

    # Create mock objects for each problematic module
    mock_objects = {}

    for module_name in mock_modules:
        mock_module = MagicMock()
        mock_module.__name__ = module_name

        # Add the key classes to each mock module
        mock_module.RequirementsAnalysisOutput = RequirementsAnalysisOutput
        mock_module.ArchitectureDesignOutput = ArchitectureDesignOutput
        mock_module.CodeGenerationOutput = CodeGenerationOutput
        mock_module.TestGenerationOutput = TestGenerationOutput
        mock_module.CodeReviewOutput = CodeReviewOutput
        mock_module.SecurityAnalysisOutput = SecurityAnalysisOutput
        mock_module.DocumentationGenerationOutput = DocumentationGenerationOutput
        mock_module.ProjectPlanOutput = ProjectPlanOutput
        mock_module.CodeQualityScore = CodeQualityScore
        mock_module.Issue = Issue
        mock_module.Recommendation = Recommendation
        
        # Add LangGraph workflow manager mock classes
        if module_name == 'langgraph_workflow_manager':
            mock_module.LangGraphWorkflowManager = MagicMock
            mock_module.AgentNodeFactory = MagicMock
            mock_module.AgentState = MagicMock

        mock_objects[module_name] = mock_module

    # Patch sys.modules with our mock objects
    original_modules = {}
    for module_name, mock_module in mock_objects.items():
        if module_name in sys.modules:
            original_modules[module_name] = sys.modules[module_name]
        sys.modules[module_name] = mock_module

    yield

    # Restore original modules
    for module_name in mock_objects:
        if module_name in original_modules:
            sys.modules[module_name] = original_modules[module_name]
        else:
            sys.modules.pop(module_name, None)

@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    from unittest.mock import MagicMock
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock()
    mock_llm.invoke.return_value.content = '{"test": "response"}'
    return mock_llm

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "requirements_analysis": {
            "requirements": [
                {
                    "id": "FR-001",
                    "description": "User authentication system",
                    "type": "functional",
                    "priority": "high"
                }
            ]
        }
    }

@pytest.fixture
def mock_agent_config():
    """Mock agent configuration"""
    return {
        "name": "test_agent",
        "prompt_template": "Test prompt template for {task}",
        "system_prompt": "You are a test agent. Please analyze the requirements.",
        "model": "gemini-2.5-flash-lite",
        "temperature": 0.1
    }

@pytest.fixture
def sample_state():
    """Sample workflow state for testing"""
    return {
        "requirements": "Build a simple web application",
        "architecture": {
            "design": "MVC pattern",
            "tech_stack": ["Python", "FastAPI", "SQLite"]
        },
        "code_files": {},
        "agent_outputs": {},
        "errors": [],
        "workflow_history": []
    }

@pytest.fixture
def basic_state():
    """Basic workflow state for testing"""
    return {
        "requirements": "Build a calculator app",
        "architecture": {},
        "code_files": {},
        "agent_outputs": {},
        "errors": [],
        "workflow_history": []
    }