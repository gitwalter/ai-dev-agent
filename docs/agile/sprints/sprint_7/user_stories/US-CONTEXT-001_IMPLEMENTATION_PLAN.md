# Incremental Implementation Plan: US-CONTEXT-001 - Starting with Complexity Analyzer (FIRST STEP)

**Status**: 🟢 **REVISED** - Starting from the beginning  
**Starting Agent**: `complexity_analyzer` (FIRST STEP IN WORKFLOW)  
**Strategy**: Start from the beginning - establish context early  
**Created**: 2025-10-28 (Revised based on user feedback)

## Why Complexity Analyzer? 🎯

### Perfect Match for Context Detection ✅

1. **Already Doing Classification**: 
   - Currently: Classifies complexity (simple/medium/complex)
   - Enhance: Add domain/intent classification
   - **Perfect fit**: Context detection IS classification!

2. **First in Workflow**: 
   - Very first step before anything else
   - Sets context for ALL downstream agents
   - **High leverage**: One improvement benefits everything

3. **Pure Classification Task**: 
   - No generation, no tools, just classification
   - Simplest to enhance and test
   - **Low risk**: Easy to verify correctness

4. **Clear Context Needs**:
   - Domain: What domain is this project? (ai/web/api/data/mobile/etc.)
   - Intent: What type of project? (new_feature/bug_fix/refactor/etc.)
   - Complexity: Already classifying this!

5. **Testable Success**:
   - Input: "Build a RAG system for document search"
   - Output: `{domain: "ai", intent: "new_feature", complexity: "complex"}`
   - Clear, measurable success

## Implementation Phases

### Phase 0: HITL Context Review & Persistent Memory (2-3 days)
**Goal**: Add HITL checkpoint for context review using LangGraph standard patterns

**CRITICAL**: Use ONLY LangGraph standard patterns - no custom memory systems!

**Standard LangGraph Patterns to Use**:
1. **Thread ID**: Use `ThreadManager.get_current_config()` → `{"configurable": {"thread_id": "..."}}`
2. **Checkpointer**: Use `MemorySaver()` (already in use)
3. **State Persistence**: Store context in `SwarmState` (LangGraph state)
4. **State Loading**: Use `graph.get_state(config)` to load existing state
5. **HITL Interrupts**: Use `interrupt_before=["review_context"]` pattern

**Steps**:
1. Add context fields to `SwarmState` (LangGraph state)
   ```python
   class SwarmState(TypedDict):
       # Existing fields...
       project_context: str
       project_complexity: str
       
       # NEW: Context fields (stored in LangGraph state automatically)
       project_domain: str      # ai, web, api, etc.
       project_intent: str      # new_feature, bug_fix, etc.
       detected_entities: List[str]
   ```

2. Add HITL checkpoint node for context review
   ```python
   async def review_context_detection_node(state: SwarmState):
       """HITL checkpoint: Human reviews detected context."""
       # Context is already in state (from detect_context node)
       # Just present it to human for review
       return {
           "context_review_prompt": format_context_for_review(state),
           "messages": [{"role": "system", "content": "Awaiting context review..."}]
       }
   ```

3. Add context refinement node
   ```python
   async def refine_context_node(state: SwarmState):
       """Refine context based on human feedback."""
       human_feedback = state.get("context_feedback", "")
       
       # Use LLM to refine context based on feedback
       refined = await llm_refine_context(state, human_feedback)
       
       # Update state (LangGraph automatically persists via checkpointer)
       return {
           "project_domain": refined["domain"],
           "project_intent": refined["intent"],
           "project_complexity": refined["complexity"],
           "detected_entities": refined["entities"]
       }
   ```

4. Use ThreadManager for thread ID management
   ```python
   from utils.thread_manager import ThreadManager
   
   # Create thread manager
   thread_manager = ThreadManager(session_type="development")
   
   # Get standard LangGraph config
   config = thread_manager.get_current_config()
   # Returns: {"configurable": {"thread_id": "development_xxx"}}
   
   # Execute graph - state automatically persists via checkpointer
   result = await graph.ainvoke(state, config=config)
   ```

