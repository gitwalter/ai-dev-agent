# Context Detection & Routing System Architecture

**Status**: 🟢 **DESIGN PHASE**  
**Related Stories**: US-RAG-009, US-RAG-010, US-DEV-RAG-001  
**Created**: 2025-10-28  
**Priority**: 🔴 **CRITICAL**

## Overview

This document describes the implementation of a **routing layer** that:
1. **Detects context** (intent/domain/entities/urgency)
2. **Selects the right tools** using Tool RAG (vector search over tool specs)
3. **Selects the right knowledge sources** using hierarchical RAG routing
4. **Supervises execution** with guardrails, fallbacks, and confidence gates

This system enables intelligent, context-aware agent behavior across:
- **RAG Swarm**: Routing queries to appropriate knowledge sources
- **Development Agent Swarm**: Selecting tools and docs for dev tasks
- **Dynamic Graph Composition**: Self-building workflows based on context

## Architecture Principles

### 1. Layered Context Detection

**First Hop = Classification Only** (No Tool Use)
- Fast semantic classifier or lightweight LLM call
- Returns: `{intent, domain, entities, urgency, sensitivity}`
- Keeps state clean and latency predictable

### 2. Tool RAG (Vector Search Over Tool Specs)

**Problem**: Dumping 30+ tools into every agent causes:
- Tool overload (too many choices)
- Context window bloat
- Reduced accuracy

**Solution**: Index tool specs in vector store, retrieve top-k matching tools
- Tool spec includes: `{name, description, input_schema, success_examples, anti_patterns, cost_estimate, avg_latency, safety_tags}`
- Embedding richer context improves retrieval accuracy

### 3. Hierarchical Knowledge Routing

**Two-Hop Retrieve**:
1. **Collection Router**: Which index/retriever? (domain-specific)
2. **Document Retrieve**: BM25 + embeddings hybrid → re-ranker → small context window

**Ranking Stack**: BM25 (fast lexical) → dense vector (semantic) → re-ranker (cross-encoder) → small context window

## System Components

### Component 1: ContextDetectionRouter

**Purpose**: Lightweight, layered classifier for intent/domain/entities

```python
class ContextDetectionRouter:
    """
    Fast context detection using semantic routing or lightweight LLM.
    
    Classification Layers:
    1. Intent: ask/transform/generate/plan/debug/review
    2. Domain: product/code/legal/agile/architecture/api
    3. Entities: extracted product names, repos, services
    4. Urgency: low/medium/high
    5. Sensitivity: public/internal/pii/safety_critical
    """
    
    def __init__(self, use_semantic_router: bool = True):
        """
        Initialize router.
        
        Args:
            use_semantic_router: If True, use semantic-router (fast, vector-based)
                                If False, use lightweight LLM classifier
        """
        if use_semantic_router:
            # Semantic-router: vector-based, very low latency
            from semantic_router import Route, RouteLayer
            
            routes = [
                Route(
                    name="code_implementation",
                    utterances=["write code", "implement", "create function", "build feature"]
                ),
                Route(
                    name="api_integration",
                    utterances=["integrate api", "connect to", "use library", "api documentation"]
                ),
                Route(
                    name="architecture_design",
                    utterances=["design architecture", "system design", "choose pattern"]
                ),
                # ... more routes
            ]
            
            self.router = RouteLayer(routes=routes)
        else:
            # Lightweight LLM classifier
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                convert_system_message_to_human=True
            )
    
    async def detect_context(self, query: str, metadata: Optional[Dict] = None) -> ContextDetection:
        """
        Detect context from query.
        
        Returns:
            ContextDetection with intent, domain, entities, urgency, sensitivity
        """
        if self.use_semantic_router:
            route = self.router(query)
            return self._semantic_route_to_context(route)
        else:
            return await self._llm_classify(query, metadata)
    
    def _semantic_route_to_context(self, route: Route) -> ContextDetection:
        """Convert semantic router result to ContextDetection."""
        # Map route name to intent/domain
        # Extract entities using NER if needed
        pass
    
    async def _llm_classify(self, query: str, metadata: Dict) -> ContextDetection:
        """Use lightweight LLM for classification."""
        prompt = self._build_classification_prompt(query, metadata)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return self._parse_classification(response.content)
```

### Component 2: ToolRAGSystem

**Purpose**: Vector search over tool specs to retrieve relevant tools

