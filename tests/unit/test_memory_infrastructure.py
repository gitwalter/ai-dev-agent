"""
Unit tests for memory infrastructure implementation.

Tests the memory management system, enhanced state management,
and memory-enhanced agent functionality.
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from models.state import AgentState, create_initial_state
from utils.memory_manager import MemoryManager, KnowledgeTriple
from utils.memory_enhanced_agents import memory_enhanced_agent, load_memories_node


class TestMemoryManager:
    """Test the MemoryManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.memory_manager = MemoryManager(user_id="test_user")
        self.test_memory_dir = Path("generated/memory")
        self.test_memory_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test files."""
        # Clean up test memory files
        test_files = list(self.test_memory_dir.glob("memory_test_user_*.json"))
        for file in test_files:
            file.unlink(missing_ok=True)
        
        test_triple_files = list(self.test_memory_dir.glob("triple_test_user_*.json"))
        for file in test_triple_files:
            file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_memory_manager_initialization(self):
        """Test MemoryManager initialization."""
        assert self.memory_manager.user_id == "test_user"
        assert self.memory_manager.memory_dir.exists()
    
    @pytest.mark.asyncio
    async def test_save_recall_memory_fallback(self):
        """Test saving memory with fallback storage."""
        content = "Test memory content"
        context = "Test context"
        metadata = {"test": "data"}
        
        memory_id = await self.memory_manager.save_recall_memory(
            content, context, metadata
        )
        
        assert memory_id is not None
        assert len(memory_id) > 0
        
        # Check that memory file was created
        memory_files = list(self.test_memory_dir.glob("memory_test_user_*.json"))
        assert len(memory_files) == 1
        
        # Verify memory content
        with open(memory_files[0], 'r') as f:
            memory_data = json.load(f)
        
        assert memory_data["content"] == content
        assert memory_data["context"] == context
        assert memory_data["metadata"] == metadata
        assert memory_data["user_id"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_search_recall_memories_fallback(self):
        """Test searching memories with fallback storage."""
        # Save some test memories
        await self.memory_manager.save_recall_memory(
            "Python web application development",
            "Web development context"
        )
        await self.memory_manager.save_recall_memory(
            "Database design and optimization",
            "Database context"
        )
        await self.memory_manager.save_recall_memory(
            "API integration and testing",
            "API context"
        )
        
        # Search for relevant memories
        results = await self.memory_manager.search_recall_memories("web development", k=2)
        
        assert len(results) > 0
        assert any("Python web application" in result["content"] for result in results)
    
    @pytest.mark.asyncio
    async def test_save_knowledge_triple(self):
        """Test saving knowledge triples."""
        triple_id = await self.memory_manager.save_knowledge_triple(
            subject="Python",
            predicate="is_a",
            obj="programming language",
            context="Programming languages",
            confidence=0.9,
            source="test"
        )
        
        assert triple_id is not None
        
        # Check that triple file was created
        triple_files = list(self.test_memory_dir.glob("triple_test_user_*.json"))
        assert len(triple_files) == 1
        
        # Verify triple content
        with open(triple_files[0], 'r') as f:
            triple_data = json.load(f)
        
        assert triple_data["subject"] == "Python"
        assert triple_data["predicate"] == "is_a"
        assert triple_data["object"] == "programming language"
        assert triple_data["confidence"] == 0.9
        assert triple_data["source"] == "test"
    
    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        stats = self.memory_manager.get_memory_stats()
        
        assert "user_id" in stats
        assert "vector_store_available" in stats
        assert "embeddings_available" in stats
        assert "memory_files_count" in stats
        assert "triple_files_count" in stats
        assert stats["user_id"] == "test_user"


class TestEnhancedStateManagement:
    """Test enhanced state management with memory fields."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.initial_state = create_initial_state(
            project_context="Test project for memory system",
            project_name="memory_test_project",
            session_id="test_session_123"
        )
    
    def test_initial_state_memory_fields(self):
        """Test that initial state includes memory fields."""
        assert "memory_context" in self.initial_state
        assert "memory_query" in self.initial_state
        assert "memory_timestamp" in self.initial_state
        assert "recall_memories" in self.initial_state
        assert "knowledge_triples" in self.initial_state
        assert "memory_stats" in self.initial_state
        
        # Check handoff fields
        assert "handoff_queue" in self.initial_state
        assert "handoff_history" in self.initial_state
        assert "agent_availability" in self.initial_state
        assert "collaboration_context" in self.initial_state
        
        # Verify initial values
        assert self.initial_state["memory_context"] == ""
        assert self.initial_state["recall_memories"] == []
        assert self.initial_state["knowledge_triples"] == []
        assert len(self.initial_state["agent_availability"]) == 7  # All 7 agents
    
    def test_add_memory_to_state(self):
        """Test adding memory to state."""
        from models.state import add_memory_to_state
        
        updated_state = add_memory_to_state(
            self.initial_state,
            memory_content="Test memory content",
            memory_context="Test context",
            metadata={"test": "data"},
            relevance_score=0.8
        )
        
        assert len(updated_state["recall_memories"]) == 1
        memory = updated_state["recall_memories"][0]
        assert memory["content"] == "Test memory content"
        assert memory["context"] == "Test context"
        assert memory["metadata"]["test"] == "data"
        assert memory["relevance_score"] == 0.8
    
    def test_add_knowledge_triple_to_state(self):
        """Test adding knowledge triple to state."""
        from models.state import add_knowledge_triple_to_state
        
        updated_state = add_knowledge_triple_to_state(
            self.initial_state,
            subject="Python",
            predicate="is_a",
            obj="programming language",
            context="Programming",
            confidence=0.9,
            source="test"
        )
        
        assert len(updated_state["knowledge_triples"]) == 1
        triple = updated_state["knowledge_triples"][0]
        assert triple["subject"] == "Python"
        assert triple["predicate"] == "is_a"
        assert triple["object"] == "programming language"
        assert triple["confidence"] == 0.9
        assert triple["source"] == "test"
    
    def test_add_handoff_request(self):
        """Test adding handoff request to state."""
        from models.state import add_handoff_request
        
        updated_state = add_handoff_request(
            self.initial_state,
            from_agent="requirements_analyst",
            to_agent="architecture_designer",
            task_description="Design system architecture",
            data_to_transfer={"requirements": "test requirements"},
            priority="high"
        )
        
        assert len(updated_state["handoff_queue"]) == 1
        handoff = updated_state["handoff_queue"][0]
        assert handoff["from_agent"] == "requirements_analyst"
        assert handoff["to_agent"] == "architecture_designer"
        assert handoff["task_description"] == "Design system architecture"
        assert handoff["priority"] == "high"
        assert handoff["status"] == "pending"


