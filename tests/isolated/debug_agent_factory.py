"""
Debug script to test AgentNodeFactory
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from workflow.langgraph_workflow_manager import AgentNodeFactory
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

def main():
    print("🔍 Debugging AgentNodeFactory...")
    
    # Load API key
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-api-key-here":
            raise ValueError("Invalid API key")
        print("✅ API key loaded")
    except Exception as e:
        print(f"❌ Failed to load API key: {e}")
        return
    
    # Create LLM
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.1
        )
        print("✅ LLM created")
    except Exception as e:
        print(f"❌ Failed to create LLM: {e}")
        return
    
    # Create factory
    try:
        factory = AgentNodeFactory(llm)
        print("✅ AgentNodeFactory created")
    except Exception as e:
        print(f"❌ Failed to create factory: {e}")
        return
    
    # Check available methods
    print("\n📋 Available methods:")
    methods = [method for method in dir(factory) if method.startswith('create_') and method.endswith('_node')]
    for method in methods:
        print(f"  - {method}")
    
    # Test specific method
    try:
        if hasattr(factory, 'create_code_reviewer_node'):
            print("✅ create_code_reviewer_node method exists")
            node = factory.create_code_reviewer_node()
            print("✅ Code reviewer node created successfully")
        else:
            print("❌ create_code_reviewer_node method not found")
    except Exception as e:
        print(f"❌ Error creating code reviewer node: {e}")

if __name__ == "__main__":
    main()
