# User Story: US-RAG-010 - Dynamic Graph Composition (Self-Building Agent)

**Epic**: EPIC-1: RAG System Enhancement  
**Sprint**: Sprint 8 (Future)  
**Story Points**: 21  
**Priority**: 🟡 **MEDIUM**  
**Status**: 📋 **BACKLOG**  
**Created**: 2025-10-28  
**Dependencies**: US-RAG-007 (Task-Adaptive RAG), US-RAG-009 (Dev-Context RAG), US-CONTEXT-001 (Context Detection & Routing)

## Story Overview

**As a** user with varying complexity tasks  
**I want** the RAG agent to analyze my task and build its own optimal workflow on-the-fly  
**So that** I get exactly the processing I need without manual workflow configuration

## Business Value

**The agent becomes its own architect!**

Instead of pre-defined workflows for task types, the agent:
1. Analyzes the task using LLM-based meta-reasoning
2. Determines optimal agent combination
3. Selects appropriate HITL checkpoints
4. Chooses relevant knowledge sources
5. Builds a custom graph dynamically
6. Executes the self-designed workflow

**Benefits**:
- **Ultimate Flexibility**: Not limited to pre-defined workflows
- **Intelligent Adaptation**: LLM reasoning determines best approach
- **Self-Optimization**: Agent learns from task patterns
- **User-Specific**: Adapts to individual user preferences over time

## Acceptance Criteria

### Phase 1: Task Analysis Meta-Agent
- [ ] **AC-1.1**: Implement `DynamicGraphComposer` class with LLM-based task analysis
- [ ] **AC-1.2**: Create analysis prompt that extracts task characteristics
- [ ] **AC-1.3**: Parse LLM response into `TaskAnalysis` structure
- [ ] **AC-1.4**: Determine required agents based on task complexity
- [ ] **AC-1.5**: Determine HITL checkpoints based on task criticality
- [ ] **AC-1.6**: Determine knowledge sources based on task domain

### Phase 2: Dynamic Graph Builder
- [ ] **AC-2.1**: Implement graph builder that constructs workflow from TaskAnalysis
- [ ] **AC-2.2**: Dynamically add only needed agent nodes
- [ ] **AC-2.3**: Dynamically add only needed HITL checkpoint nodes
- [ ] **AC-2.4**: Build edges based on agent sequence from analysis
- [ ] **AC-2.5**: Configure interrupts based on selected checkpoints

### Phase 3: LLM-Based Analysis Logic
- [ ] **AC-3.1**: LLM determines task type (simple_qa, code_implementation, architecture_design, etc.)
- [ ] **AC-3.2**: LLM determines complexity (simple, medium, complex)
- [ ] **AC-3.3**: LLM selects required agents (query_analyst, retrieval, re_ranker, QA, writer)
- [ ] **AC-3.4**: LLM selects HITL checkpoints (where human input adds value)
- [ ] **AC-3.5**: LLM confidence scoring (how sure it is of the analysis)

### Phase 4: Self-Learning & Optimization
- [ ] **AC-4.1**: Store task analysis results for future learning
- [ ] **AC-4.2**: Track workflow performance per task type
- [ ] **AC-4.3**: Adjust analysis based on user feedback
- [ ] **AC-4.4**: Optimize agent combinations based on success metrics

## How It Works

### Step 1: User Submits Task
```python
User: "Implement a LangGraph agent with checkpointing"
```

### Step 2: Meta-Agent Analyzes Task
```
🧠 TASK_ANALYZER (LLM-powered meta-agent)

Analyzes:
- Query content and intent
- Complexity indicators
- Required knowledge domains
- Critical decision points

LLM Reasoning:
"This is a CODE_IMPLEMENTATION task with MEDIUM complexity.
Requires: coding standards, API documentation, code examples.
Agents needed: query_analyst (understand requirements),
               retrieval_specialist (get API docs + examples),
               writer (generate code).
HITL needed at: retrieval (verify API usage), writer (review code).
Confidence: 85%"

Output:
TaskAnalysis(
    task_type="code_implementation",
    complexity="medium",
    required_agents=[query_analyst, retrieval_specialist, writer],
    hitl_checkpoints=[review_retrieval, review_draft],
    knowledge_sources=["framework_docs", "coding_guidelines"],
    confidence=0.85
)
```

### Step 3: Graph Builder Constructs Workflow
```
🔧 GRAPH_BUILDER

Takes TaskAnalysis and builds:

START
  ↓
query_analyst
  ↓
retrieval_specialist
  ↓
[HITL: review_retrieval] ← Dynamic checkpoint
  ↓
writer
  ↓
[HITL: review_draft] ← Dynamic checkpoint
  ↓
END

Graph compiled with interrupts at: review_retrieval, review_draft
```

