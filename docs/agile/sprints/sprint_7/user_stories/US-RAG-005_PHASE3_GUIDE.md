# US-RAG-005 Phase 3: LangSmith Trace Validation Guide

**User Story**: US-RAG-005 - Sophisticated Multi-Agent Workflow Restoration  
**Phase**: Phase 3 - Testing & Validation  
**Date**: October 30, 2025  
**Status**: IN PROGRESS

---

## 🎯 Objective

Validate that the sophisticated 5-agent workflow is properly functioning and visible in LangSmith traces:

1. ✅ **AC-3.1**: Test complete 5-agent flow in LangSmith (show all agents)
2. ✅ **AC-3.2**: Verify each agent's work is visible in trace
3. ✅ **AC-3.3**: Validate answer quality improvement vs. simple mode
4. ✅ **AC-3.4**: Test rewrite loop when quality is insufficient

---

## 📋 Prerequisites

### 1. Environment Setup

Ensure these environment variables are set:

```bash
# Required: Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"

# Required: LangSmith tracing (for Phase 3 validation)
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="your-langsmith-api-key"
export LANGCHAIN_PROJECT="ai-dev-agent"
```

### 2. Verify LangSmith Access

1. Go to https://smith.langchain.com/
2. Ensure you're logged in
3. Verify project "ai-dev-agent" exists (or create it)
4. Check that API key is valid

### 3. Vector Store Setup

Ensure the vector store has documents indexed:

```bash
# Check if collection exists
python -c "from context.context_engine import ContextEngine; engine = ContextEngine(); print(f'Collection: {engine.vector_store.collection_name}')"

# If empty, upload some documents via Streamlit app
# Run: streamlit run apps/rag_management_app.py
```

---

## 🧪 Testing Steps

### Step 1: Run Automated Test Script

The test script will:
- Execute 3 sophisticated workflow tests
- Test rewrite loop functionality
- Compare with simple mode
- Generate LangSmith traces with proper metadata

```bash
# Activate virtual environment (if using one)
# C:\App\Anaconda\Scripts\activate.bat venv_name

# Run test script
python tests/rag/test_us_rag_005_phase3.py
```

**Expected Output**:
```
🚀 Starting US-RAG-005 Phase 3 Validation Tests
✅ EXECUTION SUCCESSFUL
   Response length: 1234 chars
   Messages: 15
   Response preview: ...
```

### Step 2: Verify LangSmith Traces

1. **Open LangSmith Dashboard**:
   - Go to https://smith.langchain.com/
   - Navigate to your project: `ai-dev-agent`
   - Look for runs with tag: `us-rag-005`

2. **Check Trace Structure**:
   Each trace should show:
   ```
   RAG-Swarm-[query]
   ├── query_analyst (QueryAnalystAgent)
   ├── retrieval_specialist (RetrievalSpecialistAgent)
   ├── re_ranker (ReRankerAgent)
   ├── writer (WriterAgent)
   └── quality_assurance (QualityAssuranceAgent)
   ```

3. **Verify Each Agent**:
   - ✅ **query_analyst**: Should show query analysis, intent classification
   - ✅ **retrieval_specialist**: Should show document retrieval with scores
   - ✅ **re_ranker**: Should show re-ranking results
   - ✅ **writer**: Should show answer generation
   - ✅ **quality_assurance**: Should show quality checks

### Step 3: Manual Test (Optional)

For more control, test manually:

```python
import asyncio
from context.context_engine import ContextEngine
from agents.rag.rag_swarm_coordinator import RAGSwarmCoordinator

async def test():
    # Initialize
    engine = ContextEngine(collection_name="project_docs")
    coordinator = RAGSwarmCoordinator(
        context_engine=engine,
        human_in_loop=False,
        retrieval_only=False
    )
    
    # Execute with LangSmith metadata
    config = {
        "configurable": {"thread_id": "test-123"},
        "run_name": "Manual-Test-US-RAG-005",
        "tags": ["us-rag-005", "manual-test"],
        "metadata": {
            "test": "manual",
            "query": "What is LangGraph?"
        }
    }
    
    result = await coordinator.execute(
        query="What is LangGraph and how does it handle state management?",
        config=config
    )
    
    print(f"Status: {result['status']}")
    print(f"Response: {result.get('response', '')[:200]}")

asyncio.run(test())
```

### Step 4: Compare Simple vs Sophisticated Mode

**Simple Mode** (retrieval_only=True):
- Should show only: `simple_retrieval` → `simple_answer`
- Faster execution (~5-10 seconds)
- Basic response quality

