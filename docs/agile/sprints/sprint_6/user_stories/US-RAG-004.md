# User Story: US-RAG-004 - Agentic RAG System with Tool Integration

**Epic**: EPIC-1: RAG System Enhancement  
**Sprint**: Sprint 6  
**Story Points**: 13  
**Priority**: 🔴 **HIGH**  
**Status**: ✅ DONE✅ **COMPLETED**  
**Created**: 2025-10-28  
**Started**: 2025-10-28  
**Completed**: 2025-10-28

## Story Overview

**As a** developer using the RAG system  
**I want** an integrated agentic RAG system that follows LangGraph best practices  
**So that** I can have intelligent retrieval with web search, document grading, and query rewriting

## Business Value

Transform our disconnected RAG micro-agents into a cohesive agentic RAG system that:
- Makes intelligent decisions about when to retrieve vs. respond
- Grades retrieved documents for relevance
- Rewrites queries when retrieval fails
- Integrates web search (Tavily) and Wikipedia alongside vector search
- Follows LangGraph/LangChain best practices for production readiness

## Current State Analysis

### What We Have (Disconnected)
- ✅ Individual RAG agents: QueryAnalyst, RetrievalSpecialist, ReRanker, Writer, QA
- ✅ ContextEngine with Gemini embeddings
- ✅ Qdrant vector store
- ❌ No coordinator to tie agents together
- ❌ Not using `MessagesState` (using custom Pydantic state)
- ❌ No retriever tool pattern
- ❌ No web search integration
- ❌ No document grading/rewriting flow

### What Tutorial Shows (Integrated)
Based on: https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/

- ✅ Uses `MessagesState` for message-based state
- ✅ Uses `create_retriever_tool()` pattern
- ✅ Uses `ToolNode` for retrieval
- ✅ Uses `.bind_tools()` for LLM tool access
- ✅ Uses `tools_condition` for conditional routing
- ✅ Document grading with structured output
- ✅ Query rewriting loop
- ✅ Integrated graph with conditional edges

## Acceptance Criteria

### Phase 1: Core Agentic RAG Architecture (5 points) ✅
- [x] **AC-1.1**: Create `RAGSwarmCoordinator` using `MessagesState`
- [x] **AC-1.2**: Create retriever tool from ContextEngine using `create_retriever_tool()`
- [x] **AC-1.3**: Implement `generate_query_or_respond` node with `.bind_tools([retriever_tool])`
- [x] **AC-1.4**: Add `ToolNode` for retrieval execution
- [x] **AC-1.5**: Use `tools_condition` for routing (retrieve vs. respond)

### Phase 2: Document Grading & Query Rewriting (3 points) ✅
- [x] **AC-2.1**: Implement `grade_documents` node with structured output (`GradeDocuments` schema)
- [x] **AC-2.2**: Implement `rewrite_question` node for query improvement
- [x] **AC-2.3**: Add conditional edges based on document relevance grading
- [x] **AC-2.4**: Implement retry loop: rewrite → retrieve → grade

### Phase 3: Web Search & Wikipedia Integration (3 points) ✅
- [x] **AC-3.1**: Integrate Tavily web search tool
- [x] **AC-3.2**: Integrate Wikipedia search tool
- [x] **AC-3.3**: Add tool selection logic (vector search vs. web search vs. Wikipedia)
- [x] **AC-3.4**: Combine results from multiple sources intelligently

### Phase 4: Answer Generation & Testing (2 points) ✅
- [x] **AC-4.1**: Implement `generate_answer` node with retrieved context
- [x] **AC-4.2**: Test complete flow: query → retrieve → grade → answer
- [x] **AC-4.3**: Test rewriting flow: query → retrieve → grade (fail) → rewrite → retrieve → grade → answer
- [x] **AC-4.4**: Test web search flow: query → web search → answer
- [x] **AC-4.5**: Update RAG Management App to use new coordinator

## Technical Architecture

### New Components

