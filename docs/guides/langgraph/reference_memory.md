# LangGraph Reference Memory

## Source
- **URL**: https://langchain-ai.github.io/langgraph/concepts/why-langgraph/
- **Accessed**: Current session
- **Purpose**: Building LangGraph agents with memory, tools, and human-in-the-loop capabilities

## Key LangGraph Features for Our Project

### 1. Reliability and Controllability
- **Moderation checks** and human-in-the-loop approvals
- **Context persistence** for long-running workflows  
- **Steerable agent actions** with built-in controls
- **State management** to keep agents on course

### 2. Low-level and Extensible
- **Fully descriptive primitives** free from rigid abstractions
- **Custom agent design** with complete control
- **Scalable multi-agent systems** with role-specific agents
- **Extensible architecture** for complex workflows

### 3. First-class Streaming Support
- **Token-by-token streaming** for real-time visibility
- **Intermediate step streaming** for agent reasoning transparency
- **Real-time action visibility** as workflows unfold

## Core Implementation Patterns

### State Management
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    messages: Annotated[list, "Chat messages"]
    current_step: Annotated[str, "Current workflow step"]
    project_requirements: Annotated[str, "Project requirements"]
    architecture_design: Annotated[str, "Architecture design"]
    generated_code: Annotated[str, "Generated code"]
    review_feedback: Annotated[str, "Review feedback"]
    human_approval: Annotated[bool, "Human approval status"]
    memory: Annotated[dict, "Persistent memory storage"]
```

### Memory Implementation
```python
from langchain.memory import ConversationBufferMemory
from langgraph.checkpoint.memory import MemorySaver

# Initialize memory
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="chat_history"
)

# Create memory saver for persistence
memory_saver = MemorySaver()

# Configure persistent memory
config = {
    "configurable": {
        "thread_id": "unique_thread_id",
        "user_id": "user_identifier"
    }
}
```

### Tool Integration
```python
from langchain.tools import tool

@tool
def search_codebase(query: str) -> str:
    """Search the codebase for relevant code examples."""
    return f"Found code examples for: {query}"

@tool
def validate_code(code: str) -> dict:
    """Validate generated code for syntax and best practices."""
    return {
        "is_valid": True,
        "issues": [],
        "suggestions": []
    }
```

### Human-in-the-Loop
```python
def human_approval_node(state: AgentState) -> AgentState:
    """Node for human approval and feedback."""
    approval_request = {
        "code_to_review": state.get("generated_code", ""),
        "architecture": state.get("architecture_design", ""),
        "requirements": state.get("project_requirements", ""),
        "review_feedback": state.get("review_feedback", "")
    }
    
    human_decision = simulate_human_approval(approval_request)
    
    return {
        **state,
        "human_approval": human_decision["approved"],
        "human_feedback": human_decision.get("feedback", ""),
        "approval_timestamp": datetime.now().isoformat()
    }
```

### Workflow Graph Creation
```python
# Create workflow graph
workflow = StateGraph(AgentState)

# Add nodes (agents)
workflow.add_node("requirements_analyst", requirements_agent)
workflow.add_node("architecture_designer", architecture_agent)
workflow.add_node("code_generator", code_generation_agent)
workflow.add_node("code_reviewer", code_review_agent)
workflow.add_node("human_approver", human_approval_node)

# Define edges and routing
workflow.add_edge("requirements_analyst", "architecture_designer")
workflow.add_edge("architecture_designer", "code_generator")
workflow.add_edge("code_generator", "code_reviewer")
workflow.add_conditional_edges(
    "code_reviewer",
    route_to_human_or_complete,
    {
        "human_approval": "human_approver",
        "complete": END
    }
)
workflow.add_edge("human_approver", "code_generator")

