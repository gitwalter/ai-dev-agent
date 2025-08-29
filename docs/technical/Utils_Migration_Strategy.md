# Utils Folder Migration Strategy

## Overview

This document provides the detailed technical strategy for reorganizing the utils folder structure without breaking existing functionality. The migration will be performed in carefully planned phases with comprehensive testing at each step.

## Current State Analysis

### File Inventory
```
Root Level Files (Need Migration):
├── check_all_code_generator_prompts.py  → utils.maintenance
├── file_manager.py                      → utils.core
├── health_dashboard.py                  → utils.monitoring  
├── helpers.py                           → utils.core
├── logging_config.py                    → utils.core (consolidate with core/logging_config.py)
├── structured_outputs.py               → utils.data
└── system_health_monitor.py             → utils.monitoring

Existing Organized Files:
├── core/logging_config.py               → Keep, consolidate root version into this

Empty Directories (Need Population):
├── collaboration/   → Ready for future collaboration utilities
├── integration/     → Create toml_config.py, rag_processor.py
├── maintenance/     → Move check_all_code_generator_prompts.py here
├── memory/          → Ready for future memory management utilities
├── parsing/         → Create output_parsers.py, enhanced_output_parsers.py
├── prompt_management/ → Create prompt_manager.py, prompt_editor.py
└── quality/         → Create quality_assurance.py, performance_optimizer.py
```

### Import Analysis

**Current Import Patterns:**
- `from utils.core.helpers import get_llm_model` ✓ Already organized
- `from utils.structured_outputs import ...` ❌ Root level import
- `from utils.system_health_monitor import ...` ❌ Root level import
- `from utils.logging_config import setup_logging` ❌ Root level import
- `from utils.file_manager import FileManager` ❌ Root level import

**Missing Files Referenced in Imports:**
- `utils.helpers` (Referenced but may not exist - need to verify)
- `utils.toml_config` (Referenced but not found - need to create)
- `utils.prompt_manager` (Referenced but not found - need to create)
- `utils.rag_processor` (Referenced but not found - need to create)
- `utils.performance_optimizer` (Referenced but not found - need to create)
- `utils.quality_assurance` (Referenced but not found - need to create)
- `utils.langchain_logging` (Referenced but not found - need to create)

## Migration Phases

### Phase 1: Pre-Migration Setup (30 minutes)

#### 1.1 Create Directory Structure
```bash
# Create all subdirectories with __init__.py files
mkdir -p utils/data utils/monitoring
touch utils/data/__init__.py utils/monitoring/__init__.py
```

#### 1.2 Backup Current State
```bash
# Create backup branch
git checkout -b backup/pre-utils-migration
git add .
git commit -m "Backup before utils migration"
git checkout -b feature/utils-reorganization
```

#### 1.3 Validate Current Test State
```bash
# Ensure all tests pass before starting
python -m pytest tests/ -v --tb=short
```

### Phase 2: Core Module Migration (45 minutes)

#### 2.1 Move Core Files
1. **Move helpers.py**
   ```bash
   mv utils/helpers.py utils/core/helpers.py
   ```

2. **Move file_manager.py**
   ```bash
   mv utils/file_manager.py utils/core/file_manager.py
   ```

3. **Consolidate logging_config.py**
   ```bash
   # Compare and merge the two versions
   diff utils/logging_config.py utils/core/logging_config.py
   # Keep the more complete version in core, remove root version
   rm utils/logging_config.py
   ```

#### 2.2 Update Core Imports
**Files to Update:**
- `agents/test_generator.py` - Line 204: `from utils.helpers import get_llm_model`
- `agents/security_analyst.py` - Line 142: `from utils.helpers import get_llm_model`
- `apps/main.py` - Lines 22, 24, 272
- `apps/streamlit_app.py` - Line 21

**Update Pattern:**
```python
# Before
from utils.helpers import get_llm_model
from utils.logging_config import setup_logging
from utils.file_manager import FileManager

# After  
from utils.core.helpers import get_llm_model
from utils.core.logging_config import setup_logging
from utils.core.file_manager import FileManager
```

#### 2.3 Test Core Migration
```bash
python -m pytest tests/ -k "test_core" --tb=short
```

### Phase 3: Data Module Migration (30 minutes)

#### 3.1 Move Data Files
```bash
mv utils/structured_outputs.py utils/data/structured_outputs.py
```

#### 3.2 Update Data Imports
**Files to Update:**
- `workflow/langgraph_workflow_manager.py` - Line 36
- `workflow/langgraph_workflow.py` - Line 30
- `tests/providers/llm_provider.py` - Line 40
- Multiple test files

