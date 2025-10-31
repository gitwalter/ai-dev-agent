# Agent Status Query Guide for LangGraph Studio

## Overview

You can query the current status of any agent graph in LangGraph Studio using the standard LangGraph `get_state()` method. This allows you to check:
- Current workflow step
- State values (context, requirements, architecture, code, etc.)
- Next nodes to execute
- Whether workflow is paused at HITL checkpoint
- Iteration count and confidence scores

## How to Query Status in Studio

### Method 1: Using State Panel (Visual)

1. **Select Graph**: Choose your agent graph (e.g., `_complexity_analyzer`)
2. **Load Thread**: If you have an existing thread_id, the state will load automatically
3. **View State**: Check the State panel on the right side of Studio
4. **Status Fields**: Look for these key fields:
   - `current_step`: Current workflow step
   - `iteration_count`: Number of refinement iterations
   - `[agent]_confidence`: Confidence score (0.0 to 1.0)
   - `human_approval`: Approval status if paused
   - `errors`: Any errors encountered

### Method 2: Using Python Script (Programmatic)

```python
from workflow.complexity_analyzer_studio import graph
from utils.agent_status_query import query_agent_status, format_status_report

# Query status
thread_id = "your-thread-id"
status = query_agent_status(graph, thread_id, "complexity_analyzer")

# Print formatted report
print(format_status_report(status))
```

### Method 3: Using Studio API (Advanced)

In Studio, you can access the graph programmatically:

```python
# In Studio Python console or script
from workflow.complexity_analyzer_studio import graph

# Get state
config = {"configurable": {"thread_id": "your-thread-id"}}
state_snapshot = graph.get_state(config)

# Inspect state
print(f"Current step: {state_snapshot.values.get('current_step')}")
print(f"Next nodes: {state_snapshot.next}")
print(f"Is interrupted: {len(state_snapshot.next) > 0}")
```

## Status Query Examples

### Complexity Analyzer Status

```python
from workflow.complexity_analyzer_studio import graph
from utils.agent_status_query import query_agent_status

status = query_agent_status(graph, "thread-123", "complexity_analyzer")

# Returns:
# {
#   "agent": "complexity_analyzer",
#   "status": "interrupted",  # or "complete", "in_progress"
#   "current_step": "context_review",
#   "next_nodes": ["review_context"],
#   "is_complete": False,
#   "is_interrupted": True,
#   "context_detected": True,
#   "confidence": 0.85,
#   "needs_more_info": False,
#   "iteration_count": 1,
#   "human_approval": "needs_refinement",
#   "timestamp": "2025-01-15T10:30:00"
# }
```

### Code Generator Status

```python
from workflow.code_generator_studio import graph
from utils.agent_status_query import query_agent_status

status = query_agent_status(graph, "thread-123", "code_generator")

# Returns:
# {
#   "agent": "code_generator",
#   "status": "complete",
#   "current_step": "completed",
#   "next_nodes": [],
#   "is_complete": True,
#   "code_generated": True,
#   "files_count": 5,
#   "confidence": 0.92,
#   "iteration_count": 0,
#   "timestamp": "2025-01-15T10:30:00"
# }
```

## Status Fields by Agent

### Complexity Analyzer
- `context_detected`: Whether context was detected
- `confidence`: Context detection confidence (0.0-1.0)
- `needs_more_info`: Whether more information is needed
- `iteration_count`: Refinement iterations (0-3)
- `project_domain`: Detected domain
- `project_intent`: Detected intent
- `project_complexity`: Detected complexity

### Agent Selector
- `agents_selected`: Number of selected agents
- `selected_agents`: List of selected agent names
- `confidence`: Selection confidence (0.0-1.0)
- `iteration_count`: Refinement iterations (0-3)

### Requirements Analyst
- `requirements_analyzed`: Whether requirements were analyzed
- `functional_requirements_count`: Number of functional requirements
- `confidence`: Analysis confidence (0.0-1.0)
- `iteration_count`: Refinement iterations (0-3)

### Architecture Designer
- `architecture_designed`: Whether architecture was designed
- `components_count`: Number of components
- `confidence`: Design confidence (0.0-1.0)
- `iteration_count`: Refinement iterations (0-3)

### Code Generator
- `code_generated`: Whether code was generated
- `files_count`: Number of generated files
- `confidence`: Generation confidence (0.0-1.0)
- `iteration_count`: Refinement iterations (0-3)

## Common Status Values

### Status Types
- `"not_started"`: Graph hasn't been executed yet
- `"in_progress"`: Graph is executing
- `"interrupted"`: Graph paused at HITL checkpoint
- `"complete"`: Graph finished successfully
- `"error"`: Graph encountered an error

### Current Steps
- `"start"`: Initial step
- `"[agent]_analyzed"`: Agent completed analysis
- `"[agent]_review"`: At HITL review checkpoint
- `"completed"`: Workflow finished

## Querying All Agents

```python
from workflow.complexity_analyzer_studio import graph as complexity_graph
from workflow.agent_selector_studio import graph as selector_graph
from workflow.requirements_analyst_studio import graph as requirements_graph
from workflow.architecture_designer_studio import graph as architecture_graph
from workflow.code_generator_studio import graph as code_graph
from utils.agent_status_query import query_all_agents_status, format_status_report

graphs = {
    "complexity_analyzer": complexity_graph,
    "agent_selector": selector_graph,
    "requirements_analyst": requirements_graph,
    "architecture_designer": architecture_graph,
    "code_generator": code_graph
}

thread_id = "your-thread-id"
all_status = query_all_agents_status(graphs, thread_id)

# Print status for each agent
for agent_name, status in all_status.items():
    print(format_status_report(status))
    print("\n" + "="*50 + "\n")
```

## Using Status in Studio UI

### Step 1: Select Graph
Choose your agent graph from the dropdown.

### Step 2: Check State Panel
The State panel shows current state values. Key fields:
- `current_step`: Where you are in the workflow
- `iteration_count`: How many refinement loops have occurred
- `[agent]_confidence`: Quality score

### Step 3: Check Next Nodes
If `next_nodes` is populated, the workflow is paused at an HITL checkpoint.

### Step 4: Query via Code
You can also run Python code in Studio to query status programmatically (see examples above).

## Status Query Best Practices

1. **Always Check `current_step`**: Tells you where you are in the workflow
2. **Monitor `iteration_count`**: Stops after 3 iterations (safety limit)
3. **Check `confidence`**: Low confidence (<0.7) may indicate issues
4. **Review `errors`**: Always check for errors before proceeding
5. **Use `is_interrupted`**: Know if workflow is waiting for human input

## Troubleshooting

### "No state found"
- Graph hasn't been executed yet
- Wrong thread_id
- Graph doesn't have checkpointer (shouldn't happen with Studio graphs)

### Status shows "error"
- Check `errors` field for details
- Check graph compilation (graph should be None if compilation failed)
- Verify thread_id is correct

### Status stuck at "interrupted"
- Workflow is paused at HITL checkpoint
- Provide feedback via state JSON editing
- Click Resume to continue

## Files

- **Utility**: `utils/agent_status_query.py`
- **Graphs**: `workflow/[agent]_studio.py`
- **This Guide**: `docs/testing/AGENT_STATUS_QUERY_GUIDE.md`

