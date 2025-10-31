# How to Provide Feedback in LangGraph Studio - Agent Selector HITL Guide

## Understanding LangGraph Studio Interrupts

When the graph pauses at a HITL checkpoint (`interrupt_after`), LangGraph Studio:

1. **Pauses execution** after the specified node completes
2. **Shows current state** in the state viewer
3. **Waits for you to update the state** (not a chat input!)
4. **Resumes execution** when you click Resume

## How to Provide Feedback

### Step 1: Graph Pauses at Checkpoint

When you execute the graph, it will:
- Run `select_agents` node
- **Pause automatically** AFTER selection completes (interrupt_after)
- Show selected agents in the state
- Show "Interrupted" status in Studio

### Step 2: Review Selected Agents

Look at the **State** panel (usually on the right side or bottom):

Check these fields:
- `required_agents`: Array of selected agent names
- `selection_summary`: Human-readable summary
- `selection_confidence`: Confidence score
- `selection_reasoning`: Why these agents were selected
- `needs_more_info`: Boolean flag
- `information_requests`: Array of questions

### Step 3: Update State with Feedback

**IMPORTANT**: In LangGraph Studio, you provide feedback by **updating the state JSON directly**.

#### Option A: Approve (No Changes Needed)

If the selected agents are correct:
1. **Don't change anything** in the state
2. Click **"Resume"** or **"Continue"** button
3. Graph will complete execution

#### Option B: Request Refinement (needs_refinement)

If you want to refine the agent selection with additional agents:

```json
{
  "human_feedback": "Add test_generator and code_reviewer",
  "human_approval": "needs_refinement"
}
```

**What happens when you provide refinement feedback:**
- ✅ **Agents extracted**: System extracts agent names from feedback
- ✅ **Selection updated**: Feedback agents merged with existing selection
- ✅ **Order enforced**: Agents sorted according to standard order
- ✅ **Confidence boosted**: Confidence score increases slightly
- ✅ **Summary updated**: Review message shows "Refinement Applied" section

**Example output**:
```
## Human Feedback Received

Add test_generator and code_reviewer

### Refinement Applied ✅

- **Updated Agents**: requirements_analyst, architecture_designer, code_generator, test_generator, code_reviewer, documentation_generator
- **Confidence Updated**: 95%
- **Next**: Will re-select agents with refined information
```

#### Option C: Remove Agents

If you want to remove specific agents:

```json
{
  "human_feedback": "Remove architecture_designer, this is a simple project",
  "human_approval": "needs_refinement"
}
```

The system will:
- Detect "remove" keyword
- Extract agent name from feedback
- Remove from selection on next iteration

#### Option D: Correct Detected Values

If you want to manually correct the agent selection:

```json
{
  "required_agents": ["requirements_analyst", "code_generator", "documentation_generator"],
  "human_feedback": "This is a simple project, only need these agents",
  "human_approval": "approved"
}
```

### Step 4: Resume Execution

1. **Click "Resume"** or **"Continue"** button in Studio
2. Graph will:
   - Process your feedback
   - Continue to `review_selection` node
   - Loop back to `select_agents` if refinement requested
   - Complete execution

## Feedback Format Examples

### Add Agents
```json
{
  "human_feedback": "Add test_generator",
  "human_approval": "needs_refinement"
}
```

### Remove Agents
```json
{
  "human_feedback": "Remove architecture_designer",
  "human_approval": "needs_refinement"
}
```

### Replace Selection
```json
{
  "human_feedback": "Only need requirements_analyst, code_generator, documentation_generator",
  "human_approval": "needs_refinement"
}
```

### Approve Current Selection
```json
{
  "human_approval": "approved"
}
```

### Reject Selection
```json
{
  "human_approval": "rejected"
}
```

## State Fields Reference

### Input Fields (Context from complexity_analyzer)
- `project_context`: Project description
- `project_complexity`: simple, medium, or complex
- `project_domain`: ai, web, api, data, mobile, library, utility, or general
- `project_intent`: new_feature, bug_fix, refactor, migration, enhancement, or general
- `detected_entities`: Array of technology names

### Output Fields (Agent Selection)
- `required_agents`: Array of selected agent names
- `selection_reasoning`: Why these agents were selected
- `selection_confidence`: Confidence score (0.0 to 1.0)
- `selection_summary`: Human-readable summary

### Feedback Fields
- `human_feedback`: Text feedback about selection
- `human_approval`: approved, rejected, or needs_refinement

### Tracking Fields
- `iteration_count`: Number of refinement iterations
- `current_step`: Current workflow step
- `errors`: Array of error messages

## Tips for Effective Feedback

1. **Be Specific**: Mention exact agent names
   - Good: "Add test_generator"
   - Bad: "Add testing"

2. **Use Clear Language**: 
   - Good: "Remove architecture_designer"
   - Bad: "Don't need architecture stuff"

3. **Provide Context**:
   - Good: "Add security_analyst because this project handles sensitive data"
   - Bad: "Add security"

4. **Combine Operations**:
   - Good: "Add test_generator and code_reviewer"
   - Bad: Multiple separate feedback messages

## Common Patterns

### Pattern 1: Simple Project (Minimum Agents)
```json
{
  "human_feedback": "This is a simple project, only need requirements_analyst, code_generator, documentation_generator",
  "human_approval": "needs_refinement"
}
```

### Pattern 2: Add Missing Agents
```json
{
  "human_feedback": "Add test_generator for test coverage",
  "human_approval": "needs_refinement"
}
```

### Pattern 3: Remove Unnecessary Agents
```json
{
  "human_feedback": "Remove architecture_designer, this is a bug fix",
  "human_approval": "needs_refinement"
}
```

### Pattern 4: Full Workflow (All Agents)
```json
{
  "human_approval": "approved"
}
```

## After Feedback

Once you provide feedback and resume:

1. **Turn 2**: Graph processes feedback
   - If `needs_refinement`: Loops back to `select_agents`
   - If `approved`: Goes to `finalize_selection` → END
   - If `rejected`: Goes to `finalize_selection` → END

2. **Final Message**: Check `selection_summary` for completion message

3. **Verify**: Check `required_agents` contains correct agents

## Troubleshooting

### Issue: Feedback not processed

**Solution**: Make sure `human_approval` is set correctly:
- `"needs_refinement"` for refinement
- `"approved"` for approval
- `"rejected"` for rejection

### Issue: Agents not extracted from feedback

**Solution**: Use exact agent names:
- Valid: `requirements_analyst`, `code_generator`, `test_generator`
- Invalid: `requirements`, `code`, `testing`

### Issue: Selection order wrong

**Solution**: Selection order is enforced by code automatically. Order is always:
1. requirements_analyst
2. architecture_designer
3. code_generator
4. test_generator
5. code_reviewer
6. documentation_generator

### Issue: Workflow loops infinitely

**Solution**: Max iterations limit (3) prevents infinite loops. Check `iteration_count` field.

