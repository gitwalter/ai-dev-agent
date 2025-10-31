"""
End-to-End Tests for RAG V2 (Phase 1 & 2)

Tests both SimpleRAG and AgenticRAG implementations with real queries.

Requirements:
- Qdrant running with documents indexed
- GEMINI_API_KEY or GOOGLE_API_KEY set

Author: AI Dev Agent
Created: 2025-01-29
Story: US-RAG-006 Phase 0
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.rag import SimpleRAG, AgenticRAG
from context.context_engine import ContextEngine
from models.config import ContextConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGTester:
    """Test harness for RAG V2 implementations."""
    
    def __init__(self):
        """Initialize test harness."""
        logger.info("=" * 80)
        logger.info("RAG V2 End-to-End Test Suite")
        logger.info("=" * 80)
        
        # Initialize context engine
        logger.info("\n[1/3] Initializing ContextEngine...")
        try:
            config = ContextConfig()
            config.qdrant_collection = "project_docs"
            self.context_engine = ContextEngine(config=config)
            logger.info("✅ ContextEngine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ContextEngine: {e}")
            raise
        
        # Initialize RAG agents
        logger.info("\n[2/3] Initializing RAG agents...")
        try:
            self.simple_rag = SimpleRAG(self.context_engine)
            logger.info("✅ SimpleRAG initialized")
            
            self.agentic_rag = AgenticRAG(self.context_engine)
            logger.info("✅ AgenticRAG initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG agents: {e}")
            raise
        
        # Test queries
        self.test_queries = [
            # Query 1: Direct factual (should work for both)
            {
                "query": "What is LangGraph?",
                "expected_topics": ["langgraph", "graph", "agent", "workflow"],
                "difficulty": "easy"
            },
            # Query 2: Multi-step reasoning (better for agentic)
            {
                "query": "How does the RAG system work in this project?",
                "expected_topics": ["rag", "retrieval", "vector", "qdrant"],
                "difficulty": "medium"
            },
            # Query 3: Requires synthesis (better for agentic)
            {
                "query": "What are the key components of the development agent system?",
                "expected_topics": ["agent", "development", "requirements", "architecture"],
                "difficulty": "medium"
            },
            # Query 4: Specific detail (good test for retrieval)
            {
                "query": "What LLM model is used in this project?",
                "expected_topics": ["gemini", "llm", "model"],
                "difficulty": "easy"
            },
            # Query 5: Potentially irrelevant (tests grading in agentic)
            {
                "query": "What is the capital of France?",
                "expected_topics": [],  # Should detect as irrelevant
                "difficulty": "irrelevant"
            },
        ]
        
        logger.info(f"✅ Test suite ready with {len(self.test_queries)} queries")
        logger.info("=" * 80)
    
    def run_phase1_tests(self):
        """Test Phase 1: SimpleRAG."""
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: SimpleRAG Tests")
        logger.info("=" * 80)
        
        results = []
        
        for i, test_case in enumerate(self.test_queries, 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"Test {i}/{len(self.test_queries)}: {test_case['query']}")
            logger.info(f"Difficulty: {test_case['difficulty']}")
            logger.info(f"{'='*70}")
            
            start_time = time.time()
            
            try:
                result = self.simple_rag.invoke(
                    query=test_case['query'],
                    thread_id=f"simple-test-{i}"
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                if result['status'] == 'completed':
                    response = result['response']
                    logger.info(f"\n✅ SUCCESS ({duration:.2f}s)")
                    logger.info(f"Response: {response[:300]}...")
                    
                    # Check for expected topics
                    if test_case['expected_topics']:
                        found_topics = [
                            topic for topic in test_case['expected_topics']
                            if topic.lower() in response.lower()
                        ]
                        logger.info(f"Topics found: {found_topics}/{len(test_case['expected_topics'])}")
                    
                    results.append({
                        'test': i,
                        'query': test_case['query'],
                        'status': 'success',
                        'duration': duration,
                        'response_length': len(response)
                    })
                else:
                    logger.error(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
                    results.append({
                        'test': i,
                        'query': test_case['query'],
                        'status': 'failed',
                        'error': result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                logger.error(f"\n❌ EXCEPTION: {e}")
                results.append({
                    'test': i,
                    'query': test_case['query'],
                    'status': 'exception',
                    'error': str(e)
                })
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("PHASE 1 SUMMARY")
        logger.info(f"{'='*80}")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        if success_count > 0:
            avg_duration = sum(r.get('duration', 0) for r in results if r['status'] == 'success') / success_count
            logger.info(f"Average Duration: {avg_duration:.2f}s")
        
        return results
    
    def run_phase2_tests(self):
        """Test Phase 2: AgenticRAG."""
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: AgenticRAG Tests")
        logger.info("=" * 80)
        
        results = []
        
        for i, test_case in enumerate(self.test_queries, 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"Test {i}/{len(self.test_queries)}: {test_case['query']}")
            logger.info(f"Difficulty: {test_case['difficulty']}")
            logger.info(f"{'='*70}")
            
            start_time = time.time()
            
            try:
                result = self.agentic_rag.invoke(
                    query=test_case['query'],
                    thread_id=f"agentic-test-{i}"
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                if result['status'] == 'completed':
                    response = result['response']
                    logger.info(f"\n✅ SUCCESS ({duration:.2f}s)")
                    logger.info(f"Response: {response[:300]}...")
                    
                    # Check for expected topics
                    if test_case['expected_topics']:
                        found_topics = [
                            topic for topic in test_case['expected_topics']
                            if topic.lower() in response.lower()
                        ]
                        logger.info(f"Topics found: {found_topics}/{len(test_case['expected_topics'])}")
                    
                    results.append({
                        'test': i,
                        'query': test_case['query'],
                        'status': 'success',
                        'duration': duration,
                        'response_length': len(response)
                    })
                else:
                    logger.error(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
                    results.append({
                        'test': i,
                        'query': test_case['query'],
                        'status': 'failed',
                        'error': result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                logger.error(f"\n❌ EXCEPTION: {e}")
                results.append({
                    'test': i,
                    'query': test_case['query'],
                    'status': 'exception',
                    'error': str(e)
                })
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("PHASE 2 SUMMARY")
        logger.info(f"{'='*80}")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        if success_count > 0:
            avg_duration = sum(r.get('duration', 0) for r in results if r['status'] == 'success') / success_count
            logger.info(f"Average Duration: {avg_duration:.2f}s")
        
        return results
    
    def compare_results(self, phase1_results, phase2_results):
        """Compare Phase 1 vs Phase 2 results."""
        logger.info(f"\n{'='*80}")
        logger.info("COMPARISON: SimpleRAG vs AgenticRAG")
        logger.info(f"{'='*80}")
        
        # Success rates
        phase1_success = sum(1 for r in phase1_results if r['status'] == 'success')
        phase2_success = sum(1 for r in phase2_results if r['status'] == 'success')
        
        logger.info(f"\nSuccess Rates:")
        logger.info(f"  SimpleRAG:  {phase1_success}/{len(phase1_results)} ({phase1_success/len(phase1_results)*100:.1f}%)")
        logger.info(f"  AgenticRAG: {phase2_success}/{len(phase2_results)} ({phase2_success/len(phase2_results)*100:.1f}%)")
        
        # Average durations
        if phase1_success > 0:
            phase1_avg = sum(r.get('duration', 0) for r in phase1_results if r['status'] == 'success') / phase1_success
            logger.info(f"\nAverage Duration:")
            logger.info(f"  SimpleRAG:  {phase1_avg:.2f}s")
        
        if phase2_success > 0:
            phase2_avg = sum(r.get('duration', 0) for r in phase2_results if r['status'] == 'success') / phase2_success
            logger.info(f"  AgenticRAG: {phase2_avg:.2f}s")
            
            if phase1_success > 0:
                diff = phase2_avg - phase1_avg
                logger.info(f"  Difference: +{diff:.2f}s (agentic does more work: grading + rewriting)")
        
        # Per-query comparison
        logger.info(f"\nPer-Query Comparison:")
        for i in range(len(phase1_results)):
            p1 = phase1_results[i]
            p2 = phase2_results[i]
            
            logger.info(f"\n  Query {i+1}: {p1['query'][:50]}...")
            logger.info(f"    SimpleRAG:  {p1['status']}")
            logger.info(f"    AgenticRAG: {p2['status']}")
    
    def run_all_tests(self):
        """Run complete test suite."""
        logger.info("\n[3/3] Running test suite...")
        
        # Phase 1 tests
        phase1_results = self.run_phase1_tests()
        
        # Phase 2 tests
        phase2_results = self.run_phase2_tests()
        
        # Comparison
        self.compare_results(phase1_results, phase2_results)
        
        # Final summary
        logger.info(f"\n{'='*80}")
        logger.info("FINAL SUMMARY")
        logger.info(f"{'='*80}")
        
        phase1_success = sum(1 for r in phase1_results if r['status'] == 'success')
        phase2_success = sum(1 for r in phase2_results if r['status'] == 'success')
        
        total_tests = len(phase1_results) + len(phase2_results)
        total_success = phase1_success + phase2_success
        
        logger.info(f"\nTotal Tests Run: {total_tests}")
        logger.info(f"Total Success: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
        
        if phase1_success == len(phase1_results) and phase2_success == len(phase2_results):
            logger.info("\n✅ ALL TESTS PASSED - RAG V2 IS READY FOR PRODUCTION")
        elif total_success >= total_tests * 0.8:
            logger.info("\n⚠️  MOST TESTS PASSED - Minor issues to fix")
        else:
            logger.info("\n❌ SIGNIFICANT FAILURES - Needs debugging")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}")
        
        return {
            'phase1': phase1_results,
            'phase2': phase2_results,
            'success_rate': total_success / total_tests
        }


def main():
    """Main test execution."""
    try:
        # Create tester
        tester = RAGTester()
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results['success_rate'] == 1.0:
            sys.exit(0)  # All passed
        elif results['success_rate'] >= 0.8:
            sys.exit(1)  # Mostly passed
        else:
            sys.exit(2)  # Many failures
            
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Test interrupted by user")
        sys.exit(3)
    except Exception as e:
        logger.error(f"\n\n❌ Test suite failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(4)


if __name__ == "__main__":
    main()

