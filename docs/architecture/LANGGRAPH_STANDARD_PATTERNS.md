# LangGraph Standard Patterns for Context Detection

**Status**: 🟢 **STANDARD PATTERNS ONLY**  
**Created**: 2025-10-28  
**CRITICAL**: Use ONLY LangGraph standard patterns - no custom systems!

## Standard Patterns We Use

### 1. State Definition (TypedDict)
```python
from typing import TypedDict, List, Annotated
import operator

class SwarmState(TypedDict):
    """LangGraph state - standard TypedDict pattern."""
    project_context: str
    project_complexity: str
    project_domain: str      # NEW: Context field
    project_intent: str      # NEW: Context field
    detected_entities: List[str]  # NEW: Context field
    
    # Messages (standard pattern)
    messages: Annotated[List, operator.add]
    
    # Other fields...
```

**Why**: LangGraph state is automatically persisted via checkpointer

---

### 2. Checkpointer (MemorySaver)
```python
from langgraph.checkpoint.memory import MemorySaver

# Standard LangGraph checkpointer
checkpointer = MemorySaver()

# Compile with checkpointer
compiled = workflow.compile(checkpointer=checkpointer)
```

**Why**: Automatic state persistence after each node execution

---

### 3. Thread ID Management (ThreadManager)
```python
from utils.thread_manager import ThreadManager

# Use existing ThreadManager (already follows LangGraph patterns)
thread_manager = ThreadManager(session_type="development")

# Get standard LangGraph config
config = thread_manager.get_current_config()
# Returns: {"configurable": {"thread_id": "development_xxx"}}

# Execute graph with config
result = await graph.ainvoke(state, config=config)
```

**Why**: ThreadManager already uses standard LangGraph config format

---

### 4. State Persistence (Automatic)
```python
# State automatically persists via checkpointer
# NO manual storage needed!

# Execute graph
result = await graph.ainvoke(
    {"project_domain": "ai", "project_intent": "new_feature"},
    config={"configurable": {"thread_id": "dev_123"}}
)

# State is automatically saved by checkpointer
# Next invocation with same thread_id loads state automatically
```

**Why**: LangGraph checkpointer handles persistence automatically

---

### 5. State Loading (Standard Pattern)
```python
# Load existing state (standard LangGraph pattern)
config = {"configurable": {"thread_id": "dev_123"}}
existing_state = graph.get_state(config)

if existing_state and existing_state.values:
    # Context already in state
    domain = existing_state.values.get("project_domain")
    intent = existing_state.values.get("project_intent")
```

**Why**: Standard LangGraph method for loading state

---

### 6. HITL Interrupts (Standard Pattern)
```python
# Standard LangGraph interrupt pattern
compiled = workflow.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["review_context"]  # Standard interrupt
)

# Resume after human input
result = await graph.ainvoke(state, config=config)
```

**Why**: Built-in LangGraph feature for human-in-the-loop

---

## What We DON'T Do

❌ **NO custom memory storage**  
❌ **NO custom persistence systems**  
❌ **NO custom thread management**  
❌ **NO custom state loading**  
❌ **NO reinventing the wheel**

## Implementation Example

```python
# Standard LangGraph pattern for context detection with persistence

from utils.thread_manager import ThreadManager
from langgraph.checkpoint.memory import MemorySaver

class ContextAwareComplexityAnalyzer:
    """Uses ONLY LangGraph standard patterns."""
    
    def __init__(self):
        self.thread_manager = ThreadManager(session_type="development")
        self.context_router = ContextDetectionRouter()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build graph with standard LangGraph patterns."""
        workflow = StateGraph(SwarmState)
        
        workflow.add_node("detect_context", self._detect_context_node)
        workflow.add_node("review_context", self._review_context_node)
        
        workflow.add_edge(START, "detect_context")
        workflow.add_edge("detect_context", "review_context")
        workflow.add_edge("review_context", END)
        
        # Standard LangGraph compilation
        return workflow.compile(
            checkpointer=MemorySaver(),  # Standard checkpointer
            interrupt_before=["review_context"]  # Standard interrupt
        )
    
    async def analyze(self, project_context: str):
        """Analyze with standard LangGraph patterns."""
        
        # Get standard config
        config = self.thread_manager.get_current_config()
        
        # Load existing state (standard pattern)
        existing_state = self.graph.get_state(config)
        if existing_state and existing_state.values.get("project_domain"):
            # Context already exists - return it
            return existing_state.values
        
        # Detect new context
        detected = await self.context_router.detect_context(project_context)
        
        # Update state (automatically persisted via checkpointer)
        state_update = {
            "project_context": project_context,
            "project_domain": detected.domain,
            "project_intent": detected.intent,
            "project_complexity": detected.complexity
        }
        
        # Execute graph - state persists automatically
        result = await self.graph.ainvoke(state_update, config=config)
        
        return result
```

## Benefits of Using Standard Patterns

✅ **Automatic Persistence**: Checkpointer handles everything  
✅ **Thread Isolation**: Automatic via thread_id  
✅ **Standard API**: Works with LangGraph Studio, debugging tools  
✅ **No Custom Code**: Less code to maintain  
✅ **Well-Tested**: LangGraph patterns are battle-tested  
✅ **Future-Proof**: Compatible with LangGraph updates  

## Reference

- LangGraph Memory: https://docs.langchain.com/oss/python/langgraph/add-memory
- LangGraph Checkpointers: https://docs.langchain.com/oss/python/langgraph/checkpointers
- Thread Management: `utils/thread_manager.py`

