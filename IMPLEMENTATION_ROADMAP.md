# Implementation Roadmap: Supervisor-Swarm Hybrid Architecture

## Overview

This roadmap provides a detailed, step-by-step implementation plan for transitioning our current LangGraph-based agent system to the hybrid Supervisor-Swarm architecture. The implementation will be done incrementally to minimize risk and ensure system stability.

## Current State Assessment (Updated)

### What We Have ✅
- ✅ LangGraph workflow foundation
- ✅ Basic agent node factory with 3 agents (requirements, architecture, code generator)
- ✅ Basic state management with TypedDict
- ✅ Comprehensive test suite structure
- ✅ Pydantic models for agent outputs
- ✅ Import error fixes completed

### What's Partially Implemented 🔄
- 🔄 Agent node factory (only 3 of 7 agents implemented)
- 🔄 Workflow graph (missing START edges and proper routing)
- 🔄 Test data structure validation (Pydantic validation errors)
- 🔄 Async/await implementation (some functions not properly async)

### What We Need to Add ❌
- ❌ Missing agent nodes (test generator, code reviewer, security analyst, documentation generator)
- ❌ Supervisor layer (Project Manager, Quality Control, Task Router)
- ❌ Handoff system for agent collaboration
- ❌ Enhanced state management
- ❌ Hybrid workflow graph
- ❌ Quality validation system
- ❌ MCP server integration for external tool access

## Immediate Priority: Fix Current Issues (Week 1)

### Step 1.1: Fix Pydantic Validation Issues ✅ COMPLETED

**Issue**: Test data doesn't match expected Pydantic model structure
**Files Fixed**: 
- ✅ `tests/langgraph/unit/test_agent_nodes.py` - Updated test data to match actual Pydantic model fields
- ✅ Fixed `RequirementsAnalysisOutput` test data structure
- ✅ Fixed `ArchitectureDesignOutput` test data structure
- ✅ Fixed `TestGenerationOutput` test data structure
- ✅ Ensured all required fields are provided in test mocks

### Step 1.2: Complete Missing Agent Nodes ✅ COMPLETED

**Current Status**: All 7 agents now implemented
**Added Agents**:
- ✅ Test Generator Node
- ✅ Code Reviewer Node  
- ✅ Security Analyst Node
- ✅ Documentation Generator Node

**File**: `langgraph_workflow_manager.py`

**Implementation Completed**:
```python
def create_test_generator_node(self) -> Callable[[AgentState], AgentState]:
    """Create a test generation node."""
    # ✅ Implementation completed

def create_code_reviewer_node(self) -> Callable[[AgentState], AgentState]:
    """Create a code review node."""
    # ✅ Implementation completed

def create_security_analyst_node(self) -> Callable[[AgentState], AgentState]:
    """Create a security analysis node."""
    # ✅ Implementation completed

def create_documentation_generator_node(self) -> Callable[[AgentState], AgentState]:
    """Create a documentation generation node."""
    # ✅ Implementation completed
```

### Step 1.3: Fix Workflow Graph Issues ✅ COMPLETED

**Issue**: Missing START edges and proper routing
**File**: `langgraph_workflow.py`

**Actions Completed**:
- ✅ Added START edge to first node
- ✅ Implemented proper conditional routing
- ✅ Added all missing agent nodes to workflow
- ✅ Added proper error handling for workflow execution

### Step 1.4: Fix Async/Await Issues ✅ COMPLETED

**Issue**: Some functions are not properly async
**Files Fixed**:
- ✅ `langgraph_workflow_manager.py` - Made all agent nodes properly async
- ✅ Test files with async/await patterns updated
- ✅ Updated workflow execution to handle async properly

## Phase 1: Foundation Implementation (Week 1-2)

### Step 1.5: Create Supervisor Base Classes ✅ COMPLETED

**File**: `agents/supervisor/base_supervisor.py`

**Status**: ✅ Completed
**Implementation**: Created comprehensive base supervisor classes with:
- ✅ BaseSupervisor abstract class with quality validation
- ✅ SupervisorConfig for configuration management
- ✅ Decision logging and performance metrics
- ✅ Escalation handling framework
- ✅ Quality assessment framework

### Step 1.6: Implement Project Manager Supervisor ✅ COMPLETED

**File**: `agents/supervisor/project_manager_supervisor.py`

