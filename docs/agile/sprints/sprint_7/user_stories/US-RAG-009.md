# User Story: US-RAG-009 - Development-Context RAG Tasks

**Epic**: EPIC-3: Agent Development & Optimization  
**Sprint**: Sprint 7  
**Story Points**: 21  
**Priority**: 🔴 **CRITICAL**  
**Status**: 📋 **BACKLOG**  
**Created**: 2025-10-28  
**Dependencies**: US-RAG-007 (Task-Adaptive RAG), US-CONTEXT-001 (Context Detection & Routing)

## Story Overview

**As a** development agent (Architecture Designer, Code Generator, Code Reviewer)  
**I want** specialized RAG workflows for development tasks  
**So that** I can access architecture docs, API documentation, coding standards, and examples relevant to my work

## Business Value

Transform RAG from general Q&A to **specialized development assistant** with task types specifically for development workflows:

1. **ARCHITECTURE_DESIGN**: Access architecture patterns, design docs, SOLID principles
2. **CODE_IMPLEMENTATION**: Access API docs, coding standards, working examples
3. **API_INTEGRATION**: Access official API documentation (NO GUESSING!)
4. **CODE_REVIEW**: Access coding standards, security guidelines, anti-patterns
5. **BUG_FIXING**: Access error patterns, known issues, debugging techniques
6. **TEST_GENERATION**: Access testing patterns, coverage requirements, edge cases
7. **REFACTORING**: Access refactoring catalogs, design patterns, code smells
8. **DOCUMENTATION_WRITING**: Access doc templates, style guides, examples
9. **AGILE_CONTEXT_RETRIEVAL**: Access sprint docs, user stories, requirements

## Acceptance Criteria

### Phase 1: Development Task Types
- [ ] **AC-1.1**: Define `DevTaskType` enum with 9 development task types
- [ ] **AC-1.2**: Implement task classification for development queries
- [ ] **AC-1.3**: Map development tasks to optimal agent combinations
- [ ] **AC-1.4**: Specify knowledge sources for each dev task type

### Phase 2: Knowledge Source Mapping
- [ ] **AC-2.1**: Map ARCHITECTURE_DESIGN → architecture docs, design patterns
- [ ] **AC-2.2**: Map CODE_IMPLEMENTATION → API docs, coding standards, examples
- [ ] **AC-2.3**: Map API_INTEGRATION → official API docs (PRIMARY source)
- [ ] **AC-2.4**: Map CODE_REVIEW → coding standards, security guidelines
- [ ] **AC-2.5**: Map BUG_FIXING → error patterns, debugging techniques
- [ ] **AC-2.6**: Map TEST_GENERATION → testing patterns, frameworks
- [ ] **AC-2.7**: Map REFACTORING → refactoring catalogs (Fowler)
- [ ] **AC-2.8**: Map DOCUMENTATION_WRITING → doc templates, style guides
- [ ] **AC-2.9**: Map AGILE_CONTEXT_RETRIEVAL → sprint docs, user stories

### Phase 3: Agent Composition for Dev Tasks
- [ ] **AC-3.1**: ARCHITECTURE_DESIGN workflow: query_analyst → architecture_doc_retriever → pattern_matcher → design_validator → architecture_writer
- [ ] **AC-3.2**: CODE_IMPLEMENTATION workflow: query_analyst → multi_source_retriever → code_synthesizer → quality_checker
- [ ] **AC-3.3**: API_INTEGRATION workflow: query_analyst → api_doc_retriever (official only!) → example_finder → integration_writer
- [ ] **AC-3.4**: CODE_REVIEW workflow: query_analyst → standards_retriever → code_analyzer → recommendation_writer
- [ ] **AC-3.5**: BUG_FIXING workflow: query_analyst → error_pattern_matcher → solution_retriever → fix_generator

