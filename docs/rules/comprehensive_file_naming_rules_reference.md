# Comprehensive File Naming Rules Reference
## For All Project File Types Following Logical Principles

**SACRED DOCUMENT**: Complete reference for every file type in the AI-Dev-Agent project following our systematic logical principles from Fowler, Carnap, Quine, and Wittgenstein.

---

## 🧠 **Philosophical Foundation**

### **Core Logical Principles**

1. **Fowler Pragmatic Principle**: Names must be **pragmatically useful** - they solve real problems and improve development velocity
2. **Carnap Systematic Clarity**: Names must provide **unambiguous communication** of purpose and category  
3. **Quine Ontological Relativity**: Names establish our **development universe** - they define what exists and how it relates
4. **Wittgenstein Language Games**: Each file type belongs to a **specific language game** with its own grammar and rules

### **Universal Meta-Rules**

- **Consistency**: Same type = same pattern
- **Predictability**: Pattern reveals purpose immediately
- **Automation-Friendly**: Names enable reliable script processing
- **Human-Readable**: Clear communication to developers
- **Context-Aware**: Names reflect their domain and usage

---

## 📋 **AGILE ARTIFACTS**

### **Epic Files**
**Pattern**: `epic-{topic}.md` *(lowercase-with-hyphens)*
**Logical Principle**: Hyphens for hierarchical topics, lowercase for simplicity

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
**Pattern**: `US-{XXX}.md` *(UPPER-CASE-WITH-HYPHENS)*
**Logical Principle**: Capital code for unique identification, hyphens for readability

```yaml
✅ CORRECT:
- US-001.md
- US-028.md
- US-PE-01.md
- US-ARCH-001.md
- US-MODESTY-001.md

❌ INCORRECT:
- us-001.md
- USER_STORY_001.md
- Story-001.md
```

### **Sprint Files**
**Pattern**: `sprint_{N}_{type}.md` *(lowercase_with_underscores)*
**Logical Principle**: Underscores for structured metadata, numbers for ordering

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
**Pattern**: `{type}_catalog.md` *(lowercase_with_underscores)*
**Logical Principle**: Descriptive type + standard suffix for easy identification

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

## 💻 **CODE ARTIFACTS**

### **Agent Files**
**Pattern**: `{name}_agent.py` *(snake_case_with_agent_suffix)*
**Logical Principle**: Snake case for Python, clear agent suffix for identification

```yaml
✅ CORRECT:
- requirements_analyst_agent.py
- system_architect_agent.py
- test_automation_agent.py
- file_organization_agent.py

❌ INCORRECT:
- RequirementsAnalystAgent.py
- system-architect-agent.py
- SYSTEM_ARCHITECT_AGENT.py
- agent_system_architect.py
```

### **Team Files**
**Pattern**: `{name}_team.py` *(snake_case_with_team_suffix)*
**Logical Principle**: Snake case for Python, clear team suffix for group identification

```yaml
✅ CORRECT:
- cursor_ide_integration_expert_team.py
- rule_system_core_architecture_team.py
- agile_coordination_team.py

❌ INCORRECT:
- CursorIdeIntegrationExpertTeam.py
- cursor-ide-integration-expert-team.py
- CURSOR_IDE_INTEGRATION_EXPERT_TEAM.py
```

### **Utility Files**
**Pattern**: `{function}_{type}.py` *(snake_case_descriptive)*
**Logical Principle**: Function first, type second for logical grouping

```yaml
✅ CORRECT:
- naming_validator.py
- file_organizer.py
- context_detector.py
- rule_loader.py
- carnap_logical_analyzer.py

❌ INCORRECT:
- NamingValidator.py
- file-organizer.py
- contextDetector.py
- RuleLoader.py
```

### **Model Files**
**Pattern**: `{entity}_model.py` *(snake_case_with_model_suffix)*
**Logical Principle**: Entity name + standard suffix for data structure identification

```yaml
✅ CORRECT:
- user_story_model.py
- agent_state_model.py
- workflow_config_model.py
- system_health_model.py

❌ INCORRECT:
- UserStoryModel.py
- user-story-model.py
- MODEL_USER_STORY.py
```

### **Workflow Files**
**Pattern**: `{process}_workflow.py` *(snake_case_with_workflow_suffix)*
**Logical Principle**: Process name + workflow suffix for orchestration identification