```python
class ToolRAGSystem:
    """
    RAG system for tool selection.
    
    Indexes tool specs (name, description, schema, examples) in vector store.
    Retrieves top-k relevant tools for given context.
    """
    
    def __init__(self, context_engine: ContextEngine):
        """
        Initialize Tool RAG system.
        
        Args:
            context_engine: ContextEngine for vector operations
        """
        self.context_engine = context_engine
        self.tool_collection = "tool_specs"  # Vector collection name
        self._index_all_tools()
    
    def _index_all_tools(self):
        """Index all available tools from MCP registry and LangChain tools."""
        # Get tools from:
        # 1. MCP Tool Registry (utils.mcp.server.MCPToolRegistry)
        # 2. LangChain tools (RAG tools, web search, etc.)
        
        tools = self._collect_all_tools()
        
        for tool in tools:
            tool_spec = self._build_tool_spec(tool)
            self._index_tool_spec(tool_spec)
    
    def _build_tool_spec(self, tool: Any) -> Dict[str, Any]:
        """
        Build rich tool spec for indexing.
        
        Includes:
        - name, description
        - input_schema (JSON Schema)
        - success_examples (example queries that use this tool well)
        - anti_patterns (queries that should NOT use this tool)
        - cost_estimate (API cost, latency)
        - avg_latency (expected execution time)
        - safety_tags (security, data access, etc.)
        """
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": self._extract_schema(tool),
            "success_examples": self._get_success_examples(tool),
            "anti_patterns": self._get_anti_patterns(tool),
            "cost_estimate": self._estimate_cost(tool),
            "avg_latency": self._estimate_latency(tool),
            "safety_tags": self._extract_safety_tags(tool),
            "category": self._categorize_tool(tool)
        }
    
    async def retrieve_relevant_tools(
        self, 
        context: ContextDetection, 
        top_k: int = 5
    ) -> List[Tool]:
        """
        Retrieve top-k relevant tools for given context.
        
        Args:
            context: ContextDetection from router
            top_k: Number of tools to retrieve
            
        Returns:
            List of relevant Tool objects
        """
        # Build search query from context
        search_query = self._build_search_query(context)
        
        # Vector search over tool specs
        results = await self.context_engine.similarity_search(
            collection_name=self.tool_collection,
            query=search_query,
            top_k=top_k * 2  # Get more, then filter
        )
        
        # Filter by confidence and compatibility
        filtered = self._filter_tools_by_confidence(results, context)
        
        # Return top-k
        return filtered[:top_k]
    
    def _build_search_query(self, context: ContextDetection) -> str:
        """Build search query from context."""
        parts = [
            f"Intent: {context.intent}",
            f"Domain: {context.domain}",
            f"Entities: {', '.join(context.entities)}",
            f"Task: {context.original_query}"
        ]
        return " ".join(parts)
```

### Component 3: KnowledgeRouter

**Purpose**: Hierarchical routing for knowledge sources

```python
class KnowledgeRouter:
    """
    Hierarchical knowledge routing system.
    
    Two-hop retrieve:
    1. Collection Router: Which index/retriever? (domain-specific)
    2. Document Retrieve: BM25 + embeddings hybrid
    """
    
    def __init__(self, context_engine: ContextEngine):
        """
        Initialize knowledge router.
        
        Args:
            context_engine: ContextEngine for vector operations
        """
        self.context_engine = context_engine
        
        # Knowledge source collections
        self.collections = {
            "architecture": "architecture_docs",
            "coding_guidelines": "coding_standards",
            "framework_docs": "api_documentation",
            "agile": "agile_artifacts",
            "security": "security_guidelines",
            "testing": "testing_patterns"
        }
    
    async def route_knowledge_sources(
        self, 
        context: ContextDetection,
        top_k_collections: int = 2
    ) -> List[KnowledgeSource]:
        """
        Route to knowledge sources based on context.
        
        Args:
            context: ContextDetection from router
            top_k_collections: Number of collections to retrieve from
            
        Returns:
            List of KnowledgeSource objects with retrievers
        """
        # Step 1: Route to collections (which indexes?)
        collections = self._route_to_collections(context, top_k_collections)
        
        # Step 2: Create retrievers for selected collections
        knowledge_sources = []
        for collection in collections:
            retriever = self.context_engine.get_retriever(
                collection_name=collection,
                k=8  # Documents per collection
            )
            
            knowledge_sources.append(KnowledgeSource(
                collection=collection,
                retriever=retriever,
                domain=context.domain,
                priority=self._calculate_priority(collection, context)
            ))
        
        return knowledge_sources
    
    def _route_to_collections(self, context: ContextDetection, top_k: int) -> List[str]:
        """Route to top-k collections based on domain and intent."""
        
        # Mapping: domain + intent → collections
        routing_map = {
            ("code", "generate"): ["coding_guidelines", "framework_docs"],
            ("code", "review"): ["coding_guidelines", "security"],
            ("architecture", "design"): ["architecture", "coding_guidelines"],
            ("api", "integrate"): ["framework_docs"],  # CRITICAL: Only official docs
            ("agile", "ask"): ["agile"],
            # ... more mappings
        }
        
        key = (context.domain, context.intent)
        collections = routing_map.get(key, ["all"])
        
        # Return top-k
        return collections[:top_k]
```

