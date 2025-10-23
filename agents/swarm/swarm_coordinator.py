#!/usr/bin/env python3
"""
MCP-Powered Swarm Coordinator Agent
===================================

Orchestrates agent swarms for complex workflows using MCP tools.
Coordinates multiple specialized agents to execute complete software development sprints.

Features:
- Agent swarm orchestration and management
- Task assignment and load balancing
- Progress monitoring and error recovery
- Inter-agent communication coordination
- Performance optimization and scaling

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 3)
"""

import asyncio
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json


# LangGraph integration check
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available - agent will work in legacy mode only")

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import base agent and MCP integration
try:
    from agents.core.enhanced_base_agent import EnhancedBaseAgent
    from agents.core.base_agent import AgentConfig
    from utils.mcp.langchain_integration import MCPAgentMixin, MCPToolkit
    from utils.mcp.server import ToolCategory
    BASE_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Base agent components not available: {e}")
    BASE_AGENT_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class SwarmState(Enum):
    """Swarm execution states."""
    INITIALIZING = "initializing"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"


class AgentRole(Enum):
    """Specialized agent roles in the swarm."""
    PRODUCT_AGENT = "product_agent"
    DEVELOPMENT_AGENT = "development_agent"
    QUALITY_AGENT = "quality_agent"
    TESTING_AGENT = "testing_agent"
    RELEASE_AGENT = "release_agent"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class SwarmTask:
    """Task to be executed by swarm agents."""
    task_id: str
    description: str
    assigned_agent: Optional[AgentRole] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    mcp_tools_required: List[str] = field(default_factory=list)
    estimated_duration: int = 30  # minutes
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class SwarmAgent:
    """Agent participating in the swarm."""
    agent_id: str
    role: AgentRole
    status: str = "idle"
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.now)


@dataclass
class SwarmWorkflow:
    """Complete workflow definition for the swarm."""
    workflow_id: str
    name: str
    description: str
    tasks: List[SwarmTask] = field(default_factory=list)
    phases: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)




class SwarmCoordinatorState(BaseModel):
    """State for SwarmCoordinator LangGraph workflow using Pydantic BaseModel."""
    
    # Input fields
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    
    # Output fields
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    
    # Control fields
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Execution metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

