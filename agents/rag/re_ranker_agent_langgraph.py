"""
Re Ranker Agent Agent - LangGraph Implementation
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

from agents.rag.re_ranker_agent import ReRankerAgent

logger = logging.getLogger(__name__)


class ReRankerAgentState(BaseModel):
    """State for Re Ranker Agent workflow using Pydantic BaseModel."""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    
    class Config:
        arbitrary_types_allowed = True


class ReRankerAgentCoordinator:
    """LangGraph coordinator for Re Ranker Agent."""
    
    def __init__(self, gemini_client=None):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph required")
        
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='re_ranker_agent',
                model_name='gemini-2.5-flash',
                temperature=0.2
            )
            logger.info("[OK] Re Ranker Agent: Created standalone LLM client")
        else:
            logger.info("[OK] Re Ranker Agent: Using shared LLM client")
        
        config = AgentConfig(
            agent_id='re_ranker_agent',
            name='Re Ranker Agent',
            description='Re Ranker Agent agent',
            model_name='gemini-2.5-flash'
        )
        self.agent = ReRankerAgent(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Re Ranker Agent Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(ReRankerAgentState)
        workflow.add_node("process", self._process)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        return workflow
    
    async def _process(self, state: ReRankerAgentState) -> ReRankerAgentState:
        try:
            result = await self.agent.execute(state.input_data)
            state.output_data = result
            state.status = "completed"
        except Exception as e:
            state.errors.append(str(e))
            state.status = "failed"
        return state