**Status**: ✅ Completed
**Implementation**: Created Project Manager Supervisor with:
- ✅ Workflow orchestration capabilities
- ✅ Task breakdown and prioritization
- ✅ Resource allocation decisions
- ✅ Quality gate management
- ✅ Escalation handling
- ✅ Comprehensive decision-making framework

### Step 1.7: Implement Quality Control Supervisor

**File**: `agents/supervisor/quality_control_supervisor.py`

```python
#!/usr/bin/env python3
"""
Quality Control Supervisor for validating agent outputs.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_supervisor import BaseSupervisor, SupervisorConfig
from utils.structured_outputs import (
    RequirementsAnalysisOutput, ArchitectureDesignOutput, 
    CodeGenerationOutput, ValidationResult
)


class QualityControlSupervisor(BaseSupervisor):
    """Ensures all outputs meet quality standards."""
    
    def __init__(self, llm, config: SupervisorConfig):
        super().__init__(llm, config)
        self.quality_criteria = self._initialize_quality_criteria()
    
    async def validate_output(self, output: Any, task_type: str) -> ValidationResult:
        """Validate worker output against quality standards."""
        self.logger.info(f"Validating {task_type} output")
        
        if task_type == "requirements_analysis":
            return await self._validate_requirements(output)
        elif task_type == "architecture_design":
            return await self._validate_architecture(output)
        elif task_type == "code_generation":
            return await self._validate_code(output)
        elif task_type == "test_generation":
            return await self._validate_tests(output)
        elif task_type == "code_review":
            return await self._validate_review(output)
        elif task_type == "security_analysis":
            return await self._validate_security(output)
        elif task_type == "documentation_generation":
            return await self._validate_documentation(output)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _validate_requirements(self, output: RequirementsAnalysisOutput) -> ValidationResult:
        """Validate requirements analysis output."""
        criteria = self.quality_criteria["requirements_analysis"]
        
        # Evaluate completeness
        completeness_score = await self._evaluate_completeness(output)
        
        # Evaluate clarity
        clarity_score = await self._evaluate_clarity(output)
        
        # Evaluate feasibility
        feasibility_score = await self._evaluate_feasibility(output)
        
        # Evaluate consistency
        consistency_score = await self._evaluate_consistency(output)
        
        # Calculate overall score
        overall_score = (
            completeness_score * criteria["completeness_weight"] +
            clarity_score * criteria["clarity_weight"] +
            feasibility_score * criteria["feasibility_weight"] +
            consistency_score * criteria["consistency_weight"]
        )
        
        # Determine validation result
        is_approved = overall_score >= self.config.quality_thresholds["requirements"]
        
        validation_result = ValidationResult(
            task_type="requirements_analysis",
            overall_score=overall_score,
            is_approved=is_approved,
            criteria_scores={
                "completeness": completeness_score,
                "clarity": clarity_score,
                "feasibility": feasibility_score,
                "consistency": consistency_score
            },
            feedback=self._generate_feedback(output, {
                "completeness": completeness_score,
                "clarity": clarity_score,
                "feasibility": feasibility_score,
                "consistency": consistency_score
            }),
            timestamp=datetime.now()
        )
        
        # Log validation decision
        self.log_decision({
            "action": "quality_validation",
            "task_type": "requirements_analysis",
            "overall_score": overall_score,
            "is_approved": is_approved
        }, {"output": output.dict()})
        
        return validation_result
    
    def _initialize_quality_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality criteria for different task types."""
        return {
            "requirements_analysis": {
                "completeness_weight": 0.3,
                "clarity_weight": 0.25,
                "feasibility_weight": 0.25,
                "consistency_weight": 0.2
            },
            "architecture_design": {
                "scalability_weight": 0.3,
                "maintainability_weight": 0.25,
                "security_weight": 0.25,
                "performance_weight": 0.2
            },
            "code_generation": {
                "functionality_weight": 0.4,
                "readability_weight": 0.3,
                "efficiency_weight": 0.2,
                "documentation_weight": 0.1
            },
            # ... other criteria
        }
```

### Step 1.8: Create Enhanced State Management

**File**: `models/supervisor_state.py`

