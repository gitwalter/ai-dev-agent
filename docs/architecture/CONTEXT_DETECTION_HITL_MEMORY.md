# Context Detection with HITL Refinement & Persistent Memory

**Status**: 🟢 **ENHANCED**  
**Enhancement**: Added HITL context refinement + persistent memory  
**Created**: 2025-10-28  
**CRITICAL**: Uses ONLY LangGraph standard patterns - no custom memory systems!

## Overview

This document describes the enhanced context detection system with:
1. **HITL Context Review**: Human can review and refine detected context
2. **Persistent Memory**: Context persists via LangGraph checkpointer (standard pattern)
3. **Conversation Loop**: Iterative refinement through conversation

**Key Principle**: Use ONLY LangGraph standard patterns:
- ✅ LangGraph state (TypedDict) for data storage
- ✅ MemorySaver checkpointer for persistence
- ✅ ThreadManager for thread_id management
- ✅ Standard config format: `{"configurable": {"thread_id": "..."}}`
- ❌ NO custom memory storage
- ❌ NO custom persistence systems
- ❌ NO reinventing the wheel

## Architecture

### Workflow with HITL Context Review

```
START
  ↓
detect_context (Complexity Analyzer)
  ↓
[HITL: review_context] ← Human reviews detected context
  ↓
human_decision: approve / refine
  ↓
  ├─ approve → Store context in thread state → Continue workflow
  └─ refine → refine_context → [HITL: review_context] (loop)
```

### State Structure

```python
class SwarmState(TypedDict):
    # Context detection
    project_context: str
    project_complexity: str  # simple, medium, complex
    project_domain: str      # ai, web, api, data, mobile, etc.
    project_intent: str      # new_feature, bug_fix, refactor, etc.
    detected_entities: List[str]  # ["rag", "document", "search"]
    
    # HITL context review
    context_review_prompt: str     # Shown to human
    context_feedback: str          # Human feedback
    context_refined: bool          # Whether context was refined
    
    # Thread persistence
    thread_id: str                 # Thread ID for persistence
    
    # Messages
    messages: Annotated[List, operator.add]
```

## Implementation

### 1. Context Detection Node

```python
async def detect_context_node(state: SwarmState) -> Dict[str, Any]:
    """Detect context from project description."""
    
    project_context = state["project_context"]
    
    # Use LLM to classify context
    context = await context_router.detect_context(project_context)
    
    return {
        "project_complexity": context.complexity,
        "project_domain": context.domain,
        "project_intent": context.intent,
        "detected_entities": context.entities,
        "context_review_prompt": format_context_review(context)
    }
```

### 2. HITL Context Review Node

```python
async def review_context_node(state: SwarmState) -> Dict[str, Any]:
    """HITL checkpoint: Human reviews detected context."""
    
    detected_context = {
        "Complexity": state.get("project_complexity"),
        "Domain": state.get("project_domain"),
        "Intent": state.get("project_intent"),
        "Entities": state.get("detected_entities", [])
    }
    
    # Format for human review
    review_prompt = f"""
DETECTED CONTEXT:
{format_context_for_review(detected_context)}

Please review and provide feedback:
- Type 'approve' to accept this context
- Type 'refine: <feedback>' to refine (e.g., 'refine: Domain should be web, not ai')
- Type 'refine: domain=web, intent=new_feature' for structured feedback
"""
    
    return {
        "context_review_prompt": review_prompt,
        "messages": [{"role": "system", "content": review_prompt}]
    }
```

### 3. Context Refinement Node

```python
async def refine_context_node(state: SwarmState) -> Dict[str, Any]:
    """Refine context based on human feedback."""
    
    human_feedback = state.get("context_feedback", "")
    detected_context = {
        "complexity": state.get("project_complexity"),
        "domain": state.get("project_domain"),
        "intent": state.get("project_intent"),
        "entities": state.get("detected_entities", [])
    }
    
    # Parse human feedback
    if "refine:" in human_feedback.lower():
        feedback_text = human_feedback.split("refine:", 1)[1].strip()
        refined = await parse_and_refine_context(detected_context, feedback_text)
    else:
        # Use LLM to interpret feedback
        refined = await llm_refine_context(detected_context, human_feedback)
    
    return {
        "project_domain": refined["domain"],
        "project_intent": refined["intent"],
        "project_complexity": refined["complexity"],
        "detected_entities": refined["entities"],
        "context_refined": True,
        "messages": [{"role": "assistant", "content": f"Context refined: {refined}"}]
    }
```

### 4. Persistent Memory Integration (Standard LangGraph Pattern)

