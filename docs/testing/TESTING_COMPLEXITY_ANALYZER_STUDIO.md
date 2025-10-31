# Testing Complexity Analyzer in LangGraph Studio

**Purpose**: Isolated testing of Phase 1 context detection (US-CONTEXT-001) in LangGraph Studio

## Prerequisites

1. **LangGraph Studio installed and running**
   - Install: `pip install langgraph-studio` or use LangGraph Cloud
   - Make sure you're in the project root directory

2. **Environment variables set**
   ```bash
   export GEMINI_API_KEY="your-api-key"
   export LANGSMITH_API_KEY="your-langsmith-key"  # Optional, for prompt loading
   ```

3. **Graph registered in langgraph.json**
   - Already configured: `"_complexity_analyzer": "workflow/complexity_analyzer_studio.py:graph"`

## Step-by-Step Testing Instructions

### Step 1: Launch LangGraph Studio

```bash
# From project root directory
langgraph studio
```

Or if using LangGraph Cloud:
- Navigate to https://studio.langchain.com
- Select your project: `ai-dev-agent`

### Step 2: Select the Complexity Analyzer Graph

1. In LangGraph Studio, locate the **Graph Selection** dropdown (usually at the top)
2. Select `_complexity_analyzer` from the dropdown
3. Wait for the graph to load - you should see a simple graph with:
   - Entry point: `START`
   - Node: `complexity_analyzer`
   - End point: `END`

### Step 3: Prepare Initial State

In the Studio interface, you'll need to provide an initial state. Use this format:

```json
{
  "project_context": "Build a RAG system for document search using vector embeddings",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "current_step": "start",
  "errors": []
}
```

**Required fields**:
- `project_context`: The project description to analyze (REQUIRED)
- Other fields can be empty strings/arrays - they will be populated by the analyzer

### Step 4: Test Cases

#### Test Case 1: AI Project (RAG System)
```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "current_step": "start",
  "errors": []
}
```

**Expected Output**:
- `project_complexity`: `"complex"` (or `"medium"`)
- `project_domain`: `"ai"`
- `project_intent`: `"new_feature"`
- `detected_entities`: Should include `["rag", "document", "search", "vector", "embeddings", "qdrant"]` or similar

#### Test Case 2: Bug Fix
```json
{
  "project_context": "Fix authentication bug in login API endpoint",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "current_step": "start",
  "errors": []
}
```

**Expected Output**:
- `project_complexity`: `"simple"` or `"medium"`
- `project_domain`: `"api"` or `"web"`
- `project_intent`: `"bug_fix"`
- `detected_entities`: Should include `["authentication", "api", "login"]` or similar

#### Test Case 3: Web Application
```json
{
  "project_context": "Create a full-stack web application with React frontend and FastAPI backend",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "current_step": "start",
  "errors": []
}
```

**Expected Output**:
- `project_complexity`: `"complex"` or `"medium"`
- `project_domain`: `"web"`
- `project_intent`: `"new_feature"`
- `detected_entities`: Should include `["react", "fastapi", "frontend", "backend"]` or similar

#### Test Case 4: Refactoring
```json
{
  "project_context": "Refactor the authentication module to use dependency injection",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "current_step": "start",
  "errors": []
}
```

**Expected Output**:
- `project_complexity`: `"medium"` or `"complex"`
- `project_domain`: `"general"` or `"api"`
- `project_intent`: `"refactor"`
- `detected_entities`: Should include `["authentication", "dependency injection"]` or similar

### Step 5: Execute the Graph

1. Click the **Run** or **Execute** button in Studio
2. Watch the execution trace:
   - Node `complexity_analyzer` should execute
   - LLM call should be made
   - JSON parsing should occur
   - State should be updated with detected values
   - **Graph pauses at HITL checkpoint** (`review_context` node)

### Step 5.5: Handle HITL Checkpoint

When the graph pauses at the HITL checkpoint:

1. **Review Detected Context**:
   - Check `context_summary` field for readable summary
   - Check `context_confidence` to see confidence level (0.0 to 1.0)
   - Review detected values: `project_complexity`, `project_domain`, `project_intent`, `detected_entities`