5. Load existing context from state (standard LangGraph pattern)
   ```python
   async def detect_context_with_persistence(state: SwarmState, config: Dict):
       """Detect context with persistence via LangGraph checkpointer."""
       
       # Load existing state from checkpointer (standard pattern)
       existing_state = await graph.get_state(config)
       
       if existing_state and existing_state.values:
           # Check if context already exists in state
           if existing_state.values.get("project_domain"):
               logger.info("Using existing context from thread state")
               return existing_state.values
       
       # Detect new context
       detected = await context_router.detect_context(state["project_context"])
       
       # Return - LangGraph checkpointer automatically saves state
       return {
           "project_domain": detected.domain,
           "project_intent": detected.intent,
           "project_complexity": detected.complexity,
           "detected_entities": detected.entities
       }
   ```

**Key Points**:
- ✅ **NO custom memory storage** - Use LangGraph state only
- ✅ **NO custom persistence** - Use MemorySaver checkpointer
- ✅ **NO custom thread management** - Use existing ThreadManager
- ✅ **State persistence**: Automatic via LangGraph checkpointer
- ✅ **Thread isolation**: Automatic via thread_id in config

**Deliverable**: HITL context review using standard LangGraph patterns

---
**Goal**: Add domain and intent classification to existing complexity analyzer

**Current State**:
```python
def _analyze_complexity(self, state: SwarmState):
    # Currently: Classifies complexity only
    # Returns: {"project_complexity": "simple|medium|complex"}
```

**Enhanced State**:
```python
def _analyze_complexity_and_context(self, state: SwarmState):
    # Enhanced: Classifies complexity + domain + intent
    # Returns: {
    #   "project_complexity": "simple|medium|complex",
    #   "project_domain": "ai|web|api|data|mobile|etc",
    #   "project_intent": "new_feature|bug_fix|refactor|migration|etc",
    #   "detected_entities": ["rag", "document", "search"]
    # }
```

**Steps**:
1. Create `ContextDetectionRouter` (simplified)
   - Expand existing complexity classification
   - Add domain classification (ai, web, api, data, mobile, etc.)
   - Add intent classification (new_feature, bug_fix, refactor, etc.)
   - Extract entities (technology names, frameworks, etc.)

2. Enhance `_analyze_complexity` method
   - Change prompt to classify: complexity + domain + intent + entities
   - Update return structure to include context
   - Store context in state for downstream agents
   - **NEW**: Add HITL checkpoint after detection

3. Add HITL context review integration
   - After detection, interrupt for human review
   - Human can approve or refine context
   - Refined context persists in thread state

4. Integrate with ThreadManager (standard pattern)
   - Use `ThreadManager.get_current_config()` for thread_id
   - Pass config to `graph.ainvoke()` - state persists automatically
   - Use `graph.get_state(config)` to load existing state
   - **NO custom storage** - LangGraph checkpointer handles everything
   ```python
   def test_complexity_analyzer_with_context():
       analyzer = ComplexityAnalyzer()
       result = analyzer.analyze("Build a RAG system for document search")
       
       assert result["project_complexity"] == "complex"
       assert result["project_domain"] == "ai"
       assert result["project_intent"] == "new_feature"
       assert "rag" in result["detected_entities"]
   ```

**Deliverable**: Complexity analyzer detects context (domain + intent + complexity)

---

### Phase 2: Use Context for Agent Selection (2-3 days)
**Goal**: Use detected context to improve agent selection

**Current State**:
```python
def _select_agents(self, state: SwarmState):
    # Currently: Uses only project_context + complexity
    # Prompt: "Select agents based on project and complexity"
```

**Enhanced State**:
```python
def _select_agents(self, state: SwarmState):
    # Enhanced: Uses detected context (domain + intent + complexity)
    # Prompt: "Select agents based on domain (ai), intent (new_feature), complexity (complex)"
    # Result: Better agent selection accuracy
```

