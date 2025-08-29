"""
Performance Optimization Module
===============================

Provides performance monitoring, optimization utilities, and metrics recording
for AI agent operations.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    agent_type: str
    operation: str
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    tokens_processed: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    additional_metrics: Dict[str, Any] = field(default_factory=dict)


class PerformanceOptimizer:
    """Performance optimization and monitoring system."""
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.performance_history: List[PerformanceMetrics] = []
        self.optimization_settings = self._init_optimization_settings()
        
        logger.info("Performance Optimizer initialized")
    
    def _init_optimization_settings(self) -> Dict[str, Any]:
        """Initialize optimization settings."""
        return {
            "enable_caching": True,
            "cache_ttl": 3600,  # 1 hour
            "max_retry_attempts": 3,
            "timeout_seconds": 300,
            "batch_size": 10,
            "enable_parallel_processing": True,
            "memory_threshold_mb": 1000,
            "cpu_threshold_percent": 80
        }
    
    def record_performance(self, agent_type: str, operation: str, 
                          execution_time: float, success: bool = True,
                          error_message: Optional[str] = None,
                          additional_metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record performance metrics for an agent operation.
        
        Args:
            agent_type: Type of agent performing the operation
            operation: Name of the operation being performed
            execution_time: Time taken to execute the operation
            success: Whether the operation was successful
            error_message: Error message if operation failed
            additional_metrics: Additional performance metrics
            
        Returns:
            bool: True if recording was successful
        """
        try:
            metrics = PerformanceMetrics(
                agent_type=agent_type,
                operation=operation,
                execution_time=execution_time,
                success=success,
                error_message=error_message,
                additional_metrics=additional_metrics or {}
            )
            
            self.performance_history.append(metrics)
            
            # Log performance issues
            if execution_time > self.optimization_settings["timeout_seconds"]:
                logger.warning(f"Slow operation detected: {agent_type}.{operation} took {execution_time:.2f}s")
            
            if not success:
                logger.error(f"Failed operation: {agent_type}.{operation} - {error_message}")
            
            logger.debug(f"Recorded performance for {agent_type}.{operation}: {execution_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {e}")
            return False
    
    def get_performance_stats(self, agent_type: Optional[str] = None,
                            operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Args:
            agent_type: Filter by agent type (optional)
            operation: Filter by operation (optional)
            
        Returns:
            Dict containing performance statistics
        """
        # Filter metrics
        filtered_metrics = self.performance_history
        
        if agent_type:
            filtered_metrics = [m for m in filtered_metrics if m.agent_type == agent_type]
        
        if operation:
            filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
        
        if not filtered_metrics:
            return {
                "total_operations": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0
            }
        
        # Calculate statistics
        total_operations = len(filtered_metrics)
        successful_operations = len([m for m in filtered_metrics if m.success])
        failed_operations = total_operations - successful_operations
        
        success_rate = (successful_operations / total_operations) * 100
        
        execution_times = [m.execution_time for m in filtered_metrics]
        average_execution_time = sum(execution_times) / len(execution_times)
        min_execution_time = min(execution_times)
        max_execution_time = max(execution_times)
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": success_rate,
            "average_execution_time": average_execution_time,
            "min_execution_time": min_execution_time,
            "max_execution_time": max_execution_time,
            "performance_threshold_violations": len([
                m for m in filtered_metrics 
                if m.execution_time > self.optimization_settings["timeout_seconds"]
            ])
        }
    
    def get_optimization_recommendations(self, agent_type: str) -> List[str]:
        """
        Get optimization recommendations for an agent type.
        
        Args:
            agent_type: Type of agent to analyze
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        stats = self.get_performance_stats(agent_type)
        
        if stats["total_operations"] == 0:
            return ["No performance data available for analysis"]
        
        # Check success rate
        if stats["success_rate"] < 90:
            recommendations.append(
                f"Low success rate ({stats['success_rate']:.1f}%) - "
                f"investigate error handling and retry mechanisms"
            )
        
        # Check execution time
        if stats["average_execution_time"] > 60:
            recommendations.append(
                f"High average execution time ({stats['average_execution_time']:.1f}s) - "
                f"consider optimization or caching"
            )
        
        # Check performance violations
        if stats["performance_threshold_violations"] > 0:
            recommendations.append(
                f"{stats['performance_threshold_violations']} operations exceeded timeout threshold - "
                f"review timeout settings or operation efficiency"
            )
        
        # General recommendations
        if stats["total_operations"] > 100:
            recommendations.append("Consider implementing caching for frequently repeated operations")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges")
        
        return recommendations
    
    def optimize_settings(self, agent_type: str) -> Dict[str, Any]:
        """
        Optimize settings based on performance history.
        
        Args:
            agent_type: Type of agent to optimize for
            
        Returns:
            Dict containing optimized settings
        """
        stats = self.get_performance_stats(agent_type)
        optimized_settings = self.optimization_settings.copy()
        
        if stats["total_operations"] > 0:
            # Adjust timeout based on actual performance
            avg_time = stats["average_execution_time"]
            max_time = stats["max_execution_time"]
            
            # Set timeout to 2x the maximum observed time, with reasonable bounds
            suggested_timeout = max(60, min(600, max_time * 2))
            optimized_settings["timeout_seconds"] = suggested_timeout
            
            # Adjust retry attempts based on success rate
            if stats["success_rate"] < 80:
                optimized_settings["max_retry_attempts"] = 5
            elif stats["success_rate"] > 95:
                optimized_settings["max_retry_attempts"] = 2
        
        return optimized_settings
    
    def clear_history(self):
        """Clear performance history."""
        self.performance_history.clear()
        logger.info("Performance history cleared")
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export performance metrics.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            str: Exported metrics data
        """
        if format.lower() == "json":
            import json
            metrics_data = [
                {
                    "agent_type": m.agent_type,
                    "operation": m.operation,
                    "execution_time": m.execution_time,
                    "success": m.success,
                    "timestamp": m.timestamp,
                    "error_message": m.error_message
                }
                for m in self.performance_history
            ]
            return json.dumps(metrics_data, indent=2)
        
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Agent Type", "Operation", "Execution Time", 
                "Success", "Timestamp", "Error Message"
            ])
            
            # Write data
            for m in self.performance_history:
                writer.writerow([
                    m.agent_type, m.operation, m.execution_time,
                    m.success, m.timestamp, m.error_message or ""
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global performance optimizer instance
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def record_agent_performance(agent_type: str, operation: str, 
                           execution_time: float, success: bool = True,
                           error_message: Optional[str] = None,
                           **kwargs) -> bool:
    """
    Record agent performance metrics.
    
    Args:
        agent_type: Type of agent
        operation: Operation name
        execution_time: Execution time in seconds
        success: Whether operation was successful
        error_message: Error message if failed
        **kwargs: Additional metrics
        
    Returns:
        bool: True if recording was successful
    """
    optimizer = get_performance_optimizer()
    return optimizer.record_performance(
        agent_type, operation, execution_time, success, error_message, kwargs
    )

def get_agent_performance_stats(agent_type: str) -> Dict[str, Any]:
    """
    Get performance statistics for an agent type.
    
    Args:
        agent_type: Type of agent
        
    Returns:
        Dict containing performance statistics
    """
    optimizer = get_performance_optimizer()
    return optimizer.get_performance_stats(agent_type)

def get_performance_recommendations(agent_type: str) -> List[str]:
    """
    Get optimization recommendations for an agent type.
    
    Args:
        agent_type: Type of agent
        
    Returns:
        List of recommendations
    """
    optimizer = get_performance_optimizer()
    return optimizer.get_optimization_recommendations(agent_type)
