# Coding Standards

**Priority**: CRITICAL - Foundation Standard  
**Authority**: Project Development Team  
**Scope**: ALL code artifacts  
**Status**: MANDATORY COMPLIANCE REQUIRED

---

## 🐍 **Python Code Standards**

### **Code Style and Formatting**

#### **PEP 8 Compliance**
```python
# ✅ CORRECT: Follow PEP 8 guidelines
class ContextAwareRuleLoader:
    """Intelligent rule selection based on development context."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.loaded_rules: List[str] = []
        
    def optimize_efficiency(self) -> float:
        """Improve token efficiency through smart rule loading."""
        return self._calculate_efficiency()
    
    def _calculate_efficiency(self) -> float:
        """Private method for efficiency calculation."""
        # Implementation details
        pass

# ❌ INCORRECT: PEP 8 violations
class contextAwareRuleLoader:  # Should be PascalCase
    def optimizeEfficiency(self):  # Should be snake_case
        return self.calculateEfficiency()  # Should be _calculate_efficiency for private
```

#### **Line Length and Formatting**
```python
# ✅ CORRECT: 120 characters max, proper line breaks
def create_complex_configuration(
    context_type: str,
    efficiency_threshold: float = 0.8,
    optimization_level: str = "standard"
) -> Dict[str, Any]:
    """Create configuration with proper parameter formatting."""
    return {
        "context": context_type,
        "threshold": efficiency_threshold,
        "optimization": optimization_level
    }

# ❌ INCORRECT: Line too long, poor formatting
def create_complex_configuration(context_type: str, efficiency_threshold: float = 0.8, optimization_level: str = "standard") -> Dict[str, Any]:
    return {"context": context_type, "threshold": efficiency_threshold, "optimization": optimization_level}
```

### **Type Hints and Documentation**

#### **Comprehensive Type Hints**
```python
# ✅ CORRECT: Complete type annotations
from typing import Dict, List, Optional, Union, Any, Callable
from pathlib import Path

def process_agent_output(
    agent_result: Dict[str, Any],
    validation_rules: List[Callable[[Dict], bool]],
    output_path: Optional[Path] = None
) -> Union[Dict[str, Any], None]:
    """Process agent output with validation."""
    pass

# ❌ INCORRECT: Missing or incomplete type hints
def process_agent_output(agent_result, validation_rules, output_path=None):
    """Process agent output with validation."""
    pass
```

#### **Docstring Standards**
```python
# ✅ CORRECT: Complete docstring with all sections
def validate_naming_conventions(file_path: str, rules: Dict[str, str]) -> bool:
    """
    Validate file naming against established conventions.
    
    Args:
        file_path (str): Path to the file to validate
        rules (Dict[str, str]): Naming rules by file type
        
    Returns:
        bool: True if naming is compliant, False otherwise
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If rules are invalid
        
    Example:
        >>> validate_naming_conventions("test_agent.py", {"test": "test_*.py"})
        True
    """
    pass

# ❌ INCORRECT: Minimal or missing docstring
def validate_naming_conventions(file_path, rules):
    """Validate file naming."""
    pass
```

### **Error Handling and Logging**

#### **Comprehensive Error Handling**
```python
# ✅ CORRECT: Specific exceptions with context
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_configuration(config_path: str) -> Dict[str, Any]:
    """Load configuration with proper error handling."""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with config_file.open() as f:
            config = yaml.safe_load(f)
            
        if not isinstance(config, dict):
            raise ValueError(f"Invalid configuration format in {config_path}")
            
        logger.info(f"Configuration loaded successfully from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {config_path}: {e}")
        raise ValueError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise

# ❌ INCORRECT: Generic exception handling
def load_configuration(config_path):
    try:
        with open(config_path) as f:
            return yaml.load(f)
    except:
        return {}
```

