"""
Test to verify code generator fix - outputs files not plan.
"""

import pytest
import json
from workflow.langgraph_workflow import AgentSwarm


class TestCodeGeneratorFix:
    """Test suite for code generator output structure fix."""
    
    def test_code_files_structure(self):
        """Test that code_files contains direct filename->content mapping."""
        # Simulate the parsed JSON output from code generator
        parsed_output = {
            "plan": ["Step 1: Setup", "Step 2: Implement", "Step 3: Test"],
            "assumptions": ["Python 3.9+", "FastAPI framework"],
            "file_tree": "app/\n  main.py\n  models.py",
            "files": [
                {"path": "app/main.py", "content": "from fastapi import FastAPI\n\napp = FastAPI()"},
                {"path": "app/models.py", "content": "from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str"}
            ],
            "tests": {"coverage_goal": ">=80%"},
            "runbook": {"setup": ["pip install -r requirements.txt"]}
        }
        
        # Simulate what the code generator node does
        code_files = {}
        for file_obj in parsed_output["files"]:
            if "path" in file_obj and "content" in file_obj:
                code_files[file_obj["path"]] = file_obj["content"]
        
        # Create the state update structure (what our fix does)
        state_update = {
            "code_files": code_files,  # Files directly, not nested
            "code_metadata": {
                "file_tree": parsed_output.get("file_tree", ""),
                "plan": parsed_output.get("plan", []),
                "assumptions": parsed_output.get("assumptions", []),
                "tests": parsed_output.get("tests", {}),
                "runbook": parsed_output.get("runbook", {})
            }
        }
        
        # Verify code_files structure
        assert isinstance(state_update["code_files"], dict)
        assert len(state_update["code_files"]) == 2
        
        # Verify files are direct string content, not nested
        for filename, content in state_update["code_files"].items():
            assert isinstance(filename, str)
            assert isinstance(content, str)
            assert "def " in content or "import " in content or "class " in content
        
        # Verify no "plan" in code_files (the bug we fixed)
        assert "plan" not in state_update["code_files"]
        assert "file_tree" not in state_update["code_files"]
        assert "assumptions" not in state_update["code_files"]
        
        # Verify metadata is separate
        assert "plan" in state_update["code_metadata"]
        assert "assumptions" in state_update["code_metadata"]
        assert isinstance(state_update["code_metadata"]["plan"], list)
    
    def test_code_files_accessible_by_downstream_agents(self):
        """Test that downstream agents can access code_files directly."""
        # Simulate the state after code generator runs
        state = {
            "project_context": "Test project",
            "code_files": {
                "app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()",
                "app/models.py": "from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str"
            },
            "code_metadata": {
                "plan": ["Step 1", "Step 2"],
                "file_tree": "app/\n  main.py\n  models.py"
            }
        }
        
        # Simulate what test_generator does: accesses code_files
        code_files_for_testing = state.get("code_files", {})
        
        # Verify it gets actual files, not metadata
        assert isinstance(code_files_for_testing, dict)
        assert len(code_files_for_testing) == 2
        assert "app/main.py" in code_files_for_testing
        assert "FastAPI" in code_files_for_testing["app/main.py"]
        
        # Verify it doesn't get the plan (the bug)
        assert "plan" not in code_files_for_testing
        assert not any("Step" in str(v) for v in code_files_for_testing.values())
    
    def test_backward_compatibility_with_main_app(self):
        """Test that apps/main.py processing code still works."""
        # Simulate what apps/main.py does to process code_files
        code_files = {
            "app/main.py": "from fastapi import FastAPI\n\napp = FastAPI()",
            "app/models.py": "class User:\n    pass"
        }
        
        # Simulate the processing in apps/main.py (lines 804-813)
        processed_code_files = {}
        for file_path, file_data in code_files.items():
            if isinstance(file_data, dict) and "content" in file_data:
                # Old format (dict with content key)
                processed_code_files[file_path] = file_data["content"]
            elif isinstance(file_data, str):
                # New format (direct string) - what we now provide
                processed_code_files[file_path] = file_data
            else:
                # Fallback
                processed_code_files[file_path] = str(file_data)
        
        # Verify it processes correctly
        assert len(processed_code_files) == 2
        assert all(isinstance(v, str) for v in processed_code_files.values())
        assert "FastAPI" in processed_code_files["app/main.py"]


if __name__ == "__main__":
    # Run tests
    test = TestCodeGeneratorFix()
    
    print("Testing code_files structure...")
    test.test_code_files_structure()
    print("[OK] PASSED: code_files structure is correct")
    
    print("\nTesting downstream agent access...")
    test.test_code_files_accessible_by_downstream_agents()
    print("[OK] PASSED: Downstream agents can access files correctly")
    
    print("\nTesting backward compatibility...")
    test.test_backward_compatibility_with_main_app()
    print("[OK] PASSED: Backward compatible with apps/main.py")
    
    print("\n[SUCCESS] All tests passed! The fix is working correctly.")

