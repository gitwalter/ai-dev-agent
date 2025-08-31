# Enhanced structured output models for AI Development Agent system.
# Based on LangChain structured outputs principles for improved stability and validation.

import json
import logging
from typing import Dict, Any, Optional, List, Union, Literal
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import conint, constr

# Configure logging
logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    """Severity levels for issues and recommendations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Status of task execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CodeQualityScore(BaseModel):
    """Structured code quality assessment."""
    
    overall_score: conint(ge=1, le=10) = Field(
        description="Overall code quality score from 1-10",
        json_schema_extra={"example": 8}
    )
    readability_score: conint(ge=1, le=10) = Field(
        description="Code readability score from 1-10",
        json_schema_extra={"example": 7}
    )
    maintainability_score: conint(ge=1, le=10) = Field(
        description="Code maintainability score from 1-10",
        json_schema_extra={"example": 8}
    )
    performance_score: conint(ge=1, le=10) = Field(
        description="Code performance score from 1-10",
        json_schema_extra={"example": 9}
    )
    security_score: conint(ge=1, le=10) = Field(
        description="Code security score from 1-10",
        json_schema_extra={"example": 6}
    )
    test_coverage_score: conint(ge=1, le=10) = Field(
        description="Test coverage score from 1-10",
        json_schema_extra={"example": 7}
    )
    
    @model_validator(mode='after')
    def validate_overall_score(self):
        """Validate that overall score is reasonable given component scores."""
        readability_score = getattr(self, 'readability_score', None)
        maintainability_score = getattr(self, 'maintainability_score', None)
        
        if readability_score is not None and maintainability_score is not None:
            avg_score = (readability_score + maintainability_score) / 2
            if abs(self.overall_score - avg_score) > 3:
                logger.warning(f"Overall score {self.overall_score} differs significantly from component average {avg_score}")
        
        return self


class Issue(BaseModel):
    """Structured issue representation."""
    
    title: constr(min_length=1, max_length=200) = Field(
        description="Brief title of the issue",
        json_schema_extra={"example": "Missing input validation"}
    )
    description: constr(min_length=10, max_length=1000) = Field(
        description="Detailed description of the issue",
        json_schema_extra={"example": "The user input is not validated before processing, which could lead to security vulnerabilities."}
    )
    severity: SeverityLevel = Field(
        description="Severity level of the issue",
        json_schema_extra={"example": SeverityLevel.HIGH}
    )
    category: constr(min_length=1, max_length=50) = Field(
        description="Category of the issue (e.g., security, performance, style)",
        json_schema_extra={"example": "security"}
    )
    location: Optional[str] = Field(
        description="File and line number where the issue occurs",
        json_schema_extra={"example": "main.py:42"}
    )
    suggestion: Optional[str] = Field(
        description="Suggested fix or improvement",
        json_schema_extra={"example": "Add input validation using Pydantic models"}
    )
    impact: Optional[str] = Field(
        description="Potential impact of the issue",
        json_schema_extra={"example": "Could allow injection attacks"}
    )


class Recommendation(BaseModel):
    """Structured recommendation representation."""
    
    title: constr(min_length=1, max_length=200) = Field(
        description="Brief title of the recommendation",
        json_schema_extra={"example": "Implement comprehensive logging"}
    )
    description: constr(min_length=10, max_length=1000) = Field(
        description="Detailed description of the recommendation",
        json_schema_extra={"example": "Add structured logging throughout the application for better debugging and monitoring."}
    )
    priority: SeverityLevel = Field(
        description="Priority level of the recommendation",
        json_schema_extra={"example": SeverityLevel.MEDIUM}
    )
    category: constr(min_length=1, max_length=50) = Field(
        description="Category of the recommendation",
        json_schema_extra={"example": "monitoring"}
    )
    implementation_effort: constr(min_length=1, max_length=20) = Field(
        description="Estimated implementation effort",
        json_schema_extra={"example": "low"}
    )
    benefits: List[str] = Field(
        description="List of benefits from implementing this recommendation",
        json_schema_extra={"example": ["Better debugging", "Improved monitoring", "Easier troubleshooting"]}
    )
    steps: Optional[List[str]] = Field(
        description="Step-by-step implementation guide",
        json_schema_extra={"example": ["1. Install logging library", "2. Configure loggers", "3. Add log statements"]}
    )


class SourceFile(BaseModel):
    """Model for source code files."""
    filename: str = Field(...)  # Removed max_length constraint to allow custom validation
    content: str
    language: Optional[str] = None
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename length and format."""
        if len(v) > 500:
            # Truncate filename if too long
            return v[:497] + "..."
        return v
    
    class Config:
        extra = "allow"  # Allow extra fields for flexibility


