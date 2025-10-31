# Task-Adaptive RAG Workflows - LangChain HITL Edition

**Created:** 2025-01-29  
**Purpose:** Define task-specific workflows with LangChain-compatible HITL  
**Status:** 🚀 Active

---

## 🎯 **Core Philosophy**

**"The workflow should adapt to the task, not force every task through the same pipeline"**

Different tasks require:
- Different agent combinations
- Different HITL checkpoints
- Different quality thresholds
- Different routing logic

---

## 📊 **Task Type Classification**

### **Task Types (6 Categories)**

```python
class TaskType(Enum):
    SIMPLE_QA = "simple_qa"                      # Quick factual questions
    RESEARCH_ARTICLE = "research_article"        # Deep research + writing
    CONCEPT_EXPLANATION = "concept_explanation"  # Educational content
    CODE_GENERATION = "code_generation"          # Code examples, debugging
    API_INTEGRATION = "api_integration"          # API docs + integration
    COMPARATIVE_ANALYSIS = "comparative_analysis" # Compare X vs Y
```

---

## 🔄 **Workflow Definitions**

### **1. SIMPLE_QA (Quick Factual Questions)**

**Example**: "What is LangGraph?", "Who created Python?"

**LangChain HITL Workflow:**
```python
from deepagents import create_deep_agent

simple_qa_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[analyze_query, retrieve_context, generate_response],
    interrupt_on={
        # Optional HITL - only if user enables it
        "retrieve_context": False,  # Skip by default
        "generate_response": False  # Skip by default
    },
    checkpointer=MemorySaver()
)
```

**Agent Flow:**
```
query_analyst → retrieval_specialist → writer → END
```

**Characteristics:**
- **Agents Used**: 3 (skip re-ranker, skip QA)
- **HITL Checkpoints**: 0 (fully automated)
- **Quality Threshold**: 0.5 (lower bar)
- **Max Results**: 5
- **Estimated Time**: 10-15 seconds

**When to Use:**
- Single, clear question
- Factual answer expected
- Minimal context needed
- Speed is priority

---

### **2. RESEARCH_ARTICLE (Deep Research + Writing)**

**Example**: "Write a comprehensive guide on LangGraph state management"

**LangChain HITL Workflow:**
```python
research_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query,
        retrieve_context,
        rerank_results,
        assess_quality,
        generate_response
    ],
    interrupt_on={
        "analyze_query": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "Review research plan and search strategy"
        },
        "retrieve_context": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "Review retrieved sources for comprehensiveness"
        },
        "rerank_results": {
            "allowed_decisions": ["approve", "reject"],
            "description": "Review ranked context quality"
        },
        "assess_quality": {
            "allowed_decisions": ["approve", "reject"],
            "description": "Review quality assessment"
        },
        "generate_response": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "Review draft article"
        }
    }
)
```

**Agent Flow:**
```
query_analyst 
  → [HITL #1: Approve research plan]
  → retrieval_specialist (multi-source, deep)
  → [HITL #2: Review sources]
  → re_ranker (comprehensive filtering)
  → [HITL #3: Approve context]
  → writer (long-form content)
  → [HITL #4: Review draft]
  → quality_assurance (thorough checks)
  → [HITL #5: Final approval]
  → END
```

**Characteristics:**
- **Agents Used**: All 5 agents
- **HITL Checkpoints**: 5 (all checkpoints)
- **Quality Threshold**: 0.8 (high bar)
- **Max Results**: 20-30
- **Estimated Time**: 2-5 minutes (with human feedback)

**When to Use:**
- Complex, multi-faceted topic
- Requires deep research
- Multiple sources needed
- Quality critical
- Iterative refinement expected

---

### **3. CONCEPT_EXPLANATION (Educational Content)**

**Example**: "Explain how async/await works in Python"