```python
#!/usr/bin/env python3
"""
Enhanced state management for supervisor-swarm hybrid system.
"""

from typing import TypedDict, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel


class SupervisorSwarmState(TypedDict):
    """Enhanced state for supervisor-swarm hybrid system."""
    # Project context
    project_context: str
    project_name: str
    session_id: str
    
    # Workflow state
    current_phase: str  # 'planning', 'execution', 'review', 'completion'
    current_supervisor_task: Optional[str]
    active_agent: Optional[str]
    
    # Agent outputs
    requirements: List[Dict[str, Any]]
    architecture: Dict[str, Any]
    code_files: Dict[str, Any]
    tests: Dict[str, Any]
    documentation: Dict[str, Any]
    agent_outputs: Dict[str, Any]
    
    # Supervisor oversight
    supervisor_decisions: List[Dict[str, Any]]
    quality_validations: List[Dict[str, Any]]
    task_delegations: List[Dict[str, Any]]
    escalations: List[Dict[str, Any]]
    
    # Swarm coordination
    handoff_history: List[Dict[str, Any]]
    agent_collaborations: List[Dict[str, Any]]
    current_collaboration: Optional[Dict[str, Any]]
    
    # Error handling
    errors: List[str]
    warnings: List[str]
    retry_count: int
    
    # Performance tracking
    execution_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, Dict[str, Any]]


class Task(BaseModel):
    """Structured task definition for delegation."""
    id: str
    type: str  # 'requirements_analysis', 'architecture_design', etc.
    description: str
    requirements: Dict[str, Any]
    priority: str  # 'low', 'medium', 'high', 'critical'
    estimated_complexity: str  # 'simple', 'moderate', 'complex'
    dependencies: List[str]
    quality_criteria: Dict[str, Any]
    created_at: datetime
    assigned_to: Optional[str] = None
    status: str = "pending"  # 'pending', 'in_progress', 'completed', 'failed'


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_id: str
    worker: str
    result: Dict[str, Any]
    validation: Optional[Dict[str, Any]] = None
    timestamp: datetime
    execution_time: Optional[float] = None
    status: str = "completed"


class Escalation(BaseModel):
    """Escalation from worker agent to supervisor."""
    id: str
    from_agent: str
    issue: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    context: Dict[str, Any]
    timestamp: datetime
    status: str = "pending"  # 'pending', 'in_progress', 'resolved'


class ValidationResult(BaseModel):
    """Result of quality validation."""
    task_type: str
    overall_score: float
    is_approved: bool
    criteria_scores: Dict[str, float]
    feedback: str
    timestamp: datetime
    validator: str = "quality_control_supervisor"
```

## Phase 2: Handoff System Implementation (Week 2-3)

### Step 2.1: Create Handoff Tools

**File**: `agents/handoff/handoff_system.py`

```python
#!/usr/bin/env python3
"""
Handoff system for dynamic agent collaboration.
"""

from typing import Dict, Callable, Any
from langchain_core.tools import tool
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState, InjectedToolCallId


class AgentHandoffSystem:
    """Manages dynamic handoffs between specialized agents."""
    
    def __init__(self):
        self.handoff_tools = self._create_handoff_tools()
    
    def get_handoff_tools(self) -> Dict[str, Callable]:
        """Get all handoff tools."""
        return self.handoff_tools
    
    def _create_handoff_tools(self) -> Dict[str, Callable]:
        """Create handoff tools for each agent."""
        return {
            "transfer_to_requirements": self._create_handoff_tool("requirements_analyst"),
            "transfer_to_architecture": self._create_handoff_tool("architecture_designer"),
            "transfer_to_code_generator": self._create_handoff_tool("code_generator"),
            "transfer_to_test_generator": self._create_handoff_tool("test_generator"),
            "transfer_to_code_reviewer": self._create_handoff_tool("code_reviewer"),
            "transfer_to_security_analyst": self._create_handoff_tool("security_analyst"),
            "transfer_to_documentation": self._create_handoff_tool("documentation_generator"),
            "escalate_to_supervisor": self._create_escalation_tool()
        }
    
    def _create_handoff_tool(self, agent_name: str):
        """Create a handoff tool for transferring to another agent."""
        @tool(f"transfer_to_{agent_name}", f"Transfer to {agent_name}")
        def handoff_tool(
            state: MessagesState = InjectedState,
            tool_call_id: str = InjectedToolCallId,
            reason: str = "Task requires specialized expertise"
        ) -> Command:
            tool_message = {
                "role": "tool",
                "content": f"Transferred to {agent_name}: {reason}",
                "name": f"transfer_to_{agent_name}",
                "tool_call_id": tool_call_id,
            }
            return Command(
                goto=agent_name,
                update={"messages": state["messages"] + [tool_message]},
                graph=Command.PARENT,
            )
        return handoff_tool
    
    def _create_escalation_tool(self):
        """Create escalation tool for supervisor intervention."""
        @tool("escalate_to_supervisor", "Escalate issue to supervisor for resolution")
        def escalation_tool(
            state: MessagesState = InjectedState,
            tool_call_id: str = InjectedToolCallId,
            issue: str = "Complex issue requiring supervisor intervention",
            severity: str = "medium"
        ) -> Command:
            tool_message = {
                "role": "tool",
                "content": f"Escalated to supervisor: {issue} (severity: {severity})",
                "name": "escalate_to_supervisor",
                "tool_call_id": tool_call_id,
            }
            return Command(
                goto="supervisor_intervention",
                update={"messages": state["messages"] + [tool_message]},
                graph=Command.PARENT,
            )
        return escalation_tool
```

