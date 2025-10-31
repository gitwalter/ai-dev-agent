# User Story: US-CONTEXT-001 - Context Detection & Routing System

**Epic**: EPIC-1: RAG System Enhancement  
**Sprint**: Sprint 7 (Week 3-4)  
**Total Story Points**: 39 (was 34, +5 for HITL & Memory)  
**Priority**: 🔴 **CRITICAL**  
**Status**: 📋 **BACKLOG**  
**Created**: 2025-10-28  
**Dependencies**: US-RAG-005 (Sophisticated Multi-Agent), US-RAG-006 (HITL Architecture)  
**Blocks**: US-RAG-009 (Dev-Context RAG), US-RAG-010 (Dynamic Graph), US-DEV-RAG-001 (RAG-Enhanced Dev Workflow)

## Story Overview

**As a** developer using the agent swarm system  
**I want** intelligent context detection and routing that selects the right tools and knowledge sources  
**So that** agents make smarter decisions with less context window bloat and better accuracy

## Business Value

Transform agent systems from "dump all tools" to **intelligent, context-aware routing**:

1. **Tool Overload Prevention**: Instead of 30+ tools, agents get only 3-5 relevant tools
2. **Knowledge Source Efficiency**: Routes to correct knowledge collections before document retrieval
3. **Better Accuracy**: Context-aware routing improves tool/knowledge selection accuracy
4. **Lower Latency**: Fast semantic routing reduces classification overhead
5. **Self-Optimization**: Routing metrics enable continuous improvement

**Benefits**:
- **Reduced Context Window**: Smaller tool sets = more room for actual content
- **Higher Accuracy**: Right tools + right knowledge = better results
- **Faster Execution**: Semantic routing is faster than LLM classification
- **Debuggable**: Explicit routing decisions visible in traces
- **Adaptive**: System learns from routing metrics

## Current State vs. Desired State

### Current State
- ❌ All tools registered at once (tool overload)
- ❌ All knowledge sources searched (inefficient)
- ❌ No context detection (one-size-fits-all)
- ❌ No tool/knowledge routing
- ❌ No confidence gates or fallbacks

### Desired State
- ✅ Context detection (intent/domain/entities) before any action
- ✅ Tool RAG (vector search over tool specs)
- ✅ Knowledge routing (select collections before docs)
- ✅ Confidence gates (fallback when confidence low)
- ✅ Routing metrics (evaluate and improve)

## Architecture Overview

### 1. Context Detection Router
**Purpose**: Fast classification (intent/domain/entities/urgency/sensitivity)

**Options**:
- **Semantic-Router**: Vector-based, very low latency (preferred for high-QPS)
- **Lightweight LLM**: Small model for classification (fallback)

**Output**: `ContextDetection {intent, domain, entities, urgency, sensitivity, confidence}`

### 2. Tool RAG System
**Purpose**: Vector search over tool specs to retrieve relevant tools

**Tool Spec Indexed**:
```python
{
    "name": "tool_name",
    "description": "...",
    "input_schema": {...},  # JSON Schema
    "success_examples": [...],  # Example queries
    "anti_patterns": [...],  # What NOT to use for
    "cost_estimate": "...",
    "avg_latency": 0.5,
    "safety_tags": [...]
}
```

**Process**: Query → Vector Search → Filter by Confidence → Return Top-K

### 3. Knowledge Router
**Purpose**: Hierarchical routing (collection → documents)

**Two-Hop Retrieve**:
1. **Collection Router**: Which index? (architecture, coding_guidelines, framework_docs, agile)
2. **Document Retrieve**: BM25 + embeddings → re-ranker → small context window

### 4. Routing Graph Builder
**Purpose**: LangGraph workflow with routing layer

**Graph Flow**:
```
START
  ↓
classify (detect context)
  ↓
select_tools (Tool RAG)
  ↓
select_knowledge (Knowledge Router)
  ↓
plan (LLM creates step plan)
  ↓
execute (agent with selected tools)
  ↓
reflect/repair (error handler)
  ↓
END
```

## Acceptance Criteria

### Phase 0: HITL Context Review & Persistent Memory (5 points)
- [ ] **AC-0.1**: Implement `review_context_detection_node` for HITL checkpoint
- [ ] **AC-0.2**: Implement `refine_context_node` for context refinement
- [ ] **AC-0.3**: Integrate with ThreadManager using standard LangGraph config pattern
- [ ] **AC-0.4**: Add conversation loop for context refinement
- [ ] **AC-0.5**: Store context in LangGraph state (SwarmState) - automatic persistence via checkpointer
- [ ] **AC-0.6**: Load context using `graph.get_state(config)` standard pattern
- [ ] **AC-0.7**: Test context persistence across sessions using LangGraph patterns
- [ ] **AC-0.8**: Verify NO custom memory storage (use LangGraph state only)

