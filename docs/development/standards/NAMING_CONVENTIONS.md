# Universal Naming Conventions Standard

**Priority**: CRITICAL - Foundation Standard  
**Authority**: Project Development Team  
**Scope**: ALL project artifacts  
**Status**: MANDATORY COMPLIANCE REQUIRED

---

## 📐 **Philosophical Foundation**

**Fowler Principle**: Naming conventions must be **pragmatically useful** - they solve real problems and improve development velocity.

**Carnap Principle**: Naming must provide **systematic clarity** - every name should unambiguously communicate its purpose and category.

**Quine Principle**: Names establish **ontological relativity** - naming conventions define our development universe.

---

## 📋 **Agile Artifacts Naming**

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
**Pattern**: `{TYPE}_CATALOG.md` (UPPER_CASE_WITH_UNDERSCORES for strategic documents)

```yaml
✅ CORRECT:
- USER_STORY_CATALOG.md
- EPIC_OVERVIEW.md
- TASK_CATALOG.md
- SPRINT_SUMMARY.md

❌ INCORRECT:
- user_story_catalog.md
- Epic-Overview.md
- TaskCatalog.md
```

---

## 💻 **Code Artifacts Naming**

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

### **Class and Function Naming**
**Pattern**: Follow Python PEP 8 conventions

```python
# ✅ CORRECT: Classes use PascalCase
class ContextAwareRuleLoader:
    """Intelligent rule selection based on development context."""
    
    def optimize_efficiency(self):
        """Improve token efficiency through smart rule loading."""
        
# ✅ CORRECT: Functions and variables use snake_case
def validate_naming_conventions(file_path: str) -> bool:
    context_efficiency = 85.0
    rule_activation_status = "active"
    optimization_threshold = 0.8
    
# ❌ INCORRECT: Mixed naming patterns
class divine_rule_loader:  # Should be PascalCase
    def ManifestPerfection(self):  # Should be snake_case
        divineEfficiency = 85.0  # Should be snake_case
```

---

## 🧪 **Test Artifacts Naming**

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

## 📖 **Documentation Naming**

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
**Pattern**: `{topic}_rule.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- universal_naming_convention_rule.md
- file_organization_rule.md
- quality_validation_rule.md

❌ INCORRECT:
- UniversalNamingConventionRule.md
- file-organization-rule.md
- FileOrganizationRule.md
```

### **Standards Files**
**Pattern**: `{TOPIC}.md` (UPPER_CASE for formal standards)

```yaml
✅ CORRECT:
- NAMING_CONVENTIONS.md
- CODING_STANDARDS.md
- FILE_ORGANIZATION_STANDARDS.md

❌ INCORRECT:
- naming_conventions.md
- Coding-Standards.md
- fileOrganizationStandards.md
```

---

## ⚙️ **Configuration and Data Files**

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

### **Configuration Files**
**Pattern**: `{purpose}.(json|yaml|yml)` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- package.json
- docker_compose.yml
- ci_pipeline.yaml
- agent_settings.json

❌ INCORRECT:
- Package.json
- docker-compose.yml
- AgentSettings.json
```

---

## 🎯 **Quick Reference Summary**

### **Primary Patterns**
1. **lowercase_with_underscores** - Most files (Python, docs, configs)
2. **lowercase-with-hyphens** - Epic files only
3. **UPPER_CASE_WITH_UNDERSCORES** - Strategic documents and formal standards
4. **UPPER-CASE-CODES** - User story IDs only
5. **PascalCase** - Python classes
6. **snake_case** - Python functions and variables

### **File Extension Guidelines**
- **`.py`** - Python modules
- **`.md`** - Markdown documentation
- **`.json`** - JSON configuration/data
- **`.yaml/.yml`** - YAML configuration
- **`.db/.sqlite`** - Database files
- **`.log`** - Log files

---

## 🔧 **Enforcement and Validation**

### **Validation Tools**
```bash
# Validate file naming conventions
python utils/validation/universal_naming_validator.py --check {file_path}

# Auto-fix naming violations
python utils/quality/boyscout_naming_integration.py --fix {directory}
```

### **Required Implementation**
```python
from utils.validation.universal_naming_validator import UniversalNamingValidator

# REQUIRED: Use in all file operations
validator = UniversalNamingValidator()

def create_file(file_path: str, content: str) -> None:
    # MANDATORY: Validate naming before creation
    if not validator.validate_file_naming(file_path):
        raise NamingConventionViolation(f"File {file_path} violates naming conventions")
    
    # Proceed with creation
    Path(file_path).write_text(content)
```

---

## 📊 **Success Criteria**

- **100%** compliance with naming conventions across ALL artifact types
- **Zero** automation failures due to naming inconsistencies  
- **Immediate** recognition of purpose from file names
- **Systematic** organization enabling reliable navigation
- **Professional** appearance for all stakeholders

---

**Remember**: "Every name should immediately communicate its purpose, category, and relationship within our systematic development universe."

**Foundation**: Fowler (pragmatic utility) + Carnap (systematic clarity) + Quine (ontological consistency) = Universal Excellence
