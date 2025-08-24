"""
Configuration models for the AI Development Agent system.
Defines configuration classes for agents, workflow, and system settings.
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from pathlib import Path


class GeminiConfig(BaseModel):
    """Configuration for Gemini API integration."""
    
    api_key: str = Field(..., description="Gemini API key")
    model_name: str = Field(default="gemini-2.5-flash-lite", description="Gemini model to use")
    max_tokens: int = Field(default=8192, description="Maximum tokens per request")
    temperature: float = Field(default=0.1, description="Temperature for generation")
    top_p: float = Field(default=0.8, description="Top-p sampling parameter")
    top_k: int = Field(default=40, description="Top-k sampling parameter")
    safety_settings: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError("Gemini API key is required")
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class AgentConfig(BaseModel):
    """Configuration for individual agents."""
    
    name: str
    description: str
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 300  # seconds
    prompt_template: str
    system_prompt: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowConfig(BaseModel):
    """Configuration for the workflow system."""
    
    max_concurrent_agents: int = Field(default=3, description="Maximum concurrent agents")
    enable_human_approval: bool = Field(default=True, description="Enable human approval workflow")
    approval_required_tasks: List[str] = Field(
        default=["architecture_design", "security_analysis", "deployment"],
        description="Tasks that require human approval"
    )
    auto_retry_failed_tasks: bool = Field(default=True, description="Automatically retry failed tasks")
    max_workflow_duration: int = Field(default=3600, description="Maximum workflow duration in seconds")
    save_intermediate_results: bool = Field(default=True, description="Save intermediate results")


class ContextConfig(BaseModel):
    """Configuration for the context engine."""
    
    enable_codebase_indexing: bool = Field(default=True, description="Enable codebase indexing")
    index_file_extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".md", ".txt"],
        description="File extensions to index"
    )
    exclude_patterns: List[str] = Field(
        default=["__pycache__", "node_modules", ".git", "venv", "env"],
        description="Patterns to exclude from indexing"
    )
    max_context_size: int = Field(default=10000, description="Maximum context size in tokens")
    max_file_size: int = Field(default=1024 * 1024, description="Maximum file size to index in bytes")
    enable_semantic_search: bool = Field(default=True, description="Enable semantic search")
    vector_db_path: str = Field(default="./context_db", description="Path to vector database")


class StorageConfig(BaseModel):
    """Configuration for storage and persistence."""
    
    output_dir: str = Field(default="./generated", description="Output directory for generated files")
    temp_dir: str = Field(default="./temp", description="Temporary directory")
    backup_dir: str = Field(default="./backups", description="Backup directory")
    max_backup_count: int = Field(default=10, description="Maximum number of backups to keep")
    enable_compression: bool = Field(default=True, description="Enable compression for backups")
    
    @validator('output_dir', 'temp_dir', 'backup_dir')
    def validate_directories(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="./logs/agent.log", description="Log file path")
    max_log_size: int = Field(default=10 * 1024 * 1024, description="Maximum log file size in bytes")
    backup_count: int = Field(default=5, description="Number of log backups to keep")
    enable_console_logging: bool = Field(default=True, description="Enable console logging")
    enable_file_logging: bool = Field(default=True, description="Enable file logging")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class SecurityConfig(BaseModel):
    """Configuration for security settings."""
    
    enable_security_scanning: bool = Field(default=True, description="Enable security scanning")
    security_rules_file: str = Field(default="./config/security_rules.yaml", description="Security rules file")
    enable_secrets_detection: bool = Field(default=True, description="Enable secrets detection")
    secrets_patterns: List[str] = Field(
        default=[r"api_key", r"password", r"secret", r"token"],
        description="Patterns for secrets detection"
    )
    enable_dependency_scanning: bool = Field(default=True, description="Enable dependency vulnerability scanning")


class UIConfig(BaseModel):
    """Configuration for the user interface."""
    
    enable_web_ui: bool = Field(default=True, description="Enable web UI")
    web_port: int = Field(default=8000, description="Web UI port")
    web_host: str = Field(default="localhost", description="Web UI host")
    enable_streamlit: bool = Field(default=True, description="Enable Streamlit dashboard")
    streamlit_port: int = Field(default=8501, description="Streamlit port")
    enable_websocket: bool = Field(default=True, description="Enable WebSocket for real-time updates")
    websocket_port: int = Field(default=8001, description="WebSocket port")


class SystemConfig(BaseModel):
    """Main system configuration."""
    
    project_name: str = Field(default="AI Development Agent", description="Project name")
    version: str = Field(default="1.0.0", description="System version")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Sub-configurations
    gemini: GeminiConfig
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    # Agent configurations
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v
    
    class Config:
        env_prefix = "AGENT_"


def load_config_from_env() -> SystemConfig:
    """Load configuration from environment variables and TOML files."""
    
    # Load API key with fallback logic
    api_key = _load_gemini_api_key()
    
    # Load Gemini config
    gemini_config = GeminiConfig(
        api_key=api_key,
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "8192")),
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.1")),
        top_p=float(os.getenv("GEMINI_TOP_P", "0.8")),
        top_k=int(os.getenv("GEMINI_TOP_K", "40"))
    )
    
    # Create system config
    config = SystemConfig(
        project_name=os.getenv("PROJECT_NAME", "AI Development Agent"),
        version=os.getenv("VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "development"),
        gemini=gemini_config
    )
    
    return config


def _load_gemini_api_key() -> str:
    """
    Load Gemini API key with fallback logic:
    1. Try to load from Streamlit secrets (highest priority)
    2. Try to load from secrets.toml
    3. Fallback to GEMINI_API_KEY environment variable
    4. Return empty string if not found
    
    Returns:
        API key string or empty string if not found
    """
    # Priority 1: Try to load from Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st.secrets, "GEMINI_API_KEY"):
            api_key = st.secrets.GEMINI_API_KEY
            if api_key and api_key != "your-gemini-api-key-here":
                return api_key
    except Exception:
        # Continue to next source if Streamlit secrets fail
        pass
    
    # Priority 2: Try to load from secrets.toml
    try:
        from utils.toml_config import load_gemini_api_key
        toml_api_key = load_gemini_api_key()
        if toml_api_key and toml_api_key != "your-gemini-api-key-here":
            return toml_api_key
    except Exception:
        # Continue to environment variable if TOML loading fails
        pass
    
    # Priority 3: Fallback to environment variable
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    if env_api_key:
        return env_api_key
    
    # Return empty string if no API key found
    return ""


def load_config_from_file(config_path: str) -> SystemConfig:
    """Load configuration from a YAML file."""
    
    import yaml
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return SystemConfig(**config_data)


def save_config_to_file(config: SystemConfig, config_path: str):
    """Save configuration to a YAML file."""
    
    import yaml
    
    # Create directory if it doesn't exist
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config.dict(), f, default_flow_style=False, indent=2)


def get_default_config() -> SystemConfig:
    """Get the default configuration."""
    
    gemini_config = GeminiConfig(
        api_key="your-api-key-here",
        model_name="gemini-2.5-flash-lite",
        max_tokens=8192,
        temperature=0.1,
        top_p=0.8,
        top_k=40
    )
    
    return SystemConfig(
        project_name="AI Development Agent",
        version="1.0.0",
        environment="development",
        gemini=gemini_config
    )
