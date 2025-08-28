# Utilities

This directory contains utility functions, helpers, and tools that support the AI Development Agent system. These utilities provide common functionality used across multiple components of the system.

## 🛠️ Utility Overview

The utilities directory provides a comprehensive set of tools for:

### Core Utilities

#### 1. **Output Parsing** (`output_parsers.py`, `enhanced_output_parsers.py`)
- **Purpose**: Parse and validate AI-generated responses
- **Features**:
  - JSON-based response parsing
  - Multiple parsing strategies
  - Fallback mechanisms
  - Error handling and recovery
  - Response validation

#### 2. **Structured Outputs** (`structured_outputs.py`)
- **Purpose**: Generate and manage structured outputs
- **Features**:
  - Structured output generation
  - Output validation and formatting
  - Type-safe output handling
  - Error recovery mechanisms
  - Performance optimization

#### 3. **File Management** (`file_manager.py`)
- **Purpose**: File system operations and management
- **Features**:
  - File creation and manipulation
  - Directory management
  - File validation and verification
  - Backup and recovery
  - File organization

#### 4. **Prompt Management** (`prompt_manager.py`, `prompt_editor.py`)
- **Purpose**: Manage and edit system prompts
- **Features**:
  - Database-driven prompt storage
  - Prompt editing and versioning
  - Performance tracking
  - Prompt validation
  - Bulk operations

#### 5. **RAG Processing** (`rag_processor.py`)
- **Purpose**: Retrieval-Augmented Generation document processing
- **Features**:
  - Web scraping and content extraction
  - Document processing and cleaning
  - Content chunking and indexing
  - Metadata extraction
  - Agent association

### Advanced Utilities

#### 6. **Memory Management** (`memory_manager.py`, `memory_enhanced_agents.py`)
- **Purpose**: Memory and context management for agents
- **Features**:
  - Context memory management
  - Memory persistence and retrieval
  - Memory optimization
  - Context-aware processing
  - Memory cleanup

#### 7. **Collaboration Context** (`collaboration_context.py`)
- **Purpose**: Multi-agent collaboration and context sharing
- **Features**:
  - Inter-agent communication
  - Context sharing and synchronization
  - Collaboration state management
  - Conflict resolution
  - Performance optimization

#### 8. **Handoff Management** (`handoff_manager.py`)
- **Purpose**: Agent handoff and transition management
- **Features**:
  - Seamless agent transitions
  - State preservation during handoffs
  - Handoff validation and verification
  - Error handling during transitions
  - Performance monitoring

#### 9. **LangChain Integration** (`langchain_logging.py`, `langchain_data_exchange.py`)
- **Purpose**: LangChain framework integration and utilities
- **Features**:
  - LangChain logging and monitoring
  - Data exchange and transformation
  - Framework-specific optimizations
  - Integration utilities
  - Performance enhancements

### Configuration and Setup

#### 10. **Configuration Management** (`toml_config.py`)
- **Purpose**: TOML-based configuration management
- **Features**:
  - TOML file parsing and validation
  - Configuration loading and caching
  - Environment variable integration
  - Configuration validation
  - Error handling

#### 11. **Logging Configuration** (`logging_config.py`)
- **Purpose**: Centralized logging configuration
- **Features**:
  - Structured logging setup
  - Log level management
  - Log formatting and output
  - Performance logging
  - Error logging

#### 12. **Database Automation** (`database_cleaner.py`, `github_database_automation.py`)
- **Purpose**: Database maintenance and automation
- **Features**:
  - Database cleanup and optimization
  - GitHub integration for database management
  - Automated maintenance tasks
  - Performance monitoring
  - Error recovery

## 🔧 Core Functionality

### Output Parsing System

The output parsing system provides robust parsing of AI-generated responses:

```python
# Example: Enhanced output parsing
from utils.enhanced_output_parsers import EnhancedOutputParser

parser = EnhancedOutputParser()
result = parser.parse_response(
    response=ai_response,
    expected_schema=requirements_schema,
    fallback_strategies=["json", "markdown", "text"]
)
```

#### Parsing Strategies

1. **JSON Parsing**: Primary parsing strategy for structured responses
2. **Markdown Parsing**: Fallback for markdown-formatted responses
3. **Text Parsing**: Final fallback for unstructured text
4. **Regex Parsing**: Pattern-based extraction for specific formats
5. **AI-Assisted Parsing**: Use AI to parse malformed responses

### File Management System

The file management system provides comprehensive file operations:

