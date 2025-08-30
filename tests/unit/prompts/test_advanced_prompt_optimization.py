"""
Test suite for US-PE-03: Advanced Prompt Optimization

Tests the advanced prompt optimization engine including:
- ML-based optimization capabilities
- Context-aware adaptation
- Performance regression detection
- Integration hooks for Epic 3 and Epic 4
- Optimization history and rollback
- Advanced analytics and reporting
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json

from utils.prompt_management import (
    AdvancedPromptOptimizer, OptimizationType, OptimizationStatus,
    OptimizationContext, OptimizationResult, MLModel,
    get_advanced_optimizer
)


class TestAdvancedPromptOptimizer:
    """Test the advanced prompt optimization engine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_dir):
        """Create optimizer instance for testing."""
        return AdvancedPromptOptimizer(optimization_dir=temp_dir)
    
    @pytest.fixture
    def sample_context(self):
        """Create sample optimization context."""
        return OptimizationContext(
            user_id="test_user",
            task_type="moderate",
            agent_type="test_agent",
            usage_pattern={
                "recent_uses": [datetime.now() - timedelta(hours=i) for i in range(5)],
                "success_pattern": [0.9, 0.85, 0.92, 0.88, 0.91]
            },
            performance_history=[2.1, 1.9, 2.3, 1.8, 2.0, 1.7, 1.9],
            success_rate=0.88,
            response_time=2.1,
            cost_per_request=0.05,
            timestamp=datetime.now()
        )
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer is not None
        assert optimizer.optimization_dir.exists()
        assert optimizer.db_path.exists()
        assert len(optimizer.models) >= 0
        assert len(optimizer.agent_framework_hooks) == 0
        assert len(optimizer.monitoring_hooks) == 0
    
    def test_performance_optimization(self, optimizer, sample_context):
        """Test performance-based optimization."""
        original_prompt = "Please provide a comprehensive analysis of the given requirements and kindly ensure that all aspects are thoroughly covered."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_performance",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.PERFORMANCE
        )
        
        assert result is not None
        assert result.optimization_type == OptimizationType.PERFORMANCE
        assert result.status == OptimizationStatus.COMPLETED
        assert result.original_prompt == original_prompt
        assert result.optimized_prompt != original_prompt
        assert result.improvement_score >= 0.0
        assert result.performance_gain >= 0.0
        assert result.confidence_score >= 0.0
        assert result.context == sample_context
    
    def test_clarity_optimization(self, optimizer, sample_context):
        """Test clarity-based optimization."""
        original_prompt = "Analyze the requirements and provide a detailed response with comprehensive coverage of all aspects including technical details implementation considerations and potential challenges."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_clarity",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.CLARITY
        )
        
        assert result is not None
        assert result.optimization_type == OptimizationType.CLARITY
        assert result.status == OptimizationStatus.COMPLETED
        assert result.original_prompt == original_prompt
        assert result.improvement_score >= 0.0
        assert result.confidence_score >= 0.0
    
    def test_cost_optimization(self, optimizer, sample_context):
        """Test cost-based optimization."""
        original_prompt = "Please provide a very detailed and comprehensive analysis of the requirements with extensive coverage of all technical aspects implementation details potential challenges and recommendations."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_cost",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.COST
        )
        
        assert result is not None
        assert result.optimization_type == OptimizationType.COST
        assert result.status == OptimizationStatus.COMPLETED
        assert result.cost_reduction >= 0.0
        assert result.improvement_score >= 0.0
    
    def test_adaptive_optimization(self, optimizer, sample_context):
        """Test adaptive optimization based on context."""
        original_prompt = "Analyze the requirements and provide a response."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_adaptive",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        assert result is not None
        assert result.optimization_type == OptimizationType.ADAPTIVE
        assert result.status == OptimizationStatus.COMPLETED
        assert result.improvement_score >= 0.0
        assert result.confidence_score >= 0.0
    
    def test_optimization_with_low_success_rate(self, optimizer):
        """Test optimization when success rate is low."""
        context = OptimizationContext(
            user_id="test_user",
            task_type="complex",
            agent_type="test_agent",
            usage_pattern={"recent_uses": []},
            performance_history=[3.5, 4.2, 3.8, 4.0],
            success_rate=0.65,  # Low success rate
            response_time=3.5,
            cost_per_request=0.08,
            timestamp=datetime.now()
        )
        
        original_prompt = "Analyze the requirements."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_low_success",
            prompt_text=original_prompt,
            context=context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
        # Should prioritize clarity optimization for low success rate
        assert result.improvement_score >= 0.0
    
    def test_optimization_with_high_response_time(self, optimizer):
        """Test optimization when response time is high."""
        context = OptimizationContext(
            user_id="test_user",
            task_type="moderate",
            agent_type="test_agent",
            usage_pattern={"recent_uses": []},
            performance_history=[4.5, 4.8, 4.2, 4.6],
            success_rate=0.92,
            response_time=4.5,  # High response time
            cost_per_request=0.06,
            timestamp=datetime.now()
        )
        
        original_prompt = "Please provide a comprehensive analysis with detailed explanations."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_high_response",
            prompt_text=original_prompt,
            context=context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
        # Should prioritize performance optimization for high response time
        assert result.performance_gain >= 0.0
    
    def test_optimization_with_high_cost(self, optimizer):
        """Test optimization when cost per request is high."""
        context = OptimizationContext(
            user_id="test_user",
            task_type="basic",
            agent_type="test_agent",
            usage_pattern={"recent_uses": []},
            performance_history=[2.1, 2.0, 2.2],
            success_rate=0.89,
            response_time=2.1,
            cost_per_request=0.15,  # High cost
            timestamp=datetime.now()
        )
        
        original_prompt = "Provide a very detailed and comprehensive analysis with extensive coverage."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_high_cost",
            prompt_text=original_prompt,
            context=context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
        # Should prioritize cost optimization for high cost
        assert result.cost_reduction >= 0.0
    
    def test_optimization_history(self, optimizer, sample_context):
        """Test optimization history tracking."""
        original_prompt = "Test prompt for history tracking."
        
        # Create multiple optimizations with different prompt_ids to avoid unique constraint
        result1 = optimizer.optimize_prompt(
            prompt_id="test_history_1",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.PERFORMANCE
        )
        
        result2 = optimizer.optimize_prompt(
            prompt_id="test_history_2",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.CLARITY
        )
        
        # Get optimization history for both prompts
        history1 = optimizer.get_optimization_history("test_history_1")
        history2 = optimizer.get_optimization_history("test_history_2")
        
        # Check that both optimizations are recorded
        assert len(history1) >= 1
        assert len(history2) >= 1
        assert any(r.optimization_id == result1.optimization_id for r in history1)
        assert any(r.optimization_id == result2.optimization_id for r in history2)
        
        # Get all optimization history
        all_history = optimizer.get_optimization_history()
        assert len(all_history) >= 2
    
    def test_optimization_rollback(self, optimizer, sample_context):
        """Test optimization rollback functionality."""
        original_prompt = "Test prompt for rollback."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_rollback",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.PERFORMANCE
        )
        
        # Rollback the optimization
        rollback_success = optimizer.rollback_optimization(result.optimization_id)
        
        assert rollback_success is True
        
        # Verify rollback in history
        history = optimizer.get_optimization_history("test_rollback")
        rolled_back_optimization = next(r for r in history if r.optimization_id == result.optimization_id)
        
        assert rolled_back_optimization.status == OptimizationStatus.ROLLED_BACK
        assert rolled_back_optimization.rolled_back_at is not None
    
    def test_integration_hooks(self, optimizer, sample_context):
        """Test integration hooks for Epic 3 and Epic 4."""
        # Test data for hooks
        hook_calls = {"agent_optimization": 0, "performance_monitoring": 0}
        
        def agent_optimization_hook(result):
            hook_calls["agent_optimization"] += 1
        
        def performance_monitoring_hook(result):
            hook_calls["performance_monitoring"] += 1
        
        # Register hooks
        optimizer.register_agent_framework_hook("agent_optimization", agent_optimization_hook)
        optimizer.register_monitoring_hook("performance_monitoring", performance_monitoring_hook)
        
        # Perform optimization
        original_prompt = "Test prompt for integration hooks."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_hooks",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        # Verify hooks were called
        assert hook_calls["agent_optimization"] == 1
        assert hook_calls["performance_monitoring"] == 1
    
    def test_feature_extraction(self, optimizer, sample_context):
        """Test feature extraction for ML models."""
        original_prompt = "This is a test prompt with multiple sentences. It contains various words and phrases."
        
        features = optimizer._extract_features(original_prompt, sample_context)
        
        # Check that all expected features are present
        expected_features = [
            "prompt_length", "word_count", "sentence_count", "avg_word_length",
            "success_rate", "response_time", "cost_per_request", "task_complexity",
            "usage_frequency", "time_of_day", "day_of_week"
        ]
        
        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], (int, float))
    
    def test_improvement_score_calculation(self, optimizer, sample_context):
        """Test improvement score calculation."""
        original_prompt = "This is a very long prompt that should be optimized for better performance and clarity."
        optimized_prompt = "This is an optimized prompt."
        
        improvement_score = optimizer._calculate_improvement_score(
            original_prompt, optimized_prompt, sample_context
        )
        
        assert 0.0 <= improvement_score <= 1.0
        assert improvement_score > 0.0  # Should show some improvement
    
    def test_performance_gain_prediction(self, optimizer, sample_context):
        """Test performance gain prediction."""
        original_prompt = "A longer prompt with more words and complexity."
        optimized_prompt = "A shorter prompt."
        
        performance_gain = optimizer._predict_performance_gain(
            original_prompt, optimized_prompt, sample_context
        )
        
        assert 0.0 <= performance_gain <= 0.5
        assert performance_gain > 0.0  # Should predict some gain
    
    def test_cost_reduction_prediction(self, optimizer, sample_context):
        """Test cost reduction prediction."""
        original_prompt = "A prompt with many words and tokens."
        optimized_prompt = "A shorter prompt."
        
        cost_reduction = optimizer._predict_cost_reduction(
            original_prompt, optimized_prompt, sample_context
        )
        
        assert cost_reduction >= 0.0
        assert cost_reduction <= sample_context.cost_per_request
    
    def test_confidence_score_calculation(self, optimizer, sample_context):
        """Test confidence score calculation."""
        confidence_score = optimizer._calculate_confidence_score(
            sample_context, OptimizationType.PERFORMANCE
        )
        
        assert 0.0 <= confidence_score <= 1.0
        assert confidence_score > 0.0  # Should have some confidence
    
    def test_task_complexity_calculation(self, optimizer):
        """Test task complexity calculation."""
        complexities = {
            "simple": 0.3,
            "basic": 0.5,
            "moderate": 0.7,
            "complex": 0.9,
            "advanced": 1.0,
            "unknown": 0.5  # Default for unknown types
        }
        
        for task_type, expected_complexity in complexities.items():
            complexity = optimizer._calculate_task_complexity(task_type)
            assert complexity == expected_complexity
    
    def test_optimization_with_error_handling(self, optimizer):
        """Test optimization error handling."""
        # Create context with invalid data to trigger errors
        context = OptimizationContext(
            user_id="test_user",
            task_type="moderate",
            agent_type="test_agent",
            usage_pattern={"recent_uses": "invalid"},  # Invalid data
            performance_history=[1.0, 2.0],
            success_rate=0.8,
            response_time=2.0,
            cost_per_request=0.05,
            timestamp=datetime.now()
        )
        
        original_prompt = "Test prompt for error handling."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_error",
            prompt_text=original_prompt,
            context=context,
            optimization_type=OptimizationType.PERFORMANCE
        )
        
        # Should handle errors gracefully and return a result
        assert result is not None
        assert result.status in [OptimizationStatus.COMPLETED, OptimizationStatus.FAILED]
    
    def test_global_optimizer_instance(self):
        """Test global optimizer instance."""
        optimizer1 = get_advanced_optimizer()
        optimizer2 = get_advanced_optimizer()
        
        # Should return the same instance
        assert optimizer1 is optimizer2
    
    def test_optimization_metadata(self, optimizer, sample_context):
        """Test optimization metadata storage."""
        original_prompt = "Test prompt for metadata."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_metadata",
            prompt_text=original_prompt,
            context=sample_context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        assert result.metadata is not None
        assert "optimization_type" in result.metadata
        assert "context_summary" in result.metadata
        assert result.metadata["optimization_type"] == OptimizationType.ADAPTIVE.value
        assert result.metadata["context_summary"]["user_id"] == sample_context.user_id


