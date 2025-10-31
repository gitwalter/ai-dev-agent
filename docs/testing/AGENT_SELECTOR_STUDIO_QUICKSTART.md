# Agent Selector Studio Testing Guide

## Overview

This guide explains how to test the isolated agent selector graph in LangGraph Studio, following the same pattern as the complexity analyzer.

## Quick Start

1. **Open LangGraph Studio**
2. **Select Graph**: `_agent_selector` from dropdown
3. **Input State**: Use JSON format below
4. **Execute**: Click Run button
5. **Verify**: Check output state for selected agents

## Required Initial State Format

```json
{
  "project_context": "Your project description here",
  "project_complexity": "medium",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search"],
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

**Note**: You need to provide context from complexity_analyzer:
- `project_complexity`: simple, medium, or complex
- `project_domain`: ai, web, api, data, mobile, library, utility, or general
- `project_intent`: new_feature, bug_fix, refactor, migration, enhancement, or general
- `detected_entities`: Array of technology names

## Graph Flow with Iterative Refinement Loop

```
START → select_agents → [HITL PAUSE] → review_selection → [conditional]
                                                          ├→ select_agents (if needs_refinement)
                                                          └→ finalize_selection → END (if approved/rejected)
```

**HITL Checkpoint**: Graph pauses AFTER `select_agents` completes (interrupt_after)

**Iterative Loop**: If `human_approval: "needs_refinement"`, graph loops back to re-select with refined information

**End Conditions**:
- ✅ `human_approval: "approved"` → END
- ❌ `human_approval: "rejected"` → END  
- ⚠️ `iteration_count >= 3` → END (safety limit)
- ✅ `selection_confidence >= 0.9` AND no feedback → END (auto-approve)

## How to Provide Feedback

**IMPORTANT**: In LangGraph Studio, you provide feedback by **updating the state JSON**, NOT through a chat interface!

### Step 1: Graph Pauses at Checkpoint

When you execute the graph, it will:
- Run `select_agents` node
- **Pause automatically** AFTER selection completes (interrupt_after)
- Show selected agents in the state
- Show "Interrupted" status in Studio

### Step 2: Review Selected Agents

Look at the **State** panel:
- `required_agents`: Array of selected agent names
- `selection_reasoning`: Why these agents were selected
- `selection_confidence`: Confidence score (0.0 to 1.0)
- `selection_summary`: Human-readable summary

### Step 3: Update State with Feedback

#### Option A: Approve (No Changes Needed)

If the selected agents are correct:
1. **Don't change anything** in the state
2. Click **"Resume"** or **"Continue"** button
3. Graph will complete execution

#### Option B: Request Refinement (needs_refinement)

If you want to refine the agent selection:

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

#### Option C: Reject

If the selection is completely wrong:

```json
{
  "human_approval": "rejected"
}
```

**What happens**: Workflow ends immediately with rejection status

### Step 4: Resume Execution

1. **Click "Resume"** or **"Continue"** button in Studio
2. Graph will:
   - Process your feedback
   - Continue to `review_selection` node
   - Loop back to `select_agents` if refinement requested
   - Complete execution with final message

## State Fields for Feedback

### Required Fields (Always Present)

```json
{
  "project_context": "Your project description",
  "project_complexity": "medium",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": [],
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

### Feedback Fields

- **`human_feedback`**: Text feedback about agent selection
  - Example: "Add test_generator" or "Remove architecture_designer"
  
- **`human_approval`**: Approval status
  - `"approved"`: Accept selection and end workflow
  - `"rejected"`: Reject selection and end workflow
  - `"needs_refinement"`: Refine selection and loop back

## Example Test Cases

### Test Case 1: Simple Project (Bug Fix)

**Input**:
```json
{
  "project_context": "Fix bug in authentication module where invalid tokens are accepted",
  "project_complexity": "simple",
  "project_domain": "web",
  "project_intent": "bug_fix",
  "detected_entities": ["authentication", "tokens"]
}
```

**Expected Selection**:
- `requirements_analyst` (always required)
- `code_generator` (always required)
- `test_generator` (bug fix needs tests)
- `code_reviewer` (review fix)
- `documentation_generator` (always required)

**Expected Confidence**: High (0.8+)

### Test Case 2: Complex AI Project

**Input**:
```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search", "vector", "embeddings", "qdrant"]
}
```

**Expected Selection**:
- All agents (complex AI project needs full lifecycle)

**Expected Confidence**: High (0.9+)

### Test Case 3: Refinement Request

**Input** (after initial selection):
```json
{
  "human_feedback": "Add security_analyst for security review",
  "human_approval": "needs_refinement"
}
```

**Expected Behavior**:
- System extracts "security_analyst" from feedback
- Adds to selection (if valid agent)
- Loops back to re-select
- Confidence increases

## Available Agents

- **requirements_analyst**: Analyzes requirements and creates user stories (ALWAYS REQUIRED)
- **architecture_designer**: Designs system architecture (Required for medium+, web_app, api, data_processing)
- **code_generator**: Generates production-ready code (ALWAYS REQUIRED)
- **test_generator**: Creates test suites (Required for medium+, critical functionality)
- **code_reviewer**: Reviews code quality (Required for medium+, production code)
- **documentation_generator**: Creates documentation (ALWAYS REQUIRED)

## Standard Execution Order

Agents execute in this order (enforced by code, not LLM):

1. `requirements_analyst` (always first)
2. `architecture_designer` (if selected)
3. `code_generator` (always required)
4. `test_generator` (if selected)
5. `code_reviewer` (if selected)
6. `documentation_generator` (always last)

## Troubleshooting

### Issue: No agents selected

**Solution**: Check that `project_context` is provided and contains enough detail

### Issue: Wrong agents selected

**Solution**: Use `human_approval: "needs_refinement"` with feedback to refine selection

### Issue: Workflow doesn't end

**Solution**: Check that `human_approval` is set to `"approved"` or `"rejected"`

### Issue: Selection confidence is low

**Solution**: Provide more context in `project_context`, `project_domain`, or `project_intent`

## Next Steps

After testing agent selector:
1. Verify agent selection accuracy
2. Test refinement loop
3. Verify final completion message
4. Move to next node in workflow (router or specific agents)