```python
# Example: File management
from utils.file_manager import FileManager

file_manager = FileManager()
file_manager.create_project_structure(
    project_name="user-management-api",
    structure=project_structure,
    base_path="./generated_projects"
)
```

#### File Operations

- **Project Creation**: Create complete project structures
- **File Generation**: Generate files with proper formatting
- **Directory Management**: Organize and manage directories
- **File Validation**: Validate file contents and structure
- **Backup Management**: Create and manage backups

### Prompt Management System

The prompt management system provides database-driven prompt management:

```python
# Example: Prompt management
from utils.prompt_manager import PromptManager

prompt_manager = PromptManager()
prompt = prompt_manager.get_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    version="latest"
)
```

#### Prompt Features

- **Database Storage**: All prompts stored in SQLite database
- **Version Control**: Track prompt versions and changes
- **Performance Tracking**: Monitor prompt effectiveness
- **Dynamic Loading**: Load prompts at runtime
- **Web Editor**: Edit prompts through Streamlit interface

## 📊 Performance Optimization

### Caching Strategies

1. **Response Caching**: Cache AI responses for repeated queries
2. **Prompt Caching**: Cache frequently used prompts
3. **File Caching**: Cache file operations and validations
4. **Configuration Caching**: Cache configuration data
5. **Memory Caching**: Cache context and memory data

### Optimization Techniques

1. **Lazy Loading**: Load resources on demand
2. **Batch Processing**: Process multiple items efficiently
3. **Parallel Processing**: Use concurrent operations where possible
4. **Memory Management**: Optimize memory usage and cleanup
5. **Connection Pooling**: Reuse database and API connections

## 🛡️ Error Handling

### Error Categories

1. **Parsing Errors**: Output parsing and validation failures
2. **File Errors**: File system operation failures
3. **Database Errors**: Database operation failures
4. **Network Errors**: API and network communication failures
5. **Configuration Errors**: Configuration and setup failures

### Error Recovery Strategies

```python
# Example: Error recovery
try:
    result = parser.parse_response(response)
except ParsingError as e:
    # Try fallback strategies
    result = parser.parse_with_fallbacks(response)
except FileError as e:
    # Retry file operation
    result = file_manager.retry_operation(operation)
except DatabaseError as e:
    # Reconnect and retry
    result = database_manager.reconnect_and_retry(operation)
```

## 🧪 Testing

### Test Organization

```
tests/
├── unit/utils/             # Unit tests for utility functions
├── integration/utils/      # Integration tests for utility interactions
└── system/utils/          # System tests for complete utility workflows
```

### Testing Standards

- **Function Testing**: Test individual utility functions
- **Integration Testing**: Test utility interactions
- **Error Testing**: Test error handling and recovery
- **Performance Testing**: Test utility performance
- **Edge Case Testing**: Test boundary conditions and edge cases

## 📚 Usage Examples

### Output Parsing

```python
from utils.enhanced_output_parsers import EnhancedOutputParser

# Initialize parser
parser = EnhancedOutputParser()

# Parse AI response
try:
    parsed_result = parser.parse_response(
        response=ai_response,
        expected_schema=requirements_schema,
        agent_type="requirements_analyst"
    )
    print(f"Parsed successfully: {parsed_result}")
except ParsingError as e:
    print(f"Parsing failed: {e}")
    # Handle parsing failure
```

### File Management

```python
from utils.file_manager import FileManager

# Initialize file manager
file_manager = FileManager()

# Create project structure
project_structure = {
    "src": {
        "main.py": "# Main application file",
        "config.py": "# Configuration file"
    },
    "tests": {
        "test_main.py": "# Test file"
    },
    "README.md": "# Project documentation"
}

file_manager.create_project_structure(
    project_name="my-project",
    structure=project_structure,
    base_path="./generated_projects"
)
```

### Prompt Management

```python
from utils.prompt_manager import PromptManager

# Initialize prompt manager
prompt_manager = PromptManager()

# Get prompt for agent
prompt = prompt_manager.get_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    version="latest"
)

# Update prompt
prompt_manager.update_prompt(
    agent_type="requirements_analyst",
    prompt_type="main",
    content=new_prompt_content,
    version="2.0"
)
```

### RAG Processing

```python
from utils.rag_processor import RAGProcessor

# Initialize RAG processor
rag_processor = RAGProcessor()

# Process URL document
document = rag_processor.process_url(
    url="https://example.com/document",
    agent_type="requirements_analyst",
    tags=["api", "documentation"]
)

# Process file document
document = rag_processor.process_file(
    file_path="./documents/requirements.txt",
    agent_type="requirements_analyst",
    tags=["requirements", "specification"]
)
```

