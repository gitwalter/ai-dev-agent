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
            
            # Determine verdict
            quality_score = quality_report['quality_score']
            if quality_score >= quality_threshold:
                verdict = 'excellent' if quality_score >= 0.9 else 'good'
                passed = True
            elif quality_score >= 0.5:
                verdict = 'insufficient'
                passed = False
            else:
                verdict = 'poor'
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
        """Assess quality of retrieval results."""
        
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
        
        # Overall quality
        quality_score = (
            0.4 * relevance_score +
            0.4 * coverage_score +
            0.2 * diversity_score
        )
        
        # Identify issues
        issues = []
        recommendations = []
        
        if relevance_score < 0.6:
            issues.append('Low relevance scores')
            recommendations.append('Refine query understanding')
        
        if coverage_score < 0.6:
            issues.append('Incomplete coverage of query aspects')
            recommendations.append('Expand search with key concepts')
        
        if diversity_score < 0.5:
            issues.append('Results too similar')
            recommendations.append('Increase diversity in retrieval')
        
        if len(results) < 5:
            issues.append('Too few results')
            recommendations.append('Broaden search strategy')
        
        # Determine if re-retrieval needed
        needs_re_retrieval = quality_score < 0.6
        re_retrieval_strategy = None
        
        if needs_re_retrieval:
            if coverage_score < 0.5:
                re_retrieval_strategy = 'multi-stage'
            elif relevance_score < 0.5:
                re_retrieval_strategy = 'focused'
            else:
                re_retrieval_strategy = 'broad'
        
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
            return 0.7  # Assume decent coverage if no concepts identified
        
        # Check how many key concepts appear in results
        all_content = ' '.join([r.get('content', '').lower() for r in results])
        
        covered_concepts = sum(
            1 for concept in key_concepts 
            if concept.lower() in all_content
        )
        
        coverage = covered_concepts / len(key_concepts) if key_concepts else 0.5
        
        return min(coverage, 1.0)
    
    def _calculate_diversity(self, results: List[Dict]) -> float:
        """Estimate diversity of results."""
        if len(results) <= 1:
            return 0.5
        
        # Simple diversity: check if results come from different sources
        sources = set()
        for result in results:
            source = result.get('source', result.get('file', 'unknown'))
            sources.add(source)
        
        # Diversity = ratio of unique sources to total results
        diversity = len(sources) / len(results)
        
        return diversity
    
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

