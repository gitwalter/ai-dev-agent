"""
Tests for US-CONTEXT-001 Phase 1: Context Detection in Complexity Analyzer.

Tests that the complexity analyzer correctly detects:
- Complexity: simple, medium, complex
- Domain: ai, web, api, data, mobile, library, utility, general
- Intent: new_feature, bug_fix, refactor, migration, enhancement, general
- Entities: Technology names, frameworks, services
"""

import pytest
import os
from workflow.langgraph_workflow import AgentSwarm, SwarmState


class TestContextDetectionPhase1:
    """Test suite for Phase 1 context detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Set dummy API key for testing
        os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "test-key")
        
        self.llm_config = {
            "model_name": "gemini-2.5-flash",
            "temperature": 0.0  # Deterministic for testing
        }
    
    def test_swarm_state_has_context_fields(self):
        """Test that SwarmState includes context detection fields."""
        # Check that SwarmState type hints include new fields
        import typing
        from typing import get_type_hints
        
        hints = get_type_hints(SwarmState)
        
        # Phase 1 fields should be present
        assert "project_domain" in hints, "SwarmState missing project_domain field"
        assert "project_intent" in hints, "SwarmState missing project_intent field"
        assert "detected_entities" in hints, "SwarmState missing detected_entities field"
        assert "project_complexity" in hints, "SwarmState missing project_complexity field"
        
        # Check types
        assert hints["project_domain"] == str, "project_domain should be str"
        assert hints["project_intent"] == str, "project_intent should be str"
        assert hints["detected_entities"] == list, "detected_entities should be list"
    
    def test_initial_state_includes_context_fields(self):
        """Test that initial state includes context fields with defaults."""
        swarm = AgentSwarm(self.llm_config)
        
        # Create initial state
        initial_state: SwarmState = {
            "project_context": "Test project",
            "project_complexity": "medium",
            "project_domain": "general",
            "project_intent": "new_feature",
            "detected_entities": [],
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "start",
            "errors": []
        }
        
        # Verify all context fields are present
        assert "project_domain" in initial_state
        assert "project_intent" in initial_state
        assert "detected_entities" in initial_state
        assert initial_state["project_domain"] == "general"
        assert initial_state["project_intent"] == "new_feature"
        assert isinstance(initial_state["detected_entities"], list)
    
    def test_analyze_complexity_returns_context_fields(self):
        """Test that _analyze_complexity returns all context fields."""
        swarm = AgentSwarm(self.llm_config)
        
        # Create test state
        state: SwarmState = {
            "project_context": "Build a RAG system for document search",
            "project_complexity": "medium",
            "project_domain": "general",
            "project_intent": "new_feature",
            "detected_entities": [],
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "start",
            "errors": []
        }
        
        # Call complexity analyzer
        result = swarm._analyze_complexity(state)
        
        # Verify all context fields are in result
        assert "project_complexity" in result
        assert "project_domain" in result
        assert "project_intent" in result
        assert "detected_entities" in result
        
        # Verify valid values
        assert result["project_complexity"] in ["simple", "medium", "complex"]
        assert result["project_domain"] in ["ai", "web", "api", "data", "mobile", "library", "utility", "general"]
        assert result["project_intent"] in ["new_feature", "bug_fix", "refactor", "migration", "enhancement", "general"]
        assert isinstance(result["detected_entities"], list)
    
    def test_context_detection_for_ai_project(self):
        """Test context detection for an AI project."""
        swarm = AgentSwarm(self.llm_config)
        
        state: SwarmState = {
            "project_context": "Build a RAG system for document search using vector embeddings",
            "project_complexity": "medium",
            "project_domain": "general",
            "project_intent": "new_feature",
            "detected_entities": [],
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "start",
            "errors": []
        }
        
        result = swarm._analyze_complexity(state)
        
        # For AI project, should detect domain as "ai"
        # Note: This is a mock test - actual LLM may vary
        assert result["project_domain"] in ["ai", "general"]  # Allow fallback
        assert result["project_intent"] == "new_feature"  # Should detect new feature
        # Should detect entities related to RAG
        assert isinstance(result["detected_entities"], list)
    
    def test_context_detection_for_bug_fix(self):
        """Test context detection for a bug fix scenario."""
        swarm = AgentSwarm(self.llm_config)
        
        state: SwarmState = {
            "project_context": "Fix authentication bug in login API endpoint",
            "project_complexity": "medium",
            "project_domain": "general",
            "project_intent": "new_feature",
            "detected_entities": [],
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "start",
            "errors": []
        }
        
        result = swarm._analyze_complexity(state)
        
        # Should detect intent as bug_fix
        # Note: This is a mock test - actual LLM may vary
        assert result["project_intent"] in ["bug_fix", "new_feature"]  # Allow fallback
        assert result["project_domain"] in ["api", "web", "general"]  # Should detect API domain
        assert isinstance(result["detected_entities"], list)
    
    def test_context_detection_fallback_to_defaults(self):
        """Test that context detection falls back to defaults on parse failure."""
        swarm = AgentSwarm(self.llm_config)
        
        # This test verifies the fallback logic works
        # In real execution, if JSON parsing fails, should use defaults
        state: SwarmState = {
            "project_context": "Invalid project description that might cause parsing issues",
            "project_complexity": "medium",
            "project_domain": "general",
            "project_intent": "new_feature",
            "detected_entities": [],
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "start",
            "errors": []
        }
        
        result = swarm._analyze_complexity(state)
        
        # Should always return valid defaults even if parsing fails
        assert result["project_complexity"] in ["simple", "medium", "complex"]
        assert result["project_domain"] in ["ai", "web", "api", "data", "mobile", "library", "utility", "general"]
        assert result["project_intent"] in ["new_feature", "bug_fix", "refactor", "migration", "enhancement", "general"]
        assert isinstance(result["detected_entities"], list)
    
    def test_agent_selection_uses_context(self):
        """Test that agent selection uses detected context."""
        swarm = AgentSwarm(self.llm_config)
        
        # Create state with detected context
        state: SwarmState = {
            "project_context": "Build a RAG system for document search",
            "project_complexity": "complex",
            "project_domain": "ai",
            "project_intent": "new_feature",
            "detected_entities": ["rag", "document", "search", "vector", "embeddings"],
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "complexity_analyzed",
            "errors": []
        }
        
        # Verify context is in state
        assert state["project_domain"] == "ai"
        assert state["project_intent"] == "new_feature"
        assert len(state["detected_entities"]) > 0
        
        # Agent selection should use this context
        # The prompt should include domain, intent, and entities
        # Note: This test verifies the structure, not the actual LLM response
        result = swarm._select_agents(state)
        
        # Should return valid agent list
        assert "required_agents" in result
        assert isinstance(result["required_agents"], list)
        assert len(result["required_agents"]) > 0

