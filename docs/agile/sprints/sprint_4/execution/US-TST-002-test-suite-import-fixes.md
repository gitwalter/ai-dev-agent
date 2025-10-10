# User Story: US-TST-002 - Test Suite Import Fixes and Stabilization

**Epic**: EPIC-0 - Development Excellence
**Sprint**: Sprint 4  
**Story Points**: 5  
**Priority**: HIGH  
**Created**: 2025-09-26  
**Status**: In Progress  

## Story Description

**As a** developer working on the AI-Dev-Agent system  
**I want** the test suite to run without import errors and collection failures  
**So that** I can reliably validate code changes and maintain system quality  

## Background

After reorganizing the `utils/` directory structure to improve code organization, multiple test files have import errors due to outdated import paths. The test suite currently fails to collect tests from 10 different modules, preventing effective testing and validation.

## Acceptance Criteria

### ✅ Primary Acceptance Criteria

1. **All Test Collection Passes**
   - [ ] All test files can be collected without import errors
   - [ ] No collection failures in any test module
   - [ ] Test discovery completes successfully

2. **Import Path Corrections**
   - [x] Fix `utils.safe_git_operations` → `utils.system.safe_git_operations`
   - [x] Fix `utils.reliable_context_integration` → `utils.system.context.reliable_context_integration`
   - [x] Fix `utils.structured_outputs` → `utils.core.structured_outputs`
   - [ ] Fix all remaining utils import paths

3. **Test Execution Success**
   - [ ] Unit tests run without errors
   - [ ] Integration tests execute properly
   - [ ] Infrastructure tests complete successfully

4. **Missing Module Handling**
   - [ ] Identify tests that reference non-existent modules
   - [ ] Either fix missing dependencies or disable/mock problematic tests
   - [ ] Document any disabled tests with clear reasoning

### 🎯 Secondary Acceptance Criteria

5. **Test Suite Performance**
   - [ ] Test collection time < 30 seconds
   - [ ] No hanging or infinite loop issues
   - [ ] Clear error messages for any remaining issues

6. **Documentation Updates**
   - [ ] Update test documentation if import patterns changed
   - [ ] Add notes about new utils directory structure
   - [ ] Document any test modifications made

## Technical Implementation

### 📋 Tasks Breakdown

1. **Import Path Analysis** (1 point)
   - [x] Identify all failing test modules
   - [x] Map old import paths to new locations
   - [x] Create systematic replacement strategy

2. **Systematic Import Fixes** (2 points)
   - [x] Fix infrastructure tests (`test_git_hooks_automation.py`)
   - [x] Fix integration tests (`test_context_system_validation.py`)
   - [x] Fix LangGraph tests (workflow integration, manager, agent nodes)
   - [ ] Fix workflow tests (orchestrator, task analyzer, composer)
   - [ ] Fix scripts tests (health monitoring)

3. **Missing Module Resolution** (1 point)
   - [ ] Identify modules that no longer exist
   - [ ] Create mock implementations or disable tests
   - [ ] Document reasoning for disabled tests

4. **Test Execution Validation** (1 point)
   - [ ] Run complete test suite successfully
   - [ ] Verify all tests can be collected
   - [ ] Confirm no regression in existing functionality

### 🔧 Technical Details

**Import Path Mappings Completed:**
```python
# BEFORE → AFTER
utils.safe_git_operations → utils.system.safe_git_operations
utils.reliable_context_integration → utils.system.context.reliable_context_integration  
utils.structured_outputs → utils.core.structured_outputs
utils.parsing.structured_outputs → utils.core.structured_outputs
```

**Modules Needing Investigation:**
- `utils.system_health_monitor` (not found)
- `utils.system.monitoring.proactive_alerting` (not found)
- `utils.monitoring.health_api_endpoints` (not found)
- `utils.monitoring.health_dashboard` (not found)

## Definition of Done

- [ ] **All test collection passes** - No import errors during test discovery
- [ ] **Test suite runs cleanly** - pytest execution completes without collection failures
- [ ] **Import paths updated** - All utils imports reflect new directory structure
- [ ] **Missing modules handled** - Non-existent modules are either created, mocked, or tests disabled
- [ ] **Documentation updated** - Any changes to test structure are documented
- [ ] **No regression** - Existing working tests continue to pass

## Notes and Considerations

### 🎯 Context Detection Impact
This story was triggered by the `@agile` keyword, demonstrating that our unified keyword detection system is working correctly for agile workflow management.

### 🔗 Dependencies
- Depends on completion of utils directory reorganization
- Blocks reliable CI/CD pipeline operation
- Required for US-UKD-001 (Unified Keyword Detection) validation

### 🚨 Risks
- Some health monitoring tests may reference features not yet implemented
- LangGraph tests might need additional dependency management
- Workflow tests could have complex import chains

### 📊 Success Metrics
- Test collection time: < 30 seconds
- Test execution success rate: 100%
- Import error count: 0
- Collection failure count: 0

## Sprint Integration

This story supports Sprint 4's focus on system stability and testing infrastructure. Completing this work enables reliable validation of other sprint features including the unified keyword detection system and agent monitoring improvements.

---

**Story Owner**: Development Team  
**Technical Lead**: AI Assistant  
**Stakeholders**: QA Team, DevOps Team  
**Estimated Completion**: Sprint 4 (Current Sprint)
