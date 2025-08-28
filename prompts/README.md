# Prompt Management System

This directory contains the prompt management system for the AI Development Agent, providing database-driven prompt storage, versioning, and management capabilities.

## 🎯 System Overview

The prompt management system provides:
- **Database Storage**: All prompts stored in SQLite database (`prompt_templates.db`)
- **Version Control**: Track prompt versions and changes  
- **Performance Tracking**: Monitor prompt effectiveness
- **Dynamic Loading**: Load prompts at runtime
- **Web Editor**: Edit prompts through Streamlit interface

## 🏗️ Core Components

### **Prompt Database** (`prompt_templates.db`)
SQLite database storing all system prompts with:
- Agent-specific prompt storage
- System prompt storage
- Version tracking and history
- Performance metrics storage

### **Prompt Loader** (`agent_prompt_loader.py`)
Load and manage prompts from database with:
- Dynamic prompt loading
- Version selection
- Error handling with proper exceptions (no fallbacks)
- Performance optimization

## 🤖 Agent Prompts

### Supported Agent Types
- **requirements_analyst** - Requirements analysis prompts
- **architecture_designer** - Architecture design prompts
- **code_generator** - Code generation prompts
- **test_generator** - Test generation prompts
- **code_reviewer** - Code review prompts
- **security_analyst** - Security analysis prompts
- **documentation_generator** - Documentation generation prompts

### Prompt Types
- **main** - Primary prompt for agent execution
- **validation** - Output validation prompts
- **enhancement** - Output improvement prompts
- **specialized** - Agent-specific specialized prompts

## 🔧 Usage Examples

### Loading Prompts
```python
from prompts.agent_prompt_loader import AgentPromptLoader

loader = AgentPromptLoader()

# Load main prompt for requirements analyst
main_prompt = loader.get_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
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
```

## 🛠️ Web Interface

Access the prompt management interface:
```bash
streamlit run apps/prompt_manager_app.py
```

Features:
- Rich text editor for prompt content
- Version management and comparison
- Performance monitoring
- Bulk operations

## 🔒 Error Handling

Following the project's **No Silent Errors** rule:
- All prompt loading errors are exposed immediately
- No fallback mechanisms or default prompts
- Comprehensive error logging with context
- Proper exception handling for database issues

## 📚 Related Documentation

For comprehensive prompt management documentation, see:

- **[Prompt Engineering Concept](../docs/concepts/prompt_engineering_concept.md)** - Core concepts and strategies
- **[Agent Development Guide](../docs/guides/langgraph/agent_development_guide.md)** - Agent prompt patterns
- **[Database Automation](../docs/guides/database/)** - Database management and automation
- **[System Architecture](../docs/architecture/)** - System design and prompt flow
- **[Testing Documentation](../docs/testing/)** - Prompt testing strategies

## 🧪 Testing

- **Unit Tests**: See `tests/unit/` for prompt loading tests
- **Integration Tests**: See `tests/integration/` for prompt system tests
- **Testing Standards**: See [docs/testing/](../docs/testing/README.md)

## 🤝 Contributing

### Adding New Prompts
1. Follow consistent naming conventions
2. Always version new prompts
3. Test prompts thoroughly before deployment
4. Document prompt changes and rationale
5. Monitor performance after deployment

### Prompt Standards
- **Clarity**: Prompts must be clear and unambiguous
- **Completeness**: Comprehensive and complete prompts
- **Consistency**: Follow established patterns
- **Performance**: Optimize for effectiveness
- **Maintainability**: Easy to maintain and update

### Database Management
- **No Direct Hardcoded Prompts**: All prompts must be in database
- **Version Control**: All changes must be versioned
- **Error Handling**: No silent failures or fallback prompts
- **Performance Tracking**: Monitor and optimize prompt performance

---

**📖 For complete prompt management documentation and engineering guides, see [docs/](../docs/README.md)**