"""
Simplified response models for the AI Development Agent system.
These models provide cleaner, more maintainable alternatives to the complex response formats.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Requirements Analyst - Simplified Models
# ============================================================================

class SimplifiedRequirement(BaseModel):
    """Simplified requirement model."""
    id: str = Field(..., description="Unique requirement identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed requirement description")
    type: str = Field(..., description="Requirement type: functional, non_functional, user_story")
    priority: str = Field(..., description="Priority level: low, medium, high")
    status: str = Field(default="draft", description="Requirement status")

class SimplifiedRequirementsResponse(BaseModel):
    """Simplified requirements analysis response."""
    requirements: List[SimplifiedRequirement] = Field(..., description="List of requirements")
    technical_constraints: List[str] = Field(default_factory=list, description="Technical constraints")
    assumptions: List[str] = Field(default_factory=list, description="Project assumptions")
    risks: List[str] = Field(default_factory=list, description="Project risks")
    quality_gate_passed: bool = Field(default=True, description="Quality gate status")


# ============================================================================
# Architecture Designer - Simplified Models
# ============================================================================

class SimplifiedComponent(BaseModel):
    """Simplified component model."""
    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    technology: str = Field(..., description="Technology used for this component")
    responsibilities: List[str] = Field(..., description="Component responsibilities")

class SimplifiedArchitectureResponse(BaseModel):
    """Simplified architecture design response."""
    architecture_type: str = Field(..., description="Architecture type: monolithic, microservices, layered")
    components: List[SimplifiedComponent] = Field(..., description="System components")
    technology_stack: dict = Field(..., description="Technology stack by category")
    security_measures: List[str] = Field(default_factory=list, description="Security measures")
    deployment_approach: str = Field(..., description="Deployment strategy")
    quality_gate_passed: bool = Field(default=True, description="Quality gate status")


# ============================================================================
# Code Generator - Simplified Models
# ============================================================================

class SimplifiedCodeFile(BaseModel):
    """Simplified code file model."""
    filename: str = Field(..., description="File name")
    content: str = Field(..., description="File content")
    file_type: str = Field(..., description="File type: source, config, test, docs")

class SimplifiedCodeResponse(BaseModel):
    """Simplified code generation response."""
    files: List[SimplifiedCodeFile] = Field(..., description="Generated files")
    dependencies: List[str] = Field(default_factory=list, description="Project dependencies")
    build_instructions: str = Field(..., description="Build instructions")
    run_instructions: str = Field(..., description="Run instructions")
    quality_gate_passed: bool = Field(default=True, description="Quality gate status")


# ============================================================================
# Test Generator - Simplified Models
# ============================================================================

class SimplifiedTestFile(BaseModel):
    """Simplified test file model."""
    filename: str = Field(..., description="Test file name")
    content: str = Field(..., description="Test file content")
    test_type: str = Field(..., description="Test type: unit, integration, e2e")

class SimplifiedTestResponse(BaseModel):
    """Simplified test generation response."""
    test_files: List[SimplifiedTestFile] = Field(..., description="Generated test files")
    test_framework: str = Field(..., description="Testing framework used")
    run_command: str = Field(..., description="Command to run tests")
    coverage_target: str = Field(..., description="Coverage target percentage")
    quality_gate_passed: bool = Field(default=True, description="Quality gate status")


# ============================================================================
# Code Reviewer - Simplified Models
# ============================================================================

class SimplifiedIssue(BaseModel):
    """Simplified issue model."""
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    severity: str = Field(..., description="Severity: low, medium, high, critical")
    category: str = Field(..., description="Category: security, performance, style, bug")
    suggestion: str = Field(..., description="Suggested fix")

class SimplifiedReviewResponse(BaseModel):
    """Simplified code review response."""
    overall_score: float = Field(..., ge=1, le=10, description="Overall code quality score (1-10)")
    issues: List[SimplifiedIssue] = Field(default_factory=list, description="Found issues")
    quality_gate_passed: bool = Field(default=True, description="Quality gate status")


# ============================================================================
# Security Analyst - Simplified Models
# ============================================================================

class SimplifiedVulnerability(BaseModel):
    """Simplified vulnerability model."""
    title: str = Field(..., description="Vulnerability title")
    description: str = Field(..., description="Vulnerability description")
    severity: str = Field(..., description="Severity: low, medium, high, critical")
    affected_component: str = Field(..., description="Affected component")
    fix: str = Field(..., description="Fix description")

class SimplifiedSecurityResponse(BaseModel):
    """Simplified security analysis response."""
    security_score: float = Field(..., ge=1, le=10, description="Security score (1-10)")
    vulnerabilities: List[SimplifiedVulnerability] = Field(default_factory=list, description="Found vulnerabilities")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    security_gate_passed: bool = Field(default=True, description="Security gate status")


# ============================================================================
# Documentation Generator - Simplified Models
# ============================================================================

class SimplifiedDocument(BaseModel):
    """Simplified document model."""
    filename: str = Field(..., description="Document filename")
    content: str = Field(..., description="Document content")
    doc_type: str = Field(..., description="Document type: readme, api, user_guide, deployment")

class SimplifiedDocumentationResponse(BaseModel):
    """Simplified documentation generation response."""
    documents: List[SimplifiedDocument] = Field(..., description="Generated documents")
    coverage_score: float = Field(..., ge=1, le=10, description="Documentation coverage score (1-10)")
    documentation_gate_passed: bool = Field(default=True, description="Documentation gate status")


# ============================================================================
# Common Models
# ============================================================================

class SimplifiedAgentResponse(BaseModel):
    """Simplified agent response wrapper."""
    agent_name: str = Field(..., description="Agent name")
    task_name: str = Field(..., description="Task name")
    status: str = Field(..., description="Task status: completed, failed, pending")
    output: dict = Field(..., description="Agent output data")
    execution_time: float = Field(..., description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    quality_gate_passed: bool = Field(default=True, description="Quality gate status")


# ============================================================================
# Response Factory Functions
# ============================================================================

def create_simplified_requirements_response(
    requirements: List[SimplifiedRequirement],
    technical_constraints: List[str] = None,
    assumptions: List[str] = None,
    risks: List[str] = None,
    quality_gate_passed: bool = True
) -> SimplifiedRequirementsResponse:
    """Create a simplified requirements response."""
    return SimplifiedRequirementsResponse(
        requirements=requirements,
        technical_constraints=technical_constraints or [],
        assumptions=assumptions or [],
        risks=risks or [],
        quality_gate_passed=quality_gate_passed
    )


def create_simplified_architecture_response(
    architecture_type: str,
    components: List[SimplifiedComponent],
    technology_stack: dict,
    security_measures: List[str] = None,
    deployment_approach: str = "",
    quality_gate_passed: bool = True
) -> SimplifiedArchitectureResponse:
    """Create a simplified architecture response."""
    return SimplifiedArchitectureResponse(
        architecture_type=architecture_type,
        components=components,
        technology_stack=technology_stack,
        security_measures=security_measures or [],
        deployment_approach=deployment_approach,
        quality_gate_passed=quality_gate_passed
    )


def create_simplified_code_response(
    files: List[SimplifiedCodeFile],
    dependencies: List[str] = None,
    build_instructions: str = "",
    run_instructions: str = "",
    quality_gate_passed: bool = True
) -> SimplifiedCodeResponse:
    """Create a simplified code response."""
    return SimplifiedCodeResponse(
        files=files,
        dependencies=dependencies or [],
        build_instructions=build_instructions,
        run_instructions=run_instructions,
        quality_gate_passed=quality_gate_passed
    )


def create_simplified_test_response(
    test_files: List[SimplifiedTestFile],
    test_framework: str,
    run_command: str,
    coverage_target: str = "80%",
    quality_gate_passed: bool = True
) -> SimplifiedTestResponse:
    """Create a simplified test response."""
    return SimplifiedTestResponse(
        test_files=test_files,
        test_framework=test_framework,
        run_command=run_command,
        coverage_target=coverage_target,
        quality_gate_passed=quality_gate_passed
    )


def create_simplified_review_response(
    overall_score: float,
    issues: List[SimplifiedIssue] = None,
    quality_gate_passed: bool = True
) -> SimplifiedReviewResponse:
    """Create a simplified review response."""
    return SimplifiedReviewResponse(
        overall_score=overall_score,
        issues=issues or [],
        quality_gate_passed=quality_gate_passed
    )


def create_simplified_security_response(
    security_score: float,
    vulnerabilities: List[SimplifiedVulnerability] = None,
    recommendations: List[str] = None,
    security_gate_passed: bool = True
) -> SimplifiedSecurityResponse:
    """Create a simplified security response."""
    return SimplifiedSecurityResponse(
        security_score=security_score,
        vulnerabilities=vulnerabilities or [],
        recommendations=recommendations or [],
        security_gate_passed=security_gate_passed
    )


def create_simplified_documentation_response(
    documents: List[SimplifiedDocument],
    coverage_score: float,
    documentation_gate_passed: bool = True
) -> SimplifiedDocumentationResponse:
    """Create a simplified documentation response."""
    return SimplifiedDocumentationResponse(
        documents=documents,
        coverage_score=coverage_score,
        documentation_gate_passed=documentation_gate_passed
    )


def create_simplified_agent_response(
    agent_name: str,
    task_name: str,
    status: str,
    output: dict,
    execution_time: float,
    error_message: str = None,
    quality_gate_passed: bool = True
) -> SimplifiedAgentResponse:
    """Create a simplified agent response."""
    return SimplifiedAgentResponse(
        agent_name=agent_name,
        task_name=task_name,
        status=status,
        output=output,
        execution_time=execution_time,
        error_message=error_message,
        quality_gate_passed=quality_gate_passed
    )
