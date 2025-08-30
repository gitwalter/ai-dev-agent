#!/usr/bin/env python3
"""
Rule Performance Analytics Engine

Advanced analytics system for tracking and optimizing rule application performance.
Provides real-time monitoring, optimization recommendations, and effectiveness tracking.
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import statistics

@dataclass
class RulePerformanceMetrics:
    """Metrics for tracking rule application performance."""
    rule_name: str
    execution_time: float
    success_rate: float
    efficiency_score: float
    quality_impact: float
    context_appropriateness: float
    timestamp: str
    task_context: Dict[str, Any]

@dataclass  
class RuleEffectivenessReport:
    """Comprehensive report on rule effectiveness."""
    total_applications: int
    average_execution_time: float
    success_rate: float
    quality_improvement: float
    efficiency_gain: float
    recommendations: List[str]
    optimization_opportunities: List[str]

class RulePerformanceAnalytics:
    """
    Advanced analytics engine for tracking and optimizing rule performance.
    
    This system provides real-time monitoring of rule application effectiveness,
    identifies optimization opportunities, and generates actionable insights
    for continuous improvement of the rule system.
    """
    
    def __init__(self, analytics_file: Path = None):
        self.analytics_file = analytics_file or Path('monitoring/rule_performance_analytics.json')
        self.analytics_file.parent.mkdir(parents=True, exist_ok=True)
        self.performance_history = self._load_performance_history()
        self.current_session_metrics = []
        
    def record_rule_application(self, 
                              rule_name: str,
                              execution_time: float,
                              success: bool,
                              task_context: Dict[str, Any],
                              quality_metrics: Dict[str, float] = None) -> None:
        """
        Record metrics for a rule application.
        
        Args:
            rule_name: Name of the rule applied
            execution_time: Time taken to apply the rule
            success: Whether the rule application was successful
            task_context: Context in which the rule was applied
            quality_metrics: Optional quality impact metrics
        """
        metrics = RulePerformanceMetrics(
            rule_name=rule_name,
            execution_time=execution_time,
            success_rate=1.0 if success else 0.0,
            efficiency_score=self._calculate_efficiency_score(execution_time, success),
            quality_impact=quality_metrics.get('quality_impact', 0.0) if quality_metrics else 0.0,
            context_appropriateness=self._assess_context_appropriateness(rule_name, task_context),
            timestamp=datetime.now().isoformat(),
            task_context=task_context
        )
        
        self.current_session_metrics.append(metrics)
        self.performance_history.append(asdict(metrics))
        self._save_performance_history()
        
    def generate_effectiveness_report(self, rule_name: str = None) -> RuleEffectivenessReport:
        """
        Generate comprehensive effectiveness report for a rule or all rules.
        
        Args:
            rule_name: Optional specific rule name, if None analyzes all rules
            
        Returns:
            Comprehensive effectiveness report
        """
        if rule_name:
            metrics = [m for m in self.performance_history if m['rule_name'] == rule_name]
        else:
            metrics = self.performance_history
            
        if not metrics:
            return RuleEffectivenessReport(
                total_applications=0,
                average_execution_time=0.0,
                success_rate=0.0,
                quality_improvement=0.0,
                efficiency_gain=0.0,
                recommendations=["No data available for analysis"],
                optimization_opportunities=[]
            )
        
        # Calculate aggregate metrics
        total_apps = len(metrics)
        avg_time = statistics.mean(m['execution_time'] for m in metrics)
        success_rate = statistics.mean(m['success_rate'] for m in metrics)
        avg_quality = statistics.mean(m['quality_impact'] for m in metrics)
        avg_efficiency = statistics.mean(m['efficiency_score'] for m in metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics)
        optimizations = self._identify_optimization_opportunities(metrics)
        
        return RuleEffectivenessReport(
            total_applications=total_apps,
            average_execution_time=avg_time,
            success_rate=success_rate,
            quality_improvement=avg_quality,
            efficiency_gain=avg_efficiency,
            recommendations=recommendations,
            optimization_opportunities=optimizations
        )
    
    def get_top_performing_rules(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing rules based on composite score."""
        rule_scores = {}
        
        for metric in self.performance_history:
            rule_name = metric['rule_name']
            if rule_name not in rule_scores:
                rule_scores[rule_name] = []
            
            # Composite score: efficiency + quality + success - time_penalty
            time_penalty = min(metric['execution_time'] / 60.0, 1.0)  # Normalize to 0-1
            composite_score = (
                metric['efficiency_score'] * 0.3 +
                metric['quality_impact'] * 0.3 +
                metric['success_rate'] * 0.3 +
                metric['context_appropriateness'] * 0.1 -
                time_penalty * 0.1
            )
            rule_scores[rule_name].append(composite_score)
        
        # Calculate average scores
        avg_scores = {
            rule: statistics.mean(scores) 
            for rule, scores in rule_scores.items()
        }
        
        # Sort by score and return top performers
        top_rules = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'rule_name': rule,
                'performance_score': score,
                'applications': len(rule_scores[rule]),
                'avg_execution_time': statistics.mean(
                    m['execution_time'] for m in self.performance_history 
                    if m['rule_name'] == rule
                )
            }
            for rule, score in top_rules[:limit]
        ]
    
    def _calculate_efficiency_score(self, execution_time: float, success: bool) -> float:
        """Calculate efficiency score based on time and success."""
        if not success:
            return 0.0
        
        # Inverse relationship with time (faster = more efficient)
        # Scale to 0-1 range
        time_efficiency = max(0.0, 1.0 - (execution_time / 300.0))  # 5 minutes = 0 efficiency
        return min(1.0, time_efficiency)
    
    def _assess_context_appropriateness(self, rule_name: str, task_context: Dict[str, Any]) -> float:
        """Assess how appropriate the rule is for the given context."""
        # Simple heuristic based on rule-context matching
        context_keywords = set(str(v).lower() for v in task_context.values())
        
        rule_contexts = {
            'file_organization': ['file', 'move', 'organization', 'structure'],
            'documentation': ['doc', 'update', 'readme', 'changelog'],
            'clean_repository': ['clean', 'temp', 'artifact', 'cleanup'],
            'test_driven': ['test', 'validation', 'verification'],
            'boy_scout': ['improve', 'refactor', 'quality', 'cleanup']
        }
        
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        relevant_keywords = set(rule_contexts.get(rule_key, []))
        
        if not relevant_keywords:
            return 0.7  # Default appropriateness for unknown rules
        
        overlap = len(context_keywords & relevant_keywords)
        return min(1.0, overlap / len(relevant_keywords)) if relevant_keywords else 0.7
    
    def _generate_recommendations(self, metrics: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on performance metrics."""
        recommendations = []
        
        # Analyze execution times
        if metrics:
            avg_time = statistics.mean(m['execution_time'] for m in metrics)
            if avg_time > 60:  # More than 1 minute average
                recommendations.append("Consider rule sequence optimization to reduce execution time")
            
            # Analyze success rates
            success_rate = statistics.mean(m['success_rate'] for m in metrics)
            if success_rate < 0.9:
                recommendations.append("Improve rule application reliability through better validation")
            
            # Analyze context appropriateness
            context_score = statistics.mean(m['context_appropriateness'] for m in metrics)
            if context_score < 0.8:
                recommendations.append("Enhance rule selection logic for better context matching")
        
        return recommendations
    
    def _identify_optimization_opportunities(self, metrics: List[Dict[str, Any]]) -> List[str]:
        """Identify specific optimization opportunities."""
        opportunities = []
        
        # Group by rule and find slow rules
        rule_times = {}
        for metric in metrics:
            rule_name = metric['rule_name']
            if rule_name not in rule_times:
                rule_times[rule_name] = []
            rule_times[rule_name].append(metric['execution_time'])
        
        for rule, times in rule_times.items():
            avg_time = statistics.mean(times)
            if avg_time > 30:  # Rules taking more than 30 seconds
                opportunities.append(f"Optimize '{rule}' rule execution (avg: {avg_time:.1f}s)")
        
        return opportunities
    
    def _load_performance_history(self) -> List[Dict[str, Any]]:
        """Load performance history from file."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_performance_history(self) -> None:
        """Save performance history to file."""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.performance_history, f, indent=2)

    def generate_analytics_dashboard(self) -> str:
        """Generate a comprehensive analytics dashboard."""
        dashboard = []
        dashboard.append("📊 RULE PERFORMANCE ANALYTICS DASHBOARD")
        dashboard.append("=" * 50)
        dashboard.append("")
        
        # Overall statistics
        if self.performance_history:
            dashboard.append("🎯 **OVERALL PERFORMANCE**")
            total_apps = len(self.performance_history)
            avg_time = statistics.mean(m['execution_time'] for m in self.performance_history)
            avg_success = statistics.mean(m['success_rate'] for m in self.performance_history)
            dashboard.append(f"Total Rule Applications: {total_apps}")
            dashboard.append(f"Average Execution Time: {avg_time:.2f}s")
            dashboard.append(f"Overall Success Rate: {avg_success:.1%}")
            dashboard.append("")
            
            # Top performing rules
            top_rules = self.get_top_performing_rules(5)
            dashboard.append("🏆 **TOP PERFORMING RULES**")
            for i, rule in enumerate(top_rules, 1):
                dashboard.append(f"{i}. {rule['rule_name']} (Score: {rule['performance_score']:.3f})")
            dashboard.append("")
            
            # Recent trends
            recent_metrics = [m for m in self.performance_history 
                            if datetime.fromisoformat(m['timestamp']) > 
                            datetime.now() - timedelta(hours=24)]
            if recent_metrics:
                dashboard.append("📈 **24-HOUR TRENDS**")
                recent_avg_time = statistics.mean(m['execution_time'] for m in recent_metrics)
                recent_success = statistics.mean(m['success_rate'] for m in recent_metrics)
                dashboard.append(f"Recent Applications: {len(recent_metrics)}")
                dashboard.append(f"Recent Avg Time: {recent_avg_time:.2f}s")
                dashboard.append(f"Recent Success Rate: {recent_success:.1%}")
                dashboard.append("")
        
        # Recommendations
        all_recommendations = self._generate_recommendations(self.performance_history)
        if all_recommendations:
            dashboard.append("💡 **OPTIMIZATION RECOMMENDATIONS**")
            for rec in all_recommendations:
                dashboard.append(f"• {rec}")
            dashboard.append("")
        
        return "\n".join(dashboard)

def demo_analytics_system():
    """Demonstrate the analytics system functionality."""
    print("🚀 RULE PERFORMANCE ANALYTICS ENGINE")
    print("=" * 60)
    
    # Create analytics instance
    analytics = RulePerformanceAnalytics()
    
    # Record sample rule applications
    sample_contexts = [
        {'task_type': 'file_organization', 'files_count': 3, 'complexity': 'simple'},
        {'task_type': 'documentation_update', 'files_count': 5, 'complexity': 'medium'},
        {'task_type': 'code_implementation', 'files_count': 2, 'complexity': 'complex'}
    ]
    
    print("📊 Recording sample rule applications...")
    for i, context in enumerate(sample_contexts):
        analytics.record_rule_application(
            rule_name=f"File Organization Rule",
            execution_time=15.0 + i * 5,
            success=True,
            task_context=context,
            quality_metrics={'quality_impact': 0.8 + i * 0.05}
        )
    
    print("✅ Sample data recorded")
    print()
    print("📈 ANALYTICS DASHBOARD:")
    print(analytics.generate_analytics_dashboard())
    
    return analytics

if __name__ == "__main__":
    demo_analytics_system()
