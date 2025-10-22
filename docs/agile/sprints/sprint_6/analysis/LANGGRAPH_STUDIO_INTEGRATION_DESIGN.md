# LangGraph Studio Integration Design

**Epic**: EPIC-2: Software Development Agents  
**User Story**: US-MCP-001 (MCP-Enhanced Agent Tool Access)  
**Sprint**: Sprint 6  
**Created**: 2025-10-22  
**Status**: 🎯 Design Phase

---

## 🎯 Executive Summary

Design document for integrating our AI-Dev-Agent system with **LangGraph Studio** - the first IDE specifically designed for agent development. This will enable:

- **Visual debugging** of agent workflows
- **Step-by-step execution** with pause/resume
- **State inspection** and manipulation at any point
- **Real-time graph visualization** of agent interactions
- **Human-in-the-loop** capabilities

**Reference**: [LangGraph Studio Blog Post](https://blog.langchain.com/langgraph-studio-the-first-agent-ide/)

---

## 📊 Current State Analysis

### ✅ **What We Have**

1. **LangGraph Already Installed**
   - `langgraph==0.2.28` in requirements.txt
   - Two agents already using LangGraph:
     - `agents/rag/rag_swarm_langgraph.py` - RAG pipeline with 5 agents
     - `agents/research/web_research_swarm.py` - Research pipeline with 5 agents

2. **Agent Architecture**
   - **7 Development Agents**: requirements_analyst, architecture_designer, code_generator, test_generator, code_reviewer, security_analyst, documentation_generator
   - **Base Classes**: `BaseAgent`, `EnhancedBaseAgent`, `ContextAwareAgent`
   - **Team Coordinators**: 15+ specialized team agents
   - **Supervisor System**: Project manager supervisors

3. **State Management**
   - Agents use dataclass-based state
   - Some TypedDict usage in LangGraph agents
   - Comprehensive AgentState and AgentConfig classes

4. **Execution Patterns**
   - Async execution with `execute()` method
   - Database-backed prompts (no hardcoded prompts)
   - Structured outputs with validation

### ❌ **What's Missing for LangGraph Studio**

1. **`langgraph.json` Configuration** - Required by LangGraph Studio
2. **Graph Entry Points** - Discoverable graph definitions
3. **TypedDict State** for non-LangGraph agents
4. **Checkpointing** for human-in-the-loop
5. **Unified Graph Interface** for all agents

---

## 🏗️ Integration Architecture

### **Layer 1: LangGraph Wrapper System**

Create a unified LangGraph wrapper that converts our existing agents into LangGraph-compatible graphs:

```python
# agents/langgraph_studio/agent_graph_wrapper.py

from typing import TypedDict, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.core.enhanced_base_agent import EnhancedBaseAgent

class AgentGraphState(TypedDict):
    """Universal state for single-agent graphs."""
    # Input
    task: Annotated[Dict[str, Any], "Input task specification"]
    agent_config: Annotated[Dict[str, Any], "Agent configuration"]
    
    # Execution state
    current_step: Annotated[str, "Current execution step"]
    steps_completed: Annotated[list[str], "Completed steps"]
    
    # Output
    result: Annotated[Dict[str, Any], "Agent execution result"]
    metrics: Annotated[Dict[str, float], "Performance metrics"]
    errors: Annotated[list[str], "Error messages if any"]
    
    # Human-in-the-loop
    human_feedback: Annotated[Dict[str, Any], "Human feedback at checkpoints"]
    needs_human_review: Annotated[bool, "Whether human review is needed"]

class SingleAgentGraph:
    """Wrapper that converts any EnhancedBaseAgent into a LangGraph."""
    
    def __init__(self, agent: EnhancedBaseAgent):
        self.agent = agent
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentGraphState)
        
        # Single agent execution node
        workflow.add_node("execute_agent", self._execute_node)
        workflow.add_node("validate_output", self._validate_node)
        workflow.add_node("human_review", self._human_review_node)
        
        # Workflow
        workflow.set_entry_point("execute_agent")
        workflow.add_conditional_edges(
            "execute_agent",
            self._needs_validation,
            {
                "validate": "validate_output",
                "human_review": "human_review",
                END: END
            }
        )
        workflow.add_edge("validate_output", END)
        workflow.add_edge("human_review", END)
        
        return workflow
```

### **Layer 2: Development Pipeline Graphs**

Create multi-agent graphs for complete development workflows:

```python
# agents/langgraph_studio/development_pipeline_graph.py

class DevelopmentPipelineState(TypedDict):
    """State for complete development pipeline."""
    # Input
    project_description: Annotated[str, "Project requirements"]
    
    # Agent outputs
    requirements: Annotated[Dict, "Requirements analysis output"]
    architecture: Annotated[Dict, "Architecture design output"]
    code: Annotated[Dict, "Generated code output"]
    tests: Annotated[Dict, "Generated tests output"]
    review: Annotated[Dict, "Code review output"]
    security: Annotated[Dict, "Security analysis output"]
    documentation: Annotated[Dict, "Documentation output"]
    
    # Workflow control
    current_stage: Annotated[str, "Current pipeline stage"]
    stages_completed: Annotated[list[str], "Completed stages"]
    human_approvals: Annotated[Dict[str, bool], "Human approval at each stage"]
    
    # Metrics
    metrics: Annotated[Dict[str, float], "Pipeline metrics"]

class DevelopmentPipelineGraph:
    """Complete software development pipeline as a LangGraph."""
    
    def __init__(self):
        from agents.development.requirements_analyst import RequirementsAnalyst
        from agents.development.architecture_designer import ArchitectureDesigner
        from agents.development.code_generator import CodeGenerator
        from agents.development.test_generator import TestGenerator
        from agents.development.code_reviewer import CodeReviewer
        from agents.development.security_analyst import SecurityAnalyst
        from agents.development.documentation_generator import DocumentationGenerator
        
        # Initialize all agents
        self.requirements_analyst = RequirementsAnalyst({...})
        self.architecture_designer = ArchitectureDesigner({...})
        # ... etc
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(DevelopmentPipelineState)
        
        # Add nodes for each agent
        workflow.add_node("requirements_analysis", self._requirements_node)
        workflow.add_node("architecture_design", self._architecture_node)
        workflow.add_node("code_generation", self._code_generation_node)
        workflow.add_node("test_generation", self._test_generation_node)
        workflow.add_node("code_review", self._code_review_node)
        workflow.add_node("security_analysis", self._security_analysis_node)
        workflow.add_node("documentation_generation", self._documentation_node)
        
        # Human-in-the-loop checkpoints
        workflow.add_node("review_requirements", self._human_review_requirements)
        workflow.add_node("review_architecture", self._human_review_architecture)
        workflow.add_node("review_code", self._human_review_code)
        
        # Define workflow with conditional human review
        workflow.set_entry_point("requirements_analysis")
        
        workflow.add_conditional_edges(
            "requirements_analysis",
            self._should_review_requirements,
            {
                "review": "review_requirements",
                "continue": "architecture_design"
            }
        )
        
        # Continue the pipeline...
        workflow.add_edge("review_requirements", "architecture_design")
        workflow.add_edge("architecture_design", "code_generation")
        workflow.add_edge("code_generation", "test_generation")
        workflow.add_edge("test_generation", "code_review")
        workflow.add_edge("code_review", "security_analysis")
        workflow.add_edge("security_analysis", "documentation_generation")
        workflow.add_edge("documentation_generation", END)
        
        return workflow
```

### **Layer 3: Graph Registry & Discovery**

Create a central registry for all available graphs:

```python
# agents/langgraph_studio/graph_registry.py

from typing import Dict, Type
from langgraph.graph import CompiledGraph

class GraphRegistry:
    """Central registry for all LangGraph Studio compatible graphs."""
    
    _graphs: Dict[str, CompiledGraph] = {}
    
    @classmethod
    def register(cls, name: str, graph: CompiledGraph):
        """Register a graph for LangGraph Studio discovery."""
        cls._graphs[name] = graph
    
    @classmethod
    def get_graph(cls, name: str) -> CompiledGraph:
        """Get a registered graph by name."""
        return cls._graphs.get(name)
    
    @classmethod
    def list_graphs(cls) -> list[str]:
        """List all registered graph names."""
        return list(cls._graphs.keys())

# Auto-register all available graphs
def register_all_graphs():
    """Register all graphs on module import."""
    from agents.langgraph_studio.development_pipeline_graph import DevelopmentPipelineGraph
    from agents.rag.rag_swarm_langgraph import RAGSwarmCoordinator
    from agents.research.web_research_swarm import WebResearchSwarmCoordinator
    
    # Development pipeline
    dev_pipeline = DevelopmentPipelineGraph()
    GraphRegistry.register("development_pipeline", dev_pipeline.app)
    
    # RAG pipeline (needs context_engine - will be created on demand)
    # GraphRegistry.register("rag_pipeline", rag_swarm.app)
    
    # Research pipeline
    research_swarm = WebResearchSwarmCoordinator()
    GraphRegistry.register("research_pipeline", research_swarm.app)
    
    print(f"✅ Registered {len(GraphRegistry.list_graphs())} graphs for LangGraph Studio")

# Auto-register on import
register_all_graphs()
```

---

## 📋 `langgraph.json` Configuration

Create the required configuration file at project root:

```json
{
  "dependencies": [
    "requirements.txt"
  ],
  "graphs": {
    "development_pipeline": {
      "path": "./agents/langgraph_studio/development_pipeline_graph.py",
      "graph": "DevelopmentPipelineGraph",
      "description": "Complete software development pipeline with 7 specialized agents"
    },
    "rag_pipeline": {
      "path": "./agents/rag/rag_swarm_langgraph.py",
      "graph": "RAGSwarmCoordinator",
      "description": "RAG document retrieval and synthesis pipeline with 5 agents"
    },
    "research_pipeline": {
      "path": "./agents/research/web_research_swarm.py",
      "graph": "WebResearchSwarmCoordinator",
      "description": "Web research and synthesis pipeline with 5 agents"
    },
    "requirements_agent": {
      "path": "./agents/langgraph_studio/single_agents.py",
      "graph": "RequirementsAnalystGraph",
      "description": "Single requirements analysis agent"
    },
    "architecture_agent": {
      "path": "./agents/langgraph_studio/single_agents.py",
      "graph": "ArchitectureDesignerGraph",
      "description": "Single architecture design agent"
    },
    "code_generator_agent": {
      "path": "./agents/langgraph_studio/single_agents.py",
      "graph": "CodeGeneratorGraph",
      "description": "Single code generation agent"
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

## 🎯 Implementation Plan

### **Phase 1: Foundation** (2-3 days)

1. ✅ Create `agents/langgraph_studio/` directory
2. ✅ Implement `AgentGraphWrapper` for single agents
3. ✅ Implement `GraphRegistry` for discovery
4. ✅ Create `langgraph.json` at project root
5. ✅ Test with existing LangGraph agents (RAG, Research)

### **Phase 2: Development Pipeline** (3-4 days)

1. ✅ Implement `DevelopmentPipelineGraph`
2. ✅ Add human-in-the-loop checkpoints
3. ✅ Implement proper state management
4. ✅ Add conditional edges for workflow control
5. ✅ Test complete pipeline in LangGraph Studio

### **Phase 3: Single Agent Wrappers** (2-3 days)

1. ✅ Wrap each development agent individually
2. ✅ Create `single_agents.py` with all wrappers
3. ✅ Add to graph registry
4. ✅ Test individual agent execution

### **Phase 4: Advanced Features** (2-3 days)

1. ✅ Implement state persistence
2. ✅ Add breakpoints for debugging
3. ✅ Implement state modification UI
4. ✅ Add metrics and monitoring
5. ✅ Documentation and examples

---

## 🔑 Key Features

### **1. Visual Debugging**

LangGraph Studio provides:
- Real-time graph visualization
- Step-by-step execution
- State inspection at any node
- Pause/resume capabilities

### **2. Human-in-the-Loop**

We'll add human review checkpoints at:
- After requirements analysis
- After architecture design
- After code generation
- Before deployment

### **3. State Manipulation**

Users can:
- Modify agent responses mid-execution
- Edit prompts and retry nodes
- Inject feedback at any point
- Fork execution paths

### **4. Performance Monitoring**

Track:
- Execution time per node
- State size and complexity
- Agent decision points
- Error rates and recovery

---

## 📊 Success Metrics

### **Technical Metrics**
- ✅ All 7 development agents wrapped in LangGraph
- ✅ Complete pipeline graph functional
- ✅ Human-in-the-loop working
- ✅ State persistence operational
- ✅ <1s graph load time

### **Developer Experience Metrics**
- ✅ Visual debugging saves 50%+ debugging time
- ✅ Human review reduces iteration cycles
- ✅ State inspection improves agent understanding
- ✅ 90%+ developer satisfaction

---

## 🚀 Quick Start (After Implementation)

1. **Install LangGraph Studio** (Mac only currently)
   ```bash
   # Download from LangChain website
   ```

2. **Open Project in Studio**
   ```bash
   # LangGraph Studio will read langgraph.json
   # and discover all available graphs
   ```

3. **Select a Graph**
   - Choose "development_pipeline" for full workflow
   - Choose individual agent for single execution
   - Choose "rag_pipeline" for document queries

4. **Run and Debug**
   - Click "Run" to start execution
   - Click "Pause" at any time
   - Inspect state in real-time
   - Modify and continue

---

## 🔗 Dependencies

### **Required**
- `langgraph>=0.2.28` ✅ (already installed)
- `langchain>=0.3.27` ✅ (already installed)
- `langchain-core>=0.3.78` ✅ (already installed)

### **Optional but Recommended**
- LangSmith account (free tier)
- LangGraph Studio (Mac desktop app)

---

## 📝 File Structure

```
ai-dev-agent/
├── langgraph.json                           # 🆕 LangGraph Studio config
├── agents/
│   ├── langgraph_studio/                    # 🆕 Studio integration
│   │   ├── __init__.py
│   │   ├── agent_graph_wrapper.py           # 🆕 Single agent wrapper
│   │   ├── development_pipeline_graph.py    # 🆕 Full pipeline
│   │   ├── single_agents.py                 # 🆕 Individual wrappers
│   │   ├── graph_registry.py                # 🆕 Discovery system
│   │   └── README.md                        # 🆕 Documentation
│   ├── rag/
│   │   └── rag_swarm_langgraph.py          # ✅ Already LangGraph
│   ├── research/
│   │   └── web_research_swarm.py           # ✅ Already LangGraph
│   └── development/
│       ├── requirements_analyst.py          # 📝 Needs wrapper
│       ├── architecture_designer.py         # 📝 Needs wrapper
│       ├── code_generator.py                # 📝 Needs wrapper
│       ├── test_generator.py                # 📝 Needs wrapper
│       ├── code_reviewer.py                 # 📝 Needs wrapper
│       ├── security_analyst.py              # 📝 Needs wrapper
│       └── documentation_generator.py       # 📝 Needs wrapper
```

---

## ⚠️ Challenges & Solutions

### **Challenge 1: Agent Dependencies**
**Problem**: Some agents need context_engine, database connections, etc.  
**Solution**: Lazy initialization in graph nodes, dependency injection in state

### **Challenge 2: State Serialization**
**Problem**: Complex Python objects don't serialize well  
**Solution**: Convert to JSON-serializable TypedDict structures

### **Challenge 3: Long-Running Operations**
**Problem**: Code generation can take minutes  
**Solution**: Use streaming updates, checkpointing, timeout handling

### **Challenge 4: Platform Compatibility**
**Problem**: LangGraph Studio currently Mac-only  
**Solution**: Still beneficial for development, works with LangSmith web UI

---

## 🎯 Next Steps

1. **Create User Story**
   - US-STUDIO-001: LangGraph Studio Integration
   - Priority: HIGH
   - Points: 13
   - Sprint: Current (Sprint 6) or Next (Sprint 7)

2. **Implementation Order**
   - Start with Phase 1 (Foundation)
   - Test with existing LangGraph agents
   - Proceed to Phase 2 (Pipeline)
   - Add individual wrappers in Phase 3

3. **Documentation**
   - User guide for LangGraph Studio
   - Developer guide for adding new graphs
   - Architecture documentation
   - Video walkthrough

---

**Status**: 🎯 **DESIGN COMPLETE** - Ready for Implementation  
**Next Action**: Create user story and add to Sprint 6 or 7 backlog  
**Estimated Effort**: 10-13 story points (2 sprints)  
**Value**: HIGH - Revolutionary debugging and development experience

