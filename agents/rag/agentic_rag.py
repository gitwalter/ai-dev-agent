"""
Agentic RAG - Phase 2: Intelligence

Official LangChain pattern with document grading and question rewriting:
- Grades retrieved documents for relevance
- Rewrites unclear questions for better retrieval
- Intelligent routing based on relevance

Based on: https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/

Architecture:
    START → agent → [tools_condition] → tools → grade_documents
                                      ↘ END        ↓            ↓
                                              generate_answer  rewrite_question
                                                    ↓                ↓
                                                  END            agent (retry)

Enhancements over Phase 1:
    - Document grading with structured output
    - Question rewriting loop
    - Conditional routing (relevant/not_relevant)

Author: AI Dev Agent
Created: 2025-01-29
Story: US-RAG-006 Phase 0D
"""

import logging
import os
from typing import Dict, Any, List, Optional, Literal

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import create_retriever_tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from pydantic import BaseModel, Field

from context.context_engine import ContextEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Structured output for document grading
class GradeDocuments(BaseModel):
    """Binary relevance score for retrieved documents."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if document is relevant to question, 'no' if not relevant"
    )


class AgenticRAG:
    """
    Agentic RAG with document grading and question rewriting.
    
    Phase 2: Intelligence
    - Grades retrieved documents for relevance
    - Rewrites unclear questions
    - Intelligent routing based on grading
    
    Enhancements over SimpleRAG (Phase 1):
    - Document grading node
    - Question rewriting node
    - Conditional routing (grade → generate OR rewrite)
    - Rewrite loop back to agent
    
    Usage:
        >>> from context.context_engine import ContextEngine
        >>> context_engine = ContextEngine(collection_name="project_docs")
        >>> rag = AgenticRAG(context_engine)
        >>> 
        >>> result = rag.invoke("Tell me about reward hacking", thread_id="user-123")
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
        Initialize Agentic RAG.
        
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
            temperature=temperature,  # MANDATORY: 0 for deterministic
            convert_system_message_to_human=True,
            transport="rest"  # CRITICAL: Avoid grpc event loop issues
        )
        
        # Initialize grader LLM with structured output
        self.grader_llm = self.llm.with_structured_output(GradeDocuments)
        
        logger.info(f"[INIT] ✅ LLMs initialized: {model}, temp={temperature}, transport=rest")
        
        # Create retriever tool
        self.retriever_tool = self._create_retriever_tool()
        
        # Load system instruction from LangSmith Hub (project standard)
        from prompts.agent_prompt_loader import get_agent_prompt_loader
        prompt_loader = get_agent_prompt_loader("agentic_rag_system")
        self.system_instruction = prompt_loader.get_system_prompt()
        
        # Build graph
        self.graph = self._build_graph()
        
        logger.info("[INIT] ✅ Agentic RAG initialized successfully")
    
    def _create_retriever_tool(self):
        """Create retriever tool using official LangChain method."""
        retriever = self.context_engine.vector_store.as_retriever(
            search_kwargs={"k": self.k}
        )
        
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
        
        Decides whether to call retriever tool or respond directly.
        """
        messages = state["messages"]
        logger.info(f"[AGENT] Processing {len(messages)} message(s)")
        
        # Prepend system message if not already present
        from langchain_core.messages import SystemMessage
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=self.system_instruction)] + messages
        
        # Bind tools and invoke
        response = self.llm.bind_tools([self.retriever_tool]).invoke(messages)
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"[AGENT] → Calling tool: {response.tool_calls[0]['name']}")
        else:
            logger.info("[AGENT] → Responding directly (no tool call)")
        
        return {"messages": [response]}
    
    def _grade_documents_node(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """
        Grade documents for relevance.
        
        Returns:
            "generate_answer" if relevant, "rewrite_question" if not
        """
        messages = state["messages"]
        
        # Get original question (first HumanMessage)
        question = None
        for msg in messages:
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
        
        if not question:
            logger.error("[GRADE] ❌ No question found in messages")
            return "generate_answer"  # Fallback
        
        # Get retrieved context (last ToolMessage)
        context = None
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                context = msg.content
                break
        
        if not context:
            logger.error("[GRADE] ❌ No context found in messages")
            return "rewrite_question"  # No context = rewrite
        
        logger.info(f"[GRADE] Grading context ({len(context)} chars) for question")
        
        # Grade with structured output
        grade_prompt = f"""You are a grader assessing relevance of a retrieved document to a user question.
        
Here is the retrieved document:
{context}

Here is the user question:
{question}

