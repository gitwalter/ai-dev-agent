# Agent Q&A Guide - How to Ask Questions in Studio

## Overview

All Studio agents now support **Q&A (Question & Answer)** capability at HITL checkpoints. You can ask questions about agent decisions, outputs, or reasoning at any review step.

## How to Ask Questions

### Step 1: Graph Pauses at HITL Checkpoint

When the graph pauses at a review checkpoint (e.g., after `complexity_analyzer` completes), you'll see:
- Current state displayed
- Review summary showing agent's work
- Workflow paused, waiting for input

### Step 2: Add Question to State

Update the state JSON by adding a `human_question` field:

```json
{
  "human_question": "Why did you classify this as complex instead of medium?",
  ...other state fields...
}
```

### Step 3: Resume Workflow

Click **Resume** or **Continue** in Studio. The agent will:
1. Process your question
2. Generate an answer based on current state
3. Display answer in `agent_answer` field
4. Show Q&A in review summary

### Step 4: View Answer

Check the `agent_answer` field in state, or look at the review summary which includes:

```
## Question & Answer

**Question**: Why did you classify this as complex instead of medium?

**Answer**: [Agent's explanation based on detected context]
```

## Example Questions by Agent

### Complexity Analyzer

```json
{
  "human_question": "Why did you detect this as 'ai' domain?",
  "human_question": "What factors led to the 'complex' classification?",
  "human_question": "Can you explain why these entities were detected?",
  "human_question": "Why is the confidence score 0.85?"
}
```

### Agent Selector

```json
{
  "human_question": "Why did you select these specific agents?",
  "human_question": "Why wasn't test_generator included?",
  "human_question": "What criteria did you use for selection?",
  "human_question": "Can you explain the selection reasoning?"
}
```

### Requirements Analyst

```json
{
  "human_question": "Why are there only 3 functional requirements?",
  "human_question": "What gaps did you identify and why?",
  "human_question": "Can you explain the quality assessment?",
  "human_question": "Why is this requirement marked as High priority?"
}
```

### Architecture Designer

```json
{
  "human_question": "Why did you choose microservices pattern?",
  "human_question": "Can you explain the technology stack choices?",
  "human_question": "Why are there 5 components?",
  "human_question": "What security considerations are most important?"
}
```

### Code Generator

```json
{
  "human_question": "Why did you generate these specific files?",
  "human_question": "Can you explain the implementation plan?",
  "human_question": "What security measures were implemented?",
  "human_question": "Why is this architecture pattern used in the code?"
}
```

## Complete Example: Asking a Question

### Initial State
```json
{
  "project_context": "Build a RAG system for document search",
  "project_complexity": "",
  "project_domain": "",
  "project_intent": "",
  "detected_entities": [],
  "current_step": "start",
  "errors": []
}
```

### After Complexity Analyzer Completes (Graph Pauses)

State shows:
```json
{
  "project_context": "Build a RAG system for document search",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "vector", "embeddings"],
  "context_confidence": 0.85,
  "current_step": "context_review",
  ...other fields...
}
```

### Add Question and Resume

Update state:
```json
{
  "human_question": "Why is the confidence 0.85? What would make it higher?",
  ...all existing fields...
}
```

Click Resume → Agent answers → Answer appears in `agent_answer` field

### View Answer

Check `agent_answer` or review summary:
```
## Question & Answer

**Question**: Why is the confidence 0.85? What would make it higher?

**Answer**: The confidence is 0.85 because I detected domain (ai), intent (new_feature), 
complexity (complex), and several entities (rag, vector, embeddings). The confidence 
could be higher (closer to 0.95) if you provided more specific details about:
- Expected user load or scale
- Specific performance requirements
- Integration requirements with other systems
- Deployment environment details
```

## Q&A Best Practices

### 1. Ask Specific Questions
- ✅ **Good**: "Why did you select microservices pattern?"
- ❌ **Too vague**: "Why this?"

### 2. Ask About Decisions
- ✅ **Good**: "What factors led to this classification?"
- ✅ **Good**: "Can you explain the reasoning behind this choice?"

### 3. Ask About State Values
- ✅ **Good**: "Why is confidence 0.85 instead of higher?"
- ✅ **Good**: "What would increase the confidence score?"

### 4. Ask About Process
- ✅ **Good**: "How did you detect these entities?"
- ✅ **Good**: "What information did you use to make this decision?"

## Using Q&A with Feedback

You can combine questions with feedback:

```json
{
  "human_question": "Why did you select these agents?",
  "human_feedback": "Add test_generator to the selection",
  "human_approval": "needs_refinement"
}
```

The agent will:
1. Answer your question
2. Process your feedback
3. Refine the output

## Q&A vs Information Requests

### Agent Questions (Information Requests)
- Agent asks **you** questions when it needs more info
- Shown in `information_requests` field
- Example: "What is the expected user load?"

### Human Questions (Q&A)
- **You** ask agent questions about its work
- Add to `human_question` field
- Agent answers based on its state
- Example: "Why did you classify this as complex?"

## Technical Details

### State Fields Added

All agent states now include:
```python
human_question: str  # Question asked by human (for Q&A)
agent_answer: str    # Answer provided by agent to human question
```

### Q&A Node Integration

Q&A is integrated into all review nodes:
- `review_context_node` (complexity_analyzer)
- `review_selection_node` (agent_selector)
- `review_requirements_node` (requirements_analyst)
- `review_architecture_node` (architecture_designer)
- `review_code_node` (code_generator)

### Answer Generation

Answers are generated using:
- Current agent state
- Agent-specific context
- LLM (Gemini 2.5 Flash, temperature=0)
- Context-aware reasoning

## Files

- **Q&A Node**: `utils/agent_qa_node.py`
- **Integrated in**: All `*_studio.py` review nodes
- **This Guide**: `docs/testing/AGENT_QA_GUIDE.md`

## Quick Reference

| Step | Action |
|------|--------|
| **1. Graph pauses** | Wait for HITL checkpoint |
| **2. Add question** | Update state: `{"human_question": "Your question"}` |
| **3. Resume** | Click Resume button |
| **4. View answer** | Check `agent_answer` field or review summary |

## Example Workflow

```
1. Execute graph → Agent analyzes → Graph pauses
2. Review agent output in state
3. Add question: {"human_question": "Why...?"}
4. Resume → Agent answers → Answer in state
5. Continue with approval/refinement or ask more questions
```

**That's it!** All agents can now answer questions at every HITL checkpoint. Just add `human_question` to state and resume!

