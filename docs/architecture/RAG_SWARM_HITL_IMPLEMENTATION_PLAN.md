# RAG Agent Swarm HITL Implementation Plan - LangChain Compatible

**Created:** 2025-01-29  
**Purpose:** Redesign RAG Agent Swarm with LangChain-compatible Human-in-the-Loop patterns  
**Status:** 📋 Implementation Plan

---

## 🎯 **Vision**

Implement a **LangChain-native HITL RAG system** that follows official patterns from:
- [LangChain HITL Middleware](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

---

## 📊 **Current State Analysis**

### ✅ **What We Have**
- Custom HITL implementation using `interrupt_before` nodes
- `RAGSwarmCoordinator` with LangGraph StateGraph
- 5 specialized agents (QueryAnalyst, RetrievalSpecialist, ReRanker, QA, Writer)
- Thread-based state persistence with MemorySaver
- Streamlit UI with manual interrupt handling

### ❌ **What's Missing (LangChain Compliance)**
- Not using LangChain's `HumanInTheLoopMiddleware`
- Custom routing logic instead of LangChain's `Command` pattern
- No integration with Deep Agents' `interrupt_on` parameter
- Manual decision parsing instead of structured `HITLRequest`/`HITLResponse`
- No `allowed_decisions` configuration per checkpoint

---

## 🏗️ **Redesign Architecture**

### **Option 1: Deep Agents Integration (Recommended)**

Use LangChain's Deep Agents framework which provides built-in HITL:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

# Define specialized tools for each RAG stage
@tool
def analyze_query(query: str) -> str:
    """Analyze query intent and extract key concepts."""
    # QueryAnalystAgent logic
    return query_analysis

@tool
def retrieve_context(query: str, analysis: dict) -> str:
    """Retrieve relevant context from vector store."""
    # RetrievalSpecialistAgent logic
    return retrieval_results

@tool
def rerank_results(results: List, query: str) -> str:
    """Re-rank and deduplicate retrieved results."""
    # ReRankerAgent logic
    return ranked_results

@tool
def assess_quality(results: List, query: str) -> str:
    """Assess quality and completeness of context."""
    # QualityAssuranceAgent logic
    return quality_report

@tool
def generate_response(context: str, query: str) -> str:
    """Generate final response from context."""
    # WriterAgent logic
    return final_response

# Create deep agent with HITL configuration
rag_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query,
        retrieve_context,
        rerank_results,
        assess_quality,
        generate_response
    ],
    interrupt_on={
        # HITL #1: Query Analysis Review
        "analyze_query": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "Review query understanding and search strategy"
        },
        
        # HITL #2: Retrieval Results Review
        "retrieve_context": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "Review retrieved sources and relevance"
        },
        
        # HITL #3: Re-ranking Review
        "rerank_results": {
            "allowed_decisions": ["approve", "reject"],
            "description": "Review ranked context quality"
        },
        
        # HITL #4: Quality Assessment Review
        "assess_quality": {
            "allowed_decisions": ["approve", "reject"],
            "description": "Review quality assessment and completeness"
        },
        
        # No interrupt for final generation (trust the writer)
        "generate_response": False
    },
    checkpointer=MemorySaver()  # Required for HITL
)
```

**Benefits:**
- ✅ LangChain-native implementation
- ✅ Structured `HITLRequest`/`HITLResponse` handling
- ✅ Built-in decision validation
- ✅ Automatic state management
- ✅ Official LangChain patterns

---

### **Option 2: LangChain HITL Middleware (Alternative)**

Use `HumanInTheLoopMiddleware` with agent harness:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

# Create agent with HITL middleware
rag_agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[
        analyze_query_tool,
        retrieve_context_tool,
        rerank_results_tool,
        assess_quality_tool,
        generate_response_tool
    ],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "analyze_query": True,  # All decisions allowed
                "retrieve_context": True,
                "rerank_results": {"allowed_decisions": ["approve", "reject"]},
                "assess_quality": {"allowed_decisions": ["approve", "reject"]},
                "generate_response": False  # No interrupt
            },
            description_prefix="RAG Stage pending review"
        )
    ],
    checkpointer=MemorySaver()
)
```

---

### **Option 3: Custom LangGraph with LangChain Patterns (Current + Enhancements)**

Keep our LangGraph implementation but align with LangChain patterns:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, Interrupt
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, Literal

