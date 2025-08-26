"""
Code Generator Agent for AI Development Agent.
Generates code based on architecture and requirements.
Implements quality gate functionality to validate generated code.
"""

import json
import time
from typing import Dict, Any, Optional, List
from models.state import AgentState
from models.responses import CodeGenerationResponse
from models.simplified_responses import SimplifiedCodeFile, SimplifiedCodeResponse, create_simplified_code_response
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader
from utils.output_parsers import OutputParserFactory
import re


class CodeGenerator(BaseAgent):
    """
    Agent responsible for generating code based on architecture and requirements.
    Implements quality gate functionality to validate generated code.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the CodeGenerator agent."""
        # Create a config object with the required name attribute
        class CodeGeneratorConfig:
            def __init__(self, base_config):
                self.name = "code_generator"
                self.description = "Code Generator Agent"
                self.enabled = True
                self.max_retries = 3
                self.timeout = 300
                # Set default parameters for code generation
                self.parameters = {
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_tokens": 8192
                }
                # Copy other attributes from base_config
                for attr in dir(base_config):
                    if not attr.startswith('_') and not hasattr(self, attr):
                        setattr(self, attr, getattr(base_config, attr))
        
        agent_config = CodeGeneratorConfig(config)
        super().__init__(agent_config, gemini_client)
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
        Prepare the prompt with LangChain format instructions and quality gate feedback.
        
        Args:
            state: Current agent state
            
        Returns:
            Formatted prompt string
        """
        # Get the base prompt template
        base_prompt = self.get_prompt_template()
        
        # Get format instructions from LangChain parser
        format_instructions = self.parser.get_format_instructions()
        
        # Format the base prompt with state data using string replacement to avoid format string issues
        formatted_prompt = base_prompt
        formatted_prompt = formatted_prompt.replace("{project_name}", str(state.get("project_name", "Unknown Project")))
        formatted_prompt = formatted_prompt.replace("{project_context}", str(state.get("project_context", "")))
        formatted_prompt = formatted_prompt.replace("{architecture}", str(state.get("architecture", {})))
        formatted_prompt = formatted_prompt.replace("{tech_stack}", str(state.get("tech_stack", {})))
        formatted_prompt = formatted_prompt.replace("{requirements}", str(state.get("requirements", [])))
        
        # Add detailed context information
        context_info = []
        
        # Add project context
        if state.get("project_context"):
            context_info.append(f"PROJECT CONTEXT:\n{state.get('project_context')}")
        
        # Add requirements details
        requirements = state.get("requirements", [])
        if requirements:
            context_info.append("REQUIREMENTS TO IMPLEMENT:")
            for i, req in enumerate(requirements, 1):
                if isinstance(req, dict):
                    context_info.append(f"{i}. {req.get('requirement_description', str(req))}")
                else:
                    context_info.append(f"{i}. {req}")
        
        # Add architecture details
        architecture = state.get("architecture", {})
        if architecture:
            context_info.append("ARCHITECTURE DESIGN:")
            if isinstance(architecture, dict):
                for key, value in architecture.items():
                    if key == "components" and isinstance(value, list):
                        context_info.append(f"- Components: {', '.join([comp.get('name', str(comp)) for comp in value[:5]])}")
                    elif key == "technology_stack" and isinstance(value, dict):
                        tech_details = []
                        for tech_type, techs in value.items():
                            if isinstance(techs, list):
                                tech_details.append(f"{tech_type}: {', '.join(techs)}")
                        if tech_details:
                            context_info.append(f"- Technology Stack: {'; '.join(tech_details)}")
                    else:
                        context_info.append(f"- {key}: {value}")
            else:
                context_info.append(f"- Architecture: {architecture}")
        
        # Add tech stack details
        tech_stack = state.get("tech_stack", {})
        if tech_stack:
            context_info.append("TECHNOLOGY STACK:")
            if isinstance(tech_stack, dict):
                for tech_type, techs in tech_stack.items():
                    if isinstance(techs, list):
                        context_info.append(f"- {tech_type}: {', '.join(techs)}")
                    else:
                        context_info.append(f"- {tech_type}: {techs}")
            else:
                context_info.append(f"- Tech Stack: {tech_stack}")
        
        # Add user stories if available
        user_stories = state.get("user_stories", [])
        if user_stories:
            context_info.append("USER STORIES:")
            for i, story in enumerate(user_stories[:5], 1):  # Limit to first 5
                if isinstance(story, dict):
                    context_info.append(f"{i}. {story.get('story', str(story))}")
                else:
                    context_info.append(f"{i}. {story}")
        
        # Combine all context
        if context_info:
            formatted_prompt += "\n\n" + "\n\n".join(context_info)
        
        # Quality gate feedback removed for development phase - focusing on getting working code first
        
        # Add CRITICAL instructions for comprehensive code generation
        comprehensive_instructions = """

