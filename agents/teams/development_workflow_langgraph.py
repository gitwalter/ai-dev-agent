"""
Development Workflow LangGraph Coordinator.
Orchestrates the complete software development lifecycle using LangGraph.
"""

import logging
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

from agents.development.requirements_analyst_langgraph import RequirementsAnalystCoordinator
from agents.development.architecture_designer_langgraph import ArchitectureDesignerCoordinator
from agents.development.code_generator_langgraph import CodeGeneratorCoordinator
from agents.development.test_generator_langgraph import TestGeneratorCoordinator
from agents.development.code_reviewer_langgraph import CodeReviewerCoordinator
from agents.development.documentation_generator_langgraph import DocumentationGeneratorCoordinator

logger = logging.getLogger(__name__)


class DevelopmentWorkflowState(BaseModel):
    """
    Pydantic-based state for development workflow.
    Using Pydantic provides validation and better type safety.
    """
    # Input
    project_description: str = Field(default="", description="Project description")
    requirements: Optional[Dict[str, Any]] = Field(default=None, description="Analyzed requirements")
    
    # Architecture
    architecture: Optional[Dict[str, Any]] = Field(default=None, description="System architecture")
    
    # Code
    code_files: Dict[str, str] = Field(default_factory=dict, description="Generated code files")
    
    # Testing
    test_files: Dict[str, str] = Field(default_factory=dict, description="Generated test files")
    
    # Review
    review_feedback: List[Dict[str, Any]] = Field(default_factory=list, description="Code review feedback")
    quality_score: float = Field(default=0.0, description="Overall quality score")
    
    # Documentation
    documentation: Dict[str, str] = Field(default_factory=dict, description="Generated documentation")
    
    # Workflow control
    current_phase: Literal["requirements", "architecture", "code", "test", "review", "docs", "complete"] = Field(
        default="requirements", 
        description="Current workflow phase"
    )
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    needs_revision: bool = Field(default=False, description="Whether revision is needed")
    iteration_count: int = Field(default=0, description="Number of iterations")
    max_iterations: int = Field(default=3, description="Maximum iterations")
    
    class Config:
        arbitrary_types_allowed = True


