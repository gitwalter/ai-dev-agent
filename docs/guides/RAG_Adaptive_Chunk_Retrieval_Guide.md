# Adaptive RAG Chunk Retrieval System - User Guide

## Overview

The Adaptive RAG Chunk Retrieval System (US-RAG-003) intelligently determines the optimal number of document chunks to retrieve based on query characteristics, providing both automatic optimization and manual control.

## Features

### 🤖 **Auto Mode (Recommended)**
The system intelligently analyzes your query and retrieves the optimal number of chunks:

- **Simple Questions**: 5-20 chunks
  - Example: "What is Python?"
  - Fast retrieval for factual queries

- **Moderate Queries**: 15-30 chunks  
  - Example: "How does error handling work?"
  - Balanced context for conceptual understanding

- **Complex Analysis**: 25-45 chunks
  - Example: "Analyze microservices architecture trade-offs"
  - Comprehensive context for deep analysis

- **Multi-Step Reasoning**: 30-50 chunks
  - Example: "First explain caching, then show how it affects performance, finally discuss trade-offs"
  - Maximum context for complex reasoning

### 👤 **Manual Mode**
Full control over chunk retrieval (5-50 chunks):

**Guidelines:**
- Simple questions: 5-15 chunks
- Moderate queries: 15-25 chunks
- Complex analysis: 25-40 chunks
- Multi-step reasoning: 35-50 chunks

### ⚡ **Performance Mode**
Fast response with focused retrieval (8 chunks):
- Optimized for speed
- Best for quick queries
- Lower resource usage

## Using the System

### 1. **Access RAG Management**
Navigate to the RAG Management page in the Streamlit UI.

### 2. **Select Retrieval Strategy**
Choose from three modes:
- 🤖 Auto (Recommended) - Intelligent adaptation
- 👤 Manual Control - Specify exact chunk count
- ⚡ Performance Mode - Fast, focused retrieval

### 3. **Manual Control (Optional)**
If you select Manual mode:
1. Use the slider to specify chunk count (5-50)
2. Real-time feedback shows if your selection is optimal
3. Guidelines help you choose the right count for your query type

### 4. **Submit Your Query**
Type your question and let the system work:
- Auto mode: Analyzes query complexity and retrieves optimal chunks
- Manual mode: Uses your specified chunk count
- Performance mode: Fast retrieval with 8 chunks

### 5. **Review Adaptive Decision (Debug Mode)**
Enable debug mode to see:
- Query type classification
- Complexity and specificity scores
- Number of chunks retrieved
- Rationale for the decision

## Query Type Classification

### Simple Factual
**Characteristics:**
- Direct questions with single answer
- Definition requests
- Simple lookups

**Examples:**
- "What is Python?"
- "Define machine learning"
- "Who invented the internet?"

**Chunks:** 5-20

### Moderate Conceptual
**Characteristics:**
- Questions requiring concept understanding
- How-to questions
- Benefit/feature explanations

**Examples:**
- "How does error handling work?"
- "What are the benefits of RAG systems?"
- "Explain the concept of embeddings"

**Chunks:** 15-30

### Complex Conceptual
**Characteristics:**
- Multi-faceted questions
- Deep analysis required
- Multiple concepts involved

**Examples:**
- "Analyze microservices architecture trade-offs"
- "Compare different machine learning approaches"
- "Evaluate database indexing strategies"

**Chunks:** 25-45

### Multi-Hop Reasoning
**Characteristics:**
- Multiple steps of reasoning
- Sequential analysis
- Conditional logic

**Examples:**
- "If we implement feature A, then integrate with B, what's the impact?"
- "First explain X, then Y, finally Z"
- "Given microservices improve scalability but increase complexity, when should we migrate?"

**Chunks:** 30-50

## Performance Characteristics

### Speed
- **Query Analysis**: < 10ms per query
- **Decision Making**: < 20ms average
- **Throughput**: > 50 queries/second

