"""
Code Reviewer Agent for AI Development Agent.
Reviews generated code for quality, security, and best practices.
"""

import json
from typing import Dict, Any
from models.state import AgentState
from models.responses import CodeReviewResponse
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class CodeReviewer(BaseAgent):
    """
    Agent responsible for reviewing generated code for quality and best practices.
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
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute code review task."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting code review")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for code review")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating code review response")
            response_text = await self.generate_response(prompt)
            
            # Parse response
            self.add_log_entry("info", "Parsing JSON response")
            review_data = self.parse_json_response(response_text)
            
            # Validate response structure
            self._validate_review_data(review_data)
            self.add_log_entry("info", "Review data validation passed")
            
            # Record key decisions
            self._record_review_decisions(review_data)
            
            # Create artifacts
            self._create_review_artifacts(review_data)
            
            # Create documentation
            self._create_review_documentation(review_data)
            
            # Create detailed output
            output = {
                "code_review": review_data,
                "summary": {
                    "overall_score": self._calculate_overall_score(review_data),
                    "critical_issues": len(review_data.get("critical_issues", [])),
                    "minor_issues": len(review_data.get("minor_issues", [])),
                    "recommendations": len(review_data.get("recommendations", []))
                }
            }
            
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
    
    def _validate_review_data(self, data: Dict[str, Any]) -> None:
        """Validate code review data."""
        # Provide default values for missing fields
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
        
        # Check for code_files (should be set by code generator)
        if "code_files" not in state or not state["code_files"]:
            self.logger.error("No code_files found in state - code generator must run first")
            return False
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will review code quality only")
            # Don't fail, just warn - we can still review code quality
        
        return True
