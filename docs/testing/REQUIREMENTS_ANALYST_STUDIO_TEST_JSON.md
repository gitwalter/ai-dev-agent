# Requirements Analyst Studio - Test JSON Examples

## 🚀 Initial State JSON (Start Requirements Analyst)

### Complex RAG System Project (Recommended)
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

### Medium Web API Project
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

### Data Processing Project
```json
{
  "project_context": "Build ETL pipeline for processing customer data from multiple sources",
  "project_complexity": "complex",
  "project_domain": "data",
  "project_intent": "new_feature",
  "detected_entities": ["etl", "pipeline", "data", "processing", "customer"],
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

---

## ✅ Approve Requirements (No Changes Needed)

After reviewing the requirements analysis, if you approve:

```json
{
  "human_approval": "approved"
}
```

---

## 🔄 Request Refinement - Add Requirements

If you want to add more requirements:

```json
{
  "human_feedback": "Add requirement for authentication and user management. Include security requirements for API access.",
  "human_approval": "needs_refinement"
}
```

### Example: Add Performance Requirements
```json
{
  "human_feedback": "The performance requirements should specify response time < 200ms. Add scalability requirement for 1000 concurrent users.",
  "human_approval": "needs_refinement"
}
```

### Example: Add Security Requirements
```json
{
  "human_feedback": "Add comprehensive security requirements: OAuth 2.0 authentication, data encryption at rest and in transit, rate limiting, and audit logging.",
  "human_approval": "needs_refinement"
}
```

### Example: Add UI Requirements
```json
{
  "human_feedback": "Include requirements for responsive web UI that works on mobile and desktop. Add accessibility requirements (WCAG 2.1 AA compliance).",
  "human_approval": "needs_refinement"
}
```

---

## 🔄 Request Refinement - Modify Requirements

If you want to modify existing requirements:

```json
{
  "human_feedback": "Change the authentication requirement to use OAuth 2.0 instead of basic auth. Update the performance requirement to include 99.9% uptime SLA.",
  "human_approval": "needs_refinement"
}
```

### Example: Clarify Requirements
```json
{
  "human_feedback": "The requirements are too vague. Need more specific acceptance criteria for each functional requirement. Add measurable metrics for non-functional requirements.",
  "human_approval": "needs_refinement"
}
```

---

## ❌ Reject Requirements

If the requirements analysis is insufficient:

```json
{
  "human_feedback": "Requirements are too vague. Need more specific acceptance criteria.",
  "human_approval": "rejected"
}
```

### Example: Reject Due to Missing Information
```json
{
  "human_feedback": "Critical requirements missing: no mention of API versioning, error handling, or deployment strategy. Analysis incomplete.",
  "human_approval": "rejected"
}
```

---

## 📋 Complete Test Scenarios

### Scenario 1: Simple Approval Flow
**Step 1 - Initial State:**
```json
{
  "project_context": "Build a simple todo list API",
  "project_complexity": "simple",
  "project_domain": "api",
  "project_intent": "new_feature",
  "detected_entities": ["api", "todo"],
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

**Step 2 - After Analysis (Approve):**
```json
{
  "human_approval": "approved"
}
```

### Scenario 2: Refinement Flow
**Step 1 - Initial State:**
```json
{
  "project_context": "Build a RAG system for document search",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search"],
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

**Step 2 - After Analysis (Request Refinement):**
```json
{
  "human_feedback": "Add requirements for chunking strategy, embedding model selection, and retrieval accuracy metrics. Include scalability requirements for handling 1 million documents.",
  "human_approval": "needs_refinement"
}
```

**Step 3 - After Refinement (Approve):**
```json
{
  "human_approval": "approved"
}
```

### Scenario 3: Multiple Refinements
**Step 1 - Initial State:** (Use Complex RAG System example above)

**Step 2 - First Refinement:**
```json
{
  "human_feedback": "Add security requirements for API access",
  "human_approval": "needs_refinement"
}
```

**Step 3 - Second Refinement:**
```json
{
  "human_feedback": "Add deployment requirements: Docker containerization and Kubernetes orchestration",
  "human_approval": "needs_refinement"
}
```

**Step 4 - Final Approval:**
```json
{
  "human_approval": "approved"
}
```

---

## 📝 Usage Instructions

1. **Select Graph**: Choose `_requirements_analyst` from LangGraph Studio dropdown
2. **Copy Initial State**: Copy one of the initial state JSON examples above
3. **Paste & Execute**: Paste into Studio and click Run
4. **Review Analysis**: Check `analysis_summary` field in state
5. **Provide Feedback**: Edit state JSON with `human_feedback` and `human_approval`
6. **Resume**: Click Resume to continue workflow
7. **Iterate**: Repeat feedback/resume up to 3 times
8. **Finalize**: Approve or reject to end workflow

---

## ⚠️ Important Notes

- **Max Iterations**: 3 (safety limit - workflow ends after 3 refinements)
- **Auto-Approval**: High confidence (≥90%) auto-approves if no feedback provided
- **Feedback Format**: Free text in `human_feedback` field
- **Approval Options**: 
  - `"approved"` - Accept requirements and end workflow
  - `"rejected"` - Reject requirements and end workflow
  - `"needs_refinement"` - Request refinement (loops back to analysis)
- **Context Fields**: Ensure `project_domain`, `project_intent`, `project_complexity`, and `detected_entities` are set from complexity_analyzer output

