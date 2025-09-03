# File Organization Standards
===========================

**Created**: 2025-01-31  
**Priority**: CRITICAL - Sacred Rule Documentation  
**Purpose**: Comprehensive documentation of project file organization standards  

## 📍 **File Organization Quick Reference**

**ALWAYS USE THESE EXACT PATHS** - No searching required:

### **Current Real Directory Structure**
```
project_root/
├── agents/                 # AI agent implementations ✅ EXISTS
├── apps/                   # Application entry points ✅ EXISTS  
├── context/                # Context management ✅ EXISTS
├── docs/                   # Documentation ✅ EXISTS
│   ├── agile/             # Agile artifacts ✅ EXISTS
│   ├── architecture/      # Architecture docs ✅ EXISTS
│   ├── development/       # This file is here ✅ EXISTS
│   └── [other subdirs]    # Various doc categories ✅ EXISTS
├── examples/               # Code examples ✅ EXISTS
├── logs/                   # Log files ✅ EXISTS
├── models/                 # Data models and schemas ✅ EXISTS
├── monitoring/             # Monitoring and analytics ✅ EXISTS
├── prompts/                # Prompt management ✅ EXISTS
├── scripts/                # Utility scripts ✅ EXISTS
├── tests/                  # All test files ✅ EXISTS
├── tools/                  # Development tools ✅ EXISTS
├── utils/                  # Utility modules ✅ EXISTS
└── workflow/               # Workflow management ✅ EXISTS
```

### **FORMAL Directory Structure Rules** ⚖️
*These directory names and locations are SACRED and NEVER configurable:*

| Directory | Purpose | Rule Status |
|-----------|---------|-------------|
| `docs/agile/catalogs/` | Agile artifact catalogs | 🔒 **IMMUTABLE** |
| `docs/agile/sprints/` | Sprint data storage | 🔒 **IMMUTABLE** |
| `docs/development/` | Development documentation | 🔒 **IMMUTABLE** |
| `agents/` | AI agent implementations | 🔒 **IMMUTABLE** |
| `scripts/` | Utility scripts | 🔒 **IMMUTABLE** |
| `tests/` | All test files | 🔒 **IMMUTABLE** |
| `utils/` | Utility modules | 🔒 **IMMUTABLE** |
| `workflow/` | Workflow management | 🔒 **IMMUTABLE** |

### **Configurable File Movement Commands**
*Commands adapt to your environment via `.agile-config.toml`:*

```bash
# Parametrized file movement (Windows PowerShell default)
move {source_file} {target_directory}\{source_file}

# Examples with formal directory structure:
move demo_script.py scripts\demo_script.py        # ← "scripts" NEVER changes
move test_feature.py tests\test_feature.py        # ← "tests" NEVER changes  
move helper_agent.py agents\helper_agent.py       # ← "agents" NEVER changes
move data_utils.py utils\data_utils.py            # ← "utils" NEVER changes

# Compliance check (parametrized)
dir *.py                                           # Should only show setup.py
```

📋 **Configuration**: See `docs/agile/core/COMMAND_CONFIGURATION.md` for command customization

## Overview

This document provides the complete specification for file organization in the AI-Dev-Agent project. These standards are **SACRED** and must be followed by all team members and automated systems.

## Root Directory Files

### **ALLOWED Root Directory Files** ✅

The following files **MUST** be in the project root directory:

#### **System Configuration Files**
- `.cursor-rules` - Cursor AI configuration (required by Cursor editor)
- `pytest.ini` - pytest configuration (required by pytest)
- `.gitignore` - Git ignore rules (required by Git)
- `.editorconfig` - Editor configuration (required by editors)

#### **Project Metadata Files**
- `README.md` - Main project documentation (required for GitHub/GitLab)
- `requirements.txt` - Python dependencies (required by pip)
- `package.json` - Node.js configuration (if applicable)
- `pyproject.toml` - Python project configuration (modern Python standard)
- `setup.py` - Python package setup (legacy, but sometimes required)
- `setup.cfg` - Python setup configuration

#### **Legal and Documentation**
- `LICENSE` - Project license (required for open source)
- `CHANGELOG.md` - Version history (best practice)
- `.env.example` - Environment variable template (security best practice)

#### **Build and Deployment**
- `Dockerfile` - Container configuration (if using Docker)
- `docker-compose.yml` - Docker composition (if using Docker)

### **FORBIDDEN Root Directory Files** ❌

The following files **MUST NOT** be in the root directory:

#### **Python Code Files**
- `*.py` files (except very specific build scripts)
- Test files (`test_*.py`, `*_test.py`)
- Agent implementations (`*_agent.py`, `*_team.py`)
- Utility modules (`*_utils.py`, `*_helper.py`)

#### **Database Files**
- `*.db` files (SQLite databases)
- `*.sqlite` files
- Database backups

#### **Data Files**
- `*.json` data files (except configuration)
- `*.csv` files
- `*.xml` files
- Log files (`*.log`)

#### **Generated Files**
- Compiled files (`*.pyc`, `*.pyo`)
- Cache directories (`__pycache__/`)
- Build artifacts

## Directory Structure Standards

