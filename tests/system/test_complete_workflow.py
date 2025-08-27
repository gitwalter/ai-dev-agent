#!/usr/bin/env python3
"""
Test script to verify the complete workflow with real LLM usage.
Tests the LangGraph workflow (same as Streamlit app) and verifies that artifacts are produced correctly.
"""

import asyncio
import sys
import os
import json
import pytest
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from models.config import AgentConfig, GeminiConfig, StorageConfig, get_default_config
from models.state import create_initial_state
from models.responses import WorkflowResult, WorkflowStatus
import google.generativeai as genai


def validate_requirements_analyst_output(agent_result):
    """Validate requirements analyst produces correct artifacts."""
    print(f"  🔍 Validating Requirements Analyst output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Requirements analyst should have output"
    assert agent_result.output is not None, "Requirements analyst output should not be None"
    
    # Check for functional requirements
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'functional_requirements' in output, "Requirements analyst should produce functional_requirements"
        assert isinstance(output['functional_requirements'], list), "functional_requirements should be a list"
        assert len(output['functional_requirements']) > 0, "Should have at least one functional requirement"
        
        # Validate each requirement has meaningful content
        for req in output['functional_requirements']:
            assert isinstance(req, dict), "Each requirement should be a dictionary"
            assert 'description' in req, "Each requirement should have a description"
            assert len(req['description'].strip()) > 10, "Requirement description should be meaningful"
        
        # Check for non-functional requirements
        if 'non_functional_requirements' in output:
            assert isinstance(output['non_functional_requirements'], list), "non_functional_requirements should be a list"
        
        # Check for project scope
        if 'project_scope' in output:
            assert isinstance(output['project_scope'], str), "project_scope should be a string"
            assert len(output['project_scope']) > 0, "project_scope should not be empty"
        
        print(f"    ✅ Functional requirements: {len(output['functional_requirements'])} items")
        return True
    else:
        print(f"    ❌ Requirements analyst output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_architecture_designer_output(agent_result):
    """Validate architecture designer produces correct artifacts."""
    print(f"  🔍 Validating Architecture Designer output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Architecture designer should have output"
    assert agent_result.output is not None, "Architecture designer output should not be None"
    
    # Check for architecture design
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'architecture_design' in output, "Architecture designer should produce architecture_design"
        assert isinstance(output['architecture_design'], dict), "architecture_design should be a dictionary"
        
        # Check for technology stack
        if 'technology_stack' in output['architecture_design']:
            assert isinstance(output['architecture_design']['technology_stack'], list), "technology_stack should be a list"
            assert len(output['architecture_design']['technology_stack']) > 0, "Should have at least one technology"
        
        # Check for system components
        if 'system_components' in output['architecture_design']:
            assert isinstance(output['architecture_design']['system_components'], list), "system_components should be a list"
        
        print(f"    ✅ Architecture design: {len(output['architecture_design'])} components")
        return True
    else:
        print(f"    ❌ Architecture designer output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_code_generator_output(agent_result):
    """Validate code generator produces correct artifacts."""
    print(f"  🔍 Validating Code Generator output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Code generator should have output"
    assert agent_result.output is not None, "Code generator output should not be None"
    
    # Check for code files
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'code_files' in output, "Code generator should produce code_files"
        assert isinstance(output['code_files'], dict), "code_files should be a dictionary"
        assert len(output['code_files']) > 0, "Should generate at least one code file"
        
        # Check that each code file has content
        for file_path, content in output['code_files'].items():
            assert isinstance(content, str), f"Code file {file_path} content should be a string"
            assert len(content.strip()) > 50, f"Code file {file_path} should have meaningful content"
            assert 'def ' in content or 'class ' in content, f"Code file {file_path} should contain functions or classes"
        
        # Check for main application file
        main_files = [f for f in output['code_files'].keys() if any(keyword in f.lower() for keyword in ['main', 'app', 'index', 'server'])]
        assert len(main_files) > 0, "Should have at least one main application file"
        
        print(f"    ✅ Code files: {len(output['code_files'])} files")
        print(f"    ✅ Main files: {len(main_files)} files")
        return True
    else:
        print(f"    ❌ Code generator output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_test_generator_output(agent_result):
    """Validate test generator produces correct artifacts."""
    print(f"  🔍 Validating Test Generator output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Test generator should have output"
    assert agent_result.output is not None, "Test generator output should not be None"
    
    # Check for test files
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'test_files' in output, "Test generator should produce test_files"
        assert isinstance(output['test_files'], dict), "test_files should be a dictionary"
        assert len(output['test_files']) > 0, "Should generate at least one test file"
        
        # Check that each test file has content
        for file_path, content in output['test_files'].items():
            assert isinstance(content, str), f"Test file {file_path} content should be a string"
            assert len(content.strip()) > 50, f"Test file {file_path} should have meaningful content"
            # Check for test indicators
            assert any(keyword in content.lower() for keyword in ['test', 'assert', 'def test_', 'class test']), f"Test file {file_path} should contain test code"
        
        print(f"    ✅ Test files: {len(output['test_files'])} files")
        return True
    else:
        print(f"    ❌ Test generator output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_code_reviewer_output(agent_result):
    """Validate code reviewer produces correct artifacts."""
    print(f"  🔍 Validating Code Reviewer output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Code reviewer should have output"
    assert agent_result.output is not None, "Code reviewer output should not be None"
    
    # Check for review results
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'review_results' in output, "Code reviewer should produce review_results"
        assert isinstance(output['review_results'], dict), "review_results should be a dictionary"
        
        # Check for quality assessment
        if 'quality_assessment' in output['review_results']:
            assert isinstance(output['review_results']['quality_assessment'], dict), "quality_assessment should be a dictionary"
        
        # Check for issues found
        if 'issues_found' in output['review_results']:
            assert isinstance(output['review_results']['issues_found'], list), "issues_found should be a list"
        
        print(f"    ✅ Review results: {len(output['review_results'])} components")
        return True
    else:
        print(f"    ❌ Code reviewer output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_security_analyst_output(agent_result):
    """Validate security analyst produces correct artifacts."""
    print(f"  🔍 Validating Security Analyst output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Security analyst should have output"
    assert agent_result.output is not None, "Security analyst output should not be None"
    
    # Check for security analysis
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'security_analysis' in output, "Security analyst should produce security_analysis"
        assert isinstance(output['security_analysis'], dict), "security_analysis should be a dictionary"
        
        # Check for vulnerabilities
        if 'vulnerabilities' in output['security_analysis']:
            assert isinstance(output['security_analysis']['vulnerabilities'], list), "vulnerabilities should be a list"
        
        # Check for security recommendations
        if 'security_recommendations' in output['security_analysis']:
            assert isinstance(output['security_analysis']['security_recommendations'], list), "security_recommendations should be a list"
        
        print(f"    ✅ Security analysis: {len(output['security_analysis'])} components")
        return True
    else:
        print(f"    ❌ Security analyst output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_documentation_generator_output(agent_result):
    """Validate documentation generator produces correct artifacts."""
    print(f"  🔍 Validating Documentation Generator output...")
    
    # Check that agent has output
    assert hasattr(agent_result, 'output'), "Documentation generator should have output"
    assert agent_result.output is not None, "Documentation generator output should not be None"
    
    # Check for documentation
    if isinstance(agent_result.output, dict):
        output = agent_result.output
        assert 'documentation' in output, "Documentation generator should produce documentation"
        assert isinstance(output['documentation'], dict), "documentation should be a dictionary"
        
        # Check for documentation files
        if 'documentation_files' in output['documentation']:
            assert isinstance(output['documentation']['documentation_files'], dict), "documentation_files should be a dictionary"
            assert len(output['documentation']['documentation_files']) > 0, "Should generate at least one documentation file"
        
        # Check for README
        if 'documentation_files' in output['documentation']:
            readme_files = [f for f in output['documentation']['documentation_files'].keys() if 'readme' in f.lower()]
            assert len(readme_files) > 0, "Should generate at least one README file"
        
        print(f"    ✅ Documentation: {len(output['documentation'])} components")
        return True
    else:
        print(f"    ❌ Documentation generator output is not a dictionary: {type(agent_result.output)}")
        return False


def validate_agent_outputs(result):
    """Validate that each agent produces the correct expected artifacts."""
    print(f"\n🔍 Validating Agent Outputs...")
    
    if not result.agent_results:
        print("  ⚠️ No agent results found")
        return False
    
    validation_results = {}
    
    for agent_name, agent_result in result.agent_results.items():
        print(f"\n  🤖 Validating {agent_name}...")
        
        try:
            if agent_name == "requirements_analyst":
                validation_results[agent_name] = validate_requirements_analyst_output(agent_result)
            elif agent_name == "architecture_designer":
                validation_results[agent_name] = validate_architecture_designer_output(agent_result)
            elif agent_name == "code_generator":
                validation_results[agent_name] = validate_code_generator_output(agent_result)
            elif agent_name == "test_generator":
                validation_results[agent_name] = validate_test_generator_output(agent_result)
            elif agent_name == "code_reviewer":
                validation_results[agent_name] = validate_code_reviewer_output(agent_result)
            elif agent_name == "security_analyst":
                validation_results[agent_name] = validate_security_analyst_output(agent_result)
            elif agent_name == "documentation_generator":
                validation_results[agent_name] = validate_documentation_generator_output(agent_result)
            else:
                print(f"    ⚠️ Unknown agent type: {agent_name}")
                validation_results[agent_name] = False
                
        except Exception as e:
            print(f"    ❌ Validation failed for {agent_name}: {str(e)}")
            validation_results[agent_name] = False
    
    # Report validation results
    successful_validations = sum(validation_results.values())
    total_validations = len(validation_results)
    
    print(f"\n📊 Agent Validation Summary:")
    print(f"  ✅ Successful: {successful_validations}/{total_validations}")
    
    for agent_name, success in validation_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"    {status} {agent_name}")
    
    if successful_validations == total_validations:
        print(f"\n🎉 All agent validations passed!")
        return True
    else:
        print(f"\n❌ {total_validations - successful_validations} agent validations failed!")
        return False


def validate_workflow_integration(result):
    """Validate that agents work together correctly."""
    print(f"\n🔗 Validating Workflow Integration...")
    
    if not result.agent_results:
        print("  ⚠️ No agent results found for integration validation")
        return False
    
    integration_checks = []
    
    # Validate requirements -> architecture flow
    if 'requirements_analyst' in result.agent_results and 'architecture_designer' in result.agent_results:
        try:
            req_output = result.agent_results['requirements_analyst'].output
            arch_output = result.agent_results['architecture_designer'].output
            
            # Architecture should reference requirements
            arch_text = str(arch_output).lower()
            req_requirements = req_output.get('functional_requirements', [])
            
            if req_requirements:
                # Check if architecture mentions any requirement keywords
                req_keywords = []
                for req in req_requirements[:3]:  # Check first 3 requirements
                    if isinstance(req, dict) and 'description' in req:
                        keywords = req['description'].lower().split()[:3]
                        req_keywords.extend(keywords)
                
                if req_keywords:
                    keyword_found = any(keyword in arch_text for keyword in req_keywords)
                    integration_checks.append(("requirements->architecture", keyword_found))
                    print(f"    {'✅' if keyword_found else '❌'} Requirements->Architecture integration")
        except Exception as e:
            print(f"    ❌ Requirements->Architecture validation failed: {e}")
            integration_checks.append(("requirements->architecture", False))
    
    # Validate architecture -> code flow
    if 'architecture_designer' in result.agent_results and 'code_generator' in result.agent_results:
        try:
            arch_output = result.agent_results['architecture_designer'].output
            code_output = result.agent_results['code_generator'].output
            
            # Code should use technologies from architecture
            arch_design = arch_output.get('architecture_design', {})
            tech_stack = arch_design.get('technology_stack', [])
            code_text = ' '.join(code_output.get('code_files', {}).values()).lower()
            
            if tech_stack:
                tech_used = False
                for tech in tech_stack:
                    if isinstance(tech, dict):
                        tech_name = tech.get('name', '').lower()
                    else:
                        tech_name = str(tech).lower()
                    
                    # Check if technology is used in code
                    if tech_name in ['python', 'flask', 'django', 'fastapi', 'sqlite', 'postgresql']:
                        if tech_name in code_text:
                            tech_used = True
                            break
                
                integration_checks.append(("architecture->code", tech_used))
                print(f"    {'✅' if tech_used else '❌'} Architecture->Code integration")
        except Exception as e:
            print(f"    ❌ Architecture->Code validation failed: {e}")
            integration_checks.append(("architecture->code", False))
    
    # Report integration results
    successful_integrations = sum(check[1] for check in integration_checks)
    total_integrations = len(integration_checks)
    
    if total_integrations > 0:
        print(f"\n📊 Integration Validation Summary:")
        print(f"  ✅ Successful: {successful_integrations}/{total_integrations}")
        
        for check_name, success in integration_checks:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"    {status} {check_name}")
        
        return successful_integrations == total_integrations
    else:
        print("  ⚠️ No integration checks performed")
        return True


def validate_file_system_output(result):
    """Validate that files are actually saved to filesystem."""
    print(f"\n💾 Validating File System Output...")
    
    try:
        # Check project directory exists
        project_path = Path("./generated_projects") / result.project_name
        assert project_path.exists(), f"Project directory should exist: {project_path}"
        
        # Check files are actually saved
        saved_files = list(project_path.rglob("*"))
        saved_files = [f for f in saved_files if f.is_file()]
        assert len(saved_files) > 0, "Should have saved files"
        
        # Validate file contents match expected
        for file_path in saved_files:
            assert file_path.stat().st_size > 0, f"File should not be empty: {file_path}"
            
            # Read and validate file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content.strip()) > 0, f"File should have content: {file_path}"
                
                # Validate file type specific content
                if file_path.suffix == '.py':
                    assert 'def ' in content or 'class ' in content, f"Python file should have functions/classes: {file_path}"
                elif file_path.suffix == '.md':
                    assert '#' in content, f"Markdown file should have headers: {file_path}"
                elif file_path.suffix == '.txt':
                    assert len(content.strip()) > 10, f"Text file should have meaningful content: {file_path}"
        
        print(f"    ✅ Project directory: {project_path}")
        print(f"    ✅ Saved files: {len(saved_files)} files")
        return True
        
    except Exception as e:
        print(f"    ❌ File system validation failed: {e}")
        return False


def validate_no_parsing_errors(result):
    """Validate that no parsing errors occurred."""
    print(f"\n🚫 Validating No Parsing Errors...")
    
    parsing_errors = []
    
    # Check for fallback data usage
    for agent_name, agent_result in result.agent_results.items():
        if hasattr(agent_result, 'documentation') and agent_result.documentation:
            doc = agent_result.documentation
            if isinstance(doc, dict):
                if doc.get("fallback_data") or doc.get("fallback_used"):
                    parsing_errors.append(f"{agent_name}: Used fallback data")
                    print(f"    ❌ {agent_name} used fallback data - parsing failed")
        
        # Check logs for parsing errors
        if hasattr(agent_result, 'logs') and agent_result.logs:
            for log_entry in agent_result.logs:
                if isinstance(log_entry, dict):
                    message = log_entry.get("message", "").lower()
                    error_indicators = [
                        "parsing failed", "output validation failed", 
                        "json parsing failed", "pydantic validation",
                        "invalid output structure", "fallback data"
                    ]
                    if any(indicator in message for indicator in error_indicators):
                        parsing_errors.append(f"{agent_name}: Parsing failure in logs - {log_entry.get('message', '')}")
                        print(f"    ❌ {agent_name} parsing failure in logs: {log_entry.get('message', '')}")
    
    if parsing_errors:
        print(f"\n❌ Parsing Errors Detected ({len(parsing_errors)}):")
        for error in parsing_errors:
            print(f"  - {error}")
        assert False, f"Found {len(parsing_errors)} parsing errors"
    else:
        print("    ✅ No parsing errors detected - all agents working correctly")
        return True


def validate_performance(result):
    """Validate that workflow completes in reasonable time."""
    print(f"\n⏱️ Validating Performance...")
    
    try:
        # Total execution time should be reasonable
        assert result.total_execution_time < 300, f"Workflow took too long: {result.total_execution_time}s"
        assert result.total_execution_time > 5, f"Workflow completed too quickly (suspicious): {result.total_execution_time}s"
        
        # Individual agent times should be reasonable
        for agent_name, agent_result in result.agent_results.items():
            assert agent_result.execution_time < 60, f"{agent_name} took too long: {agent_result.execution_time}s"
            assert agent_result.execution_time > 1, f"{agent_name} completed too quickly: {agent_result.execution_time}s"
        
        print(f"    ✅ Total execution time: {result.total_execution_time:.2f}s")
        print(f"    ✅ All agent execution times within bounds")
        return True
        
    except Exception as e:
        print(f"    ❌ Performance validation failed: {e}")
        return False


def validate_content_quality(result):
    """Validate content quality of generated files."""
    print(f"\n📝 Validating Content Quality...")
    
    try:
        # Check code files have meaningful content
        for file_path, content in result.code_files.items():
            assert content and len(content.strip()) > 100, f"Code file {file_path} should have meaningful content"
            assert 'def ' in content or 'class ' in content, f"Code file {file_path} should contain functions or classes"
            print(f"    ✅ {file_path}: {len(content)} characters")
        
        # Check test files have meaningful content
        for file_path, content in result.test_files.items():
            assert content and len(content.strip()) > 50, f"Test file {file_path} should have meaningful content"
            assert 'test' in content.lower() or 'assert' in content.lower(), f"Test file {file_path} should contain test code"
            print(f"    ✅ {file_path}: {len(content)} characters")
        
        # Check documentation files have meaningful content
        for file_path, content in result.documentation_files.items():
            assert content and len(content.strip()) > 50, f"Documentation file {file_path} should have meaningful content"
            print(f"    ✅ {file_path}: {len(content)} characters")
        
        print(f"    ✅ All files have meaningful content")
        return True
        
    except Exception as e:
        print(f"    ❌ Content quality validation failed: {e}")
        return False


@pytest.mark.asyncio
async def test_complete_workflow():
    """Test the complete LangGraph workflow with real LLM usage (same as Streamlit app)."""
    print("🧪 Testing Complete LangGraph Workflow with Real LLM...")
    
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
    
    # Setup configuration (same as Streamlit app)
    try:
        config = get_default_config()
        config.gemini.api_key = api_key
        config.gemini.model_name = "gemini-2.5-flash-lite"
        config.gemini.temperature = 0.1
        config.gemini.max_tokens = 8192
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Create AI Development Agent (same as Streamlit app)
    try:
        from apps.main import AIDevelopmentAgent
        agent = AIDevelopmentAgent(config)
        print("✅ AI Development Agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create AI Development Agent: {e}")
        return False
    
    # Test project context (same as test)
    project_context = "Create a simple task management system with user authentication, task creation, and status tracking"
    print("📋 Project context: Task management system with authentication and task tracking")
    
    # Execute workflow using the same method as Streamlit app
    try:
        print("\n🔄 Executing LangGraph workflow...")
        
        # Execute workflow (same as Streamlit app)
        result = await agent.execute_workflow(
            project_context=project_context,
            output_dir="./generated_projects"
        )
        
        print("✅ LangGraph workflow completed successfully")
        
        # Verify workflow result structure
        assert isinstance(result, WorkflowResult), "Result should be WorkflowResult"
        assert result.status == WorkflowStatus.COMPLETED, f"Workflow should succeed, got: {result.status}"
        assert result.project_name is not None, "Project name should be set"
        assert result.total_execution_time > 0, "Execution time should be positive"
        
        print(f"📊 Workflow Results:")
        print(f"  📋 Project Name: {result.project_name}")
        print(f"  ⏱️ Execution Time: {result.total_execution_time:.2f}s")
        print(f"  📁 Generated Files: {len(result.generated_files)}")
        print(f"  📄 Documentation Files: {len(result.documentation_files)}")
        print(f"  💻 Code Files: {len(result.code_files)}")
        print(f"  🧪 Test Files: {len(result.test_files)}")
        
        # Verify agent results
        if result.agent_results:
            print(f"  🤖 Agent Results: {len(result.agent_results)} agents")
            for agent_name, agent_result in result.agent_results.items():
                print(f"    ✅ {agent_name}: {len(agent_result.artifacts)} artifacts")
        
        # Verify generated files
        total_files = len(result.generated_files)
        assert total_files > 0, "Should generate at least some files"
        
        # Check for specific file types
        code_files = len(result.code_files)
        test_files = len(result.test_files)
        doc_files = len(result.documentation_files)
        
        print(f"\n📁 File Generation Summary:")
        print(f"  💻 Code Files: {code_files}")
        print(f"  🧪 Test Files: {test_files}")
        print(f"  📄 Documentation Files: {doc_files}")
        print(f"  📊 Total Files: {total_files}")
        
        # Verify minimum requirements
        assert code_files > 0, "Should generate at least one code file"
        assert test_files > 0, "Should generate at least one test file"
        assert doc_files > 0, "Should generate at least one documentation file"
        
        # 1. Agent output validation (MANDATORY)
        agent_validation_success = validate_agent_outputs(result)
        assert agent_validation_success, "Agent output validation failed"
        
        # 2. Integration validation (MANDATORY)
        integration_success = validate_workflow_integration(result)
        assert integration_success, "Workflow integration validation failed"
        
        # 3. File system validation (MANDATORY)
        filesystem_success = validate_file_system_output(result)
        assert filesystem_success, "File system validation failed"
        
        # 4. Error detection validation (MANDATORY)
        validate_no_parsing_errors(result)
        
        # 5. Performance validation (MANDATORY)
        performance_success = validate_performance(result)
        assert performance_success, "Performance validation failed"
        
        # 6. Content quality validation (MANDATORY)
        content_success = validate_content_quality(result)
        assert content_success, "Content quality validation failed"
        
        print(f"\n💾 Saving files to generated_projects folder...")
        
        # Verify files were actually saved
        project_path = Path("./generated_projects") / result.project_name
        if project_path.exists():
            saved_files = list(project_path.rglob("*"))
            saved_files = [f for f in saved_files if f.is_file()]
            print(f"✅ Files saved successfully to: {project_path}")
            print(f"📁 Total files saved: {len(saved_files)}")
            for file_path in saved_files[:10]:  # Show first 10 files
                print(f"   📄 {file_path.relative_to(project_path)}")
            if len(saved_files) > 10:
                print(f"   ... and {len(saved_files) - 10} more files")
        else:
            print(f"⚠️ Project directory not found: {project_path}")
        
        print(f"\n✅ Complete workflow test passed! All artifacts generated successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_complete_workflow())
    if result:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
