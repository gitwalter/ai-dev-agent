# AI-Dev-Agent Applications

This directory contains the complete application suite for the AI Development Agent system, providing specialized interfaces for different user needs and development workflows.

## 🚀 **Application Suite Overview**

Our comprehensive application suite offers four specialized interfaces, each optimized for specific use cases and user types:

### **🔧 Universal Composition App** (`universal_composition_app.py`)
**Port 8502** | **Enterprise System Builder**

- **Purpose**: Professional AI Agent Builder & Enterprise System Composer
- **Target Users**: Enterprise developers, system architects, AI engineers
- **Key Features**: 
  - Multi-platform AI framework integration (LangChain, LangGraph, CrewAI, AutoGen, Semantic Kernel, n8n)
  - Enterprise module composition (Authentication, Database, API Gateway, Cache, etc.)
  - Visual agent builder interface with role-based design
  - Vibe-Agile fusion engine for emotional intelligence
  - Dynamic rule system monitoring and management
  - Complete project generation with deployment automation

### **🚀 Streamlit App** (`streamlit_app.py`) 
**Port 8501** | **Main Web Interface**

- **Purpose**: Primary user-friendly web interface for AI-powered development
- **Target Users**: Developers, project managers, end users, first-time users
- **Key Features**:
  - Interactive project generation with real-time feedback
  - Vibe coding integration for emotional development workflows
  - Progress tracking and comprehensive monitoring
  - Direct agent conversation interface
  - Configuration management and setup
  - RAG integration for enhanced AI responses

### **🤖 Prompt Manager App** (`prompt_manager_app.py`)
**Port 8504** | **Professional Prompt Management**

- **Purpose**: Advanced prompt management, optimization, and analytics system
- **Target Users**: System administrators, prompt engineers, AI specialists
- **Key Features**:
  - Professional prompt creation and editing with syntax highlighting
  - Template system with variable substitution and inheritance
  - AI-powered prompt optimization and improvement
  - Comprehensive performance analytics and tracking
  - RAG document management and processing
  - Version control, A/B testing, and collaboration tools

### **🌈 Vibe Coding App** (`vibe_coding_app.py`)
**Port 8503** | **Emotional Intelligence Interface**

- **Purpose**: Original vibe-driven development with emotional intelligence integration
- **Target Users**: Researchers, teams interested in innovative development approaches
- **Key Features**:
  - Emotional context integration and management
  - Team dynamics optimization and synchronization
  - Comprehensive mood tracking and analytics
  - Adaptive vibe systems and learning algorithms
  - Research platform for academic and industry studies
  - Original implementation preservation for reference

### **⚙️ Main Application** (`main.py`)
**Programmatic Interface**

- **Purpose**: Direct programmatic entry point for automation and integration
- **Target Users**: Developers, integrators, automation scripts, CI/CD systems
- **Key Features**: 
  - Direct API access without web interface overhead
  - Workflow execution and automation capabilities
  - Advanced configuration management
  - Integration with external systems and tools
  - Batch processing and bulk operations

## 🚀 Getting Started

### Running the Streamlit Web App
```bash
# Install dependencies
pip install -r requirements.txt

# Set up configuration in .streamlit/secrets.toml
GEMINI_API_KEY = "your-api-key"

# Run the main app (Port 8501)
streamlit run apps/streamlit_app.py

# Run the Universal Composition App (Port 8502)
streamlit run apps/universal_composition_app.py --server.port 8502

# Run the original Vibe Coding App (Port 8503)
streamlit run apps/vibe_coding_app.py --server.port 8503
```

### VS Code Launch Configurations
Use the preconfigured launch configurations in `.vscode/launch.json`:
- **🚀 Main Streamlit App** - Original app with vibe coding integration
- **🔧 Universal Composition App** - Professional enterprise system builder
- **🌈 Vibe Coding App (Original)** - Preserved original implementation
- **🤖 Prompt Manager App** - Prompt management interface

### Running the Main Application
```bash
# Set up environment variables
export GEMINI_API_KEY="your-api-key"

# Run the main application
python apps/main.py
```

## 🏗️ Architecture

All applications follow the project's architecture standards:
- **Streamlit Secrets**: Use `st.secrets` for API key management
- **Model Selection**: Standardized Gemini model selection
- **Error Handling**: Comprehensive error handling without silent failures
- **Structured Outputs**: JSON-based output parsing with validation

## 🔒 Security

- **API Key Management**: Secure handling through Streamlit secrets
- **Input Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Secure error handling without information leakage
- **Access Control**: Role-based access control for different features

## 📚 **Comprehensive Documentation**

### **📖 Complete User Guides**
- **[📱 Application Index](../docs/guides/applications/APPLICATION_INDEX.md)** - Complete application overview and selection guide
- **[🔧 Universal Composition App Guide](../docs/guides/applications/UNIVERSAL_COMPOSITION_APP_GUIDE.md)** - Enterprise system builder documentation
- **[🚀 Streamlit App Guide](../docs/guides/applications/STREAMLIT_APP_GUIDE.md)** - Main web interface documentation
- **[🤖 Prompt Manager App Guide](../docs/guides/applications/PROMPT_MANAGER_APP_GUIDE.md)** - Professional prompt management documentation
- **[🌈 Vibe Coding App Guide](../docs/guides/applications/VIBE_CODING_APP_GUIDE.md)** - Emotional intelligence interface documentation

### **🏗️ Technical Documentation**
- **[System Architecture](../docs/architecture/)** - Complete system design and architecture
- **[Implementation Guides](../docs/guides/implementation/)** - Application implementation patterns and best practices
- **[Development Standards](../docs/guides/development/)** - Development guidelines and coding standards
- **[Security Guidelines](../docs/testing/security_testing.md)** - Security standards and testing procedures

### **🔧 Integration Documentation**
- **[Cursor IDE Integration](../docs/technical/cursor-integration-architecture.md)** - IDE automation and rule system
- **[Database Automation](../docs/guides/database/)** - Database management and automation
- **[API Reference](../docs/reference/)** - Complete API documentation and integration guides

## 🧪 Testing

For application testing:
- **Unit Tests**: See `tests/unit/`
- **Integration Tests**: See `tests/integration/`
- **System Tests**: See `tests/system/`
- **Testing Standards**: See [docs/testing/](../docs/testing/README.md)

## 🤝 Contributing

### Adding New Applications
1. Follow established application patterns
2. Implement comprehensive security measures
3. Use Streamlit secrets for configuration
4. Add comprehensive test coverage
5. Follow project documentation standards

### Application Standards
- **User-Friendly**: Intuitive interfaces and workflows
- **Secure**: Comprehensive security implementation
- **Testable**: Full test coverage with quality gates
- **Documented**: Complete documentation and examples
- **Accessible**: Ensure accessibility for all users

---

**📖 For complete application documentation and development guides, see [docs/](../docs/README.md)**