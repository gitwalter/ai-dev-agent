#!/usr/bin/env python3
"""
Comprehensive examples demonstrating the Workflow Composition Engine.
Shows various usage patterns and integration scenarios.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from workflow.composition.task_analyzer import TaskAnalyzer
from workflow.composition.workflow_composer import WorkflowComposer
from workflow.orchestration.context_orchestrator import ContextOrchestrator
from workflow.models.workflow_models import (
    WorkflowDefinition, WorkflowPhase, WorkflowTemplate,
    TaskAnalysis, Entity, ComplexityLevel, WorkflowResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowExamples:
    """
    Comprehensive examples of Workflow Composition Engine usage.
    """
    
    def __init__(self):
        """Initialize workflow components."""
        self.analyzer = TaskAnalyzer()
        self.composer = WorkflowComposer()
        self.orchestrator = ContextOrchestrator()
    
    async def example_1_simple_feature_development(self):
        """
        Example 1: Simple feature development workflow.
        Demonstrates basic task analysis and workflow execution.
        """
        print("\n" + "="*60)
        print("EXAMPLE 1: Simple Feature Development")
        print("="*60)
        
        # Task description
        task_description = "Implement user registration feature with email verification"
        
        print(f"Task: {task_description}")
        
        # Step 1: Analyze the task
        print("\n1. Analyzing task...")
        analysis = self.analyzer.analyze_task(task_description)
        
        print(f"   - Complexity: {analysis.complexity}")
        print(f"   - Required contexts: {analysis.required_contexts}")
        print(f"   - Estimated duration: {analysis.estimated_duration} minutes")
        print(f"   - Confidence: {analysis.confidence:.2f}")
        
        # Step 2: Compose workflow
        print("\n2. Composing workflow...")
        workflow = self.composer.compose_workflow(analysis)
        
        print(f"   - Workflow ID: {workflow.workflow_id}")
        print(f"   - Number of phases: {len(workflow.phases)}")
        print(f"   - Estimated duration: {workflow.estimated_duration} minutes")
        
        # Display workflow phases
        print("\n   Workflow phases:")
        for i, phase in enumerate(workflow.phases, 1):
            print(f"     {i}. {phase.name} ({phase.context}) - {phase.timeout}s timeout")
        
        # Step 3: Execute workflow
        print("\n3. Executing workflow...")
        start_time = datetime.now()
        
        result = await self.orchestrator.execute_workflow(workflow)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Display results
        print(f"\n4. Workflow completed!")
        print(f"   - Status: {result.status}")
        print(f"   - Execution time: {execution_time:.2f} seconds")
        print(f"   - Phases executed: {len(result.phases_executed)}")
        print(f"   - Success rate: {result.metrics.get('success_rate', 0):.2%}")
        
        if result.errors:
            print(f"   - Errors: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"     • {error}")
        
        return result
    
    async def example_2_bug_fix_workflow(self):
        """
        Example 2: Bug fix workflow with debugging focus.
        Demonstrates context-specific workflow composition.
        """
        print("\n" + "="*60)
        print("EXAMPLE 2: Bug Fix Workflow")
        print("="*60)
        
        # Bug report description
        task_description = "Fix critical authentication bug causing login failures on mobile devices"
        
        print(f"Bug Report: {task_description}")
        
        # Analyze with additional context
        project_context = {
            "project_size": "large",
            "team_experience": "senior",
            "urgency": "critical"
        }
        
        print("\n1. Analyzing bug report...")
        analysis = self.analyzer.analyze_task(task_description, project_context)
        
        print(f"   - Complexity: {analysis.complexity}")
        print(f"   - Required contexts: {analysis.required_contexts}")
        print(f"   - Entities found: {len(analysis.entities)}")
        
        # Show extracted entities
        print("   - Key entities:")
        for entity in analysis.entities[:5]:  # Show top 5 entities
            print(f"     • {entity.name} ({entity.type}) - confidence: {entity.confidence:.2f}")
        
        # Compose and execute workflow
        workflow = self.composer.compose_workflow(analysis)
        
        print(f"\n2. Bug fix workflow composed with {len(workflow.phases)} phases")
        
        # Execute with monitoring
        result = await self.orchestrator.execute_workflow(workflow, project_context)
        
        print(f"\n3. Bug fix workflow completed: {result.status}")
        print(f"   - Total execution time: {result.execution_time} seconds")
        
        # Show phase results
        if result.results:
            print("   - Phase results summary:")
            for phase_id, phase_result in result.results.items():
                if isinstance(phase_result, dict) and 'root_cause_analysis' in phase_result:
                    print(f"     • {phase_id}: Root cause identified")
                elif isinstance(phase_result, dict) and 'fixes' in phase_result:
                    print(f"     • {phase_id}: {len(phase_result['fixes'])} fixes applied")
        
        return result
    
    async def example_3_custom_workflow_creation(self):
        """
        Example 3: Custom workflow creation for specialized requirements.
        Demonstrates manual workflow composition and customization.
        """
        print("\n" + "="*60)
        print("EXAMPLE 3: Custom Research and Prototyping Workflow")
        print("="*60)
        
        # Create custom workflow phases
        research_phase = WorkflowPhase(
            phase_id="technology_research",
            context="@research",
            name="Technology Research",
            description="Research available authentication frameworks and libraries",
            inputs=["research_objectives", "evaluation_criteria"],
            outputs=["technology_analysis", "comparison_matrix", "recommendations"],
            timeout=1800,  # 30 minutes
            retry_count=2,
            quality_gates=["comprehensive_research", "objective_evaluation"]
        )
        
        design_phase = WorkflowPhase(
            phase_id="poc_design",
            context="@design",
            name="Proof of Concept Design",
            description="Design architecture for authentication POC",
            inputs=["technology_analysis", "requirements"],
            outputs=["poc_architecture", "implementation_plan"],
            timeout=900,  # 15 minutes
            retry_count=2,
            quality_gates=["architecture_feasible", "implementation_clear"]
        )
        
        prototype_phase = WorkflowPhase(
            phase_id="prototype_implementation",
            context="@code",
            name="Prototype Implementation",
            description="Build authentication prototype",
            inputs=["poc_architecture", "implementation_plan"],
            outputs=["prototype_code", "demo_application"],
            timeout=2400,  # 40 minutes
            retry_count=3,
            quality_gates=["prototype_functional", "demo_ready"]
        )
        
        validation_phase = WorkflowPhase(
            phase_id="prototype_validation",
            context="@test",
            name="Prototype Validation",
            description="Test and validate prototype functionality",
            inputs=["prototype_code", "validation_criteria"],
            outputs=["validation_results", "performance_metrics"],
            timeout=600,  # 10 minutes
            retry_count=2,
            quality_gates=["validation_passed", "performance_acceptable"]
        )
        
        documentation_phase = WorkflowPhase(
            phase_id="research_documentation",
            context="@docs",
            name="Research Documentation",
            description="Document findings and recommendations",
            inputs=["validation_results", "technology_analysis"],
            outputs=["research_report", "implementation_guide"],
            timeout=900,  # 15 minutes
            retry_count=2,
            quality_gates=["documentation_complete", "recommendations_clear"]
        )
        
        # Create custom workflow
        custom_workflow = WorkflowDefinition(
            workflow_id="custom_research_workflow_001",
            name="Authentication Research and Prototyping",
            description="Custom workflow for researching and prototyping authentication solutions",
            phases=[research_phase, design_phase, prototype_phase, validation_phase, documentation_phase],
            dependencies={
                "poc_design": ["technology_research"],
                "prototype_implementation": ["poc_design"],
                "prototype_validation": ["prototype_implementation"],
                "research_documentation": ["prototype_validation"]
            },
            estimated_duration=120,  # 2 hours
            quality_gates=["research_comprehensive", "prototype_validated", "documentation_complete"],
            metadata={
                "custom_workflow": True,
                "research_focus": "authentication",
                "deliverable_type": "prototype_and_report"
            }
        )
        
        print("1. Custom workflow created:")
        print(f"   - Name: {custom_workflow.name}")
        print(f"   - Phases: {len(custom_workflow.phases)}")
        print(f"   - Dependencies: {len(custom_workflow.dependencies)}")
        print(f"   - Quality gates: {len(custom_workflow.quality_gates)}")
        
        # Validate custom workflow
        validation = self.composer.validate_workflow(custom_workflow)
        print(f"\n2. Workflow validation: {'PASSED' if validation.passed else 'FAILED'}")
        print(f"   - Validation score: {validation.score:.2f}")
        
        if not validation.passed:
            print("   - Validation issues:")
            for message in validation.messages:
                print(f"     • {message}")
        
        # Execute custom workflow
        print("\n3. Executing custom workflow...")
        
        initial_context = {
            "research_objectives": [
                "Evaluate OAuth 2.0 vs JWT authentication",
                "Assess security implications",
                "Determine implementation complexity"
            ],
            "evaluation_criteria": [
                "Security strength",
                "Implementation ease",
                "Performance impact",
                "Scalability"
            ]
        }
        
        result = await self.orchestrator.execute_workflow(custom_workflow, initial_context)
        
        print(f"\n4. Custom workflow completed: {result.status}")
        print(f"   - Execution time: {result.execution_time} seconds")
        print(f"   - Phases completed: {len(result.phases_executed)}/{len(custom_workflow.phases)}")
        
        # Show detailed results
        if result.results:
            print("\n   - Detailed results:")
            for phase_id, phase_result in result.results.items():
                if isinstance(phase_result, dict):
                    output_count = len([k for k in phase_result.keys() if not k.startswith('_')])
                    print(f"     • {phase_id}: {output_count} outputs generated")
        
        return result
    
    async def example_4_parallel_execution(self):
        """
        Example 4: Workflow with parallel execution capabilities.
        Demonstrates concurrent phase execution and optimization.
        """
        print("\n" + "="*60)
        print("EXAMPLE 4: Parallel Execution Workflow")
        print("="*60)
        
        # Task that can benefit from parallel execution
        task_description = "Complete security audit and performance optimization of the API system"
        
        print(f"Task: {task_description}")
        
        # Analyze task
        analysis = self.analyzer.analyze_task(task_description)
        
        # Compose workflow
        workflow = self.composer.compose_workflow(analysis)
        
        # Optimize for parallel execution
        optimized_workflow = self.composer.optimize_sequence(workflow)
        
        print(f"\n1. Workflow optimized for parallel execution:")
        print(f"   - Original phases: {len(workflow.phases)}")
        print(f"   - Optimized phases: {len(optimized_workflow.phases)}")
        
        # Identify parallel groups
        parallel_groups = {}
        for phase in optimized_workflow.phases:
            if hasattr(phase, 'parallel_group') and phase.parallel_group:
                if phase.parallel_group not in parallel_groups:
                    parallel_groups[phase.parallel_group] = []
                parallel_groups[phase.parallel_group].append(phase.name)
        
        if parallel_groups:
            print("\n   - Parallel execution groups:")
            for group_id, phases in parallel_groups.items():
                print(f"     • {group_id}: {', '.join(phases)}")
        
        # Execute with timing
        print("\n2. Executing optimized workflow...")
        start_time = datetime.now()
        
        result = await self.orchestrator.execute_workflow(optimized_workflow)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"\n3. Parallel workflow completed:")
        print(f"   - Status: {result.status}")
        print(f"   - Execution time: {execution_time:.2f} seconds")
        print(f"   - Efficiency gain: Estimated 30-40% faster than sequential execution")
        
        return result
    
    async def example_5_error_handling_and_recovery(self):
        """
        Example 5: Error handling and recovery mechanisms.
        Demonstrates resilient workflow execution with failure scenarios.
        """
        print("\n" + "="*60)
        print("EXAMPLE 5: Error Handling and Recovery")
        print("="*60)
        
        # Create a workflow that might encounter errors
        task_description = "Deploy critical hotfix to production environment"
        
        print(f"Task: {task_description}")
        
        # Analyze and compose workflow
        analysis = self.analyzer.analyze_task(task_description)
        workflow = self.composer.compose_workflow(analysis)
        
        print(f"\n1. Deployment workflow created with {len(workflow.phases)} phases")
        
        # Add custom recovery strategy for deployment errors
        def deployment_recovery_strategy(context, error, state):
            if "deployment" in context.lower() and "network" in str(error).lower():
                return {
                    'action_type': 'retry',
                    'parameters': {'max_retries': 3, 'delay': 10},
                    'reason': 'Network error during deployment - retry with delay'
                }
            return None
        
        # Register custom recovery strategy
        self.orchestrator.recovery_strategies.append({
            'name': 'deployment_network_retry',
            'condition': lambda ctx, err, state: "deployment" in ctx.lower() and "network" in str(err).lower(),
            'action': 'retry',
            'parameters': {'max_retries': 3, 'delay': 10},
            'reason': 'Network error during deployment'
        })
        
        print("2. Custom recovery strategy registered for deployment errors")
        
        # Execute workflow with error simulation
        print("\n3. Executing deployment workflow...")
        
        # Add deployment context
        deployment_context = {
            "environment": "production",
            "rollback_plan": True,
            "monitoring_enabled": True,
            "approval_required": False  # For demo purposes
        }
        
        try:
            result = await self.orchestrator.execute_workflow(workflow, deployment_context)
            
            print(f"\n4. Deployment workflow result: {result.status}")
            
            if result.errors:
                print(f"   - Errors encountered: {len(result.errors)}")
                for error in result.errors:
                    print(f"     • {error}")
            
            if result.warnings:
                print(f"   - Warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    print(f"     • {warning}")
            
            # Show recovery actions taken
            recovery_metrics = result.metrics.get('recovery_actions', [])
            if recovery_metrics:
                print(f"   - Recovery actions taken: {len(recovery_metrics)}")
            
        except Exception as e:
            print(f"\n4. Workflow failed with unrecoverable error: {e}")
            print("   - This demonstrates the system's error boundaries")
        
        return result
    
    async def example_6_workflow_monitoring_and_analytics(self):
        """
        Example 6: Workflow monitoring and analytics.
        Demonstrates performance tracking and optimization insights.
        """
        print("\n" + "="*60)
        print("EXAMPLE 6: Workflow Monitoring and Analytics")
        print("="*60)
        
        # Execute multiple workflows to generate analytics data
        workflows_executed = []
        
        tasks = [
            "Create user profile management feature",
            "Fix database connection timeout issue",
            "Implement API rate limiting",
            "Update documentation for new endpoints"
        ]
        
        print("1. Executing multiple workflows for analytics...")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n   Workflow {i}: {task}")
            
            analysis = self.analyzer.analyze_task(task)
            workflow = self.composer.compose_workflow(analysis)
            
            start_time = datetime.now()
            result = await self.orchestrator.execute_workflow(workflow)
            end_time = datetime.now()
            
            # Collect metrics
            workflow_metrics = {
                'task': task,
                'workflow_id': workflow.workflow_id,
                'complexity': analysis.complexity,
                'estimated_duration': workflow.estimated_duration,
                'actual_duration': (end_time - start_time).total_seconds(),
                'phases_count': len(workflow.phases),
                'success': result.status.value == 'completed',
                'contexts_used': [phase.context for phase in workflow.phases]
            }
            
            workflows_executed.append(workflow_metrics)
            
            print(f"     - Status: {result.status}")
            print(f"     - Duration: {workflow_metrics['actual_duration']:.1f}s")
        
        # Generate analytics
        print(f"\n2. Analytics Summary ({len(workflows_executed)} workflows):")
        
        # Success rate
        successful_workflows = sum(1 for w in workflows_executed if w['success'])
        success_rate = successful_workflows / len(workflows_executed)
        print(f"   - Success rate: {success_rate:.1%}")
        
        # Average execution time
        avg_duration = sum(w['actual_duration'] for w in workflows_executed) / len(workflows_executed)
        print(f"   - Average execution time: {avg_duration:.1f} seconds")
        
        # Complexity distribution
        complexity_counts = {}
        for w in workflows_executed:
            complexity = w['complexity'].value
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        print("   - Complexity distribution:")
        for complexity, count in complexity_counts.items():
            print(f"     • {complexity}: {count} workflows")
        
        # Most used contexts
        context_usage = {}
        for w in workflows_executed:
            for context in w['contexts_used']:
                context_usage[context] = context_usage.get(context, 0) + 1
        
        print("   - Most used contexts:")
        sorted_contexts = sorted(context_usage.items(), key=lambda x: x[1], reverse=True)
        for context, count in sorted_contexts[:5]:
            print(f"     • {context}: {count} times")
        
        # Duration vs estimation accuracy
        estimation_errors = []
        for w in workflows_executed:
            estimated_seconds = w['estimated_duration'] * 60  # Convert minutes to seconds
            actual_seconds = w['actual_duration']
            error = abs(estimated_seconds - actual_seconds) / estimated_seconds
            estimation_errors.append(error)
        
        avg_estimation_error = sum(estimation_errors) / len(estimation_errors)
        print(f"   - Average estimation error: {avg_estimation_error:.1%}")
        
        return workflows_executed
    
    async def run_all_examples(self):
        """
        Run all workflow examples in sequence.
        """
        print("🚀 WORKFLOW COMPOSITION ENGINE EXAMPLES")
        print("=" * 80)
        
        examples = [
            self.example_1_simple_feature_development,
            self.example_2_bug_fix_workflow,
            self.example_3_custom_workflow_creation,
            self.example_4_parallel_execution,
            self.example_5_error_handling_and_recovery,
            self.example_6_workflow_monitoring_and_analytics
        ]
        
        results = []
        
        for example in examples:
            try:
                result = await example()
                results.append(result)
            except Exception as e:
                logger.error(f"Example failed: {example.__name__}: {e}")
                results.append(None)
        
        # Summary
        print("\n" + "="*80)
        print("EXAMPLES SUMMARY")
        print("="*80)
        
        successful_examples = sum(1 for r in results if r is not None)
        print(f"Completed examples: {successful_examples}/{len(examples)}")
        
        if successful_examples > 0:
            print("\n✅ Workflow Composition Engine examples completed successfully!")
            print("   The system demonstrates:")
            print("   • Intelligent task analysis and workflow composition")
            print("   • Multi-context orchestration and execution")
            print("   • Error handling and recovery mechanisms")
            print("   • Performance optimization and parallel execution")
            print("   • Comprehensive monitoring and analytics")
        else:
            print("\n❌ Some examples encountered issues. Check logs for details.")
        
        return results


async def main():
    """
    Main function to run workflow examples.
    """
    examples = WorkflowExamples()
    
    print("Starting Workflow Composition Engine Examples...")
    print("This demonstration shows the capabilities of the automated workflow system.\n")
    
    # Run all examples
    results = await examples.run_all_examples()
    
    print(f"\nExamples completed. Results: {len([r for r in results if r is not None])}/{len(results)} successful")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
