"""
Documentation Generator LangGraph Coordinator.
Orchestrates comprehensive documentation generation using LangGraph.
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

from agents.development.documentation_generator import DocumentationGenerator

logger = logging.getLogger(__name__)


class DocumentationGeneratorState(BaseModel):
    """State for documentation generation workflow using Pydantic BaseModel."""
    code_files: Dict[str, str] = Field(default_factory=dict, description="Code files to document")
    project_context: str = Field(default="", description="Project context")
    architecture: Dict[str, Any] = Field(default_factory=dict, description="Architecture information")
    documents: Dict[str, str] = Field(default_factory=dict, description="Generated documents")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    next_action: str = Field(default="analyze", description="Next action")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class DocumentationGeneratorCoordinator:
    """LangGraph coordinator for documentation generation."""
    
    def __init__(self, gemini_client=None):
        """
        Initialize Documentation Generator with LangGraph.
        
        Args:
            gemini_client: Optional LLM client for swarm coordination.
                          If None, creates standalone client for independent use.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Create or use LLM client
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='documentation_generator',
                model_name='gemini-2.5-flash',
                temperature=0.3
            )
            logger.info("[OK] Documentation Generator: Created standalone LLM client")
        else:
            logger.info("[OK] Documentation Generator: Using shared LLM client from swarm")
        
        config = AgentConfig(
            agent_id='documentation_generator',
            name='Documentation Generator',
            description='Generates comprehensive documentation',
            model_name='gemini-2.5-flash'
        )
        self.generator = DocumentationGenerator(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Documentation Generator Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for documentation generation."""
        
        workflow = StateGraph(DocumentationGeneratorState)
        
        workflow.add_node("analyze_content", self._analyze_content)
        workflow.add_node("generate_docs", self._generate_docs)
        workflow.add_node("validate_docs", self._validate_docs)
        
        workflow.set_entry_point("analyze_content")
        
        workflow.add_edge("analyze_content", "generate_docs")
        workflow.add_edge("generate_docs", "validate_docs")
        workflow.add_edge("validate_docs", END)
        
        return workflow
    
    def _analyze_content(self, state: DocumentationGeneratorState) -> DocumentationGeneratorState:
        """Analyze content for documentation."""
        logger.info("Analyzing content")
        state["next_action"] = "generate"
        return state
    
    def _generate_docs(self, state: DocumentationGeneratorState) -> DocumentationGeneratorState:
        """Generate documentation."""
        logger.info("Generating documentation")
        
        task = {
            "code_files": state.get("code_files", {}),
            "project_context": state.get("project_context", ""),
            "architecture": state.get("architecture", {})
        }
        
        result = self.generator.execute(task)
        
        if result.get("success"):
            state["documents"] = result.get("documents", {})
        else:
            state["errors"] = state.get("errors", []) + [result.get("error", "Unknown error")]
        
        state["next_action"] = "validate"
        return state
    
    def _validate_docs(self, state: DocumentationGeneratorState) -> DocumentationGeneratorState:
        """Validate generated documentation."""
        logger.info("Validating documentation")
        state["next_action"] = "complete"
        return state


coordinator = DocumentationGeneratorCoordinator()

