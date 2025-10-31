# RAG V2 Architecture - Official LangChain Pattern Implementation

**Document Version**: 2.0  
**Status**: 🟢 **ACTIVE IMPLEMENTATION**  
**Created**: 2025-01-29  
**Last Updated**: 2025-01-29  
**Related Story**: US-RAG-006 Phase 0  

---

## Executive Summary

This document defines the **RAG V2 Architecture** - a complete ground-up rebuild of the RAG system following **official LangChain patterns** exclusively. 

**Why the Reset?**: All previous RAG implementations are broken due to:
- ❌ Complex custom patterns conflicting with LangChain
- ❌ Qdrant filter validation errors
- ❌ Over-engineered HITL causing workflow failures
- ❌ No working retrieval

**Solution**: Start fresh with official LangChain patterns, build incrementally from simple → agentic → HITL.

---

## Design Philosophy

### Core Principles

1. **Official Patterns Only**
   - Use ONLY documented LangChain/LangGraph APIs
   - No custom workarounds or "improvements"
   - If it's not in the docs, we don't use it

2. **Incremental Complexity**
   - Phase 1: Get basic RAG working (single agent + retriever)
   - Phase 2: Add intelligence (grading + rewriting)
   - Phase 3: Add HITL (only after basics work)
   - Phase 4: Synthetic data & continuous improvement (RAG Flywheel)

3. **Test Constantly**
   - Every phase must have 100% working tests
   - No moving to next phase until current phase is solid

4. **Simple First, Optimize Later**
   - Prioritize working over optimized
   - Refactor only after validation

### RAG Flywheel Philosophy

