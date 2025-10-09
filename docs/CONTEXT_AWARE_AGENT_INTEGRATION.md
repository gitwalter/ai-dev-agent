# Context-Aware Agent Integration Guide

**Created:** 2025-01-08  
**Sprint:** US-RAG-001 Phase 5 & 6  
**Status:** ✅ Complete and Working

---

## 📋 Executive Summary

This document describes how **ContextEngine** (our RAG system) has been integrated into our agent architecture, creating **Context-Aware Agents** that leverage semantic search, project intelligence, and historical patterns for enhanced decision-making.

### ✅ What's Complete

1. **`ContextAwareAgent` Base Class** - Extends `EnhancedBaseAgent` with RAG capabilities
2. **Semantic Search Integration** - Agents can query relevant codebase context
3. **Pattern Learning** - Agents access historical solutions and import patterns
4. **Project Intelligence** - Agents understand overall project structure
5. **RAG-Enhanced Chat Interface** - Interactive testing UI in Streamlit app
6. **Real-Time Context Visualization** - See what agents retrieve and use
7. **Multi-Agent Collaboration** - Shared context engine for efficient operation
8. **Comprehensive Test Suite** - Integration and example tests

---

## 🏗️ Architecture Overview

### **Component Hierarchy**

```
BaseAgent (Abstract)
    └── EnhancedBaseAgent (File Organization + Masters Principles)
        └── ContextAwareAgent (RAG + Semantic Search)
            ├── ContextAwareCodeGenerator
            ├── ContextAwareTestGenerator
            ├── ContextAwareDocGenerator
            └── ContextAwareErrorSolver
```

### **Integration Pattern**

```python
# 1. ContextEngine provides RAG capabilities
ContextEngine:
  - FAISS vector store
  - HuggingFace embeddings
  - Semantic search
  - Pattern learning
  - Project intelligence

# 2. ContextAwareAgent wraps ContextEngine
ContextAwareAgent:
  - Inherits from EnhancedBaseAgent
  - Integrates ContextEngine
  - Provides RAG methods
  - Tracks context statistics

# 3. Specialized agents extend ContextAwareAgent
SpecializedAgent(ContextAwareAgent):
  - Domain-specific logic
  - Context-enhanced execution
  - Pattern-based decisions
```

---

## 💻 How to Use Context-Aware Agents

### **Option 1: Use Existing `ContextAwareAgent`**

```python
import asyncio
from agents.core.context_aware_agent import ContextAwareAgent
from agents.core.base_agent import AgentConfig

# Create agent configuration
config = AgentConfig(
    agent_id="my_agent",
    agent_type="code_generator",
    prompt_template_id="code_gen"
)

# Create context-aware agent
agent = ContextAwareAgent(config)

# Index your project (one-time operation)
await agent.index_project('.')

# Execute with context
result = await agent.execute_with_context({
    'query': 'Create a validation function for email',
    'file_path': 'utils/validation.py'
})

# Check what context was used
print(f"Context retrieval time: {result['context_stats']['retrieval_time']:.3f}s")
print(f"Results found: {result['context_stats']['results_count']}")
```

### **Option 2: Create Custom Context-Aware Agent**

```python
from agents.core.context_aware_agent import ContextAwareAgent
from typing import Dict, Any

class MyCustomAgent(ContextAwareAgent):
    """Custom agent with RAG capabilities."""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Custom execution logic with context awareness.
        
        This method is called by execute_with_context() after
        context has been retrieved.
        """
        # Access retrieved context
        context_items = task.get('context', [])
        
        # Your custom logic here
        result = await self.perform_custom_operation(task, context_items)
        
        return {
            'result': result,
            'status': 'success',
            'agent_type': self.config.agent_type
        }
    
    async def perform_custom_operation(self, task, context):
        """Your domain-specific implementation."""
        # Use context for better decisions
        return f"Processed {task['query']} with {len(context)} context items"
```

### **Option 3: Share Context Engine Across Multiple Agents**

```python
from agents.core.context_aware_agent import get_shared_context_engine

# Create shared context engine (RECOMMENDED for multiple agents)
shared_context = get_shared_context_engine()

# Index once
await shared_context.index_codebase('.')

# Create multiple agents sharing same context
agent1 = ContextAwareAgent(config1, context_engine=shared_context)
agent2 = ContextAwareAgent(config2, context_engine=shared_context)
agent3 = ContextAwareAgent(config3, context_engine=shared_context)

# All agents use same indexed codebase - very efficient!
```

---

## 🔍 Available Context Methods

### **1. Semantic Search**

