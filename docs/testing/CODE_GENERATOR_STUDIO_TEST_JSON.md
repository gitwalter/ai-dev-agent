# Code Generator Studio - Test JSON Examples

## 🚀 Initial State JSON (Start Code Generator)

### Complete State with Context, Requirements, and Architecture (Recommended)
```json
{
  "project_context": "Build a RAG system for document search using vector embeddings and Qdrant database",
  "project_complexity": "complex",
  "project_domain": "ai",
  "project_intent": "new_feature",
  "detected_entities": ["rag", "document", "search", "vector", "embeddings", "qdrant"],
  "requirements_analysis": {
    "summary": "Build a comprehensive RAG system for document search with vector embeddings"
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
  "business_constraints": [],
  "assumptions": ["Documents are in PDF or text format"],
  "risks": [],
  "architecture_design": {
    "system_overview": "Microservices-based RAG system with separate ingestion and search services",
    "architecture_pattern": "Microservices"
  },
  "system_overview": "Microservices-based RAG system with separate ingestion and search services",
  "architecture_pattern": "Microservices",
  "components": [
    {
      "name": "Document Ingestion Service",
      "description": "Handles document upload and embedding generation",
      "technology": "Python 3.11 + FastAPI"
    },
    {
      "name": "Search Service",
      "description": "Handles vector search queries",
      "technology": "Python 3.11 + FastAPI"
    }
  ],
  "technology_stack": {
    "backend": ["Python 3.11", "FastAPI 0.115"],
    "database": ["Qdrant"],
    "infrastructure": ["Docker"]
  },
  "data_flow": "Documents → Embedding → Qdrant → Search",
  "security_considerations": ["API authentication"],
  "scalability_considerations": ["Horizontal scaling"],
  "performance_considerations": ["Caching"],
  "deployment_strategy": "Docker containers",
  "code_files": {},
  "code_metadata": {},
  "file_tree": "",
  "plan": [],
  "assumptions": [],
  "tests": {},
  "runbook": {},
  "config_notes": "",
  "api_contracts": [],
  "security_review": [],
  "performance_notes": [],
  "limitations": [],
  "generation_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "generation_summary": "",
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
  "project_context": "Build a simple REST API for todo list management",
  "project_complexity": "simple",
  "project_domain": "api",
  "project_intent": "new_feature",
  "detected_entities": ["rest", "api"],
  "requirements_analysis": {
    "summary": "Simple REST API for todo list CRUD operations"
  },
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "CRUD Operations",
      "description": "Create, read, update, delete todos",
      "priority": "High"
    }
  ],
  "non_functional_requirements": [],
  "technical_constraints": ["Python 3.11", "FastAPI"],
  "business_constraints": [],
  "assumptions": [],
  "risks": [],
  "architecture_design": {
    "system_overview": "Simple REST API with FastAPI",
    "architecture_pattern": "Monolithic"
  },
  "system_overview": "Simple REST API with FastAPI",
  "architecture_pattern": "Monolithic",
  "components": [
    {
      "name": "API Service",
      "description": "REST API endpoints",
      "technology": "Python 3.11 + FastAPI"
    }
  ],
  "technology_stack": {
    "backend": ["Python 3.11", "FastAPI"]
  },
  "data_flow": "",
  "security_considerations": [],
  "scalability_considerations": [],
  "performance_considerations": [],
  "deployment_strategy": "",
  "code_files": {},
  "code_metadata": {},
  "file_tree": "",
  "plan": [],
  "assumptions": [],
  "tests": {},
  "runbook": {},
  "config_notes": "",
  "api_contracts": [],
  "security_review": [],
  "performance_notes": [],
  "limitations": [],
  "generation_confidence": 0.0,
  "needs_more_info": false,
  "information_requests": [],
  "generation_summary": "",
  "human_feedback": "",
  "human_approval": "",
  "iteration_count": 0,
  "current_step": "start",
  "errors": []
}
```

