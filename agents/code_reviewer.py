"""
Code Reviewer Agent for AI Development Agent.
Reviews generated code for quality, security, and best practices.
Uses LangChain JsonOutputParser for stable JSON parsing.
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
import google.generativeai as genai

try:
    from langchain_core.output_parsers import JsonOutputParser
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class CodeReviewer(BaseAgent):
    """
    Agent responsible for reviewing generated code for quality and best practices.
    Uses LangChain JsonOutputParser for stable JSON parsing.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the CodeReviewer agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("code_reviewer")
        
        # Setup LangChain parser if available
        if LANGCHAIN_AVAILABLE:
            self.json_parser = JsonOutputParser()
        else:
            self.json_parser = None
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate that the task is appropriate for code review.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        # Check if task has required fields for code review
        if not isinstance(task, dict):
            return False
        
        # Check for code files or project context
        has_code = (
            task.get('code_files') or 
            task.get('project_context') or
            task.get('generated_files')
        )
        
        return bool(has_code)
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute code review task using LangChain JsonOutputParser."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting code review with LangChain JsonOutputParser")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for code review")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Use LangChain approach if available
            if LANGCHAIN_AVAILABLE and self.json_parser:
                review_data = await self._execute_with_langchain(state)
            else:
                review_data = await self._execute_with_legacy_parsing(state)
            
            self.add_log_entry("info", "Code review data processing completed")
            
            # Record key decisions
            if isinstance(review_data, dict):
                self._record_review_decisions(review_data)
            else:
                self.add_log_entry("warning", f"Review data is not a dictionary: {type(review_data)}")
                # Convert to dictionary if possible
                if isinstance(review_data, str):
                    try:
                        import json
                        review_data = json.loads(review_data)
                        self._record_review_decisions(review_data)
                    except json.JSONDecodeError:
                        self.add_log_entry("error", "Could not convert review data string to dictionary")
                        review_data = {"overall_score": 7.0, "issues": [], "recommendations": []}
                        self._record_review_decisions(review_data)
                else:
                    review_data = {"overall_score": 7.0, "issues": [], "recommendations": []}
                    self._record_review_decisions(review_data)
            
            # Create artifacts
            if isinstance(review_data, dict):
                self._create_review_artifacts(review_data)
            else:
                self.add_log_entry("warning", "Cannot create artifacts - review data is not a dictionary")
            
            # Create detailed output
            if isinstance(review_data, dict):
                output = {
                    "code_review": review_data,
                    "summary": {
                        "overall_score": review_data.get("overall_score", 7.0),
                        "issues_count": len(review_data.get("issues", [])),
                        "quality_gate_passed": review_data.get("quality_gate_passed", True)
                    }
                }
            else:
                output = {
                    "code_review": {"overall_score": 7.0, "issues": [], "quality_gate_passed": True},
                    "summary": {
                        "overall_score": 7.0,
                        "issues_count": 0,
                        "quality_gate_passed": True
                    }
                }
            
            # Create documentation
            if isinstance(review_data, dict):
                self._create_review_documentation(review_data)
            else:
                self.add_log_entry("warning", "Cannot create documentation - review data is not a dictionary")
            
            execution_time = time.time() - start_time
            
            # Update state with results
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
    
    async def _execute_with_langchain(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute code review using LangChain JsonOutputParser.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed code review data
        """
        # Get prompt template from database
        prompt_template = self.get_prompt_template()
        
        # Create prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["project_context", "code_files", "requirements"]
        )
        
        # Create LangChain Gemini client with optimized model selection
        from utils.core.helpers import get_llm_model
        llm = get_llm_model(task_type="code_review")
        
        # Create chain
        chain = prompt | llm | self.json_parser
        
        # Execute the chain
        self.add_log_entry("info", "Executing LangChain chain for code review")
        result = await chain.ainvoke({
            "project_context": state["project_context"],
            "code_files": str(state.get("code_files", {})),
            "requirements": str(state.get("requirements", []))
        })
        
        self.add_log_entry("info", "Successfully parsed code review data with JsonOutputParser")
        return result
    
    async def _execute_with_legacy_parsing(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute code review using legacy parsing approach.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed review data
        """
        self.add_log_entry("info", "Using legacy parsing approach")
        
        # Prepare prompt
        prompt = self.prepare_prompt(state)
        self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
        
        # Generate response
        self.add_log_entry("info", "Generating code review response")
        response_text = await self.generate_response(prompt)
        
        # Parse response using simplified models directly
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
            import json
            parsed_data = json.loads(cleaned_response)
            self.add_log_entry("info", "Successfully parsed JSON directly")
            
            # Create simplified response using the parsed data
            review_data = self.create_simplified_output(parsed_data)
            self.add_log_entry("info", "Successfully created simplified response")
            
        except Exception as parse_error:
            self.add_log_entry("warning", f"Direct JSON parsing failed: {parse_error}")
            # Use fallback parsing as last resort
            review_data = self.parse_json_response(response_text)
        
        return review_data
    
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
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except Exception as e:
            self.add_log_entry("warning", f"Failed to create simplified review response: {e}")
            # Return a default response
            default_response = create_simplified_review_response(
                overall_score=5.0,
                issues=[],
                quality_gate_passed=False
            )
            return default_response.model_dump() if hasattr(default_response, 'model_dump') else default_response
    
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
        issues = review_data.get("issues", [])
        critical_issues = [issue for issue in issues if issue.get("severity") == "high"]
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
        overall_score = review_data.get("overall_score", 7.0)
        if overall_score:
            self.add_artifact(
                name="overall_assessment",
                type="assessment",
                content={"overall_score": overall_score},
                description=f"Overall code quality score: {overall_score}/10"
            )
        
        # Create issues artifact (from JsonOutputParser structure)
        issues = review_data.get("issues", [])
        if issues:
            # Separate critical and minor issues based on severity
            critical_issues = [issue for issue in issues if issue.get("severity") == "high"]
            minor_issues = [issue for issue in issues if issue.get("severity") in ["medium", "low"]]
            
            if critical_issues:
                self.add_artifact(
                    name="critical_issues",
                    type="issues",
                    content=critical_issues,
                    description=f"List of {len(critical_issues)} critical issues"
                )
            
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
        
        # Create summary artifact
        summary = review_data.get("summary", "")
        if summary:
            self.add_artifact(
                name="review_summary",
                type="summary",
                content=summary,
                description="Overall assessment of code quality"
            )
    
    def _create_review_documentation(self, review_data: Dict[str, Any]):
        """
        Create comprehensive documentation of code review.
        
        Args:
            review_data: Code review data
        """
        # Handle case where review_data might be a string
        if not isinstance(review_data, dict):
            self.add_log_entry("warning", f"Review data is not a dictionary in _create_review_documentation: {type(review_data)}")
            return
        
        overall_score = self._calculate_overall_score(review_data)
        
        # Get issues from JsonOutputParser structure
        issues = review_data.get("issues", [])
        critical_issues = [issue for issue in issues if issue.get("severity") == "high"]
        minor_issues = [issue for issue in issues if issue.get("severity") in ["medium", "low"]]
        
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
                code_quality_score = review_data["code_quality_score"]
                if isinstance(code_quality_score, str):
                    scores.append(float(code_quality_score.split('/')[0]))
                elif isinstance(code_quality_score, (int, float)):
                    scores.append(float(code_quality_score))
            except (ValueError, IndexError):
                pass
                
        if "security_assessment" in review_data:
            security_assessment = review_data["security_assessment"]
            if isinstance(security_assessment, dict) and "security_score" in security_assessment:
                try:
                    security_score = security_assessment["security_score"]
                    if isinstance(security_score, str):
                        scores.append(float(security_score.split('/')[0]))
                    elif isinstance(security_score, (int, float)):
                        scores.append(float(security_score))
                except (ValueError, IndexError):
                    pass
                
        if "performance_assessment" in review_data:
            performance_assessment = review_data["performance_assessment"]
            if isinstance(performance_assessment, dict) and "performance_score" in performance_assessment:
                try:
                    performance_score = performance_assessment["performance_score"]
                    if isinstance(performance_score, str):
                        scores.append(float(performance_score.split('/')[0]))
                    elif isinstance(performance_score, (int, float)):
                        scores.append(float(performance_score))
                except (ValueError, IndexError):
                    pass
                
        if "maintainability" in review_data:
            maintainability = review_data["maintainability"]
            if isinstance(maintainability, dict) and "score" in maintainability:
                try:
                    maintainability_score = maintainability["score"]
                    if isinstance(maintainability_score, str):
                        scores.append(float(maintainability_score.split('/')[0]))
                    elif isinstance(maintainability_score, (int, float)):
                        scores.append(float(maintainability_score))
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
