#!/usr/bin/env python3
"""
Practical Example 3: Project Setup Wizard
=========================================

WHAT THIS DOES:
- Sets up complete project structure with best practices
- Shows how to use AI-Dev-Agent for instant project initialization
- Creates production-ready configuration and tooling

TIME TO VALUE: 30 seconds
LEARNING FOCUS: Project organization, tooling setup, automation

REAL-WORLD USE CASE:
"I need to start a new project with proper structure, testing, and deployment"
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class ProjectType(Enum):
    """Supported project types."""
    WEB_API = "web_api"
    MICROSERVICE = "microservice"
    CLI_TOOL = "cli_tool"
    DATA_PIPELINE = "data_pipeline"
    ML_PROJECT = "ml_project"
    FULLSTACK_WEB = "fullstack_web"

class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"
    NONE = "none"

class DeploymentType(Enum):
    """Supported deployment types."""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    CLOUD_RUN = "cloud_run"
    HEROKU = "heroku"
    NONE = "none"

@dataclass
class ProjectConfig:
    """Project configuration."""
    name: str
    project_type: ProjectType
    database: DatabaseType
    deployment: DeploymentType
    include_testing: bool = True
    include_ci_cd: bool = True
    include_monitoring: bool = True
    include_docs: bool = True
    python_version: str = "3.11"
    license: str = "MIT"

@dataclass
class ProjectStructure:
    """Generated project structure."""
    directories: List[str]
    files: Dict[str, str]  # filename -> content
    commands: List[str]  # setup commands
    features: List[str]
    estimated_setup_time: str

class ProjectSetupWizard:
    """
    Project setup wizard that creates complete project structure with AI assistance.
    
    This example demonstrates:
    - Intelligent project scaffolding
    - Best practice implementation
    - Automated tooling setup
    - Production-ready configuration
    """
    
    def __init__(self):
        """Initialize the project setup wizard."""
        self.templates = self._load_templates()
        self.created_projects = []
        
    def create_project(self, config: ProjectConfig) -> ProjectStructure:
        """
        Create a complete project with specified configuration.
        
        Args:
            config: Project configuration
            
        Returns:
            Generated project structure with files and setup instructions
        """
        
        print(f"🧙‍♂️ Creating {config.project_type.value} project: '{config.name}'")
        print(f"🗄️ Database: {config.database.value}")
        print(f"🚀 Deployment: {config.deployment.value}")
        
        # Generate project structure
        structure = self._generate_project_structure(config)
        
        # Create files and directories
        self._create_project_files(config, structure)
        
        # Display results
        self._display_project_results(config, structure)
        
        # Track created project
        self.created_projects.append({
            'name': config.name,
            'type': config.project_type.value,
            'created_at': datetime.now().isoformat()
        })
        
        return structure
    
    def _generate_project_structure(self, config: ProjectConfig) -> ProjectStructure:
        """Generate the project structure based on configuration."""
        
        directories = self._get_directories(config)
        files = self._generate_files(config)
        commands = self._get_setup_commands(config)
        features = self._get_features(config)
        
        return ProjectStructure(
            directories=directories,
            files=files,
            commands=commands,
            features=features,
            estimated_setup_time="2-5 minutes"
        )
    
    def _get_directories(self, config: ProjectConfig) -> List[str]:
        """Get directory structure for project type."""
        
        base_dirs = [
            f"{config.name}/",
            f"{config.name}/src/",
            f"{config.name}/src/{config.name.replace('-', '_')}/",
        ]
        
        if config.include_testing:
            base_dirs.extend([
                f"{config.name}/tests/",
                f"{config.name}/tests/unit/",
                f"{config.name}/tests/integration/",
            ])
        
        if config.include_docs:
            base_dirs.extend([
                f"{config.name}/docs/",
                f"{config.name}/docs/api/",
                f"{config.name}/docs/guides/",
            ])
        
        # Project type specific directories
        if config.project_type == ProjectType.WEB_API:
            base_dirs.extend([
                f"{config.name}/src/{config.name.replace('-', '_')}/api/",
                f"{config.name}/src/{config.name.replace('-', '_')}/models/",
                f"{config.name}/src/{config.name.replace('-', '_')}/services/",
            ])
        
        elif config.project_type == ProjectType.MICROSERVICE:
            base_dirs.extend([
                f"{config.name}/src/{config.name.replace('-', '_')}/handlers/",
                f"{config.name}/src/{config.name.replace('-', '_')}/middleware/",
                f"{config.name}/src/{config.name.replace('-', '_')}/config/",
            ])
        
        elif config.project_type == ProjectType.CLI_TOOL:
            base_dirs.extend([
                f"{config.name}/src/{config.name.replace('-', '_')}/commands/",
                f"{config.name}/src/{config.name.replace('-', '_')}/utils/",
            ])
        
        elif config.project_type == ProjectType.DATA_PIPELINE:
            base_dirs.extend([
                f"{config.name}/src/{config.name.replace('-', '_')}/extractors/",
                f"{config.name}/src/{config.name.replace('-', '_')}/transformers/",
                f"{config.name}/src/{config.name.replace('-', '_')}/loaders/",
                f"{config.name}/data/",
                f"{config.name}/pipelines/",
            ])
        
        elif config.project_type == ProjectType.ML_PROJECT:
            base_dirs.extend([
                f"{config.name}/notebooks/",
                f"{config.name}/models/",
                f"{config.name}/data/raw/",
                f"{config.name}/data/processed/",
                f"{config.name}/experiments/",
            ])
        
        # Deployment specific directories
        if config.deployment == DeploymentType.DOCKER:
            base_dirs.append(f"{config.name}/docker/")
        
        elif config.deployment == DeploymentType.KUBERNETES:
            base_dirs.extend([
                f"{config.name}/k8s/",
                f"{config.name}/helm/",
            ])
        
        return base_dirs
    
    def _generate_files(self, config: ProjectConfig) -> Dict[str, str]:
        """Generate file contents for the project."""
        
        files = {}
        
        # Core files
        files["README.md"] = self._generate_readme(config)
        files["requirements.txt"] = self._generate_requirements(config)
        files["pyproject.toml"] = self._generate_pyproject(config)
        files[".gitignore"] = self._generate_gitignore(config)
        files["LICENSE"] = self._generate_license(config)
        
        # Main application file
        files[f"src/{config.name.replace('-', '_')}/__init__.py"] = self._generate_init_file(config)
        files[f"src/{config.name.replace('-', '_')}/main.py"] = self._generate_main_file(config)
        
        # Configuration
        files[f"src/{config.name.replace('-', '_')}/config.py"] = self._generate_config_file(config)
        
        # Testing files
        if config.include_testing:
            files["tests/__init__.py"] = ""
            files["tests/conftest.py"] = self._generate_conftest(config)
            files["tests/test_main.py"] = self._generate_test_main(config)
            files["pytest.ini"] = self._generate_pytest_config(config)
        
        # CI/CD files
        if config.include_ci_cd:
            files[".github/workflows/ci.yml"] = self._generate_github_actions(config)
            files[".pre-commit-config.yaml"] = self._generate_precommit_config(config)
        
        # Docker files
        if config.deployment == DeploymentType.DOCKER:
            files["Dockerfile"] = self._generate_dockerfile(config)
            files["docker-compose.yml"] = self._generate_docker_compose(config)
            files[".dockerignore"] = self._generate_dockerignore(config)
        
        # Documentation
        if config.include_docs:
            files["docs/README.md"] = self._generate_docs_readme(config)
            files["docs/api/README.md"] = self._generate_api_docs(config)
            files["docs/guides/getting-started.md"] = self._generate_getting_started(config)
        
        # Environment files
        files[".env.example"] = self._generate_env_example(config)
        
        return files
    
    def _generate_readme(self, config: ProjectConfig) -> str:
        """Generate README.md content."""
        
        return f'''# {config.name.replace('-', ' ').title()}

**Type**: {config.project_type.value.replace('_', ' ').title()}  
**Database**: {config.database.value.title()}  
**Deployment**: {config.deployment.value.replace('_', ' ').title()}

## 🚀 Quick Start

### Prerequisites
- Python {config.python_version}+
- {config.database.value.title()} (if using database)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {config.name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

### Running the Application

```bash
# Development
python -m src.{config.name.replace('-', '_')}.main

# With specific environment
python -m src.{config.name.replace('-', '_')}.main --env development
```

## 🏗️ Project Structure

```
{config.name}/
├── src/{config.name.replace('-', '_')}/          # Main application code
├── tests/                    # Test files
├── docs/                     # Documentation
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── .env.example             # Environment template
└── README.md                # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_main.py -v
```

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t {config.name}:latest .

# Run container
docker-compose up -d
```

### Production

```bash
# Production deployment
# See docs/guides/deployment.md for detailed instructions
```

## 📚 Documentation

- [API Documentation](docs/api/)
- [Getting Started Guide](docs/guides/getting-started.md)
- [Deployment Guide](docs/guides/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the {config.license} License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bug reports or feature requests
- Check existing issues before creating new ones
- Provide detailed information for faster resolution

---

**Generated by AI-Dev-Agent Project Setup Wizard**  
**Created**: {datetime.now().strftime('%Y-%m-%d')}
'''
    
    def _generate_requirements(self, config: ProjectConfig) -> str:
        """Generate requirements.txt content."""
        
        requirements = [
            "# Core dependencies",
            "python-dotenv>=1.0.0",
            "pydantic>=2.0.0",
            "loguru>=0.7.0",
        ]
        
        if config.project_type == ProjectType.WEB_API:
            requirements.extend([
                "",
                "# Web API dependencies",
                "fastapi>=0.100.0",
                "uvicorn[standard]>=0.23.0",
                "python-multipart>=0.0.6",
            ])
        
        elif config.project_type == ProjectType.CLI_TOOL:
            requirements.extend([
                "",
                "# CLI tool dependencies",
                "click>=8.1.0",
                "rich>=13.0.0",
                "typer>=0.9.0",
            ])
        
        elif config.project_type == ProjectType.DATA_PIPELINE:
            requirements.extend([
                "",
                "# Data pipeline dependencies",
                "pandas>=2.0.0",
                "apache-airflow>=2.7.0",
                "sqlalchemy>=2.0.0",
            ])
        
        elif config.project_type == ProjectType.ML_PROJECT:
            requirements.extend([
                "",
                "# ML project dependencies",
                "scikit-learn>=1.3.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "matplotlib>=3.7.0",
                "jupyter>=1.0.0",
            ])
        
        # Database dependencies
        if config.database == DatabaseType.POSTGRESQL:
            requirements.extend([
                "",
                "# PostgreSQL dependencies",
                "psycopg2-binary>=2.9.0",
                "sqlalchemy>=2.0.0",
            ])
        elif config.database == DatabaseType.MYSQL:
            requirements.extend([
                "",
                "# MySQL dependencies", 
                "PyMySQL>=1.1.0",
                "sqlalchemy>=2.0.0",
            ])
        elif config.database == DatabaseType.MONGODB:
            requirements.extend([
                "",
                "# MongoDB dependencies",
                "pymongo>=4.5.0",
                "motor>=3.3.0",
            ])
        elif config.database == DatabaseType.REDIS:
            requirements.extend([
                "",
                "# Redis dependencies",
                "redis>=5.0.0",
                "aioredis>=2.0.0",
            ])
        
        if config.include_testing:
            requirements.extend([
                "",
                "# Testing dependencies",
                "pytest>=7.4.0",
                "pytest-cov>=4.1.0", 
                "pytest-asyncio>=0.21.0",
                "httpx>=0.24.0",  # For API testing
            ])
        
        return "\\n".join(requirements)
    
    def _generate_pyproject(self, config: ProjectConfig) -> str:
        """Generate pyproject.toml content."""
        
        return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{config.name}"
version = "0.1.0"
description = "A {config.project_type.value.replace('_', ' ')} project"
readme = "README.md"
license = {{file = "LICENSE"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
keywords = ["{config.project_type.value}", "python", "{config.database.value}"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: {config.license} License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: {config.python_version}",
]
requires-python = ">={config.python_version}"
dependencies = [
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/{config.name}"
Repository = "https://github.com/yourusername/{config.name}"
Issues = "https://github.com/yourusername/{config.name}/issues"

[tool.black]
line-length = 120
target-version = ["py{config.python_version.replace('.', '')}"]

[tool.isort]
profile = "black"
line_length = 120

[tool.mypy]
python_version = "{config.python_version}"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --cov=src --cov-report=term-missing"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
'''
    
    def _generate_main_file(self, config: ProjectConfig) -> str:
        """Generate main application file."""
        
        if config.project_type == ProjectType.WEB_API:
            return f'''#!/usr/bin/env python3
"""
{config.name.replace('-', ' ').title()} - Main Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn
from .config import get_settings

