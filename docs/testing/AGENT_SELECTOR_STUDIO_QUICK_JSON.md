# Agent Selector Studio - Quick Test JSON Reference

## 🚀 Start Agent Selector - Initial State

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

## ✅ Approve Selection (No Changes)

```json
{
  "human_approval": "approved"
}
```

## 🔄 Request Refinement - Add Agents

```json
{
  "human_feedback": "Add test_generator and code_reviewer",
  "human_approval": "needs_refinement"
}
```

## ❌ Reject Selection

```json
{
  "human_approval": "rejected"
}
```

