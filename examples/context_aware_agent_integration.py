#!/usr/bin/env python3
"""
Context-Aware Agent Integration Examples
========================================

Practical examples showing how to integrate ContextEngine
into existing agents for context-enhanced decision-making.

Based on 2025 context engineering best practices:
- Phil Schmid: Context as a system, not a string
- LangChain: Quality > Quantity for context
- Prompt Engineering Guide: Dynamic context assembly

Created: 2025-01-08
Sprint: US-RAG-001 Phase 5
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.core.context_aware_agent import (
    ContextAwareAgent,
    get_shared_context_engine
)
from agents.core.base_agent import AgentConfig


# Example 1: Basic Context-Aware Code Generator
# ==============================================

class ContextAwareCodeGenerator(ContextAwareAgent):
    """
    Code generator that uses ContextEngine for:
    - Finding similar code examples
    - Getting import suggestions
    - Learning from existing patterns
    """
    
    async def generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code with context-enhanced decision making.
        
        Example task:
        {
            'query': 'Create a user authentication function',
            'file_path': 'auth/login.py',
            'requirements': ['password hashing', 'JWT tokens']
        }
        """
        print(f"\n🔨 Generating code for: {task['query']}")
        
        # 1. Get context from ContextEngine
        context_results = await self.get_relevant_context(
            task['query'],
            limit=5
        )
        
        print(f"📚 Found {len(context_results['results'])} relevant examples")
        
        # 2. Get file-specific context if file exists
        file_context = None
        if 'file_path' in task:
            file_context = self.get_file_context(task['file_path'])
            if file_context:
                print(f"📄 Loaded existing file context")
        
        # 3. Get import suggestions based on patterns
        imports = self.get_import_suggestions(task.get('file_path', ''))
        if imports:
            print(f"📦 Suggested imports: {len(imports)} patterns")
        
        # 4. Assemble rich context
        enhanced_task = {
            **task,
            'context': {
                'similar_examples': context_results['results'],
                'file_content': file_context,
                'import_patterns': imports,
                'project_intelligence': self.get_project_intelligence()
            }
        }
        
        # 5. Execute with context
        result = await self.execute_with_context(enhanced_task)
        
        print(f"✅ Code generated with context in {result['context_stats']['retrieval_time']:.3f}s")
        
        return result


# Example 2: Context-Aware Test Generator
# ========================================

class ContextAwareTestGenerator(ContextAwareAgent):
    """
    Test generator that uses ContextEngine to:
    - Find existing test patterns
    - Understand code structure
    - Generate comprehensive test cases
    """
    
    async def generate_tests(self, target_file: str) -> Dict[str, Any]:
        """
        Generate tests for a target file with context awareness.
        
        Args:
            target_file: Path to file that needs tests
        """
        print(f"\n🧪 Generating tests for: {target_file}")
        
        # 1. Get the code to test
        code_to_test = self.get_file_context(target_file)
        if not code_to_test:
            return {'error': 'File not found in context'}
        
        print(f"📄 Loaded target file ({len(code_to_test)} chars)")
        
        # 2. Find similar test files for patterns
        test_examples = await self.get_relevant_context(
            f"test examples for {target_file}",
            limit=3
        )
        
        print(f"🔍 Found {len(test_examples['results'])} test pattern examples")
        
        # 3. Get project testing patterns
        project_intel = self.get_project_intelligence()
        
        # 4. Assemble test generation context
        task = {
            'query': f'Generate comprehensive tests for {target_file}',
            'file_path': target_file,
            'code_content': code_to_test,
            'test_patterns': test_examples['results'],
            'project_context': project_intel
        }
        
        # 5. Generate tests with context
        result = await self.execute_with_context(task)
        
        print(f"✅ Tests generated using {result['context_stats']['results_count']} context examples")
        
        return result


# Example 3: Context-Aware Documentation Generator
# ================================================

