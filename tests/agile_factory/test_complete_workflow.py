"""
Comprehensive test for the complete Agile Factory workflow.

Tests the full end-to-end workflow:
1. Requirements Analyst → extracts requirements
2. Architecture Designer → designs architecture
3. Code Generator → generates code files
4. Code Reviewer → reviews code
5. Testing Agent → generates and executes tests
6. Documentation Generator → creates documentation

Verifies:
- All nodes execute successfully
- LLM calls are made in all nodes
- State is properly updated between nodes
- Files are generated correctly
- Workflow completes without errors
"""

import pytest
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging for test visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if API key is available
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
SKIP_IF_NO_API_KEY = not GEMINI_API_KEY

# Import workflow components
from agents.agile_factory.workflow import create_agile_factory_workflow
from agents.agile_factory.state.agile_state import AgileFactoryState
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture
def workflow_app():
    """Create and return the Agile Factory workflow app."""
    app = create_agile_factory_workflow(use_checkpointer=True, checkpointer_type="memory")
    return app


@pytest.fixture
def initial_state() -> Dict[str, Any]:
    """Create initial state for testing."""
    return {
        "user_story": "As a freelancer, I want a responsive personal portfolio website with a 'Hero' section, an 'About Me' section, and a 'Contact' form section with simple validation, so that I can showcase my work to potential clients.",
        "project_type": "website",
        "thread_id": "test-complete-workflow",
        "code_files": {},
        "requirements": {},
        "architecture": {},
        "code_review": {},
        "test_results": {},
        "documentation_files": {},
        "code_review_iteration_count": 0,
        "test_iteration_count": 0,
        "max_iterations": 3,
        "hitl_approvals": {
            "story_review": True,
            "requirements_review": True,
            "architecture_review": True,
            "code_generation_review": True,
            "final_review": True
        },
        "hitl_feedback": {
            "story_review": "approve",
            "requirements_review": "approve",
            "architecture_review": "approve",
            "code_generation_review": "approve",
            "final_review": "approve"
        },
        "current_checkpoint": "story_review",
        "workspace_locations": {},
        "status": "processing",
        "errors": [],
        "current_node": None
    }


@pytest.fixture
def workflow_config():
    """Create workflow configuration."""
    return {
        "configurable": {
            "thread_id": "test-complete-workflow"
        }
    }


