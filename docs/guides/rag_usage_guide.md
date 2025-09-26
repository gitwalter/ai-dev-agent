# RAG System Usage Guide

## Quick Start with RAG-Enhanced IDE Integration

**US-RAG-001: Your intelligent coding assistant is ready!** 🚀

## Overview

The RAG (Retrieval-Augmented Generation) system transforms your AI Development Agent into an intelligent coding assistant that understands your project deeply and provides contextually relevant suggestions.

## Getting Started

### 1. System Initialization

```python
import asyncio
from context.context_engine import ContextEngine
from models.config import ContextConfig

# Quick setup
config = ContextConfig()
engine = ContextEngine(config)

# Index your project (one-time setup)
await engine.index_codebase(".")
```

### 2. Basic Usage Examples

#### Find Similar Code Patterns

```python
# Natural language search
results = engine.search_context("database connection pooling")

for result in results:
    print(f"📁 {result['file_path']}")
    print(f"🎯 Relevance: {result['relevance_score']:.1%}")
    print(f"📝 {result['content'][:150]}...\n")
```

#### Project Intelligence Insights

```python
# Get project-specific intelligence
intelligence = engine.get_project_intelligence_summary()

print(f"🧠 Project Intelligence:")
print(f"   📊 Files indexed: {intelligence['total_files']}")
print(f"   🎯 Import patterns: {intelligence['import_patterns_learned']}")
print(f"   🔧 Error solutions: {intelligence['error_solutions_stored']}")
print(f"   📚 Code snippets: {intelligence['code_snippets']}")
```

#### Smart Code Suggestions

```python
# Get intelligent coding suggestions
query = "How to implement async error handling?"
suggestions = engine.search_context(query, max_results=5)

print(f"💡 Smart Suggestions for: {query}")
for i, suggestion in enumerate(suggestions, 1):
    print(f"{i}. {suggestion['file_path']}")
    print(f"   Context: {suggestion['metadata']['context_type']}")
    print(f"   Pattern: {suggestion['metadata']['code_pattern']}")
```

## Advanced Features

### Context-Aware Search

```python
# Search with specific context
context_results = engine.search_context_aware(
    query="error handling patterns",
    current_file="api/handlers.py",
    context_type="error_management"
)
```

### Pattern Learning

```python
# Learn from your coding patterns
patterns = engine.extract_coding_patterns(file_path="./")

print("🎨 Your Coding Patterns:")
for pattern_type, examples in patterns.items():
    print(f"  {pattern_type}: {len(examples)} examples found")
```

### Project-Specific Intelligence

```python
# Get tailored advice for your project
advice = engine.get_project_specific_advice("implementing new API endpoint")

print("🧭 Project-Specific Guidance:")
print(f"  📋 Recommended approach: {advice['approach']}")
print(f"  🔗 Related files: {advice['related_files']}")
print(f"  ⚠️  Common issues: {advice['potential_issues']}")
```

## Integration with Development Workflow

### 1. Code Review Assistant

```python
def rag_enhanced_code_review(file_path: str):
    """Get intelligent code review suggestions."""
    
    # Analyze file against project patterns
    analysis = engine.analyze_code_quality(file_path)
    
    return {
        "style_consistency": analysis["style_score"],
        "pattern_adherence": analysis["pattern_score"],
        "suggestions": analysis["improvement_suggestions"]
    }
```

### 2. Error Solution Finder

```python
def find_error_solutions(error_message: str):
    """Find solutions for common errors in your project."""
    
    # Search for similar error patterns
    solutions = engine.search_context(f"error: {error_message}")
    
    # Filter for actual solutions
    return [s for s in solutions if "solution" in s["metadata"]]
```

### 3. API Discovery

```python
def discover_project_apis():
    """Discover available APIs and their usage patterns."""
    
    apis = engine.search_context("API endpoint definition")
    
    api_map = {}
    for api in apis:
        endpoint = api["metadata"].get("endpoint", "unknown")
        api_map[endpoint] = {
            "file": api["file_path"],
            "usage_examples": api["metadata"].get("examples", [])
        }
    
    return api_map
```

## Real-World Use Cases

### Use Case 1: New Team Member Onboarding

```python
# Help new developers understand the project
def onboarding_assistant(topic: str):
    """Provide project-specific guidance for new developers."""
    
    results = engine.search_context(f"how to {topic}")
    
    guidance = {
        "relevant_files": [r["file_path"] for r in results[:5]],
        "code_examples": [r["content"] for r in results[:3]],
        "best_practices": engine.extract_best_practices(topic)
    }
    
    return guidance

# Example usage
auth_guidance = onboarding_assistant("implement authentication")
```

### Use Case 2: Refactoring Assistant

