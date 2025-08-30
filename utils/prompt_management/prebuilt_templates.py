"""
Pre-built Prompt Templates
==========================

A comprehensive collection of well-designed prompt templates for testing
and demonstrating the prompt engineering system capabilities.

These templates cover various use cases and can be used immediately for
testing optimization, analytics, and template management features.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

from typing import Dict, List, Any
from utils.prompt_management.prompt_template_system import TemplateType, TemplateStatus


class PrebuiltTemplates:
    """Collection of pre-built prompt templates for testing."""
    
    @staticmethod
    def get_all_templates() -> List[Dict[str, Any]]:
        """Get all pre-built templates."""
        all_templates = []
        
        # Add all template categories
        all_templates.extend(PrebuiltTemplates.get_code_generation_templates())
        all_templates.extend(PrebuiltTemplates.get_code_review_templates())
        all_templates.extend(PrebuiltTemplates.get_documentation_templates())
        all_templates.extend(PrebuiltTemplates.get_testing_templates())
        all_templates.extend(PrebuiltTemplates.get_debugging_templates())
        all_templates.extend(PrebuiltTemplates.get_architecture_templates())
        all_templates.extend(PrebuiltTemplates.get_analysis_templates())
        all_templates.extend(PrebuiltTemplates.get_optimization_templates())
        
        return all_templates
    
    @staticmethod
    def get_code_generation_templates() -> List[Dict[str, Any]]:
        """Get code generation templates."""
        return [
            {
                "name": "Python Function Generator",
                "description": "Generate clean, well-documented Python functions with type hints",
                "template_type": TemplateType.SIMPLE,
                "agent_type": "code_generator",
                "template_text": """You are an expert Python developer. Generate a clean, well-documented function for the following task:

Task: {task}

Requirements:
- Use type hints
- Include docstring with parameters and return value
- Follow PEP 8 style guidelines
- Handle edge cases appropriately
- Include error handling where necessary

Please provide only the function code without explanations.""",
                "author": "system",
                "tags": ["python", "function", "generation", "type-hints"]
            },
            {
                "name": "JavaScript Class Generator",
                "description": "Generate modern JavaScript classes with ES6+ features",
                "template_type": TemplateType.ENHANCED,
                "agent_type": "code_generator",
                "template_text": """You are an expert JavaScript developer. Create a modern JavaScript class for the following requirements:

Requirements: {requirements}

Guidelines:
- Use ES6+ class syntax
- Include proper constructor
- Add getter/setter methods where appropriate
- Use JSDoc comments for documentation
- Follow modern JavaScript best practices
- Include error handling
- Make the class reusable and extensible

Please provide only the class code with JSDoc comments.""",
                "author": "system",
                "tags": ["javascript", "class", "es6", "modern"]
            },
            {
                "name": "SQL Query Generator",
                "description": "Generate optimized SQL queries for database operations",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "code_generator",
                "template_text": """You are a database expert. Generate an optimized SQL query for the following scenario:

Database Schema: {schema}
Requirements: {requirements}

Guidelines:
- Use appropriate JOINs for performance
- Include proper indexing considerations
- Add WHERE clauses for filtering
- Use appropriate aggregate functions
- Consider query optimization
- Include comments explaining the logic

Please provide the SQL query with explanatory comments.""",
                "author": "system",
                "tags": ["sql", "database", "query", "optimization"]
            }
        ]
    
    @staticmethod
    def get_code_review_templates() -> List[Dict[str, Any]]:
        """Get code review templates."""
        return [
            {
                "name": "Python Code Review",
                "description": "Comprehensive Python code review with best practices",
                "template_type": TemplateType.ENHANCED,
                "agent_type": "code_reviewer",
                "template_text": """You are a senior Python developer conducting a code review. Analyze the following code:

Code to Review:
{code}

Review Criteria:
1. **Code Quality**: PEP 8 compliance, naming conventions, structure
2. **Performance**: Efficiency, algorithms, memory usage
3. **Security**: Potential vulnerabilities, input validation
4. **Maintainability**: Readability, documentation, modularity
5. **Testing**: Test coverage, edge cases
6. **Best Practices**: Python idioms, design patterns

Please provide a structured review with:
- Overall assessment (1-10 scale)
- Critical issues (if any)
- Suggestions for improvement
- Positive aspects
- Specific recommendations""",
                "author": "system",
                "tags": ["python", "review", "quality", "best-practices"]
            },
            {
                "name": "Security Code Review",
                "description": "Security-focused code review for vulnerabilities",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "code_reviewer",
                "template_text": """You are a security expert conducting a security code review. Analyze the following code for vulnerabilities:

Code to Review:
{code}

Security Focus Areas:
1. **Input Validation**: SQL injection, XSS, injection attacks
2. **Authentication**: Session management, access control
3. **Data Protection**: Encryption, sensitive data handling
4. **Error Handling**: Information disclosure
5. **Dependencies**: Known vulnerabilities in libraries
6. **Configuration**: Secure defaults, environment variables

Please provide:
- Security risk assessment (Low/Medium/High/Critical)
- Identified vulnerabilities
- Exploitation scenarios
- Remediation recommendations
- Security best practices to follow""",
                "author": "system",
                "tags": ["security", "vulnerabilities", "review", "protection"]
            }
        ]
    
    @staticmethod
    def get_documentation_templates() -> List[Dict[str, Any]]:
        """Get documentation templates."""
        return [
            {
                "name": "API Documentation Generator",
                "description": "Generate comprehensive API documentation",
                "template_type": TemplateType.ENHANCED,
                "agent_type": "documentation_writer",
                "template_text": """You are a technical writer specializing in API documentation. Create comprehensive documentation for the following API:

API Details:
{api_details}

Documentation Requirements:
1. **Overview**: Purpose and functionality
2. **Authentication**: How to authenticate
3. **Endpoints**: Complete endpoint documentation
4. **Request/Response Examples**: Real examples
5. **Error Codes**: All possible error responses
6. **Rate Limiting**: Usage limits and policies
7. **SDK Examples**: Code examples in multiple languages

Please provide well-structured, clear documentation that developers can easily follow.""",
                "author": "system",
                "tags": ["api", "documentation", "technical-writing"]
            },
            {
                "name": "README Generator",
                "description": "Generate professional README files for projects",
                "template_type": TemplateType.SIMPLE,
                "agent_type": "documentation_writer",
                "template_text": """You are a technical writer creating a README file. Generate a comprehensive README for the following project:

Project Information:
{project_info}

README Sections to Include:
1. **Project Title and Description**
2. **Features and Benefits**
3. **Installation Instructions**
4. **Usage Examples**
5. **Configuration Options**
6. **API Reference** (if applicable)
7. **Contributing Guidelines**
8. **License Information**
9. **Support and Contact**

Please create a professional, well-structured README that follows best practices.""",
                "author": "system",
                "tags": ["readme", "documentation", "project"]
            }
        ]
    
    @staticmethod
    def get_testing_templates() -> List[Dict[str, Any]]:
        """Get testing templates."""
        return [
            {
                "name": "Unit Test Generator",
                "description": "Generate comprehensive unit tests for functions and classes",
                "template_type": TemplateType.ENHANCED,
                "agent_type": "test_generator",
                "template_text": """You are a testing expert. Generate comprehensive unit tests for the following code:

Code to Test:
{code}

Testing Requirements:
1. **Test Coverage**: Aim for 90%+ coverage
2. **Edge Cases**: Test boundary conditions
3. **Error Scenarios**: Test error handling
4. **Mocking**: Use appropriate mocks for dependencies
5. **Assertions**: Clear, meaningful assertions
6. **Test Organization**: Well-structured test classes/methods
7. **Documentation**: Clear test descriptions

Please provide:
- Complete test suite
- Setup and teardown methods
- Mock configurations
- Test data examples
- Coverage considerations""",
                "author": "system",
                "tags": ["testing", "unit-tests", "coverage", "mocking"]
            },
            {
                "name": "Integration Test Generator",
                "description": "Generate integration tests for system components",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "test_generator",
                "template_text": """You are a testing expert specializing in integration testing. Create integration tests for the following system:

System Components:
{components}

Integration Testing Focus:
1. **Component Interaction**: Test how components work together
2. **Data Flow**: Test data passing between components
3. **Error Propagation**: Test error handling across components
4. **Performance**: Test system performance under load
5. **End-to-End Scenarios**: Test complete user workflows
6. **Database Integration**: Test database operations
7. **External Services**: Test third-party service integration

Please provide:
- Integration test scenarios
- Test data setup
- Mock external dependencies
- Performance test cases
- Error scenario tests""",
                "author": "system",
                "tags": ["integration", "testing", "system", "workflow"]
            }
        ]
    
    @staticmethod
    def get_debugging_templates() -> List[Dict[str, Any]]:
        """Get debugging templates."""
        return [
            {
                "name": "Error Analysis Assistant",
                "description": "Analyze and debug error messages and stack traces",
                "template_type": TemplateType.ENHANCED,
                "agent_type": "debugger",
                "template_text": """You are a debugging expert. Analyze the following error and provide a solution:

Error Information:
{error_details}

Analysis Requirements:
1. **Root Cause**: Identify the underlying cause
2. **Error Context**: Understand the execution context
3. **Code Review**: Review related code for issues
4. **Solution Options**: Provide multiple solution approaches
5. **Prevention**: Suggest ways to prevent similar errors
6. **Testing**: Recommend tests to catch this issue
7. **Documentation**: Update documentation if needed

Please provide:
- Detailed error analysis
- Step-by-step debugging process
- Recommended solutions
- Code examples
- Prevention strategies""",
                "author": "system",
                "tags": ["debugging", "error-analysis", "troubleshooting"]
            },
            {
                "name": "Performance Debugger",
                "description": "Analyze and optimize performance issues",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "debugger",
                "template_text": """You are a performance optimization expert. Analyze the following performance issue:

Performance Problem:
{performance_issue}

Analysis Areas:
1. **Bottleneck Identification**: Find performance bottlenecks
2. **Algorithm Analysis**: Review algorithm efficiency
3. **Memory Usage**: Analyze memory consumption patterns
4. **Database Queries**: Optimize database operations
5. **Caching Strategy**: Implement appropriate caching
6. **Resource Utilization**: Monitor CPU, memory, I/O
7. **Profiling**: Suggest profiling tools and techniques

Please provide:
- Performance analysis report
- Bottleneck identification
- Optimization recommendations
- Code improvements
- Monitoring suggestions""",
                "author": "system",
                "tags": ["performance", "optimization", "profiling", "bottlenecks"]
            }
        ]
    
    @staticmethod
    def get_architecture_templates() -> List[Dict[str, Any]]:
        """Get architecture templates."""
        return [
            {
                "name": "System Architecture Designer",
                "description": "Design scalable system architectures",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "architect",
                "template_text": """You are a senior software architect. Design a system architecture for the following requirements:

System Requirements:
{requirements}

Architecture Considerations:
1. **Scalability**: Handle growth and load
2. **Reliability**: High availability and fault tolerance
3. **Security**: Data protection and access control
4. **Performance**: Response time and throughput
5. **Maintainability**: Code organization and deployment
6. **Technology Stack**: Appropriate technologies
7. **Integration**: Third-party services and APIs

Please provide:
- High-level architecture diagram
- Component breakdown
- Technology recommendations
- Scalability strategy
- Security considerations
- Deployment approach""",
                "author": "system",
                "tags": ["architecture", "design", "scalability", "system"]
            },
            {
                "name": "Microservices Architect",
                "description": "Design microservices architecture patterns",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "architect",
                "template_text": """You are a microservices architecture expert. Design a microservices solution for the following system:

System Overview:
{system_overview}

Microservices Design:
1. **Service Decomposition**: Break down into services
2. **Service Boundaries**: Define clear service boundaries
3. **Communication**: Inter-service communication patterns
4. **Data Management**: Data consistency and storage
5. **API Design**: RESTful or GraphQL APIs
6. **Deployment**: Containerization and orchestration
7. **Monitoring**: Observability and logging

Please provide:
- Service decomposition
- API specifications
- Data flow diagrams
- Deployment strategy
- Monitoring approach
- Best practices recommendations""",
                "author": "system",
                "tags": ["microservices", "architecture", "decomposition", "api"]
            }
        ]
    
    @staticmethod
    def get_analysis_templates() -> List[Dict[str, Any]]:
        """Get analysis templates."""
        return [
            {
                "name": "Code Complexity Analyzer",
                "description": "Analyze code complexity and maintainability",
                "template_type": TemplateType.ENHANCED,
                "agent_type": "analyzer",
                "template_text": """You are a code quality analyst. Analyze the complexity and maintainability of the following code:

Code to Analyze:
{code}

Analysis Metrics:
1. **Cyclomatic Complexity**: Measure code complexity
2. **Code Duplication**: Identify repeated code patterns
3. **Function Length**: Analyze function size and structure
4. **Naming Conventions**: Review naming quality
5. **Documentation**: Assess code documentation
6. **Test Coverage**: Evaluate testing completeness
7. **Technical Debt**: Identify areas for improvement

