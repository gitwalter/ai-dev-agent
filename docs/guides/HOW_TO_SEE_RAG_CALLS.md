# How to See RAG Calls in Action

**Created:** 2025-01-08  
**Purpose:** Guide to visualizing multi-stage RAG retrieval  
**Audience:** Developers testing the RAG system

---

## 🎯 **Quick Answer**

There are **3 ways** to see the RAG system's multi-stage retrieval:

1. ✅ **RAG UI Testing Page** (BEST for transparency)
2. ✅ **Agent Chat with Debug Mode** (Real-time visualization)
3. ✅ **LangSmith Dashboard** (Complete traces)

---

## 📊 **Method 1: RAG UI Testing Page** (RECOMMENDED)

### **Where:** `🧪 Testing & Evaluation` tab in RAG Management App

### **What You'll See:**

```
🔍 Transparency Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ Retrieval Time    📄 Results Found    🔍 Search Type    ✅ Success
   425ms                   12              Multi-Stage       Yes

💬 Generated Response
[Your LLM-generated answer appears here]

🔍 Retrieved Context Details (Expanded)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retrieved 12 context chunks:

Result #1
Content Preview: [First 300 chars of retrieved text...]
Score: 0.892
  Semantic: 0.85
  Keyword: 0.92
  Quality: 0.90
  Diversity: 0.88

Result #2
[... and so on ...]

⚙️ Processing Pipeline (Expanded)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Searches Performed: 4

[Query Rewriting]
[Multi-Stage Retrieval]
[Deduplication]
[Multi-Signal Re-ranking]
[Position Optimization]
[LLM Generation]
```

### **How to Use:**

1. Start the RAG UI:
   ```bash
   streamlit run apps/rag_management_app.py --server.port 8510
   ```

2. Navigate to **"🧪 Testing & Evaluation"** tab

3. Enter a test query (e.g., "What is context engineering?")

4. Click **"🚀 Run Test"**

5. Expand **"🔍 Retrieved Context Details"** to see all search results with scores

6. Expand **"⚙️ Processing Pipeline"** to see which stages were executed

---

## 💬 **Method 2: Agent Chat with Debug Mode**

### **Where:** `💬 Agent Chat` tab in RAG Management App

### **What You'll See:**

```
[User Message]
What is context engineering?

[Agent Response]
Context engineering is the art of...

📊 Context Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ Retrieval Time: 412ms
📄 Results Found: 12
🔍 Search Type: Multi-Stage

🔍 Context Debug Panel (If Debug Mode ON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Quality Metrics
  Average Relevance: 0.78
  Context Diversity: 0.85

🔎 Retrieval Details
  Total Searches: 4
  Total Results: 18 (deduplicated to 12)
  Query Variants: 3

📊 Agent Statistics
  Searches Performed: 4
  Total Context Time: 0.412s
```

### **How to Use:**

1. Navigate to **"💬 Agent Chat"** tab

2. **Enable Debug Mode** (checkbox at top)

3. Adjust **Context Detail Level** slider to "Debug"

4. Ask your question

5. After response, you'll see:
   - Context statistics
   - Debug panel (if enabled)
   - Quality metrics
   - Full retrieval breakdown

---

## 🌐 **Method 3: LangSmith Dashboard**

### **Where:** [https://smith.langchain.com/](https://smith.langchain.com/)

### **Setup:**

Add to `.streamlit/secrets.toml`:
```toml
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_API_KEY = "your-api-key"
LANGCHAIN_PROJECT = "ai-dev-agent-rag"
```

### **What You'll See in LangSmith:**

```
Trace: "ContextAwareAgent Query"
├─ Input: "What is context engineering?"
├─ Context Retrieval
│  ├─ Query Rewriting (3 variants)
│  ├─ Search #1: original query → 5 results
│  ├─ Search #2: variant 1 → 5 results  
│  ├─ Search #3: variant 2 → 5 results
│  ├─ Search #4: variant 3 → 5 results
│  └─ Deduplication: 18 → 12 unique results
├─ LLM Call: ChatGoogleGenerativeAI
│  ├─ Prompt: [Full prompt with context]
│  ├─ Tokens: 1,245 input / 387 output
│  ├─ Latency: 2,134ms
│  └─ Response: [Full response text]
└─ Output: [Final answer]
```

### **How to Use:**

1. Verify LangSmith is enabled in **"⚙️ System Settings"** page

2. Run any query in RAG UI

