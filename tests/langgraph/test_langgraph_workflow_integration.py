#!/usr/bin/env python3
"""
Integration test for LangGraph workflow implementation.
Tests the complete LangGraph workflow with real LLM usage.
"""

import asyncio
import sys
import os
from pathlib import Path
try:
    import tomllib
except ImportError:
    import tomli as tomllib
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from langgraph_workflow import LangGraphWorkflowManager


class TestLangGraphWorkflowIntegration:
    """Integration tests for LangGraph workflow implementation."""
    
    @pytest.fixture
    def api_key(self):
        """Load API key from secrets."""
        try:
            secrets_path = Path(".streamlit/secrets.toml")
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
                api_key = secrets.get("GEMINI_API_KEY")
                if not api_key or api_key == "your-gemini-api-key-here":
                    pytest.skip("Invalid Gemini API key")
                return api_key
        except Exception as e:
            pytest.skip(f"Failed to load API key: {e}")
    
    @pytest.fixture
    def llm_config(self, api_key):
        """Setup LLM configuration."""
        return {
            "api_key": api_key,
            "model_name": "gemini-2.5-flash-lite",
            "temperature": 0.1,
            "max_tokens": 8192
        }
    
    @pytest.fixture
    def workflow_manager(self, llm_config):
        """Create workflow manager."""
        return LangGraphWorkflowManager(llm_config)
    
    @pytest.fixture
    def test_state(self):
        """Create test state."""
        return {
            "project_context": "Create a simple task management system with user authentication, task creation, and status tracking",
            "project_name": "test-task-management",
            "session_id": "test-langgraph-session-123"
        }
    
    @pytest.mark.asyncio
    async def test_langgraph_workflow_execution(self, workflow_manager, test_state):
        """Test the complete LangGraph workflow execution."""
        print("🧪 Testing LangGraph Workflow Implementation...")
        
        try:
            print("✅ LangGraph workflow manager created")
            print("✅ Test state created")
            print("📋 Project context: Task management system with authentication and task tracking")
            
            print("\n🔄 Executing LangGraph Workflow...")
            result = await workflow_manager.execute_workflow(test_state)
            print("✅ LangGraph workflow completed")
            
            # Check results
            print(f"\n📊 Results:")
            print(f"  Current Step: {result.get('current_step', 'unknown')}")
            print(f"  Requirements: {len(result.get('requirements', []))}")
            print(f"  Architecture: {bool(result.get('architecture', {}))}")
            print(f"  Code Files: {len(result.get('code_files', {}))}")
            print(f"  Tests: {len(result.get('tests', {}))}")
            print(f"  Documentation: {len(result.get('documentation', {}))}")
            print(f"  Agent Outputs: {len(result.get('agent_outputs', {}))}")
            print(f"  Errors: {len(result.get('errors', []))}")
            print(f"  Execution History: {len(result.get('execution_history', []))}")
            
            # Check for errors
            errors = result.get('errors', [])
            if errors:
                print(f"\n❌ Errors encountered:")
                for error in errors:
                    print(f"  - {error}")
                pytest.fail(f"Workflow encountered errors: {errors}")
            
            # Check for successful completion
            if result.get('current_step') == 'completed':
                print(f"\n✅ Workflow completed successfully!")
                
                # Show execution history
                history = result.get('execution_history', [])
                print(f"\n📋 Execution History:")
                for step in history:
                    status = "✅" if step.get('status') == 'completed' else "❌"
                    print(f"  {status} {step.get('step', 'unknown')} - {step.get('status', 'unknown')}")
                
                # Assert minimum requirements
                assert len(result.get('requirements', [])) > 0, "No requirements generated"
                assert result.get('architecture', {}), "No architecture generated"
                assert len(result.get('code_files', {})) > 0, "No code files generated"
                assert len(result.get('tests', {})) > 0, "No test files generated"
                assert len(result.get('agent_outputs', {})) > 0, "No agent outputs recorded"
                
            else:
                print(f"\n⚠️ Workflow did not complete successfully. Current step: {result.get('current_step')}")
                pytest.fail(f"Workflow did not complete. Current step: {result.get('current_step')}")
            
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"Workflow execution failed: {e}")
    
    @pytest.mark.asyncio
    async def test_workflow_state_management(self, workflow_manager, test_state):
        """Test workflow state management and persistence."""
        print("🧪 Testing Workflow State Management...")
        
        try:
            result = await workflow_manager.execute_workflow(test_state)
            
            # Verify state structure
            required_keys = [
                'project_context', 'project_name', 'session_id',
                'requirements', 'architecture', 'code_files', 'tests',
                'documentation', 'agent_outputs', 'errors', 'current_step',
                'execution_history'
            ]
            
            for key in required_keys:
                assert key in result, f"Missing required state key: {key}"
            
            # Verify state types
            assert isinstance(result['requirements'], list), "Requirements should be a list"
            assert isinstance(result['architecture'], dict), "Architecture should be a dict"
            assert isinstance(result['code_files'], dict), "Code files should be a dict"
            assert isinstance(result['tests'], dict), "Tests should be a dict"
            assert isinstance(result['agent_outputs'], dict), "Agent outputs should be a dict"
            assert isinstance(result['errors'], list), "Errors should be a list"
            assert isinstance(result['execution_history'], list), "Execution history should be a list"
            
            print("✅ State management test passed")
            
        except Exception as e:
            print(f"❌ State management test failed: {e}")
            pytest.fail(f"State management test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, workflow_manager):
        """Test workflow error handling with invalid state."""
        print("🧪 Testing Workflow Error Handling...")
        
        # Test with invalid state
        invalid_state = {
            "project_context": "",  # Empty context should trigger error handling
            "project_name": "test-error-handling",
            "session_id": "test-error-session-123"
        }
        
        try:
            result = await workflow_manager.execute_workflow(invalid_state)
            
            # Should handle errors gracefully
            assert 'errors' in result, "Result should contain errors field"
            assert 'current_step' in result, "Result should contain current_step field"
            
            print("✅ Error handling test passed")
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            pytest.fail(f"Error handling test failed: {e}")


if __name__ == "__main__":
    # Run the integration test
    async def main():
        test_instance = TestLangGraphWorkflowIntegration()
        
        # Create fixtures
        api_key = test_instance.api_key()
        llm_config = test_instance.llm_config(api_key)
        workflow_manager = test_instance.workflow_manager(llm_config)
        test_state = test_instance.test_state()
        
        # Run the main test
        await test_instance.test_langgraph_workflow_execution(workflow_manager, test_state)
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
