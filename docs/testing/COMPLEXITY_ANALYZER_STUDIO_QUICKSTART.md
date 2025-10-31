# Quick Reference: Testing Complexity Analyzer in Studio

## Quick Start

1. **Launch Studio**: `langgraph studio` (from project root)
2. **Select Graph**: `_complexity_analyzer` from dropdown
3. **Input State**: Use JSON format below
4. **Execute**: Click Run button
5. **Verify**: Check output state for detected context

## Required Initial State Format

```json
{
  "project_context": "Your project description here",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "context_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "context_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## Graph Flow with Iterative Refinement Loop

```
START → complexity_analyzer → [HITL PAUSE] → review_context → [conditional]
                                                              ├→ complexity_analyzer (if needs_refinement)
                                                              └→ END (if approved/rejected/max_iterations)
```

**HITL Checkpoint**: Graph pauses AFTER `complexity_analyzer` completes (interrupt_after)

**Iterative Loop**: If `human_approval: "needs_refinement"`, graph loops back to re-analyze with enriched context

**End Conditions**:
- ✅ `human_approval: "approved"` → END
- ❌ `human_approval: "rejected"` → END  
- ⚠️ `iteration_count >= 3` → END (safety limit)
- ✅ `context_confidence >= 0.9` AND no feedback → END (auto-approve)

## How to Provide Feedback

**IMPORTANT**: In LangGraph Studio, you provide feedback by **updating the state JSON**, NOT through a chat interface!

### When Graph Pauses:

1. **Review State**: Check detected context in the State panel
2. **Update State**: Edit the state JSON directly:
   - Add `human_feedback`: Your feedback text
   - Add `human_approval`: `"approved"`, `"rejected"`, or `"needs_refinement"`
   - Or update `project_context` with more information
3. **Click Resume**: Continue execution

**See**: `docs/testing/STUDIO_HITL_FEEDBACK_GUIDE.md` for detailed instructions

## Example Test Cases

### AI Project
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

### Bug Fix
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

## Expected Output Fields

- `project_complexity`: `"simple"` | `"medium"` | `"complex"`
- `project_domain`: `"ai"` | `"web"` | `"api"` | `"data"` | `"mobile"` | `"library"` | `"utility"` | `"general"`
- `project_intent`: `"new_feature"` | `"bug_fix"` | `"refactor"` | `"migration"` | `"enhancement"` | `"general"`
- `detected_entities`: `["entity1", "entity2", ...]`
- `context_confidence`: `0.0` to `1.0` (confidence score)
- `needs_more_info`: `true` if more information needed
- `information_requests`: `["question1", "question2"]` (if needs_more_info is true)
- `context_summary`: Human-readable summary string
- `current_step`: `"complexity_analyzed"` → `"context_review"`

## Files

- Graph: `workflow/complexity_analyzer_studio.py`
- Config: `langgraph.json` (entry: `"_complexity_analyzer"`)
- Full Guide: `docs/testing/TESTING_COMPLEXITY_ANALYZER_STUDIO.md`