## 📚 Related Documentation

- **Agents**: See `agents/` directory for agent implementations
- **Workflow**: See `workflow/` directory for workflow management
- **Models**: See `models/` directory for data models
- **Testing**: See `tests/` directory for comprehensive test suite
- **Configuration**: See `models/config.py` for configuration management

## 🤝 Contributing

### Adding New Utilities

1. **Follow Patterns**: Adhere to established utility patterns
2. **Error Handling**: Implement comprehensive error handling
3. **Testing**: Add comprehensive test coverage
4. **Documentation**: Document utility purpose and usage
5. **Performance**: Optimize for performance and efficiency

### Utility Standards

- **Reusability**: Utilities should be reusable across components
- **Error Handling**: Comprehensive error handling and recovery
- **Performance**: Optimize for performance and efficiency
- **Testing**: Full test coverage for all utilities
- **Documentation**: Complete documentation for all utilities

---

**Last Updated**: Current session  
**Version**: 1.0  
**Maintainer**: Development Team

# Documentation Cleaner Utility

## Overview
The `documentation_cleaner.py` utility enforces the **Documentation Cleanliness and Organization rule** to maintain a pristine documentation folder with no temporary, messy, or redundant files.

## Key Features
- **Temporary File Removal**: Automatically removes temporary and summary files
- **File Organization**: Moves files to appropriate subdirectories
- **Duplicate Detection**: Identifies and removes duplicate documentation
- **Structure Validation**: Ensures proper directory structure
- **Index Management**: Keeps documentation index current
- **Quality Gates**: Validates documentation cleanliness before commits

## Usage

### Basic Cleanup
```python
from utils.documentation_cleaner import DocumentationCleaner

cleaner = DocumentationCleaner()
results = cleaner.cleanup_documentation()
```

### Pre-Commit Validation
```python
from utils.documentation_cleaner import validate_documentation_cleanliness

# This will raise an exception if documentation is not clean
validate_documentation_cleanliness()
```

### Quality Gates
```python
from utils.documentation_cleaner import documentation_quality_gates

# Run all quality gates
documentation_quality_gates()
```

### Scheduled Maintenance
```python
from utils.documentation_cleaner import DocumentationMaintenance

maintenance = DocumentationMaintenance()

# Daily cleanup
results = maintenance.daily_cleanup()

# Weekly comprehensive cleanup
results = maintenance.weekly_cleanup()

# Monthly audit
audit_results = maintenance.monthly_audit()
```

## Forbidden File Patterns
The cleaner automatically removes files matching these patterns:
- `DOCUMENTATION_*_SUMMARY.md` - Temporary summary files
- `*_TEMP.md` - Temporary files
- `*_DRAFT.md` - Draft files
- `*_BACKUP.md` - Backup files
- `*_OLD.md` - Old versions
- `*_COPY.md` - Copy files
- `temp_*` - Temporary files
- `draft_*` - Draft files
- `*_notes.md` - Personal notes
- `*_TODO.md` - TODO files
- `*_CHANGES.md` - Change logs (use git)
- `*_UPDATES.md` - Update logs (use git)
- `*_INTEGRATION_SUMMARY.md` - Integration summaries
- `*_UPDATE_SUMMARY.md` - Update summaries
- `*_RULE_INTEGRATION_SUMMARY.md` - Rule integration summaries

## Documentation Structure
The cleaner enforces this structure:
```
docs/
├── DOCUMENTATION_INDEX.md     # Master index (ALWAYS CURRENT)
├── README.md                  # Main docs overview
├── concepts/                  # Concept papers and strategic documents
├── guides/                    # Implementation and how-to guides
├── analysis/                  # Research and analysis documents
└── architecture/              # Architecture documentation
```

## Error Handling
The utility provides specific exception types:
- `DocumentationCleanlinessError` - General cleanliness violations
- `DocumentationOrganizationError` - File organization issues
- `DocumentationIndexError` - Index currency problems
- `DocumentationDuplicateError` - Duplicate file issues

## Integration
This utility integrates with:
- **Pre-commit hooks** - Validate documentation before commits
- **CI/CD pipelines** - Ensure documentation quality in builds
- **Daily maintenance** - Regular cleanup tasks
- **Quality gates** - Documentation quality validation

## CRITICAL RULE ENFORCEMENT
This utility enforces the **Documentation Cleanliness and Organization rule** which is **CRITICAL** for maintaining a clean, professional documentation structure. Always run this utility before making documentation changes to ensure compliance with project standards.
