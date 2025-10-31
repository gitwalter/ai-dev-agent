# Revised Implementation Plan: US-CONTEXT-001 - Starting with Complexity Analyzer

**Status**: 🟢 **REVISED BASED ON FEEDBACK**  
**Starting Agent**: `complexity_analyzer` (FIRST STEP)  
**Strategy**: Start from the beginning - establish context early  
**Created**: 2025-10-28 (Revised)

## Why Start with Complexity Analyzer? 🎯

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
   - Domain: What domain is this project? (web/api/data/ai/etc.)
   - Intent: What type of project? (new_feature/bug_fix/refactor/etc.)
   - Complexity: Already classifying this!

5. **Testable Success**:
   - Input: "Build a RAG system for document search"
   - Output: `{domain: "ai", intent: "new_feature", complexity: "complex"}`
   - Clear, measurable success

## Why This is Better Than Architecture Designer

| Aspect | Complexity Analyzer | Architecture Designer |
|--------|-------------------|---------------------|
| **Position** | First step | Second agent |
| **Task Type** | Classification | Generation |
| **Complexity** | Simple | Complex |
| **Impact** | Benefits ALL agents | Benefits downstream only |
| **Knowledge Needs** | Minimal (just examples) | Extensive (docs, patterns) |
| **Tools Needed** | None | Many |
| **Testability** | Very easy | Moderate |

**Key Insight**: Complexity Analyzer is **already doing context detection** (complexity classification). We just need to **expand** it to detect domain and intent too!

## Revised Implementation Phases

### Phase 1: Enhance Complexity Analyzer with Domain/Intent Detection (2-3 days)
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

3. Create test
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

### Phase 3: Pass Context to Requirements Analyst (2-3 days) ✅ **IN PROGRESS**
**Goal**: Requirements analyst uses context for better analysis

**Status**: 🔄 **ISOLATED TESTING COMPLETE** - Studio graph created with HITL and iterative refinement

**Current State**:
```python
def _requirements_node(self, state: SwarmState):
    # Currently: Only uses project_context
    # Prompt: "Analyze requirements for: {project_context}"
```

**Enhanced State** (✅ COMPLETED):
```python
def analyze_requirements_node(state: RequirementsAnalystState):
    # Enhanced: Uses detected context
    # Prompt: "Analyze requirements for: {project_context}
    #          Domain: {domain}, Intent: {intent}, Complexity: {complexity}"
    # Result: Better requirements analysis
```

**Steps** (✅ COMPLETED):
1. ✅ Create isolated `requirements_analyst_studio.py` graph
   - Uses context from complexity_analyzer (domain, intent, complexity, entities)
   - Context-aware requirements analysis prompt
   - HITL checkpoint for requirements review
   - Iterative refinement loop (max 3 iterations)
   - Finalize node for completion message

2. ✅ Test in LangGraph Studio
   - Graph: `_requirements_analyst`
   - Initial state with context fields
   - Feedback via state JSON editing
   - Iterative refinement workflow

3. ⏳ Next: Integrate into main workflow
   - Pass context from complexity_analyzer → requirements_analyst
   - Update main workflow node to use context
   - Test end-to-end context propagation

**Deliverable**: ✅ Requirements analyst isolated Studio graph with context-aware analysis

**Files Created**:
- ✅ `workflow/requirements_analyst_studio.py` - Isolated graph for Studio testing
- ✅ `docs/testing/REQUIREMENTS_ANALYST_STUDIO_QUICK_JSON.md` - Test JSON guide
- ✅ Updated `langgraph.json` - Added `_requirements_analyst` graph

**Next Steps**:
- Integrate context-aware requirements analysis into main workflow
- Test end-to-end: complexity_analyzer → agent_selector → requirements_analyst
- Verify context propagation and improved requirements analysis quality

---

### Phase 4: Pass Context to Architecture Designer (2-3 days) ✅ **IN PROGRESS**
**Goal**: Architecture designer uses context and requirements for better design

**Status**: 🔄 **ISOLATED TESTING COMPLETE** - Studio graph created with HITL and iterative refinement