2. **If More Information Needed**:
   - Check `needs_more_info` field (true/false)
   - Review `information_requests` array for questions
   - Update `project_context` with additional information
   - Or provide answers to specific questions

3. **Resume Execution**:
   - Click **Resume** or **Continue** in Studio
   - Graph will complete and show final state

### Step 6: Verify Results

Check the output state for:

✅ **All fields populated**:
- `project_complexity`: Should be `"simple"`, `"medium"`, or `"complex"`
- `project_domain`: Should be one of the valid domains
- `project_intent`: Should be one of the valid intents
- `detected_entities`: Should be a list of strings

✅ **Values are valid**:
- Complexity: `simple`, `medium`, or `complex`
- Domain: `ai`, `web`, `api`, `data`, `mobile`, `library`, `utility`, or `general`
- Intent: `new_feature`, `bug_fix`, `refactor`, `migration`, `enhancement`, or `general`
- Entities: Array of strings (technology names, frameworks, etc.)

✅ **Current step updated**:
- `current_step`: Should be `"complexity_analyzed"`

### Step 7: View Execution Details

In LangGraph Studio, you can:

1. **View Node Execution**:
   - Click on the `complexity_analyzer` node
   - View input/output
   - See LLM prompt and response

2. **View State Transitions**:
   - See how state changes from initial to final
   - Verify all context fields are populated

3. **View Traces** (if LangSmith enabled):
   - Check LangSmith traces for LLM calls
   - Verify prompt and response quality

## Troubleshooting

### Issue: Graph not appearing in Studio dropdown

**Solution**:
1. Check `langgraph.json` has the entry:
   ```json
   "_complexity_analyzer": "workflow/complexity_analyzer_studio.py:graph"
   ```
2. Restart LangGraph Studio
3. Verify file exists: `workflow/complexity_analyzer_studio.py`

### Issue: Import errors

**Solution**:
1. Ensure you're in project root directory
2. Check `PYTHONPATH` includes `.` (current directory)
3. Verify all dependencies installed: `pip install -r requirements.txt`

### Issue: API key errors

**Solution**:
1. Set environment variable: `export GEMINI_API_KEY="your-key"`
2. Restart Studio after setting environment variables
3. Check `.env` file if using one

### Issue: JSON parsing errors

**Solution**:
1. Check LangSmith traces to see LLM response
2. Verify prompt is loaded correctly
3. Check fallback logic is working (should use defaults)

### Issue: Empty or invalid values

**Solution**:
1. Check LLM response in Studio trace viewer
2. Verify prompt is correct
3. Check validation logic in `analyze_complexity_node`
4. Fallback should provide defaults if parsing fails

## Validation Checklist

After testing, verify:

- [ ] Graph loads in Studio
- [ ] Initial state accepts `project_context`
- [ ] Node executes successfully
- [ ] All context fields are populated
- [ ] Values are valid (within allowed ranges)
- [ ] Entities are extracted correctly
- [ ] Error handling works (test with invalid input)
- [ ] Fallback defaults work (test with unparseable response)

## Next Steps

After successful testing:

1. **Test in Full Workflow**: Test complexity analyzer as part of the full agent swarm
2. **Phase 2**: Test agent selection that uses detected context
3. **Phase 3**: Test requirements analyst that uses context
4. **Phase 4**: Test knowledge routing using domain detection

## File Locations

- **Graph File**: `workflow/complexity_analyzer_studio.py`
- **Configuration**: `langgraph.json`
- **Test File**: `tests/workflow/test_context_detection_phase1.py`
- **Main Workflow**: `workflow/langgraph_workflow.py` (contains full implementation)

## Related Documentation

- US-CONTEXT-001 User Story: `docs/agile/sprints/sprint_7/user_stories/US-CONTEXT-001.md`
- Implementation Plan: `docs/agile/sprints/sprint_7/user_stories/US-CONTEXT-001_IMPLEMENTATION_PLAN_REVISED.md`
- LangGraph Patterns: `docs/architecture/LANGGRAPH_STANDARD_PATTERNS.md`

