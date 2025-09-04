#!/usr/bin/env python3
"""
Simple Test Script for AI Development Agent System.
Tests each agent in isolation with real LLM integration without Streamlit.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration with API key."""
    try:
        from models.config import get_default_config
        config = get_default_config()
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None

def setup_gemini_client(config):
    """Setup Gemini client for testing."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=config.gemini.api_key)
        gemini_client = genai.GenerativeModel(
            model_name=config.gemini.model_name,
            generation_config={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        return gemini_client
    except Exception as e:
        logger.error(f"Failed to setup Gemini client: {e}")
        return None

def get_mock_state_for_agent(agent_name: str) -> Dict[str, Any]:
    """Get realistic mock state for testing a specific agent."""
    from models.state import create_initial_state
    
    # Base state
    base_state = create_initial_state(
        project_name="test-ecommerce-app",
        project_context="""Create a comprehensive E-commerce API and UI with the following features:
- Product catalog with categories and search functionality
- Shopping cart with persistent storage
- User authentication and profile management
- Order management and tracking system
- Payment integration (Stripe/PayPal)
- Inventory management with stock tracking
- Product reviews and ratings system
- Discount codes and promotional features
- Shipping calculation and tracking
- Admin dashboard with analytics
- RESTful API with FastAPI
- PostgreSQL database with complex relationships
- Redis for caching and session management
- Comprehensive testing suite
- API documentation with Swagger UI
- Streamlit UI for all admin functions""",
        session_id="test-session-123"
    )
    
    # Add mock outputs from previous agents based on which agent we're testing
    if agent_name == "requirements_analyst":
        return base_state
    
    elif agent_name == "architecture_designer":
        base_state["requirements"] = [
            {
                "id": "FR-001",
                "title": "Product Catalog Management",
                "description": "Complete product management system with CRUD operations",
                "priority": "high",
                "complexity": "high",
                "acceptance_criteria": [
                    "Users can browse products by category",
                    "Users can search products by name and description",
                    "Admin can add, edit, and delete products",
                    "Products have images, descriptions, and pricing"
                ]
            },
            {
                "id": "FR-002",
                "title": "User Authentication",
                "description": "Secure user authentication and authorization system",
                "priority": "high",
                "complexity": "medium",
                "acceptance_criteria": [
                    "Users can register with email and password",
                    "Users can login and logout",
                    "Password reset functionality",
                    "JWT token-based authentication"
                ]
            }
        ]
        return base_state
    
    elif agent_name == "code_generator":
        base_state["requirements"] = [
            {
                "id": "FR-001",
                "title": "Product Catalog Management",
                "description": "Complete product management system with CRUD operations",
                "priority": "high",
                "complexity": "high"
            }
        ]
        base_state["architecture"] = {
            "system_overview": "Microservices architecture with FastAPI backend and React frontend",
            "technology_stack": {
                "backend": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
                "frontend": ["React", "TypeScript", "Material-UI"],
                "database": ["PostgreSQL", "Redis"],
                "infrastructure": ["Docker", "AWS"]
            },
            "components": [
                {
                    "name": "Product Service",
                    "description": "Handles product catalog and inventory management",
                    "technology": "FastAPI + SQLAlchemy + PostgreSQL"
                }
            ]
        }
        return base_state
    
    elif agent_name == "test_generator":
        base_state["requirements"] = [
            {
                "id": "FR-001",
                "title": "Product Catalog Management",
                "description": "Complete product management system with CRUD operations",
                "priority": "high",
                "complexity": "high"
            }
        ]
        base_state["architecture"] = {
            "system_overview": "Microservices architecture with FastAPI backend",
            "technology_stack": {
                "backend": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
                "frontend": ["React", "TypeScript"],
                "database": ["PostgreSQL"]
            }
        }
        base_state["code_files"] = {
            "main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}",
            "models.py": "from sqlalchemy import Column, Integer, String\nfrom sqlalchemy.ext.declarative import declarative_base\nBase = declarative_base()\nclass Product(Base):\n    __tablename__ = 'products'\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n    price = Column(Integer)"
        }
        return base_state
    
    elif agent_name == "code_reviewer":
        base_state["code_files"] = {
            "main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}",
            "models.py": "from sqlalchemy import Column, Integer, String\nfrom sqlalchemy.ext.declarative import declarative_base\nBase = declarative_base()\nclass Product(Base):\n    __tablename__ = 'products'\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n    price = Column(Integer)"
        }
        return base_state
    
    elif agent_name == "security_analyst":
        base_state["code_files"] = {
            "main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}",
            "models.py": "from sqlalchemy import Column, Integer, String\nfrom sqlalchemy.ext.declarative import declarative_base\nBase = declarative_base()\nclass Product(Base):\n    __tablename__ = 'products'\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n    price = Column(Integer)"
        }
        base_state["architecture"] = {
            "system_overview": "FastAPI backend with PostgreSQL database",
            "technology_stack": {
                "backend": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
                "frontend": ["React", "TypeScript"]
            }
        }
        return base_state
    
    elif agent_name == "documentation_generator":
        base_state["code_files"] = {
            "main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello World'}",
            "models.py": "from sqlalchemy import Column, Integer, String\nfrom sqlalchemy.ext.declarative import declarative_base\nBase = declarative_base()\nclass Product(Base):\n    __tablename__ = 'products'\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n    price = Column(Integer)"
        }
        base_state["architecture"] = {
            "system_overview": "FastAPI backend with PostgreSQL database",
            "technology_stack": {
                "backend": ["FastAPI", "SQLAlchemy", "PostgreSQL"]
            }
        }
        return base_state
    
    else:
        return base_state

async def test_agent(agent_name: str, config) -> bool:
    """Test a specific agent with realistic input."""
    try:
        logger.info(f"Testing agent: {agent_name}")
        
        # Setup Gemini client
        gemini_client = setup_gemini_client(config)
        if not gemini_client:
            logger.error("Failed to setup Gemini client")
            return False
        
        # Get mock state for this agent
        state = get_mock_state_for_agent(agent_name)
        
        # Create agent-specific config
        from models.config import AgentConfig
        agent_config = AgentConfig(
            name=agent_name,
            description=f"Test {agent_name} agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Placeholder prompt template - using database",
            system_prompt="Placeholder system prompt - using database",
            parameters={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_tokens": 8192
            }
        )
        
        # Import the agent
        if agent_name == "requirements_analyst":
            from agents.development.requirements_analyst import RequirementsAnalyst
            agent = RequirementsAnalyst(agent_config, gemini_client)
        elif agent_name == "architecture_designer":
            from agents.development.architecture_designer import ArchitectureDesigner
            agent = ArchitectureDesigner(agent_config, gemini_client)
        elif agent_name == "code_generator":
            from agents.development.code_generator import CodeGenerator
            agent = CodeGenerator(agent_config, gemini_client)
        elif agent_name == "test_generator":
            from agents.development.test_generator import TestGenerator
            agent = TestGenerator(agent_config, gemini_client)
        elif agent_name == "code_reviewer":
            from agents.development.code_reviewer import CodeReviewer
            agent = CodeReviewer(agent_config, gemini_client)
        elif agent_name == "security_analyst":
            from agents.security.security_analyst import SecurityAnalyst
            agent = SecurityAnalyst(agent_config, gemini_client)
        elif agent_name == "documentation_generator":
            from agents.development.documentation_generator import DocumentationGenerator
            agent = DocumentationGenerator(agent_config, gemini_client)
        else:
            logger.error(f"Unknown agent: {agent_name}")
            return False
        
        # Execute the agent
        start_time = time.time()
        result = await agent.execute(state)
        execution_time = time.time() - start_time
        
        # Log results
        logger.info(f"Agent {agent_name} executed in {execution_time:.2f}s")
        logger.info(f"Result keys: {list(result.keys())}")
        
        # Check for specific outputs based on agent type
        if agent_name == "requirements_analyst":
            # Add detailed logging to debug the issue
            logger.info(f"Requirements analyst result keys: {list(result.keys())}")
            
            # Check for requirements in the correct location based on actual output structure
            requirements = []
            agent_outputs = result.get("agent_outputs", {})
            if "requirements_analyst" in agent_outputs:
                requirements_analysis = agent_outputs["requirements_analyst"]
                if isinstance(requirements_analysis, dict):
                    # Check in requirements_analysis.output.requirements_analysis.requirements
                    output = requirements_analysis.get("output", {})
                    if isinstance(output, dict):
                        req_analysis = output.get("requirements_analysis", {})
                        if isinstance(req_analysis, dict):
                            requirements = req_analysis.get("requirements", [])
            
            if len(requirements) > 0:
                logger.info(f"Generated {len(requirements)} requirements")
                return True
            else:
                logger.error("No requirements generated")
                logger.error(f"Available keys in result: {list(result.keys())}")
                # Log the actual result structure for debugging
                logger.error(f"Result structure: {result}")
                return False
        
        elif agent_name == "architecture_designer":
            architecture = result.get("architecture", {})
            if architecture and "system_overview" in architecture:
                logger.info("Architecture generated successfully")
                return True
            else:
                logger.error("No architecture generated")
                return False
        
        elif agent_name == "code_generator":
            code_files = result.get("code_files", {})
            if len(code_files) > 0:
                logger.info(f"Generated {len(code_files)} code files")
                return True
            else:
                logger.error("No code files generated")
                return False
        
        elif agent_name == "test_generator":
            tests = result.get("tests", {})
            if len(tests) > 0:
                logger.info(f"Generated {len(tests)} test files")
                return True
            else:
                logger.error("No test files generated")
                return False
        
        elif agent_name == "code_reviewer":
            agent_outputs = result.get("agent_outputs", {})
            if agent_outputs and "code_reviewer" in agent_outputs:
                logger.info("Code review completed")
                return True
            else:
                logger.error("No code review output")
                return False
        
        elif agent_name == "security_analyst":
            agent_outputs = result.get("agent_outputs", {})
            if agent_outputs and "security_analyst" in agent_outputs:
                logger.info("Security analysis completed")
                return True
            else:
                logger.error("No security analysis output")
                return False
        
        elif agent_name == "documentation_generator":
            documentation = result.get("documentation", {})
            if len(documentation) > 0:
                logger.info(f"Generated {len(documentation)} documentation files")
                return True
            else:
                logger.error("No documentation generated")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing agent {agent_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    logger.info("Starting agent tests...")
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
    
    # Test each agent
    agents = [
        "requirements_analyst",
        "architecture_designer", 
        "code_generator",
        "test_generator",
        "code_reviewer",
        "security_analyst",
        "documentation_generator"
    ]
    
    results = {}
    for agent_name in agents:
        success = await test_agent(agent_name, config)
        results[agent_name] = success
        logger.info(f"Agent {agent_name}: {'PASS' if success else 'FAIL'}")
    
    # Summary
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    logger.info(f"Test Summary: {passed}/{total} agents passed")
    
    # Print detailed results
    for agent_name, success in results.items():
        status = "PASS" if success else "FAIL"
        logger.info(f"  {agent_name}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
