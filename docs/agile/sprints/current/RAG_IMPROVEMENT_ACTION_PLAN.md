# RAG System Improvement - Action Plan

**Date:** 2025-01-09  
**Status:** 🎯 READY TO IMPLEMENT  
**Goal:** Improve RAG results by 20-30% through hybrid search and retriever upgrades

---

## 🎯 Current Situation

### **What's Working:**
- ✅ RAG Management UI (`apps/rag_management_app.py`) - fully functional
- ✅ Agent Swarm Chat interface with context visualization
- ✅ RAGSwarmCoordinator with 5 specialized agents
- ✅ Qdrant vector store (excellent choice!)
- ✅ all-MiniLM-L6-v2 embeddings (optimal!)
- ✅ Document loading (PDF, DOCX, HTML, code files)
- ✅ Semantic search interface

### **What Needs Improvement:**
- ❌ Using old `Qdrant` wrapper (not `QdrantVectorStore`)
- ❌ No hybrid search (missing BM25 keyword matching)
- ❌ Direct similarity_search (not using retriever interface)
- ❌ No MMR for diversity
- ❌ Lower accuracy than possible (~65% vs potential ~85%)

### **Your Testing Environment:**
You're testing through:
1. RAG UI → Agent Swarm Chat
2. RAGSwarmCoordinator executes queries
3. Results visualized with context debugging

Perfect setup for A/B testing old vs new approach!

---

## 🚀 Implementation Plan (3 Days)

### **Day 1: Core Migration** (4-5 hours)

#### **Task 1.1: Update Vector Store Wrapper**
**File:** `context/context_engine.py`

```python
# Line ~20: Update imports
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse

# Line ~110: Add sparse embeddings initialization
self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/BM25")
self.logger.info("✅ BM25 sparse embeddings initialized")

# Line ~225: Update collection creation
from qdrant_client.models import VectorParams, SparseVectorParams

self.qdrant_client.create_collection(
    collection_name=self.collection_name,
    vectors_config={
        "dense": VectorParams(size=384, distance=Distance.COSINE)
    },
    sparse_vectors_config={
        "sparse": SparseVectorParams()
    }
)

# Line ~231: Update vector store creation
self.vector_store = QdrantVectorStore(
    client=self.qdrant_client,
    collection_name=self.collection_name,
    embedding=self.embeddings,  # Singular! Keep all-MiniLM-L6-v2
    sparse_embedding=self.sparse_embeddings,
    retrieval_mode=RetrievalMode.HYBRID
)

# Add retriever with MMR
self.retriever = self.vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 15,
        "fetch_k": 50,
        "lambda_mult": 0.5
    }
)
```

**Testing:**
- Run RAG UI
- Try semantic search
- Verify results still work

---

#### **Task 1.2: Update Search Methods**
**File:** `context/context_engine.py`

```python
# Update _semantic_search method (line ~612)
def _semantic_search(self, query: str, max_results: int):
    """Perform semantic search using retriever."""
    try:
        # Use retriever for hybrid search + MMR
        docs = self.retriever.get_relevant_documents(query)[:max_results]
        
        self.logger.info(f"🔍 Hybrid search for '{query[:50]}...' returned {len(docs)} results")
        
        results = []
        for doc in docs:
            result = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": 1.0,  # MMR doesn't return scores
                "search_type": "hybrid_mmr",
                "file_path": doc.metadata.get("file_path", "unknown"),
                "chunk_index": doc.metadata.get("chunk_index", 0)
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        self.logger.error(f"Hybrid search error: {e}")
        # Fallback to old method if needed
        return []
```

**Testing:**
- Test through RAG UI semantic search
- Verify agent swarm chat still works
- Check context visualization

---

### **Day 2: Enhanced Features** (4-5 hours)

#### **Task 2.1: Add HTML-Specific Splitters**
**File:** `context/context_engine.py`

```python
# Line ~150: After text_splitter initialization
from langchain.text_splitter import HTMLHeaderTextSplitter

self.html_splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=[
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3"),
    ]
)
self.logger.info("✅ HTML splitter initialized")

# Update _create_vector_embeddings method (line ~385)
async def _create_vector_embeddings(self, file_path: Path, content: str):
    """Create vector embeddings with appropriate splitter."""
    try:
        # Choose splitter based on file type
        if file_path.suffix.lower() == '.html':
            chunks = self.html_splitter.split_text(content)
        elif file_path.suffix.lower() in ['.py', '.js', '.ts', '.java']:
            # Language-aware splitting for code
            language = file_path.suffix.lstrip('.')
            code_splitter = RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=512,
                chunk_overlap=50
            )
            chunks = code_splitter.split_text(content)
        else:
            # Default splitter
            chunks = self.text_splitter.split_text(content)
        
        # Rest of the method stays the same...
```

