"""
AI Development Agent Prompts Package.

This package contains organized system prompts for AI development agents,
based on best practices from AI-powered software development.
"""

try:
    from utils.prompt_management import PromptManager, get_prompt_manager
except ImportError:
    # Fallback prompt manager for testing
    class PromptManager:
        def get_prompt(self, prompt_id): return {"content": "test prompt"}
    def get_prompt_manager(): return PromptManager()

try:
    from .agent_prompt_loader import AgentPromptLoader, get_agent_prompt_loader
except ImportError:
    # Fallback agent prompt loader for testing
    class AgentPromptLoader:
        def __init__(self, agent_name):
            self.agent_name = agent_name
        def get_system_prompt(self):
            return f"You are a {self.agent_name} agent. Perform your designated tasks effectively."
    def get_agent_prompt_loader(agent_name):
        return AgentPromptLoader(agent_name)

__all__ = [
    'PromptManager',
    'get_prompt_manager',
    'AgentPromptLoader', 
    'get_agent_prompt_loader'
]

__version__ = "1.0.0"