If the document contains keywords or semantic meaning related to the user question, grade it as relevant.
Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question."""
        
        try:
            response = self.grader_llm.invoke([{"role": "user", "content": grade_prompt}])
            score = response.binary_score
            
            logger.info(f"[GRADE] → Score: {score}")
            
            if score == "yes":
                logger.info("[GRADE] ✅ Documents relevant → generate_answer")
                return "generate_answer"
            else:
                logger.info("[GRADE] ❌ Documents not relevant → rewrite_question")
                return "rewrite_question"
                
        except Exception as e:
            logger.error(f"[GRADE] ❌ Grading error: {e}")
            return "generate_answer"  # Fallback to generating answer
    
    def _rewrite_question_node(self, state: MessagesState) -> Dict[str, List]:
        """
        Rewrite question for better retrieval.
        
        Replaces original question with improved version.
        """
        messages = state["messages"]
        
        # Get original question
        question = None
        for msg in messages:
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
        
        if not question:
            logger.error("[REWRITE] ❌ No question found")
            return {"messages": []}
        
        logger.info(f"[REWRITE] Rewriting question: {question}")
        
        rewrite_prompt = f"""Look at the input question and try to reason about the underlying semantic intent/meaning.

Original question:
{question}

Formulate an improved question that will retrieve better, more relevant context from the documentation.
Return only the improved question, nothing else."""
        
        try:
            response = self.llm.invoke([{"role": "user", "content": rewrite_prompt}])
            rewritten = response.content
            
            logger.info(f"[REWRITE] ✅ Rewritten to: {rewritten}")
            
            # Replace original question with rewritten version
            # This causes the agent to retry with better question
            return {"messages": [HumanMessage(content=rewritten)]}
            
        except Exception as e:
            logger.error(f"[REWRITE] ❌ Rewrite error: {e}")
            return {"messages": []}  # Keep original
    
    def _generate_answer_node(self, state: MessagesState) -> Dict[str, List]:
        """
        Generate final answer using retrieved context.
        """
        messages = state["messages"]
        
        # Get question
        question = None
        for msg in messages:
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
        
        # Get context
        context = None
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                context = msg.content
                break
        
        if not question or not context:
            logger.error("[GENERATE] ❌ Missing question or context")
            return {"messages": [AIMessage(content="Error: Missing question or context")]}
        
        logger.info(f"[GENERATE] Generating answer ({len(context)} chars context)")
        
        answer_prompt = f"""You are an assistant for question-answering tasks.