```python
# agents/rag/rag_swarm_coordinator.py
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Literal
import logging

logger = logging.getLogger(__name__)

class GradeDocuments(BaseModel):
    """Binary score for document relevance."""
    binary_score: Literal["yes", "no"] = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

class RAGSwarmCoordinator:
    """
    Agentic RAG system following LangGraph best practices.
    
    Architecture (from tutorials):
    1. agent: LLM with tools decides to retrieve or respond directly
    2. tools: ToolNode executes selected tools (retrieval, web search, Wikipedia)
    3. grade_documents: Assess relevance → generate_answer or rewrite_question
    4. rewrite_question: Improve query and retry retrieval
    5. generate_answer: Generate final response with retrieved context
    
    References:
    - https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/
    - https://qdrant.tech/documentation/agentic-rag-langgraph/
    """
    
    def __init__(self, context_engine: ContextEngine):
        """Initialize coordinator with ContextEngine."""
        self.context_engine = context_engine
        
        # Initialize LLM (use Gemini for consistency)
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0,
            convert_system_message_to_human=True
        )
        
        # Create tools
        self.tools = self._create_tools()
        self.tool_node = ToolNode(self.tools)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build and compile graph
        self.graph = self._build_graph()
        
        logger.info("✅ RAGSwarmCoordinator initialized with agentic RAG graph")
    
    def _create_tools(self) -> list:
        """Create all tools following Qdrant tutorial pattern."""
        tools = []
        
        # Tool 1: Project documentation retriever
        project_docs_tool = create_retriever_tool(
            self.context_engine.vector_store.as_retriever(search_kwargs={"k": 5}),
            "retrieve_project_docs",
            "Search and return information from project documentation, code, and internal knowledge base. "
            "Use for questions about the AI agent project, implementation details, and architecture."
        )
        tools.append(project_docs_tool)
        
        # Tool 2: Web search (Tavily)
        @tool("web_search")
        def web_search_tool(query: str) -> str:
            """Search the web for current information, news, latest updates, and real-time data.
            Use when the question requires recent information not in the knowledge base."""
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                search = TavilySearchResults(
                    max_results=3,
                    search_depth="advanced"
                )
                results = search.invoke({"query": query})
                return str(results)
            except Exception as e:
                return f"Web search unavailable: {e}"
        
        tools.append(web_search_tool)
        
        # Tool 3: Wikipedia search
        @tool("wikipedia_search")
        def wikipedia_tool(query: str) -> str:
            """Search Wikipedia for encyclopedic, factual, and general knowledge information.
            Use for questions about concepts, definitions, history, and general knowledge."""
            try:
                from langchain_community.tools import WikipediaQueryRun
                from langchain_community.utilities import WikipediaAPIWrapper
                
                api_wrapper = WikipediaAPIWrapper(
                    top_k_results=2,
                    doc_content_chars_max=2000
                )
                wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
                return wikipedia.invoke({"query": query})
            except Exception as e:
                return f"Wikipedia search unavailable: {e}"
        
        tools.append(wikipedia_tool)
        
        logger.info(f"✅ Created {len(tools)} tools: project_docs, web_search, wikipedia")
        return tools
    
    def _build_graph(self) -> StateGraph:
        """Build agentic RAG graph following tutorial patterns."""
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("generate_answer", self._generate_answer)
        workflow.add_node("rewrite_question", self._rewrite_question)
        
        # Entry point: start with agent
        workflow.add_edge(START, "agent")
        
        # Agent decides: use tools or respond directly
        workflow.add_conditional_edges(
            "agent",
            tools_condition,  # Built-in LangGraph routing
            {
                "tools": "tools",  # LLM called tools → execute them
                END: END  # LLM responded directly → done
            }
        )
        
        # After tool execution: grade documents
        workflow.add_conditional_edges(
            "tools",
            self._route_after_tools,  # Grade and route
            {
                "generate_answer": "generate_answer",
                "rewrite_question": "rewrite_question"
            }
        )
        
        # Generate answer → END
        workflow.add_edge("generate_answer", END)
        
        # Rewrite question → back to agent
        workflow.add_edge("rewrite_question", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: MessagesState):
        """Agent with tools - decides to retrieve or respond."""
        response = self.llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    def _route_after_tools(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """Grade documents for relevance and route accordingly."""
        messages = state["messages"]
        
        # Get original question (first user message)
        question = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                question = msg.content
                break
        
        # Get tool results (last message should be tool result)
        last_message = messages[-1]
        if hasattr(last_message, 'type') and last_message.type == 'tool':
            context = last_message.content
        else:
            # No tool results, generate answer anyway
            return "generate_answer"
        
        # Grade relevance using structured output
        GRADE_PROMPT = (
            "You are a grader assessing relevance of retrieved documents to a user question.\n"
            "Here is the retrieved document:\n\n{context}\n\n"
            "Here is the user question: {question}\n"
            "If the document contains keywords or semantic meaning related to the question, grade it as relevant.\n"
            "Give a binary score 'yes' or 'no' to indicate whether the document is relevant."
        )
        
        prompt = GRADE_PROMPT.format(question=question, context=context[:1000])  # Limit context
        
        try:
            grade = self.llm.with_structured_output(GradeDocuments).invoke([
                {"role": "user", "content": prompt}
            ])
            
            logger.info(f"📊 Document grading: {grade.binary_score}")
            
            if grade.binary_score == "yes":
                return "generate_answer"
            else:
                logger.info("📝 Documents not relevant - rewriting question")
                return "rewrite_question"
        except Exception as e:
            logger.error(f"❌ Grading failed: {e}")
            # Fallback: generate answer anyway
            return "generate_answer"
    
    def _rewrite_question(self, state: MessagesState):
        """Rewrite the original question for better retrieval."""
        messages = state["messages"]
        
        # Get original question
        question = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                question = msg.content
                break
        
        REWRITE_PROMPT = (
            "You are a question re-writer. Your task is to convert the input question to a better version "
            "that is optimized for vectorstore retrieval.\n\n"
            "Original question: {question}\n\n"
            "Formulate an improved question:"
        )
        
        prompt = REWRITE_PROMPT.format(question=question)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        logger.info(f"📝 Rewrote question: {question} → {response.content}")
        
        # Return rewritten question as new user message
        return {"messages": [{"role": "user", "content": response.content}]}
    
    def _generate_answer(self, state: MessagesState):
        """Generate final answer using retrieved context."""
        messages = state["messages"]
        
        # Get original question
        question = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                question = msg.content
                break
        
        # Get context from tool results
        context = ""
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'tool':
                context = msg.content
                break
        
        GENERATE_PROMPT = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know. "
            "Use three sentences maximum and keep the answer concise.\n\n"
            "Question: {question}\n\n"
            "Context: {context}\n\n"
            "Answer:"
        )
        
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        return {"messages": [response]}
    
    async def execute(self, query: str) -> dict:
        """Execute agentic RAG for a query."""
        logger.info(f"🚀 Executing agentic RAG for: {query[:60]}...")
        
        # Stream through graph
        final_response = None
        for event in self.graph.stream({"messages": [{"role": "user", "content": query}]}):
            for value in event.values():
                final_response = value
        
        return {
            "status": "success",
            "response": final_response["messages"][-1].content if final_response else "No response",
            "messages": final_response["messages"] if final_response else []
        }
```