#### **Proper Logging Usage**
```python
# ✅ CORRECT: Structured logging with appropriate levels
import logging

logger = logging.getLogger(__name__)

class AgentManager:
    def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute task with proper logging."""
        logger.info(f"Starting task execution: {task}")
        
        try:
            result = self._process_task(task)
            logger.info(f"Task completed successfully: {task}")
            return result
            
        except ValidationError as e:
            logger.warning(f"Task validation failed: {task} - {e}")
            raise
        except Exception as e:
            logger.error(f"Task execution failed: {task} - {e}", exc_info=True)
            raise

# ❌ INCORRECT: Poor logging practices
def execute_task(self, task):
    print(f"Doing task: {task}")  # Should use logger
    try:
        result = self._process_task(task)
        print("Done")  # Not informative
        return result
    except Exception as e:
        print(f"Error: {e}")  # Should log with proper level
        return None  # Should raise, not return None
```

---

## 🏗️ **Architecture and Design Standards**

### **Class Design Principles**

#### **Single Responsibility Principle**
```python
# ✅ CORRECT: Each class has one responsibility
class FileValidator:
    """Validates files against naming conventions."""
    
    def validate_file_naming(self, file_path: str) -> bool:
        """Validate file naming conventions."""
        pass
    
    def validate_file_structure(self, file_path: str) -> bool:
        """Validate file internal structure."""
        pass

class FileOrganizer:
    """Organizes files according to project structure."""
    
    def move_file_to_correct_location(self, file_path: str) -> str:
        """Move file to its correct directory."""
        pass

# ❌ INCORRECT: Class with multiple responsibilities
class FileManager:
    """Manages files, validates them, organizes them, and logs everything."""
    
    def validate_file(self, file_path):
        pass
    
    def organize_files(self):
        pass
    
    def send_notifications(self):
        pass
    
    def generate_reports(self):
        pass
```

#### **Dependency Injection**
```python
# ✅ CORRECT: Dependencies injected, testable
from abc import ABC, abstractmethod

class ConfigLoader(ABC):
    @abstractmethod
    def load_config(self, path: str) -> Dict[str, Any]:
        pass

class YamlConfigLoader(ConfigLoader):
    def load_config(self, path: str) -> Dict[str, Any]:
        # Implementation
        pass

class AgentManager:
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
    
    def initialize(self, config_path: str) -> None:
        config = self.config_loader.load_config(config_path)
        # Use config

# ❌ INCORRECT: Hard-coded dependencies
class AgentManager:
    def __init__(self):
        self.config_loader = YamlConfigLoader()  # Hard-coded dependency
    
    def initialize(self, config_path: str) -> None:
        config = self.config_loader.load_config(config_path)
```

### **Function Design Standards**

#### **Pure Functions When Possible**
```python
# ✅ CORRECT: Pure function, predictable and testable
def calculate_efficiency_score(
    active_rules: List[str],
    total_rules: List[str],
    context_weight: float = 1.0
) -> float:
    """Calculate efficiency score based on rule activation."""
    if not total_rules:
        return 0.0
    
    base_efficiency = len(active_rules) / len(total_rules)
    return base_efficiency * context_weight

# ❌ INCORRECT: Function with side effects
efficiency_cache = {}

def calculate_efficiency_score(active_rules, total_rules):
    # Side effect: modifies global state
    global efficiency_cache
    
    key = f"{len(active_rules)}_{len(total_rules)}"
    if key in efficiency_cache:
        print(f"Using cached result")  # Side effect: I/O
        return efficiency_cache[key]
    
    result = len(active_rules) / len(total_rules)
    efficiency_cache[key] = result  # Side effect: modifies global
    return result
```

#### **Small, Focused Functions**
```python
# ✅ CORRECT: Small, focused functions
def validate_file_name(file_name: str, pattern: str) -> bool:
    """Validate single file name against pattern."""
    return re.match(pattern, file_name) is not None

def validate_file_location(file_path: str, expected_dir: str) -> bool:
    """Validate file is in expected directory."""
    return Path(file_path).parent.name == expected_dir

def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> bool:
    """Validate file has allowed extension."""
    return Path(file_path).suffix in allowed_extensions

# ❌ INCORRECT: Large, multi-purpose function
def validate_file(file_path, naming_rules, location_rules, extension_rules):
    """Validate file against all rules."""
    # 50+ lines of validation logic
    # Multiple responsibilities
    # Hard to test individual aspects
    pass
```

