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

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# LangChain imports
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

# Context engine
from context.context_engine import ContextEngine

logger = logging.getLogger(__name__)


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
    
    def __init__(self, context_engine: ContextEngine, human_in_loop: bool = False):
        """
        Initialize RAG Swarm Coordinator.
        
        Args:
            context_engine: ContextEngine instance with initialized vector store
            human_in_loop: Enable human approval before generating final answer
        """
        self.context_engine = context_engine
        self.human_in_loop = human_in_loop
        
        # Initialize LLM (use Gemini for consistency)
        self.llm = self._create_llm()
        
        # Load prompts from LangSmith Hub (following langgraph_workflow pattern)
        from prompts.agent_prompt_loader import get_agent_prompt_loader
        self.document_grader_loader = get_agent_prompt_loader("document_grader")
        self.query_rewriter_loader = get_agent_prompt_loader("query_rewriter")
        self.answer_generator_loader = get_agent_prompt_loader("answer_generator")
        
        # Create tools
        self.tools = self._create_tools()
        self.tool_node = ToolNode(self.tools)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build and compile graph (with checkpointing for interrupts)
        self.graph = self._build_graph()
        
        logger.info("✅ RAGSwarmCoordinator initialized with agentic RAG graph")
        logger.info(f"   Tools: {[t.name for t in self.tools]}")
        logger.info(f"   Human-in-loop: {self.human_in_loop}")
    
    def _create_llm(self):
        """Create LLM instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os
            
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY not set, LLM may fail")
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                convert_system_message_to_human=True
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
    
    def _build_graph(self) -> StateGraph:
        """
        Build agentic RAG graph with research assistant and human-in-loop support.
        
        Graph structure (with human-in-loop):
        START → agent → [tools_condition]
                        ├─ tools → [route_after_tools]
                        │          ├─ human_review → generate_answer → END
                        │          └─ rewrite_question → agent
                        └─ END (direct response)
        
        Interrupts:
        - Before generate_answer: Human can review retrieved context
        - After tools: Human can approve/reject retrieval results
        
        Returns:
            Compiled StateGraph with checkpointer for interrupts
        """
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)
        
        # Add human review node if human-in-loop enabled
        if self.human_in_loop:
            workflow.add_node("human_review", self._human_review_node)
        
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
        if self.human_in_loop:
            # With human-in-loop: route to human_review or rewrite
            workflow.add_conditional_edges(
                "tools",
                self._route_after_tools,
                {
                    "human_review": "human_review",
                    "rewrite_question": "rewrite_question"
                }
            )
            
            # Human review decides: generate answer or rewrite
            workflow.add_conditional_edges(
                "human_review",
                self._route_after_human_review,
                {
                    "generate_answer": "generate_answer",
                    "rewrite_question": "rewrite_question"
                }
            )
        else:
            # Without human-in-loop: direct routing
            workflow.add_conditional_edges(
                "tools",
                self._route_after_tools,
                {
                    "generate_answer": "generate_answer",
                    "rewrite_question": "rewrite_question"
                }
            )
        
        # Generate answer → END
        workflow.add_edge("generate_answer", END)
        
        # Rewrite question → back to agent
        workflow.add_edge("rewrite_question", "agent")
        
        # Compile with checkpointer for interrupts
        try:
            from langgraph.checkpoint.memory import MemorySaver
            checkpointer = MemorySaver()
            
            # Set interrupt points for human-in-loop
            interrupt_before = ["human_review"] if self.human_in_loop else []
            
            compiled = workflow.compile(
                checkpointer=checkpointer,
                interrupt_before=interrupt_before
            )
            
            logger.info(f"✅ Graph compiled with checkpointer (interrupts: {interrupt_before})")
            return compiled
            
        except Exception as e:
            logger.warning(f"⚠️ Could not enable checkpointer: {e}")
            # Fallback: compile without checkpointer
            return workflow.compile()
    
    def _agent_node(self, state: MessagesState):
        """
        Agent node with tool binding.
        
        The LLM decides whether to:
        - Use tools (retrieval, web search, Wikipedia)
        - Respond directly to the user
        
        Args:
            state: Current MessagesState
            
        Returns:
            Updated state with agent response
        """
        messages = state["messages"]
        
        # Add system message to guide tool usage
        # Only add if not already present
        has_system_message = any(
            hasattr(msg, 'type') and msg.type == 'system' 
            for msg in messages
        )
        
        if not has_system_message:
            from langchain_core.messages import SystemMessage
            system_msg = SystemMessage(content=(
                "You are a helpful research assistant with access to multiple knowledge sources.\n\n"
                "IMPORTANT: For ALL user questions, you MUST use the available tools to retrieve information.\n"
                "Available tools:\n"
                "- project_docs_tool: Search project documentation and codebase\n"
                "- web_search: Search the web for current information\n"
                "- wikipedia_search: Search Wikipedia for general knowledge\n\n"
                "Always call at least one tool to retrieve context before answering. "
                "Choose the most appropriate tool(s) based on the question:\n"
                "- Use project_docs_tool for questions about this project, code, architecture, or implementation\n"
                "- Use web_search for recent news, updates, or real-time information\n"
                "- Use wikipedia_search for general knowledge, concepts, or definitions\n\n"
                "After retrieving information, the system will automatically generate an answer using the retrieved context."
            ))
            messages = [system_msg] + list(messages)
        
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
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
                {"role": "user", "content": prompt}
            ])
            
            logger.info(f"📊 Document grading: {grade.binary_score}")
            
            if grade.binary_score == "yes":
                # Documents are relevant
                if self.human_in_loop:
                    logger.info("👤 Routing to human review")
                    return "human_review"
                else:
                    return "generate_answer"
            else:
                logger.info("📝 Documents not relevant - rewriting question")
                return "rewrite_question"
        except Exception as e:
            logger.error(f"❌ Grading failed: {e}")
            # Fallback: generate answer anyway
            if self.human_in_loop:
                return "human_review"
            else:
                return "generate_answer"
    
    def _rewrite_question(self, state: MessagesState):
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
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        logger.info(f"📝 Rewrote question: '{question}' → '{response.content}'")
        
        # Return rewritten question as new user message
        return {"messages": [{"role": "user", "content": response.content}]}
    
    def _human_review_node(self, state: MessagesState):
        """
        Human review node - pauses execution for human input.
        
        This node is interrupted before execution, allowing human to:
        - Review retrieved documents
        - Approve/reject the retrieval results
        - Provide additional guidance
        
        The human can then resume execution with approval or request rewrite.
        
        Args:
            state: Current MessagesState
            
        Returns:
            Updated state (unchanged, waiting for human input)
        """
        messages = state["messages"]
        
        # Get context for human review - collect all tool results
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                tool_results.append(msg.content)
        
        context = "\n\n".join(tool_results) if tool_results else "No context retrieved"
        
        logger.info("👤 Human review requested")
        logger.info(f"   Context preview: {context[:200]}...")
        
        # State is unchanged - human will provide input to resume
        return {"messages": []}
    
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
        
        # Check last message for human decision
        if messages:
            last_msg = messages[-1]
            content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            if isinstance(content, str):
                content_lower = content.lower()
                if "rewrite" in content_lower or "reject" in content_lower:
                    logger.info("👤 Human requested rewrite")
                    return "rewrite_question"
        
        # Default: proceed with answer generation
        logger.info("👤 Human approved - generating answer")
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
            return {"messages": [{"role": "assistant", "content": "I don't have a question to answer."}]}
        
        # Load prompt from LangSmith Hub
        generate_prompt_template = self.answer_generator_loader.get_system_prompt()
        
        # Format prompt with question and context
        prompt = f"{generate_prompt_template}\n\nQuestion: {question}\n\nContext: {context}\n\nAnswer:"
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        logger.info(f"✅ Generated answer for: '{question[:50]}...'")
        
        return {"messages": [response]}
    
    async def execute(self, query: str, config: Optional[dict] = None, stream: bool = False) -> dict:
        """
        Execute agentic RAG for a query.
        
        Args:
            query: User question
            config: Optional LangGraph config (for thread_id, checkpointer, etc.)
            stream: If True, return generator for streaming responses
            
        Returns:
            Dictionary with status, response, and full message history
            If interrupted, returns status="interrupted" with instructions
        """
        logger.info(f"🚀 Executing agentic RAG for: '{query[:60]}...'")
        
        try:
            # Create config with thread_id for checkpointing
            if config is None:
                config = {}
            if "configurable" not in config:
                config["configurable"] = {}
            if "thread_id" not in config["configurable"]:
                import uuid
                config["configurable"]["thread_id"] = str(uuid.uuid4())
            
            thread_id = config["configurable"]["thread_id"]
            logger.info(f"📋 Thread ID: {thread_id}")
            
            # Stream through graph
            final_response = None
            interrupted = False
            
            for event in self.graph.stream(
                {"messages": [{"role": "user", "content": query}]},
                config=config,
                stream_mode="values"
            ):
                final_response = event
                
                # Check if interrupted
                if self.human_in_loop and "messages" in event:
                    # If we're at human_review node, execution is interrupted
                    pass
            
            # Check if execution was interrupted (incomplete)
            state_snapshot = self.graph.get_state(config)
            if state_snapshot and state_snapshot.next:
                # Graph has next nodes to execute - it's interrupted
                interrupted = True
                logger.info(f"⏸️ Execution interrupted at: {state_snapshot.next}")
                
                return {
                    "status": "interrupted",
                    "next_node": state_snapshot.next[0] if state_snapshot.next else None,
                    "thread_id": thread_id,
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
    
    def resume(self, thread_id: str, human_input: Optional[str] = None) -> dict:
        """
        Resume interrupted execution after human review.
        
        Args:
            thread_id: Thread ID from interrupted execution
            human_input: Optional human feedback ("approve", "rewrite", or guidance)
            
        Returns:
            Dictionary with final response or next interrupt
        """
        logger.info(f"▶️ Resuming execution for thread: {thread_id}")
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Add human input if provided
            if human_input:
                logger.info(f"👤 Human input: {human_input}")
                # Update state with human message
                current_state = self.graph.get_state(config)
                if current_state:
                    self.graph.update_state(
                        config,
                        {"messages": [{"role": "human", "content": human_input}]}
                    )
            
            # Resume execution
            final_response = None
            for event in self.graph.stream(None, config, stream_mode="values"):
                final_response = event
            
            # Check if interrupted again
            state_snapshot = self.graph.get_state(config)
            if state_snapshot and state_snapshot.next:
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
                
                return {
                    "status": "success",
                    "response": response_content,
                    "thread_id": thread_id,
                    "messages": final_response["messages"]
                }
            else:
                return {
                    "status": "error",
                    "response": "No response after resume",
                    "thread_id": thread_id
                }
                
        except Exception as e:
            logger.error(f"❌ Resume failed: {e}")
            return {
                "status": "error",
                "response": f"Resume error: {e}",
                "thread_id": thread_id
            }
    
    def _get_context_preview(self, state: dict) -> str:
        """Get preview of retrieved context for human review."""
        if not state or "messages" not in state:
            return ""
        
        # Collect all tool results
        tool_results = []
        for msg in state["messages"]:
            if isinstance(msg, ToolMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                tool_results.append(content)
        
        if tool_results:
            combined = "\n\n".join(tool_results)
            return combined[:500] + "..." if len(combined) > 500 else combined
        
        return ""
    
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
    Create graph for LangGraph Studio.
    This initializes a default ContextEngine for Studio testing.
    """
    try:
        from models.config import ContextConfig
        from context.context_engine import ContextEngine
        
        # Create default context engine
        config = ContextConfig()
        context_engine = ContextEngine(config)
        
        # Create and return coordinator graph
        coordinator = RAGSwarmCoordinator(context_engine)
        return coordinator.graph
    except Exception as e:
        logger.error(f"Failed to create graph for LangGraph Studio: {e}")
        # Return a minimal error graph
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(MessagesState)
        workflow.add_node("error", lambda s: {"messages": [f"Error: {e}"]})
        workflow.set_entry_point("error")
        workflow.add_edge("error", END)
        return workflow.compile()


# Export for langgraph.json
graph = _create_default_graph()