class ConfigurationFile(BaseModel):
    """Structured configuration file representation."""
    
    filename: str = Field(
        description="Name of the configuration file",
        json_schema_extra={"example": "requirements.txt"}
    )
    content: constr(min_length=1) = Field(
        description="Content of the configuration file",
        json_schema_extra={"example": "fastapi==0.104.1\nuvicorn==0.24.0"}
    )
    file_type: constr(min_length=1, max_length=50) = Field(
        description="Type of configuration file",
        json_schema_extra={"example": "requirements"}
    )
    description: Optional[str] = Field(
        description="Description of what this configuration file does",
        json_schema_extra={"example": "Python package dependencies"}
    )
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename length and format."""
        if len(v) > 500:
            # Truncate filename if too long
            return v[:497] + "..."
        return v


class TestFile(BaseModel):
    """Structured test file representation."""
    
    filename: str = Field(
        description="Name of the test file",
        json_schema_extra={"example": "test_main.py"}
    )
    content: constr(min_length=1) = Field(
        description="Content of the test file",
        json_schema_extra={"example": "import pytest\nfrom main import app\n\ndef test_read_root():\n    response = app.get('/')\n    assert response.status_code == 200"}
    )
    test_type: constr(min_length=1, max_length=50) = Field(
        description="Type of tests in this file",
        json_schema_extra={"example": "unit"}
    )
    coverage_target: Optional[str] = Field(
        default=None,
        description="Target coverage for this test file",
        json_schema_extra={"example": "80%"}
    )
    dependencies: Optional[List[str]] = Field(
        default=None,
        description="Test dependencies required",
        json_schema_extra={"example": ["pytest", "httpx"]}
    )
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename length and format."""
        if len(v) > 500:
            # Truncate filename if too long
            return v[:497] + "..."
        return v