### **Required Directories**

```
project_root/
├── agents/                 # AI agent implementations
├── apps/                   # Application entry points
├── context/                # Context management
├── docs/                   # Documentation
├── logs/                   # Log files
├── models/                 # Data models and schemas
├── monitoring/             # Monitoring and analytics
├── prompts/                # Prompt management
├── scripts/                # Utility scripts
├── tests/                  # All test files
├── tools/                  # Development tools
├── ui/                     # User interface components
├── utils/                  # Utility modules
└── workflow/               # Workflow management
```

### **File Type to Directory Mapping**

| File Type | Directory | Pattern | Example |
|-----------|-----------|---------|---------|
| Agent implementations | `agents/` | `*_agent.py`, `*_team.py` | `code_generator_agent.py` |
| Test files | `tests/` | `test_*.py`, `*_test.py` | `test_agents.py` |
| Utility modules | `utils/` | `*_utils.py`, `*_helper.py` | `file_utils.py` |
| Data models | `models/` | `*_model.py`, `*_schema.py` | `user_model.py` |
| Database files | `utils/`, `prompts/analytics/` | `*.db` | `learning_experiences.db` |
| Documentation | `docs/` | `*.md` (except root README) | `api_docs.md` |
| Scripts | `scripts/` | Executable `.py` files | `setup_project.py` |
| Monitoring data | `monitoring/` | Analytics, metrics | `performance.json` |
| Prompts | `prompts/` | Prompt templates, databases | `prompt_templates.db` |
| Workflows | `workflow/` | Workflow definitions | `agent_workflow.py` |

## Database File Organization

### **Database Location Rules**

| Database Type | Correct Location | Example |
|---------------|------------------|---------|
| Prompt audit databases | `prompts/analytics/` | `prompt_audit.db` |
| Prompt quality databases | `prompts/analytics/` | `prompt_quality.db` |
| Prompt templates | `prompts/` | `prompt_templates.db` |
| Learning data | `utils/` | `learning_experiences.db` |
| Test databases | `tests/fixtures/` | `test_data.db` |
| Monitoring data | `monitoring/` | `agent_performance.db` |
| Workflow state | `workflow/` | `workflow_state.db` |

### **Database Creation Standards**

When creating databases in code, **ALWAYS** use proper paths:

```python
# ✅ CORRECT - Specify full path
audit_db = PromptAuditTrail("prompts/analytics/prompt_audit.db")
quality_db = PromptQualityAssessor("prompts/analytics/prompt_quality.db")

# ❌ WRONG - Never use root relative paths
audit_db = PromptAuditTrail("prompt_audit.db")  # Creates in root!
```

## Enforcement Mechanisms

### **Automatic Enforcement**
- `file_organization_enforcer.py` - Scans and corrects violations
- `database_cleanup_specialist_team.py` - Handles database violations
- Git pre-commit hooks - Prevent commits with violations

### **Manual Checks**
- Code review process includes file organization verification
- Sprint retrospectives include file organization assessment
- Quarterly audits of project structure

## Common Violations and Solutions

### **Root Directory Python Files**
**Problem**: Python files in root directory  
**Solution**: Move to appropriate subdirectory based on file type

### **Database Files in Root**
**Problem**: `.db` files in root directory  
**Solution**: Move to correct subdirectory, update source code paths

### **Test Files Outside tests/**
**Problem**: Test files in random locations  
**Solution**: Move all test files to `tests/` with proper subdirectory structure

### **Documentation Scattered**
**Problem**: `.md` files throughout project  
**Solution**: Consolidate in `docs/` (except root README.md)

## Integration with Development Tools

### **IDE Configuration**
File organization rules are enforced through:
- `.cursor-rules` (Cursor AI)
- `.editorconfig` (Editor standards)
- `pytest.ini` (Test configuration)

### **CI/CD Pipeline**
Automated checks include:
- File organization validation
- Database location verification
- Documentation structure validation

## Best Practices

### **Creating New Files**
1. Determine file type and purpose
2. Consult directory mapping table
3. Place in correct directory
4. Update documentation if needed
5. Run file organization validator

### **Moving Existing Files**
1. Use file organization enforcer tools
2. Update all import statements
3. Update configuration files
4. Run tests to ensure nothing breaks
5. Update documentation

### **Database Creation**
1. Always specify full directory path
2. Create directory if it doesn't exist
3. Use appropriate subdirectory for database type
4. Never create databases in root directory

## Validation and Monitoring

### **Daily Checks**
- Automated scans for file organization violations
- Database location verification
- Root directory cleanliness check

### **Weekly Reviews**
- File organization compliance report
- Trend analysis of violations
- Tool effectiveness assessment

### **Monthly Audits**
- Complete project structure review
- Documentation synchronization check
- Tool and process improvement recommendations

## Contact and Support

For questions about file organization standards:
- Review this documentation
- Use file organization enforcer tools
- Consult Database Cleanup Specialist Team
- Refer to `.cursor-rules` for AI-specific guidance

---

*This documentation is part of the Sacred File Organization Rule system*  
*Last updated: 2025-01-31*  
*Maintained by: AI-Dev-Agent Development Team*
