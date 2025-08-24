"""
Architecture Designer Agent for AI Development Agent.
Designs system architecture based on requirements.
"""

import json
from typing import Dict, Any
from models.state import AgentState
from models.responses import ArchitectureDesignResponse
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class ArchitectureDesigner(BaseAgent):
    """
    Agent responsible for designing system architecture.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the ArchitectureDesigner agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("architecture_designer")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute architecture design task."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting architecture design")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for architecture design")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating architecture design response")
            response_text = await self.generate_response(prompt)
            
            # Parse response
            self.add_log_entry("info", "Parsing JSON response")
            architecture_data = self.parse_json_response(response_text)
            
            # Validate response structure
            self._validate_architecture_data(architecture_data)
            self.add_log_entry("info", "Architecture data validation passed")
            
            # Record key decisions
            self._record_architecture_decisions(architecture_data)
            
            # Create artifacts
            self._create_architecture_artifacts(architecture_data)
            
            # Update state
            state["architecture"] = architecture_data
            state["tech_stack"] = architecture_data.get("technology_stack", {})
            
            # Create detailed output
            output = {
                "architecture_design": architecture_data,
                "summary": {
                    "pattern": architecture_data.get("architecture_pattern"),
                    "components_count": len(architecture_data.get("components", [])),
                    "tech_stack_summary": self._summarize_tech_stack(architecture_data.get("technology_stack", {}))
                }
            }
            
            # Create documentation
            self._create_architecture_documentation(architecture_data)
            
            execution_time = time.time() - start_time
            
            # Update state with results
            state = self.update_state_with_result(
                state=state,
                task_name="architecture_design",
                output=output,
                execution_time=execution_time
            )
            
            self.add_log_entry("info", f"Architecture design completed successfully in {execution_time:.2f}s")
            
            return state
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_log_entry("error", f"Architecture design failed: {str(e)}")
            return self.handle_error(state, e, "architecture_design")
    
    def _validate_architecture_data(self, data: Dict[str, Any]) -> None:
        """Validate architecture design data."""
        required_fields = ["system_overview", "architecture_pattern", "components", "technology_stack"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in architecture data: {field}")
    
    def _summarize_tech_stack(self, tech_stack: Dict[str, Any]) -> Dict[str, int]:
        """Create a summary of the technology stack."""
        summary = {}
        for category, technologies in tech_stack.items():
            if isinstance(technologies, list):
                summary[category] = len(technologies)
            else:
                summary[category] = 0
        return summary
    
    def _record_architecture_decisions(self, architecture_data: Dict[str, Any]):
        """
        Record key decisions made during architecture design.
        
        Args:
            architecture_data: Architecture design data
        """
        # Record architecture pattern decision
        pattern = architecture_data.get("architecture_pattern", "unknown")
        self.add_decision(
            decision=f"Selected architecture pattern: {pattern}",
            rationale=f"Based on project requirements and complexity analysis",
            alternatives=["monolithic", "microservices", "layered", "event-driven"],
            impact="Will influence system design and technology choices"
        )
        
        # Record technology stack decisions
        tech_stack = architecture_data.get("technology_stack", {})
        if tech_stack:
            for category, technologies in tech_stack.items():
                if isinstance(technologies, list) and technologies:
                    self.add_decision(
                        decision=f"Selected {category}: {', '.join(technologies)}",
                        rationale=f"Based on architecture requirements and best practices for {category}",
                        alternatives=["Different technologies considered based on requirements"],
                        impact=f"Will guide {category} implementation approach"
                    )
        
        # Record component decisions
        components = architecture_data.get("components", [])
        if components:
            self.add_decision(
                decision=f"Designed {len(components)} system components",
                rationale="Components identified based on functional requirements and architecture pattern",
                alternatives=["Different component breakdown considered"],
                impact="Will guide implementation and integration approach"
            )
    
    def _create_architecture_artifacts(self, architecture_data: Dict[str, Any]):
        """
        Create artifacts from architecture design.
        
        Args:
            architecture_data: Architecture design data
        """
        # Create architecture overview artifact
        overview = architecture_data.get("system_overview", {})
        self.add_artifact(
            name="architecture_overview",
            type="overview",
            content=overview,
            description="High-level system architecture overview"
        )
        
        # Create components artifact
        components = architecture_data.get("components", [])
        self.add_artifact(
            name="system_components",
            type="components_list",
            content=components,
            description=f"List of {len(components)} system components"
        )
        
        # Create technology stack artifact
        tech_stack = architecture_data.get("technology_stack", {})
        self.add_artifact(
            name="technology_stack",
            type="tech_stack",
            content=tech_stack,
            description="Selected technology stack for implementation"
        )
        
        # Create architecture diagram artifact
        diagram = architecture_data.get("architecture_diagram", {})
        if diagram:
            self.add_artifact(
                name="architecture_diagram",
                type="diagram",
                content=diagram,
                description="System architecture diagram"
            )
    
    def _create_architecture_documentation(self, architecture_data: Dict[str, Any]):
        """
        Create comprehensive documentation of architecture design.
        
        Args:
            architecture_data: Architecture design data
        """
        components = architecture_data.get("components", [])
        tech_stack = architecture_data.get("technology_stack", {})
        
        self.create_documentation(
            summary=f"Designed system architecture with {len(components)} components using {architecture_data.get('architecture_pattern', 'unknown')} pattern",
            details={
                "architecture_pattern": architecture_data.get("architecture_pattern", "unknown"),
                "components_count": len(components),
                "technology_categories": len(tech_stack),
                "key_decisions": {
                    "pattern_selection": architecture_data.get("architecture_pattern", "unknown"),
                    "component_breakdown": len(components),
                    "tech_stack_selection": len(tech_stack)
                },
                "design_principles": architecture_data.get("design_principles", []),
                "scalability_considerations": architecture_data.get("scalability_considerations", [])
            }
        )
    
    def validate_input(self, state: AgentState) -> bool:
        """Validate input state for architecture design."""
        # Check for basic required fields
        if not super().validate_input(state):
            return False
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will proceed with basic architecture")
            # Don't fail, just warn - we can still design basic architecture
        
        return True
