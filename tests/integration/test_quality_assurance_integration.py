"""
Integration tests for Quality Assurance System.
Tests quality assurance integration with real agent outputs and workflow.
"""

import pytest
import asyncio
from typing import Dict, Any

from utils.quality_assurance import quality_assurance, QualityGateResult
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
    
    def test_requirements_analyst_quality_gate(self):
        """Test quality gate for requirements analyst output."""
        # Simulate requirements analyst output
        requirements_output = {
            "requirements": [
                "Functional requirement: User authentication system",
                "Functional requirement: Data validation and sanitization",
                "Functional requirement: User profile management",
                "Non-functional requirement: Response time < 2 seconds",
                "Non-functional requirement: 99.9% uptime",
                "Non-functional requirement: Support for 1000 concurrent users"
            ],
            "summary": "Comprehensive web application requirements covering authentication, data management, and performance standards",
            "priorities": ["high", "high", "medium", "high", "high", "medium"]
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "requirements_analyst", 
            requirements_output, 
            "requirements"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "requirements_analyst_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["requirements_analyst"]
        assert len(result.validations) > 0
        
        # Check that all validations passed
        for validation in result.validations:
            assert validation.passed is True
    
    def test_architecture_designer_quality_gate(self):
        """Test quality gate for architecture designer output."""
        # Simulate architecture designer output
        architecture_output = {
            "architecture": "Microservices architecture with API Gateway pattern",
            "components": [
                "API Gateway",
                "Authentication Service",
                "User Service",
                "Data Service",
                "Notification Service"
            ],
            "diagrams": {
                "system_overview": "System architecture diagram showing service interactions",
                "data_flow": "Data flow diagram showing information flow between services"
            },
            "decisions": [
                "Use microservices for scalability and maintainability",
                "Implement API Gateway for centralized routing and security",
                "Use event-driven architecture for loose coupling"
            ]
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "architecture_designer", 
            architecture_output, 
            "architecture"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "architecture_designer_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["architecture_designer"]
    
    def test_code_generator_quality_gate(self):
        """Test quality gate for code generator output."""
        # Simulate code generator output
        code_output = {
            "source_files": {
                "main.py": "from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef hello(): return 'Hello World'\nif __name__ == '__main__': app.run()",
                "requirements.txt": "flask==2.0.0\npytest==6.2.5",
                "app/__init__.py": "from flask import Flask\ndef create_app():\n    app = Flask(__name__)\n    return app",
                "app/routes.py": "from flask import Blueprint\napi = Blueprint('api', __name__)\n@api.route('/api/health')\ndef health(): return {'status': 'ok'}"
            },
            "project_structure": "main.py, requirements.txt, app/__init__.py, app/routes.py",
            "dependencies": ["flask", "pytest"]
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "code_generator", 
            code_output, 
            "code"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "code_generator_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["code_generator"]
    
    def test_test_generator_quality_gate(self):
        """Test quality gate for test generator output."""
        # Simulate test generator output
        test_output = {
            "test_files": {
                "test_main.py": "import pytest\nfrom main import app\ndef test_hello():\n    with app.test_client() as client:\n        response = client.get('/')\n        assert response.status_code == 200",
                "test_api.py": "import pytest\nfrom app.routes import api\ndef test_health():\n    with api.test_client() as client:\n        response = client.get('/api/health')\n        assert response.status_code == 200"
            },
            "test_strategy": {
                "unit_tests": "pytest for unit testing",
                "integration_tests": "API endpoint testing",
                "test_data": "Sample test fixtures and data"
            },
            "test_data": {
                "sample_user": {"id": 1, "name": "Test User", "email": "test@example.com"}
            }
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "test_generator", 
            test_output, 
            "tests"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "test_generator_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["test_generator"]
    
    def test_code_reviewer_quality_gate(self):
        """Test quality gate for code reviewer output."""
        # Simulate code reviewer output
        review_output = {
            "overall_score": 8.5,
            "issues": [
                {
                    "title": "Missing error handling",
                    "severity": "medium",
                    "description": "API endpoints should include proper error handling"
                },
                {
                    "title": "Incomplete documentation",
                    "severity": "low",
                    "description": "Functions should have docstrings"
                }
            ],
            "recommendations": [
                "Add try-catch blocks for database operations",
                "Add input validation for API endpoints",
                "Include docstrings for all functions"
            ],
            "summary": "Good code quality with room for improvement in error handling and documentation"
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "code_reviewer", 
            review_output, 
            "review"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "code_reviewer_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["code_reviewer"]
    
    def test_security_analyst_quality_gate(self):
        """Test quality gate for security analyst output."""
        # Simulate security analyst output
        security_output = {
            "security_score": 8.0,
            "vulnerabilities": [
                {
                    "title": "SQL Injection Risk",
                    "severity": "high",
                    "description": "Direct string concatenation in database queries",
                    "recommendation": "Use parameterized queries"
                },
                {
                    "title": "Missing Input Validation",
                    "severity": "medium",
                    "description": "API endpoints lack input validation",
                    "recommendation": "Add input validation middleware"
                }
            ],
            "recommendations": [
                "Implement parameterized queries for all database operations",
                "Add input validation for all API endpoints",
                "Enable HTTPS in production",
                "Implement rate limiting"
            ],
            "summary": "Security analysis identifies several vulnerabilities that should be addressed before deployment"
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "security_analyst", 
            security_output, 
            "security"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "security_analyst_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["security_analyst"]
    
    def test_documentation_generator_quality_gate(self):
        """Test quality gate for documentation generator output."""
        # Simulate documentation generator output
        documentation_output = {
            "documentation_files": {
                "README.md": "# Project Name\n\nA comprehensive web application with authentication and data management.\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython main.py\n```",
                "API_DOCS.md": "# API Documentation\n\n## Endpoints\n\n### GET /\nReturns a greeting message.\n\n### GET /api/health\nReturns system health status."
            },
            "readme": "# Project Name\n\nA comprehensive web application with authentication and data management.\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython main.py\n```",
            "api_docs": "# API Documentation\n\n## Endpoints\n\n### GET /\nReturns a greeting message.\n\n### GET /api/health\nReturns system health status.",
            "setup_instructions": [
                "1. Clone the repository",
                "2. Install dependencies: pip install -r requirements.txt",
                "3. Set environment variables",
                "4. Run the application: python main.py"
            ]
        }
        
        # Validate the output
        result = quality_assurance.validate_agent_output(
            "documentation_generator", 
            documentation_output, 
            "documentation"
        )
        
        # Assertions
        assert isinstance(result, QualityGateResult)
        assert result.gate_name == "documentation_generator_quality_gate"
        assert result.passed is True
        assert result.score >= quality_assurance.quality_thresholds["documentation_generator"]
    
    def test_quality_gate_failure_scenario(self):
        """Test quality gate failure scenario."""
        # Simulate poor quality output
        poor_output = {
            "requirements": [],  # Empty requirements
            "summary": ""  # Empty summary
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
        assert result.score < quality_assurance.quality_thresholds["requirements_analyst"]
        
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
        assert "agent_performance" in report
        assert "validation_breakdown" in report
        
        # Check agent performance
        agent_performance = report["agent_performance"]
        assert len(agent_performance) > 0
        
        for agent_name, performance in agent_performance.items():
            assert "average_score" in performance
            assert "gates_passed" in performance
            assert "total_gates" in performance
            assert "success_rate" in performance
    
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
        structure_history = quality_assurance.get_validation_history("structure")
        content_history = quality_assurance.get_validation_history("content")
        consistency_history = quality_assurance.get_validation_history("consistency")
        completeness_history = quality_assurance.get_validation_history("completeness")
        
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
