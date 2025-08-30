"""
Test Suite for Prompt Engineering System
========================================

Comprehensive tests for the prompt engineering system components:
- Template system
- Optimization framework
- A/B testing framework
- Integration testing

This validates all US-PE-01 functionality.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from utils.prompt_management import (
    PromptEngineeringSystem,
    get_prompt_engineering_system,
    TemplateType,
    TemplateStatus,
    OptimizationStrategy,
    TestType,
    TestStatus
)


class TestPromptEngineeringSystem:
    """Test the unified prompt engineering system."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def system(self, temp_dir):
        """Create prompt engineering system with temporary directory."""
        # Override default directories
        system = PromptEngineeringSystem()
        system.template_system.templates_dir = Path(temp_dir) / "templates"
        system.optimizer.cache_dir = Path(temp_dir) / "cache"
        system.ab_testing.tests_dir = Path(temp_dir) / "ab_tests"
        return system
    
    def test_create_optimized_template(self, system):
        """Test creating an optimized template."""
        template_id = system.create_optimized_template(
            name="Test Template",
            description="A test template",
            agent_type="test_agent",
            template_text="Please analyze {{input}} and provide insights.",
            author="test_user",
            optimization_strategy=OptimizationStrategy.CLARITY_ENHANCEMENT,
            tags=["test", "analysis"]
        )
        
        assert template_id is not None
        
        # Verify template was created
        template = system.template_system.get_template(template_id)
        assert template is not None
        assert template.name == "Test Template"
        assert template.agent_type == "test_agent"
        assert template.status == TemplateStatus.ACTIVE
        
        # Verify optimization was applied
        assert template.metadata.get('optimization_applied') is True
        assert template.metadata.get('optimization_strategy') == 'clarity_enhancement'
        # Note: Improvement score can be negative if optimization adds clarity at cost of tokens
        assert 'improvement_score' in template.metadata
    
    def test_create_ab_test(self, system):
        """Test creating an A/B test."""
        test_id = system.create_ab_test(
            name="Test A/B Test",
            description="Testing prompt variants",
            agent_type="test_agent",
            variant_a_text="Please analyze the data.",
            variant_b_text="Please analyze the data and provide detailed insights.",
            test_type=TestType.PROMPT_VARIATION
        )
        
        assert test_id is not None
        
        # Verify test was created
        test = system.ab_testing.get_test(test_id)
        assert test is not None
        assert test.name == "Test A/B Test"
        assert test.test_type == TestType.PROMPT_VARIATION
        assert test.status == TestStatus.DRAFT
        
        # Verify variants
        assert test.variant_a['prompt_text'] == "Please analyze the data."
        assert test.variant_b['prompt_text'] == "Please analyze the data and provide detailed insights."
    
    def test_get_optimization_recommendations(self, system):
        """Test getting optimization recommendations."""
        # Create a very long prompt that will trigger recommendations
        long_prompt = "This is a very long prompt that should trigger optimization recommendations. " * 100
        
        recommendations = system.get_optimization_recommendations(long_prompt)
        
        assert len(recommendations) > 0
        
        # Should recommend token reduction for long prompt
        token_reduction_rec = next(
            (r for r in recommendations if r['strategy'] == OptimizationStrategy.TOKEN_REDUCTION),
            None
        )
        assert token_reduction_rec is not None
        assert token_reduction_rec['priority'] == 'high'
    
    def test_render_template_with_context(self, system):
        """Test rendering template with context."""
        # Create template
        template_id = system.template_system.create_template(
            name="Context Template",
            description="Template with context variables",
            template_type=TemplateType.SIMPLE,
            agent_type="test_agent",
            template_text="Hello {{name}}, please analyze {{data}}.",
            author="test_user"
        )
        
        # Render with context
        context = {"name": "John", "data": "sales data"}
        rendered = system.render_template_with_context(template_id, context)
        
        assert rendered == "Hello John, please analyze sales data."
    
    def test_record_prompt_performance(self, system):
        """Test recording prompt performance."""
        system.record_prompt_performance(
            prompt_id="test_prompt_123",
            execution_time=2.5,
            token_count=150,
            response_quality=0.85,
            success=True,
            metadata={"user_id": "test_user"}
        )
        
        # Verify performance was recorded
        metrics = system.optimizer.get_performance_metrics("test_prompt_123")
        assert len(metrics) == 1
        
        metric = metrics[0]
        assert metric.prompt_id == "test_prompt_123"
        assert metric.execution_time == 2.5
        assert metric.token_count == 150
        assert metric.response_quality == 0.85
        assert metric.success_rate == 1.0
    
    def test_get_system_status(self, system):
        """Test getting system status."""
        status = system.get_system_status()
        
        assert 'prompt_manager' in status
        assert 'template_system' in status
        assert 'optimizer' in status
        assert 'ab_testing' in status
        
        # Verify all components are initialized
        assert status['prompt_manager']['database_status'] == 'active'
        assert status['template_system']['total_templates'] >= 0
        assert status['optimizer']['optimization_history'] >= 0
        assert status['ab_testing']['total_tests'] >= 0


