"""
Simple test to isolate agent creation issue
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
    print("🔍 Simple Agent Test...")
    
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
    
    # Check all methods
    print("\n📋 All methods in factory:")
    all_methods = [method for method in dir(factory) if not method.startswith('_')]
    for method in all_methods:
        print(f"  - {method}")
    
    # Check specifically for code reviewer
    print(f"\n🔍 Looking for code reviewer method...")
    if hasattr(factory, 'create_code_reviewer_node'):
        print("✅ create_code_reviewer_node found")
        try:
            node = factory.create_code_reviewer_node()
            print("✅ Code reviewer node created")
        except Exception as e:
            print(f"❌ Error creating node: {e}")
    else:
        print("❌ create_code_reviewer_node not found")
        
        # Check if it's a different name
        code_review_methods = [m for m in all_methods if 'review' in m.lower()]
        if code_review_methods:
            print(f"Found similar methods: {code_review_methods}")

if __name__ == "__main__":
    main()
