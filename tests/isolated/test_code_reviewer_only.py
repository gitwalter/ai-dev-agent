"""
Minimal test for Code Reviewer parsing issue
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.code_reviewer import CodeReviewer
from models.config import AgentConfig
import google.generativeai as genai
import streamlit as st

async def test_code_reviewer():
    """Test code reviewer in isolation."""
    print("🧪 Testing Code Reviewer in isolation...")
    
    # Load API key
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-api-key-here":
            raise ValueError("Invalid API key")
    except Exception as e:
        print(f"❌ Failed to load API key: {e}")
        return False
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    gemini_client = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        generation_config={"temperature": 0.1}
    )
    
    # Create agent config
    config = AgentConfig(
        name="code_reviewer",
        description="Test code reviewer agent",
        enabled=True,
        max_retries=3,
        timeout=300,
        prompt_template="Test prompt template",
        system_prompt="Test system prompt"
    )
    
    # Create agent instance
    agent = CodeReviewer(config, gemini_client)
    
    # Create mock state
    mock_state = {
        "project_context": "Create a simple calculator application",
        "project_requirements": "Create a simple calculator application",
        "architecture_design": "Basic calculator with add, subtract, multiply, divide operations",
        "generated_code": """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
        """,
        "code_files": {
            "calculator.py": """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
            """
        },
        "requirements": [
            {"id": "REQ-001", "title": "Basic Calculator", "description": "Simple calculator with 4 operations"}
        ],
        "tests": {
            "test_calculator.py": "def test_add(): assert add(2, 3) == 5"
        },
        "test_cases": [
            "test_add_positive_numbers",
            "test_subtract_negative_numbers", 
            "test_multiply_by_zero",
            "test_divide_by_zero"
        ],
        "agent_outputs": {},
        "errors": [],
        "warnings": [],
        "current_step": "testing"
    }
    
    try:
        # Execute agent
        result = await agent.execute(mock_state)
        print("✅ Code reviewer executed successfully")
        return True
    except Exception as e:
        print(f"❌ Code reviewer failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_code_reviewer())
    sys.exit(0 if success else 1)
