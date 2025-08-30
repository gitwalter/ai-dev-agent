"""
Prompt Management System
========================

Comprehensive prompt management system for AI agents, including:
- Prompt database management
- Template system with version control
- Performance optimization framework
- A/B testing capabilities
- Dynamic loading and caching

This module provides the core prompt engineering capabilities for US-PE-01.

Author: AI-Dev-Agent System
Version: 2.0
Last Updated: Current Session
"""

from .prompt_manager import PromptManager, get_prompt_manager
from .prompt_template_system import (
    PromptTemplateSystem, 
    PromptTemplate, 
    TemplateType, 
    TemplateStatus,
    get_template_system
)
from .prompt_optimizer import (
    PromptOptimizer,
    OptimizationStrategy,
    OptimizationResult,
    PerformanceMetrics,
    get_prompt_optimizer
)
from .prompt_ab_testing import (
    PromptABTesting,
    ABTest,
    TestResult,
    StatisticalResult,
    TestStatus,
    TestType,
    get_ab_testing
)

# Analytics and web interface components
from .prompt_analytics import (
    PromptAnalytics, 
    PerformanceMetrics as AnalyticsPerformanceMetrics,
    CostMetrics, 
    QualityMetrics, 
    OptimizationRecommendation, 
    TrendAnalysis,
    MetricType, 
    TrendDirection
)
from .prompt_web_interface import PromptWebInterface

# Legacy imports for backward compatibility
# from .agent_prompt_loader import AgentPromptLoader  # File doesn't exist yet

__all__ = [
    # Core prompt management
    'PromptManager',
    'get_prompt_manager',
    
    # Template system
    'PromptTemplateSystem',
    'PromptTemplate',
    'TemplateType',
    'TemplateStatus',
    'get_template_system',
    
    # Optimization framework
    'PromptOptimizer',
    'OptimizationStrategy',
    'OptimizationResult',
    'PerformanceMetrics',
    'get_prompt_optimizer',
    
    # A/B testing framework
    'PromptABTesting',
    'ABTest',
    'TestResult',
    'StatisticalResult',
    'TestStatus',
    'TestType',
    'get_ab_testing',
    
    # Analytics components
    'PromptAnalytics',
    'AnalyticsPerformanceMetrics',
    'CostMetrics',
    'QualityMetrics',
    'OptimizationRecommendation',
    'TrendAnalysis',
    'MetricType',
    'TrendDirection',
    
    # Web interface components
    'PromptWebInterface',
    
    # Legacy components
    # 'AgentPromptLoader'  # File doesn't exist yet
]


class PromptEngineeringSystem:
    """
    Unified prompt engineering system that integrates all components.
    
    This class provides a high-level interface to all prompt engineering
    capabilities for US-PE-01.
    """
    
    def __init__(self):
        """Initialize the unified prompt engineering system."""
        self.prompt_manager = get_prompt_manager()
        self.template_system = get_template_system()
        self.optimizer = get_prompt_optimizer()
        self.ab_testing = get_ab_testing()
    
    def create_optimized_template(self, name: str, description: str, 
                                agent_type: str, template_text: str,
                                author: str, optimization_strategy: OptimizationStrategy = None,
                                tags: list = None) -> str:
        """
        Create an optimized prompt template.
        
        Args:
            name: Template name
            description: Template description
            agent_type: Target agent type
            template_text: Template content
            author: Template author
            optimization_strategy: Optional optimization strategy
            tags: Template tags
            
        Returns:
            str: Template ID
        """
        # Create template
        template_id = self.template_system.create_template(
            name=name,
            description=description,
            template_type=TemplateType.ENHANCED,
            agent_type=agent_type,
            template_text=template_text,
            author=author,
            tags=tags
        )
        
        # Optimize if strategy provided
        if optimization_strategy:
            result = self.optimizer.optimize_prompt(
                template_text, 
                optimization_strategy
            )
            
            # Update template with optimized version
            self.template_system.update_template(template_id, {
                'template_text': result.optimized_prompt,
                'status': TemplateStatus.ACTIVE
            })
            
            # Store optimization metadata
            self.template_system.update_template(template_id, {
                'metadata': {
                    'optimization_applied': True,
                    'optimization_strategy': optimization_strategy.value,
                    'improvement_score': result.improvement_score,
                    'token_reduction': result.token_reduction
                }
            })
        
        return template_id
    
    def create_ab_test(self, name: str, description: str, agent_type: str,
                      variant_a_text: str, variant_b_text: str,
                      test_type: TestType = TestType.PROMPT_VARIATION) -> str:
        """
        Create an A/B test for prompt variants.
        
        Args:
            name: Test name
            description: Test description
            agent_type: Target agent type
            variant_a_text: Variant A prompt text
            variant_b_text: Variant B prompt text
            test_type: Type of test
            
        Returns:
            str: Test ID
        """
        variant_a = {
            'prompt_text': variant_a_text,
            'agent_type': agent_type,
            'variant_type': 'A'
        }
        
        variant_b = {
            'prompt_text': variant_b_text,
            'agent_type': agent_type,
            'variant_type': 'B'
        }
        
        return self.ab_testing.create_test(
            name=name,
            description=description,
            test_type=test_type,
            variant_a=variant_a,
            variant_b=variant_b
        )
    
    def get_optimization_recommendations(self, prompt_text: str) -> list:
        """
        Get optimization recommendations for a prompt.
        
        Args:
            prompt_text: Prompt text to analyze
            
        Returns:
            list: Optimization recommendations
        """
        return self.optimizer.get_optimization_recommendations(prompt_text)
    
    def render_template_with_context(self, template_id: str, context: dict) -> str:
        """
        Render a template with context.
        
        Args:
            template_id: Template ID
            context: Context variables
            
        Returns:
            str: Rendered prompt
        """
        return self.template_system.render_template(template_id, context)
    
    def record_prompt_performance(self, prompt_id: str, execution_time: float,
                                token_count: int, response_quality: float,
                                success: bool, metadata: dict = None):
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
        self.optimizer.record_performance(
            prompt_id=prompt_id,
            execution_time=execution_time,
            token_count=token_count,
            response_quality=response_quality,
            success=success,
            metadata=metadata
        )
    
    def get_system_status(self) -> dict:
        """
        Get overall system status.
        
        Returns:
            dict: System status information
        """
        return {
            'prompt_manager': {
                'total_prompts': len(self.prompt_manager.get_all_prompts()),
                'database_status': 'active'
            },
            'template_system': {
                'total_templates': len(self.template_system.templates),
                'active_templates': len([
                    t for t in self.template_system.templates.values()
                    if t.status == TemplateStatus.ACTIVE
                ])
            },
            'optimizer': {
                'optimization_history': len(self.optimizer.optimization_history),
                'performance_metrics': len(self.optimizer.performance_metrics)
            },
            'ab_testing': {
                'total_tests': len(self.ab_testing.tests),
                'active_tests': len(self.ab_testing.get_active_tests()),
                'total_results': len(self.ab_testing.results)
            }
        }


# Global unified system instance
_unified_system = None

def get_prompt_engineering_system() -> PromptEngineeringSystem:
    """Get the global unified prompt engineering system instance."""
    global _unified_system
    if _unified_system is None:
        _unified_system = PromptEngineeringSystem()
    return _unified_system
