# Rule Organization Structure - Situation & Task Specific

**CRITICAL**: This document defines the hierarchical organization of all rules by **situations** and **tasks** to enable effective rule discovery and application in any specific context.

## Overview

Our rule system is organized by **situations** (when rules apply) and **tasks** (what rules govern) rather than generic categories. This ensures that the right rules are found and applied based on the specific context and activity being performed.

## Rule Hierarchy - Situation & Task Based

```
┌─────────────────────────────────────────────────────────────┐
│                    META-RULES (GOVERNANCE)                  │
├─────────────────────────────────────────────────────────────┤
│  • Rule Discovery and Application                          │
│  • Rule Priority and Conflict Resolution                   │
│  • Rule Compliance Monitoring                              │
│  • Rule Effectiveness Evaluation                           │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              SITUATION-SPECIFIC RULES                      │
├─────────────────────────────────────────────────────────────┤
│  • Code Development Situations                             │
│  • Testing Situations                                      │
│  • Documentation Situations                                │
│  • Deployment Situations                                   │
│  • Maintenance Situations                                  │
│  • Problem-Solving Situations                              │
│  • Quality Assurance Situations                            │
│  • Security Situations                                     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                TASK-SPECIFIC RULES                         │
├─────────────────────────────────────────────────────────────┤
│  • Writing Code Tasks                                      │
│  • Reviewing Code Tasks                                    │
│  • Testing Tasks                                           │
│  • Documenting Tasks                                       │
│  • Deploying Tasks                                         │
│  • Debugging Tasks                                         │
│  • Refactoring Tasks                                       │
│  • Security Assessment Tasks                               │
└─────────────────────────────────────────────────────────────┘
```

## 1. META-RULES (GOVERNANCE LAYER)

### **Core Meta-Rules**

#### **M1: Situation-Based Rule Discovery Meta-Rule**
**Purpose**: Governs how to find and apply relevant rules based on specific situations
**File**: `meta_rule_situation_discovery.mdc`

```python
class SituationBasedRuleDiscovery:
    """Meta-rule for discovering rules based on specific situations."""
    
    def discover_rules_for_situation(self, situation: dict) -> List[Rule]:
        """Find all rules applicable to the current situation."""
        
        # Analyze situation characteristics
        situation_analysis = self._analyze_situation(situation)
        
        # Identify applicable rules by situation type
        applicable_rules = []
        
        # Situation-specific rule matching
        if situation_analysis.is_code_development:
            applicable_rules.extend(self._get_code_development_rules(situation_analysis))
        
        if situation_analysis.is_testing:
            applicable_rules.extend(self._get_testing_rules(situation_analysis))
        
        if situation_analysis.is_documentation:
            applicable_rules.extend(self._get_documentation_rules(situation_analysis))
        
        if situation_analysis.is_deployment:
            applicable_rules.extend(self._get_deployment_rules(situation_analysis))
        
        # Task-specific rule matching
        if situation_analysis.current_task:
            applicable_rules.extend(self._get_task_specific_rules(situation_analysis.current_task))
        
        # Sort by priority and relevance
        applicable_rules.sort(key=lambda r: (r.priority_score, r.relevance_score), reverse=True)
        
        return applicable_rules
    
    def _analyze_situation(self, situation: dict) -> SituationAnalysis:
        """Analyze situation to identify relevant characteristics."""
        
        analysis = SituationAnalysis()
        
        # Identify situation type
        analysis.situation_type = self._identify_situation_type(situation)
        
        # Identify current task
        analysis.current_task = self._identify_current_task(situation)
        
        # Identify file types involved
        analysis.file_types = self._identify_file_types(situation)
        
        # Identify process context
        analysis.process_context = self._identify_process_context(situation)
        
        # Identify quality requirements
        analysis.quality_requirements = self._identify_quality_requirements(situation)
        
        # Identify security considerations
        analysis.security_considerations = self._identify_security_considerations(situation)
        
        return analysis
```

## 2. SITUATION-SPECIFIC RULES

