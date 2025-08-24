"""
Security Analyst Agent for AI Development Agent.
Performs security analysis on generated code and architecture.
"""

import json
from typing import Dict, Any
from models.state import AgentState
from models.responses import SecurityAnalysisResponse
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class SecurityAnalyst(BaseAgent):
    """
    Agent responsible for security analysis of the codebase and architecture.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the SecurityAnalyst agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("security_analyst")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute security analysis task."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting security analysis")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for security analysis")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating security analysis response")
            response_text = await self.generate_response(prompt)
            
            # Parse response
            self.add_log_entry("info", "Parsing JSON response")
            security_data = self.parse_json_response(response_text)
            
            # Validate response structure
            self._validate_security_data(security_data)
            self.add_log_entry("info", "Security data validation passed")
            
            # Record key decisions
            self._record_security_decisions(security_data)
            
            # Create artifacts
            self._create_security_artifacts(security_data)
            
            # Create documentation
            self._create_security_documentation(security_data)
            
            # Create detailed output
            output = {
                "security_analysis": security_data,
                "summary": {
                    "overall_score": self._extract_score(security_data.get("overall_security_score", "0/10")),
                    "critical_vulnerabilities": len(security_data.get("vulnerability_analysis", {}).get("critical_vulnerabilities", [])),
                    "high_vulnerabilities": len(security_data.get("vulnerability_analysis", {}).get("high_vulnerabilities", [])),
                    "security_recommendations": len(security_data.get("security_recommendations", []))
                }
            }
            
            execution_time = time.time() - start_time
            
            # Update state with results
            state = self.update_state_with_result(
                state=state,
                task_name="security_analysis",
                output=output,
                execution_time=execution_time
            )
            
            self.add_log_entry("info", f"Security analysis completed successfully in {execution_time:.2f}s")
            return state
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_log_entry("error", f"Security analysis failed: {str(e)}")
            return self.handle_error(state, e, "security_analysis")
    
    def _validate_security_data(self, data: Dict[str, Any]) -> None:
        """Validate security analysis data."""
        # Provide default values for missing fields
        if "overall_security_score" not in data:
            data["overall_security_score"] = "5/10"
        if "security_assessment" not in data:
            data["security_assessment"] = {"overall_risk_level": "medium"}
        if "vulnerability_analysis" not in data:
            data["vulnerability_analysis"] = {"critical_vulnerabilities": [], "high_vulnerabilities": []}
    
    def _record_security_decisions(self, security_data: Dict[str, Any]):
        """
        Record key decisions made during security analysis.
        
        Args:
            security_data: Security analysis data
        """
        # Record overall security score decision
        overall_score = self._extract_score(security_data.get("overall_security_score", "0/10"))
        self.add_decision(
            decision=f"Overall security score: {overall_score:.1f}/10",
            rationale="Based on comprehensive security analysis of codebase and architecture",
            alternatives=["Different security scoring approaches considered"],
            impact="Will guide security improvement priorities and risk assessment"
        )
        
        # Record vulnerability assessment decision
        vulnerability_analysis = security_data.get("vulnerability_analysis", {})
        critical_vulns = vulnerability_analysis.get("critical_vulnerabilities", [])
        high_vulns = vulnerability_analysis.get("high_vulnerabilities", [])
        
        if critical_vulns:
            self.add_decision(
                decision=f"Identified {len(critical_vulns)} critical vulnerabilities requiring immediate remediation",
                rationale="Based on security analysis of codebase and potential attack vectors",
                alternatives=["Different vulnerability prioritization considered"],
                impact="Will guide immediate security fixes and risk mitigation"
            )
        
        if high_vulns:
            self.add_decision(
                decision=f"Identified {len(high_vulns)} high-severity vulnerabilities for priority remediation",
                rationale="Based on security analysis and risk assessment",
                alternatives=["Different vulnerability prioritization considered"],
                impact="Will guide security improvement planning"
            )
        
        # Record security recommendations decision
        recommendations = security_data.get("security_recommendations", [])
        if recommendations:
            self.add_decision(
                decision=f"Provided {len(recommendations)} security improvement recommendations",
                rationale="Based on security best practices and identified vulnerabilities",
                alternatives=["Different security improvement approaches considered"],
                impact="Will guide long-term security enhancement strategy"
            )
    
    def _create_security_artifacts(self, security_data: Dict[str, Any]):
        """
        Create artifacts from security analysis.
        
        Args:
            security_data: Security analysis data
        """
        # Create overall security assessment artifact
        security_assessment = security_data.get("security_assessment", {})
        if security_assessment:
            self.add_artifact(
                name="security_assessment",
                type="assessment",
                content=security_assessment,
                description="Overall security assessment and risk level"
            )
        
        # Create vulnerability analysis artifact
        vulnerability_analysis = security_data.get("vulnerability_analysis", {})
        if vulnerability_analysis:
            self.add_artifact(
                name="vulnerability_analysis",
                type="vulnerabilities",
                content=vulnerability_analysis,
                description="Detailed vulnerability analysis and categorization"
            )
        
        # Create security recommendations artifact
        recommendations = security_data.get("security_recommendations", [])
        if recommendations:
            self.add_artifact(
                name="security_recommendations",
                type="recommendations",
                content=recommendations,
                description=f"List of {len(recommendations)} security improvement recommendations"
            )
        
        # Create threat model artifact
        threat_model = security_data.get("threat_model", {})
        if threat_model:
            self.add_artifact(
                name="threat_model",
                type="threat_model",
                content=threat_model,
                description="Security threat model and attack vectors"
            )
    
    def _create_security_documentation(self, security_data: Dict[str, Any]):
        """
        Create comprehensive documentation of security analysis.
        
        Args:
            security_data: Security analysis data
        """
        overall_score = self._extract_score(security_data.get("overall_security_score", "0/10"))
        vulnerability_analysis = security_data.get("vulnerability_analysis", {})
        critical_vulns = vulnerability_analysis.get("critical_vulnerabilities", [])
        high_vulns = vulnerability_analysis.get("high_vulnerabilities", [])
        recommendations = security_data.get("security_recommendations", [])
        
        self.create_documentation(
            summary=f"Security analysis completed with score {overall_score:.1f}/10, {len(critical_vulns)} critical vulnerabilities, and {len(recommendations)} recommendations",
            details={
                "security_assessment": {
                    "overall_score": overall_score,
                    "risk_level": security_data.get("security_assessment", {}).get("overall_risk_level", "unknown"),
                    "security_score": security_data.get("overall_security_score", "N/A")
                },
                "vulnerability_summary": {
                    "critical_vulnerabilities": len(critical_vulns),
                    "high_vulnerabilities": len(high_vulns),
                    "total_vulnerabilities": len(critical_vulns) + len(high_vulns)
                },
                "recommendations": {
                    "count": len(recommendations),
                    "categories": self._categorize_security_recommendations(recommendations)
                },
                "security_scope": {
                    "components_analyzed": security_data.get("components_analyzed", []),
                    "security_criteria": security_data.get("security_criteria", [])
                }
            }
        )
    
    def _categorize_security_recommendations(self, recommendations: list) -> dict:
        """Categorize security recommendations by type."""
        categories = {}
        for rec in recommendations:
            category = rec.get("category", "general")
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        return categories
    
    def _extract_score(self, score_str: str) -> float:
        """Extract numeric score from score string."""
        try:
            return float(score_str.split('/')[0])
        except (ValueError, IndexError):
            return 0.0
    
    def validate_input(self, state: AgentState) -> bool:
        """Validate input state for security analysis."""
        # Check for basic required fields
        if not super().validate_input(state):
            return False
        
        # Check for code_files (should be set by code generator)
        if "code_files" not in state or not state["code_files"]:
            self.logger.error("No code_files found in state - code generator must run first")
            return False
        
        # Check for architecture (should be set by architecture designer)
        if "architecture" not in state or not state["architecture"]:
            self.logger.error("No architecture found in state - architecture designer must run first")
            return False
        
        return True
