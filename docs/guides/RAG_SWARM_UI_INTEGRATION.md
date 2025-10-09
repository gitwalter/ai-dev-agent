# RAG Agent Swarm UI Integration Guide

**Created:** 2025-01-08  
**Status:** ✅ Integration Complete  
**Purpose:** Guide for using the RAG Agent Swarm in the RAG Management UI

---

## 🎉 **What's New**

The RAG Management App now supports **dual modes**:
1. **🔥 Agent Swarm (Best Quality)** - 5 specialized agents working together
2. **⚡ Single Agent (Fast)** - Original single-agent approach

You can switch between them and compare results in real-time!

---

## 🚀 **How to Use**

### **Starting the RAG UI**

```bash
# Activate environment
C:\App\Anaconda\Scripts\activate.bat base

# Start RAG Management App
streamlit run apps/rag_management_app.py --server.port 8510
```

Navigate to: [http://localhost:8510](http://localhost:8510)

---

## 💬 **Agent Chat Page**

### **Selecting Mode**

1. Go to **"💬 Agent Chat"** tab
2. In the **"RAG Mode"** dropdown, choose:
   - **🔥 Agent Swarm (Best Quality)** ← Recommended for best results
   - **⚡ Single Agent (Fast)** ← Faster, simpler

### **What You'll See with Agent Swarm**

When using **Agent Swarm mode**, the UI shows:

#### **Chat Interface:**
- Your query
- Agent's comprehensive response with citations
- Context statistics panel (if Debug Mode enabled)

#### **Context Statistics Panel** (Debug Mode):
```
🔥 Agent Swarm Pipeline
✅ 1. Query Analysis
✅ 2. Context Retrieval
✅ 3. Re-ranking
✅ 4. Quality Assurance
✅ 5. Response Generation

Quality & Confidence
Quality Score: 🟢 0.85
Confidence: 🟢 0.82

⏱️ Pipeline Timing
Query Analysis: 234ms
Retrieval: 412ms
Re Ranking: 156ms
Qa: 189ms
Generation: 1,845ms

📚 Sources Cited
• agents/rag/query_analyst_agent.py
• docs/architecture/RAG_AGENT_SWARM_ARCHITECTURE.md
```

---

## 🧪 **Testing & Evaluation Page**

### **Running Tests**

1. Go to **"🧪 Testing & Evaluation"** tab
2. Click **"Single Query Test"** tab
3. Enter your test query
4. Click **"🚀 Run Test"**

The test now uses **Agent Swarm by default**!

### **Transparency Report**

The transparency report now shows:

#### **Overview Metrics:**
```
Mode: 🔥 Agent Swarm

⏱️ Total Time  📄 Results  Quality  Confidence  Stages
   2,845ms        10      🟢 0.85   🟢 0.82    ✅ 5/5
```

#### **Generated Response:**
Full response with proper citations and formatting

#### **Retrieved Context Details:**
- Top 10 results with scores
- Scoring breakdown (Semantic, Keyword, Quality, Diversity)
- Source information

#### **Processing Pipeline:**
```
🔥 Agent Swarm Pipeline

✅ 1️⃣ Query Analysis (QueryAnalystAgent)
✅ 2️⃣ Context Retrieval (RetrievalSpecialistAgent)
✅ 3️⃣ Re-ranking (ReRankerAgent)
✅ 4️⃣ Quality Assurance (QualityAssuranceAgent)
✅ 5️⃣ Response Generation (WriterAgent)

⏱️ Stage Timing
Query Analysis: 234ms
Retrieval: 412ms
Re Ranking: 156ms
Qa: 189ms
Generation: 1,845ms

🔍 Query Analysis Details
{
  "original_query": "What is context engineering?",
  "intent": "conceptual",
  "rewritten_queries": [...],
  "key_concepts": [...],
  "search_strategy": "broad",
  "complexity": 0.55
}

📚 Sources Cited
• file1.py
• file2.md
```

---

## 🔍 **Debug Mode Features**

### **Enabling Debug Mode**

In the Agent Chat page:
1. Check the **"Debug Mode"** checkbox
2. Adjust **"Context Detail Level"** slider to "Debug"

### **What Debug Mode Shows**

- **Real-time pipeline visualization**
- **Quality scores and confidence**
- **Stage-by-stage timing**
- **Query analysis breakdown**
- **Sources cited**
- **Full context statistics**

---

## 📊 **Comparing Swarm vs Single Agent**

### **Side-by-Side Comparison**

To compare both modes:

1. Ask the same question in **Agent Swarm** mode
2. Note the response quality and timing
3. Switch to **Single Agent** mode
4. Ask the same question again
5. Compare:
   - **Response quality and completeness**
   - **Source citations**
   - **Processing time**
   - **Confidence scores** (swarm only)

### **Expected Differences**

| Aspect | Single Agent | Agent Swarm |
|--------|-------------|-------------|
| **Quality** | Good | Excellent ✨ |
| **Citations** | Basic | Comprehensive |
| **Speed** | Fast (1-2s) | Moderate (3-5s) |
| **Context** | Single search | Multi-stage |
| **QA** | Self-check | Dedicated QA agent |
| **Confidence** | Implicit | Explicit score |
| **Traceability** | Limited | Full pipeline visibility |

---

## 🎯 **Best Practices**

### **When to Use Agent Swarm**
- ✅ Complex queries requiring comprehensive answers
- ✅ Multi-hop questions spanning multiple concepts
- ✅ When accuracy and citations are critical
- ✅ For production-quality responses
- ✅ When you need quality scoring

### **When to Use Single Agent**
- ✅ Simple factual queries
- ✅ Quick testing during development
- ✅ When speed is more important than depth
- ✅ For exploratory queries

---

## 🔧 **Configuration**

### **Swarm Parameters** (in code)

When using the swarm programmatically:

```python
from agents.rag import RAGSwarmCoordinator
from context.context_engine import ContextEngine

# Initialize
context_engine = ContextEngine(context_config)
swarm = RAGSwarmCoordinator(context_engine)

# Execute with custom parameters
result = await swarm.execute({
    'query': 'Your question here',
    'max_results': 10,           # Default: 10
    'quality_threshold': 0.7,     # Default: 0.7 (0.0-1.0)
    'enable_re_retrieval': True   # Default: True
})
```

### **Parameters Explained:**

- **max_results**: Number of top results to return (after ranking)
- **quality_threshold**: Minimum quality score (triggers re-retrieval if below)
- **enable_re_retrieval**: Allow automatic re-retrieval if quality is low

---

## 🐛 **Troubleshooting**

### **"Agent Swarm mode not available"**
- Check that all RAG agent files are present in `agents/rag/`
- Verify imports are working: `from agents.rag import RAGSwarmCoordinator`

### **"Quality score is always low"**
- Check that your vector store has sufficient documents indexed
- Try uploading more relevant documents
- Verify embeddings are initialized

### **"Pipeline stages incomplete"**
- Check logs for specific agent failures
- Verify API keys are configured (Gemini)
- Check LangSmith configuration if tracing is enabled

### **"Responses are slow"**
- Normal for Agent Swarm (3-5 seconds is expected)
- Check if re-retrieval is happening (adds 2-3s)
- Consider using Single Agent mode for speed

---

## 📚 **LangSmith Tracing**

### **Viewing Swarm Traces**

If LangSmith is configured:

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Select project: **"ai-dev-agent-rag"**
3. Find your query trace
4. Click to expand the execution tree

### **What You'll See:**

```
Trace: "RAGSwarmCoordinator.execute"
├─ QueryAnalystAgent.execute
│  ├─ LLM: Gemini 2.0 Flash (intent analysis)
│  └─ Output: query_analysis
├─ RetrievalSpecialistAgent.execute
│  ├─ Search #1: original query
│  ├─ Search #2: variant 1
│  ├─ Search #3: variant 2
│  └─ Output: 24 candidates
├─ ReRankerAgent.execute
│  ├─ Deduplication: 24 → 18
│  ├─ Multi-signal scoring
│  └─ Output: Top 10 ranked
├─ QualityAssuranceAgent.execute
│  └─ Output: quality_report (0.85)
└─ WriterAgent.execute
   ├─ LLM: Gemini 2.0 Flash Thinking (synthesis)
   └─ Output: final_response
```

---

## ✅ **Verification Checklist**

Before testing, ensure:

- [ ] RAG system initialized (documents uploaded or codebase indexed)
- [ ] Vector store has data (check "📊 Context Statistics" on home page)
- [ ] Gemini API key configured in `.streamlit/secrets.toml`
- [ ] Debug Mode enabled for full visibility
- [ ] LangSmith configured (optional but recommended)

---

## 🎓 **Example Queries**

### **Good Queries for Agent Swarm:**

1. **Conceptual:**
   - "What is context engineering and how is it implemented in this project?"
   - "Explain the difference between RAG and fine-tuning"

2. **Multi-hop:**
   - "How does the QueryAnalystAgent interact with the RetrievalSpecialistAgent?"
   - "What are the main components of the RAG system and how do they work together?"

3. **Procedural:**
   - "How do I add a new agent to the swarm?"
   - "What steps are involved in the RAG pipeline?"

4. **Comparative:**
   - "Compare the agent swarm approach vs single agent for RAG"
   - "What are the pros and cons of different retrieval strategies?"

---

## 📖 **Related Documentation**

- [RAG Agent Swarm Architecture](../architecture/RAG_AGENT_SWARM_ARCHITECTURE.md)
- [RAG Agent Swarm Implementation](../architecture/RAG_AGENT_SWARM_IMPLEMENTATION.md)
- [How to See RAG Calls](./HOW_TO_SEE_RAG_CALLS.md)
- [RAG LangSmith Integration](../architecture/RAG_LANGSMITH_INTEGRATION.md)

---

## 🚀 **Next Steps**

1. **Test with your queries** - Try both modes and compare
2. **Build golden dataset** - Add good queries to "Golden Dataset Management"
3. **Monitor quality scores** - Track improvement over time
4. **Optimize parameters** - Adjust thresholds based on results
5. **Check LangSmith traces** - Understand the full pipeline

---

**Status:** ✅ Fully integrated and ready to use!  
**Last Updated:** 2025-01-08

