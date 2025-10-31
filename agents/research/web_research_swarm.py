#!/usr/bin/env python3
"""
Web Research Swarm Coordinator - LangGraph Architecture
========================================================

Multi-agent web research system using LangGraph for comprehensive
internet research, parsing, and synthesis.

This coordinator orchestrates 5 specialized agents:
1. QueryPlannerAgent - Plans research strategy
2. WebSearchAgent - Executes web searches
3. ContentParserAgent - Parses and extracts information
4. VerificationAgent - Verifies information quality and reliability
5. SynthesisAgent - Synthesizes findings into comprehensive report

Created: 2025-10-10
Sprint: US-RAG-001 Enhancement
Architecture: Matches RAG Swarm pattern
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Annotated
try:
    from typing_extensions import TypedDict  # Python < 3.12 compatibility
except ImportError:
    from typing import TypedDict  # Python >= 3.12
from datetime import datetime

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

# Import specialized research agents
from agents.research.query_planner_agent import QueryPlannerAgent
from agents.research.web_search_agent import WebSearchAgent
from agents.research.content_parser_agent import ContentParserAgent
from agents.research.verification_agent import VerificationAgent
from agents.research.synthesis_agent import SynthesisAgent

logger = logging.getLogger(__name__)


# ============================================================================
# Research Swarm State Definition
# ============================================================================

class ResearchSwarmState(TypedDict):
    """State passed between research agents in LangGraph workflow."""
    
    # Input
    query: str
    max_sources: int
    research_depth: str  # quick, standard, comprehensive, exhaustive
    
    # Stage outputs
    research_plan: Annotated[Dict[str, Any], "QueryPlannerAgent output"]
    search_results: Annotated[List[Dict], "WebSearchAgent output"]
    parsed_content: Annotated[List[Dict], "ContentParserAgent output"]
    verification_report: Annotated[Dict[str, Any], "VerificationAgent output"]
    final_synthesis: Annotated[Dict[str, Any], "SynthesisAgent output"]
    
    # Control flow
    stages_completed: Annotated[List[str], "Completed pipeline stages"]
    needs_additional_search: Annotated[bool, "Whether more search is needed"]
    
    # Metrics
    metrics: Annotated[Dict[str, float], "Pipeline timing metrics"]


# ============================================================================
# Research Swarm Coordinator (LangGraph)
# ============================================================================

class WebResearchSwarmCoordinator:
    """
    Web Research Agent Swarm using LangGraph for proper tracing.
    
    Orchestrates 5 specialized agents in a LangGraph workflow with:
    - Full LangSmith visibility of agent handoffs
    - Conditional re-search based on quality assessment
    - Comprehensive metrics tracking
    - State management via LangGraph
    """
    
    def __init__(self):
        """Initialize research swarm with LangGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            raise ImportError(
                "LangGraph is required for research swarm. "
                "Install with: pip install langgraph"
            )
        
        # Initialize specialized agents
        self.query_planner = QueryPlannerAgent()
        self.web_search = WebSearchAgent()
        self.content_parser = ContentParserAgent()
        self.verification = VerificationAgent()
        self.synthesis = SynthesisAgent()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info(
            "✅ Web Research Swarm Coordinator initialized with 5 specialized agents "
            "(QueryPlanner, WebSearch, ContentParser, Verification, Synthesis)"
        )
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for research pipeline."""
        workflow = StateGraph(ResearchSwarmState)
        
        # Add nodes (agents)
        workflow.add_node("query_planning", self._query_planning_node)
        workflow.add_node("web_search", self._web_search_node)
        workflow.add_node("content_parsing", self._content_parsing_node)
        workflow.add_node("verification", self._verification_node)
        workflow.add_node("synthesis", self._synthesis_node)
        
        # Define edges (workflow)
        workflow.set_entry_point("query_planning")
        workflow.add_edge("query_planning", "web_search")
        workflow.add_edge("web_search", "content_parsing")
        workflow.add_edge("content_parsing", "verification")
        
        # Conditional edge: re-search if quality insufficient
        workflow.add_conditional_edges(
            "verification",
            self._should_re_search,
            {
                "re_search": "web_search",
                "synthesize": "synthesis"
            }
        )
        
        workflow.add_edge("synthesis", END)
        
        return workflow
    
    # ========================================================================
    # Agent Nodes
    # ========================================================================
    
    async def _query_planning_node(self, state: ResearchSwarmState) -> ResearchSwarmState:
        """Query planning agent node."""
        start_time = datetime.now()
        
        logger.info(f"[QueryPlanner] Planning research for: {state['query']}")
        
        plan = await self.query_planner.plan_research(
            state["query"],
            state.get("research_depth", "standard")
        )
        
        state["research_plan"] = plan
        state["stages_completed"].append("query_planning")
        state["metrics"]["query_planning_time"] = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"[QueryPlanner] ✅ Plan created: {plan.get('strategy')} strategy, "
            f"{len(plan.get('sub_queries', []))} sub-queries"
        )
        
        return state
    
    async def _web_search_node(self, state: ResearchSwarmState) -> ResearchSwarmState:
        """Web search agent node."""
        start_time = datetime.now()
        
        search_terms = state["research_plan"].get("search_terms", [state["query"]])
        
        logger.info(f"[WebSearch] Searching {len(search_terms)} terms...")
        
        results = await self.web_search.search(search_terms, state["max_sources"])
        
        state["search_results"] = results
        state["stages_completed"].append("web_search")
        state["metrics"]["web_search_time"] = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"[WebSearch] ✅ Found {len(results)} sources")
        
        return state
    
    async def _content_parsing_node(self, state: ResearchSwarmState) -> ResearchSwarmState:
        """Content parsing agent node."""
        start_time = datetime.now()
        
        logger.info(f"[ContentParser] Parsing {len(state['search_results'])} sources...")
        
        parsed = await self.content_parser.parse_content(state["search_results"])
        
        state["parsed_content"] = parsed
        state["stages_completed"].append("content_parsing")
        state["metrics"]["content_parsing_time"] = (datetime.now() - start_time).total_seconds()
        
        key_points_total = sum(len(p.get("key_points", [])) for p in parsed)
        logger.info(f"[ContentParser] ✅ Parsed {len(parsed)} items, {key_points_total} key points")
        
        return state
    
    async def _verification_node(self, state: ResearchSwarmState) -> ResearchSwarmState:
        """Verification agent node."""
        start_time = datetime.now()
        
        logger.info(f"[Verification] Verifying {len(state['parsed_content'])} sources...")
        
        report = await self.verification.verify(
            state["parsed_content"],
            state["query"],
            quality_threshold=0.7
        )
        
        state["verification_report"] = report
        state["needs_additional_search"] = report.get("needs_additional_search", False)
        state["stages_completed"].append("verification")
        state["metrics"]["verification_time"] = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"[Verification] ✅ {report['verified_sources']}/{report['total_sources']} verified, "
            f"Quality: {report['quality_score']:.2f}, Need more: {state['needs_additional_search']}"
        )
        
        return state
    
    async def _synthesis_node(self, state: ResearchSwarmState) -> ResearchSwarmState:
        """Synthesis agent node."""
        start_time = datetime.now()
        
        verified_content = state["verification_report"].get("verified_content", [])
        
        logger.info(f"[Synthesis] Synthesizing {len(verified_content)} verified sources...")
        
        synthesis = await self.synthesis.synthesize(
            state["query"],
            verified_content,
            state["research_plan"]
        )
        
        state["final_synthesis"] = synthesis
        state["stages_completed"].append("synthesis")
        state["metrics"]["synthesis_time"] = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"[Synthesis] ✅ Report complete: {len(synthesis.get('key_findings', []))} findings, "
            f"Confidence: {synthesis.get('confidence_level')}"
        )
        
        return state
    
    # ========================================================================
    # Control Flow
    # ========================================================================
    
    def _should_re_search(self, state: ResearchSwarmState) -> str:
        """Determine if additional search is needed."""
        # Only allow one re-search to prevent infinite loops
        search_count = state["stages_completed"].count("web_search")
        
        if state.get("needs_additional_search") and search_count < 2:
            logger.info("[Control] 🔄 Triggering re-search for better quality")
            return "re_search"
        
        logger.info("[Control] ➡️ Proceeding to synthesis")
        return "synthesize"
    
    # ========================================================================
    # Public API
    # ========================================================================
    
    async def research(
        self,
        query: str,
        max_sources: int = 10,
        research_depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Execute web research using agent swarm.
        
        Args:
            query: Research query
            max_sources: Maximum sources to collect (default: 10)
            research_depth: Research depth (quick, standard, comprehensive, exhaustive)
            
        Returns:
            Complete research report with:
            - query: Original query
            - synthesis: Comprehensive research report
            - verification_report: Quality and verification details
            - stages_completed: List of completed pipeline stages
            - metrics: Performance metrics for each stage
            - success: Boolean indicating success
        """
        pipeline_start = datetime.now()
        
        logger.info(f"🔬 Starting research swarm for: {query}")
        logger.info(f"   Max sources: {max_sources}, Depth: {research_depth}")
        
        # Initialize state
        initial_state: ResearchSwarmState = {
            "query": query,
            "max_sources": max_sources,
            "research_depth": research_depth,
            "research_plan": {},
            "search_results": [],
            "parsed_content": [],
            "verification_report": {},
            "final_synthesis": {},
            "stages_completed": [],
            "needs_additional_search": False,
            "metrics": {}
        }
        
        try:
            # Execute LangGraph workflow
            config = {"configurable": {"thread_id": f"research_{datetime.now().timestamp()}"}}
            final_state = await self.app.ainvoke(initial_state, config)
            
            # Calculate total time
            total_time = (datetime.now() - pipeline_start).total_seconds()
            final_state["metrics"]["total_time"] = total_time
            
            logger.info(
                f"✅ Research complete: {len(final_state['stages_completed'])} stages "
                f"in {total_time:.2f}s"
            )
            
            return {
                "query": query,
                "synthesis": final_state["final_synthesis"],
                "verification_report": final_state["verification_report"],
                "research_plan": final_state["research_plan"],
                "stages_completed": final_state["stages_completed"],
                "metrics": final_state["metrics"],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Research swarm failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "success": False,
                "metrics": {"total_time": (datetime.now() - pipeline_start).total_seconds()}
            }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    async def test_research_swarm():
        """Test research swarm coordinator."""
        print("🧪 Testing Web Research Swarm Coordinator\n")
        
        coordinator = WebResearchSwarmCoordinator()
        
        result = await coordinator.research(
            query="How to integrate Google Drive API with Python MCP server?",
            max_sources=5,
            research_depth="standard"
        )
        
        print(f"\n{'='*60}")
        print(f"✅ Research Complete!")
        print(f"{'='*60}")
        
        if result["success"]:
            print(f"\nStages: {' → '.join(result['stages_completed'])}")
            print(f"Total time: {result['metrics']['total_time']:.2f}s")
            
            synthesis = result['synthesis']
            print(f"\n📊 Synthesis:")
            print(f"   Sources used: {synthesis.get('sources_used', 0)}")
            print(f"   Key findings: {len(synthesis.get('key_findings', []))}")
            print(f"   Confidence: {synthesis.get('confidence_level', 'unknown')}")
            
            print(f"\n📝 Executive Summary:")
            print(f"   {synthesis.get('executive_summary', 'N/A')}")
            
            if synthesis.get('key_findings'):
                print(f"\n🔍 Key Findings:")
                for i, finding in enumerate(synthesis['key_findings'][:3], 1):
                    print(f"   {i}. {finding}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
    
    asyncio.run(test_research_swarm())


# ============================================================================
# Export for LangGraph Studio
# ============================================================================

_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        _default_instance = WebResearchSwarmCoordinator()
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()