### **Code Development Situations**

#### **S1: New Feature Development**
**Purpose**: Rules for developing new features
**Directory**: `situations/code_development/new_feature/`

```
situations/code_development/new_feature/
├── test_first_development.mdc        # XP test-first development
├── code_quality_standards.mdc        # Code quality requirements
├── naming_conventions.mdc            # Naming standards
├── error_handling.mdc                # Error handling patterns
├── documentation_requirements.mdc    # Documentation needs
└── security_considerations.mdc       # Security requirements
```

#### **S2: Bug Fix Development**
**Purpose**: Rules for fixing bugs
**Directory**: `situations/code_development/bug_fix/`

```
situations/code_development/bug_fix/
├── root_cause_analysis.mdc           # Root cause analysis
├── regression_testing.mdc            # Regression testing
├── minimal_change_principle.mdc      # Minimal change approach
├── documentation_updates.mdc         # Documentation updates
└── verification_requirements.mdc     # Verification needs
```

#### **S3: Refactoring Development**
**Purpose**: Rules for refactoring code
**Directory**: `situations/code_development/refactoring/`

```
situations/code_development/refactoring/
├── boy_scout_principle.mdc           # Leave code cleaner
├── test_coverage_maintenance.mdc     # Maintain test coverage
├── incremental_refactoring.mdc       # Incremental approach
├── documentation_sync.mdc            # Keep docs in sync
└── performance_validation.mdc        # Validate performance
```

### **Testing Situations**

#### **S4: Unit Testing**
**Purpose**: Rules for unit testing
**Directory**: `situations/testing/unit_testing/`

```
situations/testing/unit_testing/
├── test_first_development.mdc        # Write tests first
├── test_coverage_requirements.mdc    # Coverage requirements
├── test_quality_standards.mdc        # Test quality
├── mock_usage.mdc                    # Mock usage patterns
└── test_naming_conventions.mdc       # Test naming
```

#### **S5: Integration Testing**
**Purpose**: Rules for integration testing
**Directory**: `situations/testing/integration_testing/`

```
situations/testing/integration_testing/
├── end_to_end_validation.mdc         # E2E validation
├── component_interaction.mdc         # Component interaction
├── data_flow_testing.mdc             # Data flow testing
├── performance_testing.mdc           # Performance testing
└── error_scenario_testing.mdc        # Error scenarios
```

#### **S6: System Testing**
**Purpose**: Rules for system testing
**Directory**: `situations/testing/system_testing/`

```
situations/testing/system_testing/
├── full_system_validation.mdc        # Full system validation
├── user_scenario_testing.mdc         # User scenarios
├── load_testing.mdc                  # Load testing
├── security_testing.mdc              # Security testing
└── recovery_testing.mdc              # Recovery testing
```

### **Documentation Situations**

#### **S7: Code Documentation**
**Purpose**: Rules for documenting code
**Directory**: `situations/documentation/code_documentation/`

```
situations/documentation/code_documentation/
├── docstring_requirements.mdc        # Docstring standards
├── api_documentation.mdc             # API documentation
├── inline_comments.mdc               # Inline comments
├── architecture_documentation.mdc    # Architecture docs
└── live_documentation_updates.mdc    # Live updates
```

#### **S8: User Documentation**
**Purpose**: Rules for user documentation
**Directory**: `situations/documentation/user_documentation/`

```
situations/documentation/user_documentation/
├── user_guide_creation.mdc           # User guide creation
├── installation_instructions.mdc     # Installation docs
├── troubleshooting_guides.mdc        # Troubleshooting
├── api_reference.mdc                 # API reference
└── examples_and_tutorials.mdc        # Examples and tutorials
```

### **Deployment Situations**

#### **S9: Production Deployment**
**Purpose**: Rules for production deployment
**Directory**: `situations/deployment/production/`

```
situations/deployment/production/
├── pre_deployment_checks.mdc         # Pre-deployment validation
├── zero_downtime_deployment.mdc      # Zero downtime
├── rollback_procedures.mdc           # Rollback procedures
├── monitoring_setup.mdc              # Monitoring setup
└── post_deployment_validation.mdc    # Post-deployment checks
```

