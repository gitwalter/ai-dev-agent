"""
RAG Agent Swarm with LangGraph Integration

This implements the RAG agent swarm using LangGraph for proper LangSmith tracing
and agent handover visibility.
"""

import logging
from typing import Dict, Any, List, TypedDict, Annotated, Optional
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available")

from context.context_engine import ContextEngine
from agents.rag.query_analyst_agent import QueryAnalystAgent
from agents.rag.retrieval_specialist_agent import RetrievalSpecialistAgent
from agents.rag.re_ranker_agent import ReRankerAgent
from agents.rag.quality_assurance_agent import QualityAssuranceAgent
from agents.rag.writer_agent import WriterAgent

logger = logging.getLogger(__name__)


class RAGSwarmState(TypedDict):
    """State for RAG agent swarm workflow."""
    
    # Input
    query: Annotated[str, "User's original query"]
    max_results: Annotated[int, "Maximum results to return"]
    quality_threshold: Annotated[float, "Quality threshold for re-retrieval"]
    enable_re_retrieval: Annotated[bool, "Enable automatic re-retrieval"]
    
    # Agent outputs
    query_analysis: Annotated[Dict[str, Any], "Output from QueryAnalystAgent"]
    retrieval_results: Annotated[List[Dict], "Output from RetrievalSpecialistAgent"]
    ranked_results: Annotated[List[Dict], "Output from ReRankerAgent"]
    quality_report: Annotated[Dict[str, Any], "Output from QualityAssuranceAgent"]
    final_response: Annotated[Dict[str, Any], "Output from WriterAgent"]
    
    # Workflow control
    current_stage: Annotated[str, "Current pipeline stage"]
    stages_completed: Annotated[List[str], "Completed stages"]
    needs_re_retrieval: Annotated[bool, "Whether re-retrieval is needed"]
    re_retrieval_done: Annotated[bool, "Flag to prevent infinite re-retrieval loops"]
    errors: Annotated[List[str], "Error messages"]
    
    # Metrics
    metrics: Annotated[Dict[str, float], "Pipeline timing metrics"]


