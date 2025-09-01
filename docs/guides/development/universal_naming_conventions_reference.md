# Universal Naming Conventions Reference Guide

**Complete reference for ALL artifact types in the AI-Dev-Agent project**

Based on Fowler/Carnap/Quine philosophical principles for systematic excellence.

---

## 📚 **Table of Contents**

1. [Philosophical Foundation](#philosophical-foundation)
2. [Agile Artifacts](#agile-artifacts)
3. [Code Artifacts](#code-artifacts)
4. [Test Artifacts](#test-artifacts)
5. [Documentation Artifacts](#documentation-artifacts)
6. [Configuration Artifacts](#configuration-artifacts)
7. [Data Artifacts](#data-artifacts)
8. [Infrastructure Artifacts](#infrastructure-artifacts)
9. [Monitoring Artifacts](#monitoring-artifacts)
10. [Quick Reference](#quick-reference)

---

## 🧠 **Philosophical Foundation**

**Fowler Principle**: Naming conventions must be **pragmatically useful** - they solve real problems and improve development velocity.

**Carnap Principle**: Naming must provide **systematic clarity** - every name should unambiguously communicate its purpose and category.

**Quine Principle**: Names establish **ontological relativity** - naming conventions define our development universe.

---

## 📋 **Agile Artifacts**

### **Epic Files**
**Pattern**: `epic-{topic}.md` (lowercase-with-hyphens)

```yaml
✅ CORRECT:
- epic-formal-principles.md
- epic-agent-development.md  
- epic-ui-excellence.md
- epic-system-integration.md

❌ INCORRECT:
- EPIC-FORMAL-PRINCIPLES.md
- Epic_Formal_Principles.md
- epic_formal_principles.md
```

### **User Story Files**
**Pattern**: `US-{XXX}.md` (UPPER-CASE-WITH-HYPHENS)

```yaml
✅ CORRECT:
- US-001.md
- US-028.md
- US-PE-01.md
- US-ARCH-001.md

❌ INCORRECT:
- us-001.md
- USER_STORY_001.md
- Story-001.md
```

### **Sprint Files**
**Pattern**: `sprint_{N}_{type}.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- sprint_1_summary.md
- sprint_2_retrospective.md
- sprint_1_completion_status.md
- sprint_3_planning.md

❌ INCORRECT:
- SPRINT_1_COMPLETION_REPORT.md
- Sprint1Summary.md
- sprint-1-summary.md
```

### **Catalog Files**
**Pattern**: `{type}_catalog.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- user_story_catalog.md
- epic_overview.md
- task_catalog.md
- sprint_summary.md

❌ INCORRECT:
- USER_STORY_CATALOG.md
- Epic-Overview.md
- TaskCatalog.md
```

---

## 💻 **Code Artifacts**

### **Agent Modules**
**Pattern**: `{name}_(agent|team|specialist).py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- requirements_analysis_agent.py
- pydantic_migration_specialist_team.py
- ui_testing_specialist_team.py
- code_generator_agent.py

❌ INCORRECT:
- RequirementsAnalysisAgent.py
- pydantic-migration-specialist.py
- UITestingTeam.py
```

### **Model Modules**
**Pattern**: `{name}_(model|state|schema|config).py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- supervisor_state.py
- agent_config.py
- user_model.py
- response_schema.py

❌ INCORRECT:
- SupervisorState.py
- agent-config.py
- UserModel.py
```

### **Utility Modules**
**Pattern**: `{name}_(utils|helper|manager).py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- file_organization_enforcer.py
- prompt_optimization_utils.py
- database_manager.py
- validation_helper.py

❌ INCORRECT:
- FileOrganizationEnforcer.py
- prompt-optimization-utils.py
- DatabaseManager.py
```

### **Workflow Modules**
**Pattern**: `{name}_workflow.py` or `{name}_orchestrator.py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- task_workflow.py
- agent_orchestrator.py
- development_workflow.py
- deployment_orchestrator.py

❌ INCORRECT:
- TaskWorkflow.py
- agent-orchestrator.py
- DevelopmentWorkflow.py
```

### **App Modules**
**Pattern**: `{name}_app.py` or `{descriptive_name}.py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- streamlit_app.py
- prompt_manager_app.py
- advanced_prompt_engineering_ui.py
- main.py

❌ INCORRECT:
- StreamlitApp.py
- prompt-manager-app.py
- AdvancedPromptUI.py
```

---

## 🧪 **Test Artifacts**

### **Unit Test Files**
**Pattern**: `test_{module_name}.py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- test_agent_validation.py
- test_prompt_optimization.py
- test_workflow_manager.py
- test_database_operations.py

❌ INCORRECT:
- TestAgentValidation.py
- test-agent-validation.py
- agent_validation_test.py
```

### **Integration Test Files**
**Pattern**: `test_{integration_scope}.py` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- test_agent_execution.py
- test_workflow_integration.py
- test_system_validation.py
- test_api_integration.py

❌ INCORRECT:
- TestAgentExecution.py
- test-workflow-integration.py
- integration_test_workflow.py
```

### **Test Directories**
**Pattern**: `{category}/` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- tests/unit/
- tests/integration/
- tests/system/
- tests/performance/

❌ INCORRECT:
- tests/Unit/
- tests/Integration/
- tests/system-tests/
```

---

## 📖 **Documentation Artifacts**

### **Guide Files**
**Pattern**: `{topic}_guide.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- development_workflow_guide.md
- testing_strategy_guide.md
- deployment_guide.md
- naming_conventions_guide.md

❌ INCORRECT:
- DevelopmentWorkflowGuide.md
- testing-strategy-guide.md
- DeploymentGuide.md
```

### **Rule Files**
**Pattern**: `{topic}_rule.(md|mdc)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- universal_naming_convention_rule.md
- boyscout_leave_cleaner_rule.mdc
- file_organization_rule.md
- quality_validation_rule.md

❌ INCORRECT:
- UniversalNamingConventionRule.md
- boyscout-leave-cleaner-rule.md
- FileOrganizationRule.md
```

### **Architecture Documents**
**Pattern**: `{component}_architecture.md` or `{topic}_overview.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- system_architecture.md
- agent_framework_overview.md
- database_design.md
- security_architecture.md

❌ INCORRECT:
- SystemArchitecture.md
- agent-framework-overview.md
- DatabaseDesign.md
```

### **README Files**
**Pattern**: `README.md` (UPPER-CASE, standard convention)

```yaml
✅ CORRECT:
- README.md (in any directory)

❌ INCORRECT:
- readme.md
- Readme.md
- READ_ME.md
```

---

## ⚙️ **Configuration Artifacts**

### **JSON Configuration Files**
**Pattern**: `{purpose}.json` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- package.json
- tsconfig.json
- pytest_config.json
- agent_settings.json

❌ INCORRECT:
- Package.json
- pytest-config.json
- AgentSettings.json
```

### **YAML Configuration Files**
**Pattern**: `{purpose}.(yaml|yml)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- docker_compose.yml
- ci_pipeline.yaml
- deployment_config.yml
- test_settings.yaml

❌ INCORRECT:
- DockerCompose.yml
- ci-pipeline.yaml
- DeploymentConfig.yml
```

### **Environment Files**
**Pattern**: `.env` or `.env.{environment}` (lowercase)

```yaml
✅ CORRECT:
- .env
- .env.development
- .env.production
- .env.test

❌ INCORRECT:
- .ENV
- .env.Development
- .Env.production
```

### **Requirements Files**
**Pattern**: `requirements.txt` or `requirements_{env}.txt` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- requirements.txt
- requirements_dev.txt
- requirements_test.txt
- requirements_prod.txt

❌ INCORRECT:
- Requirements.txt
- requirements-dev.txt
- RequirementsDev.txt
```

---

## 📊 **Data Artifacts**

### **Database Files**
**Pattern**: `{purpose}.(db|sqlite)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- prompt_templates.db
- learning_experiences.db
- monitoring.sqlite
- user_data.db

❌ INCORRECT:
- PromptTemplates.db
- prompt-templates.db
- LearningExperiences.db
```

### **JSON Data Files**
**Pattern**: `{data_type}.json` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- health_data.json
- metrics_data.json
- alert_settings.json
- user_preferences.json

❌ INCORRECT:
- HealthData.json
- metrics-data.json
- AlertSettings.json
```

### **CSV Data Files**
**Pattern**: `{data_type}.csv` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- user_analytics.csv
- performance_metrics.csv
- test_results.csv
- export_data.csv

❌ INCORRECT:
- UserAnalytics.csv
- performance-metrics.csv
- TestResults.csv
```

### **Log Files**
**Pattern**: `{component}.log` or `{component}_{date}.log` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- agent.log
- application.log
- error_20250101.log
- performance_metrics.log

❌ INCORRECT:
- Agent.log
- application-log.txt
- ErrorLog.log
```

---

## 🏗️ **Infrastructure Artifacts**

### **Script Files**
**Pattern**: `{purpose}.(py|sh|bat)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- setup_environment.py
- deploy_application.sh
- backup_database.py
- run_tests.bat

❌ INCORRECT:
- SetupEnvironment.py
- deploy-application.sh
- BackupDatabase.py
```

### **Docker Files**
**Pattern**: `Dockerfile` or `docker-compose.yml` (standard convention)

```yaml
✅ CORRECT:
- Dockerfile
- docker-compose.yml
- Dockerfile.prod
- docker-compose.test.yml

❌ INCORRECT:
- dockerfile
- Docker-Compose.yml
- DockerFile
```

### **CI/CD Files**
**Pattern**: `{purpose}.(yml|yaml)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- github_workflow.yml
- ci_pipeline.yaml
- deployment_config.yml
- test_automation.yaml

❌ INCORRECT:
- GitHubWorkflow.yml
- ci-pipeline.yaml
- DeploymentConfig.yml
```

---

## 📈 **Monitoring Artifacts**

### **Metrics Files**
**Pattern**: `{metric_type}_metrics.json` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- performance_metrics.json
- system_health_metrics.json
- user_engagement_metrics.json
- error_rate_metrics.json

❌ INCORRECT:
- PerformanceMetrics.json
- performance-metrics.json
- SystemHealthMetrics.json
```

### **Alert Files**
**Pattern**: `{alert_type}_alerts.json` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- system_alerts.json
- performance_alerts.json
- security_alerts.json
- maintenance_alerts.json

❌ INCORRECT:
- SystemAlerts.json
- performance-alerts.json
- SecurityAlerts.json
```

### **Dashboard Files**
**Pattern**: `{dashboard_type}_dashboard.(json|yaml)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- system_health_dashboard.json
- performance_dashboard.yaml
- user_analytics_dashboard.json
- error_monitoring_dashboard.yaml

❌ INCORRECT:
- SystemHealthDashboard.json
- performance-dashboard.yaml
- UserAnalyticsDashboard.json
```

---

## ⚡ **Quick Reference**

### **Primary Patterns**
1. **lowercase_with_underscores** - Most files (Python, docs, configs)
2. **lowercase-with-hyphens** - Epic files only
3. **UPPER-CASE-CODES** - User story IDs only
4. **Standard conventions** - README.md, Dockerfile, etc.

### **File Extension Guidelines**
- **`.py`** - Python modules
- **`.md`** - Markdown documentation
- **`.json`** - JSON configuration/data
- **`.yaml/.yml`** - YAML configuration
- **`.db/.sqlite`** - Database files
- **`.log`** - Log files
- **`.csv`** - CSV data files
- **`.txt`** - Text files (requirements, etc.)

### **Directory Structure**
```
project_root/
├── agents/                 # AI agent implementations
├── apps/                   # Application entry points
├── context/                # Context management
├── docs/                   # Documentation
│   ├── guides/             # Development guides
│   ├── rules/              # Project rules
│   ├── agile/              # Agile artifacts
│   └── reports/            # Implementation reports
├── models/                 # Data models and schemas
├── monitoring/             # Monitoring and analytics
├── prompts/                # Prompt management
├── scripts/                # Utility scripts
├── tests/                  # All test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── system/             # System tests
├── utils/                  # Utility modules
└── workflow/               # Workflow management
```

### **Validation Command**
```bash
# Validate file naming conventions
python utils/validation/universal_naming_validator.py --check {file_path}

# Auto-fix naming violations
python utils/quality/boyscout_naming_integration.py --fix {directory}
```

---

## 🎯 **Success Criteria**

- **100%** compliance with naming conventions across ALL artifact types
- **Zero** automation failures due to naming inconsistencies  
- **Immediate** recognition of purpose from file names
- **Systematic** organization enabling reliable navigation
- **Professional** appearance for all stakeholders

---

**Remember**: "Every name should immediately communicate its purpose, category, and relationship within our systematic development universe."

**Philosophical Foundation**: Fowler (pragmatic utility) + Carnap (systematic clarity) + Quine (ontological consistency) = Universal Excellence