### Step 2.2: Enhance Agent Factory

**File**: `agents/enhanced_agent_factory.py`

```python
#!/usr/bin/env python3
"""
Enhanced agent factory with handoff capabilities.
"""

from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from .handoff.handoff_system import AgentHandoffSystem


class EnhancedAgentFactory:
    """Creates agents with handoff capabilities."""
    
    def __init__(self):
        self.handoff_system = AgentHandoffSystem()
    
    def create_requirements_analyst(self, llm: ChatGoogleGenerativeAI) -> Any:
        """Create requirements analyst with handoff tools."""
        handoff_tools = [
            self.handoff_system.get_handoff_tools()["transfer_to_architecture"],
            self.handoff_system.get_handoff_tools()["escalate_to_supervisor"]
        ]
        
        return create_react_agent(
            model=llm,
            tools=handoff_tools,
            prompt="""You are an expert Requirements Analyst. Your role is to:
            1. Analyze project context and extract comprehensive requirements
            2. Identify functional and non-functional requirements
            3. Create user stories and acceptance criteria
            4. If you encounter architecture-related questions, transfer to the Architecture Designer
            5. If you encounter complex issues beyond your expertise, escalate to the supervisor
            
            Always ensure requirements are clear, complete, and feasible.""",
            name="requirements_analyst"
        )
    
    def create_architecture_designer(self, llm: ChatGoogleGenerativeAI) -> Any:
        """Create architecture designer with handoff tools."""
        handoff_tools = [
            self.handoff_system.get_handoff_tools()["transfer_to_requirements"],
            self.handoff_system.get_handoff_tools()["transfer_to_code_generator"],
            self.handoff_system.get_handoff_tools()["escalate_to_supervisor"]
        ]
        
        return create_react_agent(
            model=llm,
            tools=handoff_tools,
            prompt="""You are an expert Architecture Designer. Your role is to:
            1. Design scalable and maintainable system architecture
            2. Select appropriate technologies and patterns
            3. Create system diagrams and documentation
            4. If you need clarification on requirements, transfer to Requirements Analyst
            5. If you need to discuss implementation details, transfer to Code Generator
            6. If you encounter complex architectural decisions, escalate to supervisor
            
            Always ensure architecture is scalable, secure, and follows best practices.""",
            name="architecture_designer"
        )
    
    # ... similar methods for other agents
```

## Phase 3: Hybrid Workflow Implementation (Week 3-4)

### Step 3.1: Create Hybrid Workflow Manager

**File**: `workflow/hybrid_workflow_manager.py`

