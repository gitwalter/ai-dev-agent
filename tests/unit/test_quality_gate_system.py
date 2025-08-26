"""
Tests for the quality gate system functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from models.state import AgentState
from workflow.workflow_graph import check_quality_gate, route_to_code_generator, determine_next_quality_gate


class TestQualityGateSystem:
    """Test cases for the quality gate system."""
    
    def test_check_quality_gate_passed(self):
        """Test quality gate check when it passes."""
        state = AgentState({
            "current_task": "code_review",
            "quality_gate_failed": False,
            "agent_outputs": {
                "code_review": {
                    "quality_gate_passed": True
                }
            }
        })
        
        result = check_quality_gate(state)
        assert result == "quality_gate_passed"
    
    def test_check_quality_gate_failed_state_flag(self):
        """Test quality gate check when state flag indicates failure."""
        state = AgentState({
            "current_task": "code_review",
            "quality_gate_failed": True
        })
        
        result = check_quality_gate(state)
        assert result == "quality_gate_failed"
    
    def test_check_quality_gate_failed_output(self):
        """Test quality gate check when agent output indicates failure."""
        state = AgentState({
            "current_task": "code_review",
            "quality_gate_failed": False,
            "agent_outputs": {
                "code_review": {
                    "quality_gate_passed": False
                }
            }
        })
        
        result = check_quality_gate(state)
        assert result == "quality_gate_failed"
    
    def test_route_to_code_generator(self):
        """Test routing to code generator."""
        state = AgentState({
            "current_task": "code_review"
        })
        
        result = route_to_code_generator(state)
        
        assert result["reroute_to"] == "code_generator"
        assert result["quality_gate_failed"] is True
    
    def test_determine_next_quality_gate_requirements(self):
        """Test determining next quality gate for requirements issues."""
        state = AgentState({
            "reroute_reason": "Missing requirements implementation"
        })
        
        result = determine_next_quality_gate(state)
        assert result == "code_review"
    
    def test_determine_next_quality_gate_security(self):
        """Test determining next quality gate for security issues."""
        state = AgentState({
            "reroute_reason": "Security quality gate failed"
        })
        
        result = determine_next_quality_gate(state)
        assert result == "security_analysis"
    
    def test_determine_next_quality_gate_default(self):
        """Test determining next quality gate with default routing."""
        state = AgentState({
            "reroute_reason": "General quality issue"
        })
        
        result = determine_next_quality_gate(state)
        assert result == "code_review"


class TestQualityGateIntegration:
    """Integration tests for quality gate system."""
    
    def test_quality_gate_workflow_flow(self):
        """Test the complete quality gate workflow flow."""
        # Test the flow: code_review -> quality_gate_failed -> route_to_code_generator -> code_review
        
        # Initial state after code review fails
        state = AgentState({
            "current_task": "code_review",
            "quality_gate_failed": True,
            "reroute_reason": "Missing requirements implementation"
        })
        
        # Check quality gate
        result = check_quality_gate(state)
        assert result == "quality_gate_failed"
        
        # Route to code generator
        state = route_to_code_generator(state)
        assert state["reroute_to"] == "code_generator"
        
        # Determine next quality gate
        next_gate = determine_next_quality_gate(state)
        assert next_gate == "code_review"
    
    def test_quality_gate_prompts_inclusion(self):
        """Test that quality gate functionality is included in prompts."""
        from prompts.agent_prompt_loader import get_agent_prompt_loader
        
        # Check code reviewer prompt
        code_reviewer_loader = get_agent_prompt_loader("code_reviewer")
        prompt = code_reviewer_loader.get_default_prompt()
        
        assert "QUALITY GATE RESPONSIBILITY" in prompt
        assert "quality_gate_passed" in prompt
        assert "Cross-check generated code against requirements" in prompt
        
        # Check security analyst prompt
        security_analyst_loader = get_agent_prompt_loader("security_analyst")
        prompt = security_analyst_loader.get_default_prompt()
        
        assert "QUALITY GATE RESPONSIBILITY" in prompt
        assert "quality_gate_passed" in prompt
        assert "No critical security vulnerabilities" in prompt
        
        # Check code generator prompt
        code_generator_loader = get_agent_prompt_loader("code_generator")
        prompt = code_generator_loader.get_default_prompt()
        
        assert "QUALITY GATE RESPONSIBILITY" in prompt
        assert "Address all missing requirements" in prompt
        assert "Fix all security issues" in prompt


class TestQualityGateAgentMethods:
    """Test quality gate methods from agents using mocks."""
    
    @patch('agents.code_reviewer.CodeReviewer')
    def test_code_reviewer_requirements_cross_check_structure(self, mock_code_reviewer):
        """Test code reviewer requirements cross-check prompt structure."""
        # Test the prompt structure without full initialization
        from agents.code_reviewer import CodeReviewer
        
        # Mock the class to avoid logging issues
        with patch.object(CodeReviewer, '__init__', return_value=None):
            reviewer = CodeReviewer(Mock(), Mock())
            
            # Test the prompt preparation method
            requirements = {"functional_requirements": [{"id": "FR1", "description": "User authentication"}]}
            code_files = {"main.py": "def authenticate_user(): pass"}
            
            prompt = reviewer._prepare_requirements_cross_check_prompt(requirements, code_files)
            
            assert "REQUIREMENTS:" in prompt
            assert "GENERATED CODE FILES:" in prompt
            assert "TASK:" in prompt
            assert "RESPONSE FORMAT" in prompt
            assert "all_requirements_met" in prompt
    
    @patch('agents.security_analyst.SecurityAnalyst')
    def test_security_analyst_quality_gate_logic(self, mock_security_analyst):
        """Test security analyst quality gate logic."""
        from agents.security_analyst import SecurityAnalyst
        
        # Mock the class to avoid logging issues
        with patch.object(SecurityAnalyst, '__init__', return_value=None):
            analyst = SecurityAnalyst(Mock(), Mock())
            
            # Test security data with no critical vulnerabilities
            security_data = {
                "overall_security_score": "8/10",
                "vulnerability_analysis": {
                    "critical_vulnerabilities": [],
                    "high_vulnerabilities": [{"description": "Minor issue"}]
                },
                "security_anti_patterns": []
            }
            
            result = analyst._perform_security_quality_gate(security_data)
            
            assert result["security_gate_passed"] is True
            assert len(result["critical_issues"]) == 0
            
            # Test with critical vulnerabilities
            security_data["vulnerability_analysis"]["critical_vulnerabilities"] = [
                {"description": "SQL injection", "location": "user_input.py"}
            ]
            
            result = analyst._perform_security_quality_gate(security_data)
            
            assert result["security_gate_passed"] is False
            assert len(result["critical_issues"]) > 0
    
    @patch('agents.code_generator.CodeGenerator')
    def test_code_generator_quality_gate_logic(self, mock_code_generator):
        """Test code generator quality gate logic."""
        from agents.code_generator import CodeGenerator
        
        # Mock the class to avoid logging issues
        with patch.object(CodeGenerator, '__init__', return_value=None):
            generator = CodeGenerator(Mock(), Mock())
            
            # Test with valid code data
            code_data = {
                "files": [
                    {
                        "filename": "main.py",
                        "content": "def main():\n    print('Hello World')\n    return True",
                        "language": "python"
                    }
                ]
            }
            
            state = AgentState({})
            
            result = generator._perform_internal_quality_gate(code_data, state)
            
            assert result["quality_gate_passed"] is True
            assert result["quality_score"] >= 7.0
            assert len(result["issues"]) == 0
            
            # Test with empty files
            code_data["files"][0]["content"] = ""
            
            result = generator._perform_internal_quality_gate(code_data, state)
            
            assert result["quality_gate_passed"] is False
            assert len(result["issues"]) > 0