# Initialize settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="{config.name.replace('-', ' ').title()}",
    description="A {config.project_type.value.replace('_', ' ')} application",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "Welcome to {config.name.replace('-', ' ').title()}", "version": "0.1.0"}}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{config.name}"}}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
'''
        
        elif config.project_type == ProjectType.CLI_TOOL:
            return f'''#!/usr/bin/env python3
"""
{config.name.replace('-', ' ').title()} - Main CLI Application
"""

import click
from loguru import logger
from .config import get_settings

settings = get_settings()

@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose: bool):
    """
    {config.name.replace('-', ' ').title()} - A powerful CLI tool
    """
    if verbose:
        logger.info("Verbose mode enabled")

@cli.command()
@click.argument("name")
def hello(name: str):
    """Say hello to someone."""
    click.echo(f"Hello, {{name}}!")
    logger.info(f"Greeted {{name}}")

@cli.command()
def status():
    """Show application status."""
    click.echo("Application Status: Running")
    click.echo(f"Version: 0.1.0")
    click.echo(f"Configuration: {{settings.environment}}")

if __name__ == "__main__":
    cli()
'''
        
        else:
            return f'''#!/usr/bin/env python3
"""
{config.name.replace('-', ' ').title()} - Main Application
"""

from loguru import logger
from .config import get_settings