**LangChain HITL Workflow:**
```python
explanation_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query,
        retrieve_context,
        rerank_results,
        generate_response
    ],
    interrupt_on={
        "retrieve_context": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Verify explanation approach and examples"
        },
        "generate_response": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Review explanation clarity"
        }
    }
)
```

**Agent Flow:**
```
query_analyst
  → retrieval_specialist (focus on tutorials, examples)
  → [HITL #1: Verify explanation approach]
  → re_ranker (prioritize clarity)
  → writer (educational formatting)
  → [HITL #2: Review explanation]
  → END
```

**Characteristics:**
- **Agents Used**: 4 (skip QA, writer handles quality)
- **HITL Checkpoints**: 2 (after retrieval, after writer)
- **Quality Threshold**: 0.7
- **Max Results**: 10-15
- **Estimated Time**: 30-60 seconds

**When to Use:**
- Educational purpose
- Needs examples and analogies
- Clarity over comprehensiveness
- Some back-and-forth expected

---

### **4. CODE_GENERATION (Code Examples, Debugging)**

**Example**: "Show me how to implement a LangGraph checkpointer"

**LangChain HITL Workflow:**
```python
code_gen_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query,
        retrieve_code_examples,
        generate_code
    ],
    interrupt_on={
        "retrieve_code_examples": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Verify relevant code examples"
        },
        "generate_code": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Test and verify code"
        }
    }
)
```

**Agent Flow:**
```
query_analyst (identify code requirements)
  → retrieval_specialist (code-focused search)
  → [HITL #1: Verify relevant code examples]
  → writer (code formatting, syntax highlighting)
  → [HITL #2: Test/verify code]
  → END
```

**Characteristics:**
- **Agents Used**: 3 (query analyst, retrieval, writer)
- **HITL Checkpoints**: 2 (verify examples, verify code)
- **Quality Threshold**: 0.6
- **Max Results**: 5-8 (code examples)
- **Estimated Time**: 20-40 seconds

**When to Use:**
- Code examples needed
- Syntax-specific queries
- Debugging scenarios
- Implementation guidance

---

### **5. API_INTEGRATION (API Docs + Integration Guide)**

**Example**: "How do I integrate LangSmith tracing into my agent?"

**LangChain HITL Workflow:**
```python
api_integration_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query,
        retrieve_api_docs,
        retrieve_examples,
        generate_integration_guide
    ],
    interrupt_on={
        "retrieve_api_docs": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Confirm API documentation sources"
        },
        "generate_integration_guide": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Review integration steps"
        }
    }
)
```

**Agent Flow:**
```
query_analyst
  → retrieval_specialist (prioritize official API docs)
  → [HITL #1: Confirm API docs + version]
  → re_ranker (official docs first)
  → writer (step-by-step integration)
  → [HITL #2: Review integration steps]
  → END
```

**Characteristics:**
- **Agents Used**: 4 (all except QA)
- **HITL Checkpoints**: 2 (confirm docs, review steps)
- **Quality Threshold**: 0.75
- **Max Results**: 8-12
- **Estimated Time**: 30-60 seconds

**When to Use:**
- API integration tasks
- Library usage questions
- Official docs critical
- Version-specific queries

---

### **6. COMPARATIVE_ANALYSIS (Compare X vs Y)**

**Example**: "Compare LangChain vs LlamaIndex for RAG"

**LangChain HITL Workflow:**
```python
comparison_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query,
        retrieve_context_x,
        retrieve_context_y,
        rerank_results,
        generate_comparison
    ],
    interrupt_on={
        "retrieve_context_y": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Review sources for both sides"
        },
        "generate_comparison": {
            "allowed_decisions": ["approve", "edit"],
            "description": "Review comparison fairness and completeness"
        }
    }
)
```

**Agent Flow:**
```
query_analyst (identify comparison aspects)
  → retrieval_specialist (dual retrieval for X and Y)
  → [HITL #1: Review balanced sources]
  → re_ranker (balance across both topics)
  → writer (structured comparison table)
  → [HITL #2: Review comparison]
  → END
```

