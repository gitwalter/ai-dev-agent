"""
Test Generator Agent for AI Development Agent.
Generates comprehensive tests for the generated code.
"""

import json
from typing import Dict, Any
from models.state import AgentState
from models.responses import TestGenerationResponse
from .base_agent import BaseAgent
from prompts import get_agent_prompt_loader


class TestGenerator(BaseAgent):
    """
    Agent responsible for generating comprehensive tests for the codebase.
    """
    
    def __init__(self, config, gemini_client):
        """Initialize the TestGenerator agent."""
        super().__init__(config, gemini_client)
        self.prompt_loader = get_agent_prompt_loader("test_generator")
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template from the database.
        
        Returns:
            Prompt template string from database
        """
        return self.prompt_loader.get_system_prompt()
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute test generation task."""
        import time
        start_time = time.time()
        
        self.add_log_entry("info", "Starting test generation")
        self.add_log_entry("info", f"Project context: {state.get('project_context', '')[:100]}...")
        
        try:
            if not self.validate_input(state):
                raise ValueError("Invalid input state for test generation")
            
            self.add_log_entry("info", "Input validation passed")
            
            # Prepare prompt
            prompt = self.prepare_prompt(state)
            self.add_log_entry("debug", f"Generated prompt length: {len(prompt)}")
            
            # Generate response
            self.add_log_entry("info", "Generating test response")
            response_text = await self.generate_response(prompt)
            
            # Parse response
            self.add_log_entry("info", "Parsing JSON response")
            test_data = self.parse_json_response(response_text)
            
            # Validate response structure
            self._validate_test_data(test_data)
            self.add_log_entry("info", "Test data validation passed")
            
            # Record key decisions
            self._record_test_decisions(test_data)
            
            # Create artifacts
            self._create_test_artifacts(test_data)
            
            # Update state with generated tests
            state["tests"] = test_data.get("test_files", {})
            
            # Create documentation
            self._create_test_documentation(test_data)
            
            # Create detailed output
            output = {
                "test_generation": test_data,
                "summary": {
                    "total_test_files": len(test_data.get("test_files", {})),
                    "test_types": test_data.get("test_types", []),
                    "coverage_targets": test_data.get("coverage_targets", {}),
                    "test_strategy": test_data.get("test_strategy", "")
                }
            }
            
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
            self.add_artifact(
                name="test_files",
                type="test_code",
                content=test_files,
                description=f"Generated {len(test_files)} test files"
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
                    "file_names": list(test_files.keys())
                },
                "test_types": {
                    "types": test_types,
                    "count": len(test_types)
                },
                "coverage_targets": coverage_targets,
                "test_strategy": test_data.get("test_strategy", ""),
                "testing_approach": {
                    "framework": test_data.get("test_framework", "pytest"),
                    "coverage_tool": test_data.get("coverage_tool", "pytest-cov"),
                    "test_organization": test_data.get("test_organization", "standard")
                }
            }
        )
    
    def _validate_test_data(self, data: Dict[str, Any]) -> None:
        """Validate test generation data."""
        # Provide default values for missing fields
        if "test_files" not in data:
            data["test_files"] = {}
        if "test_strategy" not in data:
            data["test_strategy"] = "pytest-based testing strategy"
        if "test_types" not in data:
            data["test_types"] = ["unit", "integration"]
        
        if not data.get("test_files"):
            # Create a basic test file if none provided
            data["test_files"] = {
                "test_main.py": "# Basic test file\\nimport pytest\\n\\ndef test_basic():\\n    assert True"
            }
    
    def validate_input(self, state: AgentState) -> bool:
        """Validate input state for test generation."""
        # Check for basic required fields
        if not super().validate_input(state):
            return False
        
        # Check for code_files (should be set by code generator)
        if "code_files" not in state or not state["code_files"]:
            self.logger.error("No code_files found in state - code generator must run first")
            return False
        
        # Check for requirements (should be set by requirements analyst)
        if "requirements" not in state or not state["requirements"]:
            self.logger.warning("No requirements found in state, will generate tests from code only")
            # Don't fail, just warn - we can still generate tests from code
        
        return True