---

## 🧪 **Testing Standards**

### **Test Organization**
```python
# ✅ CORRECT: Well-organized test class
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

class TestFileValidator:
    """Test suite for FileValidator class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.validator = FileValidator()
        self.test_file = Path("test_example.py")
    
    def test_validate_file_naming_with_valid_name(self):
        """Test file validation with valid naming convention."""
        # Arrange
        file_name = "test_agent_validation.py"
        pattern = r"test_.*\.py"
        
        # Act
        result = self.validator.validate_file_naming(file_name, pattern)
        
        # Assert
        assert result is True
    
    def test_validate_file_naming_with_invalid_name(self):
        """Test file validation with invalid naming convention."""
        # Arrange
        file_name = "AgentValidationTest.py"
        pattern = r"test_.*\.py"
        
        # Act
        result = self.validator.validate_file_naming(file_name, pattern)
        
        # Assert
        assert result is False
    
    @patch('pathlib.Path.exists')
    def test_validate_file_location_with_mocked_filesystem(self, mock_exists):
        """Test file location validation with mocked filesystem."""
        # Arrange
        mock_exists.return_value = True
        file_path = "tests/unit/test_example.py"
        
        # Act
        result = self.validator.validate_file_location(file_path, "tests")
        
        # Assert
        assert result is True
        mock_exists.assert_called_once()

# ❌ INCORRECT: Poor test organization
def test_stuff():
    # Multiple unrelated tests in one function
    # No clear arrange/act/assert structure
    # No descriptive test names
    pass
```

### **Test Coverage Requirements**
```python
# ✅ CORRECT: Comprehensive test coverage
class TestAgentManager:
    """Comprehensive test coverage for AgentManager."""
    
    def test_normal_operation(self):
        """Test normal successful operation."""
        pass
    
    def test_edge_case_empty_input(self):
        """Test edge case with empty input."""
        pass
    
    def test_edge_case_maximum_input(self):
        """Test edge case with maximum allowed input."""
        pass
    
    def test_error_condition_invalid_input(self):
        """Test error handling with invalid input."""
        with pytest.raises(ValueError):
            # Test code
            pass
    
    def test_error_condition_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            # Test code
            pass
    
    def test_integration_with_file_system(self):
        """Test integration with actual file system."""
        pass
```

---

## 📁 **File and Project Organization**

### **Import Organization**
```python
# ✅ CORRECT: Organized imports with proper grouping
# Standard library imports
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Third-party imports
import yaml
import pytest
from pydantic import BaseModel

# Local application imports
from agents.base_agent import BaseAgent
from utils.validation.naming_validator import NamingValidator
from models.agent_state import AgentState

# ❌ INCORRECT: Disorganized imports
from utils.validation.naming_validator import NamingValidator
import os
from agents.base_agent import BaseAgent
import yaml
from typing import Dict
import sys
from models.agent_state import AgentState
```

### **Module Structure**
```python
# ✅ CORRECT: Well-structured module
"""
Module docstring explaining purpose and usage.

Example:
    from utils.validation import FileValidator
    
    validator = FileValidator()
    result = validator.validate_file("test.py")
"""

# Imports (grouped as shown above)

# Constants
DEFAULT_CONFIG_PATH = "config.yaml"
MAX_RETRY_ATTEMPTS = 3

# Exception classes
class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

# Main classes
class FileValidator:
    """Main file validation class."""
    pass

# Utility functions
def load_validation_rules(path: str) -> Dict[str, str]:
    """Load validation rules from configuration file."""
    pass

# Entry point (if executable)
if __name__ == "__main__":
    main()
```

---

## 🔧 **Performance and Optimization Standards**