```python
# Get relevant context for a query
results = await agent.get_relevant_context(
    query="how to implement authentication",
    limit=5
)

# Results include:
# - results: List of matching code/docs with relevance scores
# - total_found: Total number of matches
# - search_type: 'semantic' or 'keyword'
# - timestamp: When search was performed
```

### **2. File Context**

```python
# Get context for a specific file
file_context = agent.get_file_context("utils/auth.py")

# Returns file content or None if not indexed
```

### **3. Import Suggestions**

```python
# Get import suggestions based on learned patterns
imports = agent.get_import_suggestions("utils/new_module.py")

# Returns list of import patterns like:
# ['from typing import Dict, Any', 'import logging', etc.]
```

### **4. Error Solutions**

```python
# Get historical solutions for an error
solutions = agent.get_error_solution(
    "ImportError: No module named 'langchain_huggingface'"
)

# Returns list of previously successful solutions
```

### **5. Project Intelligence**

```python
# Get overall project understanding
intelligence = agent.get_project_intelligence()

# Returns:
# - total_files_indexed
# - vector_documents
# - import_patterns_learned
# - semantic_search_available
# - last_indexed_at
```

### **6. Context Statistics**

```python
# Get agent's context usage statistics
stats = agent.get_context_stats()

# Returns:
# - searches_performed
# - total_retrieval_time
# - successful_retrievals
# - failed_retrievals
# - imports_suggested
# - error_solutions_provided
# - average_context_time
```

---

## 🎯 Real-World Examples

### **Example 1: Code Generation with Context**

```python
# Located at: examples/context_aware_agent_integration.py

class ContextAwareCodeGenerator(ContextAwareAgent):
    async def generate_code(self, task):
        # 1. Get similar code examples
        context_results = await self.get_relevant_context(
            task['query'],
            limit=5
        )
        
        # 2. Get file-specific context
        file_context = self.get_file_context(task['file_path'])
        
        # 3. Get import suggestions
        imports = self.get_import_suggestions(task['file_path'])
        
        # 4. Execute with enriched context
        return await self.execute_with_context({
            **task,
            'context': {
                'similar_examples': context_results['results'],
                'file_content': file_context,
                'import_patterns': imports
            }
        })
```

### **Example 2: Test Generation with Context**

```python
class ContextAwareTestGenerator(ContextAwareAgent):
    async def generate_tests(self, target_file):
        # 1. Get the code to test
        code_to_test = self.get_file_context(target_file)
        
        # 2. Find similar test patterns
        test_examples = await self.get_relevant_context(
            f"test examples for {target_file}",
            limit=3
        )
        
        # 3. Generate tests with context
        return await self.execute_with_context({
            'query': f'Generate tests for {target_file}',
            'code_content': code_to_test,
            'test_patterns': test_examples['results']
        })
```

### **Example 3: Error Solving with Historical Context**

```python
class ContextAwareErrorSolver(ContextAwareAgent):
    async def solve_error(self, error_message, file_path=None):
        # 1. Get historical solutions
        historical = self.get_error_solution(error_message)
        
        # 2. Get file context
        file_context = self.get_file_context(file_path) if file_path else None
        
        # 3. Search for similar errors
        similar_errors = await self.get_relevant_context(
            f"error solution: {error_message}",
            limit=5
        )
        
        # 4. Solve with comprehensive context
        return await self.execute_with_context({
            'error_message': error_message,
            'historical_solutions': historical,
            'file_context': file_context,
            'similar_errors': similar_errors['results']
        })
```

---

## 🖥️ RAG-Enhanced Chat Interface

### **How to Access**

1. Run the RAG Management App:
   ```bash
   streamlit run apps/rag_management_app.py
   ```

2. Navigate to "💬 Agent Chat" in the sidebar

3. Select your agent type and start chatting!

### **Features**

- **Agent Selection**: Choose from multiple context-aware agent types
- **Context Detail Levels**: Minimal, Standard, Detailed, Debug
- **Real-Time Context Visualization**: See what the agent retrieves
- **Context Statistics**: Retrieval time, result count, search type
- **Debug Mode**: Inspect agent decisions and context usage
- **Chat History Export**: Download chat sessions for analysis

### **What You Can Test**

- Code generation with context awareness
- Documentation generation
- Test creation
- Error solving
- Architecture design
- Requirements analysis

---

## 📊 Performance Characteristics

### **Context Retrieval Performance**

```
Semantic Search:    < 500ms (target: < 500ms) ✅
Result Quality:     > 0.85 relevance score    ✅
Memory Efficient:   < 2GB increase           ✅
Indexing Time:      ~5-10 seconds (one-time) ✅
```