```python
#!/usr/bin/env python3
"""
Hybrid workflow manager combining supervisor and swarm patterns.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from models.supervisor_state import SupervisorSwarmState
from agents.supervisor.project_manager_supervisor import ProjectManagerSupervisor
from agents.supervisor.quality_control_supervisor import QualityControlSupervisor
from agents.enhanced_agent_factory import EnhancedAgentFactory
from utils.structured_outputs import SupervisorConfig


class HybridWorkflowManager:
    """Manages the hybrid supervisor-swarm workflow."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.llm = self._setup_llm()
        self.supervisor_config = self._create_supervisor_config()
        
        # Initialize supervisors
        self.project_manager = ProjectManagerSupervisor(self.llm, self.supervisor_config)
        self.quality_control = QualityControlSupervisor(self.llm, self.supervisor_config)
        
        # Initialize agent factory
        self.agent_factory = EnhancedAgentFactory()
        
        # Create workflow
        self.workflow = self._create_hybrid_workflow()
    
    def _setup_llm(self):
        """Setup the LLM for the workflow."""
        # Implementation similar to existing workflow manager
        pass
    
    def _create_supervisor_config(self) -> SupervisorConfig:
        """Create supervisor configuration."""
        return SupervisorConfig(
            quality_thresholds={
                "requirements": 0.8,
                "architecture": 0.8,
                "code": 0.7,
                "tests": 0.7,
                "review": 0.8,
                "security": 0.9,
                "documentation": 0.7
            },
            max_retries=3,
            escalation_threshold=0.7,
            enable_parallel_execution=True
        )
    
    def _create_hybrid_workflow(self) -> StateGraph:
        """Create the hybrid supervisor-swarm workflow."""
        workflow = StateGraph(SupervisorSwarmState)
        
        # Add supervisor nodes
        workflow.add_node("supervisor_planning", self._supervisor_planning_node)
        workflow.add_node("supervisor_quality_check", self._supervisor_quality_check_node)
        workflow.add_node("supervisor_intervention", self._supervisor_intervention_node)
        
        # Add swarm agent nodes
        workflow.add_node("requirements_analyst", 
                         self.agent_factory.create_requirements_analyst(self.llm))
        workflow.add_node("architecture_designer", 
                         self.agent_factory.create_architecture_designer(self.llm))
        workflow.add_node("code_generator", 
                         self.agent_factory.create_code_generator(self.llm))
        workflow.add_node("test_generator", 
                         self.agent_factory.create_test_generator(self.llm))
        workflow.add_node("code_reviewer", 
                         self.agent_factory.create_code_reviewer(self.llm))
        workflow.add_node("security_analyst", 
                         self.agent_factory.create_security_analyst(self.llm))
        workflow.add_node("documentation_generator", 
                         self.agent_factory.create_documentation_generator(self.llm))
        
        # Define workflow edges
        workflow.add_edge(START, "supervisor_planning")
        workflow.add_edge("supervisor_planning", "requirements_analyst")
        
        # Add conditional edges for handoffs
        workflow.add_conditional_edges(
            "requirements_analyst",
            self._route_based_on_agent_decision,
            {
                "continue": "supervisor_quality_check",
                "handoff_to_architecture": "architecture_designer",
                "escalate": "supervisor_intervention"
            }
        )
        
        # Add quality check routing
        workflow.add_conditional_edges(
            "supervisor_quality_check",
            self._route_based_on_quality,
            {
                "approved": "architecture_designer",
                "needs_revision": "requirements_analyst",
                "failed": "supervisor_intervention"
            }
        )
        
        # Similar patterns for other agents...
        
        workflow.add_edge("supervisor_intervention", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _supervisor_planning_node(self, state: SupervisorSwarmState) -> SupervisorSwarmState:
        """Supervisor planning node."""
        self.logger.info("Executing supervisor planning")
        
        # Create task breakdown
        tasks = await self.project_manager._create_task_breakdown(state["project_context"])
        
        # Update state
        return {
            **state,
            "current_phase": "planning",
            "supervisor_decisions": [
                *state["supervisor_decisions"],
                {
                    "step": "supervisor_planning",
                    "action": "task_breakdown",
                    "tasks_created": len(tasks),
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def _supervisor_quality_check_node(self, state: SupervisorSwarmState) -> SupervisorSwarmState:
        """Supervisor quality check node."""
        self.logger.info("Executing supervisor quality check")
        
        # Get current agent output
        current_agent = state["active_agent"]
        agent_output = state["agent_outputs"].get(current_agent)
        
        if not agent_output:
            return {
                **state,
                "errors": [*state["errors"], "No agent output found for quality check"]
            }
        
        # Validate output
        validation_result = await self.quality_control.validate_output(
            agent_output, current_agent
        )
        
        # Update state
        return {
            **state,
            "quality_validations": [
                *state["quality_validations"],
                validation_result.dict()
            ],
            "current_validation": validation_result.dict()
        }
    
    def _route_based_on_agent_decision(self, state: SupervisorSwarmState) -> str:
        """Route based on agent's decision."""
        # This would analyze the agent's output and determine routing
        # For now, return "continue" as default
        return "continue"
    
    def _route_based_on_quality(self, state: SupervisorSwarmState) -> str:
        """Route based on quality validation result."""
        current_validation = state.get("current_validation")
        
        if not current_validation:
            return "failed"
        
        if current_validation["is_approved"]:
            return "approved"
        elif current_validation["overall_score"] > 0.5:
            return "needs_revision"
        else:
            return "failed"
    
    async def execute_workflow(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the hybrid workflow."""
        try:
            # Convert to SupervisorSwarmState
            swarm_state = SupervisorSwarmState(
                project_context=initial_state.get("project_context", ""),
                project_name=initial_state.get("project_name", ""),
                session_id=initial_state.get("session_id", ""),
                current_phase="started",
                current_supervisor_task=None,
                active_agent=None,
                requirements=[],
                architecture={},
                code_files={},
                tests={},
                documentation={},
                agent_outputs={},
                supervisor_decisions=[],
                quality_validations=[],
                task_delegations=[],
                escalations=[],
                handoff_history=[],
                agent_collaborations=[],
                current_collaboration=None,
                errors=[],
                warnings=[],
                retry_count=0,
                execution_history=[],
                performance_metrics={}
            )
            
            # Execute workflow
            result = await self.workflow.ainvoke(swarm_state)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                **initial_state,
                "errors": [f"Workflow execution failed: {str(e)}"],
                "current_phase": "failed"
            }
```