class TestTemplateSystem:
    """Test the template system component."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def template_system(self, temp_dir):
        """Create template system with temporary directory."""
        from utils.prompt_management.prompt_template_system import PromptTemplateSystem
        return PromptTemplateSystem(templates_dir=temp_dir)
    
    def test_create_template(self, template_system):
        """Test creating a template."""
        template_id = template_system.create_template(
            name="Test Template",
            description="A test template",
            template_type=TemplateType.ENHANCED,
            agent_type="test_agent",
            template_text="Test prompt text",
            author="test_user",
            tags=["test"],
            parameters={"max_tokens": 100}
        )
        
        assert template_id is not None
        
        # Verify template was created
        template = template_system.get_template(template_id)
        assert template is not None
        assert template.name == "Test Template"
        assert template.template_type == TemplateType.ENHANCED
        assert template.agent_type == "test_agent"
        assert template.status == TemplateStatus.DRAFT
        assert template.tags == ["test"]
        assert template.parameters == {"max_tokens": 100}
    
    def test_update_template(self, template_system):
        """Test updating a template."""
        # Create template
        template_id = template_system.create_template(
            name="Original Name",
            description="Original description",
            template_type=TemplateType.SIMPLE,
            agent_type="test_agent",
            template_text="Original text",
            author="test_user"
        )
        
        # Update template
        success = template_system.update_template(template_id, {
            'name': 'Updated Name',
            'status': TemplateStatus.ACTIVE,
            'template_text': 'Updated text'
        })
        
        assert success is True
        
        # Verify updates
        template = template_system.get_template(template_id)
        assert template.name == "Updated Name"
        assert template.status == TemplateStatus.ACTIVE
        assert template.template_text == "Updated text"
    
    def test_create_version(self, template_system):
        """Test creating a new version of a template."""
        # Create original template
        original_id = template_system.create_template(
            name="Original Template",
            description="Original description",
            template_type=TemplateType.SIMPLE,
            agent_type="test_agent",
            template_text="Original text",
            author="test_user"
        )
        
        # Create new version
        new_version_id = template_system.create_version(
            template_id=original_id,
            new_version="2.0.0",
            template_text="New version text",
            author="test_user"
        )
        
        assert new_version_id != original_id
        
        # Verify new version
        new_template = template_system.get_template(new_version_id)
        assert new_template.name == "Original Template (v2.0.0)"
        assert new_template.version == "2.0.0"
        assert new_template.template_text == "New version text"
        assert new_template.status == TemplateStatus.DRAFT
    
    def test_render_template(self, template_system):
        """Test rendering a template with context."""
        # Create template with variables
        template_id = template_system.create_template(
            name="Variable Template",
            description="Template with variables",
            template_type=TemplateType.SIMPLE,
            agent_type="test_agent",
            template_text="Hello {{name}}, analyze {{data}}.",
            author="test_user"
        )
        
        # Render with context
        context = {"name": "Alice", "data": "sales data"}
        rendered = template_system.render_template(template_id, context)
        
        assert rendered == "Hello Alice, analyze sales data."
    
    def test_get_templates_by_agent(self, template_system):
        """Test getting templates by agent type."""
        # Create templates for different agents
        template_system.create_template(
            name="Agent A Template",
            description="Template for agent A",
            template_type=TemplateType.SIMPLE,
            agent_type="agent_a",
            template_text="Agent A prompt",
            author="test_user"
        )
        
        template_system.create_template(
            name="Agent B Template",
            description="Template for agent B",
            template_type=TemplateType.SIMPLE,
            agent_type="agent_b",
            template_text="Agent B prompt",
            author="test_user"
        )
        
        # Activate templates (they start as DRAFT)
        for template in template_system.templates.values():
            template_system.update_template(template.template_id, {'status': TemplateStatus.ACTIVE})
        
        # Get templates for agent A
        agent_a_templates = template_system.get_templates_by_agent("agent_a")
        assert len(agent_a_templates) == 1
        assert agent_a_templates[0].agent_type == "agent_a"
        
        # Get templates for agent B
        agent_b_templates = template_system.get_templates_by_agent("agent_b")
        assert len(agent_b_templates) == 1
        assert agent_b_templates[0].agent_type == "agent_b"


class TestOptimizer:
    """Test the optimization framework component."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def optimizer(self, temp_dir):
        """Create optimizer with temporary directory."""
        from utils.prompt_management.prompt_optimizer import PromptOptimizer
        return PromptOptimizer(cache_dir=temp_dir)
    
    def test_optimize_token_reduction(self, optimizer):
        """Test token reduction optimization."""
        original_prompt = """
        Please note that it is important to analyze the data thoroughly and provide comprehensive insights 
        that will help us understand the underlying patterns and trends that may be present in the dataset.
        """
        
        result = optimizer.optimize_prompt(
            original_prompt,
            OptimizationStrategy.TOKEN_REDUCTION
        )
        
        assert result.original_prompt == original_prompt
        assert result.optimized_prompt != original_prompt
        assert result.strategy == OptimizationStrategy.TOKEN_REDUCTION
        assert result.token_reduction > 0
        assert result.improvement_score > 0
    
    def test_optimize_clarity(self, optimizer):
        """Test clarity enhancement optimization."""
        original_prompt = "Analyze data and provide insights."
        
        result = optimizer.optimize_prompt(
            original_prompt,
            OptimizationStrategy.CLARITY_ENHANCEMENT
        )
        
        assert result.original_prompt == original_prompt
        assert result.optimized_prompt != original_prompt
        assert result.strategy == OptimizationStrategy.CLARITY_ENHANCEMENT
        assert "Instructions:" in result.optimized_prompt
    
    def test_optimize_context(self, optimizer):
        """Test context optimization."""
        original_prompt = "Analyze the data."
        context = {"data_type": "sales", "timeframe": "Q1 2024"}
        
        result = optimizer.optimize_prompt(
            original_prompt,
            OptimizationStrategy.CONTEXT_OPTIMIZATION,
            context=context
        )
        
        assert result.original_prompt == original_prompt
        assert result.optimized_prompt != original_prompt
        assert result.strategy == OptimizationStrategy.CONTEXT_OPTIMIZATION
        assert "Context:" in result.optimized_prompt
        assert "sales" in result.optimized_prompt
    
    def test_get_optimization_recommendations(self, optimizer):
        """Test getting optimization recommendations."""
        # Create a very long prompt that will trigger recommendations
        long_prompt = "This is a very long prompt that should trigger optimization recommendations. " * 100
        
        recommendations = optimizer.get_optimization_recommendations(long_prompt)
        
        assert len(recommendations) > 0
        
        # Should recommend token reduction
        token_rec = next(
            (r for r in recommendations if r['strategy'] == OptimizationStrategy.TOKEN_REDUCTION),
            None
        )
        assert token_rec is not None
        assert token_rec['priority'] == 'high'
    
    def test_record_performance(self, optimizer):
        """Test recording performance metrics."""
        optimizer.record_performance(
            prompt_id="test_prompt",
            execution_time=1.5,
            token_count=100,
            response_quality=0.9,
            success=True,
            metadata={"user_id": "test"}
        )
        
        metrics = optimizer.get_performance_metrics("test_prompt")
        assert len(metrics) == 1
        
        metric = metrics[0]
        assert metric.prompt_id == "test_prompt"
        assert metric.execution_time == 1.5
        assert metric.token_count == 100
        assert metric.response_quality == 0.9
        assert metric.success_rate == 1.0


