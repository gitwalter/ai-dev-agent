"""
Test Context-Sensitive Rule System
==================================

Comprehensive tests for the integrated context detection and rule activation system.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from utils.rule_system.context_specific_rule_detector import (
    ContextSpecificRuleDetector,
    DevelopmentContext,
    ContextDetectionResult
)
from utils.rule_system.language_layer_activator import (
    LanguageLayerActivator,
    LanguageLayer,
    LayerActivationContext,
    LayerActivationResult
)
from utils.rule_system.integrated_context_system import (
    IntegratedContextSystem,
    IntegratedContextResult
)


class TestContextSpecificRuleDetector:
    """Test the context-specific rule detector."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ContextSpecificRuleDetector()
    
    def test_agile_context_detection(self):
        """Test detection of agile development context."""
        result = self.detector.detect_context(
            current_files=["docs/agile/sprints/sprint_1/user_stories/US-036.md"],
            user_input="Let's update our sprint planning and review user story progress",
            recent_commands=["git add docs/agile/", "git commit -m 'Update user stories'"]
        )
        
        assert result.primary_context == DevelopmentContext.AGILE_DEVELOPMENT
        assert result.confidence_score > 0.7
        assert "agile/agile_development_rule" in result.recommended_rules
        assert "agile" in result.reasoning.lower()
    
    def test_coding_context_detection(self):
        """Test detection of code development context."""
        result = self.detector.detect_context(
            current_files=["src/main.py", "utils/helper.py"],
            user_input="Let's implement the new feature and add proper error handling",
            recent_commands=["python -m pytest", "python main.py"]
        )
        
        assert result.primary_context == DevelopmentContext.CODE_DEVELOPMENT
        assert result.confidence_score > 0.6
        assert "development/development_core_principles_rule" in result.recommended_rules
    
    def test_testing_context_detection(self):
        """Test detection of testing context."""
        result = self.detector.detect_context(
            current_files=["tests/test_main.py", "tests/unit/test_helper.py"],
            user_input="Run the test suite and fix any failing tests",
            recent_commands=["pytest", "python -m pytest tests/"]
        )
        
        assert result.primary_context == DevelopmentContext.TESTING
        assert result.confidence_score > 0.8
        assert "testing/xp_test_first_development_rule" in result.recommended_rules
    
    def test_git_context_detection(self):
        """Test detection of git operations context."""
        result = self.detector.detect_context(
            current_files=[],
            user_input="Let's commit our changes and push to main",
            recent_commands=["git status", "git add .", "git commit -m 'Feature complete'"]
        )
        
        assert result.primary_context == DevelopmentContext.GIT_OPERATIONS
        assert "git" in result.reasoning.lower()
    
    def test_mixed_context_detection(self):
        """Test detection with mixed signals."""
        result = self.detector.detect_context(
            current_files=["tests/test_agile.py", "docs/agile/README.md"],
            user_input="Let's test our agile implementation and document the process",
            recent_commands=["pytest tests/test_agile.py"]
        )
        
        # Should detect primary context with secondary contexts
        assert result.primary_context in [
            DevelopmentContext.TESTING, 
            DevelopmentContext.AGILE_DEVELOPMENT
        ]
        assert len(result.secondary_contexts) > 0
        assert result.confidence_score > 0.5


