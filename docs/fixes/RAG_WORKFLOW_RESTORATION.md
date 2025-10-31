# RAG Workflow Restoration Plan

## Problem

The agentic RAG workflow has been oversimplified. Looking at the LangSmith trace:
- https://smith.langchain.com/public/3f828c4c-bdf1-41a7-941e-07afc1c3a183/r

Current workflow is too simple:
```
agent → tools → generate_answer → END
```

**Missing sophisticated RAG agents**:
- ❌ QueryAnalystAgent (query understanding and expansion)
- ❌ RetrievalSpecialistAgent (multi-source retrieval orchestration)
- ❌ ReRankerAgent (relevance scoring and filtering)
- ❌ QualityAssuranceAgent (comprehensive quality checks)
- ❌ WriterAgent (sophisticated answer generation)

## Original Sophisticated Workflow

The original workflow had:
1. **Query Analysis**: Understanding user intent, extracting key concepts
2. **Retrieval**: Multi-source retrieval (project docs, web, Wikipedia)
3. **Re-Ranking**: Relevance scoring and filtering
4. **Quality Assurance**: Completeness, consistency, readiness checks
5. **Answer Generation**: Sophisticated synthesis with citations

## Desired Workflow (with HITL)

```
START
  ↓
query_analyst (QueryAnalystAgent)
  ↓
retrieval_specialist (RetrievalSpecialistAgent) 
  ↓
re_ranker (ReRankerAgent)
  ↓
[INTERRUPT: human_review] ← Human approves/rejects
  ↓
quality_assurance (QualityAssuranceAgent)
  ↓
writer (WriterAgent)
  ↓
END
```

With conditional edges:
- If re-ranking quality is low → `rewrite_question` → back to query_analyst
- If human rejects → `rewrite_question` → back to query_analyst

## Implementation Plan

### Phase 1: Verify Agent Interfaces ✅
- [x] QueryAnalystAgent has `execute(task)` method
- [x] RetrievalSpecialistAgent has `execute(task)` method  
- [x] ReRankerAgent has `execute(task)` method
- [x] QualityAssuranceAgent has `execute(task)` method
- [x] WriterAgent has `execute(task)` method

All agents extend `EnhancedBaseAgent` with standard `execute()` interface.

### Phase 2: Create Sophisticated Node Implementations
- [ ] `_query_analyst_node`: Calls `QueryAnalystAgent.execute()`
- [ ] `_retrieval_specialist_node`: Calls `RetrievalSpecialistAgent.execute()`
- [ ] `_re_ranker_node`: Calls `ReRankerAgent.execute()`
- [ ] `_quality_assurance_node`: Calls `QualityAssuranceAgent.execute()`
- [ ] `_writer_node`: Calls `WriterAgent.execute()`
- [ ] `_rewrite_question_node`: Calls `QueryAnalystAgent.execute()` with rewrite mode

### Phase 3: Rebuild Graph
- [ ] Replace simple `agent → tools → generate` with sophisticated multi-agent flow
- [ ] Add conditional routing after re-ranking
- [ ] Integrate human_review interrupt after re-ranking
- [ ] Add rewrite loop back to query_analyst

### Phase 4: Update Streamlit UI
- [ ] Show which agent is currently active
- [ ] Display intermediate results (query analysis, retrieval stats, re-ranking scores)
- [ ] Enhance human review UI with quality metrics
- [ ] Show full agent flow in UI

### Phase 5: Test and Validate
- [ ] Test complete flow in Streamlit
- [ ] Test human-in-the-loop interrupts
- [ ] Verify LangSmith traces show all agents
- [ ] Test rewrite loop
- [ ] Validate answer quality

## Key Changes Needed

### 1. RAGSwarmCoordinator.__init__
```python
# Add agent initialization
self.query_analyst = QueryAnalystAgent()
self.retrieval_specialist = RetrievalSpecialistAgent(context_engine)
self.re_ranker = ReRankerAgent()
self.quality_assurance = QualityAssuranceAgent()
self.writer = WriterAgent()
```

### 2. _build_graph()
Replace simple tool-based flow with multi-agent orchestration.

### 3. Node Implementations
Each node calls the corresponding agent's `execute()` method and properly formats the state.

## Expected Benefits

1. **Better Answers**: Sophisticated multi-agent processing
2. **Transparent Process**: Each agent's work visible in LangSmith trace
3. **Quality Assurance**: Multiple quality checkpoints
4. **Human Oversight**: Strategic interrupt points for review
5. **Adaptive Retrieval**: Query rewriting when quality is insufficient

## Timeline

- Phase 1: ✅ Done (agent verification)
- Phase 2-3: 2-3 hours (node implementation + graph rebuild)
- Phase 4: 1 hour (UI enhancements)
- Phase 5: 1-2 hours (testing and validation)

**Total**: ~5-6 hours of focused development

## Next Steps

1. Implement sophisticated node methods in `rag_swarm_coordinator.py`
2. Rebuild `_build_graph()` with multi-agent flow
3. Update UI to show agent-level progress
4. Test end-to-end with human-in-the-loop

