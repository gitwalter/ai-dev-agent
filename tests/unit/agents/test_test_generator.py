#!/usr/bin/env python3
"""
Test file for TestGenerator agent.

Tests the test generator agent functionality and output validation.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import components to test
from agents.test_generator import TestGenerator
from agents.base_agent import AgentConfig
import streamlit as st
import google.generativeai as genai

class TestTestGenerator:
    """Test cases for TestGenerator agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pass
        
    def teardown_method(self):
        """Clean up after tests."""
        pass
    
    @pytest.mark.asyncio
    async def test_test_generator_functionality(self):
        """Test the test generator agent functionality."""
        print("🧪 Testing Test Generator Agent...")
        
        try:
            # Setup configuration
            config = AgentConfig(
                agent_id='test_generator',
                agent_type='test_generation',
                prompt_template_id='test_generator_template',
                optimization_enabled=True,
                performance_monitoring=True,
                max_retries=3,
                timeout_seconds=300,
                model_name='gemini-2.5-flash-lite',
                temperature=0.1
            )
            
            # Setup Gemini client
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                pytest.skip("No API key found")
                
            genai.configure(api_key=api_key)
            client = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            # Create test generator
            agent = TestGenerator(config, client)
            
            # Create test state using proper initial state
            from models.state import create_initial_state
            import uuid
            
            state = create_initial_state(
                project_context='Simple test project',
                project_name='test-project',
                session_id=str(uuid.uuid4())
            )
            
            # Add code files to the state
            state['code_files'] = {
                'app.py': {'content': 'def hello(): return "Hello World"'}
            }
            
            print("🔄 Executing test generator...")
            result = await agent.execute(state)
            
            # Check results
            test_files = result.get('tests', {})
            print(f"📊 Test files generated: {len(test_files)}")
            print(f"📁 Test file keys: {list(test_files.keys())}")
            
            # Assertions
            assert test_files, "Test generator should produce test files"
            assert len(test_files) > 0, "Should generate at least one test file"
            
            # Check that test files have meaningful content
            for file_path, content in test_files.items():
                # Test files can be stored as dictionaries with metadata or as strings
                if isinstance(content, dict):
                    # Extract content from dictionary structure
                    file_content = content.get('content', '')
                    filename = content.get('filename', file_path)
                    test_type = content.get('test_type', 'unknown')
                    print(f"    📄 {filename} ({test_type}): {len(file_content)} characters")
                else:
                    # Direct string content
                    file_content = content
                    filename = file_path
                    print(f"    📄 {filename}: {len(file_content)} characters")
                
                assert file_content, f"Test file {filename} should have content"
                assert len(file_content.strip()) > 50, f"Test file {filename} should have meaningful content"
                assert 'test' in file_content.lower() or 'assert' in file_content.lower(), f"Test file {filename} should contain test code"
            
            print("✅ Test generator is working correctly!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"Test generator test failed: {e}")
