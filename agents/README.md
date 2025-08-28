# AI Agents

This directory contains the core AI agent implementations for the AI Development Agent system. Each agent is specialized for a specific development task and follows a consistent architecture pattern.

## 🏗️ Agent Architecture

All agents inherit from `base_agent.py` and implement:
- **Specialized Role**: Each agent has a specific development responsibility
- **LangChain Integration**: Built on LangChain framework for LLM interactions
- **Database Prompts**: All prompts stored in SQLite database (no hardcoded prompts)
- **Structured Outputs**: JSON-based output parsing with validation
- **Error Handling**: Comprehensive error handling with proper exception management
- **State Management**: TypedDict-based state with proper validation

## 🤖 Core Agents

### Development Agents
- **`requirements_analyst.py`** - Transforms project descriptions into detailed specifications
- **`architecture_designer.py`** - Designs system architecture and technology stack
- **`code_generator.py`** - Generates source code based on requirements and architecture
- **`test_generator.py`** - Creates comprehensive test suites
- **`code_reviewer.py`** - Analyzes code quality and suggests improvements
- **`security_analyst.py`** - Identifies and addresses security vulnerabilities
- **`documentation_generator.py`** - Creates comprehensive project documentation

### Management Agents
- **`project_manager.py`** - Orchestrates the overall development workflow

### Supervisor System
- **`supervisor/base_supervisor.py`** - Base class for all supervisor agents
- **`supervisor/project_manager_supervisor.py`** - High-level project management and coordination

## 🔧 Configuration & Standards

### Model Selection
- **Simple Tasks**: `gemini-2.5-flash-lite` for basic operations
- **Complex Tasks**: `gemini-2.5-flash` for sophisticated analysis

### Prompt Management
- All prompts stored in `prompt_templates.db`
- Dynamic loading from database at runtime
- Web-based prompt editor available

### Error Handling
- Zero silent errors - all errors exposed immediately
- No fallback mechanisms or mock data
- Comprehensive logging with context

## 📊 Current Status

All agents achieve **100% success rate** with recent optimizations and fixes.

## 📚 Related Documentation

For comprehensive agent documentation, see:

- **[Agent System Implementation](../docs/concepts/agent_system_implementation_concept.md)** - Core concepts and architecture
- **[Agent Development Guide](../docs/guides/langgraph/agent_development_guide.md)** - Development patterns and best practices
- **[Framework Analysis](../docs/analysis/agent_analysis/framework_analysis.md)** - Technical analysis and design decisions
- **[Agent Testing](../docs/testing/)** - Testing strategies and standards
- **[Architecture Documentation](../docs/architecture/)** - System architecture and design
- **[Structured Outputs Guide](../docs/guides/architecture/structured_outputs.md)** - Output formatting and validation

## 🧪 Testing

For testing information:
- **Unit Tests**: See `tests/unit/` 
- **Integration Tests**: See `tests/integration/`
- **Testing Standards**: See [docs/testing/](../docs/testing/README.md)

## 🤝 Contributing

### Adding New Agents
1. Inherit from `BaseAgent` in `base_agent.py`
2. Implement required methods: `execute()` and output parsing
3. Store all prompts in the database
4. Add comprehensive test suite
5. Follow project documentation standards

### Agent Standards
- **Single Responsibility**: Each agent has one clear purpose
- **Consistent Interface**: Follow established patterns
- **No Silent Errors**: All errors must be exposed
- **Performance**: Optimize for speed and efficiency
- **Documentation**: Maintain complete documentation

---

**📖 For complete agent documentation and development guides, see [docs/](../docs/README.md)**