"""
LangChain Data Exchange System for AI Development Agent.
Implements proper data flow patterns between agents using LangChain techniques.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from langchain.output_parsers import PydanticOutputParser
    from langchain.schema import OutputParserException, BaseOutputParser
    from langchain.prompts import PromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser
    from pydantic import BaseModel, Field, ValidationError
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available, using fallback patterns")

from utils.structured_outputs import (
    RequirementsAnalysisOutput, ArchitectureDesignOutput, CodeGenerationOutput,
    TestGenerationOutput, CodeReviewOutput, SecurityAnalysisOutput, DocumentationGenerationOutput
)

logger = logging.getLogger(__name__)


@dataclass
class AgentOutput:
    """Standardized agent output structure for data exchange."""
    agent_name: str
    task_name: str
    output_data: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    documentation: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    execution_time: float
    success: bool
    error_message: Optional[str] = None


class LangChainDataExchange:
    """
    Manages data exchange between agents using LangChain patterns.
    """
    
    def __init__(self):
        """Initialize the data exchange system."""
        self.logger = logging.getLogger(__name__)
        self.output_parsers = self._setup_output_parsers()
        self.data_validators = self._setup_data_validators()
        
    def _setup_output_parsers(self) -> Dict[str, BaseOutputParser]:
        """Setup LangChain output parsers for each agent type."""
        parsers = {}
        
        if LANGCHAIN_AVAILABLE:
            try:
                parsers["requirements_analyst"] = PydanticOutputParser(pydantic_object=RequirementsAnalysisOutput)
                parsers["architecture_designer"] = PydanticOutputParser(pydantic_object=ArchitectureDesignOutput)
                parsers["code_generator"] = PydanticOutputParser(pydantic_object=CodeGenerationOutput)
                parsers["test_generator"] = PydanticOutputParser(pydantic_object=TestGenerationOutput)
                parsers["code_reviewer"] = PydanticOutputParser(pydantic_object=CodeReviewOutput)
                parsers["security_analyst"] = PydanticOutputParser(pydantic_object=SecurityAnalysisOutput)
                parsers["documentation_generator"] = PydanticOutputParser(pydantic_object=DocumentationGenerationOutput)
                
                self.logger.info("LangChain output parsers setup successful")
            except Exception as e:
                self.logger.warning(f"Failed to setup LangChain parsers: {e}")
        
        return parsers
    
    def _setup_data_validators(self) -> Dict[str, Any]:
        """Setup data validation schemas for each agent type."""
        return {
            "requirements_analyst": RequirementsAnalysisOutput,
            "architecture_designer": ArchitectureDesignOutput,
            "code_generator": CodeGenerationOutput,
            "test_generator": TestGenerationOutput,
            "code_reviewer": CodeReviewOutput,
            "security_analyst": SecurityAnalysisOutput,
            "documentation_generator": DocumentationGenerationOutput
        }
    
    def create_agent_chain(self, agent_name: str, prompt_template: str) -> Any:
        """
        Create a LangChain chain for an agent with proper output parsing.
        
        Args:
            agent_name: Name of the agent
            prompt_template: Prompt template string
            
        Returns:
            LangChain chain with output parsing
        """
        if not LANGCHAIN_AVAILABLE:
            return None
            
        try:
            # Create the prompt template
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["project_context", "requirements", "architecture", "code_files", "format_instructions"],
                partial_variables={"format_instructions": self._get_format_instructions(agent_name)}
            )
            
            # Create the chain with output parsing
            if agent_name in self.output_parsers:
                chain = prompt | self.output_parsers[agent_name]
            else:
                chain = prompt | StrOutputParser()
            
            return chain
            
        except Exception as e:
            self.logger.error(f"Failed to create chain for {agent_name}: {e}")
            return None
    
    def _get_format_instructions(self, agent_name: str) -> str:
        """Get format instructions for an agent."""
        if agent_name in self.output_parsers:
            return self.output_parsers[agent_name].get_format_instructions()
        return "Please respond with valid JSON format."
    
    def parse_agent_output(self, agent_name: str, raw_output: str) -> Dict[str, Any]:
        """
        Parse agent output using LangChain parsers with fallback.
        
        Args:
            agent_name: Name of the agent
            raw_output: Raw output string from the agent
            
        Returns:
            Parsed and validated output data
        """
        try:
            # Try LangChain parsing first
            if agent_name in self.output_parsers and LANGCHAIN_AVAILABLE:
                try:
                    parsed_result = self.output_parsers[agent_name].parse(raw_output)
                    return parsed_result.dict()
                except (OutputParserException, ValidationError) as e:
                    self.logger.warning(f"LangChain parsing failed for {agent_name}: {e}")
            
            # Fallback to manual parsing
            return self._manual_parse_output(agent_name, raw_output)
            
        except Exception as e:
            self.logger.error(f"Failed to parse output for {agent_name}: {e}")
            return self._create_fallback_output(agent_name)
    
    def _manual_parse_output(self, agent_name: str, raw_output: str) -> Dict[str, Any]:
        """Manual parsing with JSON extraction and validation."""
        try:
            # Extract JSON from the response
            json_match = self._extract_json_from_text(raw_output)
            if json_match:
                parsed_data = json.loads(json_match)
                
                # Validate against the expected schema
                if agent_name in self.data_validators:
                    validator = self.data_validators[agent_name]
                    validated_data = validator(**parsed_data)
                    return validated_data.dict()
                
                return parsed_data
            
            # If no JSON found, create structured output
            return self._create_structured_output(agent_name, raw_output)
            
        except Exception as e:
            self.logger.error(f"Manual parsing failed for {agent_name}: {e}")
            return self._create_fallback_output(agent_name)
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extract JSON from text using regex patterns."""
        import re
        
        # Try to find JSON object
        json_patterns = [
            r'\{.*\}',  # Basic JSON object
            r'\[.*\]',  # JSON array
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _create_structured_output(self, agent_name: str, raw_output: str) -> Dict[str, Any]:
        """Create structured output from raw text when JSON parsing fails."""
        # Create a basic structured output based on agent type
        base_output = {
            "output": raw_output,
            "artifacts": [],
            "documentation": {},
            "metadata": {
                "parsing_method": "text_extraction",
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Add agent-specific structure
        if agent_name == "requirements_analyst":
            base_output.update({
                "functional_requirements": [],
                "non_functional_requirements": [],
                "user_stories": [],
                "technical_constraints": [],
                "assumptions": [],
                "risks": [],
                "summary": {}
            })
        elif agent_name == "architecture_designer":
            base_output.update({
                "system_overview": raw_output,
                "architecture_pattern": "unknown",
                "components": [],
                "data_flow": {},
                "technology_stack": [],
                "deployment_architecture": {},
                "security_considerations": [],
                "scalability_plan": {},
                "summary": {}
            })
        
        return base_output
    
    def _create_fallback_output(self, agent_name: str) -> Dict[str, Any]:
        """Create fallback output when all parsing methods fail."""
        return {
            "output": f"Failed to parse output for {agent_name}",
            "artifacts": [],
            "documentation": {},
            "metadata": {
                "parsing_method": "fallback",
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat(),
                "error": "All parsing methods failed"
            }
        }
    
    def prepare_agent_input(self, agent_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare input data for an agent based on its requirements.
        
        Args:
            agent_name: Name of the agent
            state: Current workflow state
            
        Returns:
            Prepared input data for the agent
        """
        base_input = {
            "project_context": state.get("project_context", ""),
            "project_name": state.get("project_name", ""),
            "session_id": state.get("session_id", "")
        }
        
        # Add agent-specific input data
        if agent_name == "requirements_analyst":
            # Requirements analyst only needs project context
            pass
        elif agent_name == "architecture_designer":
            # Architecture designer needs requirements
            base_input["requirements"] = state.get("requirements", [])
        elif agent_name == "code_generator":
            # Code generator needs requirements and architecture
            base_input["requirements"] = state.get("requirements", [])
            base_input["architecture"] = state.get("architecture", {})
        elif agent_name == "test_generator":
            # Test generator needs requirements, architecture, and code
            base_input["requirements"] = state.get("requirements", [])
            base_input["architecture"] = state.get("architecture", {})
            base_input["code_files"] = state.get("code_files", {})
        elif agent_name == "code_reviewer":
            # Code reviewer needs code files
            base_input["code_files"] = state.get("code_files", {})
            base_input["requirements"] = state.get("requirements", [])
        elif agent_name == "security_analyst":
            # Security analyst needs code, architecture, and requirements
            base_input["code_files"] = state.get("code_files", {})
            base_input["architecture"] = state.get("architecture", {})
            base_input["requirements"] = state.get("requirements", [])
        elif agent_name == "documentation_generator":
            # Documentation generator needs everything
            base_input["requirements"] = state.get("requirements", [])
            base_input["architecture"] = state.get("architecture", {})
            base_input["code_files"] = state.get("code_files", {})
            base_input["tests"] = state.get("tests", {})
        
        return base_input
    
    def validate_agent_output(self, agent_name: str, output_data: Dict[str, Any]) -> bool:
        """
        Validate agent output against expected schema.
        
        Args:
            agent_name: Name of the agent
            output_data: Output data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if agent_name in self.data_validators:
                validator = self.data_validators[agent_name]
                validator(**output_data)
                return True
            return True  # If no validator, assume valid
        except ValidationError as e:
            self.logger.error(f"Validation failed for {agent_name}: {e}")
            return False
    
    def create_agent_output(self, agent_name: str, task_name: str, output_data: Dict[str, Any], 
                          execution_time: float, success: bool, error_message: Optional[str] = None) -> AgentOutput:
        """
        Create a standardized agent output object.
        
        Args:
            agent_name: Name of the agent
            task_name: Name of the task performed
            output_data: Parsed output data
            execution_time: Time taken for execution
            success: Whether the execution was successful
            error_message: Error message if any
            
        Returns:
            Standardized agent output object
        """
        return AgentOutput(
            agent_name=agent_name,
            task_name=task_name,
            output_data=output_data,
            artifacts=output_data.get("artifacts", []),
            documentation=output_data.get("documentation", {}),
            metadata={
                "parsing_method": output_data.get("metadata", {}).get("parsing_method", "unknown"),
                "validation_status": self.validate_agent_output(agent_name, output_data),
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )


# Global instance for use across the system
data_exchange = LangChainDataExchange()
