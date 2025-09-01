# Universal Naming Convention Enforcement Rule

**CRITICAL**: Enforce universal naming conventions across ALL project artifacts based on Fowler/Carnap/Quine philosophical principles.

## Philosophical Foundation

**Fowler Principle**: Naming conventions must be pragmatically useful - they solve real problems and improve development velocity.

**Carnap Principle**: Naming must provide systematic clarity - every name should unambiguously communicate its purpose and category.

**Quine Principle**: Names establish ontological relativity - naming conventions define our development universe.

## Universal Enforcement Requirements

### 1. **All File Operations Must Validate Naming**
Every file creation, rename, or move operation must validate against naming conventions.

### 2. **All Agents Must Enforce Naming**
Every agent that creates or maintains files must validate naming conventions.

### 3. **All Automation Must Check Naming**
Every script, workflow, or automation must include naming validation.

## Enforcement Implementation

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

## Success Metrics

- **100%** compliance with naming conventions across ALL artifact types
- **Zero** automation failures due to naming inconsistencies
- **Universal** adoption across all development workflows

This rule is **TIER 1 CRITICAL** and applies to ALL development activities.
