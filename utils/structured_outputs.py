#!/usr/bin/env python3
"""
LangChain-Compatible Structured Outputs for AI Development Agent.
100% compliant with LangChain standards and Pydantic V2 best practices.
"""

from typing import Dict, List, Any, Optional, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
import logging

# LangChain imports with fallback
try:
    from langchain.output_parsers import PydanticOutputParser
    from langchain.schema import OutputParserException
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available for structured outputs")

logger = logging.getLogger(__name__)


# LangChain Standard: Use Literal types for better schema generation
SeverityType = Literal["low", "medium", "high", "critical"]
TaskStatusType = Literal["pending", "in_progress", "completed", "failed", "cancelled"]
PriorityType = Literal["low", "normal", "high", "critical"]


class SeverityLevel(str, Enum):
    """Severity levels for issues and recommendations - LangChain compatible."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status enumeration - LangChain compatible."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """Priority enumeration - LangChain compatible."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(BaseModel):
    """Represents an issue found during analysis - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={
            "description": "Issue detected during code analysis",
            "examples": [{
                "id": "ISS-001",
                "severity": "medium",
                "description": "Missing error handling",
                "location": "line 42",
                "suggestion": "Add try-catch block"
            }]
        }
    )
    
    id: str = Field(description="Unique identifier for the issue", min_length=1)
    severity: SeverityType = Field(description="Severity level of the issue")
    description: str = Field(description="Description of the issue", min_length=1)
    location: Optional[str] = Field(default=None, description="Location where issue was found")
    suggestion: str = Field(description="Suggested fix for the issue", min_length=1)


class Recommendation(BaseModel):
    """Represents a recommendation for improvement - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={
            "description": "Recommendation for code improvement",
            "examples": [{
                "id": "REC-001",
                "priority": "high",
                "description": "Implement logging",
                "category": "observability",
                "implementation": "Add structured logging with appropriate levels"
            }]
        }
    )
    
    id: str = Field(description="Unique identifier for the recommendation", min_length=1)
    priority: SeverityType = Field(description="Priority level of the recommendation")
    description: str = Field(description="Description of the recommendation", min_length=1)
    category: str = Field(description="Category of the recommendation", min_length=1)
    implementation: str = Field(description="How to implement the recommendation", min_length=1)


class CodeQualityScore(BaseModel):
    """Code quality scoring metrics - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Code quality assessment scores",
            "examples": [{
                "overall_score": 85.0,
                "maintainability": 90.0,
                "readability": 88.0,
                "performance": 82.0,
                "security": 78.0,
                "recommendations": ["Add more comments", "Improve error handling"]
            }]
        }
    )
    
    overall_score: float = Field(ge=0, le=100, description="Overall quality score (0-100)")
    maintainability: float = Field(ge=0, le=100, description="Maintainability score")
    readability: float = Field(ge=0, le=100, description="Readability score")
    performance: float = Field(ge=0, le=100, description="Performance score")
    security: float = Field(ge=0, le=100, description="Security score")
    recommendations: List[str] = Field(default_factory=list, description="List of recommendations")


class RequirementsAnalysisOutput(BaseModel):
    """Output from requirements analysis agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Structured output for requirements analysis results",
            "examples": [{
                "functional_requirements": [{"id": "FR-001", "title": "User Login", "description": "Users can log in"}],
                "summary": {"total_requirements": 1}
            }]
        }
    )
    
    functional_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="List of functional requirements")
    non_functional_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="List of non-functional requirements") 
    user_stories: List[Dict[str, Any]] = Field(default_factory=list, description="List of user stories")
    technical_constraints: List[str] = Field(default_factory=list, description="Technical constraints and limitations")
    assumptions: List[str] = Field(default_factory=list, description="Project assumptions")
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="Identified risks and mitigations")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Analysis summary and metrics")