**Steps**:
1. Enhance `_select_agents` prompt
   - Include domain, intent, entities in prompt
   - Example: "Domain: AI, Intent: new_feature, Complexity: complex → Select agents"

2. Map context to agent recommendations
   - Domain mapping: ai → [requirements, architecture, code, test]
   - Intent mapping: new_feature → [all agents], bug_fix → [code, test, review]
   - Use as hints for LLM selection

3. Test
   ```python
   def test_agent_selection_with_context():
       state = {
           "project_context": "Build RAG system",
           "project_complexity": "complex",
           "project_domain": "ai",
           "project_intent": "new_feature"
       }
       selected = analyzer._select_agents(state)
       # Should select all agents for new_feature
       assert len(selected["required_agents"]) >= 5
   ```

**Deliverable**: Agent selection uses detected context

---

### Phase 3: Pass Context to Requirements Analyst (2-3 days)
**Goal**: Requirements analyst uses context for better analysis

**Current State**:
```python
def _requirements_node(self, state: SwarmState):
    # Currently: Only uses project_context
    # Prompt: "Analyze requirements for: {project_context}"
```

**Enhanced State**:
```python
def _requirements_node(self, state: SwarmState):
    # Enhanced: Uses detected context
    # Prompt: "Analyze requirements for: {project_context}
    #          Domain: {domain}, Intent: {intent}, Complexity: {complexity}"
    # Result: Better requirements analysis
```

**Steps**:
1. Enhance requirements analyst prompt
   - Include domain, intent, complexity in prompt
   - Example: "Domain: AI project, Intent: new_feature → Focus on AI-specific requirements"

2. Route to domain-specific knowledge (if needed)
   - Domain: ai → Load AI/ML knowledge sources
   - Domain: web → Load web development knowledge sources
   - Only if requirements analyst needs knowledge retrieval

3. Test
   ```python
   def test_requirements_with_context():
       state = {
           "project_context": "Build RAG system",
           "project_domain": "ai",
           "project_intent": "new_feature"
       }
       result = analyzer._requirements_node(state)
       # Requirements should mention AI/ML-specific concerns
       assert any("ai" in str(req).lower() or "ml" in str(req).lower() 
                  for req in result["requirements"])
   ```

**Deliverable**: Requirements analyst uses context for better analysis

---

### Phase 4: End-to-End Test (1-2 days)
**Goal**: Test complete routing flow

**Steps**:
1. Create end-to-end test
   ```python
   async def test_architecture_designer_with_routing():
       # Setup
       coordinator = EnhancedArchitectureDesigner(context_engine)
       
       # Execute
       result = await coordinator.execute(
           "Design architecture for RAG document ingestion pipeline"
       )
       
       # Verify
       assert result["context"]["domain"] == "architecture"
       assert len(result["selected_tools"]) <= 5
       assert "architecture_docs" in result["knowledge_sources"]
       assert "SOLID" in result["architecture_proposal"]  # Shows knowledge used
   ```

2. Measure improvements:
   - Latency: Should be faster (fewer docs searched)
   - Accuracy: Better architecture (uses right docs)
   - Context window: More room (fewer tools)

**Deliverable**: Working architecture designer with context routing

---

### Phase 5: Semantic Router (2-3 days)
**Goal**: Replace hard-coded detection with semantic-router

**Steps**:
1. Install semantic-router: `pip install semantic-router`
2. Define routes for architecture context
3. Replace hard-coded detection with semantic-router
4. Test: Same results, but faster

**Deliverable**: Fast semantic routing for architecture

---

### Phase 6: Tool RAG Vector Search (2-3 days)
**Goal**: Replace hard-coded tool selection with vector search

**Steps**:
1. Build rich tool specs (name, description, examples, anti-patterns)
2. Index tool specs in Qdrant collection `tool_specs`
3. Replace hard-coded filtering with vector search
4. Test: Better tool selection accuracy

