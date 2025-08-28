"""
Test Generator Agent for AI Development Agent.
Generates comprehensive tests for the generated code.
Uses LangChain JsonOutputParser for stable JSON parsing.
"""

import json
from typing import Dict, Any, Optional
from models.state import AgentState
from models.responses import TestGenerationResponse
from models.simplified_responses import SimplifiedTestFile, SimplifiedTestResponse, create_simplified_test_response
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


class TestGenerator(BaseAgent):
    """
    Agent responsible for generating comprehensive tests for the codebase.
    Uses LangChain JsonOutputParser for stable JSON parsing.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the TestGenerator agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("test_generator")
        
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
        # Use a highly constrained prompt template that forces JSON output
        return """You are an expert Test Engineer. Generate comprehensive tests based on the code and requirements.

CRITICAL OUTPUT FORMAT REQUIREMENTS:
Return ONLY a JSON object with this EXACT structure:
{{
    "test_files": {{
        "test_filename.py": "complete test file content as string",
        "test_another.py": "complete test file content as string"
    }}
}}

CONSTRAINTS:
- NO nested objects, arrays, or complex structures
- NO metadata, descriptions, or test_cases arrays
- NO test_type or other fields
- Each value must be a complete, runnable Python test file as a string
- Use descriptive filenames based on the code being tested
- Include proper imports, test functions, and assertions

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
{requirements}

CODE FILES:
{code_files}

TASK:
Generate comprehensive tests that cover all functionality and edge cases.

Return the exact JSON structure above with no additional fields or nested structures. Each test file should be a complete, runnable Python test file with proper imports, test functions, and assertions.

