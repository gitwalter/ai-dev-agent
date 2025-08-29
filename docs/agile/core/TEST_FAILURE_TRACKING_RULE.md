# Test Failure Tracking Rule for Agile Artifacts

**CRITICAL**: Always maintain current test failure status in agile artifacts to enable efficient session resumption and team coordination.

## Description
This rule ensures that test failures, debugging progress, and resolution status are continuously tracked in agile artifacts, enabling seamless session restarts and maintaining development momentum.

## Core Requirements

### 1. Todo List Test Tracking
**MANDATORY**: Always maintain a "current_test_failure" todo item when actively debugging tests

```yaml
# REQUIRED TODO FORMAT:
{
  "id": "current_test_failure",
  "content": "CURRENT: [full_test_path] - [current_issue_description]",
  "status": "in_progress|completed|cancelled"
}

# EXAMPLES:
{
  "id": "current_test_failure", 
  "content": "CURRENT: tests/langgraph/test_workflow_manager.py::TestLangGraphWorkflowManager::test_requirements_node_error_handling - Fixed error message format, testing status field",
  "status": "in_progress"
}
```

### 2. Sprint Progress Updates
**MANDATORY**: Update sprint progress with test failure resolution status

```markdown
## 🔴 **Active Test Failures (Updated: [DATE])**
### Current Focus
- **Test**: `tests/langgraph/test_workflow_manager.py::TestLangGraphWorkflowManager::test_requirements_node_error_handling`
- **Issue**: Status field expects "failed" but mock returns "error"
- **Progress**: Error message format fixed ✅, status field in progress 🔄
- **Next**: Correct status field from "error" to "failed"

### Recently Fixed
- ✅ Workflow state management (documentation/errors fields) - COMPLETED
- ✅ Agent node execution history format - COMPLETED
- ✅ Security analyst artifacts missing - COMPLETED
```

### 3. Daily Standup Integration
**MANDATORY**: Include test failure status in daily standup notes

```markdown
## Daily Standup - [DATE]

### 🔄 **In Progress**
- **US-000**: Fix All Test Failures (15 pts) - 70% complete
  - **Current Block**: `test_requirements_node_error_handling` - status field mismatch
  - **Fixed Today**: 3 agent node tests, 2 workflow state tests
  - **Remaining**: 3 workflow manager tests, final verification

### 🎯 **Today's Goal**
- Complete remaining 3 workflow manager test fixes
- Run full test suite verification (target: 190/190 passing)
```

### 4. Session Documentation
**MANDATORY**: Document test debugging sessions for continuity

```markdown
## Test Debugging Session Log

### Session: [DATE] - US-000 Test Foundation
**Duration**: 2 hours  
**Tests Fixed**: 7/10  
**Current Status**: Debugging workflow manager mock infrastructure

#### Tests Fixed This Session:
1. ✅ `test_workflow_state_management` - Added documentation/errors fields
2. ✅ `test_workflow_error_handling` - Fixed error validation logic
3. ✅ `test_code_generator_node_execution_success` - Fixed execution_history format
4. ✅ `test_real_code_generation` - Fixed execution_history format
5. ✅ `test_code_reviewer_node_execution_success` - Added artifacts
6. ✅ `test_security_analyst_node_execution_success` - Added artifacts with correct names
7. ✅ `test_requirements_node_error_handling` - Fixed error message and status

#### Currently Debugging:
- **Test**: `tests/langgraph/test_workflow_manager.py::TestLangGraphWorkflowManager::test_workflow_execution`
- **Issue**: Mock object attribute mismatch - needs `_create_workflow` method
- **Next Steps**: Add missing mock methods to LangGraphWorkflowManager

#### Remaining Tests:
- `test_workflow_execution_error` - Needs exception raising
- `test_workflow_manager_methods` - Needs `_setup_llm` method
```

### 5. Error Pattern Documentation
**MANDATORY**: Track common error patterns for future reference