class RAGState(TypedDict):
    """State for RAG workflow."""
    messages: Annotated[list, "Messages in conversation"]
    query: str
    query_analysis: dict
    retrieval_results: dict
    ranked_results: dict
    quality_report: dict
    final_response: dict
    interrupt_config: dict  # NEW: Store HITL configuration

class RAGSwarmCoordinator:
    """LangChain-compatible RAG Swarm with proper HITL patterns."""
    
    def __init__(self, context_engine, human_in_loop: bool = True):
        self.context_engine = context_engine
        self.human_in_loop = human_in_loop
        
        # HITL Configuration (LangChain-style)
        self.interrupt_config = {
            "query_analysis": {
                "allowed_decisions": ["approve", "edit", "reject"],
                "description": "Review query understanding"
            },
            "retrieval": {
                "allowed_decisions": ["approve", "edit", "reject"],
                "description": "Review retrieved context"
            },
            "re_ranking": {
                "allowed_decisions": ["approve", "reject"],
                "description": "Review ranked results"
            },
            "quality_assurance": {
                "allowed_decisions": ["approve", "reject"],
                "description": "Review quality assessment"
            }
        }
        
        # Build graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow with HITL nodes."""
        workflow = StateGraph(RAGState)
        
        # Add agent nodes
        workflow.add_node("query_analysis", self._query_analysis_node)
        workflow.add_node("query_review", self._query_review_hitl_node)
        
        workflow.add_node("retrieval", self._retrieval_node)
        workflow.add_node("retrieval_review", self._retrieval_review_hitl_node)
        
        workflow.add_node("re_ranking", self._re_ranking_node)
        workflow.add_node("ranking_review", self._ranking_review_hitl_node)
        
        workflow.add_node("quality_assurance", self._quality_assurance_node)
        workflow.add_node("quality_review", self._quality_review_hitl_node)
        
        workflow.add_node("response_generation", self._response_generation_node)
        
        # Standard flow with HITL checkpoints
        workflow.set_entry_point("query_analysis")
        workflow.add_edge("query_analysis", "query_review")
        workflow.add_conditional_edges(
            "query_review",
            self._route_after_query_review,
            {
                "retrieval": "retrieval",
                "rewrite": "query_analysis",
                "end": END
            }
        )
        
        workflow.add_edge("retrieval", "retrieval_review")
        workflow.add_conditional_edges(
            "retrieval_review",
            self._route_after_retrieval_review,
            {
                "re_ranking": "re_ranking",
                "retry": "retrieval",
                "rewrite": "query_analysis",
                "end": END
            }
        )
        
        workflow.add_edge("re_ranking", "ranking_review")
        workflow.add_conditional_edges(
            "ranking_review",
            self._route_after_ranking_review,
            {
                "quality_assurance": "quality_assurance",
                "retry": "re_ranking",
                "end": END
            }
        )
        
        workflow.add_edge("quality_assurance", "quality_review")
        workflow.add_conditional_edges(
            "quality_review",
            self._route_after_quality_review,
            {
                "response_generation": "response_generation",
                "retry": "retrieval",
                "end": END
            }
        )
        
        workflow.add_edge("response_generation", END)
        
        # Compile with checkpointer
        return workflow.compile(checkpointer=MemorySaver())
    
    def _query_review_hitl_node(self, state: RAGState) -> RAGState:
        """HITL checkpoint for query analysis review."""
        if not self.human_in_loop:
            return state  # Skip HITL if disabled
        
        # Raise interrupt using LangGraph's Interrupt class
        config = self.interrupt_config["query_analysis"]
        
        raise Interrupt({
            "action_requests": [{
                "name": "query_analysis",
                "arguments": state["query_analysis"],
                "description": self._format_query_analysis_preview(state)
            }],
            "review_configs": [{
                "action_name": "query_analysis",
                "allowed_decisions": config["allowed_decisions"]
            }]
        })
    
    def _format_query_analysis_preview(self, state: RAGState) -> str:
        """Format query analysis for human review."""
        analysis = state["query_analysis"]
        return f"""
📊 Query Analysis Results

Query: {state['query']}

Intent: {analysis.get('intent', 'unknown')}
Key Concepts: {', '.join(analysis.get('key_concepts', []))}
Search Strategy: {analysis.get('search_strategy', 'default')}

👤 Your Review:
[ ] approve - Continue to retrieval
[ ] edit - Modify analysis
[ ] reject - Rewrite query

Feedback: _________________
        """.strip()
    
    def _route_after_query_review(self, state: RAGState) -> Literal["retrieval", "rewrite", "end"]:
        """Route after query review based on human decision."""
        # Get last human message
        messages = state.get("messages", [])
        if not messages:
            return "retrieval"  # Default: continue
        
        last_msg = messages[-1]
        if not hasattr(last_msg, "type") or last_msg.type != "human":
            return "retrieval"
        
        feedback = last_msg.content.lower().strip()
        
        # Parse decision (LangChain-compatible)
        if any(word in feedback for word in ["approve", "continue", "yes", "ok"]):
            return "retrieval"
        elif any(word in feedback for word in ["reject", "rewrite", "restart"]):
            return "rewrite"
        elif any(word in feedback for word in ["edit", "refine", "modify"]):
            # TODO: Apply edits from feedback
            return "retrieval"
        else:
            return "retrieval"  # Default: continue
    
    async def execute(self, query: str, config: dict) -> dict:
        """Execute RAG workflow with HITL."""
        initial_state = {
            "messages": [{"role": "human", "content": query}],
            "query": query,
            "query_analysis": {},
            "retrieval_results": {},
            "ranked_results": {},
            "quality_report": {},
            "final_response": {},
            "interrupt_config": self.interrupt_config
        }
        
        try:
            # Stream through graph
            async for event in self.graph.astream(initial_state, config):
                if "__interrupt__" in event:
                    # Return interrupt for UI to handle
                    return {
                        "status": "interrupted",
                        "interrupt": event["__interrupt__"],
                        "thread_id": config["configurable"]["thread_id"]
                    }
            
            # Completed successfully
            return {
                "status": "success",
                "response": event.get("final_response", {}).get("response", ""),
                "thread_id": config["configurable"]["thread_id"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "thread_id": config["configurable"]["thread_id"]
            }
    
    def resume(self, thread_id: str, human_input: str, parent_run_id: str = None) -> dict:
        """Resume workflow after human review (LangChain-compatible)."""
        from langgraph.types import Command
        from langchain_core.messages import HumanMessage
        
        config = {"configurable": {"thread_id": thread_id}}
        if parent_run_id:
            config["run_id"] = parent_run_id
        
        # Use LangChain's Command pattern for resume
        command = Command(
            resume={
                "decisions": [
                    self._parse_human_decision(human_input)
                ]
            }
        )
        
        # Invoke with command
        result = self.graph.invoke(command, config=config)
        
        if "__interrupt__" in result:
            return {
                "status": "interrupted",
                "interrupt": result["__interrupt__"],
                "thread_id": thread_id
            }
        
        return {
            "status": "success",
            "response": result.get("final_response", {}).get("response", ""),
            "thread_id": thread_id
        }
    
    def _parse_human_decision(self, feedback: str) -> dict:
        """Parse human feedback into structured decision (LangChain-compatible)."""
        feedback_lower = feedback.lower().strip()
        
        if any(word in feedback_lower for word in ["approve", "continue", "yes", "ok"]):
            return {"type": "approve"}
        elif any(word in feedback_lower for word in ["reject", "no", "restart"]):
            return {"type": "reject"}
        elif any(word in feedback_lower for word in ["edit", "refine", "modify"]):
            # Extract edited content (simplified)
            return {
                "type": "edit",
                "edited_action": {
                    "name": "query_analysis",  # Context-dependent
                    "args": {"feedback": feedback}
                }
            }
        else:
            return {"type": "approve"}  # Default: approve
```

---

## 🔄 **Migration Strategy**

### **Phase 1: Deep Agents Proof-of-Concept (Week 1)**

1. **Create `agents/rag/rag_deep_agent.py`**:
   - Convert each RAG agent to a LangChain tool
   - Use `create_deep_agent` with `interrupt_on`
   - Test basic HITL flow

2. **Test with Streamlit UI**:
   - Adapt UI to handle Deep Agents' interrupt format
   - Test decision types (approve, edit, reject)
   - Validate LangSmith traces

3. **Compare with current implementation**:
   - Performance comparison
   - Trace clarity comparison
   - Developer experience comparison

### **Phase 2: Choose Best Approach (Week 1)**

**Decision Criteria:**
- **Simplicity**: Deep Agents vs. Custom LangGraph
- **Flexibility**: Can we maintain our sophisticated routing?
- **LangSmith Integration**: Which has better tracing?
- **Maintenance**: Which is easier to maintain long-term?

### **Phase 3: Full Implementation (Week 2-3)**

1. **Implement chosen approach**:
   - Complete HITL for all 5 checkpoints
   - Implement all routing logic
   - Add decision validation

2. **UI Enhancement**:
   - Structured review forms
   - Decision type selection (approve/edit/reject)
   - Context preview improvements

3. **Testing**:
   - End-to-end HITL testing
   - Multi-session persistence testing
   - LangSmith trace validation

### **Phase 4: Documentation & Training (Week 3)**

1. **Update documentation**:
   - Implementation guide
   - API reference
   - UI usage guide

2. **Create examples**:
   - Simple query with HITL
   - Complex multi-hop query
   - Long-running project

---

## 📊 **Comparison: Deep Agents vs. Custom LangGraph**

| Aspect | Deep Agents | Custom LangGraph |
|--------|-------------|------------------|
| **Setup Complexity** | ✅ Low (built-in HITL) | ⚠️ Medium (manual implementation) |
| **LangChain Compliance** | ✅ Official pattern | ⚠️ Custom pattern |
| **Flexibility** | ⚠️ Limited to tool-based | ✅ Full control over graph |
| **Routing Logic** | ⚠️ Simple approval flow | ✅ Complex conditional routing |
| **LangSmith Tracing** | ✅ Excellent | ✅ Excellent (with proper setup) |
| **State Management** | ✅ Automatic | ✅ Manual but flexible |
| **Decision Validation** | ✅ Built-in | ⚠️ Manual implementation |
| **Maintenance** | ✅ Low (official support) | ⚠️ Medium (custom code) |

---

## 🎯 **Recommended Path**

### **Hybrid Approach: Best of Both Worlds**

1. **Use Deep Agents framework** for:
   - HITL infrastructure (`interrupt_on`, decision handling)
   - Structured `HITLRequest`/`HITLResponse`
   - Decision validation

2. **Keep Custom LangGraph** for:
   - Sophisticated routing logic
   - Multi-agent coordination
   - Quality feedback loops

**Implementation:**
```python
from deepagents import create_deep_agent
from langgraph.graph import StateGraph

class RAGSwarmWithDeepAgents:
    """Hybrid: Deep Agents HITL + Custom LangGraph orchestration."""
    
    def __init__(self, context_engine):
        # Create Deep Agent for HITL infrastructure
        self.deep_agent = create_deep_agent(
            model="anthropic:claude-sonnet-4-20250514",
            tools=self._create_rag_tools(),
            interrupt_on=self._get_interrupt_config(),
            checkpointer=MemorySaver()
        )
        
        # Keep custom LangGraph for orchestration
        self.orchestrator = self._build_orchestration_graph()
    
    def _create_rag_tools(self):
        """Convert RAG agents to LangChain tools."""
        # Each agent becomes a tool with HITL configuration
        pass
    
    def _build_orchestration_graph(self):
        """Custom LangGraph for sophisticated routing."""
        # Our existing complex routing logic
        pass
```

---

## ✅ **Success Criteria**

### **Functional Requirements:**
- [ ] All 5 HITL checkpoints working
- [ ] Structured decision handling (approve/edit/reject)
- [ ] Decision validation per checkpoint
- [ ] Multi-session persistence
- [ ] Clear LangSmith traces

### **Code Quality:**
- [ ] LangChain-compatible patterns
- [ ] Type-safe state management
- [ ] Comprehensive error handling
- [ ] Unit tests for each checkpoint
- [ ] Integration tests for full workflow

### **User Experience:**
- [ ] Clear context previews at each checkpoint
- [ ] Intuitive decision selection
- [ ] Helpful feedback prompts
- [ ] Progress indication
- [ ] Error recovery

---

## 📚 **References**

- [LangChain HITL Middleware](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Deep Agents HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [LangGraph HITL Tutorial](https://langchain-ai.github.io/langgraph/tutorials/get-started/4-human-in-the-loop/)
- [LangGraph Interrupts](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [Deep Agents GitHub](https://github.com/langchain-ai/deepagents)

---

**Next Steps:**
1. Review this plan with team
2. Choose implementation approach (Deep Agents vs. Hybrid)
3. Start Phase 1: Deep Agents POC
4. Evaluate and decide on final approach


