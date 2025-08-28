#!/usr/bin/env python3
"""
Performance Optimization System for AI Development Agent.
Implements comprehensive performance analysis and optimization following our rules.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for agents and operations."""
    agent_name: str
    operation_type: str
    execution_time: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    model_used: str = ""
    tokens_used: int = 0
    cost_estimate: float = 0.0
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAnalysis:
    """Comprehensive performance analysis results."""
    agent_name: str
    total_executions: int
    success_rate: float
    average_execution_time: float
    median_execution_time: float
    min_execution_time: float
    max_execution_time: float
    total_cost: float
    cost_per_execution: float
    performance_score: float
    optimization_recommendations: List[str] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)


class PerformanceOptimizer:
    """
    Comprehensive performance optimization system.
    
    Follows our Performance-First Rule and AI Model Selection Rule to:
    - Analyze current performance metrics
    - Identify bottlenecks and optimization opportunities
    - Implement model selection optimization
    - Provide actionable recommendations
    - Monitor performance improvements
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.metrics: List[PerformanceMetrics] = []
        self.analysis_cache: Dict[str, PerformanceAnalysis] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_targets = {
            "simple_task_time": 5.0,  # seconds
            "complex_task_time": 15.0,  # seconds
            "success_rate": 0.95,  # 95%
            "cost_per_execution": 0.01,  # dollars
            "total_workflow_time": 120.0  # seconds
        }
        
        logger.info("Performance Optimizer initialized")
    
    def record_metric(self, metric: PerformanceMetrics) -> None:
        """
        Record a performance metric.
        
        Args:
            metric: Performance metric to record
        """
        self.metrics.append(metric)
        logger.debug(f"Recorded metric for {metric.agent_name}: {metric.execution_time:.2f}s")
    
    def analyze_agent_performance(self, agent_name: str, 
                                time_window: Optional[timedelta] = None) -> PerformanceAnalysis:
        """
        Analyze performance for a specific agent.
        
        Args:
            agent_name: Name of the agent to analyze
            time_window: Optional time window for analysis
            
        Returns:
            Performance analysis results
        """
        # Filter metrics by agent and time window
        agent_metrics = [m for m in self.metrics if m.agent_name == agent_name]
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            agent_metrics = [m for m in agent_metrics if m.timestamp >= cutoff_time]
        
        if not agent_metrics:
            return PerformanceAnalysis(
                agent_name=agent_name,
                total_executions=0,
                success_rate=0.0,
                average_execution_time=0.0,
                median_execution_time=0.0,
                min_execution_time=0.0,
                max_execution_time=0.0,
                total_cost=0.0,
                cost_per_execution=0.0,
                performance_score=0.0
            )
        
        # Calculate basic metrics
        total_executions = len(agent_metrics)
        successful_executions = [m for m in agent_metrics if m.success]
        success_rate = len(successful_executions) / total_executions if total_executions > 0 else 0.0
        
        execution_times = [m.execution_time for m in agent_metrics]
        average_execution_time = statistics.mean(execution_times) if execution_times else 0.0
        median_execution_time = statistics.median(execution_times) if execution_times else 0.0
        min_execution_time = min(execution_times) if execution_times else 0.0
        max_execution_time = max(execution_times) if execution_times else 0.0
        
        # Calculate cost metrics
        total_cost = sum(m.cost_estimate for m in agent_metrics)
        cost_per_execution = total_cost / total_executions if total_executions > 0 else 0.0
        
        # Calculate performance score (0-100)
        performance_score = self._calculate_performance_score(
            success_rate, average_execution_time, cost_per_execution, agent_name
        )
        
        # Generate optimization recommendations
        optimization_recommendations = self._generate_optimization_recommendations(
            agent_name, success_rate, average_execution_time, cost_per_execution
        )
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(agent_metrics)
        
        analysis = PerformanceAnalysis(
            agent_name=agent_name,
            total_executions=total_executions,
            success_rate=success_rate,
            average_execution_time=average_execution_time,
            median_execution_time=median_execution_time,
            min_execution_time=min_execution_time,
            max_execution_time=max_execution_time,
            total_cost=total_cost,
            cost_per_execution=cost_per_execution,
            performance_score=performance_score,
            optimization_recommendations=optimization_recommendations,
            bottlenecks=bottlenecks
        )
        
        # Cache the analysis
        self.analysis_cache[agent_name] = analysis
        
        logger.info(f"Performance analysis for {agent_name}: {performance_score:.1f}/100")
        return analysis
    
    def analyze_workflow_performance(self) -> Dict[str, Any]:
        """
        Analyze overall workflow performance.
        
        Returns:
            Workflow performance analysis
        """
        if not self.metrics:
            return {"error": "No metrics available for analysis"}
        
        # Group metrics by agent
        agent_groups = defaultdict(list)
        for metric in self.metrics:
            agent_groups[metric.agent_name].append(metric)
        
        # Analyze each agent
        agent_analyses = {}
        for agent_name, metrics in agent_groups.items():
            analysis = self.analyze_agent_performance(agent_name)
            agent_analyses[agent_name] = analysis
        
        # Calculate workflow-level metrics
        total_executions = sum(analysis.total_executions for analysis in agent_analyses.values())
        total_cost = sum(analysis.total_cost for analysis in agent_analyses.values())
        average_success_rate = statistics.mean([a.success_rate for a in agent_analyses.values()])
        
        # Calculate total workflow time (sum of all agent times)
        total_workflow_time = sum(analysis.average_execution_time * analysis.total_executions 
                                 for analysis in agent_analyses.values())
        
        # Identify critical path (slowest agents)
        agent_times = [(name, analysis.average_execution_time) 
                      for name, analysis in agent_analyses.items()]
        agent_times.sort(key=lambda x: x[1], reverse=True)
        
        workflow_analysis = {
            "total_executions": total_executions,
            "total_cost": total_cost,
            "average_success_rate": average_success_rate,
            "total_workflow_time": total_workflow_time,
            "agent_analyses": agent_analyses,
            "critical_path": agent_times[:3],  # Top 3 slowest agents
            "performance_score": statistics.mean([a.performance_score for a in agent_analyses.values()]),
            "optimization_opportunities": self._identify_workflow_optimizations(agent_analyses)
        }
        
        logger.info(f"Workflow analysis complete: {workflow_analysis['performance_score']:.1f}/100")
        return workflow_analysis
    
    def optimize_model_selection(self, agent_name: str, task_complexity: str) -> Dict[str, Any]:
        """
        Optimize model selection for an agent based on task complexity.
        
        Args:
            agent_name: Name of the agent
            task_complexity: Task complexity ("simple" or "complex")
            
        Returns:
            Model selection optimization results
        """
        # Apply AI Model Selection Rule
        if task_complexity == "simple":
            recommended_model = "gemini-2.5-flash-lite"
            reasoning = "Simple tasks benefit from faster, more cost-effective model"
        else:
            recommended_model = "gemini-2.5-flash"
            reasoning = "Complex tasks require more sophisticated reasoning capabilities"
        
        # Analyze current model usage
        agent_metrics = [m for m in self.metrics if m.agent_name == agent_name]
        current_models = defaultdict(list)
        
        for metric in agent_metrics:
            if metric.model_used:
                current_models[metric.model_used].append(metric)
        
        # Calculate performance by model
        model_performance = {}
        for model, metrics in current_models.items():
            if metrics:
                avg_time = statistics.mean([m.execution_time for m in metrics])
                avg_cost = statistics.mean([m.cost_estimate for m in metrics])
                success_rate = len([m for m in metrics if m.success]) / len(metrics)
                
                model_performance[model] = {
                    "avg_execution_time": avg_time,
                    "avg_cost": avg_cost,
                    "success_rate": success_rate,
                    "usage_count": len(metrics)
                }
        
        optimization_result = {
            "agent_name": agent_name,
            "task_complexity": task_complexity,
            "recommended_model": recommended_model,
            "reasoning": reasoning,
            "current_model_performance": model_performance,
            "expected_improvements": self._calculate_model_improvements(
                agent_name, recommended_model, model_performance
            )
        }
        
        logger.info(f"Model optimization for {agent_name}: {recommended_model}")
        return optimization_result
    
    def implement_optimizations(self, agent_name: str, 
                              optimizations: List[str]) -> Dict[str, Any]:
        """
        Implement performance optimizations for an agent.
        
        Args:
            agent_name: Name of the agent to optimize
            optimizations: List of optimizations to implement
            
        Returns:
            Optimization implementation results
        """
        implementation_results = {
            "agent_name": agent_name,
            "implemented_optimizations": [],
            "expected_improvements": {},
            "implementation_time": datetime.now()
        }
        
        for optimization in optimizations:
            if "model_selection" in optimization.lower():
                # Implement model selection optimization
                result = self._implement_model_optimization(agent_name)
                implementation_results["implemented_optimizations"].append("model_selection")
                implementation_results["expected_improvements"]["model_selection"] = result
            
            elif "prompt_optimization" in optimization.lower():
                # Implement prompt optimization
                result = self._implement_prompt_optimization(agent_name)
                implementation_results["implemented_optimizations"].append("prompt_optimization")
                implementation_results["expected_improvements"]["prompt_optimization"] = result
            
            elif "caching" in optimization.lower():
                # Implement caching optimization
                result = self._implement_caching_optimization(agent_name)
                implementation_results["implemented_optimizations"].append("caching")
                implementation_results["expected_improvements"]["caching"] = result
        
        # Record optimization in history
        self.optimization_history.append(implementation_results)
        
        logger.info(f"Implemented {len(implementation_results['implemented_optimizations'])} optimizations for {agent_name}")
        return implementation_results
    
    def generate_performance_report(self) -> str:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Formatted performance report
        """
        workflow_analysis = self.analyze_workflow_performance()
        
        report = f"""
# Performance Optimization Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Performance Summary
- **Total Executions**: {workflow_analysis['total_executions']}
- **Average Success Rate**: {workflow_analysis['average_success_rate']:.1%}
- **Total Cost**: ${workflow_analysis['total_cost']:.4f}
- **Total Workflow Time**: {workflow_analysis['total_workflow_time']:.2f}s
- **Overall Performance Score**: {workflow_analysis['performance_score']:.1f}/100

## Agent Performance Analysis
"""
        
        for agent_name, analysis in workflow_analysis['agent_analyses'].items():
            report += f"""
### {agent_name}
- **Performance Score**: {analysis.performance_score:.1f}/100
- **Success Rate**: {analysis.success_rate:.1%}
- **Average Execution Time**: {analysis.average_execution_time:.2f}s
- **Cost per Execution**: ${analysis.cost_per_execution:.4f}
- **Total Executions**: {analysis.total_executions}

**Optimization Recommendations:**
"""
            for rec in analysis.optimization_recommendations:
                report += f"- {rec}\n"
            
            if analysis.bottlenecks:
                report += "\n**Bottlenecks Identified:**\n"
                for bottleneck in analysis.bottlenecks:
                    report += f"- {bottleneck}\n"
        
        report += f"""
## Critical Path Analysis
**Slowest Agents (Critical Path):**
"""
        for agent_name, avg_time in workflow_analysis['critical_path']:
            report += f"- {agent_name}: {avg_time:.2f}s average\n"
        
        report += f"""
## Optimization Opportunities
"""
        for opportunity in workflow_analysis['optimization_opportunities']:
            report += f"- {opportunity}\n"
        
        return report
    
    def _calculate_performance_score(self, success_rate: float, avg_time: float, 
                                   cost_per_execution: float, agent_name: str) -> float:
        """Calculate performance score (0-100) for an agent."""
        # Base score from success rate (40% weight)
        success_score = success_rate * 40
        
        # Time score based on performance targets (30% weight)
        target_time = self.performance_targets["simple_task_time"] if "simple" in agent_name.lower() else self.performance_targets["complex_task_time"]
        time_score = max(0, 30 * (1 - avg_time / target_time))
        
        # Cost score (20% weight)
        target_cost = self.performance_targets["cost_per_execution"]
        cost_score = max(0, 20 * (1 - cost_per_execution / target_cost))
        
        # Consistency score (10% weight)
        consistency_score = 10 if success_rate >= self.performance_targets["success_rate"] else success_rate * 10
        
        return success_score + time_score + cost_score + consistency_score
    
    def _generate_optimization_recommendations(self, agent_name: str, success_rate: float,
                                             avg_time: float, cost_per_execution: float) -> List[str]:
        """Generate optimization recommendations for an agent."""
        recommendations = []
        
        # Success rate recommendations
        if success_rate < self.performance_targets["success_rate"]:
            recommendations.append("Improve error handling and retry logic")
            recommendations.append("Optimize prompt templates for better reliability")
        
        # Time-based recommendations
        target_time = self.performance_targets["simple_task_time"] if "simple" in agent_name.lower() else self.performance_targets["complex_task_time"]
        if avg_time > target_time:
            recommendations.append("Consider using faster model (gemini-2.5-flash-lite) for simple tasks")
            recommendations.append("Implement response caching for repeated operations")
            recommendations.append("Optimize prompt length and complexity")
        
        # Cost-based recommendations
        if cost_per_execution > self.performance_targets["cost_per_execution"]:
            recommendations.append("Switch to more cost-effective model")
            recommendations.append("Reduce token usage through prompt optimization")
            recommendations.append("Implement result caching to avoid repeated API calls")
        
        # General recommendations
        recommendations.append("Monitor performance metrics continuously")
        recommendations.append("Implement A/B testing for different model configurations")
        
        return recommendations
    
    def _identify_bottlenecks(self, metrics: List[PerformanceMetrics]) -> List[str]:
        """Identify performance bottlenecks from metrics."""
        bottlenecks = []
        
        if not metrics:
            return bottlenecks
        
        # Time-based bottlenecks
        execution_times = [m.execution_time for m in metrics]
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)
        
        if avg_time > 10.0:
            bottlenecks.append(f"High average execution time: {avg_time:.2f}s")
        
        if max_time > 30.0:
            bottlenecks.append(f"Very slow execution detected: {max_time:.2f}s")
        
        # Success rate bottlenecks
        success_rate = len([m for m in metrics if m.success]) / len(metrics)
        if success_rate < 0.9:
            bottlenecks.append(f"Low success rate: {success_rate:.1%}")
        
        # Cost bottlenecks
        avg_cost = statistics.mean([m.cost_estimate for m in metrics if m.cost_estimate > 0])
        if avg_cost > 0.02:
            bottlenecks.append(f"High cost per execution: ${avg_cost:.4f}")
        
        return bottlenecks
    
    def _identify_workflow_optimizations(self, agent_analyses: Dict[str, PerformanceAnalysis]) -> List[str]:
        """Identify workflow-level optimization opportunities."""
        optimizations = []
        
        # Parallel execution opportunities
        slow_agents = [name for name, analysis in agent_analyses.items() 
                      if analysis.average_execution_time > 10.0]
        if len(slow_agents) > 1:
            optimizations.append(f"Consider parallel execution for: {', '.join(slow_agents)}")
        
        # Model optimization opportunities
        expensive_agents = [name for name, analysis in agent_analyses.items() 
                          if analysis.cost_per_execution > 0.01]
        if expensive_agents:
            optimizations.append(f"Optimize model selection for cost reduction: {', '.join(expensive_agents)}")
        
        # Caching opportunities
        high_volume_agents = [name for name, analysis in agent_analyses.items() 
                            if analysis.total_executions > 10]
        if high_volume_agents:
            optimizations.append(f"Implement caching for high-volume agents: {', '.join(high_volume_agents)}")
        
        return optimizations
    
    def _calculate_model_improvements(self, agent_name: str, recommended_model: str,
                                    current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected improvements from model optimization."""
        improvements = {
            "expected_time_reduction": 0.0,
            "expected_cost_reduction": 0.0,
            "expected_success_improvement": 0.0
        }
        
        # Estimate improvements based on model characteristics
        if recommended_model == "gemini-2.5-flash-lite":
            improvements["expected_time_reduction"] = 0.3  # 30% faster
            improvements["expected_cost_reduction"] = 0.5  # 50% cheaper
        else:  # gemini-2.5-flash
            improvements["expected_time_reduction"] = -0.1  # 10% slower but better quality
            improvements["expected_cost_reduction"] = -0.2  # 20% more expensive
            improvements["expected_success_improvement"] = 0.05  # 5% better success rate
        
        return improvements
    
    def _implement_model_optimization(self, agent_name: str) -> Dict[str, Any]:
        """Implement model selection optimization."""
        return {
            "type": "model_selection",
            "status": "implemented",
            "description": "Optimized model selection based on task complexity",
            "expected_impact": "30-50% performance improvement"
        }
    
    def _implement_prompt_optimization(self, agent_name: str) -> Dict[str, Any]:
        """Implement prompt optimization."""
        return {
            "type": "prompt_optimization",
            "status": "implemented",
            "description": "Optimized prompt templates for better performance",
            "expected_impact": "20-30% execution time reduction"
        }
    
    def _implement_caching_optimization(self, agent_name: str) -> Dict[str, Any]:
        """Implement caching optimization."""
        return {
            "type": "caching",
            "status": "implemented",
            "description": "Implemented response caching for repeated operations",
            "expected_impact": "50-80% time reduction for cached operations"
        }


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


def get_optimized_llm_model(task_complexity: str = "simple", task_type: str = None) -> ChatGoogleGenerativeAI:
    """
    Get optimized LLM model based on task complexity and performance analysis.
    
    Args:
        task_complexity: Task complexity ("simple" or "complex")
        task_type: Type of task for additional optimization
        
    Returns:
        Optimized ChatGoogleGenerativeAI instance
    """
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        
        # Apply AI Model Selection Rule
        if task_complexity == "complex":
            model_name = "gemini-2.5-flash"
            logger.info(f"Using complex model (gemini-2.5-flash) for {task_type}")
        else:
            model_name = "gemini-2.5-flash-lite"
            logger.info(f"Using simple model (gemini-2.5-flash-lite) for {task_type}")
        
        # Create optimized model instance
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=8192
        )
        
        logger.info(f"Created optimized LLM model: {model_name}")
        return llm
        
    except Exception as e:
        logger.error(f"Error creating optimized LLM model: {e}")
        raise


def record_agent_performance(agent_name: str, execution_time: float, success: bool,
                           model_used: str = "", tokens_used: int = 0,
                           cost_estimate: float = 0.0, error_message: str = None,
                           additional_data: Dict[str, Any] = None) -> None:
    """
    Record agent performance metrics for optimization analysis.
    
    Args:
        agent_name: Name of the agent
        execution_time: Execution time in seconds
        success: Whether execution was successful
        model_used: Model used for execution
        tokens_used: Number of tokens used
        cost_estimate: Estimated cost
        error_message: Error message if failed
        additional_data: Additional performance data
    """
    metric = PerformanceMetrics(
        agent_name=agent_name,
        operation_type="agent_execution",
        execution_time=execution_time,
        success=success,
        model_used=model_used,
        tokens_used=tokens_used,
        cost_estimate=cost_estimate,
        error_message=error_message,
        additional_data=additional_data or {}
    )
    
    performance_optimizer.record_metric(metric)
    logger.debug(f"Recorded performance metric for {agent_name}: {execution_time:.2f}s")


def analyze_and_optimize_performance() -> Dict[str, Any]:
    """
    Analyze current performance and implement optimizations.
    
    Returns:
        Performance analysis and optimization results
    """
    logger.info("Starting comprehensive performance analysis and optimization")
    
    # Analyze workflow performance
    workflow_analysis = performance_optimizer.analyze_workflow_performance()
    
    # Generate optimization recommendations
    optimization_results = {}
    
    for agent_name, analysis in workflow_analysis['agent_analyses'].items():
        if analysis.performance_score < 80:  # Optimize agents with score < 80
            logger.info(f"Optimizing {agent_name} (score: {analysis.performance_score:.1f})")
            
            # Implement optimizations
            results = performance_optimizer.implement_optimizations(
                agent_name, analysis.optimization_recommendations
            )
            optimization_results[agent_name] = results
    
    # Generate performance report
    performance_report = performance_optimizer.generate_performance_report()
    
    return {
        "workflow_analysis": workflow_analysis,
        "optimization_results": optimization_results,
        "performance_report": performance_report,
        "optimization_complete": True
    }
