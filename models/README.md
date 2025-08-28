# Data Models

This directory contains all data models, schemas, and configuration management for the AI Development Agent system. The models provide type safety, validation, and structured data handling throughout the system.

## 🏗️ Model Architecture

The models system provides a comprehensive data layer with the following components:

### Core Models

#### 1. **Configuration Management** (`config.py`)
- **Purpose**: Centralized configuration management and validation
- **Features**:
  - Environment-based configuration loading
  - API key management and validation
  - Model selection configuration
  - Workflow configuration options
  - Security settings and validation

#### 2. **State Management** (`state.py`)
- **Purpose**: Workflow state management and persistence
- **Features**:
  - TypedDict-based state structure
  - State validation and type checking
  - State persistence and recovery
  - State transition management
  - Metadata tracking

#### 3. **Supervisor State** (`supervisor_state.py`)
- **Purpose**: Supervisor-specific state management
- **Features**:
  - Supervisor workflow state
  - Agent coordination state
  - Quality gate state management
  - Progress tracking and monitoring
  - Error state handling

#### 4. **Response Models** (`responses.py`)
- **Purpose**: Structured response models for all agents
- **Features**:
  - Agent-specific response schemas
  - Response validation and parsing
  - Error response handling
  - Response transformation utilities
  - Type-safe response handling

#### 5. **Simplified Responses** (`simplified_responses.py`)
- **Purpose**: Simplified response models for basic operations
- **Features**:
  - Streamlined response schemas
  - Quick response validation
  - Basic error handling
  - Performance-optimized parsing
  - Minimal response overhead

## 📊 Model Structure

### Configuration Model

```python
class Config(TypedDict):
    api_keys: Dict[str, str]
    models: Dict[str, str]
    workflow: Dict[str, Any]
    logging: Dict[str, Any]
    security: Dict[str, Any]
    monitoring: Dict[str, Any]
```

### State Model

```python
class WorkflowState(TypedDict):
    project_name: str
    project_description: str
    requirements: Dict[str, Any]
    architecture: Dict[str, Any]
    code: Dict[str, Any]
    tests: Dict[str, Any]
    review: Dict[str, Any]
    security: Dict[str, Any]
    documentation: Dict[str, Any]
    metadata: Dict[str, Any]
```

### Response Models

Each agent has specific response models:

```python
class RequirementsResponse(TypedDict):
    functional_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[Dict[str, Any]]
    technical_constraints: List[str]
    assumptions: List[str]
    acceptance_criteria: List[Dict[str, Any]]

class ArchitectureResponse(TypedDict):
    system_architecture: Dict[str, Any]
    technology_stack: Dict[str, Any]
    database_design: Dict[str, Any]
    api_specifications: Dict[str, Any]
    security_considerations: List[str]
```

## 🔧 Configuration Management

### Environment Configuration

The configuration system supports multiple configuration sources:

```python
# Environment-based configuration
config = load_config_from_env()

# File-based configuration
config = load_config_from_file("config.yaml")

# Streamlit secrets configuration
config = load_config_from_streamlit_secrets()
```

### Configuration Validation

All configuration is validated for:

- **Required Fields**: Ensure all required fields are present
- **Type Validation**: Validate data types and formats
- **Value Validation**: Validate configuration values
- **Security Validation**: Validate security settings
- **Dependency Validation**: Validate configuration dependencies

### API Key Management

Secure API key management through multiple sources:

```python
# Streamlit secrets (recommended)
api_key = st.secrets.get("GEMINI_API_KEY")

# Environment variables
api_key = os.environ.get("GEMINI_API_KEY")

# Configuration file
api_key = config.get("api_keys", {}).get("gemini_api_key")
```

## 🔄 State Management

### State Structure

The workflow state follows a hierarchical structure:

```python
# Main workflow state
state = {
    "project_name": "user-management-api",
    "project_description": "REST API for user management",
    "requirements": {
        "functional": [...],
        "non_functional": [...],
        "constraints": [...]
    },
    "architecture": {
        "system_design": {...},
        "technology_stack": {...},
        "database_design": {...}
    },
    "code": {
        "files": {...},
        "structure": {...},
        "dependencies": {...}
    },
    "tests": {
        "unit_tests": {...},
        "integration_tests": {...},
        "system_tests": {...}
    },
    "review": {
        "code_quality": {...},
        "recommendations": [...],
        "issues": [...]
    },
    "security": {
        "vulnerabilities": [...],
        "recommendations": [...],
        "compliance": {...}
    },
    "documentation": {
        "readme": {...},
        "api_docs": {...},
        "user_manual": {...}
    },
    "metadata": {
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "status": "completed"
    }
}
```

