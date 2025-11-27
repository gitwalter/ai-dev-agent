"""
Safe prompt formatting utility.

Handles prompt templates that contain JSON examples with braces by using
string replacement instead of Python's .format() method, which would
interpret JSON braces as placeholders.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def safe_format_prompt(template: str, **kwargs) -> str:
    """
    Safely format a prompt template by replacing only specific placeholders.
    
    This function uses string replacement instead of Python's .format() to
    avoid issues with JSON examples in prompts that contain braces.
    
    Args:
        template: Prompt template string
        **kwargs: Placeholder values to replace
        
    Returns:
        Formatted prompt string
        
    Example:
        template = "User Story: {user_story}\\nJSON: {\\"key\\": \\"value\\"}"
        result = safe_format_prompt(template, user_story="Test story")
        # Result: "User Story: Test story\\nJSON: {\\"key\\": \\"value\\"}"
    """
    if not isinstance(template, str):
        raise TypeError(f"Template must be a string, got {type(template)}")
    
    result = template
    
    # Replace each placeholder with its value
    for key, value in kwargs.items():
        # Escape special regex characters in the key
        placeholder = f"{{{key}}}"
        
        # Convert value to string
        value_str = str(value)
        
        # Replace all occurrences of the placeholder
        result = result.replace(placeholder, value_str)
    
    return result


def safe_format_prompt_with_validation(template: str, **kwargs) -> tuple[str, list[str]]:
    """
    Safely format a prompt template and return missing placeholders.
    
    Args:
        template: Prompt template string
        **kwargs: Placeholder values to replace
        
    Returns:
        Tuple of (formatted_prompt, missing_placeholders)
    """
    if not isinstance(template, str):
        raise TypeError(f"Template must be a string, got {type(template)}")
    
    # Find all placeholders in template (single braces with word characters)
    placeholder_pattern = r'\{(\w+)\}'
    found_placeholders = set(re.findall(placeholder_pattern, template))
    
    # Find which placeholders are missing from kwargs
    missing_placeholders = found_placeholders - set(kwargs.keys())
    
    # Format the template
    formatted = safe_format_prompt(template, **kwargs)
    
    return formatted, list(missing_placeholders)

