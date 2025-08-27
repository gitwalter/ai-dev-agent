"""
Helper utilities for the AI Development Agent system.
"""

import re
import string
from typing import List, Optional
import logging

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


def get_llm_model(task_complexity: str = "simple"):
    """
    Get appropriate LLM model based on task complexity.
    
    Args:
        task_complexity (str): "simple" or "complex"
        
    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance
    """
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in Streamlit secrets")
        
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
        
    except Exception as e:
        logger.error(f"Error creating LLM model: {e}")
        raise


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace spaces and dots with hyphens
    filename = re.sub(r'[.\s]+', '-', filename)
    
    # Remove leading/trailing hyphens and dots
    filename = filename.strip('-.')
    
    # Convert to lowercase
    filename = filename.lower()
    
    # Limit length
    if len(filename) > 50:
        filename = filename[:50]
    
    return filename


def extract_key_concepts(project_description: str) -> List[str]:
    """
    Extract key concepts from project description for naming.
    
    Args:
        project_description: Project description text
        
    Returns:
        List of key concepts
    """
    # Common technology keywords
    tech_keywords = [
        'api', 'web', 'mobile', 'desktop', 'cli', 'bot', 'dashboard',
        'cms', 'ecommerce', 'blog', 'forum', 'chat', 'social',
        'todo', 'calendar', 'calculator', 'game', 'analytics',
        'dashboard', 'admin', 'portal', 'marketplace', 'booking',
        'payment', 'auth', 'user', 'profile', 'notification',
        'email', 'sms', 'file', 'upload', 'download', 'search',
        'filter', 'sort', 'export', 'import', 'report', 'chart',
        'graph', 'map', 'location', 'weather', 'news', 'feed',
        'stream', 'real-time', 'websocket', 'rest', 'graphql',
        'microservice', 'monolith', 'serverless', 'container',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'heroku'
    ]
    
    # Common domain keywords
    domain_keywords = [
        'management', 'system', 'platform', 'service', 'app',
        'tool', 'utility', 'helper', 'assistant', 'automation',
        'workflow', 'process', 'tracker', 'monitor', 'analyzer',
        'generator', 'converter', 'validator', 'formatter',
        'scheduler', 'reminder', 'notifier', 'messenger',
        'store', 'shop', 'market', 'exchange', 'trading',
        'banking', 'finance', 'accounting', 'inventory',
        'hr', 'recruitment', 'education', 'learning', 'course',
        'health', 'medical', 'fitness', 'nutrition', 'travel',
        'transport', 'logistics', 'delivery', 'shipping'
    ]
    
    # Convert to lowercase for matching
    description_lower = project_description.lower()
    
    # Extract technology keywords
    found_tech = [keyword for keyword in tech_keywords if keyword in description_lower]
    
    # Extract domain keywords
    found_domain = [keyword for keyword in domain_keywords if keyword in description_lower]
    
    # Combine and return unique keywords
    all_keywords = list(set(found_tech + found_domain))
    
    return all_keywords


def generate_project_name(project_description: str) -> str:
    """
    Generate a project name from project description.
    
    Args:
        project_description: Project description text
        
    Returns:
        Generated project name
    """
    try:
        # Extract key concepts
        key_concepts = extract_key_concepts(project_description)
        
        if not key_concepts:
            # Fallback: use first few meaningful words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', project_description.lower())
            # Filter out common stop words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'within', 'without', 'against', 'toward', 'towards', 'upon', 'across', 'behind', 'beneath', 'beside', 'beyond', 'inside', 'outside', 'under', 'over', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'create', 'build', 'develop', 'make', 'generate', 'implement', 'design', 'using', 'with', 'features', 'include', 'following', 'such', 'like', 'example', 'project', 'application', 'system', 'platform', 'service'}
            meaningful_words = [word for word in words if word not in stop_words]
            key_concepts = meaningful_words[:3]  # Take first 3 meaningful words
        
        # Create project name from key concepts
        if len(key_concepts) >= 2:
            # Use first two concepts
            project_name = f"{key_concepts[0]}-{key_concepts[1]}"
        elif len(key_concepts) == 1:
            # Use single concept with a generic suffix
            project_name = f"{key_concepts[0]}-app"
        else:
            # Fallback to generic name
            project_name = "ai-generated-project"
        
        # Sanitize the name
        project_name = sanitize_filename(project_name)
        
        # Ensure it's not empty
        if not project_name:
            project_name = "ai-generated-project"
        
        logger.info(f"Generated project name '{project_name}' from description")
        return project_name
        
    except Exception as e:
        logger.error(f"Error generating project name: {str(e)}")
        return "ai-generated-project"


def create_project_path(base_dir: str, project_name: str) -> str:
    """
    Create the full project path within the generated_projects directory.
    
    Args:
        base_dir: Base directory (usually './generated_projects')
        project_name: Generated project name
        
    Returns:
        Full project path
    """
    from pathlib import Path
    
    # Ensure base_dir is './generated_projects'
    if not base_dir.endswith('generated_projects'):
        base_dir = str(Path(base_dir) / 'generated_projects')
    
    # Create the full project path
    project_path = Path(base_dir) / project_name
    
    return str(project_path)
