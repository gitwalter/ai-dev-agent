# ContextEngine and Agents Analysis

**Created:** 2025-01-08  
**Sprint:** MCP & RAG Integration  
**Status:** Analysis Complete

---

## 🔍 **Analysis Summary**

Our project already has a sophisticated RAG system (ContextEngine) and a well-structured agent hierarchy. We need to **connect** them, not build new infrastructure.

---

## 📊 **What We Have: ContextEngine**

### **Location:** `context/context_engine.py`

### **Key Features:**
```python
class ContextEngine:
    # Core RAG Capabilities
    - semantic_search()              # ✅ FAISS + HuggingFace embeddings
    - index_codebase()               # ✅ Indexes .py, .md, .yaml, .json, .toml
    - search_context()               # ✅ Hybrid (semantic + keyword)
    
    # Intelligence Features  
    - get_context_for_file()         # ✅ File-specific context
    - get_import_suggestions()       # ✅ Pattern-based suggestions
    - get_error_solutions()          # ✅ Error memory
    - get_project_intelligence_summary()  # ✅ Project analysis
    - get_codebase_summary()         # ✅ Statistics
    
    # Advanced Features
    - _extract_python_metadata()     # ✅ Extracts functions, classes, imports
    - _extract_markdown_metadata()   # ✅ Extracts headings, code blocks
    - _learn_import_patterns()       # ✅ Pattern learning
    - _learn_from_git_history()      # ✅ Git-based learning
```

### **Technical Details:**

**Embeddings:**
- Primary: HuggingFace `all-MiniLM-L6-v2` (free, local, fast)
- Fallback: OpenAI embeddings (if available)
- No API keys required for HuggingFace

**Vector Store:**
- FAISS (Facebook AI Similarity Search)
- Efficient similarity search
- Already integrated with LangChain

**Text Chunking:**
- RecursiveCharacterTextSplitter
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Separators: paragraph, line, space

**File Support:**
- Python (.py): Extracts functions, classes, imports, decorators
- Markdown (.md): Extracts headings, code blocks, document types
- Config (.yaml, .json, .toml): Full text indexing
- Robust encoding detection: UTF-8, Latin-1, CP1252, ISO-8859-1

**Performance:**
- Batch processing (50 files per batch)
- Progress tracking during indexing
- Hybrid search (semantic + keyword fallback)
- Relevance scoring for all results

---

## 🤖 **What We Have: Agent Hierarchy**

### **Core Agent Structure:**

```
BaseAgent (abstract)
├── AgentConfig (dataclass)
│   ├── agent_id, agent_type, prompt_template_id
│   ├── model_name, temperature
│   └── performance_monitoring, optimization
│
├── AgentState (dataclass)
│   ├── status, current_task
│   └── performance_metrics
│
└── Core Methods:
    ├── execute() [abstract]
    ├── validate_task() [abstract]
    ├── run() [lifecycle management]
    ├── get_optimized_prompt()
    ├── generate_response()
    └── parse_json_response()

EnhancedBaseAgent (extends BaseAgent)
├── FileOrganizationMixin
│   ├── create_file() [with auto-organization]
│   └── move_file() [with auto-organization]
│
├── MastersIntegratedAgent
│   ├── apply_masters_principles()
│   └── get_masters_prompt_enhancement()
│
└── Additional Features:
    ├── File organization enforcement
    ├── Compliance reporting
    └── Organization statistics
```

### **Specialized Agents:**

**Development Agents** (`agents/development/`):
- `ArchitectureDesigner`
- `CodeGenerator`
- `CodeReviewer`
- `DocumentationGenerator`
- `RequirementsAnalyst`
- `TestGenerator`

**Management Agents** (`agents/management/`):
- `ProjectManager`
- `SelfOptimizingValidationAgent`

**Security Agents** (`agents/security/`):
- `SecurityAnalyst`
- `EthicalAIProtectionTeam`
- `QuantumResistantEthicalDNACore`

**Research Agent** (`agents/research/`):
- `ComprehensiveResearchAgent`

**MCP Agent** (`agents/mcp/`):
- `MCPEnhancedAgent` (with MCP tool integration)

**Swarm Coordinator** (`agents/swarm/`):
- `SwarmCoordinator` (orchestrates multiple agents)

### **Key Patterns:**

1. **Inheritance Chain:**
   ```python
   BaseAgent → EnhancedBaseAgent → SpecializedAgent
   ```

2. **Mixin Pattern:**
   ```python
   class SpecializedAgent(EnhancedBaseAgent, MCPAgentMixin):
       pass
   ```

3. **Universal Tracking:**
   - All agents register with `UniversalAgentTracker`
   - Logging through `AgentLoggingCoordinator`
   - Performance metrics collection

4. **Prompt Management:**
   - Integration with `PromptTemplateSystem`
   - Optimization through `AdvancedPromptOptimizer`
   - Context-aware prompt generation

---

## 🔌 **Integration Opportunities**

### **1. ContextEngine → BaseAgent Integration**