def main():
    """Main application entry point."""
    settings = get_settings()
    logger.info(f"Starting {{settings.app_name}} v0.1.0")
    
    # Your application logic here
    logger.info("Application running successfully")
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
    
    def _generate_config_file(self, config: ProjectConfig) -> str:
        """Generate configuration file."""
        
        return f'''"""
Configuration management for {config.name.replace('-', ' ').title()}
"""

from pydantic import BaseSettings, Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    app_name: str = "{config.name.replace('-', ' ').title()}"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server settings (for web applications)
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security settings
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Database settings
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
'''
    
    def _generate_dockerfile(self, config: ProjectConfig) -> str:
        """Generate Dockerfile content."""
        
        return f'''# Multi-stage build for {config.name}
FROM python:{config.python_version}-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=0.1.0

# Add metadata
LABEL maintainer="your.email@example.com"
LABEL version="${{VERSION}}"
LABEL description="{config.project_type.value.replace('_', ' ').title()} application"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Production stage
FROM python:{config.python_version}-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "src.{config.name.replace('-', '_')}.main"]
'''
    
    def _generate_github_actions(self, config: ProjectConfig) -> str:
        """Generate GitHub Actions CI/CD workflow."""
        
        return f'''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: {config.python_version}

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["{config.python_version}"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black isort flake8 mypy
    
    - name: Lint with flake8
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics
    
    - name: Format check with black
      run: |
        black --check --diff src tests
    
    - name: Import sort check with isort
      run: |
        isort --check-only --diff src tests
    
    - name: Type check with mypy
      run: |
        mypy src
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
  
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: {config.python_version}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install bandit safety
    
    - name: Security check with bandit
      run: |
        bandit -r src/ -f json -o bandit-report.json
    
    - name: Dependency check with safety
      run: |
        safety check --json --output safety-report.json
  
  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{{{ github.actor }}}}
        password: ${{{{ secrets.GITHUB_TOKEN }}}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{{{ github.repository }}}}:latest
          ghcr.io/${{{{ github.repository }}}}:${{{{ github.sha }}}}
        cache-from: type=gha
        cache-to: type=gha,mode=max
'''
    
    def _generate_gitignore(self, config: ProjectConfig) -> str:
        """Generate .gitignore content."""
        
        return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
