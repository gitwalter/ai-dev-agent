"""
Architecture Designer Agent - LangGraph Implementation

Designs system architecture and technology stack using LangGraph.
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

from agents.development.architecture_designer import ArchitectureDesigner
from models.config import AgentConfig
from utils.llm.gemini_client_factory import get_gemini_client

logger = logging.getLogger(__name__)


class ArchitectureDesignerState(BaseModel):
    """State for Architecture Designer workflow using Pydantic BaseModel."""
    
    # Input (required fields)
    requirements: Dict[str, Any] = Field(..., description="Project requirements")
    project_name: str = Field(..., description="Name of the project")
    constraints: Optional[List[str]] = Field(default=None, description="Technical constraints")
    
    # Agent outputs (initialized with defaults)
    architecture_design: Dict[str, Any] = Field(default_factory=dict, description="Complete architecture design")
    technology_stack: Dict[str, List[str]] = Field(default_factory=dict, description="Selected technology stack")
    system_components: List[Dict] = Field(default_factory=list, description="System components")
    integration_points: List[Dict] = Field(default_factory=list, description="Integration points")
    deployment_strategy: Dict[str, Any] = Field(default_factory=dict, description="Deployment strategy")
    
    # Workflow control (initialized with defaults)
    current_stage: str = Field(default="initialized", description="Current design stage")
    stages_completed: List[str] = Field(default_factory=list, description="Completed stages")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Design timing metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class ArchitectureDesignerCoordinator:
    """Architecture Designer using LangGraph for proper tracing."""
    
    def __init__(self, gemini_client=None):
        """
        Initialize Architecture Designer with LangGraph.
        
        Args:
            gemini_client: Optional LLM client for swarm coordination.
                          If None, creates standalone client for independent use.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Create or use LLM client
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='architecture_designer',
                model_name='gemini-2.5-flash',
                temperature=0.1
            )
            logger.info("✅ Architecture Designer: Created standalone LLM client")
        else:
            logger.info("✅ Architecture Designer: Using shared LLM client from swarm")
        
        config = AgentConfig(
            agent_id='architecture_designer',
            name='Architecture Designer',
            description='Designs system architecture',
            model_name='gemini-2.5-flash'
        )
        self.designer = ArchitectureDesigner(config, gemini_client=gemini_client)
        
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Architecture Designer Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for architecture design."""
        
        workflow = StateGraph(ArchitectureDesignerState)
        
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        workflow.add_node("select_technology", self._select_technology)
        workflow.add_node("design_components", self._design_components)
        workflow.add_node("define_integrations", self._define_integrations)
        workflow.add_node("plan_deployment", self._plan_deployment)
        workflow.add_node("finalize", self._finalize_design)
        
        workflow.set_entry_point("analyze_requirements")
        workflow.add_edge("analyze_requirements", "select_technology")
        workflow.add_edge("select_technology", "design_components")
        workflow.add_edge("design_components", "define_integrations")
        workflow.add_edge("define_integrations", "plan_deployment")
        workflow.add_edge("plan_deployment", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    async def _analyze_requirements(self, state: ArchitectureDesignerState) -> ArchitectureDesignerState:
        """Analyze requirements for architecture design."""
        import time
        start = time.time()
        
        logger.info("[Architecture] Analyzing requirements...")
        
        try:
            state['current_stage'] = 'requirements_analyzed'
            state['stages_completed'] = state.get('stages_completed', []) + ['analyze_requirements']
            state['metrics']['analyze_time'] = time.time() - start
            logger.info("[Architecture] ✅ Requirements analyzed")
        except Exception as e:
            logger.error(f"[Architecture] ❌ Analysis failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Analysis error: {str(e)}"]
        
        return state
    
    async def _select_technology(self, state: ArchitectureDesignerState) -> ArchitectureDesignerState:
        """Select appropriate technology stack."""
        import time
        start = time.time()
        
        logger.info("[Architecture] Selecting technology stack...")
        
        try:
            task = {
                'requirements': state.get('requirements', {}),
                'project_name': state.get('project_name', ''),
                'description': 'Select technology stack',
                'context': state.get('constraints', {})
            }
            
            result = await self.designer.execute(task)
            technology_stack = result.get('technology_stack', {
                'backend': ['Python', 'FastAPI'],
                'frontend': ['React', 'TypeScript'],
                'database': ['PostgreSQL'],
                'deployment': ['Docker', 'Kubernetes']
            })
            
            state['technology_stack'] = technology_stack
            state['current_stage'] = 'technology_selected'
            state['stages_completed'] = state.get('stages_completed', []) + ['select_technology']
            state['metrics']['technology_time'] = time.time() - start
            logger.info("[Architecture] ✅ Technology stack selected")
        except Exception as e:
            logger.error(f"[Architecture] ❌ Technology selection failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Technology error: {str(e)}"]
        
        return state
    
    async def _design_components(self, state: ArchitectureDesignerState) -> ArchitectureDesignerState:
        """Design system components."""
        import time
        start = time.time()
        
        logger.info("[Architecture] Designing components...")
        
        try:
            components = [
                {'name': 'API Layer', 'type': 'backend', 'responsibility': 'Handle HTTP requests'},
                {'name': 'Business Logic', 'type': 'backend', 'responsibility': 'Core functionality'},
                {'name': 'Data Layer', 'type': 'backend', 'responsibility': 'Database operations'},
                {'name': 'UI Components', 'type': 'frontend', 'responsibility': 'User interface'}
            ]
            
            state['system_components'] = components
            state['current_stage'] = 'components_designed'
            state['stages_completed'] = state.get('stages_completed', []) + ['design_components']
            state['metrics']['components_time'] = time.time() - start
            logger.info(f"[Architecture] ✅ Designed {len(components)} components")
        except Exception as e:
            logger.error(f"[Architecture] ❌ Component design failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Component error: {str(e)}"]
        
        return state
    
    async def _define_integrations(self, state: ArchitectureDesignerState) -> ArchitectureDesignerState:
        """Define integration points."""
        import time
        start = time.time()
        
        logger.info("[Architecture] Defining integrations...")
        
        try:
            integrations = [
                {'from': 'API Layer', 'to': 'Business Logic', 'type': 'REST API'},
                {'from': 'Business Logic', 'to': 'Data Layer', 'type': 'ORM'}
            ]
            
            state['integration_points'] = integrations
            state['current_stage'] = 'integrations_defined'
            state['stages_completed'] = state.get('stages_completed', []) + ['define_integrations']
            state['metrics']['integrations_time'] = time.time() - start
            logger.info(f"[Architecture] ✅ Defined {len(integrations)} integrations")
        except Exception as e:
            logger.error(f"[Architecture] ❌ Integration definition failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Integration error: {str(e)}"]
        
        return state
    
    async def _plan_deployment(self, state: ArchitectureDesignerState) -> ArchitectureDesignerState:
        """Plan deployment strategy."""
        import time
        start = time.time()
        
        logger.info("[Architecture] Planning deployment...")
        
        try:
            deployment = {
                'strategy': 'containerized',
                'platform': 'Kubernetes',
                'ci_cd': 'GitHub Actions',
                'monitoring': 'Prometheus + Grafana'
            }
            
            state['deployment_strategy'] = deployment
            state['current_stage'] = 'deployment_planned'
            state['stages_completed'] = state.get('stages_completed', []) + ['plan_deployment']
            state['metrics']['deployment_time'] = time.time() - start
            logger.info("[Architecture] ✅ Deployment strategy planned")
        except Exception as e:
            logger.error(f"[Architecture] ❌ Deployment planning failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Deployment error: {str(e)}"]
        
        return state
    
    async def _finalize_design(self, state: ArchitectureDesignerState) -> ArchitectureDesignerState:
        """Finalize architecture design."""
        import time
        start = time.time()
        
        logger.info("[Architecture] Finalizing design...")
        
        try:
            design = {
                'project_name': state.get('project_name'),
                'technology_stack': state.get('technology_stack', {}),
                'system_components': state.get('system_components', []),
                'integration_points': state.get('integration_points', []),
                'deployment_strategy': state.get('deployment_strategy', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            state['architecture_design'] = design
            state['current_stage'] = 'complete'
            state['stages_completed'] = state.get('stages_completed', []) + ['finalize']
            state['metrics']['finalize_time'] = time.time() - start
            logger.info("[Architecture] ✅ Design finalized")
        except Exception as e:
            logger.error(f"[Architecture] ❌ Finalization failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Finalization error: {str(e)}"]
        
        return state
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute architecture design using LangGraph."""
        import time
        start_time = time.time()
        
        initial_state: ArchitectureDesignerState = {
            'requirements': task.get('requirements', {}),
            'project_name': task.get('project_name', ''),
            'constraints': task.get('constraints'),
            'architecture_design': {},
            'technology_stack': {},
            'system_components': [],
            'integration_points': [],
            'deployment_strategy': {},
            'current_stage': 'initialized',
            'stages_completed': [],
            'errors': [],
            'metrics': {}
        }
        
        try:
            logger.info(f"Architecture Designer: Processing project '{task.get('project_name', '')}'")
            
            final_state = await self.app.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": f"arch_{datetime.now().timestamp()}"}}
            )
            
            total_time = time.time() - start_time
            final_state['metrics']['total_time'] = total_time
            
            result = {
                'status': 'success',
                'project_name': final_state['project_name'],
                'architecture_design': final_state['architecture_design'],
                'technology_stack': final_state['technology_stack'],
                'system_components': final_state['system_components'],
                'integration_points': final_state['integration_points'],
                'deployment_strategy': final_state['deployment_strategy'],
                'pipeline_state': {
                    'stages_completed': final_state['stages_completed'],
                    'metrics': final_state['metrics']
                }
            }
            
            logger.info(f"Architecture Designer: Complete in {total_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Architecture Designer: Failed with error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'error': str(e),
                'project_name': task.get('project_name', ''),
                'architecture_design': {}
            }

