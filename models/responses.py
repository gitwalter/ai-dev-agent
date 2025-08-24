"""
Response models for the AI Development Agent system.
Defines response structures for API endpoints and agent communications.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkflowStatus(str, Enum):
    """Status of the overall workflow."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class AgentResponse(BaseModel):
    """Response from an individual agent."""
    
    agent_name: str
    task_name: str
    status: TaskStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    # Enhanced documentation and logging
    documentation: Dict[str, Any] = Field(default_factory=dict, description="Detailed documentation of the agent's work")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed execution logs")
    decisions: List[Dict[str, Any]] = Field(default_factory=list, description="Key decisions made during execution")
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="Artifacts created during execution")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkflowResult(BaseModel):
    """Result of a complete workflow execution."""
    
    workflow_id: str
    session_id: str
    status: WorkflowStatus
    project_name: str
    project_context: str
    
    # Results from each agent
    agent_results: Dict[str, AgentResponse] = Field(default_factory=dict)
    
    # Generated artifacts
    generated_files: Dict[str, str] = Field(default_factory=dict)
    code_files: Dict[str, str] = Field(default_factory=dict)
    test_files: Dict[str, str] = Field(default_factory=dict)
    documentation_files: Dict[str, str] = Field(default_factory=dict)
    configuration_files: Dict[str, str] = Field(default_factory=dict)
    
    # Workflow metadata
    total_execution_time: float = 0.0
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    human_approvals: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RequirementsAnalysisResponse(BaseModel):
    """Response from the requirements analysis agent."""
    
    functional_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[Dict[str, Any]]
    user_stories: List[Dict[str, Any]]
    acceptance_criteria: List[Dict[str, Any]]
    technical_constraints: List[str]
    assumptions: List[str]
    risks: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "functional_requirements": [
                    {
                        "id": "FR-001",
                        "title": "User Authentication",
                        "description": "System must support user login and registration",
                        "priority": "high",
                        "complexity": "medium"
                    }
                ],
                "non_functional_requirements": [
                    {
                        "id": "NFR-001",
                        "title": "Performance",
                        "description": "API response time must be under 200ms",
                        "metric": "response_time",
                        "target": "200ms"
                    }
                ],
                "user_stories": [
                    {
                        "id": "US-001",
                        "as_a": "user",
                        "i_want": "to register an account",
                        "so_that": "I can access the system",
                        "acceptance_criteria": ["Email validation", "Password requirements"]
                    }
                ],
                "acceptance_criteria": [
                    {
                        "id": "AC-001",
                        "requirement_id": "FR-001",
                        "description": "User can register with valid email and password",
                        "test_scenarios": ["Valid registration", "Invalid email", "Weak password"]
                    }
                ],
                "technical_constraints": ["Python 3.8+", "PostgreSQL database", "REST API"],
                "assumptions": ["Users have email addresses", "Internet connectivity required"],
                "risks": [
                    {
                        "id": "RISK-001",
                        "description": "Third-party API dependencies",
                        "impact": "high",
                        "probability": "medium",
                        "mitigation": "Implement fallback mechanisms"
                    }
                ]
            }
        }


class ArchitectureDesignResponse(BaseModel):
    """Response from the architecture design agent."""
    
    system_architecture: Dict[str, Any]
    component_breakdown: List[Dict[str, Any]]
    technology_stack: Dict[str, List[str]]
    design_patterns: List[Dict[str, Any]]
    database_schema: Dict[str, Any]
    api_design: Dict[str, Any]
    security_considerations: List[str]
    scalability_plan: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "system_architecture": {
                    "type": "layered",
                    "layers": ["presentation", "business", "data"],
                    "diagram": "architecture_diagram.png"
                },
                "component_breakdown": [
                    {
                        "name": "User Management Service",
                        "responsibility": "Handle user authentication and authorization",
                        "dependencies": ["Database", "Email Service"],
                        "interfaces": ["REST API", "Internal API"]
                    }
                ],
                "technology_stack": {
                    "backend": ["Python", "FastAPI", "SQLAlchemy"],
                    "database": ["PostgreSQL"],
                    "frontend": ["React", "TypeScript"],
                    "deployment": ["Docker", "Kubernetes"]
                },
                "design_patterns": [
                    {
                        "name": "Repository Pattern",
                        "description": "Abstract data access layer",
                        "implementation": "UserRepository class"
                    }
                ],
                "database_schema": {
                    "tables": [
                        {
                            "name": "users",
                            "columns": [
                                {"name": "id", "type": "UUID", "primary_key": True},
                                {"name": "email", "type": "VARCHAR(255)", "unique": True},
                                {"name": "password_hash", "type": "VARCHAR(255)"}
                            ]
                        }
                    ]
                },
                "api_design": {
                    "base_url": "/api/v1",
                    "endpoints": [
                        {
                            "path": "/users",
                            "method": "POST",
                            "description": "Create new user",
                            "request_body": {"email": "string", "password": "string"},
                            "response": {"user_id": "UUID", "email": "string"}
                        }
                    ]
                },
                "security_considerations": [
                    "JWT token authentication",
                    "Password hashing with bcrypt",
                    "Input validation and sanitization",
                    "Rate limiting"
                ],
                "scalability_plan": {
                    "horizontal_scaling": "Load balancer with multiple instances",
                    "database_scaling": "Read replicas and connection pooling",
                    "caching": "Redis for session storage"
                }
            }
        }


