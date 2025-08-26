#!/usr/bin/env python3
"""
Real LLM integration test using Streamlit secrets.
"""

import asyncio
import sys
from pathlib import Path
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from workflow.langgraph_workflow_manager import AgentNodeFactory

async def test_real_requirements_analysis():
    """Test real requirements analysis with actual LLM."""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        print(f"API Key found: {api_key[:10]}..." if api_key else "No API key found")
        
        if not api_key:
            print("ERROR: No GEMINI_API_KEY in Streamlit secrets")
            return False
        
        # Create LLM instance
        print("Creating LLM instance...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Test basic LLM call first
        print("Testing basic LLM call...")
        test_response = llm.invoke("Say 'Hello, World!'")
        print(f"Basic test response: {test_response.content}")
        
        # Create agent node factory
        factory = AgentNodeFactory(llm)
        
        # Create test state
        test_state = {
            "project_context": "Create a simple todo list application with user authentication",
            "project_name": "test-todo-app",
            "session_id": "test-session-real-llm",
            "requirements": [],
            "architecture": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "requirements_analysis",
            "execution_history": []
        }
        
        # Create and execute requirements node
        print("Creating requirements node...")
        requirements_node = factory.create_requirements_node()
        
        print("Executing requirements analysis...")
        result = await requirements_node(test_state)
        
        # Verify the result
        print(f"Result keys: {list(result.keys())}")
        print(f"Requirements: {result.get('requirements', [])}")
        print(f"Agent outputs: {list(result.get('agent_outputs', {}).keys())}")
        
        # Check if we got requirements
        requirements = result.get("requirements", [])
        if len(requirements) > 0:
            print(f"SUCCESS: Got {len(requirements)} requirements!")
            print(f"First requirement: {requirements[0]}")
            return True
        else:
            print("ERROR: No requirements generated")
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the async test
    success = asyncio.run(test_real_requirements_analysis())
    print(f"Test {'PASSED' if success else 'FAILED'}")
