# Architecture Designer Studio - Test JSON Examples

## 🚀 Initial State JSON (Start Architecture Designer)

### Complete State with Requirements (Recommended)
```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search", "vector", "embeddings", "qdrant"],
  "requirements_analysis": {
    "summary": "Build a comprehensive RAG system for document search with vector embeddings",
    "functional_requirements": [
      {
        "id": "FR-001",
        "title": "Document Ingestion",
        "description": "System should ingest documents and create vector embeddings",
        "priority": "High",
        "acceptance_criteria": ["Documents can be uploaded", "Embeddings are generated"]
      },
      {
        "id": "FR-002",
        "title": "Vector Search",
        "description": "System should perform semantic search using vector similarity",
        "priority": "High",
        "acceptance_criteria": ["Search queries return relevant documents", "Results ranked by similarity"]
      }
    ],
    "non_functional_requirements": [
      {
        "id": "NFR-001",
        "category": "Performance",
        "description": "Search response time should be < 200ms",
        "metric": "Response time < 200ms",
        "priority": "High"
      },
      {
        "id": "NFR-002",
        "category": "Scalability",
        "description": "System should handle 1000 concurrent users",
        "metric": "1000 concurrent users",
        "priority": "Medium"
      }
    ]
  },
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "Document Ingestion",
      "description": "System should ingest documents and create vector embeddings",
      "priority": "High"
    },
    {
      "id": "FR-002",
      "title": "Vector Search",
      "description": "System should perform semantic search using vector similarity",
      "priority": "High"
    }
  ],
  "non_functional_requirements": [
    {
      "id": "NFR-001",
      "category": "Performance",
      "description": "Search response time should be < 200ms",
      "metric": "Response time < 200ms",
      "priority": "High"
    }
  ],
  "technical_constraints": ["Use Qdrant for vector storage", "Python 3.11+"],
  "business_constraints": ["Budget limited", "Quick time-to-market"],
  "assumptions": ["Documents are in PDF or text format"],
  "risks": ["Vector database scalability", "Embedding model performance"],
  "architecture_design": {},
  "system_overview": "",
  "architecture_pattern": "",
  "components": [],
  "technology_stack": {},
  "data_flow": "",
  "security_considerations": [],
  "scalability_considerations": [],
  "performance_considerations": [],
  "deployment_strategy": "",
  "design_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "design_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

### Minimal State (For Quick Testing)
```json
{
  "project_context": "Build a REST API for e-commerce product management",
  "project_complexity": "medium",
  "project_domain": "api",
  "project_intent": "new_feature",
  "detected_entities": ["rest", "api", "e-commerce"],
  "requirements_analysis": {
    "summary": "Build REST API for product management with CRUD operations"
  },
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "Product CRUD",
      "description": "Create, read, update, delete products",
      "priority": "High"
    }
  ],
  "non_functional_requirements": [
    {
      "id": "NFR-001",
      "category": "Security",
      "description": "API authentication required",
      "priority": "High"
    }
  ],
  "technical_constraints": [],
  "business_constraints": [],
  "assumptions": [],
  "risks": [],
  "architecture_design": {},
  "system_overview": "",
  "architecture_pattern": "",
  "components": [],
  "technology_stack": {},
  "data_flow": "",
  "security_considerations": [],
  "scalability_considerations": [],
  "performance_considerations": [],
  "deployment_strategy": "",
  "design_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "design_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## ✅ Approve Architecture (No Changes)

```json
{
  "human_approval": "approved"
}
```

## 🔄 Request Refinement - Add Component

```json
{
  "human_feedback": "Add an authentication service component using OAuth 2.0. Include API gateway component for rate limiting.",
  "human_approval": "needs_refinement"
}
```

## 🔄 Request Refinement - Change Architecture Pattern

```json
{
  "human_feedback": "Change architecture pattern from monolithic to microservices. Add service mesh for inter-service communication.",
  "human_approval": "needs_refinement"
}
```

## 🔄 Request Refinement - Update Technology Stack

```json
{
  "human_feedback": "Use FastAPI instead of Flask for backend. Add Redis for caching. Use PostgreSQL instead of MongoDB.",
  "human_approval": "needs_refinement"
}
```

## ❌ Reject Architecture

```json
{
  "human_feedback": "Architecture is too complex for the project scope. Need simpler monolithic design.",
  "human_approval": "rejected"
}
```

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
  "requirements_analysis": {"summary": "Simple todo list API"},
  "functional_requirements": [{"id": "FR-001", "title": "CRUD operations", "priority": "High"}],
  "non_functional_requirements": [],
  "technical_constraints": [],
  "business_constraints": [],
  "assumptions": [],
  "risks": [],
  "architecture_design": {},
  "system_overview": "",
  "architecture_pattern": "",
  "components": [],
  "technology_stack": {},
  "data_flow": "",
  "security_considerations": [],
  "scalability_considerations": [],
  "performance_considerations": [],
  "deployment_strategy": "",
  "design_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "design_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

**Step 2 - After Design (Approve):**
```json
{
  "human_approval": "approved"
}
```

### Scenario 2: Refinement Flow
**Step 1 - Initial State:** (Use Complete State example above)

**Step 2 - After Design (Request Refinement):**
```json
{
  "human_feedback": "Add caching layer component using Redis. Include message queue component for async processing.",
  "human_approval": "needs_refinement"
}
```

**Step 3 - After Refinement (Approve):**
```json
{
  "human_approval": "approved"
}
```

## 📝 Usage Instructions

1. **Select Graph**: Choose `_architecture_designer` from LangGraph Studio dropdown
2. **Copy Initial State**: Copy one of the initial state JSON examples above
3. **Paste & Execute**: Paste into Studio and click Run
4. **Review Design**: Check `design_summary` field in state
5. **Provide Feedback**: Edit state JSON with `human_feedback` and `human_approval`
6. **Resume**: Click Resume to continue workflow
7. **Iterate**: Repeat feedback/resume up to 3 times
8. **Finalize**: Approve or reject to end workflow

## ⚠️ Important Notes

- **Max Iterations**: 3 (safety limit - workflow ends after 3 refinements)
- **Auto-Approval**: High confidence (≥90%) auto-approves if no feedback provided
- **Feedback Format**: Free text in `human_feedback` field
- **Approval Options**: 
  - `"approved"` - Accept architecture and end workflow
  - `"rejected"` - Reject architecture and end workflow
  - `"needs_refinement"` - Request refinement (loops back to design)
- **Context Fields**: Ensure `project_domain`, `project_intent`, `project_complexity`, and `detected_entities` are set from complexity_analyzer output
- **Requirements Fields**: Ensure `requirements_analysis`, `functional_requirements`, and `non_functional_requirements` are set from requirements_analyst output

## 🔄 Input Flow

The architecture designer expects:
1. **Context from Complexity Analyzer**: `project_domain`, `project_intent`, `project_complexity`, `detected_entities`
2. **Requirements from Requirements Analyst**: `requirements_analysis`, `functional_requirements`, `non_functional_requirements`, `technical_constraints`

This allows the architecture designer to create context-aware and requirements-driven architecture designs.

