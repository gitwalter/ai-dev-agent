# RAG System Architecture Overview

**Created:** 2025-01-29  
**Purpose:** Comprehensive overview of LangChain-compatible RAG system  
**Status:** 🚀 Active Development

---

## 🎯 **Vision**

Build a **LangChain-native RAG system** with sophisticated multi-agent orchestration and Human-in-the-Loop (HITL) control using official LangChain patterns.

---

## 🏗️ **Architecture Components**

### **1. Specialized Agent Swarm**

Five expert agents working together:

| Agent | Role | LLM Model | Responsibilities |
|-------|------|-----------|------------------|
| **QueryAnalystAgent** | Query Understanding | Gemini 2.5 Flash | Intent classification, query rewriting, concept extraction |
| **RetrievalSpecialistAgent** | Context Retrieval | N/A (pure search) | Multi-strategy search, query expansion |
| **ReRankerAgent** | Result Ranking | N/A (algorithmic) | Multi-signal scoring, deduplication |
| **QualityAssuranceAgent** | Quality Validation | Gemini 2.5 Flash | Quality assessment, coverage analysis |
| **WriterAgent** | Response Synthesis | Gemini 2.5 Flash | Answer generation, citation, formatting |

**Coordinated by:** `RAGSwarmCoordinator` (LangGraph orchestration)

---

### **2. LangChain-Compatible HITL Integration**

