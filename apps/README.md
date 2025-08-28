# Applications

This directory contains the application entry points for the AI Development Agent system. Each application provides a different interface for interacting with the system.

## 🚀 Application Overview

The AI Development Agent provides multiple ways to interact with the system:

### Core Applications

#### 1. **Main Application** (`main.py`)
- **Purpose**: Programmatic entry point for the AI Development Agent
- **Target Users**: Developers, integrators, automation scripts
- **Features**:
  - Direct API access to all system functionality
  - Programmatic workflow execution
  - Configuration management
  - Error handling and logging
  - Integration capabilities

#### 2. **Streamlit Web App** (`streamlit_app.py`)
- **Purpose**: User-friendly web interface for the AI Development Agent
- **Target Users**: End users, developers, project managers
- **Features**:
  - Interactive web interface
  - Project generation workflow
  - Real-time progress tracking
  - File download and management
  - Configuration management
  - Prompt management interface
  - RAG document management

#### 3. **Prompt Manager App** (`prompt_manager_app.py`)
- **Purpose**: Dedicated interface for managing system prompts
- **Target Users**: System administrators, prompt engineers
- **Features**:
  - Agent prompt editing and management
  - System prompt configuration
  - Prompt version control
  - Performance tracking
  - Prompt testing and validation

## 🏗️ Application Architecture

### Main Application (`main.py`)

The main application provides a programmatic interface to the AI Development Agent system:

```python
# Example usage
from apps.main import AIDevelopmentAgent
from models.config import load_config_from_env

async def main():
    # Initialize the agent
    config = load_config_from_env()
    agent = AIDevelopmentAgent(config)
    
    # Execute workflow
    result = await agent.execute_workflow(
        project_context="Create a REST API for user management...",
        project_name="user-management-api",
        output_dir="./generated_projects/user-management-api"
    )
    
    print(f"Workflow completed: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Key Features

- **Configuration Management**: Load and validate configuration
- **Workflow Execution**: Execute complete development workflows
- **Error Handling**: Comprehensive error handling and recovery
- **Logging**: Detailed logging and monitoring
- **Integration**: Easy integration with other systems

### Streamlit Web App (`streamlit_app.py`)

The Streamlit web app provides a user-friendly interface with four main sections:

#### 1. **🚀 Main App**
- **Project Generation**: Complete project generation workflow
- **Real-time Progress**: Live progress tracking and status updates
- **File Management**: Download generated projects and files
- **Configuration**: Project settings and configuration
- **Results Display**: View generated code, tests, and documentation

#### 2. **🔧 Prompt Manager**
- **Agent Prompts**: Edit and manage agent-specific prompts
- **System Prompts**: Configure system-wide prompts
- **Prompt Testing**: Test prompts with sample inputs
- **Version Control**: Track prompt changes and performance
- **Performance Metrics**: Monitor prompt effectiveness

#### 3. **📚 RAG Documents**
- **URL Processing**: Add and process web documents
- **File Upload**: Upload and process local documents
- **Document Management**: Organize and tag documents
- **Agent Association**: Link documents to specific agents
- **Content Preview**: Preview processed document content

#### 4. **⚙️ System Prompts**
- **Category Management**: Organize prompts by category
- **Template Creation**: Create and edit prompt templates
- **Performance Tracking**: Monitor prompt usage and success rates
- **Configuration**: System-wide prompt configuration

#### Key Features

- **User-Friendly Interface**: Intuitive web-based interface
- **Real-time Updates**: Live progress tracking and status updates
- **File Management**: Download and manage generated files
- **Configuration**: Easy project and system configuration
- **Monitoring**: Real-time monitoring and observability

### Prompt Manager App (`prompt_manager_app.py`)

The dedicated prompt manager provides advanced prompt management capabilities:

#### Key Features

- **Advanced Editing**: Rich text editing for prompts
- **Version Control**: Track prompt changes and versions
- **Performance Analytics**: Monitor prompt effectiveness
- **Testing Framework**: Test prompts with various inputs
- **Bulk Operations**: Manage multiple prompts efficiently

## 🔧 Configuration

### Application Configuration

All applications use a shared configuration system:

```python
# Configuration structure
config = {
    "api_keys": {
        "gemini_api_key": "your-api-key"
    },
    "models": {
        "default_model": "gemini-2.5-flash-lite",
        "complex_model": "gemini-2.5-flash"
    },
    "workflow": {
        "enable_human_approval": True,
        "quality_gates_enabled": True,
        "parallel_execution": False
    },
    "logging": {
        "level": "INFO",
        "format": "detailed"
    }
}
```

### Environment Configuration

Applications can be configured through environment variables:

```bash
# Required environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export LANGSMITH_API_KEY="your-langsmith-api-key"
export LANGSMITH_PROJECT="ai-dev-agent"

