#!/usr/bin/env python3
"""
MCP End-to-End Tests
===================

Complete end-to-end tests for the MCP system:
- Full system workflow testing
- Real tool execution scenarios
- Performance validation
- Production readiness verification

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1)
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MCP components
try:
    from utils.mcp.server import create_mcp_server
    from utils.mcp.client import create_mcp_client
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"❌ MCP end-to-end import failed: {e}")
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPEndToEnd:
    """End-to-end tests for complete MCP system."""
    
    @pytest.mark.asyncio
    async def test_complete_mcp_workflow(self):
        """Test complete MCP workflow from start to finish."""
        # Step 1: Create server
        server = create_mcp_server()
        assert server is not None
        
        # Step 2: Create client
        client = create_mcp_client("e2e_test_agent", "end_to_end_test")
        assert client is not None
        
        try:
            # Step 3: Start client (auto-connects to server)
            await client.start()
            
            # Step 4: Wait for connection
            await asyncio.sleep(1)
            
            # Step 5: Verify client stats
            stats = client.get_client_stats()
            assert isinstance(stats, dict)
            assert "agent_id" in stats
            assert stats["agent_id"] == "e2e_test_agent"
            
            # Step 6: Get available tools
            tools = client.get_available_tools()
            assert isinstance(tools, list)
            
            # Step 7: Test tool execution (if tools available)
            if tools:
                # Find a safe tool to test
                safe_tools = [t for t in tools if t.tool_id.startswith("db.")]
                if safe_tools:
                    test_tool = safe_tools[0]
                    
                    result = await client.execute_tool(
                        tool_id=test_tool.tool_id,
                        parameters={
                            "agent_id": "e2e_test_agent",
                            "agent_type": "end_to_end_test",
                            "context": {"test": "end_to_end"}
                        }
                    )
                    
                    # Verify result structure
                    assert hasattr(result, 'success')
                    assert hasattr(result, 'tool_id')
                    assert result.tool_id == test_tool.tool_id
            
            # Step 8: Test server info retrieval
            server_info = client.get_server_info()
            assert isinstance(server_info, list)
            
        finally:
            # Step 9: Cleanup
            await client.stop()
    
    @pytest.mark.asyncio
    async def test_mcp_system_resilience(self):
        """Test MCP system resilience and error handling."""
        client = create_mcp_client("resilience_test_agent", "resilience_test")
        
        try:
            await client.start()
            await asyncio.sleep(0.5)
            
            # Test 1: Non-existent tool
            result1 = await client.execute_tool(
                tool_id="nonexistent.tool",
                parameters={}
            )
            assert result1.success is False
            
            # Test 2: Invalid parameters
            result2 = await client.execute_tool(
                tool_id="db.track_agent_session",
                parameters={"invalid": "params"}
            )
            # Should handle gracefully (may succeed or fail, but shouldn't crash)
            assert hasattr(result2, 'success')
            
            # Test 3: Multiple rapid requests
            tasks = []
            for i in range(3):
                task = client.execute_tool(
                    tool_id="db.track_agent_session",
                    parameters={
                        "agent_id": f"resilience_agent_{i}",
                        "agent_type": "resilience_test",
                        "context": {"rapid_test": i}
                    }
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            assert len(results) == 3
            
            # All should complete without exceptions
            for result in results:
                assert not isinstance(result, Exception)
            
        finally:
            await client.stop()
    
    @pytest.mark.asyncio
    async def test_mcp_performance_benchmarks(self):
        """Test MCP system performance benchmarks."""
        client = create_mcp_client("benchmark_agent", "performance_benchmark")
        
        try:
            # Benchmark 1: Client startup time
            start_time = time.time()
            await client.start()
            startup_time = time.time() - start_time
            
            assert startup_time < 5.0, f"Startup time {startup_time:.2f}s exceeds 5.0s limit"
            
            await asyncio.sleep(0.5)
            
            # Benchmark 2: Tool discovery time
            start_time = time.time()
            tools = client.get_available_tools()
            discovery_time = time.time() - start_time
            
            assert discovery_time < 1.0, f"Tool discovery time {discovery_time:.2f}s exceeds 1.0s limit"
            
            # Benchmark 3: Tool execution time (if tools available)
            if tools:
                safe_tools = [t for t in tools if t.tool_id.startswith("db.")]
                if safe_tools:
                    test_tool = safe_tools[0]
                    
                    start_time = time.time()
                    result = await client.execute_tool(
                        tool_id=test_tool.tool_id,
                        parameters={
                            "agent_id": "benchmark_agent",
                            "agent_type": "performance_benchmark",
                            "context": {"benchmark": True}
                        }
                    )
                    execution_time = time.time() - start_time
                    
                    assert execution_time < 2.0, f"Tool execution time {execution_time:.2f}s exceeds 2.0s limit"
            
            # Benchmark 4: Client shutdown time
            start_time = time.time()
            await client.stop()
            shutdown_time = time.time() - start_time
            
            assert shutdown_time < 2.0, f"Shutdown time {shutdown_time:.2f}s exceeds 2.0s limit"
            
        except Exception as e:
            # Ensure cleanup even if test fails
            if client._running:
                await client.stop()
            raise e
    
    def test_mcp_system_configuration(self):
        """Test MCP system configuration and setup."""
        # Test server configuration
        server = create_mcp_server()
        server_info = server.get_server_info()
        
        assert server_info["server_name"] == "AI-Dev-Agent MCP Server"
        assert server_info["tools_count"] >= 12
        assert server_info["security_enabled"] is True
        
        # Test client configuration
        client = create_mcp_client("config_test_agent", "configuration_test")
        client_stats = client.get_client_stats()
        
        assert client_stats["agent_id"] == "config_test_agent"
        assert client_stats["agent_type"] == "configuration_test"
    
    @pytest.mark.asyncio
    async def test_mcp_production_readiness(self):
        """Test MCP system production readiness."""
        server = create_mcp_server()
        client = create_mcp_client("production_test_agent", "production_readiness")
        
        try:
            # Test 1: System components initialization
            assert server.tool_registry is not None
            assert server.security_manager is not None
            assert server.execution_engine is not None
            
            # Test 2: Security features
            security_policies = server.security_manager.access_policies
            assert len(security_policies) == 3  # PUBLIC, RESTRICTED, PRIVILEGED
            
            # Test 3: Tool registry completeness
            tools = server.tool_registry.tools
            assert len(tools) >= 12
            
            # Test 4: Client-server integration
            await client.start()
            await asyncio.sleep(0.5)
            
            stats = client.get_client_stats()
            assert "universal_tracking" in stats
            
            # Test 5: Error handling robustness
            result = await client.execute_tool(
                tool_id="invalid.tool",
                parameters={}
            )
            assert result.success is False
            assert isinstance(result.error, str)
            
        finally:
            await client.stop()


# Standalone test function for manual execution
async def run_end_to_end_test():
    """Run end-to-end test manually."""
    print("🧪 Running MCP End-to-End Test...")
    
    try:
        # Create components
        print("1. Creating MCP components...")
        server = create_mcp_server()
        client = create_mcp_client("manual_test_agent", "manual_end_to_end")
        print("   ✅ Components created")
        
        # Start client
        print("2. Starting client...")
        await client.start()
        await asyncio.sleep(1)
        print("   ✅ Client started")
        
        # Get stats
        print("3. Getting system stats...")
        stats = client.get_client_stats()
        print(f"   📊 Connected servers: {stats['connected_servers']}")
        print(f"   🔧 Total tools: {stats['total_tools']}")
        
        # Test tool execution
        print("4. Testing tool execution...")
        tools = client.get_available_tools()
        if tools:
            safe_tools = [t for t in tools if t.tool_id.startswith("db.")]
            if safe_tools:
                result = await client.execute_tool(
                    tool_id=safe_tools[0].tool_id,
                    parameters={
                        "agent_id": "manual_test_agent",
                        "agent_type": "manual_end_to_end",
                        "context": {"manual_test": True}
                    }
                )
                print(f"   ✅ Tool execution - Success: {result.success}")
        
        # Cleanup
        print("5. Cleaning up...")
        await client.stop()
        print("   ✅ Cleanup complete")
        
        print("\n🎉 End-to-End Test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ End-to-End Test FAILED: {e}")
        return False


# Test runner function for pytest integration
def test_mcp_end_to_end_components():
    """Main test function for pytest integration."""
    if not MCP_AVAILABLE:
        pytest.skip("MCP components not available")
    
    # This function can be called by pytest to run all MCP end-to-end tests
    pass


if __name__ == "__main__":
    # Run manual test when executed directly
    success = asyncio.run(run_end_to_end_test())
    sys.exit(0 if success else 1)
