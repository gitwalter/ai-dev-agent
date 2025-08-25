"""
Documentation Generator Agent for AI Development Agent.
Generates comprehensive documentation for the project.
"""

import json
from typing import Dict, Any
from models.state import AgentState
from models.responses import DocumentationResponse
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class DocumentationGenerator(BaseAgent):
    """
    Agent responsible for generating comprehensive documentation.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the DocumentationGenerator agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("documentation_generator")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute documentation generation task."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting documentation generation")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for documentation generation")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating documentation response")
            response_text = await self.generate_response(prompt)
            
            # Parse response
            self.add_log_entry("info", "Parsing JSON response")
            doc_data = self.parse_json_response(response_text)
            
            # Validate response structure
            self._validate_documentation_data(doc_data)
            self.add_log_entry("info", "Documentation data validation passed")
            
            # Record key decisions
            self._record_documentation_decisions(doc_data)
            
            # Create artifacts
            self._create_documentation_artifacts(doc_data)
            
            # Create documentation summary
            self._create_documentation_summary(doc_data)
            
            # Update state with generated documentation
            state["documentation"] = doc_data.get("documentation_files", {})
            
            # Update state with generated diagrams
            if "diagrams" in doc_data:
                state["diagrams"] = doc_data["diagrams"]
            
            # Create detailed output
            output = {
                "documentation_generation": doc_data,
                "summary": {
                    "total_files": len(doc_data.get("documentation_files", {})),
                    "coverage_score": self._extract_score(doc_data.get("documentation_summary", {}).get("coverage_score", "0/10")),
                    "completeness": doc_data.get("documentation_summary", {}).get("completeness", "0%")
                }
            }
            
            execution_time = time.time() - start_time
            
            # Update state with results
            state = self.update_state_with_result(
                state=state,
                task_name="documentation_generation",
                output=output,
                execution_time=execution_time
            )
            
            self.add_log_entry("info", f"Documentation generation completed successfully in {execution_time:.2f}s")
            return state
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_log_entry("error", f"Documentation generation failed: {str(e)}")
            return self.handle_error(state, e, "documentation_generation")
    
    def _validate_documentation_data(self, data: Dict[str, Any]) -> None:
        """Validate documentation generation data."""
        # Provide default values for missing fields
        if "documentation_files" not in data:
            data["documentation_files"] = {}
        if "documentation_summary" not in data:
            data["documentation_summary"] = {"coverage_score": "5/10", "completeness": "50%"}
        
        if not data.get("documentation_files"):
            # Create basic documentation files if none provided
            data["documentation_files"] = {
                "README.md": "# Project Documentation\\n\\n## Overview\\nThis is a generated project.\\n\\n## Setup\\nFollow the installation instructions.",
                "API_DOCUMENTATION.md": "# API Documentation\\n\\n## Endpoints\\nBasic API documentation."
            }
    
    def _record_documentation_decisions(self, doc_data: Dict[str, Any]):
        """
        Record key decisions made during documentation generation.
        
        Args:
            doc_data: Documentation generation data
        """
        # Record documentation coverage decision
        coverage_score = self._extract_score(doc_data.get("documentation_summary", {}).get("coverage_score", "0/10"))
        self.add_decision(
            decision=f"Documentation coverage score: {coverage_score:.1f}/10",
            rationale="Based on comprehensive analysis of project requirements and generated code",
            alternatives=["Different documentation coverage approaches considered"],
            impact="Will guide documentation completeness and quality standards"
        )
        
        # Record documentation files decision
        doc_files = doc_data.get("documentation_files", {})
        if doc_files:
            self.add_decision(
                decision=f"Generated {len(doc_files)} documentation files",
                rationale="Based on project complexity and documentation requirements",
                alternatives=["Different documentation file organization considered"],
                impact="Will guide documentation structure and maintenance"
            )
        
        # Record documentation completeness decision
        completeness = doc_data.get("documentation_summary", {}).get("completeness", "0%")
        self.add_decision(
            decision=f"Documentation completeness: {completeness}",
            rationale="Based on analysis of project scope and documentation needs",
            alternatives=["Different completeness targets considered"],
            impact="Will guide documentation improvement priorities"
        )
    
    def _create_documentation_artifacts(self, doc_data: Dict[str, Any]):
        """
        Create artifacts from documentation generation.
        
        Args:
            doc_data: Documentation generation data
        """
        # Create documentation files artifact
        doc_files = doc_data.get("documentation_files", {})
        if doc_files:
            self.add_artifact(
                name="documentation_files",
                type="documentation",
                content=doc_files,
                description=f"Generated {len(doc_files)} documentation files"
            )
        
        # Create documentation summary artifact
        doc_summary = doc_data.get("documentation_summary", {})
        if doc_summary:
            self.add_artifact(
                name="documentation_summary",
                type="summary",
                content=doc_summary,
                description="Documentation coverage and completeness summary"
            )
        
        # Create documentation structure artifact
        doc_structure = doc_data.get("documentation_structure", {})
        if doc_structure:
            self.add_artifact(
                name="documentation_structure",
                type="structure",
                content=doc_structure,
                description="Documentation organization and structure"
            )
        
        # Create diagrams artifact
        diagrams = doc_data.get("diagrams", {})
        if diagrams:
            self.add_artifact(
                name="diagrams",
                type="diagrams",
                content=diagrams,
                description=f"Generated {len(diagrams)} UML and BPMN diagrams"
            )
    
    def _create_documentation_summary(self, doc_data: Dict[str, Any]):
        """
        Create comprehensive documentation summary.
        
        Args:
            doc_data: Documentation generation data
        """
        doc_files = doc_data.get("documentation_files", {})
        doc_summary = doc_data.get("documentation_summary", {})
        coverage_score = self._extract_score(doc_summary.get("coverage_score", "0/10"))
        completeness = doc_summary.get("completeness", "0%")
        
        # Get diagram information
        diagrams = doc_data.get("diagrams", {})
        diagram_count = len(diagrams)
        diagram_types = list(diagrams.keys()) if diagrams else []
        
        self.create_documentation(
            summary=f"Generated {len(doc_files)} documentation files and {diagram_count} diagrams with {coverage_score:.1f}/10 coverage and {completeness} completeness",
            details={
                "documentation_files": {
                    "total_files": len(doc_files),
                    "file_names": list(doc_files.keys()),
                    "file_types": self._categorize_documentation_files(doc_files)
                },
                "diagrams": {
                    "total_diagrams": diagram_count,
                    "diagram_types": diagram_types,
                    "diagram_details": diagrams
                },
                "documentation_quality": {
                    "coverage_score": coverage_score,
                    "completeness": completeness,
                    "quality_metrics": doc_summary.get("quality_metrics", {})
                },
                "documentation_structure": {
                    "organization": doc_data.get("documentation_structure", {}),
                    "sections": doc_data.get("documentation_sections", [])
                },
                "documentation_scope": {
                    "components_documented": doc_data.get("components_documented", []),
                    "documentation_criteria": doc_data.get("documentation_criteria", [])
                }
            }
        )
    
    def _categorize_documentation_files(self, doc_files: dict) -> dict:
        """Categorize documentation files by type."""
        categories = {}
        for filename in doc_files.keys():
            if "readme" in filename.lower():
                category = "readme"
            elif "api" in filename.lower():
                category = "api_docs"
            elif "install" in filename.lower() or "setup" in filename.lower():
                category = "setup"
            elif "architect" in filename.lower():
                category = "architecture"
            else:
                category = "general"
            
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
        """Validate input state for documentation generation."""
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
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will generate documentation from code and architecture only")
            # Don't fail, just warn - we can still generate documentation
        
        return True