#### **S10: Development Deployment**
**Purpose**: Rules for development deployment
**Directory**: `situations/deployment/development/`

```
situations/deployment/development/
├── environment_setup.mdc             # Environment setup
├── configuration_management.mdc      # Configuration
├── testing_environment.mdc           # Testing environment
├── data_management.mdc               # Data management
└── collaboration_setup.mdc           # Collaboration setup
```

### **Maintenance Situations**

#### **S11: System Maintenance**
**Purpose**: Rules for system maintenance
**Directory**: `situations/maintenance/system_maintenance/`

```
situations/maintenance/system_maintenance/
├── health_monitoring.mdc             # Health monitoring
├── performance_optimization.mdc      # Performance optimization
├── security_updates.mdc              # Security updates
├── dependency_updates.mdc            # Dependency updates
└── backup_and_recovery.mdc           # Backup and recovery
```

#### **S12: Code Maintenance**
**Purpose**: Rules for code maintenance
**Directory**: `situations/maintenance/code_maintenance/`

```
situations/maintenance/code_maintenance/
├── technical_debt_management.mdc     # Technical debt
├── code_cleanup.mdc                  # Code cleanup
├── dependency_management.mdc         # Dependency management
├── version_compatibility.mdc         # Version compatibility
└── legacy_code_handling.mdc          # Legacy code
```

### **Problem-Solving Situations**

#### **S13: Debugging**
**Purpose**: Rules for debugging
**Directory**: `situations/problem_solving/debugging/`

```
situations/problem_solving/debugging/
├── systematic_debugging.mdc          # Systematic approach
├── logging_requirements.mdc          # Logging requirements
├── error_analysis.mdc                # Error analysis
├── reproduction_steps.mdc            # Reproduction steps
└── fix_validation.mdc                # Fix validation
```

#### **S14: Performance Issues**
**Purpose**: Rules for performance issues
**Directory**: `situations/problem_solving/performance/`

```
situations/problem_solving/performance/
├── performance_profiling.mdc         # Performance profiling
├── bottleneck_identification.mdc     # Bottleneck identification
├── optimization_strategies.mdc       # Optimization strategies
├── performance_testing.mdc           # Performance testing
└── monitoring_setup.mdc              # Monitoring setup
```

### **Quality Assurance Situations**

#### **S15: Code Review**
**Purpose**: Rules for code review
**Directory**: `situations/quality_assurance/code_review/`

```
situations/quality_assurance/code_review/
├── review_checklist.mdc              # Review checklist
├── quality_standards.mdc             # Quality standards
├── security_review.mdc               # Security review
├── performance_review.mdc            # Performance review
└── documentation_review.mdc          # Documentation review
```

#### **S16: Quality Validation**
**Purpose**: Rules for quality validation
**Directory**: `situations/quality_assurance/quality_validation/`

```
situations/quality_assurance/quality_validation/
├── test_validation.mdc               # Test validation
├── code_quality_metrics.mdc          # Quality metrics
├── performance_validation.mdc        # Performance validation
├── security_validation.mdc           # Security validation
└── user_experience_validation.mdc    # UX validation
```

### **Security Situations**

#### **S17: Security Assessment**
**Purpose**: Rules for security assessment
**Directory**: `situations/security/security_assessment/`

```
situations/security/security_assessment/
├── vulnerability_scanning.mdc        # Vulnerability scanning
├── code_security_review.mdc          # Code security review
├── dependency_security.mdc           # Dependency security
├── configuration_security.mdc        # Configuration security
├── access_control_review.mdc         # Access control review
└── security_testing.mdc              # Security testing
```

#### **S18: Security Implementation**
**Purpose**: Rules for security implementation
**Directory**: `situations/security/security_implementation/`

