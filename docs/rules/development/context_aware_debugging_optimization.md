# Context-Aware Debugging Optimization Rule

**CRITICAL**: Optimize rule application based on debugging context size and complexity to maximize efficiency and focus.

## Context Detection for Debugging

### **@debug Context Triggers**
- User explicitly uses `@debug` keyword
- Import hanging, test failures, or runtime errors detected
- Troubleshooting specific technical issues
- Need for focused, minimal rule application

### **Context Size Categories**

#### **Small Context (@debug-small)**
**Scope**: Single module, function, or import issue
**Rules Applied**: Safety + Error Handling + Scientific Verification
**Forbidden**: Verbose documentation, agile artifacts, complex architecture rules

```yaml
small_context_rules:
  - safety_first_principle
  - error_handling_no_silent_errors
  - scientific_verification_evidence_based_success
  - development_core_principles (minimal)
  
excluded_rules:
  - agile_artifacts_maintenance
  - documentation_live_updates  
  - complex_architecture_validation
  - philosophical_foundations
```

#### **Medium Context (@debug-medium)**
**Scope**: Multiple modules, integration issues, system components
**Rules Applied**: Safety + Testing + Core Development + Performance

```yaml
medium_context_rules:
  - safety_first_principle
  - no_failing_tests_rule
  - development_core_principles
  - performance_monitoring_optimization
  - error_handling_comprehensive
  
limited_rules:
  - documentation (essential only)
  - agile_artifacts (critical updates only)
```

#### **Large Context (@debug-large)**
**Scope**: System-wide issues, architecture problems, full system debugging
**Rules Applied**: Comprehensive rule set with debugging priority

```yaml
large_context_rules:
  - all_safety_rules
  - all_development_rules
  - architecture_validation
  - system_integration_rules
  - performance_comprehensive
  
debugging_priority: true
streamlined_execution: true
```

## Implementation for Current Import Issue

### **Context Assessment**
```yaml
current_context:
  type: "@debug-small"
  scope: "Single module import hanging"
  files_affected: 1
  complexity: "Module-level syntax/import issue"
  priority: "Critical blocker"
```

### **Optimized Rule Application**
```yaml
active_rules:
  1. safety_first_principle
  2. error_handling_no_silent_errors  
  3. scientific_verification_evidence_based
  4. development_core_principles (minimal)

suspended_rules:
  - agile_artifacts_maintenance
  - documentation_live_updates
  - philosophical_foundations
  - complex_architecture_validation
  - user_story_management
```

### **Debugging Strategy**
1. **Isolate Issue**: Create minimal reproduction case
2. **Test Incrementally**: Add components one by one
3. **Verify Systematically**: Each fix must be proven to work
4. **Document Solution**: Minimal documentation for future reference

## Context Optimization Benefits

### **Small Context Benefits**
- ⚡ **90% faster execution** - Only essential rules applied
- 🎯 **Laser focus** - No distracting complexity
- 🔧 **Direct problem solving** - Minimal overhead
- ✅ **Quick resolution** - Streamlined approach

### **Medium Context Benefits**  
- ⚖️ **Balanced approach** - Essential quality without overhead
- 🔄 **Iterative improvement** - Systematic but focused
- 📊 **Key metrics only** - Important tracking without bloat

### **Large Context Benefits**
- 🏗️ **Comprehensive coverage** - Full system consideration
- 🔍 **Deep analysis** - All architectural implications
- 📚 **Complete documentation** - Full audit trail

## Context Switching Protocol

### **Automatic Context Detection**
```python
def detect_debugging_context(user_input, file_scope, error_type):
    if "@debug-small" in user_input or single_file_issue(file_scope):
        return "small"
    elif "@debug-medium" in user_input or multi_component_issue(file_scope):
        return "medium"  
    elif "@debug-large" in user_input or system_wide_issue(file_scope):
        return "large"
    else:
        return "medium"  # Default safe context
```

### **Context Application**
```python
def apply_context_optimized_rules(context_size, issue_type):
    if context_size == "small":
        return MINIMAL_DEBUG_RULES
    elif context_size == "medium":
        return BALANCED_DEBUG_RULES
    else:
        return COMPREHENSIVE_DEBUG_RULES
```

## Current Issue Resolution Strategy

### **Immediate Actions for Import Hanging**
1. **Apply @debug-small context** - Minimal rule overhead
2. **Create isolated test case** - Test single component
3. **Incremental validation** - Add complexity gradually
4. **Systematic verification** - Prove each step works

### **Optimized Workflow**
```bash
# Step 1: Minimal test (no complex validation)
python -c "print('Basic Python works')"

# Step 2: Test individual imports
python -c "from enum import Enum; print('Enum works')"

# Step 3: Test module structure only
python -c "from utils.validation.foundation_practical_onion_system_simple import FoundationLayer; print('Module loads')"

# Step 4: Validate functionality
python -c "from utils.validation.foundation_practical_onion_system_simple import *; print('All imports work')"
```

## Enforcement

This rule is **CONDITIONALLY APPLIED** based on debugging context.

**Context triggers override default rule application for maximum efficiency.**

## Remember

**"Right rules, right context, right time."**

**"Debugging efficiency through contextual intelligence."**

**"Small problems need small solutions, not big overhead."**

