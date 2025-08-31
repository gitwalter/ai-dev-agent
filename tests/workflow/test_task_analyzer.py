#!/usr/bin/env python3
"""
Comprehensive tests for the TaskAnalyzer component.
Tests natural language task analysis and workflow requirement determination.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from workflow.composition.task_analyzer import TaskAnalyzer
from workflow.models.workflow_models import TaskAnalysis, Entity, ComplexityLevel


class TestTaskAnalyzer:
    """Test suite for TaskAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TaskAnalyzer()
    
    def test_initialization(self):
        """Test TaskAnalyzer initialization."""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'context_patterns')
        assert hasattr(self.analyzer, 'entity_patterns')
        assert hasattr(self.analyzer, 'complexity_indicators')
        assert hasattr(self.analyzer, 'duration_estimates')
    
    def test_analyze_simple_task(self):
        """Test analysis of a simple task."""
        task_description = "Fix the login bug in the authentication system"
        
        result = self.analyzer.analyze_task(task_description)
        
        assert isinstance(result, TaskAnalysis)
        assert result.description == task_description
        assert result.complexity == ComplexityLevel.SIMPLE
        assert '@debug' in result.required_contexts
        assert '@test' in result.required_contexts
        assert result.confidence > 0.5
        assert result.estimated_duration > 0
    
    def test_analyze_complex_task(self):
        """Test analysis of a complex task."""
        task_description = ("Implement a distributed microservices architecture "
                          "with advanced security features, performance optimization, "
                          "and comprehensive monitoring for the enterprise system")
        
        result = self.analyzer.analyze_task(task_description)
        
        assert result.complexity == ComplexityLevel.COMPLEX
        assert '@design' in result.required_contexts
        assert '@code' in result.required_contexts
        assert '@security' in result.required_contexts
        assert '@optimize' in result.required_contexts
        assert result.estimated_duration > 120  # Should be longer for complex tasks
    
    def test_analyze_feature_development_task(self):
        """Test analysis of a feature development task."""
        task_description = "Create a new user registration feature with email verification"
        
        result = self.analyzer.analyze_task(task_description)
        
        assert '@agile' in result.required_contexts
        assert '@design' in result.required_contexts
        assert '@code' in result.required_contexts
        assert '@test' in result.required_contexts
        assert '@git' in result.required_contexts
        
        # Should have feature-related entities
        feature_entities = [e for e in result.entities if e.type == 'feature']
        assert len(feature_entities) > 0
    
    def test_extract_entities_bug_task(self):
        """Test entity extraction for bug-related tasks."""
        task_description = "Fix critical security vulnerability in payment processing API"
        
        entities = self.analyzer.extract_entities(task_description)
        
        # Should extract bug, security, and API entities
        entity_types = {e.type for e in entities}
        assert 'bug' in entity_types or 'security' in entity_types
        assert any('payment' in e.name.lower() for e in entities)
        
        # All entities should have confidence scores
        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0
    
    def test_extract_entities_feature_task(self):
        """Test entity extraction for feature development tasks."""
        task_description = "Implement user dashboard with analytics charts and data export"
        
        entities = self.analyzer.extract_entities(task_description)
        
        # Should extract feature and UI entities
        entity_types = {e.type for e in entities}
        assert 'feature' in entity_types or 'ui' in entity_types
        
        # Should find dashboard-related entities
        entity_names = [e.name.lower() for e in entities]
        assert any('dashboard' in name for name in entity_names)
    
    def test_assess_complexity_simple(self):
        """Test complexity assessment for simple tasks."""
        entities = [
            Entity(name="login bug", type="bug", confidence=0.8),
            Entity(name="authentication", type="component", confidence=0.7)
        ]
        task_description = "Fix login bug"
        
        complexity = self.analyzer.assess_complexity(entities, task_description, {})
        
        assert complexity == ComplexityLevel.SIMPLE
    
    def test_assess_complexity_medium(self):
        """Test complexity assessment for medium tasks."""
        entities = [
            Entity(name="user registration", type="feature", confidence=0.9),
            Entity(name="email service", type="service", confidence=0.8),
            Entity(name="database", type="database", confidence=0.7)
        ]
        task_description = "Create user registration feature with email verification"
        
        complexity = self.analyzer.assess_complexity(entities, task_description, {})
        
        assert complexity in [ComplexityLevel.SIMPLE, ComplexityLevel.MEDIUM]
    
    def test_assess_complexity_complex(self):
        """Test complexity assessment for complex tasks."""
        entities = [
            Entity(name="microservices", type="architecture", confidence=0.9),
            Entity(name="distributed system", type="system", confidence=0.8),
            Entity(name="security", type="security", confidence=0.9),
            Entity(name="performance", type="performance", confidence=0.8)
        ]
        task_description = "Design complex distributed microservices architecture with advanced security"
        
        complexity = self.analyzer.assess_complexity(entities, task_description, {})
        
        assert complexity == ComplexityLevel.COMPLEX
    
    def test_identify_contexts_bug_fix(self):
        """Test context identification for bug fix tasks."""
        entities = [Entity(name="login bug", type="bug", confidence=0.8)]
        task_description = "Fix the login bug"
        
        contexts = self.analyzer.identify_contexts(entities, task_description, ComplexityLevel.SIMPLE)
        
        assert '@debug' in contexts
        assert '@test' in contexts
        assert '@code' in contexts
        assert '@git' in contexts
    
    def test_identify_contexts_feature_development(self):
        """Test context identification for feature development."""
        entities = [Entity(name="user dashboard", type="feature", confidence=0.9)]
        task_description = "Implement user dashboard feature"
        
        contexts = self.analyzer.identify_contexts(entities, task_description, ComplexityLevel.MEDIUM)
        
        assert '@agile' in contexts
        assert '@design' in contexts
        assert '@code' in contexts
        assert '@test' in contexts
        assert '@git' in contexts
    
    def test_identify_contexts_security_task(self):
        """Test context identification for security tasks."""
        entities = [Entity(name="security audit", type="security", confidence=0.9)]
        task_description = "Perform security audit of the authentication system"
        
        contexts = self.analyzer.identify_contexts(entities, task_description, ComplexityLevel.MEDIUM)
        
        assert '@security' in contexts
        assert '@code' in contexts
        assert '@test' in contexts
    
    def test_estimate_duration_simple_task(self):
        """Test duration estimation for simple tasks."""
        complexity = ComplexityLevel.SIMPLE
        contexts = ['@debug', '@test', '@code']
        entities = [Entity(name="bug", type="bug", confidence=0.8)]
        
        duration = self.analyzer.estimate_duration(complexity, contexts, entities)
        
        assert duration >= 5  # Minimum duration
        assert duration <= 120  # Should be reasonable for simple task
        assert duration % 5 == 0  # Should be rounded to 5-minute intervals
    
    def test_estimate_duration_complex_task(self):
        """Test duration estimation for complex tasks."""
        complexity = ComplexityLevel.COMPLEX
        contexts = ['@agile', '@design', '@code', '@test', '@security', '@docs', '@git']
        entities = [
            Entity(name="architecture", type="architecture", confidence=0.9),
            Entity(name="security", type="security", confidence=0.8),
            Entity(name="performance", type="performance", confidence=0.8)
        ]
        
        duration = self.analyzer.estimate_duration(complexity, contexts, entities)
        
        assert duration >= 120  # Should be longer for complex tasks
        assert duration % 5 == 0  # Should be rounded to 5-minute intervals
    
    def test_identify_dependencies(self):
        """Test dependency identification."""
        entities = [Entity(name="user service", type="prerequisite", confidence=0.8)]
        task_description = "Implement payment feature that depends on user authentication service"
        
        dependencies = self.analyzer.identify_dependencies(entities, task_description)
        
        assert len(dependencies) > 0
        assert any('authentication' in dep.lower() for dep in dependencies)
    
    def test_generate_success_criteria_feature(self):
        """Test success criteria generation for features."""
        entities = [Entity(name="user registration", type="feature", confidence=0.9)]
        task_description = "Implement user registration feature"
        
        criteria = self.analyzer.generate_success_criteria(entities, task_description)
        
        assert len(criteria) > 0
        assert any('feature' in criterion.lower() for criterion in criteria)
        assert any('test' in criterion.lower() for criterion in criteria)
    
    def test_generate_success_criteria_bug(self):
        """Test success criteria generation for bugs."""
        entities = [Entity(name="login bug", type="bug", confidence=0.8)]
        task_description = "Fix login bug"
        
        criteria = self.analyzer.generate_success_criteria(entities, task_description)
        
        assert len(criteria) > 0
        assert any('bug' in criterion.lower() for criterion in criteria)
        assert any('fix' in criterion.lower() for criterion in criteria)
    
    def test_generate_success_criteria_security(self):
        """Test success criteria generation for security tasks."""
        entities = [Entity(name="security vulnerability", type="security", confidence=0.9)]
        task_description = "Fix security vulnerability in API"
        
        criteria = self.analyzer.generate_success_criteria(entities, task_description)
        
        assert len(criteria) > 0
        assert any('security' in criterion.lower() for criterion in criteria)
        assert any('vulnerability' in criterion.lower() for criterion in criteria)
    
    def test_task_id_generation(self):
        """Test unique task ID generation."""
        task_description = "Test task for ID generation"
        
        result1 = self.analyzer.analyze_task(task_description)
        result2 = self.analyzer.analyze_task(task_description)
        
        # Task IDs should be unique even for same description
        assert result1.task_id != result2.task_id
        assert result1.task_id.startswith('task_')
        assert result2.task_id.startswith('task_')
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # High confidence task with clear entities and contexts
        high_confidence_task = "Fix critical login bug in authentication system"
        result1 = self.analyzer.analyze_task(high_confidence_task)
        
        # Low confidence task with vague description
        low_confidence_task = "Do something with the system"
        result2 = self.analyzer.analyze_task(low_confidence_task)
        
        assert result1.confidence > result2.confidence
        assert 0.0 <= result1.confidence <= 1.0
        assert 0.0 <= result2.confidence <= 1.0
    
    def test_context_with_project_info(self):
        """Test analysis with additional project context."""
        task_description = "Implement new feature"
        context = {
            "project_size": "large",
            "team_experience": "junior"
        }
        
        result = self.analyzer.analyze_task(task_description, context)
        
        # Should adjust complexity based on context
        assert result.complexity is not None
        assert result.estimated_duration > 0
    
    def test_empty_task_description(self):
        """Test handling of empty task description."""
        task_description = ""
        
        result = self.analyzer.analyze_task(task_description)
        
        assert result.description == ""
        assert len(result.entities) == 0
        assert len(result.required_contexts) > 0  # Should have at least @code
        assert result.confidence < 0.5  # Should have low confidence
    
    def test_very_long_task_description(self):
        """Test handling of very long task descriptions."""
        task_description = "Implement " + "very complex " * 100 + "feature with many requirements"
        
        result = self.analyzer.analyze_task(task_description)
        
        assert result.description == task_description
        assert len(result.entities) <= 20  # Should limit entities
        assert result.complexity == ComplexityLevel.COMPLEX
    
    def test_special_characters_in_task(self):
        """Test handling of special characters in task description."""
        task_description = "Fix bug in API endpoint /api/users/{id} with 404 error"
        
        result = self.analyzer.analyze_task(task_description)
        
        assert result.description == task_description
        assert '@debug' in result.required_contexts
        assert len(result.entities) > 0
    
    def test_multiple_entity_types(self):
        """Test extraction of multiple entity types from complex description."""
        task_description = ("Implement secure payment API with performance optimization, "
                          "comprehensive testing, and detailed documentation")
        
        result = self.analyzer.analyze_task(task_description)
        
        entity_types = {e.type for e in result.entities}
        assert len(entity_types) > 1  # Should extract multiple types
        
        # Should identify multiple contexts
        assert '@code' in result.required_contexts
        assert '@security' in result.required_contexts
        assert '@test' in result.required_contexts
        assert '@docs' in result.required_contexts
    
    @pytest.mark.parametrize("task_description,expected_contexts", [
        ("Fix login bug", ["@debug", "@test", "@code", "@git"]),
        ("Create user dashboard", ["@agile", "@design", "@code", "@test", "@git"]),
        ("Security audit", ["@security", "@code", "@test", "@git"]),
        ("Optimize database performance", ["@optimize", "@test", "@code", "@git"]),
        ("Write API documentation", ["@docs", "@git"]),
    ])
    def test_context_identification_patterns(self, task_description, expected_contexts):
        """Test context identification for various task patterns."""
        result = self.analyzer.analyze_task(task_description)
        
        for context in expected_contexts:
            assert context in result.required_contexts, f"Expected {context} for task: {task_description}"
    
    def test_entity_confidence_scoring(self):
        """Test entity confidence scoring accuracy."""
        task_description = "Fix critical authentication bug in login system"
        
        entities = self.analyzer.extract_entities(task_description)
        
        # Should have high confidence for clear entities
        auth_entities = [e for e in entities if 'auth' in e.name.lower()]
        if auth_entities:
            assert auth_entities[0].confidence > 0.6
        
        bug_entities = [e for e in entities if e.type == 'bug']
        if bug_entities:
            assert bug_entities[0].confidence > 0.6
