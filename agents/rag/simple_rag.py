"""
Simple RAG Agent - Phase 1: Foundation

Official LangChain pattern implementation for basic RAG:
- Single agent with retriever tool
- Simple flow: question → retrieval → answer
- No grading, no rewriting (Phase 2 feature)

Based on: https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/

Architecture:
    START → agent → [tools_condition] → tools → agent → END
                                      ↘ END

Components:
    - MessagesState: Official LangGraph state
    - create_retriever_tool: Official tool creation
    - ToolNode: Official tool execution
    - tools_condition: Official routing

Author: AI Dev Agent
Created: 2025-01-29
Story: US-RAG-006 Phase 0C
"""

import logging
import os
from typing import Dict, Any, List, Optional

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import create_retriever_tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from context.context_engine import ContextEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleRAG:
    """
    Simple RAG agent following official LangChain patterns.
    
    Phase 1: Foundation
    - Single LLM with retriever tool
    - Official LangGraph components only
    - Simple question → retrieval → answer
    
    Usage:
        >>> from context.context_engine import ContextEngine
        >>> context_engine = ContextEngine(collection_name="project_docs")
        >>> rag = SimpleRAG(context_engine)
        >>> 
        >>> result = rag.invoke("What is RAG?", thread_id="user-123")
        >>> print(result["response"])
    """
    
    def __init__(
        self,
        context_engine: ContextEngine,
        model: str = "gemini-2.5-flash",
        temperature: int = 0,
        k: int = 5
    ):
        """
        Initialize Simple RAG agent.
        
        Args:
            context_engine: ContextEngine for vector operations
            model: LLM model name (default: gemini-2.5-flash)
            temperature: LLM temperature (must be 0 for deterministic)
            k: Number of documents to retrieve
        """
        self.context_engine = context_engine
        self.k = k
        
        # Validate API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
        
        # Initialize LLM (project standard: Gemini 2.5 Flash, temp=0, REST)
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,  # MANDATORY: 0 for deterministic responses
            convert_system_message_to_human=True,  # Gemini compatibility
            transport="rest"  # CRITICAL: Avoid grpc event loop issues in Streamlit
        )
        
        logger.info(f"[INIT] ✅ LLM initialized: {model}, temp={temperature}, transport=rest")
        
        # Create retriever tool (official LangChain method)
        self.retriever_tool = self._create_retriever_tool()
        
        # Load system instruction from LangSmith Hub (project standard)
        from prompts.agent_prompt_loader import get_agent_prompt_loader
        prompt_loader = get_agent_prompt_loader("simple_rag_system")
        self.system_instruction = prompt_loader.get_system_prompt()
        
        # Build graph
        self.graph = self._build_graph()
        
        logger.info("[INIT] ✅ Simple RAG agent initialized successfully")
    
    def _create_retriever_tool(self):
        """
        Create retriever tool using official LangChain method.
        
        Returns:
            Retriever tool for LLM to call
        """
        # Get base retriever from vector store
        retriever = self.context_engine.vector_store.as_retriever(
            search_kwargs={"k": self.k}
        )
        
        # Create tool using official LangChain utility
        retriever_tool = create_retriever_tool(
            retriever,
            name="retrieve_project_docs",
            description=(
                "Search and return information from the project documentation. "
                "Use this tool when you need to find specific information to answer user questions. "
                "Input should be a search query."
            )
        )
        
        logger.info(f"[TOOL] ✅ Retriever tool created: {retriever_tool.name}")
        return retriever_tool
    
    def _agent_node(self, state: MessagesState) -> Dict[str, List]:
        """
        Agent node: LLM with retriever tool.
        
        The LLM decides whether to:
        1. Call the retriever tool to get context (first time only)
        2. Respond directly to the user (after getting tool results)
        
        Args:
            state: Current graph state (contains messages)
            
        Returns:
            Updated messages
        """
        messages = state["messages"]
        
        # Log current state
        logger.info(f"[AGENT] Processing {len(messages)} message(s)")
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            content_preview = str(msg.content)[:100] if hasattr(msg, 'content') else str(msg)[:100]
            logger.info(f"[AGENT] Message {i}: {msg_type} - {content_preview}...")
        
        # Check if we've already called tools (ToolMessage present)
        has_tool_results = any(isinstance(msg, ToolMessage) for msg in messages)
        
        if has_tool_results:
            # Tools already called - now generate final answer WITHOUT tools bound
            logger.info("[AGENT] Tool results present - generating final answer WITHOUT tools")
            response = self.llm.invoke(messages)
        else:
            # First call - bind tools so agent can retrieve
            logger.info("[AGENT] No tool results yet - binding tools for retrieval")
            response = self.llm.bind_tools([self.retriever_tool]).invoke(messages)
        
        # Log response details
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"[AGENT] → Calling tool: {response.tool_calls[0]['name']}")
        else:
            response_preview = str(response.content)[:200] if hasattr(response, 'content') else str(response)[:200]
            logger.info(f"[AGENT] → Responding directly: {response_preview}...")
        
        return {"messages": [response]}
    
    def _build_graph(self):
        """
        Build LangGraph workflow following official pattern.
        
        Graph structure:
            START → agent → [tools_condition] → tools → agent → END
                                              ↘ END
        
        Returns:
            Compiled graph
        """
        # Create state graph with MessagesState (official)
        workflow = StateGraph(MessagesState)
        
        # Add agent node
        workflow.add_node("agent", self._agent_node)
        
        # Add tools node (official ToolNode)
        workflow.add_node("tools", ToolNode([self.retriever_tool]))
        
        # Define edges
        workflow.add_edge(START, "agent")
        
        # Conditional edge: agent → tools OR END
        # Uses official tools_condition function
        workflow.add_conditional_edges(
            "agent",
            tools_condition,  # Prebuilt function checks if tools were called
            {
                "tools": "tools",  # If tools called, execute them
                END: END           # Otherwise, end conversation
            }
        )
        
        # After tools execute, return to agent for response
        workflow.add_edge("tools", "agent")
        
        # Compile graph with checkpointer for thread persistence
        # Set recursion_limit to prevent infinite tool-calling loops
        graph = workflow.compile(
            checkpointer=MemorySaver(),
            debug=False
        )
        
        logger.info("[GRAPH] ✅ Graph compiled successfully")
        logger.info("[GRAPH] Nodes: agent, tools")
        logger.info("[GRAPH] Edges: START→agent, agent→tools/END, tools→agent")
        
        return graph
    
    def invoke(
        self,
        query: str,
        thread_id: str = "default",
        document_filters: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Execute RAG workflow for a single query.
        
        Args:
            query: User question
            thread_id: Thread ID for conversation persistence
            document_filters: Optional document scope (e.g., {'source': ['url1', 'url2']})
            
        Returns:
            Dict with:
                - response: Final answer string
                - status: "completed" or "error"
                - messages: Full conversation history
                - thread_id: Thread ID used
        """
        try:
            logger.info(f"[INVOKE] Query: {query}")
            logger.info(f"[INVOKE] Thread: {thread_id}")
            
            # Apply document filters if provided
            if document_filters:
                logger.info(f"[INVOKE] Filters: {document_filters}")
                # TODO: Implement filter support in Phase 2
                logger.warning("[INVOKE] ⚠️ Document filters not yet supported in Phase 1")
            
            # Create config with thread ID and recursion limit
            config = {
                "configurable": {"thread_id": thread_id},
                "run_name": "simple_rag_query",
                "tags": ["simple_rag", "phase1"],
                "recursion_limit": 10  # Prevent infinite loops
            }
            
            # Load existing conversation from checkpointer and append new message
            from langchain_core.messages import SystemMessage
            
            # Get existing state for this thread (if any)
            try:
                existing_state = self.graph.get_state(config)
                existing_messages = existing_state.values.get("messages", []) if existing_state.values else []
                logger.info(f"[INVOKE] Loaded {len(existing_messages)} existing message(s) from thread")
            except Exception as e:
                logger.info(f"[INVOKE] No existing state found (new thread): {e}")
                existing_messages = []
            
            # Build messages: existing + system instruction (if first) + new query
            if not existing_messages:
                # First message in thread - add system instruction
                input_messages = [
                    SystemMessage(content=self.system_instruction),
                    HumanMessage(content=query)
                ]
                logger.info("[INVOKE] First message in thread - adding system instruction")
            else:
                # Continuing conversation - just add new query
                input_messages = existing_messages + [HumanMessage(content=query)]
                logger.info(f"[INVOKE] Continuing conversation - appending to {len(existing_messages)} messages")
            
            # Invoke graph
            logger.info("[INVOKE] → Executing graph...")
            result = self.graph.invoke(
                {"messages": input_messages},
                config=config
            )
            
            # Extract response
            messages = result.get("messages", [])
            
            logger.info(f"[INVOKE] Result contains {len(messages)} message(s)")
            
            if not messages:
                logger.error("[INVOKE] ❌ No messages in result")
                return {
                    "status": "error",
                    "error": "No messages returned from graph",
                    "response": "",
                    "messages": [],
                    "thread_id": thread_id
                }
            
            # Find last AIMessage with actual content (skip ToolMessages and empty AIMessages)
            response_text = ""
            for msg in reversed(messages):
                msg_type = type(msg).__name__
                logger.info(f"[INVOKE] Checking message: {msg_type}")
                
                if isinstance(msg, AIMessage):
                    # Check if this AIMessage has content (not just tool_calls)
                    has_tool_calls = hasattr(msg, 'tool_calls') and msg.tool_calls
                    content = msg.content if hasattr(msg, 'content') else ""
                    
                    logger.info(f"[INVOKE] AIMessage - has_tool_calls={has_tool_calls}, content_length={len(str(content))}")
                    
                    # Only use AIMessage if it has actual content text
                    if content and isinstance(content, str) and content.strip():
                        response_text = content
                        logger.info(f"[INVOKE] Found AIMessage with content: {response_text[:200]}...")
                        break
                    elif has_tool_calls:
                        logger.info(f"[INVOKE] Skipping AIMessage with tool_calls (no content)")
                    else:
                        logger.warning(f"[INVOKE] Skipping empty AIMessage")
            
            if not response_text:
                logger.error("[INVOKE] ❌ No AIMessage with content found")
                # Log all message types for debugging
                for i, msg in enumerate(messages):
                    msg_type = type(msg).__name__
                    if isinstance(msg, AIMessage):
                        has_tool_calls = hasattr(msg, 'tool_calls') and msg.tool_calls
                        content_len = len(msg.content) if hasattr(msg, 'content') else 0
                        logger.error(f"[INVOKE] Message {i}: {msg_type} - tool_calls={has_tool_calls}, content_len={content_len}")
                    else:
                        logger.error(f"[INVOKE] Message {i}: {msg_type}")
                
                return {
                    "status": "error",
                    "error": "No AI response with content found in graph output. Agent may be stuck in tool-calling loop.",
                    "response": "",
                    "messages": messages,
                    "thread_id": thread_id
                }
            
            logger.info(f"[INVOKE] ✅ Response generated ({len(response_text)} chars)")
            
            return {
                "status": "completed",
                "response": response_text,
                "messages": messages,
                "thread_id": thread_id
            }
            
        except Exception as e:
            logger.error(f"[INVOKE] ❌ Error: {e}")
            import traceback
            logger.error(f"[INVOKE] Traceback: {traceback.format_exc()}")
            
            return {
                "status": "error",
                "error": str(e),
                "response": f"Error: {e}",
                "messages": [],
                "thread_id": thread_id
            }
    
    def stream(
        self,
        query: str,
        thread_id: str = "default",
        document_filters: Optional[Dict[str, List[str]]] = None
    ):
        """
        Stream RAG workflow execution (for future UI integration).
        
        Args:
            query: User question
            thread_id: Thread ID for conversation persistence
            document_filters: Optional document scope
            
        Yields:
            Chunks of execution updates
        """
        try:
            logger.info(f"[STREAM] Query: {query}")
            logger.info(f"[STREAM] Thread: {thread_id}")
            
            # Apply document filters if provided
            if document_filters:
                logger.info(f"[STREAM] Filters: {document_filters}")
                logger.warning("[STREAM] ⚠️ Document filters not yet supported in Phase 1")
            
            # Create config
            config = {
                "configurable": {"thread_id": thread_id},
                "run_name": "simple_rag_stream",
                "tags": ["simple_rag", "phase1", "streaming"]
            }
            
            # Create input
            input_messages = [HumanMessage(content=query)]
            
            # Stream execution
            for chunk in self.graph.stream(
                {"messages": input_messages},
                config=config,
                stream_mode="updates"
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"[STREAM] ❌ Error: {e}")
            import traceback
            logger.error(f"[STREAM] Traceback: {traceback.format_exc()}")
            yield {"error": str(e)}


# Factory function for easy instantiation
def create_simple_rag(
    context_engine: ContextEngine,
    **kwargs
) -> SimpleRAG:
    """
    Factory function to create SimpleRAG instance.
    
    Args:
        context_engine: ContextEngine for vector operations
        **kwargs: Additional arguments for SimpleRAG
        
    Returns:
        SimpleRAG instance
    """
    return SimpleRAG(context_engine, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Simple RAG Agent - Phase 1 Test")
    print("=" * 70)
    
    # Initialize context engine
    print("\n[1] Initializing ContextEngine...")
    context_engine = ContextEngine(collection_name="project_docs")
    
    # Create RAG agent
    print("[2] Creating Simple RAG agent...")
    rag = SimpleRAG(context_engine)
    
    # Test queries
    test_queries = [
        "What is RAG?",
        "How does vector search work?",
        "What is LangGraph?",
    ]
    
    print(f"\n[3] Running {len(test_queries)} test queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print(f"{'='*70}")
        
        result = rag.invoke(query, thread_id="test-session")
        
        if result["status"] == "completed":
            print(f"\n✅ SUCCESS")
            print(f"Response: {result['response'][:200]}...")
        else:
            print(f"\n❌ ERROR: {result.get('error', 'Unknown error')}")
    
    print(f"\n{'='*70}")
    print("Test complete!")
    print(f"{'='*70}")

