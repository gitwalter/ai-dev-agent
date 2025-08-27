"""
Architecture Designer Agent for AI Development Agent.
Designs system architecture based on requirements.
Uses LangChain JsonOutputParser for stable JSON parsing.
"""

import json
from typing import Dict, Any, Optional
from models.state import AgentState
from models.responses import ArchitectureDesignResponse
from models.simplified_responses import SimplifiedComponent, SimplifiedArchitectureResponse, create_simplified_architecture_response
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader
import google.generativeai as genai

try:
    from langchain_core.output_parsers import JsonOutputParser
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class ArchitectureDesigner(BaseAgent):
    """
    Agent responsible for designing system architecture.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the ArchitectureDesigner agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("architecture_designer")
        
        # Setup LangChain parser if available
        if LANGCHAIN_AVAILABLE:
            self.json_parser = JsonOutputParser()
        else:
            self.json_parser = None
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    def prepare_prompt(self, state: AgentState) -> str:
        """
        Prepare the prompt with detailed context for architecture design.
        
        Args:
            state: Current agent state
            
        Returns:
            Formatted prompt string
        """
        # Get the base prompt template
        base_prompt = self.get_prompt_template()
        
        # Add detailed context information
        context_info = []
        
        # Add project context
        if state.get("project_context"):
            context_info.append(f"PROJECT CONTEXT:\n{state.get('project_context')}")
        
        # Add requirements details
        requirements = state.get("requirements", [])
        if requirements:
            context_info.append("REQUIREMENTS TO ADDRESS:")
            for i, req in enumerate(requirements, 1):
                if isinstance(req, dict):
                    context_info.append(f"{i}. {req.get('requirement_description', str(req))}")
                    if req.get('requirement_type'):
                        context_info.append(f"   Type: {req['requirement_type']}")
                    if req.get('priority'):
                        context_info.append(f"   Priority: {req['priority']}")
                else:
                    context_info.append(f"{i}. {req}")
        
        # Add user stories if available
        user_stories = state.get("user_stories", [])
        if user_stories:
            context_info.append("USER STORIES:")
            for i, story in enumerate(user_stories[:5], 1):  # Limit to first 5
                if isinstance(story, dict):
                    context_info.append(f"{i}. {story.get('story', str(story))}")
                else:
                    context_info.append(f"{i}. {story}")
        
        # Add project name and type
        project_name = state.get("project_name", "Unknown Project")
        context_info.append(f"PROJECT NAME: {project_name}")
        
        # Combine all context
        if context_info:
            formatted_prompt = base_prompt + "\n\n" + "\n\n".join(context_info)
        else:
            formatted_prompt = base_prompt
        
        return formatted_prompt
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute architecture design task using LangChain JsonOutputParser."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting architecture design with LangChain JsonOutputParser")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for architecture design")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Use LangChain approach if available
            if LANGCHAIN_AVAILABLE and self.json_parser:
                architecture_data = await self._execute_with_langchain(state)
            else:
                architecture_data = await self._execute_with_legacy_parsing(state)
            
            self.add_log_entry("info", "Architecture data processing completed")
            
            # Record key decisions
            self._record_architecture_decisions(architecture_data)
            
            # Create artifacts
            self._create_architecture_artifacts(architecture_data)
            
            # Update state
            state["architecture"] = architecture_data
            
            # Also set tech_stack for compatibility with code generator
            tech_stack = architecture_data.get("technology_stack", {})
            if tech_stack:
                state["tech_stack"] = tech_stack
            
            # Create detailed output
            output = {
                "architecture_design": architecture_data,
                "summary": {
                    "components_count": len(architecture_data.get("components", [])),
                    "layers_count": len(architecture_data.get("layers", [])),
                    "technologies_count": len(architecture_data.get("technologies", [])),
                    "patterns_count": len(architecture_data.get("design_patterns", []))
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
    
    async def _execute_with_langchain(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute architecture design using LangChain JsonOutputParser.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed architecture data
        """
        # Get prompt template from database
        prompt_template = self.get_prompt_template()
        
        # Create prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["project_context", "requirements"]
        )
        
        # Create LangChain Gemini client
        import streamlit as st
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=st.secrets["GEMINI_API_KEY"],
            temperature=0.1,
            max_output_tokens=8192
        )
        
        # Create chain
        chain = prompt | llm | self.json_parser
        
        # Execute the chain
        self.add_log_entry("info", "Executing LangChain chain for architecture design")
        result = await chain.ainvoke({
            "project_context": state["project_context"],
            "requirements": str(state.get("requirements", []))
        })
        
        self.add_log_entry("info", "Successfully parsed architecture with JsonOutputParser")
        return result
    
    async def _execute_with_legacy_parsing(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute architecture design using legacy parsing approach.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed architecture data
        """
        self.add_log_entry("info", "Using legacy parsing approach")
        
        # Prepare prompt
        prompt = self.prepare_prompt(state)
        self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
        
        # Generate response
        self.add_log_entry("info", "Generating architecture design response")
        response_text = await self.generate_response(prompt)
        
        # Parse response using simplified models directly
        self.add_log_entry("info", "Parsing JSON response with simplified models")
        
        # Parse JSON directly without using the old structured output parser
        try:
            # Find JSON in the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                architecture_data = json.loads(json_str)
                self.add_log_entry("info", "Successfully parsed JSON directly")
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            self.add_log_entry("error", f"Failed to parse JSON directly: {e}")
            # Fall back to old parser
            architecture_data = self.parse_json_response(response_text)
        
        # Create simplified response
        try:
            simplified_response = self.create_architecture_response(architecture_data)
            architecture_data = simplified_response.dict()
            self.add_log_entry("info", "Successfully created simplified response")
        except Exception as e:
            self.add_log_entry("warning", f"Failed to create simplified response: {e}")
            # Fall back to validation of original format
            self._validate_architecture_data(architecture_data)
        
        return architecture_data
    
    def _validate_architecture_data(self, data: Dict[str, Any]) -> None:
        """Validate architecture design data and provide fallback values."""
        self.add_log_entry("info", f"Validating architecture data with keys: {list(data.keys())}")
        
        # Define required fields with fallback values
        required_fields = {
            "system_overview": {
                "description": "High-level system description",
                "architecture_type": "web_application",
                "deployment_model": "cloud_based"
            },
            "architecture_pattern": "layered",
            "components": [],
            "technology_stack": {
                "frontend": ["HTML", "CSS", "JavaScript"],
                "backend": ["Python", "Flask"],
                "database": ["SQLite"],
                "deployment": ["Docker"]
            }
        }
        
        # Check and provide fallbacks for missing fields
        for field, fallback_value in required_fields.items():
            if field not in data or not data[field]:
                self.add_log_entry("warning", f"Missing or empty field '{field}' in architecture data, using fallback")
                data[field] = fallback_value
            else:
                self.add_log_entry("info", f"Field '{field}' found in architecture data")
        
        # Additional quality checks for better architecture
        if isinstance(data.get("components"), list) and len(data["components"]) < 3:
            self.add_log_entry("warning", "Very few components defined, adding basic components")
            # Add some basic components if too few are defined
            basic_components = [
                {"name": "User Management", "responsibility": "Handle user authentication and authorization"},
                {"name": "Data Access Layer", "responsibility": "Handle database operations and data persistence"},
                {"name": "API Gateway", "responsibility": "Handle external API requests and routing"}
            ]
            data["components"].extend(basic_components[:3 - len(data["components"])])
        
        # Check for generic technology choices
        tech_stack = data.get("technology_stack", {})
        if isinstance(tech_stack, dict):
            for category, techs in tech_stack.items():
                if isinstance(techs, list):
                    # Check for generic choices like just "Python" or "JavaScript"
                    generic_techs = ["python", "javascript", "java", "database", "web server"]
                    if any(tech.lower() in generic_techs for tech in techs):
                        self.add_log_entry("warning", f"Generic technology choices detected in {category}, consider more specific options")
        
        # Ensure system_overview has sufficient detail
        system_overview = data.get("system_overview", {})
        if isinstance(system_overview, dict) and len(str(system_overview)) < 100:
            self.add_log_entry("warning", "System overview is too brief, consider adding more detail")
        
        # Ensure components is a list
        if not isinstance(data.get("components"), list):
            self.add_log_entry("warning", "Components field is not a list, converting to empty list")
            data["components"] = []
        
        # Ensure technology_stack is a dict
        if not isinstance(data.get("technology_stack"), dict):
            self.add_log_entry("warning", "Technology stack field is not a dict, using fallback")
            data["technology_stack"] = required_fields["technology_stack"]
        
        self.add_log_entry("info", "Architecture data validation completed with fallbacks applied")
    
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
    
    def create_simplified_architecture_response(self, data: Dict[str, Any]) -> SimplifiedArchitectureResponse:
        """
        Create a SimplifiedArchitectureResponse from the architecture data.
        
        Args:
            data: Architecture design data
            
        Returns:
            SimplifiedArchitectureResponse object
        """
        # Convert components to simplified format
        components = []
        for comp in data.get("components", []):
            components.append(SimplifiedComponent(
                name=comp.get("name", "Unnamed Component"),
                description=comp.get("description", ""),
                technology=comp.get("technology", "Unknown"),
                responsibilities=comp.get("responsibilities", [])
            ))
        
        return create_simplified_architecture_response(
            architecture_type=data.get("architecture_pattern", "layered"),
            components=components,
            technology_stack=data.get("technology_stack", {}),
            security_measures=data.get("security_considerations", []),
            deployment_approach=data.get("deployment_strategy", ""),
            quality_gate_passed=data.get("quality_gate_passed", True)
        )

    def create_simplified_output(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a simplified output from the architecture design.
        
        Args:
            output: Original output data
            
        Returns:
            Simplified output data
        """
        try:
            simplified_response = self.create_simplified_architecture_response(output)
            return simplified_response.dict()
        except Exception as e:
            self.logger.error(f"Failed to create simplified architecture output: {e}")
            return None

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
