"""
Enhanced Output Parsing Utilities
=================================

Advanced output parsing capabilities with improved error handling,
validation, and structured output processing for AI agents.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import json
import logging
import re
from typing import Dict, Any, Optional, Type, List, Union
from abc import ABC, abstractmethod
from datetime import datetime

from .output_parsers import OutputParser, JSONOutputParser

logger = logging.getLogger(__name__)


class EnhancedOutputParser(OutputParser):
    """Enhanced output parser with advanced capabilities."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize enhanced parser.
        
        Args:
            schema: Optional JSON schema for validation
        """
        self.schema = schema
        self.parsing_history: List[Dict[str, Any]] = []
    
    def parse(self, raw_output: str) -> Dict[str, Any]:
        """Parse with enhanced error recovery."""
        start_time = datetime.now()
        
        try:
            # First attempt: direct JSON parsing
            result = self._parse_direct(raw_output)
            self._record_success(raw_output, result, start_time)
            return result
            
        except Exception as e1:
            logger.warning(f"Direct parsing failed: {e1}")
            
            try:
                # Second attempt: intelligent extraction
                result = self._parse_with_extraction(raw_output)
                self._record_success(raw_output, result, start_time)
                return result
                
            except Exception as e2:
                logger.warning(f"Extraction parsing failed: {e2}")
                
                try:
                    # Third attempt: pattern-based recovery
                    result = self._parse_with_patterns(raw_output)
                    self._record_success(raw_output, result, start_time)
                    return result
                    
                except Exception as e3:
                    logger.error(f"All parsing attempts failed: {e3}")
                    self._record_failure(raw_output, [e1, e2, e3], start_time)
                    raise ValueError(f"Enhanced parsing failed: {e3}")
    
    def _parse_direct(self, raw_output: str) -> Dict[str, Any]:
        """Direct JSON parsing attempt."""
        cleaned = self._clean_output(raw_output)
        parsed = json.loads(cleaned)
        
        if not isinstance(parsed, dict):
            raise ValueError("Output is not a dictionary")
        
        if not self.validate(parsed):
            raise ValueError("Validation failed")
        
        return parsed
    
    def _parse_with_extraction(self, raw_output: str) -> Dict[str, Any]:
        """Intelligent content extraction and parsing."""
        # Extract JSON from mixed content
        json_candidates = self._extract_json_candidates(raw_output)
        
        for candidate in json_candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and self.validate(parsed):
                    return parsed
            except:
                continue
        
        raise ValueError("No valid JSON found in extraction")
    
    def _parse_with_patterns(self, raw_output: str) -> Dict[str, Any]:
        """Pattern-based parsing for malformed content."""
        # Extract key-value pairs using patterns
        result = {}
        
        # Pattern for "key": "value" or "key": value
        kv_pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
        matches = re.findall(kv_pattern, raw_output)
        
        for key, value in matches:
            result[key] = value
        
        # Pattern for "key": number
        num_pattern = r'"([^"]+)"\s*:\s*(\d+(?:\.\d+)?)'
        num_matches = re.findall(num_pattern, raw_output)
        
        for key, value in num_matches:
            try:
                result[key] = float(value) if '.' in value else int(value)
            except:
                result[key] = value
        
        if result and self.validate(result):
            return result
        
        raise ValueError("Pattern-based parsing failed")
    
    def _extract_json_candidates(self, raw_output: str) -> List[str]:
        """Extract potential JSON objects from text."""
        candidates = []
        
        # Find all potential JSON objects
        brace_count = 0
        start_pos = None
        
        for i, char in enumerate(raw_output):
            if char == '{':
                if brace_count == 0:
                    start_pos = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_pos is not None:
                    candidate = raw_output[start_pos:i+1]
                    candidates.append(candidate)
                    start_pos = None
        
        return candidates
    
    def _clean_output(self, raw_output: str) -> str:
        """Enhanced output cleaning."""
        cleaned = raw_output.strip()
        
        # Remove various markdown formats
        patterns = [
            r'```json\s*',
            r'```\s*',
            r'`{3,}\s*',
            r'^.*?(?=\{)',  # Remove text before first {
            r'\}.*?$',      # Remove text after last }
        ]
        
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.DOTALL)
        
        # Find the main JSON object
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        
        if start != -1 and end != -1 and start < end:
            cleaned = cleaned[start:end+1]
        
        return cleaned.strip()
    
    def validate(self, parsed_output: Dict[str, Any]) -> bool:
        """Enhanced validation with schema support."""
        if not isinstance(parsed_output, dict):
            return False
        
        # Schema validation if available
        if self.schema:
            return self._validate_schema(parsed_output)
        
        # Basic validation
        return len(parsed_output) > 0
    
    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """Validate against JSON schema."""
        # Basic schema validation (can be extended with jsonschema library)
        required = self.schema.get('required', [])
        
        for field in required:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _record_success(self, raw_output: str, result: Dict[str, Any], start_time: datetime):
        """Record successful parsing."""
        duration = (datetime.now() - start_time).total_seconds()
        
        self.parsing_history.append({
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "duration": duration,
            "input_length": len(raw_output),
            "output_keys": len(result.keys()),
            "method": "enhanced"
        })
    
    def _record_failure(self, raw_output: str, errors: List[Exception], start_time: datetime):
        """Record parsing failure."""
        duration = (datetime.now() - start_time).total_seconds()
        
        self.parsing_history.append({
            "timestamp": datetime.now().isoformat(),
            "status": "failure",
            "duration": duration,
            "input_length": len(raw_output),
            "errors": [str(e) for e in errors],
            "method": "enhanced"
        })
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing performance statistics."""
        if not self.parsing_history:
            return {"total_attempts": 0}
        
        total = len(self.parsing_history)
        successes = len([h for h in self.parsing_history if h["status"] == "success"])
        failures = total - successes
        
        avg_duration = sum(h["duration"] for h in self.parsing_history) / total
        
        return {
            "total_attempts": total,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / total * 100,
            "average_duration": avg_duration
        }


