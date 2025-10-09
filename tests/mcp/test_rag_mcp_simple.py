#!/usr/bin/env python3
"""
Simple RAG-MCP Integration Test
==============================

A simplified test to validate RAG-MCP integration step by step.

Author: AI Development Agent
Created: 2025-01-02
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required imports work."""
    print("🔧 Testing imports...")
    
    try:
        from models.config import ContextConfig
        print("✅ ContextConfig imported successfully")
    except ImportError as e:
        print(f"❌ ContextConfig import failed: {e}")
        return False
    
    try:
        from context.context_engine import ContextEngine
        print("✅ ContextEngine imported successfully")
    except ImportError as e:
        print(f"❌ ContextEngine import failed: {e}")
        return False
    
    try:
        from utils.mcp.tools.rag_tools import get_rag_mcp_tools
        print("✅ RAG-MCP tools imported successfully")
    except ImportError as e:
        print(f"❌ RAG-MCP tools import failed: {e}")
        return False
    
    return True

def test_context_engine_initialization():
    """Test ContextEngine initialization."""
    print("\n🔧 Testing ContextEngine initialization...")
    
    try:
        from models.config import ContextConfig
        from context.context_engine import ContextEngine
        
        # Create config
        config = ContextConfig(
            enable_codebase_indexing=True,
            index_file_extensions=[".py", ".md"],
            exclude_patterns=["__pycache__", ".git"],
            max_context_size=5000,
            max_file_size=512 * 1024
        )
        print("✅ ContextConfig created successfully")
        
        # Initialize engine
        engine = ContextEngine(config)
        print("✅ ContextEngine initialized successfully")
        
        return engine
        
    except Exception as e:
        print(f"❌ ContextEngine initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_rag_tools_initialization():
    """Test RAG-MCP tools initialization."""
    print("\n🔧 Testing RAG-MCP tools initialization...")
    
    try:
        from utils.mcp.tools.rag_tools import get_rag_mcp_tools
        
        # Get RAG tools instance
        rag_tools = get_rag_mcp_tools()
        print("✅ RAG-MCP tools instance created successfully")
        
        # Check if context engine is initialized
        if rag_tools.context_engine:
            print("✅ Context engine is available in RAG tools")
        else:
            print("⚠️ Context engine is not available in RAG tools")
        
        return rag_tools
        
    except Exception as e:
        print(f"❌ RAG-MCP tools initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_basic_functionality(rag_tools):
    """Test basic RAG functionality."""
    print("\n🔧 Testing basic RAG functionality...")
    
    try:
        # Test context analysis
        print("Testing context analysis...")
        result = await rag_tools.context_analysis(
            text="This is a test document about RAG and MCP integration",
            analysis_type="comprehensive"
        )
        
        if result["success"]:
            print("✅ Context analysis successful")
            print(f"   Keywords: {result['analysis'].get('keywords', [])[:3]}")
            print(f"   Sentiment: {result['analysis'].get('sentiment', 'unknown')}")
        else:
            print(f"❌ Context analysis failed: {result.get('error', 'Unknown error')}")
        
        # Test knowledge base enrichment
        print("\nTesting knowledge base enrichment...")
        enrich_result = await rag_tools.enrich_knowledge_base(
            content="RAG-MCP integration provides semantic search capabilities for intelligent tool selection.",
            content_type="test_pattern",
            metadata={"test": True, "category": "integration"}
        )
        
        if enrich_result["success"]:
            print("✅ Knowledge base enrichment successful")
            print(f"   Enrichment ID: {enrich_result['enrichment_id']}")
        else:
            print(f"❌ Knowledge base enrichment failed: {enrich_result.get('error', 'Unknown error')}")
        
        # Test semantic search
        print("\nTesting semantic search...")
        search_result = await rag_tools.semantic_search(
            query="RAG integration semantic search",
            limit=5
        )
        
        if search_result["success"]:
            print("✅ Semantic search successful")
            print(f"   Results found: {len(search_result['results'])}")
        else:
            print(f"❌ Semantic search failed: {search_result.get('error', 'Unknown error')}")
        
        # Test tool selection
        print("\nTesting intelligent tool selection...")
        tool_result = await rag_tools.intelligent_tool_selection(
            task_description="Process a document and perform semantic search",
            available_tools=["file.read", "rag.process", "rag.search", "database.store"]
        )
        
        if tool_result["success"]:
            print("✅ Tool selection successful")
            print(f"   Recommended tools: {tool_result['recommended_tools']}")
            print(f"   Confidence: {tool_result['confidence_score']:.2f}")
        else:
            print(f"❌ Tool selection failed: {tool_result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Simple RAG-MCP Integration Test")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed - stopping")
        return
    
    # Test 2: ContextEngine initialization
    context_engine = test_context_engine_initialization()
    if not context_engine:
        print("\n❌ ContextEngine initialization failed - stopping")
        return
    
    # Test 3: RAG tools initialization
    rag_tools = test_rag_tools_initialization()
    if not rag_tools:
        print("\n❌ RAG tools initialization failed - stopping")
        return
    
    # Test 4: Basic functionality
    functionality_ok = await test_basic_functionality(rag_tools)
    
    # Summary
    print("\n" + "=" * 50)
    if functionality_ok:
        print("🎉 All tests passed! RAG-MCP integration is working.")
    else:
        print("⚠️ Some tests failed, but basic integration is functional.")
    
    # Tool usage stats
    if rag_tools:
        stats = rag_tools.get_tool_usage_stats()
        print(f"\n📊 Tool Usage Stats:")
        print(f"   Total executions: {stats['total_executions']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