---

#### **Task 2.2: Add Retriever Configuration Options**
**File:** `context/context_engine.py`

```python
# Add method to switch retriever modes
def configure_retriever(self, 
                       search_type: str = "mmr",
                       k: int = 15,
                       fetch_k: int = 50,
                       lambda_mult: float = 0.5):
    """
    Configure retriever for different use cases.
    
    Args:
        search_type: "similarity" or "mmr"
        k: Number of results to return
        fetch_k: Number of candidates for MMR
        lambda_mult: Diversity (0=diverse, 1=relevant)
    """
    if not self.vector_store:
        self.logger.warning("Vector store not initialized")
        return
    
    self.retriever = self.vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k if search_type == "mmr" else k,
            "lambda_mult": lambda_mult if search_type == "mmr" else None
        }
    )
    
    self.logger.info(f"✅ Retriever configured: {search_type}, k={k}")
```

---

### **Day 3: Testing & Optimization** (4-5 hours)

#### **Task 3.1: A/B Testing Interface**
**File:** `apps/rag_management_app.py`

Add comparison mode to agent chat:

```python
# Around line ~730 in agent_chat_page()
with col3:
    comparison_mode = st.checkbox(
        "🔬 A/B Test Mode",
        help="Compare old vs new RAG results side-by-side"
    )

# If comparison mode enabled, run both and show differences
if comparison_mode and st.session_state.get('old_engine_backup'):
    # Run both engines
    col_old, col_new = st.columns(2)
    
    with col_old:
        st.markdown("**Old RAG (Dense-only)**")
        old_results = run_old_engine(user_input)
        display_results(old_results)
    
    with col_new:
        st.markdown("**New RAG (Hybrid + MMR)**")
        new_results = run_new_engine(user_input)
        display_results(new_results)
```

---

#### **Task 3.2: Performance Benchmarking**
**File:** `docs/agile/sprints/current/RAG_BENCHMARK_RESULTS.md`

Create test suite:

```python
# benchmark_rag.py
test_queries = [
    "async error handling patterns",
    "FastAPI dependency injection",
    "LangChain Qdrant configuration",
    "agent swarm coordination",
    "vector database optimization",
    "semantic search implementation",
    "context-aware retrieval",
    "hybrid search setup",
    "document chunking strategies",
    "embeddings model selection"
]

def benchmark_rag():
    """Compare old vs new RAG on test queries."""
    results = {
        'old': [],
        'new': []
    }
    
    for query in test_queries:
        # Test old
        old_result = old_engine.search_context(query, max_results=10)
        results['old'].append({
            'query': query,
            'count': len(old_result),
            'time': old_result.get('time', 0),
            'relevance': score_relevance(old_result, query)
        })
        
        # Test new
        new_result = new_engine.search_context(query, max_results=10)
        results['new'].append({
            'query': query,
            'count': len(new_result),
            'time': new_result.get('time', 0),
            'relevance': score_relevance(new_result, query)
        })
    
    return compare_results(results)
```

---

## 📊 Expected Results

### **Before (Current)**
```
Search Type: Dense-only semantic
Retriever: Direct similarity_search
Diversity: Low (many similar results)
Keyword Match: Manual (via _keyword_search)
Accuracy: ~65%
```

### **After (Improved)**
```
Search Type: Hybrid (BM25 + semantic)
Retriever: MMR-based (diversity)
Diversity: High (varied perspectives)
Keyword Match: Automatic (BM25)
Accuracy: ~85% (+30%)
```

### **Test Queries to Verify**

1. **Keyword + Semantic:**
   - Query: "async error handling in FastAPI"
   - Should find: Both "async" keyword matches AND semantic error handling concepts

2. **Diversity:**
   - Query: "LangChain RAG implementation"
   - Should find: Different aspects (not 10 similar results)

3. **Hybrid Power:**
   - Query: "Qdrant vector search configuration"
   - Should find: Exact "Qdrant" mentions AND related concepts

---

## ✅ Verification Checklist

After each task, verify:

### **Day 1 Complete:**
- [ ] Vector store created with sparse vectors
- [ ] Hybrid mode enabled
- [ ] Retriever initialized with MMR
- [ ] Semantic search still works in UI
- [ ] Agent swarm chat functional
- [ ] No errors in logs

