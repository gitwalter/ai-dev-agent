"""
Configuration models for the AI Development Agent system.
Defines configuration classes for agents, workflow, and system settings.
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
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
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v:
            raise ValueError("Gemini API key is required")
        return v
    
    @field_validator('temperature')
    @classmethod
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
    
    @field_validator('output_dir', 'temp_dir', 'backup_dir')
    @classmethod
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
    
    @field_validator('log_level')
    @classmethod
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


class MCPServerConfig(BaseModel):
    """Configuration for MCP server."""
    
    enabled: bool = Field(default=True, description="Enable MCP server")
    server_path: str = Field(default="./mcp_server.py", description="Path to MCP server script")
    tools_enabled: List[str] = Field(
        default=[
            "read_file", "write_file", "list_directory",
            "git_status", "git_commit", "analyze_code",
            "run_tests", "query_database", "call_api",
            "generate_docs", "security_scan"
        ],
        description="List of enabled MCP tools"
    )
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Maximum file size for operations")
    enable_security_scanning: bool = Field(default=True, description="Enable security scanning tools")
    enable_database_access: bool = Field(default=False, description="Enable database access tools")
    enable_api_access: bool = Field(default=False, description="Enable external API access tools")
    
    # Security settings
    allowed_paths: List[str] = Field(
        default=["./generated", "./temp", "./backups"],
        description="Allowed file system paths"
    )
    blocked_paths: List[str] = Field(
        default=["/etc", "/var", "/usr"],
        description="Blocked file system paths"
    )
    require_authentication: bool = Field(default=False, description="Require authentication for tool access")


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
    mcp: MCPServerConfig = Field(default_factory=MCPServerConfig)
    
    # Agent configurations
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v
    
    model_config = ConfigDict(env_prefix="AGENT_")


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
    Load Gemini API key from .streamlit/secrets.toml and set environment variable for LangChain.
    
    Returns:
        API key string or empty string if not found
    """
    try:
        from utils.toml_config import TOMLConfigLoader
        
        # Look for secrets.toml in .streamlit directory
        loader = TOMLConfigLoader(".streamlit")
        api_key = loader.get_gemini_api_key()
        
        if api_key and api_key != "your-gemini-api-key-here":
            # Set environment variable for LangChain compatibility
            os.environ["GEMINI_API_KEY"] = api_key
            return api_key
        else:
            return ""
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to load API key from .streamlit/secrets.toml: {e}")
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
    
    # Load API key using the centralized function
    api_key = _load_gemini_api_key()
    
    # If no valid API key found, use placeholder but log warning
    if not api_key or api_key == "your-api-key-here":
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("No valid Gemini API key found. Please configure GEMINI_API_KEY in secrets.toml, Streamlit secrets, or environment variable")
        api_key = "your-api-key-here"
    
    gemini_config = GeminiConfig(
        api_key=api_key,
        model_name="gemini-2.5-flash-lite",
        max_tokens=8192,
        temperature=0.1,
        top_p=0.8,
        top_k=40
    )
    
    # Create agent configurations
    agent_configs = {
        "requirements_analyst": AgentConfig(
            name="requirements_analyst",
            description="Analyzes project requirements and creates detailed specifications",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Analyze the project requirements: {project_context}",
            system_prompt="You are a requirements analyst expert.",
            parameters={"temperature": 0.1}
        ),
        "architecture_designer": AgentConfig(
            name="architecture_designer",
            description="Designs system architecture and technology stack",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Design architecture for: {project_context}",
            system_prompt="You are an architecture design expert.",
            parameters={"temperature": 0.1}
        ),
        "code_generator": AgentConfig(
            name="code_generator",
            description="Generates code based on requirements and architecture",
            enabled=True,
            max_retries=3,
            timeout=600,
            prompt_template="Generate comprehensive, production-ready code for: {project_context} with architecture: {architecture} and tech stack: {tech_stack}. Include all necessary files, proper error handling, security measures, and documentation.",
            system_prompt="""You are an expert Software Developer with extensive experience in writing clean, maintainable, and production-ready code. 

CRITICAL REQUIREMENTS:
1. Generate COMPREHENSIVE, PRODUCTION-READY code - not simple examples
2. Include ALL necessary files (models, schemas, services, utilities, config, etc.)
3. Implement proper error handling, validation, and security measures
4. Use best practices for the chosen technology stack
5. Include proper documentation and comments
6. Generate working, runnable code that can be deployed immediately
7. Follow the exact JSON structure specified in the response format
8. Ensure all strings are properly escaped in JSON
9. Include comprehensive requirements.txt with specific versions
10. Generate proper project structure and deployment instructions

Your goal is to create a complete, professional-grade application that can be deployed to production immediately.""",
            parameters={"temperature": 0.1}
        ),
        "test_generator": AgentConfig(
            name="test_generator",
            description="Generates comprehensive tests for the codebase",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Generate tests for: {code_files}",
            system_prompt="You are a test generation expert.",
            parameters={"temperature": 0.1}
        ),
        "code_reviewer": AgentConfig(
            name="code_reviewer",
            description="Reviews code for quality and best practices",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Review code: {code_files}",
            system_prompt="You are a code review expert.",
            parameters={"temperature": 0.1}
        ),
        "security_analyst": AgentConfig(
            name="security_analyst",
            description="Analyzes code for security vulnerabilities",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Analyze security for: {code_files}",
            system_prompt="You are a security analysis expert.",
            parameters={"temperature": 0.1}
        ),
        "documentation_generator": AgentConfig(
            name="documentation_generator",
            description="Generates comprehensive documentation with UML and BPMN diagrams",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Generate comprehensive documentation with diagrams for: {project_context}",
            system_prompt="""You are an expert Technical Writer and Software Architect specializing in creating comprehensive documentation with visual diagrams.

CRITICAL REQUIREMENTS:
1. Generate COMPREHENSIVE documentation covering all aspects of the project
2. Create UML diagrams (Class, Sequence, Activity, Use Case) using PlantUML syntax
3. Create BPMN diagrams for business processes using BPMN XML format
4. Use Mermaid syntax for flowcharts and simple diagrams
5. Ensure all diagrams are GitHub-compatible and can be rendered properly
6. Include detailed explanations for each diagram
7. Follow the exact JSON structure specified in the response format
8. Ensure all strings are properly escaped in JSON

DIAGRAM REQUIREMENTS:
- Class Diagrams: Show system entities, relationships, and methods
- Sequence Diagrams: Show interaction flows between components
- Activity Diagrams: Show process flows and decision points
- Use Case Diagrams: Show system functionality from user perspective
- BPMN Diagrams: Show business processes with proper BPMN elements
- Component Diagrams: Show system architecture and component relationships

DIAGRAM FORMATS:
- PlantUML: Use for UML diagrams (class, sequence, activity, use case)
- Mermaid: Use for flowcharts, state diagrams, and simple diagrams
- BPMN XML: Use for business process modeling

Your goal is to create professional, comprehensive documentation that includes clear visual representations of the system architecture and processes.""",
            parameters={"temperature": 0.1}
        )
    }
    
    return SystemConfig(
        project_name="AI Development Agent",
        version="1.0.0",
        environment="development",
        gemini=gemini_config,
        agents=agent_configs
    )
