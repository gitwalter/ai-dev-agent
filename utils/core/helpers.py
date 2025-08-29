"""
Helper utility functions for the AI Development Agent system.
Contains commonly used utility functions and helpers.
"""

import os
import re
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import hashlib
import logging


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Generate a short random ID.
    
    Args:
        length: Length of the ID
        
    Returns:
        Short random ID string
    """
    return str(uuid.uuid4()).replace('-', '')[:length]


def get_timestamp() -> str:
    """Get current timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def get_formatted_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get formatted timestamp.
    
    Args:
        format_str: Format string for timestamp
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_str)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing or replacing problematic characters.
    
    Args:
        text: Original text
        
    Returns:
        Sanitized text
    """
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> Optional[str]:
    """
    Calculate hash of file content.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm to use
        
    Returns:
        Hash string or None if calculation failed
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception as e:
        logging.getLogger("utils.helpers").error(f"Failed to calculate hash for {file_path}: {e}")
        return None


def calculate_text_hash(text: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of text content.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm to use
        
    Returns:
        Hash string
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for flattened keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def validate_json_string(json_str: str) -> bool:
    """
    Validate if string is valid JSON.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        True if valid JSON
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string with fallback.
    
    Args:
        json_str: JSON string to load
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown text.
    
    Args:
        text: Markdown text
        
    Returns:
        List of code blocks with language and content
    """
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, content in matches:
        code_blocks.append({
            'language': language or 'text',
            'content': content.strip()
        })
    
    return code_blocks


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def is_valid_email(email: str) -> bool:
    """
    Check if email address is valid.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize path object.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized Path object
    """
    return Path(path).resolve()


def ensure_list(value: Union[Any, List[Any]]) -> List[Any]:
    """
    Ensure value is a list.
    
    Args:
        value: Value to convert to list
        
    Returns:
        List containing the value(s)
    """
    if isinstance(value, list):
        return value
    elif value is None:
        return []
    else:
        return [value]


def remove_duplicates(items: List[Any]) -> List[Any]:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        items: List with potential duplicates
        
    Returns:
        List without duplicates
    """
    seen = set()
    result = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks


def get_llm_model(task_complexity="simple", task_type=None):
    """
    Get appropriate LLM model based on task complexity.
    
    Args:
        task_complexity (str): "simple" or "complex"
        task_type (str): Task type for backward compatibility (optional)
        
    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance
    """
    import streamlit as st
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Get API key from Streamlit secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    
    # If task_type is provided, map it to complexity
    if task_type:
        # Map task types to complexity levels
        complex_tasks = {
            "requirements_analysis": "complex",
            "architecture_design": "complex", 
            "code_review": "complex",
            "security_analysis": "complex",
            "documentation": "simple",  # Can be simple or complex
            "code_generation": "simple",  # Can be simple or complex
            "test_generation": "simple"  # Can be simple or complex
        }
        task_complexity = complex_tasks.get(task_type, "simple")
    
    # Select model based on complexity
    if task_complexity == "complex":
        model_name = "gemini-2.5-flash"
    else:
        model_name = "gemini-2.5-flash-lite"
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.1,
        max_tokens=8192
    )


# Export commonly used functions
__all__ = [
    "generate_uuid",
    "generate_short_id", 
    "get_timestamp",
    "get_formatted_timestamp",
    "sanitize_filename",
    "sanitize_text",
    "calculate_file_hash",
    "calculate_text_hash",
    "deep_merge_dicts",
    "flatten_dict",
    "validate_json_string",
    "safe_json_loads",
    "truncate_text",
    "extract_code_blocks",
    "format_file_size",
    "is_valid_email",
    "normalize_path",
    "ensure_list",
    "remove_duplicates",
    "chunk_list",
    "get_llm_model"
]

