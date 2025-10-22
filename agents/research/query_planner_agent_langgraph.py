"""
Query Planner Agent Agent - LangGraph Implementation
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

from agents.research.query_planner_agent import QueryPlannerAgent

logger = logging.getLogger(__name__)


class QueryPlannerAgentState(BaseModel):
    """State for Query Planner Agent workflow using Pydantic BaseModel."""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    
    class Config:
        arbitrary_types_allowed = True


class QueryPlannerAgentCoordinator:
    """LangGraph coordinator for Query Planner Agent."""
    
    def __init__(self, gemini_client=None):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph required")
        
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='query_planner_agent',
                model_name='gemini-2.5-flash',
                temperature=0.2
            )
            logger.info("[OK] Query Planner Agent: Created standalone LLM client")
        else:
            logger.info("[OK] Query Planner Agent: Using shared LLM client")
        
        config = AgentConfig(
            agent_id='query_planner_agent',
            name='Query Planner Agent',
            description='Query Planner Agent agent',
            model_name='gemini-2.5-flash'
        )
        self.agent = QueryPlannerAgent(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Query Planner Agent Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(QueryPlannerAgentState)
        workflow.add_node("process", self._process)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        return workflow
    
    async def _process(self, state: QueryPlannerAgentState) -> QueryPlannerAgentState:
        try:
            result = await self.agent.execute(state.input_data)
            state.output_data = result
            state.status = "completed"
        except Exception as e:
            state.errors.append(str(e))
            state.status = "failed"
        return state
