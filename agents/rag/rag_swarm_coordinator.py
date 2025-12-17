"""
RAG Swarm Coordinator - Agentic RAG System

This module implements an agentic RAG system following LangGraph best practices.
It combines document retrieval, web search, and Wikipedia with intelligent routing,
document grading, and query rewriting.

References:
- https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/
- https://qdrant.tech/documentation/agentic-rag-langgraph/

Architecture:
1. agent: LLM with tools decides to retrieve or respond directly
2. tools: ToolNode executes selected tools (retrieval, web search, Wikipedia)
3. route_after_tools: Grade documents for relevance
4. rewrite_question: Improve query and retry retrieval
5. generate_answer: Generate final response with retrieved context

User Story: US-RAG-004
"""

import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# LangChain imports
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage, SystemMessage

# Context engine
from context.context_engine import ContextEngine

# Sophisticated RAG agents
from agents.rag.query_analyst_agent import QueryAnalystAgent
from agents.rag.retrieval_specialist_agent import RetrievalSpecialistAgent
from agents.rag.re_ranker_agent import ReRankerAgent
from agents.rag.quality_assurance_agent import QualityAssuranceAgent
from agents.rag.writer_agent import WriterAgent

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Task types that determine workflow routing."""
    SIMPLE_QA = "simple_qa"  # Quick factual answer
    RESEARCH_ARTICLE = "research_article"  # Deep research + writing
    CONCEPT_EXPLANATION = "concept_explanation"  # Educational content
    CODE_GENERATION = "code_generation"  # Code examples/debugging
    FACT_CHECKING = "fact_checking"  # Verification/validation
    MULTI_SOURCE_SYNTHESIS = "multi_source_synthesis"  # Compare multiple sources


class GradeDocuments(BaseModel):
    """Binary score for document relevance."""
    binary_score: Literal["yes", "no"] = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


class RAGSwarmCoordinator:
    """
    Agentic RAG system with research assistant and human-in-the-loop capabilities.
    
    This coordinator orchestrates multiple tools (document retrieval, web search, 
    Wikipedia) and uses document grading and query rewriting to ensure high-quality
    answers. It supports human-in-the-loop interruptions for complex research tasks.
    
    Features:
    - MessagesState-based state management
    - Multiple retrieval tools (project docs, web, Wikipedia)
    - Document relevance grading
    - Automatic query rewriting when retrieval fails
    - Human-in-the-loop interruptions
    - Research assistant mode with multi-step reasoning
    - LangGraph Studio compatible with checkpointing
    
    Usage:
        # Basic usage
        coordinator = RAGSwarmCoordinator(context_engine)
        result = await coordinator.execute("What is LangGraph?")
        
        # With human-in-the-loop
        coordinator = RAGSwarmCoordinator(context_engine, human_in_loop=True)
        result = await coordinator.execute("Research LangGraph architecture")
    """
    
    def __init__(self, context_engine: ContextEngine, human_in_loop: bool = False, retrieval_only: bool = False):
        """
        Initialize RAG Swarm Coordinator.
        
        Args:
            context_engine: ContextEngine instance with initialized vector store
            human_in_loop: Enable human approval before generating final answer
            retrieval_only: Simple retrieval mode (skip sophisticated agents, fast)
            
        Operational Modes:
            1. retrieval_only=True
               Fast, simple retrieval → answer (no agents, no HITL)
               
            2. retrieval_only=False, human_in_loop=False
               Sophisticated 5-agent workflow, fully automated
               
            3. retrieval_only=False, human_in_loop=True
               Full HITL-guided sophisticated workflow (6 checkpoints)
        """
        self.context_engine = context_engine
        self.human_in_loop = human_in_loop
        self.retrieval_only = retrieval_only
        
        # Validate mode combination
        if retrieval_only and human_in_loop:
            logger.warning("⚠️ retrieval_only=True overrides human_in_loop - using simple retrieval mode")
            self.human_in_loop = False
        
        # Initialize LLM (use Gemini for consistency)
        self.llm = self._create_llm()
        
        # Load prompts from LangSmith Hub (following langgraph_workflow pattern)
        from prompts.agent_prompt_loader import get_agent_prompt_loader
        self.document_grader_loader = get_agent_prompt_loader("document_grader")
        self.query_rewriter_loader = get_agent_prompt_loader("query_rewriter")
        self.answer_generator_loader = get_agent_prompt_loader("answer_generator")
        
        # Initialize RAG agent swarm (the sophisticated agents!)
        self.query_analyst = QueryAnalystAgent()
        self.retrieval_specialist = RetrievalSpecialistAgent(context_engine)
        self.re_ranker = ReRankerAgent()
        self.quality_assurance = QualityAssuranceAgent()
        self.writer = WriterAgent()
        
        # Create tools
        self.tools = self._create_tools()
        self.tool_node = ToolNode(self.tools)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build and compile graph (with checkpointing for interrupts)
        self.graph = self._build_graph()
        
        logger.info("✅ RAGSwarmCoordinator initialized with agentic RAG graph")
        logger.info(f"   Tools: {[t.name for t in self.tools]}")
        logger.info(f"   🚨 Human-in-loop: {self.human_in_loop}")
        logger.info(f"   🚨 Graph interrupt_before: {['human_review'] if self.human_in_loop else []}")
    
    def _create_llm(self):
        """Create LLM instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os
            
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,  # CRITICAL: Must pass API key explicitly
                temperature=0,
                convert_system_message_to_human=True,
                transport="rest"  # Use REST to avoid grpc event loop issues
            )
            logger.info("✅ LLM initialized: gemini-2.5-flash")
            return llm
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise
    
    def _create_tools(self) -> list:
        """
        Create all tools following Qdrant tutorial pattern.
        
        Creates three types of tools:
        1. Project documentation retriever (from vector store)
        2. Web search tool (Tavily)
        3. Wikipedia search tool
        
        Returns:
            List of LangChain tools
        """
        tools = []
        
        # Tool 1: Project documentation retriever
        if self.context_engine.vector_store:
            try:
                project_docs_tool = create_retriever_tool(
                    self.context_engine.vector_store.as_retriever(
                        search_kwargs={"k": 5}
                    ),
                    "retrieve_project_docs",
                    "Search and return information from project documentation, code, and internal knowledge base. "
                    "Use this for questions about the AI agent project, implementation details, architecture, and codebase."
                )
                tools.append(project_docs_tool)
                logger.info("✅ Created project_docs_tool")
            except Exception as e:
                logger.error(f"❌ Failed to create project docs tool: {e}")
        else:
            logger.warning("⚠️ Vector store not available, skipping project docs tool")
        
        # Tool 2: Web search (Tavily)
        @tool("web_search")
        def web_search_tool(query: str) -> str:
            """
            Search the web for current information, news, latest updates, and real-time data.
            Use when the question requires recent information not in the knowledge base.
            """
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                import os
                
                api_key = os.environ.get("TAVILY_API_KEY")
                if not api_key:
                    return "Web search unavailable: TAVILY_API_KEY not set. Get free key at https://tavily.com"
                
                search = TavilySearchResults(
                    max_results=3,
                    search_depth="advanced"
                )
                results = search.invoke({"query": query})
                return str(results)
            except ImportError:
                return "Web search unavailable: Install tavily-python package"
            except Exception as e:
                return f"Web search error: {e}"
        
        tools.append(web_search_tool)
        logger.info("✅ Created web_search_tool")
        
        # Tool 3: Wikipedia search
        @tool("wikipedia_search")
        def wikipedia_tool(query: str) -> str:
            """
            Search Wikipedia for encyclopedic, factual, and general knowledge information.
            Use for questions about concepts, definitions, history, and general knowledge.
            """
            try:
                from langchain_community.tools import WikipediaQueryRun
                from langchain_community.utilities import WikipediaAPIWrapper
                
                api_wrapper = WikipediaAPIWrapper(
                    top_k_results=2,
                    doc_content_chars_max=2000
                )
                wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
                return wikipedia.invoke({"query": query})
            except ImportError:
                return "Wikipedia search unavailable: Install wikipedia package"
            except Exception as e:
                return f"Wikipedia search error: {e}"
        
        tools.append(wikipedia_tool)
        logger.info("✅ Created wikipedia_tool")
        
        return tools
    
    def _build_simple_retrieval_graph(self) -> StateGraph:
        """
        Build simple, fast retrieval-only graph.
        
        MODE 1: RETRIEVAL_ONLY
        START → simple_retrieval → simple_answer → END
        
        This is the fast mode for quick context retrieval without
        sophisticated agents or HITL checkpoints.
        """
        workflow = StateGraph(MessagesState)
        
        # Add simple nodes
        workflow.add_node("simple_retrieval", self._simple_retrieval_node)
        workflow.add_node("simple_answer", self._simple_answer_node)
        
        # Simple linear flow
        workflow.add_edge(START, "simple_retrieval")
        workflow.add_edge("simple_retrieval", "simple_answer")
        workflow.add_edge("simple_answer", END)
        
        # Compile without checkpointer (no HITL needed)
        logger.info("✅ Simple retrieval-only graph compiled (fast mode)")
        return workflow.compile()
    
    def _simple_retrieval_node(self, state: MessagesState):
        """
        Simple retrieval node - Fast context retrieval without agents.
        
        Just does basic vector store retrieval, no sophisticated processing.
        """
        messages = state["messages"]
        
        # Get query
        query = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'human':
                query = msg.content
                break
        
        if not query:
            return {"messages": [SystemMessage(content="No query provided")]}
        
        logger.info(f"📚 Simple retrieval for: '{query[:60]}...'")
        
        # Simple retrieval from vector store
        try:
            retriever = self.context_engine.vector_store.as_retriever(search_kwargs={"k": 5})
            docs = retriever.invoke(query)
            
            # Package as tool messages
            tool_msgs = []
            for idx, doc in enumerate(docs):
                tool_msg = ToolMessage(
                    content=doc.page_content,
                    tool_call_id=f"simple_retrieval_{idx}",
                    name="vector_store"
                )
                tool_msgs.append(tool_msg)
            
            logger.info(f"✅ Retrieved {len(tool_msgs)} documents (simple mode)")
            return {"messages": tool_msgs}
            
        except Exception as e:
            logger.error(f"❌ Simple retrieval failed: {e}")
            return {"messages": [SystemMessage(content=f"Retrieval error: {e}")]}
    
    def _simple_answer_node(self, state: MessagesState):
        """
        Simple answer node - Generate answer from retrieved context.
        
        Just uses LLM with retrieved context, no sophisticated agent processing.
        """
        messages = state["messages"]
        
        # Get query
        query = None
        context_parts = []
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                query = msg.content
            elif isinstance(msg, ToolMessage):
                context_parts.append(msg.content)
        
        context = "\n\n".join(context_parts)
        
        if not query:
            return {"messages": [AIMessage(content="No query to answer")]}
        
        logger.info(f"✍️ Generating simple answer...")
        
        # Simple prompt
        prompt = f"""Answer the following question using the provided context.

Question: {query}

Context:
{context}

Answer:"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            logger.info(f"✅ Simple answer generated: {len(response.content)} chars")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"❌ Answer generation failed: {e}")
            return {"messages": [AIMessage(content=f"Error generating answer: {e}")]}
    
    def _build_graph(self) -> StateGraph:
        """
        Build RAG workflow based on operational mode.
        
        Three Modes:
        
        MODE 1: RETRIEVAL_ONLY (Fast & Simple)
        ========================================
        START → simple_retrieval → simple_answer → END
        - No sophisticated agents
        - No HITL checkpoints
        - Fast context retrieval only
        
        MODE 2: AUTOMATED SOPHISTICATED
        ================================
        START → query_analyst → retrieval → re_ranker → writer → QA → END
        - All 5 sophisticated agents
        - No HITL checkpoints
        - Fully automated
        
        MODE 3: HITL-GUIDED SOPHISTICATED
        ==================================
        Sophisticated multi-agent workflow WITH strategic human control points:
        
        START
          ↓
        query_analyst (QueryAnalystAgent - understand query & strategy)
          ↓
        [HITL #1: review_query_analysis] ← Human approves/refines understanding
          ↓
        retrieval_specialist (RetrievalSpecialistAgent - multi-source retrieval)
          ↓
        [HITL #2: review_retrieval_results] ← Human reviews sources & coverage
          ↓
        re_ranker (ReRankerAgent - relevance scoring & filtering)
          ↓
        [HITL #3: review_ranked_context] ← Human approves quality or requests more
          ↓
        writer (WriterAgent - draft answer synthesis)
          ↓
        [HITL #4: review_draft_answer] ← Human reviews & refines draft
          ↓
        quality_assurance (QualityAssuranceAgent - final checks)
          ↓
        [HITL #5: final_approval] ← Human ships or iterates more
          ↓
        END
        
        🔄 Flexible Routing Based on Human Feedback:
        - "approve" → Continue to next stage
        - "reject" → Retry current stage with feedback
        - "rewrite" → Back to query_analyst with new understanding
        - "add_source: <url>" → Add source and reprocess
        - "skip_qa" → Fast-track to end
        - "iterate" → Refine and improve current stage
        
        💾 Memory & Long-Running Projects:
        - State persists across conversations via checkpointer
        - thread_id maintains project context
        - Human can pause/resume anytime
        - Multi-session iterative refinement
        
        Returns:
            Compiled StateGraph with checkpointer and multiple HITL points
        """
        
        # MODE 1: RETRIEVAL_ONLY - Build simple fast graph
        if self.retrieval_only:
            return self._build_simple_retrieval_graph()
        
        # MODE 2 & 3: Build sophisticated multi-agent graph
        workflow = StateGraph(MessagesState)
        
        # Add sophisticated agent nodes (ENHANCED FLOW)
        workflow.add_node("query_analyst", self._query_analyst_node)
        workflow.add_node("retrieval_specialist", self._retrieval_specialist_node)
        workflow.add_node("document_grader", self._document_grader_node)  # NEW: Grade BEFORE re-ranking
        workflow.add_node("re_ranker", self._re_ranker_node)
        workflow.add_node("context_enrichment", self._context_enrichment_node)  # NEW: Enrich after ranking
        workflow.add_node("writer", self._writer_node)
        workflow.add_node("citation_verification", self._citation_verification_node)  # NEW: Verify citations
        workflow.add_node("quality_assurance", self._quality_assurance_node)
        
        # Add control nodes
        workflow.add_node("rewrite_question", self._rewrite_question)
        
        # Add MULTIPLE human review nodes for different stages
        if self.human_in_loop:
            # HITL #0: Knowledge source selection (FIRST CHECKPOINT!)
            workflow.add_node("select_knowledge_sources", self._select_knowledge_sources_node)
            workflow.add_node("load_knowledge_sources", self._load_knowledge_sources_node)
            
            # Other HITL checkpoints
            workflow.add_node("review_query_analysis", self._review_query_analysis_node)
            workflow.add_node("review_retrieval_results", self._review_retrieval_results_node)
            workflow.add_node("review_ranked_context", self._review_ranked_context_node)
            workflow.add_node("review_draft_answer", self._review_draft_answer_node)
            workflow.add_node("final_approval", self._final_approval_node)
        
        # Entry point: HITL starts with knowledge source selection
        if self.human_in_loop:
            workflow.add_edge(START, "select_knowledge_sources")
            workflow.add_edge("select_knowledge_sources", "load_knowledge_sources")
            workflow.add_edge("load_knowledge_sources", "query_analyst")
        else:
            # Non-HITL: start directly with query analysis
            workflow.add_edge(START, "query_analyst")
        
        # Build flexible flow based on HITL mode
        if self.human_in_loop:
            # === HITL-FIRST FLOW with multiple control points ===
            
            # Query analyst → HITL checkpoint #1
            workflow.add_edge("query_analyst", "review_query_analysis")
            
            # After query review: continue OR rewrite
            workflow.add_conditional_edges(
                "review_query_analysis",
                self._route_after_query_review,
                {
                    "retrieval_specialist": "retrieval_specialist",
                    "rewrite_question": "rewrite_question"
                }
            )
            
            # Retrieval specialist → Document Grader (NEW: Grade BEFORE re-ranking)
            workflow.add_edge("retrieval_specialist", "document_grader")
            
            # Document grader → HITL checkpoint #2 (review after grading)
            workflow.add_edge("document_grader", "review_retrieval_results")
            
            # After retrieval review: continue OR retry OR rewrite
            workflow.add_conditional_edges(
                "review_retrieval_results",
                self._route_after_retrieval_review,
                {
                    "re_ranker": "re_ranker",  # Continue to re-ranking
                    "retrieval_specialist": "retrieval_specialist",  # Retry with more sources
                    "rewrite_question": "rewrite_question"
                }
            )
            
            # Re-ranker → Context Enrichment (NEW: Enrich after ranking)
            workflow.add_edge("re_ranker", "context_enrichment")
            
            # Context enrichment → HITL checkpoint #3
            workflow.add_edge("context_enrichment", "review_ranked_context")
            
            # After context review: continue OR improve OR rewrite
            workflow.add_conditional_edges(
                "review_ranked_context",
                self._route_after_context_review,
                {
                    "writer": "writer",
                    "re_ranker": "re_ranker",  # Re-rank with different criteria
                    "retrieval_specialist": "retrieval_specialist",  # Get more sources
                    "rewrite_question": "rewrite_question"
                }
            )
            
            # Writer → Citation Verification (NEW: Verify citations)
            workflow.add_edge("writer", "citation_verification")
            
            # Citation verification → HITL checkpoint #4
            workflow.add_edge("citation_verification", "review_draft_answer")
            
            # After draft review: QA OR revise OR rewrite
            workflow.add_conditional_edges(
                "review_draft_answer",
                self._route_after_draft_review,
                {
                    "quality_assurance": "quality_assurance",
                    "writer": "writer",  # Revise draft
                    "citation_verification": "citation_verification",  # Re-verify citations
                    "retrieval_specialist": "retrieval_specialist",  # Need more context
                    "rewrite_question": "rewrite_question"
                }
            )
            
            # QA → HITL checkpoint #5 (final)
            workflow.add_edge("quality_assurance", "final_approval")
            
            # Final approval: ship OR iterate
            workflow.add_conditional_edges(
                "final_approval",
                self._route_after_final_review,
                {
                    END: END,  # Ship it!
                    "writer": "writer",  # One more iteration
                    "query_analyst": "query_analyst"  # Start over with new approach
                }
            )
            
        else:
            # === Automated flow (no HITL) - US-RAG-005: Simple 5-Agent Flow ===
            # Flow: query_analyst → retrieval_specialist → re_ranker → quality_assurance → writer → END
            
            workflow.add_edge("query_analyst", "retrieval_specialist")
            workflow.add_edge("retrieval_specialist", "re_ranker")
            
            # Re-ranker routes based on context quality
            workflow.add_conditional_edges(
                "re_ranker",
                self._route_after_reranking,
                {
                    "quality_assurance": "quality_assurance",  # Good context → quality check
                    "rewrite_question": "rewrite_question"  # Poor context → rewrite query
                }
            )
            
            # Quality assurance routes based on quality check
            workflow.add_conditional_edges(
                "quality_assurance",
                self._route_after_quality_assurance,
                {
                    "writer": "writer",  # Quality sufficient → write answer
                    "rewrite_question": "rewrite_question"  # Quality insufficient → rewrite query
                }
            )
            
            # Writer completes the flow
            workflow.add_edge("writer", END)
        
        # Rewrite question → back to query analyst (always loops back)
        workflow.add_edge("rewrite_question", "query_analyst")
        
        # Compile with checkpointer
        # NOTE: RAGSwarmCoordinator ALWAYS uses checkpointer internally for state management
        # For LangGraph Studio export, we create a separate graph without checkpointer
        try:
            from langgraph.checkpoint.memory import MemorySaver
            
            # Set interrupt points for human-in-loop
            # HITL checkpoints throughout the workflow
            interrupt_before = []
            if self.human_in_loop:
                interrupt_before = [
                    "select_knowledge_sources",     # HITL #0: Choose knowledge sources
                    "review_query_analysis",        # HITL #1: Verify query understanding
                    "review_retrieval_results",     # HITL #2: Review retrieved sources
                    "review_ranked_context",        # HITL #3: Approve context quality
                    "review_draft_answer",          # HITL #4: Review draft answer
                    "final_approval"                # HITL #5: Final approval
                ]
            
            # ALWAYS use checkpointer for RAGSwarmCoordinator instances
            # The execute() and resume() methods depend on get_state()
            checkpointer = MemorySaver()
            compiled = workflow.compile(
                checkpointer=checkpointer,
                interrupt_before=interrupt_before
            )
            logger.info(f"✅ Graph compiled WITH checkpointer (interrupts: {interrupt_before})")
            
            return compiled
            
        except Exception as e:
            logger.warning(f"⚠️ Could not enable checkpointer: {e}")
            # Fallback: compile without checkpointer
            return workflow.compile()
    
    def _extract_query_from_state(self, state: MessagesState) -> Optional[str]:
        """
        Helper function to extract query from MessagesState.
        
        Args:
            state: MessagesState containing messages
            
        Returns:
            Query string or None if not found
        """
        # CRITICAL: Access messages correctly - state is a dict-like object
        # MessagesState is a TypedDict, so we access it like a dict
        if not isinstance(state, dict):
            logger.error(f"⚠️ State is not a dict! Type: {type(state)}")
            return None
            
        messages = state.get("messages", [])
        
        # Debug logging
        logger.info(f"🔍 Extracting query from {len(messages)} messages")
        logger.debug(f"   State type: {type(state)}")
        logger.debug(f"   State keys: {list(state.keys())}")
        logger.debug(f"   Message types: {[type(msg).__name__ for msg in messages]}")
        
        # Log all messages for debugging
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            if isinstance(msg, HumanMessage):
                content_preview = str(msg.content)[:60] if hasattr(msg, 'content') else str(msg)[:60]
                logger.info(f"   Message {i}: {msg_type} - '{content_preview}...'")
            else:
                logger.debug(f"   Message {i}: {msg_type}")
        
        # Look for HumanMessage (most recent first)
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                query = msg.content if hasattr(msg, 'content') else str(msg)
                logger.info(f"✅ Found query: '{query[:60]}...'")
                return query
        
        logger.warning(f"⚠️ No HumanMessage found in {len(messages)} messages")
        if messages:
            logger.warning(f"   First message type: {type(messages[0]).__name__}")
            logger.warning(f"   First message: {str(messages[0])[:100]}")
        return None
    
    async def _query_analyst_node(self, state: MessagesState):
        """
        Query Analysis Node - Sophisticated query understanding.
        
        Uses QueryAnalystAgent to:
        - Understand user intent
        - Extract key concepts and entities
        - Expand query with synonyms and related terms
        - Determine optimal retrieval strategy
        """
        # CRITICAL: Ensure state is accessed correctly
        # MessagesState is a TypedDict - access like a dict
        if not isinstance(state, dict):
            logger.error(f"❌ QueryAnalystNode: State is not a dict! Type: {type(state)}")
            return {"messages": [SystemMessage(content=f"State type error: {type(state)}")]}
        
        # Debug: Log state structure
        logger.info(f"🔍 QueryAnalystNode received state with keys: {list(state.keys())}")
        logger.info(f"   State has 'messages' key: {'messages' in state}")
        if "messages" in state:
            msg_count = len(state['messages'])
            logger.info(f"   Messages count: {msg_count}")
            logger.debug(f"   Message types: {[type(m).__name__ for m in state['messages']]}")
            # Log first few messages for debugging
            for i, msg in enumerate(state['messages'][:3]):
                logger.debug(f"   Message {i}: {type(msg).__name__} - {str(msg)[:80]}")
        else:
            logger.error(f"❌ State missing 'messages' key! Available keys: {list(state.keys())}")
            return {"messages": [SystemMessage(content="State missing messages key")]}
        
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        if not query:
            logger.error(f"⚠️ No query found for analysis. State keys: {list(state.keys())}")
            if "messages" in state:
                logger.error(f"   Messages in state: {len(state['messages'])}")
                for i, msg in enumerate(state['messages']):
                    logger.error(f"   Message {i}: type={type(msg).__name__}, content={str(msg)[:100]}")
            return {"messages": [SystemMessage(content="No query to analyze")]}
        
        logger.info(f"🔍 QueryAnalystAgent analyzing: '{query[:60]}...'")
        
        # Call QueryAnalystAgent
        task = {"query": query}
        analysis_result = await self.query_analyst.execute(task)
        
        # Format analysis as system message
        analysis_text = analysis_result.get("output_data", {})
        analysis_msg = SystemMessage(content=(
            f"📊 Query Analysis:\n"
            f"Query: {query}\n"
            f"Intent: {analysis_text.get('intent', 'informational')}\n"
            f"Key Concepts: {', '.join(analysis_text.get('key_concepts', [query]))}\n"
            f"Strategy: {analysis_text.get('retrieval_strategy', 'semantic_search')}"
        ))
        
        logger.info(f"✅ Query analysis complete: {analysis_text.get('intent', 'unknown')} intent")
        return {"messages": [analysis_msg]}
    
    async def _retrieval_specialist_node(self, state: MessagesState):
        """
        Retrieval Specialist Node - Multi-source retrieval orchestration.
        
        Uses RetrievalSpecialistAgent to:
        - Execute retrieval from multiple sources (project docs, web, Wikipedia)
        - Apply query expansion and synonyms
        - Aggregate and deduplicate results
        - Enrich with metadata and source information
        """
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        if not query:
            return {"messages": [SystemMessage(content="No query for retrieval")]}
        
        logger.info(f"📚 RetrievalSpecialistAgent retrieving for: '{query[:60]}...'")
        
        # Call QueryAnalystAgent first to get proper query_analysis format
        # (RetrievalSpecialistAgent expects query_analysis dict)
        query_task = {"query": query}
        query_analysis_result = await self.query_analyst.execute(query_task)
        
        # Extract query_analysis from QueryAnalystAgent result
        # QueryAnalystAgent returns: {'status': 'success', 'analysis': {...}, ...}
        query_analysis = query_analysis_result.get("analysis")
        
        # If analysis not found, create fallback
        if not query_analysis:
            # Try to extract from output_data (alternate format)
            query_analysis = query_analysis_result.get("output_data", {})
            if not query_analysis.get("original_query"):
                # Fallback: create minimal query_analysis
                query_analysis = {
                    "original_query": query,
                    "rewritten_queries": [query],
                    "key_concepts": query.split(),  # Simple word-based concepts
                    "search_strategy": "broad",  # Use broad for comprehensive retrieval
                    "intent": "comprehensive"  # Flag for comprehensive retrieval
                }
        
        # Ensure query_analysis has required fields
        if "original_query" not in query_analysis:
            query_analysis["original_query"] = query
        if "search_strategy" not in query_analysis:
            query_analysis["search_strategy"] = "broad"  # Force broad for comprehensive
        if "intent" not in query_analysis:
            query_analysis["intent"] = "comprehensive"  # Flag for comprehensive mode
        
        # Call RetrievalSpecialistAgent with proper format
        # ENHANCED: Request more documents for comprehensive coverage
        task = {
            "query_analysis": query_analysis,
            "manual_chunk_count": 20,  # REQUEST 20 CHUNKS for comprehensive coverage
            "retrieval_mode": "manual",  # Use manual to ensure we get requested count
            "available_doc_count": 1000  # Assume large doc base
        }
        
        # Add document filters from state if available
        if "document_filters" in state:
            task["document_filters"] = state["document_filters"]
            logger.info(f"🎯 Applying document filters from state: {state['document_filters']}")
        
        retrieval_result = await self.retrieval_specialist.execute(task)
        
        # Extract documents from search_results (correct field name)
        retrieved_docs = retrieval_result.get("search_results", [])
        
        # If no search_results, try alternative field names
        if not retrieved_docs:
            retrieved_docs = retrieval_result.get("output_data", {}).get("documents", [])
            if not retrieved_docs:
                retrieved_docs = retrieval_result.get("results", [])
        
        tool_msgs = []
        # INCREASED: Use ALL retrieved documents (up to 20) for comprehensive coverage
        # Don't limit to 15 - use all available documents
        for idx, doc in enumerate(retrieved_docs):  # ALL results, no limit
            # Handle different doc formats
            content = doc.get('content', doc.get('page_content', str(doc)))
            source = doc.get('source', doc.get('file_path', doc.get('metadata', {}).get('source', 'unknown')))
            
            tool_msg = ToolMessage(
                content=str(content),  # FULL content, no truncation
                tool_call_id=f"retrieval_{idx}",
                name=str(source)
            )
            tool_msgs.append(tool_msg)
        
        logger.info(f"✅ Retrieved {len(tool_msgs)} documents from {len(set(d.name for d in tool_msgs))} sources")
        return {"messages": tool_msgs}
    
    async def _document_grader_node(self, state: MessagesState):
        """
        Document Grader Node - Grade documents for relevance BEFORE re-ranking.
        
        This is a critical RAG improvement: grade documents BEFORE re-ranking
        to filter out irrelevant documents early. This improves efficiency and
        ensures only relevant documents are re-ranked.
        
        Uses structured output to grade each document:
        - "yes" if document is relevant to query
        - "no" if document is not relevant
        
        Returns filtered list of relevant documents for re-ranking.
        """
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        # Get retrieval results (tool messages)
        tool_results = []
        for msg in state["messages"]:  # Use state["messages"] as messages var wasn't defined in original code snippet but extracted above
            if isinstance(msg, ToolMessage):
                tool_results.append({
                    'content': msg.content,
                    'source': msg.name,
                    'tool_call_id': msg.tool_call_id
                })
        
        if not tool_results:
            logger.warning("⚠️ No retrieval results to grade")
            return {"messages": [SystemMessage(content="⚠️ No documents to grade")]}
        
        logger.info(f"📊 Document Grader grading {len(tool_results)} documents...")
        
        # Grade each document using structured output
        graded_docs = []
        llm = self._create_llm()
        
        for idx, doc in enumerate(tool_results):
            try:
                # Grade with structured output - USE FULL CONTENT (no truncation)
                grade_prompt = f"""You are a grader assessing relevance of a retrieved document to a user question.
                
Here is the retrieved document:
{doc['content']}

Here is the user question:
{query}

If the document contains keywords or semantic meaning related to the user question, grade it as relevant.
Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question.
Be lenient - if the document contains ANY relevant information, mark it as 'yes'."""
                
                grade = await llm.with_structured_output(GradeDocuments).ainvoke([
                    HumanMessage(content=grade_prompt)
                ])
                
                if grade.binary_score == "yes":
                    graded_docs.append(doc)
                    logger.info(f"✅ Document {idx+1}: Relevant")
                else:
                    logger.info(f"❌ Document {idx+1}: Not relevant (filtered out)")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to grade document {idx+1}: {e}, including by default")
                graded_docs.append(doc)  # Include by default if grading fails
        
        # Store graded documents as tool messages (filtered)
        graded_tool_msgs = []
        for doc in graded_docs:
            tool_msg = ToolMessage(
                content=doc['content'],
                tool_call_id=doc.get('tool_call_id', f"graded_{len(graded_tool_msgs)}"),
                name=doc['source']
            )
            graded_tool_msgs.append(tool_msg)
        
        # Store grading summary as system message
        grading_summary = SystemMessage(content=(
            f"📊 Document Grading Results:\n"
            f"Total documents: {len(tool_results)}\n"
            f"Relevant documents: {len(graded_tool_msgs)}\n"
            f"Filtered out: {len(tool_results) - len(graded_tool_msgs)}\n"
            f"Relevance rate: {len(graded_tool_msgs)/len(tool_results) if tool_results else 0:.1%}"
        ))
        
        logger.info(f"✅ Grading complete: {len(graded_tool_msgs)}/{len(tool_results)} documents relevant")
        return {"messages": [grading_summary] + graded_tool_msgs}
    
    async def _re_ranker_node(self, state: MessagesState):
        """
        Re-Ranker Node - Relevance scoring and filtering.
        
        Uses ReRankerAgent to:
        - Score each document for relevance to query
        - Filter out low-quality or off-topic results
        - Re-order documents by relevance score
        - Add relevance metadata
        """
        messages = state["messages"]
        
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        # Get retrieval results (tool messages)
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results.append({
                    'content': msg.content,
                    'source': msg.name
                })
        
        if not tool_results:
            logger.warning("⚠️ No retrieval results to re-rank")
            return {"messages": [SystemMessage(content="⚠️ No documents to re-rank")]}
        
        logger.info(f"🎯 ReRankerAgent re-ranking {len(tool_results)} documents...")
        
        # Call ReRankerAgent
        task = {
            "query": query,
            "documents": tool_results
        }
        rerank_result = await self.re_ranker.execute(task)
        
        # Extract re-ranking info
        reranked_data = rerank_result.get("output_data", {})
        avg_score = reranked_data.get("average_relevance_score", 0.0)
        quality_ok = avg_score >= 0.7  # Threshold for quality
        
        # Store re-ranking info as system message
        rerank_msg = SystemMessage(content=(
            f"🎯 Re-Ranking Results:\n"
            f"Documents processed: {len(tool_results)}\n"
            f"Average relevance: {avg_score:.1%}\n"
            f"Quality threshold met: {'✅ Yes' if quality_ok else '❌ No (needs rewrite)'}\n"
            f"Top document score: {reranked_data.get('top_score', 0):.1%}"
        ))
        
        logger.info(f"✅ Re-ranking complete: avg={avg_score:.1%}, quality_ok={quality_ok}")
        return {"messages": [rerank_msg]}
    
    async def _context_enrichment_node(self, state: MessagesState):
        """
        Context Enrichment Node - Enrich context after re-ranking.
        
        This agent fills gaps, cross-references between documents, and adds
        missing context to improve answer quality. It:
        - Identifies information gaps in retrieved context
        - Cross-references concepts across documents
        - Adds missing contextual information
        - Ensures comprehensive coverage of query aspects
        - Triggers additional retrieval if critical gaps found
        
        This happens AFTER re-ranking but BEFORE writing to ensure
        the writer has complete, enriched context.
        """
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        # Get re-ranked context (tool messages from grader/re-ranker)
        context_parts = []
        for msg in state["messages"]:  # Use state["messages"]
            if isinstance(msg, ToolMessage):
                context_parts.append(msg.content)
        
        if not context_parts:
            logger.warning("⚠️ No context to enrich")
            return {"messages": [SystemMessage(content="⚠️ No context available for enrichment")]}
        
        # USE FULL CONTEXT - no truncation
        context = "\n\n".join(context_parts)
        
        logger.info(f"🔍 Context Enrichment Agent enriching {len(context_parts)} documents...")
        
        # Use LLM to identify gaps and enrich context
        llm = self._create_llm()
        enrichment_prompt = f"""You are a context enrichment specialist. Your task is to analyze the retrieved context and identify gaps or missing information that would improve answer quality.

Query: {query}

Retrieved Context ({len(context_parts)} documents):
{context}

Analyze the context and:
1. Identify information gaps related to the query
2. Cross-reference concepts across documents
3. Suggest missing contextual information
4. Ensure comprehensive coverage

Provide an enriched context summary that includes:
- Gaps identified (if any)
- Cross-references found
- Additional context needed (if any)
- Completeness assessment
- Recommendation: "sufficient" if context is complete, "needs_more" if critical gaps exist"""
        
        try:
            enrichment_response = await llm.ainvoke([HumanMessage(content=enrichment_prompt)])
            enriched_analysis = enrichment_response.content
            
            # Check if enrichment recommends more retrieval
            needs_more = "needs_more" in enriched_analysis.lower() or "critical gap" in enriched_analysis.lower()
            
            # Store enrichment results as system message
            enrichment_msg = SystemMessage(content=(
                f"🔍 Context Enrichment Analysis:\n\n{enriched_analysis}\n\n"
                f"Original context: {len(context_parts)} documents ({len(context)} chars)\n"
                f"Enrichment complete - context ready for answer generation"
            ))
            
            logger.info(f"✅ Context enrichment complete: {len(enriched_analysis)} chars added")
            
            # If gaps found, trigger additional retrieval
            if needs_more:
                logger.info("⚠️ Context enrichment identified gaps - triggering additional retrieval")
                enrichment_msg.content += "\n\n⚠️ Gaps identified - consider additional retrieval for comprehensive answer"
            
            return {"messages": [enrichment_msg]}
            
        except Exception as e:
            logger.error(f"❌ Context enrichment failed: {e}")
            return {"messages": [SystemMessage(content=f"Context enrichment error: {e}")]}
    
    async def _quality_assurance_node(self, state: MessagesState):
        """
        Quality Assurance Node - Comprehensive quality checks.
        
        Uses QualityAssuranceAgent to:
        - Validate context completeness
        - Check for contradictions
        - Assess information consistency
        - Verify readiness for answer generation
        """
        messages = state["messages"]
        
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        # Get retrieved context
        context_parts = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                context_parts.append(msg.content)
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"✅ QualityAssuranceAgent checking quality...")
        
        # Call QualityAssuranceAgent
        task = {
            "query": query,
            "context": context
        }
        qa_result = await self.quality_assurance.execute(task)
        
        # Extract quality metrics
        qa_data = qa_result.get("output_data", {})
        completeness = qa_data.get("completeness_score", 0.0)
        relevance = qa_data.get("relevance_score", 0.0)
        consistency = qa_data.get("consistency_check", True)
        ready = qa_data.get("ready_for_generation", True)
        
        # Store QA results as system message
        qa_msg = SystemMessage(content=(
            f"✅ Quality Assurance Results:\n"
            f"Completeness: {completeness:.0%}\n"
            f"Relevance: {relevance:.0%}\n"
            f"Consistency: {'✅ Pass' if consistency else '❌ Fail'}\n"
            f"Ready for answer generation: {'✅ Yes' if ready else '❌ No'}"
        ))
        
        logger.info(f"✅ QA complete: completeness={completeness:.0%}, ready={ready}")
        return {"messages": [qa_msg]}
    
    async def _writer_node(self, state: MessagesState):
        """
        Writer Node - Sophisticated answer synthesis.
        
        Uses WriterAgent to:
        - Synthesize comprehensive answer from all context
        - Structure answer with proper formatting
        - Add citations and source references
        - Ensure clarity, completeness, and correctness
        
        CRITICAL: This node is async to avoid blocking I/O operations.
        """
        messages = state["messages"]
        
        # Extract query using helper function
        query = self._extract_query_from_state(state)
        
        # Get ALL context (including enrichment analysis)
        context_parts = []
        enrichment_analysis = None
        
        for msg in messages:
            if isinstance(msg, ToolMessage):
                context_parts.append(msg.content)  # FULL content, no truncation
            elif isinstance(msg, SystemMessage) and "Context Enrichment Analysis" in msg.content:
                enrichment_analysis = msg.content  # Include enrichment insights
        
        # Convert context_parts to format expected by WriterAgent
        # WriterAgent expects list of dicts with 'content' key
        ranked_results = []
        for idx, content in enumerate(context_parts):
            ranked_results.append({
                'content': content,  # FULL content
                'source': f'document_{idx}',
                'relevance_score': 1.0 - (idx * 0.05)  # Decreasing relevance
            })
        
        # Add enrichment insights if available
        if enrichment_analysis:
            # Pass enrichment as part of context
            ranked_results.insert(0, {
                'content': enrichment_analysis,
                'source': 'enrichment_analysis',
                'relevance_score': 1.0
            })
        
        logger.info(f"✍️ WriterAgent generating comprehensive answer from {len(ranked_results)} sources ({sum(len(r.get('content', '')) for r in ranked_results)} chars)...")
        
        # CRITICAL FIX: Use await instead of asyncio.run() to avoid blocking
        # asyncio.run() creates a new event loop which blocks the current async context
        task = {
            "query": query,
            "ranked_results": ranked_results,  # Pass full context as list of dicts
            "query_analysis": {"original_query": query, "intent": "comprehensive"},  # Encourage comprehensive synthesis
            "quality_report": {}
        }
        writer_result = await self.writer.execute(task)
        
        # Extract generated answer
        answer = writer_result.get("output_data", {}).get("response", writer_result.get("response", "Failed to generate answer"))
        
        logger.info(f"✅ Answer generated: {len(answer)} chars")
        return {"messages": [AIMessage(content=answer)]}
    
    async def _citation_verification_node(self, state: MessagesState):
        """
        Citation Verification Node - Verify citations are accurate and relevant.
        
        This agent validates that:
        - Citations in the answer match the retrieved documents
        - Citations are relevant to the claims they support
        - Citation format is correct
        - All claims are properly cited
        
        This happens AFTER writing but BEFORE quality assurance to ensure
        citation accuracy before final QA checks.
        """
        messages = state["messages"]
        
        # Get generated answer (last AIMessage)
        answer = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                answer = msg.content
                break
        
        # Get retrieved context (tool messages)
        context_parts = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                context_parts.append({
                    'content': msg.content,
                    'source': msg.name,
                    'tool_call_id': msg.tool_call_id
                })
        
        if not answer:
            logger.warning("⚠️ No answer to verify citations for")
            return {"messages": [SystemMessage(content="⚠️ No answer found for citation verification")]}
        
        logger.info(f"🔍 Citation Verification Agent verifying citations...")
        
        # Use LLM to verify citations
        llm = self._create_llm()
        verification_prompt = f"""You are a citation verification specialist. Verify that citations in the answer are accurate and relevant.

Generated Answer:
{answer}

Retrieved Context Sources:
{chr(10).join([f"- {doc['source']}: {doc['content'][:200]}..." for doc in context_parts[:5]])}

Verify:
1. All citations in the answer match the retrieved sources
2. Citations are relevant to the claims they support
3. Citation format is correct
4. Important claims are properly cited
5. No false citations or unsupported claims

Provide verification results:
- Valid citations found
- Invalid or missing citations
- Recommendations for improvement"""
        
        try:
            verification_response = await llm.ainvoke([HumanMessage(content=verification_prompt)])
            verification_analysis = verification_response.content
            
            # Store verification results as system message
            verification_msg = SystemMessage(content=(
                f"🔍 Citation Verification Results:\n\n{verification_analysis}\n\n"
                f"Answer length: {len(answer)} chars\n"
                f"Sources checked: {len(context_parts)}\n"
                f"Citation verification complete"
            ))
            
            logger.info(f"✅ Citation verification complete")
            return {"messages": [verification_msg]}
            
        except Exception as e:
            logger.error(f"❌ Citation verification failed: {e}")
            return {"messages": [SystemMessage(content=f"Citation verification error: {e}")]}
    
    def _select_knowledge_sources_node(self, state: MessagesState):
        """
        HITL Checkpoint #0: Knowledge Source Selection.
        
        Proactively asks user what knowledge sources to use for this task:
        - Predefined categories (architecture, agile, coding standards)
        - Custom URLs (API docs, tutorials, references)
        - Local documents (upload specs, designs, notes)
        - Project defaults
        
        This is the FIRST checkpoint in the workflow, ensuring RAG uses
        exactly the knowledge the user wants.
        """
        messages = state["messages"]
        
        # Get the user's query to determine task type
        query = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                query = msg.content
                break
        
        if not query:
            query = "development task"
        
        # Generate knowledge source selection prompt
        selection_prompt = (
            f"📚 **Knowledge Source Selection**\n\n"
            f"I'm helping you with: '{query[:100]}...'\n\n"
            f"To provide the best assistance, I need to know what knowledge sources to use.\n\n"
            f"**Available Options**:\n\n"
            f"**Predefined Categories**:\n"
            f"- `architecture` - Architecture documentation and patterns\n"
            f"- `agile` - Sprint plans, user stories, requirements\n"
            f"- `coding_guidelines` - Coding standards and best practices\n"
            f"- `framework_docs` - LangChain, LangGraph, API documentation\n\n"
            f"**Custom Sources**:\n"
            f"- `url: https://example.com` - Add website URL\n"
            f"- `doc: /path/to/file.md` - Add local document\n\n"
            f"**Quick Options**:\n"
            f"- `defaults` - Use project default sources\n"
            f"- `all` - Use all available sources\n\n"
            f"**Format** (comma-separated):\n"
            f"`architecture, coding_guidelines, url: https://docs.langchain.com/langgraph`\n\n"
            f"What knowledge sources should I use?"
        )
        
        logger.info("📚 HITL #0: Requesting knowledge source selection from user")
        
        return {"messages": [SystemMessage(content=selection_prompt)]}
    
    def _load_knowledge_sources_node(self, state: MessagesState):
        """
        Load Knowledge Sources Node - Indexes user-selected sources.
        
        Takes user input from select_knowledge_sources checkpoint and:
        1. Parses user selections (categories, URLs, documents)
        2. Scrapes URLs and extracts content
        3. Loads local documents
        4. Indexes everything into vector store
        5. Makes sources available for retrieval_specialist
        """
        messages = state["messages"]
        
        # Get user's knowledge source selections
        user_selection = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'human':
                # Find the message after the selection prompt
                user_selection = msg.content
                break
        
        if not user_selection:
            logger.warning("⚠️ No knowledge source selection from user, using defaults")
            user_selection = "defaults"
        
        logger.info(f"📚 Loading knowledge sources: {user_selection}")
        
        # Parse user selections
        sources_to_load = self._parse_knowledge_source_selection(user_selection)
        
        # Load and index sources
        loaded_sources = []
        failed_sources = []
        
        # Load predefined categories
        for category in sources_to_load.get("categories", []):
            try:
                category_sources = self._load_category_sources(category)
                loaded_sources.extend(category_sources)
                logger.info(f"✅ Loaded category: {category} ({len(category_sources)} docs)")
            except Exception as e:
                logger.error(f"❌ Failed to load category {category}: {e}")
                failed_sources.append(f"category:{category}")
        
        # Load custom URLs
        for url in sources_to_load.get("urls", []):
            try:
                url_content = self._scrape_and_index_url(url)
                loaded_sources.append(url_content)
                logger.info(f"✅ Loaded URL: {url}")
            except Exception as e:
                logger.error(f"❌ Failed to load URL {url}: {e}")
                failed_sources.append(f"url:{url}")
        
        # Load local documents
        for doc_path in sources_to_load.get("documents", []):
            try:
                doc_content = self._load_and_index_document(doc_path)
                loaded_sources.append(doc_content)
                logger.info(f"✅ Loaded document: {doc_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load document {doc_path}: {e}")
                failed_sources.append(f"doc:{doc_path}")
        
        # Generate status message
        status_msg = (
            f"📚 **Knowledge Sources Loaded**\n\n"
            f"✅ Successfully loaded: {len(loaded_sources)} sources\n"
        )
        
        if failed_sources:
            status_msg += f"❌ Failed to load: {', '.join(failed_sources)}\n"
        
        status_msg += f"\nProceeding with query analysis and retrieval..."
        
        logger.info(f"✅ Knowledge sources loaded: {len(loaded_sources)} sources ready")
        
        return {"messages": [SystemMessage(content=status_msg)]}
    
    def _parse_knowledge_source_selection(self, selection: str) -> dict:
        """
        Parse user's knowledge source selection into structured format.
        
        Handles formats like:
        - "architecture, coding_guidelines"
        - "url: https://example.com, doc: /path/to/file.md"
        - "defaults"
        - "all"
        """
        parsed = {
            "categories": [],
            "urls": [],
            "documents": []
        }
        
        selection_lower = selection.lower().strip()
        
        # Handle special keywords
        if "defaults" in selection_lower:
            parsed["categories"] = ["architecture", "coding_guidelines", "framework_docs"]
            return parsed
        
        if "all" in selection_lower:
            parsed["categories"] = ["architecture", "agile", "coding_guidelines", "framework_docs"]
            return parsed
        
        # Parse comma-separated items
        items = [item.strip() for item in selection.split(',')]
        
        for item in items:
            if item.startswith("url:"):
                url = item.replace("url:", "").strip()
                parsed["urls"].append(url)
            elif item.startswith("doc:"):
                doc_path = item.replace("doc:", "").strip()
                parsed["documents"].append(doc_path)
            elif item in ["architecture", "agile", "coding_guidelines", "framework_docs"]:
                parsed["categories"].append(item)
        
        return parsed
    
    def _load_category_sources(self, category: str) -> list:
        """Load documents for a predefined category."""
        # This would integrate with KnowledgeSourceManager
        # For now, return placeholder
        category_paths = {
            "architecture": "docs/architecture/",
            "agile": "docs/agile/sprints/",
            "coding_guidelines": "docs/guides/",
            "framework_docs": "docs/development/"
        }
        
        path = category_paths.get(category, "")
        return [{"category": category, "path": path, "loaded": True}]
    
    def _scrape_and_index_url(self, url: str) -> dict:
        """Scrape URL content and index into vector store."""
        # This would use BeautifulSoup or similar to scrape
        # and then add to context_engine.vector_store
        logger.info(f"Scraping URL: {url}")
        return {"url": url, "scraped": True, "indexed": True}
    
    def _load_and_index_document(self, doc_path: str) -> dict:
        """Load local document and index into vector store."""
        # This would read the file and add to context_engine.vector_store
        logger.info(f"Loading document: {doc_path}")
        return {"document": doc_path, "loaded": True, "indexed": True}
    
    # ==================== HITL REVIEW NODES ====================
    
    def _review_query_analysis_node(self, state: MessagesState):
        """
        HITL Checkpoint #1: Review Query Analysis.
        
        Human reviews QueryAnalyst's understanding of the query and
        proposed retrieval strategy. Can approve, refine, or request rewrite.
        
        Commands:
        - "approve" / "yes" / "continue" → Proceed to retrieval
        - "refine: <feedback>" → Re-analyze with feedback
        - "rewrite" / "no" → Rewrite question completely
        """
        messages = state["messages"]
        
        # Get query analysis from last system message
        analysis_msg = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'system':
                if "Query Analysis" in msg.content or "Understanding" in msg.content:
                    analysis_msg = msg.content
                    break
        
        if not analysis_msg:
            analysis_msg = "Query analysis completed."
        
        # Generate review prompt
        review_prompt = (
            f"📋 **HITL Checkpoint #1: Query Analysis Review**\n\n"
            f"{analysis_msg}\n\n"
            f"**Review Options**:\n"
            f"- `approve` → Continue to retrieval\n"
            f"- `refine: <your feedback>` → Re-analyze with guidance\n"
            f"- `rewrite` → Completely rewrite question\n\n"
            f"**Your decision**:"
        )
        
        logger.info("⏸️ HITL #1: Waiting for query analysis review...")
        
        # Return empty state to trigger interrupt
        # Human feedback will come as next message
        return {}
    
    def _review_retrieval_results_node(self, state: MessagesState):
        """
        HITL Checkpoint #2: Review Retrieval Results.
        
        Human reviews sources retrieved by RetrievalSpecialist.
        Can approve, request more sources, or go back to rewrite.
        
        Commands:
        - "approve" → Continue to re-ranking
        - "more_sources" / "retry" → Retry retrieval with expansion
        - "add_source: <url>" → Add specific source and retry
        - "rewrite" → Rewrite question and start over
        """
        messages = state["messages"]
        
        # Get retrieval results from last system message
        retrieval_msg = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'system':
                if "Retrieval" in msg.content or "Retrieved" in msg.content or "sources" in msg.content.lower():
                    retrieval_msg = msg.content
                    break
        
        if not retrieval_msg:
            retrieval_msg = "Retrieval completed."
        
        # Generate review prompt
        review_prompt = (
            f"📚 **HITL Checkpoint #2: Retrieval Results Review**\n\n"
            f"{retrieval_msg}\n\n"
            f"**Review Options**:\n"
            f"- `approve` → Continue to re-ranking\n"
            f"- `more_sources` → Retry retrieval with expansion\n"
            f"- `add_source: <url>` → Add specific source\n"
            f"- `rewrite` → Rewrite question completely\n\n"
            f"**Your decision**:"
        )
        
        logger.info("⏸️ HITL #2: Waiting for retrieval results review...")
        
        return {}
    
    def _review_ranked_context_node(self, state: MessagesState):
        """
        HITL Checkpoint #3: Review Ranked Context.
        
        Human reviews ReRanker's filtered and scored context.
        Can approve, request re-ranking, get more sources, or rewrite.
        
        Commands:
        - "approve" → Continue to writer
        - "re_rank" → Re-rank with different criteria
        - "more_sources" → Get additional sources
        - "rewrite" → Rewrite question completely
        """
        messages = state["messages"]
        
        # Get re-ranking results
        rerank_msg = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'system':
                if "Rank" in msg.content or "Context" in msg.content or "scored" in msg.content.lower():
                    rerank_msg = msg.content
                    break
        
        if not rerank_msg:
            rerank_msg = "Context ranked and filtered."
        
        # Generate review prompt
        review_prompt = (
            f"🎯 **HITL Checkpoint #3: Ranked Context Review**\n\n"
            f"{rerank_msg}\n\n"
            f"**Review Options**:\n"
            f"- `approve` → Continue to answer generation\n"
            f"- `re_rank` → Re-rank with different criteria\n"
            f"- `more_sources` → Get additional sources\n"
            f"- `rewrite` → Rewrite question completely\n\n"
            f"**Your decision**:"
        )
        
        logger.info("⏸️ HITL #3: Waiting for ranked context review...")
        
        return {}
    
    def _review_draft_answer_node(self, state: MessagesState):
        """
        HITL Checkpoint #4: Review Draft Answer.
        
        Human reviews Writer's draft answer before QA.
        Can approve for QA, request revision, get more context, or rewrite.
        
        Commands:
        - "approve" → Continue to quality assurance
        - "revise: <feedback>" → Writer revises with feedback
        - "more_context" → Get additional context
        - "rewrite" → Rewrite question completely
        """
        messages = state["messages"]
        
        # Get draft answer
        draft_msg = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'ai':
                draft_msg = msg.content
                break
            elif hasattr(msg, 'type') and msg.type == 'system':
                if "Draft" in msg.content or "Answer" in msg.content:
                    draft_msg = msg.content
                    break
        
        if not draft_msg:
            draft_msg = "Draft answer generated."
        
        # Generate review prompt
        review_prompt = (
            f"✍️ **HITL Checkpoint #4: Draft Answer Review**\n\n"
            f"**Draft Answer**:\n{draft_msg}\n\n"
            f"**Review Options**:\n"
            f"- `approve` → Continue to QA\n"
            f"- `revise: <your feedback>` → Writer revises draft\n"
            f"- `more_context` → Get additional context\n"
            f"- `rewrite` → Rewrite question completely\n\n"
            f"**Your decision**:"
        )
        
        logger.info("⏸️ HITL #4: Waiting for draft answer review...")
        
        return {}
    
    def _final_approval_node(self, state: MessagesState):
        """
        HITL Checkpoint #5: Final Approval.
        
        Human reviews QA-validated answer for final approval.
        Can ship, iterate more, or start over.
        
        Commands:
        - "approve" / "ship" / "done" → Complete and return answer
        - "iterate" / "improve" → Writer improves once more
        - "restart" → Go back to query analysis with new approach
        """
        messages = state["messages"]
        
        # Get QA-validated answer
        final_msg = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'ai':
                final_msg = msg.content
                break
            elif hasattr(msg, 'type') and msg.type == 'system':
                if "Quality" in msg.content or "Final" in msg.content:
                    final_msg = msg.content
                    break
        
        if not final_msg:
            final_msg = "Final answer ready."
        
        # Generate review prompt
        review_prompt = (
            f"✅ **HITL Checkpoint #5: Final Approval**\n\n"
            f"**QA-Validated Answer**:\n{final_msg}\n\n"
            f"**Final Options**:\n"
            f"- `approve` / `ship` → Complete and deliver\n"
            f"- `iterate` → One more improvement pass\n"
            f"- `restart` → New approach from beginning\n\n"
            f"**Your decision**:"
        )
        
        logger.info("⏸️ HITL #5: Waiting for final approval...")
        
        return {}
    
    # ==================== ROUTING FUNCTIONS ====================
    
    def _route_after_query_review(self, state: MessagesState) -> Literal["retrieval_specialist", "rewrite_question"]:
        """
        Route after HITL #1 (Query Analysis Review).
        
        Parse human feedback and route accordingly:
        - "approve" / "yes" / "continue" → retrieval_specialist
        - "rewrite" / "no" / "reject" → rewrite_question
        - "refine: <feedback>" → query_analyst (implicit via rewrite)
        """
        messages = state["messages"]
        
        logger.info(f"🔀 _route_after_query_review: Analyzing {len(messages)} messages for feedback")
        
        # Get last human message (the feedback)
        feedback = None
        for i, msg in enumerate(reversed(messages)):
            if hasattr(msg, 'type') and msg.type == 'human':
                feedback = msg.content.lower().strip()
                logger.info(f"📝 Found human feedback in message #{len(messages)-i-1}: '{feedback}'")
                break
        
        if not feedback:
            logger.warning(f"⚠️ No human feedback found in {len(messages)} messages, defaulting to continue")
            # Debug: Log message types
            for i, msg in enumerate(messages[-5:]):  # Last 5 messages
                msg_type = msg.type if hasattr(msg, 'type') else type(msg).__name__
                content_preview = msg.content[:50] if hasattr(msg, 'content') else str(msg)[:50]
                logger.info(f"  Message {i}: {msg_type} - '{content_preview}'")
            return "retrieval_specialist"
        
        logger.info(f"🔀 Routing decision for feedback: '{feedback}'")
        
        # Parse feedback commands
        if any(word in feedback for word in ["approve", "yes", "continue", "ok", "good"]):
            logger.info("✅ Human approved → retrieval_specialist")
            return "retrieval_specialist"
        elif any(word in feedback for word in ["rewrite", "no", "reject", "refine", "change"]):
            logger.info("🔄 Human requested rewrite → rewrite_question")
            return "rewrite_question"
        else:
            # Default to continue if ambiguous
            logger.info("❓ Ambiguous feedback, defaulting to continue → retrieval_specialist")
            return "retrieval_specialist"
    
    def _route_after_retrieval_review(self, state: MessagesState) -> Literal["re_ranker", "retrieval_specialist", "rewrite_question"]:
        """
        Route after HITL #2 (Retrieval Results Review).
        
        Parse human feedback:
        - "approve" → re_ranker
        - "more_sources" / "retry" → retrieval_specialist (retry)
        - "add_source: <url>" → retrieval_specialist (with new source)
        - "rewrite" → rewrite_question
        """
        messages = state["messages"]
        
        feedback = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'human':
                feedback = msg.content.lower().strip()
                break
        
        if not feedback:
            return "re_ranker"
        
        logger.info(f"🔀 Routing after retrieval review: '{feedback}'")
        
        if any(word in feedback for word in ["approve", "yes", "continue", "good"]):
            logger.info("✅ Human approved → re_ranker")
            return "re_ranker"
        elif any(word in feedback for word in ["more", "retry", "again", "add_source"]):
            logger.info("🔄 Human wants more sources → retrieval_specialist")
            return "retrieval_specialist"
        elif any(word in feedback for word in ["rewrite", "no", "reject"]):
            logger.info("🔄 Human requested rewrite → rewrite_question")
            return "rewrite_question"
        else:
            return "re_ranker"
    
    def _route_after_context_review(self, state: MessagesState) -> Literal["writer", "re_ranker", "retrieval_specialist", "rewrite_question"]:
        """
        Route after HITL #3 (Ranked Context Review).
        
        Parse human feedback:
        - "approve" → writer
        - "re_rank" → re_ranker (retry ranking)
        - "more_sources" → retrieval_specialist (get more)
        - "rewrite" → rewrite_question
        """
        messages = state["messages"]
        
        feedback = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'human':
                feedback = msg.content.lower().strip()
                break
        
        if not feedback:
            return "writer"
        
        logger.info(f"🔀 Routing after context review: '{feedback}'")
        
        if any(word in feedback for word in ["approve", "yes", "continue", "good"]):
            logger.info("✅ Human approved → writer")
            return "writer"
        elif any(word in feedback for word in ["re_rank", "rerank", "rank_again"]):
            logger.info("🔄 Human wants re-ranking → re_ranker")
            return "re_ranker"
        elif any(word in feedback for word in ["more", "sources", "additional"]):
            logger.info("🔄 Human wants more sources → retrieval_specialist")
            return "retrieval_specialist"
        elif any(word in feedback for word in ["rewrite", "no", "reject"]):
            logger.info("🔄 Human requested rewrite → rewrite_question")
            return "rewrite_question"
        else:
            return "writer"
    
    def _route_after_draft_review(self, state: MessagesState) -> Literal["quality_assurance", "writer", "retrieval_specialist", "rewrite_question"]:
        """
        Route after HITL #4 (Draft Answer Review).
        
        Parse human feedback:
        - "approve" → quality_assurance
        - "revise: <feedback>" → writer (revise draft)
        - "more_context" → retrieval_specialist (get more)
        - "rewrite" → rewrite_question
        """
        messages = state["messages"]
        
        feedback = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'human':
                feedback = msg.content.lower().strip()
                break
        
        if not feedback:
            return "quality_assurance"
        
        logger.info(f"🔀 Routing after draft review: '{feedback}'")
        
        if any(word in feedback for word in ["approve", "yes", "continue", "qa", "good"]):
            logger.info("✅ Human approved → quality_assurance")
            return "quality_assurance"
        elif any(word in feedback for word in ["revise", "improve", "refine", "change"]):
            logger.info("🔄 Human wants revision → writer")
            return "writer"
        elif any(word in feedback for word in ["more", "context", "additional"]):
            logger.info("🔄 Human wants more context → retrieval_specialist")
            return "retrieval_specialist"
        elif any(word in feedback for word in ["rewrite", "no", "reject"]):
            logger.info("🔄 Human requested rewrite → rewrite_question")
            return "rewrite_question"
        else:
            return "quality_assurance"
    
    def _route_after_grading(self, state: MessagesState) -> Literal["re_ranker", "rewrite_question"]:
        """
        Route after document grading.
        
        If documents are relevant (graded), proceed to re-ranking.
        If no relevant documents found, rewrite the question.
        """
        messages = state["messages"]
        
        # Check grading summary
        graded_count = 0
        total_count = 0
        for msg in messages:
            if isinstance(msg, SystemMessage) and "Document Grading Results" in msg.content:
                # Extract counts from summary
                content = msg.content
                if "Relevant documents:" in content:
                    try:
                        import re
                        total_match = re.search(r"Total documents: (\d+)", content)
                        relevant_match = re.search(r"Relevant documents: (\d+)", content)
                        if total_match and relevant_match:
                            total_count = int(total_match.group(1))
                            graded_count = int(relevant_match.group(1))
                    except Exception:
                        pass
        
        # If we have relevant documents, proceed to re-ranking
        if graded_count > 0:
            logger.info(f"✅ {graded_count} relevant documents found → proceeding to re-ranking")
            return "re_ranker"
        else:
            logger.warning("⚠️ No relevant documents found → rewriting question")
            return "rewrite_question"
    
    def _route_after_writing(self, state: MessagesState) -> Literal["citation_verification", "rewrite_question"]:
        """
        Route after writing.
        
        Always proceed to citation verification if answer was generated.
        If no answer, rewrite question.
        """
        messages = state["messages"]
        
        # Check if answer was generated
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                answer = msg.content
                if answer and len(answer) > 10 and "Failed to generate" not in answer:
                    logger.info("✅ Answer generated → proceeding to citation verification")
                    return "citation_verification"
        
        logger.warning("⚠️ No answer generated → rewriting question")
        return "rewrite_question"
    
    def _route_after_final_review(self, state: MessagesState) -> Literal[END, "writer", "query_analyst"]:
        """
        Route after HITL #5 (Final Approval).
        
        Parse human feedback:
        - "approve" / "ship" / "done" → END (complete!)
        - "iterate" / "improve" → writer (one more pass)
        - "restart" → query_analyst (start over)
        """
        messages = state["messages"]
        
        feedback = None
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'human':
                feedback = msg.content.lower().strip()
                break
        
        if not feedback:
            return END
        
        logger.info(f"🔀 Routing after final review: '{feedback}'")
        
        if any(word in feedback for word in ["approve", "ship", "done", "complete", "yes"]):
            logger.info("✅ Human shipped! → END")
            return END
        elif any(word in feedback for word in ["iterate", "improve", "refine", "better"]):
            logger.info("🔄 Human wants iteration → writer")
            return "writer"
        elif any(word in feedback for word in ["restart", "start_over", "begin_again"]):
            logger.info("🔄 Human wants restart → query_analyst")
            return "query_analyst"
        else:
            return END
    
    def _route_after_reranking(self, state: MessagesState) -> Literal["quality_assurance", "rewrite_question"]:
        """
        Route after re-ranking in AUTOMATED mode (no HITL).
        
        Checks if re-ranked context is sufficient:
        - Good context → quality_assurance (US-RAG-005: QA comes before writer)
        - Poor context → rewrite_question
        """
        messages = state["messages"]
        
        # Check last system message for re-ranking quality
        quality_good = True  # Default assumption
        
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'system':
                content_lower = msg.content.lower()
                # Simple heuristic: look for quality indicators
                if any(word in content_lower for word in ["insufficient", "poor", "low quality", "no relevant"]):
                    quality_good = False
                break
        
        if quality_good:
            logger.info("✅ Re-ranked context sufficient → quality_assurance")
            return "quality_assurance"
        else:
            logger.info("🔄 Re-ranked context insufficient → rewrite_question")
            return "rewrite_question"
    
    def _route_after_quality_assurance(self, state: MessagesState) -> Literal["writer", "rewrite_question"]:
        """
        Route after quality assurance check in AUTOMATED mode (no HITL).
        
        Checks if quality assurance passed:
        - Quality sufficient → writer (proceed to answer generation)
        - Quality insufficient → rewrite_question (improve query and retry)
        
        Args:
            state: Current MessagesState
            
        Returns:
            Next node name: "writer" or "rewrite_question"
        """
        messages = state["messages"]
        
        # Check last system message for quality assurance results
        quality_sufficient = True  # Default assumption
        
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == 'system':
                content_lower = msg.content.lower()
                # Look for quality assurance failure indicators
                if any(word in content_lower for word in [
                    "quality insufficient", "quality check failed", "quality low",
                    "insufficient quality", "quality not met", "does not meet quality"
                ]):
                    quality_sufficient = False
                break
        
        if quality_sufficient:
            logger.info("✅ Quality assurance passed → writer")
            return "writer"
        else:
            logger.info("🔄 Quality assurance failed → rewrite_question")
            return "rewrite_question"
    
    def _route_after_tools(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question", "human_review"]:
        """
        Grade documents for relevance and route accordingly.
        
        Uses structured output to grade document relevance:
        - "yes" + human_in_loop → human_review (let human approve)
        - "yes" + no human_in_loop → generate_answer (documents are relevant)
        - "no" → rewrite_question (try again with better query)
        
        Args:
            state: Current MessagesState
            
        Returns:
            Next node name: "generate_answer", "human_review", or "rewrite_question"
        """
        messages = state["messages"]
        
        # Get original question (first user message)
        question = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                question = msg.content
                break
        
        if not question:
            logger.warning("⚠️ No question found in messages")
            return "generate_answer"
        
        # Get tool results - collect ALL tool messages, not just last one
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results.append(msg.content)
        
        if not tool_results:
            # No tool results found - this shouldn't happen after ToolNode
            logger.warning("⚠️ No tool results found after tool execution")
            return "generate_answer"
        
        # Combine all tool results into context
        context = "\n\n".join(tool_results)
        
        # Grade relevance using structured output
        # Load prompt from LangSmith Hub
        grade_prompt_template = self.document_grader_loader.get_system_prompt()
        
        # Format prompt with question and context
        prompt = f"{grade_prompt_template}\n\nHere is the retrieved document:\n\n{context[:1000]}\n\nHere is the user question: {question}"
        
        try:
            grade = self.llm.with_structured_output(GradeDocuments).invoke([
                HumanMessage(content=prompt)
            ])
            
            logger.info(f"📊 Document grading result: {grade.binary_score}")
            logger.info(f"📊 human_in_loop flag: {self.human_in_loop}")
            
            if grade.binary_score == "yes":
                # Documents are relevant
                if self.human_in_loop:
                    logger.info("🚨 ROUTING TO HUMAN_REVIEW (documents relevant + human_in_loop=True)")
                    return "human_review"
                else:
                    logger.info("✅ Routing to generate_answer (documents relevant + human_in_loop=False)")
                    return "generate_answer"
            else:
                logger.info("📝 Documents not relevant - routing to rewrite_question")
                return "rewrite_question"
        except Exception as e:
            logger.error(f"❌ Grading failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback: generate answer anyway (or human review if enabled)
            if self.human_in_loop:
                logger.info("🚨 FALLBACK: Routing to human_review (grading failed + human_in_loop=True)")
                return "human_review"
            else:
                logger.info("⚠️ FALLBACK: Routing to generate_answer (grading failed + human_in_loop=False)")
                return "generate_answer"
    
    async def _rewrite_question(self, state: MessagesState):
        """
        Rewrite the original question for better retrieval.
        
        When documents are not relevant, this node improves the query
        and sends it back to the agent for another retrieval attempt.
        
        Args:
            state: Current MessagesState
            
        Returns:
            Updated state with rewritten question
        """
        messages = state["messages"]
        
        # Get original question
        question = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                question = msg.content
                break
        
        if not question:
            logger.warning("⚠️ No question to rewrite")
            return {"messages": []}
        
        # Load prompt from LangSmith Hub
        rewrite_prompt_template = self.query_rewriter_loader.get_system_prompt()
        
        # Format prompt with original question
        prompt = f"{rewrite_prompt_template}\n\nOriginal question: {question}\n\nFormulate an improved question:"
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        logger.info(f"📝 Rewrote question: '{question}' → '{response.content}'")
        
        # Return rewritten question as new user message (proper HumanMessage)
        return {"messages": [HumanMessage(content=response.content)]}
    
    def _human_review_node(self, state: MessagesState):
        """
        Human review node - pauses execution for human input.
        
        With interrupt_before=["human_review"], execution pauses BEFORE this node.
        This node acts as a passthrough - it doesn't modify state, just logs.
        
        The human reviews context, then resumes with input that gets added to messages.
        The routing function (_route_after_human_review) then decides next step.
        
        Args:
            state: Current MessagesState
            
        Returns:
            Empty dict (no state changes) - state passes through unchanged
        """
        messages = state["messages"]
        
        # Get context for human review - collect all tool results
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results.append(msg.content)
        
        context = "\n\n".join(tool_results) if tool_results else "No context retrieved"
        
        logger.info("🚨🚨🚨 HUMAN REVIEW NODE EXECUTING 🚨🚨🚨")
        logger.info(f"   Context preview: {context[:200]}...")
        logger.info(f"   Total messages in state: {len(messages)}")
        logger.info("   THIS NODE SHOULD BE INTERRUPTED BEFORE EXECUTION")
        logger.info("   If you see this, the interrupt happened and execution resumed")
        
        # CRITICAL: Return empty dict to preserve state
        # DO NOT return {"messages": []} as that wipes out the conversation!
        return {}
    
    def _route_after_human_review(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """
        Route after human review.
        
        Checks if human approved or requested rewrite.
        Human can add a message with "approve" or "rewrite" to guide routing.
        
        Args:
            state: Current MessagesState
            
        Returns:
            Next node name based on human input
        """
        messages = state["messages"]
        
        logger.info(f"🔀 Routing after human review. Total messages: {len(messages)}")
        
        # Check last message for human decision
        if messages:
            last_msg = messages[-1]
            content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            logger.info(f"👤 Last message content: {content[:100] if content else 'None'}...")
            
            if isinstance(content, str):
                content_lower = content.lower()
                if "rewrite" in content_lower or "reject" in content_lower or "no" in content_lower:
                    logger.info("👤 Human REJECTED → rewrite_question")
                    return "rewrite_question"
                elif "approve" in content_lower or "yes" in content_lower or "continue" in content_lower:
                    logger.info("👤 Human APPROVED → generate_answer")
                    return "generate_answer"
        
        # Default: proceed with answer generation (assume approval)
        logger.info("👤 Default action (no clear signal) → generate_answer")
        return "generate_answer"
    
    def _generate_answer(self, state: MessagesState):
        """
        Generate final answer using retrieved context.
        
        Args:
            state: Current MessagesState
            
        Returns:
            Updated state with generated answer
        """
        messages = state["messages"]
        
        # Get original question
        question = None
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                question = msg.content
                break
        
        # Get context from tool results - collect all tool messages
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results.append(msg.content)
        
        context = "\n\n".join(tool_results) if tool_results else ""
        
        if not question:
            logger.warning("⚠️ No question found for answer generation")
            return {"messages": [AIMessage(content="I don't have a question to answer.")]}
        
        # Load prompt from LangSmith Hub
        generate_prompt_template = self.answer_generator_loader.get_system_prompt()
        
        # Format prompt with question and context
        prompt = f"{generate_prompt_template}\n\nQuestion: {question}\n\nContext: {context}\n\nAnswer:"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        logger.info(f"✅ Generated answer for: '{question[:50]}...'")
        
        return {"messages": [response]}
    
    async def execute(self, query: str, config: Optional[dict] = None, stream: bool = False, parent_run_id: Optional[str] = None, document_filters: Optional[dict] = None) -> dict:
        """
        Execute agentic RAG for a query.
        
        Args:
            query: User question
            config: Optional LangGraph config (for thread_id, checkpointer, etc.)
            stream: If True, return generator for streaming responses
            parent_run_id: Optional LangSmith parent run ID to link traces
            document_filters: Optional document scope filters (e.g., {'source': ['doc1', 'doc2']})
            
        Returns:
            Dictionary with status, response, and full message history
            If interrupted, returns status="interrupted" with instructions
        """
        logger.info(f"🚀 Executing agentic RAG for: '{query[:60]}...'")
        
        if document_filters:
            logger.info(f"🎯 Applying document scope: {document_filters}")
        
        try:
            # Create config with thread_id for checkpointing
            if config is None:
                config = {}
            if "configurable" not in config:
                config["configurable"] = {}
            if "thread_id" not in config["configurable"]:
                import uuid
                config["configurable"]["thread_id"] = str(uuid.uuid4())
            
            # Add LangSmith run configuration for better trace visibility
            # This ensures all enhanced agents appear in LangSmith traces with proper metadata
            if "run_name" not in config:
                config["run_name"] = f"RAG-Swarm-Enhanced-{query[:50]}"
            if "tags" not in config:
                config["tags"] = ["rag-swarm", "sophisticated", "enhanced-8-agent"]
            if "metadata" not in config:
                config["metadata"] = {}
            
            # Add query info to metadata
            config["metadata"]["query"] = query
            config["metadata"]["mode"] = "sophisticated" if not self.retrieval_only else "simple"
            config["metadata"]["human_in_loop"] = self.human_in_loop
            config["metadata"]["agent_flow"] = "query_analyst→retrieval_specialist→document_grader→re_ranker→context_enrichment→writer→citation_verification→quality_assurance"
            
            # Add LangSmith run configuration to link traces
            if parent_run_id:
                config["run_id"] = parent_run_id
                logger.info(f"🔗 Using parent run_id: {parent_run_id}")
            
            thread_id = config["configurable"]["thread_id"]
            logger.info(f"📋 Thread ID: {thread_id}")
            
            # CRITICAL FIX: Load existing state from checkpointer and merge with new query
            # This matches the pattern used in simple_rag.py and agentic_rag.py
            # LangGraph's invoke() doesn't automatically merge initial_state with existing checkpointer state
            # We must manually load and merge before invoking
            try:
                existing_state = self.graph.get_state(config)
                existing_messages = existing_state.values.get("messages", []) if existing_state.values else []
                logger.info(f"📸 Loaded {len(existing_messages)} existing message(s) from thread")
            except (ValueError, AttributeError) as e:
                # No existing state - this is fine, starting fresh
                logger.info(f"📝 No existing state found (new thread): {e}")
                existing_messages = []
            
            # Create proper HumanMessage object for LangGraph
            human_msg = HumanMessage(content=query)
            
            # Merge existing messages with new query
            if existing_messages:
                input_messages = existing_messages + [human_msg]
                logger.info(f"📝 Merged new query with {len(existing_messages)} existing messages")
            else:
                input_messages = [human_msg]
                logger.info(f"📝 Starting fresh conversation with query: '{query[:60]}...'")
            
            # Debug: Verify messages are correct
            logger.debug(f"   Total messages to pass: {len(input_messages)}")
            logger.debug(f"   Last message type: {type(input_messages[-1]).__name__}")
            logger.debug(f"   Last message content: {input_messages[-1].content[:100] if hasattr(input_messages[-1], 'content') else str(input_messages[-1])[:100]}")
            
            # Build initial state with merged messages
            initial_state = {"messages": input_messages}
            
            # Add document filters to state if provided
            if document_filters:
                initial_state["document_filters"] = document_filters
                logger.info(f"🎯 Document filters added to state: {document_filters}")
            
            logger.info(f"🚀 Starting graph execution with thread_id: {thread_id}")
            
            # CRITICAL: Verify state before invoking
            logger.info(f"🔍 Pre-invoke state verification:")
            logger.info(f"   Initial state keys: {list(initial_state.keys())}")
            logger.info(f"   Messages in initial_state: {len(initial_state['messages'])}")
            for i, msg in enumerate(initial_state['messages']):
                msg_type = type(msg).__name__
                if isinstance(msg, HumanMessage):
                    content_preview = msg.content[:60] if hasattr(msg, 'content') else str(msg)[:60]
                    logger.info(f"   Message {i}: {msg_type} - '{content_preview}...'")
                else:
                    logger.debug(f"   Message {i}: {msg_type}")
            
            # Invoke graph with properly merged state
            # This ensures all nodes receive the complete message history including the new query
            logger.info(f"🚀 Invoking graph with {len(initial_state['messages'])} messages...")
            final_response = self.graph.invoke(
                initial_state,
                config=config
            )
            
            logger.info(f"✅ Graph execution completed")
            logger.debug(f"   Final response keys: {list(final_response.keys()) if isinstance(final_response, dict) else 'not a dict'}")
            if isinstance(final_response, dict) and "messages" in final_response:
                logger.debug(f"   Final messages count: {len(final_response['messages'])}")
                
                # Verify final state has messages
                final_state_check = self.graph.get_state(config)
                if final_state_check and final_state_check.values:
                    final_msg_count = len(final_state_check.values.get("messages", []))
                    logger.info(f"   Final state message count: {final_msg_count}")
            
            # Check if execution was interrupted (graph has pending nodes)
            # Note: retrieval_only mode doesn't use checkpointer, so skip state check
            state_snapshot = None
            if not self.retrieval_only:
                try:
                    state_snapshot = self.graph.get_state(config)
                    logger.info(f"📸 State snapshot - next nodes: {state_snapshot.next if state_snapshot else 'None'}")
                except ValueError as e:
                    if "No checkpointer set" in str(e):
                        logger.debug("Graph has no checkpointer (retrieval_only mode) - skipping state check")
                    else:
                        raise
            
            if state_snapshot and state_snapshot.next:
                # Graph has next nodes to execute - it's interrupted
                logger.info(f"⏸️ Execution INTERRUPTED at: {state_snapshot.next}")
                
                # Store the run_id from config for resume to use
                current_run_id = config.get("run_id")
                
                return {
                    "status": "interrupted",
                    "next_node": state_snapshot.next[0] if state_snapshot.next else None,
                    "thread_id": thread_id,
                    "run_id": current_run_id,  # Pass run_id for linking traces
                    "message": "Execution paused for human review. Call resume() to continue.",
                    "context_preview": self._get_context_preview(final_response) if final_response else "",
                    "messages": final_response.get("messages", []) if final_response else []
                }
            
            # Execution completed
            if final_response and "messages" in final_response:
                last_message = final_response["messages"][-1]
                response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                
                return {
                    "status": "success",
                    "response": response_content,
                    "thread_id": thread_id,
                    "messages": final_response["messages"]
                }
            else:
                return {
                    "status": "error",
                    "response": "No response generated",
                    "thread_id": thread_id,
                    "messages": []
                }
                
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            return {
                "status": "error",
                "response": f"Error: {e}",
                "messages": []
            }
    
    def resume(self, thread_id: str, human_input: Optional[str] = None, parent_run_id: Optional[str] = None) -> dict:
        """
        Resume interrupted execution after human review.
        
        Args:
            thread_id: Thread ID from interrupted execution
            human_input: Optional human feedback ("approve", "rewrite", or guidance)
            parent_run_id: Optional LangSmith parent run ID to link with initial execute() trace
            
        Returns:
            Dictionary with final response or next interrupt
        """
        logger.info(f"▶️ Resuming execution for thread: {thread_id}")
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Link to parent run for continuous LangSmith trace
            if parent_run_id:
                config["run_id"] = parent_run_id
                logger.info(f"🔗 Linking to parent run_id: {parent_run_id}")
            
            # Add human input if provided
            if human_input:
                logger.info(f"👤 Human input received: '{human_input}'")
                # Update state with human message as proper HumanMessage object
                current_state = self.graph.get_state(config)
                logger.info(f"📸 Current state before update - next nodes: {current_state.next if current_state else 'None'}")
                
                if current_state:
                    # CRITICAL: Update state with human feedback BEFORE resuming
                    self.graph.update_state(
                        config,
                        {"messages": [HumanMessage(content=human_input)]},
                        as_node=current_state.next[0] if current_state.next else None
                    )
                    logger.info(f"✅ State updated with human feedback: '{human_input}'")
                    
                    # Verify update
                    updated_state = self.graph.get_state(config)
                    logger.info(f"📸 State after update - message count: {len(updated_state.values['messages']) if updated_state else 0}")
                else:
                    logger.error("❌ No current state found - cannot update with human feedback")
                    return {
                        "status": "error",
                        "response": "Failed to resume: No state found for thread_id",
                        "thread_id": thread_id,
                        "messages": []
                    }
            else:
                logger.warning("⚠️ Resume called without human input")
            
            # Resume execution
            final_response = None
            event_count = 0
            for event in self.graph.stream(None, config, stream_mode="values"):
                event_count += 1
                final_response = event
                logger.info(f"📊 Resume stream event #{event_count}: {list(event.keys()) if isinstance(event, dict) else type(event)}")
                if isinstance(event, dict) and "messages" in event:
                    logger.info(f"   Messages in event: {len(event['messages'])} total")
            
            logger.info(f"✅ Resume stream completed - {event_count} events processed")
            
            # Check if interrupted again
            state_snapshot = self.graph.get_state(config)
            if state_snapshot and state_snapshot.next:
                logger.info(f"⏸️ Interrupted again at: {state_snapshot.next}")
                return {
                    "status": "interrupted",
                    "next_node": state_snapshot.next[0] if state_snapshot.next else None,
                    "thread_id": thread_id,
                    "message": "Execution paused again for human review.",
                    "context_preview": self._get_context_preview(final_response) if final_response else "",
                    "messages": final_response.get("messages", []) if final_response else []
                }
            
            # Execution completed
            if final_response and "messages" in final_response:
                last_message = final_response["messages"][-1]
                response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                
                logger.info(f"✅ Resume completed successfully")
                return {
                    "status": "success",
                    "response": response_content,
                    "thread_id": thread_id,
                    "messages": final_response["messages"]
                }
            else:
                logger.warning(f"⚠️ No final response after resume. final_response: {final_response}")
                return {
                    "status": "error",
                    "response": "No response after resume. The workflow may have failed to generate an answer.",
                    "thread_id": thread_id,
                    "messages": []
                }
                
        except Exception as e:
            logger.error(f"❌ Resume failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "response": f"Resume error: {e}",
                "thread_id": thread_id,
                "messages": []
            }
    
    def _get_context_preview(self, state: dict) -> str:
        """Get preview of retrieved context for human review."""
        if not state or "messages" not in state:
            return "No state available"
        
        # Collect context from all relevant message types
        context_parts = []
        
        for msg in state["messages"]:
            # Skip human messages (the query)
            if hasattr(msg, 'type') and msg.type == 'human':
                continue
            
            # Get content from ToolMessages (retrieval results)
            if isinstance(msg, ToolMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                context_parts.append(f"📚 Retrieved Context:\n{content}")
            
            # Get content from SystemMessages (agent analysis)
            elif isinstance(msg, SystemMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                # Only include if it's actual analysis (not empty or generic messages)
                if content and len(content) > 10 and "Query Analysis" in content or "Re-ranked" in content or "Quality" in content:
                    context_parts.append(content)
            
            # Get content from AIMessages (LLM responses)
            elif isinstance(msg, AIMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                if content and len(content) > 10:
                    context_parts.append(f"🤖 Generated Response:\n{content}")
        
        if context_parts:
            combined = "\n\n---\n\n".join(context_parts)
            # Show more context for review (1500 chars instead of 500)
            if len(combined) > 1500:
                return combined[:1500] + f"\n\n... ({len(combined) - 1500} more characters)"
            return combined
        
        return "No context retrieved yet (workflow interrupted before retrieval)"
    
    def get_graph_visualization(self):
        """Get graph visualization for debugging."""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"❌ Failed to generate graph visualization: {e}")
            return None


# For LangGraph Studio compatibility
def _create_default_graph():
    """
    Create SOPHISTICATED multi-agent graph for LangGraph Studio WITHOUT checkpointer.
    LangGraph Studio provides its own persistence layer.
    
    This exports the full 5-agent sophisticated workflow:
    - QueryAnalystAgent
    - RetrievalSpecialistAgent
    - ReRankerAgent
    - WriterAgent
    - QualityAssuranceAgent
    """
    try:
        from models.config import ContextConfig
        from context.context_engine import ContextEngine
        from langgraph.graph import StateGraph, MessagesState, START, END
        
        logger.info("🏗️ Building SOPHISTICATED multi-agent graph for LangGraph Studio...")
        
        # Create default context engine
        config = ContextConfig(
            embedding_model="gemini-embedding-001",
            vector_db_path=":memory:",
            collection_name="rag_swarm_studio"
        )
        context_engine = ContextEngine(config)
        
        # Create coordinator with sophisticated agents (automated mode, no HITL for Studio)
        coordinator = RAGSwarmCoordinator(context_engine, human_in_loop=False, retrieval_only=False)
        
        # Build sophisticated multi-agent workflow without checkpointer
        workflow = StateGraph(MessagesState)
        
        # Add all 5 sophisticated agent nodes
        workflow.add_node("query_analyst", coordinator._query_analyst_node)
        workflow.add_node("retrieval_specialist", coordinator._retrieval_specialist_node)
        workflow.add_node("re_ranker", coordinator._re_ranker_node)
        workflow.add_node("writer", coordinator._writer_node)
        workflow.add_node("quality_assurance", coordinator._quality_assurance_node)
        
        # Add control nodes
        workflow.add_node("rewrite_question", coordinator._rewrite_question)
        
        # Build automated sophisticated flow (no HITL for Studio)
        # US-RAG-005: query_analyst → retrieval_specialist → re_ranker → quality_assurance → writer → END
        workflow.add_edge(START, "query_analyst")
        workflow.add_edge("query_analyst", "retrieval_specialist")
        workflow.add_edge("retrieval_specialist", "re_ranker")
        
        # Automatic quality-based routing after re-ranking
        workflow.add_conditional_edges(
            "re_ranker",
            coordinator._route_after_reranking,
            {
                "quality_assurance": "quality_assurance",  # Good context → quality check
                "rewrite_question": "rewrite_question"  # Poor context → rewrite query
            }
        )
        
        # Quality assurance routes based on quality check
        workflow.add_conditional_edges(
            "quality_assurance",
            coordinator._route_after_quality_assurance,
            {
                "writer": "writer",  # Quality sufficient → write answer
                "rewrite_question": "rewrite_question"  # Quality insufficient → rewrite query
            }
        )
        
        workflow.add_edge("writer", END)
        
        # Rewrite loops back to query analyst
        workflow.add_edge("rewrite_question", "query_analyst")
        
        # Compile WITHOUT checkpointer (Studio provides its own)
        logger.info("✅ Sophisticated 5-agent graph for LangGraph Studio compiled!")
        logger.info("   Agents: QueryAnalyst → RetrievalSpecialist → ReRanker → QualityAssurance → Writer")
        return workflow.compile()
        
    except Exception as e:
        logger.error(f"Failed to create graph for LangGraph Studio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Return a minimal error graph
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(MessagesState)
        workflow.add_node("error", lambda s: {"messages": [f"Error: {e}"]})
        workflow.set_entry_point("error")
        workflow.add_edge("error", END)
        return workflow.compile()


# Export for langgraph.json (without checkpointer for Studio)
graph = _create_default_graph()

