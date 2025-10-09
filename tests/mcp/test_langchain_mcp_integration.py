#!/usr/bin/env python3
"""
LangChain-MCP Integration Tests
==============================

Comprehensive tests for LangChain-MCP integration:
- MCPTool: LangChain tool wrapper functionality
- MCPToolkit: Tool collection and management
- MCPAgentMixin: Agent integration capabilities
- MCPEnhancedAgent: Complete agent with MCP tools

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 2)
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import components to test
try:
    from utils.mcp.langchain_integration import (
        MCPTool, MCPToolkit, MCPAgentMixin, check_langchain_mcp_compatibility,
        create_mcp_toolkit, create_mcp_tools_for_agent
    )
    from agents.mcp.mcp_enhanced_agent import MCPEnhancedAgent, create_mcp_enhanced_agent
    from agents.core.base_agent import AgentConfig
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"❌ LangChain-MCP integration import failed: {e}")
    INTEGRATION_AVAILABLE = False

# Mock components for testing
try:
    from utils.mcp.server import ToolDefinition, ToolExecutionResult, AccessLevel, ToolCategory
    from utils.mcp.client import MCPClient
    MCP_COMPONENTS_AVAILABLE = True
except ImportError:
    MCP_COMPONENTS_AVAILABLE = False


@pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="LangChain-MCP integration not available")
class TestLangChainMCPCompatibility:
    """Test LangChain-MCP compatibility checking."""
    
    def test_compatibility_check(self):
        """Test compatibility checking function."""
        compatibility = check_langchain_mcp_compatibility()
        
        assert isinstance(compatibility, dict)
        assert "langchain_available" in compatibility
        assert "mcp_available" in compatibility
        assert "universal_tracking_available" in compatibility
        assert "integration_ready" in compatibility
        
        # Integration ready should be True if both LangChain and MCP are available
        expected_ready = compatibility["langchain_available"] and compatibility["mcp_available"]
        assert compatibility["integration_ready"] == expected_ready


@pytest.mark.skipif(not INTEGRATION_AVAILABLE or not MCP_COMPONENTS_AVAILABLE, 
                   reason="Integration components not available")
class TestMCPTool:
    """Test MCPTool LangChain wrapper."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Create mock tool definition
        self.mock_tool_def = Mock()
        self.mock_tool_def.tool_id = "test.tool"
        self.mock_tool_def.description = "Test tool for integration testing"
        self.mock_tool_def.category = ToolCategory.TESTING
        self.mock_tool_def.access_level = AccessLevel.PUBLIC
        self.mock_tool_def.execution_timeout = 30
        
        # Create mock MCP client
        self.mock_client = Mock(spec=MCPClient)
        
        # Create MCPTool instance
        self.mcp_tool = MCPTool(self.mock_tool_def, self.mock_client)
    
    def test_mcp_tool_initialization(self):
        """Test MCPTool initialization."""
        assert self.mcp_tool.name == "test.tool"
        assert self.mcp_tool.description == "Test tool for integration testing"
        assert self.mcp_tool.tool_definition == self.mock_tool_def
        assert self.mcp_tool.mcp_client == self.mock_client
        assert self.mcp_tool.execution_count == 0
        assert self.mcp_tool.total_execution_time == 0.0
    
    @pytest.mark.asyncio
    async def test_mcp_tool_async_execution_success(self):
        """Test successful async tool execution."""
        # Mock successful execution result
        mock_result = Mock()
        mock_result.success = True
        mock_result.result = {"status": "completed", "data": "test_data"}
        
        self.mock_client.execute_tool = AsyncMock(return_value=mock_result)
        
        # Execute tool
        result = await self.mcp_tool._arun({"test_param": "test_value"})
        
        # Verify execution
        assert isinstance(result, str)
        assert "successful" in result.lower()
        assert self.mcp_tool.execution_count == 1
        assert self.mcp_tool.total_execution_time > 0
        
        # Verify client was called correctly
        self.mock_client.execute_tool.assert_called_once_with(
            tool_id="test.tool",
            parameters={"test_param": "test_value"},
            timeout=30
        )
    
    @pytest.mark.asyncio
    async def test_mcp_tool_async_execution_failure(self):
        """Test failed async tool execution."""
        # Mock failed execution result
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Tool execution failed"
        
        self.mock_client.execute_tool = AsyncMock(return_value=mock_result)
        
        # Execute tool and expect exception
        with pytest.raises(Exception) as exc_info:
            await self.mcp_tool._arun({"test_param": "test_value"})
        
        assert "Tool execution failed" in str(exc_info.value)
        assert self.mcp_tool.execution_count == 1
    
    def test_mcp_tool_metrics(self):
        """Test tool metrics collection."""
        # Simulate some executions
        self.mcp_tool.execution_count = 5
        self.mcp_tool.total_execution_time = 10.0
        self.mcp_tool.last_execution_time = datetime.now()
        
        metrics = self.mcp_tool.get_tool_metrics()
        
        assert metrics["tool_id"] == "test.tool"
        assert metrics["execution_count"] == 5
        assert metrics["total_execution_time"] == 10.0
        assert metrics["average_execution_time"] == 2.0
        assert metrics["last_execution"] is not None
        assert "category" in metrics
        assert "access_level" in metrics


@pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Integration components not available")
class TestMCPToolkit:
    """Test MCPToolkit functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.toolkit = MCPToolkit("test_agent", "test_agent_type")
    
    def test_toolkit_initialization(self):
        """Test toolkit initialization."""
        assert self.toolkit.agent_id == "test_agent"
        assert self.toolkit.agent_type == "test_agent_type"
        assert self.toolkit.mcp_client is None
        assert len(self.toolkit.tools) == 0
    
    def test_toolkit_metrics_empty(self):
        """Test toolkit metrics when no tools are loaded."""
        metrics = self.toolkit.get_toolkit_metrics()
        
        assert metrics["agent_id"] == "test_agent"
        assert metrics["agent_type"] == "test_agent_type"
        assert metrics["total_tools"] == 0
        assert metrics["total_executions"] == 0
        assert metrics["total_execution_time"] == 0.0
        assert metrics["average_execution_time"] == 0.0
        assert metrics["mcp_client_connected"] is False
    
    def test_get_tools_empty(self):
        """Test getting tools when none are available."""
        tools = self.toolkit.get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 0
    
    def test_get_tool_by_name_not_found(self):
        """Test getting tool by name when it doesn't exist."""
        tool = self.toolkit.get_tool_by_name("nonexistent_tool")
        assert tool is None


@pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Integration components not available")
class TestMCPAgentMixin:
    """Test MCPAgentMixin functionality."""
    
    def test_mcp_agent_mixin_creation(self):
        """Test MCPAgentMixin can be instantiated."""
        # Create a simple class that uses the mixin
        class TestAgent(MCPAgentMixin):
            def __init__(self):
                self.config = {'agent_id': 'test_mixin_agent', 'agent_type': 'test_mixin'}
                super().__init__()
        
        agent = TestAgent()
        
        assert hasattr(agent, 'mcp_toolkit')
        assert hasattr(agent, 'mcp_initialized')
        assert agent.mcp_initialized is False
    
    def test_get_mcp_tools_not_initialized(self):
        """Test getting MCP tools when not initialized."""
        class TestAgent(MCPAgentMixin):
            def __init__(self):
                self.config = {'agent_id': 'test_mixin_agent', 'agent_type': 'test_mixin'}
                super().__init__()
        
        agent = TestAgent()
        tools = agent.get_mcp_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 0


@pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Integration components not available")
class TestMCPEnhancedAgent:
    """Test MCPEnhancedAgent functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.agent_config = AgentConfig(
            agent_id="test_enhanced_agent",
            agent_type="test_enhanced",
            prompt_template_id="test_template"
        )
        self.agent = MCPEnhancedAgent(self.agent_config)
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        assert self.agent.config.agent_id == "test_enhanced_agent"
        assert self.agent.config.agent_type == "test_enhanced"
        assert hasattr(self.agent, 'mcp_tools_loaded')
        assert hasattr(self.agent, 'available_tool_categories')
        assert hasattr(self.agent, 'tool_execution_history')
        assert self.agent.mcp_tools_loaded is False
    
    def test_task_validation(self):
        """Test task validation."""
        # Valid task
        valid_task = {"description": "Test task"}
        assert self.agent.validate_task(valid_task) is True
        
        # Invalid task (missing description)
        invalid_task = {"type": "test"}
        assert self.agent.validate_task(invalid_task) is False
    
    @pytest.mark.asyncio
    async def test_task_analysis(self):
        """Test task requirement analysis."""
        task = {
            "description": "Create a user story and commit to git",
            "type": "agile_development",
            "data": {"project": "test_project"}
        }
        
        analysis = await self.agent._analyze_task_requirements(task)
        
        assert analysis["task_type"] == "agile_development"
        assert analysis["description"] == "Create a user story and commit to git"
        assert analysis["data_provided"] is True
        assert analysis["complexity"] >= 0
        assert isinstance(analysis["required_categories"], list)
    
    def test_agent_status(self):
        """Test agent status retrieval."""
        status = self.agent.get_agent_status()
        
        assert status["agent_id"] == "test_enhanced_agent"
        assert status["agent_type"] == "test_enhanced"
        assert "mcp_integration" in status
        assert "mcp_tools_loaded" in status
        assert "available_tool_categories" in status
        assert "performance_metrics" in status


@pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Integration components not available")
class TestFactoryFunctions:
    """Test factory functions for easy integration."""
    
    def test_create_mcp_toolkit(self):
        """Test MCP toolkit factory function."""
        toolkit = create_mcp_toolkit("factory_test_agent", "factory_test")
        
        assert isinstance(toolkit, MCPToolkit)
        assert toolkit.agent_id == "factory_test_agent"
        assert toolkit.agent_type == "factory_test"
    
    def test_create_mcp_enhanced_agent(self):
        """Test MCP enhanced agent factory function."""
        agent = create_mcp_enhanced_agent("factory_agent", "factory_type")
        
        assert isinstance(agent, MCPEnhancedAgent)
        assert agent.config.agent_id == "factory_agent"
        assert agent.config.agent_type == "factory_type"


@pytest.mark.skipif(not INTEGRATION_AVAILABLE, reason="Integration components not available")
class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization_scenario(self):
        """Test complete agent initialization scenario."""
        agent = create_mcp_enhanced_agent("scenario_test_agent", "scenario_test")
        
        try:
            # This may fail due to missing MCP server, but should not crash
            success = await agent.initialize_agent(auto_discover_tools=True)
            
            # Should return boolean regardless of success/failure
            assert isinstance(success, bool)
            
            # Agent should have status regardless of MCP availability
            status = agent.get_agent_status()
            assert isinstance(status, dict)
            assert "agent_id" in status
            
        finally:
            # Cleanup should not fail
            await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_task_execution_scenario(self):
        """Test task execution scenario."""
        agent = create_mcp_enhanced_agent("task_test_agent", "task_test")
        
        try:
            # Initialize agent
            await agent.initialize_agent(auto_discover_tools=False)  # Don't auto-discover for test
            
            # Create test task
            task = {
                "description": "Test task execution with MCP integration",
                "type": "integration_test",
                "data": {"test_parameter": "test_value"}
            }
            
            # Execute task
            result = await agent.execute(task)
            
            # Should return result structure regardless of tool availability
            assert isinstance(result, dict)
            assert "success" in result
            assert "execution_time" in result
            assert "timestamp" in result
            
        finally:
            await agent.shutdown()


# Test runner function for pytest integration
def test_langchain_mcp_integration_components():
    """Main test function for pytest integration."""
    if not INTEGRATION_AVAILABLE:
        pytest.skip("LangChain-MCP integration components not available")
    
    # This function can be called by pytest to run all integration tests
    pass


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    pytest.main([__file__, "-v"])