Please provide:
- Complexity analysis report
- Maintainability score
- Refactoring recommendations
- Quality improvement suggestions
- Technical debt assessment""",
                "author": "system",
                "tags": ["analysis", "complexity", "maintainability", "quality"]
            },
            {
                "name": "Dependency Analyzer",
                "description": "Analyze project dependencies and security",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "analyzer",
                "template_text": """You are a dependency analysis expert. Analyze the dependencies of the following project:

Project Dependencies:
{dependencies}

Analysis Focus:
1. **Security Vulnerabilities**: Check for known vulnerabilities
2. **Version Compatibility**: Ensure compatible versions
3. **License Compliance**: Review license requirements
4. **Dependency Health**: Assess maintenance status
5. **Size Impact**: Analyze bundle size impact
6. **Update Strategy**: Plan dependency updates
7. **Alternative Options**: Suggest better alternatives

Please provide:
- Security vulnerability report
- Dependency health assessment
- Update recommendations
- License compliance summary
- Optimization suggestions""",
                "author": "system",
                "tags": ["dependencies", "security", "vulnerabilities", "licenses"]
            }
        ]
    
    @staticmethod
    def get_optimization_templates() -> List[Dict[str, Any]]:
        """Get optimization templates."""
        return [
            {
                "name": "Code Optimizer",
                "description": "Optimize code for performance and efficiency",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "optimizer",
                "template_text": """You are a code optimization expert. Optimize the following code for better performance:

Code to Optimize:
{code}

Optimization Areas:
1. **Algorithm Efficiency**: Improve algorithm complexity
2. **Memory Usage**: Reduce memory consumption
3. **CPU Utilization**: Optimize CPU-intensive operations
4. **I/O Operations**: Minimize I/O overhead
5. **Caching**: Implement appropriate caching
6. **Parallelization**: Use parallel processing where possible
7. **Code Structure**: Improve code organization

Please provide:
- Performance analysis
- Optimization recommendations
- Optimized code examples
- Performance benchmarks
- Implementation guidelines""",
                "author": "system",
                "tags": ["optimization", "performance", "efficiency", "algorithms"]
            },
            {
                "name": "Database Query Optimizer",
                "description": "Optimize database queries for better performance",
                "template_type": TemplateType.SPECIALIZED,
                "agent_type": "optimizer",
                "template_text": """You are a database optimization expert. Optimize the following database query:

Query to Optimize:
{query}

Database Context:
{context}

Optimization Focus:
1. **Query Structure**: Improve query logic
2. **Indexing**: Suggest appropriate indexes
3. **JOIN Optimization**: Optimize table joins
4. **Filtering**: Improve WHERE clauses
5. **Aggregation**: Optimize GROUP BY operations
6. **Subqueries**: Convert to more efficient alternatives
7. **Execution Plan**: Analyze query execution

Please provide:
- Query analysis
- Optimization recommendations
- Optimized query examples
- Index suggestions
- Performance improvements""",
                "author": "system",
                "tags": ["database", "query-optimization", "indexing", "performance"]
            }
        ]


def load_prebuilt_templates(template_system) -> List[str]:
    """
    Load all pre-built templates into the template system.
    
    Args:
        template_system: The PromptTemplateSystem instance
        
    Returns:
        List of created template IDs
    """
    created_ids = []
    
    for template_data in PrebuiltTemplates.get_all_templates():
        try:
            template_id = template_system.create_template(
                name=template_data["name"],
                description=template_data["description"],
                template_type=template_data["template_type"],
                agent_type=template_data["agent_type"],
                template_text=template_data["template_text"],
                author=template_data["author"],
                tags=template_data["tags"]
            )
            created_ids.append(template_id)
            print(f"✅ Created template: {template_data['name']} (ID: {template_id})")
        except Exception as e:
            print(f"❌ Failed to create template {template_data['name']}: {e}")
    
    return created_ids


if __name__ == "__main__":
    """Test the pre-built templates."""
    from utils.prompt_management.prompt_template_system import PromptTemplateSystem
    
    # Initialize template system
    template_system = PromptTemplateSystem()
    
    # Load all pre-built templates
    print("🚀 Loading pre-built templates...")
    created_ids = load_prebuilt_templates(template_system)
    
    print(f"\n📊 Summary:")
    print(f"✅ Successfully created {len(created_ids)} templates")
    print(f"📝 Template IDs: {created_ids}")
    
    # List all templates
    all_templates = template_system.get_all_templates()
    print(f"\n📋 All templates in system: {len(all_templates)}")
    for template in all_templates:
        print(f"  - {template.name} ({template.template_id})")
