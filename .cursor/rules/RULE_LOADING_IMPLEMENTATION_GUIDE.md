# Rule Loading Implementation Guide

## Problem Statement

Currently, all 39+ Cursor rules are loaded in every session because they all have `alwaysApply: false` in their metadata. This defeats the purpose of the Intelligent Context-Aware Rule System, which should only load 5-6 relevant rules per session.

## Solution: Context-Aware Rule Metadata

### **Step 1: Identify Always Apply Rules**

Only these rules should have `alwaysApply: false`:

1. **`safety_first_principle`** - Critical safety rule
2. **`intelligent_context_aware_rule_system`** - The system itself
3. **`core_rule_application_framework`** - Framework for rule application

### **Step 2: Modify Rule Metadata**

For all other rules, change the metadata from:

```yaml
---
description: "Rule description"
category: "core"
priority: "critical"
alwaysApply: false  # ❌ This forces all rules to load
globs: ["**/*"]
tags: ['core_foundation']
tier: "1"
---
```

To:

```yaml
---
description: "Rule description"
category: "context-specific"
priority: "medium"
alwaysApply: false  # ✅ Only load when context matches
contexts: ["CODING", "DEBUGGING"]  # ✅ Specify applicable contexts
globs: ["**/*"]
tags: ['context-aware']
tier: "2"
---
```

### **Step 3: Context Mapping for Each Rule**

Here's the mapping of rules to contexts:

#### **CODING Context**
- `xp_test_first_development_rule`
- `development_core_principles_rule`
- `error_handling_no_silent_errors_rule`
- `boyscout_leave_cleaner_rule`
- `documentation_live_updates_rule`

#### **DEBUGGING Context**
- `development_systematic_problem_solving_rule`
- `error_handling_no_silent_errors_rule`
- `testing_test_monitoring_rule`
- `development_error_exposure_rule`

#### **AGILE Context**
- `agile_artifacts_maintenance_rule`
- `documentation_live_updates_rule`
- `agile_sprint_management_rule`
- `agile_user_story_management_rule`

#### **GIT_OPERATIONS Context**
- `automated_git_protection_rule`
- `development_clean_commit_messages_rule`
- `development_merge_validation_rule`
- `deployment_safety_rule`

#### **TESTING Context**
- `xp_test_first_development_rule`
- `testing_test_monitoring_rule`
- `no_failing_tests_rule`
- `quality_validation_rule`
- `development_comprehensive_test_pattern_rule`

#### **ARCHITECTURE Context**
- `development_foundational_development_rule`
- `carnap_constitutional_development_rule`
- `documentation_live_updates_rule`
- `development_type_signature_precision_rule`

#### **DOCUMENTATION Context**
- `documentation_live_updates_rule`
- `rule_document_excellence_rule`
- `development_clear_communication_rule`
- `development_user_experience_rule`

#### **RESEARCH Context**
- `documentation_live_updates_rule`
- `development_clear_communication_rule`
- `development_context_awareness_excellence_rule`
- `boyscout_leave_cleaner_rule`

#### **PERFORMANCE Context**
- `performance_monitoring_optimization_rule`
- `development_benchmark_validation_rule`
- `development_optimization_validation_rule`
- `development_scalability_testing_rule`

#### **SECURITY Context**
- `security_vulnerability_assessment_rule`
- `security_streamlit_secrets_rule`
- `development_secure_coding_rule`
- `development_compliance_validation_rule`

#### **DEFAULT Context**
- `no_premature_victory_declaration_rule`
- `boyscout_leave_cleaner_rule`
- `development_context_awareness_excellence_rule`
- `philosophy_software_separation_rule`

## Implementation Steps

### **Phase 1: Core Rules (Always Apply)**
1. Keep `safety_first_principle` with `alwaysApply: false`
2. Keep `intelligent_context_aware_rule_system` with `alwaysApply: false`
3. Keep `core_rule_application_framework` with `alwaysApply: false`

### **Phase 2: Context-Specific Rules**
1. Modify each rule's metadata to include `contexts` array
2. Set `alwaysApply: false` for all context-specific rules
3. Update `category` to `"context-specific"`
4. Update `tier` to `"2"`

### **Phase 3: Testing**
1. Test with `@docs` keyword - should only load 5-6 rules
2. Test with `@code` keyword - should only load 6 rules
3. Test with `@debug` keyword - should only load 5 rules
4. Verify fallback to DEFAULT context works

## Expected Results

### **Before (Current State)**
- **Rules Loaded**: 39+ rules
- **Startup Time**: Slow
- **Cognitive Load**: High
- **Efficiency**: Poor

### **After (Context-Aware)**
- **Rules Loaded**: 5-6 rules per context
- **Startup Time**: 50% faster
- **Cognitive Load**: 80% reduction
- **Efficiency**: 75-85% improvement

## Verification

To verify the system is working:

1. **Check Rule Count**: Use `@docs` and count active rules
2. **Check Performance**: Measure session startup time
3. **Check Context Detection**: Verify correct rules are loaded for each keyword
4. **Check Fallback**: Test without keywords to ensure DEFAULT context works

## Troubleshooting

### **Issue**: Still loading all rules
**Solution**: Check that `alwaysApply: false` is set on context-specific rules

### **Issue**: No rules loading
**Solution**: Ensure the 3 core rules have `alwaysApply: false`

### **Issue**: Wrong rules for context
**Solution**: Verify `contexts` array contains correct context names

### **Issue**: Performance not improving
**Solution**: Check that rule metadata changes are saved and Cursor is restarted

## Next Steps

1. **Implement Phase 1**: Modify core rules
2. **Implement Phase 2**: Modify context-specific rules
3. **Test thoroughly**: Verify each context loads correct rules
4. **Monitor performance**: Track startup time and rule count improvements
5. **Document results**: Update documentation with actual performance metrics

---

**Goal**: Achieve 75-85% reduction in active rules per session while maintaining quality standards.