class TestMemoryEnhancedAgents:
    """Test memory-enhanced agent functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.initial_state = create_initial_state(
            project_context="Test project for memory-enhanced agents",
            project_name="memory_agent_test",
            session_id="test_session_456"
        )
    
    @pytest.mark.asyncio
    async def test_memory_enhanced_agent_execution(self):
        """Test memory-enhanced agent execution."""
        # Mock agent function
        async def mock_agent_function(state: AgentState) -> AgentState:
            return {
                **state,
                "agent_outputs": {
                    "test_agent": {
                        "result": "Test agent output",
                        "status": "success"
                    }
                },
                "current_task": "test_task"
            }
        
        # Execute memory-enhanced agent
        result_state = await memory_enhanced_agent(
            agent_function=mock_agent_function,
            state=self.initial_state,
            agent_name="test_agent",
            memory_query="test agent execution",
            memory_k=3,
            extract_triples=False  # Disable for this test
        )
        
        # Verify agent execution
        assert "agent_outputs" in result_state
        assert "test_agent" in result_state["agent_outputs"]
        assert result_state["agent_outputs"]["test_agent"]["result"] == "Test agent output"
        
        # Verify memory context was added
        assert "memory_context" in result_state
        assert "memory_query" in result_state
    
    @pytest.mark.asyncio
    async def test_load_memories_node(self):
        """Test memory loading node."""
        # Add some test memories first
        memory_manager = MemoryManager(user_id="test_user")
        await memory_manager.save_recall_memory(
            "Test memory for workflow",
            "Workflow context"
        )
        
        # Execute memory loading node
        result_state = await load_memories_node(self.initial_state)
        
        # Verify memory loading
        assert "memory_context" in result_state
        assert "memory_stats" in result_state
        assert "memory_timestamp" in result_state


class TestMemoryIntegration:
    """Test memory system integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.initial_state = create_initial_state(
            project_context="Integration test project",
            project_name="integration_test",
            session_id="test_session_789"
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_memory_workflow(self):
        """Test end-to-end memory workflow."""
        memory_manager = MemoryManager(user_id="test_user")
        
        # Step 1: Save initial memories
        await memory_manager.save_recall_memory(
            "Python web development best practices",
            "Web development context"
        )
        await memory_manager.save_knowledge_triple(
            "Flask", "is_a", "web framework",
            "Python web frameworks", 0.9, "test"
        )
        
        # Step 2: Create memory-enhanced state
        from models.state import add_memory_to_state, add_knowledge_triple_to_state
        
        enhanced_state = add_memory_to_state(
            self.initial_state,
            "Previous project used Flask framework",
            "Project history context"
        )
        
        enhanced_state = add_knowledge_triple_to_state(
            enhanced_state,
            "Flask", "provides", "web routing",
            "Framework features", 0.8, "test"
        )
        
        # Step 3: Test memory search
        memories = await memory_manager.search_recall_memories("web development", k=3)
        assert len(memories) > 0
        
        # Step 4: Test memory context creation
        from utils.memory_manager import create_memory_context
        context = await create_memory_context(enhanced_state, "web development", k=3, user_id="test_user")
        assert "RELEVANT MEMORIES:" in context
        
        # Set the memory context in the enhanced state
        enhanced_state["memory_context"] = context
        
        # Step 5: Verify state integrity
        assert len(enhanced_state["recall_memories"]) > 0
        assert len(enhanced_state["knowledge_triples"]) > 0
        assert enhanced_state["memory_context"] == context


if __name__ == "__main__":
    pytest.main([__file__])
