#!/usr/bin/env python3
"""
Test script to verify the complete workflow with real LLM usage.
Tests all agents in sequence and verifies that artifacts are produced correctly.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.config import AgentConfig, GeminiConfig, StorageConfig
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
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key and api_key != "your-gemini-api-key-here":
            print("✅ API key loaded from Streamlit secrets")
        else:
            print("❌ Invalid Gemini API key in Streamlit secrets")
            print("Please set a valid API key in .streamlit/secrets.toml")
            return False
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
    
    # Track parsing failures
    parsing_failures = []
    
    # Capture console output to detect parsing failures
    import io
    import sys
    from contextlib import redirect_stdout
    
    try:
        for agent_name, step_name in workflow_steps:
            print(f"\n🔄 Executing {step_name}...")
            
            # Capture console output during agent execution
            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                agent = agents[agent_name]
                test_state = await agent.execute(test_state)
            
            # Analyze captured output for parsing failures
            output_text = captured_output.getvalue()
            if any(keyword in output_text.lower() for keyword in [
                "parsing failed", "output validation failed", "json parsing failed",
                "pydantic validation", "invalid output structure", "fallback data",
                "all parsing methods failed", "using fallback data"
            ]):
                parsing_failures.append(f"{agent_name}: Parsing failures detected in console output")
                print(f"  ❌ {agent_name} parsing failures detected in console output")
                # Print the relevant part of the output for debugging
                lines = output_text.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in [
                        "parsing failed", "validation failed", "fallback data"
                    ]):
                        print(f"    📝 {line.strip()}")
            
            print(f"✅ {step_name} completed successfully")
            
            # Check for parsing failures in agent outputs
            agent_output = test_state.get("agent_outputs", {}).get(agent_name, {})
            if agent_output:
                # Check for fallback data indicators
                if agent_output.get("fallback_data") or agent_output.get("fallback_used"):
                    parsing_failures.append(f"{agent_name}: Used fallback data")
                    print(f"  ❌ {agent_name} used fallback data - parsing failed")
                
                # Check for error messages indicating parsing failures
                error_message = agent_output.get("error_message", "")
                if error_message and any(keyword in error_message.lower() for keyword in [
                    "parsing failed", "output validation failed", "json parsing failed",
                    "pydantic validation", "invalid output structure"
                ]):
                    parsing_failures.append(f"{agent_name}: {error_message}")
                    print(f"  ❌ {agent_name} parsing error: {error_message}")
                
                # Check for artifacts that indicate fallback usage
                artifacts = agent_output.get("artifacts", [])
                for artifact in artifacts:
                    if isinstance(artifact, dict) and artifact.get("name") in [
                        "fallback_data", "parsing_error", "invalid_output"
                    ]:
                        parsing_failures.append(f"{agent_name}: Fallback artifact detected")
                        print(f"  ❌ {agent_name} fallback artifact detected")
                
                # Check for execution logs that indicate parsing failures
                execution_logs = agent_output.get("execution_logs", [])
                for log_entry in execution_logs:
                    if isinstance(log_entry, dict):
                        message = log_entry.get("message", "").lower()
                        if any(keyword in message for keyword in [
                            "parsing failed", "output validation failed", "json parsing failed",
                            "pydantic validation", "invalid output structure", "fallback data",
                            "all parsing methods failed"
                        ]):
                            parsing_failures.append(f"{agent_name}: Parsing failure in logs - {log_entry.get('message', '')}")
                            print(f"  ❌ {agent_name} parsing failure in logs: {log_entry.get('message', '')}")
            
            # Check console output for parsing failure messages (capture from the execution logs)
            # Since we can see parsing failures in the console output, we need to detect them
            # The agents are logging parsing failures but still completing successfully with fallbacks
            # We need to be more aggressive in detecting these failures
            
            # Check if the agent output is minimal or empty, which might indicate fallback usage
            if agent_output and len(str(agent_output)) < 100:
                # Very small output might indicate fallback data
                parsing_failures.append(f"{agent_name}: Minimal output detected - possible fallback usage")
                print(f"  ❌ {agent_name} minimal output detected - possible fallback usage")
            
            # Check for specific agent patterns that indicate parsing failures
            if agent_name in ["code_reviewer", "test_generator", "documentation_generator", "security_analyst"]:
                # These agents should have rich, structured outputs
                if not agent_output.get("artifacts") and not agent_output.get("output"):
                    parsing_failures.append(f"{agent_name}: Missing expected structured output")
                    print(f"  ❌ {agent_name} missing expected structured output")
            
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
        
        # Assert no parsing failures occurred
        if parsing_failures:
            print(f"\n🔍 PARSING ERROR ANALYSIS REQUIRED")
            print(f"❌ Parsing failures detected in {len(parsing_failures)} agent(s):")
            for failure in parsing_failures:
                print(f"  - {failure}")
            
            print(f"\n📋 PARSER-PROMPT OPTIMIZATION NEEDED:")
            print("Based on the parsing error analysis rule, the following actions are required:")
            
            # Analyze each failure and suggest optimizations
            for failure in parsing_failures:
                agent_name = failure.split(":")[0]
                error_type = failure.split(":")[1].strip()
                
                print(f"\n🔧 Agent: {agent_name}")
                print(f"   Error: {error_type}")
                
                # Suggest parser-prompt optimizations based on agent type
                if "fallback" in error_type.lower():
                    print("   💡 Suggestion: Current parser may be too strict for this agent's output")
                    print("   🔄 Action: Consider switching to StrOutputParser for text-heavy outputs")
                    print("   📝 Action: Update prompt to specify exact output format")
                
                elif "json" in error_type.lower():
                    print("   💡 Suggestion: JSON parsing issues detected")
                    print("   🔄 Action: Review JSON format in prompts")
                    print("   📝 Action: Add JSON validation examples to prompts")
                
                elif "validation" in error_type.lower():
                    print("   💡 Suggestion: Output validation failures")
                    print("   🔄 Action: Consider using PydanticOutputParser with proper schema")
                    print("   📝 Action: Update prompts with explicit field requirements")
                
                else:
                    print("   💡 Suggestion: General parsing failure")
                    print("   🔄 Action: Analyze current parser-prompt combination")
                    print("   📝 Action: Test alternative parser options")
            
            print(f"\n📊 RECOMMENDED PARSER-PROMPT OPTIMIZATIONS:")
            print("1. Review current parser selection for each failing agent")
            print("2. Update prompts with explicit output format instructions")
            print("3. Test alternative parser-prompt combinations")
            print("4. Implement error prevention strategies")
            print("5. Monitor parsing success rates after optimization")
            
            failure_summary = "\n".join([f"  - {failure}" for failure in parsing_failures])
            raise AssertionError(f"Parsing failures detected in {len(parsing_failures)} agent(s):\n{failure_summary}")
        
        print(f"✅ All {len(workflow_steps)} agents completed with successful parsing")
        
        # Save files to generated_projects folder
        print("\n💾 Saving files to generated_projects folder...")
        try:
            from utils.file_manager import FileManager
            from models.config import StorageConfig
            from pathlib import Path
            
            # Create storage config
            storage_config = StorageConfig(
                output_dir="./generated_projects",
                temp_dir="./temp", 
                backup_dir="./backups"
            )
            
            # Initialize file manager
            file_manager = FileManager(storage_config)
            
            # Prepare files for saving (convert from object format to string content)
            files_to_save = {}
            
            # Add source files (with filename validation)
            for filename, file_obj in test_state.get("code_files", {}).items():
                # Skip if filename is suspiciously long (likely content used as filename)
                if len(filename) > 100:
                    continue
                # Skip if filename contains newlines (definitely content used as filename)
                if '\n' in filename or '\r' in filename:
                    continue
                if isinstance(file_obj, dict) and "content" in file_obj:
                    files_to_save[filename] = file_obj["content"]
                elif isinstance(file_obj, str):
                    files_to_save[filename] = file_obj
            
            # Add test files
            for filename, content in test_state.get("tests", {}).items():
                if isinstance(content, dict) and "content" in content:
                    files_to_save[f"tests/{filename}"] = content["content"]
                elif isinstance(content, str):
                    files_to_save[f"tests/{filename}"] = content
            
            # Add documentation files
            for filename, content in test_state.get("documentation", {}).items():
                if isinstance(content, dict) and "content" in content:
                    files_to_save[f"docs/{filename}"] = content["content"]
                elif isinstance(content, str):
                    files_to_save[f"docs/{filename}"] = content
            
            # Add configuration files
            for filename, content in test_state.get("configuration_files", {}).items():
                if isinstance(content, dict) and "content" in content:
                    files_to_save[filename] = content["content"]
                elif isinstance(content, str):
                    files_to_save[filename] = content
            
            # Create project requirements file
            requirements = test_state.get("requirements", [])
            if requirements:
                requirements_content = "# Project Requirements\n\n"
                for i, req in enumerate(requirements, 1):
                    if isinstance(req, dict):
                        title = req.get("title", f"Requirement {i}")
                        description = req.get("description", "No description")
                        requirements_content += f"## {title}\n{description}\n\n"
                    else:
                        requirements_content += f"## Requirement {i}\n{req}\n\n"
                files_to_save["REQUIREMENTS.md"] = requirements_content
            
            # Save state file
            state_content = {
                "project_name": test_state.get("project_name", ""),
                "project_context": test_state.get("project_context", ""),
                "session_id": test_state.get("session_id", ""),
                "total_artifacts": total_artifacts,
                "artifact_counts": artifact_counts,
                "timestamp": datetime.now().isoformat()
            }
            files_to_save["workflow_state.json"] = json.dumps(state_content, indent=2)
            
            # Save all files
            if files_to_save:
                project_path = file_manager.save_generated_files(
                    files_to_save,
                    test_state.get("project_name", "test-task-management")
                )
                print(f"✅ Files saved successfully to: {project_path}")
                print(f"📁 Total files saved: {len(files_to_save)}")
                
                # List saved files
                saved_file_list = list(files_to_save.keys())
                for filename in saved_file_list[:10]:  # Show first 10 files
                    print(f"   📄 {filename}")
                if len(saved_file_list) > 10:
                    print(f"   ... and {len(saved_file_list) - 10} more files")
            else:
                print("⚠️ No files to save")
                
        except Exception as e:
            print(f"❌ Failed to save files: {e}")
            import traceback
            traceback.print_exc()
        
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