class RAGSwarmCoordinator:
    """
    RAG Agent Swarm using LangGraph for proper tracing.
    
    This provides full LangSmith visibility of agent handoffs and interactions.
    """
    
    def __init__(self, context_engine: ContextEngine):
        """
        Initialize RAG swarm with LangGraph.
        
        Args:
            context_engine: ContextEngine for retrieval operations
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required for RAG swarm. Install with: pip install langgraph")
        
        self.context_engine = context_engine
        
        # Initialize agents
        self.query_analyst = QueryAnalystAgent()
        self.retrieval_specialist = RetrievalSpecialistAgent(context_engine)
        self.re_ranker = ReRankerAgent()
        self.quality_assurance = QualityAssuranceAgent()
        self.writer = WriterAgent()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
        
        logger.info("✅ RAG Swarm Coordinator (LangGraph) initialized with 5 specialized agents")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for RAG pipeline."""
        
        workflow = StateGraph(RAGSwarmState)
        
        # Add agent nodes
        workflow.add_node("query_analysis", self._query_analysis_node)
        workflow.add_node("retrieval", self._retrieval_node)
        workflow.add_node("re_ranking", self._re_ranking_node)
        workflow.add_node("quality_assurance", self._quality_assurance_node)
        workflow.add_node("response_generation", self._response_generation_node)
        
        # Define workflow edges
        workflow.set_entry_point("query_analysis")
        workflow.add_edge("query_analysis", "retrieval")
        workflow.add_edge("retrieval", "re_ranking")
        workflow.add_edge("re_ranking", "quality_assurance")
        
        # Conditional edge: re-retrieval or response generation
        workflow.add_conditional_edges(
            "quality_assurance",
            self._should_re_retrieve,
            {
                "re_retrieve": "retrieval",  # Loop back
                "generate": "response_generation",
                END: END
            }
        )
        
        workflow.add_edge("response_generation", END)
        
        return workflow
    
    async def _query_analysis_node(self, state: RAGSwarmState) -> RAGSwarmState:
        """Node 1: Query Analysis with error tracking."""
        import time
        
        logger.info("[1/5] Query Analysis stage")
        start_time = time.time()
        
        try:
            result = await self.query_analyst.execute({
                'query': state['query']
            })
            
            state['query_analysis'] = result.get('analysis', {})
            state['stages_completed'].append('query_analysis')
            state['metrics']['query_analysis_time'] = time.time() - start_time
            state['current_stage'] = 'retrieval'
            
            logger.info(f"✅ Query analysis complete: intent={state['query_analysis'].get('intent')}")
            
        except Exception as e:
            error_msg = f"Query Analysis FAILED: {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            state['errors'].append({'stage': 'query_analysis', 'error': error_msg})
            # Provide fallback analysis so pipeline can continue
            state['query_analysis'] = {
                'original_query': state['query'],
                'intent': 'unknown',
                'key_concepts': [state['query']],
                'error': error_msg
            }
            state['stages_completed'].append('query_analysis_failed')
        
        return state
    
    async def _retrieval_node(self, state: RAGSwarmState) -> RAGSwarmState:
        """Node 2: Context Retrieval with smart re-retrieval strategy."""
        import time
        
        is_re_retrieval = state.get('re_retrieval_done', False)
        
        if is_re_retrieval:
            logger.info(f"[2/5] Retrieval stage (RE-RETRIEVAL)")
        else:
            logger.info(f"[2/5] Retrieval stage (INITIAL)")
        
        # On re-retrieval, use reformulated query strategy
        if is_re_retrieval:
            quality_report = state.get('quality_report', {})
            re_retrieval_strategy = quality_report.get('re_retrieval_strategy', 'broad')
            
            logger.info(f"🔄 RE-RETRIEVAL with strategy: {re_retrieval_strategy}")
            
            # Enhance query analysis for re-retrieval
            query_analysis = state['query_analysis'].copy()
            query_analysis['re_retrieval_strategy'] = re_retrieval_strategy
            query_analysis['previous_quality_score'] = quality_report.get('quality_score', 0)
            query_analysis['identified_gaps'] = quality_report.get('issues', [])
        else:
            query_analysis = state['query_analysis']
            logger.info(f"🔍 INITIAL RETRIEVAL")
        
        start_time = time.time()
        
        try:
            result = await self.retrieval_specialist.execute({
                'query_analysis': query_analysis,
                'max_results': state['max_results'] * 2  # Get more for ranking
            })
            
            state['retrieval_results'] = result.get('search_results', [])
            if 'retrieval' not in state['stages_completed']:
                state['stages_completed'].append('retrieval')
            state['metrics']['retrieval_time'] = time.time() - start_time
            state['current_stage'] = 're_ranking'
            
            logger.info(f"✅ Retrieval complete: {len(state['retrieval_results'])} candidates")
            
        except Exception as e:
            error_msg = f"Retrieval FAILED: {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            state['errors'].append({'stage': 'retrieval', 'error': error_msg})
            # Provide empty results so pipeline can continue
            state['retrieval_results'] = []
            state['stages_completed'].append('retrieval_failed')
        
        return state
    
    async def _re_ranking_node(self, state: RAGSwarmState) -> RAGSwarmState:
        """Node 3: Re-ranking."""
        import time
        
        logger.info("[3/5] Re-ranking stage")
        start_time = time.time()
        
        result = await self.re_ranker.execute({
            'search_results': state['retrieval_results'],
            'query_analysis': state['query_analysis'],
            'top_k': state['max_results']
        })
        
        state['ranked_results'] = result.get('ranked_results', [])
        if 're_ranking' not in state['stages_completed']:
            state['stages_completed'].append('re_ranking')
        state['metrics']['re_ranking_time'] = time.time() - start_time
        state['current_stage'] = 'quality_assurance'
        
        logger.info(f"Re-ranking complete: top {len(state['ranked_results'])} results")
        
        return state
    
    async def _quality_assurance_node(self, state: RAGSwarmState) -> RAGSwarmState:
        """Node 4: Quality Assurance."""
        import time
        
        # Count QA executions
        qa_count = state['stages_completed'].count('quality_assurance')
        logger.info(f"[4/5] Quality Assurance stage (execution #{qa_count + 1})")
        start_time = time.time()
        
        result = await self.quality_assurance.execute({
            'ranked_results': state['ranked_results'],
            'query_analysis': state['query_analysis'],
            'quality_threshold': state['quality_threshold']
        })
        
        state['quality_report'] = {
            'quality_score': result.get('quality_score', 0),
            'coverage_score': result.get('coverage_score', 0),
            'relevance_score': result.get('relevance_score', 0),
            'passed': result.get('passed', False),
            'needs_re_retrieval': result.get('needs_re_retrieval', False)
        }
        
        state['needs_re_retrieval'] = result.get('needs_re_retrieval', False)
        state['stages_completed'].append('quality_assurance')
        state['metrics']['qa_time'] = time.time() - start_time
        
        quality_score = state['quality_report']['quality_score']
        needs_re_retrieval = result.get('needs_re_retrieval', False)
        
        # CRITICAL: Use qa_count to control re-retrieval
        # qa_count == 0: First QA, can re-retrieve
        # qa_count >= 1: Second+ QA, must stop
        if qa_count >= 1:
            # Already did at least one re-retrieval → STOP
            state['re_retrieval_done'] = True
            logger.info(f"✅ QA #{qa_count + 1}: score={quality_score:.2f}, STOP (max re-retrieval reached)")
        else:
            logger.info(f"✅ QA #{qa_count + 1}: score={quality_score:.2f}")
        
        return state
    
    async def _response_generation_node(self, state: RAGSwarmState) -> RAGSwarmState:
        """Node 5: Response Generation."""
        import time
        
        logger.info("[5/5] Response Generation stage")
        start_time = time.time()
        
        result = await self.writer.execute({
            'ranked_results': state['ranked_results'],
            'query_analysis': state['query_analysis'],
            'quality_report': state['quality_report']
        })
        
        state['final_response'] = {
            'response': result.get('response', ''),
            'confidence': result.get('confidence', 0),
            'sources_cited': result.get('sources_cited', []),
            'limitations': result.get('limitations')
        }
        
        state['stages_completed'].append('response_generation')
        state['metrics']['generation_time'] = time.time() - start_time
        state['current_stage'] = 'complete'
        
        logger.info("Response generation complete")
        
        return state
    
    def _should_re_retrieve(self, state: RAGSwarmState) -> str:
        """
        Conditional edge function - ONLY READS state, does NOT mutate it!
        
        State mutations happen in NODES, not in conditional functions.
        The re_retrieval_done flag is set in the QA node.
        """
        
        # Rule 1: Already did re-retrieval? → STOP
        if state.get('re_retrieval_done', False):
            logger.info(f"⛔ FLAG SET - Already decided to re-retrieve, now GENERATE")
            return "generate"
        
        # Rule 2: Re-retrieval disabled?
        if not state.get('enable_re_retrieval', False):
            logger.info(f"⛔ Re-retrieval disabled - GENERATE")
            return "generate"
        
        # Rule 3: Check quality
        quality_report = state.get('quality_report', {})
        quality_score = quality_report.get('quality_score', 1.0)
        needs_re_retrieval = quality_report.get('needs_re_retrieval', False)
        
        logger.info(f"🔍 RE-RETRIEVAL DECISION:")
        logger.info(f"   - Quality score: {quality_score:.2f}")
        logger.info(f"   - Needs re-retrieval: {needs_re_retrieval}")
        logger.info(f"   - Flag set: {state.get('re_retrieval_done', False)}")
        
        if needs_re_retrieval and quality_score < 0.6:
            logger.info(f"🔄 Quality low - RE-RETRIEVE")
            return "re_retrieve"
        
        # Quality OK - generate answer
        logger.info(f"✅ Quality acceptable - GENERATE")
        return "generate"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute RAG pipeline using LangGraph.
        
        Args:
            task: Dictionary with:
                - query: str
                - max_results: int (optional)
                - quality_threshold: float (optional)
                - enable_re_retrieval: bool (optional)
                
        Returns:
            Complete RAG result with response and metadata
        """
        import time
        
        start_time = time.time()
        
        # Initialize state
        initial_state: RAGSwarmState = {
            'query': task.get('query', ''),
            'max_results': task.get('max_results', 50),
            'quality_threshold': task.get('quality_threshold', 0.6),
            'enable_re_retrieval': task.get('enable_re_retrieval', True),  # ✅ ENABLED by default (max 1 re-retrieval)
            'query_analysis': {},
            'retrieval_results': [],
            'ranked_results': [],
            'quality_report': {},
            'final_response': {},
            'current_stage': 'query_analysis',
            'stages_completed': [],
            'needs_re_retrieval': False,
            're_retrieval_done': False,  # Boolean flag for loop control (correct LangGraph pattern)
            'errors': [],
            'metrics': {}
        }
        
        try:
            # Execute workflow (no timeout - termination logic is bulletproof)
            logger.info(f"RAG Swarm LangGraph: Processing query '{task.get('query', '')[:60]}...'")
            
            final_state = await self.app.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": f"rag_{datetime.now().timestamp()}"}}
            )
            
            total_time = time.time() - start_time
            final_state['metrics']['total_time'] = total_time
            
            # Build result
            result = {
                'status': 'success',
                'query': final_state['query'],
                'response': final_state['final_response'].get('response', ''),
                'confidence': final_state['final_response'].get('confidence', 0),
                'sources_cited': final_state['final_response'].get('sources_cited', []),
                'limitations': final_state['final_response'].get('limitations'),
                'pipeline_state': {
                    'query_analysis': final_state['query_analysis'],
                    'ranked_results': final_state['ranked_results'],
                    'quality_report': final_state['quality_report'],
                    'stages_completed': final_state['stages_completed'],
                    'metrics': final_state['metrics']
                }
            }
            
            logger.info(f"RAG Swarm LangGraph: Complete in {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ RAG Swarm LangGraph: Failed with error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'error': str(e),
                'query': task.get('query', ''),
                'response': f'An error occurred: {str(e)}',
                'confidence': 0,
                'quality_score': 0,
                'sources_cited': [],
                'stages_completed': [],
                'pipeline_metrics': {}
            }