## Phase 4: Testing and Validation (Week 4-5)

### Step 4.1: Create Comprehensive Tests

**File**: `tests/supervisor_swarm/test_hybrid_workflow.py`

```python
#!/usr/bin/env python3
"""
Tests for the hybrid supervisor-swarm workflow.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from workflow.hybrid_workflow_manager import HybridWorkflowManager
from models.supervisor_state import SupervisorSwarmState, Task, ValidationResult
from agents.supervisor.project_manager_supervisor import ProjectManagerSupervisor
from agents.supervisor.quality_control_supervisor import QualityControlSupervisor


class TestHybridWorkflow:
    """Tests for the hybrid supervisor-swarm workflow."""
    
    @pytest.fixture
    def mock_llm_config(self):
        return {
            "model_name": "gemini-2.5-flash-lite",
            "temperature": 0.1,
            "max_tokens": 8192,
            "api_key": "test_key"
        }
    
    @pytest.fixture
    def workflow_manager(self, mock_llm_config):
        with patch('workflow.hybrid_workflow_manager.ChatGoogleGenerativeAI'):
            return HybridWorkflowManager(mock_llm_config)
    
    @pytest.fixture
    def test_state(self):
        return SupervisorSwarmState(
            project_context="Create a simple web application",
            project_name="test_project",
            session_id="test_session",
            current_phase="started",
            current_supervisor_task=None,
            active_agent=None,
            requirements=[],
            architecture={},
            code_files={},
            tests={},
            documentation={},
            agent_outputs={},
            supervisor_decisions=[],
            quality_validations=[],
            task_delegations=[],
            escalations=[],
            handoff_history=[],
            agent_collaborations=[],
            current_collaboration=None,
            errors=[],
            warnings=[],
            retry_count=0,
            execution_history=[],
            performance_metrics={}
        )
    
    @pytest.mark.asyncio
    async def test_workflow_initialization(self, workflow_manager):
        """Test workflow manager initialization."""
        assert workflow_manager.workflow is not None
        assert workflow_manager.project_manager is not None
        assert workflow_manager.quality_control is not None
        assert workflow_manager.agent_factory is not None
    
    @pytest.mark.asyncio
    async def test_supervisor_planning_node(self, workflow_manager, test_state):
        """Test supervisor planning node."""
        with patch.object(workflow_manager.project_manager, '_create_task_breakdown') as mock_breakdown:
            mock_breakdown.return_value = [
                Task(
                    id="task_1",
                    type="requirements_analysis",
                    description="Analyze project requirements",
                    requirements={},
                    priority="high",
                    estimated_complexity="moderate",
                    dependencies=[],
                    quality_criteria={},
                    created_at=datetime.now()
                )
            ]
            
            result = await workflow_manager._supervisor_planning_node(test_state)
            
            assert result["current_phase"] == "planning"
            assert len(result["supervisor_decisions"]) == 1
            assert result["supervisor_decisions"][0]["action"] == "task_breakdown"
    
    @pytest.mark.asyncio
    async def test_quality_validation(self, workflow_manager, test_state):
        """Test quality validation node."""
        # Mock agent output
        test_state["active_agent"] = "requirements_analyst"
        test_state["agent_outputs"] = {
            "requirements_analyst": {
                "functional_requirements": ["req1", "req2"],
                "non_functional_requirements": ["perf1", "sec1"]
            }
        }
        
        with patch.object(workflow_manager.quality_control, 'validate_output') as mock_validate:
            mock_validate.return_value = ValidationResult(
                task_type="requirements_analysis",
                overall_score=0.85,
                is_approved=True,
                criteria_scores={"completeness": 0.9, "clarity": 0.8},
                feedback="Good requirements analysis",
                timestamp=datetime.now()
            )
            
            result = await workflow_manager._supervisor_quality_check_node(test_state)
            
            assert len(result["quality_validations"]) == 1
            assert result["current_validation"]["is_approved"] is True
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, workflow_manager):
        """Test complete workflow execution."""
        initial_state = {
            "project_context": "Create a simple web application",
            "project_name": "test_project",
            "session_id": "test_session"
        }
        
        with patch.object(workflow_manager.workflow, 'ainvoke') as mock_invoke:
            mock_invoke.return_value = {
                **initial_state,
                "current_phase": "completed",
                "requirements": [{"id": "req1", "description": "User authentication"}],
                "architecture": {"type": "web", "framework": "flask"}
            }
            
            result = await workflow_manager.execute_workflow(initial_state)
            
            assert result["current_phase"] == "completed"
            assert len(result["requirements"]) > 0
            assert result["architecture"] is not None
```

