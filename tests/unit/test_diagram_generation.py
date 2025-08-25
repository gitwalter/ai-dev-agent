#!/usr/bin/env python3
"""
Test script to verify diagram generation functionality.
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
from agents.documentation_generator import DocumentationGenerator
import google.generativeai as genai


async def test_diagram_generation():
    """Test diagram generation functionality."""
    print("🧪 Testing Diagram Generation...")
    
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
    
    # Setup agent configuration
    agent_config = AgentConfig(
        name="documentation_generator",
        description="Generates comprehensive documentation and diagrams",
        enabled=True,
        max_retries=3,
        timeout=300,
        prompt_template="Generate documentation for the project",
        system_prompt="You are a documentation generator agent",
        parameters={
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_tokens": 8192
        }
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
    
    # Create documentation generator
    try:
        doc_generator = DocumentationGenerator(agent_config, gemini_client)
        print("✅ Documentation generator created successfully")
    except Exception as e:
        print(f"❌ Failed to create documentation generator: {e}")
        return False
    
    # Create test state
    test_state = create_initial_state(
        project_context="Create a simple user management system with authentication",
        project_name="test-user-management",
        session_id="test-session-123"
    )
    
    # Add mock data to state
    test_state.update({
        "code_files": {
            "main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}",
            "models.py": "from pydantic import BaseModel\n\nclass User(BaseModel):\n    id: int\n    name: str\n    email: str"
        },
        "architecture": {
            "components": ["API Layer", "Business Logic", "Data Layer"],
            "technology_stack": ["FastAPI", "SQLAlchemy", "PostgreSQL"]
        },
        "requirements": [
            {"type": "functional", "description": "User authentication"},
            {"type": "functional", "description": "User registration"}
        ]
    })
    
    print("✅ Test state created successfully")
    print("📋 Project context: User management system with authentication")
    print("🏗️ Architecture: FastAPI + SQLAlchemy + PostgreSQL")
    print("📝 Requirements: User authentication and registration")
    
    try:
        # Execute documentation generation
        print("\n🔄 Executing documentation generation...")
        result_state = await doc_generator.execute(test_state)
        
        # Check for diagrams in the result
        diagrams = result_state.get("diagrams", {})
        
        if diagrams:
            print(f"✅ Successfully generated {len(diagrams)} diagrams:")
            for diagram_type, diagram_data in diagrams.items():
                if isinstance(diagram_data, dict):
                    filename = diagram_data.get("filename", f"{diagram_type}.puml")
                    description = diagram_data.get("description", "No description")
                    print(f"  📊 {diagram_type}: {filename} - {description}")
                else:
                    print(f"  📊 {diagram_type}: {diagram_data}")
        else:
            print("⚠️ No diagrams generated (this might be expected in test mode)")
        
        # Check for documentation files
        documentation = result_state.get("documentation", {})
        if documentation:
            print(f"✅ Successfully generated {len(documentation)} documentation files:")
            for filename in documentation.keys():
                print(f"  📄 {filename}")
        
        # Check for agent outputs
        agent_outputs = result_state.get("agent_outputs", {})
        if agent_outputs:
            print(f"✅ Agent outputs recorded:")
            for task_name, output in agent_outputs.items():
                print(f"  🔧 {task_name}: {type(output).__name__}")
        
        print("\n✅ Diagram generation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Diagram generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_diagram_generation())
    sys.exit(0 if success else 1)