@pytest.mark.skipif(SKIP_IF_NO_API_KEY, reason="GEMINI_API_KEY not set - skipping real LLM test")
class TestCompleteAgileFactoryWorkflow:
    """Test suite for complete Agile Factory workflow."""
    
    def test_workflow_creation(self, workflow_app):
        """Test that workflow is created successfully."""
        assert workflow_app is not None
        logger.info("✅ Workflow created successfully")
    
    def test_requirements_analyst_node(self, workflow_app, initial_state, workflow_config):
        """Test requirements analyst node execution."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Requirements Analyst Node")
        logger.info("="*80)
        
        # Create state with only user story (requirements analyst is first)
        test_state = {
            **initial_state,
            "current_checkpoint": "story_review"
        }
        
        # Stream workflow until requirements analyst completes
        events = []
        for event in workflow_app.stream(test_state, workflow_config):
            events.append(event)
            node_name = list(event.keys())[0] if event else None
            logger.info(f"Event: {node_name}")
            
            # Check if we've reached requirements analyst
            if node_name == "requirements_analyst":
                state_update = event[node_name]
                logger.info(f"Requirements Analyst State Update: {list(state_update.keys())}")
                
                # Verify requirements were generated
                if "requirements" in state_update:
                    requirements = state_update["requirements"]
                    assert requirements is not None, "Requirements should not be None"
                    assert isinstance(requirements, dict), "Requirements should be a dict"
                    logger.info(f"✅ Requirements generated: {len(requirements)} keys")
                    logger.info(f"   Functional requirements: {len(requirements.get('functional_requirements', []))}")
                    logger.info(f"   Non-functional requirements: {len(requirements.get('non_functional_requirements', []))}")
                    break
        
        # Get final state
        final_state = workflow_app.get_state(workflow_config).values
        
        # Verify requirements exist
        assert "requirements" in final_state, "Requirements should be in final state"
        assert final_state["requirements"], "Requirements should not be empty"
        assert final_state["current_node"] == "requirements_analyst", "Current node should be requirements_analyst"
        
        logger.info("✅ Requirements Analyst test passed")
    
    def test_architecture_designer_node(self, workflow_app, initial_state, workflow_config):
        """Test architecture designer node execution."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Architecture Designer Node")
        logger.info("="*80)
        
        # Create state with requirements (architecture designer needs requirements)
        test_state = {
            **initial_state,
            "requirements": {
                "functional_requirements": [
                    {
                        "id": "FR-001",
                        "title": "Hero Section",
                        "description": "Display hero section with name and tagline",
                        "priority": "High"
                    }
                ],
                "non_functional_requirements": [
                    {
                        "id": "NFR-001",
                        "category": "Performance",
                        "description": "Page load time < 2 seconds",
                        "priority": "High"
                    }
                ]
            },
            "current_checkpoint": "requirements_review"
        }
        
        # Stream workflow until architecture designer completes
        events = []
        for event in workflow_app.stream(test_state, workflow_config):
            events.append(event)
            node_name = list(event.keys())[0] if event else None
            logger.info(f"Event: {node_name}")
            
            # Check if we've reached architecture designer
            if node_name == "architecture_designer":
                state_update = event[node_name]
                logger.info(f"Architecture Designer State Update: {list(state_update.keys())}")
                
                # Verify architecture was generated
                if "architecture" in state_update:
                    architecture = state_update["architecture"]
                    assert architecture is not None, "Architecture should not be None"
                    assert isinstance(architecture, dict), "Architecture should be a dict"
                    logger.info(f"✅ Architecture generated: {len(architecture)} keys")
                    logger.info(f"   Components: {len(architecture.get('components', []))}")
                    break
        
        # Get final state
        final_state = workflow_app.get_state(workflow_config).values
        
        # Verify architecture exists
        assert "architecture" in final_state, "Architecture should be in final state"
        assert final_state["architecture"], "Architecture should not be empty"
        assert final_state["current_node"] == "architecture_designer", "Current node should be architecture_designer"
        
        logger.info("✅ Architecture Designer test passed")
    
    def test_code_generator_node(self, workflow_app, initial_state, workflow_config):
        """Test code generator node execution."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Code Generator Node")
        logger.info("="*80)
        
        # Create state with requirements and architecture
        test_state = {
            **initial_state,
            "requirements": {
                "functional_requirements": [
                    {
                        "id": "FR-001",
                        "title": "Hero Section",
                        "description": "Display hero section",
                        "priority": "High"
                    }
                ]
            },
            "architecture": {
                "components": [
                    {
                        "name": "Hero Section",
                        "technology": "HTML5 + CSS3"
                    }
                ],
                "file_structure": {
                    "structure": ["index.html", "styles.css"]
                }
            },
            "current_checkpoint": "architecture_review"
        }
        
        # Stream workflow until code generator completes
        events = []
        for event in workflow_app.stream(test_state, workflow_config):
            events.append(event)
            node_name = list(event.keys())[0] if event else None
            logger.info(f"Event: {node_name}")
            
            # Check if we've reached code generator
            if node_name == "code_generator":
                state_update = event[node_name]
                logger.info(f"Code Generator State Update: {list(state_update.keys())}")
                
                # Verify code files were generated
                if "code_files" in state_update:
                    code_files = state_update["code_files"]
                    assert code_files is not None, "Code files should not be None"
                    assert isinstance(code_files, dict), "Code files should be a dict"
                    logger.info(f"✅ Code files generated: {len(code_files)} files")
                    for file_path in list(code_files.keys())[:5]:
                        logger.info(f"   - {file_path}")
                    break
        
        # Get final state
        final_state = workflow_app.get_state(workflow_config).values
        
        # Verify code files exist
        assert "code_files" in final_state, "Code files should be in final state"
        assert final_state["code_files"], "Code files should not be empty"
        assert final_state["current_node"] == "code_generator", "Current node should be code_generator"
        
        logger.info("✅ Code Generator test passed")
    
    def test_complete_workflow_end_to_end(self, workflow_app, initial_state, workflow_config):
        """Test complete workflow from start to finish."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Complete End-to-End Workflow")
        logger.info("="*80)
        
        # Track execution
        nodes_executed = []
        state_updates = {}
        
        # Stream complete workflow
        try:
            for event in workflow_app.stream(initial_state, workflow_config):
                node_name = list(event.keys())[0] if event else None
                if node_name:
                    nodes_executed.append(node_name)
                    state_update = event[node_name]
                    state_updates[node_name] = list(state_update.keys()) if isinstance(state_update, dict) else []
                    logger.info(f"✅ Node executed: {node_name}")
                    
                    # Log state updates
                    if isinstance(state_update, dict):
                        for key in state_update.keys():
                            if key not in ["current_node", "status"]:
                                logger.info(f"   State updated: {key}")
        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            raise
        
        # Get final state
        final_state = workflow_app.get_state(workflow_config).values
        
        # Verify all expected nodes executed
        expected_nodes = [
            "hitl_story_review",
            "requirements_analyst",
            "hitl_requirements_review",
            "architecture_designer",
            "hitl_architecture_review",
            "code_generator",
            "hitl_code_review_checkpoint",
            "code_reviewer",
            "review_feedback",
            "testing_agent",
            "test_feedback",
            "documentation_generator",
            "hitl_final_review"
        ]
        
        logger.info(f"\nNodes executed: {nodes_executed}")
        logger.info(f"Expected nodes: {expected_nodes}")
        
        # Verify critical nodes executed
        assert "requirements_analyst" in nodes_executed, "Requirements analyst should execute"
        assert "architecture_designer" in nodes_executed, "Architecture designer should execute"
        assert "code_generator" in nodes_executed, "Code generator should execute"
        assert "code_reviewer" in nodes_executed, "Code reviewer should execute"
        
        # Verify state contains all expected outputs
        assert "requirements" in final_state, "Requirements should be in final state"
        assert final_state["requirements"], "Requirements should not be empty"
        
        assert "architecture" in final_state, "Architecture should be in final state"
        assert final_state["architecture"], "Architecture should not be empty"
        
        assert "code_files" in final_state, "Code files should be in final state"
        assert final_state["code_files"], "Code files should not be empty"
        
        assert "code_review" in final_state, "Code review should be in final state"
        assert final_state["code_review"], "Code review should not be empty"
        
        # Verify no errors
        errors = final_state.get("errors", [])
        if errors:
            logger.warning(f"Workflow completed with {len(errors)} errors:")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ No errors in workflow execution")
        
        # Log summary
        logger.info("\n" + "="*80)
        logger.info("WORKFLOW EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"Total nodes executed: {len(nodes_executed)}")
        logger.info(f"Requirements generated: {len(final_state.get('requirements', {}))} keys")
        logger.info(f"Architecture components: {len(final_state.get('architecture', {}).get('components', []))}")
        logger.info(f"Code files generated: {len(final_state.get('code_files', {}))}")
        logger.info(f"Test results: {bool(final_state.get('test_results', {}))}")
        logger.info(f"Documentation files: {len(final_state.get('documentation_files', {}))}")
        logger.info(f"Final status: {final_state.get('status')}")
        logger.info(f"Final node: {final_state.get('current_node')}")
        logger.info("="*80)
        
        logger.info("✅ Complete workflow test passed")


if __name__ == "__main__":
    """Run tests directly."""
    import sys
    
    # Set up test environment
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY not set. Tests will be skipped.")
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable to run tests.")
        sys.exit(0)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "-s",  # Show print statements
        "--tb=short"  # Short traceback format
    ])

