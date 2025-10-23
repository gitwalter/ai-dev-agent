"""
Re-Ranker Agent for RAG Swarm

This agent specializes in intelligent result scoring, ranking, and deduplication.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


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




class ReRankerAgentState(BaseModel):
    """State for ReRankerAgent LangGraph workflow using Pydantic BaseModel."""
    
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

class ReRankerAgent(EnhancedBaseAgent):
    """
    Re-Ranker Agent - Expert at scoring and ranking retrieval results.
    
    Responsibilities:
    - Multi-signal scoring (semantic, keyword, quality, diversity)
    - Intelligent deduplication
    - Position optimization (lost-in-middle mitigation)
    - Context window budget management
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Re-Ranker Agent."""
        if config is None:
            config = AgentConfig(
                agent_id="re_ranker",
                name="Re-Ranker Agent",
                role="result_ranking",
                description="Expert at scoring, ranking, and filtering retrieval results",
                capabilities=[
                    "multi_signal_scoring",
                    "semantic_deduplication",
                    "position_optimization",
                    "quality_filtering"
                ]
            )
        
        super().__init__(config)
        self.ranking_stats = {
            'total_rankings': 0,
            'total_input_results': 0,
            'total_output_results': 0,
            'avg_deduplication_rate': 0,
            'avg_top_score': 0
        }
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            logger.info("⚠️ LangGraph not available - using legacy mode")
        
        logger.info(f"✅ {self.name} initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank and filter retrieval results using multi-signal scoring.
        
        Args:
            task: Dictionary containing:
                - search_results: List[Dict] from RetrievalSpecialistAgent
                - query_analysis: Dict from QueryAnalystAgent
                - top_k: int (optional, default 10)
                - min_score: float (optional, default 0.4)
                
        Returns:
            Dictionary with ranked and filtered results
        """
        search_results = task.get('search_results', [])
        query_analysis = task.get('query_analysis', {})
        top_k = task.get('top_k', 10)
        min_score = task.get('min_score', 0.4)  # Increased from 0.3 for better precision
        
        if not search_results:
            logger.warning(f"⚠️ {self.name}: No search results to rank")
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'ranked_results': [],
                'scores': [],
                'scoring_details': [],
                'removed_count': 0
            }
        
        original_query = query_analysis.get('original_query', '')
        key_concepts = query_analysis.get('key_concepts', [])
        
        logger.info(f"📊 {self.name}: Ranking {len(search_results)} results")
        
        try:
            # Step 1: Deduplicate
            unique_results = self._deduplicate_results(search_results)
            dedup_removed = len(search_results) - len(unique_results)
            logger.info(f"🔀 {self.name}: Deduplication removed {dedup_removed} duplicates")
            
            # Step 2: Multi-signal scoring
            scored_results = []
            for result in unique_results:
                score_details = self._calculate_multi_signal_score(
                    result, 
                    original_query, 
                    key_concepts
                )
                scored_results.append({
                    'result': result,
                    'combined_score': score_details['combined'],
                    'score_details': score_details
                })
            
            # Step 3: Sort by combined score
            scored_results.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Step 4: Filter by minimum score
            filtered_results = [
                sr for sr in scored_results 
                if sr['combined_score'] >= min_score
            ]
            filter_removed = len(scored_results) - len(filtered_results)
            
            # Step 5: Take top K
            top_results = filtered_results[:top_k]
            
            # Step 6: Position optimization (lost-in-middle mitigation)
            optimized_results = self._optimize_positions(top_results)
            
            # Update stats
            self.ranking_stats['total_rankings'] += 1
            self.ranking_stats['total_input_results'] += len(search_results)
            self.ranking_stats['total_output_results'] += len(optimized_results)
            
            if self.ranking_stats['total_rankings'] > 0:
                self.ranking_stats['avg_deduplication_rate'] = (
                    (self.ranking_stats['avg_deduplication_rate'] * (self.ranking_stats['total_rankings'] - 1) +
                     (dedup_removed / max(len(search_results), 1))) / self.ranking_stats['total_rankings']
                )
            
            if optimized_results:
                top_score = optimized_results[0]['combined_score']
                self.ranking_stats['avg_top_score'] = (
                    (self.ranking_stats['avg_top_score'] * (self.ranking_stats['total_rankings'] - 1) +
                     top_score) / self.ranking_stats['total_rankings']
                )
            
            # Extract final results
            final_results = [sr['result'] for sr in optimized_results]
            final_scores = [sr['combined_score'] for sr in optimized_results]
            final_details = [sr['score_details'] for sr in optimized_results]
            
            # Add scores to results for downstream agents
            for i, result in enumerate(final_results):
                result['combined_score'] = final_scores[i]
                result['scoring_details'] = final_details[i]
            
            # Log top results with scores for debugging
            if final_results:
                logger.info(f"✅ {self.name}: Ranked to {len(final_results)} results "
                           f"(removed {dedup_removed} duplicates, {filter_removed} low-quality)")
                logger.info(f"   Top 3 scores: {final_scores[:3]}")
                for i, result in enumerate(final_results[:3]):
                    source = result.get('metadata', {}).get('source', 'unknown')[:50]
                    score = final_scores[i]
                    details = final_details[i]
                    logger.info(f"   {i+1}. {source}... | Score: {score:.3f} | "
                              f"Semantic: {details['base']:.3f}, Keyword: {details['keyword']:.3f}")
            else:
                logger.info(f"✅ {self.name}: Ranked to {len(final_results)} results "
                           f"(removed {dedup_removed} duplicates, {filter_removed} low-quality)")
            
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'timestamp': datetime.now().isoformat(),
                'ranked_results': final_results,
                'scores': final_scores,
                'scoring_details': final_details,
                'removed_count': dedup_removed + filter_removed,
                'ranking_metadata': {
                    'input_count': len(search_results),
                    'after_dedup': len(unique_results),
                    'after_filter': len(filtered_results),
                    'final_count': len(final_results),
                    'avg_score': sum(final_scores) / len(final_scores) if final_scores else 0,
                    'top_score': final_scores[0] if final_scores else 0,
                    'min_score_threshold': min_score
                },
                'stats': self.ranking_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Ranking failed: {e}")
            return {
                'status': 'error',
                'agent_id': self.config.agent_id,
                'error': str(e),
                'ranked_results': search_results[:top_k]  # Fallback: just take first K
            }
    

    def _deduplicate_results(self, results: List[Dict], similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Deduplicate results based on content similarity.
        
        Uses simple hash-based deduplication for now. Could be enhanced with
        semantic similarity in the future.
        """
        seen_hashes = set()
        unique_results = []
        
        for result in results:
            content = result.get('content', '')
            # Create hash of content (first 500 chars for efficiency)
            content_hash = hashlib.md5(content[:500].encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _calculate_multi_signal_score(
        self, 
        result: Dict, 
        query: str, 
        key_concepts: List[str]
    ) -> Dict[str, float]:
        """
        Calculate multi-signal score combining multiple relevance factors.
        
        Signals:
        - Semantic score (from vector search)
        - Keyword overlap
        - Content quality
        - Diversity (uniqueness)
        """
        # Signal 1: Semantic score (from vector search)
        semantic_score = result.get('relevance_score', 0.5)
        
        # Signal 2: Keyword overlap
        keyword_score = self._calculate_keyword_score(result, query, key_concepts)
        
        # Signal 3: Content quality
        quality_score = self._calculate_quality_score(result)
        
        # Signal 4: Diversity (placeholder for now)
        diversity_score = 0.5  # Could be enhanced with semantic similarity to other results
        
        # Weighted combination (increased keyword weight for phrase matching)
        combined = (
            0.35 * semantic_score +     # Semantic similarity (embeddings)
            0.35 * keyword_score +      # Keyword/phrase matching (exact matches prioritized)
            0.20 * quality_score +      # Content quality
            0.10 * diversity_score      # Diversity
        )
        
        return {
            'base': semantic_score,
            'keyword': keyword_score,
            'quality': quality_score,
            'diversity': diversity_score,
            'combined': combined
        }
    
    def _calculate_keyword_score(
        self, 
        result: Dict, 
        query: str, 
        key_concepts: List[str]
    ) -> float:
        """
        Calculate keyword overlap score with phrase matching and metadata awareness.
        
        RAG Best Practice: Leverage document metadata for intelligent selection.
        Prioritizes:
        1. Title matches (document-level)
        2. Keyword metadata matches 
        3. Exact phrase matches in content
        4. Concept matches
        """
        content = result.get('content', '').lower()
        metadata = result.get('metadata', {})
        query_lower = query.lower()
        
        # CRITICAL: Check metadata first (document-level intelligence)
        title = (metadata.get('title') or '').lower()
        doc_keywords = [kw.lower() for kw in metadata.get('keywords', [])]
        doc_summary = (metadata.get('summary') or '').lower()
        
        # Score component 1: Title match (huge boost)
        title_match_score = 0.0
        if title:
            if query_lower in title:
                title_match_score = 0.7  # Exact query in title = very relevant!
            elif any(word in title for word in query_lower.split() if len(word) > 3):
                title_match_score = 0.4  # Partial title match
        
        # Score component 2: Keyword metadata match
        keyword_match_score = 0.0
        if doc_keywords:
            query_words = set(query_lower.split())
            matching_keywords = sum(1 for kw in doc_keywords if kw in query_lower or any(word in kw for word in query_words))
            keyword_match_score = min(0.3, matching_keywords * 0.15)
        
        # Score component 3: Summary match (if no title match)
        summary_match_score = 0.0
        if not title_match_score and doc_summary:
            if query_lower in doc_summary:
                summary_match_score = 0.3
        
        # Score component 4: Content exact phrase match
        content_phrase_score = 0.4 if query_lower in content else 0.0
        
        # Score component 5: Key concept matches in content
        key_phrase_matches = sum(1 for concept in key_concepts if concept.lower() in content)
        concept_score = min(0.2, key_phrase_matches * 0.1)
        
        # Combine scores (prioritize metadata over content)
        if title_match_score > 0:
            # Title match found - use title + keywords + concepts
            final_score = title_match_score + keyword_match_score * 0.5 + concept_score * 0.5
        elif summary_match_score > 0:
            # Summary match found
            final_score = summary_match_score + keyword_match_score + concept_score
        else:
            # Fall back to content matching
            final_score = content_phrase_score + keyword_match_score + concept_score
        
        return min(final_score, 1.0)
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """
        Calculate content quality score.
        
        Factors:
        - Length (too short = low quality)
        - Completeness (has metadata)
        - Structure (has source info)
        """
        content = result.get('content', '')
        
        # Length score
        length = len(content)
        if length < 50:
            length_score = 0.3
        elif length < 200:
            length_score = 0.6
        elif length < 500:
            length_score = 0.8
        else:
            length_score = 1.0
        
        # Metadata completeness
        has_source = 'source' in result or 'file' in result
        has_metadata = 'metadata' in result
        metadata_score = (0.5 if has_source else 0.0) + (0.5 if has_metadata else 0.0)
        
        # Combine
        quality = 0.6 * length_score + 0.4 * metadata_score
        
        return quality
    
    def _optimize_positions(self, scored_results: List[Dict]) -> List[Dict]:
        """
        Optimize result positions to mitigate 'lost in the middle' effect.
        
        Strategy: Keep highest-scored results at beginning and end,
        place medium-scored results in the middle.
        """
        if len(scored_results) <= 3:
            return scored_results  # Too few to optimize
        
        # Sort by score
        sorted_results = sorted(scored_results, key=lambda x: x['combined_score'], reverse=True)
        
        # Keep top 2 at beginning
        optimized = sorted_results[:2]
        
        # Put lowest scores in middle
        middle = sorted_results[2:-1] if len(sorted_results) > 3 else []
        middle.reverse()  # Put lower scores in middle
        
        # Put high score at end
        if len(sorted_results) > 2:
            optimized.extend(middle)
            optimized.append(sorted_results[-1] if len(middle) > 0 else sorted_results[2])
        
        return optimized
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate that task has required search_results field."""
        if not isinstance(task, dict):
            logger.error(f"❌ {self.name}: Task must be a dictionary")
            return False
        
        if 'search_results' not in task:
            logger.error(f"❌ {self.name}: Task must contain 'search_results' field")
            return False
        
        if not isinstance(task['search_results'], list):
            logger.error(f"❌ {self.name}: search_results must be a list")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ranking statistics."""
        return {
            'agent_id': self.config.agent_id,
            'agent_name': self.name,
            'stats': self.ranking_stats,
            'timestamp': datetime.now().isoformat()
        }


    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for ReRankerAgent."""
        workflow = StateGraph(ReRankerAgentState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: ReRankerAgentState) -> ReRankerAgentState:
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


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        
        config = AgentConfig(
            agent_id='re_ranker_agent',
            name='ReRankerAgent',
            description='ReRankerAgent agent',
            model_name='gemini-2.5-flash'
        )
        _default_instance = ReRankerAgent(config)
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
