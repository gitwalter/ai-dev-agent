#!/usr/bin/env python3
"""
Test File Organizer Agent
==========================

Demonstrates:
1. MCP file.read tool integration
2. Human-in-the-loop workflow
3. LangGraph Studio compatibility
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.workflow.file_organizer_agent import FileOrganizerAgent


async def test_file_organizer():
    """Test file organizer agent with MCP tools."""
    
    print("=" * 70)
    print("FILE ORGANIZER AGENT - MCP TOOLS + HUMAN-IN-THE-LOOP DEMO")
    print("=" * 70)
    
    # Create and initialize agent
    print("\n1. Initializing agent...")
    agent = FileOrganizerAgent()
    await agent.initialize()
    print("   [OK] Agent initialized with MCP tools")
    
    # Use project root as test directory
    test_directory = str(project_root)
    
    print(f"\n2. Starting file organization for: {test_directory}")
    print("   Organization rule: 'organize Python files by type'")
    
    # Start organization (will interrupt at human_review)
    result = await agent.organize_files(
        directory_path=test_directory,
        organization_rules="analyze Python files and suggest organization by type (tests, agents, utils, etc.)",
        thread_id="test_demo_1"
    )
    
    print(f"\n3. Workflow Status: {result.get('current_step')}")
    print(f"   Files scanned: {len(result.get('scanned_files', []))}")
    print(f"   Analysis: {result.get('file_analysis', 'N/A')[:200]}...")
    
    # Show proposed changes
    proposed = result.get('proposed_changes', [])
    print(f"\n4. Proposed Changes ({len(proposed)} total):")
    for i, change in enumerate(proposed[:5], 1):  # Show first 5
        print(f"   {i}. {change.get('description', 'N/A')}")
    if len(proposed) > 5:
        print(f"   ... and {len(proposed) - 5} more changes")
    
    # Human review simulation
    print("\n5. Human-in-the-Loop:")
    print("   [INTERRUPT] Workflow paused for human approval")
    print("   Human reviewing proposed changes...")
    
    # Simulate human decision
    user_decision = input("\n   Do you approve these changes? (yes/no): ").strip().lower()
    approved = user_decision == "yes"
    
    if approved:
        print("   [APPROVED] Continuing with execution...")
        
        # Continue workflow after approval
        final_result = await agent.continue_after_approval(
            approved=True,
            feedback="Changes approved by user",
            thread_id="test_demo_1"
        )
        
        print(f"\n6. Execution Result:")
        print(f"   Status: {final_result.get('execution_status')}")
        print(f"   Changes executed: {len(final_result.get('executed_changes', []))}")
        
        # Show executed changes
        executed = final_result.get('executed_changes', [])
        for i, change in enumerate(executed[:5], 1):
            print(f"   {i}. {change.get('change', 'N/A')[:100]}...")
        
        print("\n[SUCCESS] File organization workflow completed!")
    else:
        print("   [REJECTED] Changes rejected by user")
        print("\n[CANCELLED] File organization workflow cancelled")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    
    return result


async def test_mcp_tool_direct():
    """Test MCP file.read tool directly."""
    
    print("\n" + "=" * 70)
    print("BONUS: DIRECT MCP TOOL TEST")
    print("=" * 70)
    
    # Create simple agent just to get MCP tools
    agent = FileOrganizerAgent()
    await agent.initialize()
    
    print(f"\n[INFO] MCP Tools loaded: {len(agent.mcp_tools)}")
    print("[INFO] Available tools:")
    for tool in agent.mcp_tools[:10]:  # Show first 10
        print(f"  - {tool.name}: {tool.description[:60]}...")
    
    # Find file.read tool
    file_read_tool = None
    for tool in agent.mcp_tools:
        if tool.name == "file.read":
            file_read_tool = tool
            break
    
    if file_read_tool:
        print(f"\n[OK] Found file.read tool!")
        print(f"     Description: {file_read_tool.description}")
        print(f"     Can read files: YES ✅")
    else:
        print("\n[WARNING] file.read tool not found")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_file_organizer())
    
    # Optional: Test MCP tools directly
    print("\n\nRun direct MCP tool test? (yes/no): ", end="")
    if input().strip().lower() == "yes":
        asyncio.run(test_mcp_tool_direct())