**Current State**:
```python
def _architecture_node(self, state: SwarmState):
    # Currently: Only uses project_context and requirements
    # Prompt: "Design architecture for: {project_context}, Requirements: {requirements}"
```

**Enhanced State** (✅ COMPLETED):
```python
def design_architecture_node(state: ArchitectureDesignerState):
    # Enhanced: Uses detected context AND requirements analysis
    # Prompt: "Design architecture for: {project_context}
    #          Domain: {domain}, Intent: {intent}, Complexity: {complexity}
    #          Requirements: {functional_requirements}, {non_functional_requirements}"
    # Result: Better architecture design with context-aware and requirements-driven approach
```

**Steps** (✅ COMPLETED):
1. ✅ Create isolated `architecture_designer_studio.py` graph
   - Uses context from complexity_analyzer (domain, intent, complexity, entities)
   - Uses requirements from requirements_analyst (functional, non-functional, constraints)
   - Context-aware and requirements-driven architecture design prompt
   - HITL checkpoint for architecture review
   - Iterative refinement loop (max 3 iterations)
   - Finalize node for completion message

2. ✅ Test in LangGraph Studio
   - Graph: `_architecture_designer`
   - Initial state with context fields AND requirements fields
   - Feedback via state JSON editing
   - Iterative refinement workflow

3. ⏳ Next: Integrate into main workflow
   - Pass context from complexity_analyzer → architecture_designer
   - Pass requirements from requirements_analyst → architecture_designer
   - Update main workflow node to use context and requirements
   - Test end-to-end context and requirements propagation

**Deliverable**: ✅ Architecture designer isolated Studio graph with context-aware and requirements-driven design

**Files Created**:
- ✅ `workflow/architecture_designer_studio.py` - Isolated graph for Studio testing
- ✅ `docs/testing/ARCHITECTURE_DESIGNER_STUDIO_TEST_JSON.md` - Test JSON guide
- ✅ Updated `langgraph.json` - Added `_architecture_designer` graph

**Next Steps**:
- Integrate context-aware and requirements-driven architecture design into main workflow
- Test end-to-end: complexity_analyzer → agent_selector → requirements_analyst → architecture_designer
- Verify context and requirements propagation and improved architecture design quality

---

### Phase 5: Pass Context to Code Generator (2-3 days) ✅ **IN PROGRESS**
**Goal**: Code generator uses context, requirements, and architecture for better code generation

**Status**: 🔄 **ISOLATED TESTING COMPLETE** - Studio graph created with HITL and iterative refinement

**Current State**:
```python
def _code_node(self, state: SwarmState):
    # Currently: Only uses project_context, requirements, and architecture
    # Prompt: "Generate code for: {project_context}, Requirements: {requirements}, Architecture: {architecture}"
```

**Enhanced State** (✅ COMPLETED):
```python
def generate_code_node(state: CodeGeneratorState):
    # Enhanced: Uses detected context AND requirements AND architecture
    # Prompt: "Generate code for: {project_context}
    #          Domain: {domain}, Intent: {intent}, Complexity: {complexity}
    #          Requirements: {functional_requirements}, {non_functional_requirements}
    #          Architecture: {components}, {technology_stack}, {architecture_pattern}"
    # Result: Better code generation with context-aware, requirements-driven, and architecture-guided approach
```

**Steps** (✅ COMPLETED):
1. ✅ Create isolated `code_generator_studio.py` graph
   - Uses context from complexity_analyst (domain, intent, complexity, entities)
   - Uses requirements from requirements_analyst (functional, non-functional, constraints)
   - Uses architecture from architecture_designer (components, technology stack, pattern)
   - Context-aware, requirements-driven, and architecture-guided code generation prompt
   - HITL checkpoint for code review
   - Iterative refinement loop (max 3 iterations)
   - Finalize node for completion message

2. ✅ Test in LangGraph Studio
   - Graph: `_code_generator`
   - Initial state with context fields AND requirements fields AND architecture fields
   - Feedback via state JSON editing
   - Iterative refinement workflow