**Sophisticated Mode** (retrieval_only=False):
- Should show all 5 agents
- Slower execution (~30-60 seconds)
- Higher quality response

**Comparison Criteria**:
- Response length (sophisticated should be longer/more detailed)
- Response accuracy (sophisticated should be more accurate)
- Source citations (sophisticated should cite sources better)
- Context understanding (sophisticated should demonstrate better understanding)

### Step 5: Test Rewrite Loop

The test script includes a nonsense query test:

```python
query = "asdfghjkl random gibberish"
```

**Expected Behavior**:
1. query_analyst processes query
2. Quality is insufficient
3. System triggers rewrite_question node
4. Rewritten query loops back to query_analyst
5. Process continues with improved query

**Verify in LangSmith**:
- Trace should show `rewrite_question` node
- Should see loop back to `query_analyst`
- Final response should be based on rewritten query

---

## ✅ Acceptance Criteria Checklist

### AC-3.1: Test complete 5-agent flow in LangSmith
- [ ] Test script executed successfully
- [ ] LangSmith trace shows all 5 agents
- [ ] Trace structure is correct: query_analyst → retrieval → rerank → writer → QA
- [ ] Each agent node appears in trace

### AC-3.2: Verify each agent's work is visible in trace
- [ ] query_analyst trace shows query analysis output
- [ ] retrieval_specialist trace shows retrieved documents
- [ ] re_ranker trace shows ranking scores
- [ ] writer trace shows answer generation
- [ ] quality_assurance trace shows quality checks

### AC-3.3: Validate answer quality improvement vs. simple mode
- [ ] Comparison test executed
- [ ] Sophisticated mode response is longer
- [ ] Sophisticated mode response is more accurate
- [ ] Sophisticated mode has better citations
- [ ] Quality metrics documented

### AC-3.4: Test rewrite loop when quality is insufficient
- [ ] Nonsense query test executed
- [ ] rewrite_question node triggered
- [ ] Loop back to query_analyst visible
- [ ] Final response based on rewritten query

---

## 📊 Test Results Documentation

After running tests, document results:

```markdown
### Test Results - [Date]

**Test Execution**: ✅ PASSED / ❌ FAILED

**AC-3.1 Results**:
- Traces visible: Yes/No
- All 5 agents shown: Yes/No
- Trace URL: [link]

**AC-3.2 Results**:
- QueryAnalyst visible: Yes/No
- RetrievalSpecialist visible: Yes/No
- ReRanker visible: Yes/No
- Writer visible: Yes/No
- QualityAssurance visible: Yes/No

**AC-3.3 Results**:
- Simple mode avg response length: XXX chars
- Sophisticated mode avg response length: XXX chars
- Quality improvement: Measurable/Not measurable

**AC-3.4 Results**:
- Rewrite loop triggered: Yes/No
- Loop visible in trace: Yes/No
- Final response improved: Yes/No
```

---

## 🔗 LangSmith Trace Links

After running tests, save trace URLs here:

1. **Sophisticated Test 1**: [LangSmith URL]
2. **Sophisticated Test 2**: [LangSmith URL]
3. **Sophisticated Test 3**: [LangSmith URL]
4. **Rewrite Loop Test**: [LangSmith URL]
5. **Simple Mode Comparison**: [LangSmith URL]

---

## 🐛 Troubleshooting

### Issue: No traces in LangSmith

**Solution**:
1. Verify `LANGCHAIN_TRACING_V2=true` is set
2. Verify `LANGCHAIN_API_KEY` is valid
3. Check LangSmith dashboard for errors
4. Verify project name matches `LANGCHAIN_PROJECT`

### Issue: Only some agents visible

**Solution**:
1. Check that all agent nodes are calling LLM (each agent should make LLM calls)
2. Verify LangSmith trace depth (may need to expand trace)
3. Check agent execution logs for errors

### Issue: Rewrite loop not triggering

**Solution**:
1. Verify quality_assurance agent is properly detecting low quality
2. Check routing logic in `_route_after_reranking`
3. Ensure rewrite_question node is properly connected

---

## 📝 Next Steps After Validation

Once all acceptance criteria are met:

1. ✅ Update US-RAG-005.md to mark Phase 3 complete
2. ✅ Document test results and trace URLs
3. ✅ Move to Phase 4: Answer quality testing
4. ✅ Update sprint status in current_sprint.md

---

## 🎯 Success Criteria

Phase 3 is complete when:
- ✅ All 4 acceptance criteria pass
- ✅ LangSmith traces show complete 5-agent workflow
- ✅ Test results documented
- ✅ Quality improvement verified

**Phase 3 Completion**: [ ] IN PROGRESS / [ ] COMPLETE