### Phase 4: HITL Checkpoints for Dev Tasks
- [ ] **AC-4.1**: ARCHITECTURE_DESIGN checkpoints: After pattern selection, after design validation
- [ ] **AC-4.2**: CODE_IMPLEMENTATION checkpoints: After standards retrieval, after code generation
- [ ] **AC-4.3**: API_INTEGRATION checkpoints: After API doc retrieval (verify version!), after integration code
- [ ] **AC-4.4**: CODE_REVIEW checkpoints: After issue identification
- [ ] **AC-4.5**: BUG_FIXING checkpoints: After root cause hypothesis, after fix generation

### Phase 5: Integration with Development Agents
- [ ] **AC-5.1**: Architecture Designer delegates to RAG with ARCHITECTURE_DESIGN task type
- [ ] **AC-5.2**: Code Generator delegates to RAG with CODE_IMPLEMENTATION task type
- [ ] **AC-5.3**: Code Reviewer delegates to RAG with CODE_REVIEW task type
- [ ] **AC-5.4**: Bug Fixer delegates to RAG with BUG_FIXING task type

## Development Task Type Details

### 1. ARCHITECTURE_DESIGN
**When**: Designing system architecture, choosing patterns  
**Information Needed**:
- Architecture documentation (Onion, Clean, Microservices)
- Design patterns (Gang of Four, Enterprise patterns)
- SOLID principles, coupling/cohesion guidelines
- Component interaction patterns

**Agent Workflow**:
```
query_analyst (understand design requirements)
  ↓
[HITL: Approve design approach]
  ↓
architecture_doc_retriever (specialized for architecture docs)
  ↓
pattern_matcher (match patterns to requirements)
  ↓
[HITL: Approve pattern selection]
  ↓
design_validator (check SOLID, coupling, cohesion)
  ↓
architecture_writer (generate architecture doc)
  ↓
[HITL: Final architecture approval]
```

**Example**: "Design architecture for RAG document ingestion pipeline"

---

### 2. CODE_IMPLEMENTATION
**When**: Writing new code, implementing features  
**Information Needed**:
- Coding standards (PEP 8, type hints, docstrings)
- API documentation (LangChain, LangGraph, Framework APIs)
- Code examples (reference implementations)
- Project-specific conventions

**Agent Workflow**:
```
query_analyst (understand code requirements)
  ↓
multi_source_retriever (standards + API docs + examples + codebase)
  ↓
[HITL: Verify standards and API usage]
  ↓
code_synthesizer (generate implementation)
  ↓
[HITL: Review generated code]
  ↓
quality_checker (PEP 8, type checking, best practices)
```

**Example**: "Implement LangGraph agent with checkpointing and HITL"

---

### 3. API_INTEGRATION (CRITICAL!)
**When**: Integrating with external APIs, libraries  
**Information Needed**:
- **Official API documentation (NO GUESSING!)**
- Authentication patterns
- Error handling examples
- Working code examples from official sources

**Agent Workflow**:
```
query_analyst (understand API integration need)
  ↓
api_doc_retriever (official documentation ONLY)
  ↓
[HITL: Confirm correct API version and endpoints]
  ↓
example_finder (working examples from official sources)
  ↓
integration_code_writer (use documented patterns)
  ↓
[HITL: Review integration code]
```

**Example**: "Integrate LangSmith prompt management into agents"

**CRITICAL RULE**: For API integration, ONLY use official documentation. Never guess at API usage!

---

### 4. CODE_REVIEW
**When**: Reviewing code for quality, standards, security  
**Information Needed**:
- Coding standards and style guides
- Security best practices (OWASP, input validation)
- Performance guidelines
- Common anti-patterns

**Agent Workflow**:
```
query_analyst (identify review focus)
  ↓
standards_retriever (coding standards + security guidelines)
  ↓
code_analyzer (scan for issues)
  ↓
[HITL: Review identified issues]
  ↓
issue_prioritizer (critical vs. nice-to-have)
  ↓
recommendation_writer (actionable feedback)
```

**Example**: "Review this authentication code for security issues"

---

### 5. BUG_FIXING
**When**: Debugging issues, fixing bugs  
**Information Needed**:
- Error pattern database
- Stack trace analysis
- Similar bug resolutions
- Debugging techniques

