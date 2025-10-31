"""
Dynamic Graph Composer - Self-Building RAG Workflows

The agent analyzes the task and builds its own graph on-the-fly,
selecting only the agents and HITL points it needs.

This is meta-programming at the graph level - the agent is its own architect!
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Available agent types for composition."""
    QUERY_ANALYST = "query_analyst"
    RETRIEVAL_SPECIALIST = "retrieval_specialist"
    RE_RANKER = "re_ranker"
    QUALITY_ASSURANCE = "quality_assurance"
    WRITER = "writer"


class HITLCheckpoint(str, Enum):
    """Available HITL checkpoint types."""
    SELECT_SOURCES = "select_knowledge_sources"
    REVIEW_QUERY = "review_query_analysis"
    REVIEW_RETRIEVAL = "review_retrieval_results"
    REVIEW_CONTEXT = "review_ranked_context"
    REVIEW_DRAFT = "review_draft_answer"
    FINAL_APPROVAL = "final_approval"


@dataclass
class TaskAnalysis:
    """Result of task analysis - blueprint for graph construction."""
    
    # Task characteristics
    task_type: str  # "code_implementation", "architecture_design", etc.
    complexity: str  # "simple", "medium", "complex"
    estimated_steps: int
    
    # Agent composition
    required_agents: List[AgentType]
    agent_sequence: List[str]  # Order of agent execution
    
    # Knowledge requirements
    knowledge_sources: List[str]  # Categories or specific sources
    
    # HITL configuration
    hitl_checkpoints: List[HITLCheckpoint]
    
    # Routing rules
    allow_rewrite: bool  # Can loop back on quality issues
    allow_iteration: bool  # Can iterate for refinement
    
    # Metadata
    confidence: float  # How confident we are in this analysis
    reasoning: str  # Why this composition was chosen


