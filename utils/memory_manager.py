"""
Memory Management System for AI Development Agent

This module implements the long-term memory infrastructure using vector stores
and knowledge triples for persistent, semantic memory capabilities.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict
from pathlib import Path

import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.tools import tool
from langchain_core.output_parsers import JsonOutputParser

# Import project-specific modules
from models.state import AgentState


class KnowledgeTriple(TypedDict):
    """Structured knowledge triple for memory storage."""
    subject: str
    predicate: str
    object: str
    context: str
    confidence: float
    timestamp: str
    source: str
    user_id: str


class MemoryManager:
    """Manages long-term memory using vector stores and knowledge triples."""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.vector_store = None
        self.embeddings = None
        self.memory_dir = Path("generated/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store with embeddings."""
        try:
            # Get API key from Streamlit secrets
            openai_api_key = st.secrets.get("OPENAI_API_KEY")
            if not openai_api_key:
                # Fallback to Gemini embeddings if OpenAI not available
                self.embeddings = self._create_gemini_embeddings()
            else:
                self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            
            if self.embeddings:
                # Initialize Chroma vector store
                persist_directory = str(self.memory_dir / f"vectorstore_{self.user_id}")
                self.vector_store = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=self.embeddings
                )
            
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
            # Fallback to in-memory storage
            self.vector_store = None
    
    def _create_gemini_embeddings(self):
        """Create fallback embeddings using Gemini."""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            gemini_api_key = st.secrets.get("GEMINI_API_KEY")
            if gemini_api_key:
                return GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=gemini_api_key
                )
        except Exception as e:
            print(f"Warning: Could not create Gemini embeddings: {e}")
        
        # Return None if no embeddings available
        return None
    
    async def save_recall_memory(
        self,
        content: str,
        context: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save a memory to the vector store."""
        try:
            if not self.vector_store or not self.embeddings:
                return await self._save_memory_fallback(content, context, metadata)
            
            # Create document for vector store
            doc = Document(
                page_content=content,
                metadata={
                    "context": context,
                    "user_id": self.user_id,
                    "timestamp": datetime.now().isoformat(),
                    "memory_id": str(uuid.uuid4()),
                    **(metadata or {})
                }
            )
            
            # Add to vector store
            self.vector_store.add_documents([doc])
            self.vector_store.persist()
            
            return doc.metadata["memory_id"]
            
        except Exception as e:
            print(f"Error saving memory: {e}")
            return await self._save_memory_fallback(content, context, metadata)
    
    async def search_recall_memories(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories."""
        try:
            if not self.vector_store:
                return await self._search_memory_fallback(query, k)
            
            # Prepare filter
            filter_dict = {"user_id": self.user_id}
            if filter_metadata:
                filter_dict.update(filter_metadata)
            
            # Search vector store
            results = self.vector_store.similarity_search_with_relevance_scores(
                query, k=k, filter=filter_dict
            )
            
            # Format results
            memories = []
            for doc, score in results:
                memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
            
            return memories
            
        except Exception as e:
            print(f"Error searching memories: {e}")
            return await self._search_memory_fallback(query, k)
    
    async def save_knowledge_triple(
        self,
        subject: str,
        predicate: str,
        obj: str,
        context: str = "",
        confidence: float = 1.0,
        source: str = "agent"
    ) -> str:
        """Save a structured knowledge triple."""
        try:
            triple = KnowledgeTriple(
                subject=subject,
                predicate=predicate,
                object=obj,
                context=context,
                confidence=confidence,
                timestamp=datetime.now().isoformat(),
                source=source,
                user_id=self.user_id
            )
            
            # Save as structured memory
            triple_id = str(uuid.uuid4())
            triple_file = self.memory_dir / f"triple_{self.user_id}_{triple_id}.json"
            
            with open(triple_file, 'w') as f:
                json.dump(triple, f, indent=2)
            
            # Also save as searchable memory
            content = f"{subject} {predicate} {obj}"
            await self.save_recall_memory(
                content=content,
                context=context,
                metadata={
                    "type": "knowledge_triple",
                    "triple_id": triple_id,
                    "subject": subject,
                    "predicate": predicate,
                    "object": obj,
                    "confidence": confidence,
                    "source": source
                }
            )
            
            return triple_id
            
        except Exception as e:
            print(f"Error saving knowledge triple: {e}")
            return ""
    
    async def extract_knowledge_triples(
        self,
        text: str,
        context: str = ""
    ) -> List[KnowledgeTriple]:
        """Extract knowledge triples from text using LLM."""
        try:
            # Get LLM for triple extraction
            from utils.helpers import get_llm_model
            llm = get_llm_model("complex")  # Use complex model for triple extraction
            
            # Create extraction prompt
            extraction_prompt = f"""
            Extract knowledge triples from the following text. A knowledge triple consists of:
            - Subject: The main entity or concept
            - Predicate: The relationship or action
            - Object: The target or result
            
            Text: {text}
            Context: {context}
            
            Return a JSON array of triples in this format:
            [
                {{
                    "subject": "entity or concept",
                    "predicate": "relationship or action", 
                    "object": "target or result",
                    "confidence": 0.9
                }}
            ]
            
            Only extract triples that are clearly stated or strongly implied in the text.
            """
            
            # Extract triples using LLM
            response = await llm.ainvoke(extraction_prompt)
            
            # Parse response
            parser = JsonOutputParser()
            try:
                triples_data = parser.parse(response.content)
                
                # Convert to KnowledgeTriple format
                triples = []
                for triple_data in triples_data:
                    triple = KnowledgeTriple(
                        subject=triple_data["subject"],
                        predicate=triple_data["predicate"],
                        object=triple_data["object"],
                        context=context,
                        confidence=triple_data.get("confidence", 0.8),
                        timestamp=datetime.now().isoformat(),
                        source="llm_extraction",
                        user_id=self.user_id
                    )
                    triples.append(triple)
                
                return triples
                
            except Exception as parse_error:
                print(f"Error parsing triples: {parse_error}")
                return []
                
        except Exception as e:
            print(f"Error extracting knowledge triples: {e}")
            return []
    
    async def _save_memory_fallback(
        self,
        content: str,
        context: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Fallback memory storage when vector store is unavailable."""
        try:
            memory_id = str(uuid.uuid4())
            memory_data = {
                "content": content,
                "context": context,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "user_id": self.user_id,
                "memory_id": memory_id
            }
            
            # Save to file
            memory_file = self.memory_dir / f"memory_{self.user_id}_{memory_id}.json"
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            return memory_id
            
        except Exception as e:
            print(f"Error in fallback memory save: {e}")
            return ""
    
    async def _search_memory_fallback(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Fallback memory search when vector store is unavailable."""
        try:
            # Simple text-based search in fallback files
            memories = []
            memory_files = list(self.memory_dir.glob(f"memory_{self.user_id}_*.json"))
            
            for memory_file in memory_files:
                try:
                    with open(memory_file, 'r') as f:
                        memory_data = json.load(f)
                    
                    # Simple relevance check (contains query words)
                    query_words = query.lower().split()
                    content_words = memory_data["content"].lower().split()
                    
                    # Calculate relevance score
                    if query_words:
                        relevance_score = sum(1 for word in query_words if word in content_words) / len(query_words)
                    else:
                        relevance_score = 0.0
                    
                    # Include all memories with any relevance
                    if relevance_score > 0:
                        memories.append({
                            "content": memory_data["content"],
                            "metadata": memory_data.get("metadata", {}),
                            "relevance_score": relevance_score
                        })
                        
                except Exception as e:
                    print(f"Error reading memory file {memory_file}: {e}")
                    continue
            
            # Sort by relevance and return top k
            memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            return memories[:k]
            
        except Exception as e:
            print(f"Error in fallback memory search: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        try:
            stats = {
                "user_id": self.user_id,
                "vector_store_available": self.vector_store is not None,
                "embeddings_available": self.embeddings is not None,
                "memory_files_count": 0,
                "triple_files_count": 0
            }
            
            # Count memory files
            memory_files = list(self.memory_dir.glob(f"memory_{self.user_id}_*.json"))
            triple_files = list(self.memory_dir.glob(f"triple_{self.user_id}_*.json"))
            
            stats["memory_files_count"] = len(memory_files)
            stats["triple_files_count"] = len(triple_files)
            
            return stats
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"error": str(e)}


# LangChain tools for memory operations
@tool
async def save_recall_memory(
    content: str,
    context: str = "",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save a memory to the long-term memory system.
    
    Args:
        content: The content to remember
        context: Additional context for the memory
        metadata: Optional metadata for the memory
        
    Returns:
        Memory ID of the saved memory
    """
    memory_manager = MemoryManager()
    return await memory_manager.save_recall_memory(content, context, metadata)


@tool
async def search_recall_memories(
    query: str,
    k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for relevant memories in the long-term memory system.
    
    Args:
        query: Search query
        k: Number of results to return
        filter_metadata: Optional metadata filters
        
    Returns:
        List of relevant memories with relevance scores
    """
    memory_manager = MemoryManager()
    return await memory_manager.search_recall_memories(query, k, filter_metadata)


@tool
async def save_knowledge_triple(
    subject: str,
    predicate: str,
    obj: str,
    context: str = "",
    confidence: float = 1.0,
    source: str = "agent"
) -> str:
    """
    Save a structured knowledge triple to the memory system.
    
    Args:
        subject: The main entity or concept
        predicate: The relationship or action
        obj: The target or result
        context: Additional context
        confidence: Confidence score (0.0 to 1.0)
        source: Source of the knowledge
        
    Returns:
        Triple ID of the saved knowledge triple
    """
    memory_manager = MemoryManager()
    return await memory_manager.save_knowledge_triple(
        subject, predicate, obj, context, confidence, source
    )


@tool
async def extract_knowledge_triples(
    text: str,
    context: str = ""
) -> List[Dict[str, Any]]:
    """
    Extract knowledge triples from text using LLM analysis.
    
    Args:
        text: Text to analyze for knowledge triples
        context: Additional context for extraction
        
    Returns:
        List of extracted knowledge triples
    """
    memory_manager = MemoryManager()
    triples = await memory_manager.extract_knowledge_triples(text, context)
    return [triple for triple in triples]


# Memory context creation for agents
async def create_memory_context(
    state: AgentState,
    query: str,
    k: int = 5,
    user_id: str = "default"
) -> str:
    """Create memory context for agent execution."""
    try:
        memory_manager = MemoryManager(user_id=user_id)
        
        # Search for relevant memories
        memories = await memory_manager.search_recall_memories(query, k)
        
        if not memories:
            return "NO RELEVANT MEMORIES FOUND."
        
        # Format memory context
        context_parts = ["RELEVANT MEMORIES:"]
        for i, memory in enumerate(memories, 1):
            context_parts.append(f"{i}. {memory['content']}")
            if memory.get('metadata', {}).get('context'):
                context_parts.append(f"   Context: {memory['metadata']['context']}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"Error creating memory context: {e}")
        return "ERROR: Could not load memories."


# Memory loading for workflow state
async def load_memories(
    state: AgentState,
    query: str = None,
    k: int = 5
) -> AgentState:
    """Load relevant memories into the workflow state."""
    try:
        # Extract context from state for memory search
        if not query:
            query = extract_context_from_state(state)
        
        # Create memory context
        memory_context = await create_memory_context(state, query, k)
        
        # Update state with memory context
        updated_state = {
            **state,
            "memory_context": memory_context,
            "memory_query": query,
            "memory_timestamp": datetime.now().isoformat()
        }
        
        return updated_state
        
    except Exception as e:
        print(f"Error loading memories: {e}")
        # Return state unchanged if memory loading fails
        return state


def extract_context_from_state(state: AgentState) -> str:
    """Extract context from state for memory search."""
    context_parts = []
    
    # Add project context
    if state.get("project_context"):
        context_parts.append(f"Project: {state['project_context']}")
    
    # Add current task
    if state.get("current_task"):
        context_parts.append(f"Current task: {state['current_task']}")
    
    # Add current agent
    if state.get("current_agent"):
        context_parts.append(f"Current agent: {state['current_agent']}")
    
    # Add recent requirements
    if state.get("requirements"):
        req_text = " ".join([str(req) for req in state["requirements"][-3:]])
        context_parts.append(f"Recent requirements: {req_text}")
    
    # Add recent architecture
    if state.get("architecture"):
        arch_text = str(state["architecture"])
        context_parts.append(f"Architecture: {arch_text[:200]}...")
    
    return " ".join(context_parts)