# Optional configuration
export LOG_LEVEL="INFO"
export ENABLE_MONITORING="true"
export WORKFLOW_TIMEOUT="300"
```

## 🚀 Getting Started

### Running the Streamlit Web App

```bash
# Install dependencies
pip install -r requirements.txt

# Set up configuration
# Create .streamlit/secrets.toml with your API keys

# Run the web app
streamlit run apps/streamlit_app.py
```

### Running the Main Application

```bash
# Set up environment variables
export GEMINI_API_KEY="your-api-key"

# Run the main application
python apps/main.py
```

### Running the Prompt Manager

```bash
# Run the prompt manager
streamlit run apps/prompt_manager_app.py
```

## 📊 Monitoring and Observability

### LangSmith Integration

All applications integrate with LangSmith for comprehensive observability:

- **Agent Executions**: Track individual agent performance
- **Workflow Steps**: Monitor workflow progression
- **User Interactions**: Track user actions and decisions
- **Performance Metrics**: Monitor application performance
- **Error Tracking**: Comprehensive error monitoring

### Application Metrics

- **User Engagement**: Track user interactions and usage patterns
- **Performance**: Monitor application response times
- **Error Rates**: Track application errors and failures
- **Feature Usage**: Monitor feature adoption and usage
- **User Satisfaction**: Track user feedback and satisfaction

## 🧪 Testing

### Test Organization

```
tests/
├── unit/apps/              # Unit tests for application components
├── integration/apps/       # Integration tests for application interactions
├── system/apps/           # System tests for complete applications
└── e2e/                   # End-to-end application tests
```

### Testing Standards

- **Application Testing**: Test complete application workflows
- **UI Testing**: Test user interface functionality
- **Integration Testing**: Test application integration with agents
- **Performance Testing**: Test application performance
- **User Experience Testing**: Test user experience and usability

## 🔒 Security

### Security Features

- **API Key Management**: Secure API key handling through Streamlit secrets
- **Input Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Secure error handling without information leakage
- **Access Control**: Role-based access control for different features
- **Audit Logging**: Comprehensive audit logging for security events

### Security Best Practices

- **Never Hardcode Secrets**: All secrets managed through secure configuration
- **Input Sanitization**: All user inputs validated and sanitized
- **Error Handling**: Secure error handling without exposing sensitive information
- **Regular Updates**: Keep dependencies updated for security patches
- **Security Monitoring**: Monitor for security issues and vulnerabilities

## 📚 Related Documentation

- **Agents**: See `agents/` directory for agent implementations
- **Workflow**: See `workflow/` directory for workflow management
- **Models**: See `models/` directory for data models and configuration
- **Testing**: See `tests/` directory for comprehensive test suite
- **Configuration**: See `models/config.py` for configuration management

## 🤝 Contributing

### Adding New Applications

1. **Follow Architecture**: Adhere to established application patterns
2. **Implement Security**: Implement comprehensive security measures
3. **Add Testing**: Add comprehensive test coverage
4. **Update Documentation**: Document new applications and usage
5. **User Experience**: Focus on user experience and usability

### Application Standards

- **User-Friendly**: All applications should be user-friendly and intuitive
- **Secure**: Implement comprehensive security measures
- **Testable**: All applications should be fully testable
- **Documented**: Maintain complete documentation
- **Accessible**: Ensure applications are accessible to all users

---

**Last Updated**: Current session  
**Version**: 1.0  
**Maintainer**: Development Team
