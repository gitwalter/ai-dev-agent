"""
Prompt Analytics Engine

Provides comprehensive analytics and optimization recommendations for prompt management.
Includes performance tracking, cost analysis, quality assessment, and trend analysis.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked for prompts."""
    PERFORMANCE = "performance"
    COST = "cost"
    QUALITY = "quality"
    USAGE = "usage"
    OPTIMIZATION = "optimization"


class TrendDirection(Enum):
    """Trend direction for analytics."""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    UNKNOWN = "unknown"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a prompt."""
    prompt_id: str
    response_time: float  # seconds
    token_count: int
    success_rate: float  # 0.0 to 1.0
    error_rate: float  # 0.0 to 1.0
    user_satisfaction: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class CostMetrics:
    """Cost metrics for a prompt."""
    prompt_id: str
    input_tokens: int
    output_tokens: int
    total_cost: float  # USD
    cost_per_request: float  # USD
    model_used: str
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class QualityMetrics:
    """Quality metrics for a prompt."""
    prompt_id: str
    clarity_score: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    completeness_score: float  # 0.0 to 1.0
    consistency_score: float  # 0.0 to 1.0
    overall_quality: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation for a prompt."""
    prompt_id: str
    recommendation_type: str
    description: str
    expected_improvement: float  # percentage
    confidence_score: float  # 0.0 to 1.0
    implementation_effort: str  # "low", "medium", "high"
    priority: str  # "low", "medium", "high", "critical"
    created_at: datetime
    metadata: Dict[str, Any] = None


@dataclass
class TrendAnalysis:
    """Trend analysis for metrics."""
    prompt_id: str
    metric_type: MetricType
    trend_direction: TrendDirection
    change_percentage: float
    time_period: str  # "1h", "24h", "7d", "30d"
    confidence: float  # 0.0 to 1.0
    analysis_date: datetime
    metadata: Dict[str, Any] = None


