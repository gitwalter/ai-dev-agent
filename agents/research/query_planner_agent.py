#!/usr/bin/env python3
"""
Query Planner Agent - Research Swarm
=====================================

Plans research strategy and decomposes queries for comprehensive web research.

Responsibilities:
- Decompose complex queries into sub-queries
- Identify key concepts and search terms
- Determine research strategy (broad, focused, multi-stage)
- Estimate required sources and depth

Created: 2025-10-10
Part of: Web Research Swarm
"""

import logging
from typing import Dict, List, Any
import json


# LangGraph integration check
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available - agent will work in legacy mode only")

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

logger = logging.getLogger(__name__)




class QueryPlannerAgentState(BaseModel):
    """State for QueryPlannerAgent LangGraph workflow using Pydantic BaseModel."""
    
    # Input fields
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    
    # Output fields
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    
    # Control fields
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Execution metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

class QueryPlannerAgent(EnhancedBaseAgent):
    """
    Plans research strategy and query decomposition.
    
    This agent analyzes research queries and creates comprehensive research plans
    including sub-queries, key concepts, search terms, and strategy recommendations.
    """
    
    def __init__(self):
        """Initialize Query Planner Agent with Gemini 2.0 Flash."""
        config = AgentConfig(
            agent_id="query_planner",
            agent_type="research",
            prompt_template_id="research_query_planner",
            model_name="gemini-2.0-flash-exp",
            max_retries=2,
            timeout_seconds=30
        )
        super().__init__(config)
        logger.info("QueryPlannerAgent initialized")
    
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            self.logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            self.logger.info("⚠️ LangGraph not available - using legacy mode")

    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task has required query."""
        return isinstance(task, dict) and 'query' in task
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query planning."""
        query = task.get('query', '')
        depth = task.get('depth', 'standard')
        plan = await self.plan_research(query, depth)
        return {'success': True, 'plan': plan}
    
    async def plan_research(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        """
        Create research plan from query.
        
        Args:
            query: Research query to plan
            depth: Research depth (quick, standard, comprehensive, exhaustive)
            
        Returns:
            Research plan with:
            - sub_queries: List[str] - 3-5 decomposed queries
            - key_concepts: List[str] - Key concepts to research
            - search_terms: List[str] - Effective search terms
            - strategy: str - Research strategy (broad, focused, multi-stage)
            - estimated_sources: int - Estimated number of sources needed
        """
        prompt = self._create_planning_prompt(query, depth)
        
        try:
            result = await self.execute_async({"prompt": prompt})
            
            if result.get("success"):
                content = result.get("content", "{}")
                plan = self._extract_json(content)
                
                # Validate plan structure
                plan = self._validate_plan(plan, query)
                
                logger.info(
                    f"Research plan created: {plan.get('strategy')} strategy "
                    f"with {len(plan.get('sub_queries', []))} sub-queries"
                )
                return plan
            else:
                logger.error(f"Query planning failed: {result.get('error')}")
                return self._default_plan(query)
                
        except Exception as e:
            logger.error(f"Query planning error: {e}")
            return self._default_plan(query)
    
    def _create_planning_prompt(self, query: str, depth: str) -> str:
        """Create prompt for query planning."""
        return f"""
You are an expert research strategist. Analyze this research query and create a comprehensive research plan.

Research Query: {query}
Research Depth: {depth}

Please provide a detailed research plan in JSON format with:

1. **sub_queries**: Break down the main query into 3-5 focused sub-queries that cover different aspects
2. **key_concepts**: Identify 5-10 key concepts that should be researched
3. **search_terms**: Generate 5-15 effective search terms optimized for search engines
4. **strategy**: Recommend research strategy:
   - "focused": For simple, specific queries
   - "broad": For exploratory or multi-faceted topics
   - "multi-stage": For complex topics requiring iterative research
5. **estimated_sources**: Estimate how many sources would provide good coverage

Return ONLY valid JSON with this exact structure:
{{
    "sub_queries": ["query1", "query2", ...],
    "key_concepts": ["concept1", "concept2", ...],
    "search_terms": ["term1", "term2", ...],
    "strategy": "focused|broad|multi-stage",
    "estimated_sources": 10
}}
"""
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        try:
            # Remove markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end]
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end]
            
            # Parse JSON
            parsed = json.loads(content.strip())
            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"JSON extraction error: {e}")
            return {}
    
    def _validate_plan(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validate and ensure plan has all required fields."""
        validated = {
            "sub_queries": plan.get("sub_queries", [query]),
            "key_concepts": plan.get("key_concepts", query.split()[:5]),
            "search_terms": plan.get("search_terms", [query]),
            "strategy": plan.get("strategy", "focused"),
            "estimated_sources": plan.get("estimated_sources", 10)
        }
        
        # Ensure strategy is valid
        if validated["strategy"] not in ["focused", "broad", "multi-stage"]:
            validated["strategy"] = "focused"
        
        # Ensure reasonable limits
        validated["sub_queries"] = validated["sub_queries"][:10]
        validated["key_concepts"] = validated["key_concepts"][:15]
        validated["search_terms"] = validated["search_terms"][:20]
        validated["estimated_sources"] = min(max(validated["estimated_sources"], 5), 50)
        
        return validated
    
    def _default_plan(self, query: str) -> Dict[str, Any]:
        """Fallback research plan when LLM fails."""
        words = query.split()
        
        return {
            "sub_queries": [query],
            "key_concepts": words[:5],
            "search_terms": [query] + words[:4],
            "strategy": "focused",
            "estimated_sources": 10
        }
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for QueryPlannerAgent."""
        workflow = StateGraph(QueryPlannerAgentState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: QueryPlannerAgentState) -> QueryPlannerAgentState:
        """Execute agent in LangGraph workflow."""
        import time
        start = time.time()
        
        try:
            # Call the agent's execute method
            result = await self.execute(state.input_data)
            
            # Update state with results
            state.output_data = result
            state.status = "completed"
            state.metrics["execution_time"] = time.time() - start
            
        except Exception as e:
            self.logger.error(f"LangGraph execution failed: {e}")
            state.errors.append(str(e))
            state.status = "failed"
            state.metrics["execution_time"] = time.time() - start
        
        return state


if __name__ == "__main__":
    import asyncio
    
    async def test_query_planner():
        """Test Query Planner Agent."""
        print("🧪 Testing Query Planner Agent\n")
        
        agent = QueryPlannerAgent()
        
        test_query = "How to integrate Google Drive API with Python MCP server?"
        
        plan = await agent.plan_research(test_query, depth="standard")
        
        print(f"✅ Research Plan Created:")
        print(f"   Strategy: {plan['strategy']}")
        print(f"   Sub-queries: {len(plan['sub_queries'])}")
        print(f"   Key concepts: {len(plan['key_concepts'])}")
        print(f"   Search terms: {len(plan['search_terms'])}")
        print(f"   Estimated sources: {plan['estimated_sources']}")
        print(f"\n📋 Plan Details:")
        print(json.dumps(plan, indent=2))
    
    asyncio.run(test_query_planner())


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        
        config = AgentConfig(
            agent_id='query_planner_agent',
            name='QueryPlannerAgent',
            description='QueryPlannerAgent agent',
            model_name='gemini-2.5-flash'
        )
        _default_instance = QueryPlannerAgent()
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
