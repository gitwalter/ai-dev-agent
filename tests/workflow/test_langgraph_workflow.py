"""
Tests for LangGraph Agent Swarm Workflow.
"""

import pytest
import asyncio
import os
from workflow.langgraph_workflow import AgentSwarm, LangGraphWorkflowManager


class TestAgentSwarm:
    """Test suite for AgentSwarm implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Set dummy API key for testing
        os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "test-key")
        
        self.llm_config = {
            "model_name": "gemini-2.5-flash",
            "temperature": 0.7
        }
    
    def test_agent_swarm_initialization(self):
        """Test that AgentSwarm initializes correctly."""
        swarm = AgentSwarm(self.llm_config)
        
        assert swarm is not None
        assert swarm.llm_config == self.llm_config
        assert swarm.workflow is not None
        assert swarm.agents == {}
        assert swarm.prompt_loader is not None
    
    def test_backward_compatibility_alias(self):
        """Test that LangGraphWorkflowManager is an alias for AgentSwarm."""
        assert LangGraphWorkflowManager == AgentSwarm
        
        manager = LangGraphWorkflowManager(self.llm_config)
        assert isinstance(manager, AgentSwarm)
    
    def test_workflow_has_required_nodes(self):
        """Test that workflow graph contains all required nodes."""
        swarm = AgentSwarm(self.llm_config)
        workflow = swarm.workflow
        
        # Check that workflow is compiled
        assert workflow is not None
        
        # The workflow should have the graph structure
        assert hasattr(workflow, 'get_graph')
        graph = workflow.get_graph()
        
        # Get node names
        node_names = [node.id for node in graph.nodes.values()]
        
        # Check for supervisor nodes
        expected_supervisors = [
            "complexity_analyzer",
            "agent_selector", 
            "router"
        ]
        
        for supervisor in expected_supervisors:
            assert supervisor in node_names, f"Missing supervisor node: {supervisor}"
        
        # Check for specialist agent nodes
        expected_agents = [
            "requirements_analyst",
            "code_generator",
            "documentation_generator"
        ]
        
        for agent in expected_agents:
            assert agent in node_names, f"Missing agent node: {agent}"
    
    @pytest.mark.asyncio
    async def test_create_requirements_analyst_agent(self):
        """Test requirements analyst agent creation."""
        swarm = AgentSwarm(self.llm_config)
        
        agent = await swarm._create_requirements_analyst_agent()
        
        assert agent is not None
        assert "requirements_analyst" in swarm.agents
        
        # Test agent is cached
        agent2 = await swarm._create_requirements_analyst_agent()
        assert agent == agent2
    
    @pytest.mark.asyncio
    async def test_create_code_generator_agent(self):
        """Test code generator agent creation."""
        swarm = AgentSwarm(self.llm_config)
        
        agent = await swarm._create_code_generator_agent()
        
        assert agent is not None
        assert "code_generator" in swarm.agents
    
    @pytest.mark.asyncio
    async def test_create_documentation_generator_agent(self):
        """Test documentation generator agent creation."""
        swarm = AgentSwarm(self.llm_config)
        
        agent = await swarm._create_documentation_generator_agent()
        
        assert agent is not None
        assert "documentation_generator" in swarm.agents
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "test-key",
        reason="Requires valid GEMINI_API_KEY"
    )
    async def test_execute_swarm_simple_project(self):
        """Test complete swarm execution with simple project.
        
        This test requires a valid GEMINI_API_KEY and makes real API calls.
        Skip if API key is not available.
        """
        swarm = AgentSwarm(self.llm_config)
        
        result = await swarm.execute_swarm(
            "Create a simple Python function that adds two numbers"
        )
        
        # Verify result structure
        assert "current_step" in result
        assert "completed_agents" in result
        assert "errors" in result
        assert "requirements" in result
        
        # Verify execution completed without errors
        assert result["current_step"] != "error"
        assert isinstance(result["completed_agents"], list)
        assert isinstance(result["errors"], list)
        
        # For simple projects, should complete successfully
        if result["errors"]:
            print(f"Warning: Errors occurred: {result['errors']}")


class TestPromptLoader:
    """Test suite for PromptLoader."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from workflow.langgraph_workflow import PromptLoader
        self.prompt_loader = PromptLoader(use_langsmith=False)
    
    @pytest.mark.asyncio
    async def test_load_prompt_with_fallback(self):
        """Test loading prompt with fallback template."""
        prompt = await self.prompt_loader.load_prompt(
            "test_prompt",
            fallback_template="You are a test assistant.",
            input_variables=[]
        )
        
        assert prompt is not None
        assert hasattr(prompt, 'template') or hasattr(prompt, 'format')
    
    @pytest.mark.asyncio
    async def test_prompt_caching(self):
        """Test that prompts are cached properly."""
        prompt1 = await self.prompt_loader.load_prompt(
            "test_prompt",
            fallback_template="You are a test assistant.",
            input_variables=[]
        )
        
        prompt2 = await self.prompt_loader.load_prompt(
            "test_prompt",
            fallback_template="You are a test assistant.",
            input_variables=[]
        )
        
        # Should return cached version
        assert prompt1 == prompt2


class TestSwarmState:
    """Test suite for SwarmState TypedDict."""
    
    def test_swarm_state_structure(self):
        """Test that SwarmState has correct structure."""
        from workflow.langgraph_workflow import SwarmState
        
        # Verify it's a TypedDict
        assert hasattr(SwarmState, '__annotations__')
        
        # Check required fields
        required_fields = [
            'project_context',
            'project_type',
            'project_complexity',
            'requirements',
            'architecture',
            'code_files',
            'test_files',
            'documentation',
            'required_agents',
            'completed_agents',
            'next_agent',
            'needs_human_approval',
            'human_feedback',
            'current_step',
            'errors'
        ]
        
        annotations = SwarmState.__annotations__
        
        for field in required_fields:
            assert field in annotations, f"Missing required field: {field}"


def test_graph_export_for_studio():
    """Test that graph is properly exported for LangGraph Studio."""
    from workflow.langgraph_workflow import graph, get_graph
    
    # Verify get_graph function exists
    assert get_graph is not None
    assert callable(get_graph)
    
    # Verify graph variable is set
    assert graph is not None
    
    # Verify graph has required attributes for Studio
    assert hasattr(graph, 'get_graph')


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