class ArchitectureDesignOutput(BaseModel):
    """Output from architecture design agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Architecture design analysis results",
            "examples": [{
                "architecture_overview": "Microservices architecture with API gateway",
                "components": [{"name": "API Gateway", "type": "service"}],
                "data_flow": "Client -> API Gateway -> Services",
                "tech_stack": {"backend": ["Python", "FastAPI"], "database": ["PostgreSQL"]},
                "deployment_strategy": "Docker containers with Kubernetes"
            }]
        }
    )
    
    architecture_overview: str = Field(description="High-level architecture overview", min_length=1)
    components: List[Dict[str, Any]] = Field(default_factory=list, description="Architecture components")
    data_flow: str = Field(description="Data flow description", min_length=1)
    tech_stack: Dict[str, List[str]] = Field(default_factory=dict, description="Technology stack by category")
    security_considerations: List[str] = Field(default_factory=list, description="Security considerations")
    scalability_considerations: List[str] = Field(default_factory=list, description="Scalability considerations")
    performance_considerations: List[str] = Field(default_factory=list, description="Performance considerations")
    deployment_strategy: str = Field(description="Deployment strategy", min_length=1)
    risks_and_mitigations: List[Dict[str, str]] = Field(default_factory=list, description="Risks and mitigation strategies")


class CodeGenerationOutput(BaseModel):
    """Output from code generation agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Code generation results and analysis",
            "examples": [{
                "generated_files": {"main.py": "# Generated Python code"},
                "file_structure": {"src": {"type": "directory"}},
                "dependencies": ["fastapi", "pydantic"],
                "setup_instructions": ["pip install -r requirements.txt"],
                "deployment_instructions": ["docker build -t app ."]
            }]
        }
    )
    
    generated_files: Dict[str, str] = Field(default_factory=dict, description="Generated code files with content")
    file_structure: Dict[str, Any] = Field(default_factory=dict, description="Project file structure")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies and packages")
    setup_instructions: List[str] = Field(default_factory=list, description="Setup and installation instructions")
    deployment_instructions: List[str] = Field(default_factory=list, description="Deployment instructions")
    code_quality: Optional[CodeQualityScore] = Field(default=None, description="Code quality metrics")
    issues: List[Issue] = Field(default_factory=list, description="Issues found in generated code")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Code improvement recommendations")


class TestFile(BaseModel):
    """Represents a generated test file - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Generated test file with metadata",
            "examples": [{
                "filename": "test_main.py",
                "content": "# Generated test code\nimport pytest\n\ndef test_example():\n    assert True",
                "test_type": "unit",
                "coverage": "85%"
            }]
        }
    )
    
    filename: str = Field(description="Test file name", min_length=1)
    content: str = Field(description="Test file content", min_length=1)
    test_type: str = Field(description="Type of test (unit, integration, etc.)", min_length=1)
    coverage: str = Field(description="Coverage information for this test file", min_length=1)


class TestGenerationOutput(BaseModel):
    """Output from test generation agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Test generation results and metrics",
            "examples": [{
                "test_files": {"test_main.py": "# Generated test code"},
                "test_coverage": 85.0,
                "test_strategy": "Unit and integration testing",
                "test_frameworks": ["pytest", "unittest"],
                "test_data": {"fixtures": ["sample_data.json"]}
            }]
        }
    )
    
    test_files: Dict[str, str] = Field(default_factory=dict, description="Generated test files with content")
    test_coverage: float = Field(ge=0, le=100, description="Test coverage percentage")
    test_strategy: str = Field(description="Testing strategy and approach", min_length=1)
    test_frameworks: List[str] = Field(default_factory=list, description="Test frameworks used")
    test_data: Dict[str, Any] = Field(default_factory=dict, description="Test data and fixtures")
    quality_score: Optional[CodeQualityScore] = Field(default=None, description="Test quality metrics")


class CodeReviewOutput(BaseModel):
    """Output from code review agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Code review analysis and feedback",
            "examples": [{
                "overall_rating": "good",
                "review_summary": "Code is well-structured with minor improvements needed",
                "approval_status": "approved_with_suggestions",
                "issues": [],
                "recommendations": []
            }]
        }
    )
    
    overall_rating: str = Field(description="Overall code rating", min_length=1)
    code_quality: Optional[CodeQualityScore] = Field(default=None, description="Quality metrics")
    issues: List[Issue] = Field(default_factory=list, description="Issues found during review")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Improvement recommendations")
    review_summary: str = Field(description="Summary of the review", min_length=1)
    approval_status: str = Field(description="Approval status", min_length=1)


class SecurityAnalysisOutput(BaseModel):
    """Output from security analysis agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Security analysis results and recommendations",
            "examples": [{
                "security_score": 78.0,
                "vulnerabilities": [],
                "security_recommendations": [],
                "compliance_status": {"OWASP": "compliant"},
                "security_controls": ["input_validation", "encryption"],
                "risk_assessment": {"overall_risk": "medium"}
            }]
        }
    )
    
    security_score: float = Field(ge=0, le=100, description="Overall security score")
    vulnerabilities: List[Issue] = Field(default_factory=list, description="Security vulnerabilities found")
    security_recommendations: List[Recommendation] = Field(default_factory=list, description="Security recommendations")
    compliance_status: Dict[str, str] = Field(default_factory=dict, description="Compliance status for various standards")
    security_controls: List[str] = Field(default_factory=list, description="Implemented security controls")
    risk_assessment: Dict[str, Any] = Field(default_factory=dict, description="Security risk assessment")


