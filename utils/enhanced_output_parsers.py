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
        
        # All parsing methods failed - raise exception instead of using fallback
        error_msg = f"All parsing methods failed for {self.agent_type}. Response could not be parsed into valid format."
        self.logger.error(error_msg)
        raise OutputParserException(error_msg)
    
    def _fix_common_format_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix common format issues in parsed data."""
        
        # Fix source_files format for code generator - convert strings to SourceFile objects
        if self.agent_type == "code_generator" and "source_files" in data:
            if isinstance(data["source_files"], dict):
                fixed_source_files = {}
                for filename, content in data["source_files"].items():
                    if isinstance(content, str):
                        # Convert string content to SourceFile object
                        fixed_source_files[filename] = {
                            "filename": filename,
                            "content": content,
                            "language": self._detect_language(filename),
                            "purpose": self._detect_purpose(filename)
                        }
                    elif isinstance(content, dict):
                        # Ensure it has required fields
                        if "content" not in content:
                            content["content"] = "# Placeholder content"
                        if "filename" not in content:
                            content["filename"] = filename
                        if "language" not in content:
                            content["language"] = self._detect_language(filename)
                        if "purpose" not in content:
                            content["purpose"] = self._detect_purpose(filename)
                        fixed_source_files[filename] = content
                data["source_files"] = fixed_source_files
        
        # Fix configuration_files format for code generator
        if self.agent_type == "code_generator" and "configuration_files" in data:
            if isinstance(data["configuration_files"], dict):
                fixed_config_files = {}
                for filename, content in data["configuration_files"].items():
                    if isinstance(content, str):
                        # Convert string content to ConfigurationFile object
                        fixed_config_files[filename] = {
                            "filename": filename,
                            "content": content,
                            "file_type": self._detect_file_type(filename),
                            "description": f"Configuration file: {filename}"
                        }
                    elif isinstance(content, dict):
                        # Ensure it has required fields
                        if "content" not in content:
                            content["content"] = "# Placeholder content"
                        if "filename" not in content:
                            content["filename"] = filename
                        if "file_type" not in content:
                            content["file_type"] = self._detect_file_type(filename)
                        if "description" not in content:
                            content["description"] = f"Configuration file: {filename}"
                        fixed_config_files[filename] = content
                data["configuration_files"] = fixed_config_files

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
        
        # Fix security analysis output format
        if self.agent_type == "security_analyst":
            # Fix vulnerabilities format
            if "vulnerabilities" in data and isinstance(data["vulnerabilities"], list):
                fixed_vulnerabilities = []
                for vuln in data["vulnerabilities"]:
                    if isinstance(vuln, dict):
                        # Map LLM output fields to expected Pydantic fields
                        fixed_vuln = {
                            "title": vuln.get("title") or vuln.get("name") or vuln.get("id") or "Security Vulnerability",
                            "description": vuln.get("description") or vuln.get("details") or vuln.get("summary") or "Security vulnerability identified",
                            "severity": vuln.get("severity") or vuln.get("level") or "medium",
                            "category": vuln.get("category") or vuln.get("type") or "security",
                            "location": vuln.get("location") or vuln.get("file") or "Unknown",
                            "suggestion": vuln.get("suggestion") or vuln.get("mitigation") or "Implement security best practices",
                            "impact": vuln.get("impact") or "Security vulnerability that needs to be addressed"
                        }
                        fixed_vulnerabilities.append(fixed_vuln)
                data["vulnerabilities"] = fixed_vulnerabilities
        
        # Fix documentation generator output format
        if self.agent_type == "documentation_generator":
            # Ensure diagrams field is present
            if "diagrams" not in data:
                data["diagrams"] = {}
            
            # Fix documentation_files format
            if "documentation_files" in data and isinstance(data["documentation_files"], dict):
                # Clean up any malformed content in documentation files
                fixed_doc_files = {}
                for filename, content in data["documentation_files"].items():
                    if isinstance(content, str):
                        # Fix common string issues
                        fixed_content = content
                        # Remove any unterminated quotes or braces
                        fixed_content = re.sub(r'(["\'])([^"\']*)$', r'\1\2"', fixed_content)
                        fixed_content = re.sub(r'([{[])([^{}\]]*)$', r'\1\2}', fixed_content)
                        fixed_doc_files[filename] = fixed_content
                    else:
                        fixed_doc_files[filename] = content
                data["documentation_files"] = fixed_doc_files
            
            # Fix documentation_summary format
            if "documentation_summary" not in data:
                data["documentation_summary"] = {
                    "coverage_score": "5/10",
                    "completeness": "50%",
                    "quality_metrics": {}
                }
            
            # Fix security recommendations format
            if "security_recommendations" in data and isinstance(data["security_recommendations"], list):
                fixed_recommendations = []
                for rec in data["security_recommendations"]:
                    if isinstance(rec, dict):
                        # Map LLM output fields to expected Pydantic fields
                        fixed_rec = {
                            "title": rec.get("title") or rec.get("name") or rec.get("recommendation") or "Security Recommendation",
                            "description": rec.get("description") or rec.get("details") or rec.get("summary") or "Security improvement recommendation",
                            "priority": rec.get("priority") or rec.get("severity") or "medium",
                            "category": rec.get("category") or rec.get("type") or "security",
                            "implementation_effort": rec.get("implementation_effort") or rec.get("effort") or "medium",
                            "benefits": rec.get("benefits") or rec.get("impact") or "Improved security",
                            "steps": rec.get("steps") or rec.get("actions") or ["Implement the recommended security measure"]
                        }
                        # Fix priority enum values
                        if fixed_rec["priority"] == "immediate":
                            fixed_rec["priority"] = "critical"
                        elif fixed_rec["priority"] not in ["low", "medium", "high", "critical"]:
                            fixed_rec["priority"] = "medium"
                        
                        # Ensure benefits is a list
                        if isinstance(fixed_rec["benefits"], str):
                            fixed_rec["benefits"] = [fixed_rec["benefits"]]
                        elif not isinstance(fixed_rec["benefits"], list):
                            fixed_rec["benefits"] = ["Improved security"]
                        
                        fixed_recommendations.append(fixed_rec)
                data["security_recommendations"] = fixed_recommendations
            
            # Fix compliance requirements format
            if "compliance_requirements" in data and isinstance(data["compliance_requirements"], list):
                fixed_compliance = []
                for req in data["compliance_requirements"]:
                    if isinstance(req, dict):
                        # Convert dict to string
                        if "framework" in req and "requirement" in req:
                            fixed_compliance.append(f"{req['framework']}: {req['requirement']}")
                        elif "framework" in req:
                            fixed_compliance.append(f"{req['framework']} compliance")
                        else:
                            fixed_compliance.append(str(req))
                    elif isinstance(req, str):
                        fixed_compliance.append(req)
                data["compliance_requirements"] = fixed_compliance
        
        # Fix code reviewer output format
        if self.agent_type == "code_reviewer":
            # Fix security concerns format
            if "security_concerns" in data and isinstance(data["security_concerns"], list):
                fixed_security_concerns = []
                for concern in data["security_concerns"]:
                    if isinstance(concern, dict):
                        # Map LLM output fields to expected Pydantic fields
                        fixed_concern = {
                            "title": concern.get("title") or concern.get("vulnerability") or concern.get("name") or "Security Concern",
                            "description": concern.get("description") or concern.get("details") or concern.get("summary") or "Security concern identified",
                            "severity": concern.get("severity") or concern.get("level") or "medium",
                            "category": concern.get("category") or concern.get("type") or "security",
                            "location": concern.get("location") or concern.get("file") or "Unknown",
                            "suggestion": concern.get("suggestion") or concern.get("recommendation") or "Address the security concern",
                            "impact": concern.get("impact") or "Potential security vulnerability"
                        }
                        fixed_security_concerns.append(fixed_concern)
                data["security_concerns"] = fixed_security_concerns
            
            # Fix performance issues format
            if "performance_issues" in data and isinstance(data["performance_issues"], list):
                fixed_performance_issues = []
                for issue in data["performance_issues"]:
                    if isinstance(issue, dict):
                        # Map LLM output fields to expected Pydantic fields
                        fixed_issue = {
                            "title": issue.get("title") or issue.get("issue") or issue.get("name") or "Performance Issue",
                            "description": issue.get("description") or issue.get("details") or issue.get("summary") or "Performance issue identified",
                            "severity": issue.get("severity") or issue.get("level") or "medium",
                            "category": issue.get("category") or issue.get("type") or "performance",
                            "location": issue.get("location") or issue.get("file") or "Unknown",
                            "suggestion": issue.get("suggestion") or issue.get("recommendation") or "Optimize the code",
                            "impact": issue.get("impact") or "Performance degradation"
                        }
                        fixed_performance_issues.append(fixed_issue)
                data["performance_issues"] = fixed_performance_issues
            
            # Fix recommendations format
            if "recommendations" in data and isinstance(data["recommendations"], list):
                fixed_recommendations = []
                for rec in data["recommendations"]:
                    if isinstance(rec, dict):
                        # Map LLM output fields to expected Pydantic fields
                        fixed_rec = {
                            "title": rec.get("title") or rec.get("recommendation") or rec.get("name") or "Code Improvement",
                            "description": rec.get("description") or rec.get("details") or rec.get("summary") or "Code improvement recommendation",
                            "priority": rec.get("priority") or rec.get("type") or "medium",
                            "category": rec.get("category") or rec.get("type") or "improvement",
                            "implementation_effort": rec.get("implementation_effort") or rec.get("effort") or "medium",
                            "benefits": rec.get("benefits") or rec.get("impact") or "Improved code quality",
                            "steps": rec.get("steps") or rec.get("actions") or ["Implement the recommended improvement"]
                        }
                        # Fix priority enum values
                        if fixed_rec["priority"] == "immediate":
                            fixed_rec["priority"] = "critical"
                        elif fixed_rec["priority"] == "short_term":
                            fixed_rec["priority"] = "high"
                        elif fixed_rec["priority"] == "long_term":
                            fixed_rec["priority"] = "low"
                        elif fixed_rec["priority"] not in ["low", "medium", "high", "critical"]:
                            fixed_rec["priority"] = "medium"
                        
                        # Ensure benefits is a list
                        if isinstance(fixed_rec["benefits"], str):
                            fixed_rec["benefits"] = [fixed_rec["benefits"]]
                        elif not isinstance(fixed_rec["benefits"], list):
                            fixed_rec["benefits"] = ["Improved code quality"]
                        
                        fixed_recommendations.append(fixed_rec)
                data["recommendations"] = fixed_recommendations
            
            # Fix summary length
            if "summary" in data and isinstance(data["summary"], str) and len(data["summary"]) > 500:
                data["summary"] = data["summary"][:497] + "..."
        
        # Fix test generator output format
        if self.agent_type == "test_generator":
            # Fix test_categories format - convert dict items to strings
            if "test_categories" in data and isinstance(data["test_categories"], dict):
                fixed_test_categories = {}
                for category, tests in data["test_categories"].items():
                    if isinstance(tests, list):
                        # Convert each test dict to a string
                        fixed_tests = []
                        for test in tests:
                            if isinstance(test, dict):
                                test_name = test.get("test_name", "Unknown Test")
                                test_desc = test.get("description", "Test description")
                                fixed_tests.append(f"{test_name}: {test_desc}")
                            elif isinstance(test, str):
                                fixed_tests.append(test)
                        fixed_test_categories[category] = fixed_tests
                    else:
                        fixed_test_categories[category] = [str(tests)]
                data["test_categories"] = fixed_test_categories
        
        return data
    
    def _enhanced_manual_parse(self, response: str) -> Dict[str, Any]:
        """
        Enhanced manual parsing with better handling of complex responses.
        
        Args:
            response: Raw response string
            
        Returns:
            Parsed data dictionary
        """
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response")
        
        json_str = json_match.group(0)
        
        # Try to fix common JSON issues
        json_str = self._fix_json_issues(json_str)
        
        try:
            parsed_data = json.loads(json_str)
            
            # Fix filename length issues by truncating long filenames
            parsed_data = self._fix_filename_lengths(parsed_data)
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            # If JSON parsing still fails, try to extract code blocks manually
            self.logger.warning(f"JSON parsing failed after fixing: {e}")
            return self._extract_code_blocks_manually(response)
    
    def _fix_filename_lengths(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix filename length issues by truncating long filenames.
        
        Args:
            data: Parsed data dictionary
            
        Returns:
            Data with fixed filenames
        """
        # Fix source files
        if "source_files" in data and isinstance(data["source_files"], dict):
            fixed_source_files = {}
            for filename, content in data["source_files"].items():
                # Truncate filename if too long
                if len(filename) > 255:
                    # Try to extract a meaningful filename from the content
                    new_filename = self._extract_meaningful_filename(filename, content)
                    if len(new_filename) > 255:
                        # Fallback: use first part of filename
                        new_filename = filename[:250] + "..."
                else:
                    new_filename = filename
                
                fixed_source_files[new_filename] = content
            
            data["source_files"] = fixed_source_files
        
        # Fix configuration files
        if "configuration_files" in data and isinstance(data["configuration_files"], dict):
            fixed_config_files = {}
            for filename, content in data["configuration_files"].items():
                # Truncate filename if too long
                if len(filename) > 255:
                    new_filename = self._extract_meaningful_filename(filename, content)
                    if len(new_filename) > 255:
                        new_filename = filename[:250] + "..."
                else:
                    new_filename = filename
                
                fixed_config_files[new_filename] = content
            
            data["configuration_files"] = fixed_config_files
        
        return data
    
    def _extract_meaningful_filename(self, long_filename: str, content: Any) -> str:
        """
        Extract a meaningful filename from content or long filename.
        
        Args:
            long_filename: The original long filename
            content: File content
            
        Returns:
            Meaningful filename
        """
        # If the long filename contains code content, try to extract a proper filename
        if isinstance(content, dict):
            content_str = content.get("content", "")
        else:
            content_str = str(content)
        
        # First, try to extract a proper filename from the long filename
        # Look for patterns like "filename.py" or "filename.txt"
        import re
        
        # Try to find a proper filename pattern in the long filename
        filename_pattern = r'([a-zA-Z0-9_-]+\.(py|js|ts|java|txt|json|yml|yaml|md|html|css|sql))'
        match = re.search(filename_pattern, long_filename)
        if match:
            return match.group(1)
        
        # Try to find common file patterns in the content
        content_lower = content_str.lower()
        
        # Python files
        if "from fastapi import" in content_str or "fastapi" in content_lower:
            return "main.py"
        elif "class Settings" in content_str or "basesettings" in content_lower:
            return "config.py"
        elif "sqlalchemy" in content_lower or "create_engine" in content_lower:
            return "database.py"
        elif "class " in content_str and ("user" in content_lower or "product" in content_lower or "order" in content_lower):
            return "models.py"
        elif "@router" in content_str or "apirouter" in content_lower:
            return "endpoints.py"
        elif "crud" in content_lower or "crud_" in content_lower:
            return "crud.py"
        elif "auth" in content_lower or "jwt" in content_lower or "login" in content_lower:
            return "auth.py"
        elif "test" in content_lower and ("pytest" in content_lower or "def test_" in content_str):
            return "test_main.py"
        
        # Configuration files
        elif "requirements" in content_lower or "fastapi" in content_lower or "uvicorn" in content_lower:
            return "requirements.txt"
        elif "package.json" in content_str or "npm" in content_lower:
            return "package.json"
        elif "docker" in content_lower:
            if "compose" in content_lower:
                return "docker-compose.yml"
            else:
                return "Dockerfile"
        elif "nginx" in content_lower:
            return "nginx.conf"
        elif "postgres" in content_lower or "postgresql" in content_lower:
            return "database.sql"
        
        # Documentation files
        elif "readme" in content_lower or "# " in content_str:
            return "README.md"
        elif "api" in content_lower and "doc" in content_lower:
            return "API.md"
        
        # Try to extract from the long filename based on content
        else:
            # Look for file extensions in the long filename
            if ".py" in long_filename:
                # Try to extract a meaningful name
                py_match = re.search(r'([a-zA-Z0-9_-]+)\.py', long_filename)
                if py_match:
                    name = py_match.group(1)
                    if len(name) <= 50:  # Reasonable length
                        return f"{name}.py"
                return "main.py"
            elif ".txt" in long_filename:
                return "requirements.txt"
            elif ".json" in long_filename:
                return "package.json"
            elif ".yml" in long_filename or ".yaml" in long_filename:
                return "docker-compose.yml"
            elif ".md" in long_filename:
                return "README.md"
            elif ".sql" in long_filename:
                return "database.sql"
            elif ".html" in long_filename:
                return "index.html"
            elif ".css" in long_filename:
                return "styles.css"
            elif ".js" in long_filename:
                return "app.js"
            else:
                # Fallback: use a generic name based on content type
                if "import " in content_str or "def " in content_str:
                    return "main.py"
                elif "{" in content_str and "}" in content_str:
                    return "config.json"
                else:
                    return "generated_file.py"
    
    def _extract_code_blocks_manually(self, response: str) -> Dict[str, Any]:
        """
        Extract code blocks manually when JSON parsing fails.
        
        Args:
            response: Raw response string
            
        Returns:
            Parsed data dictionary
        """
        self.logger.info("Extracting code blocks manually due to JSON parsing failure")
        
        # Initialize result structure
        result = {
            "source_files": {},
            "configuration_files": {},
            "project_structure": [],
            "implementation_notes": [],
            "testing_strategy": [],
            "deployment_instructions": []
        }
        
        # Split response into lines
        lines = response.split('\n')
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            # Look for file indicators
            if line.strip().startswith('"') and ('.py' in line or '.txt' in line or '.json' in line):
                # Save previous file if exists
                if current_file and current_content:
                    content = '\n'.join(current_content)
                    if current_file.endswith(('.py', '.js', '.ts', '.java')):
                        result["source_files"][current_file] = {"content": content, "language": "python"}
                    else:
                        result["configuration_files"][current_file] = {"content": content, "language": "text"}
                
                # Start new file
                current_file = line.strip().strip('"').strip(':').strip('"')
                current_content = []
                in_code_block = True
                continue
            
            # If we're in a code block, collect content
            if in_code_block and current_file:
                current_content.append(line)
        
        # Save the last file
        if current_file and current_content:
            content = '\n'.join(current_content)
            if current_file.endswith(('.py', '.js', '.ts', '.java')):
                result["source_files"][current_file] = {"content": content, "language": "python"}
            else:
                result["configuration_files"][current_file] = {"content": content, "language": "text"}
        
        # If no files were extracted, try a different approach
        if not result["source_files"] and not result["configuration_files"]:
            # Look for code blocks with ``` markers
            code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', response, re.DOTALL)
            for i, (lang, code) in enumerate(code_blocks):
                if lang and lang.lower() in ['python', 'py']:
                    filename = f"generated_file_{i+1}.py"
                    result["source_files"][filename] = {"content": code, "language": "python"}
                elif lang and lang.lower() in ['json']:
                    filename = f"config_{i+1}.json"
                    result["configuration_files"][filename] = {"content": code, "language": "json"}
                else:
                    filename = f"file_{i+1}.txt"
                    result["configuration_files"][filename] = {"content": code, "language": "text"}
        
        return result
    
    def _fix_source_files_structure(self, source_files: Any) -> Dict[str, Any]:
        """
        Fix source files structure to ensure proper filename/content separation.
        
        Args:
            source_files: Raw source files data
            
        Returns:
            Fixed source files structure
        """
        if not isinstance(source_files, dict):
            return {}
        
        fixed_files = {}
        
        for key, value in source_files.items():
            if isinstance(value, str):
                # If the value is a string, it's the content
                # Extract a proper filename from the key
                filename = self._extract_proper_filename(key)
                fixed_files[filename] = {
                    "filename": filename,
                    "content": value,
                    "language": self._detect_language(filename),
                    "purpose": self._detect_purpose(filename)
                }
            elif isinstance(value, dict):
                # If the value is already a dict, ensure it has the right structure
                if "content" in value:
                    # Extract proper filename
                    filename = self._extract_proper_filename(key)
                    fixed_files[filename] = {
                        "filename": filename,
                        "content": value["content"],
                        "language": value.get("language") or self._detect_language(filename),
                        "purpose": value.get("purpose") or self._detect_purpose(filename)
                    }
                else:
                    # Assume the entire dict is content
                    filename = self._extract_proper_filename(key)
                    fixed_files[filename] = {
                        "filename": filename,
                        "content": str(value),
                        "language": self._detect_language(filename),
                        "purpose": self._detect_purpose(filename)
                    }
        
        return fixed_files
    
    def _fix_configuration_files_structure(self, config_files: Any) -> Dict[str, Any]:
        """
        Fix configuration files structure to ensure proper filename/content separation.
        
        Args:
            config_files: Raw configuration files data
            
        Returns:
            Fixed configuration files structure
        """
        if not isinstance(config_files, dict):
            return {}
        
        fixed_files = {}
        
        for key, value in config_files.items():
            if isinstance(value, str):
                # If the value is a string, it's the content
                filename = self._extract_proper_filename(key)
                fixed_files[filename] = {
                    "filename": filename,
                    "content": value,
                    "file_type": self._detect_config_type(filename),
                    "description": self._detect_config_description(filename)
                }
            elif isinstance(value, dict):
                # If the value is already a dict, ensure it has the right structure
                if "content" in value:
                    filename = self._extract_proper_filename(key)
                    fixed_files[filename] = {
                        "filename": filename,
                        "content": value["content"],
                        "file_type": value.get("file_type") or self._detect_config_type(filename),
                        "description": value.get("description") or self._detect_config_description(filename)
                    }
                else:
                    # Assume the entire dict is content
                    filename = self._extract_proper_filename(key)
                    fixed_files[filename] = {
                        "filename": filename,
                        "content": str(value),
                        "file_type": self._detect_config_type(filename),
                        "description": self._detect_config_description(filename)
                    }
        
        return fixed_files
    
    def _extract_proper_filename(self, key: str) -> str:
        """
        Extract a proper filename from a potentially long key.
        
        Args:
            key: The original key which might be too long
            
        Returns:
            A proper filename (max 255 characters)
        """
        # If the key is already a reasonable filename, use it
        if len(key) <= 255 and '/' in key or '.' in key:
            # Extract just the filename part if it's a path
            if '/' in key:
                return key.split('/')[-1]
            return key
        
        # If the key is too long, try to extract a meaningful filename
        if len(key) > 255:
            # Look for common file extensions
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']
            for ext in extensions:
                if ext in key:
                    # Find the last occurrence of the extension
                    parts = key.split(ext)
                    if len(parts) > 1:
                        # Take the part before the extension and add the extension
                        base = parts[0]
                        if len(base) > 250:  # Leave room for extension
                            base = base[-250:]
                        return base + ext
            
            # If no extension found, create a generic filename
            return f"file_{hash(key) % 10000}.txt"
        
        return key
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'h': 'c',
            'cs': 'csharp',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala'
        }
        return language_map.get(ext, 'unknown')
    
    def _detect_purpose(self, filename: str) -> str:
        """Detect file purpose from filename."""
        filename_lower = filename.lower()
        if 'main' in filename_lower or 'app' in filename_lower:
            return "Main application entry point"
        elif 'model' in filename_lower:
            return "Data model definition"
        elif 'api' in filename_lower or 'router' in filename_lower:
            return "API endpoint definitions"
        elif 'auth' in filename_lower or 'jwt' in filename_lower:
            return "Authentication and authorization"
        elif 'config' in filename_lower or 'settings' in filename_lower:
            return "Configuration and settings"
        elif 'db' in filename_lower or 'database' in filename_lower:
            return "Database related code"
        elif 'schema' in filename_lower:
            return "Data schema definition"
        elif 'test' in filename_lower:
            return "Test file"
        elif 'util' in filename_lower or 'helper' in filename_lower:
            return "Utility and helper functions"
        else:
            return "Source code file"
    
    def _detect_file_type(self, filename: str) -> str:
        """Detect configuration file type from filename."""
        filename_lower = filename.lower()
        if filename_lower == 'requirements.txt':
            return "requirements"
        elif filename_lower == 'dockerfile':
            return "docker"
        elif filename_lower.endswith('.yml') or filename_lower.endswith('.yaml'):
            return "yaml"
        elif filename_lower.endswith('.json'):
            return "json"
        elif filename_lower.endswith('.toml'):
            return "toml"
        elif filename_lower.endswith('.ini'):
            return "ini"
        elif filename_lower.endswith('.env') or filename_lower.startswith('.env'):
            return "environment"
        elif filename_lower.endswith('.conf') or filename_lower.endswith('.config'):
            return "config"
        elif filename_lower.endswith('.xml'):
            return "xml"
        elif filename_lower.endswith('.md') or filename_lower.endswith('.markdown'):
            return "markdown"
        elif filename_lower.endswith('.txt'):
            return "text"
        else:
            return "generic"
    
    def _detect_config_type(self, filename: str) -> str:
        """Detect configuration file type from filename."""
        filename_lower = filename.lower()
        if 'requirements' in filename_lower:
            return "requirements"
        elif 'package' in filename_lower:
            return "package"
        elif 'docker' in filename_lower:
            return "docker"
        elif 'docker-compose' in filename_lower:
            return "docker-compose"
        elif 'gitignore' in filename_lower:
            return "gitignore"
        elif 'env' in filename_lower:
            return "environment"
        elif 'config' in filename_lower or 'settings' in filename_lower:
            return "configuration"
        elif 'yaml' in filename_lower or 'yml' in filename_lower:
            return "yaml"
        elif 'json' in filename_lower:
            return "json"
        elif 'toml' in filename_lower:
            return "toml"
        elif 'ini' in filename_lower:
            return "ini"
        else:
            return "configuration"
    
    def _detect_config_description(self, filename: str) -> str:
        """Detect configuration file description from filename."""
        filename_lower = filename.lower()
        if 'requirements' in filename_lower:
            return "Python package dependencies"
        elif 'package' in filename_lower:
            return "Node.js package dependencies"
        elif 'docker' in filename_lower:
            return "Docker container configuration"
        elif 'docker-compose' in filename_lower:
            return "Docker Compose service configuration"
        elif 'gitignore' in filename_lower:
            return "Git ignore patterns"
        elif 'env' in filename_lower:
            return "Environment variables"
        elif 'config' in filename_lower or 'settings' in filename_lower:
            return "Application configuration"
        else:
            return "Configuration file"
    
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
        # Re-raise the exception instead of using fallback
        raise OutputParserException(f"Enhanced parsing failed for {agent_type}: {e}")


def get_enhanced_format_instructions(agent_type: str) -> str:
    """Get enhanced format instructions for a specific agent type."""
    
    try:
        parser = EnhancedOutputParserFactory.get_parser(agent_type)
        return parser.get_format_instructions()
    except Exception as e:
        logger.error(f"Failed to get format instructions for {agent_type}: {e}")
        return "Please respond with valid JSON format."