**Agent Workflow**:
```
query_analyst (understand bug symptoms)
  ↓
error_pattern_matcher (find similar issues)
  ↓
[HITL: Confirm root cause hypothesis]
  ↓
solution_retriever (proven fixes)
  ↓
fix_generator (generate fix code)
  ↓
[HITL: Review and test fix]
```

**Example**: "Fix AttributeError in RAG coordinator"

---

## Technical Implementation

### DevTaskType Enum
```python
class DevTaskType(str, Enum):
    ARCHITECTURE_DESIGN = "architecture_design"
    CODE_IMPLEMENTATION = "code_implementation"
    API_INTEGRATION = "api_integration"
    CODE_REVIEW = "code_review"
    BUG_FIXING = "bug_fixing"
    TEST_GENERATION = "test_generation"
    REFACTORING = "refactoring"
    DOCUMENTATION_WRITING = "documentation_writing"
    AGILE_CONTEXT_RETRIEVAL = "agile_context_retrieval"
```

### Knowledge Source Routing
```python
DEV_TASK_KNOWLEDGE_SOURCES = {
    DevTaskType.ARCHITECTURE_DESIGN: [
        "docs/architecture/",
        "Design Patterns (Gang of Four)",
        "Clean Architecture (Uncle Bob)",
        "Enterprise Patterns (Fowler)"
    ],
    
    DevTaskType.CODE_IMPLEMENTATION: [
        "docs/guides/",
        "API Documentation",
        "Code Examples",
        "Current Codebase"
    ],
    
    DevTaskType.API_INTEGRATION: [
        "Official API Documentation (PRIMARY)",
        "Official Code Examples ONLY",
        "API Changelogs",
        "Integration Patterns"
    ],
    
    # ... other mappings
}
```

### Files Modified
- `agents/rag/rag_swarm_coordinator.py` - DevTaskType enum, dev workflows
- `agents/rag/development_rag_composer.py` - **NEW** Development-specific composer
- `agents/development/architecture_designer.py` - Delegate to RAG
- `agents/development/code_generator.py` - Delegate to RAG
- `agents/development/code_reviewer.py` - Delegate to RAG

### Integration with US-CONTEXT-001 (Context Detection & Routing)
- **Context Detection**: `ContextDetectionRouter` identifies dev task type (ARCHITECTURE_DESIGN, CODE_IMPLEMENTATION, etc.)
- **Tool Selection**: `ToolRAGSystem` retrieves dev-specific tools (code generation, architecture design, etc.)
- **Knowledge Routing**: `KnowledgeRouter` routes to dev knowledge collections (architecture docs, coding standards, API docs)
- **Dev Task Mapping**: Maps `DevTaskType` → context → tools → knowledge sources

## Testing Strategy

1. **Task Classification Test**: Verify dev task detection
2. **Knowledge Routing Test**: Verify correct sources loaded per task
3. **Workflow Test**: Test each dev task workflow
4. **Integration Test**: Test development agent delegation to RAG
5. **Quality Test**: Measure answer quality for dev tasks

## Definition of Done

- [ ] All 9 dev task types defined and classified
- [ ] Knowledge source mappings complete
- [ ] Agent compositions defined for each dev task
- [ ] HITL checkpoints implemented for each dev task
- [ ] Integration with development agents working
- [ ] All tests passing
- [ ] Documentation updated

## Dependencies

- Depends on: US-RAG-007 (Task-Adaptive RAG)
- Blocks: US-DEV-RAG-001 (RAG Integration into Development Workflow)

## Success Metrics

- Dev task classification accuracy: > 90%
- Developer satisfaction with RAG assistance
- Reduction in API integration errors (from documentation usage)
- Code quality improvements from standards enforcement

## Notes

**Key Insight**: Development tasks require specialized knowledge sources and workflows. A "simple Q&A" approach doesn't work for complex development scenarios.

**Critical Rule for API Integration**: ALWAYS use official documentation. No guessing, no assumptions, no outdated examples. This prevents bugs and ensures correct usage.