```yaml
✅ CORRECT:
- agile_coordination_workflow.py
- file_organization_workflow.py
- test_automation_workflow.py
- deployment_workflow.py

❌ INCORRECT:
- AgileCoordinationWorkflow.py
- agile-coordination-workflow.py
- AGILE_COORDINATION_WORKFLOW.py
```

---

## 🧪 **TEST ARTIFACTS**

### **Test Files**
**Pattern**: `test_{module_name}.py` *(test_prefix_snake_case)*
**Logical Principle**: Standard test prefix for automatic discovery, snake case for consistency

```yaml
✅ CORRECT:
- test_naming_validator.py
- test_agent_coordination.py
- test_file_organization.py
- test_rule_system.py

❌ INCORRECT:
- TestNamingValidator.py
- test-naming-validator.py
- naming_validator_test.py
- TEST_NAMING_VALIDATOR.py
```

### **Test Data Files**
**Pattern**: `{test_type}_test_data.json` *(snake_case_with_test_data_suffix)*
**Logical Principle**: Test type + standard suffix for data identification

```yaml
✅ CORRECT:
- naming_validation_test_data.json
- agent_coordination_test_data.json
- file_organization_test_data.json

❌ INCORRECT:
- NamingValidationTestData.json
- naming-validation-test-data.json
- TEST_DATA_NAMING_VALIDATION.json
```

---

## 📚 **DOCUMENTATION ARTIFACTS**

### **Guide Files**
**Pattern**: `{topic}_guide.md` *(snake_case_with_guide_suffix)*
**Logical Principle**: Topic + standard suffix for easy categorization

```yaml
✅ CORRECT:
- development_guide.md
- testing_guide.md
- deployment_guide.md
- naming_conventions_guide.md

❌ INCORRECT:
- DevelopmentGuide.md
- development-guide.md
- DEVELOPMENT_GUIDE.md
- guide_development.md
```

### **Rule Files**
**Pattern**: `{rule_name}_rule.mdc` *(snake_case_with_rule_suffix)*
**Logical Principle**: Rule name + standard suffix + mdc extension for Cursor IDE

```yaml
✅ CORRECT:
- safety_first_principle_rule.mdc
- file_organization_cleanup_rule.mdc
- agile_strategic_coordination_rule.mdc

❌ INCORRECT:
- SafetyFirstPrincipleRule.mdc
- safety-first-principle-rule.mdc
- SAFETY_FIRST_PRINCIPLE_RULE.mdc
```

### **Architecture Files**
**Pattern**: `{component}_architecture.md` *(snake_case_with_architecture_suffix)*
**Logical Principle**: Component + architecture suffix for system design documents

```yaml
✅ CORRECT:
- system_architecture.md
- agent_architecture.md
- database_architecture.md
- rule_system_architecture.md

❌ INCORRECT:
- SystemArchitecture.md
- system-architecture.md
- SYSTEM_ARCHITECTURE.md
```

### **Reference Files**
**Pattern**: `{topic}_reference.md` *(snake_case_with_reference_suffix)*
**Logical Principle**: Topic + reference suffix for lookup documents

```yaml
✅ CORRECT:
- api_reference.md
- naming_conventions_reference.md
- command_reference.md
- configuration_reference.md

❌ INCORRECT:
- ApiReference.md
- api-reference.md
- API_REFERENCE.md
```

---

## ⚙️ **CONFIGURATION ARTIFACTS**

### **JSON Configuration Files**
**Pattern**: `{purpose}_config.json` *(snake_case_with_config_suffix)*
**Logical Principle**: Purpose + config suffix for configuration identification

```yaml
✅ CORRECT:
- database_config.json
- logging_config.json
- agent_config.json
- system_config.json

❌ INCORRECT:
- DatabaseConfig.json
- database-config.json
- DATABASE_CONFIG.json
- config_database.json
```

### **YAML Configuration Files**
**Pattern**: `{purpose}_config.yaml` *(snake_case_with_config_suffix)*
**Logical Principle**: Same as JSON but with YAML extension

```yaml
✅ CORRECT:
- docker_compose_config.yaml
- deployment_config.yaml
- ci_cd_config.yaml

❌ INCORRECT:
- DockerComposeConfig.yaml
- docker-compose-config.yaml
- DOCKER_COMPOSE_CONFIG.yaml
```

### **Environment Files**
**Pattern**: `.env.{environment}` *(standard_dot_env_format)*
**Logical Principle**: Standard environment file convention