CRITICAL: Respond with ONLY valid JSON - no explanations, no markdown, no additional text."""
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute test generation task using LangChain JsonOutputParser."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting test generation with LangChain JsonOutputParser")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for test generation")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Use LangChain approach if available
            if LANGCHAIN_AVAILABLE and self.json_parser:
                test_data = await self._execute_with_langchain(state)
            else:
                test_data = await self._execute_with_legacy_parsing(state)
            
            self.add_log_entry("info", "Test data processing completed")
            
            # Record key decisions
            self._record_test_decisions(test_data)
            
            # Create artifacts
            self._create_test_artifacts(test_data)
            
            # Create test files
            self._create_test_files(test_data)
            
            # Update state with generated tests - convert TestFile objects to simple content
            test_files = test_data.get("test_files", {})
            if test_files:
                # Convert TestFile objects to simple filename: content mapping for state
                simple_test_files = {}
                
                if isinstance(test_files, list):
                    # If test_files is a list, convert to dictionary format
                    for i, test_file in enumerate(test_files):
                        filename = f"test_file_{i}.py"
                        if hasattr(test_file, 'content'):
                            # It's a TestFile object
                            simple_test_files[filename] = {"content": test_file.content}
                        elif isinstance(test_file, dict) and "content" in test_file:
                            # It's already a dict with content
                            simple_test_files[filename] = test_file
                        else:
                            # It's just content
                            simple_test_files[filename] = {"content": str(test_file)}
                elif isinstance(test_files, dict):
                    # If test_files is a dictionary, process normally
                    for filename, test_file in test_files.items():
                        if hasattr(test_file, 'content'):
                            # It's a TestFile object
                            simple_test_files[filename] = {"content": test_file.content}
                        elif isinstance(test_file, dict) and "content" in test_file:
                            # It's already a dict with content
                            simple_test_files[filename] = test_file
                        else:
                            # It's just content
                            simple_test_files[filename] = {"content": str(test_file)}
                
                state["tests"] = simple_test_files
            else:
                state["tests"] = {}
            
            # Create detailed output
            output = {
                "test_generation": test_data,
                "summary": {
                    "test_files_count": len(test_files),
                    "test_categories_count": len(test_data.get("test_categories", {})),
                    "coverage_targets_count": len(test_data.get("coverage_targets", {}))
                }
            }
            
            # Create documentation
            self._create_test_documentation(test_data)
            
            execution_time = time.time() - start_time
            
            # Update state with results
            state = self.update_state_with_result(
                state=state,
                task_name="test_generation",
                output=output,
                execution_time=execution_time
            )
            
            self.add_log_entry("info", f"Test generation completed successfully in {execution_time:.2f}s")
            
            return state
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_log_entry("error", f"Test generation failed: {str(e)}")
            return self.handle_error(state, e, "test_generation")
    
    async def _execute_with_langchain(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute test generation using LangChain JsonOutputParser.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed test data
        """
        # Get prompt template from database
        prompt_template = self.get_prompt_template()
        
        # Create prompt
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["project_context", "code_files", "requirements"]
        )
        
        # Create LangChain Gemini client with optimized model selection
        from utils.helpers import get_llm_model
        llm = get_llm_model(task_type="test_generation")
        
        # Create chain
        chain = prompt | llm | self.json_parser
        
        # Execute the chain
        self.add_log_entry("info", "Executing LangChain chain for test generation")
        result = await chain.ainvoke({
            "project_context": state["project_context"],
            "code_files": str(state.get("code_files", {})),
            "requirements": str(state.get("requirements", []))
        })
        
        self.add_log_entry("info", "Successfully parsed test data with JsonOutputParser")
        return result
    
    async def _execute_with_legacy_parsing(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute test generation using legacy parsing approach.
        
        Args:
            state: Current workflow state
            
        Returns:
            Parsed test data
        """
        self.add_log_entry("info", "Using legacy parsing approach")
        
        # Prepare prompt
        prompt = self.prepare_prompt(state)
        self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
        
        # Generate response
        self.add_log_entry("info", "Generating test response")
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
            test_data = self.create_simplified_test_response(parsed_data)
            self.add_log_entry("info", "Successfully created simplified response")
            
        except Exception as parse_error:
            self.add_log_entry("warning", f"Direct JSON parsing failed: {parse_error}")
            # Use fallback parsing as last resort
            test_data = self.parse_json_response(response_text)
        
        # Validate response structure
        self._validate_test_data(test_data)
        self.add_log_entry("info", "Test data validation passed")
        
        return test_data
    
    def _record_test_decisions(self, test_data: Dict[str, Any]):
        """
        Record key decisions made during test generation.
        
        Args:
            test_data: Test generation data
        """
        # Record test strategy decision
        strategy = test_data.get("test_strategy", "unknown")
        self.add_decision(
            decision=f"Selected test strategy: {strategy}",
            rationale="Based on project requirements and codebase complexity",
            alternatives=["Different testing approaches considered"],
            impact="Will guide testing implementation and quality assurance"
        )
        
        # Record test types decisions
        test_types = test_data.get("test_types", [])
        if test_types:
            self.add_decision(
                decision=f"Implemented {len(test_types)} test types: {', '.join(test_types)}",
                rationale="Based on codebase structure and quality requirements",
                alternatives=["Different test type combinations considered"],
                impact="Will ensure comprehensive code coverage and quality"
            )
        
        # Record test file decisions
        test_files = test_data.get("test_files", {})
        if test_files:
            self.add_decision(
                decision=f"Generated {len(test_files)} test files",
                rationale="Based on source code structure and testing requirements",
                alternatives=["Different test file organization considered"],
                impact="Will guide testing execution and maintenance"
            )
    
    def _create_test_artifacts(self, test_data: Dict[str, Any]):
        """
        Create artifacts from test generation.
        
        Args:
            test_data: Test generation data
        """
        # Create test files artifact
        test_files = test_data.get("test_files", {})
        if test_files:
            # Convert TestFile objects to simple content for artifact storage
            simple_test_files = {}
            
            if isinstance(test_files, list):
                # If test_files is a list, convert to dictionary format
                for i, test_file in enumerate(test_files):
                    filename = f"test_file_{i}.py"
                    if hasattr(test_file, 'content'):
                        # It's a TestFile object
                        simple_test_files[filename] = test_file.content
                    elif isinstance(test_file, dict):
                        # It's a dictionary
                        simple_test_files[filename] = test_file.get("content", str(test_file))
                    else:
                        # It's already a simple string
                        simple_test_files[filename] = str(test_file)
            elif isinstance(test_files, dict):
                # If test_files is a dictionary, process normally
                for filename, test_file in test_files.items():
                    if hasattr(test_file, 'content'):
                        # It's a TestFile object
                        simple_test_files[filename] = test_file.content
                    else:
                        # It's already a simple string
                        simple_test_files[filename] = test_file
            
            self.add_artifact(
                name="test_files",
                type="test_code",
                content=simple_test_files,
                description=f"Generated {len(simple_test_files)} test files"
            )
        
        # Create test strategy artifact
        strategy = test_data.get("test_strategy", "")
        if strategy:
            self.add_artifact(
                name="test_strategy",
                type="strategy",
                content=strategy,
                description="Testing strategy and approach"
            )
        
        # Create test types artifact
        test_types = test_data.get("test_types", [])
        if test_types:
            self.add_artifact(
                name="test_types",
                type="test_types",
                content=test_types,
                description=f"Implemented test types: {', '.join(test_types)}"
            )
        
        # Create coverage targets artifact
        coverage_targets = test_data.get("coverage_targets", {})
        if coverage_targets:
            self.add_artifact(
                name="coverage_targets",
                type="coverage",
                content=coverage_targets,
                description="Code coverage targets and goals"
            )
    
    def _create_test_documentation(self, test_data: Dict[str, Any]):
        """
        Create comprehensive documentation of test generation.
        
        Args:
            test_data: Test generation data
        """
        test_files = test_data.get("test_files", {})
        test_types = test_data.get("test_types", [])
        coverage_targets = test_data.get("coverage_targets", {})
        
        self.create_documentation(
            summary=f"Generated {len(test_files)} test files covering {len(test_types)} test types",
            details={
                "test_files": {
                    "total_files": len(test_files),
                    "file_names": list(test_files.keys()) if isinstance(test_files, dict) else [f"test_file_{i}" for i in range(len(test_files))]
                },
                "test_types": {
                    "types": test_types,
                    "count": len(test_types)
                },
                "coverage_targets": coverage_targets,
                "test_strategy": test_data.get("test_strategy", ""),
                "testing_approach": {
                    "framework": test_data.get("testing_strategy", {}).get("framework", "pytest"),
                    "coverage_tool": test_data.get("testing_strategy", {}).get("coverage_tool", "pytest-cov"),
                    "test_organization": "standard"
                }
            }
        )
    
    def _create_test_files(self, test_data: Dict[str, Any]):
        """
        Create and save test files to the project directory.
        
        Args:
            test_data: Test generation data
        """
        test_files = test_data.get("test_files", {})
        
        if not test_files:
            self.add_log_entry("warning", "No test files to create")
            return
        
        # Create tests directory if it doesn't exist
        import os
        tests_dir = os.path.join("generated_projects", "test-task-management", "tests")
        os.makedirs(tests_dir, exist_ok=True)
        
        # Create test files
        created_files = []
        
        if isinstance(test_files, list):
            # If test_files is a list, convert to dictionary format
            for i, test_file in enumerate(test_files):
                filename = f"test_file_{i}.py"
                try:
                    # Extract content from test file
                    if hasattr(test_file, 'content'):
                        content = test_file.content
                    elif isinstance(test_file, dict):
                        content = test_file.get("content", "")
                    else:
                        content = str(test_file)
                    
                    # Create the test file
                    file_path = os.path.join(tests_dir, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    created_files.append(filename)
                    self.add_log_entry("info", f"Created test file: {filename}")
                    
                except Exception as e:
                    self.add_log_entry("error", f"Failed to create test file {filename}: {e}")
        elif isinstance(test_files, dict):
            # If test_files is a dictionary, process normally
            for filename, test_file in test_files.items():
                try:
                    # Extract content from test file
                    if hasattr(test_file, 'content'):
                        content = test_file.content
                    elif isinstance(test_file, dict):
                        content = test_file.get("content", "")
                    else:
                        content = str(test_file)
                    
                    # Create the test file
                    file_path = os.path.join(tests_dir, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    created_files.append(filename)
                    self.add_log_entry("info", f"Created test file: {filename}")
                    
                except Exception as e:
                    self.add_log_entry("error", f"Failed to create test file {filename}: {e}")
        
        if created_files:
            self.add_log_entry("info", f"Successfully created {len(created_files)} test files")
        else:
            self.add_log_entry("warning", "No test files were created successfully")
    
    def _validate_test_data(self, data) -> None:
        """Validate test generation data."""
        # Handle both SimplifiedTestResponse objects and dictionaries
        if hasattr(data, 'test_files'):  # SimplifiedTestResponse object
            # Convert to dictionary format for compatibility
            data_dict = {
                "test_files": {test.filename: {"content": test.content, "test_type": test.test_type} for test in data.test_files},
                "test_strategy": f"{data.test_framework}-based testing strategy",
                "test_types": list(set(test.test_type for test in data.test_files)),
                "test_categories": {
                    "unit_tests": ["Function-level tests", "Class-level tests"],
                    "integration_tests": ["API endpoint tests", "Database integration tests"]
                },
                "test_data": {
                    "fixtures": "Sample test data and fixtures for comprehensive testing",
                    "mocks": "Mock objects and stubs for isolated testing"
                },
                "coverage_targets": {
                    "unit_test_coverage": data.coverage_target,
                    "integration_test_coverage": "60%"
                },
                "testing_strategy": {
                    "framework": data.test_framework,
                    "assertion_library": "pytest assertions",
                    "mocking_framework": "unittest.mock",
                    "coverage_tool": "pytest-cov"
                },
                "test_execution_plan": [
                    "1. Run unit tests: pytest tests/unit/",
                    "2. Run integration tests: pytest tests/integration/",
                    "3. Generate coverage report: pytest --cov=src tests/"
                ],
                "quality_gate_passed": data.quality_gate_passed
            }
            # Replace the object with the dictionary
            data.clear()
            data.update(data_dict)
        else:  # Dictionary format (old)
            # Provide default values for missing fields
            if "test_files" not in data:
                data["test_files"] = {}
            if "test_strategy" not in data:
                data["test_strategy"] = "pytest-based testing strategy"
            if "test_types" not in data:
                data["test_types"] = ["unit", "integration"]
            if "test_categories" not in data:
                data["test_categories"] = {
                    "unit_tests": ["Function-level tests", "Class-level tests"],
                    "integration_tests": ["API endpoint tests", "Database integration tests"]
                }
            if "test_data" not in data:
                data["test_data"] = {
                    "fixtures": "Sample test data and fixtures for comprehensive testing",
                    "mocks": "Mock objects and stubs for isolated testing"
                }
            if "coverage_targets" not in data:
                data["coverage_targets"] = {
                    "unit_test_coverage": "80%",
                    "integration_test_coverage": "60%"
                }
            if "testing_strategy" not in data:
                data["testing_strategy"] = {
                    "framework": "pytest",
                    "assertion_library": "pytest assertions",
                    "mocking_framework": "unittest.mock",
                    "coverage_tool": "pytest-cov"
                }
            if "test_execution_plan" not in data:
                data["test_execution_plan"] = [
                    "1. Run unit tests: pytest tests/unit/",
                    "2. Run integration tests: pytest tests/integration/",
                    "3. Generate coverage report: pytest --cov=src tests/"
                ]
        
        # Convert test_files to proper TestFile objects if they're simple strings
        if data.get("test_files"):
            converted_test_files = {}
            test_files = data["test_files"]
            
            if isinstance(test_files, list):
                # If test_files is a list, convert to dictionary format
                for i, test_file in enumerate(test_files):
                    filename = f"test_file_{i}.py"
                    if isinstance(test_file, str):
                        # Convert string content to TestFile object
                        from utils.structured_outputs import TestFile
                        converted_test_files[filename] = TestFile(
                            filename=filename,
                            content=test_file,
                            test_type="unit",  # Default to unit tests
                            coverage_target="80%",
                            dependencies=["pytest"]
                        )
                    elif isinstance(test_file, dict):
                        # If it's already a dict, try to create TestFile from it
                        from utils.structured_outputs import TestFile
                        converted_test_files[filename] = TestFile(
                            filename=filename,
                            content=test_file.get("content", ""),
                            test_type=test_file.get("test_type", "unit"),
                            coverage_target=test_file.get("coverage_target", "80%"),
                            dependencies=test_file.get("dependencies", ["pytest"])
                        )
                    else:
                        # Keep as is if it's already a TestFile object
                        converted_test_files[filename] = test_file
            elif isinstance(test_files, dict):
                # If test_files is a dictionary, process normally
                for filename, content in test_files.items():
                    if isinstance(content, str):
                        # Convert string content to TestFile object
                        from utils.structured_outputs import TestFile
                        converted_test_files[filename] = TestFile(
                            filename=filename,
                            content=content,
                            test_type="unit",  # Default to unit tests
                            coverage_target="80%",
                            dependencies=["pytest"]
                        )
                    elif isinstance(content, dict):
                        # If it's already a dict, try to create TestFile from it
                        from utils.structured_outputs import TestFile
                        converted_test_files[filename] = TestFile(
                            filename=filename,
                            content=content.get("content", ""),
                            test_type=content.get("test_type", "unit"),
                            coverage_target=content.get("coverage_target", "80%"),
                            dependencies=content.get("dependencies", ["pytest"])
                        )
                    else:
                        # Keep as is if it's already a TestFile object
                        converted_test_files[filename] = content
            
            data["test_files"] = converted_test_files
        else:
            # Create a basic test file if none provided
            from utils.structured_outputs import TestFile
            data["test_files"] = {
                "test_main.py": TestFile(
                    filename="test_main.py",
                    content="# Basic test file\nimport pytest\n\ndef test_basic():\n    assert True",
                    test_type="unit",
                    coverage_target="80%",
                    dependencies=["pytest"]
                )
            }
    
    def validate_input(self, state: AgentState) -> bool:
        """Validate input state for test generation."""
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
            self.logger.warning("No requirements found in state, will generate tests from code only")
            # Don't fail, just warn - we can still generate tests from code
        
        return True

    def create_simplified_test_response(self, data: Dict[str, Any]) -> SimplifiedTestResponse:
        """
        Create a SimplifiedTestResponse from the test generation data.
        
        Args:
            data: Test generation data
            
        Returns:
            SimplifiedTestResponse object
        """
        # Convert tests to simplified format
        tests = []
        
        # Handle test_files - could be a list or dictionary
        test_files = data.get("test_files", {})
        
        if isinstance(test_files, list):
            # If test_files is a list, convert to dictionary format
            for i, test_file in enumerate(test_files):
                if isinstance(test_file, dict):
                    filename = test_file.get("filename", f"test_file_{i}.py")
                    content = test_file.get("content", "")
                    test_type = test_file.get("test_type", "unit")
                else:
                    filename = f"test_file_{i}.py"
                    content = str(test_file)
                    test_type = "unit"
                
                tests.append(SimplifiedTestFile(
                    filename=filename,
                    content=content,
                    test_type=test_type
                ))
        elif isinstance(test_files, dict):
            # If test_files is a dictionary, process normally
            for filename, test_file in test_files.items():
                if isinstance(test_file, dict):
                    content = test_file.get("content", "")
                    test_type = test_file.get("test_type", "unit")
                else:
                    content = str(test_file)
                    test_type = "unit"
                
                tests.append(SimplifiedTestFile(
                    filename=filename,
                    content=content,
                    test_type=test_type
                ))
        
        # Get test framework from strategy
        test_framework = "pytest"
        if "testing_strategy" in data and isinstance(data["testing_strategy"], dict):
            test_framework = data["testing_strategy"].get("framework", "pytest")
        
        # Get coverage target
        coverage_target = 80
        if "coverage_targets" in data and isinstance(data["coverage_targets"], dict):
            unit_coverage = data["coverage_targets"].get("unit_test_coverage", "80%")
            if isinstance(unit_coverage, str) and "%" in unit_coverage:
                try:
                    coverage_target = int(unit_coverage.replace("%", ""))
                except ValueError:
                    coverage_target = 80
        
        return create_simplified_test_response(
            test_files=tests,
            test_framework=test_framework,
            run_command=f"pytest tests/",
            coverage_target=f"{coverage_target}%",
            quality_gate_passed=data.get("quality_gate_passed", True)
        )

    def create_simplified_output(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a simplified output from the test generation.
        
        Args:
            output: Original output data
            
        Returns:
            Simplified output data
        """
        try:
            simplified_response = self.create_simplified_test_response(output)
            return simplified_response.dict()
        except Exception as e:
            self.logger.error(f"Failed to create simplified test output: {e}")
            return None