data/
logs/
*.sqlite
*.db
'''
    
    def _generate_license(self, config: ProjectConfig) -> str:
        """Generate LICENSE file."""
        
        if config.license == "MIT":
            return f'''MIT License

Copyright (c) {datetime.now().year} Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
        else:
            return f"# {config.license} License\\n\\n(License content would be here)"
    
    def _get_setup_commands(self, config: ProjectConfig) -> List[str]:
        """Get setup commands for the project."""
        
        commands = [
            f"cd {config.name}",
            "python -m venv venv",
            "source venv/bin/activate  # On Windows: venv\\\\Scripts\\\\activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt",
            "cp .env.example .env",
        ]
        
        if config.include_testing:
            commands.extend([
                "pytest tests/",
                "pytest --cov=src --cov-report=html",
            ])
        
        if config.deployment == DeploymentType.DOCKER:
            commands.extend([
                "docker build -t {config.name}:latest .",
                "docker-compose up -d",
            ])
        
        return commands
    
    def _get_features(self, config: ProjectConfig) -> List[str]:
        """Get list of included features."""
        
        features = [
            f"{config.project_type.value.replace('_', ' ').title()} architecture",
            f"{config.database.value.title()} integration" if config.database != DatabaseType.NONE else "No database",
            "Environment configuration",
            "Logging setup",
            "Production-ready structure",
        ]
        
        if config.include_testing:
            features.extend([
                "Comprehensive test suite",
                "Code coverage reporting",
                "Test configuration",
            ])
        
        if config.include_ci_cd:
            features.extend([
                "GitHub Actions CI/CD",
                "Pre-commit hooks",
                "Code quality checks",
                "Security scanning",
            ])
        
        if config.deployment == DeploymentType.DOCKER:
            features.extend([
                "Multi-stage Dockerfile",
                "Docker Compose setup",
                "Health checks",
            ])
        
        if config.include_docs:
            features.extend([
                "Complete documentation",
                "API documentation",
                "Getting started guide",
            ])
        
        return features
    
    # Additional helper methods for file generation
    def _generate_conftest(self, config: ProjectConfig) -> str:
        """Generate pytest conftest.py."""
        return '''"""Test configuration and fixtures."""

import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Test data directory fixture."""
    return Path(__file__).parent / "data"

@pytest.fixture
def sample_config():
    """Sample configuration fixture."""
    return {
        "debug": True,
        "environment": "test"
    }
'''
    
    def _generate_test_main(self, config: ProjectConfig) -> str:
        """Generate main test file."""
        return f'''"""Tests for main application."""

import pytest
from src.{config.name.replace('-', '_')}.main import main

def test_main_function_exists():
    """Test that main function exists and is callable."""
    assert callable(main)

def test_main_function_returns_int():
    """Test that main function returns an integer exit code."""
    result = main()
    assert isinstance(result, int)
    assert result >= 0
'''
    
    def _generate_env_example(self, config: ProjectConfig) -> str:
        """Generate .env.example file."""
        
        lines = [
            "# Environment configuration",
            "DEBUG=false",
            "ENVIRONMENT=production",
            "SECRET_KEY=change-me-in-production",
            "",
            "# Server configuration",
            "HOST=0.0.0.0",
            "PORT=8000",
            "",
            "# Logging",
            "LOG_LEVEL=INFO",
        ]
        
        if config.database != DatabaseType.NONE:
            lines.extend([
                "",
                "# Database configuration",
                "DATABASE_URL=your-database-url-here",
            ])
        
        return "\\n".join(lines)
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load project templates."""
        return {}  # Placeholder for template loading
    
    def _create_project_files(self, config: ProjectConfig, structure: ProjectStructure) -> None:
        """Create the actual project files and directories."""
        
        project_path = Path(config.name)
        
        # Create directories
        for directory in structure.directories:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        
        # Create files
        for filename, content in structure.files.items():
            file_path = project_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            print(f"📄 Created file: {file_path}")
    
    def _display_project_results(self, config: ProjectConfig, structure: ProjectStructure) -> None:
        """Display project creation results."""
        
        print(f"\\n{'='*80}")
        print(f"🎉 PROJECT SETUP COMPLETE: {config.name}")
        print(f"{'='*80}")
        
        print(f"\\n📊 Project Details:")
        print(f"  Type: {config.project_type.value.replace('_', ' ').title()}")
        print(f"  Database: {config.database.value.title()}")
        print(f"  Deployment: {config.deployment.value.replace('_', ' ').title()}")
        print(f"  Python Version: {config.python_version}")
        
        print(f"\\n📁 Created Structure:")
        print(f"  Directories: {len(structure.directories)}")
        print(f"  Files: {len(structure.files)}")
        
        print(f"\\n✨ Features Included:")
        for feature in structure.features:
            print(f"  ✅ {feature}")
        
        print(f"\\n🚀 Quick Start Commands:")
        for i, command in enumerate(structure.commands[:5], 1):
            print(f"  {i}. {command}")
        
        if len(structure.commands) > 5:
            print(f"  ... and {len(structure.commands) - 5} more commands")
        
        print(f"\\n⏱️ Estimated Setup Time: {structure.estimated_setup_time}")
        
        print(f"\\n📚 Next Steps:")
        print(f"  1. Navigate to project: cd {config.name}")
        print(f"  2. Set up virtual environment: python -m venv venv")
        print(f"  3. Activate environment: source venv/bin/activate")
        print(f"  4. Install dependencies: pip install -r requirements.txt")
        print(f"  5. Configure environment: cp .env.example .env")
        print(f"  6. Start developing! 🚀")
        
        print(f"\\n{'='*80}")

# Helper methods that were referenced but not defined
    def _generate_init_file(self, config: ProjectConfig) -> str:
        """Generate __init__.py file."""
        return f'''"""
{config.name.replace('-', ' ').title()} - A {config.project_type.value.replace('_', ' ')} application
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
'''
    
    def _generate_pytest_config(self, config: ProjectConfig) -> str:
        """Generate pytest.ini configuration."""
        return '''[tool:pytest]