### **Efficient Code Practices**
```python
# ✅ CORRECT: Efficient list comprehension
def filter_valid_files(files: List[str], pattern: str) -> List[str]:
    """Filter files matching the pattern efficiently."""
    compiled_pattern = re.compile(pattern)
    return [f for f in files if compiled_pattern.match(f)]

# ❌ INCORRECT: Inefficient loop with repeated compilation
def filter_valid_files(files, pattern):
    result = []
    for f in files:
        if re.match(pattern, f):  # Compiles pattern each time
            result.append(f)
    return result
```

### **Memory Management**
```python
# ✅ CORRECT: Generator for large datasets
def process_large_file(file_path: str) -> Iterator[Dict[str, Any]]:
    """Process large file line by line to save memory."""
    with open(file_path, 'r') as f:
        for line in f:
            yield process_line(line)

# ❌ INCORRECT: Loading entire file into memory
def process_large_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()  # Loads entire file
    return [process_line(line) for line in lines]
```

---

## 🛡️ **Security Standards**

### **Input Validation**
```python
# ✅ CORRECT: Comprehensive input validation
def load_user_configuration(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Load user configuration with security validation."""
    # Validate required fields
    required_fields = ["project_name", "python_exe"]
    for field in required_fields:
        if field not in config_data:
            raise ValueError(f"Required field missing: {field}")
    
    # Sanitize file paths
    python_exe = str(config_data["python_exe"])
    if not python_exe.endswith((".exe", "")):
        raise ValueError("Invalid Python executable path")
    
    # Validate project name (alphanumeric plus specific chars)
    project_name = str(config_data["project_name"])
    if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
        raise ValueError("Invalid project name format")
    
    return {
        "project_name": project_name,
        "python_exe": python_exe
    }

# ❌ INCORRECT: No input validation
def load_user_configuration(config_data):
    return config_data  # Trusts all input
```

---

## 📊 **Code Quality Metrics**

### **Required Standards**
```yaml
code_quality_requirements:
  test_coverage: "≥ 90%"
  cyclomatic_complexity: "≤ 10 per function"
  line_length: "≤ 120 characters"
  function_length: "≤ 50 lines"
  class_length: "≤ 500 lines"
  documentation_coverage: "100% for public APIs"
  type_hint_coverage: "100% for function signatures"
```

### **Quality Validation Tools**
```bash
# Code formatting
black --line-length 120 .
isort .

# Type checking
mypy --strict .

# Linting
flake8 --max-line-length=120 .
pylint --max-line-length=120 .

# Security scanning
bandit -r .

# Test coverage
pytest --cov=. --cov-report=html --cov-fail-under=90
```

---

## ✅ **Pre-commit Checklist**

Before committing any code, ensure:

- [ ] **Code Style**: Passes black and isort formatting
- [ ] **Type Hints**: All functions have complete type annotations
- [ ] **Documentation**: All public APIs have docstrings
- [ ] **Tests**: New code has ≥90% test coverage
- [ ] **Linting**: Passes flake8 and pylint checks
- [ ] **Security**: Passes bandit security scan
- [ ] **Naming**: Follows project naming conventions
- [ ] **Error Handling**: Proper exception handling implemented
- [ ] **Logging**: Appropriate logging levels used
- [ ] **Performance**: No obvious performance issues

---

## 🔗 **Integration with Development Tools**

### **IDE Configuration**
```json
// VS Code settings.json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "120"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### **Git Hooks**
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running code quality checks..."

# Format code
black --line-length 120 .
isort .

# Type checking
mypy --strict . || exit 1

# Linting
flake8 --max-line-length=120 . || exit 1

# Security scan
bandit -r . || exit 1

# Tests
pytest --cov=. --cov-fail-under=90 || exit 1

echo "All checks passed!"
```

---

**Remember**: "Clean code is not written by following a set of rules. Clean code is written by programmers who care about quality and maintainability."

**Standards Foundation**: PEP 8 + Type Safety + Testing Excellence + Security Awareness = Professional Code Quality
