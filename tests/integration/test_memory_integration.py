"""
Integration test for memory infrastructure.

Tests the complete memory system including vector store setup,
memory saving/retrieval, and knowledge triple extraction.
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from models.state import create_initial_state
from utils.memory_manager import MemoryManager


class TestMemoryIntegration:
    """Test memory system integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.memory_manager = MemoryManager(user_id="integration_test")
        self.test_memory_dir = Path("generated/memory")
        self.test_memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test state
        self.test_state = create_initial_state(
            project_context="Test project for memory integration",
            project_name="memory_integration_test",
            session_id="test_session_integration"
        )
    
    def teardown_method(self):
        """Clean up test files."""
        # Clean up test memory files
        test_files = list(self.test_memory_dir.glob("memory_integration_test_*.json"))
        for file in test_files:
            file.unlink(missing_ok=True)
        
        test_triple_files = list(self.test_memory_dir.glob("triple_integration_test_*.json"))
        for file in test_triple_files:
            file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_memory_save_and_retrieve(self):
        """Test saving and retrieving memories."""
        # Save test memory
        memory_id = await self.memory_manager.save_recall_memory(
            content="Python web development with Flask framework",
            context="Web development best practices",
            metadata={"technology": "Flask", "language": "Python"}
        )
        
        assert memory_id is not None
        
        # Search for the memory
        results = await self.memory_manager.search_recall_memories(
            query="Flask web development",
            k=5
        )
        
        assert len(results) > 0
        assert any("Flask" in result["content"] for result in results)
    
    @pytest.mark.asyncio
    async def test_knowledge_triple_storage(self):
        """Test knowledge triple storage and retrieval."""
        # Save knowledge triple
        triple_id = await self.memory_manager.save_knowledge_triple(
            subject="Flask",
            predicate="is_a",
            obj="web framework",
            context="Python web frameworks",
            confidence=0.9,
            source="test"
        )
        
        assert triple_id is not None
        
        # Search for the triple
        results = await self.memory_manager.search_recall_memories(
            query="Flask web framework",
            k=5
        )
        
        assert len(results) > 0
        assert any("Flask" in result["content"] for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_context_creation(self):
        """Test memory context creation for agents."""
        from utils.memory_manager import create_memory_context
        
        # Save some test memories
        await self.memory_manager.save_recall_memory(
            "Python web development best practices",
            "Web development context"
        )
        await self.memory_manager.save_recall_memory(
            "Flask framework features and usage",
            "Framework context"
        )
        
        # Create memory context
        context = await create_memory_context(
            self.test_state,
            "web development Flask",
            k=3
        )
        
        assert "RELEVANT MEMORIES:" in context
        assert "Python web development" in context or "Flask" in context
    
    @pytest.mark.asyncio
    async def test_memory_stats(self):
        """Test memory statistics."""
        # Save some test data
        await self.memory_manager.save_recall_memory("Test memory 1", "Context 1")
        await self.memory_manager.save_recall_memory("Test memory 2", "Context 2")
        await self.memory_manager.save_knowledge_triple(
            "Test", "is_a", "example", "Test context", 0.8, "test"
        )
        
        # Get stats
        stats = self.memory_manager.get_memory_stats()
        
        assert stats["user_id"] == "integration_test"
        assert stats["memory_files_count"] >= 2
        assert stats["triple_files_count"] >= 1
        assert "vector_store_available" in stats
        assert "embeddings_available" in stats
    
    @pytest.mark.asyncio
    async def test_memory_fallback_functionality(self):
        """Test memory fallback when vector store is unavailable."""
        # Force fallback by setting vector store to None
        self.memory_manager.vector_store = None
        
        # Save memory using fallback
        memory_id = await self.memory_manager.save_recall_memory(
            "Fallback test memory",
            "Fallback context"
        )
        
        assert memory_id is not None
        
        # Search using fallback
        results = await self.memory_manager.search_recall_memories(
            "fallback test",
            k=3
        )
        
        assert len(results) > 0
        assert any("Fallback test memory" in result["content"] for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_tools(self):
        """Test memory tools functionality."""
        from utils.memory_manager import save_recall_memory, search_recall_memories
        
        # Test save tool
        memory_id = await save_recall_memory(
            content="Tool test memory",
            context="Tool test context",
            metadata={"test": "tool"}
        )
        
        assert memory_id is not None
        
        # Test search tool
        results = await search_recall_memories(
            query="tool test",
            k=3
        )
        
        assert len(results) > 0
        assert any("Tool test memory" in result["content"] for result in results)


class TestMemoryEnhancedState:
    """Test memory-enhanced state management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.initial_state = create_initial_state(
            project_context="Test project for memory-enhanced state",
            project_name="memory_state_test",
            session_id="test_session_state"
        )
    
    def test_memory_fields_in_state(self):
        """Test that state includes memory fields."""
        assert "memory_context" in self.initial_state
        assert "memory_query" in self.initial_state
        assert "memory_timestamp" in self.initial_state
        assert "recall_memories" in self.initial_state
        assert "knowledge_triples" in self.initial_state
        assert "memory_stats" in self.initial_state
        
        # Verify initial values
        assert self.initial_state["memory_context"] == ""
        assert self.initial_state["recall_memories"] == []
        assert self.initial_state["knowledge_triples"] == []
    
    @pytest.mark.asyncio
    async def test_memory_state_integration(self):
        """Test memory integration with state."""
        from models.state import add_memory_to_state, add_knowledge_triple_to_state
        from utils.memory_manager import load_memories
        
        # Add memory to state
        state_with_memory = add_memory_to_state(
            self.initial_state,
            memory_content="State integration test memory",
            memory_context="State test context",
            metadata={"test": "state_integration"},
            relevance_score=0.9
        )
        
        assert len(state_with_memory["recall_memories"]) == 1
        assert state_with_memory["recall_memories"][0]["content"] == "State integration test memory"
        
        # Add knowledge triple to state
        state_with_triple = add_knowledge_triple_to_state(
            state_with_memory,
            subject="State",
            predicate="supports",
            obj="memory integration",
            context="State management",
            confidence=0.8,
            source="test"
        )
        
        assert len(state_with_triple["knowledge_triples"]) == 1
        assert state_with_triple["knowledge_triples"][0]["subject"] == "State"
        
        # Test memory loading
        loaded_state = await load_memories(state_with_triple, "state integration", k=3)
        
        assert "memory_context" in loaded_state
        assert "memory_timestamp" in loaded_state


if __name__ == "__main__":
    pytest.main([__file__])
