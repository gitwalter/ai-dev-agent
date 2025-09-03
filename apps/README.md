# Applications

This directory contains the application entry points for the AI Development Agent system, providing multiple interfaces for interacting with the system.

## 🚀 Applications Overview

### Core Applications

#### **Main Application** (`main.py`)
- **Purpose**: Programmatic entry point for the AI Development Agent
- **Target Users**: Developers, integrators, automation scripts
- **Features**: Direct API access, workflow execution, configuration management

#### **Streamlit Web App** (`streamlit_app.py`)
- **Purpose**: User-friendly web interface for the AI Development Agent
- **Target Users**: End users, developers, project managers
- **Features**: Interactive web interface, project generation, progress tracking, Vibe Coding

#### **Universal Composition App** (`universal_composition_app.py`) 🆕
- **Purpose**: Professional AI Agent Builder & Enterprise System Composer
- **Target Users**: Enterprise developers, system architects, AI engineers
- **Features**: Multi-platform AI framework integration, enterprise module composition, universal compatibility

#### **Vibe Coding App (Original)** (`vibe_coding_app.py`)
- **Purpose**: Preserved original vibe coding implementation
- **Target Users**: Developers interested in vibe-driven development
- **Features**: Reference implementation for emotional coding approaches

#### **Prompt Manager App** (`prompt_manager_app.py`)
- **Purpose**: Dedicated interface for managing system prompts
- **Target Users**: System administrators, prompt engineers
- **Features**: Prompt editing, version control, performance tracking

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

## 📚 Related Documentation

For comprehensive application documentation, see:

- **[Implementation Guides](../docs/guides/implementation/)** - Application implementation patterns
- **[Development Standards](../docs/guides/development/)** - Development guidelines and best practices
- **[Database Automation](../docs/guides/database/)** - Database management and automation
- **[System Architecture](../docs/architecture/)** - System design and architecture
- **[Security Guidelines](../docs/testing/security_testing.md)** - Security standards and testing

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