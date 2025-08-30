"""
Prompt Performance Optimization Framework
========================================

Provides comprehensive performance optimization, caching, and monitoring
capabilities for AI agent prompts. This is a core component of the prompt
engineering system for US-PE-01.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import logging
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Prompt optimization strategies."""
    TOKEN_REDUCTION = "token_reduction"
    CLARITY_ENHANCEMENT = "clarity_enhancement"
    CONTEXT_OPTIMIZATION = "context_optimization"
    PERFORMANCE_TUNING = "performance_tuning"


@dataclass
class OptimizationResult:
    """Result of prompt optimization."""
    original_prompt: str
    optimized_prompt: str
    strategy: OptimizationStrategy
    improvement_score: float
    token_reduction: int
    performance_gain: float
    optimization_time: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PerformanceMetrics:
    """Performance metrics for prompts."""
    prompt_id: str
    execution_time: float
    token_count: int
    response_quality: float
    success_rate: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PromptOptimizer:
    """Core prompt optimization engine."""
    
    def __init__(self, cache_dir: str = "prompts/cache"):
        """
        Initialize the prompt optimizer.
        
        Args:
            cache_dir: Directory for optimization cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.optimization_cache: Dict[str, OptimizationResult] = {}
        self.performance_metrics: List[PerformanceMetrics] = []
        self.optimization_history: List[OptimizationResult] = []
    
    def optimize_prompt(self, prompt: str, strategy: OptimizationStrategy,
                       context: Dict[str, Any] = None) -> OptimizationResult:
        """
        Optimize a prompt using the specified strategy.
        
        Args:
            prompt: Original prompt
            strategy: Optimization strategy
            context: Additional context for optimization
            
        Returns:
            OptimizationResult: Optimization result
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(prompt, strategy, context)
        if cache_key in self.optimization_cache:
            logger.info(f"Using cached optimization for {cache_key}")
            return self.optimization_cache[cache_key]
        
        # Apply optimization strategy
        if strategy == OptimizationStrategy.TOKEN_REDUCTION:
            optimized_prompt = self._optimize_token_reduction(prompt)
        elif strategy == OptimizationStrategy.CLARITY_ENHANCEMENT:
            optimized_prompt = self._optimize_clarity(prompt)
        elif strategy == OptimizationStrategy.CONTEXT_OPTIMIZATION:
            optimized_prompt = self._optimize_context(prompt, context)
        elif strategy == OptimizationStrategy.PERFORMANCE_TUNING:
            optimized_prompt = self._optimize_performance(prompt)
        else:
            raise ValueError(f"Unknown optimization strategy: {strategy}")
        
        # Calculate metrics
        optimization_time = time.time() - start_time
        token_reduction = self._count_tokens(prompt) - self._count_tokens(optimized_prompt)
        improvement_score = self._calculate_improvement_score(prompt, optimized_prompt)
        performance_gain = self._estimate_performance_gain(token_reduction)
        
        # Create result
        result = OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=optimized_prompt,
            strategy=strategy,
            improvement_score=improvement_score,
            token_reduction=token_reduction,
            performance_gain=performance_gain,
            optimization_time=optimization_time,
            metadata={"context": context}
        )
        
        # Cache result
        self.optimization_cache[cache_key] = result
        self.optimization_history.append(result)
        
        # Save to file
        self._save_optimization_result(result, cache_key)
        
        logger.info(f"Optimized prompt with {strategy.value}: {token_reduction} tokens reduced")
        return result
    
    def get_optimization_history(self, limit: int = 100) -> List[OptimizationResult]:
        """
        Get optimization history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of optimization results
        """
        return self.optimization_history[-limit:]
    
    def get_performance_metrics(self, prompt_id: str = None, 
                              since: datetime = None) -> List[PerformanceMetrics]:
        """
        Get performance metrics.
        
        Args:
            prompt_id: Filter by prompt ID
            since: Filter by timestamp
            
        Returns:
            List of performance metrics
        """
        metrics = self.performance_metrics
        
        if prompt_id:
            metrics = [m for m in metrics if m.prompt_id == prompt_id]
        
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        return sorted(metrics, key=lambda m: m.timestamp, reverse=True)
    
    def record_performance(self, prompt_id: str, execution_time: float,
                          token_count: int, response_quality: float,
                          success: bool, metadata: Dict[str, Any] = None):
        """
        Record performance metrics for a prompt execution.
        
        Args:
            prompt_id: Prompt ID
            execution_time: Execution time in seconds
            token_count: Number of tokens used
            response_quality: Quality score (0-1)
            success: Whether execution was successful
            metadata: Additional metadata
        """
        metric = PerformanceMetrics(
            prompt_id=prompt_id,
            execution_time=execution_time,
            token_count=token_count,
            response_quality=response_quality,
            success_rate=1.0 if success else 0.0,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.performance_metrics.append(metric)
        
        # Keep only last 1000 metrics to prevent memory bloat
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
    
    def get_optimization_recommendations(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Get optimization recommendations for a prompt.
        
        Args:
            prompt: Prompt to analyze
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Analyze token count
        token_count = self._count_tokens(prompt)
        if token_count > 500:  # Lower threshold for testing
            recommendations.append({
                "strategy": OptimizationStrategy.TOKEN_REDUCTION,
                "priority": "high",
                "reason": f"Prompt is {token_count} tokens, consider reducing for cost efficiency",
                "expected_improvement": min(0.3, (token_count - 250) / token_count)
            })
        
        # Analyze clarity
        clarity_score = self._analyze_clarity(prompt)
        if clarity_score < 0.7:
            recommendations.append({
                "strategy": OptimizationStrategy.CLARITY_ENHANCEMENT,
                "priority": "medium",
                "reason": f"Clarity score is {clarity_score:.2f}, consider improving clarity",
                "expected_improvement": 0.2
            })
        
        # Analyze context usage
        context_efficiency = self._analyze_context_efficiency(prompt)
        if context_efficiency < 0.6:
            recommendations.append({
                "strategy": OptimizationStrategy.CONTEXT_OPTIMIZATION,
                "priority": "medium",
                "reason": f"Context efficiency is {context_efficiency:.2f}, consider optimizing context usage",
                "expected_improvement": 0.15
            })
        
        return recommendations
    
    def _optimize_token_reduction(self, prompt: str) -> str:
        """Optimize prompt for token reduction."""
        # Remove unnecessary whitespace
        optimized = " ".join(prompt.split())
        
        # Remove redundant phrases
        redundant_phrases = [
            "please note that",
            "it is important to",
            "you should know that",
            "I would like to",
            "I want to"
        ]
        
        for phrase in redundant_phrases:
            optimized = optimized.replace(phrase, "")
        
        # Simplify complex sentences
        optimized = self._simplify_sentences(optimized)
        
        return optimized.strip()
    
    def _optimize_clarity(self, prompt: str) -> str:
        """Optimize prompt for clarity."""
        # Add structure markers
        if "instructions:" not in prompt.lower():
            prompt = f"Instructions: {prompt}"
        
        # Ensure clear action verbs
        action_verbs = ["analyze", "create", "generate", "review", "validate", "optimize"]
        has_action = any(verb in prompt.lower() for verb in action_verbs)
        
        if not has_action:
            prompt = f"{prompt}\n\nPlease provide a clear response."
        
        # Add output format if not specified
        if "format" not in prompt.lower() and "output" not in prompt.lower():
            prompt = f"{prompt}\n\nPlease provide your response in a clear, structured format."
        
        return prompt
    
    def _optimize_context(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Optimize prompt for context usage."""
        if not context:
            return prompt
        
        # Add relevant context at the beginning
        context_str = "Context:\n"
        for key, value in context.items():
            if isinstance(value, str) and len(value) < 200:  # Only add short context
                context_str += f"- {key}: {value}\n"
        
        if context_str != "Context:\n":
            prompt = f"{context_str}\n{prompt}"
        
        return prompt
    
    def _optimize_performance(self, prompt: str) -> str:
        """Optimize prompt for performance."""
        # Add performance hints
        if "efficient" not in prompt.lower() and "performance" not in prompt.lower():
            prompt = f"{prompt}\n\nPlease provide an efficient solution."
        
        # Add timeout hints if not present
        if "timeout" not in prompt.lower() and "quick" not in prompt.lower():
            prompt = f"{prompt}\n\nPlease respond quickly and efficiently."
        
        return prompt
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _calculate_improvement_score(self, original: str, optimized: str) -> float:
        """Calculate improvement score between original and optimized prompts."""
        original_tokens = self._count_tokens(original)
        optimized_tokens = self._count_tokens(optimized)
        
        # Token reduction score (0-1)
        token_score = min(1.0, (original_tokens - optimized_tokens) / original_tokens)
        
        # Clarity improvement score
        original_clarity = self._analyze_clarity(original)
        optimized_clarity = self._analyze_clarity(optimized)
        clarity_score = max(0, optimized_clarity - original_clarity)
        
        # Combined score
        return (token_score * 0.6) + (clarity_score * 0.4)
    
    def _estimate_performance_gain(self, token_reduction: int) -> float:
        """Estimate performance gain from token reduction."""
        # Rough estimation: 1 token ≈ 0.01 seconds processing time
        return token_reduction * 0.01
    
    def _analyze_clarity(self, prompt: str) -> float:
        """Analyze prompt clarity (0-1 score)."""
        score = 1.0
        
        # Penalize very long sentences
        sentences = prompt.split('.')
        for sentence in sentences:
            if len(sentence.split()) > 30:
                score -= 0.1
        
        # Penalize complex words
        complex_words = ["notwithstanding", "aforementioned", "subsequently", "consequently"]
        for word in complex_words:
            if word in prompt.lower():
                score -= 0.05
        
        # Bonus for clear structure
        if "instructions:" in prompt.lower():
            score += 0.1
        if "please" in prompt.lower():
            score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _analyze_context_efficiency(self, prompt: str) -> float:
        """Analyze context efficiency (0-1 score)."""
        # Simple heuristic: shorter prompts are more context efficient
        word_count = len(prompt.split())
        if word_count < 50:
            return 1.0
        elif word_count < 100:
            return 0.8
        elif word_count < 200:
            return 0.6
        else:
            return 0.4
    
    def _simplify_sentences(self, text: str) -> str:
        """Simplify complex sentences."""
        # Basic sentence simplification
        sentences = text.split('.')
        simplified = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) > 25:
                # Split long sentences
                words = sentence.split()
                mid = len(words) // 2
                simplified.append(' '.join(words[:mid]))
                simplified.append(' '.join(words[mid:]))
            else:
                simplified.append(sentence)
        
        return '. '.join(simplified)
    
    def _generate_cache_key(self, prompt: str, strategy: OptimizationStrategy,
                           context: Dict[str, Any] = None) -> str:
        """Generate cache key for optimization result."""
        content = f"{prompt}:{strategy.value}:{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _save_optimization_result(self, result: OptimizationResult, cache_key: str):
        """Save optimization result to file."""
        # Ensure directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)


# Global optimizer instance
_optimizer = None

def get_prompt_optimizer() -> PromptOptimizer:
    """Get the global prompt optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = PromptOptimizer()
    return _optimizer