```
situations/security/security_implementation/
├── authentication_implementation.mdc # Authentication implementation
├── authorization_implementation.mdc  # Authorization implementation
├── data_encryption.mdc               # Data encryption
├── secure_coding.mdc                 # Secure coding
├── security_monitoring.mdc           # Security monitoring
└── incident_response.mdc             # Incident response
```

## 3. TASK-SPECIFIC RULES

### **Writing Code Tasks**

#### **T1: Function Implementation**
**Purpose**: Rules for implementing functions
**Directory**: `tasks/code_writing/function_implementation/`

```
tasks/code_writing/function_implementation/
├── function_design.mdc               # Function design
├── parameter_validation.mdc          # Parameter validation
├── error_handling.mdc                # Error handling
├── return_value_handling.mdc         # Return value handling
├── documentation_requirements.mdc    # Documentation
└── testing_requirements.mdc          # Testing requirements
```

#### **T2: Class Implementation**
**Purpose**: Rules for implementing classes
**Directory**: `tasks/code_writing/class_implementation/`

```
tasks/code_writing/class_implementation/
├── class_design.mdc                  # Class design
├── encapsulation.mdc                 # Encapsulation
├── inheritance_usage.mdc             # Inheritance usage
├── method_implementation.mdc         # Method implementation
├── property_implementation.mdc       # Property implementation
└── documentation_requirements.mdc    # Documentation
```

#### **T3: Module Implementation**
**Purpose**: Rules for implementing modules
**Directory**: `tasks/code_writing/module_implementation/`

```
tasks/code_writing/module_implementation/
├── module_structure.mdc              # Module structure
├── import_organization.mdc           # Import organization
├── public_interface.mdc              # Public interface
├── internal_implementation.mdc       # Internal implementation
├── documentation_requirements.mdc    # Documentation
└── testing_requirements.mdc          # Testing requirements
```

### **Reviewing Code Tasks**

#### **T4: Code Review**
**Purpose**: Rules for reviewing code
**Directory**: `tasks/code_review/code_review/`

```
tasks/code_review/code_review/
├── review_process.mdc                # Review process
├── quality_checklist.mdc             # Quality checklist
├── security_review.mdc               # Security review
├── performance_review.mdc            # Performance review
├── maintainability_review.mdc        # Maintainability review
└── documentation_review.mdc          # Documentation review
```

#### **T5: Architecture Review**
**Purpose**: Rules for reviewing architecture
**Directory**: `tasks/code_review/architecture_review/`

```
tasks/code_review/architecture_review/
├── architectural_principles.mdc      # Architectural principles
├── design_patterns.mdc               # Design patterns
├── scalability_review.mdc            # Scalability review
├── maintainability_review.mdc        # Maintainability review
├── security_architecture.mdc         # Security architecture
└── performance_architecture.mdc      # Performance architecture
```

### **Testing Tasks**

#### **T6: Unit Test Writing**
**Purpose**: Rules for writing unit tests
**Directory**: `tasks/testing/unit_test_writing/`

```
tasks/testing/unit_test_writing/
├── test_structure.mdc                # Test structure
├── test_naming.mdc                   # Test naming
├── test_data_management.mdc          # Test data management
├── mock_usage.mdc                    # Mock usage
├── assertion_usage.mdc               # Assertion usage
└── test_coverage.mdc                 # Test coverage
```

#### **T7: Integration Test Writing**
**Purpose**: Rules for writing integration tests
**Directory**: `tasks/testing/integration_test_writing/`

```
tasks/testing/integration_test_writing/
├── test_setup.mdc                    # Test setup
├── component_interaction.mdc         # Component interaction
├── data_flow_testing.mdc             # Data flow testing
├── error_scenario_testing.mdc        # Error scenario testing
├── performance_testing.mdc           # Performance testing
└── test_cleanup.mdc                  # Test cleanup
```

### **Documenting Tasks**

#### **T8: API Documentation**
**Purpose**: Rules for documenting APIs
**Directory**: `tasks/documentation/api_documentation/`