class ContextAwareDocGenerator(ContextAwareAgent):
    """
    Documentation generator that uses ContextEngine to:
    - Understand code structure and relationships
    - Find related documentation
    - Maintain consistent doc style
    """
    
    async def generate_documentation(self, target_file: str, format: str = "markdown") -> Dict[str, Any]:
        """
        Generate documentation with context awareness.
        
        Args:
            target_file: File to document
            format: Output format (markdown, rst, etc.)
        """
        print(f"\n📝 Generating {format} documentation for: {target_file}")
        
        # 1. Get the code to document
        code_content = self.get_file_context(target_file)
        if not code_content:
            return {'error': 'File not found'}
        
        # 2. Find related code files
        related_code = await self.get_relevant_context(
            f"related code to {target_file}",
            limit=5
        )
        
        print(f"🔗 Found {len(related_code['results'])} related files")
        
        # 3. Find existing documentation for style consistency
        doc_examples = await self.get_relevant_context(
            "documentation examples markdown",
            limit=3
        )
        
        print(f"📚 Found {len(doc_examples['results'])} doc style examples")
        
        # 4. Assemble documentation context
        task = {
            'query': f'Document {target_file} in {format} format',
            'file_path': target_file,
            'code_content': code_content,
            'related_files': related_code['results'],
            'doc_examples': doc_examples['results'],
            'format': format
        }
        
        # 5. Generate documentation with context
        result = await self.execute_with_context(task)
        
        print(f"✅ Documentation generated with context")
        
        return result


# Example 4: Error-Solving Agent with Historical Context
# =======================================================

class ContextAwareErrorSolver(ContextAwareAgent):
    """
    Error solver that uses ContextEngine to:
    - Find historical error solutions
    - Understand error context
    - Suggest fixes based on past successes
    """
    
    async def solve_error(self, error_message: str, file_path: str = None) -> Dict[str, Any]:
        """
        Solve an error using historical context and code understanding.
        
        Args:
            error_message: The error message to solve
            file_path: Optional file where error occurred
        """
        print(f"\n🔧 Solving error: {error_message[:100]}...")
        
        # 1. Get historical solutions for this error
        historical_solutions = self.get_error_solution(error_message)
        
        if historical_solutions:
            print(f"💡 Found {len(historical_solutions)} historical solutions")
        
        # 2. Get file context if provided
        file_context = None
        if file_path:
            file_context = self.get_file_context(file_path)
            if file_context:
                print(f"📄 Loaded file context for {file_path}")
        
        # 3. Search for similar errors and solutions
        similar_errors = await self.get_relevant_context(
            f"error solution: {error_message}",
            limit=5
        )
        
        print(f"🔍 Found {len(similar_errors['results'])} similar error contexts")
        
        # 4. Assemble error-solving context
        task = {
            'query': f'Solve error: {error_message}',
            'file_path': file_path,
            'error_message': error_message,
            'historical_solutions': historical_solutions,
            'file_context': file_context,
            'similar_errors': similar_errors['results']
        }
        
        # 5. Solve with context
        result = await self.execute_with_context(task)
        
        print(f"✅ Solution found using context")
        
        return result


# Example 5: Multi-Agent Collaboration with Shared Context
# =========================================================

async def multi_agent_workflow_example():
    """
    Example of multiple agents collaborating with shared ContextEngine.
    
    Demonstrates:
    - Shared context across agents
    - Context reuse for efficiency
    - Coordinated multi-step workflow
    """
    print("\n" + "="*70)
    print("MULTI-AGENT COLLABORATION EXAMPLE")
    print("="*70)
    
    # 1. Create shared context engine (RECOMMENDED PATTERN)
    print("\n1️⃣ Creating shared ContextEngine...")
    shared_context = get_shared_context_engine()
    
    # 2. Index project once
    print("2️⃣ Indexing project (one-time cost)...")
    await shared_context.index_codebase('.')
    print(f"   ✅ Indexed {len(shared_context.documents)} document chunks")
    
    # 3. Create multiple specialized agents
    print("\n3️⃣ Creating specialized agents...")
    
    # Code Generator
    code_gen_config = AgentConfig(
        agent_id="code_generator",
        agent_type="code_generator",
        prompt_template_id="code_gen"
    )
    code_gen = ContextAwareCodeGenerator(code_gen_config, context_engine=shared_context)
    
    # Test Generator
    test_gen_config = AgentConfig(
        agent_id="test_generator",
        agent_type="test_generator",
        prompt_template_id="test_gen"
    )
    test_gen = ContextAwareTestGenerator(test_gen_config, context_engine=shared_context)
    
    # Doc Generator
    doc_gen_config = AgentConfig(
        agent_id="doc_generator",
        agent_type="documentation_generator",
        prompt_template_id="doc_gen"
    )
    doc_gen = ContextAwareDocGenerator(doc_gen_config, context_engine=shared_context)
    
    print("   ✅ Created 3 specialized agents")
    
    # 4. Execute coordinated workflow
    print("\n4️⃣ Executing coordinated workflow...")
    
    # Step 1: Generate code
    print("\n   Step 1: Code Generation")
    code_result = await code_gen.generate_code({
        'query': 'Create a user validation function',
        'file_path': 'utils/validation.py',
        'requirements': ['email validation', 'password strength']
    })
    
    # Step 2: Generate tests for the code
    print("\n   Step 2: Test Generation")
    test_result = await test_gen.generate_tests('utils/validation.py')
    
    # Step 3: Generate documentation
    print("\n   Step 3: Documentation Generation")
    doc_result = await doc_gen.generate_documentation(
        'utils/validation.py',
        format='markdown'
    )
    
    # 5. Show collaboration benefits
    print("\n5️⃣ Collaboration benefits:")
    print(f"   - Shared context: All agents used same indexed codebase")
    print(f"   - Total context retrievals: {sum([
        code_gen.get_context_stats()['statistics']['searches_performed'],
        test_gen.get_context_stats()['statistics']['searches_performed'],
        doc_gen.get_context_stats()['statistics']['searches_performed']
    ])}")
    print(f"   - Context reuse: Efficient shared memory model")
    
    print("\n" + "="*70)
    print("✅ MULTI-AGENT WORKFLOW COMPLETE")
    print("="*70)