Use the following retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}"""
        
        try:
            response = self.llm.invoke([{"role": "user", "content": answer_prompt}])
            
            logger.info(f"[GENERATE] ✅ Answer generated ({len(response.content)} chars)")
            
            return {"messages": [response]}
            
        except Exception as e:
            logger.error(f"[GENERATE] ❌ Generation error: {e}")
            return {"messages": [AIMessage(content=f"Error generating answer: {e}")]}
    
    def _build_graph(self):
        """
        Build LangGraph workflow with grading and rewriting.
        
        Graph structure:
            START → agent → [tools_condition] → tools → grade_documents
                                              ↘ END        ↓            ↓
                                                      generate_answer  rewrite_question
                                                            ↓                ↓
                                                          END            agent (retry)
        """
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode([self.retriever_tool]))
        workflow.add_node("generate_answer", self._generate_answer_node)
        workflow.add_node("rewrite_question", self._rewrite_question_node)
        
        # Define edges
        workflow.add_edge(START, "agent")
        
        # Agent → tools OR END
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Tools → grade_documents (conditional routing)
        workflow.add_conditional_edges(
            "tools",
            self._grade_documents_node,  # Returns "generate_answer" or "rewrite_question"
            {
                "generate_answer": "generate_answer",
                "rewrite_question": "rewrite_question"
            }
        )
        
        # Generate answer → END
        workflow.add_edge("generate_answer", END)
        
        # Rewrite question → agent (retry with better question)
        workflow.add_edge("rewrite_question", "agent")
        
        # Compile
        graph = workflow.compile(checkpointer=MemorySaver())
        
        logger.info("[GRAPH] ✅ Agentic RAG graph compiled")
        logger.info("[GRAPH] Nodes: agent, tools, grade_documents, generate_answer, rewrite_question")
        logger.info("[GRAPH] Routing: tools→grade→(generate OR rewrite→agent)")
        
        return graph
    
    def invoke(
        self,
        query: str,
        thread_id: str = "default",
        document_filters: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Execute Agentic RAG workflow.
        
        Args:
            query: User question
            thread_id: Thread ID for conversation persistence
            document_filters: Optional document scope
            
        Returns:
            Dict with response, status, messages, thread_id
        """
        try:
            logger.info(f"[INVOKE] Query: {query}")
            logger.info(f"[INVOKE] Thread: {thread_id}")
            
            if document_filters:
                logger.info(f"[INVOKE] Filters: {document_filters}")
                logger.warning("[INVOKE] ⚠️ Document filters not yet supported")
            
            # Config
            config = {
                "configurable": {"thread_id": thread_id},
                "run_name": "agentic_rag_query",
                "tags": ["agentic_rag", "phase2"]
            }
            
            # Load existing conversation from checkpointer and append new message
            try:
                existing_state = self.graph.get_state(config)
                existing_messages = existing_state.values.get("messages", []) if existing_state.values else []
                logger.info(f"[INVOKE] Loaded {len(existing_messages)} existing message(s) from thread")
            except Exception as e:
                logger.info(f"[INVOKE] No existing state found (new thread): {e}")
                existing_messages = []
            
            # Append new query to existing conversation
            if existing_messages:
                input_messages = existing_messages + [HumanMessage(content=query)]
                logger.info(f"[INVOKE] Continuing conversation with {len(existing_messages)} previous messages")
            else:
                input_messages = [HumanMessage(content=query)]
                logger.info("[INVOKE] Starting new conversation")
            
            # Invoke
            logger.info("[INVOKE] → Executing graph...")
            result = self.graph.invoke(
                {"messages": input_messages},
                config=config
            )
            
            # Extract response
            messages = result.get("messages", [])
            
            if not messages:
                logger.error("[INVOKE] ❌ No messages in result")
                return {
                    "status": "error",
                    "error": "No messages returned",
                    "response": "",
                    "messages": [],
                    "thread_id": thread_id
                }
            
            # Get last AI message
            last_message = messages[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
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
        Stream Agentic RAG execution.
        
        Args:
            query: User question
            thread_id: Thread ID
            document_filters: Optional filters
            
        Yields:
            Execution updates
        """
        try:
            logger.info(f"[STREAM] Query: {query}")
            logger.info(f"[STREAM] Thread: {thread_id}")
            
            if document_filters:
                logger.warning("[STREAM] ⚠️ Document filters not yet supported")
            
            config = {
                "configurable": {"thread_id": thread_id},
                "run_name": "agentic_rag_stream",
                "tags": ["agentic_rag", "phase2", "streaming"]
            }
            
            # Load existing conversation from checkpointer
            try:
                existing_state = self.graph.get_state(config)
                existing_messages = existing_state.values.get("messages", []) if existing_state.values else []
                logger.info(f"[STREAM] Loaded {len(existing_messages)} existing message(s) from thread")
            except Exception as e:
                logger.info(f"[STREAM] No existing state found (new thread): {e}")
                existing_messages = []
            
            # Append new query to existing conversation
            if existing_messages:
                input_messages = existing_messages + [HumanMessage(content=query)]
            else:
                input_messages = [HumanMessage(content=query)]
            
            for chunk in self.graph.stream(
                {"messages": input_messages},
                config=config,
                stream_mode="updates"
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"[STREAM] ❌ Error: {e}")
            yield {"error": str(e)}


# Factory function
def create_agentic_rag(
    context_engine: ContextEngine,
    **kwargs
) -> AgenticRAG:
    """
    Factory function to create AgenticRAG instance.
    
    Args:
        context_engine: ContextEngine for vector operations
        **kwargs: Additional arguments
        
    Returns:
        AgenticRAG instance
    """
    return AgenticRAG(context_engine, **kwargs)


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Agentic RAG - Phase 2 Test")
    print("=" * 70)
    
    # Initialize
    print("\n[1] Initializing ContextEngine...")
    context_engine = ContextEngine(collection_name="project_docs")
    
    print("[2] Creating Agentic RAG...")
    rag = AgenticRAG(context_engine)
    
    # Test queries
    test_queries = [
        "What types of reward hacking exist?",  # Should find relevant docs
        "What is the capital of France?",       # Should detect irrelevant, rewrite
        "How does LangGraph work?",             # Should find relevant docs
    ]
    
    print(f"\n[3] Running {len(test_queries)} test queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print(f"{'='*70}")
        
        result = rag.invoke(query, thread_id="test-agentic")
        
        if result["status"] == "completed":
            print(f"\n✅ SUCCESS")
            print(f"Response: {result['response'][:200]}...")
        else:
            print(f"\n❌ ERROR: {result.get('error', 'Unknown error')}")
    
    print(f"\n{'='*70}")
    print("Test complete!")
    print(f"{'='*70}")