```python
def refactoring_suggestions(component: str):
    """Get intelligent refactoring suggestions."""
    
    # Find all usages of the component
    usages = engine.search_context(f"usage of {component}")
    
    # Analyze patterns and suggest improvements
    return engine.analyze_refactoring_opportunities(usages)
```

### Use Case 3: Documentation Generator

```python
def generate_smart_documentation(module_path: str):
    """Generate intelligent documentation using RAG."""
    
    # Analyze module and find related examples
    module_analysis = engine.analyze_module(module_path)
    related_examples = engine.search_context(f"examples using {module_path}")
    
    return {
        "description": module_analysis["purpose"],
        "usage_examples": [ex["content"] for ex in related_examples[:3]],
        "common_patterns": module_analysis["patterns"]
    }
```

## Performance Tips

### Optimization Strategies

1. **Efficient Querying**
   ```python
   # Use specific queries for better results
   specific_results = engine.search_context("FastAPI dependency injection")
   # vs
   vague_results = engine.search_context("dependencies")
   ```

2. **Batch Operations**
   ```python
   # Process multiple queries efficiently
   queries = ["error handling", "database queries", "API validation"]
   batch_results = engine.batch_search(queries)
   ```

3. **Context Filtering**
   ```python
   # Filter results by file type or context
   python_only = engine.search_context(
       "async functions", 
       file_filter="*.py"
   )
   ```

### Memory Management

```python
# Monitor and optimize memory usage
memory_stats = engine.get_memory_usage()
print(f"Vector store size: {memory_stats['vector_store_mb']:.1f} MB")
print(f"Documents loaded: {memory_stats['documents_count']}")

# Optimize if needed
if memory_stats['vector_store_mb'] > 500:
    engine.optimize_memory_usage()
```

## Configuration Examples

### Development Setup

```python
# Optimized for development
dev_config = ContextConfig(
    enable_semantic_search=True,
    max_search_results=10,
    max_file_size=1024 * 512,  # 512KB max
    vector_db_path="./dev_context_db"
)
```

### Production Setup

```python
# Optimized for production
prod_config = ContextConfig(
    enable_semantic_search=True,
    max_search_results=20,
    max_file_size=1024 * 1024,  # 1MB max
    vector_db_path="/var/lib/rag/context_db"
)
```

## Troubleshooting

### Common Issues and Solutions

1. **No Search Results**
   ```python
   # Check if indexing completed
   summary = engine.get_codebase_summary()
   if summary["total_files"] == 0:
       await engine.index_codebase(".")
   ```

2. **Slow Performance**
   ```python
   # Check index size and optimize
   if engine.get_index_size() > 100_000:
       engine.optimize_index()
   ```

3. **Memory Issues**
   ```python
   # Reduce batch size for large projects
   engine.config.batch_size = 25  # Default: 50
   ```

## Best Practices

### Query Writing

✅ **Good Queries**
- "async database connection patterns"
- "error handling in API endpoints"
- "user authentication implementation"

❌ **Poor Queries**
- "code"
- "function"
- "database"

### Project Organization

1. **Include Descriptive Comments**
   ```python
   # RAG learns from comments - make them descriptive
   def handle_user_authentication(token: str) -> User:
       """
       Authenticate user using JWT token with Redis caching.
       
       This implementation follows the project's auth pattern
       established in auth/middleware.py
       """
   ```

2. **Use Consistent Naming**
   ```python
   # Consistent patterns help RAG learn your style
   class UserRepository:  # Follow naming convention
   class ProductRepository:
   class OrderRepository:
   ```

## Integration with Agent Swarm

```python
# Enhanced agent coordination using RAG
from utils.system.universal_agent_tracker import get_universal_tracker

def rag_enhanced_agent_coordination(task: str):
    """Use RAG to enhance agent coordination."""
    
    tracker = get_universal_tracker()
    
    # Find relevant past solutions
    solutions = engine.search_context(f"agent coordination {task}")
    
    # Suggest optimal agent assignment
    assignment = engine.suggest_agent_assignment(task, solutions)
    
    # Track with Universal Agent Tracker
    session_id = tracker.register_agent("rag_coordinator", AgentType.PROJECT_AGENT)
    tracker.record_context_switch(session_id, ContextType.COORDINATION, reason=f"RAG-enhanced {task}")
    
    return assignment
```

## Next Steps

1. **Explore Advanced Features**: Try project pattern analysis
2. **Integrate with Cursor**: Set up IDE integration (Phase 2)
3. **Customize for Your Project**: Adjust configuration for optimal performance
4. **Monitor Performance**: Use built-in analytics to optimize usage

---

**🎯 Your RAG system is ready to enhance your development experience!**

For advanced features and troubleshooting, see the [complete RAG documentation](../architecture/components/rag_system.md).
