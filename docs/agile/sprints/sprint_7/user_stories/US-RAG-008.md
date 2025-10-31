# User Story: US-RAG-008 - Retrieval-Only Mode & Long-Running Project Support

**Epic**: EPIC-1: RAG System Enhancement  
**Sprint**: Sprint 7  
**Story Points**: 8  
**Priority**: 🟡 **HIGH**  
**Status**: 🟢 **IN PROGRESS**  
**Created**: 2025-10-28  
**Started**: 2025-10-28

## Story Overview

**As a** user who sometimes needs quick context lookups and sometimes needs long-running projects  
**I want** three operational modes: retrieval-only (fast), automated sophisticated, and HITL-guided  
**So that** I can choose the right level of processing for my needs and maintain project state across sessions

## Business Value

**Three Operational Modes for Different Needs**:

1. **MODE 1: Retrieval-Only** (Fast & Simple)
   - Quick context lookup
   - No sophisticated agents
   - No HITL checkpoints
   - ~5-10 seconds

2. **MODE 2: Automated Sophisticated** (Thorough)
   - All 5 sophisticated agents
   - No HITL checkpoints
   - Fully automated
   - ~30-60 seconds

3. **MODE 3: HITL-Guided** (Collaborative)
   - All 5 sophisticated agents
   - 6 HITL checkpoints
   - Human-guided workflow
   - 2-5 minutes (with feedback)

**Plus Long-Running Project Support**:
- Thread-based state persistence
- Multi-session continuity
- Pause and resume capability
- Full conversation history maintained

## Acceptance Criteria

### Phase 1: Retrieval-Only Mode ✅
- [x] **AC-1.1**: Add `retrieval_only` parameter to RAGSwarmCoordinator
- [x] **AC-1.2**: Implement `_build_simple_retrieval_graph()` for fast mode
- [x] **AC-1.3**: Implement `_simple_retrieval_node` for basic vector store retrieval
- [x] **AC-1.4**: Implement `_simple_answer_node` for basic answer generation
- [x] **AC-1.5**: Skip checkpointer in retrieval-only mode (no HITL needed)

### Phase 2: Mode Selection Logic ✅
- [x] **AC-2.1**: Validate mode combinations (retrieval_only overrides human_in_loop)
- [x] **AC-2.2**: Route to correct graph builder based on mode
- [x] **AC-2.3**: Log operational mode for telemetry
- [x] **AC-2.4**: Document three modes in code and docs

### Phase 3: Long-Running Project Support
- [ ] **AC-3.1**: Thread ID persistence across sessions
- [ ] **AC-3.2**: State checkpointing at each workflow step
- [ ] **AC-3.3**: Resume from exact interruption point
- [ ] **AC-3.4**: Full conversation history maintained
- [ ] **AC-3.5**: Multi-session iterative refinement

### Phase 4: UI Integration
- [ ] **AC-4.1**: Add mode selector in Streamlit UI (Simple/Automated/Guided)
- [ ] **AC-4.2**: Thread ID management UI (view, create, switch threads)
- [ ] **AC-4.3**: Session history viewer
- [ ] **AC-4.4**: Pause/resume controls

## Three Operational Modes

### MODE 1: Retrieval-Only (Fast)
```python
coordinator = RAGSwarmCoordinator(
    context_engine=engine,
    retrieval_only=True  # Fast mode
)

result = await coordinator.execute("What is LangGraph?")
# ~5-10 seconds, simple retrieval + answer
```

**Workflow**:
```
START → simple_retrieval → simple_answer → END
```

**Use Cases**:
- Quick context lookups
- Simple Q&A
- Fast development context retrieval
- When speed matters more than depth

---

### MODE 2: Automated Sophisticated
```python
coordinator = RAGSwarmCoordinator(
    context_engine=engine,
    retrieval_only=False,
    human_in_loop=False  # Automated
)

result = await coordinator.execute("Explain LangGraph state management")
# ~30-60 seconds, full 5-agent processing
```

**Workflow**:
```
START → query_analyst → retrieval → re_ranker → writer → QA → END
```

**Use Cases**:
- Thorough automated research
- When you trust the agents
- Background processing
- Batch operations

---

### MODE 3: HITL-Guided (Collaborative)
```python
coordinator = RAGSwarmCoordinator(
    context_engine=engine,
    retrieval_only=False,
    human_in_loop=True  # Guided
)

result = await coordinator.execute(
    "Design architecture for RAG pipeline",
    thread_id="architecture_project_123"
)
# First interrupt: Knowledge source selection
# User: "architecture, design_patterns, url: https://..."
# → Continues with human guidance at 5 more checkpoints
```