```
tasks/documentation/api_documentation/
├── endpoint_documentation.mdc        # Endpoint documentation
├── parameter_documentation.mdc       # Parameter documentation
├── response_documentation.mdc        # Response documentation
├── error_documentation.mdc           # Error documentation
├── example_usage.mdc                 # Example usage
└── versioning_documentation.mdc      # Versioning documentation
```

#### **T9: User Guide Writing**
**Purpose**: Rules for writing user guides
**Directory**: `tasks/documentation/user_guide_writing/`

```
tasks/documentation/user_guide_writing/
├── guide_structure.mdc               # Guide structure
├── step_by_step_instructions.mdc     # Step-by-step instructions
├── troubleshooting_section.mdc       # Troubleshooting section
├── faq_section.mdc                   # FAQ section
├── example_workflows.mdc             # Example workflows
└── visual_aids.mdc                   # Visual aids
```

### **Deploying Tasks**

#### **T10: Environment Setup**
**Purpose**: Rules for setting up environments
**Directory**: `tasks/deployment/environment_setup/`

```
tasks/deployment/environment_setup/
├── environment_configuration.mdc     # Environment configuration
├── dependency_installation.mdc       # Dependency installation
├── configuration_management.mdc      # Configuration management
├── security_setup.mdc                # Security setup
├── monitoring_setup.mdc              # Monitoring setup
└── backup_setup.mdc                  # Backup setup
```

#### **T11: Deployment Execution**
**Purpose**: Rules for executing deployment
**Directory**: `tasks/deployment/deployment_execution/`

```
tasks/deployment/deployment_execution/
├── pre_deployment_checks.mdc         # Pre-deployment checks
├── deployment_process.mdc            # Deployment process
├── health_checks.mdc                 # Health checks
├── rollback_procedures.mdc           # Rollback procedures
├── post_deployment_validation.mdc    # Post-deployment validation
└── monitoring_setup.mdc              # Monitoring setup
```

### **Debugging Tasks**

#### **T12: Problem Investigation**
**Purpose**: Rules for investigating problems
**Directory**: `tasks/debugging/problem_investigation/`

```
tasks/debugging/problem_investigation/
├── problem_identification.mdc        # Problem identification
├── reproduction_steps.mdc            # Reproduction steps
├── log_analysis.mdc                  # Log analysis
├── error_analysis.mdc                # Error analysis
├── root_cause_analysis.mdc           # Root cause analysis
└── impact_assessment.mdc             # Impact assessment
```

#### **T13: Fix Implementation**
**Purpose**: Rules for implementing fixes
**Directory**: `tasks/debugging/fix_implementation/`

```
tasks/debugging/fix_implementation/
├── fix_design.mdc                    # Fix design
├── minimal_change_principle.mdc      # Minimal change principle
├── regression_testing.mdc            # Regression testing
├── fix_validation.mdc                # Fix validation
├── documentation_updates.mdc         # Documentation updates
└── deployment_considerations.mdc     # Deployment considerations
```

### **Refactoring Tasks**

#### **T14: Code Refactoring**
**Purpose**: Rules for refactoring code
**Directory**: `tasks/refactoring/code_refactoring/`

```
tasks/refactoring/code_refactoring/
├── refactoring_planning.mdc          # Refactoring planning
├── incremental_refactoring.mdc       # Incremental refactoring
├── test_coverage_maintenance.mdc     # Test coverage maintenance
├── documentation_sync.mdc            # Documentation sync
├── performance_validation.mdc        # Performance validation
└── code_review_requirements.mdc      # Code review requirements
```

#### **T15: Architecture Refactoring**
**Purpose**: Rules for refactoring architecture
**Directory**: `tasks/refactoring/architecture_refactoring/`

```
tasks/refactoring/architecture_refactoring/
├── architectural_analysis.mdc        # Architectural analysis
├── refactoring_strategy.mdc          # Refactoring strategy
├── component_extraction.mdc          # Component extraction
├── interface_design.mdc              # Interface design
├── migration_planning.mdc            # Migration planning
└── validation_and_testing.mdc        # Validation and testing
```

### **Security Assessment Tasks**

