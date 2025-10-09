# RAG System LangSmith Integration

**Created:** 2025-01-08  
**Purpose:** Document LangSmith tracing integration for RAG system  
**Status:** ✅ COMPLETE

---

## 🎯 **Overview**

The RAG system now uses LangChain's `ChatGoogleGenerativeAI` for automatic LangSmith tracing. This means **all LLM calls are automatically logged to LangSmith** without custom tracking code.

---

## 🔍 **How It Works**

### **1. LangChain Integration**

The `ContextAwareAgent` now uses LangChain's `ChatGoogleGenerativeAI`:

```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Create LLM with automatic LangSmith tracing
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=api_key,
    temperature=0.7,
    convert_system_message_to_human=True
)

# Invoke - automatically traced to LangSmith
messages = [
    SystemMessage(content="You are a helpful AI assistant..."),
    HumanMessage(content=prompt)
]

response = await llm.ainvoke(messages)
```

**Benefits:**
- ✅ **Automatic tracing** - No custom tracking code needed
- ✅ **Full transparency** - All prompts, responses, tokens visible in LangSmith
- ✅ **Performance metrics** - Latency, token usage automatically tracked
- ✅ **Error tracking** - Failures and retries logged automatically
- ✅ **Cost tracking** - Token usage for cost estimation

### **2. Configuration**

Add to `.streamlit/secrets.toml`:

```toml
# LangSmith Configuration
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_API_KEY = "your-langsmith-api-key-here"
LANGCHAIN_PROJECT = "ai-dev-agent-rag"
```

The RAG UI automatically loads these and sets environment variables.

### **3. What Gets Traced**

When you use the RAG system, LangSmith automatically logs:

1. **RAG Query Processing**
   - Original user query
   - Query rewriting variants
   - Key concept extraction

2. **Context Retrieval**
   - Semantic search results
   - Retrieved document chunks
   - Relevance scores

3. **LLM Generation**
   - Full prompt with context
   - System message
   - LLM response
   - Token usage
   - Latency

4. **End-to-End Trace**
   - Complete flow from query → retrieval → generation → response
   - Time spent in each stage
   - Any errors or retries

---

## 📊 **Viewing Traces**

### **Access LangSmith Dashboard**

🔗 **[https://smith.langchain.com/](https://smith.langchain.com/)**

### **What You'll See**

1. **Project: ai-dev-agent-rag**
   - All RAG queries listed chronologically
   
2. **Individual Traces**
   - Full execution tree
   - Input (user query + context)
   - Output (LLM response)
   - Metadata (tokens, latency, model)

3. **Performance Metrics**
   - Average response time
   - Token usage trends
   - Success/error rates
   - Cost estimates

---

## 🧪 **Testing with LangSmith**

### **In the RAG UI**

1. Navigate to **"🧪 Testing & Evaluation"** page
2. Enter a test query
3. Click **"🚀 Run Test"**
4. Go to LangSmith dashboard to see the trace

### **In Agent Chat**

1. Navigate to **"💬 Agent Chat"** page
2. Ask any question
3. Check LangSmith for complete trace including:
   - Query rewriting
   - Multi-stage retrieval
   - Context deduplication
   - LLM generation with full prompt

---

## 🎨 **Transparency Features**

### **Removed Custom Tracking**

We **removed** custom tracking code because LangSmith provides:
- ✅ Better visualization
- ✅ Standard format
- ✅ No maintenance overhead
- ✅ Industry-standard tooling

### **Kept for UI Transparency**

We **kept** these for in-app visualization:
- Query variants (query rewriting stage)
- Retrieved context chunks with scores
- Multi-signal scoring breakdown
- Processing pipeline stages

**Why?** Users testing in the UI need immediate feedback without switching to LangSmith.

---

## 🔧 **Implementation Details**

### **File: `agents/core/context_aware_agent.py`**

```python
async def _call_gemini(self, prompt: str) -> str:
    """
    Call Gemini API with LangChain for automatic LangSmith tracing.
    """
    if LANGCHAIN_AVAILABLE:
        # Use LangChain - automatically traced
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.7
        )
        
        messages = [
            SystemMessage(content="You are a helpful AI assistant..."),
            HumanMessage(content=prompt)
        ]
        
        response = await llm.ainvoke(messages)
        return response.content
    else:
        # Fallback to direct API (no tracing)
        # ... direct genai call ...
```

### **File: `apps/rag_management_app.py`**

```python
# Enable LangSmith tracing from secrets
try:
    if 'LANGCHAIN_TRACING_V2' in st.secrets:
        os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets['LANGCHAIN_TRACING_V2'])
    if 'LANGCHAIN_API_KEY' in st.secrets:
        os.environ['LANGCHAIN_API_KEY'] = st.secrets['LANGCHAIN_API_KEY']
    if 'LANGCHAIN_PROJECT' in st.secrets:
        os.environ['LANGCHAIN_PROJECT'] = st.secrets['LANGCHAIN_PROJECT']
except Exception:
    pass  # Fallback to environment variables
```

---

## ✅ **Verification Checklist**

To verify LangSmith integration is working:

- [ ] Added LangSmith API key to `.streamlit/secrets.toml`
- [ ] Set `LANGCHAIN_TRACING_V2 = "true"`
- [ ] Started RAG UI (`streamlit run apps/rag_management_app.py`)
- [ ] Ran a test query in "Agent Chat" or "Testing & Evaluation"
- [ ] Checked LangSmith dashboard at https://smith.langchain.com/
- [ ] Verified trace appears with full prompt/response
- [ ] Confirmed token usage and latency metrics visible

---

## 🎯 **Benefits Summary**

| Feature | Before | After (with LangSmith) |
|---------|--------|------------------------|
| **Tracing** | Custom logging | ✅ Automatic LangChain tracing |
| **Visibility** | Local logs only | ✅ Web dashboard with search |
| **Metrics** | Manual calculation | ✅ Auto token/latency tracking |
| **Debugging** | Text logs | ✅ Visual execution tree |
| **Cost Tracking** | Manual | ✅ Automatic token-based |
| **Sharing** | Export logs | ✅ Share dashboard links |
| **Maintenance** | Custom code | ✅ Zero maintenance |

---

## 📚 **Related Documentation**

- [RAG Best Practices 2025](./RAG_BEST_PRACTICES_2025.md)
- [LangSmith Tracing Guide](../guides/observability/langsmith_tracing_guide.md)
- [Context Engineering Research](../research/MCP_CONTEXT_ENGINEERING_2025.md)

---

**Status:** ✅ Complete and Production Ready  
**Last Updated:** 2025-01-08