### Phase 1: Context Detection Router (8 points)
- [ ] **AC-1.1**: Implement `ContextDetectionRouter` class
- [ ] **AC-1.2**: Support semantic-router (vector-based, fast)
- [ ] **AC-1.3**: Support lightweight LLM classifier (fallback)
- [ ] **AC-1.4**: Classify intent (ask/transform/generate/plan/debug/review)
- [ ] **AC-1.5**: Classify domain (product/code/legal/agile/architecture/api)
- [ ] **AC-1.6**: Extract entities (product names, repos, services)
- [ ] **AC-1.7**: Detect urgency (low/medium/high)
- [ ] **AC-1.8**: Detect sensitivity (public/internal/pii/safety_critical)

### Phase 2: Tool RAG System (10 points)
- [ ] **AC-2.1**: Implement `ToolRAGSystem` class
- [ ] **AC-2.2**: Collect all tools from MCP registry and LangChain tools
- [ ] **AC-2.3**: Build rich tool specs (name, description, schema, examples, anti-patterns)
- [ ] **AC-2.4**: Index tool specs in vector store (Qdrant collection: "tool_specs")
- [ ] **AC-2.5**: Implement `retrieve_relevant_tools()` method
- [ ] **AC-2.6**: Vector search over tool specs
- [ ] **AC-2.7**: Filter by confidence and compatibility
- [ ] **AC-2.8**: Return top-k relevant tools
- [ ] **AC-2.9**: Support tool spec updates (re-index when tools change)
- [ ] **AC-2.10**: Add success examples and anti-patterns for each tool

### Phase 3: Knowledge Router (8 points)
- [ ] **AC-3.1**: Implement `KnowledgeRouter` class
- [ ] **AC-3.2**: Define knowledge source collections (architecture, coding_guidelines, framework_docs, agile, security, testing)
- [ ] **AC-3.3**: Implement collection routing (domain + intent → collections)
- [ ] **AC-3.4**: Create retrievers for selected collections
- [ ] **AC-3.5**: Support two-hop retrieve (collection → documents)
- [ ] **AC-3.6**: Implement ranking stack (BM25 → dense vector → re-ranker)
- [ ] **AC-3.7**: Calculate priority for knowledge sources
- [ ] **AC-3.8**: Support custom collection mapping

### Phase 4: Routing Graph Integration (8 points)
- [ ] **AC-4.1**: Implement `RoutingGraphBuilder` class
- [ ] **AC-4.2**: Build LangGraph workflow with routing nodes
- [ ] **AC-4.3**: Integrate classify → select_tools → select_knowledge → plan → execute flow
- [ ] **AC-4.4**: Add conditional routing after plan (agent vs. direct answer)
- [ ] **AC-4.5**: Add conditional routing after tools (success vs. repair)
- [ ] **AC-4.6**: Support reflection/repair node
- [ ] **AC-4.7**: Test full routing workflow end-to-end
- [ ] **AC-4.8**: Verify routing decisions visible in LangSmith traces

### Phase 5: Safeguards & Fallbacks (5 points)
- [ ] **AC-5.1**: Implement `ConfidenceGate` class
- [ ] **AC-5.2**: Check tool selection confidence (< threshold → add fallback tool)
- [ ] **AC-5.3**: Check knowledge routing confidence (< threshold → use "all" collection)
- [ ] **AC-5.4**: Implement `LatencyCaps` class (max_tool_calls, per_tool_timeout)
- [ ] **AC-5.5**: Implement `RetryHandler` for alternate tool routes

### Phase 6: Evaluation & Telemetry (5 points)
- [ ] **AC-6.1**: Implement `RoutingMetrics` class
- [ ] **AC-6.2**: Track route accuracy (chosen vs. human-labeled)
- [ ] **AC-6.3**: Track tool precision/recall (selected vs. relevant)
- [ ] **AC-6.4**: Track knowledge accuracy (correct sources selected)
- [ ] **AC-6.5**: Track latency by route type
- [ ] **AC-6.6**: Log routing decisions for auditability

## Technical Implementation

### Files Created

```
agents/routing/
├── __init__.py
├── context_detection_router.py    # ContextDetectionRouter
├── tool_rag_system.py             # ToolRAGSystem
├── knowledge_router.py             # KnowledgeRouter
├── routing_graph_builder.py       # RoutingGraphBuilder
├── confidence_gates.py             # ConfidenceGate, LatencyCaps
└── routing_metrics.py             # RoutingMetrics

docs/architecture/
└── CONTEXT_DETECTION_ROUTING_SYSTEM.md  # This architecture doc
```

