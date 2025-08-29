"""
Parsing Utilities Package
=========================

Provides comprehensive parsing utilities for AI agent outputs including
JSON parsing, enhanced parsing, and structured output handling.

Modules:
- output_parsers: Basic output parsing functionality
- enhanced_output_parsers: Advanced parsing with error recovery

Author: AI-Dev-Agent System
Version: 1.0
"""

from .output_parsers import (
    OutputParser,
    JSONOutputParser,
    CodeGenerationParser,
    RequirementsParser,
    ArchitectureParser,
    TestGenerationParser,
    DocumentationParser,
    OutputParserFactory,
    create_parser,
    parse_json_output
)

from .enhanced_output_parsers import (
    EnhancedOutputParser,
    CodeGenerationEnhancedParser,
    RequirementsEnhancedParser,
    EnhancedOutputParserFactory,
    parse_with_enhanced_parser,
    get_enhanced_parser_stats
)

__all__ = [
    # Basic parsers
    "OutputParser",
    "JSONOutputParser", 
    "CodeGenerationParser",
    "RequirementsParser",
    "ArchitectureParser",
    "TestGenerationParser",
    "DocumentationParser",
    "OutputParserFactory",
    "create_parser",
    "parse_json_output",
    
    # Enhanced parsers
    "EnhancedOutputParser",
    "CodeGenerationEnhancedParser",
    "RequirementsEnhancedParser", 
    "EnhancedOutputParserFactory",
    "parse_with_enhanced_parser",
    "get_enhanced_parser_stats"
]
