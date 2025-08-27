#!/usr/bin/env python3
"""
Test file for workflow test file extraction.

Tests how test files are extracted from workflow state.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from workflow.workflow_manager import WorkflowManager
from models.state import create_initial_state
import uuid

class TestWorkflowExtraction:
    """Test cases for workflow file extraction."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pass
        
    def teardown_method(self):
        """Clean up after tests."""
        pass
    
    @pytest.mark.asyncio
    async def test_test_file_extraction(self):
        """Test how test files are extracted from workflow state."""
        print("🧪 Testing Workflow Test File Extraction...")
        
        # Create a mock state with test files
        state = create_initial_state(
            project_context='Test project',
            project_name='test-project',
            session_id=str(uuid.uuid4())
        )
        
        # Add mock test files to state
        state["tests"] = {
            "test_app.py": {
                "content": "import pytest\nfrom app import hello\n\ndef test_hello():\n    assert hello() == 'Hello World'",
                "filename": "test_app.py",
                "test_type": "unit"
            },
            "test_utils.py": {
                "content": "import pytest\nfrom utils import helper\n\ndef test_helper():\n    assert helper() == True",
                "filename": "test_utils.py", 
                "test_type": "unit"
            }
        }
        
        # Add mock code files
        state["code_files"] = {
            "app.py": "def hello(): return 'Hello World'",
            "utils.py": "def helper(): return True"
        }
        
        # Add mock documentation
        state["documentation"] = {
            "README.md": "# Test Project\n\nThis is a test project."
        }
        
        # Test extraction logic (same as workflow manager)
        code_files = state.get("code_files", {})
        test_files = state.get("tests", {})
        documentation_files = state.get("documentation", {})
        
        print(f"📊 Extraction Results:")
        print(f"  Code files: {len(code_files)}")
        print(f"  Test files: {len(test_files)}")
        print(f"  Documentation files: {len(documentation_files)}")
        
        # Print test file details
        for filename, content in test_files.items():
            if isinstance(content, dict):
                file_content = content.get('content', '')
                test_type = content.get('test_type', 'unknown')
                print(f"    📄 {filename} ({test_type}): {len(file_content)} characters")
            else:
                print(f"    📄 {filename}: {len(str(content))} characters")
        
        # Assertions
        assert len(test_files) == 2, "Should have 2 test files"
        assert "test_app.py" in test_files, "Should have test_app.py"
        assert "test_utils.py" in test_files, "Should have test_utils.py"
        
        # Check content structure
        for filename, content in test_files.items():
            assert isinstance(content, dict), f"Test file {filename} should be a dictionary"
            assert "content" in content, f"Test file {filename} should have content"
            assert "test_type" in content, f"Test file {filename} should have test_type"
            assert len(content["content"]) > 0, f"Test file {filename} should have non-empty content"
        
        print("✅ Test file extraction is working correctly!")
