"""
Prompt Management Package
=========================

Provides utilities for prompt storage, management, and execution tracking.

Modules:
- prompt_manager: Core prompt management functionality

Author: AI-Dev-Agent System
Version: 1.0
"""

from .prompt_manager import (
    PromptManager,
    get_prompt_manager,
    store_agent_prompt,
    record_prompt_execution,
    get_agent_prompt,
    get_prompt_execution_history
)

__all__ = [
    "PromptManager",
    "get_prompt_manager", 
    "store_agent_prompt",
    "record_prompt_execution",
    "get_agent_prompt",
    "get_prompt_execution_history"
]
