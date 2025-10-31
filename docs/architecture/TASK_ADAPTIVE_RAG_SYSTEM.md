# Task-Adaptive RAG System Design

## 🎯 Core Philosophy

**"The workflow should adapt to the task, not force every task through the same pipeline"**

Different tasks require different levels of sophistication, HITL involvement, and agent combinations.

## 📊 Task Types & Workflows

### 1. SIMPLE_QA (Quick Factual Questions)
**Example**: "What is LangGraph?", "Who created Python?"

**Workflow**:
```
query_analyst → retrieval_specialist → writer → END
```

**Agents**: 3 agents
**HITL**: Optional (only if human_in_loop=True and user wants control)
**Estimated Time**: ~10-15 seconds

**Characteristics**:
- Single, clear question
- Factual answer expected
- Minimal context needed
- Skip re-ranking (use top results)
- Skip QA (writer handles quality)

---

### 2. RESEARCH_ARTICLE (Deep Research + Writing)
**Example**: "Write a comprehensive guide on LangGraph state management"

**Workflow**:
```
query_analyst 
  → [HITL: Approve research plan]
  → retrieval_specialist (multi-source, deep)
  → [HITL: Review sources]
  → re_ranker (comprehensive filtering)
  → [HITL: Approve context]
  → writer (long-form content)
  → [HITL: Review draft]
  → quality_assurance (thorough checks)
  → [HITL: Final approval]
  → END
```

**Agents**: All 5 agents
**HITL**: All 5 checkpoints
**Estimated Time**: 2-5 minutes (with human feedback)

**Characteristics**:
- Complex, multi-faceted topic
- Requires deep research
- Multiple sources needed
- Quality critical
- Iterative refinement expected

---

### 3. CONCEPT_EXPLANATION (Educational Content)
**Example**: "Explain how async/await works in Python"

**Workflow**:
```
query_analyst
  → retrieval_specialist (focus on tutorials, examples)
  → [HITL: Verify explanation approach]
  → re_ranker (prioritize clarity)
  → writer (educational formatting)
  → [HITL: Review explanation]
  → END
```

**Agents**: 4 agents (skip QA, writer handles quality)
**HITL**: 2 checkpoints (after retrieval, after writer)
**Estimated Time**: ~30-60 seconds

**Characteristics**:
- Educational purpose
- Needs examples and analogies
- Clarity over comprehensiveness
- Some back-and-forth expected

---

### 4. CODE_GENERATION (Code Examples, Debugging)
**Example**: "Show me how to implement a LangGraph checkpointer"

**Workflow**:
```
query_analyst (identify code requirements)
  → retrieval_specialist (code-focused search)
  → [HITL: Verify relevant code examples]
  → writer (code formatting, syntax highlighting)
  → [HITL: Test/verify code]
  → END
```

**Agents**: 3 agents (skip re-ranker, skip QA)
**HITL**: 2 checkpoints (verify examples, verify generated code)
**Estimated Time**: ~20-30 seconds

**Characteristics**:
- Code-centric query
- Working examples critical
- Syntax and imports matter
- Testing/verification needed

---

### 5. FACT_CHECKING (Verification, Validation)
**Example**: "Verify if LangGraph supports custom checkpointers"

**Workflow**:
```
query_analyst (identify claim to verify)
  → retrieval_specialist (authoritative sources)
  → re_ranker (prioritize official docs)
  → quality_assurance (cross-reference sources)
  → [HITL: Review evidence]
  → writer (verdict with citations)
  → END
```

**Agents**: 5 agents (heavy on QA)
**HITL**: 1 checkpoint (review evidence before verdict)
**Estimated Time**: ~30-45 seconds

**Characteristics**:
- Verification-focused
- Source authority critical
- Cross-referencing needed
- Evidence-based conclusion

---

### 6. MULTI_SOURCE_SYNTHESIS (Compare/Contrast)
**Example**: "Compare LangGraph vs. CrewAI for agent orchestration"

**Workflow**:
```
query_analyst (identify comparison dimensions)
  → [HITL: Approve comparison criteria]
  → retrieval_specialist (balanced multi-source)
  → [HITL: Verify source coverage]
  → re_ranker (balanced representation)
  → writer (comparative analysis)
  → [HITL: Review analysis]
  → END
```

**Agents**: 4 agents (skip QA for opinion-based content)
**HITL**: 3 checkpoints (criteria, sources, analysis)
**Estimated Time**: ~60-90 seconds

