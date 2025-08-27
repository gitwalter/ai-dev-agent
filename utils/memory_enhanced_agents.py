"""
Memory-Enhanced Agent System

This module provides memory-enhanced agent functions that integrate
long-term memory capabilities with agent execution.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from models.state import AgentState
from utils.memory_manager import MemoryManager, create_memory_context, load_memories
from utils.helpers import get_llm_model


async def memory_enhanced_agent(
    agent_function,
    state: AgentState,
    agent_name: str,
    memory_query: str = None,
    memory_k: int = 5,
    extract_triples: bool = True
) -> AgentState:
    """
    Execute an agent with memory enhancement.
    
    Args:
        agent_function: The agent function to execute
        state: Current workflow state
        agent_name: Name of the agent for context
        memory_query: Custom query for memory search
        memory_k: Number of memories to retrieve
        extract_triples: Whether to extract knowledge triples from output
        
    Returns:
        Updated state with agent output and memory integration
    """
    try:
        # Step 1: Load relevant memories
        print(f"🔄 Loading memories for {agent_name}...")
        state_with_memory = await load_memories(state, memory_query, memory_k)
        
        # Step 2: Create memory context for agent
        if not memory_query:
            memory_query = f"{agent_name} {state.get('current_task', '')} {state.get('project_context', '')}"
        
        memory_context = await create_memory_context(state, memory_query, memory_k)
        
        # Step 3: Execute agent with memory context
        print(f"🤖 Executing {agent_name} with memory context...")
        
        # Add memory context to state for agent access
        enhanced_state = {
            **state_with_memory,
            "memory_context": memory_context,
            "current_agent": agent_name,
            "memory_query": memory_query
        }
        
        # Execute the agent
        result_state = await agent_function(enhanced_state)
        
        # Step 4: Extract and save knowledge triples from agent output
        if extract_triples:
            print(f"🧠 Extracting knowledge triples from {agent_name} output...")
            result_state = await extract_and_save_triples(result_state, agent_name)
        
        # Step 5: Save agent output as memory
        print(f"💾 Saving {agent_name} output to memory...")
        result_state = await save_agent_output_as_memory(result_state, agent_name)
        
        return result_state
        
    except Exception as e:
        print(f"❌ Error in memory-enhanced agent execution: {e}")
        # Return state with error information
        error_state = {
            **state,
            "errors": state.get("errors", []) + [{
                "error_type": "memory_enhanced_agent_error",
                "error_message": str(e),
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat()
            }]
        }
        return error_state


async def extract_and_save_triples(
    state: AgentState,
    agent_name: str
) -> AgentState:
    """Extract knowledge triples from agent output and save to memory."""
    try:
        memory_manager = MemoryManager()
        
        # Get agent output
        agent_outputs = state.get("agent_outputs", {})
        agent_output = agent_outputs.get(agent_name, {})
        
        if not agent_output:
            return state
        
        # Convert output to text for triple extraction
        output_text = str(agent_output)
        
        # Extract knowledge triples
        triples = await memory_manager.extract_knowledge_triples(
            text=output_text,
            context=f"Agent: {agent_name}, Task: {state.get('current_task', '')}"
        )
        
        # Save triples to memory and state
        for triple in triples:
            # Save to memory system
            await memory_manager.save_knowledge_triple(
                subject=triple["subject"],
                predicate=triple["predicate"],
                obj=triple["object"],
                context=triple["context"],
                confidence=triple["confidence"],
                source=f"{agent_name}_extraction"
            )
            
            # Add to state
            from models.state import add_knowledge_triple_to_state
            state = add_knowledge_triple_to_state(
                state,
                subject=triple["subject"],
                predicate=triple["predicate"],
                obj=triple["object"],
                context=triple["context"],
                confidence=triple["confidence"],
                source=f"{agent_name}_extraction"
            )
        
        print(f"✅ Extracted {len(triples)} knowledge triples from {agent_name}")
        return state
        
    except Exception as e:
        print(f"❌ Error extracting triples: {e}")
        return state


async def save_agent_output_as_memory(
    state: AgentState,
    agent_name: str
) -> AgentState:
    """Save agent output as memory for future reference."""
    try:
        memory_manager = MemoryManager()
        
        # Get agent output
        agent_outputs = state.get("agent_outputs", {})
        agent_output = agent_outputs.get(agent_name, {})
        
        if not agent_output:
            return state
        
        # Create memory content
        memory_content = f"Agent {agent_name} output: {str(agent_output)}"
        memory_context = f"Task: {state.get('current_task', '')}, Project: {state.get('project_context', '')}"
        
        # Save to memory system
        memory_id = await memory_manager.save_recall_memory(
            content=memory_content,
            context=memory_context,
            metadata={
                "agent_name": agent_name,
                "task": state.get("current_task", ""),
                "project": state.get("project_name", ""),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Add to state
        from models.state import add_memory_to_state
        state = add_memory_to_state(
            state,
            memory_content=memory_content,
            memory_context=memory_context,
            metadata={
                "agent_name": agent_name,
                "task": state.get("current_task", ""),
                "project": state.get("project_name", ""),
                "memory_id": memory_id
            },
            relevance_score=1.0
        )
        
        print(f"✅ Saved {agent_name} output as memory (ID: {memory_id})")
        return state
        
    except Exception as e:
        print(f"❌ Error saving agent output as memory: {e}")
        return state


async def create_memory_enhanced_workflow_node(
    agent_function,
    agent_name: str,
    memory_query_template: str = None,
    memory_k: int = 5,
    extract_triples: bool = True
):
    """
    Create a memory-enhanced workflow node for LangGraph.
    
    Args:
        agent_function: The agent function to wrap
        agent_name: Name of the agent
        memory_query_template: Template for memory query
        memory_k: Number of memories to retrieve
        extract_triples: Whether to extract knowledge triples
        
    Returns:
        Memory-enhanced agent function for LangGraph
    """
    
    async def memory_enhanced_node(state: AgentState) -> AgentState:
        """Memory-enhanced node function for LangGraph."""
        
        # Create memory query from template or state
        if memory_query_template:
            memory_query = memory_query_template.format(
                agent_name=agent_name,
                current_task=state.get("current_task", ""),
                project_context=state.get("project_context", "")
            )
        else:
            memory_query = f"{agent_name} {state.get('current_task', '')} {state.get('project_context', '')}"
        
        # Execute memory-enhanced agent
        return await memory_enhanced_agent(
            agent_function=agent_function,
            state=state,
            agent_name=agent_name,
            memory_query=memory_query,
            memory_k=memory_k,
            extract_triples=extract_triples
        )
    
    return memory_enhanced_node


async def memory_enhanced_requirements_analyst(state: AgentState) -> AgentState:
    """Memory-enhanced requirements analyst."""
    from agents.requirements_analyst import RequirementsAnalyst
    
    async def requirements_function(state: AgentState) -> AgentState:
        agent = RequirementsAnalyst()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=requirements_function,
        state=state,
        agent_name="requirements_analyst",
        memory_query=f"requirements analysis {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


async def memory_enhanced_architecture_designer(state: AgentState) -> AgentState:
    """Memory-enhanced architecture designer."""
    from agents.architecture_designer import ArchitectureDesigner
    
    async def architecture_function(state: AgentState) -> AgentState:
        agent = ArchitectureDesigner()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=architecture_function,
        state=state,
        agent_name="architecture_designer",
        memory_query=f"architecture design {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


async def memory_enhanced_code_generator(state: AgentState) -> AgentState:
    """Memory-enhanced code generator."""
    from agents.code_generator import CodeGenerator
    
    async def code_function(state: AgentState) -> AgentState:
        agent = CodeGenerator()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=code_function,
        state=state,
        agent_name="code_generator",
        memory_query=f"code generation {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


async def memory_enhanced_test_generator(state: AgentState) -> AgentState:
    """Memory-enhanced test generator."""
    from agents.test_generator import TestGenerator
    
    async def test_function(state: AgentState) -> AgentState:
        agent = TestGenerator()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=test_function,
        state=state,
        agent_name="test_generator",
        memory_query=f"test generation {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


async def memory_enhanced_code_reviewer(state: AgentState) -> AgentState:
    """Memory-enhanced code reviewer."""
    from agents.code_reviewer import CodeReviewer
    
    async def review_function(state: AgentState) -> AgentState:
        agent = CodeReviewer()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=review_function,
        state=state,
        agent_name="code_reviewer",
        memory_query=f"code review {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


async def memory_enhanced_security_analyst(state: AgentState) -> AgentState:
    """Memory-enhanced security analyst."""
    from agents.security_analyst import SecurityAnalyst
    
    async def security_function(state: AgentState) -> AgentState:
        agent = SecurityAnalyst()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=security_function,
        state=state,
        agent_name="security_analyst",
        memory_query=f"security analysis {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


async def memory_enhanced_documentation_generator(state: AgentState) -> AgentState:
    """Memory-enhanced documentation generator."""
    from agents.documentation_generator import DocumentationGenerator
    
    async def doc_function(state: AgentState) -> AgentState:
        agent = DocumentationGenerator()
        return await agent.execute(state)
    
    return await memory_enhanced_agent(
        agent_function=doc_function,
        state=state,
        agent_name="documentation_generator",
        memory_query=f"documentation generation {state.get('project_context', '')}",
        memory_k=5,
        extract_triples=True
    )


# Memory loading node for workflow
async def load_memories_node(state: AgentState) -> AgentState:
    """Node for loading memories into workflow state."""
    try:
        print("🔄 Loading memories into workflow state...")
        
        # Extract context from state
        context_query = f"{state.get('current_task', '')} {state.get('project_context', '')}"
        
        # Load memories
        updated_state = await load_memories(state, context_query, k=5)
        
        # Update memory stats
        memory_manager = MemoryManager()
        stats = memory_manager.get_memory_stats()
        from models.state import update_memory_stats
        updated_state = update_memory_stats(updated_state, stats)
        
        print(f"✅ Loaded memories. Stats: {stats}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error loading memories: {e}")
        return state


# Memory analysis node for workflow
async def analyze_memory_patterns_node(state: AgentState) -> AgentState:
    """Node for analyzing memory patterns and insights."""
    try:
        print("🧠 Analyzing memory patterns...")
        
        memory_manager = MemoryManager()
        
        # Get memory statistics
        stats = memory_manager.get_memory_stats()
        
        # Analyze patterns (basic analysis for now)
        analysis = {
            "total_memories": stats.get("memory_files_count", 0),
            "total_triples": stats.get("triple_files_count", 0),
            "vector_store_available": stats.get("vector_store_available", False),
            "analysis_timestamp": datetime.now().isoformat(),
            "insights": []
        }
        
        # Add basic insights
        if stats.get("memory_files_count", 0) > 0:
            analysis["insights"].append("Memory system is actively storing information")
        
        if stats.get("triple_files_count", 0) > 0:
            analysis["insights"].append("Knowledge triples are being extracted and stored")
        
        if not stats.get("vector_store_available", False):
            analysis["insights"].append("Using fallback memory storage (vector store unavailable)")
        
        # Update state with analysis
        updated_state = {
            **state,
            "memory_analysis": analysis,
            "memory_stats": stats
        }
        
        print(f"✅ Memory analysis complete. Insights: {len(analysis['insights'])}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error analyzing memory patterns: {e}")
        return state