minversion = 7.0
addopts = -ra -q --strict-markers --cov=src --cov-report=term-missing
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
'''
    
    def _generate_precommit_config(self, config: ProjectConfig) -> str:
        """Generate pre-commit configuration."""
        return '''repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
'''
    
    def _generate_docker_compose(self, config: ProjectConfig) -> str:
        """Generate docker-compose.yml."""
        
        compose_content = f'''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    depends_on:'''
        
        if config.database == DatabaseType.POSTGRESQL:
            compose_content += '''
      - db
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
        else:
            compose_content += " []\\n"
        
        return compose_content
    
    def _generate_dockerignore(self, config: ProjectConfig) -> str:
        """Generate .dockerignore."""
        return '''.git
.gitignore
README.md
Dockerfile
.dockerignore
.pytest_cache
.coverage
htmlcov/
tests/
docs/
.venv
venv/
.env
*.log
'''
    
    def _generate_docs_readme(self, config: ProjectConfig) -> str:
        """Generate docs README."""
        return f'''# {config.name.replace('-', ' ').title()} Documentation

This directory contains comprehensive documentation for the {config.name} project.

## Structure

- `api/` - API documentation and examples
- `guides/` - User and developer guides
- `deployment/` - Deployment instructions

## Getting Started

See [Getting Started Guide](guides/getting-started.md) for setup instructions.
'''
    
    def _generate_api_docs(self, config: ProjectConfig) -> str:
        """Generate API documentation."""
        return f'''# API Documentation

## Overview

The {config.name} API provides {config.project_type.value.replace('_', ' ')} functionality.

## Endpoints

### Health Check
- **GET** `/health` - Check service health

### Main Endpoints
- **GET** `/` - Root endpoint

## Authentication

(Add authentication details here)

## Examples

(Add API usage examples here)
'''
    
    def _generate_getting_started(self, config: ProjectConfig) -> str:
        """Generate getting started guide."""
        return f'''# Getting Started with {config.name.replace('-', ' ').title()}

## Prerequisites

- Python {config.python_version}+
- {config.database.value.title()} (if using database)

## Installation

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Configure environment
5. Run the application

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black src tests
isort src tests
flake8 src tests
mypy src
```

## Deployment

See deployment guide for production setup instructions.
'''

