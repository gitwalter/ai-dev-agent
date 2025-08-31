#!/usr/bin/env python3
"""
Workflow Composer for the Workflow Composition Engine.
Composes optimal workflows using available contexts and templates.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import yaml
import os

from workflow.models.workflow_models import (
    TaskAnalysis, WorkflowDefinition, WorkflowPhase, WorkflowTemplate,
    ValidationResult, ComplexityLevel
)

logger = logging.getLogger(__name__)


class WorkflowComposer:
    """
    Composes optimal workflows using available contexts and templates.
    
    This class handles:
    1. Template selection and customization
    2. Workflow sequence optimization
    3. Dependency resolution
    4. Quality gate integration
    """
    
    def __init__(self, template_directory: Optional[str] = None):
        """
        Initialize the workflow composer.
        
        Args:
            template_directory: Directory containing workflow templates
        """
        self.template_directory = template_directory or "workflow/templates"
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.context_capabilities = self._build_context_capabilities()
        self.optimization_rules = self._build_optimization_rules()
        
        # Load templates
        self._load_templates()
        
    def compose_workflow(self, analysis: TaskAnalysis) -> WorkflowDefinition:
        """
        Compose optimal workflow based on task analysis.
        
        Args:
            analysis: Task analysis results
            
        Returns:
            Complete workflow definition with context sequences
        """
        logger.info(f"Composing workflow for task: {analysis.task_id}")
        
        # Select best matching template
        template = self.select_template(analysis)
        
        if template:
            logger.info(f"Using template: {template.name}")
            workflow = self.customize_workflow(template, analysis)
        else:
            logger.info("No suitable template found, creating custom workflow")
            workflow = self.create_custom_workflow(analysis)
        
        # Optimize the workflow sequence
        workflow = self.optimize_sequence(workflow)
        
        # Validate the workflow
        validation = self.validate_workflow(workflow)
        if not validation.passed:
            logger.warning(f"Workflow validation issues: {validation.messages}")
            workflow = self._fix_validation_issues(workflow, validation)
        
        logger.info(f"Workflow composed: {len(workflow.phases)} phases, "
                   f"{workflow.estimated_duration}min estimated")
        
        return workflow
    
    def select_template(self, analysis: TaskAnalysis) -> Optional[WorkflowTemplate]:
        """
        Select best matching workflow template.
        
        Args:
            analysis: Task analysis results
            
        Returns:
            Best matching template or None if no good match
        """
        if not self.templates:
            return None
        
        best_template = None
        best_score = 0.0
        
        for template in self.templates.values():
            score = self._calculate_template_score(template, analysis)
            if score > best_score and score >= 0.6:  # Minimum match threshold
                best_score = score
                best_template = template
        
        if best_template:
            logger.info(f"Selected template '{best_template.name}' with score {best_score:.2f}")
        
        return best_template
    
    def customize_workflow(self, template: WorkflowTemplate, analysis: TaskAnalysis) -> WorkflowDefinition:
        """
        Customize template based on specific requirements.
        
        Args:
            template: Selected workflow template
            analysis: Task analysis results
            
        Returns:
            Customized workflow definition
        """
        workflow_id = f"workflow_{analysis.task_id}"
        
        # Start with template phases
        phases = []
        for template_phase in template.phases:
            phase = WorkflowPhase(
                phase_id=f"{workflow_id}_{template_phase.phase_id}",
                context=template_phase.context,
                name=template_phase.name,
                description=template_phase.description,
                inputs=template_phase.inputs.copy(),
                outputs=template_phase.outputs.copy(),
                condition=template_phase.condition,
                timeout=template_phase.timeout,
                retry_count=template_phase.retry_count,
                quality_gates=template_phase.quality_gates.copy()
            )
            phases.append(phase)
        
        # Add missing contexts from analysis
        required_contexts = set(analysis.required_contexts)
        template_contexts = {phase.context for phase in phases}
        missing_contexts = required_contexts - template_contexts
        
        for context in missing_contexts:
            phase = self._create_context_phase(context, analysis, workflow_id)
            phases.append(phase)
        
        # Remove unnecessary phases based on analysis
        phases = self._filter_unnecessary_phases(phases, analysis)
        
        # Build dependencies
        dependencies = self._build_phase_dependencies(phases, analysis)
        
        # Estimate duration
        estimated_duration = self._estimate_workflow_duration(phases, analysis.complexity)
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=f"Workflow for {analysis.description[:50]}...",
            description=f"Automated workflow for: {analysis.description}",
            phases=phases,
            dependencies=dependencies,
            estimated_duration=estimated_duration,
            quality_gates=self._get_quality_gates(analysis),
            metadata={
                "template_used": template.template_id,
                "task_analysis": analysis.dict(),
                "customization_applied": True
            }
        )
        
        return workflow
    
    def create_custom_workflow(self, analysis: TaskAnalysis) -> WorkflowDefinition:
        """
        Create custom workflow from scratch.
        
        Args:
            analysis: Task analysis results
            
        Returns:
            Custom workflow definition
        """
        workflow_id = f"workflow_{analysis.task_id}"
        phases = []
        
        # Create phases for each required context
        for i, context in enumerate(analysis.required_contexts):
            phase = self._create_context_phase(context, analysis, workflow_id, i)
            phases.append(phase)
        
        # Ensure logical ordering
        phases = self._order_phases_logically(phases)
        
        # Build dependencies
        dependencies = self._build_phase_dependencies(phases, analysis)
        
        # Estimate duration
        estimated_duration = self._estimate_workflow_duration(phases, analysis.complexity)
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=f"Custom workflow for {analysis.description[:50]}...",
            description=f"Custom automated workflow for: {analysis.description}",
            phases=phases,
            dependencies=dependencies,
            estimated_duration=estimated_duration,
            quality_gates=self._get_quality_gates(analysis),
            metadata={
                "custom_workflow": True,
                "task_analysis": analysis.dict()
            }
        )
        
        return workflow
    
    def optimize_sequence(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """
        Optimize context sequence for maximum efficiency.
        
        Args:
            workflow: Workflow definition to optimize
            
        Returns:
            Optimized workflow definition
        """
        logger.info("Optimizing workflow sequence")
        
        # Apply optimization rules
        optimized_phases = self._apply_optimization_rules(workflow.phases)
        
        # Identify parallel execution opportunities
        optimized_phases = self._identify_parallel_groups(optimized_phases, workflow.dependencies)
        
        # Optimize phase ordering
        optimized_phases = self._optimize_phase_order(optimized_phases, workflow.dependencies)
        
        # Update workflow
        workflow.phases = optimized_phases
        workflow.estimated_duration = self._estimate_workflow_duration(optimized_phases, ComplexityLevel.MEDIUM)
        
        return workflow
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> ValidationResult:
        """
        Validate workflow definition for completeness and correctness.
        
        Args:
            workflow: Workflow definition to validate
            
        Returns:
            Validation result with details
        """
        messages = []
        score = 1.0
        
        # Check basic requirements
        if not workflow.phases:
            messages.append("Workflow has no phases")
            score = 0.0
        
        # Check context validity
        valid_contexts = {
            '@code', '@debug', '@agile', '@git', '@test', '@design', 
            '@docs', '@optimize', '@security', '@research', '@default'
        }
        
        for phase in workflow.phases:
            if phase.context not in valid_contexts:
                messages.append(f"Invalid context in phase {phase.name}: {phase.context}")
                score -= 0.2
        
        # Check for essential contexts
        contexts = {phase.context for phase in workflow.phases}
        
        # Most workflows should have @git for deployment
        if '@git' not in contexts and len(contexts) > 1:
            messages.append("Workflow missing deployment phase (@git)")
            score -= 0.1
        
        # Complex workflows should have testing
        if len(workflow.phases) > 2 and '@test' not in contexts:
            messages.append("Complex workflow missing testing phase (@test)")
            score -= 0.1
        
        # Check phase connectivity
        if not self._is_workflow_connected(workflow):
            messages.append("Workflow phases are not properly connected")
            score -= 0.3
        
        # Check for circular dependencies
        if self._has_circular_dependencies(workflow.dependencies):
            messages.append("Circular dependencies detected")
            score -= 0.4
        
        return ValidationResult(
            passed=score >= 0.7,
            score=max(0.0, score),
            messages=messages,
            details={"validation_type": "workflow_definition", "workflow_id": workflow.workflow_id}
        )
    
    def _load_templates(self) -> None:
        """Load workflow templates from files."""
        if not os.path.exists(self.template_directory):
            logger.warning(f"Template directory not found: {self.template_directory}")
            return
        
        template_count = 0
        for root, dirs, files in os.walk(self.template_directory):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    template_path = os.path.join(root, file)
                    try:
                        template = self._load_template_file(template_path)
                        if template:
                            self.templates[template.template_id] = template
                            template_count += 1
                    except Exception as e:
                        logger.error(f"Failed to load template {template_path}: {e}")
        
        logger.info(f"Loaded {template_count} workflow templates")
    
    def _load_template_file(self, template_path: str) -> Optional[WorkflowTemplate]:
        """Load a single template file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Convert YAML data to WorkflowTemplate
            phases = []
            for phase_data in data.get('contexts', []):
                phase = WorkflowPhase(
                    phase_id=phase_data.get('phase', f"phase_{len(phases)}"),
                    context=phase_data['context'],
                    name=phase_data.get('name', phase_data['phase']),
                    description=phase_data.get('description', ''),
                    inputs=phase_data.get('inputs', []),
                    outputs=phase_data.get('outputs', []),
                    condition=phase_data.get('condition'),
                    timeout=phase_data.get('timeout', 300),
                    retry_count=phase_data.get('retry_count', 3),
                    quality_gates=phase_data.get('quality_gates', [])
                )
                phases.append(phase)
            
            template = WorkflowTemplate(
                template_id=data['name'],
                name=data['name'],
                description=data.get('description', ''),
                category=data.get('category', 'general'),
                phases=phases,
                parameters=data.get('parameters', {}),
                tags=data.get('tags', [])
            )
            
            return template
            
        except Exception as e:
            logger.error(f"Error loading template {template_path}: {e}")
            return None
    
    def _calculate_template_score(self, template: WorkflowTemplate, analysis: TaskAnalysis) -> float:
        """Calculate how well a template matches the task analysis."""
        score = 0.0
        
        # Context matching
        template_contexts = {phase.context for phase in template.phases}
        required_contexts = set(analysis.required_contexts)
        
        if required_contexts:
            context_overlap = len(template_contexts & required_contexts) / len(required_contexts)
            score += context_overlap * 0.4
        
        # Entity type matching
        entity_types = {entity.type for entity in analysis.entities}
        
        # Template category matching
        category_matches = {
            'feature_development': {'feature', 'component', 'api', 'ui'},
            'bug_fix': {'bug', 'issue', 'error'},
            'security_audit': {'security', 'vulnerability'},
            'performance_optimization': {'performance', 'optimization'},
            'code_review': {'review', 'quality'},
            'documentation': {'documentation', 'guide', 'manual'}
        }
        
        if template.category in category_matches:
            category_entities = category_matches[template.category]
            if entity_types & category_entities:
                score += 0.3
        
        # Complexity matching
        phase_count = len(template.phases)
        if analysis.complexity == ComplexityLevel.SIMPLE and phase_count <= 3:
            score += 0.2
        elif analysis.complexity == ComplexityLevel.MEDIUM and 3 <= phase_count <= 6:
            score += 0.2
        elif analysis.complexity == ComplexityLevel.COMPLEX and phase_count >= 5:
            score += 0.2
        
        # Success rate bonus
        if hasattr(template, 'success_rate') and template.success_rate > 0.8:
            score += 0.1
        
        return min(1.0, score)
    
    def _create_context_phase(self, context: str, analysis: TaskAnalysis, workflow_id: str, index: int = 0) -> WorkflowPhase:
        """Create a workflow phase for a specific context."""
        phase_templates = {
            '@agile': {
                'name': 'Requirements Analysis',
                'description': 'Analyze requirements and create user stories',
                'inputs': ['task_description', 'project_context'],
                'outputs': ['user_stories', 'acceptance_criteria'],
                'quality_gates': ['requirements_completeness', 'acceptance_criteria_clarity']
            },
            '@design': {
                'name': 'Architecture Design',
                'description': 'Create system architecture and design specifications',
                'inputs': ['requirements', 'existing_architecture'],
                'outputs': ['design_specifications', 'architecture_diagrams'],
                'quality_gates': ['design_completeness', 'architecture_consistency']
            },
            '@code': {
                'name': 'Implementation',
                'description': 'Implement the required functionality',
                'inputs': ['design_specifications', 'coding_standards'],
                'outputs': ['source_code', 'implementation_notes'],
                'quality_gates': ['code_quality', 'coding_standards_compliance']
            },
            '@test': {
                'name': 'Testing',
                'description': 'Create and execute comprehensive tests',
                'inputs': ['source_code', 'test_requirements'],
                'outputs': ['test_suite', 'test_results', 'coverage_report'],
                'quality_gates': ['test_coverage', 'test_quality']
            },
            '@debug': {
                'name': 'Issue Resolution',
                'description': 'Debug and resolve identified issues',
                'inputs': ['error_reports', 'system_logs'],
                'outputs': ['root_cause_analysis', 'fixes'],
                'quality_gates': ['issue_resolution', 'no_regressions']
            },
            '@docs': {
                'name': 'Documentation',
                'description': 'Create and update documentation',
                'inputs': ['implementation_details', 'api_specifications'],
                'outputs': ['documentation', 'user_guides'],
                'quality_gates': ['documentation_completeness', 'clarity']
            },
            '@security': {
                'name': 'Security Review',
                'description': 'Perform security analysis and vulnerability assessment',
                'inputs': ['source_code', 'security_requirements'],
                'outputs': ['security_analysis', 'vulnerability_report'],
                'quality_gates': ['security_compliance', 'vulnerability_assessment']
            },
            '@optimize': {
                'name': 'Performance Optimization',
                'description': 'Optimize performance and efficiency',
                'inputs': ['performance_requirements', 'benchmark_data'],
                'outputs': ['optimized_code', 'performance_report'],
                'quality_gates': ['performance_targets', 'efficiency_metrics']
            },
            '@git': {
                'name': 'Deployment',
                'description': 'Commit, test, and deploy changes',
                'inputs': ['finalized_code', 'test_results'],
                'outputs': ['commit_hash', 'deployment_status'],
                'quality_gates': ['deployment_success', 'no_breaking_changes']
            }
        }
        
        template = phase_templates.get(context, {
            'name': f'Phase {index + 1}',
            'description': f'Execute {context} context',
            'inputs': ['previous_outputs'],
            'outputs': ['phase_results'],
            'quality_gates': ['basic_validation']
        })
        
        return WorkflowPhase(
            phase_id=f"{workflow_id}_phase_{index}_{context.replace('@', '')}",
            context=context,
            name=template['name'],
            description=template['description'],
            inputs=template['inputs'],
            outputs=template['outputs'],
            timeout=self._get_context_timeout(context, analysis.complexity),
            retry_count=3,
            quality_gates=template['quality_gates']
        )
    
    def _get_context_timeout(self, context: str, complexity: ComplexityLevel) -> int:
        """Get appropriate timeout for context and complexity."""
        base_timeouts = {
            '@agile': 300,    # 5 minutes
            '@design': 600,   # 10 minutes
            '@code': 1800,    # 30 minutes
            '@test': 900,     # 15 minutes
            '@debug': 1200,   # 20 minutes
            '@docs': 600,     # 10 minutes
            '@security': 900, # 15 minutes
            '@optimize': 1200, # 20 minutes
            '@git': 300       # 5 minutes
        }
        
        base_timeout = base_timeouts.get(context, 600)
        
        # Adjust for complexity
        if complexity == ComplexityLevel.COMPLEX:
            return int(base_timeout * 1.5)
        elif complexity == ComplexityLevel.SIMPLE:
            return int(base_timeout * 0.7)
        
        return base_timeout
    
    def _build_context_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Build context capabilities mapping."""
        return {
            '@agile': {
                'primary_function': 'requirements_analysis',
                'outputs': ['user_stories', 'acceptance_criteria', 'sprint_planning'],
                'dependencies': [],
                'parallel_safe': False
            },
            '@design': {
                'primary_function': 'architecture_design',
                'outputs': ['design_specifications', 'architecture_diagrams'],
                'dependencies': ['@agile'],
                'parallel_safe': False
            },
            '@code': {
                'primary_function': 'implementation',
                'outputs': ['source_code', 'implementation_notes'],
                'dependencies': ['@design'],
                'parallel_safe': False
            },
            '@test': {
                'primary_function': 'quality_assurance',
                'outputs': ['test_suite', 'test_results'],
                'dependencies': ['@code'],
                'parallel_safe': True
            },
            '@debug': {
                'primary_function': 'issue_resolution',
                'outputs': ['fixes', 'root_cause_analysis'],
                'dependencies': ['@test'],
                'parallel_safe': False
            },
            '@docs': {
                'primary_function': 'documentation',
                'outputs': ['documentation', 'user_guides'],
                'dependencies': ['@code'],
                'parallel_safe': True
            },
            '@security': {
                'primary_function': 'security_analysis',
                'outputs': ['security_report', 'vulnerability_assessment'],
                'dependencies': ['@code'],
                'parallel_safe': True
            },
            '@optimize': {
                'primary_function': 'performance_optimization',
                'outputs': ['optimized_code', 'performance_metrics'],
                'dependencies': ['@test'],
                'parallel_safe': False
            },
            '@git': {
                'primary_function': 'deployment',
                'outputs': ['commit_hash', 'deployment_status'],
                'dependencies': ['@test'],
                'parallel_safe': False
            }
        }
    
    def _build_optimization_rules(self) -> List[Dict[str, Any]]:
        """Build workflow optimization rules."""
        return [
            {
                'name': 'agile_first',
                'description': 'Requirements analysis should come first',
                'condition': lambda phases: any(p.context == '@agile' for p in phases),
                'action': lambda phases: self._move_context_to_front(phases, '@agile')
            },
            {
                'name': 'design_before_code',
                'description': 'Design should come before implementation',
                'condition': lambda phases: any(p.context == '@design' for p in phases) and any(p.context == '@code' for p in phases),
                'action': lambda phases: self._ensure_order(phases, '@design', '@code')
            },
            {
                'name': 'code_before_test',
                'description': 'Implementation should come before testing',
                'condition': lambda phases: any(p.context == '@code' for p in phases) and any(p.context == '@test' for p in phases),
                'action': lambda phases: self._ensure_order(phases, '@code', '@test')
            },
            {
                'name': 'git_last',
                'description': 'Deployment should come last',
                'condition': lambda phases: any(p.context == '@git' for p in phases),
                'action': lambda phases: self._move_context_to_end(phases, '@git')
            }
        ]
    
    def _apply_optimization_rules(self, phases: List[WorkflowPhase]) -> List[WorkflowPhase]:
        """Apply optimization rules to phases."""
        optimized_phases = phases.copy()
        
        for rule in self.optimization_rules:
            if rule['condition'](optimized_phases):
                optimized_phases = rule['action'](optimized_phases)
        
        return optimized_phases
    
    def _move_context_to_front(self, phases: List[WorkflowPhase], context: str) -> List[WorkflowPhase]:
        """Move phases with specific context to the front."""
        context_phases = [p for p in phases if p.context == context]
        other_phases = [p for p in phases if p.context != context]
        return context_phases + other_phases
    
    def _move_context_to_end(self, phases: List[WorkflowPhase], context: str) -> List[WorkflowPhase]:
        """Move phases with specific context to the end."""
        context_phases = [p for p in phases if p.context == context]
        other_phases = [p for p in phases if p.context != context]
        return other_phases + context_phases
    
    def _ensure_order(self, phases: List[WorkflowPhase], first_context: str, second_context: str) -> List[WorkflowPhase]:
        """Ensure one context comes before another."""
        first_phases = [p for p in phases if p.context == first_context]
        second_phases = [p for p in phases if p.context == second_context]
        other_phases = [p for p in phases if p.context not in [first_context, second_context]]
        
        # Simple ordering - put first context phases before second context phases
        result = []
        result.extend(first_phases)
        result.extend(other_phases)
        result.extend(second_phases)
        
        return result
    
    def _identify_parallel_groups(self, phases: List[WorkflowPhase], dependencies: Dict[str, List[str]]) -> List[WorkflowPhase]:
        """Identify phases that can run in parallel."""
        # Simple parallel grouping based on context capabilities
        parallel_contexts = {'@test', '@docs', '@security'}
        
        for i, phase in enumerate(phases):
            if phase.context in parallel_contexts:
                # Check if this phase can run in parallel with others
                for j, other_phase in enumerate(phases):
                    if (i != j and other_phase.context in parallel_contexts and
                        not self._has_dependency(phase.phase_id, other_phase.phase_id, dependencies)):
                        phase.parallel_group = f"parallel_group_{min(i, j)}"
                        other_phase.parallel_group = f"parallel_group_{min(i, j)}"
        
        return phases
    
    def _optimize_phase_order(self, phases: List[WorkflowPhase], dependencies: Dict[str, List[str]]) -> List[WorkflowPhase]:
        """Optimize the order of phases based on dependencies."""
        # Topological sort based on dependencies
        in_degree = {phase.phase_id: 0 for phase in phases}
        graph = {phase.phase_id: [] for phase in phases}
        
        # Build dependency graph
        for phase_id, deps in dependencies.items():
            for dep in deps:
                if dep in graph:
                    graph[dep].append(phase_id)
                    in_degree[phase_id] += 1
        
        # Topological sort
        queue = [phase_id for phase_id in in_degree if in_degree[phase_id] == 0]
        sorted_ids = []
        
        while queue:
            current = queue.pop(0)
            sorted_ids.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Reorder phases based on sorted IDs
        phase_map = {phase.phase_id: phase for phase in phases}
        return [phase_map[phase_id] for phase_id in sorted_ids if phase_id in phase_map]
    
    def _build_phase_dependencies(self, phases: List[WorkflowPhase], analysis: TaskAnalysis) -> Dict[str, List[str]]:
        """Build dependencies between phases."""
        dependencies = {}
        
        # Basic context-based dependencies
        context_deps = {
            '@design': ['@agile'],
            '@code': ['@design'],
            '@test': ['@code'],
            '@debug': ['@test'],
            '@docs': ['@code'],
            '@security': ['@code'],
            '@optimize': ['@test'],
            '@git': ['@test']
        }
        
        phase_by_context = {}
        for phase in phases:
            if phase.context not in phase_by_context:
                phase_by_context[phase.context] = []
            phase_by_context[phase.context].append(phase)
        
        for phase in phases:
            deps = []
            context_dependencies = context_deps.get(phase.context, [])
            
            for dep_context in context_dependencies:
                if dep_context in phase_by_context:
                    # Add dependency on all phases of the required context
                    deps.extend([p.phase_id for p in phase_by_context[dep_context]])
            
            if deps:
                dependencies[phase.phase_id] = deps
        
        return dependencies
    
    def _estimate_workflow_duration(self, phases: List[WorkflowPhase], complexity: ComplexityLevel) -> int:
        """Estimate total workflow duration."""
        total_duration = sum(phase.timeout for phase in phases) // 60  # Convert to minutes
        
        # Adjust for complexity
        if complexity == ComplexityLevel.COMPLEX:
            total_duration = int(total_duration * 1.3)
        elif complexity == ComplexityLevel.SIMPLE:
            total_duration = int(total_duration * 0.8)
        
        return max(15, total_duration)  # Minimum 15 minutes
    
    def _get_quality_gates(self, analysis: TaskAnalysis) -> List[str]:
        """Get quality gates for the workflow."""
        gates = ['basic_validation', 'error_free_execution']
        
        if analysis.complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.COMPLEX]:
            gates.extend(['comprehensive_testing', 'code_quality_check'])
        
        if any(entity.type == 'security' for entity in analysis.entities):
            gates.append('security_validation')
        
        if any(entity.type == 'performance' for entity in analysis.entities):
            gates.append('performance_validation')
        
        return gates
    
    def _filter_unnecessary_phases(self, phases: List[WorkflowPhase], analysis: TaskAnalysis) -> List[WorkflowPhase]:
        """Remove unnecessary phases based on analysis."""
        # Keep all phases for now - could be enhanced with more sophisticated filtering
        return phases
    
    def _order_phases_logically(self, phases: List[WorkflowPhase]) -> List[WorkflowPhase]:
        """Order phases in logical sequence."""
        # Define logical order of contexts
        context_order = ['@agile', '@design', '@code', '@test', '@debug', '@docs', '@security', '@optimize', '@git']
        
        ordered_phases = []
        for context in context_order:
            for phase in phases:
                if phase.context == context:
                    ordered_phases.append(phase)
        
        # Add any remaining phases
        for phase in phases:
            if phase not in ordered_phases:
                ordered_phases.append(phase)
        
        return ordered_phases
    
    def _is_workflow_connected(self, workflow: WorkflowDefinition) -> bool:
        """Check if workflow phases are properly connected."""
        if len(workflow.phases) <= 1:
            return True
        
        # Simple connectivity check - ensure dependencies form a connected graph
        phase_ids = {phase.phase_id for phase in workflow.phases}
        
        # Check if all phases are either roots or have dependencies
        roots = []
        for phase in workflow.phases:
            if phase.phase_id not in workflow.dependencies:
                roots.append(phase.phase_id)
        
        # Should have at least one root and all phases should be reachable
        return len(roots) >= 1
    
    def _has_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> bool:
        """Check for circular dependencies."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependencies:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _has_dependency(self, phase1: str, phase2: str, dependencies: Dict[str, List[str]]) -> bool:
        """Check if phase1 depends on phase2."""
        return phase2 in dependencies.get(phase1, [])
    
    def _fix_validation_issues(self, workflow: WorkflowDefinition, validation: ValidationResult) -> WorkflowDefinition:
        """Attempt to fix workflow validation issues."""
        # Simple fixes for common issues
        if "missing deployment phase" in str(validation.messages):
            # Add @git phase if missing
            git_phase = self._create_context_phase('@git', None, workflow.workflow_id, len(workflow.phases))
            workflow.phases.append(git_phase)
        
        if "missing testing phase" in str(validation.messages):
            # Add @test phase if missing
            test_phase = self._create_context_phase('@test', None, workflow.workflow_id, len(workflow.phases))
            workflow.phases.insert(-1, test_phase)  # Insert before last phase
        
        return workflow