**Characteristics**:
- Multiple perspectives needed
- Balanced representation
- Comparative structure
- Opinion/analysis component

---

## 🤖 Task Classification Logic

### Automatic Task Type Detection

The **QueryAnalystAgent** classifies the task based on:

```python
def classify_task_type(query: str) -> TaskType:
    """
    Classify query into task type based on patterns.
    
    Classification Heuristics:
    - Question words (what, who, when, where) → SIMPLE_QA
    - "write", "create", "comprehensive guide" → RESEARCH_ARTICLE
    - "explain", "how does", "understand" → CONCEPT_EXPLANATION
    - "code", "implement", "example", "function" → CODE_GENERATION
    - "verify", "check", "is it true", "confirm" → FACT_CHECKING
    - "compare", "contrast", "difference", "vs" → MULTI_SOURCE_SYNTHESIS
    """
    
    query_lower = query.lower()
    
    # Code generation patterns
    if any(word in query_lower for word in ["code", "implement", "function", "class", "script"]):
        return TaskType.CODE_GENERATION
    
    # Fact checking patterns
    if any(word in query_lower for word in ["verify", "check", "is it true", "confirm", "validate"]):
        return TaskType.FACT_CHECKING
    
    # Comparison patterns
    if any(word in query_lower for word in ["compare", "contrast", "vs", "versus", "difference between"]):
        return TaskType.MULTI_SOURCE_SYNTHESIS
    
    # Research article patterns
    if any(word in query_lower for word in ["write", "create", "comprehensive", "guide", "article", "essay"]):
        return TaskType.RESEARCH_ARTICLE
    
    # Concept explanation patterns
    if any(word in query_lower for word in ["explain", "how does", "understand", "learn about", "teach"]):
        return TaskType.CONCEPT_EXPLANATION
    
    # Default to simple QA
    return TaskType.SIMPLE_QA
```

### Manual Task Type Override

Users can explicitly specify task type:

```python
# In UI or API
result = coordinator.execute(
    query="What is LangGraph?",
    task_type=TaskType.RESEARCH_ARTICLE,  # Override automatic detection
    thread_id="project_123"
)
```

---

## 🔄 Dynamic Workflow Construction

### Workflow Definitions

```python
TASK_WORKFLOWS = {
    TaskType.SIMPLE_QA: {
        "agents": ["query_analyst", "retrieval_specialist", "writer"],
        "hitl_points": [],  # No HITL for simple Q&A (unless forced)
        "skip_quality_assurance": True,
        "skip_re_ranker": True,
    },
    
    TaskType.RESEARCH_ARTICLE: {
        "agents": ["query_analyst", "retrieval_specialist", "re_ranker", "writer", "quality_assurance"],
        "hitl_points": ["after_query", "after_retrieval", "after_reranker", "after_writer", "after_qa"],
        "skip_quality_assurance": False,
        "skip_re_ranker": False,
    },
    
    TaskType.CONCEPT_EXPLANATION: {
        "agents": ["query_analyst", "retrieval_specialist", "re_ranker", "writer"],
        "hitl_points": ["after_retrieval", "after_writer"],
        "skip_quality_assurance": True,
        "skip_re_ranker": False,
    },
    
    TaskType.CODE_GENERATION: {
        "agents": ["query_analyst", "retrieval_specialist", "writer"],
        "hitl_points": ["after_retrieval", "after_writer"],
        "skip_quality_assurance": True,
        "skip_re_ranker": True,
        "retrieval_focus": "code_examples",
    },
    
    TaskType.FACT_CHECKING: {
        "agents": ["query_analyst", "retrieval_specialist", "re_ranker", "quality_assurance", "writer"],
        "hitl_points": ["after_qa"],
        "skip_quality_assurance": False,
        "skip_re_ranker": False,
        "qa_emphasis": "verification",
    },
    
    TaskType.MULTI_SOURCE_SYNTHESIS: {
        "agents": ["query_analyst", "retrieval_specialist", "re_ranker", "writer"],
        "hitl_points": ["after_query", "after_retrieval", "after_writer"],
        "skip_quality_assurance": True,
        "skip_re_ranker": False,
        "retrieval_strategy": "balanced_multi_source",
    },
}
```

### Dynamic Graph Construction

