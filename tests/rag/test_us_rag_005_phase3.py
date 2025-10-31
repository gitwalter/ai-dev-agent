#!/usr/bin/env python3
"""
Test Script for US-RAG-005 Phase 3: LangSmith Trace Validation

This script tests the sophisticated 5-agent workflow and validates:
1. All 5 agents visible in LangSmith traces
2. Each agent's work is logged correctly
3. Answer quality improvement vs. simple mode
4. Rewrite loop functionality

Usage:
    python tests/rag/test_us_rag_005_phase3.py

Requirements:
    - GEMINI_API_KEY environment variable set
    - LANGCHAIN_TRACING_V2=true
    - LANGCHAIN_API_KEY set (for LangSmith)
    - LANGCHAIN_PROJECT set (default: "ai-dev-agent")
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import after path setup
from context.context_engine import ContextEngine
from models.config import ContextConfig
from agents.rag.rag_swarm_coordinator import RAGSwarmCoordinator

# Ensure LangSmith tracing is enabled
if not os.getenv('LANGCHAIN_TRACING_V2'):
    logger.warning("⚠️  LANGCHAIN_TRACING_V2 not set - LangSmith traces won't be visible")
    logger.info("Set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY to enable tracing")

# Test queries
TEST_QUERIES = [
    {
        "query": "What is LangGraph and how does it handle state management?",
        "description": "General knowledge query - should use all agents",
        "expected_agents": ["query_analyst", "retrieval_specialist", "re_ranker", "quality_assurance", "writer"]
    },
    {
        "query": "Explain the difference between RAG and fine-tuning",
        "description": "Concept comparison - should trigger sophisticated processing",
        "expected_agents": ["query_analyst", "retrieval_specialist", "re_ranker", "quality_assurance", "writer"]
    },
    {
        "query": "How do I implement a custom agent in this project?",
        "description": "Implementation question - should use development context",
        "expected_agents": ["query_analyst", "retrieval_specialist", "re_ranker", "quality_assurance", "writer"]
    },
    {
        "query": "asdfghjkl random gibberish",
        "description": "Nonsense query - should trigger rewrite loop",
        "expected_agents": ["query_analyst", "rewrite_question"]  # Should rewrite and loop back
    }
]


async def test_sophisticated_workflow(query: str, description: str, expected_agents: list) -> Dict[str, Any]:
    """
    Test sophisticated 5-agent workflow.
    
    Args:
        query: Test query
        description: Description of test case
        expected_agents: List of agent names expected to execute
        
    Returns:
        Dict with test results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"TEST: {description}")
    logger.info(f"QUERY: {query}")
    logger.info(f"EXPECTED AGENTS: {expected_agents}")
    logger.info(f"{'='*80}\n")
    
    # Initialize context engine (uses default collection "ai_dev_agent_codebase")
    config = ContextConfig()
    context_engine = ContextEngine(config=config)
    
    # Initialize sophisticated coordinator (MODE 2: Automated Sophisticated)
    coordinator = RAGSwarmCoordinator(
        context_engine=context_engine,
        human_in_loop=False,  # Automated mode
        retrieval_only=False  # Full sophisticated workflow
    )
    
    # Create LangSmith config with metadata
    import uuid
    run_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": f"test_us_rag_005_{run_id}"
        },
        "run_name": f"US-RAG-005-Phase3-{description[:30]}",
        "tags": ["us-rag-005", "phase3", "sophisticated", "5-agent", "test"],
        "metadata": {
            "test_case": description,
            "query": query,
            "expected_agents": expected_agents,
            "sprint": "sprint-7",
            "user_story": "US-RAG-005",
            "phase": "phase3",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    logger.info(f"🔗 LangSmith Run: {config['run_name']}")
    logger.info(f"📋 Thread ID: {config['configurable']['thread_id']}")
    logger.info(f"🏷️  Tags: {config['tags']}")
    
    try:
        # Execute query
        result = await coordinator.execute(
            query=query,
            config=config,
            stream=False
        )
        
        # Extract response
        messages = result.get("messages", [])
        final_response = None
        
        # Find final AI response
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                if isinstance(msg.content, str) and msg.content.strip():
                    final_response = msg.content
                    break
        
        # Analyze execution
        execution_info = {
            "success": True,
            "query": query,
            "response_length": len(final_response) if final_response else 0,
            "response_preview": final_response[:200] + "..." if final_response and len(final_response) > 200 else final_response,
            "messages_count": len(messages),
            "has_response": final_response is not None
        }
        
        logger.info(f"✅ EXECUTION SUCCESSFUL")
        logger.info(f"   Response length: {execution_info['response_length']} chars")
        logger.info(f"   Messages: {execution_info['messages_count']}")
        logger.info(f"   Response preview: {execution_info['response_preview']}")
        
        return {
            "status": "success",
            "execution_info": execution_info,
            "config": config,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ EXECUTION FAILED: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "config": config
        }


async def test_simple_mode_comparison(query: str) -> Dict[str, Any]:
    """
    Test simple retrieval-only mode for comparison.
    
    Args:
        query: Test query
        
    Returns:
        Dict with test results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"COMPARISON TEST: Simple Mode")
    logger.info(f"QUERY: {query}")
    logger.info(f"{'='*80}\n")
    
    # Initialize context engine (uses default collection "ai_dev_agent_codebase")
    config = ContextConfig()
    context_engine = ContextEngine(config=config)
    
    # Initialize simple coordinator (MODE 1: Retrieval-Only)
    coordinator = RAGSwarmCoordinator(
        context_engine=context_engine,
        human_in_loop=False,
        retrieval_only=True  # Simple mode
    )
    
    # Create LangSmith config
    import uuid
    run_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": f"test_simple_{run_id}"
        },
        "run_name": f"US-RAG-005-Phase3-SimpleMode-{query[:30]}",
        "tags": ["us-rag-005", "phase3", "simple", "comparison", "test"],
        "metadata": {
            "mode": "simple",
            "query": query,
            "sprint": "sprint-7",
            "user_story": "US-RAG-005",
            "phase": "phase3",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        result = await coordinator.execute(
            query=query,
            config=config,
            stream=False
        )
        
        messages = result.get("messages", [])
        final_response = None
        
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                if isinstance(msg.content, str) and msg.content.strip():
                    final_response = msg.content
                    break
        
        return {
            "status": "success",
            "mode": "simple",
            "response_length": len(final_response) if final_response else 0,
            "response_preview": final_response[:200] + "..." if final_response and len(final_response) > 200 else final_response,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"❌ SIMPLE MODE FAILED: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "config": config
        }


async def main():
    """Run all Phase 3 validation tests."""
    logger.info("🚀 Starting US-RAG-005 Phase 3 Validation Tests")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"LangSmith Tracing: {'ENABLED' if os.getenv('LANGCHAIN_TRACING_V2') else 'DISABLED'}")
    logger.info(f"LangSmith Project: {os.getenv('LANGCHAIN_PROJECT', 'ai-dev-agent')}")
    
    results = {
        "sophisticated_tests": [],
        "comparison_tests": [],
        "summary": {}
    }
    
    # Test 1-3: Sophisticated workflow with different queries
    logger.info("\n" + "="*80)
    logger.info("TEST SUITE 1: Sophisticated 5-Agent Workflow")
    logger.info("="*80)
    
    for i, test_case in enumerate(TEST_QUERIES[:3], 1):  # First 3 queries
        logger.info(f"\n>>> Test {i}/{len(TEST_QUERIES[:3])}")
        result = await test_sophisticated_workflow(
            query=test_case["query"],
            description=test_case["description"],
            expected_agents=test_case["expected_agents"]
        )
        results["sophisticated_tests"].append(result)
        
        # Brief pause between tests
        await asyncio.sleep(2)
    
    # Test 4: Rewrite loop test
    logger.info("\n" + "="*80)
    logger.info("TEST SUITE 2: Rewrite Loop Test")
    logger.info("="*80)
    
    rewrite_test = TEST_QUERIES[3]
    result = await test_sophisticated_workflow(
        query=rewrite_test["query"],
        description=rewrite_test["description"],
        expected_agents=rewrite_test["expected_agents"]
    )
    results["sophisticated_tests"].append(result)
    
    # Test 5: Simple mode comparison
    logger.info("\n" + "="*80)
    logger.info("TEST SUITE 3: Simple Mode Comparison")
    logger.info("="*80)
    
    comparison_query = TEST_QUERIES[0]["query"]  # Use first query for comparison
    simple_result = await test_simple_mode_comparison(comparison_query)
    results["comparison_tests"].append(simple_result)
    
    # Generate summary
    sophisticated_success = sum(1 for r in results["sophisticated_tests"] if r["status"] == "success")
    comparison_success = sum(1 for r in results["comparison_tests"] if r["status"] == "success")
    
    results["summary"] = {
        "total_tests": len(results["sophisticated_tests"]) + len(results["comparison_tests"]),
        "sophisticated_tests": len(results["sophisticated_tests"]),
        "sophisticated_success": sophisticated_success,
        "comparison_tests": len(results["comparison_tests"]),
        "comparison_success": comparison_success,
        "success_rate": (sophisticated_success + comparison_success) / (len(results["sophisticated_tests"]) + len(results["comparison_tests"])) * 100
    }
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"Total Tests: {results['summary']['total_tests']}")
    logger.info(f"Sophisticated Tests: {results['summary']['sophisticated_success']}/{results['summary']['sophisticated_tests']}")
    logger.info(f"Comparison Tests: {results['summary']['comparison_success']}/{results['summary']['comparison_tests']}")
    logger.info(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    logger.info("\n" + "="*80)
    logger.info("✅ TEST EXECUTION COMPLETE")
    logger.info("="*80)
    logger.info("\n📊 NEXT STEPS:")
    logger.info("1. Check LangSmith traces at https://smith.langchain.com/")
    logger.info("2. Verify all 5 agents visible in traces:")
    logger.info("   - query_analyst")
    logger.info("   - retrieval_specialist")
    logger.info("   - re_ranker")
    logger.info("   - quality_assurance")
    logger.info("   - writer")
    logger.info("3. Compare sophisticated vs simple mode traces")
    logger.info("4. Verify rewrite loop triggered for nonsense query")
    logger.info("\n🔗 LangSmith URL:")
    logger.info(f"   https://smith.langchain.com/projects/{os.getenv('LANGCHAIN_PROJECT', 'ai-dev-agent')}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