### State Validation

State validation ensures data integrity:

```python
# State validation
def validate_state(state: WorkflowState) -> bool:
    """Validate workflow state structure and content."""
    # Check required fields
    # Validate data types
    # Validate content
    # Check dependencies
    return True
```

### State Persistence

State can be persisted and recovered:

```python
# Save state
save_state(state, "checkpoint.json")

# Load state
state = load_state("checkpoint.json")

# Validate loaded state
if validate_state(state):
    continue_workflow(state)
```

## 📝 Response Models

### Agent Response Structure

Each agent produces structured responses:

```python
# Example: Requirements Analyst Response
requirements_response = {
    "functional_requirements": [
        {
            "id": "REQ-001",
            "title": "User Registration",
            "description": "System shall allow users to register",
            "priority": "high",
            "category": "authentication"
        }
    ],
    "non_functional_requirements": [
        {
            "id": "NFR-001",
            "title": "Response Time",
            "description": "API responses within 200ms",
            "category": "performance"
        }
    ],
    "technical_constraints": [
        "Must use Python 3.8+",
        "Must support PostgreSQL"
    ],
    "assumptions": [
        "Users have email addresses",
        "Database is available"
    ],
    "acceptance_criteria": [
        {
            "requirement_id": "REQ-001",
            "criteria": "User can register with email and password"
        }
    ]
}
```

### Response Validation

All responses are validated for:

- **Schema Compliance**: Ensure response matches expected schema
- **Data Types**: Validate all data types and formats
- **Required Fields**: Ensure all required fields are present
- **Content Validation**: Validate content quality and completeness
- **Error Handling**: Handle malformed or invalid responses

## 🛡️ Error Handling

### Model Error Types

1. **Validation Errors**: Data validation failures
2. **Type Errors**: Type mismatch errors
3. **Configuration Errors**: Configuration issues
4. **State Errors**: State management errors
5. **Response Errors**: Response parsing errors

### Error Handling Strategies

```python
# Validation error handling
try:
    validated_config = validate_config(config)
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise ConfigurationError(f"Invalid configuration: {e}")

# Type error handling
try:
    typed_state = WorkflowState(**state_data)
except TypeError as e:
    logger.error(f"State type error: {e}")
    raise StateError(f"Invalid state structure: {e}")
```

## 🧪 Testing

### Test Organization

```
tests/
├── unit/models/           # Unit tests for model components
├── integration/models/    # Integration tests for model interactions
└── system/models/         # System tests for complete model workflows
```

### Testing Standards

- **Model Testing**: Test all model structures and validation
- **Configuration Testing**: Test configuration loading and validation
- **State Testing**: Test state management and persistence
- **Response Testing**: Test response parsing and validation
- **Error Testing**: Test error handling and recovery

## 📊 Performance

### Optimization Strategies

1. **Lazy Loading**: Load configuration and state on demand
2. **Caching**: Cache frequently accessed data
3. **Validation Optimization**: Optimize validation performance
4. **Memory Management**: Efficient memory usage for large states
5. **Serialization**: Optimize serialization and deserialization

### Performance Metrics

- **Configuration Load Time**: Time to load and validate configuration
- **State Validation Time**: Time to validate state structure
- **Response Parse Time**: Time to parse and validate responses
- **Memory Usage**: Memory consumption for state management
- **Error Recovery Time**: Time to recover from errors

## 📚 Related Documentation

- **Agents**: See `agents/` directory for agent implementations
- **Workflow**: See `workflow/` directory for workflow management
- **Testing**: See `tests/` directory for comprehensive test suite
- **Configuration**: See `models/config.py` for configuration management
- **State Management**: See `models/state.py` for state management

## 🤝 Contributing

### Adding New Models

1. **Follow Patterns**: Adhere to established model patterns
2. **Type Safety**: Use TypedDict for type safety
3. **Validation**: Implement comprehensive validation
4. **Documentation**: Document model structure and usage
5. **Testing**: Add comprehensive test coverage

### Model Standards

- **Type Safety**: All models should be type-safe
- **Validation**: Comprehensive validation for all models
- **Documentation**: Complete documentation for all models
- **Testing**: Full test coverage for all models
- **Performance**: Optimize for performance and efficiency

---

**Last Updated**: Current session  
**Version**: 1.0  
**Maintainer**: Development Team
