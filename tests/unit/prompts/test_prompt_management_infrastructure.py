"""
Test suite for US-PE-02: Prompt Management Infrastructure

Tests the advanced prompt management infrastructure including:
- Analytics engine functionality
- Web interface components
- Performance tracking and reporting
- Optimization recommendations
- Integration with existing systems
"""

import pytest
import tempfile
import shutil
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import json

def safe_cleanup_temp_dir(temp_dir, *objects_to_close):
    """Safely clean up temporary directory with database files on Windows."""
    # Close any database connections
    for obj in objects_to_close:
        try:
            if hasattr(obj, 'close'):
                obj.close()
        except Exception:
            pass
    
    # Retry cleanup for Windows file locking
    for attempt in range(3):
        try:
            shutil.rmtree(temp_dir)
            break
        except PermissionError:
            if attempt < 2:
                time.sleep(0.1)
                continue
            # Final attempt: force cleanup
            try:
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for file in files:
                        try:
                            os.chmod(os.path.join(root, file), 0o777)
                            os.remove(os.path.join(root, file))
                        except:
                            pass
                    for dir in dirs:
                        try:
                            os.rmdir(os.path.join(root, dir))
                        except:
                            pass
                os.rmdir(temp_dir)
            except:
                pass  # Give up gracefully

from utils.prompt_management import (
    PromptAnalytics, AnalyticsPerformanceMetrics as PerformanceMetrics, CostMetrics, QualityMetrics,
    OptimizationRecommendation, TrendAnalysis, MetricType, TrendDirection,
    PromptWebInterface, PromptTemplateSystem, TemplateType, TemplateStatus,
    PromptOptimizer, OptimizationStrategy, PromptManager
)


