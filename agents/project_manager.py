"""
Project Manager Agent for AI Development Agent System.
Coordinates other agents, manages feedback loops, and makes critical decisions.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .base_agent import BaseAgent
from models.responses import AgentResult, AgentStatus
from models.state import ProjectState


@dataclass
class FeedbackRequest:
    """Represents a feedback request between agents."""
    from_agent: str
    to_agent: str
    artifact_type: str
    artifact_content: Dict[str, Any]
    feedback_type: str  # 'review', 'validation', 'improvement'
    priority: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    status: str  # 'pending', 'in_progress', 'completed', 'rejected'


@dataclass
class DecisionPoint:
    """Represents a decision point that requires project manager intervention."""
    decision_id: str
    description: str
    options: List[Dict[str, Any]]
    context: Dict[str, Any]
    priority: str
    timestamp: datetime
    status: str  # 'pending', 'resolved'
    resolution: Optional[Dict[str, Any]] = None


class ProjectManagerAgent(BaseAgent):
    """
    Project Manager Agent that coordinates the development workflow.
    
    Responsibilities:
    - Orchestrate agent interactions
    - Manage feedback loops between agents
    - Make critical decisions when agents disagree
    - Monitor project progress and quality
    - Ensure project completion criteria are met
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "project_manager")
        self.feedback_requests: List[FeedbackRequest] = []
        self.decision_points: List[DecisionPoint] = []
        self.agent_feedback_history: Dict[str, List[Dict[str, Any]]] = {}
        self.iteration_count = 0
        self.max_iterations = 3
        
    async def execute(self, state: ProjectState) -> AgentResult:
        """Execute the project manager workflow."""
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting project manager execution")
            
            # Initialize project state
            self.iteration_count = 0
            self.feedback_requests.clear()
            self.decision_points.clear()
            
            # Execute the main development workflow with feedback loops
            final_state = await self._execute_development_workflow(state)
            
            # Generate project manager documentation
            documentation = self._generate_documentation(final_state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                status=AgentStatus.COMPLETED,
                output=final_state.to_dict(),
                documentation=documentation,
                execution_time=execution_time,
                logs=self.logs,
                decisions=self.decisions,
                artifacts=self.artifacts
            )
            
        except Exception as e:
            self.logger.error(f"Project manager execution failed: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                status=AgentStatus.FAILED,
                output={"error": str(e)},
                documentation={"error": str(e)},
                execution_time=execution_time,
                logs=self.logs,
                decisions=self.decisions,
                artifacts=self.artifacts
            )
    
    async def _execute_development_workflow(self, state: ProjectState) -> ProjectState:
        """Execute the development workflow with feedback loops."""
        current_state = state
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            self.logger.info(f"Starting iteration {self.iteration_count}")
            
            # Execute the standard workflow
            current_state = await self._execute_iteration(current_state)
            
            # Check if feedback is needed
            feedback_needed = await self._assess_feedback_needs(current_state)
            
            if not feedback_needed:
                self.logger.info("No feedback needed, workflow complete")
                break
            
            # Process feedback and iterate
            current_state = await self._process_feedback_loop(current_state)
            
            # Check for decision points
            if self.decision_points:
                current_state = await self._resolve_decision_points(current_state)
        
        return current_state
    
    async def _execute_iteration(self, state: ProjectState) -> ProjectState:
        """Execute a single iteration of the development workflow."""
        self.logger.info("Executing development iteration")
        
        # Execute each agent in sequence
        agents = [
            ("requirements_analyst", "requirements"),
            ("architecture_designer", "architecture"),
            ("code_generator", "code"),
            ("test_generator", "tests"),
            ("documentation_generator", "documentation"),
            ("code_reviewer", "review"),
            ("security_analyst", "security")
        ]
        
        current_state = state
        
        for agent_name, artifact_type in agents:
            self.logger.info(f"Executing {agent_name}")
            
            # Execute agent
            agent_result = await self._execute_agent(agent_name, current_state)
            
            # Update state with agent result
            current_state = self._update_state_with_agent_result(
                current_state, agent_name, agent_result
            )
            
            # Check for immediate feedback needs
            await self._check_agent_feedback_needs(agent_name, agent_result, current_state)
        
        return current_state
    
    async def _execute_agent(self, agent_name: str, state: ProjectState) -> AgentResult:
        """Execute a specific agent."""
        # This would integrate with the existing agent system
        # For now, we'll simulate agent execution
        self.logger.info(f"Simulating execution of {agent_name}")
        
        # Simulate agent execution time
        await asyncio.sleep(0.1)
        
        return AgentResult(
            status=AgentStatus.COMPLETED,
            output={"agent": agent_name, "status": "completed"},
            documentation={"summary": f"{agent_name} completed successfully"},
            execution_time=0.1,
            logs=[],
            decisions=[],
            artifacts=[]
        )
    
    def _update_state_with_agent_result(
        self, state: ProjectState, agent_name: str, result: AgentResult
    ) -> ProjectState:
        """Update project state with agent result."""
        # Update state based on agent result
        if agent_name == "requirements_analyst":
            state.requirements = result.output
        elif agent_name == "architecture_designer":
            state.architecture = result.output
        elif agent_name == "code_generator":
            state.code_files = result.output.get("code_files", {})
        elif agent_name == "test_generator":
            state.test_files = result.output.get("test_files", {})
        elif agent_name == "documentation_generator":
            state.documentation_files = result.output.get("documentation_files", {})
        
        return state
    
    async def _assess_feedback_needs(self, state: ProjectState) -> bool:
        """Assess whether feedback loops are needed."""
        # Check for quality issues, inconsistencies, or missing requirements
        feedback_needed = False
        
        # Check requirements completeness
        if not state.requirements or not self._validate_requirements(state.requirements):
            feedback_needed = True
            self.logger.info("Requirements validation failed, feedback needed")
        
        # Check architecture consistency
        if not state.architecture or not self._validate_architecture(state.architecture):
            feedback_needed = True
            self.logger.info("Architecture validation failed, feedback needed")
        
        # Check code quality
        if state.code_files and not self._validate_code_quality(state.code_files):
            feedback_needed = True
            self.logger.info("Code quality validation failed, feedback needed")
        
        return feedback_needed
    
    async def _process_feedback_loop(self, state: ProjectState) -> ProjectState:
        """Process feedback loops between agents."""
        self.logger.info("Processing feedback loop")
        
        # Process pending feedback requests
        for feedback_request in self.feedback_requests:
            if feedback_request.status == "pending":
                await self._process_feedback_request(feedback_request, state)
        
        # Update state based on feedback
        updated_state = self._apply_feedback_to_state(state)
        
        return updated_state
    
    async def _process_feedback_request(
        self, feedback_request: FeedbackRequest, state: ProjectState
    ):
        """Process a specific feedback request."""
        self.logger.info(f"Processing feedback from {feedback_request.from_agent} to {feedback_request.to_agent}")
        
        # Simulate feedback processing
        feedback_request.status = "completed"
        
        # Record feedback in history
        if feedback_request.to_agent not in self.agent_feedback_history:
            self.agent_feedback_history[feedback_request.to_agent] = []
        
        self.agent_feedback_history[feedback_request.to_agent].append({
            "from_agent": feedback_request.from_agent,
            "feedback_type": feedback_request.feedback_type,
            "timestamp": feedback_request.timestamp.isoformat(),
            "status": feedback_request.status
        })
    
    def _apply_feedback_to_state(self, state: ProjectState) -> ProjectState:
        """Apply feedback results to the project state."""
        # Apply feedback-based improvements to the state
        # This would involve updating requirements, architecture, or code based on feedback
        return state
    
    async def _resolve_decision_points(self, state: ProjectState) -> ProjectState:
        """Resolve pending decision points."""
        self.logger.info("Resolving decision points")
        
        for decision_point in self.decision_points:
            if decision_point.status == "pending":
                resolution = await self._make_decision(decision_point)
                decision_point.resolution = resolution
                decision_point.status = "resolved"
                
                # Apply decision to state
                state = self._apply_decision_to_state(state, decision_point)
        
        return state
    
    async def _make_decision(self, decision_point: DecisionPoint) -> Dict[str, Any]:
        """Make a decision for a decision point."""
        self.logger.info(f"Making decision: {decision_point.description}")
        
        # Use AI to make the decision based on context and options
        decision_prompt = self._create_decision_prompt(decision_point)
        
        # Simulate AI decision making
        await asyncio.sleep(0.1)
        
        # For now, return the first option as the decision
        decision = {
            "selected_option": decision_point.options[0] if decision_point.options else None,
            "rationale": "Selected based on project requirements and best practices",
            "timestamp": datetime.now().isoformat()
        }
        
        self.decisions.append({
            "decision": decision_point.description,
            "rationale": decision["rationale"],
            "selected_option": decision["selected_option"],
            "timestamp": decision["timestamp"]
        })
        
        return decision
    
    def _create_decision_prompt(self, decision_point: DecisionPoint) -> str:
        """Create a prompt for AI decision making."""
        return f"""
        Decision Required: {decision_point.description}
        
        Context: {json.dumps(decision_point.context, indent=2)}
        
        Options:
        {json.dumps(decision_point.options, indent=2)}
        
        Please select the best option and provide rationale.
        """
    
    def _apply_decision_to_state(self, state: ProjectState, decision_point: DecisionPoint) -> ProjectState:
        """Apply a decision to the project state."""
        # Apply the decision resolution to the appropriate part of the state
        if decision_point.resolution:
            # Update state based on decision
            pass
        
        return state
    
    async def _check_agent_feedback_needs(
        self, agent_name: str, result: AgentResult, state: ProjectState
    ):
        """Check if an agent needs feedback from other agents."""
        # Determine which agents should provide feedback
        feedback_mapping = {
            "requirements_analyst": ["architecture_designer", "code_generator"],
            "architecture_designer": ["code_generator", "test_generator"],
            "code_generator": ["code_reviewer", "test_generator", "security_analyst"],
            "test_generator": ["code_reviewer"],
            "documentation_generator": ["code_reviewer"],
            "code_reviewer": ["code_generator"],
            "security_analyst": ["code_generator", "architecture_designer"]
        }
        
        if agent_name in feedback_mapping:
            for feedback_agent in feedback_mapping[agent_name]:
                feedback_request = FeedbackRequest(
                    from_agent=agent_name,
                    to_agent=feedback_agent,
                    artifact_type=self._get_artifact_type(agent_name),
                    artifact_content=result.output,
                    feedback_type="review",
                    priority="medium",
                    timestamp=datetime.now(),
                    status="pending"
                )
                self.feedback_requests.append(feedback_request)
    
    def _get_artifact_type(self, agent_name: str) -> str:
        """Get the artifact type for an agent."""
        artifact_types = {
            "requirements_analyst": "requirements",
            "architecture_designer": "architecture",
            "code_generator": "code",
            "test_generator": "tests",
            "documentation_generator": "documentation",
            "code_reviewer": "review",
            "security_analyst": "security_analysis"
        }
        return artifact_types.get(agent_name, "unknown")
    
    def _validate_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Validate requirements completeness."""
        # Check if requirements are complete and well-formed
        return bool(requirements and isinstance(requirements, dict))
    
    def _validate_architecture(self, architecture: Dict[str, Any]) -> bool:
        """Validate architecture consistency."""
        # Check if architecture is consistent and complete
        return bool(architecture and isinstance(architecture, dict))
    
    def _validate_code_quality(self, code_files: Dict[str, str]) -> bool:
        """Validate code quality."""
        # Check if code meets quality standards
        return bool(code_files and len(code_files) > 0)
    
    def _generate_documentation(self, state: ProjectState) -> Dict[str, Any]:
        """Generate project manager documentation."""
        return {
            "summary": f"Project managed through {self.iteration_count} iterations with feedback loops",
            "details": {
                "total_iterations": self.iteration_count,
                "feedback_requests_processed": len([f for f in self.feedback_requests if f.status == "completed"]),
                "decisions_made": len([d for d in self.decision_points if d.status == "resolved"]),
                "agent_feedback_history": self.agent_feedback_history,
                "project_status": "completed" if self.iteration_count < self.max_iterations else "max_iterations_reached"
            },
            "feedback_summary": {
                "total_requests": len(self.feedback_requests),
                "completed_requests": len([f for f in self.feedback_requests if f.status == "completed"]),
                "pending_requests": len([f for f in self.feedback_requests if f.status == "pending"])
            },
            "decision_summary": {
                "total_decisions": len(self.decision_points),
                "resolved_decisions": len([d for d in self.decision_points if d.status == "resolved"]),
                "pending_decisions": len([d for d in self.decision_points if d.status == "pending"])
            }
        }
