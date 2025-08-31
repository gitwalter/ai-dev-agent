# Workflow Composition Engine User Guide

**Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Implementation Complete

## Overview

The **Workflow Composition Engine** is a revolutionary system that transforms single-task requests into complete, multi-phase development workflows by intelligently composing different @keyword contexts in optimal sequences. This system provides full automation of development workflows while maintaining high quality and process adherence.

## Key Features

### 🎯 **Intelligent Task Analysis**
- Natural language processing of task descriptions
- Automatic entity extraction and complexity assessment
- Context requirement identification
- Duration estimation and dependency analysis

### 🔄 **Workflow Composition**
- Template-based workflow generation
- Custom workflow creation for unique requirements
- Sequence optimization for maximum efficiency
- Dependency resolution and validation

### 🎛️ **Context Orchestration**
- Seamless transitions between @keyword contexts
- State management across workflow phases
- Result propagation between contexts
- Error recovery and rollback capabilities

### 📊 **Execution Monitoring**
- Real-time workflow progress tracking
- Performance analytics and bottleneck detection
- Quality gate validation
- Comprehensive execution reporting

## Getting Started

### Installation

The Workflow Composition Engine is integrated into the AI-Dev-Agent system. No additional installation is required.

### Basic Usage

#### 1. Simple Task Execution

```python
from workflow.composition.task_analyzer import TaskAnalyzer
from workflow.composition.workflow_composer import WorkflowComposer
from workflow.orchestration.context_orchestrator import ContextOrchestrator

# Initialize components
analyzer = TaskAnalyzer()
composer = WorkflowComposer()
orchestrator = ContextOrchestrator()

# Analyze task
task_description = "Implement user authentication with JWT tokens"
analysis = analyzer.analyze_task(task_description)

# Compose workflow
workflow = composer.compose_workflow(analysis)

# Execute workflow
result = await orchestrator.execute_workflow(workflow)

print(f"Workflow completed with status: {result.status}")
print(f"Execution time: {result.execution_time} seconds")
```

#### 2. Using @Keywords for Context Control

```python
# Explicit context specification
task_with_context = "@code Implement the authentication API endpoint"
analysis = analyzer.analyze_task(task_with_context)

# The system will prioritize @code context while adding necessary supporting contexts
print(f"Required contexts: {analysis.required_contexts}")
# Output: ['@agile', '@design', '@code', '@test', '@security', '@git']
```

### Workflow Templates

The system includes predefined templates for common development scenarios:

#### Feature Development Template
```yaml
# Automatically applied for feature implementation tasks
contexts:
  - "@agile": Requirements analysis and user story creation
  - "@design": Architecture design and API specifications
  - "@code": Feature implementation with TDD
  - "@test": Comprehensive testing suite
  - "@debug": Issue resolution (conditional)
  - "@docs": Documentation updates
  - "@security": Security review and vulnerability assessment
  - "@git": Commit, push, and deployment
```

#### Bug Fix Template
```yaml
# Automatically applied for bug resolution tasks
contexts:
  - "@debug": Bug investigation and root cause analysis
  - "@test": Failing test creation for reproduction
  - "@code": Fix implementation with minimal impact
  - "@test": Fix verification and regression testing
  - "@docs": Documentation updates (conditional)
  - "@git": Fix deployment with detailed description
```

## Advanced Usage

### Custom Workflow Creation

```python
from workflow.models.workflow_models import WorkflowPhase, WorkflowDefinition

# Create custom workflow phases
custom_phases = [
    WorkflowPhase(
        phase_id="custom_research",
        context="@research",
        name="Technology Research",
        description="Research available technologies and frameworks",
        inputs=["research_objectives"],
        outputs=["technology_analysis", "recommendations"],
        timeout=1800,  # 30 minutes
        quality_gates=["comprehensive_research", "objective_evaluation"]
    ),
    WorkflowPhase(
        phase_id="custom_prototype",
        context="@code",
        name="Prototype Development",
        description="Build proof of concept prototype",
        inputs=["technology_analysis"],
        outputs=["prototype_code", "validation_results"],
        timeout=3600,  # 1 hour
        quality_gates=["prototype_functional", "concepts_validated"]
    )
]

# Create custom workflow
custom_workflow = WorkflowDefinition(
    workflow_id="custom_research_workflow",
    name="Research and Prototype Workflow",
    description="Custom workflow for technology research and prototyping",
    phases=custom_phases,
    dependencies={"custom_prototype": ["custom_research"]},
    estimated_duration=150,  # 2.5 hours
    quality_gates=["research_complete", "prototype_validated"]
)

# Execute custom workflow
result = await orchestrator.execute_workflow(custom_workflow)
```

