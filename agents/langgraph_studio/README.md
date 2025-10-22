# LangGraph Studio Integration

**Status**: 🎯 Design Complete, Implementation Pending  
**Epic**: EPIC-2: Software Development Agents  
**Target Sprint**: Sprint 7 (after Sprint 6 RAG/MCP work)

---

## 🎯 Overview

This directory contains LangGraph Studio integration for the AI-Dev-Agent system, enabling visual debugging and interactive development of our multi-agent workflows.

**LangGraph Studio** is the first IDE designed specifically for agent development, providing:
- Real-time graph visualization
- Step-by-step execution with pause/resume
- State inspection and manipulation at any point
- Human-in-the-loop review checkpoints
- Performance monitoring and metrics

**Reference**: [LangGraph Studio Blog Post](https://blog.langchain.com/langgraph-studio-the-first-agent-ide/)

---

## 📁 Directory Structure

```
agents/langgraph_studio/
├── __init__.py                          # Package initialization
├── README.md                            # This file
├── agent_graph_wrapper.py               # 🔜 Single agent wrapper (coming soon)
├── development_pipeline_graph.py        # 🔜 Full pipeline (coming soon)
├── single_agents.py                     # 🔜 Individual agent wrappers (coming soon)
└── graph_registry.py                    # 🔜 Discovery system (coming soon)
```

---

## ✅ Currently Available

### **1. RAG Pipeline** (Ready Now!)

**File**: `agents/rag/rag_swarm_langgraph.py`  
**Class**: `RAGSwarmCoordinator`

5-agent pipeline for document retrieval and synthesis:
1. QueryAnalystAgent - Analyzes user queries
2. RetrievalSpecialistAgent - Retrieves relevant documents
3. ReRankerAgent - Ranks results by relevance
4. QualityAssuranceAgent - Validates quality
5. WriterAgent - Generates final response

**Features**:
- ✅ LangGraph StateGraph implementation
- ✅ Conditional re-retrieval based on quality
- ✅ Full state management with TypedDict
- ✅ MemorySaver checkpointing
- ✅ Comprehensive metrics tracking

**To Use in LangGraph Studio**:
1. Open project in LangGraph Studio
2. Select "rag_pipeline" from available graphs
3. Requires: context_engine initialization

### **2. Research Pipeline** (Ready Now!)

**File**: `agents/research/web_research_swarm.py`  
**Class**: `WebResearchSwarmCoordinator`

5-agent pipeline for web research:
1. QueryPlannerAgent - Plans research strategy
2. WebSearchAgent - Executes web searches
3. ContentParserAgent - Parses content
4. VerificationAgent - Verifies information
5. SynthesisAgent - Synthesizes findings

**Features**:
- ✅ LangGraph StateGraph implementation
- ✅ Conditional re-search based on quality
- ✅ Full state management
- ✅ Comprehensive research workflow

---

## 🔜 Coming Soon (Sprint 7+)

### **Development Pipeline Graph**

Complete software development workflow with 7 agents:
1. RequirementsAnalyst
2. ArchitectureDesigner
3. CodeGenerator
4. TestGenerator
5. CodeReviewer
6. SecurityAnalyst
7. DocumentationGenerator

**Planned Features**:
- Human review checkpoints after each stage
- State modification mid-execution
- Conditional branching based on quality
- Parallel execution where possible
- Complete metrics and monitoring

### **Single Agent Wrappers**

Individual LangGraph wrappers for each development agent:
- Enables testing single agents in Studio
- Provides simplified debugging
- Allows quick iterations on individual agents

---

## 🚀 Getting Started with LangGraph Studio

### **Prerequisites**

1. **LangGraph Studio Desktop App** (currently Mac only)
   - Download from: https://langchain.com/langgraph-studio
   - More platforms coming soon

2. **LangSmith Account** (free tier available)
   - Sign up at: https://smith.langchain.com
   - Used for tracing and monitoring

3. **Environment Variables**
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   export LANGCHAIN_API_KEY="your-langsmith-key"
   export LANGCHAIN_TRACING_V2="true"
   export LANGCHAIN_PROJECT="ai-dev-agent"
   ```

### **Opening Project**

1. **Launch LangGraph Studio**
2. **Open Directory**: Select the `ai-dev-agent` project root
3. **Studio reads** `langgraph.json` and discovers available graphs
4. **Select a graph** from the dropdown
5. **Click "Build"** to initialize the environment

### **Running and Debugging**

1. **Input**: Provide input in the task box (e.g., query for RAG)
2. **Run**: Click "Run" to execute the graph
3. **Pause**: Click pause at any time to inspect state
4. **Inspect**: View state at any node
5. **Modify**: Edit responses or state
6. **Continue**: Resume execution with modified state

### **State Manipulation**

You can modify agent behavior mid-execution:
- Edit LLM responses
- Change search parameters
- Inject human feedback
- Modify quality thresholds
- Fork execution paths

---

## 📊 Graph Visualization

LangGraph Studio provides real-time visualization:

```
[QueryAnalyst] → [Retrieval] → [ReRanker] → [QA] → [Writer] → END
                      ↑                        |
                      └────────(re-retrieve)───┘
```

Each node shows:
- Execution status (running/complete/error)
- Execution time
- State before/after
- Decisions made

---

## 🎯 Configuration

### **langgraph.json** (Project Root)

```json
{
  "dependencies": ["requirements.txt"],
  "graphs": {
    "rag_pipeline": {
      "path": "./agents/rag/rag_swarm_langgraph.py:RAGSwarmCoordinator",
      "description": "RAG pipeline with 5 agents"
    },
    "research_pipeline": {
      "path": "./agents/research/web_research_swarm.py:WebResearchSwarmCoordinator",
      "description": "Research pipeline with 5 agents"
    }
  },
  "env": {
    "GOOGLE_API_KEY": "${GOOGLE_API_KEY}",
    "LANGCHAIN_API_KEY": "${LANGCHAIN_API_KEY}",
    "LANGCHAIN_TRACING_V2": "true",
    "LANGCHAIN_PROJECT": "ai-dev-agent"
  },
  "python_version": "3.11"
}
```

---

## 🔧 Development

### **Adding New Graphs**

1. **Create Graph Class** with LangGraph StateGraph
2. **Register in langgraph.json**
3. **Test in Studio**
4. **Document in this README**

Example:
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class MyAgentState(TypedDict):
    input: Annotated[str, "User input"]
    output: Annotated[str, "Agent output"]

class MyAgentGraph:
    def __init__(self):
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(MyAgentState)
        workflow.add_node("process", self._process_node)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        return workflow
    
    async def _process_node(self, state: MyAgentState) -> MyAgentState:
        # Your agent logic here
        state["output"] = f"Processed: {state['input']}"
        return state
```

### **Testing Graphs**

```python
# Test without Studio
async def test_graph():
    graph = MyAgentGraph()
    result = await graph.app.ainvoke({
        "input": "test query"
    })
    print(result)

# Run test
import asyncio
asyncio.run(test_graph())
```

---

## 📚 Resources

### **Official Documentation**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Studio Blog](https://blog.langchain.com/langgraph-studio-the-first-agent-ide/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)

### **Project Documentation**
- [Integration Design](../../docs/agile/sprints/sprint_6/analysis/LANGGRAPH_STUDIO_INTEGRATION_DESIGN.md)
- [Agent Development Guide](../../docs/guides/langgraph/agent_development_guide.md)
- [RAG Swarm Architecture](../../docs/architecture/RAG_SWARM_LANGGRAPH_MIGRATION.md)

### **Examples**
- RAG Pipeline: `agents/rag/rag_swarm_langgraph.py`
- Research Pipeline: `agents/research/web_research_swarm.py`

---

## 🎯 Roadmap

### **Sprint 6** (Current)
- ✅ Design complete
- ✅ `langgraph.json` created
- ✅ Existing LangGraph agents documented
- 📋 Focus on RAG and MCP integration

### **Sprint 7** (Next)
- 🔜 Create Development Pipeline Graph
- 🔜 Implement single agent wrappers
- 🔜 Add human-in-the-loop checkpoints
- 🔜 Comprehensive testing

### **Sprint 8+** (Future)
- 🔜 Team coordinator graphs
- 🔜 Supervisor system graphs
- 🔜 Advanced state persistence
- 🔜 Custom UI components

---

## 💡 Tips & Best Practices

1. **Start Simple**: Test with RAG pipeline first
2. **Use Checkpoints**: Add MemorySaver for state persistence
3. **Human Review**: Add conditional edges for human approval
4. **State Design**: Keep state JSON-serializable
5. **Error Handling**: Implement graceful error recovery
6. **Metrics**: Track execution time and decisions
7. **Documentation**: Document state structure clearly

---

## 🐛 Troubleshooting

### **"Graph not found"**
- Check `langgraph.json` path is correct
- Ensure class name matches
- Rebuild environment in Studio

### **"Import errors"**
- Check all dependencies in `requirements.txt`
- Ensure PYTHONPATH includes project root
- Verify environment variables set

### **"State serialization error"**
- Ensure state uses TypedDict
- Avoid complex Python objects in state
- Use JSON-serializable types only

### **"Graph won't compile"**
- Check all nodes are connected
- Verify conditional edges have all paths
- Ensure no circular dependencies without termination

---

**Status**: Ready for RAG/Research pipelines, Full implementation pending Sprint 7  
**Contact**: AI Development Team  
**Last Updated**: 2025-10-22