**Update Pattern:**
```python
# Before
from utils.structured_outputs import (
    RequirementsAnalysisOutput,
    ArchitectureDesignOutput
)

# After
from utils.data.structured_outputs import (
    RequirementsAnalysisOutput,
    ArchitectureDesignOutput
)
```

#### 3.3 Test Data Migration
```bash
python -m pytest tests/ -k "structured_output" --tb=short
```

### Phase 4: Monitoring Module Migration (30 minutes)

#### 4.1 Move Monitoring Files
```bash
mv utils/system_health_monitor.py utils/monitoring/system_health_monitor.py
mv utils/health_dashboard.py utils/monitoring/health_dashboard.py
```

#### 4.2 Update Monitoring Imports
**Files to Update:**
- `scripts/health_monitor_service.py` - Line 25
- `utils/health_dashboard.py` - Line 21 (internal import)

**Update Pattern:**
```python
# Before
from utils.system_health_monitor import SystemHealthMonitor, start_health_monitoring

# After
from utils.monitoring.system_health_monitor import SystemHealthMonitor, start_health_monitoring
```

#### 4.3 Test Monitoring Migration
```bash
python -m pytest tests/ -k "health" --tb=short
```

### Phase 5: Maintenance Module Migration (15 minutes)

#### 5.1 Move Maintenance Files
```bash
mv utils/check_all_code_generator_prompts.py utils/maintenance/check_all_code_generator_prompts.py
```

#### 5.2 Update Maintenance Imports
**Check for any imports of this file and update accordingly**

### Phase 6: Create Missing Referenced Files (60 minutes)

#### 6.1 Create Missing Files Based on Import Analysis

**Create utils/integration/toml_config.py:**
```python
"""TOML configuration management utilities."""
import streamlit as st
from typing import Dict, Any, Optional

class TOMLConfigLoader:
    """Load configuration from Streamlit secrets."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration from Streamlit secrets."""
        return dict(st.secrets)
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get specific configuration value."""
        return st.secrets.get(key, default)

def ensure_secrets_file():
    """Ensure secrets file exists and is properly configured."""
    # Implementation for secrets file management
    pass
```

**Create utils/integration/rag_processor.py:**
```python
"""RAG processing utilities."""

def get_rag_processor():
    """Get RAG processor instance."""
    # Implementation for RAG processing
    pass
```

**Create utils/prompt_management/prompt_manager.py:**
```python
"""Prompt management utilities."""

class PromptManager:
    """Manage prompts for the system."""
    pass

def get_prompt_manager():
    """Get prompt manager instance."""
    return PromptManager()

def store_agent_prompt(agent_type: str, prompt: str):
    """Store agent prompt."""
    pass

def record_prompt_execution(agent_type: str, success: bool):
    """Record prompt execution result."""
    pass
```

**Create utils/prompt_management/prompt_editor.py:**
```python
"""Prompt editing utilities."""

def get_prompt_editor():
    """Get prompt editor instance."""
    pass
```

**Create utils/quality/quality_assurance.py:**
```python
"""Quality assurance utilities."""
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation check."""
    passed: bool
    message: str
    details: Dict[str, Any] = None

@dataclass 
class QualityGateResult:
    """Result of quality gate check."""
    passed: bool
    validations: List[ValidationResult]

def quality_assurance(code: str, requirements: List[str]) -> QualityGateResult:
    """Perform quality assurance checks."""
    # Implementation for quality assurance
    pass

class ValidationType:
    """Types of validation."""
    SYNTAX = "syntax"
    STYLE = "style"
    SECURITY = "security"
```

**Create utils/quality/performance_optimizer.py:**
```python
"""Performance optimization utilities."""

def record_agent_performance(agent_type: str, duration: float):
    """Record agent performance metrics."""
    pass

def performance_optimizer():
    """Get performance optimizer instance."""
    pass

def analyze_and_optimize_performance():
    """Analyze and optimize system performance."""
    pass
```

**Create utils/core/langchain_logging.py:**
```python
"""LangChain logging utilities."""

def setup_langchain_logging():
    """Setup LangChain logging configuration."""
    pass

def get_logging_manager():
    """Get logging manager for LangChain."""
    pass
```

**Create utils/parsing/output_parsers.py:**
```python
"""Output parsing utilities."""

class OutputParserFactory:
    """Factory for creating output parsers."""
    
    @staticmethod
    def create_parser(parser_type: str):
        """Create parser of specified type."""
        pass
```

**Create utils/parsing/enhanced_output_parsers.py:**
```python
"""Enhanced output parsing utilities."""

class EnhancedOutputParserFactory:
    """Factory for enhanced output parsers."""
    pass

class CodeGenerationParser:
    """Parser for code generation outputs."""
    pass

class EnhancedOutputParser:
    """Enhanced output parser base class."""
    pass

def parse_with_enhanced_parser(content: str, parser_type: str):
    """Parse content with enhanced parser."""
    pass

def get_enhanced_format_instructions(parser_type: str):
    """Get format instructions for enhanced parser."""
    pass
```

