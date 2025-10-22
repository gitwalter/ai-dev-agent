"""
Requirements Analyst Agent - LangGraph Implementation

Analyzes project requirements and generates comprehensive requirements documentation
using LangGraph for proper state management and tracing.
"""

import logging
from typing import Dict, Any, List, Annotated, Optional
from pydantic import BaseModel, Field
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available")

from agents.development.requirements_analyst import RequirementsAnalyst
from models.config import AgentConfig
from utils.llm.gemini_client_factory import get_gemini_client

logger = logging.getLogger(__name__)


class RequirementsAnalystState(BaseModel):
    """State for Requirements Analyst workflow using Pydantic BaseModel."""
    
    # Input (required fields)
    project_context: str = Field(..., description="Project description and context")
    project_name: str = Field(..., description="Name of the project")
    additional_details: Optional[Dict[str, Any]] = Field(default=None, description="Additional project details")
    
    # Agent outputs (initialized with defaults)
    requirements_analysis: Dict[str, Any] = Field(default_factory=dict, description="Complete requirements analysis")
    functional_requirements: List[Dict] = Field(default_factory=list, description="Functional requirements")
    non_functional_requirements: List[Dict] = Field(default_factory=list, description="Non-functional requirements")
    user_stories: List[Dict] = Field(default_factory=list, description="User stories")
    technical_constraints: List[str] = Field(default_factory=list, description="Technical constraints")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    
    # Workflow control (initialized with defaults)
    current_stage: str = Field(default="initialized", description="Current analysis stage")
    stages_completed: List[str] = Field(default_factory=list, description="Completed stages")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    
    # Metrics (automatically initialized as empty dict)
    metrics: Dict[str, float] = Field(default_factory=dict, description="Analysis timing metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class RequirementsAnalystCoordinator:
    """
    Requirements Analyst using LangGraph for proper tracing and state management.
    """
    
    def __init__(self, gemini_client=None):
        """
        Initialize Requirements Analyst with LangGraph.
        
        Args:
            gemini_client: Optional LLM client for swarm coordination.
                          If None, creates standalone client for independent use.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Create or use LLM client
        if gemini_client is None:
            # Standalone mode: Create own LLM client
            gemini_client = get_gemini_client(
                agent_name='requirements_analyst',
                model_name='gemini-2.5-flash',
                temperature=0.1
            )
            logger.info("✅ Requirements Analyst: Created standalone LLM client")
        else:
            # Swarm mode: Use shared/injected client
            logger.info("✅ Requirements Analyst: Using shared LLM client from swarm")
        
        # Initialize the underlying agent
        config = AgentConfig(
            agent_id='requirements_analyst',
            name='Requirements Analyst',
            description='Analyzes project requirements',
            model_name='gemini-2.5-flash'
        )
        self.analyst = RequirementsAnalyst(config, gemini_client=gemini_client)
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Requirements Analyst Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for requirements analysis."""
        
        workflow = StateGraph(RequirementsAnalystState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_requirements)
        workflow.add_node("generate_user_stories", self._generate_user_stories)
        workflow.add_node("identify_constraints", self._identify_constraints)
        workflow.add_node("assess_risks", self._assess_risks)
        workflow.add_node("finalize", self._finalize_analysis)
        
        # Define workflow edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "generate_user_stories")
        workflow.add_edge("generate_user_stories", "identify_constraints")
        workflow.add_edge("identify_constraints", "assess_risks")
        workflow.add_edge("assess_risks", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    async def _analyze_requirements(self, state: RequirementsAnalystState) -> RequirementsAnalystState:
        """Analyze project requirements."""
        import time
        start = time.time()
        
        # Initialize metrics if not present
        if 'metrics' not in state or state['metrics'] is None:
            state['metrics'] = {}
        
        logger.info("[Requirements] Analyzing project requirements...")
        
        try:
            # Call underlying agent
            task = {
                'project_context': state['project_context'],
                'project_name': state['project_name'],
                'description': state['project_context'],
                'context': state.get('additional_details', {})
            }
            
            result = await self.analyst.execute(task)
            
            # Extract requirements
            analysis = result.get('requirements_analysis', {})
            
            state['functional_requirements'] = analysis.get('functional_requirements', [])
            state['non_functional_requirements'] = analysis.get('non_functional_requirements', [])
            state['current_stage'] = 'requirements_analyzed'
            state['stages_completed'] = state.get('stages_completed', []) + ['analyze']
            state['metrics']['analyze_time'] = time.time() - start
            
            logger.info(f"[Requirements] ✅ Analyzed {len(state['functional_requirements'])} functional requirements")
            
        except Exception as e:
            logger.error(f"[Requirements] ❌ Analysis failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Analysis error: {str(e)}"]
        
        return state
    
    async def _generate_user_stories(self, state: RequirementsAnalystState) -> RequirementsAnalystState:
        """Generate user stories from requirements."""
        import time
        start = time.time()
        
        # Ensure metrics exists
        if 'metrics' not in state or state['metrics'] is None:
            state['metrics'] = {}
        
        logger.info("[Requirements] Generating user stories...")
        
        try:
            # Generate user stories based on functional requirements
            user_stories = []
            for req in state.get('functional_requirements', []):
                story = {
                    'id': f"US-{len(user_stories) + 1:03d}",
                    'title': req.get('title', ''),
                    'requirement_id': req.get('id', ''),
                    'priority': req.get('priority', 'medium')
                }
                user_stories.append(story)
            
            state['user_stories'] = user_stories
            state['current_stage'] = 'user_stories_generated'
            state['stages_completed'] = state.get('stages_completed', []) + ['generate_user_stories']
            state['metrics']['user_stories_time'] = time.time() - start
            
            logger.info(f"[Requirements] ✅ Generated {len(user_stories)} user stories")
            
        except Exception as e:
            logger.error(f"[Requirements] ❌ User story generation failed: {e}")
            state['errors'] = state.get('errors', []) + [f"User story error: {str(e)}"]
        
        return state
    
    async def _identify_constraints(self, state: RequirementsAnalystState) -> RequirementsAnalystState:
        """Identify technical and business constraints."""
        import time
        start = time.time()
        
        # Ensure metrics exists
        if 'metrics' not in state or state['metrics'] is None:
            state['metrics'] = {}
        
        logger.info("[Requirements] Identifying constraints...")
        
        try:
            # Extract constraints from project context
            constraints = []
            project_context = state.get('project_context', '').lower()
            
            # Check for common technical constraints
            if 'python' in project_context:
                constraints.append('Python programming language')
            if 'web' in project_context or 'api' in project_context:
                constraints.append('Web/API development framework required')
            if 'database' in project_context:
                constraints.append('Database integration required')
            
            state['technical_constraints'] = constraints
            state['current_stage'] = 'constraints_identified'
            state['stages_completed'] = state.get('stages_completed', []) + ['identify_constraints']
            state['metrics']['constraints_time'] = time.time() - start
            
            logger.info(f"[Requirements] ✅ Identified {len(constraints)} constraints")
            
        except Exception as e:
            logger.error(f"[Requirements] ❌ Constraint identification failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Constraint error: {str(e)}"]
        
        return state
    
    async def _assess_risks(self, state: RequirementsAnalystState) -> RequirementsAnalystState:
        """Assess project risks."""
        import time
        start = time.time()
        
        # Ensure metrics exists
        if 'metrics' not in state or state['metrics'] is None:
            state['metrics'] = {}
        
        logger.info("[Requirements] Assessing risks...")
        
        try:
            # Identify potential risks
            risks = []
            
            if len(state.get('functional_requirements', [])) > 20:
                risks.append('High complexity project with many requirements')
            
            if not state.get('technical_constraints'):
                risks.append('Insufficient technical constraints specified')
            
            state['risks'] = risks
            state['current_stage'] = 'risks_assessed'
            state['stages_completed'] = state.get('stages_completed', []) + ['assess_risks']
            state['metrics']['risks_time'] = time.time() - start
            
            logger.info(f"[Requirements] ✅ Assessed {len(risks)} risks")
            
        except Exception as e:
            logger.error(f"[Requirements] ❌ Risk assessment failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Risk assessment error: {str(e)}"]
        
        return state
    
    async def _finalize_analysis(self, state: RequirementsAnalystState) -> RequirementsAnalystState:
        """Finalize requirements analysis."""
        import time
        start = time.time()
        
        logger.info("[Requirements] Finalizing analysis...")
        
        try:
            # Compile complete analysis
            analysis = {
                'project_name': state.get('project_name'),
                'functional_requirements': state.get('functional_requirements', []),
                'non_functional_requirements': state.get('non_functional_requirements', []),
                'user_stories': state.get('user_stories', []),
                'technical_constraints': state.get('technical_constraints', []),
                'risks': state.get('risks', []),
                'stages_completed': state.get('stages_completed', []),
                'timestamp': datetime.now().isoformat()
            }
            
            state['requirements_analysis'] = analysis
            state['current_stage'] = 'complete'
            state['stages_completed'] = state.get('stages_completed', []) + ['finalize']
            
            # Initialize metrics if not present
            if 'metrics' not in state or state['metrics'] is None:
                state['metrics'] = {}
            state['metrics']['finalize_time'] = time.time() - start
            
            logger.info("[Requirements] ✅ Analysis finalized")
            
        except Exception as e:
            logger.error(f"[Requirements] ❌ Finalization failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Finalization error: {str(e)}"]
        
        return state
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute requirements analysis using LangGraph.
        
        Args:
            task: Dictionary with:
                - project_context: str
                - project_name: str
                - additional_details: dict (optional)
                
        Returns:
            Complete requirements analysis result
        """
        import time
        start_time = time.time()
        
        # Initialize state
        initial_state: RequirementsAnalystState = {
            'project_context': task.get('project_context', ''),
            'project_name': task.get('project_name', ''),
            'additional_details': task.get('additional_details'),
            'requirements_analysis': {},
            'functional_requirements': [],
            'non_functional_requirements': [],
            'user_stories': [],
            'technical_constraints': [],
            'risks': [],
            'current_stage': 'initialized',
            'stages_completed': [],
            'errors': [],
            'metrics': {}
        }
        
        try:
            # Execute workflow
            logger.info(f"Requirements Analyst: Processing project '{task.get('project_name', '')}'")
            
            final_state = await self.app.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": f"req_{datetime.now().timestamp()}"}}
            )
            
            total_time = time.time() - start_time
            final_state['metrics']['total_time'] = total_time
            
            # Build result
            result = {
                'status': 'success',
                'project_name': final_state['project_name'],
                'requirements_analysis': final_state['requirements_analysis'],
                'functional_requirements': final_state['functional_requirements'],
                'non_functional_requirements': final_state['non_functional_requirements'],
                'user_stories': final_state['user_stories'],
                'technical_constraints': final_state['technical_constraints'],
                'risks': final_state['risks'],
                'pipeline_state': {
                    'stages_completed': final_state['stages_completed'],
                    'metrics': final_state['metrics']
                }
            }
            
            logger.info(f"Requirements Analyst: Complete in {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Requirements Analyst: Failed with error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'error': str(e),
                'project_name': task.get('project_name', ''),
                'requirements_analysis': {}
            }

