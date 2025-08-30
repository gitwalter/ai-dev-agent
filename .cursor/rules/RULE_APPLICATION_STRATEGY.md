# Cursor Rules Application Strategy

## Overview

This document defines the application strategy for the optimized Cursor rules system. Rules are categorized by application method to maximize effectiveness and minimize cognitive load.

## Rule Categories

### **ALWAYS APPLY Rules** (Critical Foundation)

These rules are automatically applied to every task and provide essential foundation practices:

#### Core Foundation Rules
- **Context Awareness Rule** - Read context before any work
- **File Organization Rule** - Maintain proper file structure  
- **Live Documentation Updates** - Keep docs current
- **No Silent Errors Rule** - Expose all errors
- **No Premature Victory Rule** - Verify before declaring success
- **Core Rule Application Framework** - Systematic rule application

#### Security & Infrastructure Rules
- **Streamlit Secrets Rule** - Use proper secrets management
- **Model Selection Rule** - Use correct AI models

### **INTELLIGENT APPLICATION Rules** (Context-Dependent)

These rules are applied based on task context and requirements:

#### Development Quality Rules
- **Boy Scout Rule** - Leave codebase cleaner than found
- **Courage Rule** - Complete complex tasks systematically
- **Test-Driven Development** - Write tests first for new features
- **Code Review Quality Gates** - Ensure code quality standards
- **Naming Conventions** - Follow strict naming standards
- **Type Signature Precision** - Use precise type signatures

#### Agile & Project Management Rules
- **Agile Development Rule** - Follow Agile Manifesto principles
- **Agile Artifacts Maintenance** - Keep agile artifacts current
- **Agile Sprint Management** - Manage sprints effectively
- **Agile User Story Management** - Handle user stories properly
- **Agile Daily Deployed Build** - Maintain daily deployable builds
- **Agile Manifesto Principles** - Apply Agile Manifesto principles
- **Continuous Self-Optimization** - Continuously improve processes
- **Automated User Story System** - Automate user story management
- **Automated User Story Status Updates** - Keep story status current

#### Quality & Testing Rules
- **Quality Validation Rule** - Validate quality before completion
- **Performance Monitoring** - Monitor and optimize performance
- **Error Handling** - Handle errors properly
- **Testing Test Monitoring** - Monitor test effectiveness
- **XP Test First Development** - Follow XP testing practices

#### Security Rules
- **Security Vulnerability Assessment** - Assess security vulnerabilities

### **MANUAL APPLICATION Rules** (User-Initiated)

These rules are applied only when explicitly requested:

#### Knowledge & Learning Rules
- **Active Knowledge Extension** - Extend knowledge actively

#### Infrastructure Rules
- **AI Model Selection** - Select appropriate AI models
- **Framework Standards** - Follow LangChain/LangGraph standards

#### Workflow Rules
- **Debugging Agent Flow Analysis** - Analyze agent flow for debugging

#### Meta Rules
- **Anti-Redundancy Elimination** - Eliminate redundant work
- **Continuous Improvement Systematic** - Systematically improve
- **Holistic Detailed Thinking** - Think holistically and in detail
- **Meta Rule Application Coordination** - Coordinate rule application
- **Meta Rule Enforcement** - Enforce meta rules
- **Step Back Analysis** - Step back for analysis

## Application Logic

### **Always Apply Logic**
```yaml
# These rules are applied to every task automatically
always_apply_rules:
  - context_awareness
  - file_organization
  - live_documentation
  - no_silent_errors
  - no_premature_victory
  - core_rule_framework
  - streamlit_secrets
  - model_selection
```

### **Intelligent Application Logic**
```yaml
# Rules applied based on task type
task_type_rules:
  code_development:
    - boy_scout_rule
    - courage_rule
    - test_driven_development
    - naming_conventions
    - type_signature_precision
  
  code_review:
    - code_review_quality_gates
    - quality_validation
  
  project_management:
    - agile_development
    - agile_artifacts
    - agile_sprint_management
    - agile_user_story_management
  
  testing:
    - xp_test_first
    - testing_monitoring
  
  security:
    - security_vulnerability_assessment
  
  performance:
    - performance_monitoring
```

### **Manual Application Logic**
```yaml
# Rules applied only when explicitly requested
manual_rules:
  knowledge_extension:
    - active_knowledge_extension
  
  infrastructure:
    - ai_model_selection
    - framework_standards
  
  debugging:
    - debugging_agent_flow
  
  meta_analysis:
    - anti_redundancy
    - continuous_improvement
    - holistic_thinking
    - meta_coordination
    - meta_enforcement
    - step_back_analysis
```

## Rule Priorities

### **Critical Priority (Fix Immediately)**
- Context Awareness Rule
- File Organization Rule
- Live Documentation Updates
- No Silent Errors Rule
- Streamlit Secrets Rule

### **High Priority (Fix This Week)**
- Boy Scout Rule
- Courage Rule
- Test-Driven Development
- Model Selection Rule
- Core Rule Application Framework

### **Medium Priority (Fix Next Week)**
- Agile Rules
- Security Rules
- Performance Rules
- Code Review Rules

### **Low Priority (Fix When Time Permits)**
- Meta Rules
- Knowledge Extension Rules
- Infrastructure Rules

## Success Metrics

### **Target Metrics**
- **Rule Application Success**: ≥95% successful rule applications
- **Task Completion Time**: Reduced by ≥20% with rule guidance
- **Code Quality**: Improved by ≥30% with quality rules
- **User Satisfaction**: ≥8/10 satisfaction with rule system

### **Monitoring Indicators**
- Reduced rule conflicts
- Faster task completion
- Improved code consistency
- Better project organization
- Enhanced documentation quality

## Implementation Notes

1. **Rule Conflicts**: If rules conflict, prioritize Always Apply rules over others
2. **Performance**: Monitor rule application performance and optimize as needed
3. **Feedback**: Collect user feedback on rule effectiveness and adjust accordingly
4. **Evolution**: Rules should evolve with project needs and team feedback

## Maintenance

- **Monthly Review**: Assess rule effectiveness and usage patterns
- **Quarterly Update**: Update rules based on project evolution
- **Annual Overhaul**: Major review and optimization of rule system

This strategy ensures that the most valuable rules are applied appropriately while maintaining system performance and user satisfaction.