```python
class ContextAwareComplexityAnalyzer:
    """Complexity analyzer with context detection using LangGraph patterns."""
    
    def __init__(self, graph: CompiledGraph, thread_manager: ThreadManager):
        self.graph = graph  # Compiled LangGraph with checkpointer
        self.thread_manager = thread_manager
        self.context_router = ContextDetectionRouter()
    
    async def analyze_with_persistence(self, project_context: str) -> Dict[str, Any]:
        """Analyze with context persistence via LangGraph checkpointer."""
        
        # Get standard LangGraph config (thread_id)
        config = self.thread_manager.get_current_config()
        # Returns: {"configurable": {"thread_id": "development_xxx"}}
        
        # Load existing state from checkpointer (standard pattern)
        existing_state = self.graph.get_state(config)
        
        if existing_state and existing_state.values:
            # Check if context already exists in state
            if existing_state.values.get("project_domain"):
                logger.info(f"Using existing context from thread {config['configurable']['thread_id']}")
                return {
                    "project_domain": existing_state.values.get("project_domain"),
                    "project_intent": existing_state.values.get("project_intent"),
                    "project_complexity": existing_state.values.get("project_complexity"),
                    "detected_entities": existing_state.values.get("detected_entities", [])
                }
        
        # Detect new context
        detected = await self.context_router.detect_context(project_context)
        
        # Update state - LangGraph checkpointer automatically saves
        state_update = {
            "project_context": project_context,
            "project_domain": detected.domain,
            "project_intent": detected.intent,
            "project_complexity": detected.complexity,
            "detected_entities": detected.entities
        }
        
        # Execute graph - state persists automatically via checkpointer
        result = await self.graph.ainvoke(state_update, config=config)
        
        return {
            "project_domain": detected.domain,
            "project_intent": detected.intent,
            "project_complexity": detected.complexity,
            "detected_entities": detected.entities
        }
    
    # NO custom storage methods needed!
    # LangGraph checkpointer handles everything automatically
```

### 5. Conversation Loop for Refinement

```python
async def handle_context_refinement_conversation(
    state: SwarmState,
    user_message: str
) -> Dict[str, Any]:
    """Handle conversation about context refinement."""
    
    # Check if this is context refinement feedback
    if is_context_refinement(user_message):
        # Refine context
        refined = await refine_context_node(state)
        
        # Confirm refinement
        return {
            **refined,
            "messages": [{
                "role": "assistant",
                "content": f"Context updated! Domain: {refined['project_domain']}, Intent: {refined['project_intent']}"
            }]
        }
    
    # Otherwise, continue normal conversation
    return state

def is_context_refinement(message: str) -> bool:
    """Check if message is about context refinement."""
    refinement_keywords = [
        "actually, this is",
        "it's actually",
        "refine:",
        "change domain",
        "change intent",
        "correction:"
    ]
    return any(keyword in message.lower() for keyword in refinement_keywords)
```

## Graph Structure

```python
def build_context_aware_workflow():
    """Build workflow with HITL context review."""
    
    workflow = StateGraph(SwarmState)
    
    # Context detection
    workflow.add_node("detect_context", detect_context_node)
    
    # HITL context review
    workflow.add_node("review_context", review_context_node)
    
    # Context refinement
    workflow.add_node("refine_context", refine_context_node)
    
    # Rest of workflow
    workflow.add_node("select_agents", select_agents_node)
    workflow.add_node("requirements_analyst", requirements_node)
    # ... other agents
    
    # Edges
    workflow.add_edge(START, "detect_context")
    workflow.add_edge("detect_context", "review_context")
    
    # Conditional after review
    workflow.add_conditional_edges(
        "review_context",
        route_after_review,
        {
            "approve": "select_agents",
            "refine": "refine_context"
        }
    )
    
    # Refinement loops back to review
    workflow.add_edge("refine_context", "review_context")
    
    # Rest of workflow
    workflow.add_edge("select_agents", "requirements_analyst")
    # ... rest
    
    # Compile with HITL interrupts
    compiled = workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["review_context"]  # HITL checkpoint
    )
    
    return compiled

def route_after_review(state: SwarmState) -> str:
    """Route after context review."""
    decision = state.get("human_decision", "approve")
    
    if decision == "approve":
        return "approve"
    elif decision == "refine":
        return "refine"
    else:
        return "approve"  # Default
```

## Usage Example

### Example 1: Initial Context Detection

```python
# User: "Build a RAG system for document search"

# System detects context:
{
    "project_complexity": "complex",
    "project_domain": "ai",
    "project_intent": "new_feature",
    "detected_entities": ["rag", "document", "search"]
}

# [HITL]: Human reviews
# Human: "approve"
# → Context stored in thread state
# → Continue workflow
```

### Example 2: Context Refinement

```python
# User: "Build a RAG system for document search"

# System detects context:
{
    "project_domain": "ai",
    "project_intent": "new_feature"
}

# [HITL]: Human reviews
# Human: "refine: Actually, this is a web project with AI features"

# System refines:
{
    "project_domain": "web",  # Changed from "ai"
    "project_intent": "new_feature",
    "context_refined": True
}

# [HITL]: Human reviews again
# Human: "approve"
# → Refined context stored
# → Continue workflow
```

