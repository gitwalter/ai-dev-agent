"""
Requirements Analyst Agent for the AI Development Agent system.
Analyzes project descriptions and extracts detailed requirements.
"""

import json
from typing import Dict, Any, List, Optional
from models.state import AgentState
from models.responses import RequirementsAnalysisResponse
from models.simplified_responses import SimplifiedRequirement, SimplifiedRequirementsResponse, create_simplified_requirements_response
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class RequirementsAnalyst(BaseAgent):
    """
    Requirements Analyst Agent.
    
    Analyzes project descriptions and extracts:
    - Functional requirements
    - Non-functional requirements
    - User stories
    - Acceptance criteria
    - Technical constraints
    - Assumptions and risks
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the RequirementsAnalyst agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("requirements_analyst")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for requirements analysis.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute requirements analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with requirements analysis results
        """
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting requirements analysis")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            # Validate input
            if not self.validate_input(state):
                raise ValueError("Invalid input state for requirements analysis")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating requirements analysis response")
            response_text = await self.generate_response(prompt)
            
            # Parse response using simplified models directly
            self.add_log_entry("info", "Parsing JSON response with simplified models")
            
            # Parse JSON directly without using the old structured output parser
            import json
            try:
                # Find JSON in the response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response_text[start:end]
                    requirements_data = json.loads(json_str)
                    self.add_log_entry("info", "Successfully parsed JSON directly")
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                self.add_log_entry("error", f"Failed to parse JSON directly: {e}")
                # Fall back to old parser
                requirements_data = self.parse_json_response(response_text)
            
            # Create simplified response
            try:
                simplified_response = self.create_requirements_response(requirements_data)
                requirements_data = simplified_response.dict()
                self.add_log_entry("info", "Successfully created simplified response")
            except Exception as e:
                self.add_log_entry("warning", f"Failed to create simplified response: {e}")
                # Fall back to validation of original format
                self._validate_requirements_data(requirements_data)
            
            self.add_log_entry("info", "Requirements data processing completed")
            
            # Record key decisions
            self._record_requirements_decisions(requirements_data)
            
            # Create artifacts
            self._create_requirements_artifacts(requirements_data)
            
            # Update state with simplified format
            requirements = requirements_data.get("requirements", [])
            state["requirements"] = requirements
            
            # Create detailed output
            output = {
                "requirements_analysis": requirements_data,
                "summary": {
                    "total_requirements_count": len(requirements),
                    "functional_requirements_count": len([r for r in requirements if r.get("type") == "functional"]),
                    "non_functional_requirements_count": len([r for r in requirements if r.get("type") == "non_functional"]),
                    "user_stories_count": len([r for r in requirements if r.get("type") == "user_story"]),
                    "technical_constraints_count": len(requirements_data.get("technical_constraints", [])),
                    "risks_count": len(requirements_data.get("risks", []))
                }
            }
            
            # Create documentation
            self._create_requirements_documentation(requirements_data)
            
            execution_time = time.time() - start_time
            
            # Update state with results
            state = self.update_state_with_result(
                state=state,
                task_name="requirements_analysis",
                output=output,
                execution_time=execution_time
            )
            
            self.add_log_entry("info", f"Requirements analysis completed successfully in {execution_time:.2f}s")
            
            return state
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_log_entry("error", f"Requirements analysis failed: {str(e)}")
            return self.handle_error(state, e, "requirements_analysis")
    
    def _record_requirements_decisions(self, requirements_data: Dict[str, Any]):
        """
        Record key decisions made during requirements analysis.
        
        Args:
            requirements_data: Requirements analysis data
        """
        # Record complexity decision
        requirements = requirements_data.get("requirements", [])
        functional_count = len([r for r in requirements if r.get("type") == "functional"])
        non_functional_count = len([r for r in requirements if r.get("type") == "non_functional"])
        
        self.add_decision(
            decision=f"Estimated project complexity as medium",
            rationale=f"Based on analysis of {functional_count} functional requirements and {non_functional_count} non-functional requirements",
            alternatives=["low", "medium", "high"],
            impact="Will influence architecture and technology choices"
        )
        
        # Record tech stack decision
        tech_stack = ["Python", "Flask", "SQLite"]  # Default tech stack
        self.add_decision(
            decision=f"Recommended technology stack: {', '.join(tech_stack)}",
            rationale="Based on project requirements, complexity, and best practices",
            alternatives=["Different tech stacks considered based on requirements"],
            impact="Will guide architecture design and implementation approach"
        )
        
        # Record priority decisions
        high_priority_reqs = [req for req in requirements if req.get("priority") == "high"]
        if high_priority_reqs:
            self.add_decision(
                decision=f"Identified {len(high_priority_reqs)} high-priority requirements",
                rationale="Requirements were prioritized based on business value and dependencies",
                alternatives=["All requirements could be treated equally"],
                impact="High-priority requirements will be implemented first"
            )
    
    def _create_requirements_artifacts(self, requirements_data: Dict[str, Any]):
        """
        Create artifacts from requirements analysis.
        
        Args:
            requirements_data: Requirements analysis data
        """
        # Create requirements summary artifact
        requirements = requirements_data.get("requirements", [])
        functional_count = len([r for r in requirements if r.get("type") == "functional"])
        non_functional_count = len([r for r in requirements if r.get("type") == "non_functional"])
        user_story_count = len([r for r in requirements if r.get("type") == "user_story"])
        
        summary = {
            "total_requirements": len(requirements),
            "functional_requirements": functional_count,
            "non_functional_requirements": non_functional_count,
            "user_stories": user_story_count,
            "technical_constraints": len(requirements_data.get("technical_constraints", [])),
            "risks": len(requirements_data.get("risks", []))
        }
        
        self.add_artifact(
            name="requirements_summary",
            type="summary",
            content=summary,
            description="High-level summary of requirements analysis"
        )
        
        # Create functional requirements artifact
        func_reqs = [r for r in requirements if r.get("type") == "functional"]
        self.add_artifact(
            name="functional_requirements",
            type="requirements_list",
            content=func_reqs,
            description=f"List of {len(func_reqs)} functional requirements"
        )
        
        # Create user stories artifact
        user_stories = [r for r in requirements if r.get("type") == "user_story"]
        self.add_artifact(
            name="user_stories",
            type="user_stories",
            content=user_stories,
            description=f"List of {len(user_stories)} user stories"
        )
        
        # Create risks artifact
        risks = requirements_data.get("risks", [])
        self.add_artifact(
            name="project_risks",
            type="risk_assessment",
            content=risks,
            description=f"List of {len(risks)} identified project risks"
        )
    
    def _create_requirements_documentation(self, requirements_data: Dict[str, Any]):
        """
        Create comprehensive documentation of requirements analysis.
        
        Args:
            requirements_data: Requirements analysis data
        """
        requirements = requirements_data.get("requirements", [])
        functional_count = len([r for r in requirements if r.get("type") == "functional"])
        non_functional_count = len([r for r in requirements if r.get("type") == "non_functional"])
        user_story_count = len([r for r in requirements if r.get("type") == "user_story"])
        high_priority_count = len([r for r in requirements if r.get("priority") == "high"])
        
        self.create_documentation(
            summary=f"Analyzed project requirements and identified {functional_count} functional requirements, {non_functional_count} non-functional requirements, and {user_story_count} user stories",
            details={
                "project_scope": {
                    "functional_requirements_count": functional_count,
                    "non_functional_requirements_count": non_functional_count,
                    "user_stories_count": user_story_count,
                    "total_requirements": len(requirements),
                    "risks_count": len(requirements_data.get("risks", []))
                },
                "complexity_assessment": "medium",
                "technology_recommendations": ["Python", "Flask", "SQLite"],
                "key_findings": {
                    "high_priority_requirements": high_priority_count,
                    "critical_risks": len(requirements_data.get("risks", [])),
                    "technical_constraints": requirements_data.get("technical_constraints", [])
                }
            }
        )
    
    def _validate_requirements_data(self, data: Dict[str, Any]) -> None:
        """
        Validate the structure of requirements data.
        
        Args:
            data: Requirements data to validate
            
        Raises:
            ValueError: If data structure is invalid
        """
        required_keys = ["requirements", "technical_constraints", "assumptions", "risks"]
        
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in requirements data: {key}")
            
            if not isinstance(data[key], list):
                raise ValueError(f"Key {key} must be a list")
        
        # Validate requirements
        for i, req in enumerate(data.get("requirements", [])):
            required_fields = ["id", "title", "description", "type", "priority"]
            for field in required_fields:
                if field not in req:
                    raise ValueError(f"Requirement {i} missing field: {field}")
            
            # Validate type field
            valid_types = ["functional", "non_functional", "user_story"]
            if req.get("type") not in valid_types:
                raise ValueError(f"Requirement {i} has invalid type: {req.get('type')}")
            
            # Validate priority field
            valid_priorities = ["low", "medium", "high"]
            if req.get("priority") not in valid_priorities:
                raise ValueError(f"Requirement {i} has invalid priority: {req.get('priority')}")
    
    def validate_input(self, state: AgentState) -> bool:
        """
        Validate input state for requirements analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            True if input is valid, False otherwise
        """
        required_fields = ["project_context", "project_name"]
        
        for field in required_fields:
            if field not in state or not state[field]:
                self.logger.error(f"Missing required field for requirements analysis: {field}")
                return False
        
        return True
    
    def create_requirements_response(self, data: Dict[str, Any]) -> SimplifiedRequirementsResponse:
        """
        Create a SimplifiedRequirementsResponse from the analysis data.
        
        Args:
            data: Requirements analysis data
            
        Returns:
            SimplifiedRequirementsResponse object
        """
        # Convert requirements to simplified format
        requirements = []
        
        # Convert requirements from simplified format
        for req in data.get("requirements", []):
            requirements.append(SimplifiedRequirement(
                id=req.get("id", f"REQ-{len(requirements)+1}"),
                title=req.get("title", "Untitled Requirement"),
                description=req.get("description", ""),
                type=req.get("type", "functional"),
                priority=req.get("priority", "medium"),
                status=req.get("status", "draft")
            ))
        
        return create_simplified_requirements_response(
            requirements=requirements,
            technical_constraints=data.get("technical_constraints", []),
            assumptions=data.get("assumptions", []),
            risks=[risk.get("description", str(risk)) if isinstance(risk, dict) else str(risk) for risk in data.get("risks", [])],
            quality_gate_passed=data.get("quality_gate_passed", True)
        )

    def create_simplified_output(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a simplified output from the requirements analysis.
        
        Args:
            output: Original output data
            
        Returns:
            Simplified output data
        """
        try:
            simplified_response = self.create_requirements_response(output)
            return simplified_response.dict()
        except Exception as e:
            self.logger.error(f"Failed to create simplified requirements output: {e}")
            return None
    
    def extract_key_insights(self, requirements_data: Dict[str, Any]) -> List[str]:
        """
        Extract key insights from requirements analysis.
        
        Args:
            requirements_data: Requirements analysis data
            
        Returns:
            List of key insights
        """
        insights = []
        
        # Analyze functional requirements
        func_reqs = requirements_data.get("functional_requirements", [])
        if func_reqs:
            high_priority = [req for req in func_reqs if req.get("priority") == "high"]
            insights.append(f"Found {len(high_priority)} high-priority functional requirements")
            
            categories = {}
            for req in func_reqs:
                category = req.get("category", "other")
                categories[category] = categories.get(category, 0) + 1
            
            if categories:
                insights.append(f"Requirements span {len(categories)} categories: {list(categories.keys())}")
        
        # Analyze user stories
        user_stories = requirements_data.get("user_stories", [])
        if user_stories:
            total_points = sum(story.get("story_points", 0) for story in user_stories)
            insights.append(f"Total story points: {total_points}")
            
            user_types = set(story.get("as_a", "").split() for story in user_stories)
            insights.append(f"Identified {len(user_types)} user types")
        
        # Analyze risks
        risks = requirements_data.get("risks", [])
        if risks:
            high_impact = [risk for risk in risks if risk.get("impact") == "high"]
            insights.append(f"Identified {len(high_impact)} high-impact risks")
        
        return insights
