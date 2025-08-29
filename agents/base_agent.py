"""
Base agent class for the AI Development Agent system.
Provides common functionality for all specialized agents.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import google.generativeai as genai
from pydantic import BaseModel

from models.state import AgentState
from models.responses import AgentResponse, TaskStatus
from models.config import AgentConfig
from utils.prompt_management.prompt_manager import store_agent_prompt, record_prompt_execution
from utils.quality.quality_assurance import quality_assurance, QualityGateResult, ValidationResult


class BaseAgent(ABC):
    """
    Base class for all specialized agents in the development system.
    
    Provides common functionality for:
    - Gemini API integration
    - State management
    - Error handling
    - Logging
    - Response formatting
    """
    
    def __init__(self, config: AgentConfig, gemini_client: genai.GenerativeModel):
        """
        Initialize the base agent.
        
        Args:
            config: Agent configuration
            gemini_client: Configured Gemini client
        """
        self.config = config
        self.gemini_client = gemini_client
        
        # Enhanced logging setup
        from utils.core.logging_config import setup_agent_logging
        self.logger = setup_agent_logging(config.name)
        
        # Log agent initialization
        self.logger.info(f"Initializing {config.name} agent")
        self.logger.info(f"Agent description: {config.description}")
        self.logger.info(f"Agent enabled: {config.enabled}")
        self.logger.info(f"Max retries: {config.max_retries}")
        self.logger.info(f"Timeout: {config.timeout}s")
        
        # Performance tracking
        self.execution_times: List[float] = []
        self.error_count = 0
        self.success_count = 0
        
        # Documentation and logging
        self.execution_logs: List[Dict[str, Any]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.artifacts: List[Dict[str, Any]] = []
        self.documentation: Dict[str, Any] = {}
        
        self.logger.info(f"{config.name} agent initialized successfully")
        
    @property
    def name(self) -> str:
        """Get the agent name."""
        return self.config.name if hasattr(self.config, 'name') else 'unknown'
        
    @property
    def description(self) -> str:
        """Get the agent description."""
        return self.config.description if hasattr(self.config, 'description') else 'No description available'
        
    async def execute_with_quality_assurance(self, state: AgentState) -> AgentState:
        """
        Execute the agent's main task with quality assurance.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with agent results and quality validation
        """
        start_time = time.time()
        
        try:
            # Execute the agent's specific task
            result = await self._execute_task(state)
            
            # Perform quality validation
            quality_result = self._validate_output_quality(result)
            
            # Add quality metrics to state
            state = self._add_quality_metrics_to_state(state, quality_result)
            
            # Log quality results
            self._log_quality_results(quality_result)
            
            # If quality gate failed, handle appropriately
            if not quality_result.passed:
                state = self._handle_quality_gate_failure(state, quality_result)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            raise
    
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute the agent's main task.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with agent results
        """
        pass
    
    def _validate_output_quality(self, output: Dict[str, Any]) -> QualityGateResult:
        """
        Validate agent output using the quality assurance system.
        
        Args:
            output: Agent output to validate
            
        Returns:
            QualityGateResult with validation results
        """
        # Determine output type based on agent name
        output_type = self._get_output_type()
        
        # Validate using quality assurance system
        quality_result = quality_assurance.validate_agent_output(
            agent_name=self.name,
            output=output,
            output_type=output_type
        )
        
        return quality_result
    
    def _get_output_type(self) -> str:
        """Get the output type for this agent."""
        agent_type_mappings = {
            "requirements_analyst": "requirements",
            "architecture_designer": "architecture", 
            "code_generator": "code",
            "test_generator": "tests",
            "code_reviewer": "review",
            "security_analyst": "security",
            "documentation_generator": "documentation",
            "project_manager": "project"
        }
        
        return agent_type_mappings.get(self.name, "general")
    
    def _add_quality_metrics_to_state(self, state: AgentState, quality_result: QualityGateResult) -> AgentState:
        """
        Add quality metrics to the agent state.
        
        Args:
            state: Current agent state
            quality_result: Quality gate result
            
        Returns:
            Updated state with quality metrics
        """
        # Add quality gate result to state
        state["quality_gate_result"] = {
            "gate_name": quality_result.gate_name,
            "passed": quality_result.passed,
            "score": quality_result.score,
            "threshold": quality_result.threshold,
            "timestamp": quality_result.timestamp.isoformat(),
            "validations": [
                {
                    "type": v.validation_type.value,
                    "passed": v.passed,
                    "score": v.score,
                    "issues": v.issues,
                    "recommendations": v.recommendations
                }
                for v in quality_result.validations
            ]
        }
        
        # Add quality metrics summary
        state["quality_metrics"] = {
            "agent_name": self.name,
            "overall_score": quality_result.score,
            "quality_gate_passed": quality_result.passed,
            "validation_count": len(quality_result.validations),
            "passed_validations": len([v for v in quality_result.validations if v.passed]),
            "failed_validations": len([v for v in quality_result.validations if not v.passed]),
            "timestamp": datetime.now().isoformat()
        }
        
        return state
    
    def _log_quality_results(self, quality_result: QualityGateResult):
        """Log quality validation results."""
        if quality_result.passed:
            self.logger.info(f"Quality gate PASSED: {quality_result.score:.2f}/{quality_result.threshold}")
        else:
            self.logger.warning(f"Quality gate FAILED: {quality_result.score:.2f}/{quality_result.threshold}")
            
            # Log failed validations
            for validation in quality_result.validations:
                if not validation.passed:
                    self.logger.warning(f"  Failed validation: {validation.validation_type.value}")
                    for issue in validation.issues:
                        self.logger.warning(f"    - {issue}")
    
    def _handle_quality_gate_failure(self, state: AgentState, quality_result: QualityGateResult) -> AgentState:
        """
        Handle quality gate failure by adding failure information to state.
        
        Args:
            state: Current agent state
            quality_result: Quality gate result
            
        Returns:
            Updated state with failure handling
        """
        # Add quality gate failure information
        state["quality_gate_failed"] = True
        state["quality_gate_failure_reason"] = "Quality standards not met"
        
        # Collect all issues from failed validations
        all_issues = []
        all_recommendations = []
        
        for validation in quality_result.validations:
            if not validation.passed:
                all_issues.extend(validation.issues)
                all_recommendations.extend(validation.recommendations)
        
        state["quality_issues"] = all_issues
        state["quality_recommendations"] = all_recommendations
        
        # Add retry information
        state["quality_retry_count"] = state.get("quality_retry_count", 0) + 1
        state["quality_max_retries"] = 3
        
        # Check if we should retry
        if state["quality_retry_count"] < state["quality_max_retries"]:
            state["should_retry"] = True
            state["retry_reason"] = "Quality gate failure"
            self.logger.info(f"Quality gate failed, will retry (attempt {state['quality_retry_count']}/{state['quality_max_retries']})")
        else:
            state["should_retry"] = False
            state["retry_reason"] = "Max retries exceeded"
            self.logger.error("Quality gate failed, max retries exceeded")
        
        return state
    
    async def _execute_task(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the agent's specific task (to be implemented by subclasses).
        
        Args:
            state: Current workflow state
            
        Returns:
            Agent output as dictionary
        """
        # Call the abstract execute method and convert result to dict
        result_state = await self.execute(state)
        
        # Extract the agent's output from the state
        # This will be implemented by subclasses to return their specific output
        return self._extract_output_from_state(result_state)
    
    def _extract_output_from_state(self, state: AgentState) -> Dict[str, Any]:
        """
        Extract agent output from state (to be implemented by subclasses).
        
        Args:
            state: Agent state with results
            
        Returns:
            Agent output as dictionary
        """
        # Default implementation - subclasses should override
        # Extract common output fields
        output = {}
        
        # Common output fields that might be present
        common_fields = [
            "requirements", "architecture", "code_files", "test_files",
            "overall_score", "issues", "recommendations", "vulnerabilities",
            "documentation_files", "project_structure"
        ]
        
        for field in common_fields:
            if field in state:
                output[field] = state[field]
        
        return output
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for this agent.
        
        Returns:
            Prompt template string
        """
        pass
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the Gemini API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response text
        """
        try:
            self.add_log_entry("info", "Starting Gemini API request", {
                "prompt_length": len(prompt),
                "kwargs_count": len(kwargs)
            })
            
            # Validate configuration first
            if not self.validate_gemini_config():
                self.add_log_entry("error", "Invalid Gemini configuration")
                raise ValueError("Invalid Gemini configuration")
            
            start_time = time.time()
            
            # Import performance tracking
            from utils.quality.performance_optimizer import record_agent_performance
            
            # Sanitize the prompt to prevent API errors
            sanitized_prompt = self.sanitize_prompt(prompt)
            
            # Prepare and validate generation parameters
            generation_config = {
                "temperature": self.config.parameters.get("temperature", 0.1),
                "top_p": self.config.parameters.get("top_p", 0.8),
                "top_k": self.config.parameters.get("top_k", 40),
                "max_output_tokens": self.config.parameters.get("max_tokens", 8192),
            }
            
            # Validate the generation configuration
            validated_config = self.validate_generation_config(generation_config)
            
            # Log the request for debugging
            self.add_log_entry("debug", "Gemini API request details", {
                "config": validated_config,
                "original_prompt_length": len(prompt),
                "sanitized_prompt_length": len(sanitized_prompt),
                "sanitization_changes": len(prompt) != len(sanitized_prompt)
            })
            
            # Generate response
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                sanitized_prompt,
                generation_config=validated_config,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            self.execution_times.append(execution_time)
            
            # Record performance metrics for optimization
            try:
                # Estimate cost based on model and tokens
                model_name = getattr(self.gemini_client, 'model_name', 'unknown')
                estimated_cost = self._estimate_cost(len(prompt), len(response.text if hasattr(response, 'text') else str(response)), model_name)
                
                record_agent_performance(
                    agent_name=self.name,
                    execution_time=execution_time,
                    success=True,
                    model_used=model_name,
                    tokens_used=len(prompt) + len(response.text if hasattr(response, 'text') else str(response)),
                    cost_estimate=estimated_cost,
                    additional_data={
                        "prompt_length": len(prompt),
                        "response_length": len(response.text if hasattr(response, 'text') else str(response)),
                        "model_name": model_name
                    }
                )
            except Exception as e:
                self.logger.warning(f"Failed to record performance metrics: {str(e)}")
            
            # Record the execution in the database
            if hasattr(self, 'prompt_id') and self.prompt_id:
                try:
                    record_prompt_execution(
                        prompt_id=self.prompt_id,
                        input_data={"prompt": prompt, "kwargs": kwargs},
                        output_data={"response": response.text if hasattr(response, 'text') else str(response)},
                        execution_time=execution_time,
                        success=True
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to record prompt execution: {str(e)}")
            
            # Handle different response types
            if hasattr(response, 'text') and response.text:
                self.success_count += 1
                self.add_log_entry("info", "Generated response successfully", {
                    "execution_time": f"{execution_time:.2f}s",
                    "response_length": len(response.text),
                    "response_type": "text"
                })
                return response.text
            elif hasattr(response, 'parts') and response.parts:
                # Handle response with parts
                text_parts = []
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                if text_parts:
                    self.success_count += 1
                    self.add_log_entry("info", "Generated response with parts", {
                        "execution_time": f"{execution_time:.2f}s",
                        "response_length": len(" ".join(text_parts)),
                        "parts_count": len(text_parts),
                        "response_type": "parts"
                    })
                    return " ".join(text_parts)
            elif hasattr(response, 'candidates') and response.candidates:
                # Handle response with candidates
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            if text_parts:
                                self.success_count += 1
                                self.add_log_entry("info", "Generated response with candidates", {
                                    "execution_time": f"{execution_time:.2f}s",
                                    "response_length": len(" ".join(text_parts)),
                                    "candidates_count": len(response.candidates),
                                    "response_type": "candidates"
                                })
                                return " ".join(text_parts)
            
            # If no valid text found, raise error
            self.add_log_entry("error", "Empty or invalid response from Gemini API", {
                "response_attributes": list(dir(response)),
                "has_text": hasattr(response, 'text'),
                "has_parts": hasattr(response, 'parts'),
                "has_candidates": hasattr(response, 'candidates')
            })
            raise ValueError("Empty or invalid response from Gemini API")
                
        except Exception as e:
            self.error_count += 1
            error_msg = str(e)
            execution_time = time.time() - start_time if 'start_time' in locals() else None
            
            # Record performance metrics for failed execution
            try:
                model_name = getattr(self.gemini_client, 'model_name', 'unknown')
                record_agent_performance(
                    agent_name=self.name,
                    execution_time=execution_time or 0.0,
                    success=False,
                    model_used=model_name,
                    tokens_used=len(prompt),
                    cost_estimate=0.0,  # No cost for failed requests
                    error_message=error_msg,
                    additional_data={
                        "prompt_length": len(prompt),
                        "error_type": type(e).__name__
                    }
                )
            except Exception as perf_error:
                self.logger.warning(f"Failed to record performance metrics for error: {str(perf_error)}")
            
            self.add_log_entry("error", "Gemini API request failed", {
                "error_message": error_msg,
                "error_type": type(e).__name__,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None
            })
            
            # Record the failed execution in the database
            if hasattr(self, 'prompt_id') and self.prompt_id:
                try:
                    record_prompt_execution(
                        prompt_id=self.prompt_id,
                        input_data={"prompt": prompt, "kwargs": kwargs},
                        output_data=None,
                        execution_time=execution_time,
                        success=False,
                        error_message=error_msg
                    )
                    self.add_log_entry("debug", "Failed execution recorded in database")
                except Exception as db_error:
                    self.add_log_entry("warning", "Failed to record failed prompt execution", {
                        "db_error": str(db_error)
                    })
            
            # Handle the specific "src property must be a valid json object" error
            if "src property must be a valid json object" in error_msg:
                self.add_log_entry("error", "Gemini API src property error", {
                    "error_message": error_msg,
                    "suggestion": "This error typically occurs when the prompt contains problematic content or invalid generation parameters"
                })
                
                # Try to provide a more helpful error message
                raise ValueError(
                    f"Gemini API configuration error: {error_msg}. "
                    "This may be caused by invalid generation parameters or problematic prompt content. "
                    "Please check your agent configuration and prompt template."
                )
            
            # Handle other common Gemini API errors
            elif "No API_KEY" in error_msg:
                self.add_log_entry("error", "Gemini API key not configured")
                raise ValueError("Gemini API key not configured. Please set GOOGLE_API_KEY environment variable.")
            elif "rate limit" in error_msg.lower():
                self.add_log_entry("error", "Gemini API rate limit exceeded")
                raise ValueError("Gemini API rate limit exceeded. Please wait and try again.")
            elif "quota" in error_msg.lower():
                self.add_log_entry("error", "Gemini API quota exceeded")
                raise ValueError("Gemini API quota exceeded. Please check your usage limits.")
            elif "invalid" in error_msg.lower() and "parameter" in error_msg.lower():
                self.add_log_entry("error", "Invalid Gemini API parameters", {
                    "error_message": error_msg
                })
                raise ValueError(f"Invalid Gemini API parameters: {error_msg}")
            else:
                self.add_log_entry("error", "Unknown error generating response", {
                    "error_message": error_msg
                })
            
            # Log the full response for debugging
            if 'response' in locals():
                self.add_log_entry("debug", "Response debugging information", {
                    "response_type": str(type(response)),
                    "response_attributes": list(dir(response)),
                    "has_text": hasattr(response, 'text'),
                    "has_parts": hasattr(response, 'parts'),
                    "has_candidates": hasattr(response, 'candidates')
                })
            
            raise
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from the agent using enhanced LangChain structured outputs.
        
        Args:
            response: Raw response string
            
        Returns:
            Parsed and validated JSON data
        """
        try:
            # Import the enhanced output parser factory
            from utils.parsing.enhanced_output_parsers import EnhancedOutputParserFactory
            
            # Get the appropriate enhanced parser for this agent type
            agent_type = self.config.name if hasattr(self.config, 'name') else 'unknown'
            parser = EnhancedOutputParserFactory.get_parser(agent_type)
            
            # Parse with enhanced parser (includes LangChain + fallbacks)
            parsed_data = parser.parse(response)
            
            # Debug: Check what type of data is returned
            print(f"DEBUG: parse_json_response - parsed_data type: {type(parsed_data)}")
            print(f"DEBUG: parse_json_response - parsed_data content: {parsed_data}")
            
            # Log successful parsing
            self.add_log_entry("info", "Enhanced output parsing successful", {
                "agent_type": agent_type,
                "response_length": len(response),
                "parsed_keys": list(parsed_data.keys()) if isinstance(parsed_data, dict) else []
            })
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Enhanced output parser error: {e}")
            self.add_log_entry("error", "Enhanced output parsing failed", {
                "error_message": str(e),
                "error_type": type(e).__name__,
                "fallback_used": True
            })
            
            # Use enhanced fallback parsing
            return self._enhanced_fallback_parse(response)
    
    def _enhanced_fallback_parse(self, response: str) -> Dict[str, Any]:
        """Enhanced fallback parsing with better error handling and validation."""
        try:
            # Import the enhanced parser utilities
            from utils.parsing.enhanced_output_parsers import parse_with_enhanced_parser
            
            # Get agent type
            agent_type = self.config.name if hasattr(self.config, 'name') else 'unknown'
            
            # Use the enhanced parser with full fallback handling
            parsed_data = parse_with_enhanced_parser(response, agent_type)
            
            self.add_log_entry("info", "Enhanced fallback parsing successful", {
                "agent_type": agent_type,
                "fallback_method": "enhanced_parser"
            })
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Enhanced fallback parsing failed: {e}")
            self.add_log_entry("error", "Enhanced fallback parsing failed", {
                "error_message": str(e),
                "using_legacy_fallback": True
            })
            
            # Ultimate fallback to legacy parsing
            return self._manual_json_parse(response)
    
    def _manual_json_parse(self, response: str) -> Dict[str, Any]:
        """Legacy manual JSON parsing as ultimate fallback."""
        try:
            # Clean the response first
            cleaned_response = response.strip()
            
            # Try to extract JSON from the response
            if "```json" in cleaned_response:
                json_start = cleaned_response.find("```json") + 7
                json_end = cleaned_response.find("```", json_start)
                if json_end == -1:
                    json_end = len(cleaned_response)
                json_str = cleaned_response[json_start:json_end].strip()
            elif "```" in cleaned_response:
                json_start = cleaned_response.find("```") + 3
                json_end = cleaned_response.find("```", json_start)
                if json_end == -1:
                    json_end = len(cleaned_response)
                json_str = cleaned_response[json_start:json_end].strip()
            else:
                json_str = cleaned_response
            
            # Remove any leading/trailing whitespace and newlines
            json_str = json_str.strip()
            
            # Try to parse the JSON directly first
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decode error: {str(e)}")
                
                # Try aggressive JSON fixing
                fixed_json = self._aggressive_json_fix(json_str)
                
                try:
                    return json.loads(fixed_json)
                except json.JSONDecodeError as e2:
                    self.logger.error(f"JSON decode error after aggressive fix: {str(e2)}")
                    
                    # Last resort: try to extract any valid JSON structure
                    fallback_data = self._extract_any_valid_json(json_str)
                    if fallback_data:
                        self.logger.warning("Using fallback JSON data")
                        return fallback_data
                    
                    raise ValueError(f"Invalid JSON response: {str(e2)}")
            
        except Exception as e:
            self.logger.error(f"Manual JSON parse error: {str(e)}")
            return self._get_fallback_json_data()
    
    def _aggressive_json_fix(self, json_str: str) -> str:
        """
        Aggressively fix JSON formatting issues.
        
        Args:
            json_str: Raw JSON string
            
        Returns:
            Fixed JSON string
        """
        # Remove trailing commas
        json_str = json_str.replace(',}', '}').replace(',]', ']')
        
        # Fix common quote issues
        json_str = json_str.replace('"', '"').replace('"', '"')
        json_str = json_str.replace(''', "'").replace(''', "'")
        
        # Fix unterminated strings - look for quotes that don't have a closing quote
        import re
        
        # Fix unterminated strings at the end of the JSON
        json_str = re.sub(r'(["\'])([^"\']*)$', r'\1\2"', json_str)
        
        # Fix unterminated braces/brackets at the end
        json_str = re.sub(r'([{[])([^{}\]]*)$', r'\1\2}', json_str)
        
        # Fix newline issues in strings - but be more careful
        # Only replace newlines that are not already escaped
        json_str = re.sub(r'(?<!\\)\n', '\\n', json_str)
        json_str = re.sub(r'(?<!\\)\r', '\\r', json_str)
        json_str = re.sub(r'(?<!\\)\t', '\\t', json_str)
        
        # Try to find the last complete brace/bracket
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        last_complete_pos = 0
        
        for i, char in enumerate(json_str):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_complete_pos = i + 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        last_complete_pos = i + 1
        
        # Return the complete part
        if last_complete_pos > 0:
            json_str = json_str[:last_complete_pos]
        
        # If we still have unterminated strings, try to close them
        if json_str.count('"') % 2 != 0:
            # Find the last quote and add a closing quote
            last_quote_pos = json_str.rfind('"')
            if last_quote_pos != -1:
                json_str = json_str[:last_quote_pos + 1] + '"' + json_str[last_quote_pos + 1:]
        
        return json_str
    
    def _extract_any_valid_json(self, json_str: str) -> Dict[str, Any]:
        """
        Extract any valid JSON structure from the string.
        
        Args:
            json_str: Raw JSON string
            
        Returns:
            Extracted JSON data or empty dict
        """
        try:
            # Try to find the first complete JSON object
            start_brace = json_str.find('{')
            if start_brace == -1:
                return {}
            
            brace_count = 0
            in_string = False
            escape_next = False
            
            for i in range(start_brace, len(json_str)):
                char = json_str[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            complete_json = json_str[start_brace:i+1]
                            return json.loads(complete_json)
            
            return {}
            
        except Exception:
            return {}
    
    def _fix_json_string(self, json_str: str) -> str:
        """
        Fix common JSON formatting issues.
        
        Args:
            json_str: Raw JSON string
            
        Returns:
            Fixed JSON string
        """
        # Remove trailing commas
        json_str = json_str.replace(',}', '}').replace(',]', ']')
        
        # Fix unterminated strings by finding the last complete object/array
        try:
            # Find the last complete JSON structure
            brace_count = 0
            bracket_count = 0
            in_string = False
            escape_next = False
            last_complete_pos = 0
            
            for i, char in enumerate(json_str):
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            last_complete_pos = i + 1
                    elif char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            last_complete_pos = i + 1
            
            # If we found a complete structure, truncate to that point
            if last_complete_pos > 0:
                json_str = json_str[:last_complete_pos]
        
        except Exception as e:
            self.logger.debug(f"Error during JSON fixing: {str(e)}")
        
        return json_str
    
    def _extract_partial_json(self, json_str: str) -> Dict[str, Any]:
        """
        Extract partial JSON data when full parsing fails.
        
        Args:
            json_str: Raw JSON string
            
        Returns:
            Partial JSON data as dictionary
        """
        try:
            # Try to find and extract individual key-value pairs
            import re
            
            # Look for simple key-value patterns
            pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
            matches = re.findall(pattern, json_str)
            
            if matches:
                result = {}
                for key, value in matches:
                    result[key] = value
                return result
            
            # Look for array patterns
            array_pattern = r'"([^"]+)"\s*:\s*\[([^\]]*)\]'
            array_matches = re.findall(array_pattern, json_str)
            
            if array_matches:
                result = {}
                for key, array_content in array_matches:
                    # Try to parse array content
                    try:
                        items = [item.strip().strip('"') for item in array_content.split(',') if item.strip()]
                        result[key] = items
                    except:
                        result[key] = []
                return result
            
            # If no patterns found, return empty structure
            return {
                "source_files": {},
                "configuration_files": {},
                "project_structure": [],
                "dependencies": {},
                "documentation": {}
            }
        except Exception as e:
            self.logger.error(f"Error extracting partial JSON: {str(e)}")
            return {
                "source_files": {},
                "configuration_files": {},
                "project_structure": [],
                "dependencies": {},
                "documentation": {}
            }
    
    def _extract_any_valid_json(self, json_str: str) -> Dict[str, Any]:
        """
        Extract any valid JSON structure from the response.
        
        Args:
            json_str: Raw JSON string
            
        Returns:
            Valid JSON data as dictionary
        """
        try:
            # Try to find complete JSON objects
            import re
            
            # Look for complete JSON object patterns
            object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(object_pattern, json_str)
            
            if matches:
                # Try to parse the largest match
                largest_match = max(matches, key=len)
                try:
                    return json.loads(largest_match)
                except:
                    pass
            
            # Try to extract key-value pairs from the response
            kv_pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
            kv_matches = re.findall(kv_pattern, json_str)
            
            if kv_matches:
                result = {}
                for key, value in kv_matches:
                    result[key] = value
                return result
            
            # Try to extract file patterns (common in code generation)
            file_pattern = r'"([^"]+\.(?:py|txt|md|json|yaml|yml))"\s*:\s*"([^"]*)"'
            file_matches = re.findall(file_pattern, json_str)
            
            if file_matches:
                result = {"source_files": {}}
                for filename, content in file_matches:
                    result["source_files"][filename] = content
                return result
            
            # Last resort: return minimal structure
            return {
                "source_files": {"main.py": "# Generated code\nprint('Hello, World!')"},
                "configuration_files": {"requirements.txt": "# Dependencies\n"},
                "project_structure": [],
                "implementation_notes": ["Code generation completed with fallback structure"],
                "testing_strategy": {"unit_tests": "Basic test structure"},
                "deployment_instructions": ["Basic deployment steps"]
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting valid JSON: {str(e)}")
            return {
                "source_files": {"main.py": "# Generated code\nprint('Hello, World!')"},
                "configuration_files": {"requirements.txt": "# Dependencies\n"},
                "project_structure": [],
                "implementation_notes": ["Code generation completed with fallback structure"],
                "testing_strategy": {"unit_tests": "Basic test structure"},
                "deployment_instructions": ["Basic deployment steps"]
            }
            
        except Exception as e:
            self.logger.debug(f"Error extracting partial JSON: {str(e)}")
            return {
                "source_files": {},
                "configuration_files": {},
                "project_structure": [],
                "dependencies": {},
                "documentation": {}
            }
    
    def create_agent_response(
        self,
        task_name: str,
        status: TaskStatus,
        output: Dict[str, Any],
        execution_time: float = 0.0,
        error_message: Optional[str] = None,
        warnings: Optional[List[str]] = None
    ) -> AgentResponse:
        """
        Create a standardized agent response.
        
        Args:
            task_name: Name of the executed task
            status: Task execution status
            output: Task output data
            execution_time: Time taken to execute the task
            error_message: Error message if task failed
            warnings: List of warnings
            
        Returns:
            AgentResponse object
        """
        # Try to create simplified output first
        try:
            simplified_output = self.create_simplified_output(output)
            if simplified_output is not None:
                output = simplified_output
        except Exception as e:
            self.logger.warning(f"Failed to create simplified output: {e}")
        
        # Create content dictionary with all the data
        content = {
            "task_name": task_name,
            "output": output,
            "execution_time": execution_time,
            "metadata": {
                "retry_count": self.config.max_retries,
                "success_count": self.success_count,
                "error_count": self.error_count,
                "average_execution_time": sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
            }
        }
        
        # Add error message and warnings if present
        if error_message:
            content["error_message"] = error_message
        if warnings:
            content["warnings"] = warnings
        
        return AgentResponse(
            agent_name=self.config.name,
            content=content,
            status=status,
            timestamp=datetime.now()
        )

    def create_simplified_output(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a simplified output from the agent response.
        Override this method in subclasses to provide simplified outputs.
        
        Args:
            output: Original output data
            
        Returns:
            Simplified output data or None if not implemented
        """
        # Default implementation - return None to use original output
        return None
    
    def update_state_with_result(
        self,
        state: AgentState,
        task_name: str,
        output: Dict[str, Any],
        execution_time: float = 0.0
    ) -> AgentState:
        """
        Update the workflow state with agent results.
        
        Args:
            state: Current workflow state
            task_name: Name of the executed task
            output: Task output data
            execution_time: Time taken to execute the task
            
        Returns:
            Updated state
        """
        # Create enhanced agent response with documentation and logs
        agent_response = self.get_enhanced_response(output, execution_time)
        
        # Preserve direct state updates that may have been made by the agent
        # (like requirements, architecture, code_files, etc.)
        preserved_state = {
            "requirements": state.get("requirements", []),
            "user_stories": state.get("user_stories", []),
            "architecture": state.get("architecture", {}),
            "tech_stack": state.get("tech_stack", {}),
            "database_schema": state.get("database_schema", {}),
            "code_files": state.get("code_files", {}),
            "tests": state.get("tests", {}),
            "documentation": state.get("documentation", {}),
            "configuration_files": state.get("configuration_files", {}),
        }
        
        # Update state with agent outputs and workflow history
        state["agent_outputs"][self.config.name] = agent_response.model_dump()
        state["current_agent"] = self.config.name
        
        # Add to workflow history
        from models.state import add_workflow_step
        state = add_workflow_step(
            state=state,
            step_name=task_name,
            agent_name=self.config.name,
            input_data={"prompt_template": self.get_prompt_template()},
            output_data=output,
            status="completed"
        )
        
        # Restore preserved state updates
        for key, value in preserved_state.items():
            if value:  # Only restore if there's actual data
                state[key] = value
        
        return state
    
    def handle_error(
        self,
        state: AgentState,
        error: Exception,
        task_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentState:
        """
        Handle errors during agent execution.
        
        Args:
            state: Current workflow state
            error: Exception that occurred
            task_name: Name of the task that failed
            context: Additional context about the error
            
        Returns:
            Updated state with error information
        """
        error_message = str(error)
        self.logger.error(f"Error in {task_name}: {error_message}")
        
        # Create error response
        agent_response = self.create_agent_response(
            task_name=task_name,
            status=TaskStatus.FAILED,
            output={},
            error_message=error_message
        )
        
        # Update state
        state["agent_outputs"][self.config.name] = agent_response.model_dump()
        
        # Add error to state
        from models.state import add_error
        state = add_error(
            state=state,
            error_type=type(error).__name__,
            error_message=error_message,
            context=context or {},
            severity="error"
        )
        
        return state
    
    async def execute_with_retry(self, state: AgentState) -> AgentState:
        """
        Execute the agent with retry logic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        last_error = None
        
        self.add_log_entry("info", f"Starting execution with retry logic", {
            "max_retries": self.config.max_retries,
            "timeout": self.config.timeout,
            "project_name": state.get("project_name", "unknown")
        })
        
        for attempt in range(self.config.max_retries + 1):
            try:
                self.add_log_entry("info", f"Executing {self.config.name} (attempt {attempt + 1})", {
                    "attempt": attempt + 1,
                    "max_attempts": self.config.max_retries + 1
                })
                start_time = time.time()
                
                # Log input state summary
                self.add_log_entry("debug", "Input state summary", {
                    "project_context_length": len(state.get("project_context", "")),
                    "requirements_count": len(state.get("requirements", [])),
                    "code_files_count": len(state.get("code_files", {})),
                    "tests_count": len(state.get("tests", {}))
                })
                
                result_state = await self.execute(state)
                
                execution_time = time.time() - start_time
                self.add_log_entry("info", f"Successfully executed {self.config.name}", {
                    "execution_time": f"{execution_time:.2f}s",
                    "attempt": attempt + 1
                })
                
                # Log output state summary
                self.add_log_entry("debug", "Output state summary", {
                    "updated_requirements_count": len(result_state.get("requirements", [])),
                    "updated_code_files_count": len(result_state.get("code_files", {})),
                    "updated_tests_count": len(result_state.get("tests", {}))
                })
                
                return result_state
                
            except Exception as e:
                last_error = e
                self.add_log_entry("warning", f"Attempt {attempt + 1} failed", {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "attempt": attempt + 1
                })
                
                if attempt < self.config.max_retries:
                    # Wait before retrying (exponential backoff)
                    wait_time = 2 ** attempt
                    self.add_log_entry("info", f"Retrying after delay", {
                        "wait_time": f"{wait_time}s",
                        "next_attempt": attempt + 2
                    })
                    await asyncio.sleep(wait_time)
                else:
                    self.add_log_entry("error", f"All {self.config.max_retries + 1} attempts failed", {
                        "total_attempts": self.config.max_retries + 1,
                        "final_error": str(last_error)
                    })
                    return self.handle_error(state, last_error, "execute")
        
        # This should never be reached, but just in case
        return self.handle_error(state, last_error, "execute")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this agent.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "agent_name": self.config.name,
            "total_executions": self.success_count + self.error_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0,
            "average_execution_time": sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0,
            "min_execution_time": min(self.execution_times) if self.execution_times else 0,
            "max_execution_time": max(self.execution_times) if self.execution_times else 0,
            "total_execution_time": sum(self.execution_times)
        }
    
    def validate_input(self, state: AgentState) -> bool:
        """
        Validate input state for this agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            True if input is valid, False otherwise
        """
        # Base implementation - can be overridden by subclasses
        required_fields = ["project_context", "project_name"]
        
        for field in required_fields:
            if field not in state or not state[field]:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def validate_gemini_config(self) -> bool:
        """
        Validate that the Gemini client is properly configured.
        """
        try:
            if not self.gemini_client:
                self.logger.error("Gemini client is not initialized")
                return False
            if not hasattr(self.gemini_client, 'generate_content'):
                self.logger.error("Gemini client missing generate_content method")
                return False
            if not self.config:
                self.logger.error("Agent configuration is missing")
                return False
            if not self.config.parameters:
                self.logger.error("Agent parameters are missing")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error validating Gemini configuration: {str(e)}")
            return False
    
    def sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize prompt to prevent common issues that might cause API errors.
        
        Args:
            prompt: Raw prompt string
            
        Returns:
            Sanitized prompt string
        """
        try:
            # Remove any problematic patterns that might cause src property errors
            sanitized = prompt
            
            # Remove any malformed JSON patterns
            import re
            
            # Remove any incomplete JSON blocks
            sanitized = re.sub(r'```json\s*$', '', sanitized, flags=re.MULTILINE)
            sanitized = re.sub(r'```\s*$', '', sanitized, flags=re.MULTILINE)
            
            # Remove any problematic src property patterns in prompts
            sanitized = re.sub(r'src:\s*[^\n]*', '', sanitized, flags=re.IGNORECASE)
            
            # Remove any malformed object patterns
            sanitized = re.sub(r'{\s*,', '{', sanitized)
            sanitized = re.sub(r',\s*}', '}', sanitized)
            sanitized = re.sub(r'\[\s*,', '[', sanitized)
            sanitized = re.sub(r',\s*\]', ']', sanitized)
            
            # Ensure the prompt doesn't end with incomplete structures
            sanitized = sanitized.strip()
            
            # Log if any sanitization was performed
            if sanitized != prompt:
                self.logger.warning("Prompt was sanitized to prevent API errors")
                self.logger.debug(f"Original prompt length: {len(prompt)}")
                self.logger.debug(f"Sanitized prompt length: {len(sanitized)}")
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Error sanitizing prompt: {str(e)}")
            # Return original prompt if sanitization fails
            return prompt
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> float:
        """
        Estimate the cost of an API call based on tokens and model.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_name: Name of the model used
            
        Returns:
            Estimated cost in dollars
        """
        # Approximate token costs (as of 2024)
        # These are rough estimates - actual costs may vary
        cost_per_1k_input = {
            "gemini-2.5-flash": 0.000075,  # $0.075 per 1K input tokens
            "gemini-2.5-flash-lite": 0.000025,  # $0.025 per 1K input tokens
            "gemini-1.5-flash": 0.000075,
            "gemini-1.5-pro": 0.000125
        }
        
        cost_per_1k_output = {
            "gemini-2.5-flash": 0.0003,  # $0.30 per 1K output tokens
            "gemini-2.5-flash-lite": 0.0001,  # $0.10 per 1K output tokens
            "gemini-1.5-flash": 0.0003,
            "gemini-1.5-pro": 0.0005
        }
        
        # Get costs for the model, default to flash-lite if unknown
        input_cost = cost_per_1k_input.get(model_name, cost_per_1k_input["gemini-2.5-flash-lite"])
        output_cost = cost_per_1k_output.get(model_name, cost_per_1k_output["gemini-2.5-flash-lite"])
        
        # Calculate total cost
        total_cost = (input_tokens / 1000) * input_cost + (output_tokens / 1000) * output_cost
        
        return total_cost
    
    def validate_generation_config(self, config: dict) -> dict:
        """
        Validate and sanitize generation configuration to prevent API errors.
        
        Args:
            config: Generation configuration dictionary
            
        Returns:
            Validated and sanitized configuration
        """
        try:
            validated_config = config.copy()
            
            # Ensure all values are within valid ranges
            if 'temperature' in validated_config:
                validated_config['temperature'] = max(0.0, min(2.0, validated_config['temperature']))
            
            if 'top_p' in validated_config:
                validated_config['top_p'] = max(0.0, min(1.0, validated_config['top_p']))
            
            if 'top_k' in validated_config:
                validated_config['top_k'] = max(1, min(100, validated_config['top_k']))
            
            if 'max_output_tokens' in validated_config:
                validated_config['max_output_tokens'] = max(1, min(8192, validated_config['max_output_tokens']))
            
            # Remove any unknown parameters that might cause issues
            known_params = {'temperature', 'top_p', 'top_k', 'max_output_tokens', 'candidate_count', 'stop_sequences'}
            validated_config = {k: v for k, v in validated_config.items() if k in known_params}
            
            return validated_config
            
        except Exception as e:
            self.logger.error(f"Error validating generation config: {str(e)}")
            # Return a safe default configuration
            return {
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192
            }

    def prepare_prompt(self, state: AgentState, **kwargs) -> str:
        """
        Prepare the prompt for this agent with enhanced structured output instructions.
        
        Args:
            state: Current workflow state
            **kwargs: Additional parameters for prompt preparation
            
        Returns:
            Formatted prompt string with structured output instructions
        """
        template = self.get_prompt_template()
        
        # Get agent type for format instructions
        agent_type = self.config.name if hasattr(self.config, 'name') else 'unknown'
        
        # Get enhanced format instructions for structured output
        try:
            from utils.parsing.enhanced_output_parsers import get_enhanced_format_instructions
            
            # Use simpler format instructions for architecture designer to avoid large prompts
            if agent_type == "architecture_designer":
                format_instructions = """CRITICAL: You MUST respond with a valid JSON object containing ALL of these required fields:

{
  "system_overview": {
    "description": "High-level description of the system architecture",
    "architecture_type": "web_application|mobile_app|api_service|desktop_app",
    "deployment_model": "cloud_based|on_premise|hybrid"
  },
  "architecture_pattern": "layered|microservices|monolithic|event_driven|service_oriented",
  "components": [
    {
      "name": "Component Name",
      "responsibility": "What this component does",
      "technology": "Technology used for this component"
    }
  ],
  "technology_stack": {
    "frontend": ["technology1", "technology2"],
    "backend": ["technology1", "technology2"],
    "database": ["technology1"],
    "deployment": ["technology1"]
  },
  "security_considerations": ["security measure 1", "security measure 2"],
  "scalability_considerations": ["scalability strategy 1", "scalability strategy 2"],
  "deployment_strategy": "Brief deployment approach"
}

IMPORTANT: 
- ALL fields above are REQUIRED
- system_overview must be an object with description, architecture_type, and deployment_model
- components must be an array of objects
- technology_stack must be an object with frontend, backend, database, and deployment arrays
- Respond with ONLY the JSON object, no additional text"""
            else:
                format_instructions = get_enhanced_format_instructions(agent_type)
        except Exception as e:
            self.logger.warning(f"Failed to get format instructions: {e}")
            format_instructions = "Please respond with valid JSON format."
        
        # Common variables available to all agents
        prompt_vars = {
            "project_context": state.get("project_context", ""),
            "project_name": state.get("project_name", ""),
            "requirements": state.get("requirements", []),
            "architecture": state.get("architecture", {}),
            "tech_stack": state.get("tech_stack", {}),
            "code_files": state.get("code_files", {}),
            "source_code": state.get("source_code", {}),
            "tests": state.get("tests", {}),
            "documentation": state.get("documentation", {}),
            "coding_standards": "PEP 8, type hints, docstrings, error handling",
            "format_instructions": format_instructions,
            **kwargs
        }
        
        # Store the prompt in the database for tracking and analysis
        try:
            self.prompt_id = store_agent_prompt(
                agent_name=self.config.name,
                prompt_template=template,
                prompt_variables=prompt_vars
            )
        except Exception as e:
            self.logger.warning(f"Failed to store prompt in database: {str(e)}")
            self.prompt_id = None
        
        # Format the prompt
        formatted_prompt = template.format(**prompt_vars)
        
        # Add structured output instructions if not already present
        if "format_instructions" not in formatted_prompt:
            formatted_prompt += f"\n\n{format_instructions}"
        
        self.add_log_entry("debug", "Enhanced prompt prepared with structured output instructions", {
            "prompt_length": len(formatted_prompt),
            "format_instructions_included": "format_instructions" in formatted_prompt,
            "agent_type": agent_type
        })
        
        return formatted_prompt
    
    def add_log_entry(self, level: str, message: str, data: Dict[str, Any] = None):
        """
        Add a log entry to the agent's execution logs.
        
        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            data: Additional data to include
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data or {},
            "agent_name": self.config.name,
            "method": self._get_calling_method()
        }
        self.execution_logs.append(log_entry)
        
        # Enhanced logging with context
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        if data:
            # Include data in log message if provided
            data_str = ", ".join([f"{k}={v}" for k, v in data.items() if v is not None])
            full_message = f"{message} | Data: {data_str}" if data_str else message
        else:
            full_message = message
            
        self.logger.log(log_level, full_message)
        
        # Also log to execution logs for detailed tracking
        if level.upper() in ["ERROR", "WARNING"]:
            self.logger.warning(f"Agent {self.config.name} - {level.upper()}: {message}")
    
    def _get_calling_method(self) -> str:
        """Get the name of the calling method for better log context."""
        import inspect
        try:
            frame = inspect.currentframe().f_back
            if frame:
                return frame.f_code.co_name
        except:
            pass
        return "unknown"
    
    def add_decision(self, decision: str, rationale: str, alternatives: List[str] = None, impact: str = None):
        """
        Record a decision made during execution.
        
        Args:
            decision: The decision made
            rationale: Why this decision was made
            alternatives: Alternative options considered
            impact: Impact of this decision
        """
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives or [],
            "impact": impact
        }
        self.decisions.append(decision_entry)
        self.add_log_entry("info", f"Decision made: {decision}", {"rationale": rationale})
    
    def add_artifact(self, name: str, type: str, content: Any, description: str = None):
        """
        Record an artifact created during execution.
        
        Args:
            name: Name of the artifact
            type: Type of artifact (file, data, configuration, etc.)
            content: Content of the artifact
            description: Description of the artifact
        """
        artifact_entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "type": type,
            "content": content,
            "description": description
        }
        self.artifacts.append(artifact_entry)
        self.add_log_entry("info", f"Artifact created: {name} ({type})", {"description": description})
    
    def create_documentation(self, summary: str, details: Dict[str, Any] = None):
        """
        Create comprehensive documentation of the agent's work.
        
        Args:
            summary: Summary of the work performed
            details: Detailed information about the work
        """
        self.documentation = {
            "agent_name": self.config.name,
            "task_name": self.config.description,
            "summary": summary,
            "details": details or {},
            "execution_logs": self.execution_logs,
            "decisions": self.decisions,
            "artifacts": self.artifacts,
            "performance_metrics": {
                "execution_times": self.execution_times,
                "success_count": self.success_count,
                "error_count": self.error_count,
                "average_execution_time": sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
            }
        }
    
    def get_enhanced_response(self, output: Dict[str, Any], execution_time: float) -> 'AgentResponse':
        """
        Create an enhanced agent response with documentation and logs.
        
        Args:
            output: Agent output
            execution_time: Execution time
            
        Returns:
            Enhanced AgentResponse object
        """
        from models.responses import AgentResponse, TaskStatus
        
        return AgentResponse(
            agent_name=self.config.name,
            content=output,
            status=TaskStatus.COMPLETED
        )
    
    def _get_fallback_json_data(self) -> Dict[str, Any]:
        """Get fallback JSON data when all parsing methods fail."""
        return {
            "error": "Failed to parse JSON response",
            "fallback_data": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_filename(self, filename: str) -> bool:
        """
        Validate if a filename is safe and reasonable.
        
        Args:
            filename: Filename to validate
            
        Returns:
            True if filename is valid
        """
        if not filename or not isinstance(filename, str):
            return False
        
        # Check length
        if len(filename) > 100:
            return False
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/', '\n', '\r', '\t']
        if any(char in filename for char in invalid_chars):
            return False
        
        # Check for common file extensions
        valid_extensions = ['.py', '.js', '.ts', '.java', '.txt', '.json', '.yml', '.yaml', '.md', '.html', '.css', '.xml', '.go', '.rs', '.cpp', '.c']
        if not any(filename.endswith(ext) for ext in valid_extensions):
            return False
        
        # Check that filename doesn't look like content
        if len(filename) > 50 and (' ' in filename or '\n' in filename):
            return False
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to make it safe.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not self.validate_filename(filename):
            # Generate a safe filename
            import hashlib
            safe_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
            return f"file_{safe_hash}.txt"
        
        return filename
