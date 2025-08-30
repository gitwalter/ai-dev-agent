"""
Mock structured outputs for testing - bypasses syntax errors in utils/structured_outputs.py
"""

from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime

# Mock the key classes that tests need - 100% Pydantic V2 compliant
class CodeQualityScore(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    score: float
    reasoning: str
    recommendations: List[str]

class Issue(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    severity: str
    description: str
    location: str
    suggestion: str

class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    priority: str
    description: str
    impact: str

class SourceFile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    filename: str
    content: str
    file_type: str
    description: str

class ConfigurationFile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    filename: str
    content: str
    file_type: str
    description: str

class TestFile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    filename: str
    content: str
    test_type: str
    coverage: str

class DocumentationFile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    filename: str
    content: str
    doc_type: str
    audience: str

class RequirementsAnalysisOutput(BaseModel):
    """Mock requirements analysis output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    functional_requirements: List[Dict[str, Any]] = []
    non_functional_requirements: List[Dict[str, Any]] = []
    user_stories: List[Dict[str, Any]] = []
    technical_constraints: List[str] = []
    assumptions: List[str] = []
    risks: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}

class ArchitectureDesignOutput(BaseModel):
    """Mock architecture design output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    architecture_design: Dict[str, Any] = {}
    quality_score: Optional[CodeQualityScore] = None
    issues: List[Issue] = []
    recommendations: List[Recommendation] = []

class CodeGenerationOutput(BaseModel):
    """Mock code generation output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    source_files: Dict[str, SourceFile] = {}
    configuration_files: Dict[str, ConfigurationFile] = {}
    test_files: Dict[str, TestFile] = {}
    documentation_files: Dict[str, DocumentationFile] = {}
    project_structure: List[str] = []
    implementation_notes: List[str] = []
    testing_strategy: Dict[str, str] = {}
    deployment_instructions: List[str] = []
    quality_score: Optional[CodeQualityScore] = None
    issues: List[Issue] = []
    recommendations: List[Recommendation] = []

class TestGenerationOutput(BaseModel):
    """Mock test generation output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    test_files: Dict[str, TestFile] = {}
    test_coverage: Dict[str, float] = {}
    quality_score: Optional[CodeQualityScore] = None
    issues: List[Issue] = []
    recommendations: List[Recommendation] = []

class CodeReviewOutput(BaseModel):
    """Mock code review output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    review_summary: str = ""
    issues: List[Issue] = []
    recommendations: List[Recommendation] = []
    quality_score: Optional[CodeQualityScore] = None

class SecurityAnalysisOutput(BaseModel):
    """Mock security analysis output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    security_findings: List[Dict[str, Any]] = []
    risk_assessment: str = ""
    recommendations: List[Recommendation] = []
    quality_score: Optional[CodeQualityScore] = None

class DocumentationGenerationOutput(BaseModel):
    """Mock documentation generation output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    documentation_files: Dict[str, DocumentationFile] = {}
    documentation_coverage: Dict[str, float] = {}
    quality_score: Optional[CodeQualityScore] = None
    issues: List[Issue] = []
    recommendations: List[Recommendation] = []

class ProjectPlanOutput(BaseModel):
    """Mock project plan output"""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    project_plan: Dict[str, Any] = {}
    timeline: List[Dict[str, Any]] = []
    quality_score: Optional[CodeQualityScore] = None
    issues: List[Issue] = []
    recommendations: List[Recommendation] = []