Based on [Jason Liu's RAG Playbook](https://jxnl.co/writing/2024/08/19/rag-flywheel/):

1. **Nail Retrieval Before Generation**
   - "Too many teams obsess over generation before nailing search"
   - Fix search first - it's usually the weak link
   - Use fast, unit test-like evaluations

2. **Leading Metrics Over Lagging**
   - Don't obsess over overall quality (lagging metric)
   - Focus on: experiments/week, precision/recall improvements, eval suite speed
   - Like weight loss: track workouts (leading) not just scale (lagging)

3. **Synthetic Data First**
   - Generate synthetic questions for each chunk
   - Test retrieval before you have real users
   - Calculate precision/recall baselines
   - Enables millisecond evaluations vs seconds

4. **Real-World Data Clustering**
   - Real questions are stranger than synthetic
   - Cluster by topic with domain expert labels
   - Analyze per-cluster: frequency, similarity, satisfaction
   - Monitor "Other" category growth = concept drift

5. **Continuous Improvement**
   - RAG systems are never "done"
   - Detect pattern shifts early
   - Prioritize by business impact
   - Iterate based on real feedback

### Future Direction: Reports Over RAG

Based on [Predictions for the Future of RAG](https://jxnl.co/writing/2024/06/05/predictions-for-the-future-of-rag/):

**Key Insight**: RAG will shift from Q&A to report generation

**Why Reports > Single Answers**:
- Q&A value = time saved (1-dimensional, hard to sell)
- Reports = decision-making tools (multi-dimensional, high-leverage)
- Example: RAG saves $400/hr employee time, Report enables $5M budget allocation

**Report Value**:
```
Q&A:     Value = % of wage saved
Reports: Value = % of high-leverage outcome

Research team: $20k report for $5M decision >> hourly wage savings
Hiring: Overview report for $250k hire >> Q&A during interviews
```

**SOPs (Standard Operating Procedures)**:
- Reports need templates/formats
- Scaling decisions = developing SOPs
- Market opportunity: SOP templates (workshops, coaching, books)
- AI should create structured reports, not just chat transcripts

**Implementation for Our Project**:
- Phase 5 (future): Report generation from RAG retrieval
- Templates: Architecture decisions, sprint retrospectives, code review summaries
- SOPs: Agile ceremony reports, technical assessment templates

### Anti-Patterns to Avoid

Based on [How to Build a Terrible RAG System](https://jxnl.co/writing/2024/01/07/inverted-thinking-rag/) (inverted thinking):

**What NOT to do**:
1. ❌ Ignore latency (show loading states, optimize)
2. ❌ Hide intermediate results (show thinking process)
3. ❌ Hide source documents (always cite sources)
4. ❌ Ignore churn (monitor user retention)
5. ❌ Use generic search index (domain-specific needed)
6. ❌ Skip custom UI (generic = bad UX)
7. ❌ Skip fine-tuning embeddings (synthetic data helps)
8. ❌ Train LLM from scratch (use existing models)
9. ❌ Skip manual curation (humans needed initially)
10. ❌ Ignore inbound queries (analyze what users ask)
11. ❌ Skip inventory clustering (one-size-fits-all fails)
12. ❌ Focus only on local evals (need A/B tests)

**What TO do** (our commitments):
1. ✅ Show retrieval progress and intermediate steps
2. ✅ Always display source documents with citations
3. ✅ Measure and optimize latency (<15 sec target)
4. ✅ Cluster questions by topic (project, agile, code, architecture)
5. ✅ Custom Streamlit UI for RAG workflows
6. ✅ Generate synthetic data for testing
7. ✅ Monitor query patterns and user satisfaction
8. ✅ A/B test major changes (not just local evals)

---

## Architecture Overview

### Three-Phase Evolution

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG V2 Evolution                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: Basic RAG (Foundation)                                   │
│  ┌──────────────────────────────────────────────────┐             │
│  │  START → agent → tools → END                      │             │
│  │  • Single LLM with retriever tool                 │             │
│  │  • Simple question → retrieval → answer           │             │
│  │  • No grading, no rewriting                       │             │
│  └──────────────────────────────────────────────────┘             │
│                         ↓                                           │
│  Phase 2: Agentic RAG (Intelligence)                               │
│  ┌──────────────────────────────────────────────────┐             │
│  │  START → agent → tools → grade_documents          │             │
│  │                            ↓          ↓            │             │
│  │                      generate_answer  rewrite     │             │
│  │                            ↓          ↓            │             │
│  │                          END      → agent         │             │
│  │  • Document grading (relevance check)             │             │
│  │  • Question rewriting (improvement loop)          │             │
│  │  • Intelligent routing                            │             │
│  └──────────────────────────────────────────────────┘             │
│                         ↓                                           │
│  Phase 3: HITL RAG (Human Collaboration) - FUTURE                  │
│  ┌──────────────────────────────────────────────────┐             │
│  │  • Add interrupt_before/interrupt_after           │             │
│  │  • Human review at strategic points               │             │
│  │  • Approve/edit/reject decisions                  │             │
│  └──────────────────────────────────────────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Basic RAG (Foundation)

### Goal
Get a **WORKING** basic RAG system - simple question → retrieval → answer.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 1: Basic RAG Graph                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   START                                                             │
│     ↓                                                               │
│   ┌─────────────────────────────────────────┐                      │
│   │  agent (LLM + retriever tool)           │                      │
│   │  • Decides: call tool OR respond        │                      │
│   └─────────────────────────────────────────┘                      │
│     ↓                                                               │
│   [tools_condition] (prebuilt routing)                             │
│     ↓                     ↓                                         │
│   tools (ToolNode)      END                                         │
│   • Execute retrieval                                               │
│     ↓                                                               │
│   agent (respond with context)                                      │
│     ↓                                                               │
│   END                                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. State Management
```python
from langgraph.graph import MessagesState

# Official LangGraph state - contains list of messages
# No custom state needed for Phase 1
```

#### 2. Retriever Tool
```python
from langchain.tools.retriever import create_retriever_tool

# Official tool creation - no custom wrappers
retriever_tool = create_retriever_tool(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    name="retrieve_project_docs",
    description="Search and return information about the project."
)
```

#### 3. Agent Node
```python
def agent_node(state: MessagesState):
    """Agent with retriever tool - decides to call tool or respond."""
    response = llm.bind_tools([retriever_tool]).invoke(state["messages"])
    return {"messages": [response]}
```

#### 4. Tool Node
```python
from langgraph.prebuilt import ToolNode

# Official tool execution node - handles tool calls automatically
tools_node = ToolNode([retriever_tool])
```

#### 5. Routing
```python
from langgraph.prebuilt import tools_condition

# Official routing - checks if LLM called tools
workflow.add_conditional_edges(
    "agent",
    tools_condition,  # Prebuilt function
    {
        "tools": "tools",  # If tools called, execute them
        END: END           # Otherwise, end conversation
    }
)
```

#### 6. Graph Assembly
```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tools_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")  # After tools, return to agent

graph = workflow.compile(checkpointer=MemorySaver())
```

### LLM Configuration

```python
from langchain_google_genai import ChatGoogleGenerativeAI

# Project standard: Gemini 2.5 Flash, temp=0, REST transport
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,                      # MANDATORY: deterministic
    convert_system_message_to_human=True,  # Gemini compatibility
    transport="rest"                    # Avoid grpc event loop issues
)
```

### Vector Store Setup

```python
# Use DENSE mode only (no hybrid to avoid Prefetch issues)
from context.context_engine import ContextEngine
from langchain_qdrant import RetrievalMode

context_engine = ContextEngine(collection_name="project_docs")

# Get retriever (no filters for Phase 1)
retriever = context_engine.vector_store.as_retriever(
    search_kwargs={"k": 5}
)
```

### Success Criteria

- [ ] Can initialize graph without errors
- [ ] Can retrieve documents from Qdrant (no validation errors)
- [ ] Can generate answers using retrieved context
- [ ] 5 test queries run end-to-end without crashes
- [ ] LangSmith traces show: user message → agent → tools → agent → response
- [ ] Thread persistence works (conversation history)

---

## Phase 2: Agentic RAG (Intelligence)

### Goal
Add **intelligent routing** - grade documents for relevance, rewrite unclear questions.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Phase 2: Agentic RAG Graph                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   START                                                             │
│     ↓                                                               │
│   agent (generate_query_or_respond)                                 │
│     ↓                                                               │
│   [tools_condition]                                                 │
│     ↓                     ↓                                         │
│   tools              respond_directly                               │
│     ↓                     ↓                                         │
│   grade_documents       END                                         │
│     ↓           ↓                                                   │
│  relevant   not_relevant                                            │
│     ↓           ↓                                                   │
│  generate   rewrite_question                                        │
│  _answer        ↓                                                   │
│     ↓         agent (retry with better question)                    │
│   END                                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### New Components

#### 1. Document Grading (Structured Output)
```python
from pydantic import BaseModel, Field

class GradeDocuments(BaseModel):
    """Binary relevance score for retrieved documents."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, 'no' if not"
    )

grader_llm = llm.with_structured_output(GradeDocuments)

def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
    """Determine if retrieved documents are relevant."""
    question = state["messages"][0].content
    context = state["messages"][-1].content  # Last message is ToolMessage with context
    
    prompt = f"""
    You are grading relevance of retrieved documents to user question.
    
    Retrieved document: {context}
    User question: {question}
    
    If document contains keywords or semantic meaning related to question, grade as relevant.
    Binary score: 'yes' if relevant, 'no' if not.
    """
    
    response = grader_llm.invoke([{"role": "user", "content": prompt}])
    
    if response.binary_score == "yes":
        return "generate_answer"
    else:
        return "rewrite_question"
```

#### 2. Question Rewriting
```python
def rewrite_question(state: MessagesState):
    """Improve question for better retrieval."""
    question = state["messages"][0].content
    
    prompt = f"""
    Look at the input question and try to reason about the underlying semantic intent/meaning.
    
    Original question: {question}
    
    Formulate an improved question that will retrieve better context.
    """
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    
    # Replace original question with rewritten version
    return {"messages": [{"role": "user", "content": response.content}]}
```

#### 3. Generate Answer
```python
def generate_answer(state: MessagesState):
    """Generate final answer using retrieved context."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    
    prompt = f"""
    You are an assistant for question-answering tasks.
    Use the following retrieved context to answer the question.
    If you don't know, say so. Use three sentences maximum, keep it concise.
    
    Question: {question}
    Context: {context}
    """
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}
```

### Success Criteria

- [ ] System detects irrelevant documents (binary_score='no')
- [ ] System rewrites unclear questions
- [ ] Rewritten questions loop back to agent for new retrieval
- [ ] Answer quality measurably improved vs Phase 1
- [ ] LangSmith traces show: agent → tools → grade_documents → (generate_answer OR rewrite_question)

---

## Phase 3: HITL RAG (Future)

### Goal
Add **human collaboration** - strategic interrupts for review and feedback.

### Design (Not Implemented Yet)

```python
# Use official LangGraph interrupt patterns
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)

# HITL: Interrupt after tool execution for human review
workflow.add_edge("tools", "grade_documents", interrupt_after=["tools"])

# Human can approve/reject/edit at this point
```

### HITL Checkpoints (Future)
1. **After Retrieval**: Review retrieved context before grading
2. **After Grading**: Approve relevance decision
3. **Before Answer**: Review and edit draft response
4. **Final Approval**: Ship or refine

---

## Technology Stack

### Core Framework
- **LangGraph**: StateGraph, MessagesState, START, END
- **LangChain**: create_retriever_tool, ToolNode, tools_condition
- **Pydantic**: Structured outputs (grading)

### LLM
- **Model**: Gemini 2.5 Flash (gemini-2.5-flash)
- **Temperature**: 0 (mandatory for all instantiations)
- **Transport**: REST (avoid grpc async issues)
- **Library**: langchain-google-genai

### Vector Store
- **Database**: Qdrant (local or cloud)
- **Embeddings**: Gemini native (3072-dim)
- **Mode**: DENSE (no hybrid to avoid Prefetch errors)
- **Library**: langchain-qdrant

### Observability
- **LangSmith**: Full tracing, debugging, monitoring
- **Environment Variables**:
  - `LANGCHAIN_TRACING_V2=true`
  - `LANGCHAIN_PROJECT=ai-dev-agent`
  - `LANGCHAIN_API_KEY=<your-key>`

---

## Implementation Guidelines

### Code Standards

1. **NO Custom Patterns**
   ```python
   # FORBIDDEN: Custom state, custom routing, custom tools wrapper
   # REQUIRED: Use official LangChain APIs only
   ```

2. **Temperature=0 Always**
   ```python
   # MANDATORY for all LLM instantiations
   llm = ChatGoogleGenerativeAI(
       model="gemini-2.5-flash",
       temperature=0  # Deterministic responses
   )
   ```

3. **REST Transport for Gemini**
   ```python
   # MANDATORY to avoid grpc event loop issues in Streamlit
   llm = ChatGoogleGenerativeAI(
       model="gemini-2.5-flash",
       temperature=0,
       transport="rest"  # Critical
   )
   ```

4. **DENSE Retrieval When Filters Used**
   ```python
   # Workaround for hybrid search + filter bug
   if document_filters:
       retriever = vectorstore.as_retriever(
           search_kwargs={"k": 5, "filter": qdrant_filter}
       )
       # Hybrid search disabled automatically when filter present
   ```

### Testing Strategy

#### Phase 1 Tests
```python
def test_basic_rag():
    """Test basic retrieval → answer flow."""
    graph = create_basic_rag_graph()
    
    # Test 1: Simple query
    result = graph.invoke({"messages": [{"role": "user", "content": "What is RAG?"}]})
    assert len(result["messages"]) > 1
    assert "retrieval" in result["messages"][-1].content.lower()
    
    # Test 2: Retrieval triggered
    # Check LangSmith trace for tool call
    
    # Test 3: Thread persistence
    # Multiple queries in same thread should maintain context
```

#### Phase 2 Tests
```python
def test_agentic_rag():
    """Test grading and rewriting logic."""
    graph = create_agentic_rag_graph()
    
    # Test 1: Relevant documents → generate answer
    # Test 2: Irrelevant documents → rewrite question
    # Test 3: Rewrite loop → new retrieval → success
```

### Error Handling

```python
# All nodes should have try/except
def safe_node(state: MessagesState):
    try:
        # Node logic
        return {"messages": [result]}
    except Exception as e:
        logger.error(f"Node failed: {e}")
        return {"messages": [{"role": "assistant", "content": f"Error: {e}"}]}
```

---

## File Structure

```
agents/rag/
├── simple_rag.py              # NEW - Phase 1: Basic RAG
├── agentic_rag.py             # NEW - Phase 2: Agentic RAG (with grade/rewrite)
├── hitl_rag.py                # FUTURE - Phase 3: HITL RAG
│
├── query_analyst_agent.py     # KEEP - Reference for future enhancements
├── retrieval_specialist_agent.py  # KEEP - Reference
├── re_ranker_agent.py         # KEEP - Reference
├── quality_assurance_agent.py # KEEP - Reference
├── writer_agent.py            # KEEP - Reference
│
├── langgraph_rag_agent.py     # DELETE - Broken implementation
├── rag_swarm_coordinator.py   # KEEP - Reference only, don't use
│
└── __init__.py                # Update exports

tests/rag/
├── test_simple_rag.py         # NEW - Phase 1 tests
├── test_agentic_rag.py        # NEW - Phase 2 tests
└── test_hitl_rag.py           # FUTURE - Phase 3 tests

docs/architecture/
├── RAG_V2_ARCHITECTURE.md     # This document
└── RAG_V2_IMPLEMENTATION_LOG.md  # Progress log
```

---

## Migration from V1 to V2

### What We're Removing
- ❌ Custom LangGraph patterns (not in official docs)
- ❌ Deep Agents integration (incompatible with Streamlit)
- ❌ Complex HITL middleware (caused workflow failures)
- ❌ Hybrid search with filters (Prefetch validation errors)
- ❌ Custom state management (use MessagesState)

### What We're Keeping
- ✅ Qdrant vector store
- ✅ Gemini embeddings (3072-dim native)
- ✅ Context engine (fixing retrieval mode)
- ✅ Thread management
- ✅ LangSmith tracing
- ✅ Individual RAG agents (as reference for future enhancements)

### What We're Adding
- ✅ Official LangGraph patterns (MessagesState, ToolNode, tools_condition)
- ✅ Structured output for grading (Pydantic)
- ✅ Document relevance checking
- ✅ Question rewriting loop
- ✅ Incremental complexity (basic → agentic → HITL)

---

## Success Metrics

### Phase 1 Success
- ✅ 100% query success rate (no crashes)
- ✅ Retrieval works every time (no Qdrant errors)
- ✅ Answers use retrieved context
- ✅ Clean LangSmith traces
- ✅ Thread persistence works

### Phase 2 Success
- ✅ Grading detects irrelevant documents (>80% accuracy)
- ✅ Question rewriting improves retrieval quality
- ✅ Answer quality improved vs Phase 1 (measurable)

### Phase 3 Success (Future)
- ✅ HITL interrupts trigger correctly
- ✅ Human feedback integrates smoothly
- ✅ Workflow doesn't break on resume

---

## References

### Official Documentation
1. [LangChain Agentic RAG Tutorial](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/)
2. [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
3. [LangChain QA with Chat History](https://python.langchain.com/docs/tutorials/qa_chat_history/)
4. [LangGraph Gemini Examples](https://github.com/gitwalter/intro-to-langgraph-gemini/)

### Project Documentation
- `US-RAG-006.md` - User story for implementation
- `RAG_SWARM_HITL_IMPLEMENTATION_PLAN.md` - Original HITL plan
- `RAG_ARCHITECTURE_OVERVIEW.md` - Previous architecture (superseded)

---

## Implementation Timeline

### Sprint 7 - Week 1 (Current)
- [x] Phase 0A: Documentation complete
- [ ] Phase 0B: Delete broken code
- [ ] Phase 0C: Implement Phase 1 (Basic RAG)
- [ ] Phase 0D: Implement Phase 2 (Agentic RAG)
- [ ] Phase 0E: Integration & validation

### Sprint 7 - Week 2+
- [ ] Phase 1: Add HITL checkpoints (after basics work)
- [ ] Phase 2: Add specialized agents (query analyst, re-ranker, writer)
- [ ] Phase 3: Advanced features (task adaptation, multi-source)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-29 | Complete system reset | All RAG flows broken, can't fix incrementally |
| 2025-01-29 | Use official LangChain patterns only | Custom patterns caused conflicts and errors |
| 2025-01-29 | Build incrementally (basic → agentic → HITL) | Need working foundation before adding complexity |
| 2025-01-29 | Remove Deep Agents for RAG | Incompatible with Streamlit async model |
| 2025-01-29 | Use DENSE mode when filters applied | Workaround for hybrid search Prefetch bug |
| 2025-01-29 | Keep old agents as reference | May use later for enhancements |

---

**Status**: 🟢 **ACTIVE DEVELOPMENT**  
**Next Steps**: Delete broken code, implement Phase 1 Basic RAG  
**Blocked By**: None (fresh start)  
**Last Updated**: 2025-01-29

