# How to Provide Feedback in LangGraph Studio - HITL Checkpoint Guide

## Understanding LangGraph Studio Interrupts

When the graph pauses at a HITL checkpoint (`interrupt_after`), LangGraph Studio:

1. **Pauses execution** after the specified node completes
2. **Shows current state** in the state viewer
3. **Waits for you to update the state** (not a chat input!)
4. **Resumes execution** when you click Resume

## How to Provide Feedback

### Step 1: Graph Pauses at Checkpoint

When you execute the graph, it will:
- Run `complexity_analyzer` node
- **Pause automatically** AFTER analysis completes (interrupt_after)
- Show detected context in the state
- Show "Interrupted" status in Studio

### Step 2: Review Detected Context

Look at the **State** panel (usually on the right side or bottom):

Check these fields:
- `context_summary`: Readable summary
- `context_confidence`: Confidence score
- `needs_more_info`: Boolean flag
- `information_requests`: Array of questions

### Step 3: Update State with Feedback

**IMPORTANT**: In LangGraph Studio, you provide feedback by **updating the state JSON directly**.

#### Option A: Approve (No Changes Needed)

If the detected context is correct:
1. **Don't change anything** in the state
2. Click **"Resume"** or **"Continue"** button
3. Graph will complete execution

#### Option B: Provide Additional Information

If the agent asked questions (`information_requests` array has questions):

1. **Find the state JSON** in the State panel
2. **Update `project_context`** field with additional information:

```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database. This is a new feature for our AI platform.",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search"],
  "human_feedback": "The project will use Qdrant for vector storage and FastAPI for the API",
  "human_approval": "approved"
}
```

3. **Or add feedback fields**:

```json
{
  "human_feedback": "Add more details: The system needs to handle PDF and Markdown files, and should support semantic search",
  "human_approval": "needs_refinement"
}
```

#### Option C: Request Refinement (needs_refinement)

If you want to refine the detected context with additional information:

```json
{
  "human_feedback": "Add more details: The system needs to handle PDF and Markdown files, and should support semantic search",
  "human_approval": "needs_refinement"
}
```

**What happens when you provide refinement feedback:**
- ✅ **Entities extracted**: System extracts technologies from feedback (PDF, Markdown, semantic search)
- ✅ **Context enriched**: Feedback merged into `project_context`
- ✅ **Entities updated**: New entities added to `detected_entities` list
- ✅ **Confidence boosted**: Confidence score increases slightly
- ✅ **Summary updated**: Review message shows "Refinement Applied" section

**Example output**:
```
## Human Feedback Received

Add more details: The system needs to handle PDF and Markdown files, and should support semantic search

### Refinement Applied ✅

- **Updated Entities**: rag, document, search, PDF, Markdown, semantic search
- **Context Enriched**: Additional requirements included
- **Confidence Updated**: 95%
```

#### Option D: Correct Detected Values

If you want to manually correct the detected context:

```json
{
  "project_domain": "ai",  // Change from "general" to "ai"
  "project_intent": "new_feature",  // Confirm or change
  "human_feedback": "The domain should be 'ai' not 'general'",
  "human_approval": "approved"
}
```

### Step 4: Resume Execution

1. **Click "Resume"** or **"Continue"** button in Studio
2. Graph will:
   - Process your feedback
   - Continue to `review_context` node
   - Complete execution
   - Show final state

## State Fields for Feedback

### Required Fields (Always Present)

```json
{
  "project_context": "Your project description",
  "project_complexity": "medium",
  "project_domain": "general",
  "project_intent": "new_feature",
  "detected_entities": [],
  "context_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "context_summary": "",
  "current_step": "complexity_analyzed",
  "errors": []
}
```

### Feedback Fields (Add These When Providing Feedback)

```json
{
  "human_feedback": "Your feedback text here",
  "human_approval": "approved" | "rejected" | "needs_refinement"
}
```