**Characteristics:**
- **Agents Used**: 4 (skip QA)
- **HITL Checkpoints**: 2 (balanced sources, fair comparison)
- **Quality Threshold**: 0.75
- **Max Results**: 12-16 (balanced across topics)
- **Estimated Time**: 45-90 seconds

**When to Use:**
- Compare two technologies/approaches
- Pros/cons analysis
- Decision-making support
- Balanced perspective needed

---

## 🎨 **Workflow Selection Logic**

### **Automatic Task Detection**

```python
class TaskDetector:
    """Detect task type from query for workflow selection."""
    
    def detect_task_type(self, query: str) -> TaskType:
        """Analyze query and determine task type."""
        query_lower = query.lower()
        
        # Comparative analysis
        if any(word in query_lower for word in ["compare", "vs", "versus", "difference between"]):
            return TaskType.COMPARATIVE_ANALYSIS
        
        # Code generation
        if any(word in query_lower for word in ["implement", "code", "example", "how to code"]):
            return TaskType.CODE_GENERATION
        
        # API integration
        if any(word in query_lower for word in ["integrate", "api", "setup", "configure"]):
            return TaskType.API_INTEGRATION
        
        # Research article
        if any(word in query_lower for word in ["comprehensive", "guide", "write about", "deep dive"]):
            return TaskType.RESEARCH_ARTICLE
        
        # Concept explanation
        if any(word in query_lower for word in ["explain", "what is", "how does", "why"]):
            return TaskType.CONCEPT_EXPLANATION
        
        # Default: Simple QA
        return TaskType.SIMPLE_QA
```

### **Workflow Configuration**

```python
WORKFLOW_CONFIGS = {
    TaskType.SIMPLE_QA: {
        "agents": ["query_analyst", "retrieval", "writer"],
        "hitl_checkpoints": [],
        "quality_threshold": 0.5,
        "max_results": 5,
        "enable_re_retrieval": False
    },
    TaskType.RESEARCH_ARTICLE: {
        "agents": ["query_analyst", "retrieval", "re_ranker", "quality_assurance", "writer"],
        "hitl_checkpoints": ["query_analysis", "retrieval", "ranking", "quality", "writer"],
        "quality_threshold": 0.8,
        "max_results": 30,
        "enable_re_retrieval": True
    },
    # ... other workflows
}
```

---

## 📊 **Performance Comparison**

| Task Type | Agents | HITL | Time | Quality | Use Case |
|-----------|--------|------|------|---------|----------|
| Simple QA | 3 | 0 | 10-15s | Good | Quick facts |
| Research | 5 | 5 | 2-5min | Excellent | Deep research |
| Explanation | 4 | 2 | 30-60s | Excellent | Education |
| Code Gen | 3 | 2 | 20-40s | Good | Code examples |
| API Integration | 4 | 2 | 30-60s | Excellent | Integration |
| Comparison | 4 | 2 | 45-90s | Excellent | Decision support |

---

## 🚀 **Usage**

```python
from agents.rag import RAGSwarmCoordinator
from agents.rag.task_detector import TaskDetector

# Initialize
detector = TaskDetector()
swarm = RAGSwarmCoordinator(context_engine)

# Detect task type
task_type = detector.detect_task_type(user_query)

# Execute with task-specific workflow
result = await swarm.execute_task_adaptive(
    query=user_query,
    task_type=task_type,
    config={"configurable": {"thread_id": "session_123"}}
)
```

---

## ✅ **Implementation Status**

- [x] Task type definitions
- [x] Workflow configurations
- [ ] LangChain HITL integration
- [ ] Task detector implementation
- [ ] Workflow-specific agent initialization
- [ ] UI task type selector
- [ ] Performance benchmarking per workflow

---

**Next Steps:**
1. Implement task detector
2. Create workflow-specific agent configurations
3. Test each workflow independently
4. Benchmark performance per task type

**Last Updated:** 2025-01-29


