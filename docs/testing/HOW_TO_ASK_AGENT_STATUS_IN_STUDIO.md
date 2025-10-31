# How to Ask Agents to Publish Status in Studio

## Quick Answer: Check State Panel (Always Available)

**Easiest method** - No code needed:

1. Select your agent graph in Studio (e.g., `_complexity_analyzer`)
2. Look at the **State panel** on the right side
3. Status is always visible there - look for:
   - `current_step` - Current workflow step
   - `iteration_count` - Refinement loops (0-3)
   - `[agent]_confidence` - Quality score (0.0-1.0)
   - `human_approval` - HITL status (if paused)

**That's it!** The state panel shows everything you need.

## Method 1: State Panel (Visual) - RECOMMENDED

### Step-by-Step:

1. **Select Graph**: Choose your agent from dropdown (e.g., `_complexity_analyzer`)
2. **Open State Panel**: Click on "State" tab/view (usually on right side)
3. **View Status Fields**:
   ```
   current_step: "context_review"
   iteration_count: 1
   context_confidence: 0.85
   project_domain: "ai"
   project_intent: "new_feature"
   human_approval: "needs_refinement"
   ```

This method works **immediately** - no code, no setup needed!

## Method 2: Python Console in Studio

If Studio has a Python console, you can query programmatically:

```python
# In Studio Python console (if available)
from workflow.complexity_analyzer_studio import graph

# Get state
config = {"configurable": {"thread_id": "your-thread-id"}}
state = graph.get_state(config)

# Print status
print(f"Step: {state.values.get('current_step')}")
print(f"Confidence: {state.values.get('context_confidence', 0.0):.0%}")
print(f"Iterations: {state.values.get('iteration_count', 0)}")
```

## Method 3: Add Status Node to Graph (For Regular Status Updates)

If you want to add a dedicated status publish node, modify your graph:

### Example: Adding to Complexity Analyzer

```python
# In workflow/complexity_analyzer_studio.py

from utils.agent_status_node import publish_status_node

def build_graph():
    workflow = StateGraph(ComplexityAnalyzerState)
    
    # Existing nodes
    workflow.add_node("complexity_analyzer", analyze_complexity_node)
    workflow.add_node("review_context", review_context_node)
    workflow.add_node("finalize_context", finalize_context_node)
    
    # Add status node
    workflow.add_node("publish_status", publish_status_node)
    
    # Route to status if action requested
    def route_with_status(state):
        if state.get("action") == "publish_status":
            return "publish_status"
        # Normal routing...
        return "review_context"  # or your normal routing
    
    workflow.add_conditional_edges(
        "complexity_analyzer",
        route_with_status,
        {
            "publish_status": "publish_status",
            "review_context": "review_context"
        }
    )
    
    # Status node goes to review
    workflow.add_edge("publish_status", "review_context")
    
    # ... rest of graph
```

Then in Studio:
1. Update state: `{"action": "publish_status", ...other fields...}`
2. Status appears in `status_summary` field

## Method 4: External Python Script

Query from outside Studio:

```python
from workflow.complexity_analyzer_studio import graph
from utils.agent_status_query import query_agent_status, format_status_report

# Query status
thread_id = "your-thread-id"
status = query_agent_status(graph, thread_id, "complexity_analyzer")

# Print formatted report
print(format_status_report(status))
```

## What Status Information is Available?

### All Agents Show:
- ✅ `current_step` - Where you are in workflow
- ✅ `iteration_count` - Refinement loops (0-3)
- ✅ `[agent]_confidence` - Quality score (0.0-1.0)
- ✅ `human_approval` - HITL status (if paused)
- ✅ `errors` - Error list (if any)

### Agent-Specific:

**Complexity Analyzer:**
```json
{
  "project_domain": "ai",
  "project_intent": "new_feature", 
  "project_complexity": "complex",
  "detected_entities": ["rag", "vector", "qdrant"],
  "context_confidence": 0.85
}
```

**Code Generator:**
```json
{
  "files_count": 5,
  "files_list": ["main.py", "config.py", ...],
  "generation_confidence": 0.92
}
```

## Recommended Approach

**For Studio testing**: Use **Method 1 (State Panel)** - it's the simplest and always available.

**For monitoring**: Use **Method 4 (External Script)** - query status programmatically.

**For workflow integration**: Use **Method 3 (Status Node)** - add status node to graph.

## Quick Reference

| Method | Setup Required | Best For |
|--------|---------------|----------|
| **State Panel** | None | ✅ Quick checks in Studio |
| **Python Console** | None | ✅ Ad-hoc queries |
| **Status Node** | Graph modification | ✅ Regular status updates |
| **External Script** | None | ✅ Monitoring/Automation |

## Example: Status Report Format

When status is published, you'll see:

```
# Agent Status Report: complexity_analyzer

**Status**: INTERRUPTED
**Current Step**: context_review
**Timestamp**: 2025-01-15T10:30:00

**Next Nodes**: review_context
**Workflow**: ⏸️ Paused (HITL checkpoint)

**Confidence**: 85%
**Iterations**: 1/3

**Context**: ✅ Detected
**Domain**: ai
**Intent**: new_feature
**Complexity**: complex

⏸️ **Workflow Paused** (awaiting human input)
```

## Summary

**In Studio**: Just check the **State panel** - status is always visible there! No code needed.

**Programmatically**: Use `query_agent_status()` function from `utils/agent_status_query.py`.

**In Graph**: Add `publish_status_node` to your graph for on-demand status reports.

For most use cases, **the State panel is sufficient** - it shows all status information immediately without any setup.