**human_approval values**:
- `"approved"`: Context is correct, proceed
- `"rejected"`: Context is wrong, needs correction
- `"needs_refinement"`: Context is partially correct, needs improvement

## Example Workflow

### Example 1: Approve Detected Context

**Initial State** (after `complexity_analyzer`):
```json
{
  "project_context": "Build a RAG system for document search",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search"],
  "context_confidence": 0.85,
  "needs_more_info": false
}
```

**Action**: 
- Don't change anything
- Click **Resume**
- Graph completes

### Example 2: Provide More Information

**Initial State** (after `complexity_analyzer`):
```json
{
  "project_context": "Build a system",
  "project_complexity": "medium",
  "project_domain": "general",
  "project_intent": "new_feature",
  "detected_entities": [],
  "context_confidence": 0.5,
  "needs_more_info": true,
  "information_requests": [
    "What domain does this project belong to?",
    "What technologies will be used?"
  ]
}
```

**Updated State** (before Resume):
```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant",
  "project_complexity": "medium",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "vector", "embeddings", "qdrant"],
  "context_confidence": 0.5,
  "needs_more_info": true,
  "information_requests": ["..."],
  "human_feedback": "Domain: AI, Technologies: RAG, vector embeddings, Qdrant",
  "human_approval": "approved"
}
```

**Action**: 
- Update state with additional info
- Click **Resume**
- Graph continues with updated context

### Example 3: Correct Detected Values

**Initial State**:
```json
{
  "project_domain": "general",
  "project_intent": "new_feature"
}
```

**Updated State**:
```json
{
  "project_domain": "api",  // Corrected from "general"
  "project_intent": "bug_fix",  // Corrected from "new_feature"
  "human_feedback": "This is actually an API bug fix, not a new feature",
  "human_approval": "approved"
}
```

## Visual Guide: Where to Find Things in Studio

```
┌─────────────────────────────────────────────────────────────┐
│ LangGraph Studio                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Graph Visualization]                                     │
│  START → complexity_analyzer → [PAUSED] → review_context  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  State Panel (Right Side or Bottom)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ State JSON (Editable)                               │   │
│  │ {                                                   │   │
│  │   "project_context": "...",                        │   │
│  │   "project_domain": "ai",                          │   │
│  │   ...                                               │   │
│  │   "human_feedback": "",  ← Add your feedback here   │   │
│  │   "human_approval": ""   ← Add approval here       │   │
│  │ }                                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Resume] [Cancel]  ← Click Resume to continue            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Issue: Can't find Resume button

**Solution**: 
- Make sure the graph is paused (check for "Interrupted" status)
- The Resume button appears when graph is at an interrupt point

### Issue: State JSON is read-only

**Solution**:
- Look for an "Edit" button or pencil icon
- Some Studio versions require clicking state to edit
- Try double-clicking the state JSON

### Issue: Feedback not being processed

**Solution**:
- Make sure you're updating state BEFORE clicking Resume
- State updates must be saved before resuming
- Check that `human_feedback` or `human_approval` fields are in the state

### Issue: Want to provide feedback but no questions shown

**Solution**:
- If `needs_more_info` is `false`, agent is confident
- You can still provide feedback by adding `human_feedback` field
- Set `human_approval` to `"approved"` to proceed

## Quick Reference

**To Approve**: 
- Don't change state
- Click Resume

**To Provide More Info**:
- Update `project_context` with additional details
- Add `human_feedback` field
- Set `human_approval` to `"approved"`
- Click Resume

**To Correct Values**:
- Update detected fields (`project_domain`, `project_intent`, etc.)
- Add `human_feedback` explaining corrections
- Set `human_approval` to `"approved"`
- Click Resume

## Next Steps

After providing feedback:
1. Graph processes feedback in `review_context` node
2. Shows updated context summary
3. Completes execution
4. Final state shows complete context detection results

For future enhancements:
- RAG capability to improve context detection
- Automatic refinement loop based on feedback
- Context persistence across sessions