### Step 4: Execute Custom Graph
```
▶️ EXECUTE CUSTOM GRAPH

The agent runs the dynamically built workflow,
pausing at the strategically placed HITL checkpoints
determined by the meta-agent's analysis.
```

## LLM Analysis Prompt

```python
ANALYSIS_PROMPT = """Analyze this task and determine the optimal RAG workflow:

TASK: {query}

CONTEXT: {context}

Determine:

1. TASK TYPE (one of):
   - simple_qa: Quick factual question
   - code_implementation: Writing code
   - architecture_design: System design
   - api_integration: API integration
   - bug_fixing: Debugging
   - research: Deep research

2. COMPLEXITY (one of):
   - simple: Quick answer, minimal processing
   - medium: Standard workflow
   - complex: Deep analysis, multiple iterations

3. REQUIRED AGENTS (select needed):
   - query_analyst: Understand query intent
   - retrieval_specialist: Multi-source retrieval
   - re_ranker: Relevance scoring
   - quality_assurance: Quality checks
   - writer: Answer generation

4. HITL CHECKPOINTS (where human should review):
   - review_query: Verify understanding
   - review_retrieval: Check sources
   - review_context: Approve quality
   - review_draft: Review answer
   - final_approval: Sign-off

5. KNOWLEDGE SOURCES (what to retrieve):
   - architecture, coding_guidelines, framework_docs, agile

Provide analysis in structured format with confidence score.
"""
```

## Technical Implementation

### DynamicGraphComposer Class
```python
class DynamicGraphComposer:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    async def analyze_task(self, query, context) -> TaskAnalysis:
        """LLM-powered task analysis"""
        # Send prompt to LLM
        # Parse response into TaskAnalysis
        return task_analysis
    
    def build_graph(self, analysis: TaskAnalysis) -> StateGraph:
        """Build custom graph from analysis"""
        workflow = StateGraph(MessagesState)
        
        # Add only needed agents
        for agent in analysis.required_agents:
            workflow.add_node(agent.value, self._get_node(agent))
        
        # Add only needed HITL checkpoints
        for checkpoint in analysis.hitl_checkpoints:
            workflow.add_node(checkpoint.value, self._get_hitl_node(checkpoint))
        
        # Build edges
        self._build_edges(workflow, analysis)
        
        return workflow.compile()
```

### Files Created/Modified
- `agents/rag/dynamic_graph_composer.py` - **NEW** Dynamic composer
- `agents/rag/rag_swarm_coordinator.py` - Integration with composer
- `docs/architecture/DYNAMIC_GRAPH_COMPOSITION.md` - Design docs

### Integration with US-CONTEXT-001 (Context Detection & Routing)
- **Enhanced Analysis**: `ContextDetectionRouter` provides fast context hints before LLM analysis
- **Tool Selection**: `ToolRAGSystem` informs which tools are available for the task
- **Knowledge Routing**: `KnowledgeRouter` informs which knowledge sources to use
- **Self-Optimization**: Routing metrics (`RoutingMetrics`) enable learning from successful compositions
- **Better Confidence**: Context detection confidence improves task analysis confidence scoring

## Testing Strategy

1. **Analysis Test**: Test LLM analysis on variety of tasks
2. **Graph Construction Test**: Verify graphs built correctly from analysis
3. **Execution Test**: Test dynamically built graphs execute correctly
4. **Confidence Test**: Track analysis confidence vs. actual success
5. **Learning Test**: Verify optimization over time

## Definition of Done

- [ ] DynamicGraphComposer implemented
- [ ] LLM-based task analysis working
- [ ] Dynamic graph building working
- [ ] Execution of custom graphs working
- [ ] Confidence scoring implemented
- [ ] Self-learning hooks in place
- [ ] All tests passing
- [ ] Documentation updated

## Dependencies

- Depends on: US-RAG-007 (Task-Adaptive RAG), US-RAG-009 (Dev-Context RAG)
- Enables: Truly adaptive, self-optimizing RAG system

## Success Metrics

- Analysis accuracy: > 85% correct task type classification
- Optimal agent selection: User satisfaction with chosen workflow
- Confidence correlation: High confidence = high success rate
- Learning improvement: Better decisions over time

## Notes

**This is Meta-Programming at the Graph Level!**

The agent becomes its own architect, using LLM reasoning to design optimal workflows on-the-fly.

**Key Insight**: Instead of hardcoding workflows for every possible task type, let the LLM figure out the best approach based on the specific task characteristics.

**Future**: This enables continuous learning and optimization - the agent gets smarter over time by learning which workflows work best for which tasks.