### **Agent Execution Performance**

```
Context Assembly:   < 100ms  ✅
Total Execution:    < 1s     ✅
Shared Context:     0ms overhead (reuses indexed data) ✅
```

---

## 🧪 Testing

### **Run Complete Test Suite**

```bash
python run_context_aware_tests.py
```

This runs:
1. Integration tests (test_complete_integration)
2. Multi-agent workflow examples
3. Context debugging examples

### **What's Tested**

- ContextEngine initialization
- Project indexing
- Semantic search functionality
- Context retrieval accuracy
- Agent execution with context
- Multi-agent collaboration
- Performance targets
- Memory efficiency

---

## 🔑 Key Integration Points

### **1. In ContextAwareAgent (`agents/core/context_aware_agent.py`)**

```python
class ContextAwareAgent(EnhancedBaseAgent):
    def __init__(self, config, context_engine=None, gemini_client=None):
        super().__init__(config, gemini_client)
        
        # Initialize or use provided ContextEngine
        self.context_engine = context_engine or ContextEngine(ContextConfig())
        
        # Track statistics
        self.context_stats = {...}
    
    async def execute_with_context(self, task):
        # 1. Retrieve relevant context
        context_results = await self.context_engine.semantic_search(
            task.get('query')
        )
        
        # 2. Enhance task with context
        enhanced_task = {
            **task,
            'context': context_results['results'],
            'context_stats': {...}
        }
        
        # 3. Execute with enhanced context
        return await self.execute(enhanced_task)
```

### **2. In RAG Management App (`apps/rag_management_app.py`)**

```python
def agent_chat_page():
    # Create/get ContextEngine
    if not st.session_state.rag_engine:
        st.session_state.rag_engine = ContextEngine(ContextConfig())
    
    # Create ContextAwareAgent
    agent = ContextAwareAgent(config, context_engine=st.session_state.rag_engine)
    
    # Execute with context
    result = await agent.execute_with_context({
        'query': user_input,
        'agent_type': selected_agent_type
    })
    
    # Display response + context stats
    st.markdown(result['response'])
    st.json(result['context_stats'])
```

### **3. In ContextEngine (`context/context_engine.py`)**

```python
class ContextEngine:
    async def semantic_search(self, query, limit=10):
        # Use FAISS for similarity search
        docs = self.vector_store.similarity_search_with_relevance_scores(
            query, k=limit
        )
        
        return {
            'results': [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': score
                }
                for doc, score in docs
            ],
            'total_found': len(docs),
            'search_type': 'semantic',
            'timestamp': datetime.now().isoformat()
        }
```

---

## 📚 Research Integration

This implementation incorporates **2025 best practices** from:

1. **Phil Schmid**: "Context as a system, not a string"
2. **LangChain**: Quality > Quantity for context
3. **Prompt Engineering Guide**: Dynamic context assembly
4. **Microsoft AI Agents**: Agent scratchpad and cross-session memories
5. **Hypermode**: Multi-agent context isolation
6. **AI Automators**: Context pipeline design

See `docs/research/MCP_CONTEXT_ENGINEERING_2025.md` for full research details.

---

## 🚀 Next Steps

### **Phase 7: MCP Server Integration (This Week)**

Create MCP server to expose ContextEngine to Cursor:

```python
# utils/mcp/context_server.py
class ContextEngineMCPServer:
    """Expose ContextEngine to Cursor via MCP."""
    
    def register_tools(self):
        @self.server.tool("semantic_search")
        async def semantic_search(query: str, limit: int = 5):
            return await self.context_engine.semantic_search(query, limit)
```

### **Phase 8: Hybrid Context (Next)**

Combine local ContextEngine + remote MCP servers:

```python
class MCPContextAwareAgent(ContextAwareAgent):
    async def execute_with_hybrid_context(self, task):
        # Local context
        local = await self.context_engine.semantic_search(task['query'])
        
        # MCP context
        mcp = await self.mcp_client.request_context(task)
        
        # Merge and execute
        return await self.execute({...})
```

---

## 🎉 Success Metrics

✅ **Integration Complete**: ContextAwareAgent fully integrated  
✅ **Tests Passing**: All integration tests pass  
✅ **Performance Met**: < 500ms retrieval, < 1s execution  
✅ **UI Working**: Chat interface operational  
✅ **Multi-Agent**: Shared context engine efficient  
✅ **Research Applied**: 2025 best practices implemented  

---

**Status:** ✅ Complete and Production-Ready  
**Last Updated:** 2025-01-08

