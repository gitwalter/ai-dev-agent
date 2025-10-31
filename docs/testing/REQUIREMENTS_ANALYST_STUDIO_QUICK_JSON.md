# Requirements Analyst Studio - Quick Test JSON Reference

## 🚀 Start Requirements Analyst - Initial State

```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search", "vector", "embeddings", "qdrant"],
  "requirements_analysis": {},
  "functional_requirements": [],
  "non_functional_requirements": [],
  "user_stories": [],
  "technical_constraints": [],
  "business_constraints": [],
  "assumptions": [],
  "risks": [],
  "analysis_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "analysis_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## ✅ Approve Requirements (No Changes)

```json
{
  "human_approval": "approved"
}
```

## 🔄 Request Refinement - Add Requirements

```json
{
  "human_feedback": "Add requirement for authentication and user management. Include security requirements for API access.",
  "human_approval": "needs_refinement"
}
```

## 🔄 Request Refinement - Modify Requirements

```json
{
  "human_feedback": "The performance requirements should specify response time < 200ms. Add scalability requirement for 1000 concurrent users.",
  "human_approval": "needs_refinement"
}
```

## ❌ Reject Requirements

```json
{
  "human_feedback": "Requirements are too vague. Need more specific acceptance criteria.",
  "human_approval": "rejected"
}
```

## 📋 Alternative Initial States

### Simple Bug Fix Project
```json
{
  "project_context": "Fix authentication bug where invalid credentials are accepted",
  "project_complexity": "simple",
  "project_domain": "web",
  "project_intent": "bug_fix",
  "detected_entities": ["authentication", "security", "bug"],
  "requirements_analysis": {},
  "functional_requirements": [],
  "non_functional_requirements": [],
  "user_stories": [],
  "technical_constraints": [],
  "business_constraints": [],
  "assumptions": [],
  "risks": [],
  "analysis_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "analysis_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

### Web API Project
```json
{
  "project_context": "Build REST API for e-commerce product management with CRUD operations",
  "project_complexity": "medium",
  "project_domain": "api",
  "project_intent": "new_feature",
  "detected_entities": ["rest", "api", "e-commerce", "crud"],
  "requirements_analysis": {},
  "functional_requirements": [],
  "non_functional_requirements": [],
  "user_stories": [],
  "technical_constraints": [],
  "business_constraints": [],
  "assumptions": [],
  "risks": [],
  "analysis_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "analysis_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## 📝 How to Use in LangGraph Studio

1. **Select Graph**: `_requirements_analyst` from dropdown
2. **Start State**: Copy initial state JSON above
3. **Execute**: Click Run button
4. **Review**: Check `analysis_summary` for requirements analysis
5. **Provide Feedback**: Edit state JSON with `human_feedback` and `human_approval`
6. **Resume**: Click Resume to continue workflow

## 🔄 Iterative Refinement Process

1. **First Run**: Agent analyzes requirements
2. **HITL Pause**: Review requirements in `analysis_summary`
3. **Provide Feedback**: Update state with `human_feedback` and `human_approval: "needs_refinement"`
4. **Resume**: Agent refines requirements based on feedback
5. **Repeat**: Up to 3 iterations
6. **Finalize**: Approve or reject to end workflow

## ⚠️ Important Notes

- **Max Iterations**: 3 (safety limit)
- **Auto-Approval**: High confidence (≥90%) auto-approves if no feedback
- **Feedback Format**: Free text in `human_feedback` field
- **Approval Options**: `"approved"`, `"rejected"`, `"needs_refinement"`

