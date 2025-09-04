"""
Utility functions for the AI Development Agent system.
Contains helper functions, logging configuration, and file management utilities.
"""

from .logging_config import setup_logging
from .file_manager import FileManager
from .core.helpers import *

# Import submodules with error handling to prevent import failures
try:
    from . import parsing
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import parsing module: {e}")
    parsing = None

try:
    from . import prompt_management
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import prompt_management module: {e}")
    prompt_management = None

try:
    from . import ethical_integration
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import ethical_integration module: {e}")
    ethical_integration = None

try:
    from . import rule_system
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import rule_system module: {e}")
    rule_system = None

try:
    from .safe_git_operations import SafeGitOperations
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import SafeGitOperations: {e}")
    SafeGitOperations = None

try:
    from .reliable_context_integration import ReliableContextIntegration
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import ReliableContextIntegration: {e}")
    ReliableContextIntegration = None

__all__ = [
    "setup_logging",
    "FileManager",
    "parsing",
    "prompt_management",
    "ethical_integration", 
    "rule_system",
    "SafeGitOperations",
    "ReliableContextIntegration"
]