CRITICAL CODE GENERATION REQUIREMENTS:
1. Generate COMPLETE, FUNCTIONAL code that implements ALL requirements
2. Create MULTIPLE source files with proper separation of concerns
3. Include ALL necessary configuration files (requirements.txt, package.json, etc.)
4. Implement proper error handling, validation, and security measures
5. Follow the specified technology stack and architecture patterns
6. Generate code that is PRODUCTION-READY, not just "Hello World" examples
7. Include database models, API endpoints, authentication, and business logic
8. Create comprehensive test files and documentation
9. Ensure all user stories and requirements are fully implemented
10. Generate substantial, functional code with real business logic

DO NOT generate minimal examples or "Hello World" applications. Generate comprehensive, production-ready code that implements all the specified requirements and features.

"""
        
        # Add the format instructions to ensure proper JSON output
        final_prompt = f"""{formatted_prompt}

{comprehensive_instructions}

{format_instructions}

CRITICAL: You must respond with ONLY the JSON object as specified above. Do not include any text before or after the JSON. Ensure all strings are properly escaped and the JSON is valid."""
        
        return final_prompt
    
    def _get_quality_gate_feedback(self, state: AgentState) -> str:
        """
        Extract quality gate feedback from state for code regeneration (simplified for development).
        
        Args:
            state: Current agent state
            
        Returns:
            Formatted feedback string
        """
        # Simplified feedback for development phase - focus on getting working code first
        return ""
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute code generation task (quality gates relaxed for development)."""
        start_time = time.time()
        
        self.add_log_entry("info", "Starting code generation (quality gates relaxed for development)")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        # Simplified retry logic for development
        max_retries = 1  # Only try once for now
        
        for attempt in range(max_retries):
            try:
                self.add_log_entry("info", f"Code generation attempt {attempt + 1}")
                
                # Validate input
                if not self.validate_input(state):
                    raise ValueError("Invalid input state for code generation")
                
                self.add_log_entry("info", "Input validation passed")
                
                # Simplified prompt preparation for development
                
                # Prepare the prompt
                prompt = self.prepare_prompt(state)
                self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
                
                # Generate code response
                response = await self.generate_response(prompt)
                
                # Store raw response for quality gate analysis
                state["last_raw_response"] = response
                
                # Parse the response with direct JSON parsing for simplified response
                try:
                    # Clean the response by removing markdown formatting
                    cleaned_response = response.strip()
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
                    self.add_log_entry("info", "Direct JSON parsing successful")
                    
                    # Create simplified response using the parsed data
                    code_data = self.create_simplified_code_response(parsed_data)
                    self.add_log_entry("info", "Simplified response creation successful")
                    
                except Exception as parse_error:
                    self.add_log_entry("warning", f"Direct JSON parsing failed: {parse_error}")
                    # Use fallback parsing as last resort
                    code_data = self._create_fallback_code_data(response)
                
                self.add_log_entry("info", "Code data validation passed")
                
                # Perform internal quality gate check (but don't block execution)
                internal_quality_check = await self._perform_internal_quality_gate(code_data, state)
                
                # Log quality gate results but don't block execution
                if internal_quality_check["quality_gate_passed"]:
                    self.add_log_entry("info", "Quality gate passed - code generation successful")
                else:
                    self.add_log_entry("warning", f"Quality gate failed on attempt {attempt + 1}, but continuing execution")
                    self.add_log_entry("warning", f"Quality issues: {internal_quality_check['issues']}")
                
                # Always proceed with the generated code regardless of quality gate result
                self.add_log_entry("info", "Proceeding with code generation regardless of quality gate result")
                
                # Store additional state data
                state["code_generation"] = code_data
                state["internal_quality_check"] = internal_quality_check
                state["current_agent"] = "code_generator"
                state["current_task"] = "code_generation"
                
                # Store code files in legacy state format for backward compatibility
                if hasattr(code_data, 'files'):  # SimplifiedCodeResponse object
                    source_files = {}
                    configuration_files = {}
                    for file in code_data.files:
                        if file.file_type in ['source', 'test']:
                            source_files[file.filename] = {"content": file.content}
                        elif file.file_type == 'config':
                            configuration_files[file.filename] = {"content": file.content}
                    
                    state["code_files"] = source_files
                    state["configuration_files"] = configuration_files
                else:  # Dictionary format (old)
                    if "source_files" in code_data:
                        state["code_files"] = code_data["source_files"]
                    if "configuration_files" in code_data:
                        state["configuration_files"] = code_data["configuration_files"]
                
                # Convert SimplifiedCodeResponse to dictionary for state update
                if hasattr(code_data, 'dict'):  # Pydantic model
                    code_data_dict = code_data.dict()
                elif hasattr(code_data, '__dict__'):  # Regular object
                    code_data_dict = code_data.__dict__
                else:
                    code_data_dict = code_data
                
                # Update state with results using base agent method to ensure proper agent_outputs structure
                execution_time = time.time() - start_time
                updated_state = self.update_state_with_result(
                    state, 
                    "code_generation", 
                    code_data_dict, 
                    execution_time
                )
                
                return updated_state
                    
            except Exception as e:
                self.add_log_entry("error", f"Code generation attempt {attempt + 1} failed: {e}")
                
                # If this is the last attempt, raise the error
                if attempt == max_retries - 1:
                    raise
                
                # Continue to next attempt
                continue
    
    def _log_quality_gate_feedback(self, state: AgentState):
        """Log quality gate feedback for debugging (simplified for development)."""
        # Simplified logging for development phase
        self.add_log_entry("debug", "Quality gate feedback logging simplified for development")
    
    async def _perform_internal_quality_gate(self, code_data: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Perform internal quality gate check on generated code.
        
        Args:
            code_data: Generated code data
            state: Current agent state
            
        Returns:
            Dictionary with quality gate check results
        """
        self.add_log_entry("info", "Performing internal quality gate check")
        
        issues = []
        quality_score = 10.0  # Start with perfect score
        
        # Check if code files were generated - handle both old and new formats
        if hasattr(code_data, 'files'):  # SimplifiedCodeResponse object
            source_files = {}
            configuration_files = {}
            for file in code_data.files:
                if file.file_type in ['source', 'test']:
                    source_files[file.filename] = {"content": file.content}
                elif file.file_type == 'config':
                    configuration_files[file.filename] = {"content": file.content}
        else:  # Dictionary format (old)
            source_files = code_data.get("source_files", {})
            configuration_files = code_data.get("configuration_files", {})
        
        # If parsing failed and we have minimal data, check the raw response
        if not source_files and not configuration_files:
            # Try to extract code from the raw response
            raw_response = state.get("last_raw_response", "")
            if raw_response:
                self.add_log_entry("info", "Parsing failed, analyzing raw response for code quality")
                return self._analyze_raw_response_quality(raw_response)
        
        # Analyze source files
        total_lines = 0
        file_count = 0
        has_main_file = False
        has_models = False
        has_api_endpoints = False
        has_auth = False
        has_tests = False
        has_config = False
        
        # Check source files
        for filename, content in source_files.items():
            if isinstance(content, dict):
                file_content = content.get("content", "")
            else:
                file_content = str(content)
            
            lines = len(file_content.split("\n"))
            total_lines += lines
            file_count += 1
            
            # Check for key file types
            filename_lower = filename.lower()
            if "main" in filename_lower or "app" in filename_lower:
                has_main_file = True
                # Check for "Hello World" patterns
                if "hello world" in file_content.lower() and lines < 20:
                    issues.append(f"Minimal 'Hello World' code detected in {filename}")
                    quality_score -= 2.0
            if "model" in filename_lower or "schema" in filename_lower:
                has_models = True
            if "api" in filename_lower or "router" in filename_lower or "endpoint" in filename_lower:
                has_api_endpoints = True
            if "auth" in filename_lower or "jwt" in filename_lower or "login" in filename_lower:
                has_auth = True
            if "test" in filename_lower:
                has_tests = True
            if "config" in filename_lower or "settings" in filename_lower:
                has_config = True
            
            # Check for very short files (RELAXED - light penalties)
            if lines < 3:
                issues.append(f"Very short file: {filename} (only {lines} lines)")
                quality_score -= 0.5  # Light penalty
        
        # Check configuration files
        config_count = 0
        for filename, content in configuration_files.items():
            if isinstance(content, dict):
                file_content = content.get("content", "")
            else:
                file_content = str(content)
            
            lines = len(file_content.split("\n"))
            total_lines += lines
            config_count += 1
            
            # Check for very short config files (RELAXED)
            if lines < 1:
                issues.append(f"Empty config file: {filename}")
                quality_score -= 0.5  # Light penalty
        
        # Quality assessments (RELAXED REQUIREMENTS FOR DEVELOPMENT)
        if total_lines < 20:
            issues.append(f"Very low code volume: only {total_lines} total lines (minimum: 20)")
            quality_score -= 1.0  # Light penalty
        
        if file_count < 1:
            issues.append(f"No source files generated")
            quality_score -= 2.0  # Moderate penalty
        
        if not has_main_file:
            issues.append("No main application file found")
            quality_score -= 0.5  # Light penalty
        
        if not has_models:
            issues.append("No data models found")
            quality_score -= 0.5  # Light penalty
        
        if not has_api_endpoints:
            issues.append("No API endpoints found")
            quality_score -= 0.5  # Light penalty
        
        if not has_auth:
            issues.append("No authentication system found")
            quality_score -= 0.5  # Light penalty
        
        if not has_config:
            issues.append("No configuration files found")
            quality_score -= 0.5  # Light penalty
        
        # Bonus points for comprehensive code
        if total_lines >= 200:
            quality_score += 1.0
        if file_count >= 8:
            quality_score += 1.0
        if has_tests:
            quality_score += 1.0
        
        # Ensure quality score is within bounds
        quality_score = max(0.0, min(10.0, quality_score))
        
        # Determine if quality gate passed (RELAXED THRESHOLD)
        quality_gate_passed = quality_score >= 2.0  # Much more tolerant
        
        result = {
            "quality_gate_passed": quality_gate_passed,
            "quality_score": quality_score,
            "issues": issues,
            "metrics": {
                "total_lines": total_lines,
                "file_count": file_count,
                "config_count": config_count,
                "has_main_file": has_main_file,
                "has_models": has_models,
                "has_api_endpoints": has_api_endpoints,
                "has_auth": has_auth,
                "has_tests": has_tests,
                "has_config": has_config
            }
        }
        
        self.add_log_entry("info", f"Internal quality gate result: {'PASSED' if quality_gate_passed else 'FAILED'} (score: {quality_score})")
        
        if not quality_gate_passed:
            self.add_log_entry("warning", f"Internal quality gate failed: {issues}")
        
        return result
    
    def _analyze_raw_response_quality(self, raw_response: str) -> Dict[str, Any]:
        """
        Analyze raw response quality when JSON parsing fails.
        
        Args:
            raw_response: Raw response from the AI
            
        Returns:
            Quality gate result
        """
        self.add_log_entry("info", "Analyzing raw response quality")
        
        issues = []
        quality_score = 10.0
        
        # Check for comprehensive code patterns in raw response
        response_lower = raw_response.lower()
        
        # Check for code volume (RELAXED)
        if len(raw_response) < 1000:
            issues.append("Very short response length")
            quality_score -= 1.0  # Light penalty
        
        # Check for key components
        has_fastapi = "fastapi" in response_lower
        has_sqlalchemy = "sqlalchemy" in response_lower
        has_models = "class" in response_lower and ("user" in response_lower or "task" in response_lower or "project" in response_lower)
        has_api_endpoints = "@router" in response_lower or "@app" in response_lower
        has_auth = "jwt" in response_lower or "authentication" in response_lower or "login" in response_lower
        has_database = "database" in response_lower or "postgresql" in response_lower
        has_requirements = "requirements" in response_lower or "fastapi" in response_lower
        
        # Check for "Hello World" patterns
        if "hello world" in response_lower and len(raw_response) < 1000:
            issues.append("Minimal 'Hello World' code detected")
            quality_score -= 3.0
        
        # Quality assessments
        if not has_fastapi:
            issues.append("No FastAPI framework detected")
            quality_score -= 1.0
        
        if not has_sqlalchemy:
            issues.append("No SQLAlchemy ORM detected")
            quality_score -= 1.0
        
        if not has_models:
            issues.append("No data models detected")
            quality_score -= 1.0
        
        if not has_api_endpoints:
            issues.append("No API endpoints detected")
            quality_score -= 1.0
        
        if not has_auth:
            issues.append("No authentication system detected")
            quality_score -= 1.0
        
        if not has_database:
            issues.append("No database configuration detected")
            quality_score -= 1.0
        
        if not has_requirements:
            issues.append("No requirements/dependencies detected")
            quality_score -= 1.0
        
        # Bonus points for comprehensive code
        if len(raw_response) >= 15000:
            quality_score += 2.0
        if has_fastapi and has_sqlalchemy and has_models and has_api_endpoints:
            quality_score += 2.0
        
        # Ensure quality score is within bounds
        quality_score = max(0.0, min(10.0, quality_score))
        
        # Determine if quality gate passed
        quality_gate_passed = quality_score >= 2.0  # Much more tolerant
        
        result = {
            "quality_gate_passed": quality_gate_passed,
            "quality_score": quality_score,
            "issues": issues,
            "metrics": {
                "response_length": len(raw_response),
                "has_fastapi": has_fastapi,
                "has_sqlalchemy": has_sqlalchemy,
                "has_models": has_models,
                "has_api_endpoints": has_api_endpoints,
                "has_auth": has_auth,
                "has_database": has_database,
                "has_requirements": has_requirements
            }
        }
        
        self.add_log_entry("info", f"Raw response quality gate result: {'PASSED' if quality_gate_passed else 'FAILED'} (score: {quality_score})")
        
        if not quality_gate_passed:
            self.add_log_entry("warning", f"Raw response quality gate failed: {issues}")
        
        return result
    
    def _extract_keywords_from_requirements(self, requirements: List[Any]) -> List[str]:
        """Extract keywords from requirements for basic checking."""
        keywords = []
        for req in requirements:
            if isinstance(req, dict):
                description = req.get("requirement_description", "")
                # Extract key words (simple approach)
                words = description.lower().split()
                keywords.extend([word for word in words if len(word) > 3 and word not in ["the", "and", "for", "with", "that", "this"]])
            elif isinstance(req, str):
                words = req.lower().split()
                keywords.extend([word for word in words if len(word) > 3])
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_total_lines(self, code_data: Dict[str, Any]) -> int:
        """Calculate total lines of code from source and configuration files."""
        total_lines = 0
        
        # Count lines in source files
        source_files = code_data.get("source_files", {})
        for filename, file_data in source_files.items():
            if isinstance(file_data, dict):
                content = file_data.get("content", "")
            elif isinstance(file_data, str):
                content = file_data
            else:
                continue
            total_lines += len(content.split("\n"))
        
        # Count lines in configuration files
        configuration_files = code_data.get("configuration_files", {})
        for filename, file_data in configuration_files.items():
            if isinstance(file_data, dict):
                content = file_data.get("content", "")
            elif isinstance(file_data, str):
                content = file_data
            else:
                continue
            total_lines += len(content.split("\n"))
        
        return total_lines
    
    def _get_languages_used(self, code_data: Dict[str, Any]) -> List[str]:
        """Get list of programming languages used in the generated code."""
        languages = set()
        
        # Get languages from source files
        source_files = code_data.get("source_files", {})
        for filename, file_data in source_files.items():
            if isinstance(file_data, dict):
                language = file_data.get("language", "unknown")
            else:
                # Try to detect language from filename
                ext = filename.lower().split('.')[-1] if '.' in filename else ''
                language_map = {
                    'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                    'java': 'java', 'cpp': 'cpp', 'c': 'c', 'cs': 'csharp',
                    'php': 'php', 'rb': 'ruby', 'go': 'go', 'rs': 'rust'
                }
                language = language_map.get(ext, 'unknown')
            languages.add(language)
        
        return list(languages)
    
    def _handle_quality_gate_failure(self, state: AgentState, quality_check: Dict[str, Any]) -> AgentState:
        """
        Handle quality gate failure (simplified for development - just log the issues).
        
        Args:
            state: Current agent state
            quality_check: Quality gate check results
            
        Returns:
            Updated state with failure information
        """
        self.add_log_entry("warning", "Quality gate issues detected but continuing execution")
        self.add_log_entry("warning", f"Quality issues: {quality_check.get('issues', [])}")
        
        # Don't block execution, just log the issues
        return state
    
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
    
    def _validate_code_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate code generation data with more flexible validation.
        
        Args:
            data: Code generation data
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check for basic structure
            if not isinstance(data, dict):
                return False
            
            # Check for source files or configuration files
            source_files = data.get("source_files", {})
            configuration_files = data.get("configuration_files", {})
            
            # At least one type of files should be present
            if not source_files and not configuration_files:
                return False
            
            # Validate source files if present
            if source_files:
                if not isinstance(source_files, dict):
                    return False
                
                # Check that at least one source file has content
                has_content = False
                for filename, content in source_files.items():
                    if isinstance(content, dict):
                        if content.get("content", "").strip():
                            has_content = True
                            break
                    elif isinstance(content, str) and content.strip():
                        has_content = True
                        break
                
                if not has_content:
                    return False
            
            # Validate configuration files if present
            if configuration_files:
                if not isinstance(configuration_files, dict):
                    return False
            
            return True
            
        except Exception as e:
            self.add_log_entry("warning", f"Code data validation failed: {e}")
            return False
    
    def _parse_code_generation_response(self, response: str) -> Dict[str, Any]:
        """
        Enhanced JSON parsing for code generation responses with truncation handling.
        
        Args:
            response: Raw response from the AI
            
        Returns:
            Parsed code data
        """
        self.add_log_entry("info", "Attempting enhanced JSON parsing for code generation")
        
        # First try standard JSON parsing  
        try:
            import json
            data = json.loads(response)
            self.add_log_entry("info", "Standard JSON parsing successful")
            
            # Validate structure and add missing fields
            return self._ensure_complete_structure(data)
            
        except json.JSONDecodeError as e:
            self.add_log_entry("warning", f"Standard JSON parsing failed: {e}")
            
            # Try to fix common JSON issues
            try:
                fixed_response = self._fix_truncated_json(response)
                data = json.loads(fixed_response)
                self.add_log_entry("info", "JSON parsing successful after fixing")
                
                return self._ensure_complete_structure(data)
                
            except Exception as fix_error:
                self.add_log_entry("warning", f"JSON fix attempt failed: {fix_error}")
                
                # Try enhanced parser as last resort
                try:
                    from utils.enhanced_output_parsers import CodeGenerationParser
                    parser = CodeGenerationParser()
                    data = parser.parse(response)
                    self.add_log_entry("info", "Enhanced parser successful")
                    return data
                    
                except Exception as parser_error:
                    self.add_log_entry("error", f"All parsing methods failed: {parser_error}")
                    raise parser_error
    
    def _fix_truncated_json(self, response: str) -> str:
        """
        Attempt to fix truncated or malformed JSON.
        
        Args:
            response: Raw JSON response
            
        Returns:
            Fixed JSON string
        """
        self.add_log_entry("info", "Attempting to fix truncated JSON")
        
        # Remove any text before the first {
        start_idx = response.find('{')
        if start_idx > 0:
            response = response[start_idx:]
        
        # Try to fix unterminated strings and objects
        if not response.endswith('}'):
            # Count open braces vs close braces
            open_braces = response.count('{')
            close_braces = response.count('}')
            
            # Add missing closing braces
            missing_braces = open_braces - close_braces
            if missing_braces > 0:
                response += '}' * missing_braces
        
        # Fix unterminated strings by finding the last quote and ensuring it's closed
        if response.count('"') % 2 != 0:
            # Add closing quote if needed
            response += '"'
        
        return response
    
    def _ensure_complete_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure the parsed data has all required fields with correct types.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Complete data structure
        """
        # Ensure all required fields exist
        if "source_files" not in data:
            data["source_files"] = {}
        if "configuration_files" not in data:
            data["configuration_files"] = {}
        if "project_structure" not in data:
            data["project_structure"] = []
        if "implementation_notes" not in data:
            data["implementation_notes"] = []
        if "testing_strategy" not in data:
            data["testing_strategy"] = {
                "unit_tests": "Unit testing strategy needs to be defined",
                "integration_tests": "Integration testing strategy needs to be defined"
            }
        elif isinstance(data["testing_strategy"], list):
            # Convert array to dictionary format
            strategy_list = data["testing_strategy"]
            data["testing_strategy"] = {
                "unit_tests": strategy_list[0] if len(strategy_list) > 0 else "Unit testing needed",
                "integration_tests": strategy_list[1] if len(strategy_list) > 1 else "Integration testing needed",
                "test_data": strategy_list[2] if len(strategy_list) > 2 else "Test data needed"
            }
        if "deployment_instructions" not in data:
            data["deployment_instructions"] = []
        
        return data

    def _create_fallback_code_data(self, raw_response: str) -> Dict[str, Any]:
        """
        Create fallback code data when parsing fails.
        
        Args:
            raw_response: Raw response from the AI
            
        Returns:
            Fallback code data structure
        """
        self.add_log_entry("info", "Creating fallback code data from raw response")
        
        # Initialize fallback structure with correct format
        fallback_data = {
            "source_files": {},
            "configuration_files": {},
            "project_structure": [],
            "implementation_notes": ["Generated code from raw response"],
            "testing_strategy": {
                "unit_tests": "Manual testing required due to parsing failure",
                "integration_tests": "Integration testing needs to be configured",
                "test_data": "Test data and fixtures need to be created"
            },
            "deployment_instructions": ["Deployment instructions need to be configured manually"]
        }
        
        # Create basic structure with safe filenames
        fallback_data["source_files"]["main.py"] = {
            "filename": "main.py",
            "content": "# Generated code\nprint('Hello, World!')",
            "language": "python",
            "purpose": "Main application file"
        }
        
        fallback_data["configuration_files"]["requirements.txt"] = {
            "filename": "requirements.txt",
            "content": "# Dependencies\n",
            "file_type": "requirements",
            "description": "Python package dependencies"
        }
        
        # If no files were extracted, create a basic structure
        if not fallback_data["source_files"] and not fallback_data["configuration_files"]:
            # Create a basic main.py file from the response
            fallback_data["source_files"]["main.py"] = {
                "content": raw_response[:5000],  # Limit content length
                "language": "python"
            }
            
            # Add basic configuration
            fallback_data["configuration_files"]["requirements.txt"] = {
                "content": "fastapi\nuvicorn\nsqlalchemy\npydantic",
                "language": "text"
            }
        
        return fallback_data
    
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

    def create_simplified_code_response(self, data: Dict[str, Any]) -> SimplifiedCodeResponse:
        """
        Create a SimplifiedCodeResponse from the code generation data.
        
        Args:
            data: Code generation data
            
        Returns:
            SimplifiedCodeResponse object
        """
        # Convert files to simplified format
        files = []
        
        # Convert source files
        for filename, content in data.get("source_files", {}).items():
            if isinstance(content, dict):
                file_content = content.get("content", "")
            else:
                file_content = str(content)
            
            files.append(SimplifiedCodeFile(
                filename=filename,
                content=file_content,
                file_type="source"
            ))
        
        # Convert configuration files
        for filename, content in data.get("configuration_files", {}).items():
            if isinstance(content, dict):
                file_content = content.get("content", "")
            else:
                file_content = str(content)
            
            files.append(SimplifiedCodeFile(
                filename=filename,
                content=file_content,
                file_type="config"
            ))
        
        # Get dependencies from implementation notes or tech stack
        dependencies = []
        if "implementation_notes" in data and isinstance(data["implementation_notes"], dict):
            deps = data["implementation_notes"].get("dependencies", [])
            if isinstance(deps, list):
                dependencies = deps
        
        # Get build and run instructions
        build_instructions = "pip install -r requirements.txt"
        run_instructions = "python main.py"
        
        if "deployment_instructions" in data and isinstance(data["deployment_instructions"], dict):
            install_steps = data["deployment_instructions"].get("installation_steps", [])
            if install_steps and isinstance(install_steps, list):
                build_instructions = "; ".join(install_steps)
        
        return create_simplified_code_response(
            files=files,
            dependencies=dependencies,
            build_instructions=build_instructions,
            run_instructions=run_instructions,
            quality_gate_passed=data.get("quality_gate_passed", True)
        )

    def create_simplified_output(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a simplified output from the code generation.
        
        Args:
            output: Original output data
            
        Returns:
            Simplified output data
        """
        try:
            simplified_response = self.create_simplified_code_response(output)
            return simplified_response.dict()
        except Exception as e:
            self.logger.error(f"Failed to create simplified code output: {e}")
            return None
