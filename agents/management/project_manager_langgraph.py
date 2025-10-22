"""
Project Manager Agent - LangGraph Implementation
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from models.config import AgentConfig
from utils.llm.gemini_client_factory import get_gemini_client

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from agents.management.project_manager import ProjectManager

logger = logging.getLogger(__name__)


class ProjectManagerState(BaseModel):
    """State for Project Manager workflow using Pydantic BaseModel."""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    
    class Config:
        arbitrary_types_allowed = True


class ProjectManagerCoordinator:
    """LangGraph coordinator for Project Manager."""
    
    def __init__(self, gemini_client=None):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph required")
        
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='project_manager',
                model_name='gemini-2.5-flash',
                temperature=0.2
            )
            logger.info("[OK] Project Manager: Created standalone LLM client")
        else:
            logger.info("[OK] Project Manager: Using shared LLM client")
        
        config = AgentConfig(
            agent_id='project_manager',
            name='Project Manager',
            description='Project Manager agent',
            model_name='gemini-2.5-flash'
        )
        self.agent = ProjectManager(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Project Manager Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(ProjectManagerState)
        workflow.add_node("process", self._process)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        return workflow
    
    async def _process(self, state: ProjectManagerState) -> ProjectManagerState:
        try:
            result = await self.agent.execute(state.input_data)
            state.output_data = result
            state.status = "completed"
        except Exception as e:
            state.errors.append(str(e))
            state.status = "failed"
        return state