# Example 6: Real-Time Context Debugging
# =======================================

async def context_debugging_example():
    """
    Example showing how to debug context retrieval and quality.
    
    Useful for:
    - Understanding what context agents see
    - Optimizing context quality
    - Troubleshooting agent decisions
    """
    print("\n" + "="*70)
    print("CONTEXT DEBUGGING EXAMPLE")
    print("="*70)
    
    # Create agent
    config = AgentConfig(
        agent_id="debug_agent",
        agent_type="test",
        prompt_template_id="test"
    )
    
    agent = ContextAwareAgent(config)
    await agent.index_project('.')
    
    # Query for context
    query = "context aware agent implementation"
    print(f"\n🔍 Query: '{query}'")
    
    # Get detailed context
    results = await agent.get_relevant_context(query, limit=5)
    
    # Analyze context quality
    print("\n📊 Context Analysis:")
    print(f"   Total found: {results['total_found']}")
    print(f"   Search type: {results['search_type']}")
    print(f"   Timestamp: {results['timestamp']}")
    
    if results['results']:
        print("\n📚 Retrieved Context:")
        for i, result in enumerate(results['results'], 1):
            print(f"\n   Result {i}:")
            print(f"   - File: {result['metadata'].get('file_path', 'unknown')}")
            print(f"   - Relevance: {result['relevance_score']:.3f}")
            print(f"   - Content preview: {result['content'][:100]}...")
    
    # Show project intelligence
    intelligence = agent.get_project_intelligence()
    print("\n🧠 Project Intelligence:")
    print(f"   - Files indexed: {intelligence['total_files_indexed']}")
    print(f"   - Vector documents: {intelligence['vector_documents']}")
    print(f"   - Import patterns: {intelligence['import_patterns_learned']}")
    print(f"   - Semantic search: {intelligence['semantic_search_available']}")
    
    print("\n" + "="*70)
    print("✅ CONTEXT DEBUGGING COMPLETE")
    print("="*70)


# Main execution
# ==============

async def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("CONTEXT-AWARE AGENT INTEGRATION EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate how to integrate ContextEngine")
    print("into existing agents for context-enhanced decision-making.")
    print("\nBased on 2025 best practices from:")
    print("- Phil Schmid: Context as a system, not a string")
    print("- LangChain: Quality > Quantity for context")
    print("- Prompt Engineering Guide: Dynamic context assembly")
    
    # Run examples
    await multi_agent_workflow_example()
    await context_debugging_example()
    
    print("\n" + "="*70)
    print("🎉 ALL EXAMPLES COMPLETE")
    print("="*70)
    print("\n📚 Key Takeaways:")
    print("   1. Use shared ContextEngine for multiple agents")
    print("   2. Index project once, reuse across all agents")
    print("   3. Context retrieval is fast (< 500ms)")
    print("   4. Agents make better decisions with context")
    print("   5. Debug mode helps understand agent reasoning")
    print("\n🚀 Ready to integrate into your own agents!")


if __name__ == "__main__":
    asyncio.run(main())

