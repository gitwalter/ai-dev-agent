# RAG Integration Strategy

**Date:** 2025-01-02  
**Status:** Planning Phase  
**Priority:** HIGH

---

## 🎯 **Current Situation**

### ✅ **What We Have**

1. **ContextEngine (Our RAG System!)**
   ```python
   # context/context_engine.py - Already has everything!
   class ContextEngine:
       - semantic_search()           # ✅ Async semantic search
       - index_codebase()            # ✅ Index files
       - search_context()            # ✅ Hybrid search (semantic + keyword)
       - get_context_for_file()      # ✅ File-specific context
       - get_import_suggestions()    # ✅ Pattern-based suggestions
       - get_error_solutions()       # ✅ Error memory
       - get_project_intelligence_summary()  # ✅ Project analysis
       
       # Already integrated with:
       - FAISS vector store
       - HuggingFace embeddings
       - LangChain Document objects
       - Text chunking & metadata
       - Pattern learning
   ```

2. **Document Loading System** (NEW!)
   - `utils/rag/document_loader.py` - LangChain-based loaders
   - PDF, DOCX, TXT, MD, HTML, code files
   - Website scraping with WebBaseLoader
   - Batch processing with progress tracking
   - Streamlit UI for management

3. **Agent Infrastructure**
   - BaseAgent → EnhancedBaseAgent hierarchy
   - MCPEnhancedAgent with tool integration
   - SwarmCoordinator for multi-agent workflows
   - Universal Agent Tracker for monitoring

4. **MCP Infrastructure** 
   - MCP server and client
   - Tool registry and execution
   - MCPAgentMixin for agent integration
   - Security and access control

### ❌ **What's Missing**

1. **ContextEngine Integration into Agents**
   - Agents don't have ContextEngine access
   - No standardized way to pass ContextEngine to agents
   - No LangChain retriever wrapper for ContextEngine

2. **Cursor MCP Integration**
   - No MCP server exposure for Cursor
   - ContextEngine not exposed via MCP
   - No semantic search from Cursor IDE

---

## 🚀 **Integration Strategy**

### **Path 1: ContextEngine Integration for Internal Agents**

**Goal:** All agents in `/agents/` directory can access ContextEngine for context retrieval

#### **Implementation Approach**

```python
# Add ContextEngine to Enhanced Base Agent
from context.context_engine import ContextEngine
from models.config import ContextConfig

class ContextAwareAgent(EnhancedBaseAgent):
    """Agent with built-in ContextEngine access."""
    
    def __init__(self, config, context_engine=None):
        super().__init__(config)
        
        # Use provided ContextEngine or create new one
        if context_engine:
            self.context_engine = context_engine
        else:
            # Create default ContextEngine
            context_config = ContextConfig()
            self.context_engine = ContextEngine(context_config)
        
        # Create LangChain retriever from vector store
        self.retriever = None
        if self.context_engine.vector_store:
            self.retriever = self.context_engine.vector_store.as_retriever(
                search_kwargs={"k": 5}
            )
    
    async def execute_with_context(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with ContextEngine retrieval."""
        
        # 1. Use ContextEngine's semantic_search
        query = task.get('query', '') or task.get('description', '')
        search_results = await self.context_engine.semantic_search(query, limit=5)
        
        # 2. Get additional context features
        context_data = {
            'search_results': search_results.get('results', []),
            'import_suggestions': self.context_engine.get_import_suggestions(
                task.get('file_path', '')
            ),
            'project_intelligence': self.context_engine.get_project_intelligence_summary()
        }
        
        # 3. Enhance task with rich context
        enhanced_task = {
            **task,
            'context': context_data,
            'has_context': True
        }
        
        # 4. Execute with enhanced context
        return await self.execute(enhanced_task)
    
    async def get_relevant_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context for a query."""
        return await self.context_engine.semantic_search(query, limit=5)
    
    def get_file_context(self, file_path: str) -> Optional[str]:
        """Get context for specific file."""
        return self.context_engine.get_context_for_file(file_path)
```

#### **Benefits**
- ✅ Uses existing ContextEngine (no duplication!)
- ✅ Access to ALL ContextEngine features
- ✅ Pattern learning, error solutions, intelligence
- ✅ Already tested and working
- ✅ LangChain compatible (FAISS retriever)

---

### **Path 2: Cursor MCP Integration (MCP Server)**

**Goal:** Cursor can access our RAG system via MCP for semantic search and context

#### **Implementation Approach (Based on Cursor MCP Docs)**

