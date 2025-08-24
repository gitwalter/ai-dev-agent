"""
Code Generator Agent for AI Development Agent.
Generates code based on architecture and requirements.
"""

import json
from typing import Dict, Any
from models.state import AgentState
from models.responses import CodeGenerationResponse
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader
from utils.output_parsers import OutputParserFactory


class CodeGenerator(BaseAgent):
    """
    Agent responsible for generating code based on architecture and requirements.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the CodeGenerator agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("code_generator")
        # Initialize the parser with format instructions
        self.parser = OutputParserFactory.get_parser("code_generator")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    def prepare_prompt(self, state: AgentState) -> str:
        """
        Prepare the prompt with LangChain format instructions.
        
        Args:
            state: Current agent state
            
        Returns:
            Formatted prompt string
        """
        # Get the base prompt template
        base_prompt = self.get_prompt_template()
        
        # Get format instructions from LangChain parser
        format_instructions = self.parser.get_format_instructions()
        
        # Format the base prompt with state data
        formatted_prompt = base_prompt.format(
            project_name=state.get("project_name", "Unknown Project"),
            project_context=state.get("project_context", ""),
            architecture=state.get("architecture", {}),
            tech_stack=state.get("tech_stack", {}),
            requirements=state.get("requirements", [])
        )
        
        # Add the format instructions to ensure proper JSON output
        final_prompt = f"""{formatted_prompt}

{format_instructions}