**Current State:**
- ❌ Agents don't have ContextEngine access
- ❌ No semantic search in agent workflows
- ❌ No pattern learning utilization

**Proposed Integration:**
```python
class ContextAwareAgent(EnhancedBaseAgent):
    """Agent with ContextEngine access."""
    
    def __init__(self, config, gemini_client=None, context_engine=None):
        super().__init__(config, gemini_client)
        
        # Use provided ContextEngine or create new one
        self.context_engine = context_engine or self._create_context_engine()
        
        # Create LangChain retriever for advanced RAG patterns
        self.retriever = None
        if self.context_engine.vector_store:
            self.retriever = self.context_engine.vector_store.as_retriever(
                search_kwargs={"k": 5}
            )
    
    def _create_context_engine(self):
        """Create default ContextEngine instance."""
        from context.context_engine import ContextEngine
        from models.config import ContextConfig
        return ContextEngine(ContextConfig())
    
    async def execute_with_context(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with ContextEngine retrieval."""
        
        # 1. Extract query from task
        query = task.get('query', '') or task.get('description', '')
        
        # 2. Use ContextEngine's semantic_search
        context_results = await self.context_engine.semantic_search(query, limit=5)
        
        # 3. Get additional intelligence
        file_path = task.get('file_path', '')
        intelligence = {
            'search_results': context_results.get('results', []),
            'file_context': self.context_engine.get_context_for_file(file_path) if file_path else None,
            'import_suggestions': self.context_engine.get_import_suggestions(file_path) if file_path else [],
            'project_intelligence': self.context_engine.get_project_intelligence_summary()
        }
        
        # 4. Enhance task with context
        enhanced_task = {
            **task,
            'context': intelligence,
            'has_context': True,
            'context_type': 'semantic_search'
        }
        
        # 5. Execute with enhanced context
        return await self.execute(enhanced_task)
    
    async def get_relevant_context(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Get relevant context for a query."""
        return await self.context_engine.semantic_search(query, limit)
    
    def get_file_context(self, file_path: str) -> Optional[str]:
        """Get context for specific file."""
        return self.context_engine.get_context_for_file(file_path)
    
    def get_error_solution(self, error_message: str) -> List[str]:
        """Get solution suggestions for error."""
        return self.context_engine.get_error_solutions(error_message)
```

**Benefits:**
- ✅ All agents get semantic search
- ✅ Pattern learning available to all agents
- ✅ Error solution memory accessible
- ✅ Project intelligence for better decisions
- ✅ LangChain retriever compatibility

---

### **2. ContextEngine → MCP Integration**

**Current State:**
- ❌ ContextEngine not exposed via MCP
- ❌ Cursor cannot access our RAG system
- ❌ No semantic search from IDE

**Proposed Integration:**
```python
# utils/mcp/context_server.py

from mcp import Server, Tool
from context.context_engine import ContextEngine
from models.config import ContextConfig
import asyncio

class CursorContextServer:
    """MCP server exposing ContextEngine to Cursor IDE."""
    
    def __init__(self):
        self.server = Server("ai-dev-agent-context")
        
        # Initialize ContextEngine
        context_config = ContextConfig()
        self.context_engine = ContextEngine(context_config)
        
        # Index codebase on startup
        asyncio.run(self.context_engine.index_codebase('.'))
        
        # Register MCP tools
        self.register_tools()
    
    def register_tools(self):
        """Register ContextEngine tools for Cursor."""
        
        @self.server.tool()
        async def semantic_search(query: str, limit: int = 5) -> dict:
            """Search codebase using semantic search."""
            results = await self.context_engine.semantic_search(query, limit)
            return {
                "results": results.get('results', []),
                "search_type": results.get('search_type'),
                "total_found": results.get('total_found')
            }
        
        @self.server.tool()
        async def get_file_context(file_path: str) -> dict:
            """Get context for specific file."""
            context = self.context_engine.get_context_for_file(file_path)
            return {"context": context, "file_path": file_path}
        
        @self.server.tool()
        async def get_import_suggestions(file_path: str) -> dict:
            """Get import suggestions based on patterns."""
            suggestions = self.context_engine.get_import_suggestions(file_path)
            return {"suggestions": suggestions}
        
        @self.server.tool()
        async def get_error_solution(error_message: str) -> dict:
            """Get solution for error message."""
            solutions = self.context_engine.get_error_solutions(error_message)
            return {"solutions": solutions}
        
        @self.server.tool()
        async def get_project_intelligence() -> dict:
            """Get project intelligence summary."""
            return self.context_engine.get_project_intelligence_summary()
        
        @self.server.tool()
        async def get_codebase_summary() -> dict:
            """Get codebase statistics."""
            return self.context_engine.get_codebase_summary()
    
    def run(self):
        """Run the MCP server."""
        self.server.run()

if __name__ == "__main__":
    server = CursorContextServer()
    server.run()
```

