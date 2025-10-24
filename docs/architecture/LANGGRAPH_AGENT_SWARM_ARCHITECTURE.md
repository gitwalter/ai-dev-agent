# LangGraph Agent Swarm Architecture

**Version**: 1.0  
**Date**: 2025-01-24  
**Status**: ✅ Active Architecture  
**Framework**: LangGraph + LangChain v1.0

---

## Executive Summary

This document defines our strategic architecture for building multi-agent AI systems using LangGraph and LangChain. It consolidates best practices from official documentation, real-world patterns, and our project requirements to create a scalable, maintainable, and production-ready agent swarm framework.

---

## 1. Core Architecture Principles

### 1.1 Foundation: ReAct Pattern

All specialist agents follow the **ReAct (Reasoning and Acting)** pattern:

```
User Input → Reason → Select Tool → Act → Observe → Repeat → Final Answer
```

**Key Benefits:**
- **Explainable**: Each step shows reasoning
- **Flexible**: Can use tools dynamically  
- **Debuggable**: Easy to trace decision paths
- **Maintainable**: Clear separation of concerns

### 1.2 Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERVISOR LAYER                         │
│  (Coordination, Routing, Decision Making)                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Complexity   │  │    Agent     │  │    Router    │     │
│  │  Analyzer    │→ │  Selector    │→ │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                   SPECIALIST AGENT LAYER                    │
│  (ReAct Agents with Tools)                                  │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │Requirements│  │    Code    │  │    Docs    │           │
│  │  Analyst   │  │ Generator  │  │ Generator  │  ...      │
│  │  + Tools   │  │  + Tools   │  │  + Tools   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                      STATE LAYER                            │
│  (TypedDict with Annotated Reducers)                        │
│                                                              │
│  messages, context, artifacts, errors, metrics, etc.        │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 State Management Philosophy

**Use TypedDict with Annotated Reducers for concurrent writes:**

```python
from typing import TypedDict, Annotated
import operator

class SwarmState(TypedDict):
    # Single values (last write wins)
    project_context: str
    next_agent: Optional[str]
    current_step: str
    
    # Lists (accumulate with operator.add)
    messages: Annotated[List[dict], operator.add]
    required_agents: Annotated[List[str], operator.add]
    completed_agents: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    
    # Dicts (merge/update)
    requirements: dict
    code_files: dict
    documentation: dict
    metrics: dict
```

**Why This Matters:**
- **Concurrent Updates**: Multiple agents can update lists simultaneously
- **Clear Semantics**: Explicit about how values combine
- **Type Safety**: Full IDE support and runtime validation

---

## 2. Component Specifications

### 2.1 ReAct Agent Creation (Official Pattern)

**Using `create_react_agent` from LangGraph:**

```python
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# 1. Define tools
@tool
def analyze_requirements(context: str) -> dict:
    """Analyze project requirements and extract key information."""
    return {"analyzed": True, "context": context}

@tool
def search_documentation(query: str) -> str:
    """Search documentation for relevant information."""
    return f"Documentation results for: {query}"

# 2. Create LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# 3. Create ReAct agent
agent = create_react_agent(
    model=llm,
    tools=[analyze_requirements, search_documentation],
    state_modifier="You are an expert Requirements Analyst. Analyze project requirements thoroughly."
)
```

**Critical Parameters:**
- `model`: The LLM instance
- `tools`: List of callable tools (use @tool decorator)
- `state_modifier`: System prompt or function to modify state

### 2.2 Supervisor Node Pattern

**Supervisors coordinate but don't have tools:**

```python
async def complexity_analyzer_node(state: SwarmState) -> dict:
    """Analyze project complexity and determine required agents."""
    
    # Create a simple LLM (no tools)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    # Create structured output parser
    parser = JsonOutputParser()
    
    # Build prompt
    prompt = PromptTemplate(
        template="""Analyze this project and determine complexity:
        
Project: {project_context}

Return JSON:
{{
    "complexity": "low|medium|high",
    "required_agents": ["agent1", "agent2", ...],
    "reasoning": "why these agents"
}}""",
        input_variables=["project_context"]
    )
    
    # Execute
    chain = prompt | llm | parser
    result = await chain.ainvoke({"project_context": state["project_context"]})
    
    return {
        "project_complexity": result["complexity"],
        "required_agents": result["required_agents"]
    }
```

### 2.3 Agent Wrapper Pattern

**Wrap ReAct agents to integrate with supervisor workflow:**

