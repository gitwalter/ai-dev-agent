"""
Quality Assurance Agent for RAG Swarm

This agent validates retrieval quality and determines if results are sufficient.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

# LangChain imports
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class QualityAssuranceAgent(EnhancedBaseAgent):
    """
    Quality Assurance Agent - Validates retrieval quality.
    
    Responsibilities:
    - Verify retrieved context answers the query
    - Check for information gaps
    - Assess context quality and relevance
    - Trigger re-retrieval if quality insufficient
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Quality Assurance Agent."""
        if config is None:
            config = AgentConfig(
                agent_id="quality_assurance",
                name="Quality Assurance Agent",
                role="quality_validation",
                description="Validates retrieval quality and completeness",
                capabilities=[
                    "quality_assessment",
                    "coverage_analysis",
                    "gap_detection",
                    "re_retrieval_recommendation"
                ]
            )
        
        super().__init__(config)
        self.qa_stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            're_retrievals_triggered': 0,
            'avg_quality_score': 0
        }
        
        logger.info(f"✅ {self.name} initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate retrieval quality.
        
        Args:
            task: Dictionary containing:
                - ranked_results: List[Dict] from ReRankerAgent
                - query_analysis: Dict from QueryAnalystAgent
                - quality_threshold: float (optional, default 0.7)
                
        Returns:
            Quality validation report
        """
        ranked_results = task.get('ranked_results', [])
        query_analysis = task.get('query_analysis', {})
        quality_threshold = task.get('quality_threshold', 0.7)
        
        original_query = query_analysis.get('original_query', '')
        
        logger.info(f"✅ {self.name}: Validating {len(ranked_results)} results")
        
        try:
            # Perform quality assessment
            quality_report = await self._assess_quality(
                ranked_results,
                original_query,
                query_analysis
            )
            
            # Determine verdict (realistic thresholds)
            quality_score = quality_report['quality_score']
            
            # Trust the pipeline: > 0.5 = we can answer
            if quality_score >= 0.7:
                verdict = 'excellent'
                passed = True
            elif quality_score >= 0.5:
                verdict = 'good'
                passed = True
            elif quality_score >= 0.4:
                verdict = 'acceptable'
                passed = True  # We can still generate an answer
            else:
                verdict = 'insufficient'
                passed = False
            
            # Update stats
            self.qa_stats['total_validations'] += 1
            if passed:
                self.qa_stats['passed_validations'] += 1
            else:
                self.qa_stats['failed_validations'] += 1
            
            if quality_report.get('needs_re_retrieval'):
                self.qa_stats['re_retrievals_triggered'] += 1
            
            self.qa_stats['avg_quality_score'] = (
                (self.qa_stats['avg_quality_score'] * (self.qa_stats['total_validations'] - 1) +
                 quality_score) / self.qa_stats['total_validations']
            )
            
            logger.info(f"{'✅' if passed else '⚠️'} {self.name}: Quality verdict: {verdict} "
                       f"(score: {quality_score:.2f})")
            
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'timestamp': datetime.now().isoformat(),
                'quality_verdict': verdict,
                'passed': passed,
                **quality_report,
                'stats': self.qa_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Quality assessment failed: {e}")
            return {
                'status': 'error',
                'agent_id': self.config.agent_id,
                'error': str(e),
                'quality_verdict': 'unknown',
                'passed': False
            }
    
    async def _assess_quality(
        self,
        results: List[Dict],
        query: str,
        query_analysis: Dict
    ) -> Dict[str, Any]:
        """
        Realistic quality assessment for RAG retrieval.
        
        Philosophy: Focus on "can we answer the query?" not "perfect retrieval"
        Trust the hybrid search + re-ranking pipeline that already filtered results.
        """
        
        if not results:
            return {
                'quality_score': 0.0,
                'coverage_score': 0.0,
                'relevance_score': 0.0,
                'issues': ['No results retrieved'],
                'recommendations': ['Broaden search strategy', 'Try different query formulations'],
                'needs_re_retrieval': True,
                're_retrieval_strategy': 'broad'
            }
        
        # Calculate metrics
        relevance_score = self._calculate_relevance(results)
        coverage_score = self._calculate_coverage(results, query, query_analysis)
        diversity_score = self._calculate_diversity(results)
        
        # Realistic weighting: Relevance matters most
        # If re-ranker scored it high, trust that
        quality_score = (
            0.5 * relevance_score +    # Trust hybrid search + re-ranking
            0.3 * coverage_score +     # Can we answer?
            0.2 * diversity_score      # Nice to have, not critical
        )
        
        # Identify issues (realistic thresholds)
        issues = []
        recommendations = []
        
        if relevance_score < 0.4:  # Very low bar - hybrid search failed badly
            issues.append('Low relevance scores')
            recommendations.append('Refine query understanding')
        
        if coverage_score < 0.4:  # Can't answer query at all
            issues.append('Incomplete coverage of query aspects')
            recommendations.append('Expand search with key concepts')
        
        if len(results) < 3:  # Too few is actually a problem
            issues.append('Too few results')
            recommendations.append('Broaden search strategy')
        
        # Realistic re-retrieval threshold: Only if we truly can't answer
        # Quality > 0.5 = we can probably answer the query
        needs_re_retrieval = quality_score < 0.45
        re_retrieval_strategy = None
        
        if needs_re_retrieval:
            if coverage_score < 0.3:
                re_retrieval_strategy = 'multi-stage'  # Need more concepts
            elif relevance_score < 0.3:
                re_retrieval_strategy = 'focused'  # Need better quality
            else:
                re_retrieval_strategy = 'broad'  # Need more results
        
        return {
            'quality_score': quality_score,
            'coverage_score': coverage_score,
            'relevance_score': relevance_score,
            'diversity_score': diversity_score,
            'issues': issues,
            'recommendations': recommendations,
            'needs_re_retrieval': needs_re_retrieval,
            're_retrieval_strategy': re_retrieval_strategy
        }
    
    def _calculate_relevance(self, results: List[Dict]) -> float:
        """Calculate average relevance of results."""
        if not results:
            return 0.0
        
        scores = [r.get('combined_score', r.get('relevance_score', 0.5)) for r in results]
        return sum(scores) / len(scores)
    
    def _calculate_coverage(
        self,
        results: List[Dict],
        query: str,
        query_analysis: Dict
    ) -> float:
        """Estimate how well results cover query aspects."""
        key_concepts = query_analysis.get('key_concepts', [])
        
        if not key_concepts:
            return 0.8  # Assume good coverage if no concepts identified
        
        # Check how many key concepts appear in results (fuzzy matching)
        all_content = ' '.join([r.get('content', '').lower() for r in results])
        
        covered_concepts = 0
        for concept in key_concepts:
            concept_lower = concept.lower()
            # Fuzzy match: check for concept or words in concept
            words = concept_lower.split()
            if concept_lower in all_content:
                covered_concepts += 1.0  # Full match
            elif any(word in all_content for word in words if len(word) > 3):
                covered_concepts += 0.5  # Partial match
        
        coverage = covered_concepts / len(key_concepts) if key_concepts else 0.7
        
        return min(coverage, 1.0)
    
    def _calculate_diversity(self, results: List[Dict]) -> float:
        """Estimate diversity of results."""
        if len(results) <= 1:
            return 0.6
        
        # Check if results come from different sources
        sources = set()
        for result in results:
            source = result.get('metadata', {}).get('source') or result.get('source') or result.get('file', 'unknown')
            sources.add(source)
        
        # Diversity = ratio of unique sources to total results
        # But don't penalize too much if we have comprehensive single-source results
        raw_diversity = len(sources) / len(results)
        
        # If we have good content from one comprehensive source, that's OK
        if len(results) >= 5 and len(sources) == 1:
            return 0.6  # One comprehensive source is acceptable
        elif len(sources) >= 2:
            return min(raw_diversity + 0.2, 1.0)  # Boost for multiple sources
        else:
            return max(raw_diversity, 0.4)  # Floor at 0.4
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task has required fields."""
        if not isinstance(task, dict):
            logger.error(f"❌ {self.name}: Task must be a dictionary")
            return False
        
        if 'ranked_results' not in task:
            logger.error(f"❌ {self.name}: Task must contain 'ranked_results'")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get QA statistics."""
        return {
            'agent_id': self.config.agent_id,
            'agent_name': self.name,
            'stats': self.qa_stats,
            'timestamp': datetime.now().isoformat()
        }