class CodeGenerationResponse(BaseModel):
    """Response from the code generation agent."""
    
    project_structure: Dict[str, Any]
    generated_files: Dict[str, str]
    dependencies: Dict[str, List[str]]
    build_configuration: Dict[str, Any]
    deployment_configuration: Dict[str, Any]
    code_quality_metrics: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "project_structure": {
                    "src/": {
                        "api/": ["routes.py", "models.py", "schemas.py"],
                        "core/": ["config.py", "database.py", "security.py"],
                        "services/": ["user_service.py", "auth_service.py"]
                    },
                    "tests/": ["test_api.py", "test_services.py"],
                    "docs/": ["README.md", "API.md"],
                    "config/": ["requirements.txt", "Dockerfile"]
                },
                "generated_files": {
                    "src/api/routes.py": "# Generated API routes...",
                    "src/core/config.py": "# Generated configuration...",
                    "requirements.txt": "fastapi==0.104.0\n..."
                },
                "dependencies": {
                    "production": ["fastapi", "uvicorn", "sqlalchemy"],
                    "development": ["pytest", "black", "flake8"],
                    "optional": ["redis", "celery"]
                },
                "build_configuration": {
                    "python_version": "3.8",
                    "build_tool": "poetry",
                    "docker_image": "python:3.8-slim"
                },
                "deployment_configuration": {
                    "container_port": 8000,
                    "environment_variables": ["DATABASE_URL", "SECRET_KEY"],
                    "health_check": "/health"
                },
                "code_quality_metrics": {
                    "lines_of_code": 1500,
                    "complexity": "low",
                    "test_coverage": "85%",
                    "documentation_coverage": "90%"
                }
            }
        }


class TestGenerationResponse(BaseModel):
    """Response from the test generation agent."""
    
    unit_tests: Dict[str, str]
    integration_tests: Dict[str, str]
    test_data: Dict[str, Any]
    test_configuration: Dict[str, Any]
    coverage_report: Dict[str, Any]
    test_utilities: Dict[str, str]
    
    class Config:
        schema_extra = {
            "example": {
                "unit_tests": {
                    "test_user_service.py": "import pytest\nfrom services.user_service import UserService\n\nclass TestUserService:\n    def test_create_user(self):\n        # Test implementation...",
                    "test_auth_service.py": "import pytest\nfrom services.auth_service import AuthService\n\nclass TestAuthService:\n    def test_authenticate_user(self):\n        # Test implementation..."
                },
                "integration_tests": {
                    "test_api_integration.py": "import pytest\nfrom fastapi.testclient import TestClient\nfrom main import app\n\nclient = TestClient(app)\n\ndef test_user_registration():\n    # Integration test implementation..."
                },
                "test_data": {
                    "users": [
                        {"email": "test@example.com", "password": "testpass123"},
                        {"email": "admin@example.com", "password": "adminpass123"}
                    ],
                    "test_configs": {
                        "database_url": "sqlite:///test.db",
                        "secret_key": "test-secret-key"
                    }
                },
                "test_configuration": {
                    "framework": "pytest",
                    "coverage_tool": "pytest-cov",
                    "test_database": "sqlite",
                    "parallel_execution": True
                },
                "coverage_report": {
                    "total_coverage": "85%",
                    "file_coverage": {
                        "src/api/routes.py": "90%",
                        "src/services/user_service.py": "80%"
                    },
                    "missing_lines": [15, 23, 45]
                },
                "test_utilities": {
                    "conftest.py": "# Pytest configuration and fixtures...",
                    "test_helpers.py": "# Common test utilities and helpers..."
                }
            }
        }