Following [official LangChain HITL patterns](https://docs.langchain.com/oss/python/langchain/human-in-the-loop):

**Three Implementation Options:**

#### **Option A: Deep Agents (Recommended)**
```python
from deepagents import create_deep_agent

rag_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[analyze_query, retrieve_context, rerank, assess_quality, generate],
    interrupt_on={
        "analyze_query": {"allowed_decisions": ["approve", "edit", "reject"]},
        "retrieve_context": {"allowed_decisions": ["approve", "edit", "reject"]},
        "rerank_results": {"allowed_decisions": ["approve", "reject"]},
        "assess_quality": {"allowed_decisions": ["approve", "reject"]}
    },
    checkpointer=MemorySaver()
)
```

#### **Option B: HITL Middleware**
```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[...],
    middleware=[HumanInTheLoopMiddleware(interrupt_on={...})]
)
```

#### **Option C: Custom LangGraph + LangChain Patterns**
- Keep our sophisticated routing
- Use LangChain's `Command` pattern for resume
- Structured `HITLRequest`/`HITLResponse`

---

### **3. HITL Checkpoints**

**5 Strategic Human Review Points:**

1. **Query Analysis Review**
   - Review intent classification and search strategy
   - Decisions: approve, edit, reject
   
2. **Retrieval Results Review**
   - Review retrieved sources and relevance
   - Decisions: approve, edit (add sources), reject
   
3. **Re-ranking Review**
   - Review ranked context quality
   - Decisions: approve, reject
   
4. **Quality Assessment Review**
   - Review quality score and completeness
   - Decisions: approve, reject (trigger re-retrieval)
   
5. **Final Response Review**
   - Review generated answer
   - Decisions: approve, revise, reject

---

### **4. Task-Adaptive Workflows**

Different tasks use different agent combinations:

**Simple QA:**
```
query_analyst → retrieval → writer → END
```

**Research Article:**
```
query_analyst → [HITL] → retrieval → [HITL] → 
re_ranker → [HITL] → writer → [HITL] → 
quality_assurance → [HITL] → END
```

**Code Generation:**
```
query_analyst → retrieval (code-focused) → [HITL] → 
writer (code formatter) → [HITL] → END
```

See [Task-Adaptive Workflows](./TASK_ADAPTIVE_RAG_WORKFLOWS.md) for details.

---

## 🔄 **Complete Workflow**

### **Standard Query Flow:**

```
1. User Query
   ↓
2. QueryAnalystAgent
   - Intent: factual | conceptual | procedural | multi-hop
   - Generate 3-5 query variants
   - Recommend search strategy
   ↓
3. [HITL #1: Review Query Analysis]
   - Human: approve | edit | reject
   ↓
4. RetrievalSpecialistAgent
   - Execute multi-strategy search
   - Retrieve 20-30 candidates
   ↓
5. [HITL #2: Review Retrieved Sources]
   - Human: approve | add_source | retry | reject
   ↓
6. ReRankerAgent
   - Multi-signal scoring (semantic, keyword, quality, diversity)
   - Deduplication
   - Position optimization
   - Top 10 results
   ↓
7. [HITL #3: Review Ranked Context]
   - Human: approve | improve_ranking | more_sources
   ↓
8. QualityAssuranceAgent
   - Assess quality score (0-1)
   - Assess coverage
   - Trigger re-retrieval if needed
   ↓
9. [HITL #4: Review Quality Assessment]
   - Human: approve | retry_retrieval
   ↓
10. WriterAgent
    - Synthesize context into answer
    - Cite sources
    - Format response
    ↓
11. [HITL #5: Final Response Review]
    - Human: ship | revise | restart
    ↓
12. END
```

---

## 🎨 **Key Features**

### **Multi-Signal Re-Ranking**
```python
combined_score = (
    0.40 × semantic_similarity +    # Vector search score
    0.25 × keyword_overlap +        # Term matching  
    0.20 × content_quality +        # Metadata & length
    0.15 × diversity                # Uniqueness
)
```

### **Quality Feedback Loop**
Automatically triggers re-retrieval when:
- Quality score < 0.6
- Coverage < 0.5
- Less than 3 results
- QA agent recommends it

### **Position Optimization**
Mitigates "lost in the middle" effect:
- Best results at beginning and end
- Middle results in reversed order

---

## 🔧 **Implementation Status**

### ✅ **Completed**
- [x] 5 specialized agents implemented
- [x] RAGSwarmCoordinator with LangGraph
- [x] Thread-based state persistence
- [x] Multi-signal re-ranking
- [x] Quality feedback loop
- [x] Streamlit UI integration
- [x] LangSmith tracing

### 🚧 **In Progress**
- [ ] LangChain-compatible HITL (Decision: Deep Agents vs. Custom)
- [ ] Structured decision handling (approve/edit/reject)
- [ ] Decision validation per checkpoint
- [ ] Context preview improvements

### 📋 **Planned**
- [ ] Task-adaptive routing (different workflows per task type)
- [ ] Multi-session project support
- [ ] Advanced source management (URLs, documents, categories)
- [ ] Comprehensive testing suite
- [ ] Performance benchmarking

---

## 📊 **Performance Characteristics**

| Metric | Target | Current |
|--------|--------|---------|
| **Response Quality** | Excellent | Good → Excellent |
| **Context Relevance** | >0.85 | ~0.85 |
| **Coverage** | >85% | ~88% |
| **Latency** | <5s | 3-5s |
| **Source Citations** | Comprehensive | Basic → Comprehensive |
| **Re-retrieval** | Automatic | ✅ Automatic |

---

## 🚀 **Usage**

### **In Streamlit UI:**
```bash
streamlit run apps/rag_management_app.py --server.port 8510
```

1. Navigate to "💬 Agent Chat"
2. Select "🔥 Agent Swarm (Best Quality)"
3. Enable HITL mode if desired
4. Ask your question
5. Review at each checkpoint

### **Programmatically:**
```python
from agents.rag import RAGSwarmCoordinator
from context.context_engine import ContextEngine

# Initialize
context_engine = ContextEngine(context_config)
await context_engine.initialize()

swarm = RAGSwarmCoordinator(context_engine, human_in_loop=True)

# Execute with HITL
config = {"configurable": {"thread_id": "session_123"}}
result = await swarm.execute("Your query here", config=config)

# Handle interrupt
if result['status'] == 'interrupted':
    # Present to human for review
    human_decision = get_human_feedback()
    
    # Resume
    result = swarm.resume(
        thread_id="session_123",
        human_input=human_decision,
        parent_run_id=result.get('run_id')
    )
```

---

## 📚 **Related Documentation**

- **[HITL Implementation Plan](./RAG_SWARM_HITL_IMPLEMENTATION_PLAN.md)** - Detailed LangChain HITL implementation
- **[Task-Adaptive Workflows](./TASK_ADAPTIVE_RAG_WORKFLOWS.md)** - Different workflows per task type
- **[Best Practices](./RAG_BEST_PRACTICES_2025.md)** - Industry RAG best practices
- **[LangSmith Integration](./RAG_LANGSMITH_INTEGRATION.md)** - Tracing and observability

---

## 🎯 **Design Principles**

1. **LangChain-Native**: Use official LangChain patterns, not custom implementations
2. **Human-in-Control**: HITL as primary interaction model, not afterthought
3. **Task-Adaptive**: Workflows adapt to task type, not one-size-fits-all
4. **Quality-First**: Automatic quality validation with feedback loops
5. **Transparent**: Full observability via LangSmith
6. **Modular**: Each agent independently testable and replaceable

---

**Status:** Active development with LangChain HITL patterns  
**Next Milestone:** Complete LangChain-compatible HITL implementation  
**Last Updated:** 2025-01-29