```python
async def requirements_analyst_wrapper(state: SwarmState) -> dict:
    """Wrap requirements analyst ReAct agent."""
    
    # Create agent (cached if exists)
    agent = await create_requirements_analyst_agent()
    
    # Prepare input in agent's expected format
    agent_input = {
        "messages": [
            {"role": "user", "content": f"Analyze requirements: {state['project_context']}"}
        ]
    }
    
    # Invoke ReAct agent (runs in event loop)
    result = await asyncio.to_thread(agent.invoke, agent_input)
    
    # Extract output from agent's message stream
    output = result.get("messages", [])[-1].content if result.get("messages") else {}
    
    # Return partial state update
    return {
        "requirements": {"analysis": output},
        "completed_agents": ["requirements_analyst"]
    }
```

### 2.4 StateGraph Assembly

**Build the workflow graph:**

```python
def create_swarm_workflow() -> StateGraph:
    """Create the complete swarm workflow."""
    
    # Initialize graph with state schema
    workflow = StateGraph(SwarmState)
    
    # Add supervisor nodes
    workflow.add_node("complexity_analyzer", complexity_analyzer_node)
    workflow.add_node("agent_selector", agent_selector_node)
    workflow.add_node("router", router_node)
    
    # Add specialist agent wrappers
    workflow.add_node("requirements_analyst", requirements_analyst_wrapper)
    workflow.add_node("code_generator", code_generator_wrapper)
    workflow.add_node("documentation_generator", documentation_generator_wrapper)
    
    # Define flow
    workflow.set_entry_point("complexity_analyzer")
    workflow.add_edge("complexity_analyzer", "agent_selector")
    workflow.add_edge("agent_selector", "router")
    
    # Conditional routing to specialist agents
    workflow.add_conditional_edges(
        "router",
        route_decision,  # Function that returns agent name or "END"
        {
            "requirements_analyst": "requirements_analyst",
            "code_generator": "code_generator",
            "documentation_generator": "documentation_generator",
            "END": END
        }
    )
    
    # All specialists loop back to router
    workflow.add_edge("requirements_analyst", "router")
    workflow.add_edge("code_generator", "router")
    workflow.add_edge("documentation_generator", "router")
    
    # Compile with checkpointer for memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
```

---

## 3. Integration Patterns

### 3.1 LangSmith Integration

**Centralized Prompt Management:**

```python
class PromptLoader:
    """Load prompts from LangSmith with fallbacks."""
    
    def __init__(self, use_langsmith: bool = True):
        self.use_langsmith = use_langsmith and hub is not None
        self._cache = {}
    
    async def load_prompt(
        self,
        prompt_name: str,
        fallback_template: str,
        input_variables: List[str] = None
    ) -> PromptTemplate:
        """Load prompt from LangSmith or use fallback."""
        
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        if self.use_langsmith:
            try:
                prompt = await asyncio.to_thread(hub.pull, prompt_name)
                self._cache[prompt_name] = prompt
                return prompt
            except Exception as e:
                logger.warning(f"LangSmith failed: {e}")
        
        # Fallback to local template
        prompt = PromptTemplate(
            template=fallback_template,
            input_variables=input_variables or []
        )
        self._cache[prompt_name] = prompt
        return prompt
```

**Benefits:**
- Version control for prompts
- A/B testing capabilities
- Team collaboration
- Prompt analytics

### 3.2 LangGraph Studio Integration

**Export for visualization:**

```python
# At end of workflow file
_default_instance = None

def get_graph():
    """Get compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None:
        llm_config = {"model_name": "gemini-2.5-flash", "temperature": 0}
        _default_instance = AgentSwarm(llm_config)
    return _default_instance.workflow

# Studio expects 'graph' variable
graph = get_graph()
```

**langgraph.json configuration:**

```json
{
  "dependencies": ["requirements.txt"],
  "graphs": {
    "development_workflow": "workflow/langgraph_workflow.py:graph"
  },
  "env": {
    "GOOGLE_API_KEY": "${GOOGLE_API_KEY}",
    "LANGCHAIN_API_KEY": "${LANGCHAIN_API_KEY}",
    "LANGCHAIN_TRACING_V2": "true",
    "LANGCHAIN_PROJECT": "ai-dev-agent"
  }
}
```

### 3.3 Streamlit Integration

**User interface wrapper:**

```python
import streamlit as st
from workflow.langgraph_workflow import LangGraphWorkflowManager

# Initialize
if "workflow" not in st.session_state:
    llm_config = {"model_name": "gemini-2.5-flash", "temperature": 0}
    st.session_state.workflow = LangGraphWorkflowManager(llm_config)

# User input
project_context = st.text_area("Describe your project:")

if st.button("Generate"):
    with st.spinner("Agent swarm working..."):
        result = await st.session_state.workflow.execute_swarm(
            project_context,
            session_id=st.session_state.session_id
        )
    
    # Display results
    st.success("Complete!")
    st.json(result)
```

---

## 4. Tool Development Guidelines

### 4.1 Tool Definition Pattern

**Use @tool decorator with clear docstrings:**

