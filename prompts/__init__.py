"""
AI Development Agent Prompts Package.

This package contains organized system prompts for AI development agents,
based on best practices from AI-powered software development.
"""

from utils.prompt_management.prompt_manager import PromptManager, get_prompt_manager
from .agent_prompt_loader import AgentPromptLoader, get_agent_prompt_loader

__all__ = [
    'PromptManager',
    'get_prompt_manager',
    'AgentPromptLoader', 
    'get_agent_prompt_loader'
]

__version__ = "1.0.0"