class DevelopmentWorkflowCoordinator:
    """
    LangGraph coordinator for complete software development workflow.
    Orchestrates: Requirements → Architecture → Code → Test → Review → Docs
    """
    
    def __init__(self):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Initialize all development agents
        self.requirements_analyst = RequirementsAnalystCoordinator()
        self.architecture_designer = ArchitectureDesignerCoordinator()
        self.code_generator = CodeGeneratorCoordinator()
        self.test_generator = TestGeneratorCoordinator()
        self.code_reviewer = CodeReviewerCoordinator()
        self.documentation_generator = DocumentationGeneratorCoordinator()
        
        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Development Workflow Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build complete development workflow graph.
        
        Flow:
        1. Analyze Requirements
        2. Design Architecture
        3. Generate Code
        4. Generate Tests
        5. Review Code
        6. Generate Documentation
        7. (Optional) Iterate if review requires changes
        """
        
        workflow = StateGraph(DevelopmentWorkflowState)
        
        # Add all workflow nodes
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        workflow.add_node("design_architecture", self._design_architecture)
        workflow.add_node("generate_code", self._generate_code)
        workflow.add_node("generate_tests", self._generate_tests)
        workflow.add_node("review_code", self._review_code)
        workflow.add_node("generate_documentation", self._generate_documentation)
        workflow.add_node("handle_revision", self._handle_revision)
        
        # Set entry point
        workflow.set_entry_point("analyze_requirements")
        
        # Define workflow edges
        workflow.add_edge("analyze_requirements", "design_architecture")
        workflow.add_edge("design_architecture", "generate_code")
        workflow.add_edge("generate_code", "generate_tests")
        workflow.add_edge("generate_tests", "review_code")
        
        # Conditional edge: review can trigger revision or proceed to docs
        workflow.add_conditional_edges(
            "review_code",
            self._should_revise,
            {
                "revise": "handle_revision",
                "proceed": "generate_documentation"
            }
        )
        
        # Revision can loop back to code generation or exit if max iterations
        workflow.add_conditional_edges(
            "handle_revision",
            self._check_iteration_limit,
            {
                "continue": "generate_code",
                "exit": "generate_documentation"
            }
        )
        
        workflow.add_edge("generate_documentation", END)
        
        return workflow
    
    def _analyze_requirements(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Phase 1: Analyze requirements."""
        logger.info(f"[Phase 1/6] Analyzing requirements for: {state.project_description[:50]}...")
        
        # Invoke requirements analyst
        result = self.requirements_analyst.app.invoke({
            "project_description": state.project_description,
            "requirements": None,
            "errors": [],
            "next_action": "start"
        })
        
        return {
            "requirements": result.get("requirements"),
            "current_phase": "architecture",
            "errors": state.errors + result.get("errors", [])
        }
    
    def _design_architecture(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Phase 2: Design system architecture."""
        logger.info("[Phase 2/6] Designing system architecture...")
        
        result = self.architecture_designer.app.invoke({
            "requirements": state.requirements,
            "architecture": None,
            "errors": [],
            "next_action": "start"
        })
        
        return {
            "architecture": result.get("architecture"),
            "current_phase": "code",
            "errors": state.errors + result.get("errors", [])
        }
    
    def _generate_code(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Phase 3: Generate production code."""
        logger.info(f"[Phase 3/6] Generating code (iteration {state.iteration_count + 1})...")
        
        result = self.code_generator.app.invoke({
            "requirements": state.requirements,
            "architecture": state.architecture,
            "review_feedback": state.review_feedback,
            "code_files": {},
            "errors": [],
            "next_action": "start"
        })
        
        return {
            "code_files": result.get("code_files", {}),
            "current_phase": "test",
            "errors": state.errors + result.get("errors", [])
        }
    
    def _generate_tests(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Phase 4: Generate comprehensive tests."""
        logger.info("[Phase 4/6] Generating comprehensive tests...")
        
        result = self.test_generator.app.invoke({
            "code_files": state.code_files,
            "project_context": state.project_description,
            "test_files": {},
            "coverage_metrics": {},
            "errors": [],
            "next_action": "start"
        })
        
        return {
            "test_files": result.get("test_files", {}),
            "current_phase": "review",
            "errors": state.errors + result.get("errors", [])
        }
    
    def _review_code(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Phase 5: Review code quality and standards."""
        logger.info("[Phase 5/6] Reviewing code quality...")
        
        result = self.code_reviewer.app.invoke({
            "code_files": state.code_files,
            "project_context": state.project_description,
            "review_feedback": [],
            "quality_score": 0.0,
            "issues_found": [],
            "suggestions": [],
            "errors": [],
            "next_action": "start"
        })
        
        review_feedback = result.get("review_feedback", [])
        quality_score = result.get("quality_score", 0.0)
        
        # Determine if revision is needed (quality score < 0.8)
        needs_revision = quality_score < 0.8 and state.iteration_count < state.max_iterations
        
        return {
            "review_feedback": review_feedback,
            "quality_score": quality_score,
            "needs_revision": needs_revision,
            "current_phase": "docs" if not needs_revision else "review",
            "errors": state.errors + result.get("errors", [])
        }
    
    def _generate_documentation(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Phase 6: Generate comprehensive documentation."""
        logger.info("[Phase 6/6] Generating documentation...")
        
        result = self.documentation_generator.app.invoke({
            "code_files": state.code_files,
            "project_context": state.project_description,
            "architecture": state.architecture,
            "documents": {},
            "errors": [],
            "next_action": "start"
        })
        
        return {
            "documentation": result.get("documents", {}),
            "current_phase": "complete",
            "errors": state.errors + result.get("errors", [])
        }
    
    def _handle_revision(self, state: DevelopmentWorkflowState) -> Dict[str, Any]:
        """Handle code revision based on review feedback."""
        logger.info(f"Handling revision (iteration {state.iteration_count + 1}/{state.max_iterations})...")
        
        return {
            "iteration_count": state.iteration_count + 1,
            "needs_revision": False,
            "current_phase": "code"
        }
    
    def _should_revise(self, state: DevelopmentWorkflowState) -> str:
        """Determine if code needs revision."""
        if state.needs_revision:
            logger.info(f"Quality score {state.quality_score:.2f} < 0.8 - revision needed")
            return "revise"
        logger.info(f"Quality score {state.quality_score:.2f} >= 0.8 - proceeding")
        return "proceed"
    
    def _check_iteration_limit(self, state: DevelopmentWorkflowState) -> str:
        """Check if iteration limit reached."""
        if state.iteration_count >= state.max_iterations:
            logger.warning(f"Max iterations ({state.max_iterations}) reached - exiting revision loop")
            return "exit"
        return "continue"


coordinator = DevelopmentWorkflowCoordinator()