# Compile the graph
app = workflow.compile()
```

## Integration with Our Multi-Agent System

### LangGraph Workflow Manager Pattern
```python
class LangGraphWorkflowManager:
    """Manages LangGraph workflows for our multi-agent system."""
    
    def __init__(self):
        self.workflows = {}
        self.memory_saver = MemorySaver()
    
    def create_workflow(self, workflow_name: str, agents: dict) -> StateGraph:
        """Create a new LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        for agent_name, agent_config in agents.items():
            workflow.add_node(agent_name, agent_config["function"])
        
        # Add edges based on workflow definition
        self._add_workflow_edges(workflow, agents)
        
        # Compile workflow
        compiled_workflow = workflow.compile()
        self.workflows[workflow_name] = compiled_workflow
        
        return compiled_workflow
    
    def execute_workflow(self, workflow_name: str, initial_state: dict, config: dict = None):
        """Execute a LangGraph workflow."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow {workflow_name} not found")
        
        workflow = self.workflows[workflow_name]
        
        # Execute with memory and streaming
        if config and config.get("stream", False):
            return workflow.stream(initial_state, config=config)
        else:
            return workflow.invoke(initial_state, config=config)
```

### Agent Integration Pattern
```python
def create_langgraph_agent(agent_class: str, llm, tools: list = None) -> callable:
    """Create a LangGraph-compatible agent function."""
    
    def agent_function(state: AgentState) -> AgentState:
        """LangGraph agent function wrapper."""
        # Create agent instance
        agent = AgentFactory.create_agent(agent_class, llm=llm, tools=tools)
        
        # Execute agent
        result = agent.execute(state)
        
        # Return updated state
        return {**state, **result}
    
    return agent_function
```

## Advanced Features

### Time Travel and State Exploration
```python
# Access previous states for analysis
config = {
    "configurable": {
        "thread_id": "unique_thread_id"
    }
}

# Get current state
current_state = app.get_state(config)

# Access previous states
previous_states = app.get_state_history(config)

# Time travel to previous state
previous_state = app.get_state(config, checkpoint_id="previous_checkpoint_id")
```

### Streaming with Human-in-the-Loop
```python
# Configure streaming for human-in-the-loop
config = {
    "configurable": {
        "thread_id": "unique_thread_id"
    },
    "recursion_limit": 25,
    "stream": True
}

# Execute with streaming
for chunk in app.stream(
    {"messages": [{"role": "user", "content": "Create a web app"}]},
    config=config
):
    # Stream intermediate steps to UI
    if "human_approval" in chunk:
        # Trigger UI notification for human approval
        notify_human_for_approval(chunk["human_approval"])
    
    # Stream other steps
    print(f"Step: {chunk}")
```

## Best Practices for Our Project

### 1. State Management
- Use TypedDict for clear state structure
- Implement proper state validation
- Use memory for persistence across sessions
- Handle state transitions carefully

### 2. Error Handling
- Implement comprehensive error handling at each node
- Use error recovery mechanisms
- Provide fallback options
- Log errors for debugging

### 3. Performance Optimization
- Use streaming for real-time feedback
- Implement proper memory management
- Optimize tool usage
- Monitor workflow performance

### 4. Testing and Validation
- Test individual nodes in isolation
- Test complete workflows end-to-end
- Validate state transitions
- Test error scenarios

## Implementation Checklist for Our Project

- [ ] Define state structure with TypedDict
- [ ] Create agent functions compatible with LangGraph
- [ ] Implement memory management
- [ ] Add tool integration
- [ ] Implement human-in-the-loop approval
- [ ] Add error handling and recovery
- [ ] Configure streaming for real-time feedback
- [ ] Test individual nodes and complete workflows
- [ ] Implement state validation
- [ ] Add performance monitoring
- [ ] Document workflow configurations
- [ ] Create integration tests

## References

- **Official Documentation**: https://langchain-ai.github.io/langgraph/concepts/why-langgraph/
- **Tutorials**: https://langchain-ai.github.io/langgraph/tutorials/
- **Examples**: https://langchain-ai.github.io/langgraph/examples/
- **Complete Guide**: `docs/langgraph_agent_development_guide.md`

## Notes for Implementation

1. **Memory**: LangGraph provides built-in memory management with `MemorySaver` for persistent state across sessions
2. **Tools**: Can integrate with LangChain tools for enhanced agent capabilities
3. **Human-in-the-Loop**: Built-in support for human approval and feedback loops
4. **Streaming**: First-class support for real-time streaming of agent actions and reasoning
5. **State Management**: TypedDict-based state management with validation
6. **Error Handling**: Comprehensive error handling and recovery mechanisms
7. **Extensibility**: Low-level primitives for custom agent and workflow design

This reference should be used when implementing LangGraph-based workflows in our multi-agent system.