### Example 3: Persistent Context Across Sessions (Standard LangGraph Pattern)

```python
from utils.thread_manager import ThreadManager

# Session 1: User starts project
thread_manager = ThreadManager(session_type="development")
config = thread_manager.get_current_config()
# config = {"configurable": {"thread_id": "development_a1b2c3d4"}}

result = await graph.ainvoke(
    {"project_context": "Build RAG system"},
    config=config
)
# Context detected: domain="ai", intent="new_feature"
# State automatically saved via checkpointer

# Session 2: User resumes project (next day)
# Same thread_id - context persists automatically
config = {"configurable": {"thread_id": "development_a1b2c3d4"}}

# Load existing state (standard pattern)
existing_state = graph.get_state(config)
if existing_state and existing_state.values:
    context = existing_state.values  # Has project_domain, etc.

# Continue workflow - context already in state
result = await graph.ainvoke(
    {"project_context": "Continue building RAG system"},
    config=config
)
# All agents use persisted context from state
```

### Example 4: Conversation-Based Refinement

```python
# User: "Build a RAG system"

# System: "Detected context: Domain=AI, Intent=new_feature. Correct?"

# User: "Actually, it's a web project"

# System: "Context updated! Domain=web, Intent=new_feature"

# User: "Continue with requirements analysis"

# System uses refined context (domain=web) for all downstream agents
```

## Benefits

### 1. Accuracy
- Human can correct context detection errors
- Iterative refinement improves accuracy
- Context becomes more accurate over time

### 2. Persistence
- Context survives across sessions
- Multi-day projects maintain context
- No need to re-detect context

### 3. Transparency
- Human sees what context was detected
- Can correct mistakes early
- Clear feedback loop

### 4. Flexibility
- Can refine context mid-conversation
- Supports corrections and clarifications
- Adapts to user feedback

## Testing

### Test HITL Context Review

```python
async def test_hitl_context_review():
    """Test HITL context review workflow."""
    
    # Detect context
    state = {"project_context": "Build RAG system"}
    state = await detect_context_node(state)
    assert state["project_domain"] == "ai"
    
    # Review context
    state = await review_context_node(state)
    assert "context_review_prompt" in state
    
    # Human refines
    state["context_feedback"] = "refine: Domain should be web"
    state["human_decision"] = "refine"
    
    # Refine context
    state = await refine_context_node(state)
    assert state["project_domain"] == "web"
    assert state["context_refined"] == True
```

### Test Persistent Memory (Standard LangGraph Pattern)

```python
async def test_context_persistence():
    """Test context persistence using LangGraph standard patterns."""
    
    from utils.thread_manager import ThreadManager
    
    # Setup
    thread_manager = ThreadManager(session_type="development")
    config = thread_manager.get_current_config()
    thread_id = config["configurable"]["thread_id"]
    
    # Session 1: Detect context
    state1 = {"project_context": "Build RAG system"}
    result1 = await graph.ainvoke(state1, config=config)
    assert result1.get("project_domain") == "ai"
    
    # State automatically persisted via checkpointer
    
    # Session 2: Resume - load state (standard pattern)
    existing_state = graph.get_state(config)
    assert existing_state is not None
    assert existing_state.values.get("project_domain") == "ai"
    
    # Continue workflow - context persists
    state2 = {"project_context": "Continue RAG"}
    result2 = await graph.ainvoke(state2, config=config)
    assert result2.get("project_domain") == "ai"  # Same as session 1
```

## Integration Points

### 1. ThreadManager Integration (Standard Pattern)
- Use existing `ThreadManager` from `utils.thread_manager`
- Call `thread_manager.get_current_config()` for thread_id
- Pass config to `graph.ainvoke()` - state persists automatically
- **NO custom integration needed** - ThreadManager already follows LangGraph patterns

### 2. HITL Checkpoint System (Standard Pattern)
- Use existing HITL infrastructure (`interrupt_before` pattern)
- Add `review_context` to `interrupt_before` list
- Human feedback parsed and applied
- **NO custom HITL system** - Use LangGraph's built-in interrupts

### 3. Conversation System (Standard Pattern)
- Detect context refinement messages in conversation
- Iterative refinement loop (standard state flow)
- Confirm refinements to user
- **NO custom conversation system** - Use existing message handling

## Success Criteria

- [ ] HITL context review checkpoint implemented
- [ ] Context refinement node working
- [ ] Context persists in thread state
- [ ] Conversation loop for refinement works
- [ ] Context loaded when resuming sessions
- [ ] Human can refine context mid-conversation
- [ ] All tests passing

## Next Steps

1. Implement HITL context review node
2. Implement context refinement node
3. Integrate with ThreadManager
4. Add conversation detection for refinement
5. Test end-to-end workflow