class TestABTesting:
    """Test the A/B testing framework component."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def ab_testing(self, temp_dir):
        """Create A/B testing with temporary directory."""
        from utils.prompt_management.prompt_ab_testing import PromptABTesting
        return PromptABTesting(tests_dir=temp_dir)
    
    def test_create_test(self, ab_testing):
        """Test creating an A/B test."""
        variant_a = {"prompt_text": "Analyze data."}
        variant_b = {"prompt_text": "Analyze data thoroughly."}
        
        test_id = ab_testing.create_test(
            name="Test A/B Test",
            description="Testing prompt variants",
            test_type=TestType.PROMPT_VARIATION,
            variant_a=variant_a,
            variant_b=variant_b,
            traffic_split=0.5,
            sample_size=100
        )
        
        assert test_id is not None
        
        test = ab_testing.get_test(test_id)
        assert test is not None
        assert test.name == "Test A/B Test"
        assert test.test_type == TestType.PROMPT_VARIATION
        assert test.status == TestStatus.DRAFT
        assert test.traffic_split == 0.5
        assert test.sample_size == 100
    
    def test_start_and_complete_test(self, ab_testing):
        """Test starting and completing a test."""
        # Create test
        test_id = ab_testing.create_test(
            name="Test Test",
            description="Test description",
            test_type=TestType.PROMPT_VARIATION,
            variant_a={"prompt": "A"},
            variant_b={"prompt": "B"}
        )
        
        # Start test
        success = ab_testing.start_test(test_id)
        assert success is True
        
        test = ab_testing.get_test(test_id)
        assert test.status == TestStatus.RUNNING
        assert test.started_at is not None
        
        # Complete test
        success = ab_testing.complete_test(test_id)
        assert success is True
        
        test = ab_testing.get_test(test_id)
        assert test.status == TestStatus.COMPLETED
        assert test.completed_at is not None
    
    def test_assign_variant(self, ab_testing):
        """Test variant assignment."""
        # Create and start test
        test_id = ab_testing.create_test(
            name="Variant Test",
            description="Test variant assignment",
            test_type=TestType.PROMPT_VARIATION,
            variant_a={"prompt": "A"},
            variant_b={"prompt": "B"}
        )
        ab_testing.start_test(test_id)
        
        # Test random assignment
        variant = ab_testing.assign_variant(test_id)
        assert variant in ['A', 'B']
        
        # Test consistent assignment with user_id
        variant1 = ab_testing.assign_variant(test_id, user_id="user123")
        variant2 = ab_testing.assign_variant(test_id, user_id="user123")
        assert variant1 == variant2  # Should be consistent
    
    def test_record_result(self, ab_testing):
        """Test recording test results."""
        # Create and start test
        test_id = ab_testing.create_test(
            name="Result Test",
            description="Test result recording",
            test_type=TestType.PROMPT_VARIATION,
            variant_a={"prompt": "A"},
            variant_b={"prompt": "B"}
        )
        ab_testing.start_test(test_id)
        
        # Record result
        result_id = ab_testing.record_result(
            test_id=test_id,
            variant="A",
            prompt_id="prompt_123",
            execution_time=1.0,
            token_count=50,
            response_quality=0.8,
            success=True,
            user_satisfaction=0.9
        )
        
        assert result_id is not None
        
        # Verify result was recorded
        results = ab_testing.get_test_results(test_id)
        assert len(results) == 1
        
        result = results[0]
        assert result.test_id == test_id
        assert result.variant == "A"
        assert result.execution_time == 1.0
        assert result.response_quality == 0.8
    
    def test_get_test_summary(self, ab_testing):
        """Test getting test summary."""
        # Create and start test
        test_id = ab_testing.create_test(
            name="Summary Test",
            description="Test summary",
            test_type=TestType.PROMPT_VARIATION,
            variant_a={"prompt": "A"},
            variant_b={"prompt": "B"},
            sample_size=10
        )
        ab_testing.start_test(test_id)
        
        # Record some results
        for i in range(5):
            ab_testing.record_result(
                test_id=test_id,
                variant="A",
                prompt_id=f"prompt_{i}",
                execution_time=1.0,
                token_count=50,
                response_quality=0.8,
                success=True
            )
        
        for i in range(3):
            ab_testing.record_result(
                test_id=test_id,
                variant="B",
                prompt_id=f"prompt_{i+5}",
                execution_time=1.2,
                token_count=60,
                response_quality=0.9,
                success=True
            )
        
        # Get summary
        summary = ab_testing.get_test_summary(test_id)
        
        assert summary['test_id'] == test_id
        assert summary['total_results'] == 8
        assert summary['variant_a_results'] == 5
        assert summary['variant_b_results'] == 3
        assert summary['completion_percentage'] == 80.0  # 8/10 * 100
        
        # Verify stats
        assert 'variant_a_stats' in summary
        assert 'variant_b_stats' in summary
        assert summary['variant_a_stats']['avg_execution_time'] == 1.0
        assert summary['variant_b_stats']['avg_execution_time'] == 1.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