### Tool Integration

**Multiple Retriever Tools Pattern** (from Qdrant tutorial):
```python
# Create multiple retriever tools - one per knowledge domain
from langchain.tools.retriever import create_retriever_tool

# Tool 1: Project documentation
project_docs_tool = create_retriever_tool(
    context_engine.vector_store.as_retriever(search_kwargs={"k": 5}),
    "retrieve_project_docs",
    "Search and return information from project documentation, code, and internal knowledge base."
)

# Tool 2: Python/LangChain documentation
python_docs_tool = create_retriever_tool(
    python_vectorstore.as_retriever(),
    "retrieve_python_docs", 
    "Search Python, LangChain, and framework documentation."
)

# Tool 3: Codebase search
codebase_tool = create_retriever_tool(
    codebase_vectorstore.as_retriever(),
    "search_codebase",
    "Search through project codebase for code examples and implementations."
)
```

**Web Search Tools**:

Option 1 - **Tavily** (Recommended - better for AI):
```python
from langchain_community.tools.tavily_search import TavilySearchResults

@tool("web_search")
def web_search_tool(query: str) -> str:
    """Search the web for current information, news, and real-time data."""
    search = TavilySearchResults(
        max_results=3,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )
    return search.invoke({"query": query})
```

Option 2 - **Brave Search** (Alternative):
```python
from langchain_community.tools import BraveSearch

@tool("brave_search")  
def brave_search_tool(query: str) -> str:
    """Search the web using Brave Search API."""
    search = BraveSearch.from_api_key(
        api_key=brave_api_key, 
        search_kwargs={"count": 3}
    )
    return search.run(query)
```

**Wikipedia**:
```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

@tool("wikipedia_search")
def wikipedia_tool(query: str) -> str:
    """Search Wikipedia for encyclopedic information."""
    api_wrapper = WikipediaAPIWrapper(
        top_k_results=2, 
        doc_content_chars_max=2000
    )
    wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
    return wikipedia.invoke({"query": query})
```

