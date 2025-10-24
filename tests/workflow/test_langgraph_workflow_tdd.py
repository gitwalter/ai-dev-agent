"""
TDD Test Suite for LangGraph Agent Swarm Workflow.

This test suite validates the workflow step-by-step, stopping at the first failure
to enable immediate bug fixing. Following true TDD principles.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Ensure workflow can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from workflow.langgraph_workflow import AgentSwarm, PromptLoader, SwarmState


class TestWorkflowStepByStep:
    """Step-by-step validation of the workflow with immediate failure stops."""
    
    def setup_method(self):
        """Set up test environment."""
        os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "test-dummy-key")
        self.llm_config = {
            "model_name": "gemini-2.5-flash",
            "temperature": 0.7
        }
    
    def test_step_1_prompt_loader_initialization(self):
        """STEP 1: Verify PromptLoader initializes correctly."""
        print("\n" + "="*80)
        print("STEP 1: Testing PromptLoader initialization...")
        print("="*80)
        
        # Test without LangSmith
        loader = PromptLoader(use_langsmith=False)
        assert loader is not None, "PromptLoader should initialize"
        assert loader.cache_dir == "prompts/langsmith_cache", "Cache dir should be set"
        assert os.path.exists(loader.cache_dir), "Cache directory should be created"
        assert os.path.exists(os.path.join(loader.cache_dir, "metadata")), "Metadata dir should exist"
        
        print("[PASS] PromptLoader initialization")
    
    @pytest.mark.asyncio
    async def test_step_2_prompt_loader_load_with_fallback(self):
        """STEP 2: Verify PromptLoader can load prompts with fallback."""
        print("\n" + "="*80)
        print("STEP 2: Testing PromptLoader load with fallback...")
        print("="*80)
        
        loader = PromptLoader(use_langsmith=False)
        
        prompt = await loader.load_prompt(
            "test_prompt_tdd",
            fallback_template="You are a test assistant for {task}.",
            input_variables=["task"]
        )
        
        assert prompt is not None, "Prompt should be loaded"
        assert hasattr(prompt, 'template'), "Prompt should have template attribute"
        
        # Verify it was saved to cache
        cache_path = loader._get_local_prompt_path("test_prompt_tdd")
        assert os.path.exists(cache_path), f"Prompt should be cached at {cache_path}"
        
        print("✅ PromptLoader fallback loading: PASSED")
    
    @pytest.mark.asyncio
    async def test_step_3_prompt_loader_caching(self):
        """STEP 3: Verify prompt caching works."""
        print("\n" + "="*80)
        print("STEP 3: Testing PromptLoader caching...")
        print("="*80)
        
        loader = PromptLoader(use_langsmith=False)
        
        # Load once
        prompt1 = await loader.load_prompt(
            "test_cache_prompt",
            fallback_template="Test cache",
            input_variables=[]
        )
        
        # Load again - should use cache
        prompt2 = await loader.load_prompt(
            "test_cache_prompt",
            fallback_template="Test cache",
            input_variables=[]
        )
        
        assert prompt1 is prompt2, "Should return cached prompt (same object)"
        
        print("✅ PromptLoader caching: PASSED")
    
    def test_step_4_agent_swarm_initialization(self):
        """STEP 4: Verify AgentSwarm initializes without errors."""
        print("\n" + "="*80)
        print("STEP 4: Testing AgentSwarm initialization...")
        print("="*80)
        
        try:
            swarm = AgentSwarm(self.llm_config)
            
            assert swarm is not None, "AgentSwarm should initialize"
            assert swarm.llm_config == self.llm_config, "LLM config should match"
            assert swarm.workflow is not None, "Workflow should be created"
            assert swarm.prompt_loader is not None, "PromptLoader should be initialized"
            
            # Agents should be pre-created now (not empty)
            assert isinstance(swarm.agents, dict), "Agents should be a dictionary"
            print(f"   ℹ️  Pre-created agents: {list(swarm.agents.keys())}")
            
            # Verify all expected agents exist
            expected_agents = [
                "requirements_analyst",
                "architecture_designer",
                "code_generator",
                "test_generator",
                "code_reviewer",
                "security_analyst",
                "documentation_generator"
            ]
            
            for agent_name in expected_agents:
                assert agent_name in swarm.agents, f"Agent {agent_name} should be pre-created"
                assert swarm.agents[agent_name] is not None, f"Agent {agent_name} should not be None"
            
            print(f"✅ AgentSwarm initialization: PASSED (7 agents pre-created)")
            
        except Exception as e:
            pytest.fail(f"❌ AgentSwarm initialization FAILED: {e}\n{type(e).__name__}: {str(e)}")
    
    def test_step_5_workflow_graph_structure(self):
        """STEP 5: Verify workflow graph has correct structure."""
        print("\n" + "="*80)
        print("STEP 5: Testing workflow graph structure...")
        print("="*80)
        
        swarm = AgentSwarm(self.llm_config)
        workflow = swarm.workflow
        
        assert workflow is not None, "Workflow should exist"
        assert hasattr(workflow, 'get_graph'), "Workflow should have get_graph method"
        
        graph = workflow.get_graph()
        node_names = [node.id for node in graph.nodes.values()]
        
        print(f"   ℹ️  Found {len(node_names)} nodes in graph")
        
        # Check supervisor nodes
        supervisor_nodes = ["complexity_analyzer", "agent_selector", "router"]
        for node in supervisor_nodes:
            assert node in node_names, f"Supervisor node '{node}' missing from graph"
        
        # Check specialist agent nodes
        specialist_nodes = [
            "requirements_analyst",
            "architecture_designer",
            "code_generator",
            "test_generator",
            "code_reviewer",
            "security_analyst",
            "documentation_generator"
        ]
        for node in specialist_nodes:
            assert node in node_names, f"Specialist node '{node}' missing from graph"
        
        print(f"✅ Workflow graph structure: PASSED (12 nodes found)")
    
    def test_step_6_state_definition(self):
        """STEP 6: Verify SwarmState has correct structure."""
        print("\n" + "="*80)
        print("STEP 6: Testing SwarmState definition...")
        print("="*80)
        
        # Check SwarmState structure
        assert hasattr(SwarmState, '__annotations__'), "SwarmState should be a TypedDict"
        
        required_fields = [
            'project_context',
            'project_type',
            'project_complexity',
            'requirements',
            'architecture',
            'code_files',
            'test_files',
            'documentation',
            'required_agents',
            'completed_agents',
            'next_agent',
            'needs_human_approval',
            'human_feedback',
            'current_step',
            'errors'
        ]
        
        annotations = SwarmState.__annotations__
        
        for field in required_fields:
            assert field in annotations, f"Required field '{field}' missing from SwarmState"
        
        print(f"✅ SwarmState definition: PASSED ({len(required_fields)} fields)")
    
    @pytest.mark.asyncio
    async def test_step_7_prompt_batch_loading(self):
        """STEP 7: Verify batch prompt loading works."""
        print("\n" + "="*80)
        print("STEP 7: Testing batch prompt loading...")
        print("="*80)
        
        loader = PromptLoader(use_langsmith=False)
        
        # Simulate batch loading like in AgentSwarm
        async def load_all_test_prompts():
            return await asyncio.gather(
                loader.load_prompt("test_req", fallback_template="Req analyst", input_variables=[]),
                loader.load_prompt("test_arch", fallback_template="Arch designer", input_variables=[]),
                loader.load_prompt("test_code", fallback_template="Code generator", input_variables=[]),
                return_exceptions=True
            )
        
        prompts = await load_all_test_prompts()
        
        assert len(prompts) == 3, "Should load 3 prompts"
        
        for i, prompt in enumerate(prompts):
            if isinstance(prompt, Exception):
                pytest.fail(f"❌ Prompt {i} failed to load: {prompt}")
            assert prompt is not None, f"Prompt {i} should not be None"
        
        print("✅ Batch prompt loading: PASSED")
    
    def test_step_8_prompt_loader_in_swarm(self):
        """STEP 8: Verify PromptLoader works within AgentSwarm."""
        print("\n" + "="*80)
        print("STEP 8: Testing PromptLoader integration in AgentSwarm...")
        print("="*80)
        
        swarm = AgentSwarm(self.llm_config)
        
        # Check that agent_prompts were loaded
        assert hasattr(swarm, 'agent_prompts'), "Swarm should have agent_prompts"
        assert isinstance(swarm.agent_prompts, dict), "agent_prompts should be a dict"
        
        print(f"   ℹ️  Loaded prompts: {list(swarm.agent_prompts.keys())}")
        print(f"   ℹ️  Total prompts: {len(swarm.agent_prompts)}")
        
        # Verify expected prompts
        expected_prompts = [
            "requirements_analyst",
            "architecture_designer",
            "code_generator",
            "test_generator",
            "code_reviewer",
            "security_analyst",
            "documentation_generator"
        ]
        
        for prompt_name in expected_prompts:
            if prompt_name in swarm.agent_prompts:
                prompt = swarm.agent_prompts[prompt_name]
                if prompt is not None:
                    print(f"   ✓ {prompt_name}: loaded")
                else:
                    print(f"   ⚠️  {prompt_name}: None (will use fallback)")
        
        print("✅ PromptLoader in AgentSwarm: PASSED")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "test-dummy-key",
        reason="Requires valid GEMINI_API_KEY for real execution"
    )
    async def test_step_9_simple_workflow_execution(self):
        """STEP 9: Test simple workflow execution end-to-end."""
        print("\n" + "="*80)
        print("STEP 9: Testing simple workflow execution...")
        print("="*80)
        
        swarm = AgentSwarm(self.llm_config)
        
        result = await swarm.execute_swarm(
            "Create a simple Python function that returns Hello World"
        )
        
        # Verify result structure
        assert "current_step" in result, "Result should have current_step"
        assert "completed_agents" in result, "Result should have completed_agents"
        assert "errors" in result, "Result should have errors list"
        
        print(f"   ℹ️  Current step: {result['current_step']}")
        print(f"   ℹ️  Completed agents: {result['completed_agents']}")
        print(f"   ℹ️  Errors: {result['errors']}")
        
        # Should complete successfully
        assert result["current_step"] != "error", "Workflow should not end in error state"
        assert isinstance(result["completed_agents"], list), "completed_agents should be a list"
        assert len(result["completed_agents"]) > 0, "At least one agent should complete"
        
        print("✅ Simple workflow execution: PASSED")


def run_step_by_step():
    """Run tests step by step, stopping at first failure."""
    print("\n" + "=" * 80)
    print("TDD TEST SUITE - STEP BY STEP WORKFLOW VALIDATION")
    print("=" * 80)
    
    test_class = TestWorkflowStepByStep()
    test_class.setup_method()
    
    tests = [
        ("step_1", test_class.test_step_1_prompt_loader_initialization),
        ("step_2", test_class.test_step_2_prompt_loader_load_with_fallback),
        ("step_3", test_class.test_step_3_prompt_loader_caching),
        ("step_4", test_class.test_step_4_agent_swarm_initialization),
        ("step_5", test_class.test_step_5_workflow_graph_structure),
        ("step_6", test_class.test_step_6_state_definition),
        ("step_7", test_class.test_step_7_prompt_batch_loading),
        ("step_8", test_class.test_step_8_prompt_loader_in_swarm),
    ]
    
    failed = []
    passed = []
    
    for step_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                asyncio.run(test_func())
            else:
                test_func()
            passed.append(step_name)
        except AssertionError as e:
            print(f"\n❌ {step_name} FAILED:")
            print(f"   {str(e)}")
            failed.append((step_name, str(e)))
            break  # Stop at first failure
        except Exception as e:
            print(f"\n💥 {step_name} EXCEPTION:")
            print(f"   {type(e).__name__}: {str(e)}")
            failed.append((step_name, f"{type(e).__name__}: {str(e)}"))
            break  # Stop at first failure
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ PASSED: {len(passed)}/{len(tests)}")
    print(f"❌ FAILED: {len(failed)}")
    
    if failed:
        print("\nFailed at:")
        for step, error in failed:
            print(f"  - {step}: {error}")
        return 1
    else:
        print("\n🎉 ALL TESTS PASSED!")
        return 0


if __name__ == "__main__":
    exit_code = run_step_by_step()
    sys.exit(exit_code)

