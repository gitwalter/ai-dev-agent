"""
Re-Ranker Agent for RAG Swarm

This agent specializes in intelligent result scoring, ranking, and deduplication.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

logger = logging.getLogger(__name__)


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
        
        logger.info(f"✅ {self.name} initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank and filter retrieval results using multi-signal scoring.
        
        Args:
            task: Dictionary containing:
                - search_results: List[Dict] from RetrievalSpecialistAgent
                - query_analysis: Dict from QueryAnalystAgent
                - top_k: int (optional, default 10)
                - min_score: float (optional, default 0.3)
                
        Returns:
            Dictionary with ranked and filtered results
        """
        search_results = task.get('search_results', [])
        query_analysis = task.get('query_analysis', {})
        top_k = task.get('top_k', 10)
        min_score = task.get('min_score', 0.3)
        
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
        
        # Weighted combination
        combined = (
            0.40 * semantic_score +
            0.25 * keyword_score +
            0.20 * quality_score +
            0.15 * diversity_score
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
        """Calculate keyword overlap score."""
        content = result.get('content', '').lower()
        
        # Combine query and key concepts
        query_terms = query.lower().split()
        all_terms = set(query_terms + key_concepts)
        
        if not all_terms:
            return 0.5
        
        # Count matching terms
        matches = sum(1 for term in all_terms if term.lower() in content)
        
        # Normalize by total terms
        score = matches / len(all_terms)
        
        return min(score, 1.0)
    
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

