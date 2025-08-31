#!/usr/bin/env python3
"""
Comprehensive tests for the WorkflowComposer component.
Tests workflow composition, template selection, and optimization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import yaml

from workflow.composition.workflow_composer import WorkflowComposer
from workflow.models.workflow_models import (
    TaskAnalysis, WorkflowDefinition, WorkflowTemplate, WorkflowPhase,
    Entity, ComplexityLevel, ValidationResult
)


class TestWorkflowComposer:
    """Test suite for WorkflowComposer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.composer = WorkflowComposer(template_directory=self.temp_dir)
        
        # Create sample task analysis
        self.sample_analysis = TaskAnalysis(
            task_id="test_task_001",
            description="Implement user authentication feature",
            entities=[
                Entity(name="authentication", type="feature", confidence=0.9),
                Entity(name="user login", type="component", confidence=0.8)
            ],
            complexity=ComplexityLevel.MEDIUM,
            required_contexts=["@agile", "@design", "@code", "@test", "@git"],
            estimated_duration=120,
            dependencies=["user_service"],
            success_criteria=["Feature works", "Tests pass"],
            confidence=0.85
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test WorkflowComposer initialization."""
        assert self.composer is not None
        assert hasattr(self.composer, 'templates')
        assert hasattr(self.composer, 'context_capabilities')
        assert hasattr(self.composer, 'optimization_rules')
    
    def test_compose_workflow_without_template(self):
        """Test workflow composition without matching template."""
        workflow = self.composer.compose_workflow(self.sample_analysis)
        
        assert isinstance(workflow, WorkflowDefinition)
        assert workflow.workflow_id.startswith("workflow_")
        assert len(workflow.phases) > 0
        assert workflow.estimated_duration > 0
        
        # Should have phases for required contexts
        phase_contexts = {phase.context for phase in workflow.phases}
        for context in self.sample_analysis.required_contexts:
            assert context in phase_contexts
    
    def test_compose_workflow_with_template(self):
        """Test workflow composition with matching template."""
        # Create a test template
        self._create_test_template("feature_development")
        self.composer._load_templates()
        
        workflow = self.composer.compose_workflow(self.sample_analysis)
        
        assert isinstance(workflow, WorkflowDefinition)
        assert "template_used" in workflow.metadata
        assert workflow.metadata["template_used"] == "feature_development"
    
    def test_select_template_good_match(self):
        """Test template selection with good match."""
        # Create templates
        self._create_test_template("feature_development", category="development")
        self._create_test_template("bug_fix", category="maintenance")
        self.composer._load_templates()
        
        # Analysis for feature development
        feature_analysis = TaskAnalysis(
            task_id="feature_001",
            description="Create new feature",
            entities=[Entity(name="feature", type="feature", confidence=0.9)],
            complexity=ComplexityLevel.MEDIUM,
            required_contexts=["@agile", "@code", "@test"],
            estimated_duration=120,
            dependencies=[],
            success_criteria=["Feature complete"],
            confidence=0.8
        )
        
        template = self.composer.select_template(feature_analysis)
        
        assert template is not None
        assert template.name == "feature_development"
    
    def test_select_template_no_match(self):
        """Test template selection with no good match."""
        # Create template that doesn't match
        self._create_test_template("specialized_template", category="specialized")
        self.composer._load_templates()
        
        template = self.composer.select_template(self.sample_analysis)
        
        # Should return None if no good match (score < 0.6)
        assert template is None or template.name != "specialized_template"
    
    def test_customize_workflow_add_missing_contexts(self):
        """Test workflow customization adds missing contexts."""
        # Create template with limited contexts
        template = WorkflowTemplate(
            template_id="limited_template",
            name="Limited Template",
            description="Template with limited contexts",
            category="test",
            phases=[
                WorkflowPhase(
                    phase_id="phase_1",
                    context="@code",
                    name="Code Phase",
                    description="Coding phase",
                    inputs=["requirements"],
                    outputs=["code"]
                )
            ]
        )
        
        workflow = self.composer.customize_workflow(template, self.sample_analysis)
        
        # Should add missing contexts from analysis
        phase_contexts = {phase.context for phase in workflow.phases}
        for context in self.sample_analysis.required_contexts:
            assert context in phase_contexts
    
    def test_create_custom_workflow(self):
        """Test creation of custom workflow from scratch."""
        workflow = self.composer.create_custom_workflow(self.sample_analysis)
        
        assert isinstance(workflow, WorkflowDefinition)
        assert workflow.metadata.get("custom_workflow") is True
        assert len(workflow.phases) == len(self.sample_analysis.required_contexts)
        
        # Should have phases for all required contexts
        phase_contexts = {phase.context for phase in workflow.phases}
        assert phase_contexts == set(self.sample_analysis.required_contexts)
    
    def test_optimize_sequence_logical_order(self):
        """Test sequence optimization maintains logical order."""
        # Create workflow with phases in wrong order
        workflow = WorkflowDefinition(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test workflow for optimization",
            phases=[
                WorkflowPhase(phase_id="git", context="@git", name="Git", description="Deploy", inputs=[], outputs=[]),
                WorkflowPhase(phase_id="code", context="@code", name="Code", description="Implement", inputs=[], outputs=[]),
                WorkflowPhase(phase_id="agile", context="@agile", name="Agile", description="Plan", inputs=[], outputs=[]),
                WorkflowPhase(phase_id="test", context="@test", name="Test", description="Test", inputs=[], outputs=[])
            ],
            dependencies={},
            estimated_duration=120
        )
        
        optimized = self.composer.optimize_sequence(workflow)
        
        # Should reorder phases logically
        contexts = [phase.context for phase in optimized.phases]
        
        # @agile should come before @code
        agile_index = contexts.index("@agile") if "@agile" in contexts else -1
        code_index = contexts.index("@code") if "@code" in contexts else -1
        if agile_index >= 0 and code_index >= 0:
            assert agile_index < code_index
        
        # @code should come before @test
        test_index = contexts.index("@test") if "@test" in contexts else -1
        if code_index >= 0 and test_index >= 0:
            assert code_index < test_index
        
        # @git should come last
        git_index = contexts.index("@git") if "@git" in contexts else -1
        if git_index >= 0:
            assert git_index == len(contexts) - 1
    
    def test_validate_workflow_valid(self):
        """Test workflow validation for valid workflow."""
        workflow = self.composer.create_custom_workflow(self.sample_analysis)
        
        validation = self.composer.validate_workflow(workflow)
        
        assert isinstance(validation, ValidationResult)
        assert validation.passed is True
        assert validation.score >= 0.7
    
    def test_validate_workflow_invalid_context(self):
        """Test workflow validation with invalid context."""
        workflow = WorkflowDefinition(
            workflow_id="invalid_workflow",
            name="Invalid Workflow",
            description="Workflow with invalid context",
            phases=[
                WorkflowPhase(
                    phase_id="invalid_phase",
                    context="@invalid",  # Invalid context
                    name="Invalid Phase",
                    description="Phase with invalid context",
                    inputs=[],
                    outputs=[]
                )
            ],
            dependencies={},
            estimated_duration=60
        )
        
        validation = self.composer.validate_workflow(workflow)
        
        assert validation.passed is False
        assert any("invalid context" in msg.lower() for msg in validation.messages)
    
    def test_validate_workflow_empty_phases(self):
        """Test workflow validation with no phases."""
        workflow = WorkflowDefinition(
            workflow_id="empty_workflow",
            name="Empty Workflow",
            description="Workflow with no phases",
            phases=[],  # No phases
            dependencies={},
            estimated_duration=0
        )
        
        validation = self.composer.validate_workflow(workflow)
        
        assert validation.passed is False
        assert validation.score == 0.0
    
    def test_create_context_phase(self):
        """Test creation of context-specific phases."""
        phase = self.composer._create_context_phase("@code", self.sample_analysis, "test_workflow", 0)
        
        assert isinstance(phase, WorkflowPhase)
        assert phase.context == "@code"
        assert phase.name == "Implementation"
        assert len(phase.inputs) > 0
        assert len(phase.outputs) > 0
        assert phase.timeout > 0
    
    def test_get_context_timeout_complexity_adjustment(self):
        """Test context timeout adjustment based on complexity."""
        simple_timeout = self.composer._get_context_timeout("@code", ComplexityLevel.SIMPLE)
        medium_timeout = self.composer._get_context_timeout("@code", ComplexityLevel.MEDIUM)
        complex_timeout = self.composer._get_context_timeout("@code", ComplexityLevel.COMPLEX)
        
        assert simple_timeout < medium_timeout < complex_timeout
    
    def test_build_phase_dependencies(self):
        """Test building phase dependencies."""
        phases = [
            WorkflowPhase(phase_id="agile", context="@agile", name="Agile", description="Plan", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="design", context="@design", name="Design", description="Design", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="code", context="@code", name="Code", description="Code", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="test", context="@test", name="Test", description="Test", inputs=[], outputs=[])
        ]
        
        dependencies = self.composer._build_phase_dependencies(phases, self.sample_analysis)
        
        # Should have logical dependencies
        assert "design" in dependencies
        assert "agile" in dependencies["design"]  # Design depends on agile
        
        assert "code" in dependencies
        assert "design" in dependencies["code"]  # Code depends on design
    
    def test_estimate_workflow_duration(self):
        """Test workflow duration estimation."""
        phases = [
            WorkflowPhase(phase_id="p1", context="@code", name="P1", description="", inputs=[], outputs=[], timeout=600),
            WorkflowPhase(phase_id="p2", context="@test", name="P2", description="", inputs=[], outputs=[], timeout=300)
        ]
        
        duration = self.composer._estimate_workflow_duration(phases, ComplexityLevel.MEDIUM)
        
        assert duration >= 15  # Minimum duration
        assert isinstance(duration, int)
    
    def test_load_templates_from_directory(self):
        """Test loading templates from directory."""
        # Create test templates
        self._create_test_template("template1")
        self._create_test_template("template2")
        
        # Load templates
        self.composer._load_templates()
        
        assert len(self.composer.templates) >= 2
        assert "template1" in self.composer.templates
        assert "template2" in self.composer.templates
    
    def test_load_invalid_template_file(self):
        """Test handling of invalid template files."""
        # Create invalid YAML file
        invalid_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # Should not crash on invalid file
        self.composer._load_templates()
        
        # Should not load invalid template
        assert "invalid" not in self.composer.templates
    
    def test_template_score_calculation(self):
        """Test template scoring calculation."""
        template = WorkflowTemplate(
            template_id="test_template",
            name="Test Template",
            description="Test template",
            category="development",
            phases=[
                WorkflowPhase(phase_id="p1", context="@agile", name="P1", description="", inputs=[], outputs=[]),
                WorkflowPhase(phase_id="p2", context="@code", name="P2", description="", inputs=[], outputs=[])
            ]
        )
        
        score = self.composer._calculate_template_score(template, self.sample_analysis)
        
        assert 0.0 <= score <= 1.0
        # Should have positive score for matching contexts
        assert score > 0.0
    
    def test_optimization_rules_application(self):
        """Test application of optimization rules."""
        phases = [
            WorkflowPhase(phase_id="git", context="@git", name="Git", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="code", context="@code", name="Code", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="agile", context="@agile", name="Agile", description="", inputs=[], outputs=[])
        ]
        
        optimized = self.composer._apply_optimization_rules(phases)
        
        # Should reorder according to rules
        contexts = [phase.context for phase in optimized]
        
        # @agile should be first if present
        if "@agile" in contexts:
            assert contexts[0] == "@agile"
        
        # @git should be last if present
        if "@git" in contexts:
            assert contexts[-1] == "@git"
    
    def test_parallel_group_identification(self):
        """Test identification of parallel execution groups."""
        phases = [
            WorkflowPhase(phase_id="test", context="@test", name="Test", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="docs", context="@docs", name="Docs", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="security", context="@security", name="Security", description="", inputs=[], outputs=[])
        ]
        
        result = self.composer._identify_parallel_groups(phases, {})
        
        # Should identify parallel groups for compatible contexts
        parallel_phases = [p for p in result if hasattr(p, 'parallel_group') and p.parallel_group]
        assert len(parallel_phases) > 0
    
    def test_workflow_connectivity_check(self):
        """Test workflow connectivity validation."""
        # Connected workflow
        connected_workflow = WorkflowDefinition(
            workflow_id="connected",
            name="Connected",
            description="Connected workflow",
            phases=[
                WorkflowPhase(phase_id="p1", context="@agile", name="P1", description="", inputs=[], outputs=[]),
                WorkflowPhase(phase_id="p2", context="@code", name="P2", description="", inputs=[], outputs=[])
            ],
            dependencies={"p2": ["p1"]},
            estimated_duration=60
        )
        
        assert self.composer._is_workflow_connected(connected_workflow) is True
        
        # Single phase workflow (always connected)
        single_phase_workflow = WorkflowDefinition(
            workflow_id="single",
            name="Single",
            description="Single phase workflow",
            phases=[
                WorkflowPhase(phase_id="p1", context="@code", name="P1", description="", inputs=[], outputs=[])
            ],
            dependencies={},
            estimated_duration=30
        )
        
        assert self.composer._is_workflow_connected(single_phase_workflow) is True
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        # No circular dependencies
        no_cycle = {"A": ["B"], "B": ["C"], "C": []}
        assert self.composer._has_circular_dependencies(no_cycle) is False
        
        # Circular dependencies
        cycle = {"A": ["B"], "B": ["C"], "C": ["A"]}
        assert self.composer._has_circular_dependencies(cycle) is True
        
        # Self-dependency
        self_cycle = {"A": ["A"]}
        assert self.composer._has_circular_dependencies(self_cycle) is True
    
    def test_fix_validation_issues(self):
        """Test automatic fixing of validation issues."""
        # Workflow missing @git phase
        workflow = WorkflowDefinition(
            workflow_id="incomplete",
            name="Incomplete",
            description="Workflow missing deployment",
            phases=[
                WorkflowPhase(phase_id="code", context="@code", name="Code", description="", inputs=[], outputs=[])
            ],
            dependencies={},
            estimated_duration=60
        )
        
        validation = ValidationResult(
            passed=False,
            score=0.6,
            messages=["missing deployment phase"],
            details={}
        )
        
        fixed = self.composer._fix_validation_issues(workflow, validation)
        
        # Should add missing @git phase
        contexts = {phase.context for phase in fixed.phases}
        assert "@git" in contexts
    
    def _create_test_template(self, name, category="test"):
        """Helper method to create test template files."""
        template_data = {
            "name": name,
            "description": f"Test template {name}",
            "category": category,
            "contexts": [
                {
                    "context": "@agile",
                    "phase": "planning",
                    "name": "Planning Phase",
                    "description": "Planning and requirements",
                    "inputs": ["requirements"],
                    "outputs": ["user_stories"]
                },
                {
                    "context": "@code",
                    "phase": "implementation",
                    "name": "Implementation Phase",
                    "description": "Code implementation",
                    "inputs": ["user_stories"],
                    "outputs": ["source_code"]
                }
            ]
        }
        
        template_file = os.path.join(self.temp_dir, f"{name}.yaml")
        with open(template_file, 'w') as f:
            yaml.dump(template_data, f)
    
    @pytest.mark.parametrize("complexity,expected_min_duration", [
        (ComplexityLevel.SIMPLE, 15),
        (ComplexityLevel.MEDIUM, 30),
        (ComplexityLevel.COMPLEX, 60)
    ])
    def test_duration_estimation_by_complexity(self, complexity, expected_min_duration):
        """Test duration estimation varies by complexity."""
        phases = [
            WorkflowPhase(phase_id="p1", context="@code", name="P1", description="", inputs=[], outputs=[], timeout=600)
        ]
        
        duration = self.composer._estimate_workflow_duration(phases, complexity)
        
        assert duration >= expected_min_duration
    
    def test_quality_gates_generation(self):
        """Test quality gates generation based on analysis."""
        gates = self.composer._get_quality_gates(self.sample_analysis)
        
        assert isinstance(gates, list)
        assert len(gates) > 0
        assert "basic_validation" in gates
        
        # Should include complexity-based gates
        if self.sample_analysis.complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.COMPLEX]:
            assert "comprehensive_testing" in gates
    
    def test_phase_ordering_logic(self):
        """Test logical phase ordering."""
        phases = [
            WorkflowPhase(phase_id="git", context="@git", name="Git", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="test", context="@test", name="Test", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="code", context="@code", name="Code", description="", inputs=[], outputs=[]),
            WorkflowPhase(phase_id="agile", context="@agile", name="Agile", description="", inputs=[], outputs=[])
        ]
        
        ordered = self.composer._order_phases_logically(phases)
        
        contexts = [phase.context for phase in ordered]
        
        # Should follow logical order
        expected_order = ["@agile", "@code", "@test", "@git"]
        for i, context in enumerate(expected_order):
            if context in contexts:
                actual_index = contexts.index(context)
                for j in range(i):
                    if expected_order[j] in contexts:
                        prev_index = contexts.index(expected_order[j])
                        assert prev_index < actual_index, f"{expected_order[j]} should come before {context}"
