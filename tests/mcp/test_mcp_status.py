#!/usr/bin/env python3
"""
Quick MCP Server Status Check
==============================

Tests if MCP server and tools are working properly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.mcp.client import create_mcp_client, MCPClientConfig
from utils.mcp.server import create_mcp_server


async def test_mcp_status():
    """Test MCP server and tool loading."""
    print("="*60)
    print("MCP SERVER STATUS CHECK")
    print("="*60)
    
    # Test 1: Server Creation
    print("\n1. Testing MCP Server Creation...")
    try:
        server = create_mcp_server()
        print(f"   [OK] Server created successfully")
        print(f"   [INFO] Server info: {server.get_server_info()}")
    except Exception as e:
        print(f"   [ERROR] Server creation failed: {e}")
        return False
    
    # Test 2: Tool Loading
    print("\n2. Testing Tool Loading...")
    try:
        tool_count = len(server.tool_registry.tools)
        categories = server.tool_registry.get_tool_categories()
        
        print(f"   [OK] Tools loaded: {tool_count}")
        print(f"   [INFO] Categories:")
        for category, count in categories.items():
            print(f"      - {category}: {count} tools")
        
        # List some tools
        print(f"\n   [INFO] Sample tools:")
        for i, (tool_id, tool_def) in enumerate(list(server.tool_registry.tools.items())[:5]):
            print(f"      {i+1}. {tool_id}")
            print(f"         {tool_def.description[:60]}...")
            
    except Exception as e:
        print(f"   [ERROR] Tool loading failed: {e}")
        return False
    
    # Test 3: Client Connection
    print("\n3. Testing Client Connection...")
    try:
        client = create_mcp_client("test_agent", "testing")
        await client.start()
        
        print(f"   [OK] Client started successfully")
        
        # Get available tools from client
        available_tools = client.get_available_tools()
        print(f"   [INFO] Tools available to client: {len(available_tools)}")
        
        # Cleanup
        await client.stop()
        print(f"   [OK] Client stopped cleanly")
        
    except Exception as e:
        print(f"   [ERROR] Client connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("[SUCCESS] MCP SERVER IS WORKING!")
    print("="*60)
    print(f"\n[SUMMARY]")
    print(f"   - Server: Operational (embedded mode)")
    print(f"   - Tools loaded: {tool_count}")
    print(f"   - Categories: {len(categories)}")
    print(f"   - Client connection: Working")
    print(f"\n[USAGE]")
    print(f"   1. No separate server startup needed!")
    print(f"   2. Client automatically creates embedded server")
    print(f"   3. Tools auto-discovered from tool modules")
    print(f"\n[CATEGORIES] {', '.join(categories.keys())}")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_status())
    sys.exit(0 if success else 1)