According to [Cursor MCP documentation](https://cursor.com/docs/context/mcp):

**MCP (Model Context Protocol)** allows Cursor to connect to external context sources. We need to:

1. **Create MCP Server Configuration**
   ```json
   // .cursor/mcp_config.json
   {
     "mcpServers": {
       "ai-dev-agent-rag": {
         "command": "python",
         "args": ["-m", "utils.mcp.cursor_rag_server"],
         "env": {
           "PYTHONPATH": "${workspaceFolder}"
         }
       }
     }
   }
   ```

2. **Build Cursor-Compatible MCP Server**
   ```python
   # utils/mcp/cursor_rag_server.py
   """
   MCP Server for Cursor Integration
   =================================
   
   Exposes RAG system to Cursor IDE via Model Context Protocol.
   """
   
   from mcp import Server, Tool
   from context.context_engine import ContextEngine
   from models.config import ContextConfig
   
   class CursorContextServer:
       """MCP server exposing ContextEngine to Cursor."""
       
       def __init__(self):
           self.server = Server("ai-dev-agent-context")
           
           # Initialize ContextEngine (our RAG system!)
           context_config = ContextConfig()
           self.context_engine = ContextEngine(context_config)
           
           # Index codebase on startup
           import asyncio
           asyncio.run(self.context_engine.index_codebase('.'))
           
           # Register tools
           self.register_tools()
       
       def register_tools(self):
           """Register ContextEngine tools for Cursor."""
           
           @self.server.tool()
           async def semantic_search(query: str, limit: int = 5) -> dict:
               """Search indexed codebase and documents using semantic search."""
               results = await self.context_engine.semantic_search(query, limit)
               return {
                   "results": results.get('results', []),
                   "search_type": results.get('search_type'),
                   "sources": [r.get('file_path') for r in results.get('results', [])]
               }
           
           @self.server.tool()
           async def get_file_context(file_path: str) -> dict:
               """Get context for specific file from ContextEngine."""
               context = self.context_engine.get_context_for_file(file_path)
               return {"context": context, "file_path": file_path}
           
           @self.server.tool()
           async def get_import_suggestions(file_path: str) -> dict:
               """Get import suggestions based on learned patterns."""
               suggestions = self.context_engine.get_import_suggestions(file_path)
               return {"suggestions": suggestions, "file_path": file_path}
           
           @self.server.tool()
           async def get_error_solution(error_message: str) -> dict:
               """Get solution suggestions for error message."""
               solutions = self.context_engine.get_error_solutions(error_message)
               return {"solutions": solutions, "error": error_message}
           
           @self.server.tool()
           async def get_project_intelligence() -> dict:
               """Get project intelligence summary from ContextEngine."""
               intelligence = self.context_engine.get_project_intelligence_summary()
               return intelligence
           
           @self.server.tool()
           async def get_codebase_summary() -> dict:
               """Get codebase summary statistics."""
               summary = self.context_engine.get_codebase_summary()
               return summary
       
       def run(self):
           """Run the MCP server for Cursor."""
           self.server.run()
   
   if __name__ == "__main__":
       server = CursorContextServer()
       server.run()
   ```

3. **How Cursor Uses It**
   - Cursor runs our MCP server as subprocess
   - When user asks question, Cursor can call `semantic_search`
   - Results appear as context in Cursor's AI responses
   - Automatic context injection for relevant code

#### **Benefits**
- ✅ Cursor gets semantic search access
- ✅ Automatic context enhancement
- ✅ No manual context copying
- ✅ Real-time codebase knowledge

---

## 📋 **Implementation Plan**

### **Phase 1: LangChain RAG for Agents** (Week 1)

**Stories:**
1. **US-RAG-AGENT-001: RAG-Enabled Base Agent**
   - Create `RAGEnabledAgent` base class
   - Integrate LangChain retrievers
   - Add QA chain support
   - **Points:** 8

2. **US-RAG-AGENT-002: Update Existing Agents**
   - Migrate agents to RAG-enabled base
   - Add RAG context to execution
   - Test with real documents
   - **Points:** 13

### **Phase 2: Cursor MCP Server** (Week 2)

**Stories:**
3. **US-RAG-MCP-001: Build Cursor MCP Server**
   - Implement `cursor_rag_server.py`
   - Register RAG tools
   - Add stdio communication
   - **Points:** 13

4. **US-RAG-MCP-002: Cursor Configuration**
   - Create MCP config for Cursor
   - Test Cursor integration
   - Document usage
   - **Points:** 5

### **Phase 3: Advanced Features** (Week 3)

**Stories:**
5. **US-RAG-ADV-001: Contextual Compression**
   - Add compression retriever
   - Optimize token usage
   - **Points:** 5

6. **US-RAG-ADV-002: Multi-Query Retrieval**
   - Implement query expansion
   - Better search results
   - **Points:** 5

---

## 🎯 **Success Metrics**

### **Agent Integration**
- ✅ All agents can access RAG
- ✅ Context retrieval < 500ms
- ✅ Relevant results > 90%

### **Cursor Integration**
- ✅ Cursor can search codebase
- ✅ Automatic context injection
- ✅ Real-time updates

---

## 🤔 **Decision Points**

### **Question 1: Which Path First?**

**Option A: Agents First**
- **Pros:** More control, easier testing, LangChain standard
- **Cons:** No immediate Cursor benefit
- **Recommendation:** ✅ **START HERE**

**Option B: Cursor First**
- **Pros:** Immediate IDE benefit, cool demo
- **Cons:** Depends on Cursor MCP implementation, less tested
- **Recommendation:** ⏳ **DO SECOND**

### **Question 2: LangChain vs Custom?**

**LangChain Standard RAG**
- **Pros:** Well-tested, documented, community support
- **Cons:** Less customization
- **Recommendation:** ✅ **USE FOR AGENTS**

**Custom RAG Integration**
- **Pros:** Full control, optimized
- **Cons:** More work, maintenance burden  
- **Recommendation:** ❌ **AVOID**

---

## 💡 **Recommended Next Steps**

### **CRITICAL INSIGHT: We Already Have RAG!**

Our **ContextEngine IS our RAG system**! We don't need to build a separate RAG system. We just need to:

1. **Connect ContextEngine to agents** (agents/core/)
2. **Expose ContextEngine via MCP to Cursor** (utils/mcp/)
3. **Keep using document loaders** to feed ContextEngine (utils/rag/)

### **TODAY** (2-3 hours)
1. ✅ Create `ContextAwareAgent` base class (extends EnhancedBaseAgent)
2. ✅ Add ContextEngine integration
3. ✅ Test with one agent (e.g., `SwarmCoordinator`)

### **THIS WEEK** (5 days)
1. Migrate existing agents to use ContextAwareAgent
2. Add context-aware execution patterns
3. Build comprehensive tests
4. Document ContextEngine usage for agents

### **NEXT WEEK** (5 days)
1. Build `CursorContextServer` (MCP server)
2. Configure Cursor to use our MCP server
3. Test semantic search from Cursor
4. Create user documentation

---

## 🎬 **Agile Decision Time**

### **What Should We Do RIGHT NOW?**

**Option 1: Build ContextAwareAgent** ✅ **RECOMMENDED**
- **Time:** 2-3 hours
- **Value:** Immediate - all agents get semantic search
- **Risk:** Low - ContextEngine already works
- **Implementation:**
  1. Create `agents/core/context_aware_agent.py`
  2. Extend `EnhancedBaseAgent` with ContextEngine
  3. Add `execute_with_context()` method
  4. Test with one existing agent

**Option 2: Build Cursor MCP Server**
- **Time:** 3-4 hours
- **Value:** High - Cursor gets semantic search
- **Risk:** Medium - depends on Cursor MCP implementation
- **Dependencies:** Need to verify Cursor MCP support first

**Option 3: Both in Parallel**
- **Time:** 5-6 hours
- **Value:** Maximum
- **Risk:** Higher complexity
- **Approach:** Build ContextAwareAgent first, then Cursor server

---

## 🎯 **My Strong Recommendation**

### **Do Option 1 First - Build ContextAwareAgent**

**Why?**
1. ✅ **ContextEngine is already working** - we tested it!
2. ✅ **Foundation for everything** - agents need context to be smart
3. ✅ **Uses existing code** - no duplication, leverages ContextEngine
4. ✅ **Easy to test** - we have agents, we have ContextEngine
5. ✅ **Immediate value** - smarter agents right away

**Then Option 2 - Cursor MCP Server**

**Why Second?**
1. ✅ **Depends on agents working** - better to have working pattern first
2. ✅ **Need to verify Cursor MCP** - documentation might be incomplete
3. ✅ **Can test independently** - once agents work, Cursor is bonus

---

## 📝 **Summary: The Simple Truth**

**We have everything we need:**
- ✅ ContextEngine = Our RAG system
- ✅ Document loaders = Feed the RAG
- ✅ Streamlit UI = Manage the RAG
- ✅ Agents = Need ContextEngine access
- ✅ MCP = Can expose to Cursor

**We just need to connect the pieces!**

**Shall we start building ContextAwareAgent?** 🚀