#### 6.2 Update Missing File Imports
Update all import statements to reference the new file locations.

### Phase 7: Update __init__.py Files (30 minutes)

#### 7.1 Create Comprehensive __init__.py Files

**utils/__init__.py:**
```python
"""
AI Development Agent Utilities

Organized utility modules for the AI development agent system.
"""

# Re-export commonly used utilities for backward compatibility
from .core.helpers import get_llm_model
from .core.logging_config import setup_logging  
from .core.file_manager import FileManager
from .data.structured_outputs import *
from .monitoring.system_health_monitor import SystemHealthMonitor

__version__ = "1.0.0"
__all__ = [
    "get_llm_model",
    "setup_logging", 
    "FileManager",
    "SystemHealthMonitor"
]
```

**utils/core/__init__.py:**
```python
"""Core utilities for the AI development agent."""

from .helpers import get_llm_model
from .logging_config import setup_logging, setup_agent_logging
from .file_manager import FileManager

__all__ = ["get_llm_model", "setup_logging", "setup_agent_logging", "FileManager"]
```

**utils/data/__init__.py:**
```python
"""Data structures and processing utilities."""

from .structured_outputs import *

# Re-export all structured output classes
```

**utils/monitoring/__init__.py:**
```python
"""System monitoring and health utilities."""

from .system_health_monitor import SystemHealthMonitor, start_health_monitoring
from .health_dashboard import *

__all__ = ["SystemHealthMonitor", "start_health_monitoring"]
```

### Phase 8: Final Testing and Validation (45 minutes)

#### 8.1 Comprehensive Test Run
```bash
# Run full test suite
python -m pytest tests/ -v --tb=short --maxfail=5

# Run specific test categories
python -m pytest tests/unit/ --tb=short
python -m pytest tests/integration/ --tb=short
python -m pytest tests/langgraph/ --tb=short
```

#### 8.2 Import Statement Validation
```bash
# Check for any remaining root-level utils imports
grep -r "from utils\.[a-z]" . --exclude-dir=.git --exclude-dir=__pycache__
grep -r "import utils\.[a-z]" . --exclude-dir=.git --exclude-dir=__pycache__
```

#### 8.3 Linting Check
```bash
python -m pylint utils/ --errors-only
python -m flake8 utils/ --count
```

## Rollback Procedures

### Emergency Rollback
If critical issues are discovered:
```bash
# Immediate rollback to backup branch
git checkout backup/pre-utils-migration
git checkout -b hotfix/utils-rollback
```

### Partial Rollback
If specific files cause issues:
```bash
# Rollback specific files
git checkout backup/pre-utils-migration -- utils/problematic_file.py
```

## Testing Strategy

### Pre-Migration Tests
- [ ] Document all current passing tests
- [ ] Record current import statements
- [ ] Verify current functionality baseline

### Migration Tests
- [ ] Test after each file move
- [ ] Verify imports work after each update
- [ ] Run relevant test subset after each phase

### Post-Migration Tests
- [ ] Full regression test suite
- [ ] Import statement validation
- [ ] Performance impact assessment
- [ ] Integration test verification

## Risk Mitigation

### High-Risk Areas
1. **Complex Import Dependencies**: Some files may have circular imports
2. **Test Dependencies**: Tests may rely on specific import paths
3. **Runtime Imports**: Dynamic imports may not be caught by static analysis

### Mitigation Strategies
1. **Incremental Migration**: Move files in small batches
2. **Comprehensive Testing**: Test after each batch
3. **Import Validation**: Verify all imports work before proceeding
4. **Backup Strategy**: Maintain rollback capability at each step

## Success Criteria

### Functional Success
- [ ] All tests pass after migration
- [ ] All import statements work correctly
- [ ] No functionality is broken
- [ ] Application runs without errors

### Organizational Success
- [ ] Files are logically organized
- [ ] Import paths follow consistent patterns
- [ ] Documentation reflects new structure
- [ ] Developer experience is improved

## Post-Migration Tasks

### Documentation Updates
- [ ] Update README.md with new structure
- [ ] Update architecture documentation
- [ ] Update developer onboarding guides
- [ ] Update import examples in code

### Process Improvements
- [ ] Add linting rules for import patterns
- [ ] Create utility discovery documentation
- [ ] Implement automated import validation
- [ ] Create utility usage guidelines

---

**Prepared by**: Development Team  
**Review Date**: Current Date  
**Approval Status**: Ready for Implementation
