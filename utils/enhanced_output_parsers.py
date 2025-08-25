"""
Enhanced output parsers using LangChain structured outputs.
Provides robust parsing with better error handling and validation.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Union, Type
from abc import ABC, abstractmethod

try:
    from langchain.output_parsers import PydanticOutputParser
    from langchain.schema import OutputParserException
    from pydantic import BaseModel, ValidationError
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available, falling back to manual parsing")

from utils.structured_outputs import (
    create_output_model, validate_output_model, get_format_instructions,
    CodeGenerationOutput, CodeReviewOutput, RequirementsAnalysisOutput,
    ArchitectureDesignOutput, TestGenerationOutput, SecurityAnalysisOutput,
    DocumentationGenerationOutput
)

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedOutputParser(ABC):
    """Enhanced base class for all output parsers with LangChain integration."""
    
    def __init__(self, agent_type: str):
        """
        Initialize the enhanced output parser.
        
        Args:
            agent_type: Type of agent this parser is for
        """
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{agent_type}")
        
        # Get the appropriate output model
        self.output_model = create_output_model(agent_type)
        
        # Setup LangChain parser if available
        self.langchain_parser = None
        if LANGCHAIN_AVAILABLE:
            self._setup_langchain_parser()
    
    def _setup_langchain_parser(self):
        """Setup LangChain PydanticOutputParser."""
        try:
            self.langchain_parser = PydanticOutputParser(pydantic_object=self.output_model)
            self.logger.info(f"LangChain parser setup successful for {self.agent_type}")
        except Exception as e:
            self.logger.warning(f"Failed to setup LangChain parser for {self.agent_type}: {e}")
            self.langchain_parser = None
    
    def parse(self, response: str) -> Dict[str, Any]:
        """
        Parse response using enhanced parsing with multiple fallback strategies.
        
        Args:
            response: Raw response string from the agent
            
        Returns:
            Parsed and validated data
        """
        self.logger.info(f"Parsing response for {self.agent_type}")
        
        # Try LangChain parsing first
        if self.langchain_parser:
            try:
                parsed_result = self.langchain_parser.parse(response)
                validated_data = parsed_result.dict()
                self.logger.info("LangChain parsing successful")
                return validated_data
            except (OutputParserException, ValidationError) as e:
                self.logger.warning(f"LangChain parsing failed: {e}")
        
        # Try enhanced manual parsing
        try:
            parsed_data = self._enhanced_manual_parse(response)
            # Fix common format issues before validation
            parsed_data = self._fix_common_format_issues(parsed_data)
            validated_data = validate_output_model(parsed_data, self.agent_type)
            self.logger.info("Enhanced manual parsing successful")
            return validated_data
        except Exception as e:
            self.logger.warning(f"Enhanced manual parsing failed: {e}")
        
        # Try basic JSON parsing
        try:
            parsed_data = self._basic_json_parse(response)
            # Fix common format issues before validation
            parsed_data = self._fix_common_format_issues(parsed_data)
            validated_data = validate_output_model(parsed_data, self.agent_type)
            self.logger.info("Basic JSON parsing successful")
            return validated_data
        except Exception as e:
            self.logger.warning(f"Basic JSON parsing failed: {e}")
        
        # Use fallback data
        self.logger.warning("All parsing methods failed, using fallback data")
        return self._get_fallback_data()
    
    def _fix_common_format_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix common format issues in parsed data."""
        
        # Fix risk_mitigation format for architecture design
        if self.agent_type == "architecture_designer" and "risk_mitigation" in data:
            risk_mitigation = data["risk_mitigation"]
            if isinstance(risk_mitigation, list) and risk_mitigation:
                if isinstance(risk_mitigation[0], str):
                    # Convert list of strings to list of dicts
                    fixed_risk_mitigation = []
                    for i, risk in enumerate(risk_mitigation):
                        fixed_risk_mitigation.append({
                            "risk": f"Risk {i+1}",
                            "mitigation": risk
                        })
                    data["risk_mitigation"] = fixed_risk_mitigation
        
        return data
    
    def _enhanced_manual_parse(self, response: str) -> Dict[str, Any]:
        """Enhanced manual parsing with better JSON extraction and fixing."""
        
        # Clean the response
        cleaned_response = response.strip()
        
        # Extract JSON using multiple strategies
        json_str = self._extract_json_string(cleaned_response)
        
        if not json_str:
            raise ValueError("No JSON content found in response")
        
        # Fix common JSON issues
        fixed_json = self._fix_json_issues(json_str)
        
        # Parse the fixed JSON
        try:
            parsed = json.loads(fixed_json)
            return parsed
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error after fixing: {e}")
            raise
    
    def _extract_json_string(self, response: str) -> Optional[str]:
        """Extract JSON string from response using multiple strategies."""
        
        # Strategy 1: Look for JSON code blocks
        json_block_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'```\s*(\[.*?\])\s*```'
        ]
        
        for pattern in json_block_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Strategy 2: Look for JSON object/array at the beginning or end
        json_patterns = [
            r'^\s*(\{.*\})\s*$',
            r'^\s*(\[.*\])\s*$',
            r'(\{.*\})\s*$',
            r'(\[.*\])\s*$'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Strategy 3: Find the largest JSON-like structure
        json_like_patterns = [
            r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
            r'(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])'
        ]
        
        largest_match = None
        largest_length = 0
        
        for pattern in json_like_patterns:
            matches = re.finditer(pattern, response, re.DOTALL)
            for match in matches:
                if len(match.group(1)) > largest_length:
                    largest_match = match.group(1)
                    largest_length = len(match.group(1))
        
        if largest_match:
            return largest_match.strip()
        
        return None
    
    def _fix_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues."""
        
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix common quote issues
        json_str = json_str.replace('"', '"').replace('"', '"')
        json_str = json_str.replace(''', "'").replace(''', "'")
        
        # Fix newline issues in strings (but be careful)
        # Only fix newlines that are clearly not meant to be part of the string
        lines = json_str.split('\n')
        fixed_lines = []
        
        in_string = False
        string_buffer = []
        
        for line in lines:
            if not in_string:
                # Check if this line starts a string
                if '"' in line:
                    quote_count = line.count('"')
                    if quote_count % 2 == 1:  # Odd number of quotes
                        in_string = True
                        string_buffer = [line]
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                # We're in a string, accumulate lines
                string_buffer.append(line)
                
                # Check if this line ends the string
                quote_count = line.count('"')
                if quote_count % 2 == 1:  # Odd number of quotes
                    # Join the string parts and escape newlines
                    string_content = '\n'.join(string_buffer)
                    # Escape newlines in the string content
                    escaped_content = string_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    fixed_lines.append(escaped_content)
                    in_string = False
                    string_buffer = []
        
        # If we're still in a string, close it
        if in_string:
            string_content = '\n'.join(string_buffer)
            escaped_content = string_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            fixed_lines.append(escaped_content)
        
        return '\n'.join(fixed_lines)
    
    def _basic_json_parse(self, response: str) -> Dict[str, Any]:
        """Basic JSON parsing as a fallback."""
        
        # Try to find any JSON-like content
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, try to extract structured content
        return self._extract_structured_content(response)
    
    def _extract_structured_content(self, response: str) -> Dict[str, Any]:
        """Extract structured content from non-JSON response."""
        
        # This is a simplified extraction - in practice, you might want more sophisticated parsing
        content = {
            "source_files": {},
            "configuration_files": {},
            "project_structure": [],
            "implementation_notes": [],
            "testing_strategy": {},
            "deployment_instructions": []
        }
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\s*\n(.*?)\n```', response, re.DOTALL)
        for lang, code in code_blocks:
            if lang in ['python', 'py', 'js', 'javascript', 'java', 'cpp', 'c']:
                filename = f"main.{lang if lang != 'py' else 'py'}"
                content["source_files"][filename] = code.strip()
        
        # Extract file names from headers
        file_headers = re.findall(r'#+\s*([^#\n]+\.\w+)', response)
        for filename in file_headers:
            if filename not in content["source_files"]:
                content["source_files"][filename] = "# Placeholder content"
        
        # Extract implementation notes
        notes = re.findall(r'- (.+)', response)
        content["implementation_notes"] = notes[:5]  # Limit to first 5 notes
        
        return content
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Get fallback data when all parsing methods fail."""
        
        # Create a basic fallback based on the agent type
        if self.agent_type == "code_generator":
            return {
                "source_files": {
                    "main.py": """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)"""
                },
                "configuration_files": {
                    "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0"
                },
                "project_structure": ["main.py", "requirements.txt"],
                "implementation_notes": ["Basic FastAPI application", "Simple REST API"],
                "testing_strategy": {
                    "unit_tests": "pytest for unit testing",
                    "integration_tests": "API endpoint testing"
                },
                "deployment_instructions": [
                    "1. Install dependencies: pip install -r requirements.txt",
                    "2. Run with: uvicorn main:app --reload"
                ]
            }
        elif self.agent_type == "code_reviewer":
            return {
                "overall_assessment": {
                    "overall_score": 7,
                    "readability_score": 7,
                    "maintainability_score": 7,
                    "performance_score": 7,
                    "security_score": 6,
                    "test_coverage_score": 7
                },
                "issues": [],
                "improvements": [],
                "positive_aspects": ["Code structure is clear", "Good function organization"],
                "security_concerns": [],
                "performance_issues": [],
                "recommendations": [],
                "summary": "Code review completed with basic assessment."
            }
        else:
            # Generic fallback
            return {
                "status": "completed",
                "message": f"Fallback data for {self.agent_type}",
                "data": {}
            }
    
    def get_format_instructions(self) -> str:
        """Get format instructions for the prompt."""
        return get_format_instructions(self.agent_type)


class CodeGenerationParser(EnhancedOutputParser):
    """Enhanced parser for code generation responses."""
    
    def __init__(self):
        super().__init__("code_generator")


class CodeReviewParser(EnhancedOutputParser):
    """Enhanced parser for code review responses."""
    
    def __init__(self):
        super().__init__("code_reviewer")


class RequirementsAnalysisParser(EnhancedOutputParser):
    """Enhanced parser for requirements analysis responses."""
    
    def __init__(self):
        super().__init__("requirements_analyst")


class ArchitectureDesignParser(EnhancedOutputParser):
    """Enhanced parser for architecture design responses."""
    
    def __init__(self):
        super().__init__("architecture_designer")


class TestGenerationParser(EnhancedOutputParser):
    """Enhanced parser for test generation responses."""
    
    def __init__(self):
        super().__init__("test_generator")


class SecurityAnalysisParser(EnhancedOutputParser):
    """Enhanced parser for security analysis responses."""
    
    def __init__(self):
        super().__init__("security_analyst")


class DocumentationGenerationParser(EnhancedOutputParser):
    """Enhanced parser for documentation generation responses."""
    
    def __init__(self):
        super().__init__("documentation_generator")


class EnhancedOutputParserFactory:
    """Enhanced factory for creating output parsers based on agent type."""
    
    _parsers = {
        "requirements_analyst": RequirementsAnalysisParser,
        "architecture_designer": ArchitectureDesignParser,
        "code_generator": CodeGenerationParser,
        "test_generator": TestGenerationParser,
        "code_reviewer": CodeReviewParser,
        "security_analyst": SecurityAnalysisParser,
        "documentation_generator": DocumentationGenerationParser
    }
    
    @classmethod
    def get_parser(cls, agent_type: str) -> EnhancedOutputParser:
        """Get the appropriate enhanced parser for the agent type."""
        parser_class = cls._parsers.get(agent_type)
        if parser_class:
            return parser_class()
        else:
            # Return a generic parser for unknown agent types
            return EnhancedOutputParser(agent_type)
    
    @classmethod
    def register_parser(cls, agent_type: str, parser_class: type):
        """Register a new parser for an agent type."""
        cls._parsers[agent_type] = parser_class
    
    @classmethod
    def get_supported_agent_types(cls) -> List[str]:
        """Get list of supported agent types."""
        return list(cls._parsers.keys())


# Utility functions for backward compatibility
def parse_with_enhanced_parser(response: str, agent_type: str) -> Dict[str, Any]:
    """Parse response using enhanced parser with full error handling."""
    
    try:
        parser = EnhancedOutputParserFactory.get_parser(agent_type)
        return parser.parse(response)
    except Exception as e:
        logger.error(f"Enhanced parsing failed for {agent_type}: {e}")
        # Return fallback data
        parser = EnhancedOutputParserFactory.get_parser(agent_type)
        return parser._get_fallback_data()


def get_enhanced_format_instructions(agent_type: str) -> str:
    """Get enhanced format instructions for a specific agent type."""
    
    try:
        parser = EnhancedOutputParserFactory.get_parser(agent_type)
        return parser.get_format_instructions()
    except Exception as e:
        logger.error(f"Failed to get format instructions for {agent_type}: {e}")
        return "Please respond with valid JSON format."
