# Prompt Management System

This directory contains the prompt management system for the AI Development Agent. The system provides database-driven prompt storage, versioning, and management capabilities.

## 🎯 Prompt System Overview

The prompt management system is designed to provide centralized, database-driven prompt management with the following features:

- **Database Storage**: All prompts stored in SQLite database
- **Version Control**: Track prompt versions and changes
- **Performance Tracking**: Monitor prompt effectiveness
- **Dynamic Loading**: Load prompts at runtime
- **Web Editor**: Edit prompts through Streamlit interface

## 🏗️ System Architecture

### Core Components

#### 1. **Prompt Database** (`prompt_templates.db`)
- **Purpose**: SQLite database storing all system prompts
- **Features**:
  - Agent-specific prompt storage
  - System prompt storage
  - Version tracking and history
  - Performance metrics storage
  - Prompt metadata management

#### 2. **Prompt Loader** (`agent_prompt_loader.py`)
- **Purpose**: Load and manage prompts from database
- **Features**:
  - Dynamic prompt loading
  - Version selection
  - Fallback mechanisms
  - Performance optimization
  - Error handling

### Database Schema

```sql
-- Agent prompts table
CREATE TABLE agent_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type TEXT NOT NULL,
    prompt_type TEXT NOT NULL,
    content TEXT NOT NULL,
    version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performance_score REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0
);

-- System prompts table
CREATE TABLE system_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    prompt_type TEXT NOT NULL,
    content TEXT NOT NULL,
    version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performance_score REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0
);
```

## 🤖 Agent Prompts

### Supported Agent Types

1. **Requirements Analyst** (`requirements_analyst`)
   - Main prompt for requirements analysis
   - Validation prompt for requirements verification
   - Enhancement prompt for requirements improvement

2. **Architecture Designer** (`architecture_designer`)
   - Main prompt for architecture design
   - Technology selection prompt
   - Scalability analysis prompt

3. **Code Generator** (`code_generator`)
   - Main prompt for code generation
   - File structure prompt
   - Code quality prompt

4. **Test Generator** (`test_generator`)
   - Main prompt for test generation
   - Unit test prompt
   - Integration test prompt

5. **Code Reviewer** (`code_reviewer`)
   - Main prompt for code review
   - Quality assessment prompt
   - Improvement suggestion prompt

6. **Security Analyst** (`security_analyst`)
   - Main prompt for security analysis
   - Vulnerability detection prompt
   - Security recommendation prompt

7. **Documentation Generator** (`documentation_generator`)
   - Main prompt for documentation generation
   - README generation prompt
   - API documentation prompt

### Prompt Types

Each agent supports multiple prompt types:

- **Main**: Primary prompt for agent execution
- **Validation**: Prompt for output validation
- **Enhancement**: Prompt for output improvement
- **Error Recovery**: Prompt for error handling
- **Specialized**: Agent-specific specialized prompts

## ⚙️ System Prompts

### Prompt Categories

1. **Workflow Prompts**
   - Workflow initialization
   - State management
   - Error handling
   - Progress tracking

2. **General Prompts**
   - System configuration
   - User interaction
   - Logging and monitoring
   - Performance optimization

3. **Error Handling Prompts**
   - Error detection
   - Error recovery
   - Fallback strategies
   - Error reporting

## 🔧 Prompt Management

### Database Operations

```python
# Example: Load agent prompt
from prompts.agent_prompt_loader import AgentPromptLoader

loader = AgentPromptLoader()
prompt = loader.get_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    version="latest"
)
```

### Prompt Versioning

The system supports prompt versioning with the following features:

- **Version Tracking**: Track all prompt versions
- **Rollback Capability**: Rollback to previous versions
- **Performance Comparison**: Compare version performance
- **A/B Testing**: Test different prompt versions

### Performance Tracking

Each prompt tracks performance metrics:

- **Success Rate**: Percentage of successful executions
- **Response Quality**: Quality score based on validation
- **Execution Time**: Average execution time
- **Usage Count**: Number of times used

## 🛠️ Web Interface

### Prompt Manager App

The system includes a dedicated Streamlit app for prompt management:

```bash
# Run prompt manager
streamlit run apps/prompt_manager_app.py
```

#### Features

1. **Prompt Editing**
   - Rich text editor for prompt content
   - Syntax highlighting for prompt templates
   - Real-time preview of prompt formatting

2. **Version Management**
   - View prompt version history
   - Compare different versions
   - Rollback to previous versions

3. **Performance Monitoring**
   - View performance metrics
   - Track usage statistics
   - Monitor success rates