## Implementation Timeline (Updated)

### Week 1: Immediate Fixes (CRITICAL)
- [ ] Fix Pydantic validation issues in tests
- [ ] Complete missing agent nodes (4 remaining)
- [ ] Fix workflow graph START edges
- [ ] Fix async/await implementation issues
- [ ] Create supervisor base classes

### Week 2: Foundation Implementation
- [x] Create supervisor base classes
- [ ] Implement Project Manager Supervisor
- [ ] Implement Quality Control Supervisor
- [ ] Create enhanced state management

### Week 3: Handoff System
- [ ] Create handoff tools
- [ ] Enhance agent factory
- [ ] Implement handoff system
- [ ] Add escalation mechanisms

### Week 4: Hybrid Workflow
- [ ] Create hybrid workflow manager
- [ ] Implement workflow graph
- [ ] Add conditional routing
- [ ] Integrate supervisor nodes

### Week 5: Testing and Validation
- [ ] Create comprehensive tests
- [ ] Validate workflow execution
- [ ] Performance testing
- [ ] Documentation updates

## Success Metrics (Updated)

### Quality Metrics
- **Output Quality**: 90%+ validation approval rate
- **Error Reduction**: 50% reduction in workflow errors
- **Escalation Rate**: <10% of tasks require escalation
- **Test Coverage**: >90% for all components

### Performance Metrics
- **Execution Time**: <30s for complete workflow
- **Resource Utilization**: Better agent utilization through intelligent routing
- **Scalability**: Support for 2x more concurrent workflows
- **Error Recovery**: <10s for error recovery

### Observability Metrics
- **Decision Tracking**: 100% supervisor decisions logged
- **Handoff Tracking**: Complete handoff history
- **Performance Monitoring**: Real-time performance metrics
- **Test Stability**: <5% test failure rate

## Conclusion

This updated implementation roadmap reflects the current state of our system and prioritizes the immediate fixes needed to get our tests passing and system functional. The key focus areas are:

1. **Immediate Priority**: Fix Pydantic validation and complete missing agent nodes
2. **Foundation**: Build supervisor layer for quality control and orchestration
3. **Advanced Features**: Implement handoff system and hybrid workflow
4. **Validation**: Comprehensive testing and performance optimization

The hybrid architecture will significantly enhance our agent system's capabilities while maintaining the solid foundation we've already established.
