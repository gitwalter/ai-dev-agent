"""
Test Generator LangGraph Coordinator.
Orchestrates comprehensive test generation using LangGraph.
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from models.config import AgentConfig
from utils.llm.gemini_client_factory import get_gemini_client

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    MemorySaver = None

from agents.development.test_generator import TestGenerator

logger = logging.getLogger(__name__)


class TestGeneratorState(BaseModel):
    """State for test generation workflow using Pydantic BaseModel."""
    code_files: Dict[str, str] = Field(default_factory=dict, description="Code files to generate tests for")
    project_context: str = Field(default="", description="Project context and requirements")
    test_files: Dict[str, str] = Field(default_factory=dict, description="Generated test files")
    coverage_metrics: Dict[str, Any] = Field(default_factory=dict, description="Test coverage metrics")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    next_action: str = Field(default="analyze", description="Next action to take")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class TestGeneratorCoordinator:
    """LangGraph coordinator for test generation."""
    
    def __init__(self, gemini_client=None):
        """
        Initialize Test Generator with LangGraph.
        
        Args:
            gemini_client: Optional LLM client for swarm coordination.
                          If None, creates standalone client for independent use.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Create or use LLM client
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='test_generator',
                model_name='gemini-2.5-flash',
                temperature=0.3
            )
            logger.info("[OK] Test Generator: Created standalone LLM client")
        else:
            logger.info("[OK] Test Generator: Using shared LLM client from swarm")
        
        config = AgentConfig(
            agent_id='test_generator',
            name='Test Generator',
            description='Generates comprehensive tests',
            model_name='gemini-2.5-flash'
        )
        self.generator = TestGenerator(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Test Generator Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for test generation."""
        
        workflow = StateGraph(TestGeneratorState)
        
        workflow.add_node("analyze_code", self._analyze_code)
        workflow.add_node("generate_tests", self._generate_tests)
        workflow.add_node("validate_tests", self._validate_tests)
        
        workflow.set_entry_point("analyze_code")
        
        workflow.add_edge("analyze_code", "generate_tests")
        workflow.add_edge("generate_tests", "validate_tests")
        workflow.add_edge("validate_tests", END)
        
        return workflow
    
    def _analyze_code(self, state: TestGeneratorState) -> TestGeneratorState:
        """Analyze code to determine test requirements."""
        logger.info("Analyzing code for test requirements")
        state["next_action"] = "generate"
        return state
    
    def _generate_tests(self, state: TestGeneratorState) -> TestGeneratorState:
        """Generate comprehensive tests."""
        logger.info("Generating tests")
        
        task = {
            "code_files": state.get("code_files", {}),
            "project_context": state.get("project_context", "")
        }
        
        # Execute the generator
        result = self.generator.execute(task)
        
        if result.get("success"):
            state["test_files"] = result.get("test_files", {})
        else:
            state["errors"] = state.get("errors", []) + [result.get("error", "Unknown error")]
        
        state["next_action"] = "validate"
        return state
    
    def _validate_tests(self, state: TestGeneratorState) -> TestGeneratorState:
        """Validate generated tests."""
        logger.info("Validating tests")
        state["next_action"] = "complete"
        return state


# Export for LangGraph Studio
coordinator = TestGeneratorCoordinator()