#### **T16: Vulnerability Assessment**
**Purpose**: Rules for assessing vulnerabilities
**Directory**: `tasks/security/vulnerability_assessment/`

```
tasks/security/vulnerability_assessment/
├── vulnerability_scanning.mdc        # Vulnerability scanning
├── code_security_review.mdc          # Code security review
├── dependency_security.mdc           # Dependency security
├── configuration_security.mdc        # Configuration security
├── access_control_review.mdc         # Access control review
└── security_testing.mdc              # Security testing
```

#### **T17: Security Implementation**
**Purpose**: Rules for implementing security
**Directory**: `tasks/security/security_implementation/`

```
tasks/security/security_implementation/
├── authentication_implementation.mdc # Authentication implementation
├── authorization_implementation.mdc  # Authorization implementation
├── data_encryption.mdc               # Data encryption
├── secure_coding.mdc                 # Secure coding
├── security_monitoring.mdc           # Security monitoring
└── incident_response.mdc             # Incident response
```

## 4. SITUATION & TASK DISCOVERY SYSTEM

### **Situation Analysis Engine**

```python
class SituationAnalysisEngine:
    """Engine for analyzing situations and identifying applicable rules."""
    
    def analyze_situation(self, context: dict) -> SituationAnalysis:
        """Analyze the current situation to identify applicable rules."""
        
        analysis = SituationAnalysis()
        
        # Analyze context for situation indicators
        analysis.situation_type = self._identify_situation_type(context)
        analysis.current_task = self._identify_current_task(context)
        analysis.file_types = self._identify_file_types(context)
        analysis.process_context = self._identify_process_context(context)
        
        # Identify applicable situations
        applicable_situations = self._identify_applicable_situations(analysis)
        
        # Identify applicable tasks
        applicable_tasks = self._identify_applicable_tasks(analysis)
        
        # Combine situation and task rules
        all_applicable_rules = []
        all_applicable_rules.extend(self._get_situation_rules(applicable_situations))
        all_applicable_rules.extend(self._get_task_rules(applicable_tasks))
        
        # Remove duplicates and prioritize
        unique_rules = self._deduplicate_rules(all_applicable_rules)
        prioritized_rules = self._prioritize_rules(unique_rules, analysis)
        
        analysis.applicable_rules = prioritized_rules
        return analysis
    
    def _identify_situation_type(self, context: dict) -> str:
        """Identify the type of situation based on context."""
        
        situation_indicators = {
            "code_development": [
                "new_file_creation", "feature_development", "bug_fix",
                "refactoring", "code_modification"
            ],
            "testing": [
                "test_execution", "test_creation", "test_modification",
                "test_debugging", "test_optimization"
            ],
            "documentation": [
                "documentation_creation", "documentation_update",
                "api_documentation", "user_guide_creation"
            ],
            "deployment": [
                "environment_setup", "deployment_execution",
                "configuration_management", "monitoring_setup"
            ],
            "maintenance": [
                "system_maintenance", "code_maintenance",
                "dependency_updates", "performance_optimization"
            ],
            "problem_solving": [
                "debugging", "error_investigation", "performance_issues",
                "security_issues", "compatibility_issues"
            ],
            "quality_assurance": [
                "code_review", "quality_validation", "testing_validation",
                "performance_validation", "security_validation"
            ],
            "security": [
                "security_assessment", "vulnerability_scanning",
                "security_implementation", "security_testing"
            ]
        }
        
        # Match context to situation indicators
        for situation_type, indicators in situation_indicators.items():
            if any(indicator in context for indicator in indicators):
                return situation_type
        
        return "general"
    
    def _identify_current_task(self, context: dict) -> str:
        """Identify the current task based on context."""
        
        task_indicators = {
            "function_implementation": ["function_creation", "function_modification"],
            "class_implementation": ["class_creation", "class_modification"],
            "module_implementation": ["module_creation", "module_modification"],
            "code_review": ["review_process", "quality_check"],
            "architecture_review": ["architectural_analysis", "design_review"],
            "unit_test_writing": ["test_creation", "test_modification"],
            "integration_test_writing": ["integration_test", "component_testing"],
            "api_documentation": ["api_doc", "endpoint_documentation"],
            "user_guide_writing": ["user_guide", "tutorial_creation"],
            "environment_setup": ["environment_configuration", "setup_process"],
            "deployment_execution": ["deployment_process", "release_execution"],
            "problem_investigation": ["debugging", "error_analysis"],
            "fix_implementation": ["bug_fix", "issue_resolution"],
            "code_refactoring": ["refactoring", "code_restructuring"],
            "architecture_refactoring": ["architectural_refactoring", "system_restructuring"],
            "vulnerability_assessment": ["security_scan", "vulnerability_analysis"],
            "security_implementation": ["security_feature", "security_control"]
        }
        
        # Match context to task indicators
        for task_type, indicators in task_indicators.items():
            if any(indicator in context for indicator in indicators):
                return task_type
        
        return "general"
```