### Component 4: RoutingGraphBuilder

**Purpose**: LangGraph workflow integrating routing, tool selection, knowledge selection

```python
class RoutingGraphBuilder:
    """
    Build LangGraph workflow with routing layer.
    
    Graph flow:
    1. classify (intent/domain/entities)
    2. select_tools (Tool RAG)
    3. select_knowledge (Knowledge Router)
    4. plan (LLM creates step plan)
    5. execute (agent with selected tools)
    6. reflect/repair (error handler, retry)
    7. answer + citations
    """
    
    def build_graph(self, state_type: Type = MessagesState) -> StateGraph:
        """Build routing-enabled graph."""
        
        graph = StateGraph(state_type)
        
        # Routing nodes
        graph.add_node("classify", self._classify_node)
        graph.add_node("select_tools", self._select_tools_node)
        graph.add_node("select_knowledge", self._select_knowledge_node)
        graph.add_node("plan", self._plan_node)
        
        # Agent nodes
        graph.add_node("agent", self._agent_node)  # Only selected tools
        graph.add_node("tools", ToolNode())  # Execute tool calls
        
        # Reflection/repair
        graph.add_node("reflect", self._reflect_node)
        
        # Edges
        graph.add_edge(START, "classify")
        graph.add_edge("classify", "select_tools")
        graph.add_edge("select_tools", "select_knowledge")
        graph.add_edge("select_knowledge", "plan")
        graph.add_conditional_edges("plan", self._route_after_plan)
        graph.add_edge("agent", "tools")
        graph.add_conditional_edges("tools", self._route_after_tools)
        
        return graph
```

## Integration Points

### Integration 1: RAG Swarm Coordinator

**Enhancement**: Add routing layer before agent execution

```python
class EnhancedRAGSwarmCoordinator(RAGSwarmCoordinator):
    """RAG coordinator with context detection routing."""
    
    def __init__(self, context_engine: ContextEngine, **kwargs):
        super().__init__(context_engine, **kwargs)
        
        # Add routing components
        self.context_router = ContextDetectionRouter()
        self.tool_rag = ToolRAGSystem(context_engine)
        self.knowledge_router = KnowledgeRouter(context_engine)
    
    async def execute(self, query: str, thread_id: str = None):
        """Execute with routing layer."""
        
        # Step 1: Detect context
        context = await self.context_router.detect_context(query)
        
        # Step 2: Select tools (Tool RAG)
        relevant_tools = await self.tool_rag.retrieve_relevant_tools(context)
        
        # Step 3: Update agent with selected tools only
        self.llm_with_tools = self.llm.bind_tools(relevant_tools)
        
        # Step 4: Select knowledge sources
        knowledge_sources = await self.knowledge_router.route_knowledge_sources(context)
        
        # Step 5: Execute with routing (existing flow)
        # ... rest of execution
```

### Integration 2: Development Agent Swarm

**Enhancement**: Use routing for dev task tool/knowledge selection

```python
class EnhancedDevelopmentWorkflow:
    """Development workflow with context-aware routing."""
    
    def __init__(self):
        self.context_router = ContextDetectionRouter()
        self.tool_rag = ToolRAGSystem(context_engine)
        self.knowledge_router = KnowledgeRouter(context_engine)
    
    async def execute_dev_task(self, task: str, agent_type: str):
        """Execute development task with routing."""
        
        # Detect development context
        context = await self.context_router.detect_context(task)
        
        # Map to dev task type (US-RAG-009)
        dev_task_type = self._map_to_dev_task_type(context)
        
        # Select tools for dev task
        tools = await self.tool_rag.retrieve_relevant_tools(context)
        
        # Select knowledge sources for dev task
        knowledge = await self.knowledge_router.route_knowledge_sources(context)
        
        # Execute with selected tools/knowledge
        # ... agent execution
```

### Integration 3: Dynamic Graph Composer

**Enhancement**: Use routing for better task analysis

```python
class EnhancedDynamicGraphComposer(DynamicGraphComposer):
    """Dynamic composer with routing-enhanced analysis."""
    
    async def analyze_task(self, query: str, context: Optional[Dict] = None) -> TaskAnalysis:
        """Enhanced task analysis with routing."""
        
        # Step 1: Fast context detection
        detected_context = await self.context_router.detect_context(query)
        
        # Step 2: Use context for better LLM analysis
        analysis_prompt = self._build_analysis_prompt(query, detected_context)
        
        # Step 3: LLM analysis with context hints
        analysis = await self._llm_analyze(analysis_prompt)
        
        # Step 4: Enhance analysis with routing insights
        analysis.confidence = detected_context.confidence
        analysis.knowledge_sources = self._map_context_to_sources(detected_context)
        
        return analysis
```

