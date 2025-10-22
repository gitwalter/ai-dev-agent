"""
Code Reviewer LangGraph Coordinator.
Orchestrates comprehensive code review using LangGraph.
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from models.config import AgentConfig
from utils.llm.gemini_client_factory import get_gemini_client

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

from agents.development.code_reviewer import CodeReviewer

logger = logging.getLogger(__name__)


class CodeReviewerState(BaseModel):
    """State for code review workflow using Pydantic BaseModel."""
    code_files: Dict[str, str] = Field(default_factory=dict, description="Code files to review")
    project_context: str = Field(default="", description="Project context")
    review_feedback: List[Dict[str, Any]] = Field(default_factory=list, description="Review feedback")
    quality_score: float = Field(default=0.0, description="Overall quality score")
    issues_found: List[str] = Field(default_factory=list, description="Issues found")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    next_action: str = Field(default="analyze", description="Next action")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class CodeReviewerCoordinator:
    """LangGraph coordinator for code review."""
    
    def __init__(self, gemini_client=None):
        """
        Initialize Code Reviewer with LangGraph.
        
        Args:
            gemini_client: Optional LLM client for swarm coordination.
                          If None, creates standalone client for independent use.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Create or use LLM client
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='code_reviewer',
                model_name='gemini-2.5-flash',
                temperature=0.2
            )
            logger.info("[OK] Code Reviewer: Created standalone LLM client")
        else:
            logger.info("[OK] Code Reviewer: Using shared LLM client from swarm")
        
        config = AgentConfig(
            agent_id='code_reviewer',
            name='Code Reviewer',
            description='Reviews code quality and standards',
            model_name='gemini-2.5-flash'
        )
        self.reviewer = CodeReviewer(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Code Reviewer Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for code review."""
        
        workflow = StateGraph(CodeReviewerState)
        
        workflow.add_node("analyze_structure", self._analyze_structure)
        workflow.add_node("review_quality", self._review_quality)
        workflow.add_node("check_standards", self._check_standards)
        workflow.add_node("generate_feedback", self._generate_feedback)
        
        workflow.set_entry_point("analyze_structure")
        
        workflow.add_edge("analyze_structure", "review_quality")
        workflow.add_edge("review_quality", "check_standards")
        workflow.add_edge("check_standards", "generate_feedback")
        workflow.add_edge("generate_feedback", END)
        
        return workflow
    
    def _analyze_structure(self, state: CodeReviewerState) -> CodeReviewerState:
        """Analyze code structure."""
        logger.info("Analyzing code structure")
        state["next_action"] = "quality"
        return state
    
    def _review_quality(self, state: CodeReviewerState) -> CodeReviewerState:
        """Review code quality."""
        logger.info("Reviewing code quality")
        
        task = {
            "code_files": state.get("code_files", {}),
            "project_context": state.get("project_context", "")
        }
        
        result = self.reviewer.execute(task)
        
        if result.get("success"):
            state["review_feedback"] = result.get("review_feedback", [])
            state["quality_score"] = result.get("quality_score", 0.0)
        else:
            state["errors"] = state.get("errors", []) + [result.get("error", "Unknown error")]
        
        state["next_action"] = "standards"
        return state
    
    def _check_standards(self, state: CodeReviewerState) -> CodeReviewerState:
        """Check coding standards compliance."""
        logger.info("Checking coding standards")
        state["next_action"] = "feedback"
        return state
    
    def _generate_feedback(self, state: CodeReviewerState) -> CodeReviewerState:
        """Generate review feedback."""
        logger.info("Generating feedback")
        state["next_action"] = "complete"
        return state


coordinator = CodeReviewerCoordinator()

