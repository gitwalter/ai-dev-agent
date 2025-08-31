"""
TOML configuration utilities for the AI Development Agent system.
Provides TOML file loading and parsing capabilities.
"""

import toml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


def load_toml_config(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from a TOML file.
    
    Args:
        file_path: Path to the TOML configuration file
        
    Returns:
        Dictionary containing the configuration data
        
    Raises:
        FileNotFoundError: If the TOML file doesn't exist
        toml.TomlDecodeError: If the TOML file is malformed
    """
    
    config_path = Path(file_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"TOML configuration file not found: {file_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        
        logging.getLogger(__name__).info(f"Successfully loaded TOML config from {file_path}")
        return config
        
    except toml.TomlDecodeError as e:
        logging.getLogger(__name__).error(f"Failed to parse TOML file {file_path}: {e}")
        raise
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error loading TOML file {file_path}: {e}")
        raise


def load_secrets_toml(secrets_path: str = ".streamlit/secrets.toml") -> Dict[str, Any]:
    """
    Load secrets from a TOML file, typically used for Streamlit secrets.
    
    Args:
        secrets_path: Path to the secrets TOML file
        
    Returns:
        Dictionary containing the secrets data
        
    Raises:
        FileNotFoundError: If the secrets file doesn't exist
    """
    
    try:
        return load_toml_config(secrets_path)
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"Secrets file not found: {secrets_path}")
        return {}


def get_api_key_from_toml(key_name: str, secrets_path: str = ".streamlit/secrets.toml") -> Optional[str]:
    """
    Get an API key from a TOML secrets file.
    
    Args:
        key_name: Name of the API key in the TOML file
        secrets_path: Path to the secrets TOML file
        
    Returns:
        API key value if found, None otherwise
    """
    
    try:
        secrets = load_secrets_toml(secrets_path)
        api_key = secrets.get(key_name)
        
        if api_key:
            logging.getLogger(__name__).info(f"Successfully loaded API key '{key_name}' from {secrets_path}")
            return api_key
        else:
            logging.getLogger(__name__).warning(f"API key '{key_name}' not found in {secrets_path}")
            return None
            
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to load API key '{key_name}' from {secrets_path}: {e}")
        return None


def save_toml_config(config: Dict[str, Any], file_path: str) -> bool:
    """
    Save configuration to a TOML file.
    
    Args:
        config: Configuration dictionary to save
        file_path: Path where to save the TOML file
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        config_path = Path(file_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            toml.dump(config, f)
        
        logging.getLogger(__name__).info(f"Successfully saved TOML config to {file_path}")
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to save TOML config to {file_path}: {e}")
        return False


def merge_toml_configs(*config_paths: str) -> Dict[str, Any]:
    """
    Merge multiple TOML configuration files.
    Later files override earlier ones for conflicting keys.
    
    Args:
        *config_paths: Paths to TOML files to merge
        
    Returns:
        Merged configuration dictionary
    """
    
    merged_config = {}
    
    for config_path in config_paths:
        try:
            config = load_toml_config(config_path)
            merged_config.update(config)
            logging.getLogger(__name__).info(f"Merged config from {config_path}")
        except FileNotFoundError:
            logging.getLogger(__name__).warning(f"Config file not found, skipping: {config_path}")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to merge config from {config_path}: {e}")
    
    return merged_config


def validate_toml_config(config: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that a TOML configuration contains required keys.
    
    Args:
        config: Configuration dictionary to validate
        required_keys: List of required key names
        
    Returns:
        True if all required keys are present, False otherwise
    """
    
    missing_keys = []
    
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
    
    if missing_keys:
        logging.getLogger(__name__).error(f"Missing required configuration keys: {missing_keys}")
        return False
    
    logging.getLogger(__name__).info("TOML configuration validation passed")
    return True


class TOMLConfigLoader:
    """
    Legacy compatibility class for TOML configuration loading.
    Provides backward compatibility with existing code.
    """
    
    def __init__(self, config_path: str = ".streamlit/secrets.toml"):
        """
        Initialize TOML config loader.
        
        Args:
            config_path: Path to the TOML configuration file
        """
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        if self._config is None:
            self._config = load_toml_config(self.config_path)
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        config = self.load_config()
        return config.get(key, default)
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get an API key from the configuration."""
        return get_api_key_from_toml(key_name, self.config_path)
    
    def get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from the configuration."""
        return self.get_api_key("GEMINI_API_KEY")


# Export commonly used functions
__all__ = [
    "load_toml_config",
    "load_secrets_toml", 
    "get_api_key_from_toml",
    "save_toml_config",
    "merge_toml_configs",
    "validate_toml_config",
    "TOMLConfigLoader"
]
