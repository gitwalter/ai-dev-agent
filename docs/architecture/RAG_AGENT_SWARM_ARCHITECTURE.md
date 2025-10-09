# RAG Agent Swarm Architecture

**Created:** 2025-01-08  
**Purpose:** Specialized agent swarm for high-quality RAG operations  
**Status:** 🚧 Design Phase

---

## 🎯 **Vision**

Replace the monolithic `ContextAwareAgent` with a **specialized agent swarm** where each agent excels at one aspect of RAG, resulting in higher quality responses through expert collaboration.

---

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Swarm Coordinator                     │
│  (Orchestrates the entire RAG pipeline and quality control)  │
└───────────┬─────────────────────────────────────────────────┘
            │
            ├─────────────┐
            │             │
    ┌───────▼──────┐  ┌──▼──────────────┐
    │  Query       │  │  Retrieval      │
    │  Analyst     │  │  Specialist     │
    │  Agent       │  │  Agent          │
    └───────┬──────┘  └──┬──────────────┘
            │            │
            │       ┌────▼─────────────┐
            │       │  Re-Ranker       │
            │       │  Agent           │
            │       └────┬─────────────┘
            │            │
            │       ┌────▼─────────────┐
            │       │  Quality         │
            │       │  Assurance Agent │
            │       └────┬─────────────┘
            │            │
            └────────────▼─────────────┐
                   │  Writer Agent     │
                   │  (Response Gen)   │
                   └───────────────────┘
```

---

## 👥 **Agent Roles**

### **1. RAGSwarmCoordinator** 🎯
**Role:** Orchestrates the entire RAG pipeline  
**Responsibilities:**
- Receives user query
- Routes query through specialized agents in optimal order
- Aggregates results from all agents
- Makes final quality decision
- Returns complete response with metadata

**Key Methods:**
- `async def process_query(query: str) -> Dict`
- `async def orchestrate_retrieval_pipeline(query: str) -> List[Document]`
- `async def coordinate_quality_check(results: List) -> QualityReport`
- `async def delegate_to_writer(context: List, query: str) -> str`

---

### **2. QueryAnalystAgent** 🔍
**Role:** Understands and expands user queries  
**Responsibilities:**
- Query intent classification (factual, conceptual, procedural, multi-hop)
- Query rewriting and expansion
- Key concept extraction
- Search strategy recommendation

**Input:** Raw user query  
**Output:** 
```python
{
    'original_query': str,
    'intent': str,  # 'factual', 'conceptual', 'procedural', 'multi-hop'
    'rewritten_queries': List[str],  # 3-5 variants
    'key_concepts': List[str],  # Important terms
    'search_strategy': str,  # 'broad', 'focused', 'multi-stage'
    'complexity': float  # 0-1 score
}
```

**LLM Model:** Gemini 2.0 Flash (fast, good at query understanding)

---

### **3. RetrievalSpecialistAgent** 📚
**Role:** Expert at finding relevant context  
**Responsibilities:**
- Execute multiple search strategies (semantic, keyword, hybrid)
- Implement query expansion and decomposition
- Search across multiple query variants
- Retrieve diverse, comprehensive results
- Handle different document types optimally

**Input:** Query analysis from QueryAnalystAgent  
**Output:**
```python
{
    'search_results': List[Document],  # Raw retrieved documents
    'search_metadata': {
        'searches_performed': int,
        'total_candidates': int,
        'retrieval_time': float,
        'strategies_used': List[str]
    }
}
```

**Specialization:** No LLM needed - pure retrieval optimization

---

### **4. ReRankerAgent** 📊
**Role:** Intelligent result scoring and ranking  
**Responsibilities:**
- Multi-signal scoring (semantic, keyword, quality, diversity)
- Deduplication based on semantic similarity
- Position optimization (lost-in-middle mitigation)
- Context window budget management
- Relevance threshold filtering

**Input:** Raw search results + query analysis  
**Output:**
```python
{
    'ranked_results': List[Document],  # Top N ranked and deduplicated
    'scores': List[float],  # Combined scores for each result
    'scoring_details': List[Dict],  # Breakdown per result
    'removed_count': int,  # How many filtered out
    'ranking_metadata': {
        'avg_score': float,
        'top_score': float,
        'diversity_score': float
    }
}
```

**LLM Model:** Optional - Gemini 2.0 Flash for semantic quality assessment

---

### **5. QualityAssuranceAgent** ✅
**Role:** Validates retrieval quality and completeness  
**Responsibilities:**
- Verify retrieved context answers the query
- Check for information gaps
- Assess context quality and relevance
- Trigger re-retrieval if quality insufficient
- Provide quality report for coordinator

**Input:** Ranked results + original query  
**Output:**
```python
{
    'quality_verdict': str,  # 'excellent', 'good', 'insufficient', 'poor'
    'quality_score': float,  # 0-1 overall quality
    'coverage_score': float,  # 0-1 query coverage
    'relevance_score': float,  # 0-1 relevance
    'issues': List[str],  # Any quality issues found
    'recommendations': List[str],  # Improvement suggestions
    'needs_re_retrieval': bool,  # Should we search again?
    're_retrieval_strategy': Optional[str]  # How to improve
}
```

**LLM Model:** Gemini 2.0 Flash Thinking (reasoning for quality assessment)

---

### **6. WriterAgent** ✍️
**Role:** Synthesizes context into coherent responses  
**Responsibilities:**
- Generate comprehensive, well-structured answers
- Cite sources appropriately
- Maintain factual accuracy (no hallucination)
- Adapt tone and style to query type
- Format response for clarity

**Input:** Ranked context + quality report + original query  
**Output:**
```python
{
    'response': str,  # Final answer
    'confidence': float,  # 0-1 confidence in answer
    'sources_cited': List[str],  # Source references
    'limitations': Optional[str],  # Any limitations in answer
    'writing_metadata': {
        'tokens_used': int,
        'generation_time': float,
        'style': str  # 'technical', 'explanatory', 'concise'
    }
}
```

**LLM Model:** Gemini 2.0 Flash Thinking (best for comprehensive responses)

---

## 🔄 **Workflow Pipeline**

### **Standard Query Flow:**

```python
1. User Query
   ↓