4. **Bulk Operations**
   - Bulk prompt updates
   - Batch version management
   - Mass performance analysis

## 📊 Prompt Optimization

### Performance Analysis

The system provides comprehensive performance analysis:

```python
# Example: Analyze prompt performance
from prompts.agent_prompt_loader import AgentPromptLoader

loader = AgentPromptLoader()
performance = loader.analyze_performance(
    agent_type="requirements_analyst",
    prompt_type="main"
)

print(f"Success Rate: {performance['success_rate']}%")
print(f"Average Quality: {performance['avg_quality']}")
print(f"Average Time: {performance['avg_time']}s")
```

### Optimization Strategies

1. **A/B Testing**: Test different prompt versions
2. **Performance Monitoring**: Track prompt effectiveness
3. **User Feedback**: Incorporate user feedback
4. **Continuous Improvement**: Iteratively improve prompts

## 🔒 Security and Validation

### Prompt Validation

All prompts are validated for:

- **Content Safety**: Ensure prompts are safe and appropriate
- **Format Validation**: Validate prompt structure and format
- **Template Validation**: Validate prompt templates
- **Performance Validation**: Validate prompt performance

### Access Control

- **Read Access**: All components can read prompts
- **Write Access**: Only authorized users can modify prompts
- **Version Control**: Track all prompt changes
- **Audit Trail**: Maintain change history

## 🧪 Testing

### Prompt Testing

```python
# Example: Test prompt effectiveness
def test_prompt_effectiveness():
    """Test prompt effectiveness with sample inputs."""
    loader = AgentPromptLoader()
    prompt = loader.get_prompt("requirements_analyst", "main")
    
    # Test with sample input
    test_input = "Create a REST API for user management"
    result = test_prompt_with_input(prompt, test_input)
    
    # Validate result
    assert len(result["functional_requirements"]) >= 10
    assert "authentication" in str(result).lower()
```

### Test Categories

1. **Functionality Tests**: Test prompt functionality
2. **Performance Tests**: Test prompt performance
3. **Quality Tests**: Test output quality
4. **Edge Case Tests**: Test edge cases and error scenarios

## 📚 Usage Examples

### Loading Prompts

```python
from prompts.agent_prompt_loader import AgentPromptLoader

# Initialize loader
loader = AgentPromptLoader()

# Load main prompt for requirements analyst
main_prompt = loader.get_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    version="latest"
)

# Load validation prompt
validation_prompt = loader.get_prompt(
    agent_type="requirements_analyst",
    prompt_type="validation",
    version="latest"
)
```

### Updating Prompts

```python
# Update prompt content
loader.update_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    content=new_prompt_content,
    version="2.0"
)

# Rollback to previous version
loader.rollback_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    version="1.0"
)
```

### Performance Analysis

```python
# Analyze prompt performance
performance = loader.analyze_performance(
    agent_type="requirements_analyst",
    prompt_type="main"
)

# Compare versions
comparison = loader.compare_versions(
    agent_type="requirements_analyst",
    prompt_type="main",
    version1="1.0",
    version2="2.0"
)
```

## 🔄 Maintenance

### Regular Maintenance Tasks

1. **Performance Review**: Regularly review prompt performance
2. **Version Cleanup**: Clean up old prompt versions
3. **Database Optimization**: Optimize database performance
4. **Backup Management**: Regular database backups

### Monitoring

- **Performance Metrics**: Monitor prompt performance
- **Usage Statistics**: Track prompt usage patterns
- **Error Rates**: Monitor prompt error rates
- **User Feedback**: Collect and analyze user feedback

## 📚 Related Documentation

- **Agent System**: See `agents/README.md` for agent implementations
- **Web Interface**: See `apps/prompt_manager_app.py` for web interface
- **Utilities**: See `utils/prompt_manager.py` for utility functions
- **Testing**: See `tests/unit/prompts/` for prompt testing

## 🤝 Contributing

### Adding New Prompts

1. **Follow Naming**: Use consistent naming conventions
2. **Version Control**: Always version new prompts
3. **Test Thoroughly**: Test prompts before deployment
4. **Document Changes**: Document prompt changes and rationale
5. **Monitor Performance**: Monitor prompt performance after deployment

### Prompt Standards

- **Clarity**: Prompts should be clear and unambiguous
- **Completeness**: Prompts should be complete and comprehensive
- **Consistency**: Prompts should follow consistent patterns
- **Performance**: Prompts should be optimized for performance
- **Maintainability**: Prompts should be easy to maintain and update

---

**Last Updated**: Current session  
**Version**: 1.0  
**Maintainer**: Development Team
