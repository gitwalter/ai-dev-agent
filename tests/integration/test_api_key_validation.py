#!/usr/bin/env python3
"""
Simple API key validation test using Streamlit secrets.
"""

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

def test_api_key():
    """Test if the API key is valid using Streamlit secrets."""
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("GEMINI_API_KEY")
    print(f"API Key found: {api_key[:10]}..." if api_key else "No API key found")
    
    assert api_key is not None, "No GEMINI_API_KEY in Streamlit secrets"
    
    # Try to create LLM instance
    print("Creating LLM instance...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=api_key,
        temperature=0.1
    )
    
    # Try a simple test call
    print("Testing API call...")
    response = llm.invoke("Say 'Hello, World!'")
    print(f"Response: {response.content}")
    
    # Assert that we got a valid response
    assert response is not None, "Failed to get response from API"
    assert hasattr(response, 'content'), "Response missing content attribute"
    assert response.content, "Response content is empty"
    
    print("SUCCESS: API key is valid!")

if __name__ == "__main__":
    test_api_key()
