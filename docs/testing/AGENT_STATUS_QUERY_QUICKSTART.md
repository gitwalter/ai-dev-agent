# Agent Status Query - Quick Reference

## Quick Status Check in Studio

### Visual Method (Easiest)
1. Select your agent graph in Studio
2. Check the **State panel** on the right
3. Look at these fields:
   - `current_step` → Where you are
   - `iteration_count` → Refinement loops (0-3)
   - `[agent]_confidence` → Quality score (0.0-1.0)
   - `human_approval` → HITL status (if paused)

### Programmatic Method
```python
# In Studio Python console
from workflow.complexity_analyzer_studio import graph

config = {"configurable": {"thread_id": "your-thread-id"}}
state = graph.get_state(config)

print(f"Step: {state.values.get('current_step')}")
print(f"Next: {state.next}")
print(f"Paused: {len(state.next) > 0}")
```

## Status Query Utility

```python
from utils.agent_status_query import query_agent_status, format_status_report

# Query any agent
status = query_agent_status(graph, thread_id, "complexity_analyzer")
print(format_status_report(status))
```

## Status Fields

| Agent | Key Fields |
|-------|-----------|
| **Complexity Analyzer** | `context_detected`, `confidence`, `project_domain`, `project_intent` |
| **Agent Selector** | `agents_selected`, `selected_agents`, `confidence` |
| **Requirements Analyst** | `requirements_analyzed`, `functional_requirements_count`, `confidence` |
| **Architecture Designer** | `architecture_designed`, `components_count`, `confidence` |
| **Code Generator** | `code_generated`, `files_count`, `confidence` |

## Common Status Values

- **Status**: `not_started` | `in_progress` | `interrupted` | `complete` | `error`
- **Current Step**: `start` | `[agent]_analyzed` | `[agent]_review` | `completed`
- **Is Interrupted**: `True` if paused at HITL checkpoint

## See Full Guide

📖 **Complete Guide**: `docs/testing/AGENT_STATUS_QUERY_GUIDE.md`

