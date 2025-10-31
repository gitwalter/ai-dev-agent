# Agent Selector Studio - Test JSON Examples

## Initial State JSON (Start Agent Selector)

Use this JSON to start the agent selector graph in LangGraph Studio.

```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search", "vector", "embeddings", "qdrant"],
  "required_agents": [],
  "selection_reasoning": "",
  "selection_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "selection_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## Alternative Initial States

### Simple Bug Fix Project
```json
{
  "project_context": "Fix bug in authentication module where invalid tokens are accepted",
  "project_complexity": "simple",
  "project_domain": "web",
  "project_intent": "bug_fix",
  "detected_entities": ["authentication", "tokens", "security"],
  "required_agents": [],
  "selection_reasoning": "",
  "selection_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "selection_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

### Medium Complexity API Project
```json
{
  "project_context": "Create REST API for user management with authentication and CRUD operations",
  "project_complexity": "medium",
  "project_domain": "api",
  "project_intent": "new_feature",
  "detected_entities": ["rest", "api", "authentication", "crud", "user-management"],
  "required_agents": [],
  "selection_reasoning": "",
  "selection_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "selection_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## Feedback JSON Examples

After the graph pauses at the HITL checkpoint, update the state with feedback:

### Approve Selection (No Changes)
```json
{
  "human_approval": "approved"
}
```

### Request Refinement - Add Missing Agents
```json
{
  "human_feedback": "Add test_generator and code_reviewer for quality assurance",
  "human_approval": "needs_refinement"
}
```

### Request Refinement - Remove Unnecessary Agents
```json
{
  "human_feedback": "Remove architecture_designer, this is a simple bug fix",
  "human_approval": "needs_refinement"
}
```

### Request Refinement - Replace Selection
```json
{
  "human_feedback": "Only need requirements_analyst, code_generator, and documentation_generator for this simple project",
  "human_approval": "needs_refinement"
}
```

### Reject Selection
```json
{
  "human_approval": "rejected"
}
```

## Complete Feedback State Examples

### Full State Update for Refinement
```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search", "vector", "embeddings", "qdrant"],
  "required_agents": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "documentation_generator"],
  "selection_reasoning": "Complex AI project requires full development lifecycle",
  "selection_confidence": 0.85,
  "needs_more_info": false,
  "information_requests": [],
  "selection_summary": "**Selected Agents**: requirements_analyst, architecture_designer, code_generator, test_generator, documentation_generator",
  "human_feedback": "Add code_reviewer for code quality checks",
  "human_approval": "needs_refinement",
  "iteration_count": 1,
  "current_step": "selection_review",
  "errors": []
}
```

## Testing Workflow

### Step 1: Start with Initial State
Copy one of the initial state JSONs above and paste into Studio's state editor.

### Step 2: Execute Graph
Click "Run" or "Execute" - graph will pause after `select_agents` node.

### Step 3: Review Selection
Check the `required_agents` and `selection_summary` fields in the state.

### Step 4: Provide Feedback (if needed)
Update the state with one of the feedback JSONs above and click "Resume".

### Step 5: Verify Final Message
After approval/rejection/max iterations, check `selection_summary` for final completion message.

## Available Agents

- `requirements_analyst` - Always required
- `architecture_designer` - Required for medium+, web_app, api, data_processing
- `code_generator` - Always required
- `test_generator` - Required for medium+, critical functionality
- `code_reviewer` - Required for medium+, production code
- `documentation_generator` - Always required

## Notes

- **Initial State**: Must include all fields from `AgentSelectorState`
- **Feedback State**: Can be minimal - only update `human_feedback` and `human_approval`
- **Iteration Limit**: Max 3 refinement iterations (safety limit)
- **Confidence**: Auto-approves if `selection_confidence >= 0.9` and no feedback

