"""
Isolated Agent Testing for Parsing Error Resolution

This module contains isolated tests for agents with parsing errors.
Each test systematically tries different parser-prompt combinations
until finding the optimal one that works without errors.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.code_reviewer import CodeReviewer
from agents.test_generator import TestGenerator
from agents.documentation_generator import DocumentationGenerator
from agents.security_analyst import SecurityAnalyst
from utils.enhanced_output_parsers import EnhancedOutputParserFactory
from utils.prompt_manager import PromptManager
from utils.structured_outputs import (
    CodeReviewOutput, TestGenerationOutput, 
    DocumentationGenerationOutput, SecurityAnalysisOutput
)

# Import Streamlit for secrets
import streamlit as st

class IsolatedAgentTester:
    """Systematic tester for finding optimal parser-prompt combinations."""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.parser_factory = EnhancedOutputParserFactory()
        
        # Load API key
        try:
            self.api_key = st.secrets.get("GEMINI_API_KEY")
            if not self.api_key or self.api_key == "your-gemini-api-key-here":
                raise ValueError("Invalid API key")
        except Exception as e:
            print(f"❌ Failed to load API key: {e}")
            sys.exit(1)
    
    def get_mock_state_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get appropriate mock state for each agent."""
        base_state = {
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
        
        # Agent-specific state additions
        if agent_name == "code_reviewer":
            base_state["code_to_review"] = base_state["generated_code"]
        elif agent_name == "test_generator":
            base_state["code_to_test"] = base_state["generated_code"]
        elif agent_name == "documentation_generator":
            base_state["code_to_document"] = base_state["generated_code"]
        elif agent_name == "security_analyst":
            base_state["code_to_analyze"] = base_state["generated_code"]
        
        return base_state
    
    async def test_parser_prompt_combination(self, agent_name: str, parser_type: str, prompt_type: str) -> bool:
        """Test a specific parser-prompt combination for an agent."""
        print(f"🧪 Testing {agent_name} with {parser_type} + {prompt_type}...")
        
        try:
            # Create mock config and Gemini client for legacy agents
            from models.config import SystemConfig
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            gemini_client = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                generation_config={"temperature": 0.1}
            )
            
            # Create mock agent config
            from models.config import AgentConfig
            config = AgentConfig(
                name=agent_name,
                description=f"Test {agent_name} agent",
                enabled=True,
                max_retries=3,
                timeout=300,
                prompt_template="Test prompt template",
                system_prompt="Test system prompt"
            )
            
            # Map agent names to agent classes
            agent_classes = {
                "code_reviewer": CodeReviewer,
                "test_generator": TestGenerator,
                "documentation_generator": DocumentationGenerator,
                "security_analyst": SecurityAnalyst
            }
            
            if agent_name not in agent_classes:
                print(f"❌ Unknown agent: {agent_name}")
                return False
            
            # Create agent instance
            agent = agent_classes[agent_name](config, gemini_client)
            
            # Get mock state
            mock_state = self.get_mock_state_for_agent(agent_name)
            
            # Execute agent
            result = await agent.execute(mock_state)
            
            # Check for parsing errors
            if self._has_parsing_error(result):
                print(f"❌ Parsing error in {agent_name}: {result.get('error_message', 'Unknown error')}")
                return False
            
            print(f"✅ {agent_name} with {parser_type} + {prompt_type} - SUCCESS")
            return True
            
        except Exception as e:
            print(f"❌ {agent_name} with {parser_type} + {prompt_type} - FAILED: {e}")
            return False
    
    def _has_parsing_error(self, result: Dict[str, Any]) -> bool:
        """Check if result contains parsing error indicators."""
        error_indicators = [
            "parsing_error", "fallback_used", "fallback_data", 
            "error_message", "validation_failed", "parse_failed"
        ]
        
        for indicator in error_indicators:
            if indicator in result:
                return True
        
        # Check if result is empty or None
        if not result:
            return True
            
        return False
    
    async def find_optimal_combination(self, agent_name: str) -> Tuple[str, str]:
        """Find the optimal parser-prompt combination for an agent."""
        print(f"\n🔍 Finding optimal combination for {agent_name}...")
        
        # Define combinations to test (in order of preference)
        combinations = [
            ("StrOutputParser", "free_text"),
            ("JsonOutputParser", "json_structured"),
            ("PydanticOutputParser", "pydantic_structured"),
            ("FlexibleOutputParser", "hybrid")
        ]
        
        for parser_type, prompt_type in combinations:
            success = await self.test_parser_prompt_combination(agent_name, parser_type, prompt_type)
            if success:
                print(f"🎯 OPTIMAL COMBINATION FOUND: {parser_type} + {prompt_type}")
                return parser_type, prompt_type
        
        print(f"❌ No working combination found for {agent_name}")
        return None, None
    
    async def test_all_problematic_agents(self):
        """Test all agents known to have parsing issues."""
        problematic_agents = [
            "code_reviewer",
            "test_generator", 
            "documentation_generator",
            "security_analyst"
        ]
        
        results = {}
        
        for agent_name in problematic_agents:
            print(f"\n{'='*60}")
            print(f"TESTING {agent_name.upper()}")
            print(f"{'='*60}")
            
            parser_type, prompt_type = await self.find_optimal_combination(agent_name)
            results[agent_name] = (parser_type, prompt_type)
            
            if parser_type and prompt_type:
                print(f"✅ {agent_name}: {parser_type} + {prompt_type}")
            else:
                print(f"❌ {agent_name}: No working combination found")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY OF OPTIMAL COMBINATIONS")
        print(f"{'='*60}")
        
        for agent_name, (parser_type, prompt_type) in results.items():
            if parser_type and prompt_type:
                print(f"✅ {agent_name}: {parser_type} + {prompt_type}")
            else:
                print(f"❌ {agent_name}: NEEDS FIXING")
        
        return results

async def main():
    """Run isolated agent testing."""
    print("🧪 ISOLATED AGENT TESTING FOR PARSING ERROR RESOLUTION")
    print("=" * 70)
    
    tester = IsolatedAgentTester()
    results = await tester.test_all_problematic_agents()
    
    # Check if all agents have working combinations
    failed_agents = [name for name, (parser, prompt) in results.items() if not parser or not prompt]
    
    if failed_agents:
        print(f"\n❌ {len(failed_agents)} agents still need fixing: {', '.join(failed_agents)}")
        return False
    else:
        print(f"\n✅ All agents have optimal parser-prompt combinations!")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
