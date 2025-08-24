"""
Agent Prompt Loader.

This module provides utilities for agents to load and use their system prompts.
"""

from typing import Dict, Any, Optional
from utils.prompt_manager import get_prompt_manager

class AgentPromptLoader:
    """Utility class for agents to load their prompts."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.prompt_manager = get_prompt_manager()
    
    def get_system_prompt(self, use_enhanced: bool = True) -> str:
        """Get the system prompt for this agent."""
        if use_enhanced:
            enhanced_prompt = self.prompt_manager.get_enhanced_prompt(self.agent_name)
            if enhanced_prompt:
                return enhanced_prompt
        
        # Fall back to database prompt
        best_prompt = self.prompt_manager.get_best_prompt(self.agent_name)
        if best_prompt:
            return best_prompt['template']
        
        # Fall back to default prompt
        return self.get_default_prompt()
    
    def get_default_prompt(self) -> str:
        """Get a default prompt if none is found."""
        default_prompts = {
            'requirements_analyst': 'You are an expert Requirements Analyst. Analyze the project and extract comprehensive requirements.',
            'architecture_designer': 'You are an expert Software Architect. Design scalable and maintainable system architectures.',
            'code_generator': 'You are an expert Software Developer. Generate high-quality, production-ready code.',
            'test_generator': 'You are an expert Test Engineer. Create comprehensive test suites.',
            'code_reviewer': 'You are an expert Code Reviewer. Conduct thorough code reviews.',
            'security_analyst': 'You are an expert Security Analyst. Identify and mitigate security vulnerabilities.',
            'documentation_generator': 'You are an expert Technical Writer. Create comprehensive documentation.'
        }
        
        return default_prompts.get(self.agent_name, f"You are an expert {self.agent_name.replace('_', ' ').title()}.")
    
    def format_prompt(self, variables: Dict[str, Any]) -> str:
        """Format the system prompt with variables."""
        prompt = self.get_system_prompt()
        return self.prompt_manager.format_prompt(prompt, variables)
    
    def log_usage(self, prompt_id: int, success: bool, response_time: float = None):
        """Log prompt usage."""
        self.prompt_manager.log_prompt_usage(prompt_id, success, response_time)

def get_agent_prompt_loader(agent_name: str) -> AgentPromptLoader:
    """Get a prompt loader for a specific agent."""
    return AgentPromptLoader(agent_name)