```python
def _build_task_adaptive_graph(self, task_type: TaskType) -> StateGraph:
    """
    Build workflow dynamically based on task type.
    
    This creates a specialized graph for the specific task,
    including only necessary agents and HITL points.
    """
    
    workflow_config = TASK_WORKFLOWS[task_type]
    workflow = StateGraph(MessagesState)
    
    # Add only necessary agent nodes
    for agent_name in workflow_config["agents"]:
        workflow.add_node(agent_name, getattr(self, f"_{agent_name}_node"))
    
    # Add HITL nodes at specified points
    if self.human_in_loop:
        for hitl_point in workflow_config["hitl_points"]:
            workflow.add_node(hitl_point, getattr(self, f"_{hitl_point}_node"))
    
    # Build edges based on agent sequence
    agents = workflow_config["agents"]
    hitl_points = workflow_config["hitl_points"] if self.human_in_loop else []
    
    # Connect agents with HITL checkpoints in between
    current_node = START
    for i, agent in enumerate(agents):
        workflow.add_edge(current_node, agent)
        
        # Check if there's a HITL point after this agent
        hitl_after_agent = f"after_{agent.replace('_node', '')}"
        if hitl_after_agent in hitl_points:
            workflow.add_edge(agent, hitl_after_agent)
            current_node = hitl_after_agent
        else:
            current_node = agent
    
    # Final edge to END
    workflow.add_edge(current_node, END)
    
    return workflow.compile(checkpointer=MemorySaver())
```

---

## 🎨 User Interface Adaptations

### Task Selection UI

```python
# In Streamlit UI
st.subheader("🎯 Task Type")

task_type_option = st.selectbox(
    "What type of task is this?",
    options=[
        ("🤔 Auto-detect", None),
        ("❓ Simple Question", TaskType.SIMPLE_QA),
        ("📄 Research Article", TaskType.RESEARCH_ARTICLE),
        ("💡 Concept Explanation", TaskType.CONCEPT_EXPLANATION),
        ("💻 Code Generation", TaskType.CODE_GENERATION),
        ("✅ Fact Checking", TaskType.FACT_CHECKING),
        ("⚖️ Compare Multiple Sources", TaskType.MULTI_SOURCE_SYNTHESIS),
    ],
    format_func=lambda x: x[0]
)

task_type = task_type_option[1] if task_type_option else None
```

### Dynamic Progress Indicators

```python
# Show workflow stages based on task type
if task_type == TaskType.SIMPLE_QA:
    st.info("📊 Workflow: Analysis → Retrieval → Answer (Fast)")
elif task_type == TaskType.RESEARCH_ARTICLE:
    st.info("📊 Workflow: Full Pipeline with 5 Review Points (Thorough)")
elif task_type == TaskType.CODE_GENERATION:
    st.info("📊 Workflow: Analysis → Code Search → Generation (Code-Focused)")
```

---

## 🚀 Implementation Plan

### Phase 1: Task Classification (Current)
- [x] Define TaskType enum
- [ ] Implement classification logic in QueryAnalystAgent
- [ ] Add task type to state

### Phase 2: Workflow Definitions
- [ ] Define TASK_WORKFLOWS configuration
- [ ] Implement dynamic graph builder
- [ ] Test each task type workflow

### Phase 3: HITL Integration
- [ ] Conditional HITL based on task type
- [ ] Task-specific feedback options
- [ ] Dynamic interrupt points

### Phase 4: UI Enhancements
- [ ] Task type selector
- [ ] Dynamic workflow visualization
- [ ] Task-appropriate feedback forms
- [ ] Progress indicators per task type

### Phase 5: Testing & Refinement
- [ ] Test all 6 task types
- [ ] Validate workflow efficiency
- [ ] User feedback integration
- [ ] Performance optimization

---

## 📈 Expected Benefits

1. **Efficiency**: Simple questions get fast answers
2. **Quality**: Complex tasks get thorough treatment
3. **Flexibility**: Workflow adapts to task needs
4. **User Control**: Choose automation vs. HITL level
5. **Scalability**: Easy to add new task types
6. **Transparency**: Clear workflow for each task
7. **Performance**: Optimal resource usage per task

---

## 🎯 Success Metrics

- Simple Q&A: < 15 seconds
- Research Article: 2-5 minutes (with HITL)
- Concept Explanation: < 60 seconds
- Code Generation: < 30 seconds
- Fact Checking: < 45 seconds
- Multi-Source Synthesis: < 90 seconds

---

## 📚 Next Steps

1. ✅ **Document design** (this file)
2. **Implement task classification** in QueryAnalystAgent
3. **Create workflow definitions** (TASK_WORKFLOWS)
4. **Build dynamic graph constructor**
5. **Test each task type** individually
6. **Integrate with UI** for task selection
7. **Add telemetry** to track task type performance