### **Rule Discovery Workflow**

```python
class SituationTaskRuleDiscovery:
    """Workflow for discovering rules based on situations and tasks."""
    
    def discover_applicable_rules(self, context: dict) -> RuleDiscoveryResult:
        """Discover all applicable rules for the current context."""
        
        # Step 1: Analyze situation
        situation_analysis = self.situation_analyzer.analyze_situation(context)
        
        # Step 2: Get situation-specific rules
        situation_rules = self._get_situation_rules(situation_analysis.situation_type)
        
        # Step 3: Get task-specific rules
        task_rules = self._get_task_rules(situation_analysis.current_task)
        
        # Step 4: Apply meta-rules for priority and conflict resolution
        all_rules = situation_rules + task_rules
        prioritized_rules = self.priority_manager.resolve_rule_conflicts(all_rules)
        
        # Step 5: Create compliance plan
        compliance_plan = self.compliance_monitor.create_compliance_plan(prioritized_rules, context)
        
        return RuleDiscoveryResult(
            situation=situation_analysis,
            situation_rules=situation_rules,
            task_rules=task_rules,
            prioritized_rules=prioritized_rules,
            compliance_plan=compliance_plan
        )
```

## 5. IMPLEMENTATION PLAN

### **Phase 1: Create Situation-Specific Structure**
1. Create situation-specific directories and rule files
2. Implement situation analysis engine
3. Create situation-based rule discovery system
4. Test situation-specific rule application

### **Phase 2: Create Task-Specific Structure**
1. Create task-specific directories and rule files
2. Implement task analysis engine
3. Create task-based rule discovery system
4. Test task-specific rule application

### **Phase 3: Integrate Situation and Task Discovery**
1. Combine situation and task analysis
2. Implement unified rule discovery workflow
3. Create rule priority and conflict resolution
4. Test integrated rule discovery system

### **Phase 4: Implement Rule Application System**
1. Create rule application workflow
2. Implement compliance monitoring
3. Create effectiveness evaluation
4. Test complete rule application system

## 6. BENEFITS OF SITUATION & TASK SPECIFIC ORGANIZATION

### **For Rule Discovery**
- **Context-Aware**: Rules are found based on actual situation and task
- **Relevant**: Only applicable rules are discovered and applied
- **Efficient**: Fast lookup based on situation and task indicators
- **Comprehensive**: Covers all aspects of the current context

### **For Rule Application**
- **Targeted**: Rules are applied to specific situations and tasks
- **Systematic**: Structured workflow for rule application
- **Compliant**: Ensures all relevant rules are followed
- **Effective**: Optimized for the specific context

### **For Rule Management**
- **Organized**: Clear structure based on when and what rules apply
- **Maintainable**: Easy to add, modify, and remove rules
- **Scalable**: Structure supports growth and complexity
- **Discoverable**: Easy to find rules for any situation or task

**This situation and task-specific organization transforms our rule system into a context-aware, intelligent system that automatically finds and applies the right rules based on what we're doing and the situation we're in.**