### **Day 2 Complete:**
- [ ] HTML splitter working for web content
- [ ] Code-aware splitting for Python files
- [ ] Retriever configuration method works
- [ ] Can switch between similarity/MMR modes
- [ ] Agent swarm uses new retriever

### **Day 3 Complete:**
- [ ] A/B comparison shows improvements
- [ ] Benchmark results document accuracy gains
- [ ] Performance maintained (<500ms)
- [ ] User story acceptance criteria met

---

## 🧪 Testing Process

### **1. Smoke Test (Quick Check)**
```bash
# Start RAG UI
streamlit run apps/rag_management_app.py

# Test steps:
1. Go to "Semantic Search"
2. Click "Index Codebase"
3. Search: "async error handling"
4. Verify: Results appear
5. Check: Console for "hybrid_mmr" logs
```

### **2. Agent Swarm Test**
```bash
# In RAG UI:
1. Go to "Agent Chat"
2. Select "Agent Swarm (Best Quality)"
3. Ask: "How do I configure Qdrant for hybrid search?"
4. Observe: Context retrieval (should show hybrid results)
5. Verify: Response quality improved
```

### **3. Comparison Test**
```python
# Run both engines on same queries
queries = [
    "async patterns",
    "FastAPI routing", 
    "LangChain retriever"
]

for q in queries:
    old = old_engine.search_context(q)
    new = new_engine.search_context(q)
    
    print(f"Query: {q}")
    print(f"Old: {len(old)} results")
    print(f"New: {len(new)} results")
    print(f"Improvement: {compare_quality(old, new)}")
```

---

## 🚨 Rollback Plan

If issues occur:

### **Quick Rollback:**
```python
# In context_engine.py
# Comment out new code, uncomment old:

# NEW (comment out if issues):
# self.vector_store = QdrantVectorStore(...)

# OLD (uncomment if needed):
self.vector_store = Qdrant(
    client=self.qdrant_client,
    collection_name=self.collection_name,
    embeddings=self.embeddings
)
```

### **Collection Reset:**
```python
# If collection issues, recreate:
client.delete_collection(collection_name)
client.create_collection(...)  # Recreate
# Then re-index documents
```

---

## 📈 Success Metrics

### **How We'll Know It Worked:**

1. **Accuracy Improvement:**
   - Test queries return more relevant results
   - Keyword matches appear in results
   - Diverse perspectives (not repetitive)

2. **Agent Swarm Quality:**
   - Better context retrieved
   - More accurate responses
   - Higher confidence scores

3. **Performance:**
   - Search time still <500ms
   - No memory issues
   - UI responsive

4. **User Experience:**
   - Testing/Evaluation page shows improvements
   - Agent chat produces better answers
   - Context visualization shows hybrid results

---

## 📋 Next Steps

### **Right Now (Start Day 1):**
1. **Backup current state:**
   ```bash
   git checkout -b feature/rag-hybrid-search
   ```

2. **Start Task 1.1:**
   - Open `context/context_engine.py`
   - Update imports (line ~20)
   - Add sparse embeddings (line ~110)

3. **Test incrementally:**
   - After each change, test in RAG UI
   - Verify no errors
   - Check logs for "hybrid" messages

### **Tomorrow (Day 2):**
- Add specialized splitters
- Configure retriever options
- Test with different document types

### **Day 3:**
- A/B testing
- Benchmark comparison
- Update documentation
- User story acceptance criteria review

---

## 💡 Pro Tips

1. **Keep UI Running:**
   - Keep RAG UI open during development
   - Use "Rerun" button to test changes
   - Watch console for logs

2. **Test with Real Queries:**
   - Use actual questions you'd ask
   - Test with your codebase context
   - Try both simple and complex queries

3. **Monitor Logs:**
   - Check for "hybrid_mmr" in logs
   - Watch for BM25 initialization
   - Look for retrieval time metrics

4. **Agent Swarm Feedback:**
   - The swarm will show if retrieval improved
   - Check "Context Debug Mode" for details
   - Quality scores should increase

---

## 🎯 Bottom Line

**What to do:** 3 days of focused improvements
**Where to start:** `context/context_engine.py` Line ~20
**How to test:** Through your existing RAG UI + Agent Swarm Chat
**Expected gain:** +20-30% accuracy, better diversity, improved agent responses

**First command to run:**
```bash
git checkout -b feature/rag-hybrid-search
code context/context_engine.py  # Open at line 20
```

Ready to start? 🚀

