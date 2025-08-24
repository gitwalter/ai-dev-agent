"""
TOML Configuration Loader for AI Development Agent.
Handles loading configuration from TOML files including secrets.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Use tomllib for Python 3.11+, tomli for older versions
try:
    import tomllib
except ImportError:
    import tomli as tomllib


class TOMLConfigLoader:
    """
    Loader for TOML configuration files including secrets.
    """
    
    def __init__(self, config_dir: str = "."):
        """
        Initialize the TOML config loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)
        
    def load_secrets(self, secrets_file: str = "secrets.toml") -> Dict[str, Any]:
        """
        Load secrets from TOML file.
        
        Args:
            secrets_file: Name of the secrets file
            
        Returns:
            Dictionary containing secrets
            
        Raises:
            FileNotFoundError: If secrets file doesn't exist
            tomllib.TOMLDecodeError: If TOML file is malformed
        """
        secrets_path = self.config_dir / secrets_file
        
        if not secrets_path.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_path}")
        
        try:
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
            
            self.logger.info(f"Successfully loaded secrets from {secrets_path}")
            return secrets
            
        except tomllib.TOMLDecodeError as e:
            self.logger.error(f"Error parsing TOML file {secrets_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading secrets from {secrets_path}: {e}")
            raise
    
    def load_config(self, config_file: str = "config.toml") -> Dict[str, Any]:
        """
        Load general configuration from TOML file.
        
        Args:
            config_file: Name of the configuration file
            
        Returns:
            Dictionary containing configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            tomllib.TOMLDecodeError: If TOML file is malformed
        """
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            
            self.logger.info(f"Successfully loaded config from {config_path}")
            return config
            
        except tomllib.TOMLDecodeError as e:
            self.logger.error(f"Error parsing TOML file {config_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading config from {config_path}: {e}")
            raise
    
    def get_gemini_api_key(self, secrets_file: str = "secrets.toml") -> Optional[str]:
        """
        Get Gemini API key from secrets file.
        
        Args:
            secrets_file: Name of the secrets file
            
        Returns:
            Gemini API key or None if not found
        """
        try:
            secrets = self.load_secrets(secrets_file)
            return secrets.get("GEMINI_API_KEY")
        except Exception as e:
            self.logger.error(f"Error loading Gemini API key: {e}")
            return None
    
    def create_secrets_template(self, secrets_file: str = "secrets.toml") -> None:
        """
        Create a template secrets file if it doesn't exist.
        
        Args:
            secrets_file: Name of the secrets file to create
        """
        secrets_path = self.config_dir / secrets_file
        
        if secrets_path.exists():
            self.logger.info(f"Secrets file already exists: {secrets_path}")
            return
        
        template_content = """# AI Development Agent Secrets Configuration
# This file contains sensitive configuration data
# DO NOT commit this file to version control

GEMINI_API_KEY = "your-gemini-api-key-here"
"""
        
        try:
            with open(secrets_path, "w") as f:
                f.write(template_content)
            
            self.logger.info(f"Created secrets template at {secrets_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating secrets template: {e}")
            raise


def load_gemini_api_key(config_dir: str = ".") -> Optional[str]:
    """
    Convenience function to load Gemini API key.
    
    Args:
        config_dir: Directory containing secrets.toml
        
    Returns:
        Gemini API key or None if not found
    """
    loader = TOMLConfigLoader(config_dir)
    return loader.get_gemini_api_key()


def ensure_secrets_file(config_dir: str = ".") -> None:
    """
    Ensure secrets file exists, create template if it doesn't.
    
    Args:
        config_dir: Directory to check/create secrets file in
    """
    loader = TOMLConfigLoader(config_dir)
    loader.create_secrets_template()
