# Clean Onion Architecture

**Purpose**: Practical onion architecture for AI agent systems with proper dependency inversion.

## Core Principle

**Dependency Inversion**: Outer layers depend on inner layers. Inner layers have no dependencies on outer layers.

```
┌─────────────────────────────────────────────────┐
│                Infrastructure                   │ ← Databases, APIs, Files
├─────────────────────────────────────────────────┤
│                User Interface                   │ ← Web UI, CLI, REST API  
├─────────────────────────────────────────────────┤
│              Application Services               │ ← Workflow orchestration
├─────────────────────────────────────────────────┤
│                 Domain Logic                    │ ← Business rules, agents
└─────────────────────────────────────────────────┘
                     Core ↑
```

## Layer Responsibilities

### **Core Domain Layer** (Center)
- **Agent behavior logic** - How agents reason and make decisions
- **Business rules** - Validation, constraints, policies  
- **Domain models** - Core entities and value objects
- **No dependencies** - Pure logic, no framework coupling

```python
class Agent:
    """Core agent logic - no external dependencies."""
    
    def process_request(self, request: Request) -> Decision:
        # Pure business logic
        return self._apply_reasoning_rules(request)
```

### **Application Services Layer**
- **Workflow orchestration** - Coordinates multiple agents
- **Use case implementation** - Specific application workflows
- **Agent coordination** - Inter-agent communication patterns
- **Depends only on domain** - Uses domain models and services

```python
class WorkflowOrchestrator:
    """Orchestrates agent workflows."""
    
    def __init__(self, agents: List[Agent]):
        self.agents = agents  # Dependency injection
    
    def execute_development_workflow(self, project: Project) -> Result:
        # Coordinates agents to complete project
        return self._orchestrate_agents(project)
```

### **User Interface Layer**
- **REST API endpoints** - HTTP interface for external systems
- **Web UI controllers** - User interface components
- **CLI interfaces** - Command-line interaction
- **Depends on application layer** - Calls application services

```python
class AgentAPI:
    """REST API for agent system."""
    
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
    
    def create_project(self, request_data: dict) -> dict:
        project = Project.from_dict(request_data)
        result = self.orchestrator.execute_development_workflow(project)
        return result.to_dict()
```

### **Infrastructure Layer** (Outermost)
- **Database access** - Persistent storage implementations
- **External APIs** - LLM providers, third-party services
- **File system** - Code generation, file operations
- **Depends on everything** - Implements interfaces defined by inner layers

```python
class DatabaseAgentRepository:
    """Database implementation of agent storage."""
    
    def save_agent_state(self, agent: Agent) -> None:
        # Database-specific implementation
        self.db.insert(agent.to_record())
```

## Benefits

### **1. Testability**
- **Mock outer layers** - Test domain logic in isolation
- **Independent testing** - Each layer can be tested separately
- **Fast unit tests** - Core logic tests run without infrastructure

### **2. Flexibility**
- **Swap implementations** - Change databases, UI frameworks, LLM providers
- **Multiple interfaces** - Support web UI, CLI, API simultaneously
- **Provider independence** - Switch between OpenAI, Anthropic, Google easily

### **3. Maintainability**
- **Clear separation** - Each layer has single responsibility
- **Reduced coupling** - Changes in outer layers don't affect core logic
- **Dependency direction** - Always flows inward, easier to understand

## AI Agent System Example

```python
# Domain Layer - Core agent logic
class CodeGeneratorAgent:
    def generate_code(self, requirements: Requirements) -> CodeSolution:
        # Pure agent reasoning logic
        return self._apply_coding_patterns(requirements)

# Application Layer - Workflow coordination  
class DevelopmentWorkflow:
    def __init__(self, code_gen: CodeGeneratorAgent, reviewer: ReviewerAgent):
        self.code_generator = code_gen
        self.reviewer = reviewer
    
    def develop_feature(self, feature_spec: FeatureSpec) -> Implementation:
        code = self.code_generator.generate_code(feature_spec.requirements)
        review = self.reviewer.review_code(code)
        return Implementation(code, review)

# Infrastructure Layer - LLM provider
class OpenAICodeGenerator:
    """OpenAI implementation of code generation."""
    
    def __init__(self, agent: CodeGeneratorAgent, client: OpenAIClient):
        self.agent = agent
        self.client = client
    
    def generate_code(self, requirements: Requirements) -> CodeSolution:
        # Get decision from domain agent
        solution = self.agent.generate_code(requirements)
        
        # Execute via OpenAI API
        response = self.client.complete(solution.to_prompt())
        return CodeSolution.from_response(response)
```

## Implementation Guidelines

### **1. Dependency Injection**
- Use constructor injection for dependencies
- Define interfaces in inner layers, implement in outer layers
- Use dependency injection containers for complex systems

### **2. Interface Segregation**
- Small, focused interfaces for each capability
- Separate read and write operations where appropriate
- Design interfaces based on client needs, not implementation

### **3. Error Handling**
- Domain exceptions for business rule violations
- Infrastructure exceptions for technical failures
- Application layer coordinates error handling across layers

## Benefits for AI Systems

### **1. Provider Flexibility**
- Switch between LLM providers (OpenAI, Anthropic, Google) without changing core logic
- Support multiple providers simultaneously for different agent types
- Easy A/B testing of different providers

### **2. Agent Composability**
- Mix and match agents in different workflows
- Test agent interactions without external dependencies
- Easily add new agent types

### **3. Deployment Options**
- Same core logic works in web apps, CLI tools, batch processing
- Deploy to different cloud providers without code changes
- Support both local and cloud-based execution

---

**Key Insight**: Clean onion architecture enables building flexible, testable AI agent systems that can adapt to changing requirements and technology choices.