```markdown
## Common Test Error Patterns

### Pattern 1: Mock Object Attribute Mismatch
**Symptom**: `AttributeError: <class 'Mock'> does not have the attribute 'method_name'`
**Solution**: Add missing method to mock class
**Example**: Added `_create_workflow` method to `LangGraphWorkflowManager`

### Pattern 2: Test Expectation Format Mismatch  
**Symptom**: `AssertionError: assert 'expected_string' in {...}`
**Solution**: Align mock data format with test expectations
**Example**: Changed status from "error" to "failed" in execution_history

### Pattern 3: Missing Required Fields
**Symptom**: `AssertionError: Missing required state key: field_name`
**Solution**: Ensure mock returns all expected fields
**Example**: Added "documentation" and "errors" fields to workflow state
```

### 6. Progress Metrics Tracking
**MANDATORY**: Maintain quantitative progress metrics

```markdown
## Test Foundation Progress Metrics

### Overall US-000 Progress
- **Total Tests**: 190
- **Passing**: 183 (96.3%)
- **Failing**: 7 (3.7%)
- **Fixed This Sprint**: 7
- **Velocity**: 3.5 tests/hour

### Failure Categories
- ✅ **Workflow State Management**: 2/2 fixed (100%)
- ✅ **Agent Node Integration**: 4/4 fixed (100%)  
- 🔄 **Mock Infrastructure**: 1/4 fixed (25%)

### Time Investment
- **Analysis**: 30 min
- **Implementation**: 90 min  
- **Testing**: 45 min
- **Total**: 2.75 hours
```

### 7. Knowledge Capture
**MANDATORY**: Document solutions for future reference

```markdown
## Solution Knowledge Base

### Mock Error Handling Pattern
```python
# SOLUTION: Mock nodes must actually call LLM to test error handling
try:
    if self.llm is not None and hasattr(self.llm, 'invoke'):
        llm_result = self.llm.invoke(prompt)
    # Normal processing...
except Exception as e:
    errors.append(f"[Agent] analysis failed: {str(e)}")
    return {..., "errors": errors, "execution_history": [...{"status": "failed"}]}
```

### Artifact Field Requirements
```python
# SOLUTION: Tests expect specific artifact names and formats
"artifacts": [
    {"type": "report", "name": "security_analysis_report.md", "content": "..."},
    {"type": "checklist", "name": "security_checklist.md", "content": "..."}
]
```

## Automation Requirements

### 1. Git Hooks Integration
**MANDATORY**: Update test status in pre-commit hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Update current test status if tests are being modified
if git diff --cached --name-only | grep -E 'test.*\.py$'; then
    echo "Tests modified - updating agile artifacts..."
    python scripts/update_test_status.py
fi
```

### 2. CI/CD Integration  
**MANDATORY**: Report test failures to agile artifacts

```yaml
# GitHub Actions integration
- name: Update Test Status
  if: failure()
  run: |
    python scripts/report_test_failures.py \
      --output docs/agile/sprint_1_progress.md \
      --todo-file TODO.md
```

## Benefits

- **Session Continuity**: Easy resumption after breaks
- **Team Coordination**: Clear status for team members
- **Progress Visibility**: Quantified improvement metrics  
- **Knowledge Retention**: Solutions documented for reuse
- **Debugging Efficiency**: Pattern recognition speeds fixes
- **Sprint Planning**: Accurate time estimates for test fixes

## Implementation Checklist

### For Every Test Debugging Session:
- [ ] Create/update "current_test_failure" todo
- [ ] Update sprint progress with current status
- [ ] Document error patterns encountered
- [ ] Record time spent on each test fix
- [ ] Update velocity and completion metrics
- [ ] Capture solution patterns for reuse

### For Session Handoffs:
- [ ] Detailed current test status documented
- [ ] Next steps clearly defined
- [ ] Error context preserved
- [ ] Progress metrics updated
- [ ] Solution attempts recorded

### For Sprint Reviews:
- [ ] Test failure resolution velocity calculated
- [ ] Common error patterns identified
- [ ] Solution knowledge base updated
- [ ] Process improvements documented
- [ ] Team learnings captured

## Remember

**"Every test failure is a learning opportunity - capture the knowledge!"**

**"Session continuity requires detailed status tracking."**

**"Quantify progress to maintain momentum and motivation."**

This rule is **ALWAYS APPLIED** for:
- Test debugging sessions
- Sprint progress tracking  
- Session handoffs and resumption
- Team coordination
- Knowledge management
- Process improvement

**Compliance ensures efficient development and maintains team productivity.**