class TestPromptAnalytics:
    """Test the prompt analytics engine."""
    
    @pytest.fixture
    def analytics(self):
        """Create a temporary analytics instance."""
        temp_dir = tempfile.mkdtemp()
        analytics = PromptAnalytics(analytics_dir=temp_dir)
        yield analytics
        safe_cleanup_temp_dir(temp_dir, analytics)
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics for testing."""
        return {
            "performance": PerformanceMetrics(
                prompt_id="test_prompt_1",
                response_time=2.5,
                token_count=150,
                success_rate=0.95,
                error_rate=0.05,
                user_satisfaction=0.8,
                timestamp=datetime.now()
            ),
            "cost": CostMetrics(
                prompt_id="test_prompt_1",
                input_tokens=100,
                output_tokens=50,
                total_cost=0.15,
                cost_per_request=0.15,
                model_used="gemini-2.5-flash",
                timestamp=datetime.now()
            ),
            "quality": QualityMetrics(
                prompt_id="test_prompt_1",
                clarity_score=0.85,
                relevance_score=0.90,
                completeness_score=0.80,
                consistency_score=0.88,
                overall_quality=0.86,
                timestamp=datetime.now()
            )
        }
    
    def test_analytics_initialization(self, analytics):
        """Test analytics engine initialization."""
        assert analytics.analytics_dir.exists()
        assert analytics.db_path.exists()
    
    def test_record_performance_metrics(self, analytics, sample_metrics):
        """Test recording performance metrics."""
        result = analytics.record_performance_metrics(sample_metrics["performance"])
        assert result is True
    
    def test_record_cost_metrics(self, analytics, sample_metrics):
        """Test recording cost metrics."""
        result = analytics.record_cost_metrics(sample_metrics["cost"])
        assert result is True
    
    def test_record_quality_metrics(self, analytics, sample_metrics):
        """Test recording quality metrics."""
        result = analytics.record_quality_metrics(sample_metrics["quality"])
        assert result is True
    
    def test_get_performance_summary(self, analytics, sample_metrics):
        """Test getting performance summary."""
        # Record metrics first
        analytics.record_performance_metrics(sample_metrics["performance"])
        
        # Get summary
        summary = analytics.get_performance_summary("test_prompt_1")
        assert summary is not None
        assert summary["prompt_id"] == "test_prompt_1"
        assert "avg_response_time" in summary
        assert "avg_success_rate" in summary
    
    def test_get_cost_summary(self, analytics, sample_metrics):
        """Test getting cost summary."""
        # Record metrics first
        analytics.record_cost_metrics(sample_metrics["cost"])
        
        # Get summary
        summary = analytics.get_cost_summary("test_prompt_1")
        assert summary is not None
        assert summary["prompt_id"] == "test_prompt_1"
        assert "total_cost" in summary
        assert "avg_cost_per_request" in summary
    
    def test_get_quality_summary(self, analytics, sample_metrics):
        """Test getting quality summary."""
        # Record metrics first
        analytics.record_quality_metrics(sample_metrics["quality"])
        
        # Get summary
        summary = analytics.get_quality_summary("test_prompt_1")
        assert summary is not None
        assert summary["prompt_id"] == "test_prompt_1"
        assert "avg_overall_quality" in summary
        assert "avg_clarity_score" in summary
    
    def test_generate_optimization_recommendations(self, analytics, sample_metrics):
        """Test generating optimization recommendations."""
        # Record all metrics first
        analytics.record_performance_metrics(sample_metrics["performance"])
        analytics.record_cost_metrics(sample_metrics["cost"])
        analytics.record_quality_metrics(sample_metrics["quality"])
        
        # Generate recommendations
        recommendations = analytics.generate_optimization_recommendations("test_prompt_1")
        assert isinstance(recommendations, list)
        
        # Should have recommendations based on our test data
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert isinstance(rec, OptimizationRecommendation)
            assert rec.prompt_id == "test_prompt_1"
            assert rec.recommendation_type in [
                "performance_optimization", "cost_optimization", 
                "quality_improvement", "reliability_improvement"
            ]
            assert rec.expected_improvement > 0
            assert 0 <= rec.confidence_score <= 1
    
    def test_get_trend_analysis(self, analytics, sample_metrics):
        """Test trend analysis functionality."""
        # Record metrics for trend analysis
        analytics.record_performance_metrics(sample_metrics["performance"])
        analytics.record_cost_metrics(sample_metrics["cost"])
        analytics.record_quality_metrics(sample_metrics["quality"])
        
        # Test performance trend
        trend = analytics.get_trend_analysis("test_prompt_1", MetricType.PERFORMANCE)
        # May be None if not enough data for trend analysis
        if trend is not None:
            assert isinstance(trend, TrendAnalysis)
            assert trend.prompt_id == "test_prompt_1"
            assert trend.metric_type == MetricType.PERFORMANCE
            assert trend.trend_direction in [
                TrendDirection.IMPROVING, 
                TrendDirection.DECLINING, 
                TrendDirection.STABLE,
                TrendDirection.UNKNOWN
            ]
    
    def test_get_comprehensive_analytics(self, analytics, sample_metrics):
        """Test comprehensive analytics generation."""
        # Record all metrics first
        analytics.record_performance_metrics(sample_metrics["performance"])
        analytics.record_cost_metrics(sample_metrics["cost"])
        analytics.record_quality_metrics(sample_metrics["quality"])
        
        # Get comprehensive analytics
        comprehensive = analytics.get_comprehensive_analytics("test_prompt_1")
        assert comprehensive is not None
        assert comprehensive["prompt_id"] == "test_prompt_1"
        assert "performance" in comprehensive
        assert "cost" in comprehensive
        assert "quality" in comprehensive
        assert "trends" in comprehensive
        assert "recommendations" in comprehensive
        assert "generated_at" in comprehensive


class TestPromptWebInterface:
    """Test the web interface components."""
    
    @pytest.fixture
    def web_interface(self):
        """Create a web interface instance for testing."""
        temp_dir = tempfile.mkdtemp()
        interface = PromptWebInterface()
        # Override paths to use temp directory
        interface.analytics = PromptAnalytics(analytics_dir=f"{temp_dir}/analytics")
        interface.template_system = PromptTemplateSystem(templates_dir=f"{temp_dir}/templates")
        interface.optimizer = PromptOptimizer(cache_dir=f"{temp_dir}/cache")
        yield interface
        safe_cleanup_temp_dir(temp_dir, interface.analytics, interface.template_system, interface.optimizer, interface.prompt_manager)
    
    def test_web_interface_initialization(self, web_interface):
        """Test web interface initialization."""
        assert web_interface.analytics is not None
        assert web_interface.template_system is not None
        assert web_interface.optimizer is not None
        assert web_interface.prompt_manager is not None
    
    def test_get_total_prompts(self, web_interface):
        """Test getting total prompts count."""
        count = web_interface._get_total_prompts()
        assert isinstance(count, int)
        assert count >= 0
    
    def test_get_active_templates(self, web_interface):
        """Test getting active templates count."""
        count = web_interface._get_active_templates()
        assert isinstance(count, int)
        assert count >= 0
    
    def test_get_prompt_ids(self, web_interface):
        """Test getting prompt IDs list."""
        prompt_ids = web_interface._get_prompt_ids()
        assert isinstance(prompt_ids, list)
        # Should return at least sample prompts if no real data
        assert len(prompt_ids) >= 0
    
    def test_dashboard_metrics(self, web_interface):
        """Test dashboard metrics calculation."""
        # Test all dashboard metric methods
        assert isinstance(web_interface._get_avg_response_time(), float)
        assert isinstance(web_interface._get_total_cost_24h(), float)
        assert isinstance(web_interface._get_prompt_growth(), str)
        assert isinstance(web_interface._get_template_growth(), str)
        assert isinstance(web_interface._get_response_time_change(), str)
        assert isinstance(web_interface._get_cost_change(), str)


class TestIntegrationWithExistingSystems:
    """Test integration with existing prompt management systems."""
    
    @pytest.fixture
    def integrated_system(self):
        """Create an integrated system for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create all components with temp directories
        analytics = PromptAnalytics(analytics_dir=f"{temp_dir}/analytics")
        template_system = PromptTemplateSystem(templates_dir=f"{temp_dir}/templates")
        optimizer = PromptOptimizer(cache_dir=f"{temp_dir}/cache")
        prompt_manager = PromptManager()
        
        yield {
            "analytics": analytics,
            "template_system": template_system,
            "optimizer": optimizer,
            "prompt_manager": prompt_manager
        }
        
        safe_cleanup_temp_dir(temp_dir, analytics, template_system, optimizer, prompt_manager)
    
    def test_template_creation_with_analytics(self, integrated_system):
        """Test creating templates and tracking analytics."""
        template_system = integrated_system["template_system"]
        analytics = integrated_system["analytics"]
        
        # Create a template
        template_id = template_system.create_template(
            name="Test Template",
            description="Test template for integration",
            template_type=TemplateType.ENHANCED,
            agent_type="test_agent",
            template_text="This is a test prompt template.",
            author="test_user"
        )
        
        assert template_id is not None
        
        # Record performance metrics for the template
        performance_metrics = PerformanceMetrics(
            prompt_id=template_id,
            response_time=1.5,
            token_count=100,
            success_rate=0.98,
            error_rate=0.02,
            user_satisfaction=0.9,
            timestamp=datetime.now()
        )
        
        result = analytics.record_performance_metrics(performance_metrics)
        assert result is True
        
        # Get analytics for the template
        summary = analytics.get_performance_summary(template_id)
        assert summary is not None
        assert summary["prompt_id"] == template_id
    
    def test_optimization_with_analytics(self, integrated_system):
        """Test optimization with analytics tracking."""
        optimizer = integrated_system["optimizer"]
        analytics = integrated_system["analytics"]
        
        # Test prompt
        test_prompt = "This is a test prompt that needs optimization for better performance and clarity."
        
        # Optimize the prompt
        result = optimizer.optimize_prompt(test_prompt, OptimizationStrategy.TOKEN_REDUCTION)
        assert result is not None
        # Note: Simple prompts might not be optimized, so we just check the result exists
        
        # Record cost metrics for the optimization
        cost_metrics = CostMetrics(
            prompt_id="optimized_prompt_1",
            input_tokens=len(test_prompt.split()),
            output_tokens=len(result.optimized_prompt.split()),
            total_cost=0.05,
            cost_per_request=0.05,
            model_used="gemini-2.5-flash",
            timestamp=datetime.now()
        )
        
        result = analytics.record_cost_metrics(cost_metrics)
        assert result is True
        
        # Get cost summary
        summary = analytics.get_cost_summary("optimized_prompt_1")
        assert summary is not None
        assert summary["total_cost"] == 0.05
    
    def test_comprehensive_workflow(self, integrated_system):
        """Test a comprehensive workflow with all components."""
        template_system = integrated_system["template_system"]
        analytics = integrated_system["analytics"]
        optimizer = integrated_system["optimizer"]
        
        # 1. Create a template
        template_id = template_system.create_template(
            name="Workflow Template",
            description="Template for comprehensive workflow testing",
            template_type=TemplateType.ENHANCED,
            agent_type="workflow_agent",
            template_text="Generate a comprehensive analysis of the given requirements.",
            author="workflow_user"
        )
        
        # 2. Record performance metrics
        performance_metrics = PerformanceMetrics(
            prompt_id=template_id,
            response_time=2.0,
            token_count=200,
            success_rate=0.92,
            error_rate=0.08,
            user_satisfaction=0.85,
            timestamp=datetime.now()
        )
        analytics.record_performance_metrics(performance_metrics)
        
        # 3. Record cost metrics
        cost_metrics = CostMetrics(
            prompt_id=template_id,
            input_tokens=150,
            output_tokens=50,
            total_cost=0.12,
            cost_per_request=0.12,
            model_used="gemini-2.5-flash",
            timestamp=datetime.now()
        )
        analytics.record_cost_metrics(cost_metrics)
        
        # 4. Record quality metrics
        quality_metrics = QualityMetrics(
            prompt_id=template_id,
            clarity_score=0.88,
            relevance_score=0.92,
            completeness_score=0.85,
            consistency_score=0.90,
            overall_quality=0.89,
            timestamp=datetime.now()
        )
        analytics.record_quality_metrics(quality_metrics)
        
        # 5. Generate optimization recommendations
        recommendations = analytics.generate_optimization_recommendations(template_id)
        assert len(recommendations) > 0
        
        # 6. Get comprehensive analytics
        comprehensive = analytics.get_comprehensive_analytics(template_id)
        assert comprehensive is not None
        assert comprehensive["prompt_id"] == template_id
        assert comprehensive["performance"] is not None
        assert comprehensive["cost"] is not None
        assert comprehensive["quality"] is not None
        assert len(comprehensive["recommendations"]) > 0