**Workflow**:
```
START
  ↓
[HITL #0: select_knowledge_sources]
  ↓
query_analyst
  ↓
[HITL #1: review_query]
  ↓
... (all 6 HITL checkpoints)
  ↓
END
```

**Use Cases**:
- Complex development tasks
- Architecture design
- Critical decisions
- Learning and exploration

---

## Long-Running Project Example

### Session 1: Start Project
```python
# Start new architecture design project
result = coordinator.execute(
    query="Design architecture for document ingestion pipeline",
    thread_id="arch_project_456"
)

# → Interrupts at HITL #0
# User selects: "architecture, design_patterns, url: https://..."
result = coordinator.resume(thread_id="arch_project_456", human_input="...")

# → Interrupts at HITL #1
# User approves query understanding
result = coordinator.resume(thread_id="arch_project_456", human_input="approve")

# → Interrupts at HITL #2
# User needs to think, pauses session
```

### Session 2: Resume Next Day
```python
# Resume from where we left off
result = coordinator.resume(
    thread_id="arch_project_456",
    human_input="approve retrieval results"
)

# → Continues through remaining checkpoints
# → User iteratively refines through workflow
```

### Session 3: Final Refinements
```python
# Final iteration with feedback
result = coordinator.resume(
    thread_id="arch_project_456",
    human_input="revise: add scalability considerations"
)

# → Agent refines based on feedback
# → Human approves final version
```

## Technical Implementation

### Mode Selection in __init__
```python
def __init__(self, context_engine, human_in_loop=False, retrieval_only=False):
    self.retrieval_only = retrieval_only
    self.human_in_loop = human_in_loop
    
    # Validate mode combination
    if retrieval_only and human_in_loop:
        logger.warning("retrieval_only overrides human_in_loop")
        self.human_in_loop = False
    
    # Build appropriate graph
    self.graph = self._build_graph()
```

### Graph Builder Routing
```python
def _build_graph(self):
    if self.retrieval_only:
        return self._build_simple_retrieval_graph()  # MODE 1
    elif self.human_in_loop:
        return self._build_hitl_guided_graph()  # MODE 3
    else:
        return self._build_automated_sophisticated_graph()  # MODE 2
```

### Thread Management
```python
# ThreadManager utility for session persistence
class ThreadManager:
    def create_thread(self, user_id, project_name):
        thread_id = f"{user_id}_{project_name}_{timestamp}"
        return thread_id
    
    def list_threads(self, user_id):
        return active_threads
    
    def get_thread_history(self, thread_id):
        return conversation_history
```

### Files Modified
- `agents/rag/rag_swarm_coordinator.py` - Mode selection, simple retrieval graph
- `utils/thread_manager.py` - **NEW** Thread management utility
- `apps/rag_management_app.py` - Mode selector UI, thread management UI

## Testing Strategy

1. **Mode Selection Test**: Verify correct graph built for each mode
2. **Performance Test**: Measure time for each mode
3. **Thread Persistence Test**: Verify state maintained across sessions
4. **Resume Test**: Test resume from various interruption points
5. **Multi-Session Test**: Test long-running project workflow

## Definition of Done

- [x] Retrieval-only mode implemented
- [x] Mode selection logic implemented
- [x] Simple retrieval graph working
- [ ] Thread management utility implemented
- [ ] Thread persistence verified
- [ ] Multi-session resume working
- [ ] UI for mode selection and thread management
- [ ] All tests passing
- [ ] Documentation updated

## Dependencies

- Depends on: US-RAG-005 (Multi-Agent Workflow), US-RAG-006 (HITL Architecture)
- Enables: Flexible usage patterns from quick lookups to long-running projects

## Success Metrics

- MODE 1 (retrieval-only): < 10 seconds
- MODE 2 (automated): < 60 seconds
- MODE 3 (HITL): 2-5 minutes (with human feedback)
- Thread persistence: 100% state recovery
- User satisfaction with mode flexibility

## Notes

**Key Insight**: One mode doesn't fit all use cases. Users need flexibility to choose the right processing level for their needs.

**Long-Running Projects**: Some development tasks (architecture design, complex implementation) need days/weeks with multiple sessions. Thread-based persistence enables this.

**User Control**: Give users the choice - fast when they need speed, sophisticated when they need quality, guided when they need control.