### Quality
- **Consistency**: Identical decisions for same query
- **Adaptability**: Adjusts to query complexity
- **Context**: Balances completeness vs noise

## Tips for Best Results

### 1. **Use Auto Mode for Most Queries**
The system is trained to recognize query patterns and adapt appropriately.

### 2. **Switch to Manual for Specific Needs**
Use manual mode when:
- You know exactly how much context you need
- You're exploring document content systematically
- You want to test different chunk counts

### 3. **Enable Debug Mode for Insights**
See how the system classifies your queries and makes decisions.

### 4. **Adjust Based on Results**
If Auto mode doesn't provide enough context:
- Rephrase your query to be more specific
- Add "analyze" or "explain in detail" to increase complexity
- Switch to Manual mode and increase chunk count

If Auto mode provides too much context:
- Make your query more specific and focused
- Remove unnecessary details from your question
- Switch to Performance mode for faster results

## Advanced Features

### Context-Aware Adaptation
The system considers:
- Available document count
- Previous retrieval quality
- Performance constraints

### Decision History
All retrieval decisions are logged with:
- Query type and complexity
- Chunk count used
- Rationale for decision

### Statistics Tracking
Monitor system performance:
- Total decisions made
- Average chunk count
- Mode distribution (Auto/Manual/Performance)

## Troubleshooting

### **Query Not Classified Correctly?**
- Try rephrasing your question
- Add context words ("analyze", "explain", "compare")
- Use Manual mode for specific control

### **Too Many/Few Chunks Retrieved?**
- Check query complexity
- Use Manual mode for precise control
- Enable debug mode to see classification

### **Performance Too Slow?**
- Switch to Performance mode
- Reduce document scope in filters
- Use more specific queries

## Technical Details

### Query Analysis Process
1. **Word Count Analysis**: Counts words and identifies concepts
2. **Complexity Scoring**: Analyzes reasoning patterns and structure
3. **Specificity Calculation**: Determines query focus
4. **Type Classification**: Assigns query to one of four types
5. **Chunk Optimization**: Determines optimal chunk count

### Adaptive Algorithm
```python
chunk_count = base_count_for_type
+ complexity_adjustment
+ specificity_adjustment
+ context_adjustment
- performance_penalty (if enabled)
```

### Bounds
- **Minimum**: 5 chunks (ensures basic context)
- **Maximum**: 50 chunks (prevents noise)

## Integration

### For Developers
The adaptive retrieval system integrates with:
- `RetrievalSpecialistAgent`: Executes adaptive retrieval
- `QueryAnalyzer`: Analyzes query characteristics
- `AdaptiveRetrievalStrategy`: Determines optimal chunks
- `ContextEngine`: Performs semantic search

### API Usage
```python
from utils.rag import AdaptiveRetrievalStrategy, RetrievalContext

strategy = AdaptiveRetrievalStrategy()

# Auto mode
result = await strategy.get_optimal_chunk_count(
    query="How does caching work?",
    mode="auto",
    context=RetrievalContext(available_doc_count=100)
)

# Manual mode
result = await strategy.get_optimal_chunk_count(
    query="Explain microservices",
    mode="manual",
    manual_count=25
)

# Performance mode
result = await strategy.get_optimal_chunk_count(
    query="What is Python?",
    mode="performance"
)
```

## Feedback and Improvement

The system continuously learns from usage patterns. Your feedback helps improve:
- Query classification accuracy
- Chunk count optimization
- User experience

To provide feedback:
1. Enable debug mode
2. Review adaptive decisions
3. Report any misclassifications or sub-optimal results

## Summary

The Adaptive RAG Chunk Retrieval System provides:
- ✅ **Intelligent Adaptation**: Auto mode learns from query patterns
- ✅ **User Control**: Manual mode for precise needs
- ✅ **Fast Performance**: Performance mode for quick queries
- ✅ **Transparency**: Debug mode shows decision process
- ✅ **Quality**: Consistent, reliable results

Use Auto mode for daily queries, Manual for specific needs, and Performance for speed!

