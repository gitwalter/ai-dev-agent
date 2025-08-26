"""
Code Reviewer Agent for AI Development Agent.
Reviews generated code for quality, security, and best practices.
Implements quality gate functionality to cross-check requirements against code.
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from models.state import AgentState
from models.responses import CodeReviewResponse
from models.simplified_responses import (
    SimplifiedIssue, 
    SimplifiedReviewResponse, 
    create_simplified_review_response
)
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class CodeReviewer(BaseAgent):
    """
    Agent responsible for reviewing generated code for quality and best practices.
    Implements quality gate functionality to ensure all requirements are met.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the CodeReviewer agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("code_reviewer")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    def create_simplified_output(self, parsed_data: Dict[str, Any]) -> SimplifiedReviewResponse:
        """
        Create a simplified review response from parsed data.
        
        Args:
            parsed_data: Parsed JSON data from LLM response
            
        Returns:
            SimplifiedReviewResponse object
        """
        try:
            # Extract overall score
            overall_score = parsed_data.get("overall_score", 7.0)
            if isinstance(overall_score, str):
                try:
                    overall_score = float(overall_score)
                except ValueError:
                    overall_score = 7.0
            
            # Extract issues
            issues = []
            if "issues" in parsed_data:
                for issue_data in parsed_data["issues"]:
                    if isinstance(issue_data, dict):
                        issue = SimplifiedIssue(
                            title=issue_data.get("title", "Unknown Issue"),
                            description=issue_data.get("description", ""),
                            severity=issue_data.get("severity", "medium"),
                            category=issue_data.get("category", "style"),
                            suggestion=issue_data.get("suggestion", "")
                        )
                        issues.append(issue)
            
            # Determine quality gate status
            quality_gate_passed = parsed_data.get("quality_gate_passed", True)
            if overall_score < 6.0:
                quality_gate_passed = False
            
            result = create_simplified_review_response(
                overall_score=overall_score,
                issues=issues,
                quality_gate_passed=quality_gate_passed
            )
            print(f"DEBUG: create_simplified_output - result type: {type(result)}")
            print(f"DEBUG: create_simplified_output - result content: {result}")
            # Convert to dictionary to avoid validation issues
            return result.dict() if hasattr(result, 'dict') else result
            
        except Exception as e:
            self.add_log_entry("warning", f"Failed to create simplified review response: {e}")
            # Return a default response
            default_response = create_simplified_review_response(
                overall_score=5.0,
                issues=[],
                quality_gate_passed=False
            )
            return default_response.dict() if hasattr(default_response, 'dict') else default_response
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute code review task with quality gate functionality."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting code review with quality gate")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for code review")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Perform requirements cross-check
            requirements_check = await self._cross_check_requirements(state)
            
            if not requirements_check["all_requirements_met"]:
                self.add_log_entry("warning", f"Requirements check failed: {requirements_check['missing_requirements']}")
                print("DEBUG: Calling _send_back_to_code_generator")
                return self._send_back_to_code_generator(state, requirements_check)
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating code review response")
            response_text = await self.generate_response(prompt)
            
            # Parse response with direct JSON parsing for simplified response
            self.add_log_entry("info", "Parsing JSON response with simplified models")
            try:
                # Clean the response by removing markdown formatting
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove "```json"
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]  # Remove "```"
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing "```"
                cleaned_response = cleaned_response.strip()
                
                # Direct JSON parsing for simplified response
                parsed_data = json.loads(cleaned_response)
                self.add_log_entry("info", "Successfully parsed JSON directly")
                
                # Create simplified response using the parsed data
                review_data = self.create_simplified_output(parsed_data)
                print(f"DEBUG: review_data type after create_simplified_output: {type(review_data)}")
                print(f"DEBUG: review_data content: {review_data}")
                self.add_log_entry("info", "Successfully created simplified response")
                
            except Exception as parse_error:
                self.add_log_entry("warning", f"Direct JSON parsing failed: {parse_error}")
                # Use fallback parsing as last resort
                review_data = self.parse_json_response(response_text)
            
            # Convert review_data to dictionary first (before any processing)
            if hasattr(review_data, 'dict'):  # SimplifiedReviewResponse object
                review_dict = review_data.dict()
            else:  # Already a dictionary
                review_dict = review_data
            
            # Validate response structure (now working with dictionary)
            self._validate_review_data(review_dict)
            self.add_log_entry("info", "Review data validation passed")
            
            # Record key decisions
            self._record_review_decisions(review_dict)
            
            # Create artifacts
            self._create_review_artifacts(review_dict)
            
            # Create documentation
            self._create_review_documentation(review_dict)
            
            # Create detailed output - always as dictionary
            output = {
                "code_review": review_dict,
                "requirements_check": requirements_check,
                "quality_gate_passed": review_dict.get("quality_gate_passed", True),
                "summary": {
                    "overall_score": review_dict.get("overall_score", 7.0),
                    "critical_issues": len([i for i in review_dict.get("issues", []) if isinstance(i, dict) and i.get("severity") in ['high', 'critical']]),
                    "minor_issues": len([i for i in review_dict.get("issues", []) if isinstance(i, dict) and i.get("severity") in ['low', 'medium']]),
                    "recommendations": len([i for i in review_dict.get("issues", []) if isinstance(i, dict) and i.get("suggestion")]),
                    "requirements_met": requirements_check["all_requirements_met"]
                }
            }
            
            execution_time = time.time() - start_time
            
            # Update state with results
            print(f"DEBUG: output type before update_state_with_result: {type(output)}")
            print(f"DEBUG: output content: {output}")
            
            state = self.update_state_with_result(
                state=state,
                task_name="code_review",
                output=output,
                execution_time=execution_time
            )
            
            self.add_log_entry("info", f"Code review completed successfully in {execution_time:.2f}s")
            return state
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_log_entry("error", f"Code review failed: {str(e)}")
            return self.handle_error(state, e, "code_review")
    
    async def _cross_check_requirements(self, state: AgentState) -> Dict[str, Any]:
        """
        Cross-check generated code against requirements to ensure all requirements are implemented.
        
        Args:
            state: Current agent state
            
        Returns:
            Dictionary with requirements check results
        """
        self.add_log_entry("info", "Starting requirements cross-check")
        
        requirements = state.get("requirements", {})
        code_files = state.get("code_files", {})
        
        # Handle requirements as either list or dict
        if isinstance(requirements, list):
            if not requirements:
                self.add_log_entry("warning", "No requirements found for cross-checking")
                return {
                    "all_requirements_met": True,
                    "missing_requirements": [],
                    "implemented_requirements": [],
                    "check_performed": False,
                    "reason": "No requirements available"
                }
            # Convert list to dict for processing
            requirements_dict = {f"req_{i}": req for i, req in enumerate(requirements)}
        else:
            requirements_dict = requirements
        
        if not requirements_dict:
            self.add_log_entry("warning", "No requirements found for cross-checking")
            return {
                "all_requirements_met": True,
                "missing_requirements": [],
                "implemented_requirements": [],
                "check_performed": False,
                "reason": "No requirements available"
            }
        
        if not code_files:
            self.add_log_entry("error", "No code files found for requirements check")
            return {
                "all_requirements_met": False,
                "missing_requirements": list(requirements_dict.keys()),
                "implemented_requirements": [],
                "check_performed": True,
                "reason": "No code files available"
            }
        
        # Prepare prompt for requirements cross-check
        cross_check_prompt = self._prepare_requirements_cross_check_prompt(requirements_dict, code_files)
        
        try:
            # Generate cross-check response
            response_text = await self.generate_response(cross_check_prompt)
            cross_check_data = self.parse_json_response(response_text)
            
            # Validate cross-check response
            if not self._validate_cross_check_response(cross_check_data):
                raise ValueError("Invalid cross-check response format")
            
            self.add_log_entry("info", f"Requirements cross-check completed: {cross_check_data.get('all_requirements_met', False)}")
            
            return cross_check_data
            
        except Exception as e:
            self.add_log_entry("error", f"Requirements cross-check failed: {str(e)}")
            # Fallback: assume requirements are not met
            return {
                "all_requirements_met": False,
                "missing_requirements": list(requirements_dict.keys()),
                "implemented_requirements": [],
                "check_performed": True,
                "reason": f"Cross-check failed: {str(e)}"
            }
    
    def _prepare_requirements_cross_check_prompt(self, requirements: Dict[str, Any], code_files: Dict[str, str]) -> str:
        """
        Prepare prompt for requirements cross-checking.
        
        Args:
            requirements: Requirements from requirements analyst
            code_files: Generated code files
            
        Returns:
            Formatted prompt for cross-checking
        """
        prompt = f"""
You are a quality gate agent responsible for cross-checking generated code against requirements.

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

GENERATED CODE FILES:
"""
        
        for filename, content in code_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        prompt += """
TASK:
Analyze the generated code against the requirements and determine if all requirements are properly implemented.

RESPONSE FORMAT (JSON):
{
    "all_requirements_met": boolean,
    "implemented_requirements": [
        {
            "requirement_id": "string",
            "requirement_description": "string",
            "implementation_status": "fully_implemented|partially_implemented|not_implemented",
            "evidence": "string describing where/how it's implemented",
            "confidence_score": 0.0-1.0
        }
    ],
    "missing_requirements": [
        {
            "requirement_id": "string",
            "requirement_description": "string",
            "missing_components": ["list of missing features/components"],
            "suggested_implementation": "string describing what needs to be implemented"
        }
    ],
    "quality_assessment": {
        "overall_implementation_quality": "excellent|good|fair|poor",
        "code_coverage": "percentage of requirements covered",
        "critical_gaps": ["list of critical missing features"]
    }
}

CRITERIA:
1. A requirement is considered implemented if the code contains the necessary functionality
2. Check for both functional and non-functional requirements
3. Consider code quality, error handling, and best practices
4. Be thorough but fair in your assessment
5. Provide specific evidence for your conclusions
"""
        
        return prompt
    
    def _validate_cross_check_response(self, data: Dict[str, Any]) -> bool:
        """
        Validate the cross-check response format.
        
        Args:
            data: Cross-check response data
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["all_requirements_met", "implemented_requirements", "missing_requirements"]
        
        for field in required_fields:
            if field not in data:
                self.add_log_entry("error", f"Missing required field in cross-check response: {field}")
                return False
        
        if not isinstance(data["all_requirements_met"], bool):
            self.add_log_entry("error", "all_requirements_met must be a boolean")
            return False
        
        return True
    
    def _send_back_to_code_generator(self, state: AgentState, requirements_check: Dict[str, Any]) -> AgentState:
        """
        Send the workflow back to the code generator with missing requirements information.
        
        Args:
            state: Current agent state
            requirements_check: Results of requirements cross-check
            
        Returns:
            Updated state with reroute information
        """
        self.add_log_entry("info", "Sending workflow back to code generator due to missing requirements")
        
        # Add reroute information to state
        state["reroute_to"] = "code_generator"
        state["reroute_reason"] = "Missing requirements implementation"
        state["missing_requirements"] = requirements_check.get("missing_requirements", [])
        state["quality_gate_failed"] = True
        
        # Add decision about rerouting
        self.add_decision(
            decision="Reroute to code generator due to missing requirements",
            rationale=f"Requirements cross-check found {len(requirements_check.get('missing_requirements', []))} missing requirements",
            alternatives=["Continue with current code", "Request human intervention"],
            impact="Will trigger code regeneration with missing requirements"
        )
        
        # Create artifact for missing requirements
        self.add_artifact(
            name="missing_requirements",
            type="requirements_gap",
            content=requirements_check.get("missing_requirements", []),
            description="Requirements that need to be implemented"
        )
        
        # Update state with quality gate failure
        state = self.update_state_with_result(
            state=state,
            task_name="code_review_quality_gate",
            output={
                "quality_gate_passed": False,
                "requirements_check": requirements_check,
                "reroute_to": "code_generator",
                "missing_requirements": requirements_check.get("missing_requirements", [])
            },
            execution_time=0.0
        )
        
        return state
    
    def _validate_review_data(self, data: Dict[str, Any]) -> None:
        """Validate code review data."""
        # Now data is always a dictionary, so we just need to provide default values for missing fields
        if "overall_assessment" not in data:
            data["overall_assessment"] = {"quality_score": 7, "summary": "Code review completed"}
        if "code_quality_score" not in data:
            data["code_quality_score"] = "7/10"
        if "security_assessment" not in data:
            data["security_assessment"] = {"security_score": "6/10"}
    
    def _record_review_decisions(self, review_data: Dict[str, Any]):
        """
        Record key decisions made during code review.
        
        Args:
            review_data: Code review data
        """
        # Record overall assessment decision
        overall_score = self._calculate_overall_score(review_data)
        self.add_decision(
            decision=f"Overall code quality score: {overall_score:.1f}/10",
            rationale="Based on comprehensive code review including quality, security, and best practices",
            alternatives=["Different scoring approaches considered"],
            impact="Will guide code improvement priorities and quality standards"
        )
        
        # Record critical issues decision
        critical_issues = review_data.get("critical_issues", [])
        if critical_issues:
            self.add_decision(
                decision=f"Identified {len(critical_issues)} critical issues requiring immediate attention",
                rationale="Based on security and quality analysis of the codebase",
                alternatives=["Different issue prioritization considered"],
                impact="Will guide immediate code improvements and security fixes"
            )
        
        # Record recommendations decision
        recommendations = review_data.get("recommendations", [])
        if recommendations:
            self.add_decision(
                decision=f"Provided {len(recommendations)} improvement recommendations",
                rationale="Based on best practices and code quality analysis",
                alternatives=["Different improvement approaches considered"],
                impact="Will guide long-term code quality improvements"
            )
    
    def _create_review_artifacts(self, review_data: Dict[str, Any]):
        """
        Create artifacts from code review.
        
        Args:
            review_data: Code review data
        """
        # Create overall assessment artifact
        overall_assessment = review_data.get("overall_assessment", {})
        if overall_assessment:
            self.add_artifact(
                name="overall_assessment",
                type="assessment",
                content=overall_assessment,
                description="Overall code quality assessment"
            )
        
        # Create critical issues artifact
        critical_issues = review_data.get("critical_issues", [])
        if critical_issues:
            self.add_artifact(
                name="critical_issues",
                type="issues",
                content=critical_issues,
                description=f"List of {len(critical_issues)} critical issues"
            )
        
        # Create minor issues artifact
        minor_issues = review_data.get("minor_issues", [])
        if minor_issues:
            self.add_artifact(
                name="minor_issues",
                type="issues",
                content=minor_issues,
                description=f"List of {len(minor_issues)} minor issues"
            )
        
        # Create recommendations artifact
        recommendations = review_data.get("recommendations", [])
        if recommendations:
            self.add_artifact(
                name="recommendations",
                type="recommendations",
                content=recommendations,
                description=f"List of {len(recommendations)} improvement recommendations"
            )
    
    def _create_review_documentation(self, review_data: Dict[str, Any]):
        """
        Create comprehensive documentation of code review.
        
        Args:
            review_data: Code review data
        """
        overall_score = self._calculate_overall_score(review_data)
        critical_issues = review_data.get("critical_issues", [])
        minor_issues = review_data.get("minor_issues", [])
        recommendations = review_data.get("recommendations", [])
        
        self.create_documentation(
            summary=f"Code review completed with overall score {overall_score:.1f}/10, {len(critical_issues)} critical issues, and {len(recommendations)} recommendations",
            details={
                "quality_assessment": {
                    "overall_score": overall_score,
                    "code_quality_score": review_data.get("code_quality_score", "N/A"),
                    "security_score": review_data.get("security_assessment", {}).get("security_score", "N/A")
                },
                "issues_summary": {
                    "critical_issues": len(critical_issues),
                    "minor_issues": len(minor_issues),
                    "total_issues": len(critical_issues) + len(minor_issues)
                },
                "recommendations": {
                    "count": len(recommendations),
                    "categories": self._categorize_recommendations(recommendations)
                },
                "review_scope": {
                    "files_reviewed": review_data.get("files_reviewed", []),
                    "review_criteria": review_data.get("review_criteria", [])
                }
            }
        )
    
    def _categorize_recommendations(self, recommendations: list) -> dict:
        """Categorize recommendations by type."""
        categories = {}
        for rec in recommendations:
            category = rec.get("category", "general")
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        return categories
    
    def _calculate_overall_score(self, review_data: Dict[str, Any]) -> float:
        """Calculate overall code quality score."""
        scores = []
        
        # Extract scores from different assessments
        if "code_quality_score" in review_data:
            try:
                scores.append(float(review_data["code_quality_score"].split('/')[0]))
            except (ValueError, IndexError):
                pass
                
        if "security_assessment" in review_data and "security_score" in review_data["security_assessment"]:
            try:
                scores.append(float(review_data["security_assessment"]["security_score"].split('/')[0]))
            except (ValueError, IndexError):
                pass
                
        if "performance_assessment" in review_data and "performance_score" in review_data["performance_assessment"]:
            try:
                scores.append(float(review_data["performance_assessment"]["performance_score"].split('/')[0]))
            except (ValueError, IndexError):
                pass
                
        if "maintainability" in review_data and "score" in review_data["maintainability"]:
            try:
                scores.append(float(review_data["maintainability"]["score"].split('/')[0]))
            except (ValueError, IndexError):
                pass
                
        return sum(scores) / len(scores) if scores else 0.0
    
    def validate_input(self, state: AgentState) -> bool:
        """Validate input state for code review."""
        # Check for basic required fields
        if not super().validate_input(state):
            return False
        
        # Check for code files (should be set by code generator)
        # Support both old format (code_files) and new format (source_files + configuration_files)
        code_files = state.get("code_files", {})
        source_files = state.get("source_files", {})
        configuration_files = state.get("configuration_files", {})
        
        # Check if we have any code files in any format
        if not code_files and not source_files and not configuration_files:
            self.logger.error("No code files found in state - code generator must run first")
            return False
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will review code only")
            # Don't fail, just warn - we can still review code
        
        return True