class TestLanguageLayerActivator:
    """Test the language layer activator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.activator = LanguageLayerActivator()
    
    def test_technical_layer_activation(self):
        """Test activation of technical language layer."""
        context = LayerActivationContext(
            task_type="implementation",
            audience="developers",
            artifact_type="code",
            communication_goal="technical_implementation",
            technical_depth=0.9,
            business_relevance=0.3,
            philosophical_relevance=0.1
        )
        
        result = self.activator.detect_optimal_layer(context)
        
        assert result.primary_layer == LanguageLayer.TECHNICAL
        assert result.confidence > 0.7
        assert "technical" in result.reasoning.lower()
    
    def test_business_layer_activation(self):
        """Test activation of business language layer."""
        context = LayerActivationContext(
            task_type="user_story_creation",
            audience="business_stakeholders",
            artifact_type="documentation",
            communication_goal="business_requirements",
            technical_depth=0.2,
            business_relevance=0.9,
            philosophical_relevance=0.3
        )
        
        result = self.activator.detect_optimal_layer(context)
        
        assert result.primary_layer == LanguageLayer.BUSINESS
        assert result.confidence > 0.6
        assert "business" in result.reasoning.lower()
    
    def test_documentation_layer_activation(self):
        """Test activation of documentation language layer."""
        context = LayerActivationContext(
            task_type="documentation",
            audience="mixed_audience",
            artifact_type="documentation",
            communication_goal="user_guidance",
            technical_depth=0.6,
            business_relevance=0.5,
            philosophical_relevance=0.2
        )
        
        result = self.activator.detect_optimal_layer(context)
        
        assert result.primary_layer == LanguageLayer.DOCUMENTATION
        assert result.confidence > 0.5
    
    def test_philosophical_layer_activation(self):
        """Test activation of philosophical language layer."""
        context = LayerActivationContext(
            task_type="architectural_decision",
            audience="technical_leads",
            artifact_type="architecture_document",
            communication_goal="system_design",
            technical_depth=0.8,
            business_relevance=0.6,
            philosophical_relevance=0.9
        )
        
        result = self.activator.detect_optimal_layer(context)
        
        # Should prefer technical or philosophical
        assert result.primary_layer in [LanguageLayer.TECHNICAL, LanguageLayer.PHILOSOPHICAL]
        assert result.confidence > 0.5


class TestIntegratedContextSystem:
    """Test the integrated context system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = IntegratedContextSystem()
    
    def test_agile_integration(self):
        """Test integrated context analysis for agile development."""
        result = self.system.analyze_integrated_context(
            current_files=["docs/agile/sprints/sprint_1/user_stories/US-036.md"],
            user_input="Let's review the sprint progress and update user story status",
            recent_commands=["git add docs/agile/"]
        )
        
        assert isinstance(result, IntegratedContextResult)
        assert result.context_detection.primary_context == DevelopmentContext.AGILE_DEVELOPMENT
        assert result.language_layer.primary_layer in [LanguageLayer.BUSINESS, LanguageLayer.DOCUMENTATION]
        assert result.integration_score > 0.5
        assert len(result.recommended_rules) > 0
    
    def test_coding_integration(self):
        """Test integrated context analysis for coding."""
        result = self.system.analyze_integrated_context(
            current_files=["src/main.py", "utils/database.py"],
            user_input="Implement the new database connection with error handling and logging",
            recent_commands=["python main.py", "python -m pytest"]
        )
        
        assert result.context_detection.primary_context == DevelopmentContext.CODE_DEVELOPMENT
        assert result.language_layer.primary_layer == LanguageLayer.TECHNICAL
        assert result.integration_score > 0.6
        
        # Should include technical rules
        technical_rules = [
            rule for rule in result.recommended_rules 
            if "development" in rule or "technical" in rule
        ]
        assert len(technical_rules) > 0
    
    def test_testing_integration(self):
        """Test integrated context analysis for testing."""
        result = self.system.analyze_integrated_context(
            current_files=["tests/test_database.py"],
            user_input="Run the test suite and fix any failing database tests",
            recent_commands=["pytest tests/", "python -m pytest --cov"]
        )
        
        assert result.context_detection.primary_context == DevelopmentContext.TESTING
        assert result.language_layer.primary_layer == LanguageLayer.TECHNICAL
        assert "testing" in [rule for rule in result.recommended_rules if "testing" in rule]
    
    def test_integration_score_calculation(self):
        """Test integration score calculation."""
        # High confidence, matching context and layer
        result = self.system.analyze_integrated_context(
            current_files=["src/api.py"],
            user_input="Implement REST API endpoints with proper error handling",
            recent_commands=["python api.py"]
        )
        
        # Should have high integration score for clear technical context
        assert result.integration_score > 0.7
    
    def test_optimization_suggestions(self):
        """Test generation of optimization suggestions."""
        # Ambiguous context should generate suggestions
        result = self.system.analyze_integrated_context(
            current_files=["file.txt"],
            user_input="do something",
            recent_commands=[]
        )
        
        # Should have suggestions for improvement
        assert len(result.optimization_suggestions) > 0
        assert any("context" in suggestion.lower() for suggestion in result.optimization_suggestions)
    
    @patch('subprocess.run')
    def test_git_integration(self, mock_run):
        """Test git status integration."""
        # Mock git status response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "M  src/main.py\nA  tests/test_new.py\n"
        mock_run.return_value = mock_result
        
        result = self.system.analyze_integrated_context(
            current_files=["src/main.py"],
            user_input="Let's commit our changes",
            recent_commands=["git add ."]
        )
        
        # Should detect git context
        assert result.context_detection.primary_context == DevelopmentContext.GIT_OPERATIONS
    
    def test_rule_deduplication(self):
        """Test that recommended rules are deduplicated."""
        result = self.system.analyze_integrated_context(
            current_files=["src/main.py", "tests/test_main.py"],
            user_input="Implement and test the new feature",
            recent_commands=["python main.py", "pytest"]
        )
        
        # Should not have duplicate rules
        rules = result.recommended_rules
        assert len(rules) == len(set(rules))


class TestContextSwitching:
    """Test context switching scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.system = IntegratedContextSystem()
    
    def test_context_transition(self):
        """Test smooth transition between contexts."""
        # Start with coding context
        coding_result = self.system.analyze_integrated_context(
            current_files=["src/feature.py"],
            user_input="Implement the new feature"
        )
        
        # Switch to testing context  
        testing_result = self.system.analyze_integrated_context(
            current_files=["tests/test_feature.py"],
            user_input="Write tests for the new feature"
        )
        
        # Switch to documentation context
        docs_result = self.system.analyze_integrated_context(
            current_files=["docs/feature_guide.md"],
            user_input="Document the new feature usage"
        )
        
        # Verify context transitions
        assert coding_result.context_detection.primary_context == DevelopmentContext.CODE_DEVELOPMENT
        assert testing_result.context_detection.primary_context == DevelopmentContext.TESTING
        assert docs_result.context_detection.primary_context == DevelopmentContext.DOCUMENTATION
        
        # Verify language layer adaptation
        assert coding_result.language_layer.primary_layer == LanguageLayer.TECHNICAL
        assert testing_result.language_layer.primary_layer == LanguageLayer.TECHNICAL
        assert docs_result.language_layer.primary_layer == LanguageLayer.DOCUMENTATION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
