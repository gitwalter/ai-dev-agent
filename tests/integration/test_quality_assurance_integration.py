"""
Integration tests for Quality Assurance System.
Tests quality assurance integration with real agent outputs and workflow.
"""

import pytest
import asyncio
from typing import Dict, Any

from utils.quality.quality_assurance import quality_assurance, QualityGateResult
from models.state import AgentState
from models.config import AgentConfig


class TestQualityAssuranceIntegration:
    """Test quality assurance system integration with agents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset quality assurance system for clean tests
        quality_assurance.quality_metrics.clear()
        quality_assurance.validation_history.clear()
        quality_assurance.gate_results.clear()
    
    @pytest.mark.parametrize("agent_type,output_type,test_output", [
        ("requirements_analyst", "requirements", {
            "requirements": ["Functional requirement: User authentication", "Non-functional requirement: 99.9% uptime"],
            "summary": "Comprehensive requirements",
            "priorities": ["high", "medium"]
        }),
        ("architecture_designer", "architecture", {
            "components": ["API Gateway", "Database"],
            "technology_stack": {"backend": "Python", "database": "PostgreSQL"},
            "patterns": ["MVC", "Repository"]
        }),
        ("code_generator", "code", {
            "source_files": {"main.py": "def main(): pass"},
            "file_structure": ["main.py"],
            "dependencies": ["requests"]
        })
        # DELETED redundant similar test cases - consolidated into parameterized test
    ])
    def test_agent_quality_gates(self, agent_type, output_type, test_output):
        """Test quality gates for multiple agent types efficiently."""
        result = quality_assurance.validate_agent_output(agent_type, test_output, output_type)
        
        # Essential assertions that apply to all agents
        assert isinstance(result, QualityGateResult)
        assert result.agent_type == agent_type
        assert result.output_type == output_type
        assert isinstance(result.score, float)
        assert len(result.validations) > 0
        





    
    def test_quality_gate_failure_scenario(self):
        """Test quality gate failure scenario."""
        # Simulate poor quality output - missing required fields and multiple empty fields
        poor_output = {
            # Missing both required fields: functional_requirements, non_functional_requirements
            "summary": "",  # Empty summary
            "empty_field_1": "",  # Multiple empty fields to drive score down
            "empty_field_2": "",  
            "empty_field_3": "",
            "empty_field_4": "",
            "empty_field_5": ""  # Ensure score goes below 85.0 threshold
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "requirements_analyst", 
            poor_output, 
            "requirements"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "requirements_analyst_quality_gate"
        assert result.passed is False
        assert result.score <= quality_assurance.quality_thresholds["requirements_analyst"]
        
        # Check that some validations failed
        failed_validations = [v for v in result.validations if not v.passed]
        assert len(failed_validations) > 0
    
    def test_quality_metrics_tracking(self):
        """Test that quality metrics are properly tracked."""
        # Run multiple validations
        outputs = [
            {
                "requirements": ["req1", "req2"],
                "summary": "Test requirements"
            },
            {
                "source_files": {"main.py": "content"},
                "project_structure": "main.py"
            },
            {
                "overall_score": 8.0,
                "issues": ["issue1"],
                "recommendations": ["rec1"]
            }
        ]
        
        agents = ["requirements_analyst", "code_generator", "code_reviewer"]
        output_types = ["requirements", "code", "review"]
        
        # Run validations
        for i, (agent, output_type, output) in enumerate(zip(agents, output_types, outputs)):
            result = quality_assurance.validate_agent_output(agent, output, output_type)
            assert isinstance(result, QualityGateResult)
        
        # Check that metrics are tracked
        assert len(quality_assurance.gate_results) == 3
        assert len(quality_assurance.validation_history) > 0
        
        # Generate quality report
        report = quality_assurance.generate_quality_report()
        assert isinstance(report, dict)
        assert "summary" in report
        assert "agent_statistics" in report  # Correct key name
        assert "total_validations" in report  # Correct key name
        
        # Check agent performance
        agent_statistics = report["agent_statistics"]
        assert len(agent_statistics) > 0
        
        for agent_name, performance in agent_statistics.items():
            assert "average_score" in performance
            assert "pass_rate" in performance
            assert "scores" in performance
            assert "passed" in performance
    
    def test_validation_history_tracking(self):
        """Test that validation history is properly tracked."""
        # Run a validation
        output = {
            "requirements": ["req1", "req2", "req3"],
            "summary": "Test requirements"
        }
        
        result = quality_assurance.validate_agent_output(
            "requirements_analyst", 
            output, 
            "requirements"
        )
        
        # Check validation history
        history = quality_assurance.get_validation_history()
        assert len(history) > 0
        
        # Check specific validation types
        from utils.quality.quality_assurance import ValidationType
        structure_history = quality_assurance.get_validation_history(ValidationType.STRUCTURE)
        content_history = quality_assurance.get_validation_history(ValidationType.CONTENT)
        consistency_history = quality_assurance.get_validation_history(ValidationType.CONSISTENCY)
        completeness_history = quality_assurance.get_validation_history(ValidationType.COMPLETENESS)
        
        assert len(structure_history) > 0
        assert len(content_history) > 0
        assert len(consistency_history) > 0
        assert len(completeness_history) > 0
    
    def test_gate_results_tracking(self):
        """Test that gate results are properly tracked."""
        # Run multiple validations
        outputs = [
            {
                "requirements": ["req1", "req2"],
                "summary": "Test requirements"
            },
            {
                "source_files": {"main.py": "content"},
                "project_structure": "main.py"
            }
        ]
        
        agents = ["requirements_analyst", "code_generator"]
        output_types = ["requirements", "code"]
        
        # Run validations
        for agent, output_type, output in zip(agents, output_types, outputs):
            result = quality_assurance.validate_agent_output(agent, output, output_type)
            assert isinstance(result, QualityGateResult)
        
        # Check gate results
        all_results = quality_assurance.get_gate_results()
        assert len(all_results) == 2
        
        # Check specific agent results
        req_results = quality_assurance.get_gate_results("requirements_analyst")
        code_results = quality_assurance.get_gate_results("code_generator")
        
        assert len(req_results) == 1
        assert len(code_results) == 1
        
        assert req_results[0].gate_name == "requirements_analyst_quality_gate"
        assert code_results[0].gate_name == "code_generator_quality_gate"


if __name__ == "__main__":
    pytest.main([__file__])
