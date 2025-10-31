"""
Utility functions for extracting files from workflow state.

Handles parsing of nested JSON structures and extraction of actual code/test files
while skipping metadata fields that shouldn't be saved as files.
"""

import json
import re
from typing import Dict, Any


METADATA_KEYS = {
    "raw_output", "metadata", "plan", "assumptions", "file_tree",
    "tests", "runbook", "config_notes", "api_contracts", "output",
    "test_strategy", "coverage_analysis", "test_suites",
    "performance_tests", "quality_gate_passed", "summary"
}


def _extract_json_from_markdown(text: str) -> str:
    """Extract JSON string from markdown code blocks."""
    # Try markdown code block first
    json_match = re.search(r'```json\s*(\{.*\})\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try balanced brace extraction
    first_brace = text.find('{')
    if first_brace != -1:
        brace_count = 0
        json_start = first_brace
        for i, char in enumerate(text[first_brace:], start=first_brace):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[json_start:i+1]
        # If we get here, braces weren't balanced - return what we have
        return text[first_brace:]
    
    return text


def extract_code_files(code_files: Any) -> Dict[str, str]:
    """
    Extract code files from various possible structures.
    
    Handles:
    - Direct dict of {filepath: content} (most common case)
    - Skips metadata fields that shouldn't be files
    
    Args:
        code_files: Code files data from workflow state
        
    Returns:
        Dict mapping filepath to file content
    """
    extracted = {}
    
    if not code_files:
        return extracted
    
    # Direct dict mapping filepath to content (most common)
    if isinstance(code_files, dict):
        for key, value in code_files.items():
            # Skip metadata keys
            if key in METADATA_KEYS:
                continue
            
            # Skip if value looks like JSON in markdown (metadata field)
            if isinstance(value, str):
                # Check if it's a JSON string wrapped in markdown code blocks
                if re.match(r'^\s*```json\s*\{', value, re.DOTALL):
                    # This is metadata, not a file - skip it
                    continue
                
                # This looks like actual file content
                extracted[key] = value
    
    return extracted


def extract_test_files(test_files: Any) -> Dict[str, str]:
    """
    Extract test files from various possible structures.
    
    Handles:
    - Nested raw_output with JSON string containing test_files array
    - Direct files dict
    - Skips metadata fields that shouldn't be files
    
    Args:
        test_files: Test files data from workflow state
        
    Returns:
        Dict mapping filepath to file content
    """
    extracted = {}
    
    if not test_files:
        return extracted
    
    # Case 1: raw_output contains JSON string with test_files array
    if isinstance(test_files, dict) and "raw_output" in test_files:
        raw_output = test_files["raw_output"]
        
        # Try to parse as JSON
        try:
            json_str = _extract_json_from_markdown(raw_output)
            parsed = json.loads(json_str)
            
            # Extract files from parsed structure - handle both list and dict formats
            if "test_files" in parsed:
                test_files_data = parsed["test_files"]
                
                # Format 1: List of file objects with path/content
                if isinstance(test_files_data, list):
                    for file_obj in test_files_data:
                        if isinstance(file_obj, dict):
                            # Try path/content format
                            if "path" in file_obj and "content" in file_obj:
                                extracted[file_obj["path"]] = file_obj["content"]
                            # Try filename/content format
                            elif "filename" in file_obj and "content" in file_obj:
                                extracted[file_obj["filename"]] = file_obj["content"]
                
                # Format 2: Dict mapping filename to content (direct)
                elif isinstance(test_files_data, dict):
                    for filename, content in test_files_data.items():
                        # Handle nested structure (filename -> {content: "...", ...})
                        if isinstance(content, dict) and "content" in content:
                            extracted[filename] = content["content"]
                        # Handle direct string content
                        elif isinstance(content, str):
                            extracted[filename] = content
        
        except (json.JSONDecodeError, AttributeError, KeyError):
            # If parsing fails, continue - we'll fall back to other methods
            pass
    
    # Case 2: files key contains actual test files (direct dict)
    if isinstance(test_files, dict) and "files" in test_files:
        files_content = test_files["files"]
        
        if isinstance(files_content, dict):
            # Direct mapping
            for filepath, content in files_content.items():
                if isinstance(content, str):
                    extracted[filepath] = content
    
    # Case 3: Direct dict (but skip metadata keys)
    if isinstance(test_files, dict):
        for key, value in test_files.items():
            # Skip metadata keys
            if key in METADATA_KEYS or key == "files":
                continue
            
            # Skip if value looks like JSON in markdown (metadata field)
            if isinstance(value, str):
                if re.match(r'^\s*```json\s*\{', value, re.DOTALL):
                    continue
                
                # This might be a file (but unlikely for test_files)
                if not any(meta in key.lower() for meta in ["strategy", "analysis", "suite", "test", "quality"]):
                    extracted[key] = value
    
    return extracted


def extract_documentation_files(doc_data: Any) -> Dict[str, str]:
    """
    Extract documentation files from documentation data.
    
    Args:
        doc_data: Documentation data from workflow state
        
    Returns:
        Dict mapping filepath to file content
    """
    extracted = {}
    
    if not doc_data:
        return extracted
    
    # Documentation usually has nested structure
    # Skip output/metadata fields
    if isinstance(doc_data, dict):
        for key, value in doc_data.items():
            if key in METADATA_KEYS:
                continue
            
            if isinstance(value, str):
                if re.match(r'^\s*```json\s*\{', value, re.DOTALL):
                    continue
                
                # If it looks like a file path and content, extract it
                extracted[key] = value
    
    return extracted