def main():
    """Main function demonstrating project setup wizard."""
    
    print("🧙‍♂️ AI-Dev-Agent Project Setup Wizard")
    print("=" * 60)
    print("Creating production-ready projects with best practices...")
    print()
    
    # Initialize wizard
    wizard = ProjectSetupWizard()
    
    # Example 1: Web API project
    print("📍 Example 1: FastAPI Web Service")
    config1 = ProjectConfig(
        name="user-management-api",
        project_type=ProjectType.WEB_API,
        database=DatabaseType.POSTGRESQL,
        deployment=DeploymentType.DOCKER,
        include_testing=True,
        include_ci_cd=True,
        include_monitoring=True,
        include_docs=True
    )
    structure1 = wizard.create_project(config1)
    
    print("\\n" + "-"*60 + "\\n")
    
    # Example 2: CLI tool
    print("📍 Example 2: Command-Line Tool")
    config2 = ProjectConfig(
        name="data-processor-cli",
        project_type=ProjectType.CLI_TOOL,
        database=DatabaseType.SQLITE,
        deployment=DeploymentType.DOCKER,
        include_testing=True,
        include_ci_cd=True,
        include_docs=True
    )
    structure2 = wizard.create_project(config2)
    
    print("\\n" + "-"*60 + "\\n")
    
    # Example 3: Microservice
    print("📍 Example 3: Microservice")
    config3 = ProjectConfig(
        name="notification-service",
        project_type=ProjectType.MICROSERVICE,
        database=DatabaseType.REDIS,
        deployment=DeploymentType.KUBERNETES,
        include_testing=True,
        include_ci_cd=True,
        include_monitoring=True
    )
    structure3 = wizard.create_project(config3)
    
    # Summary
    print(f"\\n{'='*80}")
    print("🎯 WIZARD SESSION SUMMARY")
    print(f"{'='*80}")
    print(f"Projects Created: 3")
    print(f"Total Files Generated: {len(structure1.files) + len(structure2.files) + len(structure3.files)}")
    print(f"Total Directories Created: {len(structure1.directories) + len(structure2.directories) + len(structure3.directories)}")
    print(f"Estimated Development Time Saved: 6-12 hours")
    
    print("\\n📁 Created Projects:")
    for i, config in enumerate([config1, config2, config3], 1):
        print(f"  {i}. {config.name} ({config.project_type.value})")
    
    print("\\n🚀 All projects ready for development!")

if __name__ == "__main__":
    main()