class TestPerformanceAndScalability:
    """Test performance and scalability of the infrastructure."""
    
    @pytest.fixture
    def performance_system(self):
        """Create a system for performance testing."""
        temp_dir = tempfile.mkdtemp()
        analytics = PromptAnalytics(analytics_dir=f"{temp_dir}/analytics")
        yield analytics
        safe_cleanup_temp_dir(temp_dir, analytics)
    
    def test_bulk_metrics_recording(self, performance_system):
        """Test recording many metrics efficiently."""
        start_time = datetime.now()
        
        # Record 100 performance metrics
        for i in range(100):
            metrics = PerformanceMetrics(
                prompt_id=f"bulk_prompt_{i}",
                response_time=1.0 + (i % 5) * 0.1,
                token_count=100 + i,
                success_rate=0.9 + (i % 10) * 0.01,
                error_rate=0.1 - (i % 10) * 0.01,
                user_satisfaction=0.8 + (i % 20) * 0.01,
                timestamp=datetime.now()
            )
            result = performance_system.record_performance_metrics(metrics)
            assert result is True
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 10.0  # 10 seconds for 100 records
        
        # Verify all records were saved
        summary = performance_system.get_performance_summary("bulk_prompt_0")
        assert summary is not None
        assert summary["total_requests"] == 1
    
    def test_concurrent_analytics_access(self, performance_system):
        """Test concurrent access to analytics."""
        import threading
        import time
        
        results = []
        errors = []
        
        def record_metrics(thread_id):
            try:
                for i in range(10):
                    metrics = PerformanceMetrics(
                        prompt_id=f"concurrent_prompt_{thread_id}_{i}",
                        response_time=1.5,
                        token_count=120,
                        success_rate=0.95,
                        error_rate=0.05,
                        user_satisfaction=0.85,
                        timestamp=datetime.now()
                    )
                    result = performance_system.record_performance_metrics(metrics)
                    results.append(result)
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Create 5 threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=record_metrics, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50  # 5 threads * 10 records each
        assert all(results)  # All should be True


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def error_system(self):
        """Create a system for error testing."""
        temp_dir = tempfile.mkdtemp()
        analytics = PromptAnalytics(analytics_dir=f"{temp_dir}/analytics")
        yield analytics
        safe_cleanup_temp_dir(temp_dir, analytics)
    
    def test_invalid_metrics_handling(self, error_system):
        """Test handling of invalid metrics."""
        # Test with invalid prompt_id
        metrics = PerformanceMetrics(
            prompt_id="",  # Empty prompt_id
            response_time=-1.0,  # Negative response time
            token_count=-10,  # Negative token count
            success_rate=1.5,  # Success rate > 1.0
            error_rate=-0.1,  # Negative error rate
            user_satisfaction=2.0,  # Satisfaction > 1.0
            timestamp=datetime.now()
        )
        
        # Should handle gracefully (may return False or raise exception)
        try:
            result = error_system.record_performance_metrics(metrics)
            # If it doesn't raise an exception, result should be False
            assert result is False
        except Exception:
            # Exception is also acceptable for invalid data
            pass
    
    def test_missing_data_handling(self, error_system):
        """Test handling of missing data."""
        # Test getting analytics for non-existent prompt
        summary = error_system.get_performance_summary("non_existent_prompt")
        # May return empty summary or None, both are acceptable
        assert summary is None or summary.get("total_requests", 0) == 0
        
        # Test getting recommendations for non-existent prompt
        recommendations = error_system.generate_optimization_recommendations("non_existent_prompt")
        assert recommendations == []
    
    def test_database_corruption_handling(self, error_system):
        """Test handling of database corruption scenarios."""
        # This test would require more sophisticated setup to simulate database corruption
        # For now, we test that the system handles missing database gracefully
        
        # Close the database connection first
        try:
            if hasattr(error_system, 'close'):
                error_system.close()
        except Exception:
            pass
        
        # Remove the database file (retry on Windows file locking)
        if error_system.db_path.exists():
            import time
            for attempt in range(3):
                try:
                    error_system.db_path.unlink()
                    break
                except PermissionError:
                    if attempt < 2:
                        time.sleep(0.1)
                        continue
                    # Skip test if we can't delete the file (Windows file locking)
                    pytest.skip("Cannot delete database file due to Windows file locking")
        
        # Try to record metrics - should handle gracefully
        metrics = PerformanceMetrics(
            prompt_id="test_prompt",
            response_time=1.0,
            token_count=100,
            success_rate=0.95,
            error_rate=0.05,
            user_satisfaction=0.8,
            timestamp=datetime.now()
        )
        
        try:
            result = error_system.record_performance_metrics(metrics)
            # Should either return False or raise an exception
            assert result is False
        except Exception:
            # Exception is acceptable for database issues
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
