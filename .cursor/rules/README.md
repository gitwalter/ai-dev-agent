# Cursor Project Rules - Optimized and Standardized

This directory contains all cursor project rules that have been optimized for better usage and standardized naming conventions.

## Rule Categories and Standards

All rules follow the standardized naming convention: `category_action_rule.mdc`

### Metadata Structure
Each rule includes standardized metadata:
```yaml
---
description: "Clear, specific description of the rule's purpose and scope"
category: "Primary category (testing, security, project-management, etc.)"
priority: "critical, high, medium, low"
alwaysApply: "true/false"
globs: ["file patterns this rule applies to"]
tags: ["relevant tags for categorization"]
---
```

## Rule Inventory

### AI and Model Management
- **ai_model_selection_rule.mdc** - Standardized LLM model selection strategy using Gemini models
- **prompt_prompt_database_management_rule.mdc** - Database-first prompt management system

### Development and Configuration
- **development_streamlit_startup_rule.mdc** - Standardized Streamlit application startup procedure
- **security_streamlit_secrets_rule.mdc** - Mandatory use of Streamlit st.secrets for API keys

### Testing and Quality Assurance
- **testing_test_monitoring_rule.mdc** - Automated test monitoring with immediate error detection
- **testing_test_organization_rule.mdc** - Comprehensive test organization and structure standards
- **testing_test_isolation_rule.mdc** - Isolated testing procedures for component isolation
- **testing_isolated_agent_testing_rule.mdc** - Systematic isolated agent testing with parsing error resolution
- **testing_no_failing_tests_rule.mdc** - Zero-tolerance policy for failing tests

### Debugging and Analysis
- **debugging_agent_flow_analysis_rule.mdc** - Agent workflow debugging using logs/agent.log as primary source

### Error Handling and Reliability
- **error_handling_no_silent_errors_rule.mdc** - Zero-tolerance policy for silent error handling and fallbacks

### Project Management
- **project_implementation_roadmap_rule.mdc** - Enforces adherence to comprehensive development plans
- **project_tasklist_management_rule.mdc** - Comprehensive tasklist management system
- **project_file_organization_rule.mdc** - File organization and structure standards
- **project_requirements_management_rule.mdc** - Requirements management and tracking

### Documentation
- **documentation_maintenance.mdc** - Comprehensive documentation maintenance system

### Framework Standards
- **framework_langchain_langgraph_standards_rule.mdc** - LangChain and LangGraph implementation standards

### Naming Standards
- **naming_standards_rule.mdc** - Comprehensive naming standards enforcement for all project elements

## Rule Priority Levels

### Critical Priority (Always Applied)
- **naming_standards_rule.mdc** - Ensures consistency across entire project
- **error_handling_no_silent_errors_rule.mdc** - Prevents hidden failures
- **testing_no_failing_tests_rule.mdc** - Maintains code quality
- **prompt_prompt_database_management_rule.mdc** - Centralized prompt management
- **security_streamlit_secrets_rule.mdc** - Security best practices

### High Priority (Applied to Relevant Files)
- **testing_test_monitoring_rule.mdc** - Test quality assurance
- **testing_test_organization_rule.mdc** - Test maintainability
- **project_implementation_roadmap_rule.mdc** - Project consistency
- **documentation_maintenance.mdc** - Documentation accuracy
- **ai_model_selection_rule.mdc** - AI configuration consistency

### Medium Priority (Applied When Relevant)
- **development_streamlit_startup_rule.mdc** - Development workflow
- **project_tasklist_management_rule.mdc** - Project tracking
- **project_file_organization_rule.mdc** - File organization
- **framework_langchain_langgraph_standards_rule.mdc** - Framework usage

### Low Priority (Applied on Demand)
- **debugging_agent_flow_analysis_rule.mdc** - Debugging assistance
- **testing_test_isolation_rule.mdc** - Specific testing scenarios
- **testing_isolated_agent_testing_rule.mdc** - Agent-specific testing
- **project_requirements_management_rule.mdc** - Requirements tracking

## Usage Guidelines

### For New Rules
1. Follow the naming convention: `category_action_rule.mdc`
2. Include complete metadata with description, category, priority, and globs
3. Use clear, specific descriptions
4. Apply appropriate tags for categorization
5. Set `alwaysApply` based on rule importance

### For Rule Updates
1. Maintain consistent metadata structure
2. Update descriptions to be specific and actionable
3. Ensure globs patterns are comprehensive
4. Review and update priority levels as needed
5. Validate rule effectiveness and clarity

### For Rule Application
1. Critical rules are always applied
2. High priority rules apply to relevant file patterns
3. Medium priority rules apply when context is relevant
4. Low priority rules apply on demand or specific scenarios

## Benefits of Standardization

- **Consistency**: Uniform naming and metadata across all rules
- **Clarity**: Clear descriptions and categorization
- **Maintainability**: Easy to understand and update rules
- **Efficiency**: Better rule application and enforcement
- **Collaboration**: Clear understanding for all team members
- **Scalability**: Easy to add new rules following established patterns

## Rule Validation

All rules should be validated for:
- [ ] Consistent naming convention
- [ ] Complete metadata structure
- [ ] Clear and specific descriptions
- [ ] Appropriate category and priority
- [ ] Comprehensive glob patterns
- [ ] Relevant tags
- [ ] Actionable content
- [ ] Proper formatting and structure

## Maintenance Schedule

- **Weekly**: Review rule effectiveness and usage
- **Monthly**: Update descriptions and metadata as needed
- **Quarterly**: Comprehensive rule review and optimization
- **As Needed**: Immediate updates for critical issues or new requirements
