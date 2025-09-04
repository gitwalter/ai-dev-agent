"""
Documentation Generator Agent for AI Development Agent.
Generates comprehensive documentation for the project.
Uses LangChain JsonOutputParser for stable JSON parsing.
"""

import json
from typing import Dict, Any, List, Optional
from models.state import AgentState
from models.responses import DocumentationResponse
from models.simplified_responses import (
    SimplifiedDocument, 
    SimplifiedDocumentationResponse, 
    create_simplified_documentation_response
)
from ..core.base_agent import BaseAgent
from prompts import get_agent_prompt_loader
import google.generativeai as genai

try:
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class DocumentationGenerator(BaseAgent):
    """
    Agent responsible for generating comprehensive documentation.
    Uses LangChain JsonOutputParser for stable JSON parsing.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the DocumentationGenerator agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("documentation_generator")
        
        # Setup LangChain parser if available
        if LANGCHAIN_AVAILABLE:
            self.json_parser = JsonOutputParser()
        else:
            self.json_parser = None
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate that the task is appropriate for documentation generation.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        if not isinstance(task, dict):
            return False
        
        # Check for code files, project context, or architecture
        has_content = (
            task.get('code_files') or 
            task.get('project_context') or
            task.get('architecture') or
            task.get('requirements')
        )
        
        return bool(has_content)
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute documentation generation task using LangChain JsonOutputParser."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting documentation generation with LangChain JsonOutputParser")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for documentation generation")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Use LangChain approach if available
            if LANGCHAIN_AVAILABLE and self.json_parser:
                documentation_data = await self._execute_with_langchain(state)
            else:
                documentation_data = await self._execute_with_legacy_parsing(state)
            
            self.add_log_entry("info", "Documentation data processing completed")
            
            # Create artifacts
            self._create_documentation_artifacts(documentation_data)
            
            # Create detailed output
            output = {
                "documentation": documentation_data,
                "summary": {
                    "documents_count": len(documentation_data.get("documents", [])),
                    "coverage_score": documentation_data.get("coverage_score", 8.0),
                    "documentation_gate_passed": documentation_data.get("documentation_gate_passed", True)
                }
            }
            
            # Create documentation
            self._create_documentation_files(documentation_data)
            
            # Update state with documentation files
            documents = documentation_data.get("documents", [])
            if documents:
                # Convert documents to filename: content mapping for state
                documentation_files = {}
                for doc in documents:
                    filename = doc.get("filename", "document.md")
                    content = doc.get("content", "")
                    doc_type = doc.get("doc_type", "general")
                    documentation_files[filename] = {
                        "content": content,
                        "doc_type": doc_type,
                        "audience": doc.get("audience", "developers"),
                        "format": doc.get("format", "markdown")
                    }
                state["documentation"] = documentation_files
            else:
                state["documentation"] = {}
            
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
    
    async def _execute_with_langchain(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute documentation generation using LangChain JsonOutputParser.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed documentation data
        """
        # Get prompt template from database
        prompt_template = self.get_prompt_template()
        
        # Create prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["project_context", "code_files", "requirements", "architecture"]
        )
        
        # Create LangChain Gemini client with optimized model selection
        from utils.core.helpers import get_llm_model
        llm = get_llm_model(task_type="documentation")
        
        # Create chain with JsonOutputParser
        chain = prompt | llm | self.json_parser
        
        # Execute the chain
        self.add_log_entry("info", "Executing LangChain chain for documentation generation")
        result = await chain.ainvoke({
            "project_context": state["project_context"],
            "code_files": str(state.get("code_files", {})),
            "requirements": str(state.get("requirements", [])),
            "architecture": str(state.get("architecture", {}))
        })
        
        self.add_log_entry("info", "Successfully parsed documentation data with JsonOutputParser")
        return result
    
    async def _execute_with_legacy_parsing(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute documentation generation using legacy parsing approach.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed documentation data
        """
        self.add_log_entry("info", "Using legacy parsing approach")
        
        # Prepare prompt
        prompt = self.prepare_prompt(state)
        self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
        
        # Generate response
        self.add_log_entry("info", "Generating documentation response")
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
            documentation_data = self.create_simplified_output(parsed_data)
            self.add_log_entry("info", "Successfully created simplified response")
            
        except Exception as parse_error:
            self.add_log_entry("warning", f"Direct JSON parsing failed: {parse_error}")
            # Use fallback parsing as last resort
            documentation_data = self.parse_json_response(response_text)
        
        return documentation_data
    
    def _validate_documentation_data(self, data: Dict[str, Any]) -> None:
        """Validate documentation generation data."""
        # Provide default values for missing fields
        if "documentation_files" not in data:
            data["documentation_files"] = {}
        if "documentation_summary" not in data:
            data["documentation_summary"] = {"coverage_score": "5/10", "completeness": "50%"}
        if "diagrams" not in data:
            data["diagrams"] = {}
        
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
    
    def _create_documentation_files(self, documentation_data: Dict[str, Any]):
        """
        Create and save documentation files to the project directory.
        
        Args:
            documentation_data: Documentation generation data
        """
        documents = documentation_data.get("documents", [])
        
        if not documents:
            self.add_log_entry("warning", "No documentation files to create")
            return
        
        # Create docs directory if it doesn't exist
        import os
        docs_dir = os.path.join("generated_projects", "test-task-management", "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        # Create documentation files
        created_files = []
        for doc in documents:
            try:
                filename = doc.get("filename", "document.md")
                content = doc.get("content", "")
                doc_type = doc.get("doc_type", "general")
                
                # Create the documentation file
                file_path = os.path.join(docs_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                created_files.append(filename)
                self.add_log_entry("info", f"Created documentation file: {filename} ({doc_type})")
                
            except Exception as e:
                self.add_log_entry("error", f"Failed to create documentation file {filename}: {e}")
        
        if created_files:
            self.add_log_entry("info", f"Successfully created {len(created_files)} documentation files")
        else:
            self.add_log_entry("warning", "No documentation files were created successfully")
    
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
            self.logger.error("Basic validation failed - missing project_context or project_name")
            return False
        
        # Check for code files (should be set by code generator)
        # Support both old format (code_files) and new format (source_files + configuration_files)
        code_files = state.get("code_files", {})
        source_files = state.get("source_files", {})
        configuration_files = state.get("configuration_files", {})
        
        # Log what we found for debugging
        self.logger.info(f"Documentation generator validation - code_files: {len(code_files)}, source_files: {len(source_files) if source_files else 0}, configuration_files: {len(configuration_files) if configuration_files else 0}")
        
        # Check if we have any code files in any format
        if not code_files and not source_files and not configuration_files:
            self.logger.error("No code files found in state - code generator must run first and generate code successfully")
            self.logger.error(f"Available state keys: {list(state.keys())}")
            self.logger.error(f"Agent outputs: {list(state.get('agent_outputs', {}).keys())}")
            return False
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will generate documentation from code only")
            # Don't fail, just warn - we can still generate documentation
        
        self.logger.info("Documentation generator validation passed")
        return True