## Safeguards & Fallbacks

### Confidence Gates

```python
class ConfidenceGate:
    """Confidence-based routing decisions."""
    
    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
    
    def check_tool_selection(self, tool_confidence: float) -> bool:
        """Check if tool selection confidence is sufficient."""
        if tool_confidence < self.min_confidence:
            # Add general "web/search" tool as fallback
            return False
        return True
    
    def check_knowledge_routing(self, routing_confidence: float) -> bool:
        """Check if knowledge routing confidence is sufficient."""
        if routing_confidence < self.min_confidence:
            # Fallback to "all" collection
            return False
        return True
```

### Latency Caps

```python
class LatencyCaps:
    """Enforce latency constraints."""
    
    def __init__(self, max_tool_calls: int = 5, per_tool_timeout: int = 30):
        self.max_tool_calls = max_tool_calls
        self.per_tool_timeout = per_tool_timeout
    
    def check_latency(self, estimated_latency: float) -> bool:
        """Check if estimated latency is acceptable."""
        if estimated_latency > self.max_latency:
            # Use fast path (semantic-router only, no LLM)
            return False
        return True
```

### Retry with Alternate Route

```python
class RetryHandler:
    """Handle failures with alternate routing."""
    
    async def handle_tool_failure(self, failed_tool: str, context: ContextDetection):
        """Retry with alternate tool route."""
        
        # Find alternate tool in same category
        alternate_tools = await self.tool_rag.find_alternates(failed_tool)
        
        # Select best alternate
        selected = await self.tool_rag.select_best_alternate(
            alternate_tools, 
            context
        )
        
        return selected
```

## Evaluation & Telemetry

### Metrics to Track

```python
class RoutingMetrics:
    """Track routing performance."""
    
    def __init__(self):
        self.metrics = {
            "route_accuracy": [],  # Chosen route vs. human-labeled
            "tool_precision": [],  # Was right tool in top-k?
            "tool_recall": [],     # Did we miss any critical tools?
            "knowledge_accuracy": [],  # Correct knowledge sources?
            "latency_by_route": {},    # Latency per route type
            "confidence_scores": [],   # Confidence vs. actual success
        }
    
    def log_routing_decision(self, decision: RoutingDecision):
        """Log routing decision for analysis."""
        self.metrics["route_accuracy"].append({
            "chosen": decision.route,
            "correct": decision.human_labeled_route,
            "confidence": decision.confidence
        })
    
    def log_tool_selection(self, selection: ToolSelection):
        """Log tool selection for analysis."""
        self.metrics["tool_precision"].append({
            "selected": selection.selected_tools,
            "relevant": selection.relevant_tools,
            "precision": self._calculate_precision(selection)
        })
```

## Implementation Roadmap

### Phase 1: Core Routing Infrastructure (Week 1)
- [ ] Implement `ContextDetectionRouter` with semantic-router
- [ ] Implement `ToolRAGSystem` with tool spec indexing
- [ ] Implement `KnowledgeRouter` with collection routing
- [ ] Create vector collection for tool specs

### Phase 2: Integration with RAG Swarm (Week 2)
- [ ] Enhance `RAGSwarmCoordinator` with routing layer
- [ ] Add confidence gates and fallbacks
- [ ] Test tool selection accuracy
- [ ] Test knowledge routing accuracy

### Phase 3: Integration with Development Swarm (Week 3)
- [ ] Enhance development workflow with routing
- [ ] Map dev task types to tools/knowledge (US-RAG-009)
- [ ] Test dev task routing accuracy
- [ ] Add telemetry and evaluation

### Phase 4: Dynamic Graph Enhancement (Week 4)
- [ ] Enhance `DynamicGraphComposer` with routing
- [ ] Self-optimization based on routing metrics
- [ ] Comprehensive testing and documentation

## Success Criteria

- **Route Accuracy**: > 85% correct route selection
- **Tool Precision**: > 80% of selected tools are relevant
- **Tool Recall**: > 90% of critical tools included
- **Knowledge Accuracy**: > 85% correct knowledge source selection
- **Latency**: Routing layer adds < 2 seconds overhead
- **Confidence Correlation**: High confidence = high success rate (> 0.8)

## References

- LangChain Routing: https://python.langchain.com/docs/how_to/routing/
- Semantic-Router: https://github.com/aurelio-labs/semantic-router
- LlamaIndex Routers: https://docs.llamaindex.ai/en/stable/module_guides/querying/router/
- LangGraph Cheatsheet: https://sumanmichael.github.io/langgraph-cheatsheet/
- Context Engineering Blog: https://blog.langchain.com/context-engineering-for-agents/