3. ⏳ Next: Integrate into main workflow
   - Pass context from complexity_analyzer → code_generator
   - Pass requirements from requirements_analyst → code_generator
   - Pass architecture from architecture_designer → code_generator
   - Update main workflow node to use context, requirements, and architecture
   - Test end-to-end context, requirements, and architecture propagation

**Deliverable**: ✅ Code generator isolated Studio graph with context-aware, requirements-driven, and architecture-guided generation

**Files Created**:
- ✅ `workflow/code_generator_studio.py` - Isolated graph for Studio testing
- ✅ `docs/testing/CODE_GENERATOR_STUDIO_TEST_JSON.md` - Test JSON guide
- ✅ Updated `langgraph.json` - Added `_code_generator` graph

**Next Steps**:
- Integrate context-aware, requirements-driven, and architecture-guided code generation into main workflow
- Test end-to-end: complexity_analyzer → agent_selector → requirements_analyst → architecture_designer → code_generator
- Verify context, requirements, and architecture propagation and improved code generation quality

---

## Comparison: Complexity Analyzer vs Architecture Designer

### Complexity Analyzer (RECOMMENDED ✅)

**Pros**:
- ✅ First step - sets context for everything
- ✅ Pure classification - simplest to enhance
- ✅ Already doing classification (just expand it)
- ✅ High impact - benefits all downstream agents
- ✅ No tools needed - just classification
- ✅ Easy to test - clear inputs/outputs

**Cons**:
- ⚠️ Less "flashy" than architecture designer
- ⚠️ May seem less directly valuable

### Requirements Analyst (ALTERNATIVE)

**Pros**:
- ✅ First actual agent (first with generation)
- ✅ Output feeds into architecture designer
- ✅ Can establish domain context early
- ✅ More directly valuable output

**Cons**:
- ⚠️ More complex (generation, not just classification)
- ⚠️ Needs knowledge routing (more complex)
- ⚠️ Harder to test success criteria

## Recommendation: Start with Complexity Analyzer 🎯

**Why**:
1. **Perfect fit**: Already doing classification, just expand it
2. **Simplest**: No tools, no generation, just classification
3. **Highest impact**: Sets context for ALL agents
4. **Easiest to test**: Clear classification outputs
5. **Lowest risk**: Simple change, easy to verify

**Then**: Move to requirements_analyst → architecture_designer → etc.

## Revised File Structure

```
agents/routing/
├── __init__.py
├── context_detection_router.py      # Phase 1: Classification enhancement
├── knowledge_router.py              # Phase 4: Knowledge routing
└── routing_metrics.py               # Phase 5: Metrics

workflow/
└── langgraph_workflow.py            # Enhanced _analyze_complexity

tests/routing/
├── test_complexity_context.py       # Phase 1 tests
├── test_agent_selection.py          # Phase 2 tests
├── test_requirements_context.py     # Phase 3 tests
└── test_end_to_end_context.py      # Phase 5 tests
```

## Success Criteria Per Phase

### Phase 1 ✅
- [ ] Complexity analyzer detects domain + intent + complexity
- [ ] Context stored in state
- [ ] Test passes

### Phase 2 ✅
- [ ] Agent selection uses detected context
- [ ] Better agent selection accuracy
- [ ] Test passes

### Phase 3 ✅
- [ ] Requirements analyst uses context
- [ ] Better requirements analysis
- [ ] Test passes

### Phase 4 ✅
- [ ] Requirements analyst uses domain-specific knowledge
- [ ] Only relevant docs searched
- [ ] Test passes

### Phase 5 ✅
- [ ] All agents use context
- [ ] Context propagates through workflow
- [ ] End-to-end test passes

## Next Steps

1. **Start Phase 1**: Enhance `_analyze_complexity` to detect domain + intent
2. **Test**: Verify context detection works
3. **Iterate**: Continue through phases sequentially

**Ready to start with Complexity Analyzer!** 🚀

This approach:
- ✅ Starts from the beginning
- ✅ Simplest to implement
- ✅ Highest impact
- ✅ Easiest to test

