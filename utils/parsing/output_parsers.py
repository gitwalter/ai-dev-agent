"""
Output Parsing Utilities
========================

Provides output parsing functionality for AI agents including JSON parsing,
validation, and structured output handling.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import json
import logging
from typing import Dict, Any, Optional, Type, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class OutputParser(ABC):
    """Abstract base class for output parsers."""
    
    @abstractmethod
    def parse(self, raw_output: str) -> Dict[str, Any]:
        """Parse raw output into structured format."""
        pass
    
    @abstractmethod
    def validate(self, parsed_output: Dict[str, Any]) -> bool:
        """Validate parsed output structure."""
        pass


class JSONOutputParser(OutputParser):
    """JSON output parser with error handling."""
    
    def __init__(self, required_fields: Optional[list] = None):
        """
        Initialize JSON parser.
        
        Args:
            required_fields: List of required fields in the output
        """
        self.required_fields = required_fields or []
    
    def parse(self, raw_output: str) -> Dict[str, Any]:
        """
        Parse JSON output with robust error handling.
        
        Args:
            raw_output: Raw string output to parse
            
        Returns:
            Dict containing parsed output
            
        Raises:
            ValueError: If parsing fails
        """
        if not raw_output or not raw_output.strip():
            raise ValueError("Empty output provided for parsing")
        
        # Clean the output - remove common formatting issues
        cleaned_output = self._clean_output(raw_output)
        
        try:
            parsed = json.loads(cleaned_output)
            if not isinstance(parsed, dict):
                raise ValueError("Parsed output is not a dictionary")
            
            # Validate required fields
            if not self.validate(parsed):
                raise ValueError("Parsed output failed validation")
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Output parsing error: {e}")
            raise ValueError(f"Parsing failed: {e}")
    
    def validate(self, parsed_output: Dict[str, Any]) -> bool:
        """
        Validate parsed output structure.
        
        Args:
            parsed_output: Dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(parsed_output, dict):
            return False
        
        # Check required fields
        for field in self.required_fields:
            if field not in parsed_output:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _clean_output(self, raw_output: str) -> str:
        """
        Clean raw output to improve JSON parsing success.
        
        Args:
            raw_output: Raw output string
            
        Returns:
            str: Cleaned output string
        """
        # Remove common markdown formatting
        cleaned = raw_output.strip()
        
        # Remove code block markers
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Find JSON object boundaries
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            cleaned = cleaned[start_idx:end_idx + 1]
        
        return cleaned


class CodeGenerationParser(JSONOutputParser):
    """Specialized parser for code generation outputs."""
    
    def __init__(self):
        """Initialize code generation parser."""
        required_fields = ["code", "description", "language", "dependencies"]
        super().__init__(required_fields)
    
    def validate(self, parsed_output: Dict[str, Any]) -> bool:
        """Validate code generation output."""
        if not super().validate(parsed_output):
            return False
        
        # Additional validation for code generation
        if "code" in parsed_output:
            if not isinstance(parsed_output["code"], str):
                logger.warning("Code field must be a string")
                return False
            
            if len(parsed_output["code"].strip()) < 10:
                logger.warning("Code field appears to be too short")
                return False
        
        return True


class RequirementsParser(JSONOutputParser):
    """Specialized parser for requirements analysis outputs."""
    
    def __init__(self):
        """Initialize requirements parser."""
        required_fields = ["functional_requirements", "non_functional_requirements"]
        super().__init__(required_fields)


class ArchitectureParser(JSONOutputParser):
    """Specialized parser for architecture design outputs."""
    
    def __init__(self):
        """Initialize architecture parser."""
        required_fields = ["system_overview", "components", "architecture_pattern"]
        super().__init__(required_fields)


class TestGenerationParser(JSONOutputParser):
    """Specialized parser for test generation outputs."""
    
    def __init__(self):
        """Initialize test generation parser."""
        required_fields = ["test_cases", "test_framework", "coverage"]
        super().__init__(required_fields)


class DocumentationParser(JSONOutputParser):
    """Specialized parser for documentation generation outputs."""
    
    def __init__(self):
        """Initialize documentation parser."""
        required_fields = ["documentation", "sections"]
        super().__init__(required_fields)


class OutputParserFactory:
    """Factory for creating output parsers based on agent type."""
    
    _parsers = {
        "code_generator": CodeGenerationParser,
        "requirements_analyst": RequirementsParser,
        "architecture_designer": ArchitectureParser,
        "test_generator": TestGenerationParser,
        "documentation_generator": DocumentationParser,
        "default": JSONOutputParser
    }
    
    @classmethod
    def get_parser(cls, agent_type: str, **kwargs) -> OutputParser:
        """
        Get parser for specific agent type.
        
        Args:
            agent_type: Type of agent requesting the parser
            **kwargs: Additional arguments for parser initialization
            
        Returns:
            OutputParser: Appropriate parser instance
        """
        parser_class = cls._parsers.get(agent_type, cls._parsers["default"])
        
        try:
            if agent_type == "default":
                # Default parser can accept additional arguments
                return parser_class(**kwargs)
            else:
                # Specialized parsers have fixed initialization
                return parser_class()
        except Exception as e:
            logger.error(f"Failed to create parser for {agent_type}: {e}")
            # Fallback to default parser
            return cls._parsers["default"]()
    
    @classmethod
    def register_parser(cls, agent_type: str, parser_class: Type[OutputParser]):
        """
        Register a custom parser for an agent type.
        
        Args:
            agent_type: Agent type identifier
            parser_class: Parser class to register
        """
        if not issubclass(parser_class, OutputParser):
            raise ValueError("Parser class must inherit from OutputParser")
        
        cls._parsers[agent_type] = parser_class
        logger.info(f"Registered custom parser for {agent_type}")
    
    @classmethod
    def get_available_parsers(cls) -> list:
        """Get list of available parser types."""
        return list(cls._parsers.keys())


# Convenience functions for backward compatibility
def create_parser(parser_type: str, **kwargs) -> OutputParser:
    """
    Create parser of specified type.
    
    Args:
        parser_type: Type of parser to create
        **kwargs: Additional arguments for parser
        
    Returns:
        OutputParser: Parser instance
    """
    return OutputParserFactory.get_parser(parser_type, **kwargs)

def parse_json_output(raw_output: str, required_fields: Optional[list] = None) -> Dict[str, Any]:
    """
    Parse JSON output with basic validation.
    
    Args:
        raw_output: Raw output string
        required_fields: Optional list of required fields
        
    Returns:
        Dict: Parsed output
    """
    parser = JSONOutputParser(required_fields)
    return parser.parse(raw_output)
