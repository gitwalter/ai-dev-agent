"""
Adaptive Retrieval Strategy for RAG System

This module determines optimal chunk retrieval counts based on
query characteristics and context.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .query_analyzer import QueryAnalyzer, QueryAnalysis

logger = logging.getLogger(__name__)


@dataclass
class RetrievalContext:
    """Context information for retrieval decisions."""
    available_doc_count: int = 100  # Total documents available
    last_retrieval_quality: float = 0.7  # Quality score from last retrieval (0.0-1.0)
    user_feedback: Optional[str] = None  # User feedback on results
    performance_mode: bool = False  # Fast mode enabled


class AdaptiveRetrievalStrategy:
    """
    Intelligent retrieval strategy with context awareness.
    
    Determines optimal chunk counts based on:
    - Query type and complexity
    - Query specificity
    - Available document count
    - Previous retrieval quality
    - Performance constraints
    """
    
    # Base chunk counts for each query type
    BASE_CHUNK_COUNTS = {
        'simple_factual': 10,
        'moderate_conceptual': 15,
        'complex_conceptual': 25,
        'multi_hop_reasoning': 35
    }
    
    # Absolute bounds
    MIN_CHUNKS = 5
    MAX_CHUNKS = 50
    
    def __init__(self):
        """Initialize adaptive retrieval strategy."""
        self.query_analyzer = QueryAnalyzer()
        self.decision_history = []
        self.stats = {
            'total_decisions': 0,
            'avg_chunk_count': 0,
            'mode_distribution': {'auto': 0, 'manual': 0, 'performance': 0}
        }
        logger.info("✅ AdaptiveRetrievalStrategy initialized")
    
    async def get_optimal_chunk_count(
        self,
        query: str,
        mode: str = "auto",
        manual_count: Optional[int] = None,
        context: Optional[RetrievalContext] = None
    ) -> Dict[str, Any]:
        """
        Get optimal chunk count based on mode and context.
        
        Args:
            query: Search query
            mode: "auto", "manual", or "performance"
            manual_count: User-specified count (if manual mode)
            context: Optional retrieval context information
            
        Returns:
            Dictionary with chunk_count and decision rationale
        """
        # Handle manual mode
        if mode == "manual" and manual_count is not None:
            chunk_count = max(self.MIN_CHUNKS, min(manual_count, self.MAX_CHUNKS))
            self.stats['total_decisions'] += 1
            self.stats['mode_distribution']['manual'] += 1
            return {
                'chunk_count': chunk_count,
                'mode': 'manual',
                'rationale': f"User-specified: {chunk_count} chunks",
                'query_analysis': None  # No analysis in manual mode
            }
        
        # Handle performance mode
        if mode == "performance":
            self.stats['total_decisions'] += 1
            self.stats['mode_distribution']['performance'] += 1
            return {
                'chunk_count': 8,
                'mode': 'performance',
                'rationale': 'Performance mode: Using 8 chunks for fast response',
                'query_analysis': None  # No analysis in performance mode
            }
        
        # Auto mode: Intelligent determination
        if context is None:
            context = RetrievalContext()
        
        analysis = self.query_analyzer.analyze_query(query)
        chunk_count = await self.determine_optimal_chunk_count(query, analysis, context)
        
        # Record decision
        decision = {
            'chunk_count': chunk_count,
            'mode': 'auto',
            'query_type': analysis.query_type,
            'complexity': analysis.complexity_score,
            'rationale': self._generate_rationale(analysis, chunk_count, context),
            'query_analysis': {
                'query_type': analysis.query_type,
                'complexity_score': analysis.complexity_score,
                'specificity_score': analysis.specificity,
                'requires_reasoning': analysis.requires_reasoning,
                'requires_multi_hop': analysis.requires_multi_hop
            }
        }
        
        self.decision_history.append(decision)
        self.stats['total_decisions'] += 1
        self.stats['mode_distribution']['auto'] += 1
        self.stats['avg_chunk_count'] = (
            (self.stats['avg_chunk_count'] * (self.stats['total_decisions'] - 1) + chunk_count) 
            / self.stats['total_decisions']
        )
        
        logger.info(
            f"🎯 Adaptive Retrieval: {chunk_count} chunks "
            f"(type={analysis.query_type}, complexity={analysis.complexity_score:.2f})"
        )
        
        return decision
    
    async def determine_optimal_chunk_count(
        self,
        query: str,
        analysis: QueryAnalysis,
        context: RetrievalContext
    ) -> int:
        """
        Determine optimal chunk count based on multiple factors.
        
        Args:
            query: Search query
            analysis: Query analysis results
            context: Retrieval context
            
        Returns:
            Optimal chunk count (5-50)
        """
        # Start with base count for query type
        base_chunks = self.BASE_CHUNK_COUNTS.get(
            analysis.query_type,
            15  # Default fallback
        )
        
        # Factor 1: Adjust for document availability
        if context.available_doc_count < 5:
            # Small document set - don't over-retrieve
            base_chunks = min(base_chunks, 8)
            logger.debug(f"📉 Reduced chunks due to small doc set ({context.available_doc_count} docs)")
        
        # Factor 2: Adjust for query specificity
        # More specific queries (longer) need fewer chunks
        if analysis.specificity > 0.7:  # Very specific
            base_chunks = int(base_chunks * 0.8)
            logger.debug(f"📉 Reduced chunks due to high specificity ({analysis.specificity:.2f})")
        
        # Factor 3: Adjust based on previous retrieval quality
        if context.last_retrieval_quality < 0.5:
            # Low quality last time - try more chunks
            base_chunks = int(base_chunks * 1.5)
            logger.debug(f"📈 Increased chunks due to low previous quality ({context.last_retrieval_quality:.2f})")
        elif context.last_retrieval_quality > 0.85:
            # Very good quality - can reduce slightly
            base_chunks = int(base_chunks * 0.9)
            logger.debug(f"📉 Slight reduction due to high previous quality ({context.last_retrieval_quality:.2f})")
        
        # Factor 4: Multiple concepts need more chunks
        if analysis.has_multiple_concepts:
            base_chunks = int(base_chunks * 1.2)
            logger.debug("📈 Increased chunks for multiple concepts")
        
        # Factor 5: Performance mode constraint
        if context.performance_mode:
            base_chunks = min(base_chunks, 10)
            logger.debug("⚡ Limited chunks for performance mode")
        
        # Enforce absolute bounds
        final_count = max(self.MIN_CHUNKS, min(base_chunks, self.MAX_CHUNKS))
        
        return final_count
    
    def _generate_rationale(
        self,
        analysis: QueryAnalysis,
        chunk_count: int,
        context: RetrievalContext
    ) -> str:
        """Generate human-readable rationale for chunk count decision."""
        reasons = []
        
        # Primary reason: query type
        type_descriptions = {
            'simple_factual': 'Simple factual query',
            'moderate_conceptual': 'Moderate complexity',
            'complex_conceptual': 'Complex conceptual query',
            'multi_hop_reasoning': 'Multi-step reasoning required'
        }
        reasons.append(type_descriptions.get(analysis.query_type, 'Query analysis'))
        
        # Additional factors
        if context.available_doc_count < 5:
            reasons.append("small document set")
        
        if analysis.specificity > 0.7:
            reasons.append("high specificity")
        
        if context.last_retrieval_quality < 0.5:
            reasons.append("improving previous quality")
        
        if analysis.has_multiple_concepts:
            reasons.append("multiple concepts")
        
        rationale = f"{chunk_count} chunks: " + ", ".join(reasons)
        return rationale
    
    def get_decision_history(self, limit: int = 10) -> list:
        """Get recent decision history for debugging."""
        return self.decision_history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about retrieval decisions."""
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'avg_chunk_count': 0,
                'mode_distribution': {}
            }
        
        total = len(self.decision_history)
        avg_chunks = sum(d['chunk_count'] for d in self.decision_history) / total
        
        # Count by mode
        mode_counts = {}
        for decision in self.decision_history:
            mode = decision['mode']
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            'total_decisions': total,
            'avg_chunk_count': round(avg_chunks, 1),
            'mode_distribution': mode_counts,
            'chunk_count_range': {
                'min': min(d['chunk_count'] for d in self.decision_history),
                'max': max(d['chunk_count'] for d in self.decision_history)
            }
        }