class DocumentationGenerationOutput(BaseModel):
    """Output from documentation generation agent - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Documentation generation results and quality metrics",
            "examples": [{
                "documentation_files": {"README.md": "# Project Documentation"},
                "documentation_structure": {"sections": ["overview", "setup", "usage"]},
                "coverage_analysis": {"api_coverage": 90.0, "function_coverage": 85.0},
                "quality_metrics": {"readability": 88.0, "completeness": 82.0}
            }]
        }
    )
    
    documentation_files: Dict[str, str] = Field(default_factory=dict, description="Generated documentation files")
    documentation_structure: Dict[str, Any] = Field(default_factory=dict, description="Documentation structure and organization")
    coverage_analysis: Dict[str, float] = Field(default_factory=dict, description="Documentation coverage metrics")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Documentation quality assessment")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Documentation improvement recommendations")


class ProjectPlanOutput(BaseModel):
    """Output for project planning - LangChain compatible."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "description": "Project planning and management output",
            "examples": [{
                "project_overview": "AI Development Agent implementation project",
                "milestones": [{"name": "MVP", "deadline": "2024-03-01", "status": "pending"}],
                "timeline": {"start_date": "2024-01-01", "end_date": "2024-06-01"},
                "resources": ["developers", "infrastructure"],
                "risks": [{"risk": "scope creep", "mitigation": "strict change control"}],
                "success_criteria": ["all tests passing", "documentation complete"]
            }]
        }
    )
    
    project_overview: str = Field(description="High-level project overview", min_length=1)
    milestones: List[Dict[str, Any]] = Field(default_factory=list, description="Project milestones and deadlines")
    timeline: Dict[str, Any] = Field(default_factory=dict, description="Project timeline and scheduling")
    resources: List[str] = Field(default_factory=list, description="Required resources and team members")
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="Project risks and mitigation strategies")
    success_criteria: List[str] = Field(default_factory=list, description="Project success criteria and KPIs")


# Model mapping for easy access - LangChain compatible
MODEL_MAPPING = {
    "requirements_analyst": RequirementsAnalysisOutput,
    "architecture_designer": ArchitectureDesignOutput,
    "code_generator": CodeGenerationOutput,
    "test_generator": TestGenerationOutput,
    "code_reviewer": CodeReviewOutput,
    "security_analyst": SecurityAnalysisOutput,
    "documentation_generator": DocumentationGenerationOutput,
    "project_planner": ProjectPlanOutput,
}


def create_output_model(agent_type: str) -> type[BaseModel]:
    """
    Create an output model for the specified agent type - LangChain compatible.
    
    Args:
        agent_type: The type of agent
        
    Returns:
        Pydantic model class for the agent type
    """
    return MODEL_MAPPING.get(agent_type, CodeGenerationOutput)


def validate_output_model(data: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
    """
    Validate output data against the appropriate model - LangChain compatible.
    
    Args:
        data: Data to validate
        agent_type: Type of agent
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If data doesn't match the model
    """
    model_class = create_output_model(agent_type)
    validated = model_class(**data)
    return validated.model_dump()


def get_format_instructions(agent_type: str) -> str:
    """
    Get format instructions for the specified agent type using LangChain patterns.
    
    Args:
        agent_type: The type of agent
        
    Returns:
        Format instructions string compatible with PydanticOutputParser
    """
    try:
        # Try to use LangChain's PydanticOutputParser for format instructions
        if LANGCHAIN_AVAILABLE:
            model_class = create_output_model(agent_type)
            parser = PydanticOutputParser(pydantic_object=model_class)
            return parser.get_format_instructions()
        
    except Exception as e:
        logger.warning(f"LangChain format instructions failed: {e}")
    
    # Fallback to manual schema generation
    model_class = create_output_model(agent_type)
    schema = model_class.model_json_schema()
    
    instructions = f"""
Please provide your response in the following JSON format for {agent_type}:

{schema}

Ensure your response is valid JSON that matches this schema exactly.
"""
    return instructions


def create_parser(agent_type: str) -> Optional[PydanticOutputParser]:
    """
    Create a LangChain PydanticOutputParser for the specified agent type.
    
    Args:
        agent_type: The type of agent
        
    Returns:
        PydanticOutputParser instance or None if LangChain not available
    """
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain not available, cannot create parser")
        return None
    
    try:
        model_class = create_output_model(agent_type)
        return PydanticOutputParser(pydantic_object=model_class)
    except Exception as e:
        logger.error(f"Failed to create parser for {agent_type}: {e}")
        return None