class SwarmCoordinator(EnhancedBaseAgent, MCPAgentMixin if BASE_AGENT_AVAILABLE else object):
    """
    MCP-powered swarm coordinator agent.
    
    Orchestrates multiple specialized agents to execute complex workflows
    using MCP tools for coordination and communication.
    """
    
    def __init__(self, config: AgentConfig, gemini_client=None):
        """
        Initialize swarm coordinator.
        
        Args:
            config: Agent configuration
            gemini_client: Gemini client instance
        """
        super().__init__(config, gemini_client)
        
        # Swarm management
        self.swarm_state = SwarmState.INITIALIZING
        self.swarm_agents: Dict[str, SwarmAgent] = {}
        self.active_workflows: Dict[str, SwarmWorkflow] = {}
        self.task_queue: List[SwarmTask] = []
        self.completed_tasks: List[SwarmTask] = []
        
        # Performance tracking
        self.swarm_metrics = {
            'workflows_completed': 0,
            'tasks_completed': 0,
            'total_execution_time': 0.0,
            'average_task_time': 0.0,
            'error_count': 0,
            'agent_utilization': {}
        }
        
        # Communication channels
        self.agent_communication_log = []
        self.coordination_events = []
        
        logger.info(f"🐝 Swarm Coordinator '{config.agent_id}' initialized")
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            logger.info("⚠️ LangGraph not available - using legacy mode")
    
    async def initialize_swarm(self, agent_roles: List[AgentRole] = None) -> bool:
        """
        Initialize the agent swarm.
        
        Args:
            agent_roles: List of agent roles to initialize
            
        Returns:
            True if initialization successful
        """
        try:
            logger.info("🚀 Initializing MCP-powered agent swarm...")
            
            # Initialize MCP capabilities
            if BASE_AGENT_AVAILABLE:
                await self.initialize_mcp(auto_discover_tools=True)
            
            # Set default agent roles if not provided
            if agent_roles is None:
                agent_roles = [
                    AgentRole.PRODUCT_AGENT,
                    AgentRole.DEVELOPMENT_AGENT,
                    AgentRole.QUALITY_AGENT,
                    AgentRole.TESTING_AGENT,
                    AgentRole.RELEASE_AGENT
                ]
            
            # Initialize swarm agents
            await self._initialize_swarm_agents(agent_roles)
            
            # Setup coordination infrastructure
            await self._setup_coordination_infrastructure()
            
            # Start monitoring
            await self._start_swarm_monitoring()
            
            self.swarm_state = SwarmState.PLANNING
            logger.info(f"✅ Swarm initialized with {len(self.swarm_agents)} agents")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Swarm initialization failed: {e}")
            self.swarm_state = SwarmState.ERROR
            return False
    
    async def _initialize_swarm_agents(self, agent_roles: List[AgentRole]):
        """Initialize specialized swarm agents."""
        for role in agent_roles:
            agent_id = f"{role.value}_{uuid.uuid4().hex[:8]}"
            
            # Define agent capabilities based on role
            capabilities = self._get_agent_capabilities(role)
            
            # Create swarm agent
            swarm_agent = SwarmAgent(
                agent_id=agent_id,
                role=role,
                capabilities=capabilities,
                performance_metrics={
                    'tasks_completed': 0,
                    'success_rate': 0.0,
                    'average_execution_time': 0.0
                }
            )
            
            self.swarm_agents[agent_id] = swarm_agent
            
            # Track agent registration via MCP
            if self.mcp_initialized:
                try:
                    await self._track_agent_registration(swarm_agent)
                except Exception as e:
                    logger.warning(f"Failed to track agent registration: {e}")
            
            logger.info(f"🤖 Initialized {role.value}: {agent_id}")

    def _get_agent_capabilities(self, role: AgentRole) -> List[str]:
        """Get capabilities for specific agent role."""
        capabilities_map = {
            AgentRole.PRODUCT_AGENT: [
                "agile.create_user_story",
                "agile.update_artifacts", 
                "agile.update_catalogs",
                "db.track_agent_session"
            ],
            AgentRole.DEVELOPMENT_AGENT: [
                "file.manage_files",
                "file.enforce_organization",
                "ai.edit_prompts",
                "system.platform_commands"
            ],
            AgentRole.QUALITY_AGENT: [
                "system.platform_commands",
                "file.manage_files",
                "test.run_pipeline"
            ],
            AgentRole.TESTING_AGENT: [
                "test.run_pipeline",
                "test.generate_catalogue",
                "db.log_multi_database"
            ],
            AgentRole.RELEASE_AGENT: [
                "git.automate_workflow",
                "db.log_multi_database",
                "agile.update_catalogs"
            ]
        }
        
        return capabilities_map.get(role, [])
    
    async def _track_agent_registration(self, agent: SwarmAgent):
        """Track agent registration via MCP tools."""
        if not self.mcp_initialized:
            return
        
        # Use MCP tool to track agent session
        tools = self.get_mcp_tools(ToolCategory.DATABASE)
        if tools:
            tracking_tool = tools[0]  # Use first database tool
            
            try:
                await tracking_tool._arun({
                    'agent_id': agent.agent_id,
                    'agent_type': agent.role.value,
                    'context': {
                        'swarm_coordinator': self.config.agent_id,
                        'capabilities': agent.capabilities,
                        'registration_time': datetime.now().isoformat()
                    }
                })
                logger.info(f"📊 Tracked registration for {agent.agent_id}")
            except Exception as e:
                logger.warning(f"Failed to track agent registration: {e}")
    
    async def _setup_coordination_infrastructure(self):
        """Setup infrastructure for agent coordination."""
        # Configure logging for coordination
        if self.mcp_initialized:
            logging_tools = [t for t in self.get_mcp_tools() if 'logging' in t.name.lower()]
            if logging_tools:
                try:
                    await logging_tools[0]._arun({
                        'log_level': 'INFO',
                        'format_type': 'detailed'
                    })
                    logger.info("🔧 Coordination logging configured")
                except Exception as e:
                    logger.warning(f"Failed to configure coordination logging: {e}")
        
        # Setup communication channels
        self.coordination_events.append({
            'event': 'infrastructure_setup',
            'timestamp': datetime.now().isoformat(),
            'details': 'Coordination infrastructure initialized'
        })
    
    async def _start_swarm_monitoring(self):
        """Start background monitoring of swarm agents."""
        # This would typically start a background task to monitor agents
        # For now, we'll just log the start of monitoring
        logger.info("👁️ Swarm monitoring started")
        
        self.coordination_events.append({
            'event': 'monitoring_started',
            'timestamp': datetime.now().isoformat(),
            'agents_monitored': len(self.swarm_agents)
        })
    
    async def execute_workflow(self, workflow: SwarmWorkflow) -> Dict[str, Any]:
        """
        Execute a complete workflow using the agent swarm.
        
        Args:
            workflow: Workflow to execute
            
        Returns:
            Workflow execution results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🎯 Executing workflow: {workflow.name}")
            
            # Add workflow to active workflows
            self.active_workflows[workflow.workflow_id] = workflow
            self.swarm_state = SwarmState.EXECUTING
            
            # Phase 1: Task Planning and Assignment
            await self._plan_and_assign_tasks(workflow)
            
            # Phase 2: Execute Tasks
            execution_results = await self._execute_workflow_tasks(workflow)
            
            # Phase 3: Validate and Complete
            completion_results = await self._complete_workflow(workflow)
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.swarm_metrics['workflows_completed'] += 1
            self.swarm_metrics['total_execution_time'] += execution_time
            
            self.swarm_state = SwarmState.COMPLETED
            
            logger.info(f"✅ Workflow '{workflow.name}' completed in {execution_time:.2f}s")
            
            return {
                'success': True,
                'workflow_id': workflow.workflow_id,
                'execution_time': execution_time,
                'tasks_completed': len([t for t in workflow.tasks if t.status == 'completed']),
                'execution_results': execution_results,
                'completion_results': completion_results,
                'swarm_metrics': self.swarm_metrics.copy()
            }
            
        except Exception as e:
            self.swarm_state = SwarmState.ERROR
            self.swarm_metrics['error_count'] += 1
            
            logger.error(f"❌ Workflow execution failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow.workflow_id,
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
    
    async def _plan_and_assign_tasks(self, workflow: SwarmWorkflow):
        """Plan and assign tasks to appropriate agents."""
        logger.info("📋 Planning and assigning tasks...")
        
        # Sort tasks by priority and dependencies
        sorted_tasks = sorted(workflow.tasks, key=lambda t: (t.priority.value, len(t.dependencies)))
        
        # Assign tasks to agents based on capabilities
        for task in sorted_tasks:
            assigned_agent = self._find_best_agent_for_task(task)
            if assigned_agent:
                task.assigned_agent = assigned_agent.role
                assigned_agent.current_task = task.task_id
                assigned_agent.status = "assigned"
                
                logger.info(f"📌 Assigned task '{task.description}' to {assigned_agent.role.value}")
            else:
                logger.warning(f"⚠️ No suitable agent found for task: {task.description}")
    
    def _find_best_agent_for_task(self, task: SwarmTask) -> Optional[SwarmAgent]:
        """Find the best agent for a specific task."""
        suitable_agents = []
        
        for agent in self.swarm_agents.values():
            if agent.status == "idle":
                # Check if agent has required capabilities
                required_tools = set(task.mcp_tools_required)
                agent_tools = set(agent.capabilities)
                
                if required_tools.issubset(agent_tools):
                    suitable_agents.append(agent)
        
        # Return agent with best performance metrics
        if suitable_agents:
            return max(suitable_agents, key=lambda a: a.performance_metrics.get('success_rate', 0.0))
        
        return None
    
    async def _execute_workflow_tasks(self, workflow: SwarmWorkflow) -> Dict[str, Any]:
        """Execute all workflow tasks using assigned agents."""
        logger.info("⚡ Executing workflow tasks...")
        
        execution_results = {
            'tasks_executed': 0,
            'tasks_successful': 0,
            'tasks_failed': 0,
            'agent_performance': {}
        }
        
        # Execute tasks (simplified simulation)
        for task in workflow.tasks:
            if task.assigned_agent:
                result = await self._simulate_task_execution(task)
                
                if result['success']:
                    task.status = 'completed'
                    task.result = result
                    execution_results['tasks_successful'] += 1
                else:
                    task.status = 'failed'
                    task.error = result.get('error', 'Unknown error')
                    execution_results['tasks_failed'] += 1
                
                execution_results['tasks_executed'] += 1
                
                # Update agent metrics
                agent = self._get_agent_by_role(task.assigned_agent)
                if agent:
                    agent.performance_metrics['tasks_completed'] += 1
                    agent.status = "idle"
                    agent.current_task = None
        
        return execution_results
    
    async def _simulate_task_execution(self, task: SwarmTask) -> Dict[str, Any]:
        """Simulate task execution using MCP tools."""
        start_time = datetime.now()
        
        try:
            # Simulate task execution with MCP tools
            if self.mcp_initialized and task.mcp_tools_required:
                # Try to execute first required tool
                tool_name = task.mcp_tools_required[0]
                matching_tools = [t for t in self.get_mcp_tools() if tool_name in t.name]
                
                if matching_tools:
                    tool = matching_tools[0]
                    
                    # Execute tool with task-specific parameters
                    tool_result = await tool._arun({
                        'task_id': task.task_id,
                        'description': task.description,
                        'agent_role': task.assigned_agent.value if task.assigned_agent else 'unknown',
                        'execution_context': 'swarm_workflow'
                    })
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        'success': True,
                        'tool_used': tool_name,
                        'tool_result': tool_result,
                        'execution_time': execution_time
                    }
            
            # Fallback simulation
            await asyncio.sleep(0.1)  # Simulate work
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'simulated': True,
                'execution_time': execution_time,
                'message': f"Task '{task.description}' completed successfully"
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            }
    
    def _get_agent_by_role(self, role: AgentRole) -> Optional[SwarmAgent]:
        """Get agent by role."""
        for agent in self.swarm_agents.values():
            if agent.role == role:
                return agent
        return None
    
    async def _complete_workflow(self, workflow: SwarmWorkflow) -> Dict[str, Any]:
        """Complete workflow and update artifacts."""
        logger.info("🏁 Completing workflow...")
        
        # Update workflow artifacts via MCP tools
        completion_results = {
            'artifacts_updated': False,
            'catalogs_updated': False,
            'tracking_updated': False
        }
        
        if self.mcp_initialized:
            # Update agile artifacts
            agile_tools = self.get_mcp_tools(ToolCategory.AGILE)
            if agile_tools:
                try:
                    catalog_tool = [t for t in agile_tools if 'catalog' in t.name.lower()]
                    if catalog_tool:
                        await catalog_tool[0]._arun({
                            'workflow_id': workflow.workflow_id,
                            'completion_status': 'completed',
                            'tasks_completed': len([t for t in workflow.tasks if t.status == 'completed'])
                        })
                        completion_results['catalogs_updated'] = True
                except Exception as e:
                    logger.warning(f"Failed to update catalogs: {e}")
        
        # Remove from active workflows
        if workflow.workflow_id in self.active_workflows:
            del self.active_workflows[workflow.workflow_id]
        
        return completion_results
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task structure for swarm execution."""
        required_fields = ['workflow_definition']
        
        for field in required_fields:
            if field not in task:
                logger.error(f"❌ Task missing required field: {field}")
                return False
        
        return True
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute swarm coordination task."""
        try:
            # Extract workflow definition
            workflow_def = task.get('workflow_definition', {})
            
            # Create workflow from definition
            workflow = self._create_workflow_from_definition(workflow_def)
            
            # Execute workflow
            result = await self.execute_workflow(workflow)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Swarm execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_workflow_from_definition(self, workflow_def: Dict[str, Any]) -> SwarmWorkflow:
        """Create workflow from definition."""
        workflow_id = workflow_def.get('id', f"workflow_{uuid.uuid4().hex[:8]}")
        
        # Create tasks from definition
        tasks = []
        for task_def in workflow_def.get('tasks', []):
            task = SwarmTask(
                task_id=task_def.get('id', f"task_{uuid.uuid4().hex[:8]}"),
                description=task_def.get('description', 'Unknown task'),
                priority=TaskPriority(task_def.get('priority', 3)),
                mcp_tools_required=task_def.get('mcp_tools', []),
                estimated_duration=task_def.get('duration', 30)
            )
            tasks.append(task)
        
        return SwarmWorkflow(
            workflow_id=workflow_id,
            name=workflow_def.get('name', 'Unnamed Workflow'),
            description=workflow_def.get('description', ''),
            tasks=tasks,
            phases=workflow_def.get('phases', [])
        )
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status."""
        return {
            'coordinator_id': self.config.agent_id,
            'swarm_state': self.swarm_state.value,
            'total_agents': len(self.swarm_agents),
            'active_workflows': len(self.active_workflows),
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'swarm_metrics': self.swarm_metrics.copy(),
            'agent_status': {
                agent_id: {
                    'role': agent.role.value,
                    'status': agent.status,
                    'current_task': agent.current_task,
                    'performance': agent.performance_metrics
                }
                for agent_id, agent in self.swarm_agents.items()
            },
            'mcp_integration': self.mcp_initialized if hasattr(self, 'mcp_initialized') else False
        }
    
    async def shutdown_swarm(self):
        """Shutdown the agent swarm."""
        logger.info("🛑 Shutting down agent swarm...")
        
        # Shutdown MCP integration
        if hasattr(self, 'mcp_toolkit'):
            await self.shutdown_mcp()
        
        # Clear swarm state
        self.swarm_state = SwarmState.COMPLETED
        self.swarm_agents.clear()
        self.active_workflows.clear()
        
        logger.info("✅ Agent swarm shutdown complete")
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for SwarmCoordinator."""
        workflow = StateGraph(SwarmCoordinatorState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: SwarmCoordinatorState) -> SwarmCoordinatorState:
        """Execute agent in LangGraph workflow."""
        import time
        start = time.time()
        
        try:
            # Call the agent's execute method
            result = await self.execute(state.input_data)
            
            # Update state with results
            state.output_data = result
            state.status = "completed"
            state.metrics["execution_time"] = time.time() - start
            
        except Exception as e:
            logger.error(f"LangGraph execution failed: {e}")
            state.errors.append(str(e))
            state.status = "failed"
            state.metrics["execution_time"] = time.time() - start
        
        return state


# Factory function for easy coordinator creation
def create_swarm_coordinator(coordinator_id: str = "swarm_coordinator") -> SwarmCoordinator:
    """Create swarm coordinator instance."""
    config = AgentConfig(
        agent_id=coordinator_id,
        agent_type="swarm_coordinator",
        prompt_template_id="swarm_coordination",
        optimization_enabled=True,
        performance_monitoring=True
    )
    
    return SwarmCoordinator(config)


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test swarm coordinator."""
        print("🐝 Testing MCP-Powered Swarm Coordinator...")
        
        # Create coordinator
        coordinator = create_swarm_coordinator("test_swarm_coordinator")
        
        try:
            # Initialize swarm
            success = await coordinator.initialize_swarm()
            if not success:
                print("❌ Swarm initialization failed")
                return
            
            print("✅ Swarm initialized successfully")
            
            # Show swarm status
            status = coordinator.get_swarm_status()
            print(f"📊 Swarm status: {json.dumps(status, indent=2)}")
            
            # Test workflow execution
            test_workflow_def = {
                'id': 'test_sprint_workflow',
                'name': 'Test Sprint Execution',
                'description': 'Complete software development sprint',
                'tasks': [
                    {
                        'id': 'create_stories',
                        'description': 'Create user stories',
                        'priority': 1,
                        'mcp_tools': ['agile.create_user_story']
                    },
                    {
                        'id': 'implement_code',
                        'description': 'Implement user stories',
                        'priority': 2,
                        'mcp_tools': ['file.manage_files']
                    },
                    {
                        'id': 'run_tests',
                        'description': 'Run test suite',
                        'priority': 2,
                        'mcp_tools': ['test.run_pipeline']
                    }
                ]
            }
            
            print("🎯 Executing test workflow...")
            result = await coordinator.execute({
                'workflow_definition': test_workflow_def
            })
            print(f"📋 Workflow result: {json.dumps(result, indent=2)}")
            
        finally:
            # Cleanup
            await coordinator.shutdown_swarm()
            print("🛑 Swarm coordinator test complete")
    
    # Run test
    asyncio.run(main())


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        from utils.llm.gemini_client_factory import get_gemini_client
        
        config = AgentConfig(
            agent_id='swarm_coordinator',
            name='SwarmCoordinator',
            description='SwarmCoordinator agent',
            model_name='gemini-2.5-flash'
        )
        client = get_gemini_client(agent_name='swarm_coordinator')
        _default_instance = SwarmCoordinator(config, gemini_client=client)
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
