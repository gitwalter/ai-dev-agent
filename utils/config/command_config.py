"""
Command Configuration System
===========================

Provides parametrizable commands that adapt to different machine configurations
while maintaining formal directory structure organization.
"""

import toml
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class CommandConfig:
    """Load and manage user-configurable command parameters."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize command configuration.
        
        Args:
            config_path: Custom path to config file. Defaults to .agile-config.toml
        """
        self.config_file = Path(config_path or ".agile-config.toml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with sensible defaults."""
        defaults = {
            "environment": {
                "python_exe": self._detect_python_executable(),
                "conda_exe": self._detect_conda_executable(), 
                "shell": "PowerShell" if os.name == 'nt' else "Bash"
            },
            "commands": {
                "test_verbosity": "short",
                "test_parallel": False,
                "test_coverage": False,
                "use_git_operations": True,
                "backup_before_move": True
            },
            "paths": {
                # Note: Core directory structure is IMMUTABLE
                # Only allow custom subdirectories or output locations
            }
        }
        
        if self.config_file.exists():
            try:
                user_config = toml.load(self.config_file)
                return self._merge_configs(defaults, user_config)
            except Exception as e:
                print(f"⚠️ Warning: Error loading config file: {e}")
                print("Using default configuration.")
                return defaults
        else:
            # Create default config file for user customization
            self._create_default_config(defaults)
            return defaults
    
    def get_command(self, command_template: str) -> str:
        """Replace template variables with configured values.
        
        Args:
            command_template: Template string with {variable} placeholders
            
        Returns:
            Command string with variables replaced
        """
        # Combine all config sections for template replacement
        template_vars = {}
        template_vars.update(self.config.get("environment", {}))
        template_vars.update(self.config.get("commands", {}))
        template_vars.update(self.config.get("paths", {}))
        
        try:
            return command_template.format(**template_vars)
        except KeyError as e:
            print(f"⚠️ Warning: Unknown template variable {e} in command: {command_template}")
            return command_template
    
    def get_python_command(self, script_args: str) -> str:
        """Get Python command with configured executable.
        
        Args:
            script_args: Arguments to pass to Python
            
        Returns:
            Full Python command string
        """
        python_exe = self.config["environment"]["python_exe"]
        return f"{python_exe} {script_args}"
    
    def get_test_command(self, test_path: str = "tests/", extra_args: str = "") -> str:
        """Get pytest command with configured options.
        
        Args:
            test_path: Path to test directory or specific test file
            extra_args: Additional pytest arguments
            
        Returns:
            Full pytest command string
        """
        python_exe = self.config["environment"]["python_exe"]
        verbosity = self.config["commands"]["test_verbosity"]
        
        cmd = f"{python_exe} -m pytest {test_path} --tb={verbosity}"
        
        if self.config["commands"]["test_parallel"]:
            cmd += " -n auto"
        
        if self.config["commands"]["test_coverage"]:
            cmd += " --cov=. --cov-report=html"
        
        if extra_args:
            cmd += f" {extra_args}"
        
        return cmd
    
    def validate_config(self) -> bool:
        """Validate configuration doesn't break formal structure.
        
        Returns:
            True if configuration is valid
        """
        # Ensure no directory path overrides that break formal structure
        forbidden_overrides = [
            "docs", "agile", "catalogs", "sprints", "agents", 
            "tests", "scripts", "utils", "workflow", "apps",
            "models", "monitoring", "prompts", "context"
        ]
        
        if "paths" in self.config:
            for path_key in self.config["paths"]:
                if any(forbidden in path_key.lower() for forbidden in forbidden_overrides):
                    print(f"❌ Error: Cannot override formal structure path: {path_key}")
                    return False
        
        # Validate Python executable exists
        python_exe = self.config["environment"]["python_exe"]
        if not shutil.which(python_exe):
            print(f"⚠️ Warning: Python executable not found: {python_exe}")
            print("Commands may fail. Please update .agile-config.toml with correct path.")
        
        return True
    
    def _detect_python_executable(self) -> str:
        """Detect the most appropriate Python executable."""
        # Try common Python executables in order of preference
        candidates = [
            "C:\\App\\Anaconda\\python.exe",  # Anaconda (current setup)
            "python",                          # Standard PATH
            "python3",                         # Linux/Mac preference
            "py",                             # Windows Python Launcher
        ]
        
        for candidate in candidates:
            if shutil.which(candidate):
                return candidate
        
        # Fallback to "python" even if not found
        return "python"
    
    def _detect_conda_executable(self) -> str:
        """Detect conda executable if available."""
        candidates = [
            "C:\\App\\Anaconda\\Scripts\\conda.exe",
            "conda",
        ]
        
        for candidate in candidates:
            if shutil.which(candidate):
                return candidate
        
        return "conda"  # Fallback
    
    def _merge_configs(self, defaults: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults."""
        result = defaults.copy()
        
        for section, values in user_config.items():
            if section in result and isinstance(result[section], dict):
                result[section].update(values)
            else:
                result[section] = values
        
        return result
    
    def _create_default_config(self, defaults: Dict[str, Any]) -> None:
        """Create default configuration file for user customization."""
        try:
            with open(self.config_file, 'w') as f:
                f.write("""# Agile Development Configuration
# This file allows you to customize commands for your specific environment
# while maintaining the formal directory structure.

[environment]
# Python executable path (customize for your installation)
python_exe = "{python_exe}"

# Conda executable (if using conda)
conda_exe = "{conda_exe}"

# Preferred shell
shell = "{shell}"

[commands]
# Test execution preferences
test_verbosity = "short"  # Options: short, long, minimal
test_parallel = false     # Enable parallel test execution
test_coverage = false     # Enable coverage reporting

# File operations
use_git_operations = true  # Enable git-based file tracking
backup_before_move = true  # Create backups before file moves

[paths]
# Custom path overrides (advanced users only)
# NOTE: Cannot override formal directory structure (docs, agents, tests, etc.)
# Only use for custom output directories or tool paths
# Example:
# custom_reports_dir = "my_reports"
""".format(**defaults["environment"]))
            
            print(f"📝 Created default configuration: {self.config_file}")
            print("You can customize this file for your environment.")
        
        except Exception as e:
            print(f"⚠️ Warning: Could not create config file: {e}")


# Global instance for easy access
config = CommandConfig()


def get_command(template: str) -> str:
    """Get a parametrized command using global configuration."""
    return config.get_command(template)


def get_python_command(script_args: str) -> str:
    """Get Python command using global configuration.""" 
    return config.get_python_command(script_args)


def get_test_command(test_path: str = "tests/", extra_args: str = "") -> str:
    """Get pytest command using global configuration."""
    return config.get_test_command(test_path, extra_args)


if __name__ == "__main__":
    # Demo/test the configuration system
    print("🔧 Command Configuration Demo")
    print("=" * 40)
    
    print(f"Python executable: {config.config['environment']['python_exe']}")
    print(f"Shell preference: {config.config['environment']['shell']}")
    print()
    
    print("Example commands:")
    print(f"Test command: {get_test_command()}")
    print(f"Health check: {get_python_command('scripts/health_monitor_service.py --check')}")
    print(f"Custom: {get_command('{python_exe} -c \"print(\\\"Hello from {shell}!\\\")\"')}")
    print()
    
    print(f"Configuration file: {config.config_file}")
    print(f"Valid configuration: {config.validate_config()}")
