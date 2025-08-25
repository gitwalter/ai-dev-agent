#!/usr/bin/env python3
"""
Test script to verify the complete workflow with real LLM usage.
Tests all agents in sequence and verifies that artifacts are produced correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.config import AgentConfig, GeminiConfig
from models.state import create_initial_state
from agents.requirements_analyst import RequirementsAnalyst
from agents.architecture_designer import ArchitectureDesigner
from agents.code_generator import CodeGenerator
from agents.code_reviewer import CodeReviewer
from agents.test_generator import TestGenerator
from agents.documentation_generator import DocumentationGenerator
from agents.security_analyst import SecurityAnalyst
import google.generativeai as genai


async def test_complete_workflow():
    """Test the complete workflow with real LLM usage."""
    print("🧪 Testing Complete Workflow with Real LLM...")
    
    # Load API key from Streamlit secrets
    try:
        import streamlit as st
        api_key = st.secrets.GEMINI_API_KEY
        if not api_key or api_key == "your-gemini-api-key-here":
            print("❌ Invalid Gemini API key in secrets.toml")
            print("Please set a valid API key in .streamlit/secrets.toml")
            return False
        print("✅ API key loaded from Streamlit secrets")
    except Exception as e:
        print(f"❌ Failed to load API key from Streamlit secrets: {e}")
        print("Please ensure .streamlit/secrets.toml exists with GEMINI_API_KEY")
        return False
    
    # Setup Gemini configuration
    gemini_config = GeminiConfig(
        api_key=api_key,
        model_name="gemini-2.5-flash-lite",
        max_tokens=8192,
        temperature=0.1,
        top_p=0.8,
        top_k=40
    )
    
    # Setup Gemini client
    try:
        genai.configure(api_key=gemini_config.api_key)
        gemini_client = genai.GenerativeModel(
            model_name=gemini_config.model_name,
            generation_config={
                "temperature": gemini_config.temperature,
                "top_p": gemini_config.top_p,
                "top_k": gemini_config.top_k,
                "max_output_tokens": gemini_config.max_tokens,
            }
        )
        print("✅ Gemini client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        return False
    
    # Create agent configurations
    agent_configs = {
        "requirements_analyst": AgentConfig(
            name="requirements_analyst",
            description="Analyzes project requirements and creates detailed specifications",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Analyze requirements for: {project_context}",
            system_prompt="You are an expert Requirements Analyst",
            parameters={"temperature": 0.1}
        ),
        "architecture_designer": AgentConfig(
            name="architecture_designer",
            description="Designs system architecture and technology stack",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Design architecture for: {project_context}",
            system_prompt="You are an expert Software Architect",
            parameters={"temperature": 0.1}
        ),
        "code_generator": AgentConfig(
            name="code_generator",
            description="Generates production-ready source code",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Generate code for: {project_context}",
            system_prompt="You are an expert Software Developer",
            parameters={"temperature": 0.1}
        ),
        "code_reviewer": AgentConfig(
            name="code_reviewer",
            description="Reviews generated code for quality and best practices",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Review code for: {project_context}",
            system_prompt="You are an expert Code Reviewer",
            parameters={"temperature": 0.1}
        ),
        "test_generator": AgentConfig(
            name="test_generator",
            description="Generates comprehensive test suites",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Generate tests for: {project_context}",
            system_prompt="You are an expert Test Engineer",
            parameters={"temperature": 0.1}
        ),
        "documentation_generator": AgentConfig(
            name="documentation_generator",
            description="Generates comprehensive documentation and diagrams",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Generate documentation for: {project_context}",
            system_prompt="You are an expert Technical Writer",
            parameters={"temperature": 0.1}
        ),
        "security_analyst": AgentConfig(
            name="security_analyst",
            description="Analyzes code and architecture for security vulnerabilities",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Analyze security for: {project_context}",
            system_prompt="You are an expert Security Analyst",
            parameters={"temperature": 0.1}
        )
    }
    
    # Create agents
    agents = {}
    try:
        agents["requirements_analyst"] = RequirementsAnalyst(agent_configs["requirements_analyst"], gemini_client)
        agents["architecture_designer"] = ArchitectureDesigner(agent_configs["architecture_designer"], gemini_client)
        agents["code_generator"] = CodeGenerator(agent_configs["code_generator"], gemini_client)
        agents["code_reviewer"] = CodeReviewer(agent_configs["code_reviewer"], gemini_client)
        agents["test_generator"] = TestGenerator(agent_configs["test_generator"], gemini_client)
        agents["documentation_generator"] = DocumentationGenerator(agent_configs["documentation_generator"], gemini_client)
        agents["security_analyst"] = SecurityAnalyst(agent_configs["security_analyst"], gemini_client)
        print("✅ All agents created successfully")
    except Exception as e:
        print(f"❌ Failed to create agents: {e}")
        return False
    
    # Create initial state
    test_state = create_initial_state(
        project_context="Create a simple task management system with user authentication, task creation, and status tracking",
        project_name="test-task-management",
        session_id="test-workflow-session-123"
    )
    
    print("✅ Test state created successfully")
    print("📋 Project context: Task management system with authentication and task tracking")
    
    # Execute workflow steps
    workflow_steps = [
        ("requirements_analyst", "Requirements Analysis"),
        ("architecture_designer", "Architecture Design"),
        ("code_generator", "Code Generation"),
        ("code_reviewer", "Code Review"),
        ("test_generator", "Test Generation"),
        ("documentation_generator", "Documentation Generation"),
        ("security_analyst", "Security Analysis")
    ]
    
    try:
        for agent_name, step_name in workflow_steps:
            print(f"\n🔄 Executing {step_name}...")
            agent = agents[agent_name]
            test_state = await agent.execute(test_state)
            print(f"✅ {step_name} completed successfully")
            
            # Check for artifacts
            if agent_name == "requirements_analyst":
                requirements = test_state.get("requirements", [])
                if requirements:
                    print(f"  📋 Generated {len(requirements)} requirements")
                else:
                    print("  ⚠️ No requirements generated")
            
            elif agent_name == "architecture_designer":
                architecture = test_state.get("architecture", {})
                if architecture:
                    print(f"  🏗️ Architecture designed: {list(architecture.keys())}")
                else:
                    print("  ⚠️ No architecture generated")
            
            elif agent_name == "code_generator":
                code_files = test_state.get("code_files", {})
                if code_files:
                    print(f"  💻 Generated {len(code_files)} code files: {list(code_files.keys())}")
                else:
                    print("  ⚠️ No code files generated")
            
            elif agent_name == "code_reviewer":
                # Check for code review results in agent outputs
                review_results = test_state.get("agent_outputs", {}).get("code_reviewer", {})
                if review_results:
                    # Check for artifacts in the agent response
                    artifacts = review_results.get("artifacts", [])
                    documentation = review_results.get("documentation", {})
                    output = review_results.get("output", {})
                    
                    print(f"  🔍 Code review completed successfully")
                    print(f"    📊 Generated {len(artifacts)} artifacts: {[a.get('name', 'unknown') for a in artifacts]}")
                    print(f"    📄 Documentation created: {bool(documentation)}")
                    print(f"    📋 Output summary: {output.get('summary', {})}")
                else:
                    print("  ⚠️ No code review results")
            
            elif agent_name == "test_generator":
                test_files = test_state.get("tests", {})
                if test_files:
                    print(f"  🧪 Generated {len(test_files)} test files: {list(test_files.keys())}")
                else:
                    print("  ⚠️ No test files generated")
            
            elif agent_name == "documentation_generator":
                documentation = test_state.get("documentation", {})
                diagrams = test_state.get("diagrams", {})
                if documentation:
                    print(f"  📄 Generated {len(documentation)} documentation files: {list(documentation.keys())}")
                if diagrams:
                    print(f"  📊 Generated {len(diagrams)} diagrams: {list(diagrams.keys())}")
                if not documentation and not diagrams:
                    print("  ⚠️ No documentation or diagrams generated")
            
            elif agent_name == "security_analyst":
                # Check for security analysis results in agent outputs
                security_results = test_state.get("agent_outputs", {}).get("security_analyst", {})
                if security_results:
                    # Check for artifacts in the agent response
                    artifacts = security_results.get("artifacts", [])
                    documentation = security_results.get("documentation", {})
                    output = security_results.get("output", {})
                    
                    print(f"  🔒 Security analysis completed successfully")
                    print(f"    📊 Generated {len(artifacts)} artifacts: {[a.get('name', 'unknown') for a in artifacts]}")
                    print(f"    📄 Documentation created: {bool(documentation)}")
                    print(f"    📋 Output summary: {output.get('summary', {})}")
                else:
                    print("  ⚠️ No security analysis results")
        
        # Final verification
        print("\n🔍 Final Artifact Verification:")
        
        # Check all artifact types
        artifact_counts = {
            "Requirements": len(test_state.get("requirements", [])),
            "Code Files": len(test_state.get("code_files", {})),
            "Test Files": len(test_state.get("tests", {})),
            "Documentation Files": len(test_state.get("documentation", {})),
            "Diagrams": len(test_state.get("diagrams", {})),
            "Agent Outputs": len(test_state.get("agent_outputs", {}))
        }
        
        total_artifacts = sum(artifact_counts.values())
        print(f"📊 Total artifacts generated: {total_artifacts}")
        
        for artifact_type, count in artifact_counts.items():
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {artifact_type}: {count}")
        
        # Assert minimum requirements
        assert artifact_counts["Requirements"] > 0, "No requirements generated"
        assert artifact_counts["Code Files"] > 0, "No code files generated"
        assert artifact_counts["Test Files"] > 0, "No test files generated"
        assert artifact_counts["Documentation Files"] > 0, "No documentation files generated"
        assert artifact_counts["Agent Outputs"] > 0, "No agent outputs recorded"
        
        print("\n✅ Complete workflow test passed! All artifacts generated successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    sys.exit(0 if success else 1)