class CodeReviewResponse(BaseModel):
    """Response from the code review agent."""
    
    code_quality_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    security_vulnerabilities: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    maintainability_score: float
    documentation_gaps: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "code_quality_score": 8.5,
                "issues_found": [
                    {
                        "file": "src/api/routes.py",
                        "line": 25,
                        "type": "code_smell",
                        "description": "Function too long (50 lines)",
                        "severity": "medium",
                        "suggestion": "Break into smaller functions"
                    }
                ],
                "recommendations": [
                    {
                        "category": "performance",
                        "description": "Add database connection pooling",
                        "priority": "high",
                        "implementation": "Use SQLAlchemy connection pool"
                    }
                ],
                "security_vulnerabilities": [
                    {
                        "type": "sql_injection",
                        "file": "src/services/user_service.py",
                        "line": 15,
                        "description": "Raw SQL query without parameterization",
                        "severity": "critical",
                        "fix": "Use parameterized queries"
                    }
                ],
                "performance_issues": [
                    {
                        "type": "n_plus_one_query",
                        "file": "src/api/routes.py",
                        "line": 30,
                        "description": "Multiple database queries in loop",
                        "severity": "medium",
                        "fix": "Use eager loading or batch queries"
                    }
                ],
                "maintainability_score": 7.8,
                "documentation_gaps": [
                    "Missing API documentation for /api/v1/users endpoint",
                    "No inline comments in complex business logic",
                    "Missing deployment instructions"
                ]
            }
        }


class SecurityAnalysisResponse(BaseModel):
    """Response from the security analysis agent."""
    
    security_score: float
    vulnerabilities: List[Dict[str, Any]]
    security_recommendations: List[Dict[str, Any]]
    compliance_status: Dict[str, Any]
    threat_model: Dict[str, Any]
    security_configuration: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "security_score": 7.2,
                "vulnerabilities": [
                    {
                        "cve_id": "CVE-2023-1234",
                        "severity": "high",
                        "description": "SQL injection vulnerability",
                        "affected_component": "user_service.py",
                        "mitigation": "Use parameterized queries"
                    }
                ],
                "security_recommendations": [
                    {
                        "category": "authentication",
                        "recommendation": "Implement multi-factor authentication",
                        "priority": "high",
                        "effort": "medium"
                    }
                ],
                "compliance_status": {
                    "gdpr": "compliant",
                    "sox": "partially_compliant",
                    "pci_dss": "not_applicable"
                },
                "threat_model": {
                    "attack_vectors": ["SQL injection", "XSS", "CSRF"],
                    "risk_assessment": "medium",
                    "mitigation_strategies": ["Input validation", "Output encoding", "CSRF tokens"]
                },
                "security_configuration": {
                    "authentication": "JWT with refresh tokens",
                    "authorization": "Role-based access control",
                    "encryption": "AES-256 for data at rest",
                    "logging": "Security event logging enabled"
                }
            }
        }


class DocumentationResponse(BaseModel):
    """Response from the documentation agent."""
    
    api_documentation: Dict[str, Any]
    user_guides: Dict[str, str]
    developer_documentation: Dict[str, str]
    deployment_guides: Dict[str, str]
    readme_files: Dict[str, str]
    diagrams: Dict[str, str]
    
    class Config:
        schema_extra = {
            "example": {
                "api_documentation": {
                    "openapi_spec": "openapi.yaml",
                    "endpoint_docs": {
                        "/api/v1/users": {
                            "description": "User management endpoints",
                            "methods": ["GET", "POST", "PUT", "DELETE"],
                            "examples": ["create_user.json", "get_users.json"]
                        }
                    }
                },
                "user_guides": {
                    "getting_started.md": "# Getting Started Guide\n\nThis guide will help you...",
                    "api_usage.md": "# API Usage Guide\n\nLearn how to use our API..."
                },
                "developer_documentation": {
                    "architecture.md": "# System Architecture\n\nDetailed architecture documentation...",
                    "development_setup.md": "# Development Setup\n\nHow to set up the development environment..."
                },
                "deployment_guides": {
                    "docker_deployment.md": "# Docker Deployment\n\nDeploy using Docker...",
                    "kubernetes_deployment.md": "# Kubernetes Deployment\n\nDeploy to Kubernetes..."
                },
                "readme_files": {
                    "README.md": "# Project Name\n\nBrief project description...",
                    "CONTRIBUTING.md": "# Contributing\n\nHow to contribute to this project..."
                },
                "diagrams": {
                    "architecture.png": "System architecture diagram",
                    "database_schema.png": "Database schema diagram",
                    "api_flow.png": "API request flow diagram"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error_code: str
    error_message: str
    error_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseModel):
    """Success response model."""
    
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