### Workflow Monitoring and Analytics

```python
from workflow.monitoring.execution_monitor import ExecutionMonitor

# Initialize monitoring
monitor = ExecutionMonitor()

# Track workflow execution
workflow_id = "workflow_001"
monitor.track_execution(workflow_id, "implementation_phase", {
    "start_time": datetime.now(),
    "phase_duration": 1200,  # 20 minutes
    "quality_score": 0.95,
    "test_coverage": 0.87
})

# Generate analytics report
report = monitor.generate_analytics("last_30_days")
print(f"Success rate: {report.success_rate:.2%}")
print(f"Average execution time: {report.average_execution_time} minutes")

# Detect bottlenecks
bottlenecks = monitor.detect_bottlenecks(workflow_history)
for bottleneck in bottlenecks:
    print(f"Bottleneck: {bottleneck.description}")
    print(f"Recommendations: {bottleneck.recommendations}")
```

## Context Reference Guide

### Available Contexts

| Context | Purpose | Typical Duration | Quality Gates |
|---------|---------|------------------|---------------|
| `@agile` | Requirements analysis, user stories | 5-15 min | Requirements completeness, stakeholder approval |
| `@design` | Architecture design, API specifications | 10-30 min | Design completeness, architecture consistency |
| `@code` | Feature implementation, coding | 30-120 min | Code quality, standards compliance, test coverage |
| `@test` | Testing, quality assurance | 15-45 min | Test coverage, quality metrics, acceptance tests |
| `@debug` | Issue investigation, bug fixing | 20-60 min | Root cause identified, issues resolved |
| `@docs` | Documentation, user guides | 10-30 min | Documentation completeness, clarity review |
| `@security` | Security review, vulnerability assessment | 15-45 min | Security compliance, vulnerability assessment |
| `@optimize` | Performance optimization, tuning | 20-60 min | Performance targets, efficiency metrics |
| `@git` | Version control, deployment | 5-15 min | Deployment success, no breaking changes |
| `@research` | Technology research, investigation | 30-120 min | Comprehensive research, objective evaluation |

### Context Dependencies

The system automatically manages context dependencies:

```
@agile → @design → @code → @test → @git
                     ↓
                 @security (parallel)
                     ↓
                  @docs (parallel)
                     ↓
                 @optimize (conditional)
```

## Error Handling and Recovery

### Automatic Recovery Strategies

The system includes built-in recovery strategies for common failure scenarios:

#### Timeout Recovery
```python
# Automatic retry with exponential backoff
recovery_action = RecoveryAction(
    action_type="retry",
    parameters={"max_retries": 3, "backoff_factor": 1.5},
    reason="Phase timeout - retry with increased timeout"
)
```

#### Validation Failure Recovery
```python
# Skip non-critical phases or request manual intervention
recovery_action = RecoveryAction(
    action_type="skip",
    parameters={"notify_user": True},
    reason="Validation failed - skip optional phase"
)
```

#### Critical Error Recovery
```python
# Abort workflow with detailed error reporting
recovery_action = RecoveryAction(
    action_type="abort",
    parameters={"create_incident": True, "notify_team": True},
    reason="Critical error - manual intervention required"
)
```

### Custom Error Handling

```python
# Define custom recovery strategy
def custom_recovery_strategy(context, error, state):
    if "network" in str(error).lower():
        return RecoveryAction(
            action_type="retry",
            parameters={"delay": 30, "max_retries": 5},
            reason="Network error - retry with delay"
        )
    return None

# Register custom strategy
orchestrator.recovery_strategies.append({
    'name': 'network_retry',
    'condition': lambda ctx, err, state: "network" in str(err).lower(),
    'action': 'retry',
    'parameters': {'delay': 30, 'max_retries': 5},
    'reason': 'Network error recovery'
})
```

## Performance Optimization

### Parallel Execution

The system automatically identifies opportunities for parallel execution:

```python
# Phases that can run in parallel
parallel_phases = [
    WorkflowPhase(context="@docs", parallel_group="documentation_group"),
    WorkflowPhase(context="@security", parallel_group="documentation_group"),
    WorkflowPhase(context="@test", parallel_group="validation_group")
]

# System will execute these phases concurrently when possible
```

### Caching and Optimization

```python
# Enable result caching for expensive operations
workflow_config = {
    "enable_caching": True,
    "cache_duration": 3600,  # 1 hour
    "parallel_execution": True,
    "optimization_level": "aggressive"
}

result = await orchestrator.execute_workflow(workflow, config=workflow_config)
```

## Integration Examples

### Integration with Existing Systems

#### LangGraph Integration
```python
from workflow.integration.langgraph_integration import LangGraphIntegration

# Initialize integration
langgraph_integration = LangGraphIntegration(llm_config, agents)

# Execute workflow phase using LangGraph
result = await langgraph_integration.execute_context_phase(
    context="@code",
    inputs={"design_specs": design_data},
    state=agent_state
)
```

#### Context-Aware Rule System Integration
```python
from workflow.integration.context_aware_integration import ContextAwareIntegration

# Initialize integration
rule_integration = ContextAwareIntegration()

# Switch context and load appropriate rules
rules = await rule_integration.switch_context("@security", workflow_state)
print(f"Loaded {len(rules)} security-specific rules")
```

## Best Practices

### 1. Task Description Guidelines

**Good Task Descriptions:**
```
✅ "Implement user authentication with JWT tokens, including login/logout endpoints and session management"
✅ "Fix critical security vulnerability in payment processing API - SQL injection in transaction endpoint"
✅ "Create comprehensive test suite for the user management module with unit and integration tests"
```

**Poor Task Descriptions:**
```
❌ "Fix the thing"
❌ "Make it work better"
❌ "Update stuff"
```

### 2. Workflow Customization

```python
# Customize workflow based on project requirements
def customize_for_project(base_workflow, project_config):
    if project_config.get("security_critical"):
        # Add additional security phases
        base_workflow.phases.append(
            WorkflowPhase(
                context="@security",
                name="Penetration Testing",
                description="Comprehensive security testing"
            )
        )
    
    if project_config.get("performance_critical"):
        # Add performance optimization phase
        base_workflow.phases.append(
            WorkflowPhase(
                context="@optimize",
                name="Performance Optimization",
                description="Performance tuning and optimization"
            )
        )
    
    return base_workflow
```

### 3. Quality Gate Configuration

```python
# Define project-specific quality gates
quality_gates = {
    "code_quality": {
        "min_score": 8.0,
        "max_complexity": 10,
        "required_coverage": 0.80
    },
    "security_compliance": {
        "max_high_vulnerabilities": 0,
        "max_medium_vulnerabilities": 2,
        "required_scans": ["sast", "dast", "dependency"]
    },
    "performance_requirements": {
        "max_response_time": 200,  # milliseconds
        "min_throughput": 1000,   # requests per second
        "max_memory_usage": 512   # MB
    }
}

# Apply quality gates to workflow
workflow.quality_gates.extend(quality_gates.keys())
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Workflow Fails to Start
```python
# Check workflow validation
validation = composer.validate_workflow(workflow)
if not validation.passed:
    print("Validation errors:")
    for message in validation.messages:
        print(f"- {message}")
```

#### Issue: Phase Timeout
```python
# Increase timeout for complex phases
phase.timeout = 3600  # 1 hour for complex implementation

# Or enable automatic timeout adjustment
workflow_config = {
    "auto_adjust_timeouts": True,
    "timeout_multiplier": 1.5
}
```

#### Issue: Context Transition Failure
```python
# Check context compatibility
valid_transitions = {
    "@agile": ["@design", "@code"],
    "@design": ["@code", "@test"],
    "@code": ["@test", "@debug", "@docs", "@security"],
    # ... more transitions
}

if target_context not in valid_transitions.get(current_context, []):
    print(f"Invalid transition: {current_context} → {target_context}")
```

### Debugging Workflow Execution

```python
# Enable detailed logging
import logging
logging.getLogger("workflow").setLevel(logging.DEBUG)