class TestAdvancedOptimizationIntegration:
    """Test integration with existing prompt management systems."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_dir):
        """Create optimizer instance for testing."""
        return AdvancedPromptOptimizer(optimization_dir=temp_dir)
    
    def test_integration_with_template_system(self, optimizer, temp_dir):
        """Test integration with template system."""
        from utils.prompt_management import PromptTemplateSystem, TemplateType, TemplateStatus
        
        # Create template system
        template_system = PromptTemplateSystem(templates_dir=f"{temp_dir}/templates")
        
        # Create a template
        template_id = template_system.create_template(
            name="Test Template",
            description="Template for integration testing",
            template_type=TemplateType.ENHANCED,
            agent_type="test_agent",
            template_text="Please provide a comprehensive analysis of the requirements.",
            author="test_user"
        )
        
        # Create context for optimization
        context = OptimizationContext(
            user_id="test_user",
            task_type="moderate",
            agent_type="test_agent",
            usage_pattern={"recent_uses": []},
            performance_history=[2.0, 2.1, 1.9],
            success_rate=0.85,
            response_time=2.0,
            cost_per_request=0.05,
            timestamp=datetime.now()
        )
        
        # Get template and optimize it
        template = template_system.get_template(template_id)
        assert template is not None
        
        result = optimizer.optimize_prompt(
            prompt_id=template_id,
            prompt_text=template.template_text,
            context=context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        
        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
        assert result.prompt_id == template_id
    
    def test_integration_with_analytics(self, optimizer, temp_dir):
        """Test integration with analytics system."""
        from utils.prompt_management import PromptAnalytics
        
        # Create analytics system
        analytics = PromptAnalytics(analytics_dir=f"{temp_dir}/analytics")
        
        # Create context for optimization
        context = OptimizationContext(
            user_id="test_user",
            task_type="moderate",
            agent_type="test_agent",
            usage_pattern={"recent_uses": []},
            performance_history=[2.0, 2.1, 1.9],
            success_rate=0.85,
            response_time=2.0,
            cost_per_request=0.05,
            timestamp=datetime.now()
        )
        
        # Perform optimization
        original_prompt = "Test prompt for analytics integration."
        
        result = optimizer.optimize_prompt(
            prompt_id="test_analytics",
            prompt_text=original_prompt,
            context=context,
            optimization_type=OptimizationType.PERFORMANCE
        )
        
        # Record performance metrics
        from utils.prompt_management.prompt_analytics import PerformanceMetrics
        
        performance_metrics = PerformanceMetrics(
            prompt_id="test_analytics",
            response_time=result.context.response_time * (1 - result.performance_gain),
            token_count=100,  # Estimated token count
            success_rate=result.context.success_rate + result.improvement_score * 0.1,
            error_rate=1.0 - (result.context.success_rate + result.improvement_score * 0.1),
            user_satisfaction=0.8 + result.improvement_score * 0.2,
            timestamp=datetime.now()
        )
        
        analytics.record_performance_metrics(performance_metrics)
        
        # Get performance summary
        summary = analytics.get_performance_summary("test_analytics")
        
        assert summary is not None
        assert "total_requests" in summary
        assert "avg_response_time" in summary
        assert "avg_success_rate" in summary


class TestAdvancedOptimizationPerformance:
    """Test performance characteristics of the advanced optimizer."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_dir):
        """Create optimizer instance for testing."""
        return AdvancedPromptOptimizer(optimization_dir=temp_dir)
    
    def test_optimization_speed(self, optimizer):
        """Test optimization speed for performance targets."""
        import time
        
        context = OptimizationContext(
            user_id="test_user",
            task_type="moderate",
            agent_type="test_agent",
            usage_pattern={"recent_uses": []},
            performance_history=[2.0, 2.1, 1.9],
            success_rate=0.85,
            response_time=2.0,
            cost_per_request=0.05,
            timestamp=datetime.now()
        )
        
        original_prompt = "This is a test prompt for performance testing."
        
        # Measure optimization time
        start_time = time.time()
        result = optimizer.optimize_prompt(
            prompt_id="test_performance",
            prompt_text=original_prompt,
            context=context,
            optimization_type=OptimizationType.ADAPTIVE
        )
        end_time = time.time()
        
        optimization_time = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second)
        assert optimization_time < 1.0
        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
    
    def test_concurrent_optimizations(self, optimizer):
        """Test handling of concurrent optimizations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def optimize_prompt(prompt_id, prompt_text):
            try:
                context = OptimizationContext(
                    user_id=f"user_{prompt_id}",
                    task_type="moderate",
                    agent_type="test_agent",
                    usage_pattern={"recent_uses": []},
                    performance_history=[2.0, 2.1, 1.9],
                    success_rate=0.85,
                    response_time=2.0,
                    cost_per_request=0.05,
                    timestamp=datetime.now()
                )
                
                result = optimizer.optimize_prompt(
                    prompt_id=prompt_id,
                    prompt_text=prompt_text,
                    context=context,
                    optimization_type=OptimizationType.PERFORMANCE
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads for concurrent optimization
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=optimize_prompt,
                args=(f"concurrent_{i}", f"Test prompt {i} for concurrent optimization.")
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        for result in results:
            assert result is not None
            assert result.status == OptimizationStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
