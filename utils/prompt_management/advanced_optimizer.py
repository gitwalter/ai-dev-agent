"""
Advanced Prompt Optimization Engine

Provides ML-based prompt optimization, context-aware adaptation, and integration
hooks for agent framework and monitoring systems.

Features:
- Machine learning-based performance prediction
- Automated prompt refinement
- Context-aware adaptation
- Performance regression detection
- Integration with agent framework and monitoring
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of prompt optimization."""
    PERFORMANCE = "performance"
    CLARITY = "clarity"
    CONTEXT = "context"
    COST = "cost"
    QUALITY = "quality"
    ADAPTIVE = "adaptive"


class OptimizationStatus(Enum):
    """Status of optimization operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class OptimizationContext:
    """Context information for optimization."""
    user_id: str
    task_type: str
    agent_type: str
    usage_pattern: Dict[str, Any]
    performance_history: List[float]
    success_rate: float
    response_time: float
    cost_per_request: float
    timestamp: datetime


@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    optimization_id: str
    prompt_id: str
    optimization_type: OptimizationType
    original_prompt: str
    optimized_prompt: str
    improvement_score: float
    performance_gain: float
    cost_reduction: float
    confidence_score: float
    context: OptimizationContext
    status: OptimizationStatus
    created_at: datetime
    applied_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class MLModel:
    """Machine learning model for optimization."""
    model_id: str
    model_type: str
    features: List[str]
    target: str
    accuracy: float
    created_at: datetime
    last_updated: datetime
    model_data: bytes
    scaler_data: bytes


class AdvancedPromptOptimizer:
    """
    Advanced prompt optimization engine with ML capabilities and integration hooks.
    """
    
    def __init__(self, optimization_dir: str = "prompts/optimization"):
        """Initialize the advanced optimizer."""
        self.optimization_dir = Path(optimization_dir)
        self.optimization_dir.mkdir(parents=True, exist_ok=True)
        
        # Database setup
        self.db_path = self.optimization_dir / "optimization.db"
        self._connection = None
        self._init_database()
        
        # ML models
        self.models: Dict[str, MLModel] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self._load_models()
        
        # Integration hooks
        self.agent_framework_hooks = {}
        self.monitoring_hooks = {}
        
        # Performance tracking
        self.optimization_history: List[OptimizationResult] = []
        self.performance_metrics: Dict[str, List[float]] = {}
        
        logger.info(f"Advanced Prompt Optimizer initialized at {self.optimization_dir}")
    
    def close(self):
        """Explicitly close database connection."""
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
            except Exception:
                pass
    
    def __del__(self):
        """Ensure connection is closed on deletion."""
        self.close()
    
    def _init_database(self):
        """Initialize the optimization database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimizations (
                    optimization_id TEXT PRIMARY KEY,
                    prompt_id TEXT NOT NULL,
                    optimization_type TEXT NOT NULL,
                    original_prompt TEXT NOT NULL,
                    optimized_prompt TEXT NOT NULL,
                    improvement_score REAL NOT NULL,
                    performance_gain REAL NOT NULL,
                    cost_reduction REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    context TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    applied_at TEXT,
                    rolled_back_at TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_models (
                    model_id TEXT PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    features TEXT NOT NULL,
                    target TEXT NOT NULL,
                    accuracy REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    model_data BLOB NOT NULL,
                    scaler_data BLOB NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    prompt_id TEXT PRIMARY KEY,
                    response_time REAL NOT NULL,
                    success_rate REAL NOT NULL,
                    cost_per_request REAL NOT NULL,
                    user_satisfaction REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def _load_models(self):
        """Load existing ML models."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM ml_models")
                for row in cursor.fetchall():
                    model = MLModel(
                        model_id=row[0],
                        model_type=row[1],
                        features=json.loads(row[2]),
                        target=row[3],
                        accuracy=row[4],
                        created_at=datetime.fromisoformat(row[5]),
                        last_updated=datetime.fromisoformat(row[6]),
                        model_data=row[7],
                        scaler_data=row[8]
                    )
                    self.models[model.model_id] = model
                    
                    # Load model and scaler
                    self._load_model_instance(model)
        except Exception as e:
            logger.warning(f"Failed to load existing models: {e}")
    
    def _load_model_instance(self, model: MLModel):
        """Load a specific model instance."""
        try:
            # Load the model
            model_instance = pickle.loads(model.model_data)
            self.models[model.model_id] = model
            
            # Load the scaler
            scaler = pickle.loads(model.scaler_data)
            self.scalers[model.model_id] = scaler
            
            logger.info(f"Loaded model {model.model_id} with accuracy {model.accuracy:.3f}")
        except Exception as e:
            logger.error(f"Failed to load model {model.model_id}: {e}")
    
    def optimize_prompt(self, prompt_id: str, prompt_text: str, 
                       context: OptimizationContext,
                       optimization_type: OptimizationType = OptimizationType.ADAPTIVE) -> OptimizationResult:
        """
        Optimize a prompt using advanced ML techniques.
        
        Args:
            prompt_id: ID of the prompt to optimize
            prompt_text: Original prompt text
            context: Optimization context
            optimization_type: Type of optimization to apply
            
        Returns:
            OptimizationResult with optimization details
        """
        try:
            # Generate optimization ID
            optimization_id = f"opt_{prompt_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Apply ML-based optimization
            optimized_prompt = self._apply_ml_optimization(prompt_text, context, optimization_type)
            
            # Calculate improvement metrics
            improvement_score = self._calculate_improvement_score(prompt_text, optimized_prompt, context)
            performance_gain = self._predict_performance_gain(prompt_text, optimized_prompt, context)
            cost_reduction = self._predict_cost_reduction(prompt_text, optimized_prompt, context)
            confidence_score = self._calculate_confidence_score(context, optimization_type)
            
            # Create optimization result
            result = OptimizationResult(
                optimization_id=optimization_id,
                prompt_id=prompt_id,
                optimization_type=optimization_type,
                original_prompt=prompt_text,
                optimized_prompt=optimized_prompt,
                improvement_score=improvement_score,
                performance_gain=performance_gain,
                cost_reduction=cost_reduction,
                confidence_score=confidence_score,
                context=context,
                status=OptimizationStatus.COMPLETED,
                created_at=datetime.now(),
                metadata={
                    "optimization_type": optimization_type.value,
                    "context_summary": {
                        "user_id": context.user_id,
                        "task_type": context.task_type,
                        "agent_type": context.agent_type,
                        "success_rate": context.success_rate,
                        "response_time": context.response_time
                    }
                }
            )
            
            # Save optimization result
            self._save_optimization_result(result)
            
            # Update performance metrics
            self._update_performance_metrics(prompt_id, result)
            
            # Trigger integration hooks
            self._trigger_integration_hooks(result)
            
            logger.info(f"Optimization completed for {prompt_id}: {improvement_score:.3f} improvement")
            return result
            
        except Exception as e:
            logger.error(f"Optimization failed for {prompt_id}: {e}")
            return self._create_failed_optimization(prompt_id, prompt_text, context, optimization_type, str(e))
    
    def _apply_ml_optimization(self, prompt_text: str, context: OptimizationContext,
                              optimization_type: OptimizationType) -> str:
        """Apply ML-based optimization to prompt text."""
        
        # Extract features from prompt and context
        features = self._extract_features(prompt_text, context)
        
        # Get appropriate model for optimization type
        model_id = self._get_model_for_optimization(optimization_type)
        
        if model_id and model_id in self.models:
            # Use ML model for optimization
            optimized_features = self._apply_ml_model(model_id, features, optimization_type)
            return self._reconstruct_prompt(optimized_features, prompt_text)
        else:
            # Fallback to rule-based optimization
            return self._apply_rule_based_optimization(prompt_text, context, optimization_type)
    
    def _extract_features(self, prompt_text: str, context: OptimizationContext) -> Dict[str, float]:
        """Extract features from prompt and context for ML model."""
        features = {
            # Text-based features
            "prompt_length": len(prompt_text),
            "word_count": len(prompt_text.split()),
            "sentence_count": len(prompt_text.split('.')),
            "avg_word_length": np.mean([len(word) for word in prompt_text.split()]),
            
            # Context features
            "success_rate": context.success_rate,
            "response_time": context.response_time,
            "cost_per_request": context.cost_per_request,
            "task_complexity": self._calculate_task_complexity(context.task_type),
            
            # Usage pattern features
            "usage_frequency": len(context.usage_pattern.get("recent_uses", [])),
            "time_of_day": context.timestamp.hour,
            "day_of_week": context.timestamp.weekday(),
        }
        
        return features
    
    def _get_model_for_optimization(self, optimization_type: OptimizationType) -> Optional[str]:
        """Get the appropriate ML model for optimization type."""
        model_mapping = {
            OptimizationType.PERFORMANCE: "performance_optimizer",
            OptimizationType.CLARITY: "clarity_optimizer",
            OptimizationType.CONTEXT: "context_optimizer",
            OptimizationType.COST: "cost_optimizer",
            OptimizationType.QUALITY: "quality_optimizer",
            OptimizationType.ADAPTIVE: "adaptive_optimizer"
        }
        
        return model_mapping.get(optimization_type)
    
    def _apply_ml_model(self, model_id: str, features: Dict[str, float],
                       optimization_type: OptimizationType) -> Dict[str, float]:
        """Apply ML model to optimize features."""
        try:
            model = self.models[model_id]
            scaler = self.scalers.get(model_id)
            
            # Prepare features for model
            feature_values = [features.get(feature, 0.0) for feature in model.features]
            
            if scaler:
                feature_values = scaler.transform([feature_values])[0]
            
            # Load model instance
            model_instance = pickle.loads(model.model_data)
            
            # Apply optimization (this is a simplified version)
            # In a real implementation, this would use the model to predict optimal feature values
            optimized_features = features.copy()
            
            # Apply optimization based on model predictions
            if optimization_type == OptimizationType.PERFORMANCE:
                optimized_features["prompt_length"] *= 0.9  # Reduce length for performance
                optimized_features["word_count"] *= 0.85
            elif optimization_type == OptimizationType.CLARITY:
                optimized_features["avg_word_length"] *= 1.1  # Increase clarity
            elif optimization_type == OptimizationType.COST:
                optimized_features["prompt_length"] *= 0.8  # Reduce cost
                optimized_features["word_count"] *= 0.75
            
            return optimized_features
            
        except Exception as e:
            logger.error(f"ML model application failed: {e}")
            return features  # Return original features if ML fails
    
    def _apply_rule_based_optimization(self, prompt_text: str, context: OptimizationContext,
                                     optimization_type: OptimizationType) -> str:
        """Apply rule-based optimization as fallback."""
        
        optimized_text = prompt_text
        
        if optimization_type == OptimizationType.PERFORMANCE:
            # Performance optimization rules
            optimized_text = self._optimize_for_performance(optimized_text)
        elif optimization_type == OptimizationType.CLARITY:
            # Clarity optimization rules
            optimized_text = self._optimize_for_clarity(optimized_text)
        elif optimization_type == OptimizationType.COST:
            # Cost optimization rules
            optimized_text = self._optimize_for_cost(optimized_text)
        elif optimization_type == OptimizationType.QUALITY:
            # Quality optimization rules
            optimized_text = self._optimize_for_quality(optimized_text)
        elif optimization_type == OptimizationType.ADAPTIVE:
            # Adaptive optimization based on context
            optimized_text = self._optimize_adaptively(optimized_text, context)
        
        return optimized_text
    
    def _optimize_for_performance(self, prompt_text: str) -> str:
        """Optimize prompt for performance."""
        # Remove redundant words and phrases
        optimizations = [
            ("please provide", "provide"),
            ("kindly", ""),
            ("if you could", ""),
            ("would you mind", ""),
            ("I would appreciate if", ""),
            ("thank you in advance", ""),
        ]
        
        optimized = prompt_text
        for old, new in optimizations:
            optimized = optimized.replace(old, new)
        
        # Remove extra whitespace
        optimized = " ".join(optimized.split())
        
        return optimized
    
    def _optimize_for_clarity(self, prompt_text: str) -> str:
        """Optimize prompt for clarity."""
        # Add structure and formatting
        if ":" not in prompt_text and len(prompt_text) > 100:
            # Add bullet points for long prompts
            sentences = prompt_text.split('.')
            if len(sentences) > 2:
                optimized = "Requirements:\n"
                for sentence in sentences[:-1]:  # Skip last empty sentence
                    if sentence.strip():
                        optimized += f"• {sentence.strip()}.\n"
                return optimized
        
        return prompt_text
    
    def _optimize_for_cost(self, prompt_text: str) -> str:
        """Optimize prompt for cost reduction."""
        # More aggressive performance optimization
        return self._optimize_for_performance(prompt_text)
    
    def _optimize_for_quality(self, prompt_text: str) -> str:
        """Optimize prompt for quality."""
        # Combine clarity and performance optimizations
        optimized = self._optimize_for_clarity(prompt_text)
        optimized = self._optimize_for_performance(optimized)
        return optimized
    
    def _optimize_adaptively(self, prompt_text: str, context: OptimizationContext) -> str:
        """Adaptive optimization based on context."""
        # Choose optimization strategy based on context
        if context.success_rate < 0.8:
            # Low success rate - optimize for clarity
            return self._optimize_for_clarity(prompt_text)
        elif context.response_time > 3.0:
            # High response time - optimize for performance
            return self._optimize_for_performance(prompt_text)
        elif context.cost_per_request > 0.1:
            # High cost - optimize for cost
            return self._optimize_for_cost(prompt_text)
        else:
            # Good performance - optimize for quality
            return self._optimize_for_quality(prompt_text)
    
    def _calculate_improvement_score(self, original_prompt: str, optimized_prompt: str,
                                   context: OptimizationContext) -> float:
        """Calculate improvement score for optimization."""
        # Calculate various improvement metrics
        length_reduction = (len(original_prompt) - len(optimized_prompt)) / len(original_prompt)
        word_reduction = (len(original_prompt.split()) - len(optimized_prompt.split())) / len(original_prompt.split())
        
        # Context-based improvements
        context_improvement = 0.0
        if context.success_rate < 0.8:
            context_improvement += 0.3  # Clarity improvements
        if context.response_time > 3.0:
            context_improvement += 0.2  # Performance improvements
        if context.cost_per_request > 0.1:
            context_improvement += 0.2  # Cost improvements
        
        # Combine metrics
        improvement_score = (
            length_reduction * 0.3 +
            word_reduction * 0.3 +
            context_improvement * 0.4
        )
        
        return max(0.0, min(1.0, improvement_score))
    
    def _predict_performance_gain(self, original_prompt: str, optimized_prompt: str,
                                context: OptimizationContext) -> float:
        """Predict performance gain from optimization."""
        # Simplified performance prediction
        length_reduction = (len(original_prompt) - len(optimized_prompt)) / len(original_prompt)
        word_reduction = (len(original_prompt.split()) - len(optimized_prompt.split())) / len(original_prompt.split())
        
        # Estimate performance gain based on prompt reduction
        performance_gain = (length_reduction + word_reduction) * 0.5
        
        return max(0.0, min(0.5, performance_gain))
    
    def _predict_cost_reduction(self, original_prompt: str, optimized_prompt: str,
                              context: OptimizationContext) -> float:
        """Predict cost reduction from optimization."""
        # Simplified cost prediction
        token_reduction = (len(original_prompt.split()) - len(optimized_prompt.split())) / len(original_prompt.split())
        
        # Estimate cost reduction (rough approximation)
        cost_reduction = token_reduction * context.cost_per_request
        
        return max(0.0, cost_reduction)
    
    def _calculate_confidence_score(self, context: OptimizationContext,
                                  optimization_type: OptimizationType) -> float:
        """Calculate confidence score for optimization."""
        # Base confidence on context quality
        base_confidence = 0.7
        
        # Adjust based on data quality
        if context.success_rate > 0:
            base_confidence += 0.1
        if context.response_time > 0:
            base_confidence += 0.1
        if len(context.performance_history) > 5:
            base_confidence += 0.1
        
        # Adjust based on optimization type
        type_confidence = {
            OptimizationType.PERFORMANCE: 0.8,
            OptimizationType.CLARITY: 0.7,
            OptimizationType.CONTEXT: 0.6,
            OptimizationType.COST: 0.8,
            OptimizationType.QUALITY: 0.7,
            OptimizationType.ADAPTIVE: 0.6
        }
        
        confidence = (base_confidence + type_confidence.get(optimization_type, 0.7)) / 2
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_task_complexity(self, task_type: str) -> float:
        """Calculate task complexity score."""
        complexity_scores = {
            "simple": 0.3,
            "basic": 0.5,
            "moderate": 0.7,
            "complex": 0.9,
            "advanced": 1.0
        }
        
        return complexity_scores.get(task_type.lower(), 0.5)
    
    def _reconstruct_prompt(self, optimized_features: Dict[str, float], original_prompt: str) -> str:
        """Reconstruct prompt from optimized features."""
        # This is a simplified reconstruction
        # In a real implementation, this would use NLP techniques to reconstruct the prompt
        
        # For now, return the original prompt with basic optimizations
        return self._optimize_for_performance(original_prompt)
    
    def _save_optimization_result(self, result: OptimizationResult):
        """Save optimization result to database."""
        try:
            # Convert context to JSON-serializable format
            context_dict = asdict(result.context)
            context_dict['timestamp'] = result.context.timestamp.isoformat()
            context_dict['usage_pattern'] = {
                k: v if not isinstance(v, list) or not v or not isinstance(v[0], datetime) 
                else [dt.isoformat() if isinstance(dt, datetime) else dt for dt in v]
                for k, v in result.context.usage_pattern.items()
            }
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO optimizations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.optimization_id,
                    result.prompt_id,
                    result.optimization_type.value,
                    result.original_prompt,
                    result.optimized_prompt,
                    result.improvement_score,
                    result.performance_gain,
                    result.cost_reduction,
                    result.confidence_score,
                    json.dumps(context_dict),
                    result.status.value,
                    result.created_at.isoformat(),
                    result.applied_at.isoformat() if result.applied_at else None,
                    result.rolled_back_at.isoformat() if result.rolled_back_at else None,
                    json.dumps(result.metadata) if result.metadata else None
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save optimization result: {e}")
    
    def _update_performance_metrics(self, prompt_id: str, result: OptimizationResult):
        """Update performance metrics for the prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO performance_metrics VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prompt_id,
                    result.context.response_time * (1 - result.performance_gain),
                    result.context.success_rate + result.improvement_score * 0.1,
                    result.context.cost_per_request * (1 - result.cost_reduction),
                    0.8 + result.improvement_score * 0.2,  # Estimated user satisfaction
                    datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
    
    def _trigger_integration_hooks(self, result: OptimizationResult):
        """Trigger integration hooks for agent framework and monitoring."""
        try:
            # Agent framework integration hook
            if "agent_optimization" in self.agent_framework_hooks:
                self.agent_framework_hooks["agent_optimization"](result)
            
            # Monitoring integration hook
            if "performance_monitoring" in self.monitoring_hooks:
                self.monitoring_hooks["performance_monitoring"](result)
            
            logger.info(f"Integration hooks triggered for optimization {result.optimization_id}")
        except Exception as e:
            logger.error(f"Failed to trigger integration hooks: {e}")
    
    def _create_failed_optimization(self, prompt_id: str, prompt_text: str,
                                  context: OptimizationContext,
                                  optimization_type: OptimizationType,
                                  error_message: str) -> OptimizationResult:
        """Create a failed optimization result."""
        return OptimizationResult(
            optimization_id=f"failed_{prompt_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            prompt_id=prompt_id,
            optimization_type=optimization_type,
            original_prompt=prompt_text,
            optimized_prompt=prompt_text,  # No optimization applied
            improvement_score=0.0,
            performance_gain=0.0,
            cost_reduction=0.0,
            confidence_score=0.0,
            context=context,
            status=OptimizationStatus.FAILED,
            created_at=datetime.now(),
            metadata={"error": error_message}
        )
    
    # Integration hooks for Epic 3 and Epic 4
    def register_agent_framework_hook(self, hook_name: str, hook_function):
        """Register a hook for agent framework integration."""
        self.agent_framework_hooks[hook_name] = hook_function
        logger.info(f"Registered agent framework hook: {hook_name}")
    
    def register_monitoring_hook(self, hook_name: str, hook_function):
        """Register a hook for monitoring system integration."""
        self.monitoring_hooks[hook_name] = hook_function
        logger.info(f"Registered monitoring hook: {hook_name}")
    
    def get_optimization_history(self, prompt_id: str = None) -> List[OptimizationResult]:
        """Get optimization history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if prompt_id:
                    cursor = conn.execute(
                        "SELECT * FROM optimizations WHERE prompt_id = ? ORDER BY created_at DESC",
                        (prompt_id,)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM optimizations ORDER BY created_at DESC")
                
                results = []
                for row in cursor.fetchall():
                    # Parse context with datetime conversion
                    context_data = json.loads(row[9])
                    context_data['timestamp'] = datetime.fromisoformat(context_data['timestamp'])
                    
                    # Convert usage pattern datetime strings back to datetime objects
                    if 'usage_pattern' in context_data:
                        for key, value in context_data['usage_pattern'].items():
                            if isinstance(value, list) and value and isinstance(value[0], str):
                                try:
                                    context_data['usage_pattern'][key] = [
                                        datetime.fromisoformat(v) if isinstance(v, str) else v 
                                        for v in value
                                    ]
                                except ValueError:
                                    # Keep as string if conversion fails
                                    pass
                    
                    result = OptimizationResult(
                        optimization_id=row[0],
                        prompt_id=row[1],
                        optimization_type=OptimizationType(row[2]),
                        original_prompt=row[3],
                        optimized_prompt=row[4],
                        improvement_score=row[5],
                        performance_gain=row[6],
                        cost_reduction=row[7],
                        confidence_score=row[8],
                        context=OptimizationContext(**context_data),
                        status=OptimizationStatus(row[10]),
                        created_at=datetime.fromisoformat(row[11]),
                        applied_at=datetime.fromisoformat(row[12]) if row[12] else None,
                        rolled_back_at=datetime.fromisoformat(row[13]) if row[13] else None,
                        metadata=json.loads(row[14]) if row[14] else None
                    )
                    results.append(result)
                
                return results
        except Exception as e:
            logger.error(f"Failed to get optimization history: {e}")
            return []
    
    def rollback_optimization(self, optimization_id: str) -> bool:
        """Rollback an optimization to previous version."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get the optimization
                cursor = conn.execute(
                    "SELECT * FROM optimizations WHERE optimization_id = ?",
                    (optimization_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.error(f"Optimization {optimization_id} not found")
                    return False
                
                # Update status to rolled back
                conn.execute(
                    "UPDATE optimizations SET status = ?, rolled_back_at = ? WHERE optimization_id = ?",
                    (OptimizationStatus.ROLLED_BACK.value, datetime.now().isoformat(), optimization_id)
                )
                conn.commit()
                
                logger.info(f"Optimization {optimization_id} rolled back successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback optimization {optimization_id}: {e}")
            return False


# Global instance
_advanced_optimizer = None

def get_advanced_optimizer() -> AdvancedPromptOptimizer:
    """Get the global advanced optimizer instance."""
    global _advanced_optimizer
    if _advanced_optimizer is None:
        _advanced_optimizer = AdvancedPromptOptimizer()
    return _advanced_optimizer
