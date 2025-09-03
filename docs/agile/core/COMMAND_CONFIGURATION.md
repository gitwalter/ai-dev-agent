# Command Configuration System

**Purpose**: Parametrizable commands that adapt to different machine configurations while maintaining formal directory structure organization.

## 🔧 **User-Configurable Commands**

### **Machine-Specific Configuration**

Create a `.agile-config.toml` file in your project root with your specific paths:

```toml
[environment]
# Python executable path (varies by machine)
python_exe = "C:\\App\\Anaconda\\python.exe"
# Alternative examples:
# python_exe = "python"                    # Standard PATH installation
# python_exe = "/usr/bin/python3"          # Linux system installation
# python_exe = "C:\\Python311\\python.exe" # Windows direct installation

# Conda executable (if using conda)
conda_exe = "C:\\App\\Anaconda\\Scripts\\conda.exe"

# Shell preferences
shell = "PowerShell"  # Options: PowerShell, CMD, Bash

[commands]
# Test execution preferences
test_verbosity = "short"  # Options: short, long, minimal
test_parallel = false     # Enable parallel test execution
test_coverage = false     # Enable coverage reporting

# File operations
use_git_operations = true  # Enable git-based file tracking
backup_before_move = true  # Create backups before file moves

[paths]
# Custom path overrides (if needed)
# logs_directory = "custom_logs"
# scripts_directory = "my_scripts"
```

### **Parametrized Command Templates**

```bash
# Test Commands (parametrizable)
{python_exe} -m pytest tests/ --tb={test_verbosity} -x
{python_exe} -m pytest tests/automated_ui/ -v
{python_exe} -m pytest tests/ --cov=. --cov-report=html  # If coverage enabled

# Health Check Commands
{python_exe} scripts/health_monitor_service.py --check
{python_exe} scripts/health_monitor_service.py --full-report

# File Organization Commands
move {source_file} {target_directory}\\{source_file}  # PowerShell
mv {source_file} {target_directory}/{source_file}    # Bash

# Development Commands  
{python_exe} -m pylint src/ --errors-only
{python_exe} -m black src/ --check
{python_exe} -c "import sys; print(sys.version)"

# Git Commands - CLEAN REPOSITORY WORKFLOW
git add .                              # ALWAYS stage everything first
git status                             # Verify staged changes
git commit --no-verify -m "[type]: [description]"  # Commit with bypass
git push                               # Push to remote

# One-liner Git Commands for Speed
git add . && git status && git commit --no-verify -m "feat: [description]" && git push
git add . && git status && git commit --no-verify -m "fix: [description]" && git push
git add . && git status && git commit --no-verify -m "docs: [description]" && git push
```

## 🏗️ **Formal Directory Structure Rules**

### **SACRED Directory Organization** 
*These paths are NEVER configurable - they define our formal structure*

```
project_root/
├── .agile-config.toml          # ← USER CONFIGURABLE (this file only)
├── docs/                       # ← FORMAL STRUCTURE (never changes)
│   ├── agile/                 # ← FORMAL: Agile artifacts location
│   │   ├── catalogs/          # ← FORMAL: Catalog files location
│   │   ├── sprints/           # ← FORMAL: Sprint data location
│   │   └── core/              # ← FORMAL: Core agile rules location
│   ├── development/           # ← FORMAL: Development documentation
│   └── architecture/          # ← FORMAL: Architecture documentation
├── agents/                     # ← FORMAL: AI agent implementations
├── apps/                       # ← FORMAL: Application entry points
├── scripts/                    # ← FORMAL: Utility scripts location
├── tests/                      # ← FORMAL: All test files location
├── utils/                      # ← FORMAL: Utility modules location
├── workflow/                   # ← FORMAL: Workflow management
└── [other formal directories]  # ← FORMAL: As defined by organization rules
```

### **Configuration vs. Structure Separation**

| **USER CONFIGURABLE** | **FORMALLY STRUCTURED** |
|----------------------|-------------------------|
| ✅ Python executable path | ❌ Directory names |
| ✅ Command parameters | ❌ File locations |
| ✅ Tool preferences | ❌ Agile artifact paths |
| ✅ Environment settings | ❌ Organization rules |
| ✅ Machine-specific paths | ❌ Project structure |

