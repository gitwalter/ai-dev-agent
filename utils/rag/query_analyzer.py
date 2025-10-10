"""
Query Analyzer for Adaptive RAG Chunk Retrieval

This module analyzes queries to determine optimal retrieval strategies
and chunk counts based on query characteristics.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)


@dataclass
class QueryAnalysis:
    """Results of query analysis."""
    query: str
    query_type: str  # simple_factual, moderate_conceptual, complex_conceptual, multi_hop_reasoning
    complexity_score: float  # 0.0 to 1.0
    specificity: float  # 0.0 to 1.0 (how specific vs broad)
    word_count: int
    has_multiple_concepts: bool
    requires_reasoning: bool
    requires_multi_hop: bool = False  # Whether multi-hop reasoning is needed
    

class QueryAnalyzer:
    """
    Analyze queries to determine optimal retrieval strategy.
    
    Classifies queries into types:
    - simple_factual: Direct questions with single answer
    - moderate_conceptual: Questions requiring understanding of concepts
    - complex_conceptual: Multi-faceted questions requiring deep context
    - multi_hop_reasoning: Questions requiring multiple steps of reasoning
    """
    
    def __init__(self):
        """Initialize QueryAnalyzer with classification patterns."""
        # Patterns for query type classification
        self.simple_patterns = [
            r'\bwhat is\b',
            r'\bwho is\b',
            r'\bwhen was\b',
            r'\bwhere is\b',
            r'\bdefine\b',
            r'\bname\b',
            r'\blist\b',
        ]
        
        self.reasoning_patterns = [
            r'\bwhy\b',
            r'\bhow does\b',
            r'\bhow do\b',
            r'\bexplain\b',
            r'\bcompare\b',
            r'\banalyze\b',
            r'\bevaluate\b',
            r'\bimplement\b',
        ]
        
        self.multi_hop_patterns = [
            r'\band then\b',
            r'\bafter that\b',
            r'\bgiven that\b',
            r'\bif.*then\b',
            r'\bstep by step\b',
            r'\bfirst.*then\b',
            r'\bfirst.*second\b',
            r'\bfirst.*finally\b',
            r'\bthen.*finally\b',
        ]
        
        logger.info("✅ QueryAnalyzer initialized")
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze query characteristics and classify type.
        
        Args:
            query: User's search query
            
        Returns:
            QueryAnalysis with classification and metrics
        """
        query_lower = query.lower().strip()
        word_count = len(query.split())
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(query_lower, word_count)
        
        # Calculate specificity (longer queries are usually more specific)
        specificity = min(word_count / 45.0, 1.0)  # Slightly more generous
        
        # Check for multiple concepts
        has_multiple_concepts = self._has_multiple_concepts(query_lower)
        
        # Check for reasoning requirements
        requires_reasoning = self._requires_reasoning(query_lower)
        
        # Check for multi-hop reasoning
        requires_multi_hop = any(
            re.search(pattern, query_lower)
            for pattern in self.multi_hop_patterns
        )
        
        # Classify query type
        query_type = self._classify_query_type(
            query_lower,
            complexity_score,
            requires_reasoning,
            has_multiple_concepts
        )
        
        analysis = QueryAnalysis(
            query=query,
            query_type=query_type,
            complexity_score=complexity_score,
            specificity=specificity,
            word_count=word_count,
            has_multiple_concepts=has_multiple_concepts,
            requires_reasoning=requires_reasoning,
            requires_multi_hop=requires_multi_hop
        )
        
        logger.info(
            f"📊 Query Analysis: type={query_type}, "
            f"complexity={complexity_score:.2f}, "
            f"specificity={specificity:.2f}, "
            f"words={word_count}"
        )
        
        return analysis
    
    def _calculate_complexity(self, query: str, word_count: int) -> float:
        """
        Calculate query complexity score (0.0 to 1.0).
        
        Factors:
        - Query length
        - Presence of reasoning words
        - Multiple concepts
        - Question structure
        """
        complexity = 0.0
        
        # Length factor (more words = more complex)
        length_factor = min(word_count / 25.0, 0.35)  # Increased weight
        complexity += length_factor
        
        # Reasoning words factor
        reasoning_count = sum(
            1 for pattern in self.reasoning_patterns
            if re.search(pattern, query)
        )
        complexity += min(reasoning_count * 0.25, 0.35)  # Increased weight
        
        # Multi-hop patterns
        multi_hop_count = sum(
            1 for pattern in self.multi_hop_patterns
            if re.search(pattern, query)
        )
        complexity += min(multi_hop_count * 0.2, 0.2)
        
        # Multiple questions/concepts
        question_marks = query.count('?')
        if question_marks > 1:
            complexity += 0.1
        
        return min(complexity, 1.0)
    
    def _has_multiple_concepts(self, query: str) -> bool:
        """Check if query involves multiple concepts."""
        # Check for conjunctions and multiple concepts
        # Use word boundaries to avoid false positives like "What is" containing "is"
        indicators = [
            r'\band\b', r'\bor\b', r'\bboth\b', 
            r'\bas well as\b', r'\balong with\b'
        ]
        return any(re.search(indicator, query) for indicator in indicators)
    
    def _requires_reasoning(self, query: str) -> bool:
        """Check if query requires reasoning vs simple lookup."""
        return any(
            re.search(pattern, query)
            for pattern in self.reasoning_patterns
        )
    
    def _classify_query_type(
        self,
        query: str,
        complexity_score: float,
        requires_reasoning: bool,
        has_multiple_concepts: bool
    ) -> str:
        """
        Classify query into one of four types.
        
        Returns:
            Query type string
        """
        # Check for multi-hop reasoning patterns
        is_multi_hop = any(
            re.search(pattern, query)
            for pattern in self.multi_hop_patterns
        )
        
        if is_multi_hop:
            return "multi_hop_reasoning"
        
        # Check for simple factual patterns
        is_simple = any(
            re.search(pattern, query)
            for pattern in self.simple_patterns
        )
        
        if is_simple and complexity_score < 0.35 and not has_multiple_concepts:
            return "simple_factual"
        
        # High complexity = complex conceptual
        if complexity_score >= 0.5 or (has_multiple_concepts and requires_reasoning and complexity_score > 0.4):
            return "complex_conceptual"
        
        # Default to moderate conceptual
        return "moderate_conceptual"
    
    def get_query_characteristics_summary(self, analysis: QueryAnalysis) -> Dict[str, Any]:
        """
        Get human-readable summary of query characteristics.
        
        Args:
            analysis: QueryAnalysis result
            
        Returns:
            Dictionary with summary information
        """
        return {
            'query': analysis.query,
            'type': analysis.query_type,
            'type_description': self._get_type_description(analysis.query_type),
            'complexity': f"{analysis.complexity_score:.0%}",
            'specificity': f"{analysis.specificity:.0%}",
            'characteristics': {
                'word_count': analysis.word_count,
                'multiple_concepts': analysis.has_multiple_concepts,
                'requires_reasoning': analysis.requires_reasoning,
            }
        }
    
    def _get_type_description(self, query_type: str) -> str:
        """Get human-readable description of query type."""
        descriptions = {
            'simple_factual': 'Simple factual question with direct answer',
            'moderate_conceptual': 'Conceptual question requiring understanding',
            'complex_conceptual': 'Complex multi-faceted question',
            'multi_hop_reasoning': 'Multi-step reasoning required'
        }
        return descriptions.get(query_type, 'Unknown type')