2. RAGSwarmCoordinator receives query
   ↓
3. QueryAnalystAgent analyzes query
   ├─ Intent classification
   ├─ Query rewriting (3-5 variants)
   ├─ Key concept extraction
   └─ Search strategy recommendation
   ↓
4. RetrievalSpecialistAgent retrieves context
   ├─ Multi-search across query variants
   ├─ Diverse retrieval strategies
   └─ Comprehensive candidate set (20-30 results)
   ↓
5. ReRankerAgent ranks and filters
   ├─ Multi-signal scoring
   ├─ Deduplication
   ├─ Position optimization
   └─ Top N results (8-12)
   ↓
6. QualityAssuranceAgent validates
   ├─ Quality assessment
   ├─ Coverage check
   ├─ Gap analysis
   └─ Re-retrieval trigger (if needed)
   ↓
7. WriterAgent generates response
   ├─ Synthesize context
   ├─ Generate answer
   ├─ Cite sources
   └─ Format output
   ↓
8. RAGSwarmCoordinator returns final result
```

### **Quality Feedback Loop:**

```python
IF QualityAssuranceAgent.quality_score < 0.7:
    ↓
    Re-analyze query with different strategy
    ↓
    Re-retrieve with expanded search
    ↓
    Re-rank with adjusted weights
    ↓
    Re-check quality
    ↓
    IF still insufficient:
        Return with limitation notice
    ELSE:
        Proceed to Writer