class CodeGenerationEnhancedParser(EnhancedOutputParser):
    """Enhanced parser for code generation with code-specific validation."""
    
    def __init__(self):
        """Initialize code generation enhanced parser."""
        schema = {
            "required": ["code", "description", "language"],
            "properties": {
                "code": {"type": "string", "minLength": 10},
                "description": {"type": "string", "minLength": 5},
                "language": {"type": "string"},
                "dependencies": {"type": "array"}
            }
        }
        super().__init__(schema)
    
    def validate(self, parsed_output: Dict[str, Any]) -> bool:
        """Enhanced validation for code generation."""
        if not super().validate(parsed_output):
            return False
        
        # Code-specific validation
        if "code" in parsed_output:
            code = parsed_output["code"]
            if not isinstance(code, str) or len(code.strip()) < 10:
                return False
            
            # Check for basic code structure
            if not any(keyword in code for keyword in ["def ", "class ", "function ", "import ", "from "]):
                logger.warning("Code appears to lack basic structure")
        
        return True


class RequirementsEnhancedParser(EnhancedOutputParser):
    """Enhanced parser for requirements analysis."""
    
    def __init__(self):
        """Initialize requirements enhanced parser."""
        schema = {
            "required": ["functional_requirements", "non_functional_requirements"],
            "properties": {
                "functional_requirements": {"type": "array", "minItems": 1},
                "non_functional_requirements": {"type": "array", "minItems": 1}
            }
        }
        super().__init__(schema)


class EnhancedOutputParserFactory:
    """Factory for creating enhanced output parsers."""
    
    _enhanced_parsers = {
        "code_generator": CodeGenerationEnhancedParser,
        "requirements_analyst": RequirementsEnhancedParser,
        "default": EnhancedOutputParser
    }
    
    @classmethod
    def get_parser(cls, agent_type: str, **kwargs) -> EnhancedOutputParser:
        """
        Get enhanced parser for specific agent type.
        
        Args:
            agent_type: Type of agent requesting the parser
            **kwargs: Additional arguments for parser initialization
            
        Returns:
            EnhancedOutputParser: Appropriate enhanced parser instance
        """
        parser_class = cls._enhanced_parsers.get(agent_type, cls._enhanced_parsers["default"])
        
        try:
            if agent_type == "default":
                return parser_class(**kwargs)
            else:
                return parser_class()
        except Exception as e:
            logger.error(f"Failed to create enhanced parser for {agent_type}: {e}")
            return cls._enhanced_parsers["default"]()
    
    @classmethod
    def register_parser(cls, agent_type: str, parser_class: Type[EnhancedOutputParser]):
        """Register a custom enhanced parser."""
        if not issubclass(parser_class, EnhancedOutputParser):
            raise ValueError("Parser class must inherit from EnhancedOutputParser")
        
        cls._enhanced_parsers[agent_type] = parser_class
        logger.info(f"Registered enhanced parser for {agent_type}")
    
    @classmethod
    def get_available_parsers(cls) -> List[str]:
        """Get list of available enhanced parser types."""
        return list(cls._enhanced_parsers.keys())


# Convenience functions
def parse_with_enhanced_parser(content: str, parser_type: str, **kwargs) -> Dict[str, Any]:
    """
    Parse content with enhanced parser.
    
    Args:
        content: Content to parse
        parser_type: Type of parser to use
        **kwargs: Additional parser arguments
        
    Returns:
        Dict: Parsed content
    """
    parser = EnhancedOutputParserFactory.get_parser(parser_type, **kwargs)
    return parser.parse(content)

def get_enhanced_parser_stats(parser_type: str) -> Dict[str, Any]:
    """Get parsing statistics for a parser type."""
    parser = EnhancedOutputParserFactory.get_parser(parser_type)
    return parser.get_parsing_stats()
