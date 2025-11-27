"""
LLM configuration utilities for Agile Factory.

Provides centralized model configuration with support for switching between
gemini-2.5-flash and gemini-2.5-flash-lite.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Default model (flash-lite for better rate limits)
DEFAULT_MODEL = "gemini-2.5-flash-lite"

# Available models
AVAILABLE_MODELS = {
    "flash": "gemini-2.5-flash",
    "flash-lite": "gemini-2.5-flash-lite",
    "lite": "gemini-2.5-flash-lite",  # Alias
    "default": DEFAULT_MODEL
}


def get_llm_model(state: Optional[dict] = None, env_var: Optional[str] = None) -> str:
    """
    Get the LLM model name to use, with priority:
    1. State parameter (if provided)
    2. Environment variable (GEMINI_MODEL or specified env_var)
    3. Default (gemini-2.5-flash-lite)
    
    Args:
        state: Optional state dict that may contain 'llm_model' or 'model_name'
        env_var: Optional environment variable name to check (defaults to GEMINI_MODEL)
        
    Returns:
        Model name string (e.g., "gemini-2.5-flash-lite")
    """
    # Check state first
    if state:
        model = state.get("llm_model") or state.get("model_name")
        if model:
            # Handle aliases
            if model in AVAILABLE_MODELS:
                model = AVAILABLE_MODELS[model]
            logger.info(f"Using model from state: {model}")
            return model
    
    # Check environment variable
    env_var_name = env_var or "GEMINI_MODEL"
    env_model = os.environ.get(env_var_name)
    if env_model:
        # Handle aliases
        if env_model in AVAILABLE_MODELS:
            env_model = AVAILABLE_MODELS[env_model]
        logger.info(f"Using model from environment variable {env_var_name}: {env_model}")
        return env_model
    
    # Use default
    logger.info(f"Using default model: {DEFAULT_MODEL}")
    return DEFAULT_MODEL


def get_model_display_name(model: str) -> str:
    """
    Get a human-readable display name for the model.
    
    Args:
        model: Model name (e.g., "gemini-2.5-flash-lite")
        
    Returns:
        Display name (e.g., "Gemini 2.5 Flash Lite")
    """
    if "flash-lite" in model or "lite" in model:
        return "Gemini 2.5 Flash Lite"
    elif "flash" in model:
        return "Gemini 2.5 Flash"
    else:
        return model