class PromptAnalytics:
    """
    Comprehensive analytics engine for prompt performance, cost, and quality.
    """
    
    def __init__(self, analytics_dir: str = "prompts/analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # Database for analytics data
        self.db_path = self.analytics_dir / "analytics.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize the analytics database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Performance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT NOT NULL,
                        response_time REAL NOT NULL,
                        token_count INTEGER NOT NULL,
                        success_rate REAL NOT NULL,
                        error_rate REAL NOT NULL,
                        user_satisfaction REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Cost metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cost_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT NOT NULL,
                        input_tokens INTEGER NOT NULL,
                        output_tokens INTEGER NOT NULL,
                        total_cost REAL NOT NULL,
                        cost_per_request REAL NOT NULL,
                        model_used TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Quality metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quality_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT NOT NULL,
                        clarity_score REAL NOT NULL,
                        relevance_score REAL NOT NULL,
                        completeness_score REAL NOT NULL,
                        consistency_score REAL NOT NULL,
                        overall_quality REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Optimization recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT NOT NULL,
                        recommendation_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        expected_improvement REAL NOT NULL,
                        confidence_score REAL NOT NULL,
                        implementation_effort TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        metadata TEXT,
                        status TEXT DEFAULT 'pending'
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_prompt_id ON performance_metrics(prompt_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_prompt_id ON cost_metrics(prompt_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_timestamp ON cost_metrics(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_prompt_id ON quality_metrics(prompt_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_timestamp ON quality_metrics(timestamp)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")
            raise
    
    def record_performance_metrics(self, metrics: PerformanceMetrics) -> bool:
        """Record performance metrics for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO performance_metrics 
                    (prompt_id, response_time, token_count, success_rate, error_rate, 
                     user_satisfaction, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.prompt_id,
                    metrics.response_time,
                    metrics.token_count,
                    metrics.success_rate,
                    metrics.error_rate,
                    metrics.user_satisfaction,
                    metrics.timestamp.isoformat(),
                    json.dumps(metrics.metadata) if metrics.metadata else None
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {e}")
            return False
    
    def record_cost_metrics(self, metrics: CostMetrics) -> bool:
        """Record cost metrics for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cost_metrics 
                    (prompt_id, input_tokens, output_tokens, total_cost, cost_per_request,
                     model_used, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.prompt_id,
                    metrics.input_tokens,
                    metrics.output_tokens,
                    metrics.total_cost,
                    metrics.cost_per_request,
                    metrics.model_used,
                    metrics.timestamp.isoformat(),
                    json.dumps(metrics.metadata) if metrics.metadata else None
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record cost metrics: {e}")
            return False
    
    def record_quality_metrics(self, metrics: QualityMetrics) -> bool:
        """Record quality metrics for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quality_metrics 
                    (prompt_id, clarity_score, relevance_score, completeness_score,
                     consistency_score, overall_quality, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.prompt_id,
                    metrics.clarity_score,
                    metrics.relevance_score,
                    metrics.completeness_score,
                    metrics.consistency_score,
                    metrics.overall_quality,
                    metrics.timestamp.isoformat(),
                    json.dumps(metrics.metadata) if metrics.metadata else None
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record quality metrics: {e}")
            return False
    
    def get_performance_summary(self, prompt_id: str, time_period: str = "24h") -> Dict[str, Any]:
        """Get performance summary for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate time filter
                time_filter = self._get_time_filter(time_period)
                
                cursor.execute("""
                    SELECT 
                        AVG(response_time) as avg_response_time,
                        AVG(token_count) as avg_token_count,
                        AVG(success_rate) as avg_success_rate,
                        AVG(error_rate) as avg_error_rate,
                        AVG(user_satisfaction) as avg_user_satisfaction,
                        COUNT(*) as total_requests
                    FROM performance_metrics 
                    WHERE prompt_id = ? AND timestamp >= ?
                """, (prompt_id, time_filter))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "prompt_id": prompt_id,
                        "time_period": time_period,
                        "avg_response_time": row[0],
                        "avg_token_count": row[1],
                        "avg_success_rate": row[2],
                        "avg_error_rate": row[3],
                        "avg_user_satisfaction": row[4],
                        "total_requests": row[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return None
    
    def get_cost_summary(self, prompt_id: str, time_period: str = "24h") -> Dict[str, Any]:
        """Get cost summary for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate time filter
                time_filter = self._get_time_filter(time_period)
                
                cursor.execute("""
                    SELECT 
                        SUM(total_cost) as total_cost,
                        AVG(cost_per_request) as avg_cost_per_request,
                        SUM(input_tokens) as total_input_tokens,
                        SUM(output_tokens) as total_output_tokens,
                        COUNT(*) as total_requests
                    FROM cost_metrics 
                    WHERE prompt_id = ? AND timestamp >= ?
                """, (prompt_id, time_filter))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "prompt_id": prompt_id,
                        "time_period": time_period,
                        "total_cost": row[0],
                        "avg_cost_per_request": row[1],
                        "total_input_tokens": row[2],
                        "total_output_tokens": row[3],
                        "total_requests": row[4]
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get cost summary: {e}")
            return None
    
    def get_quality_summary(self, prompt_id: str, time_period: str = "24h") -> Dict[str, Any]:
        """Get quality summary for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate time filter
                time_filter = self._get_time_filter(time_period)
                
                cursor.execute("""
                    SELECT 
                        AVG(clarity_score) as avg_clarity_score,
                        AVG(relevance_score) as avg_relevance_score,
                        AVG(completeness_score) as avg_completeness_score,
                        AVG(consistency_score) as avg_consistency_score,
                        AVG(overall_quality) as avg_overall_quality,
                        COUNT(*) as total_assessments
                    FROM quality_metrics 
                    WHERE prompt_id = ? AND timestamp >= ?
                """, (prompt_id, time_filter))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "prompt_id": prompt_id,
                        "time_period": time_period,
                        "avg_clarity_score": row[0],
                        "avg_relevance_score": row[1],
                        "avg_completeness_score": row[2],
                        "avg_consistency_score": row[3],
                        "avg_overall_quality": row[4],
                        "total_assessments": row[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get quality summary: {e}")
            return None
    
    def generate_optimization_recommendations(self, prompt_id: str) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations for a prompt."""
        recommendations = []
        
        try:
            # Get current metrics
            performance = self.get_performance_summary(prompt_id)
            cost = self.get_cost_summary(prompt_id)
            quality = self.get_quality_summary(prompt_id)
            
            if not performance or not cost or not quality:
                return recommendations
            
            # Performance-based recommendations
            if performance["avg_response_time"] > 3.0:
                recommendations.append(OptimizationRecommendation(
                    prompt_id=prompt_id,
                    recommendation_type="performance_optimization",
                    description="Response time is above 3 seconds. Consider simplifying the prompt or using a faster model.",
                    expected_improvement=25.0,
                    confidence_score=0.8,
                    implementation_effort="medium",
                    priority="high",
                    created_at=datetime.now(),
                    metadata={"current_response_time": performance["avg_response_time"]}
                ))
            
            # Cost-based recommendations
            if cost["avg_cost_per_request"] > 0.10:
                recommendations.append(OptimizationRecommendation(
                    prompt_id=prompt_id,
                    recommendation_type="cost_optimization",
                    description="Cost per request is high. Consider reducing token usage or using a more cost-effective model.",
                    expected_improvement=30.0,
                    confidence_score=0.7,
                    implementation_effort="medium",
                    priority="medium",
                    created_at=datetime.now(),
                    metadata={"current_cost_per_request": cost["avg_cost_per_request"]}
                ))
            
            # Quality-based recommendations
            if quality["avg_overall_quality"] < 0.7:
                recommendations.append(OptimizationRecommendation(
                    prompt_id=prompt_id,
                    recommendation_type="quality_improvement",
                    description="Overall quality score is below 0.7. Consider improving prompt clarity and specificity.",
                    expected_improvement=20.0,
                    confidence_score=0.6,
                    implementation_effort="high",
                    priority="high",
                    created_at=datetime.now(),
                    metadata={"current_quality_score": quality["avg_overall_quality"]}
                ))
            
            # Success rate recommendations
            if performance["avg_success_rate"] < 0.9:
                recommendations.append(OptimizationRecommendation(
                    prompt_id=prompt_id,
                    recommendation_type="reliability_improvement",
                    description="Success rate is below 90%. Consider adding error handling and fallback strategies.",
                    expected_improvement=15.0,
                    confidence_score=0.8,
                    implementation_effort="high",
                    priority="critical",
                    created_at=datetime.now(),
                    metadata={"current_success_rate": performance["avg_success_rate"]}
                ))
            
            # Save recommendations to database
            self._save_recommendations(recommendations)
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
        
        return recommendations
    
    def _save_recommendations(self, recommendations: List[OptimizationRecommendation]):
        """Save optimization recommendations to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for rec in recommendations:
                    cursor.execute("""
                        INSERT INTO optimization_recommendations 
                        (prompt_id, recommendation_type, description, expected_improvement,
                         confidence_score, implementation_effort, priority, created_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        rec.prompt_id,
                        rec.recommendation_type,
                        rec.description,
                        rec.expected_improvement,
                        rec.confidence_score,
                        rec.implementation_effort,
                        rec.priority,
                        rec.created_at.isoformat(),
                        json.dumps(rec.metadata) if rec.metadata else None
                    ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save recommendations: {e}")
    
    def get_trend_analysis(self, prompt_id: str, metric_type: MetricType, time_period: str = "7d") -> TrendAnalysis:
        """Analyze trends for a specific metric."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current and previous period data
                current_filter = self._get_time_filter(time_period)
                previous_filter = self._get_time_filter(time_period, offset=True)
                
                if metric_type == MetricType.PERFORMANCE:
                    current_data = self._get_performance_trend_data(cursor, prompt_id, current_filter)
                    previous_data = self._get_performance_trend_data(cursor, prompt_id, previous_filter)
                elif metric_type == MetricType.COST:
                    current_data = self._get_cost_trend_data(cursor, prompt_id, current_filter)
                    previous_data = self._get_cost_trend_data(cursor, prompt_id, previous_filter)
                elif metric_type == MetricType.QUALITY:
                    current_data = self._get_quality_trend_data(cursor, prompt_id, current_filter)
                    previous_data = self._get_quality_trend_data(cursor, prompt_id, previous_filter)
                else:
                    return None
                
                if not current_data or not previous_data:
                    return None
                
                # Calculate trend
                change_percentage = ((current_data - previous_data) / previous_data) * 100
                
                if change_percentage > 5:
                    trend_direction = TrendDirection.IMPROVING
                elif change_percentage < -5:
                    trend_direction = TrendDirection.DECLINING
                else:
                    trend_direction = TrendDirection.STABLE
                
                return TrendAnalysis(
                    prompt_id=prompt_id,
                    metric_type=metric_type,
                    trend_direction=trend_direction,
                    change_percentage=change_percentage,
                    time_period=time_period,
                    confidence=0.8,  # Simplified confidence calculation
                    analysis_date=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Failed to get trend analysis: {e}")
            return None
    
    def _get_time_filter(self, time_period: str, offset: bool = False) -> str:
        """Get timestamp filter for time period."""
        now = datetime.now()
        
        if time_period == "1h":
            delta = timedelta(hours=1)
        elif time_period == "24h":
            delta = timedelta(days=1)
        elif time_period == "7d":
            delta = timedelta(days=7)
        elif time_period == "30d":
            delta = timedelta(days=30)
        else:
            delta = timedelta(days=1)
        
        if offset:
            # For previous period comparison
            start_time = now - (delta * 2)
            end_time = now - delta
        else:
            # For current period
            start_time = now - delta
            end_time = now
        
        return start_time.isoformat()
    
    def _get_performance_trend_data(self, cursor, prompt_id: str, time_filter: str) -> float:
        """Get performance trend data."""
        cursor.execute("""
            SELECT AVG(response_time) FROM performance_metrics 
            WHERE prompt_id = ? AND timestamp >= ?
        """, (prompt_id, time_filter))
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    
    def _get_cost_trend_data(self, cursor, prompt_id: str, time_filter: str) -> float:
        """Get cost trend data."""
        cursor.execute("""
            SELECT AVG(cost_per_request) FROM cost_metrics 
            WHERE prompt_id = ? AND timestamp >= ?
        """, (prompt_id, time_filter))
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    
    def _get_quality_trend_data(self, cursor, prompt_id: str, time_filter: str) -> float:
        """Get quality trend data."""
        cursor.execute("""
            SELECT AVG(overall_quality) FROM quality_metrics 
            WHERE prompt_id = ? AND timestamp >= ?
        """, (prompt_id, time_filter))
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    
    def get_comprehensive_analytics(self, prompt_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a prompt."""
        return {
            "prompt_id": prompt_id,
            "performance": self.get_performance_summary(prompt_id),
            "cost": self.get_cost_summary(prompt_id),
            "quality": self.get_quality_summary(prompt_id),
            "trends": {
                "performance": self.get_trend_analysis(prompt_id, MetricType.PERFORMANCE),
                "cost": self.get_trend_analysis(prompt_id, MetricType.COST),
                "quality": self.get_trend_analysis(prompt_id, MetricType.QUALITY)
            },
            "recommendations": self.generate_optimization_recommendations(prompt_id),
            "generated_at": datetime.now().isoformat()
        }