### Files Modified

```
agents/rag/
├── rag_swarm_coordinator.py       # Add routing layer
└── dynamic_graph_composer.py     # Enhance with routing

workflow/
└── langgraph_workflow.py         # Add routing to dev workflow

agents/development/
├── architecture_designer.py      # Use routing for tool/knowledge selection
├── code_generator.py             # Use routing for tool/knowledge selection
└── code_reviewer.py              # Use routing for tool/knowledge selection
```

### Dependencies

**New Packages**:
```python
# semantic-router (optional, fast routing)
semantic-router>=0.2.0

# Already have:
langchain>=0.1.0
langgraph>=0.1.0
qdrant-client>=1.7.0
```

## Integration with Existing Stories

### US-RAG-009 (Dev-Context RAG)
**Integration**: Use routing to map dev task types to tools/knowledge sources
- Context detection identifies dev task type
- Tool RAG selects dev-specific tools
- Knowledge router routes to dev knowledge collections

### US-RAG-010 (Dynamic Graph)
**Integration**: Use routing for better task analysis
- Context detection provides hints for LLM analysis
- Tool/knowledge routing informs graph composition
- Routing metrics enable self-optimization

### US-DEV-RAG-001 (RAG-Enhanced Dev Workflow)
**Integration**: Route dev agents to correct tools/knowledge
- Architecture Designer → architecture knowledge + design tools
- Code Generator → coding standards + code generation tools
- Code Reviewer → security guidelines + review tools

## CRITICAL: Use Only LangGraph Standard Patterns

**DO NOT reinvent the wheel!** Use ONLY LangGraph's standard patterns:

✅ **LangGraph State (TypedDict)**: Store context in `SwarmState`  
✅ **MemorySaver Checkpointer**: Standard LangGraph checkpointer  
✅ **ThreadManager**: Use existing `utils.thread_manager.ThreadManager`  
✅ **Standard Config**: `{"configurable": {"thread_id": "..."}}`  
✅ **State Loading**: Use `graph.get_state(config)`  
✅ **State Persistence**: Automatic via checkpointer  

❌ **NO custom memory storage**  
❌ **NO custom persistence systems**  
❌ **NO custom thread management**  
❌ **NO reinventing the wheel**

### Unit Tests
- [ ] Test context detection accuracy (intent/domain)
- [ ] Test tool RAG retrieval (correct tools selected)
- [ ] Test knowledge routing (correct collections selected)
- [ ] Test confidence gates (fallbacks triggered correctly)

### Integration Tests
- [ ] Test routing workflow end-to-end
- [ ] Test RAG swarm with routing layer
- [ ] Test development workflow with routing
- [ ] Test dynamic graph with routing

### Evaluation Tests
- [ ] Measure route accuracy (> 85% target)
- [ ] Measure tool precision/recall (> 80% precision, > 90% recall)
- [ ] Measure knowledge accuracy (> 85% target)
- [ ] Measure latency overhead (< 2 seconds)

## Definition of Done

- [ ] All routing components implemented
- [ ] Routing integrated with RAG swarm
- [ ] Routing integrated with development workflow
- [ ] Routing integrated with dynamic graph composer
- [ ] Confidence gates and fallbacks working
- [ ] Routing metrics tracking implemented
- [ ] All tests passing (unit + integration + evaluation)
- [ ] Documentation complete
- [ ] LangSmith traces show routing decisions

## Success Metrics

- **Route Accuracy**: > 85% correct route selection
- **Tool Precision**: > 80% of selected tools are relevant
- **Tool Recall**: > 90% of critical tools included
- **Knowledge Accuracy**: > 85% correct knowledge source selection
- **Latency**: Routing layer adds < 2 seconds overhead
- **Confidence Correlation**: High confidence = high success rate (> 0.8)

## Notes

**Key Insight**: Routing layer enables intelligent, context-aware agent behavior without tool overload or knowledge bloat.

**Semantic-Router vs. LLM**: Use semantic-router for fast, high-QPS routing. Use lightweight LLM for complex classification when needed.

**Tool Spec Richness**: Including success examples and anti-patterns in tool specs dramatically improves retrieval accuracy.

**Two-Hop Knowledge**: Routing to collections first, then documents, is more efficient than searching everything.

**Future**: Routing metrics enable self-optimization - the system learns which routes work best for which contexts.