CRITICAL: You must respond with ONLY the JSON object as specified above. Do not include any text before or after the JSON. Ensure all strings are properly escaped and the JSON is valid."""
        
        return final_prompt
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute code generation task."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting code generation")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if not self.validate_input(state):
                    raise ValueError("Invalid input state for code generation")
                
                self.add_log_entry("info", "Input validation passed")
                
                # Prepare prompt
                prompt = self.prepare_prompt(state)
                self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
                
                # Add retry-specific instructions for better JSON formatting
                if attempt > 0:
                    prompt += f"\n\nRETRY ATTEMPT {attempt + 1}: Please ensure the JSON is properly formatted with no unterminated strings or unclosed brackets. Double-check all quotes and braces."
                    self.add_log_entry("info", f"Retry attempt {attempt + 1} with enhanced formatting instructions")
                
                # Generate response
                self.add_log_entry("info", "Generating code response")
                response_text = await self.generate_response(prompt)
                
                # Parse response
                self.add_log_entry("info", "Parsing JSON response")
                code_data = self.parser.parse_with_fallback(response_text)
                
                # Validate and update state with generated code
                try:
                    self._validate_code_data(code_data)
                    self.add_log_entry("info", "Code data validation passed")
                    
                    # Record key decisions
                    self._record_code_decisions(code_data)
                    
                    # Create artifacts
                    self._create_code_artifacts(code_data)
                    
                    # Update state
                    state["code_files"] = code_data.get("source_files", {})
                    state["configuration_files"] = code_data.get("configuration_files", {})
                    state["database_schema"] = code_data.get("database_schema", {})
                    state["source_code"] = code_data.get("source_files", {})
                except Exception as validation_error:
                    self.add_log_entry("warning", f"Validation failed, using fallback code: {str(validation_error)}")
                    # Use the comprehensive fallback from the parser
                    fallback_data = self.parser._get_comprehensive_default_output()
                    state["code_files"] = fallback_data.get("source_files", {})
                    state["configuration_files"] = fallback_data.get("configuration_files", {})
                    state["database_schema"] = {}
                    state["source_code"] = fallback_data.get("source_files", {})
                
                # Create documentation
                self._create_code_documentation(code_data)
                
                output = {
                    "code_generation": code_data,
                    "summary": {
                        "total_files": len(code_data.get("source_files", {})) + len(code_data.get("configuration_files", {})),
                        "source_files": len(code_data.get("source_files", {})),
                        "config_files": len(code_data.get("configuration_files", {})),
                        "project_structure": code_data.get("project_structure", [])
                    }
                }
                
                execution_time = time.time() - start_time
                
                # Update state with results
                state = self.update_state_with_result(
                    state=state,
                    task_name="code_generation",
                    output=output,
                    execution_time=execution_time
                )
                
                self.add_log_entry("info", f"Code generation completed successfully in {execution_time:.2f}s")
                return state
                
            except Exception as e:
                self.logger.error(f"Code generation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    # Last attempt failed, return error state
                    return self.handle_error(state, e, "code_generation")
                else:
                    # Wait before retrying
                    import asyncio
                    await asyncio.sleep(2)
        
        # This should never be reached, but just in case
        return self.handle_error(state, Exception("All retry attempts failed"), "code_generation")
    
    def _record_code_decisions(self, code_data: Dict[str, Any]):
        """
        Record key decisions made during code generation.
        
        Args:
            code_data: Code generation data
        """
        # Record file structure decisions
        source_files = code_data.get("source_files", {})
        config_files = code_data.get("configuration_files", {})
        
        if source_files:
            self.add_decision(
                decision=f"Generated {len(source_files)} source files",
                rationale="Based on architecture design and requirements analysis",
                alternatives=["Different file structure considered"],
                impact="Will guide implementation and maintenance approach"
            )
        
        if config_files:
            self.add_decision(
                decision=f"Generated {len(config_files)} configuration files",
                rationale="Based on technology stack and deployment requirements",
                alternatives=["Different configuration approach considered"],
                impact="Will guide deployment and configuration management"
            )
        
        # Record project structure decisions
        project_structure = code_data.get("project_structure", [])
        if project_structure:
            self.add_decision(
                decision=f"Organized code into {len(project_structure)} directories",
                rationale="Based on best practices and project complexity",
                alternatives=["Different directory structure considered"],
                impact="Will influence code organization and maintainability"
            )
    
    def _create_code_artifacts(self, code_data: Dict[str, Any]):
        """
        Create artifacts from code generation.
        
        Args:
            code_data: Code generation data
        """
        # Create source files artifact
        source_files = code_data.get("source_files", {})
        if source_files:
            self.add_artifact(
                name="source_files",
                type="source_code",
                content=source_files,
                description=f"Generated {len(source_files)} source code files"
            )
        
        # Create configuration files artifact
        config_files = code_data.get("configuration_files", {})
        if config_files:
            self.add_artifact(
                name="configuration_files",
                type="configuration",
                content=config_files,
                description=f"Generated {len(config_files)} configuration files"
            )
        
        # Create project structure artifact
        project_structure = code_data.get("project_structure", [])
        if project_structure:
            self.add_artifact(
                name="project_structure",
                type="structure",
                content=project_structure,
                description="Project directory structure"
            )
        
        # Create database schema artifact
        db_schema = code_data.get("database_schema", {})
        if db_schema:
            self.add_artifact(
                name="database_schema",
                type="schema",
                content=db_schema,
                description="Database schema definition"
            )
    
    def _create_code_documentation(self, code_data: Dict[str, Any]):
        """
        Create comprehensive documentation of code generation.
        
        Args:
            code_data: Code generation data
        """
        source_files = code_data.get("source_files", {})
        config_files = code_data.get("configuration_files", {})
        project_structure = code_data.get("project_structure", [])
        
        self.create_documentation(
            summary=f"Generated {len(source_files)} source files and {len(config_files)} configuration files",
            details={
                "file_counts": {
                    "source_files": len(source_files),
                    "configuration_files": len(config_files),
                    "total_files": len(source_files) + len(config_files)
                },
                "project_structure": {
                    "directories": len(project_structure),
                    "structure": project_structure
                },
                "key_files": {
                    "main_files": [f for f in source_files.keys() if "main" in f.lower() or "app" in f.lower()],
                    "config_files": list(config_files.keys())
                },
                "implementation_notes": code_data.get("implementation_notes", []),
                "deployment_instructions": code_data.get("deployment_instructions", [])
            }
        )
    
    def _validate_code_data(self, data: Dict[str, Any]) -> None:
        """Validate code generation data."""
        required_fields = ["source_files", "configuration_files"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in code data: {field}")
        
        if not data.get("source_files"):
            raise ValueError("No source files generated")
    
    def validate_input(self, state: AgentState) -> bool:
        """Validate input state for code generation."""
        # Check for basic required fields
        if not super().validate_input(state):
            return False
        
        # Check for architecture (should be set by architecture designer)
        if "architecture" not in state or not state["architecture"]:
            self.logger.error("No architecture found in state - architecture designer must run first")
            return False
        
        # Check for tech_stack (should be set by architecture designer)
        if "tech_stack" not in state or not state["tech_stack"]:
            self.logger.error("No tech_stack found in state - architecture designer must run first")
            return False
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will use architecture data only")
            # Don't fail, just warn - we can still generate code from architecture
        
        return True