```python
from langchain_core.tools import tool

@tool
def search_codebase(query: str, file_pattern: str = "*.py") -> List[dict]:
    """
    Search the codebase for specific patterns or text.
    
    Args:
        query: The text or pattern to search for
        file_pattern: Glob pattern for files to search (default: "*.py")
        
    Returns:
        List of matches with file paths and line numbers
        
    Example:
        search_codebase("def process_data", "*.py")
    """
    # Implementation
    results = []
    # ... search logic ...
    return results
```

**Critical Elements:**
- **Clear docstring**: LLM uses this to decide when to use the tool
- **Type hints**: Enable validation and IDE support
- **Error handling**: Never crash, return error info in result
- **Fast execution**: Tools should complete quickly (<5 seconds)

### 4.2 Tool Categories

**Development Tools:**
- `analyze_requirements_tool`: Extract and analyze requirements
- `validate_architecture_tool`: Check architecture against best practices
- `generate_file_tool`: Create code/config files
- `lint_code_tool`: Run code quality checks
- `run_tests_tool`: Execute test suites

**Research Tools:**
- `search_documentation_tool`: Search project docs
- `web_search_tool`: Search internet for information
- `code_search_tool`: Find patterns in codebase
- `api_lookup_tool`: Check API documentation

**Coordination Tools:**
- `create_subtask_tool`: Break down complex tasks
- `delegate_to_agent_tool`: Hand off to specialist
- `request_human_feedback_tool`: Get user input
- `validate_output_tool`: Check quality gates

---

## 5. Best Practices

### 5.1 Agent Design

**✅ DO:**
- Create focused agents with single responsibilities
- Use clear, descriptive system prompts
- Provide 3-5 relevant tools per agent
- Cache agent instances for reuse
- Log agent decisions for debugging

**❌ DON'T:**
- Create god agents with too many responsibilities
- Give agents 20+ tools (causes confusion)
- Create agents without tools (use supervisors instead)
- Recreate agents on every invocation
- Ignore error handling

### 5.2 State Management

**✅ DO:**
- Use TypedDict for clear state schemas
- Use Annotated with operator.add for lists
- Keep state flat when possible
- Include metadata (timestamps, agents used, etc.)
- Validate state transitions

**❌ DON'T:**
- Use deeply nested state structures
- Modify state directly (return partial updates)
- Store large objects in state (use references)
- Forget to handle concurrent updates
- Mix state concerns

### 5.3 Workflow Design

**✅ DO:**
- Start with simple, linear flows
- Add conditional routing as needed
- Use supervisor pattern for coordination
- Implement human-in-the-loop checkpoints
- Add comprehensive logging

**❌ DON'T:**
- Create overly complex graphs initially
- Bypass error handling
- Forget to handle END conditions
- Create circular dependencies
- Skip testing individual nodes

---

## 6. Scalability Roadmap

### Phase 1: Core Swarm (Current)

**Implemented:**
- ✅ 3 specialist agents with ReAct pattern
- ✅ 3 supervisor nodes for coordination
- ✅ TypedDict state management
- ✅ LangSmith prompt integration
- ✅ Basic tools per agent

**Status**: Production ready for simple-medium projects

### Phase 2: Enhanced Capabilities (Q1 2025)

**Planned:**
- [ ] Add 5 more specialist agents:
  - Testing specialist
  - Security analyst  
  - Performance optimizer
  - DevOps engineer
  - UI/UX designer

- [ ] Enhanced tools:
  - Database schema tools
  - API testing tools
  - Deployment tools
  - Monitoring tools

- [ ] Human-in-the-loop integration:
  - Approval checkpoints
  - Feedback loops
  - Manual override capabilities

### Phase 3: Advanced Features (Q2 2025)

**Planned:**
- [ ] Dynamic agent creation based on project type
- [ ] Agent learning from previous projects
- [ ] Multi-project coordination
- [ ] Resource optimization
- [ ] Cost tracking and optimization

### Phase 4: Enterprise Scale (Q3 2025)

**Planned:**
- [ ] Distributed agent execution
- [ ] Multi-tenant support
- [ ] Advanced security features
- [ ] Enterprise integrations
- [ ] Analytics dashboard

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Test individual components:**

```python
import pytest
from workflow.langgraph_workflow import AgentSwarm

@pytest.mark.asyncio
async def test_requirements_analyst_agent():
    """Test requirements analyst creates valid output."""
    llm_config = {"model_name": "gemini-2.5-flash", "temperature": 0}
    swarm = AgentSwarm(llm_config)
    
    agent = await swarm._create_requirements_analyst_agent()
    assert agent is not None
    
    result = await asyncio.to_thread(
        agent.invoke,
        {"messages": [{"role": "user", "content": "Create a REST API"}]}
    )
    
    assert "messages" in result
    assert len(result["messages"]) > 0
```

### 7.2 Integration Tests

**Test complete workflows:**