class DynamicGraphComposer:
    """
    Analyzes tasks and dynamically builds optimal RAG workflows.
    
    The agent becomes its own architect, composing graphs on-the-fly
    based on task requirements.
    """
    
    def __init__(self, coordinator):
        """
        Initialize with reference to RAGSwarmCoordinator for access to agents.
        
        Args:
            coordinator: RAGSwarmCoordinator instance
        """
        self.coordinator = coordinator
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0,
            transport="rest"  # Use REST to avoid grpc event loop issues
        )
        logger.info("✅ DynamicGraphComposer initialized")
    
    async def analyze_task(self, query: str, context: Optional[Dict] = None) -> TaskAnalysis:
        """
        Analyze task and determine optimal workflow composition.
        
        This is the "meta-agent" that decides what the workflow should look like.
        
        Args:
            query: User's query/task
            context: Optional context (agent role, open files, etc.)
            
        Returns:
            TaskAnalysis with graph building instructions
        """
        logger.info(f"🧠 Analyzing task for dynamic graph composition: '{query[:60]}...'")
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(query, context)
        
        # Get LLM analysis
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=analysis_prompt)
            ])
            
            # Parse LLM response into TaskAnalysis
            analysis = self._parse_analysis(response.content, query)
            
            logger.info(f"✅ Task analysis complete: {analysis.task_type} ({analysis.complexity})")
            logger.info(f"   Agents: {[a.value for a in analysis.required_agents]}")
            logger.info(f"   HITL Points: {len(analysis.hitl_checkpoints)}")
            logger.info(f"   Confidence: {analysis.confidence:.0%}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Task analysis failed: {e}")
            # Fallback to default composition
            return self._default_analysis(query)
    
    def build_graph(self, analysis: TaskAnalysis) -> StateGraph:
        """
        Build custom graph based on task analysis.
        
        This takes the TaskAnalysis blueprint and constructs a real
        LangGraph workflow with only the needed agents and HITL points.
        
        Args:
            analysis: TaskAnalysis from analyze_task()
            
        Returns:
            Compiled StateGraph ready for execution
        """
        logger.info(f"🔧 Building dynamic graph for: {analysis.task_type}")
        
        workflow = StateGraph(MessagesState)
        
        # Add nodes for required agents
        for agent_type in analysis.required_agents:
            node_func = self._get_node_function(agent_type)
            workflow.add_node(agent_type.value, node_func)
        
        # Add HITL checkpoint nodes if needed
        hitl_nodes = []
        if self.coordinator.human_in_loop:
            for checkpoint in analysis.hitl_checkpoints:
                node_func = self._get_hitl_node_function(checkpoint)
                workflow.add_node(checkpoint.value, node_func)
                hitl_nodes.append(checkpoint.value)
        
        # Build edges based on agent sequence
        self._build_edges(workflow, analysis, hitl_nodes)
        
        # Compile with checkpointing if HITL
        if self.coordinator.human_in_loop and hitl_nodes:
            from langgraph.checkpoint.memory import MemorySaver
            compiled = workflow.compile(
                checkpointer=MemorySaver(),
                interrupt_before=hitl_nodes
            )
            logger.info(f"✅ Dynamic graph compiled WITH checkpointing ({len(hitl_nodes)} HITL points)")
        else:
            compiled = workflow.compile()
            logger.info(f"✅ Dynamic graph compiled WITHOUT checkpointing")
        
        return compiled
    
    def _build_analysis_prompt(self, query: str, context: Optional[Dict]) -> str:
        """Build prompt for LLM task analysis."""
        
        prompt = f"""Analyze this task and determine the optimal RAG workflow composition:

TASK: {query}

CONTEXT: {context if context else 'No additional context'}

Determine:

1. TASK TYPE (one of):
   - simple_qa: Quick factual question
   - code_implementation: Writing code
   - architecture_design: System design
   - api_integration: API integration
   - bug_fixing: Debugging
   - documentation: Writing docs
   - research: Deep research

2. COMPLEXITY (one of):
   - simple: Quick answer, minimal processing
   - medium: Standard workflow
   - complex: Deep analysis, multiple iterations

3. REQUIRED AGENTS (select needed agents):
   - query_analyst: Understand query intent
   - retrieval_specialist: Multi-source retrieval
   - re_ranker: Relevance scoring
   - quality_assurance: Quality checks
   - writer: Answer generation

4. HITL CHECKPOINTS (where human should review):
   - select_sources: Let user choose knowledge sources
   - review_query: Verify understanding
   - review_retrieval: Check retrieved sources
   - review_context: Approve context quality
   - review_draft: Review generated answer
   - final_approval: Final sign-off

5. KNOWLEDGE SOURCES (what to retrieve from):
   - architecture: Architecture docs
   - coding_guidelines: Coding standards
   - framework_docs: API documentation
   - agile: Project requirements
   - all: Everything

Provide your analysis in this format:

TASK_TYPE: <type>
COMPLEXITY: <level>
AGENTS: <comma-separated list>
HITL_POINTS: <comma-separated list or 'none'>
KNOWLEDGE_SOURCES: <comma-separated list>
ALLOW_REWRITE: <yes/no>
CONFIDENCE: <0-100>
REASONING: <brief explanation>
"""
        return prompt
    
    def _get_system_prompt(self) -> str:
        """System prompt for task analysis."""
        return """You are a meta-agent that analyzes tasks and designs optimal RAG workflows.

Your job is to determine:
- What type of task this is
- What agents are needed
- Where human review is valuable
- What knowledge sources to use

Be efficient: Don't over-engineer simple tasks.
Be thorough: Complex tasks need comprehensive processing.
Be strategic: Place HITL checkpoints at critical decision points.

Analyze the task and provide a clear, structured response."""
    
    def _parse_analysis(self, llm_response: str, query: str) -> TaskAnalysis:
        """Parse LLM response into TaskAnalysis structure."""
        
        lines = llm_response.split('\n')
        parsed = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                parsed[key.strip().lower().replace('_', '')] = value.strip()
        
        # Extract values with defaults
        task_type = parsed.get('tasktype', 'simple_qa')
        complexity = parsed.get('complexity', 'medium')
        
        # Parse agents
        agents_str = parsed.get('agents', 'query_analyst,retrieval_specialist,writer')
        required_agents = []
        for agent in agents_str.split(','):
            agent = agent.strip()
            if agent in ['query_analyst', 'retrieval_specialist', 're_ranker', 'quality_assurance', 'writer']:
                required_agents.append(AgentType(agent))
        
        # Parse HITL checkpoints
        hitl_str = parsed.get('hitlpoints', 'none')
        hitl_checkpoints = []
        if hitl_str.lower() != 'none':
            for checkpoint in hitl_str.split(','):
                checkpoint = checkpoint.strip()
                if checkpoint in ['select_sources', 'review_query', 'review_retrieval', 'review_context', 'review_draft', 'final_approval']:
                    hitl_checkpoints.append(HITLCheckpoint(checkpoint))
        
        # Parse knowledge sources
        knowledge_str = parsed.get('knowledgesources', 'all')
        knowledge_sources = [s.strip() for s in knowledge_str.split(',')]
        
        # Parse other fields
        allow_rewrite = parsed.get('allowrewrite', 'yes').lower() == 'yes'
        confidence = float(parsed.get('confidence', '80')) / 100
        reasoning = parsed.get('reasoning', 'Default analysis')
        
        return TaskAnalysis(
            task_type=task_type,
            complexity=complexity,
            estimated_steps=len(required_agents),
            required_agents=required_agents,
            agent_sequence=[a.value for a in required_agents],
            knowledge_sources=knowledge_sources,
            hitl_checkpoints=hitl_checkpoints,
            allow_rewrite=allow_rewrite,
            allow_iteration=True,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _default_analysis(self, query: str) -> TaskAnalysis:
        """Fallback analysis if LLM analysis fails."""
        
        logger.warning("⚠️ Using default task analysis (LLM analysis failed)")
        
        return TaskAnalysis(
            task_type="simple_qa",
            complexity="medium",
            estimated_steps=3,
            required_agents=[
                AgentType.QUERY_ANALYST,
                AgentType.RETRIEVAL_SPECIALIST,
                AgentType.WRITER
            ],
            agent_sequence=["query_analyst", "retrieval_specialist", "writer"],
            knowledge_sources=["all"],
            hitl_checkpoints=[],
            allow_rewrite=True,
            allow_iteration=True,
            confidence=0.5,
            reasoning="Default fallback composition"
        )
    
    def _get_node_function(self, agent_type: AgentType):
        """Get node function for agent type."""
        node_map = {
            AgentType.QUERY_ANALYST: self.coordinator._query_analyst_node,
            AgentType.RETRIEVAL_SPECIALIST: self.coordinator._retrieval_specialist_node,
            AgentType.RE_RANKER: self.coordinator._re_ranker_node,
            AgentType.QUALITY_ASSURANCE: self.coordinator._quality_assurance_node,
            AgentType.WRITER: self.coordinator._writer_node
        }
        return node_map[agent_type]
    
    def _get_hitl_node_function(self, checkpoint: HITLCheckpoint):
        """Get node function for HITL checkpoint."""
        hitl_map = {
            HITLCheckpoint.SELECT_SOURCES: self.coordinator._select_knowledge_sources_node,
            HITLCheckpoint.REVIEW_QUERY: self.coordinator._review_query_analysis_node,
            HITLCheckpoint.REVIEW_RETRIEVAL: self.coordinator._review_retrieval_results_node,
            HITLCheckpoint.REVIEW_CONTEXT: self.coordinator._review_ranked_context_node,
            HITLCheckpoint.REVIEW_DRAFT: self.coordinator._review_draft_answer_node,
            HITLCheckpoint.FINAL_APPROVAL: self.coordinator._final_approval_node
        }
        return hitl_map.get(checkpoint, lambda state: {"messages": []})
    
    def _build_edges(self, workflow: StateGraph, analysis: TaskAnalysis, hitl_nodes: List[str]):
        """Build edges based on agent sequence and HITL checkpoints."""
        
        # Simple linear flow with HITL checkpoints interleaved
        current_node = START
        
        for i, agent in enumerate(analysis.agent_sequence):
            # Connect previous to current agent
            workflow.add_edge(current_node, agent)
            current_node = agent
            
            # Check if there's a HITL checkpoint after this agent
            # For simplicity, we'll place HITL checkpoints after specific agents
            if self.coordinator.human_in_loop:
                if agent == "retrieval_specialist" and HITLCheckpoint.REVIEW_RETRIEVAL.value in hitl_nodes:
                    workflow.add_edge(current_node, HITLCheckpoint.REVIEW_RETRIEVAL.value)
                    current_node = HITLCheckpoint.REVIEW_RETRIEVAL.value
                
                if agent == "writer" and HITLCheckpoint.REVIEW_DRAFT.value in hitl_nodes:
                    workflow.add_edge(current_node, HITLCheckpoint.REVIEW_DRAFT.value)
                    current_node = HITLCheckpoint.REVIEW_DRAFT.value
        
        # Final edge to END
        workflow.add_edge(current_node, END)