## Dependencies

### Completed
- ✅ US-RAG-001: Core RAG system with ContextEngine
- ✅ Gemini embeddings integration
- ✅ Qdrant vector store

### New Package Requirements
```bash
pip install tavily-python wikipedia
```

Add to `requirements.txt`:
```
tavily-python==0.3.3  # Web search
wikipedia==1.4.0  # Wikipedia integration
```

## Implementation Plan

### Day 1: Core Architecture (5 points)
- Create `agents/rag/rag_swarm_coordinator.py`
- Implement `MessagesState` based graph
- Create retriever tool from ContextEngine
- Implement `generate_query_or_respond` with `.bind_tools()`
- Add `ToolNode` and `tools_condition`

### Day 2: Grading & Rewriting (3 points)
- Implement `grade_documents` with structured output
- Implement `rewrite_question` node
- Add conditional routing logic
- Test retry loop

### Day 3: Web Search Integration (3 points)
- Install and configure Tavily
- Install and configure Wikipedia
- Add tools to graph
- Test multi-source retrieval

### Day 4: Integration & Testing (2 points)
- Update RAG Management App
- Comprehensive testing
- Documentation
- Performance validation

## Success Metrics

### Technical Metrics
- **Graph Execution**: Complete flow in <5 seconds
- **Relevance Grading**: 85%+ accurate document grading
- **Query Rewriting**: 70%+ improvement on retry
- **Multi-source**: Successfully combines vector + web + Wikipedia

### Business Metrics
- **Answer Quality**: 90%+ accurate responses
- **Source Diversity**: Uses web search when needed
- **User Satisfaction**: Handles complex queries effectively

## Testing Strategy

### Unit Tests
- Test each node independently
- Test conditional routing logic
- Test tool invocation

### Integration Tests
- Test complete RAG flow
- Test rewriting loop
- Test multi-source retrieval
- Test error handling

### End-to-End Tests
```python
async def test_agentic_rag_flow():
    coordinator = RAGSwarmCoordinator(context_engine)
    
    # Test vector retrieval
    result = await coordinator.execute({
        "messages": [{"role": "user", "content": "What is RAG?"}]
    })
    assert result["messages"][-1].role == "assistant"
    
    # Test web search (when needed)
    result = await coordinator.execute({
        "messages": [{"role": "user", "content": "Latest AI news today"}]
    })
    # Should use Tavily for current events
    
    # Test query rewriting
    result = await coordinator.execute({
        "messages": [{"role": "user", "content": "vague unclear query"}]
    })
    # Should trigger rewriting loop
```

## References

### Primary Tutorials
- **LangGraph Agentic RAG Tutorial**: https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/
  - Core patterns: MessagesState, create_retriever_tool, tools_condition, document grading
  
- **Qdrant Agentic RAG with LangGraph**: https://qdrant.tech/documentation/agentic-rag-langgraph/
  - Multiple retriever tools pattern
  - Web search integration with Brave
  - ToolNode implementation
  - Graph routing logic

### Tool Integration References
- **Tavily Integration**: https://docs.tavily.com/docs/python-sdk/langchain
- **Wikipedia Tool**: https://python.langchain.com/docs/integrations/tools/wikipedia
- **Brave Search**: https://pypi.org/project/langchain-brave-search/

## Definition of Done

- [ ] `RAGSwarmCoordinator` implemented following tutorial pattern
- [ ] Uses `MessagesState` for state management
- [ ] Retriever tool created from ContextEngine
- [ ] Document grading with structured output
- [ ] Query rewriting loop working
- [ ] Tavily web search integrated
- [ ] Wikipedia search integrated
- [ ] All tests passing
- [ ] RAG Management App updated
- [ ] Documentation complete
- [ ] Performance validated

## Risk Assessment

**Integration Complexity**: Medium  
*Mitigation*: Follow tutorial pattern exactly, incremental implementation

**Tool API Costs**: Low  
*Mitigation*: Tavily has free tier, configure rate limits

**State Management**: Medium  
*Mitigation*: Migrate carefully from custom state to `MessagesState`

---

**Story Status**: 📋 **READY**  
**Estimated Timeline**: 4 days  
**Next Action**: Begin Day 1 implementation - Core Architecture

**Created**: 2025-10-28  
**Sprint**: Sprint 6  
**Assignee**: AI Development Agent

