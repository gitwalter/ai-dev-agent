# Data Models

This directory contains all data models, schemas, and configuration management for the AI Development Agent system, providing type safety, validation, and structured data handling.

## 🏗️ Core Models

### **Configuration Management** (`config.py`)
- Environment-based configuration loading
- API key management and validation
- Model selection configuration
- Workflow configuration options

### **State Management** (`state.py`)
- TypedDict-based workflow state structure
- State validation and type checking
- State persistence and recovery
- Metadata tracking

### **Supervisor State** (`supervisor_state.py`)
- Supervisor workflow state management
- Agent coordination state
- Quality gate state tracking
- Progress monitoring

### **Response Models** (`responses.py`)
- Agent-specific response schemas
- Response validation and parsing
- Error response handling
- Type-safe response handling

### **Simplified Responses** (`simplified_responses.py`)
- Streamlined response schemas for basic operations
- Performance-optimized parsing
- Minimal response overhead

## 🔧 Key Features

### Configuration Management
```python
# Streamlit secrets (recommended)
config = load_config_from_streamlit_secrets()

# Environment variables
config = load_config_from_env()
```

### State Structure
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

### Response Validation
- **Schema Compliance**: Responses match expected schemas
- **Data Types**: Type validation and format checking
- **Required Fields**: Ensure completeness
- **Content Validation**: Quality and completeness validation
- **Error Handling**: Comprehensive error management

## 🛡️ Error Handling

Following the project's **No Silent Errors** rule:
- All validation errors are exposed immediately
- No fallback mechanisms or mock data
- Comprehensive error logging with context
- Proper exception types for different error categories

## 📚 Related Documentation

For comprehensive model documentation, see:

- **[Structured Outputs Guide](../docs/guides/architecture/structured_outputs.md)** - Detailed output model specifications
- **[System Architecture](../docs/architecture/)** - System design and data flow
- **[Configuration Management](../docs/guides/development/)** - Configuration standards and practices
- **[Development Standards](../docs/guides/development/OPTIMIZED_RULES.md)** - Development guidelines
- **[Testing Documentation](../docs/testing/)** - Model testing strategies

## 🧪 Testing

- **Unit Tests**: See `tests/unit/` for model validation tests
- **Integration Tests**: See `tests/integration/` for model interaction tests
- **Testing Standards**: See [docs/testing/](../docs/testing/README.md)

## 🤝 Contributing

### Adding New Models
1. Follow established TypedDict patterns
2. Implement comprehensive validation
3. Use proper type hints and annotations
4. Add comprehensive test coverage
5. Follow project documentation standards

### Model Standards
- **Type Safety**: All models must be type-safe with TypedDict
- **Validation**: Comprehensive validation for all data
- **No Silent Errors**: All errors must be exposed
- **Documentation**: Complete documentation for all models
- **Testing**: Full test coverage for all models

---

**📖 For complete model documentation and implementation guides, see [docs/](../docs/README.md)**