class DocumentationFile(BaseModel):
    """Structured documentation file representation."""
    
    filename: str = Field(
        description="Name of the documentation file",
        json_schema_extra={"example": "README.md"}
    )
    content: constr(min_length=1) = Field(
        description="Content of the documentation file",
        json_schema_extra={"example": "# Project Title\n\n## Overview\nThis is a sample project."}
    )
    doc_type: constr(min_length=1, max_length=50) = Field(
        description="Type of documentation",
        json_schema_extra={"example": "readme"}
    )
    audience: Optional[str] = Field(
        description="Target audience for this documentation",
        json_schema_extra={"example": "developers"}
    )
    format: Optional[str] = Field(
        description="Documentation format",
        json_schema_extra={"example": "markdown"}
    )
    diagrams: Optional[Dict[str, str]] = Field(
        description="Embedded diagrams in the documentation file",
        json_schema_extra={"example": { "class_diagram": "```plantuml\n@startuml\nclass User {\n  +String name\n  +String email\n  +login()\n}\n@enduml\n```", "sequence_diagram": "```mermaid\nsequenceDiagram\n    participant U as User\n    participant S as System\n    U->>S: Login\n    S-->>U: Success\n```" }}
    )
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename length and format."""
        if len(v) > 500:
            # Truncate filename if too long
            return v[:497] + "..."
        return v


class CodeGenerationOutput(BaseModel):
    """Enhanced structured output model for code generation responses."""
    
    source_files: Dict[str, SourceFile] = Field(
        description="Dictionary of source code files with their content and metadata",
        json_schema_extra={"example": {
            "main.py": {
                "filename": "main.py",
                "content": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}",
                "language": "python",
                "purpose": "Main application entry point"
            }
        }}
    )
    
    configuration_files: Dict[str, ConfigurationFile] = Field(
        default_factory=dict,
        description="Dictionary of configuration files with their content and metadata",
        json_schema_extra={"example": {
            "requirements.txt": {
                "filename": "requirements.txt",
                "content": "fastapi==0.104.1\nuvicorn==0.24.0",
                "file_type": "requirements",
                "description": "Python package dependencies"
            }
        }}
    )
    
    test_files: Dict[str, TestFile] = Field(
        description="Dictionary of test files with their content and metadata",
        default_factory=dict
    )
    
    documentation_files: Dict[str, DocumentationFile] = Field(
        description="Dictionary of documentation files with their content and metadata",
        default_factory=dict
    )
    
    project_structure: List[str] = Field(
        default_factory=list,
        description="List of project structure directories and files",
        json_schema_extra={"example": ["src/", "tests/", "docs/", "config/"]}
    )
    
    implementation_notes: List[str] = Field(
        default_factory=list,
        description="List of implementation notes and architectural decisions",
        json_schema_extra={"example": ["RESTful API design with FastAPI", "Proper error handling and validation"]}
    )
    
    testing_strategy: Dict[str, str] = Field(
        default_factory=dict,
        description="Testing strategy and approach",
        json_schema_extra={"example": {
            "unit_tests": "pytest for unit testing",
            "integration_tests": "API endpoint testing",
            "test_data": "Sample test fixtures and data"
        }}
    )
    
    deployment_instructions: List[str] = Field(
        default_factory=list,
        description="List of deployment and setup instructions",
        json_schema_extra={"example": [
            "1. Install dependencies: pip install -r requirements.txt",
            "2. Set environment variables",
            "3. Run with: uvicorn main:app --reload"
        ]}
    )
    
    quality_assessment: Optional[CodeQualityScore] = Field(
        description="Code quality assessment scores",
        default=None
    )
    
    @model_validator(mode='after')
    def validate_file_consistency(self):
        """Validate consistency between file dictionaries and project structure."""
        source_files = self.source_files
        project_structure = self.project_structure
        
        # Check that all source files are mentioned in project structure
        for filename in source_files.keys():
            if filename not in project_structure:
                logger.warning(f"Source file {filename} not found in project structure")
        
        return self
    
    @model_validator(mode='after')
    def validate_source_files(self):
        """Validate that source files contain meaningful content."""
        if not self.source_files:
            raise ValueError("At least one source file must be provided")
        
        for filename, file_data in self.source_files.items():
            if not file_data.content.strip():
                raise ValueError(f"Source file {filename} cannot have empty content")
        
        return self


class CodeReviewOutput(BaseModel):
    """Enhanced structured output model for code review responses."""
    
    overall_assessment: CodeQualityScore = Field(
        description="Overall code quality assessment with detailed scores"
    )
    
    issues: List[Issue] = Field(
        description="List of identified issues and problems",
        default_factory=list
    )
    
    improvements: List[Recommendation] = Field(
        description="List of suggested improvements",
        default_factory=list
    )
    
    positive_aspects: List[str] = Field(
        description="List of positive aspects and good practices found",
        json_schema_extra={"example": ["Well-structured functions", "Good error handling", "Clear variable names"]}
    )
    
    security_concerns: List[Issue] = Field(
        description="List of security-related issues",
        default_factory=list
    )
    
    performance_issues: List[Issue] = Field(
        description="List of performance-related issues",
        default_factory=list
    )
    
    recommendations: List[Recommendation] = Field(
        description="List of actionable recommendations",
        default_factory=list
    )
    
    summary: constr(min_length=10, max_length=500) = Field(
        description="Overall summary of the code review",
        json_schema_extra={"example": "The code demonstrates good structure and follows most best practices, but needs improvements in error handling and security validation."}
    )
    
    @model_validator(mode='after')
    def validate_summary_length(self):
        """Validate summary length is appropriate."""
        if len(self.summary) < 10:
            raise ValueError("Summary must be at least 10 characters long")
        if len(self.summary) > 500:
            raise ValueError("Summary must not exceed 500 characters")
        return self


class RequirementsAnalysisOutput(BaseModel):
    """Enhanced structured output model for requirements analysis responses."""
    
    functional_requirements: List[Dict[str, Any]] = Field(
        description="List of functional requirements with detailed specifications",
        json_schema_extra={"example": [{"id": "FR-001", "title": "User Authentication", "description": "System must support user login and logout", "priority": "high", "acceptance_criteria": ["User can login with valid credentials", "User can logout successfully"]}]}
    )
    
    non_functional_requirements: List[Dict[str, Any]] = Field(
        description="List of non-functional requirements",
        json_schema_extra={"example": [{"id": "NFR-001", "title": "Performance", "description": "System must respond within 2 seconds", "category": "performance", "measurement": "response time < 2s"}]}
    )
    
    user_stories: List[Dict[str, Any]] = Field(
        description="List of user stories in standard format",
        json_schema_extra={"example": [{"id": "US-001", "as_a": "user", "i_want": "to login to the system", "so_that": "I can access my account"}]}
    )
    
    technical_constraints: List[str] = Field(
        description="List of technical constraints and limitations",
        json_schema_extra={"example": ["Must use Python 3.9+", "Must be compatible with existing database"]}
    )
    
    assumptions: List[str] = Field(
        description="List of assumptions made during analysis",
        json_schema_extra={"example": ["Users have basic computer literacy", "Internet connection is available"]}
    )
    
    risks: List[Dict[str, Any]] = Field(
        description="List of identified risks with mitigation strategies",
        json_schema_extra={"example": [{"risk": "Data security breach", "probability": "medium", "impact": "high", "mitigation": "Implement encryption and access controls"}]}
    )
    
    summary: Dict[str, Any] = Field(
        description="Summary of requirements analysis",
        json_schema_extra={"example": {
            "total_functional_requirements": 5,
            "total_non_functional_requirements": 3,
            "total_user_stories": 8,
            "estimated_complexity": "medium",
            "recommended_tech_stack": ["Python", "FastAPI", "PostgreSQL"],
            "estimated_timeline": "2-3 weeks",
            "key_success_factors": ["Clear requirements", "Stakeholder involvement"]
        }}
    )


class ArchitectureDesignOutput(BaseModel):
    """Enhanced structured output model for architecture design responses."""
    
    system_overview: constr(min_length=10, max_length=1000) = Field(
        description="High-level system overview and description",
        json_schema_extra={"example": "A microservices-based architecture with RESTful APIs for user management and data processing."}
    )
    
    architecture_pattern: constr(min_length=1, max_length=100) = Field(
        description="Primary architecture pattern used",
        json_schema_extra={"example": "Microservices"}
    )
    
    components: List[Dict[str, Any]] = Field(
        description="List of system components with their responsibilities",
        json_schema_extra={"example": [{"name": "User Service", "responsibility": "User management and authentication", "technology": "Python/FastAPI", "dependencies": ["Database", "Auth Service"]}]}
    )
    
    data_flow: constr(min_length=10, max_length=2000) = Field(
        description="Description of data flow between components",
        json_schema_extra={"example": "User requests flow through API Gateway to appropriate microservice, which processes data and returns responses."}
    )
    
    technology_stack: Dict[str, List[str]] = Field(
        description="Technology stack by layer",
        json_schema_extra={"example": {
            "frontend": ["React", "TypeScript"],
            "backend": ["Python", "FastAPI"],
            "database": ["PostgreSQL"],
            "infrastructure": ["Docker", "Kubernetes"]
        }}
    )
    
    security_considerations: List[str] = Field(
        description="List of security considerations and measures",
        json_schema_extra={"example": ["JWT authentication", "HTTPS encryption", "Input validation"]}
    )
    
    scalability_considerations: List[str] = Field(
        description="List of scalability considerations and strategies",
        json_schema_extra={"example": ["Horizontal scaling", "Load balancing", "Database sharding"]}
    )
    
    performance_considerations: List[str] = Field(
        description="List of performance considerations and optimizations",
        json_schema_extra={"example": ["Caching strategies", "Database indexing", "CDN usage"]}
    )
    
    deployment_strategy: constr(min_length=10, max_length=2000) = Field(
        description="Deployment strategy and approach",
        json_schema_extra={"example": "Containerized deployment using Docker with Kubernetes orchestration for scalability and reliability."}
    )
    
    risk_mitigation: List[Dict[str, str]] = Field(
        description="List of risk mitigation strategies",
        json_schema_extra={"example": [{"risk": "Single point of failure", "mitigation": "Implement redundancy and failover mechanisms"}]}
    )
    
    database_schema: Dict[str, Any] = Field(
        description="Database schema design",
        json_schema_extra={"example": {
            "tables": [
                {
                    "name": "users",
                    "columns": ["id", "email", "password_hash", "created_at"],
                    "relationships": ["has_many: posts"]
                }
            ]
        }}
    )
    
    api_design: Dict[str, Any] = Field(
        description="API design specifications",
        json_schema_extra={"example": {
            "endpoints": [
                {
                    "path": "/users",
                    "method": "GET",
                    "description": "Retrieve all users",
                    "authentication": "required"
                }
            ]
        }}
    )


class TestGenerationOutput(BaseModel):
    """Enhanced structured output model for test generation responses."""
    
    test_files: Dict[str, TestFile] = Field(
        description="Dictionary of test files with their content and metadata"
    )
    
    test_categories: Dict[str, List[str]] = Field(
        description="Test categories and their descriptions",
        json_schema_extra={"example": {
            "unit_tests": ["Function-level tests", "Class-level tests"],
            "integration_tests": ["API endpoint tests", "Database integration tests"],
            "performance_tests": ["Load testing", "Stress testing"]
        }}
    )
    
    test_data: Dict[str, str] = Field(
        description="Test data and fixtures information",
        json_schema_extra={"example": {
            "fixtures": "Sample test data and fixtures for comprehensive testing",
            "mocks": "Mock objects and stubs for isolated testing",
            "test_databases": "Test database setup and configuration"
        }}
    )
    
    coverage_targets: Dict[str, str] = Field(
        description="Coverage targets for different test types",
        json_schema_extra={"example": {
            "unit_test_coverage": "80%",
            "integration_test_coverage": "60%",
            "critical_path_coverage": "100%"
        }}
    )
    
    testing_strategy: Dict[str, str] = Field(
        description="Overall testing strategy and approach",
        json_schema_extra={"example": {
            "framework": "pytest",
            "assertion_library": "pytest assertions",
            "mocking_framework": "unittest.mock",
            "coverage_tool": "pytest-cov"
        }}
    )
    
    test_execution_plan: List[str] = Field(
        description="Step-by-step test execution plan",
        json_schema_extra={"example": [ "1. Run unit tests: pytest tests/unit/", "2. Run integration tests: pytest tests/integration/", "3. Generate coverage report: pytest --cov=src tests/" ]}
    )


class SecurityAnalysisOutput(BaseModel):
    """Enhanced structured output model for security analysis responses."""
    
    security_assessment: Dict[str, Any] = Field(
        description="Overall security assessment",
        json_schema_extra={"example": {
            "overall_risk_level": "medium",
            "security_score": 7,
            "compliance_status": "partial",
            "summary": "Security assessment completed with identified vulnerabilities"
        }}
    )
    
    vulnerabilities: List[Issue] = Field(
        description="List of identified security vulnerabilities",
        default_factory=list
    )
    
    security_controls: List[Dict[str, Any]] = Field(
        description="List of implemented and recommended security controls",
        json_schema_extra={"example": [ { "control": "Input validation", "status": "implemented", "description": "All user inputs are validated" } ]}
    )
    
    risk_analysis: List[Dict[str, Any]] = Field(
        description="Detailed risk analysis",
        json_schema_extra={"example": [ { "risk": "SQL injection", "probability": "low", "impact": "high", "mitigation": "Use parameterized queries" } ]}
    )
    
    compliance_requirements: List[str] = Field(
        description="List of compliance requirements and standards",
        json_schema_extra={"example": ["GDPR compliance", "OWASP Top 10", "ISO 27001"]}
    )
    
    security_recommendations: List[Recommendation] = Field(
        description="List of security improvement recommendations",
        default_factory=list
    )
    
    security_testing: Dict[str, str] = Field(
        description="Security testing approach and tools",
        json_schema_extra={"example": {
            "penetration_testing": "Automated penetration testing with OWASP ZAP",
            "vulnerability_scanning": "Regular vulnerability scanning with Bandit",
            "code_review": "Security-focused code review checklist",
            "security_monitoring": "Real-time security monitoring and alerting"
        }}
    )


class DocumentationGenerationOutput(BaseModel):
    """Enhanced structured output model for documentation generation responses."""
    
    documentation_files: Dict[str, DocumentationFile] = Field(
        description="Dictionary of documentation files with their content and metadata"
    )
    
    code_documentation: Dict[str, str] = Field(
        description="Code documentation standards and approach",
        json_schema_extra={"example": {
            "docstrings": "Google-style docstrings for all functions and classes",
            "comments": "Inline comments for complex logic and business rules",
            "type_hints": "Type annotations for all function parameters and return values"
        }}
    )
    
    user_documentation: Dict[str, str] = Field(
        description="User documentation structure and content",
        json_schema_extra={"example": {
            "user_guide": "Comprehensive user guide with step-by-step instructions",
            "admin_guide": "Administrator documentation for system management",
            "troubleshooting": "Common issues and their solutions"
        }}
    )
    
    technical_documentation: Dict[str, str] = Field(
        description="Technical documentation structure and content",
        json_schema_extra={"example": {
            "design_decisions": "Architecture and design decision records (ADRs)",
            "database_schema": "Complete database schema documentation",
            "api_specification": "OpenAPI/Swagger specification",
            "testing_strategy": "Testing approach and coverage documentation"
        }}
    )
    
    diagrams: Dict[str, Dict[str, str]] = Field(
        description="UML and BPMN diagrams for the project",
        json_schema_extra={"example": {
            "class_diagram": {
                "filename": "docs/diagrams/class_diagram.puml",
                "content": "@startuml\nclass User {\n  +String name\n  +String email\n  +login()\n}\n@enduml",
                "description": "Class diagram showing system entities and relationships"
            },
            "sequence_diagram": {
                "filename": "docs/diagrams/sequence_diagram.puml",
                "content": "@startuml\nactor User\nparticipant System\nUser -> System: Login\nSystem --> User: Success\n@enduml",
                "description": "Sequence diagram showing user authentication flow"
            },
            "activity_diagram": {
                "filename": "docs/diagrams/activity_diagram.puml",
                "content": "@startuml\nstart\n:User Login;\nif (Valid Credentials?) then (yes)\n  :Show Dashboard;\nelse (no)\n  :Show Error;\nendif\nstop\n@enduml",
                "description": "Activity diagram showing login process flow"
            },
            "bpmn_diagram": {
                "filename": "docs/diagrams/business_process.bpmn",
                "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<bpmn:definitions xmlns:bpmn=\"http://www.omg.org/spec/BPMN/20100524/MODEL\">\n  <bpmn:process id=\"Process_1\">\n    <bpmn:startEvent id=\"StartEvent_1\"/>\n    <bpmn:task id=\"Task_1\" name=\"Process Task\"/>\n    <bpmn:endEvent id=\"EndEvent_1\"/>\n  </bpmn:process>\n</bpmn:definitions>",
                "description": "BPMN diagram showing business process flow"
            }
        }}
    )
    
    documentation_structure: List[str] = Field(
        description="Documentation directory structure",
        json_schema_extra={"example": ["docs/", "docs/api/", "docs/architecture/", "docs/user-guide/"]}
    )
    
    documentation_standards: Dict[str, str] = Field(
        description="Documentation standards and guidelines",
        json_schema_extra={"example": {
            "format": "Markdown with code examples and diagrams",
            "style_guide": "Consistent formatting and terminology",
            "review_process": "Documentation review and approval workflow",
            "diagram_standards": "PlantUML for UML diagrams, Mermaid for flowcharts, BPMN XML for business processes"
        }}
    )
    
    maintenance_plan: List[str] = Field(
        description="Documentation maintenance and update plan",
        json_schema_extra={"example": [ "1. Update documentation with each code change", "2. Monthly documentation review and cleanup", "3. User feedback collection and incorporation" ]}
    )


# Factory function for creating output models
def create_output_model(agent_type: str) -> type[BaseModel]:
    """Create the appropriate output model for a given agent type."""
    
    model_mapping = {
        "code_generator": CodeGenerationOutput,
        "code_reviewer": CodeReviewOutput,
        "requirements_analyst": RequirementsAnalysisOutput,
        "architecture_designer": ArchitectureDesignOutput,
        "test_generator": TestGenerationOutput,
        "security_analyst": SecurityAnalysisOutput,
        "documentation_generator": DocumentationGenerationOutput
    }
    
    return model_mapping.get(agent_type, CodeGenerationOutput)


# Validation utilities
def validate_output_model(data: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
    """Validate data against the appropriate output model."""
    
    try:
        model_class = create_output_model(agent_type)
        model_instance = model_class(**data)
        return model_instance.dict()
    except Exception as e:
        logger.error(f"Output validation failed for {agent_type}: {e}")
        raise ValueError(f"Invalid output structure for {agent_type}: {e}")


def get_format_instructions(agent_type: str) -> str:
    """Get format instructions for a specific agent type."""
    
    model_class = create_output_model(agent_type)
    
    # Generate format instructions based on the model
    instructions = f"""
Please respond with a JSON object that follows this exact structure for {agent_type}:

{model_class.schema_json(indent=2)}

Important formatting rules:
1. All strings must be properly escaped
2. All arrays must be properly closed
3. All objects must be properly closed
4. Use double quotes for all strings
5. Do not include trailing commas
6. Ensure all required fields are present
7. Validate that all field types match the schema
"""
    
    return instructions
