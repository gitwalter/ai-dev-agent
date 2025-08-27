"""
Handoff Management System for AI Development Agent

This module implements dynamic agent assignment and handoff validation
for the multi-agent workflow system.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from models.state import AgentState, HandoffRequest


class HandoffPriority(Enum):
    """Handoff priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class HandoffStatus(Enum):
    """Handoff status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HandoffValidationResult:
    """Result of handoff validation."""
    
    def __init__(self, is_valid: bool, reason: str = "", suggestions: List[str] = None):
        self.is_valid = is_valid
        self.reason = reason
        self.suggestions = suggestions or []


class HandoffManager:
    """Manages dynamic agent handoffs and validation."""
    
    def __init__(self):
        self.agent_capabilities = {
            "requirements_analyst": {
                "primary_tasks": ["requirements_analysis", "user_story_creation"],
                "secondary_tasks": ["project_planning", "scope_definition"],
                "expertise": ["business_analysis", "user_research", "requirement_gathering"]
            },
            "architecture_designer": {
                "primary_tasks": ["architecture_design", "system_design"],
                "secondary_tasks": ["technology_selection", "scalability_planning"],
                "expertise": ["system_architecture", "design_patterns", "technology_stack"]
            },
            "code_generator": {
                "primary_tasks": ["code_generation", "implementation"],
                "secondary_tasks": ["code_optimization", "refactoring"],
                "expertise": ["programming", "software_development", "best_practices"]
            },
            "test_generator": {
                "primary_tasks": ["test_generation", "test_planning"],
                "secondary_tasks": ["test_automation", "quality_assurance"],
                "expertise": ["testing", "quality_assurance", "test_automation"]
            },
            "code_reviewer": {
                "primary_tasks": ["code_review", "quality_assessment"],
                "secondary_tasks": ["performance_analysis", "security_review"],
                "expertise": ["code_quality", "best_practices", "performance_optimization"]
            },
            "security_analyst": {
                "primary_tasks": ["security_analysis", "vulnerability_assessment"],
                "secondary_tasks": ["security_planning", "compliance_checking"],
                "expertise": ["security", "vulnerability_analysis", "security_best_practices"]
            },
            "documentation_generator": {
                "primary_tasks": ["documentation_generation", "user_guides"],
                "secondary_tasks": ["api_documentation", "technical_writing"],
                "expertise": ["technical_writing", "documentation", "user_experience"]
            }
        }
    
    def validate_handoff_request(
        self,
        handoff: HandoffRequest,
        state: AgentState
    ) -> HandoffValidationResult:
        """
        Validate a handoff request.
        
        Args:
            handoff: The handoff request to validate
            state: Current workflow state
            
        Returns:
            HandoffValidationResult with validation status and details
        """
        # Check if from_agent exists and is available
        if handoff.from_agent not in self.agent_capabilities:
            return HandoffValidationResult(
                is_valid=False,
                reason=f"Source agent '{handoff.from_agent}' does not exist",
                suggestions=["Check agent name spelling", "Verify agent is registered"]
            )
        
        # Check if to_agent exists and is available
        if handoff.to_agent not in self.agent_capabilities:
            return HandoffValidationResult(
                is_valid=False,
                reason=f"Target agent '{handoff.to_agent}' does not exist",
                suggestions=["Check agent name spelling", "Verify agent is registered"]
            )
        
        # Check agent availability
        agent_availability = state.get("agent_availability", {})
        if not agent_availability.get(handoff.to_agent, True):
            return HandoffValidationResult(
                is_valid=False,
                reason=f"Target agent '{handoff.to_agent}' is not available",
                suggestions=["Wait for agent to become available", "Choose alternative agent"]
            )
        
        # Check task compatibility
        task_compatibility = self._check_task_compatibility(
            handoff.task_description,
            handoff.to_agent
        )
        if not task_compatibility["is_compatible"]:
            return HandoffValidationResult(
                is_valid=False,
                reason=f"Task '{handoff.task_description}' is not compatible with agent '{handoff.to_agent}'",
                suggestions=task_compatibility["suggestions"]
            )
        
        # Check data transfer validity
        data_validation = self._validate_data_transfer(
            handoff.data_to_transfer,
            handoff.from_agent,
            handoff.to_agent
        )
        if not data_validation["is_valid"]:
            return HandoffValidationResult(
                is_valid=False,
                reason=data_validation['reason'],
                suggestions=data_validation["suggestions"]
            )
        
        return HandoffValidationResult(is_valid=True, reason="Handoff request is valid")
    
    def suggest_alternative_agents(
        self,
        task_description: str,
        exclude_agents: List[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Suggest alternative agents for a task.
        
        Args:
            task_description: Description of the task
            exclude_agents: List of agents to exclude from suggestions
            
        Returns:
            List of (agent_name, confidence_score) tuples
        """
        exclude_agents = exclude_agents or []
        suggestions = []
        
        for agent_name, capabilities in self.agent_capabilities.items():
            if agent_name in exclude_agents:
                continue
            
            # Calculate compatibility score
            score = self._calculate_task_compatibility_score(
                task_description,
                capabilities
            )
            
            if score > 0.05:  # Very low threshold to get more suggestions
                suggestions.append((agent_name, score))
        
        # Sort by score (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions
    
    def create_handoff_request(
        self,
        from_agent: str,
        to_agent: str,
        task_description: str,
        data_to_transfer: Dict[str, Any],
        priority: str = "normal",
        context: Dict[str, Any] = None
    ) -> HandoffRequest:
        """
        Create a handoff request.
        
        Args:
            from_agent: Source agent name
            to_agent: Target agent name
            task_description: Description of the task to handoff
            data_to_transfer: Data to transfer between agents
            priority: Priority level of the handoff
            context: Additional context for the handoff
            
        Returns:
            HandoffRequest object
        """
        handoff_id = f"handoff_{from_agent}_{to_agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return HandoffRequest(
            handoff_id=handoff_id,
            from_agent=from_agent,
            to_agent=to_agent,
            task_description=task_description,
            data_to_transfer=data_to_transfer,
            priority=priority,
            context=context or {},
            status="pending"
        )
    
    def process_handoff_queue(
        self,
        state: AgentState
    ) -> AgentState:
        """
        Process the handoff queue and execute valid handoffs.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with processed handoffs
        """
        handoff_queue = state.get("handoff_queue", [])
        processed_handoffs = []
        
        for handoff_data in handoff_queue:
            try:
                # Convert dict back to HandoffRequest
                handoff = HandoffRequest(**handoff_data)
                
                # Validate handoff
                validation = self.validate_handoff_request(handoff, state)
                
                if validation.is_valid:
                    # Execute handoff
                    state = self._execute_handoff(handoff, state)
                    handoff.status = "completed"
                    handoff.completed_at = datetime.now()
                else:
                    # Mark as failed
                    handoff.status = "failed"
                    handoff.context["failure_reason"] = validation.reason
                
                processed_handoffs.append(handoff)
                
            except Exception as e:
                # Mark as failed due to processing error
                handoff_data["status"] = "failed"
                handoff_data["context"] = {"failure_reason": str(e)}
                processed_handoffs.append(handoff_data)
        
        # Update state
        state["handoff_history"].extend([h.model_dump() if hasattr(h, 'model_dump') else h for h in processed_handoffs])
        state["handoff_queue"] = []
        
        return state
    
    def _check_task_compatibility(
        self,
        task_description: str,
        agent_name: str
    ) -> Dict[str, Any]:
        """Check if a task is compatible with an agent."""
        capabilities = self.agent_capabilities.get(agent_name, {})
        
        # Calculate compatibility score
        score = self._calculate_task_compatibility_score(task_description, capabilities)
        
        is_compatible = score > 0.5  # Threshold for compatibility
        
        suggestions = []
        if not is_compatible:
            # Suggest alternative agents
            alternatives = self.suggest_alternative_agents(task_description, [agent_name])
            if alternatives:
                suggestions.append(f"Consider using: {', '.join([a[0] for a in alternatives[:3]])}")
            else:
                suggestions.append("No suitable agents found for this task")
        
        return {
            "is_compatible": is_compatible,
            "score": score,
            "suggestions": suggestions
        }
    
    def _calculate_task_compatibility_score(
        self,
        task_description: str,
        capabilities: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score between task and agent capabilities."""
        print(f"DEBUG: Calculating score for task: {task_description}")
        print(f"DEBUG: Capabilities: {capabilities}")
        
        task_words = set(task_description.lower().split())
        print(f"DEBUG: Task words: {task_words}")
        
        # Check primary tasks
        primary_tasks = capabilities.get("primary_tasks", [])
        primary_score = 0
        for task in primary_tasks:
            # Check for exact word matches
            task_words_set = set(task.lower().split())
            print(f"DEBUG: Checking primary task '{task}' with words {task_words_set}")
            if task_words & task_words_set:
                primary_score += 0.4
            
            # Check for substring matches (e.g., "architecture_design" in "Design system architecture")
            task_desc_lower = task_description.lower()
            task_lower = task.lower()
            
            # Check if task name is contained in description
            if task_lower in task_desc_lower:
                primary_score += 0.3
                print(f"DEBUG: Found substring match: '{task_lower}' in '{task_desc_lower}'")
            
            # Check if description words are contained in task name
            for word in task_words:
                if word in task_lower:
                    primary_score += 0.2
                    print(f"DEBUG: Found word match: '{word}' in '{task_lower}'")
        
        # Check secondary tasks
        secondary_tasks = capabilities.get("secondary_tasks", [])
        secondary_score = 0
        for task in secondary_tasks:
            task_words_set = set(task.lower().split())
            if task_words & task_words_set:
                secondary_score += 0.2
            
            # Check for substring matches
            task_desc_lower = task_description.lower()
            task_lower = task.lower()
            
            if task_lower in task_desc_lower:
                secondary_score += 0.15
            
            # Check if description words are contained in task name
            for word in task_words:
                if word in task_lower:
                    secondary_score += 0.1
        
        # Check expertise areas
        expertise_areas = capabilities.get("expertise", [])
        expertise_score = 0
        for expertise in expertise_areas:
            expertise_words = set(expertise.lower().split())
            if task_words & expertise_words:
                expertise_score += 0.1
            
            # Check for substring matches
            task_desc_lower = task_description.lower()
            expertise_lower = expertise.lower()
            
            if expertise_lower in task_desc_lower:
                expertise_score += 0.1
            
            # Check if description words are contained in expertise
            for word in task_words:
                if word in expertise_lower:
                    expertise_score += 0.05
        
        total_score = primary_score + secondary_score + expertise_score
        print(f"DEBUG: Final score: {total_score} (primary: {primary_score}, secondary: {secondary_score}, expertise: {expertise_score})")
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _validate_data_transfer(
        self,
        data_to_transfer: Dict[str, Any],
        from_agent: str,
        to_agent: str
    ) -> Dict[str, Any]:
        """Validate data transfer between agents."""
        # Basic validation - check if data is not empty
        if not data_to_transfer:
            return {
                "is_valid": False,
                "reason": "Missing required data types: requirements, project_context",
                "suggestions": ["Include relevant data in the handoff request"]
            }
        
        # Check for required data types based on agent capabilities
        from_capabilities = self.agent_capabilities.get(from_agent, {})
        to_capabilities = self.agent_capabilities.get(to_agent, {})
        
        # Validate that data types are appropriate for target agent
        required_data_types = self._get_required_data_types(to_agent)
        missing_data = []
        
        for data_type in required_data_types:
            if data_type not in data_to_transfer:
                missing_data.append(data_type)
        
        if missing_data:
            return {
                "is_valid": False,
                "reason": f"Missing required data types: {', '.join(missing_data)}",
                "suggestions": [f"Include {data_type} in the handoff data" for data_type in missing_data]
            }
        
        return {"is_valid": True, "reason": "Data transfer is valid", "suggestions": []}
    
    def _get_required_data_types(self, agent_name: str) -> List[str]:
        """Get required data types for an agent."""
        data_requirements = {
            "requirements_analyst": ["project_context"],
            "architecture_designer": ["requirements", "project_context"],
            "code_generator": ["requirements", "architecture", "tech_stack"],
            "test_generator": ["code_files", "requirements"],
            "code_reviewer": ["code_files"],
            "security_analyst": ["code_files", "architecture"],
            "documentation_generator": ["code_files", "requirements", "architecture"]
        }
        
        return data_requirements.get(agent_name, [])
    
    def _execute_handoff(
        self,
        handoff: HandoffRequest,
        state: AgentState
    ) -> AgentState:
        """Execute a handoff between agents."""
        # Update current agent
        state["current_agent"] = handoff.to_agent
        
        # Transfer data
        for key, value in handoff.data_to_transfer.items():
            state[key] = value
        
        # Update collaboration context
        collaboration_context = state.get("collaboration_context", {})
        collaboration_context[f"handoff_{handoff.handoff_id}"] = {
            "from_agent": handoff.from_agent,
            "to_agent": handoff.to_agent,
            "task": handoff.task_description,
            "timestamp": datetime.now().isoformat()
        }
        state["collaboration_context"] = collaboration_context
        
        # Add to workflow history
        workflow_step = {
            "step_id": f"handoff_{handoff.handoff_id}",
            "step_name": "agent_handoff",
            "agent_name": f"{handoff.from_agent}_to_{handoff.to_agent}",
            "input_data": {
                "from_agent": handoff.from_agent,
                "to_agent": handoff.to_agent,
                "task": handoff.task_description
            },
            "output_data": {"status": "completed"},
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        state["workflow_history"].append(workflow_step)
        
        return state


# Global handoff manager instance
handoff_manager = HandoffManager()


# Convenience functions for easy access
def validate_handoff(handoff: HandoffRequest, state: AgentState) -> HandoffValidationResult:
    """Validate a handoff request."""
    return handoff_manager.validate_handoff_request(handoff, state)


def suggest_agents(task_description: str, exclude_agents: List[str] = None) -> List[Tuple[str, float]]:
    """Suggest alternative agents for a task."""
    return handoff_manager.suggest_alternative_agents(task_description, exclude_agents)


def create_handoff(
    from_agent: str,
    to_agent: str,
    task_description: str,
    data_to_transfer: Dict[str, Any],
    priority: str = "normal",
    context: Dict[str, Any] = None
) -> HandoffRequest:
    """Create a handoff request."""
    return handoff_manager.create_handoff_request(
        from_agent, to_agent, task_description, data_to_transfer, priority, context
    )


def process_handoffs(state: AgentState) -> AgentState:
    """Process the handoff queue."""
    return handoff_manager.process_handoff_queue(state)
