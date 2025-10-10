"""
Retrieval Specialist Agent for RAG Swarm

This agent specializes in optimal context retrieval using multiple search strategies
with adaptive chunk retrieval based on query characteristics.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig
from context.context_engine import ContextEngine
from utils.rag.adaptive_retrieval_strategy import AdaptiveRetrievalStrategy, RetrievalContext

logger = logging.getLogger(__name__)


class RetrievalSpecialistAgent(EnhancedBaseAgent):
    """
    Retrieval Specialist Agent - Expert at finding relevant context.
    
    Responsibilities:
    - Multi-strategy search (semantic, keyword, hybrid)
    - Query expansion and decomposition
    - Diverse result retrieval
    - Optimal coverage of query aspects
    """
    
    def __init__(
        self, 
        context_engine: ContextEngine,
        config: Optional[AgentConfig] = None
    ):
        """
        Initialize Retrieval Specialist Agent.
        
        Args:
            context_engine: ContextEngine instance for search operations
            config: Optional agent configuration
        """
        if config is None:
            config = AgentConfig(
                agent_id="retrieval_specialist",
                name="Retrieval Specialist Agent",
                role="context_retrieval",
                description="Expert at retrieving relevant context using optimal search strategies",
                capabilities=[
                    "semantic_search",
                    "multi_query_search",
                    "hybrid_retrieval",
                    "diverse_sampling"
                ]
            )
        
        super().__init__(config)
        self.context_engine = context_engine
        self.adaptive_strategy = AdaptiveRetrievalStrategy()
        self.retrieval_stats = {
            'total_retrievals': 0,
            'total_searches': 0,
            'total_results': 0,
            'avg_results_per_search': 0,
            'avg_retrieval_time': 0,
            'last_retrieval_quality': 0.7  # Track quality for adaptive decisions
        }
        
        logger.info(f"✅ {self.name} initialized with ContextEngine and Adaptive Retrieval")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant context using optimal search strategies with adaptive chunk retrieval.
        
        Args:
            task: Dictionary containing:
                - query_analysis: Dict from QueryAnalystAgent
                - max_results: int (optional, will be determined adaptively)
                - retrieval_mode: str (optional: "auto", "manual", "performance")
                - manual_chunk_count: int (optional, for manual mode)
                - available_doc_count: int (optional, for context)
                
        Returns:
            Dictionary with retrieval results and adaptive decision info
        """
        query_analysis = task.get('query_analysis')
        
        if not query_analysis:
            return {
                'status': 'error',
                'error': 'No query_analysis provided',
                'agent_id': self.config.agent_id
            }
        
        original_query = query_analysis.get('original_query', '')
        rewritten_queries = query_analysis.get('rewritten_queries', [original_query])
        key_concepts = query_analysis.get('key_concepts', [])
        search_strategy = query_analysis.get('search_strategy', 'focused')
        document_filters = task.get('document_filters')  # Selective RAG filters
        
        # Adaptive retrieval mode
        retrieval_mode = task.get('retrieval_mode', 'auto')
        manual_chunk_count = task.get('manual_chunk_count')
        
        # Build retrieval context
        retrieval_context = RetrievalContext(
            available_doc_count=task.get('available_doc_count', 100),
            last_retrieval_quality=self.retrieval_stats.get('last_retrieval_quality', 0.7),
            performance_mode=(retrieval_mode == 'performance')
        )
        
        # Get optimal chunk count using adaptive strategy
        adaptive_decision = await self.adaptive_strategy.get_optimal_chunk_count(
            query=original_query,
            mode=retrieval_mode,
            manual_count=manual_chunk_count,
            context=retrieval_context
        )
        
        max_results = adaptive_decision['chunk_count']
        
        if document_filters:
            logger.info(f"🎯 {self.name}: Using selective RAG with {len(document_filters.get('source', []))} documents")
        
        logger.info(
            f"📚 {self.name}: Retrieving {max_results} chunks "
            f"(mode={retrieval_mode}, strategy={search_strategy})"
        )
        logger.info(f"   Rationale: {adaptive_decision['rationale']}")
        
        start_time = time.time()
        
        try:
            # Execute retrieval based on strategy (with optional document filtering)
            if search_strategy == 'focused':
                results = await self._focused_retrieval(original_query, max_results, document_filters)
            elif search_strategy == 'broad':
                results = await self._broad_retrieval(rewritten_queries, key_concepts, max_results, document_filters)
            elif search_strategy == 'multi-stage':
                results = await self._multi_stage_retrieval(rewritten_queries, key_concepts, max_results, document_filters)
            else:
                # Default to broad
                results = await self._broad_retrieval(rewritten_queries, key_concepts, max_results, document_filters)
            
            retrieval_time = time.time() - start_time
            
            # Update stats
            self.retrieval_stats['total_retrievals'] += 1
            self.retrieval_stats['total_results'] += len(results)
            self.retrieval_stats['avg_retrieval_time'] = (
                (self.retrieval_stats['avg_retrieval_time'] * (self.retrieval_stats['total_retrievals'] - 1) + 
                 retrieval_time) / self.retrieval_stats['total_retrievals']
            )
            
            logger.info(f"✅ {self.name}: Retrieved {len(results)} results in {retrieval_time:.2f}s")
            
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'timestamp': datetime.now().isoformat(),
                'search_results': results,
                'search_metadata': {
                    'searches_performed': self.retrieval_stats['total_searches'],
                    'total_candidates': len(results),
                    'retrieval_time': retrieval_time,
                    'strategy_used': search_strategy,
                    'adaptive_decision': adaptive_decision  # Include adaptive decision info
                },
                'stats': self.retrieval_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Retrieval failed: {e}")
            return {
                'status': 'error',
                'agent_id': self.config.agent_id,
                'error': str(e),
                'search_results': []
            }
    
    async def _focused_retrieval(self, query: str, max_results: int, document_filters: Dict = None) -> List[Dict]:
        """
        Focused retrieval - single high-precision search with higher limits.
        
        Best for: Simple factual queries
        """
        logger.info(f"🎯 {self.name}: Focused retrieval for '{query[:50]}...'")
        
        # INCREASED: Get more results for better coverage
        search_limit = max(max_results * 2, 40)  # At least 40 results
        search_results = await self.context_engine.semantic_search(
            query, 
            limit=search_limit,
            document_filters=document_filters  # NEW: Selective RAG
        )
        self.retrieval_stats['total_searches'] += 1
        
        return search_results.get('results', [])
    
    async def _broad_retrieval(
        self, 
        query_variants: List[str], 
        key_concepts: List[str],
        max_results: int,
        document_filters: Dict = None
    ) -> List[Dict]:
        """
        Broad retrieval - AGGRESSIVE multiple searches for comprehensive coverage.
        
        Best for: Conceptual queries needing diverse perspectives
        """
        logger.info(f"🌐 {self.name}: AGGRESSIVE broad retrieval with {len(query_variants)} variants + {len(key_concepts)} concepts")
        
        all_results = []
        # INCREASED: Get more results per query (at least 15)
        results_per_query = max(15, max_results // 3)
        
        # Search with ALL query variants (not just top 3)
        for i, query in enumerate(query_variants[:5], 1):  # Top 5 variants
            logger.info(f"  Search {i}/{len(query_variants[:5])}: '{query[:40]}...'")
            search_results = await self.context_engine.semantic_search(
                query, 
                limit=results_per_query,
                document_filters=document_filters  # NEW: Selective RAG
            )
            all_results.extend(search_results.get('results', []))
            self.retrieval_stats['total_searches'] += 1
        
        # Search with ALL key concepts (more aggressive)
        for i, concept in enumerate(key_concepts[:5], 1):  # Top 5 concepts
            logger.info(f"  Concept {i}/{len(key_concepts[:5])}: '{concept}'")
            search_results = await self.context_engine.semantic_search(
                concept, 
                limit=results_per_query,
                document_filters=document_filters  # NEW: Selective RAG
            )
            all_results.extend(search_results.get('results', []))
            self.retrieval_stats['total_searches'] += 1
        
        logger.info(f"  ✅ Collected {len(all_results)} total candidates")
        return all_results  # Return ALL results (re-ranker will filter)
    
    async def _multi_stage_retrieval(
        self,
        query_variants: List[str],
        key_concepts: List[str],
        max_results: int,
        document_filters: Dict = None
    ) -> List[Dict]:
        """
        Multi-stage retrieval - THOROUGH progressive refinement.
        
        Best for: Complex multi-hop queries
        
        Stages:
        1. Initial broad search (INCREASED)
        2. Concept-based expansion (AGGRESSIVE)
        3. Refinement search (COMPREHENSIVE)
        """
        logger.info(f"🔄 {self.name}: THOROUGH multi-stage retrieval")
        
        all_results = []
        
        # Stage 1: Initial search with top variants (INCREASED from 8 to 20)
        logger.info(f"  Stage 1: Initial search (20 results per query)")
        for query in query_variants[:3]:  # Top 3 variants
            search_results = await self.context_engine.semantic_search(query, limit=20, document_filters=document_filters)
            all_results.extend(search_results.get('results', []))
            self.retrieval_stats['total_searches'] += 1
        
        # Stage 2: Concept expansion (INCREASED from 5 to 15)
        logger.info(f"  Stage 2: Concept expansion (15 results per concept)")
        for concept in key_concepts[:5]:  # Top 5 concepts
            search_results = await self.context_engine.semantic_search(concept, limit=15, document_filters=document_filters)
            all_results.extend(search_results.get('results', []))
            self.retrieval_stats['total_searches'] += 1
        
        # Stage 3: Refinement (combined query) (INCREASED from 7 to 20)
        logger.info(f"  Stage 3: Refinement (20 results)")
        if len(key_concepts) >= 2:
            combined_query = f"{query_variants[0]} {' '.join(key_concepts[:3])}"
            search_results = await self.context_engine.semantic_search(combined_query, limit=20, document_filters=document_filters)
            all_results.extend(search_results.get('results', []))
            self.retrieval_stats['total_searches'] += 1
        
        # Stage 4: Additional broad search if needed
        if len(all_results) < 50:
            logger.info(f"  Stage 4: Additional broad search")
            for concept in key_concepts[5:8]:  # Additional concepts
                search_results = await self.context_engine.semantic_search(concept, limit=10, document_filters=document_filters)
                all_results.extend(search_results.get('results', []))
                self.retrieval_stats['total_searches'] += 1
        
        logger.info(f"  ✅ Collected {len(all_results)} total candidates")
        return all_results  # Return ALL results (re-ranker will filter)
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate that task has required query_analysis field."""
        if not isinstance(task, dict):
            logger.error(f"❌ {self.name}: Task must be a dictionary")
            return False
        
        if 'query_analysis' not in task:
            logger.error(f"❌ {self.name}: Task must contain 'query_analysis' field")
            return False
        
        query_analysis = task['query_analysis']
        if not isinstance(query_analysis, dict):
            logger.error(f"❌ {self.name}: query_analysis must be a dictionary")
            return False
        
        if 'original_query' not in query_analysis:
            logger.error(f"❌ {self.name}: query_analysis must contain 'original_query'")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        if self.retrieval_stats['total_searches'] > 0:
            self.retrieval_stats['avg_results_per_search'] = (
                self.retrieval_stats['total_results'] / self.retrieval_stats['total_searches']
            )
        
        return {
            'agent_id': self.config.agent_id,
            'agent_name': self.name,
            'stats': self.retrieval_stats,
            'timestamp': datetime.now().isoformat()
        }