## 🚀 **Implementation System**

### **Configuration Loading**

```python
# utils/config/command_config.py
import toml
import os
from pathlib import Path

class CommandConfig:
    """Load and manage user-configurable command parameters."""
    
    def __init__(self):
        self.config_file = Path(".agile-config.toml")
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration with sensible defaults."""
        defaults = {
            "environment": {
                "python_exe": "python",
                "conda_exe": "conda",
                "shell": "PowerShell" if os.name == 'nt' else "Bash"
            },
            "commands": {
                "test_verbosity": "short",
                "test_parallel": False,
                "test_coverage": False
            },
            "paths": {}
        }
        
        if self.config_file.exists():
            user_config = toml.load(self.config_file)
            # Merge user config with defaults
            return self.merge_configs(defaults, user_config)
        else:
            # Create default config file
            self.create_default_config(defaults)
            return defaults
    
    def get_command(self, command_template: str) -> str:
        """Replace template variables with configured values."""
        return command_template.format(**self.config["environment"])
    
    def create_default_config(self, defaults):
        """Create default configuration file for user customization."""
        with open(self.config_file, 'w') as f:
            toml.dump(defaults, f)
```

### **Usage in Rules and Agents**

```python
# Example usage in agent code
from utils.config.command_config import CommandConfig

config = CommandConfig()

# Get parametrized commands
test_command = config.get_command("{python_exe} -m pytest tests/ --tb={test_verbosity} -x")
health_command = config.get_command("{python_exe} scripts/health_monitor_service.py --check")

# Execute with user's specific configuration
result = subprocess.run(test_command.split(), capture_output=True, text=True)
```

## 📋 **Updated Rule Integration**

### **In Agile Cursor Rules**
```markdown
### **Working Commands (Parametrizable)**
Configure your `.agile-config.toml` file, then use:

- **Test Status**: `{python_exe} -m pytest tests/ --tb={test_verbosity} -x`
- **UI Tests**: `{python_exe} -m pytest tests/automated_ui/ -v`  
- **Health Check**: `{python_exe} scripts/health_monitor_service.py --check`

*Variables are automatically replaced with your configuration.*
```

### **In File Organization Rules**
```markdown
### **FORMAL Directory Structure** (Non-Configurable)
The following structure is SACRED and must never be modified by user configuration:

- `docs/agile/catalogs/USER_STORY_CATALOG.md` ← ALWAYS this exact path
- `docs/agile/daily_standup.md` ← ALWAYS this exact path
- `scripts/` ← ALWAYS this exact directory name
- `tests/` ← ALWAYS this exact directory name

### **Configurable Commands** (User-Customizable)
File movement and execution commands adapt to your environment via `.agile-config.toml`
```

## 🎯 **Benefits**

### **For Users**
- ✅ **Machine Flexibility**: Works on any Python installation
- ✅ **Environment Adaptation**: Supports Windows, Linux, macOS
- ✅ **Personal Preferences**: Customize verbosity, tools, options
- ✅ **Easy Setup**: Single configuration file

### **For System**
- ✅ **Formal Structure**: Directory organization remains consistent
- ✅ **Agile Compliance**: Artifact locations never change
- ✅ **Rule Integrity**: Organization rules maintain authority
- ✅ **Scalability**: New users can configure easily without breaking structure

## 🔒 **Configuration Validation**

```python
def validate_config(config):
    """Validate user configuration doesn't break formal structure."""
    
    # Ensure no directory path overrides that break formal structure
    forbidden_overrides = [
        "docs", "agile", "catalogs", "sprints", "agents", 
        "tests", "scripts", "utils", "workflow"
    ]
    
    if "paths" in config:
        for path_key in config["paths"]:
            if any(forbidden in path_key for forbidden in forbidden_overrides):
                raise ValueError(f"Cannot override formal structure path: {path_key}")
    
    # Validate Python executable exists
    python_exe = config["environment"]["python_exe"]
    if not shutil.which(python_exe):
        print(f"⚠️ Warning: Python executable not found: {python_exe}")
    
    return True
```

---

**Key Principle**: **Configuration enables flexibility, Structure ensures consistency**
