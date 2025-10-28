#!/usr/bin/env python3
"""Quick test of MCP file.read tool."""

import asyncio
import sys
from pathlib import Path

# Add project root to path (go up 2 levels from tests/mcp/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.mcp.client import MCPClient, MCPClientConfig


async def test_file_read():
    """Test the file.read MCP tool."""
    print("[TEST] Testing MCP file.read tool...\n")
    
    # Create MCP client
    config = MCPClientConfig(
        agent_id="test_agent",
        agent_type="test",
        auto_discover=True
    )
    
    client = MCPClient(config)
    
    try:
        # Start client (connects to embedded MCP server)
        print("1. Starting MCP client...")
        success = await client.start()
        if not success:
            print("[FAIL] Failed to start MCP client")
            return
        print("[OK] Client started\n")
        
        # Get available tools
        tools = client.get_available_tools()
        print(f"2. Available tools: {len(tools)}")
        
        # Find file.read tool
        file_read_tool = None
        for tool in tools:
            if tool.tool_id == "file.read":
                file_read_tool = tool
                break
        
        if not file_read_tool:
            print("[FAIL] file.read tool not found!")
            print(f"Available tools: {[t.tool_id for t in tools]}")
            return
        
        print(f"[OK] Found file.read tool: {file_read_tool.description}\n")
        
        # Test reading a real file (README.md from project root)
        test_file = str(project_root / "README.md")
        print(f"3. Testing file.read on: {test_file}")
        
        result = await client.execute_tool(
            tool_id="file.read",
            parameters={"file_path": test_file}
        )
        
        if result.success:
            print(f"[OK] Tool execution successful!")
            print(f"   Execution time: {result.execution_time:.3f}s")
            
            # Show first 500 characters of result
            result_str = str(result.result)
            if len(result_str) > 500:
                print(f"\n[FILE CONTENT] First 500 chars:\n{result_str[:500]}...")
            else:
                print(f"\n[FILE CONTENT]:\n{result_str}")
        else:
            print(f"[FAIL] Tool execution failed: {result.error}")
        
        # Stop client
        print("\n4. Stopping client...")
        await client.stop()
        print("[OK] Client stopped")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_file_read())