```

---

## 📊 **Agent Communication Protocol**

### **Message Format:**
```python
{
    'message_id': str,
    'from_agent': str,
    'to_agent': str,
    'timestamp': datetime,
    'message_type': str,  # 'request', 'response', 'notification'
    'payload': Dict,
    'metadata': {
        'query_id': str,
        'session_id': str,
        'trace_id': str  # For LangSmith
    }
}
```

### **Coordinator State:**
```python
{
    'query_id': str,
    'original_query': str,
    'current_stage': str,
    'query_analysis': Dict,
    'retrieval_results': Dict,
    'ranked_results': Dict,
    'quality_report': Dict,
    'final_response': Optional[Dict],
    'metrics': {
        'total_time': float,
        'retrieval_time': float,
        'ranking_time': float,
        'qa_time': float,
        'writing_time': float
    }
}
```

---

## 🎨 **Benefits Over Single Agent**

| Aspect | Single Agent | Agent Swarm |
|--------|--------------|-------------|
| **Specialization** | Jack of all trades | Expert specialists |
| **Quality Control** | Self-validation | Dedicated QA agent |
| **Retrieval Strategy** | Fixed approach | Adaptive, multi-strategy |
| **Re-ranking** | Simple scoring | Multi-signal, intelligent |
| **Response Quality** | Good | Excellent (dedicated writer) |
| **Debugging** | Hard to trace | Clear agent boundaries |
| **Optimization** | Optimize one thing | Optimize each stage |
| **Scalability** | Monolithic | Modular, replaceable agents |
| **LangSmith Traces** | Single span | Clear multi-agent flow |
| **Testability** | Test everything | Test each agent independently |

---

## 🔧 **Implementation Plan**

### **Phase 1: Core Agents** (Week 1)
- [x] Design architecture
- [ ] Implement RAGSwarmCoordinator
- [ ] Implement QueryAnalystAgent
- [ ] Implement RetrievalSpecialistAgent
- [ ] Basic integration test

### **Phase 2: Quality & Ranking** (Week 1-2)
- [ ] Implement ReRankerAgent
- [ ] Implement QualityAssuranceAgent
- [ ] Quality feedback loop
- [ ] Comparative testing vs single agent

### **Phase 3: Response Generation** (Week 2)
- [ ] Implement WriterAgent
- [ ] End-to-end pipeline
- [ ] LangSmith tracing integration
- [ ] UI integration

### **Phase 4: Optimization** (Week 2-3)
- [ ] Performance tuning
- [ ] Agent prompt optimization
- [ ] Caching strategies
- [ ] Golden dataset evaluation

---

## 📈 **Success Metrics**

### **Quality Metrics:**
- ✅ Response accuracy (vs golden dataset)
- ✅ Context relevance score
- ✅ Source citation accuracy
- ✅ No hallucination rate

### **Performance Metrics:**
- ✅ End-to-end latency
- ✅ Token efficiency (cost)
- ✅ Retrieval precision/recall
- ✅ Re-ranking effectiveness

### **User Experience:**
- ✅ Response completeness
- ✅ Answer clarity
- ✅ Source attribution
- ✅ Handling edge cases

---

## 🎯 **Example Scenarios**

### **Scenario 1: Simple Factual Query**
**Query:** "What is the purpose of ContextEngine?"

**Flow:**
1. QueryAnalyst → Intent: factual, Strategy: focused
2. Retrieval → 1-2 targeted searches
3. ReRanker → Top 3 highly relevant results
4. QA → Quality: excellent (clear answer found)
5. Writer → Concise, direct answer with file citation

**Expected Time:** < 2 seconds

---

### **Scenario 2: Complex Multi-Hop Query**
**Query:** "How does the RAG system integrate with LangChain and what tracing features does it provide?"

**Flow:**
1. QueryAnalyst → Intent: multi-hop, Strategy: multi-stage, Decomposed into sub-queries
2. Retrieval → 3-4 diverse searches (RAG integration + LangChain + tracing)
3. ReRanker → Top 10 results covering all aspects
4. QA → Quality: good, Coverage: 85% (check for gaps)
5. Writer → Comprehensive answer synthesizing multiple sources

**Expected Time:** 3-5 seconds

---

### **Scenario 3: Insufficient Context**
**Query:** "What is the quantum flux capacitor algorithm used in the system?"

**Flow:**
1. QueryAnalyst → Intent: conceptual, Strategy: broad
2. Retrieval → Multiple searches, few relevant results
3. ReRanker → Low scores, insufficient quality
4. QA → Quality: poor, Needs re-retrieval: YES
5. Retrieval → Expanded search with related terms
6. QA → Quality: still poor
7. Writer → "I don't have sufficient information about quantum flux capacitor in the codebase. Based on available context, I can tell you about [related concepts]..."

**Expected Time:** 4-6 seconds (due to re-retrieval)

---

## 🔍 **LangSmith Tracing**

With the swarm architecture, LangSmith traces will show:

```
Trace: "RAG Query Processing"
├─ RAGSwarmCoordinator.process_query
│  ├─ QueryAnalystAgent.analyze_query
│  │  ├─ LLM: Gemini 2.0 Flash (intent classification)
│  │  └─ Output: query_analysis
│  ├─ RetrievalSpecialistAgent.retrieve
│  │  ├─ Search #1: original query
│  │  ├─ Search #2: rewritten variant 1
│  │  ├─ Search #3: rewritten variant 2
│  │  └─ Output: 24 candidates
│  ├─ ReRankerAgent.rank_and_filter
│  │  ├─ Multi-signal scoring
│  │  ├─ Deduplication
│  │  └─ Output: 10 ranked results
│  ├─ QualityAssuranceAgent.validate
│  │  ├─ LLM: Gemini 2.0 Flash Thinking (quality check)
│  │  └─ Output: quality_report (score: 0.85)
│  └─ WriterAgent.generate_response
│     ├─ LLM: Gemini 2.0 Flash Thinking (response generation)
│     └─ Output: final_response
└─ Output: Complete RAG result with metadata
```

**Clear visibility** into each agent's contribution! 🎯

---

## 📚 **Related Documentation**

- [RAG Best Practices 2025](./RAG_BEST_PRACTICES_2025.md)
- [RAG LangSmith Integration](./RAG_LANGSMITH_INTEGRATION.md)
- [MCP Context Engineering](../research/MCP_CONTEXT_ENGINEERING_2025.md)

---

**Next Steps:** Implement the core agents and coordinator! 🚀