**Deliverable**: Intelligent tool selection via RAG

---

## File Structure

```
agents/routing/
├── __init__.py
├── context_detection_router.py      # Phase 1: Basic detection
├── knowledge_router.py              # Phase 2: Knowledge routing
├── tool_rag_system.py               # Phase 3: Tool selection
└── routing_metrics.py               # Phase 6: Metrics

agents/development/
└── architecture_designer.py         # Enhanced with routing

tests/routing/
├── test_context_detection.py        # Phase 1 tests
├── test_knowledge_routing.py        # Phase 2 tests
├── test_tool_selection.py           # Phase 3 tests
└── test_architecture_e2e.py        # Phase 4 tests
```

## Success Criteria Per Phase

### Phase 0 ✅
- [ ] HITL context review checkpoint implemented
- [ ] Context refinement node working
- [ ] Context persists in thread state
- [ ] Conversation loop for refinement works
- [ ] Test passes

### Phase 1 ✅
- [ ] Context detection runs before architecture_designer
- [ ] Detects domain="architecture", intent="design"
- [ ] Test passes

### Phase 2 ✅
- [ ] Architecture designer uses only architecture docs
- [ ] No general docs searched
- [ ] Test passes

### Phase 3 ✅
- [ ] Architecture designer uses ≤ 5 tools
- [ ] Tools are architecture-relevant
- [ ] Test passes

### Phase 4 ✅
- [ ] End-to-end test passes
- [ ] Architecture proposal cites specific guidelines
- [ ] Latency improved vs. baseline

### Phase 5 ✅
- [ ] Semantic-router integrated
- [ ] Same accuracy, faster execution
- [ ] Test passes

### Phase 6 ✅
- [ ] Tool RAG vector search working
- [ ] Better tool selection accuracy
- [ ] Test passes

## Next Agent After Architecture Designer

Once architecture_designer is working, apply same pattern to:

1. **code_generator** (3rd agent)
   - Domain: "code"
   - Intent: "generate"
   - Knowledge: coding_guidelines, api_docs, examples
   - Tools: code generation tools, file access

2. **code_reviewer** (5th agent)
   - Domain: "code"
   - Intent: "review"
   - Knowledge: coding_standards, security_guidelines
   - Tools: code analysis tools

## Testing Strategy

### Unit Tests (Each Phase)
- Test context detection accuracy
- Test knowledge routing correctness
- Test tool selection relevance

### Integration Tests (Phase 4+)
- Test architecture_designer with routing
- Compare with/without routing (latency, accuracy)

### Manual Tests
- Run architecture_designer with real tasks
- Verify it uses right docs/tools
- Check output quality

## Timeline Estimate

**Total**: ~12-18 days (2.5-3.5 weeks)

- Phase 1: 2-3 days
- Phase 2: 2-3 days
- Phase 3: 2-3 days
- Phase 4: 1-2 days
- Phase 5: 2-3 days
- Phase 6: 2-3 days

**Risk Buffer**: +20% = **15-22 days total**

## Why This Approach Works

1. **Incremental**: Each phase builds on previous
2. **Testable**: Can test each phase independently
3. **Low Risk**: Start simple, add complexity gradually
4. **Visible Value**: Each phase shows improvement
5. **Reusable**: Pattern applies to other agents

## Questions to Answer During Implementation

1. **Phase 1**: Does context detection work reliably?
2. **Phase 2**: Does knowledge routing improve accuracy?
3. **Phase 3**: Does tool selection reduce latency?
4. **Phase 4**: Does end-to-end routing improve quality?
5. **Phase 5**: Is semantic-router faster than LLM?
6. **Phase 6**: Does vector search improve tool selection?

## Next Steps

1. **Start Phase 1**: Create `ContextDetectionRouter` with hard-coded detection
2. **Test**: Verify architecture_designer detects context
3. **Iterate**: Continue through phases sequentially

Ready to start Phase 1! 🚀