3. Go to [smith.langchain.com](https://smith.langchain.com/)

4. Click on your project: **"ai-dev-agent-rag"**

5. Click on the latest trace

6. Expand the execution tree to see:
   - All context retrieval calls
   - Full prompts with retrieved context
   - LLM responses
   - Token usage
   - Timing for each stage

---

## 🔍 **What the Multi-Stage RAG Does**

When you ask a question, the system performs:

### **Stage 1: Query Rewriting** ✏️
```python
Original: "What is context engineering?"
Variant 1: "Define context engineering in AI"
Variant 2: "Context engineering techniques and practices"
Variant 3: "How does context engineering work"
```

### **Stage 2: Multi-Search Retrieval** 🔎
```
Search with original query    → 5 results
Search with variant 1         → 5 results
Search with variant 2         → 5 results
Search with variant 3         → 5 results
─────────────────────────────────────────
Total retrieved: 20 results
```

### **Stage 3: Deduplication** 🔀
```
20 results → Check similarity
→ Remove duplicates
→ 12 unique results
```

### **Stage 4: Multi-Signal Re-ranking** 📊
For each result, calculate:
- **Semantic Score** (0.0-1.0): Vector similarity
- **Keyword Score** (0.0-1.0): Query term matches
- **Quality Score** (0.0-1.0): Content completeness
- **Diversity Score** (0.0-1.0): Uniqueness from others

```python
Combined Score = (
    0.40 × semantic_score +
    0.25 × keyword_score +
    0.20 × quality_score +
    0.15 × diversity_score
)
```

### **Stage 5: Position Optimization** 🎯
```
Top results → Front of context
Medium results → Middle
Lower results → End or excluded
```

### **Stage 6: LLM Generation** 🤖
```
Prompt = System Message + Query + Ranked Context
→ Send to Gemini
→ Generate response
```

---

## 📝 **Logs You'll See in Console**

When running the RAG system, you'll see these logs:

```bash
INFO - 🔄 Query rewriting: 3 variants generated
INFO - 🔍 ContextAwareAgent: Found 5 results for 'What is context engineering?'
INFO - 🔍 ContextAwareAgent: Found 5 results for 'Define context engineering in AI'
INFO - 🔍 ContextAwareAgent: Found 5 results for 'Context engineering techniques'
INFO - 🔍 ContextAwareAgent: Found 5 results for 'How does context engineering work'
INFO - 🔀 Deduplication: 20 → 12 unique results
INFO - 📊 Multi-signal re-ranking: Top score 0.892, Avg 0.714
INFO - 🎯 Final context prepared: 12 results, avg score 0.714
INFO - 🤖 ContextAwareAgent: Executing task with LLM...
INFO - 🤖 ContextAwareAgent: Task completed successfully
```

---

## 🎯 **Quick Test Commands**

### **Test RAG UI:**
```bash
# Activate environment
C:\App\Anaconda\Scripts\activate.bat base

# Start RAG UI
streamlit run apps/rag_management_app.py --server.port 8510

# Navigate to: http://localhost:8510
# Go to "🧪 Testing & Evaluation" tab
# Enter query and click "Run Test"
```

### **Check Logs in Real-Time:**
```bash
# Windows PowerShell
Get-Content logs/agent.log -Wait -Tail 50

# Or view specific RAG logs
Get-Content logs/agent.log | Select-String "ContextAwareAgent"
```

---

## 🎨 **Understanding the Scores**

### **High Relevance (0.7-1.0)** 🟢
- Strong semantic match to query
- High keyword overlap
- Quality content
- Unique information

### **Medium Relevance (0.4-0.7)** 🟡
- Moderate semantic match
- Some keyword overlap
- Acceptable quality
- May have some overlap with other results

### **Low Relevance (0.0-0.4)** 🔴
- Weak semantic match
- Low keyword overlap
- Lower quality or incomplete
- Highly similar to other results

---

## ✅ **Verification Checklist**

To verify multi-stage RAG is working:

- [ ] See multiple searches in logs (usually 3-4)
- [ ] See "Query rewriting: X variants generated"
- [ ] See "Deduplication: X → Y unique results"
- [ ] See "Multi-signal re-ranking" log
- [ ] See scoring breakdown in UI (Semantic, Keyword, Quality, Diversity)
- [ ] See "Searches Performed: 4" in context stats
- [ ] See varied content in retrieved results (not duplicates)

---

## 🚀 **Next Steps**

1. **Test with different queries** to see how retrieval adapts
2. **Enable Debug Mode** in Agent Chat for detailed stats
3. **Check LangSmith** for complete execution traces
4. **Build Golden Dataset** in Testing page for systematic evaluation

---

**Pro Tip:** Use the **Testing & Evaluation** page for initial development and debugging, then rely on **LangSmith** for production monitoring and optimization.