## ✅ Approve Code Generation (No Changes)

```json
{
  "human_approval": "approved"
}
```

## 🔄 Request Refinement - Add File

```json
{
  "human_feedback": "Add authentication module with JWT token handling. Include tests for authentication endpoints.",
  "human_approval": "needs_refinement"
}
```

## 🔄 Request Refinement - Fix Code

```json
{
  "human_feedback": "Fix error handling in the search endpoint. Add input validation for query parameters.",
  "human_approval": "needs_refinement"
}
```

## 🔄 Request Refinement - Improve Code Quality

```json
{
  "human_feedback": "Add logging throughout the codebase. Improve error messages to be more descriptive.",
  "human_approval": "needs_refinement"
}
```

## ❌ Reject Code Generation

```json
{
  "human_feedback": "Generated code doesn't follow the architecture pattern. Needs to be refactored to match microservices design.",
  "human_approval": "rejected"
}
```

## 📋 Complete Test Scenarios

### Scenario 1: Simple Approval Flow
**Step 1 - Initial State:** (Use Minimal State example above)

**Step 2 - After Generation (Approve):**
```json
{
  "human_approval": "approved"
}
```

### Scenario 2: Refinement Flow
**Step 1 - Initial State:** (Use Complete State example above)

**Step 2 - After Generation (Request Refinement):**
```json
{
  "human_feedback": "Add database models file. Include configuration file for database connection.",
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

1. **Select Graph**: Choose `_code_generator` from LangGraph Studio dropdown
2. **Copy Initial State**: Copy one of the initial state JSON examples above
3. **Paste & Execute**: Paste into Studio and click Run
4. **Review Code**: Check `generation_summary` and `code_files` fields in state
5. **Provide Feedback**: Edit state JSON with `human_feedback` and `human_approval`
6. **Resume**: Click Resume to continue workflow
7. **Iterate**: Repeat feedback/resume up to 3 times
8. **Finalize**: Approve or reject to end workflow

## ⚠️ Important Notes

- **Max Iterations**: 3 (safety limit - workflow ends after 3 refinements)
- **Auto-Approval**: High confidence (≥90%) auto-approves if no feedback provided
- **Feedback Format**: Free text in `human_feedback` field
- **Approval Options**: 
  - `"approved"` - Accept code generation and end workflow
  - `"rejected"` - Reject code generation and end workflow
  - `"needs_refinement"` - Request refinement (loops back to generation)
- **Context Fields**: Ensure `project_domain`, `project_intent`, `project_complexity`, and `detected_entities` are set from complexity_analyzer output
- **Requirements Fields**: Ensure `requirements_analysis`, `functional_requirements`, and `non_functional_requirements` are set from requirements_analyst output
- **Architecture Fields**: Ensure `architecture_design`, `components`, and `technology_stack` are set from architecture_designer output

## 🔄 Input Flow

The code generator expects:
1. **Context from Complexity Analyzer**: `project_domain`, `project_intent`, `project_complexity`, `detected_entities`
2. **Requirements from Requirements Analyst**: `requirements_analysis`, `functional_requirements`, `non_functional_requirements`, `technical_constraints`
3. **Architecture from Architecture Designer**: `architecture_design`, `components`, `technology_stack`, `architecture_pattern`

This allows the code generator to create context-aware, requirements-driven, and architecture-guided production-ready code.

## 📁 Generated Code Structure

The code generator produces:
- **code_files**: Dictionary of file paths to code content
- **file_tree**: Text representation of file structure
- **plan**: Implementation plan steps
- **assumptions**: Assumptions made during generation
- **tests**: Test strategy and coverage goals
- **runbook**: Setup, run, build, lint commands
- **config_notes**: Configuration rationale
- **api_contracts**: API interface definitions
- **security_review**: Security controls implemented
- **performance_notes**: Performance optimizations
- **limitations**: Known gaps and next steps