**Cursor Configuration** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "ai-dev-agent-context": {
      "command": "C:\\App\\Anaconda\\python.exe",
      "args": ["utils/mcp/context_server.py"],
      "cwd": "C:\\Users\\pogawal\\WorkFolder\\Documents\\Python\\ai-dev-agent"
    }
  }
}
```

**Benefits:**
- ✅ Cursor can search our codebase semantically
- ✅ AI in Cursor gets project context
- ✅ Error solutions available in IDE
- ✅ Import suggestions from Cursor
- ✅ Project intelligence for better code generation

---

### **3. Existing MCP Integration**

**Current MCP Infrastructure:**
- `utils/mcp/server.py` - MCP server implementation
- `utils/mcp/langchain_integration.py` - LangChain integration
- `agents/mcp/mcp_enhanced_agent.py` - MCP-enabled agent
- `MCPAgentMixin` - Mixin for MCP capabilities

**How ContextEngine Fits:**
- ContextEngine becomes another MCP tool category
- MCP agents can use ContextEngine via tools
- SwarmCoordinator can distribute context-aware tasks
- All agents benefit from shared ContextEngine instance

---

## 🎯 **Integration Strategy**

### **Phase 1: ContextAwareAgent (THIS WEEK)**

**Goal:** Enable all agents to use ContextEngine

**Tasks:**
1. Create `agents/core/context_aware_agent.py`
2. Implement `ContextAwareAgent` class
3. Add `execute_with_context()` method
4. Test with existing agent (e.g., CodeGenerator)
5. Document usage patterns

**Timeline:** 2-3 hours

**Success Metrics:**
- ✅ ContextAwareAgent class created
- ✅ At least one agent using context successfully
- ✅ Tests passing
- ✅ Documentation complete

---

### **Phase 2: Cursor MCP Integration (NEXT WEEK)**

**Goal:** Expose ContextEngine to Cursor via MCP

**Tasks:**
1. Create `utils/mcp/context_server.py`
2. Implement `CursorContextServer` class
3. Register ContextEngine tools
4. Configure Cursor MCP settings
5. Test semantic search from Cursor
6. Document Cursor usage

**Timeline:** 3-4 hours

**Success Metrics:**
- ✅ MCP server running
- ✅ Cursor can call semantic_search
- ✅ Cursor gets project intelligence
- ✅ Error solutions available in IDE
- ✅ Documentation and examples complete

---

### **Phase 3: Agent Migration (WEEK 2)**

**Goal:** Migrate existing agents to use ContextAwareAgent

**Tasks:**
1. Identify agents that would benefit most
2. Update agent inheritance to ContextAwareAgent
3. Add context-aware execution patterns
4. Test each migrated agent
5. Update agent documentation

**Timeline:** 5-7 days

**Priority Agents:**
- CodeGenerator (high value)
- CodeReviewer (needs context)
- DocumentationGenerator (needs context)
- TestGenerator (needs context)
- ArchitectureDesigner (needs context)

---

## 📈 **Expected Benefits**

### **For Agents:**
- ✅ **Smarter Decisions:** Access to project context and patterns
- ✅ **Better Code Generation:** Import suggestions, pattern learning
- ✅ **Error Recovery:** Historical error solutions
- ✅ **Project Awareness:** Understanding of codebase structure
- ✅ **Performance:** Faster context retrieval vs. full file reads

### **For Cursor IDE:**
- ✅ **Semantic Search:** Find code by meaning, not just keywords
- ✅ **Context-Aware AI:** AI responses use project knowledge
- ✅ **Import Help:** Automatic import suggestions
- ✅ **Error Solutions:** Historical solutions for common errors
- ✅ **Project Intelligence:** Better understanding of codebase

### **For Development:**
- ✅ **Faster Development:** Context-aware code generation
- ✅ **Better Quality:** Pattern-based suggestions
- ✅ **Reduced Errors:** Historical error avoidance
- ✅ **Knowledge Sharing:** Project intelligence accessible
- ✅ **Consistent Patterns:** Learned from existing code

---

## 🚀 **Recommendation**

### **START WITH PHASE 1: ContextAwareAgent**

**Why?**
1. ✅ **Foundation First:** Agents are the core of our system
2. ✅ **Low Risk:** ContextEngine already works
3. ✅ **High Value:** All agents benefit immediately
4. ✅ **Easy to Test:** We have agents to test with
5. ✅ **Quick Win:** 2-3 hours to working prototype

**Next Step:**
Create `agents/core/context_aware_agent.py` and test with one agent.

**Then Phase 2:**
Once agents work well with ContextEngine, expose to Cursor via MCP.

---

## 📝 **Technical Notes**

### **Shared ContextEngine Instance**
- Consider singleton pattern for ContextEngine
- Share vector store across all agents
- Index codebase once, use everywhere
- Update index periodically or on file changes

### **Performance Considerations**
- ContextEngine initialization takes ~10-30 seconds for full codebase
- Vector store creation is one-time cost
- Semantic search is fast (~100ms per query)
- Consider background indexing for large projects

### **Memory Management**
- FAISS vector store uses ~100-500MB RAM
- HuggingFace model uses ~400MB RAM
- Total: ~1GB RAM for full RAG system
- Acceptable for development environment

---

**Ready to build ContextAwareAgent?** 🚀