# Add execution callbacks for monitoring
def phase_started_callback(phase_id, context, inputs):
    print(f"Phase started: {phase_id} ({context})")
    print(f"Inputs: {list(inputs.keys())}")

def phase_completed_callback(phase_id, context, outputs):
    print(f"Phase completed: {phase_id} ({context})")
    print(f"Outputs: {list(outputs.keys())}")

orchestrator.add_callback("phase_started", phase_started_callback)
orchestrator.add_callback("phase_completed", phase_completed_callback)
```

## API Reference

### Core Classes

#### TaskAnalyzer
```python
class TaskAnalyzer:
    def analyze_task(self, task_description: str, context: Dict[str, Any] = None) -> TaskAnalysis
    def extract_entities(self, task_description: str) -> List[Entity]
    def assess_complexity(self, entities: List[Entity], task_description: str, context: Dict[str, Any]) -> ComplexityLevel
    def identify_contexts(self, entities: List[Entity], task_description: str, complexity: ComplexityLevel) -> List[str]
```

#### WorkflowComposer
```python
class WorkflowComposer:
    def compose_workflow(self, analysis: TaskAnalysis) -> WorkflowDefinition
    def select_template(self, analysis: TaskAnalysis) -> Optional[WorkflowTemplate]
    def customize_workflow(self, template: WorkflowTemplate, analysis: TaskAnalysis) -> WorkflowDefinition
    def optimize_sequence(self, workflow: WorkflowDefinition) -> WorkflowDefinition
    def validate_workflow(self, workflow: WorkflowDefinition) -> ValidationResult
```

#### ContextOrchestrator
```python
class ContextOrchestrator:
    async def execute_workflow(self, workflow: WorkflowDefinition, initial_context: Dict[str, Any] = None) -> WorkflowResult
    async def transition_context(self, from_context: str, to_context: str, state: WorkflowState) -> WorkflowState
    async def propagate_results(self, from_phase: str, to_phase: str, results: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]
    async def handle_failure(self, context: str, error: Exception, state: WorkflowState) -> RecoveryAction
```

### Data Models

#### TaskAnalysis
```python
@dataclass
class TaskAnalysis:
    task_id: str
    description: str
    entities: List[Entity]
    complexity: ComplexityLevel
    required_contexts: List[str]
    estimated_duration: int
    dependencies: List[str]
    success_criteria: List[str]
    confidence: float
```

#### WorkflowDefinition
```python
@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    description: str
    phases: List[WorkflowPhase]
    dependencies: Dict[str, List[str]]
    estimated_duration: int
    quality_gates: List[str]
    metadata: Dict[str, Any]
```

#### WorkflowResult
```python
@dataclass
class WorkflowResult:
    workflow_id: str
    status: WorkflowStatus
    results: Dict[str, Any]
    execution_time: int
    phases_executed: List[str]
    phases_failed: List[str]
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Learn optimal sequences from usage patterns
   - Predictive analytics for workflow optimization
   - Intelligent template recommendation

2. **Advanced Analytics**
   - Real-time performance dashboards
   - Predictive bottleneck detection
   - Quality trend analysis

3. **Multi-Project Support**
   - Cross-project workflow templates
   - Shared resource management
   - Portfolio-level analytics

4. **Agent Swarm Evolution**
   - Dedicated agents for each context
   - Multi-agent coordination protocols
   - Distributed workflow execution

### Contributing

The Workflow Composition Engine is designed for extensibility. To contribute:

1. **Custom Templates**: Add new workflow templates in `workflow/templates/`
2. **Context Handlers**: Implement new context execution logic
3. **Recovery Strategies**: Add new error recovery mechanisms
4. **Quality Gates**: Define new validation criteria

## Conclusion

The Workflow Composition Engine represents a significant advancement in development automation, providing:

- **Complete Automation**: Transform single requests into full workflows
- **Intelligent Orchestration**: Optimal context sequencing and transitions
- **Quality Assurance**: Built-in validation and quality gates
- **Error Resilience**: Comprehensive error handling and recovery
- **Performance Optimization**: Parallel execution and caching
- **Extensibility**: Customizable templates and strategies

This system establishes the foundation for truly autonomous software development workflows, enabling developers to focus on creative problem-solving while the system handles process orchestration and quality assurance.

---

**For additional support or questions, refer to the technical documentation or contact the development team.**