```python
@pytest.mark.asyncio
async def test_complete_swarm_execution():
    """Test full swarm execution from start to finish."""
    llm_config = {"model_name": "gemini-2.5-flash", "temperature": 0}
    swarm = AgentSwarm(llm_config)
    
    result = await swarm.execute_swarm(
        "Create a simple Python calculator with tests"
    )
    
    assert result["current_step"] != "error"
    assert len(result["completed_agents"]) > 0
    assert "requirements" in result
    assert result["errors"] == []
```

### 7.3 Studio Testing

**Manual verification:**

1. Open project in LangGraph Studio
2. Select `development_workflow` graph
3. Build the graph
4. Provide test input
5. Step through execution
6. Verify each node output
7. Check conditional routing
8. Validate final state

---

## 8. Monitoring and Observability

### 8.1 LangSmith Tracing

**Automatic tracing enabled:**

```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ai-dev-agent"
```

**Provides:**
- Complete execution traces
- Token usage tracking
- Latency measurements
- Error tracking
- Cost analysis

### 8.2 Custom Metrics

**Track business metrics:**

```python
class SwarmMetrics:
    """Track swarm execution metrics."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.agents_used = []
        self.tools_called = {}
        self.tokens_used = 0
        self.cost = 0.0
    
    def record_agent(self, agent_name: str):
        """Record agent usage."""
        self.agents_used.append({
            "name": agent_name,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_tool_call(self, tool_name: str):
        """Record tool usage."""
        self.tools_called[tool_name] = self.tools_called.get(tool_name, 0) + 1
```

---

## 9. Deployment Considerations

### 9.1 Environment Configuration

**Required environment variables:**

```bash
# API Keys
export GOOGLE_API_KEY="your-google-api-key"
export LANGCHAIN_API_KEY="your-langsmith-key"

# LangSmith Configuration
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_PROJECT="ai-dev-agent"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# Application Configuration
export DATABASE_URI="postgresql://user:pass@localhost/db"
export REDIS_URI="redis://localhost:6379"
export LOG_LEVEL="INFO"
```

### 9.2 Resource Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB

**Recommended:**
- CPU: 4+ cores
- RAM: 8+ GB  
- Disk: 50+ GB
- GPU: Optional (for local LLMs)

### 9.3 Scaling Strategies

**Horizontal Scaling:**
- Deploy multiple workflow instances
- Use load balancer for request distribution
- Share state via Redis/PostgreSQL
- Implement request queuing

**Vertical Scaling:**
- Increase CPU/RAM per instance
- Optimize agent caching
- Tune batch sizes
- Enable concurrent tool execution

---

## 10. Migration Path

### From Legacy Agents to LangGraph

**Step-by-step migration:**

1. **Identify** existing agent logic
2. **Extract** core functionality and tools
3. **Create** @tool decorated functions
4. **Build** ReAct agent with create_react_agent()
5. **Create** wrapper node for StateGraph integration
6. **Test** individual agent thoroughly
7. **Integrate** into supervisor workflow
8. **Validate** end-to-end behavior
9. **Deploy** incrementally
10. **Monitor** and optimize

**Example Migration:**

```python
# OLD: Legacy agent
class OldRequirementsAnalyst:
    def analyze(self, context):
        prompt = f"Analyze: {context}"
        return self.llm.generate(prompt)

# NEW: LangGraph ReAct agent
@tool
def analyze_requirements(context: str) -> dict:
    """Analyze project requirements."""
    return {"analyzed": True, "context": context}

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
new_agent = create_react_agent(
    model=llm,
    tools=[analyze_requirements],
    state_modifier="You are an expert Requirements Analyst"
)
```

---

## 11. Conclusion

This architecture provides a robust foundation for building scalable, maintainable AI agent swarms using LangGraph and LangChain. By following the patterns and best practices outlined here, we can:

✅ **Build with Confidence**: Clear patterns reduce development friction  
✅ **Scale Systematically**: Add agents and tools incrementally  
✅ **Debug Effectively**: Full tracing and visualization  
✅ **Maintain Easily**: Clean separation of concerns  
✅ **Deploy Safely**: Comprehensive testing at all levels

**Next Steps:**

1. Review and approve this architecture
2. Complete remaining Phase 1 items
3. Create automated test suite
4. Document lessons learned
5. Begin Phase 2 planning

---

## References

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangChain Documentation**: https://docs.langchain.com/
- **ReAct Paper**: https://arxiv.org/abs/2210.03629
- **LangGraph Studio**: https://github.com/langchain-ai/langgraph-studio
- **Our Implementation**: `workflow/langgraph_workflow.py`

---

**Document Control**

- **Author**: AI Development Team
- **Reviewers**: [To be assigned]
- **Approval**: [Pending]
- **Version History**: 
  - v1.0 (2025-01-24): Initial architecture document