```yaml
✅ CORRECT:
- .env
- .env.development
- .env.production
- .env.testing

❌ INCORRECT:
- env.txt
- environment.env
- ENV_DEVELOPMENT
```

### **Requirements Files**
**Pattern**: `requirements_{purpose}.txt` *(requirements_prefix_snake_case)*
**Logical Principle**: Standard requirements prefix + purpose

```yaml
✅ CORRECT:
- requirements.txt
- requirements_dev.txt
- requirements_test.txt
- requirements_production.txt

❌ INCORRECT:
- Requirements.txt
- requirements-dev.txt
- DEV_REQUIREMENTS.txt
```

---

## 💾 **DATA ARTIFACTS**

### **Database Files**
**Pattern**: `{purpose}.db` *(snake_case_with_db_extension)*
**Logical Principle**: Clear purpose + standard database extension

```yaml
✅ CORRECT:
- application.db
- user_data.db
- system_logs.db
- test_data.db

❌ INCORRECT:
- Application.db
- user-data.db
- USER_DATA.db
- database_user_data.db
```

### **CSV Data Files**
**Pattern**: `{dataset_name}.csv` *(snake_case_descriptive)*
**Logical Principle**: Descriptive dataset name for clear identification

```yaml
✅ CORRECT:
- user_analytics.csv
- system_metrics.csv
- test_results.csv
- performance_data.csv

❌ INCORRECT:
- UserAnalytics.csv
- user-analytics.csv
- USER_ANALYTICS.csv
```

### **JSON Data Files**
**Pattern**: `{data_type}_data.json` *(snake_case_with_data_suffix)*
**Logical Principle**: Data type + data suffix for clear categorization

```yaml
✅ CORRECT:
- user_preferences_data.json
- system_state_data.json
- configuration_data.json

❌ INCORRECT:
- UserPreferencesData.json
- user-preferences-data.json
- DATA_USER_PREFERENCES.json
```

---

## 🏗️ **INFRASTRUCTURE ARTIFACTS**

### **Docker Files**
**Pattern**: `Dockerfile.{purpose}` *(standard_dockerfile_format)*
**Logical Principle**: Standard Docker convention + purpose specification

```yaml
✅ CORRECT:
- Dockerfile
- Dockerfile.development
- Dockerfile.production
- Dockerfile.testing

❌ INCORRECT:
- dockerfile
- docker-file
- DOCKERFILE
- Development.Dockerfile
```

### **Docker Compose Files**
**Pattern**: `docker-compose.{environment}.yml` *(standard_compose_format)*
**Logical Principle**: Standard Docker Compose convention

```yaml
✅ CORRECT:
- docker-compose.yml
- docker-compose.development.yml
- docker-compose.production.yml

❌ INCORRECT:
- dockerCompose.yml
- docker_compose.yml
- DOCKER_COMPOSE.yml
```

### **Script Files**
**Pattern**: `{action}_{purpose}.{ext}` *(snake_case_action_purpose)*
**Logical Principle**: Action + purpose for clear script identification

```yaml
✅ CORRECT:
- setup_environment.sh
- deploy_application.py
- backup_database.py
- cleanup_logs.sh

❌ INCORRECT:
- SetupEnvironment.sh
- setup-environment.sh
- SETUP_ENVIRONMENT.sh
```

---

## 📊 **MONITORING ARTIFACTS**

### **Log Files**
**Pattern**: `{component}_{date}.log` *(snake_case_with_date)*
**Logical Principle**: Component + date for temporal organization

```yaml
✅ CORRECT:
- application_20241201.log
- system_errors_20241201.log
- user_activity_20241201.log

❌ INCORRECT:
- Application_20241201.log
- application-20241201.log
- APPLICATION_20241201.log
```

### **Metrics Files**
**Pattern**: `{metric_type}_metrics.json` *(snake_case_with_metrics_suffix)*
**Logical Principle**: Metric type + metrics suffix for monitoring data

```yaml
✅ CORRECT:
- performance_metrics.json
- system_health_metrics.json
- user_engagement_metrics.json

❌ INCORRECT:
- PerformanceMetrics.json
- performance-metrics.json
- PERFORMANCE_METRICS.json
```

---

## 🎯 **SPECIALIZED CONTEXTS**

### **Keyword-Specific Rules (@agile context)**
When using `@agile` keyword, additional naming patterns apply:

```yaml
Agile Coordination Files:
- agile_{process}_coordination.py
- stakeholder_{type}_communication.md
- sprint_{number}_{artifact}_management.py

User Story Management:
- us_{id}_implementation_plan.md
- us_{id}_acceptance_criteria.md
- us_{id}_progress_tracking.json
```

### **Keyword-Specific Rules (@code context)**
When using `@code` keyword, additional naming patterns apply:

```yaml
Implementation Files:
- {feature}_implementation.py
- {module}_integration.py
- {component}_testing.py

Code Quality Files:
- {module}_code_review.md
- {feature}_refactoring_notes.md
- {component}_technical_debt.md
```

### **Keyword-Specific Rules (@debug context)**
When using `@debug` keyword, additional naming patterns apply:

```yaml
Debug Files:
- {issue}_debugging_session.md
- {bug}_root_cause_analysis.md
- {error}_fix_implementation.py

Error Tracking:
- {component}_error_log.txt
- {issue}_reproduction_steps.md
- {bug}_fix_validation.py
```

---

## 🎛️ **ENFORCEMENT RULES**

### **Automatic Validation**
ALL file operations must validate naming using:

```python
from utils.validation.universal_naming_validator import UniversalNamingValidator

# MANDATORY validation before file creation
validator = UniversalNamingValidator()
if not validator.validate_file_naming(file_path):
    raise NamingConventionViolation(f"File {file_path} violates naming conventions")
```

### **Git Pre-Commit Hooks**
```bash
#!/bin/bash
# Pre-commit naming validation
python utils/validation/validate_all_naming.py
if [ $? -ne 0 ]; then
    echo "❌ Commit blocked: Naming convention violations detected"
    exit 1
fi
```

### **CI/CD Pipeline Validation**
```yaml
naming_validation:
  runs-on: ubuntu-latest
  steps:
    - name: Validate File Naming
      run: python utils/validation/validate_all_naming.py --strict
```

---

## 📖 **QUICK REFERENCE SUMMARY**

### **Primary Patterns by File Type**

| **File Type** | **Pattern** | **Example** |
|---------------|-------------|-------------|
| **Epic Files** | `epic-{topic}.md` | `epic-formal-principles.md` |
| **User Stories** | `US-{XXX}.md` | `US-001.md` |
| **Sprint Files** | `sprint_{N}_{type}.md` | `sprint_1_summary.md` |
| **Agent Files** | `{name}_agent.py` | `requirements_analyst_agent.py` |
| **Team Files** | `{name}_team.py` | `cursor_ide_integration_expert_team.py` |
| **Utility Files** | `{function}_{type}.py` | `naming_validator.py` |
| **Test Files** | `test_{module}.py` | `test_naming_validator.py` |
| **Guide Files** | `{topic}_guide.md` | `development_guide.md` |
| **Rule Files** | `{rule}_rule.mdc` | `safety_first_principle_rule.mdc` |
| **Config Files** | `{purpose}_config.json` | `database_config.json` |
| **Database Files** | `{purpose}.db` | `application.db` |
| **Log Files** | `{component}_{date}.log` | `application_20241201.log` |

### **Universal Meta-Patterns**

1. **snake_case_with_underscores** - Most Python and documentation files
2. **lowercase-with-hyphens** - Epic files only  
3. **UPPER-CASE-CODES** - User story IDs only
4. **Standard conventions** - README.md, Dockerfile, requirements.txt

### **Forbidden Patterns**
- ❌ **CamelCase** - Never use for file names
- ❌ **SCREAMING_SNAKE_CASE** - Never use for file names  
- ❌ **Mixed-Case_Inconsistency** - Never mix conventions
- ❌ **spaces in names** - Never use spaces
- ❌ **Special$Characters** - Avoid except standard separators

---

## 🎯 **SUCCESS METRICS**

- **100%** compliance with naming conventions across ALL artifact types
- **Zero** automation failures due to naming inconsistencies  
- **Universal** adoption across all development workflows
- **Immediate** recognition of file purpose from name alone
- **Perfect** integration with tooling and automation

---

**This document is SACRED and AUTHORITATIVE for all file naming decisions in the AI-Dev-Agent project.**

**Last Updated**: December 2024  
**Status**: Comprehensive Reference - Follow Exactly  
**Enforcement**: Automatic validation required for all file operations
