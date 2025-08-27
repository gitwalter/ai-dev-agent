# LangGraph Agent Development Guide

## Overview

This guide provides comprehensive instructions for building powerful, adaptable AI agents using LangGraph, based on the [official LangGraph documentation](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/). LangGraph is designed for developers who want to build reliable, controllable, and extensible AI agents with first-class streaming support.

## Key LangGraph Features

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

## Core LangGraph Concepts

### State Management
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

# Define state structure
class AgentState(TypedDict):
    messages: Annotated[list, "Chat messages"]
    current_step: Annotated[str, "Current workflow step"]
    project_requirements: Annotated[str, "Project requirements"]
    architecture_design: Annotated[str, "Architecture design"]
    generated_code: Annotated[str, "Generated code"]
    review_feedback: Annotated[str, "Review feedback"]
    human_approval: Annotated[bool, "Human approval status"]
    memory: Annotated[dict, "Persistent memory storage"]
    recall_memories: Annotated[list, "Retrieved long-term memories"]
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

## Building LangGraph Agents with Long-Term Memory

### 1. Long-Term Memory Implementation
Based on the [LangChain long-term memory documentation](https://python.langchain.com/docs/versions/migrating_memory/long_term_memory_agent/), we can implement sophisticated memory systems using vector stores and structured knowledge triples.

```python
from langchain.vectorstores import InMemoryVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
import uuid

# Initialize vector store for long-term memory
recall_vector_store = InMemoryVectorStore(OpenAIEmbeddings())

# Define knowledge triple structure for structured memory
class KnowledgeTriple(TypedDict):
    subject: str
    predicate: str
    object_: str

# Memory tools for saving and retrieving memories
@tool
def save_recall_memory(memories: List[KnowledgeTriple], config: RunnableConfig) -> str:
    """Save memory to vectorstore for later semantic retrieval."""
    user_id = get_user_id(config)
    for memory in memories:
        serialized = " ".join(memory.values())
        document = Document(
            serialized,
            id=str(uuid.uuid4()),
            metadata={
                "user_id": user_id,
                **memory,
            },
        )
        recall_vector_store.add_documents([document])
    return memories

@tool
def search_recall_memories(query: str, config: RunnableConfig) -> List[str]:
    """Search for relevant memories in the vectorstore."""
    user_id = get_user_id(config)
    docs = recall_vector_store.similarity_search(
        query, k=5, filter=lambda doc: doc.metadata["user_id"] == user_id
    )
    return [doc.page_content for doc in docs]

def get_user_id(config: RunnableConfig) -> str:
    """Extract user ID from configuration."""
    return config.get("configurable", {}).get("user_id", "default_user")
```

### 2. Memory-Enabled State Management
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

# Enhanced state with long-term memory
class AgentState(TypedDict):
    messages: Annotated[list, "Chat messages"]
    current_step: Annotated[str, "Current workflow step"]
    project_requirements: Annotated[str, "Project requirements"]
    architecture_design: Annotated[str, "Architecture design"]
    generated_code: Annotated[str, "Generated code"]
    review_feedback: Annotated[str, "Review feedback"]
    human_approval: Annotated[bool, "Human approval status"]
    memory: Annotated[dict, "Persistent memory storage"]
    recall_memories: Annotated[list, "Retrieved long-term memories"]
    chat_history: Annotated[list, "Conversation history"]

# Memory loading node
def load_memories(state: AgentState, config: RunnableConfig) -> AgentState:
    """Load relevant memories based on current context."""
    user_id = get_user_id(config)
    
    # Extract context from current state
    context = extract_context_from_state(state)
    
    # Search for relevant memories
    relevant_memories = search_recall_memories(context, config)
    
    return {
        **state,
        "recall_memories": relevant_memories
    }

def extract_context_from_state(state: AgentState) -> str:
    """Extract context from current state for memory search."""
    context_parts = []
    
    if state.get("project_requirements"):
        context_parts.append(f"Project: {state['project_requirements']}")
    
    if state.get("architecture_design"):
        context_parts.append(f"Architecture: {state['architecture_design']}")
    
    if state.get("generated_code"):
        context_parts.append(f"Code: {state['generated_code'][:200]}...")
    
    if state.get("messages"):
        last_message = state["messages"][-1] if state["messages"] else ""
        context_parts.append(f"Current: {last_message}")
    
    return " ".join(context_parts)
```

### 3. Memory-Enhanced Agent Functions
```python
def memory_enhanced_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    """Agent function with long-term memory integration."""
    
    # Access memories
    recall_memories = state.get("recall_memories", [])
    chat_history = state.get("chat_history", [])
    
    # Create memory context
    memory_context = create_memory_context(recall_memories, chat_history)
    
    # Execute agent with memory context
    agent_response = execute_agent_with_memory(state, memory_context, config)
    
    # Extract and save new memories
    new_memories = extract_knowledge_triples(agent_response, state)
    if new_memories:
        save_recall_memory(new_memories, config)
    
    return {
        **state,
        "agent_response": agent_response,
        "new_memories_saved": len(new_memories) if new_memories else 0
    }

def create_memory_context(recall_memories: list, chat_history: list) -> str:
    """Create context from memories and chat history."""
    context_parts = []
    
    if recall_memories:
        context_parts.append("Relevant memories:")
        for memory in recall_memories[:3]:  # Limit to 3 most relevant
            context_parts.append(f"- {memory}")
    
    if chat_history:
        context_parts.append("Recent conversation:")
        for msg in chat_history[-3:]:  # Last 3 messages
            context_parts.append(f"- {msg}")
    
    return "\n".join(context_parts) if context_parts else "No relevant context found."

def extract_knowledge_triples(response: str, state: AgentState) -> List[KnowledgeTriple]:
    """Extract knowledge triples from agent response and state."""
    # This would use an LLM to extract structured knowledge
    # For now, return empty list
    return []
```

### 4. Structured Memory with Knowledge Graphs
```python
# Enhanced memory system with knowledge triples
@tool
def save_structured_memory(memories: List[KnowledgeTriple], config: RunnableConfig) -> str:
    """Save structured memory as knowledge triples."""
    user_id = get_user_id(config)
    
    for memory in memories:
        # Create document with structured metadata
        document = Document(
            content=f"{memory['subject']} {memory['predicate']} {memory['object_']}",
            id=str(uuid.uuid4()),
            metadata={
                "user_id": user_id,
                "subject": memory["subject"],
                "predicate": memory["predicate"],
                "object": memory["object_"],
                "memory_type": "knowledge_triple",
                "timestamp": datetime.now().isoformat()
            },
        )
        recall_vector_store.add_documents([document])
    
    return f"Saved {len(memories)} knowledge triples"

# Knowledge graph visualization (optional)
def visualize_knowledge_graph(user_id: str):
    """Visualize knowledge graph for a user."""
    import matplotlib.pyplot as plt
    import networkx as nx
    
    # Fetch user's knowledge triples
    records = recall_vector_store.similarity_search(
        "", k=50, filter=lambda doc: doc.metadata["user_id"] == user_id
    )
    
    # Create graph
    G = nx.DiGraph()
    for record in records:
        if record.metadata.get("memory_type") == "knowledge_triple":
            G.add_edge(
                record.metadata["subject"],
                record.metadata["object"],
                label=record.metadata["predicate"],
            )
    
    # Visualize
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(
        G, pos, with_labels=True, node_size=3000, node_color="lightblue",
        font_size=8, font_weight="bold", arrows=True
    )
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
    plt.title(f"Knowledge Graph for User {user_id}")
    plt.show()
```

### 5. Memory-Enhanced Workflow
```python
# Create memory-enhanced workflow
def create_memory_enhanced_workflow():
    """Create a workflow with long-term memory capabilities."""
    
    # Create state graph
    workflow = StateGraph(AgentState)
    
    # Add memory loading node
    workflow.add_node("load_memories", load_memories)
    
    # Add agent nodes with memory
    workflow.add_node("requirements_analyst", 
                     lambda state, config: memory_enhanced_agent(state, config))
    workflow.add_node("architecture_designer", 
                     lambda state, config: memory_enhanced_agent(state, config))
    workflow.add_node("code_generator", 
                     lambda state, config: memory_enhanced_agent(state, config))
    workflow.add_node("code_reviewer", 
                     lambda state, config: memory_enhanced_agent(state, config))
    
    # Add edges with memory loading
    workflow.add_edge(START, "load_memories")
    workflow.add_edge("load_memories", "requirements_analyst")
    workflow.add_edge("requirements_analyst", "architecture_designer")
    workflow.add_edge("architecture_designer", "code_generator")
    workflow.add_edge("code_generator", "code_reviewer")
    workflow.add_edge("code_reviewer", END)
    
    # Compile with memory saver
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Usage with memory
config = {
    "configurable": {
        "user_id": "user_123",
        "thread_id": "thread_456"
    }
}

# Execute with memory
app = create_memory_enhanced_workflow()
result = app.invoke(
    {"messages": [{"role": "user", "content": "Create a calculator app"}]},
    config=config
)
```

### 6. Memory Persistence and Retrieval
```python
# Configure persistent memory with user isolation
def configure_memory_for_user(user_id: str, thread_id: str):
    """Configure memory system for specific user and thread."""
    config = {
        "configurable": {
            "user_id": user_id,
            "thread_id": thread_id
        }
    }
    return config

# Memory retrieval across sessions
def retrieve_user_memories(user_id: str, query: str = None) -> List[str]:
    """Retrieve memories for a specific user."""
    if query:
        docs = recall_vector_store.similarity_search(
            query, k=10, filter=lambda doc: doc.metadata["user_id"] == user_id
        )
    else:
        docs = recall_vector_store.similarity_search(
            "", k=20, filter=lambda doc: doc.metadata["user_id"] == user_id
        )
    
    return [doc.page_content for doc in docs]

# Memory analysis and insights
def analyze_user_memory_patterns(user_id: str) -> dict:
    """Analyze memory patterns for a user."""
    memories = retrieve_user_memories(user_id)
    
    # Extract patterns (simplified)
    patterns = {
        "total_memories": len(memories),
        "memory_types": {},
        "frequent_subjects": {},
        "recent_activity": []
    }
    
    return patterns
```

## Implementing Tools in LangGraph Agents

### 1. Tool Definition
```python
from langchain.tools import tool
from typing import List

@tool
def search_codebase(query: str) -> str:
    """Search the codebase for relevant code examples."""
    # Implementation for codebase search
    return f"Found code examples for: {query}"

@tool
def validate_code(code: str) -> dict:
    """Validate generated code for syntax and best practices."""
    # Implementation for code validation
    return {
        "is_valid": True,
        "issues": [],
        "suggestions": []
    }

@tool
def generate_tests(code: str) -> str:
    """Generate unit tests for the provided code."""
    # Implementation for test generation
    return f"Generated tests for: {code}"
```

### 2. Tool Integration in Agents
```python
def code_generator_agent(state: AgentState) -> AgentState:
    """Code generator agent with tool usage."""
    
    # Get tools
    tools = [search_codebase, validate_code, generate_tests]
    
    # Create agent with tools
    agent = create_agent_with_tools(
        llm=llm,
        tools=tools,
        system_prompt="You are an expert code generator."
    )
    
    # Execute with tools
    response = agent.invoke({
        "input": state["project_requirements"],
        "tools": tools
    })
    
    return {
        **state,
        "generated_code": response["output"],
        "tool_usage": response.get("intermediate_steps", [])
    }
```

### 3. Tool Selection and Routing
```python
def route_tools(state: AgentState) -> List[str]:
    """Route to appropriate tools based on current state."""
    current_step = state.get("current_step", "")
    
    if current_step == "code_generation":
        return ["search_codebase", "validate_code"]
    elif current_step == "testing":
        return ["generate_tests", "validate_code"]
    else:
        return []
```

## Human-in-the-Loop Implementation

### 1. Human Approval Node
```python
def human_approval_node(state: AgentState) -> AgentState:
    """Node for human approval and feedback."""
    
    # Prepare approval request
    approval_request = {
        "code_to_review": state.get("generated_code", ""),
        "architecture": state.get("architecture_design", ""),
        "requirements": state.get("project_requirements", ""),
        "review_feedback": state.get("review_feedback", "")
    }
    
    # In a real implementation, this would trigger a UI notification
    # For now, we'll simulate human approval
    human_decision = simulate_human_approval(approval_request)
    
    return {
        **state,
        "human_approval": human_decision["approved"],
        "human_feedback": human_decision.get("feedback", ""),
        "approval_timestamp": datetime.now().isoformat()
    }

def simulate_human_approval(request: dict) -> dict:
    """Simulate human approval process."""
    # In production, this would integrate with UI components
    # For testing, we'll auto-approve with some conditions
    code_quality = assess_code_quality(request["code_to_review"])
    
    if code_quality > 0.8:
        return {
            "approved": True,
            "feedback": "Code looks good, approved."
        }
    else:
        return {
            "approved": False,
            "feedback": "Code needs improvement. Please revise."
        }
```

### 2. Conditional Routing Based on Human Input
```python
def route_to_human_or_complete(state: AgentState) -> str:
    """Route workflow based on human approval status."""
    
    if state.get("human_approval", False):
        return "complete"
    else:
        return "human_approval"

def route_with_human_feedback(state: AgentState) -> str:
    """Route based on human feedback and approval status."""
    
    human_approval = state.get("human_approval", False)
    feedback = state.get("human_feedback", "")
    
    if human_approval:
        return "complete"
    elif "revise" in feedback.lower():
        return "code_generator"  # Go back to code generation
    elif "review" in feedback.lower():
        return "code_reviewer"   # Go back to code review
    else:
        return "human_approval"  # Stay in human approval
```

### 3. Human-in-the-Loop with Streaming
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

## Advanced LangGraph Features

### 1. Time Travel and State Exploration
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

### 2. Custom State Validation
```python
from pydantic import BaseModel, Field
from typing import Optional

class ValidatedAgentState(BaseModel):
    messages: list = Field(description="Chat messages")
    current_step: str = Field(description="Current workflow step")
    project_requirements: Optional[str] = Field(description="Project requirements")
    architecture_design: Optional[str] = Field(description="Architecture design")
    generated_code: Optional[str] = Field(description="Generated code")
    
    class Config:
        extra = "allow"  # Allow additional fields

# Use validated state in workflow
def validated_agent(state: ValidatedAgentState) -> ValidatedAgentState:
    # State is automatically validated
    return state
```

### 3. Error Handling and Recovery
```python
def agent_with_error_handling(state: AgentState) -> AgentState:
    """Agent with comprehensive error handling."""
    
    try:
        # Attempt agent execution
        result = execute_agent_logic(state)
        return {**state, **result}
    
    except Exception as e:
        # Log error
        logger.error(f"Agent execution failed: {e}")
        
        # Return error state
        return {
            **state,
            "error": str(e),
            "error_timestamp": datetime.now().isoformat(),
            "status": "error"
        }

def error_recovery_node(state: AgentState) -> AgentState:
    """Node for handling and recovering from errors."""
    
    if state.get("status") == "error":
        # Attempt recovery
        recovery_result = attempt_recovery(state)
        
        if recovery_result["success"]:
            return {
                **state,
                "status": "recovered",
                "recovery_attempts": state.get("recovery_attempts", 0) + 1
            }
        else:
            # Escalate to human
            return {
                **state,
                "status": "needs_human_intervention",
                "escalation_reason": recovery_result["reason"]
            }
    
    return state
```

## Integration with Our Multi-Agent System

### 1. LangGraph Workflow Manager with Memory
```python
class LangGraphWorkflowManager:
    """Manages LangGraph workflows for our multi-agent system with long-term memory."""
    
    def __init__(self):
        self.workflows = {}
        self.memory_saver = MemorySaver()
        self.recall_vector_store = InMemoryVectorStore(OpenAIEmbeddings())
    
    def create_memory_enhanced_workflow(self, workflow_name: str, agents: dict) -> StateGraph:
        """Create a new LangGraph workflow with memory capabilities."""
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add memory loading node
        workflow.add_node("load_memories", load_memories)
        
        # Add agent nodes with memory enhancement
        for agent_name, agent_config in agents.items():
            memory_enhanced_agent = lambda state, config, agent_func=agent_config["function"]: \
                memory_enhanced_agent_wrapper(state, config, agent_func)
            workflow.add_node(agent_name, memory_enhanced_agent)
        
        # Add edges with memory loading
        workflow.add_edge(START, "load_memories")
        workflow.add_edge("load_memories", list(agents.keys())[0])
        
        # Add remaining edges
        agent_names = list(agents.keys())
        for i in range(len(agent_names) - 1):
            workflow.add_edge(agent_names[i], agent_names[i + 1])
        
        # Compile workflow
        compiled_workflow = workflow.compile(checkpointer=self.memory_saver)
        self.workflows[workflow_name] = compiled_workflow
        
        return compiled_workflow
    
    def execute_workflow(self, workflow_name: str, initial_state: dict, config: dict = None):
        """Execute a LangGraph workflow with memory."""
        
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow {workflow_name} not found")
        
        workflow = self.workflows[workflow_name]
        
        # Execute with memory and streaming
        if config and config.get("stream", False):
            return workflow.stream(initial_state, config=config)
        else:
            return workflow.invoke(initial_state, config=config)
    
    def get_user_memories(self, user_id: str, query: str = None) -> List[str]:
        """Retrieve memories for a specific user."""
        return retrieve_user_memories(user_id, query)
    
    def analyze_user_patterns(self, user_id: str) -> dict:
        """Analyze memory patterns for a user."""
        return analyze_user_memory_patterns(user_id)
```

### 2. Memory-Enhanced Agent Integration Pattern
```python
def create_memory_enhanced_langgraph_agent(agent_class: str, llm, tools: list = None) -> callable:
    """Create a LangGraph-compatible agent function with memory enhancement."""
    
    def memory_enhanced_agent_function(state: AgentState, config: RunnableConfig) -> AgentState:
        """LangGraph agent function wrapper with memory."""
        
        # Create agent instance
        agent = AgentFactory.create_agent(agent_class, llm=llm, tools=tools)
        
        # Enhance with memory context
        memory_context = create_memory_context(
            state.get("recall_memories", []),
            state.get("chat_history", [])
        )
        
        # Execute agent with memory
        result = agent.execute({**state, "memory_context": memory_context})
        
        # Extract and save new memories
        new_memories = extract_knowledge_triples(result.get("output", ""), state)
        if new_memories:
            save_recall_memory(new_memories, config)
        
        # Return updated state
        return {**state, **result, "new_memories": new_memories}
    
    return memory_enhanced_agent_function

# Usage in workflow
workflow_manager = LangGraphWorkflowManager()

# Create memory-enhanced agents
agents = {
    "requirements_analyst": {
        "function": create_memory_enhanced_langgraph_agent("requirements_analyst", llm)
    },
    "architecture_designer": {
        "function": create_memory_enhanced_langgraph_agent("architecture_designer", llm)
    },
    "code_generator": {
        "function": create_memory_enhanced_langgraph_agent("code_generator", llm, 
                                                         tools=[search_codebase, validate_code])
    },
    "code_reviewer": {
        "function": create_memory_enhanced_langgraph_agent("code_reviewer", llm)
    }
}

# Create and execute memory-enhanced workflow
workflow = workflow_manager.create_memory_enhanced_workflow("software_development", agents)
config = {"configurable": {"user_id": "user_123", "thread_id": "thread_456"}}

result = workflow_manager.execute_workflow(
    "software_development",
    {"messages": [{"role": "user", "content": "Create a calculator app"}]},
    config=config
)
```

## Best Practices

### 1. State Management
- Use TypedDict for clear state structure
- Implement proper state validation
- Use memory for persistence across sessions
- Handle state transitions carefully

### 2. Memory Management
- Use vector stores for semantic memory retrieval
- Implement structured knowledge triples for complex relationships
- Separate user memories for privacy and isolation
- Regularly analyze and clean up old memories
- Use memory context to enhance agent responses

### 3. Error Handling
- Implement comprehensive error handling at each node
- Use error recovery mechanisms
- Provide fallback options
- Log errors for debugging

### 4. Performance Optimization
- Use streaming for real-time feedback
- Implement proper memory management
- Optimize tool usage
- Monitor workflow performance
- Cache frequently accessed memories

### 5. Testing and Validation
- Test individual nodes in isolation
- Test complete workflows end-to-end
- Validate state transitions
- Test error scenarios
- Test memory persistence and retrieval

## References

- [Official LangGraph Documentation](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/)
- [LangChain Long-Term Memory Documentation](https://python.langchain.com/docs/versions/migrating_memory/long_term_memory_agent/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph Examples](https://langchain-ai.github.io/langgraph/examples/)

## Implementation Checklist

- [ ] Define state structure with TypedDict including memory fields
- [ ] Create agent functions compatible with LangGraph
- [ ] Implement long-term memory with vector stores
- [ ] Add structured knowledge triple extraction
- [ ] Implement memory loading and retrieval nodes
- [ ] Add tool integration with memory context
- [ ] Implement human-in-the-loop approval with memory
- [ ] Add error handling and recovery
- [ ] Configure streaming for real-time feedback
- [ ] Test individual nodes and complete workflows
- [ ] Implement state validation
- [ ] Add performance monitoring
- [ ] Document workflow configurations
- [ ] Create integration tests
- [ ] Implement memory analysis and visualization
- [ ] Add memory cleanup and maintenance procedures
