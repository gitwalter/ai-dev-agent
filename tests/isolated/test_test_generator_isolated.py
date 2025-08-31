#!/usr/bin/env python3
"""
Isolated test for Test Generator Agent to fix parsing issues.

This test follows our systematic problem-solving approach:
1. Define the problem clearly
2. Test in isolation with controlled inputs
3. Apply systematic prompt-parser optimization
4. Validate the solution
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import streamlit as st

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.test_generator import TestGenerator
from models.config import AgentConfig
from models.state import create_initial_state
import google.generativeai as genai
import uuid

class TestTestGeneratorIsolated:
    """Isolated test cases for Test Generator Agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Setup Gemini client
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("No API key found")
        
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Create test configuration
        self.config = AgentConfig(
            agent_id='test_generator_isolated',
            name='test_generator',
            description='Test generator',
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template='Generate tests for: {code_files}',
            system_prompt='You are a test generation expert.',
            parameters={'temperature': 0.1}
        )
        
        # Create test generator
        self.agent = TestGenerator(self.config, self.client)
    
    @pytest.mark.asyncio
    async def test_test_generator_with_simple_input(self):
        """Test test generator with simple, controlled input."""
        print("🧪 Testing Test Generator with Simple Input...")
        
        # Create minimal test state
        state = create_initial_state(
            project_context='Simple calculator project',
            project_name='calculator',
            session_id=str(uuid.uuid4())
        )
        
        # Add simple code file
        state['code_files'] = {
            'calculator.py': {
                'content': '''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b
'''
            }
        }
        
        print("🔄 Executing test generator with simple input...")
        result = await self.agent.execute(state)
        
        # Validate results
        test_files = result.get('tests', {})
        print(f"📊 Test files generated: {len(test_files)}")
        print(f"📁 Test file keys: {list(test_files.keys())}")
        
        # Assertions
        assert test_files, "Test generator should produce test files"
        assert len(test_files) > 0, "Should generate at least one test file"
        
        # Check that test files have meaningful content
        for file_path, content in test_files.items():
            if isinstance(content, dict):
                file_content = content.get('content', '')
                filename = content.get('filename', file_path)
                test_type = content.get('test_type', 'unknown')
                print(f"    📄 {filename} ({test_type}): {len(file_content)} characters")
                assert len(file_content) > 100, f"Test file {filename} should contain substantial content"
            else:
                print(f"    📄 {file_path}: {len(content)} characters")
                assert len(content) > 100, f"Test file {file_path} should contain substantial content"
        
        print("✅ Test generator working with simple input!")
    
    @pytest.mark.asyncio
    async def test_test_generator_with_requirements(self):
        """Test test generator with requirements included."""
        print("🧪 Testing Test Generator with Requirements...")
        
        # Create state with requirements
        state = create_initial_state(
            project_context='Calculator with requirements',
            project_name='calculator',
            session_id=str(uuid.uuid4())
        )
        
        # Add requirements
        state['requirements'] = [
            {
                'id': 'REQ-001',
                'title': 'Addition Function',
                'description': 'System shall provide addition functionality',
                'type': 'functional',
                'priority': 'high'
            },
            {
                'id': 'REQ-002', 
                'title': 'Subtraction Function',
                'description': 'System shall provide subtraction functionality',
                'type': 'functional',
                'priority': 'high'
            }
        ]
        
        # Add code files
        state['code_files'] = {
            'calculator.py': {
                'content': '''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b
'''
            }
        }
        
        print("🔄 Executing test generator with requirements...")
        result = await self.agent.execute(state)
        
        # Validate results
        test_files = result.get('tests', {})
        print(f"📊 Test files generated: {len(test_files)}")
        
        assert test_files, "Test generator should produce test files with requirements"
        assert len(test_files) > 0, "Should generate at least one test file"
        
        print("✅ Test generator working with requirements!")
    
    @pytest.mark.asyncio
    async def test_test_generator_output_structure(self):
        """Test that test generator produces proper output structure."""
        print("🧪 Testing Test Generator Output Structure...")
        
        # Create test state
        state = create_initial_state(
            project_context='Structure test',
            project_name='structure-test',
            session_id=str(uuid.uuid4())
        )
        
        state['code_files'] = {
            'app.py': {
                'content': 'def hello(): return "Hello World"'
            }
        }
        
        print("🔄 Executing test generator for structure validation...")
        result = await self.agent.execute(state)
        
        # Validate output structure
        assert 'tests' in result, "Result should contain 'tests' key"
        assert 'agent_outputs' in result, "Result should contain 'agent_outputs' key"
        assert 'test_generator_isolated' in result['agent_outputs'], "Should contain test_generator_isolated output"
        
        test_files = result['tests']
        assert isinstance(test_files, dict), "Tests should be a dictionary"
        
        print("✅ Test generator produces proper output structure!")
    
    @pytest.mark.asyncio
    async def test_test_generator_error_handling(self):
        """Test test generator error handling with invalid input."""
        print("🧪 Testing Test Generator Error Handling...")
        
        # Create state with invalid input
        state = create_initial_state(
            project_context='Error test',
            project_name='error-test',
            session_id=str(uuid.uuid4())
        )
        
        # No code files - should handle gracefully
        state['code_files'] = {}
        
        print("🔄 Executing test generator with invalid input...")
        result = await self.agent.execute(state)
        
        # Should handle gracefully, not crash
        assert 'tests' in result, "Should handle empty code files gracefully"
        assert 'errors' in result, "Should track errors"
        
        print("✅ Test generator handles errors gracefully!")

if __name__ == "__main__":
    # Run isolated tests
    pytest.main([__file__, "-v"])
