# Test Catalogue - Comprehensive Test Documentation

**Generated**: 2025-10-10 11:56:33  
**Generator**: Test Catalogue Generator v1.0  
**Purpose**: Complete inventory and documentation of all test cases

## 📊 **Test Suite Overview**

| Metric | Value |
|--------|--------|
| **Total Test Files** | 61 |
| **Total Test Classes** | 164 |
| **Total Test Functions** | 545 |
| **Total Tests** | 709 |
| **Total Size** | 946.5 KB |
| **Coverage Categories** | 10 |

## 🎯 **Test Categories**

- **Agile Tests**: 1 files, 14 tests
- **Infrastructure Tests**: 2 files, 52 tests
- **Integration Tests**: 13 files, 112 tests
- **Isolated Tests**: 1 files, 1 tests
- **LangGraph Tests**: 4 files, 24 tests
- **Root Tests**: 20 files, 208 tests
- **Security Tests**: 1 files, 14 tests
- **Supervisor Tests**: 2 files, 21 tests
- **System Tests**: 1 files, 0 tests
- **Unit Tests**: 16 files, 263 tests


## 📁 **Agile Tests**

### `agile\test_agile_artifacts_automation.py` (14 tests)

**Description**: Test-driven tests for Agile Artifacts Automation System

This system automates the tedious manual process of updating multiple agile artifacts
when stories are completed, following the Live Documentation Updates Rule.

| Metric | Value |
|--------|--------|
| **File Size** | 20.5 KB |
| **Test Classes** | 1 |
| **Test Functions** | 13 |
| **Total Tests** | 14 |

#### Test Classes

- **`TestAgileArtifactsAutomator`** (Line 36)
  - *Test-driven tests for the main AgileArtifactsAutomator class*
  - Category: General

#### Test Functions

- **`test_automator_initialization`** (Line 144)
  - *Test that the automator initializes correctly with docs directory*
  - Category: General
- **`test_story_completion_data_structure`** (Line 161)
  - *Test that story completion data structure is properly defined*
  - Category: General
- **`test_update_daily_standup`** (Line 192)
  - *Test that daily standup is updated correctly when story completes*
  - Category: General
- **`test_update_sprint_progress`** (Line 219)
  - *Test that sprint progress tracking is updated correctly*
  - Category: General
- **`test_update_velocity_tracking`** (Line 247)
  - *Test that velocity tracking is updated with new completion*
  - Category: General
- **`test_update_sprint_backlog`** (Line 274)
  - *Test that sprint backlog is updated to mark story as complete*
  - Category: General
- **`test_update_user_stories`** (Line 304)
  - *Test that user stories master document is updated*
  - Category: General
- **`test_update_all_artifacts`** (Line 331)
  - *Test that all artifacts are updated in a single operation*
  - Category: General
- **`test_validation_after_updates`** (Line 366)
  - *Test that validation ensures all artifacts are consistent after updates*
  - Category: General
- **`test_timestamp_management`** (Line 392)
  - *Test that timestamps are properly managed across all artifacts*
  - Category: General
- **`test_backup_and_rollback`** (Line 423)
  - *Test that backup and rollback functionality works*
  - Category: General
- **`test_error_handling`** (Line 454)
  - *Test that errors are handled gracefully during updates*
  - Category: General
- **`test_concurrent_updates_protection`** (Line 478)
  - *Test that concurrent updates are protected against conflicts*
  - Category: General

---


## 📁 **Infrastructure Tests**

### `infrastructure\test_automated_testing_pipeline.py` (29 tests)

**Description**: Test-Driven Development tests for US-002: Fully Automated Testing Pipeline

These tests define the expected behavior of the automated testing pipeline
before any implementation exists.

| Metric | Value |
|--------|--------|
| **File Size** | 24.5 KB |
| **Test Classes** | 7 |
| **Test Functions** | 22 |
| **Total Tests** | 29 |

#### Test Classes

- **`TestAutomatedTestingPipeline`** (Line 47)
  - *Test-driven tests for the main AutomatedTestingPipeline class*
  - Category: General
- **`TestCoverageTracker`** (Line 171)
  - *Test-driven tests for the CoverageTracker class*
  - Category: General
- **`TestCommitHookManager`** (Line 249)
  - *Test-driven tests for the CommitHookManager class*
  - Category: General
- **`TestTestReporter`** (Line 320)
  - *Test-driven tests for the AutomatedTestReporter class*
  - Category: General
- **`TestDeploymentBlocker`** (Line 400)
  - *Test-driven tests for the DeploymentBlocker class*
  - Category: General
- **`TestPerformanceValidation`** (Line 473)
  - *Test-driven tests for performance validation within the automated testing pipeline*
  - Category: Performance
- **`TestIntegrationScenarios`** (Line 525)
  - *Integration tests for the complete automated testing pipeline*
  - Category: Integration

#### Test Functions

- **`test_pipeline_initialization`** (Line 71)
  - *Test that the automated testing pipeline initializes correctly*
  - Category: General
- **`test_pipeline_runs_automatically_on_commit`** (Line 90)
  - *Test that the pipeline runs automatically when code is committed*
  - Category: General
- **`test_pipeline_blocks_deployment_on_test_failure`** (Line 108)
  - *Test that deployment is blocked when tests fail*
  - Category: General
- **`test_pipeline_requires_90_percent_coverage`** (Line 128)
  - *Test that pipeline enforces 90%+ test coverage requirement*
  - Category: General
- **`test_pipeline_allows_deployment_when_all_tests_pass`** (Line 147)
  - *Test that deployment is allowed when all tests pass and coverage is sufficient*
  - Category: General
- **`test_coverage_tracker_initialization`** (Line 178)
  - *Test that coverage tracker initializes with correct configuration*
  - Category: General
- **`test_coverage_tracker_runs_coverage_analysis`** (Line 191)
  - *Test that coverage tracker runs coverage analysis*
  - Category: General
- **`test_coverage_tracker_identifies_uncovered_lines`** (Line 209)
  - *Test that coverage tracker identifies uncovered lines*
  - Category: General
- **`test_coverage_tracker_enforces_minimum_coverage`** (Line 231)
  - *Test that coverage tracker enforces minimum coverage requirement*
  - Category: General
- **`test_commit_hook_manager_installs_hooks`** (Line 266)
  - *Test that commit hook manager installs necessary Git hooks*
  - Category: General
- **`test_commit_hooks_trigger_test_execution`** (Line 283)
  - *Test that commit hooks trigger test execution*
  - Category: General
- **`test_commit_hooks_block_bad_commits`** (Line 301)
  - *Test that commit hooks block commits when tests fail*
  - Category: General
- **`test_test_reporter_generates_detailed_report`** (Line 327)
  - *Test that test reporter generates detailed test results*
  - Category: General
- **`test_test_reporter_sends_notifications`** (Line 353)
  - *Test that test reporter sends notifications for test results*
  - Category: General
- **`test_test_reporter_creates_html_report`** (Line 376)
  - *Test that test reporter creates HTML reports*
  - Category: General
- **`test_deployment_blocker_blocks_on_test_failure`** (Line 407)
  - *Test that deployment blocker prevents deployment when tests fail*
  - Category: General
- **`test_deployment_blocker_blocks_on_low_coverage`** (Line 429)
  - *Test that deployment blocker prevents deployment when coverage is low*
  - Category: General
- **`test_deployment_blocker_allows_good_deployments`** (Line 451)
  - *Test that deployment blocker allows deployment when all criteria are met*
  - Category: General
- **`test_performance_validation_runs_automatically`** (Line 480)
  - *Test that performance validation runs as part of the automated pipeline*
  - Category: Performance
- **`test_performance_validation_blocks_slow_code`** (Line 502)
  - *Test that performance validation blocks deployment of slow code*
  - Category: Performance
- **`test_complete_automated_workflow`** (Line 546)
  - *Test the complete automated testing workflow from commit to deployment*
  - Category: System
- **`test_zero_manual_intervention_requirement`** (Line 565)
  - *Test that the pipeline requires absolutely zero manual intervention*
  - Category: General

---

### `infrastructure\test_git_hooks_automation.py` (23 tests)

**Description**: Infrastructure Tests for Git Hooks Automation

This module tests the complete git hooks automation system including:
- Pre-push hook functionality
- Post-merge hook functionality  
- Safe git operations for database management
- End-to-end push-pull cycles
- Error handling and recovery
- IDE and command line integration

Excellence Standards Applied:
- Comprehensive test coverage (all scenarios)
- Evidence-based validation (actual execution)
- Error exposure (no silent failures)
- Complete workflow testing (end-to-end).

| Metric | Value |
|--------|--------|
| **File Size** | 15.1 KB |
| **Test Classes** | 4 |
| **Test Functions** | 19 |
| **Total Tests** | 23 |

#### Test Classes

- **`TestGitHooksInfrastructure`** (Line 38)
  - *Comprehensive tests for git hooks automation infrastructure*
  - Category: Infrastructure
- **`TestGitHooksEndToEndScenarios`** (Line 220)
  - *End-to-end scenario tests for git hooks automation*
  - Category: General
- **`TestGitHooksErrorScenarios`** (Line 277)
  - *Test error scenarios and edge cases for git hooks automation*
  - Category: General
- **`TestGitHooksDocumentationAndCompliance`** (Line 323)
  - *Test documentation and compliance aspects of git hooks automation*
  - Category: General

#### Test Functions

- **`test_safe_git_operations_initialization`** (Line 55)
  - *Test SafeGitOperations initializes correctly*
  - Category: General
- **`test_git_status_check`** (Line 64)
  - *Test git status checking functionality*
  - Category: General
- **`test_database_files_detection`** (Line 73)
  - *Test detection of staged database files*
  - Category: General
- **`test_safe_git_operations_command_line_interface`** (Line 82)
  - *Test the command line interface of safe_git_operations*
  - Category: General
- **`test_safe_git_operations_pre_merge_command`** (Line 94)
  - *Test pre-merge command functionality*
  - Category: General
- **`test_safe_git_operations_post_merge_command`** (Line 106)
  - *Test post-merge command functionality*
  - Category: General
- **`test_git_hooks_files_exist`** (Line 118)
  - *Test that required git hook files exist*
  - Category: General
- **`test_powershell_pre_push_hook_execution`** (Line 142)
  - *Test PowerShell pre-push hook execution on Windows*
  - Category: General
- **`test_powershell_post_merge_hook_execution`** (Line 159)
  - *Test PowerShell post-merge hook execution on Windows*
  - Category: General
- **`test_error_handling_invalid_command`** (Line 175)
  - *Test error handling for invalid commands*
  - Category: General
- **`test_prepare_for_pull_functionality`** (Line 187)
  - *Test prepare_for_pull method functionality*
  - Category: General
- **`test_cleanup_after_pull_functionality`** (Line 201)
  - *Test cleanup_after_pull method functionality*
  - Category: General
- **`test_complete_push_pull_cycle_simulation`** (Line 232)
  - *Test simulated complete push-pull cycle*
  - Category: System
- **`test_database_file_handling_workflow`** (Line 244)
  - *Test database file handling workflow*
  - Category: System
- **`test_git_automation_wrapper_integration`** (Line 256)
  - *Test integration with git automation wrapper*
  - Category: Integration
- **`test_missing_git_repository`** (Line 287)
  - *Test behavior when not in a git repository*
  - Category: General
- **`test_git_command_failure_handling`** (Line 304)
  - *Test handling of git command failures*
  - Category: General
- **`test_safe_git_operations_has_proper_docstrings`** (Line 332)
  - *Test that SafeGitOperations has proper documentation*
  - Category: General
- **`test_git_hooks_contain_required_comments`** (Line 345)
  - *Test that git hooks contain proper documentation*
  - Category: General

---


## 📁 **Integration Tests**

### `integration\agents\test_specialized_subagent_team.py` (41 tests)

**Description**: Comprehensive Test Suite for Specialized Subagent Team

Tests the specialized keyword-role-subagent team implementation for Sprint 2
optimization, validating all agent roles, collaboration patterns, and integration.

| Metric | Value |
|--------|--------|
| **File Size** | 25.4 KB |
| **Test Classes** | 12 |
| **Test Functions** | 29 |
| **Total Tests** | 41 |

#### Test Classes

- **`TestSpecializedSubagentTeam`** (Line 45)
  - *Test suite for the specialized subagent team*
  - Category: General
- **`TestIndividualAgents`** (Line 113)
  - *Test individual agent functionality*
  - Category: General
- **`TestAgentSpecializations`** (Line 189)
  - *Test agent specializations and capabilities*
  - Category: General
- **`TestAgentCollaboration`** (Line 228)
  - *Test agent collaboration patterns*
  - Category: General
- **`TestModelSelection`** (Line 254)
  - *Test AI model selection based on agent complexity*
  - Category: General
- **`TestTaskExecution`** (Line 294)
  - *Test task execution and response handling*
  - Category: General
- **`TestPerformanceMetrics`** (Line 351)
  - *Test performance metrics and tracking*
  - Category: Performance
- **`TestSprint2Optimization`** (Line 389)
  - *Test Sprint 2 optimization capabilities*
  - Category: General
- **`TestTeamStatus`** (Line 464)
  - *Test team status and monitoring*
  - Category: General
- **`TestErrorHandling`** (Line 504)
  - *Test error handling and recovery*
  - Category: General
- **`TestIntegration`** (Line 543)
  - *Integration tests for the specialized subagent team*
  - Category: Integration
- **`TestPerformance`** (Line 605)
  - *Performance tests for the specialized subagent team*
  - Category: Performance

#### Test Functions

- **`test_team_initialization`** (Line 70)
  - *Test that the team initializes correctly with all agents*
  - Category: General
- **`test_keyword_detection`** (Line 90)
  - *Test keyword detection for agent routing*
  - Category: General
- **`test_architect_agent_initialization`** (Line 129)
  - *Test architect agent initialization*
  - Category: General
- **`test_developer_agent_initialization`** (Line 139)
  - *Test developer agent initialization*
  - Category: General
- **`test_tester_agent_initialization`** (Line 149)
  - *Test tester agent initialization*
  - Category: General
- **`test_optimizer_agent_initialization`** (Line 159)
  - *Test optimizer agent initialization*
  - Category: General
- **`test_coordinator_agent_initialization`** (Line 169)
  - *Test coordinator agent initialization*
  - Category: General
- **`test_documenter_agent_initialization`** (Line 179)
  - *Test documenter agent initialization*
  - Category: General
- **`test_architect_specializations`** (Line 192)
  - *Test architect agent specializations*
  - Category: General
- **`test_developer_specializations`** (Line 204)
  - *Test developer agent specializations*
  - Category: General
- **`test_tester_specializations`** (Line 216)
  - *Test tester agent specializations*
  - Category: General
- **`test_collaboration_patterns`** (Line 231)
  - *Test that agents have correct collaboration patterns*
  - Category: General
- **`test_model_selection_critical`** (Line 258)
  - *Test critical complexity model selection*
  - Category: General
- **`test_model_selection_complex`** (Line 271)
  - *Test complex complexity model selection*
  - Category: General
- **`test_model_selection_simple`** (Line 283)
  - *Test simple complexity model selection*
  - Category: General
- **`test_architect_prompt_generation`** (Line 316)
  - *Test architect agent prompt generation*
  - Category: General
- **`test_developer_prompt_generation`** (Line 335)
  - *Test developer agent prompt generation*
  - Category: General
- **`test_performance_metrics_initialization`** (Line 354)
  - *Test that agents initialize performance metrics*
  - Category: Performance
- **`test_performance_metrics_update`** (Line 361)
  - *Test performance metrics update*
  - Category: Performance
- **`test_optimization_recommendations`** (Line 397)
  - *Test optimization recommendations generation*
  - Category: General
- **`test_next_actions_generation`** (Line 409)
  - *Test next actions generation*
  - Category: General
- **`test_success_metrics_calculation`** (Line 421)
  - *Test success metrics calculation*
  - Category: General
- **`test_team_status_structure`** (Line 472)
  - *Test team status structure*
  - Category: General
- **`test_agent_status_details`** (Line 481)
  - *Test agent status details*
  - Category: General
- **`test_missing_api_key_error`** (Line 508)
  - *Test error handling for missing API key*
  - Category: Integration
- **`test_agent_task_failure_handling`** (Line 517)
  - *Test handling of agent task failures*
  - Category: General
- **`test_team_integration_workflow`** (Line 569)
  - *Test complete team integration workflow*
  - Category: Integration
- **`test_agent_initialization_performance`** (Line 608)
  - *Test that agent initialization is performant*
  - Category: Performance
- **`test_keyword_detection_performance`** (Line 624)
  - *Test keyword detection performance*
  - Category: Performance

---

### `integration\prompts\test_prompt_management_system.py` (31 tests)

**Description**: Comprehensive Test Suite for Prompt Management System (US-PE-02)

This test file validates all the new components implemented for US-PE-02:
- Quality Assessment System
- Backup and Recovery System  
- Audit Trail System
- System Integration

Author: AI-Dev-Agent System
Version: 2.

| Metric | Value |
|--------|--------|
| **File Size** | 26.4 KB |
| **Test Classes** | 5 |
| **Test Functions** | 26 |
| **Total Tests** | 31 |

#### Test Classes

- **`TestPromptQualityAssessment`** (Line 44)
  - *Test the prompt quality assessment system*
  - Category: General
- **`TestPromptBackupRecovery`** (Line 170)
  - *Test the backup and recovery system*
  - Category: General
- **`TestPromptAuditTrail`** (Line 270)
  - *Test the audit trail system*
  - Category: General
- **`TestPromptManagementSystemIntegration`** (Line 420)
  - *Test the integrated prompt management system*
  - Category: Integration
- **`TestUSPE02Completeness`** (Line 552)
  - *Test that US-PE-02 requirements are fully implemented*
  - Category: System

#### Test Functions

- **`test_quality_assessment_creation`** (Line 104)
  - *Test that quality assessor can be created*
  - Category: General
- **`test_good_prompt_assessment`** (Line 109)
  - *Test assessment of a well-written prompt*
  - Category: General
- **`test_poor_prompt_assessment`** (Line 121)
  - *Test assessment of a poorly written prompt*
  - Category: General
- **`test_complex_prompt_assessment`** (Line 132)
  - *Test assessment of a complex prompt*
  - Category: General
- **`test_quality_dimensions`** (Line 142)
  - *Test that all quality dimensions are assessed*
  - Category: General
- **`test_quality_benchmarks`** (Line 156)
  - *Test quality benchmark functionality*
  - Category: General
- **`test_backup_system_creation`** (Line 211)
  - *Test that backup system can be created*
  - Category: System
- **`test_full_backup_creation`** (Line 216)
  - *Test creation of a full backup*
  - Category: General
- **`test_backup_metadata_storage`** (Line 230)
  - *Test that backup metadata is properly stored*
  - Category: General
- **`test_data_integrity_check`** (Line 241)
  - *Test data integrity checking*
  - Category: General
- **`test_backup_cleanup`** (Line 250)
  - *Test backup cleanup functionality*
  - Category: General
- **`test_audit_trail_creation`** (Line 310)
  - *Test that audit trail system can be created*
  - Category: General
- **`test_change_recording`** (Line 315)
  - *Test recording of prompt changes*
  - Category: General
- **`test_change_history_retrieval`** (Line 331)
  - *Test retrieval of change history*
  - Category: General
- **`test_compliance_checking`** (Line 353)
  - *Test compliance checking functionality*
  - Category: General
- **`test_audit_summary`** (Line 374)
  - *Test audit summary generation*
  - Category: General
- **`test_user_activity_tracking`** (Line 395)
  - *Test user activity tracking*
  - Category: General
- **`test_system_creation`** (Line 469)
  - *Test that the integrated system can be created*
  - Category: System
- **`test_system_status`** (Line 474)
  - *Test system status reporting*
  - Category: System
- **`test_quality_assessment_integration`** (Line 493)
  - *Test quality assessment integration*
  - Category: Integration
- **`test_backup_creation_integration`** (Line 513)
  - *Test backup creation integration*
  - Category: Integration
- **`test_audit_summary_integration`** (Line 522)
  - *Test audit summary integration*
  - Category: Integration
- **`test_system_health_report`** (Line 531)
  - *Test system health report generation*
  - Category: System
- **`test_critical_requirements_implementation`** (Line 555)
  - *Test that all critical requirements are implemented*
  - Category: General
- **`test_acceptance_criteria_coverage`** (Line 573)
  - *Test that all acceptance criteria are covered*
  - Category: General
- **`test_definition_of_done_validation`** (Line 600)
  - *Test that Definition of Done criteria are met*
  - Category: General

---

### `integration\test_adaptive_retrieval_comprehensive.py` (2 tests)

**Description**: Comprehensive integration tests for Adaptive Retrieval System.

| Metric | Value |
|--------|--------|
| **File Size** | 20.9 KB |
| **Test Classes** | 2 |
| **Test Functions** | 0 |
| **Total Tests** | 2 |

#### Test Classes

- **`TestComprehensiveAdaptiveRetrieval`** (Line 25)
  - *Comprehensive tests for adaptive retrieval with diverse query types*
  - Category: General
- **`TestPerformanceBenchmarking`** (Line 391)
  - *Performance benchmarking tests for adaptive retrieval*
  - Category: Performance

---

### `integration\test_agent_execution.py` (2 tests)

**Description**: Tests for actual agent execution to identify and fix the "src property must be a valid json object" error.

| Metric | Value |
|--------|--------|
| **File Size** | 22.7 KB |
| **Test Classes** | 2 |
| **Test Functions** | 0 |
| **Total Tests** | 2 |

#### Test Classes

- **`TestAgentExecution`** (Line 27)
  - *Test actual agent execution to identify the src property error*
  - Category: General
- **`TestAgentErrorHandling`** (Line 422)
  - *Test error handling in agents*
  - Category: General

---

### `integration\test_api_key_validation.py` (1 tests)

**Description**: Simple API key validation test using Streamlit secrets.

| Metric | Value |
|--------|--------|
| **File Size** | 1.2 KB |
| **Test Classes** | 0 |
| **Test Functions** | 1 |
| **Total Tests** | 1 |

#### Test Functions

- **`test_api_key`** (Line 9)
  - *Test if the API key is valid using Streamlit secrets*
  - Category: Integration

---

### `integration\test_context_aware_agent.py` (5 tests)

**Description**: Integration Tests for Context-Aware Agents
==========================================

Tests the complete integration of ContextEngine with agents,
demonstrating real-world usage patterns.

| Metric | Value |
|--------|--------|
| **File Size** | 15.5 KB |
| **Test Classes** | 5 |
| **Test Functions** | 0 |
| **Total Tests** | 5 |

#### Test Classes

- **`TestContextAwareAgentBasics`** (Line 33)
  - *Test basic ContextAwareAgent functionality*
  - Category: General
- **`TestContextRetrieval`** (Line 78)
  - *Test context retrieval functionality*
  - Category: General
- **`TestContextAwareExecution`** (Line 142)
  - *Test execute_with_context functionality*
  - Category: General
- **`TestRealWorldScenarios`** (Line 198)
  - *Test real-world usage scenarios*
  - Category: General
- **`TestPerformance`** (Line 283)
  - *Test performance characteristics*
  - Category: Performance

---

### `integration\test_context_system_validation.py` (9 tests)

**Description**: Comprehensive validation and testing for context-aware rule system.

| Metric | Value |
|--------|--------|
| **File Size** | 7.9 KB |
| **Test Classes** | 1 |
| **Test Functions** | 8 |
| **Total Tests** | 9 |

#### Test Classes

- **`TestContextSystemValidation`** (Line 20)
  - *Comprehensive validation tests for context system*
  - Category: System

#### Test Functions

- **`test_context_detection_accuracy`** (Line 28)
  - *Test context detection accuracy for all keywords*
  - Category: General
- **`test_rule_count_reduction`** (Line 55)
  - *Test that rule count is significantly reduced per context*
  - Category: General
- **`test_file_generation_and_reload`** (Line 71)
  - *Test that *
  - Category: Performance
- **`test_context_verification`** (Line 81)
  - *Test context verification functionality*
  - Category: General
- **`test_error_handling_robustness`** (Line 94)
  - *Test error handling and fallback mechanisms*
  - Category: General
- **`test_performance_benchmarks`** (Line 110)
  - *Test performance of context switching*
  - Category: Performance
- **`test_system_status_reporting`** (Line 137)
  - *Test system status and monitoring*
  - Category: System
- **`test_context_history_tracking`** (Line 150)
  - *Test context history and tracking functionality*
  - Category: General

---

### `integration\test_cursor_integration.py` (1 tests)

**Description**: Test Cursor Integration
======================

Debug script to test cursor integration functionality.

| Metric | Value |
|--------|--------|
| **File Size** | 1.9 KB |
| **Test Classes** | 0 |
| **Test Functions** | 1 |
| **Total Tests** | 1 |

#### Test Functions

- **`test_cursor_integration`** (Line 17)
  - *Test cursor integration step by step*
  - Category: Integration

---

### `integration\test_dialogues.py` (0 tests)

| Metric | Value |
|--------|--------|
| **File Size** | 1.0 B |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---

### `integration\test_gemini_integration.py` (3 tests)

**Description**: Integration tests for Gemini API to identify and fix the "src property must be a valid json object" error.

| Metric | Value |
|--------|--------|
| **File Size** | 16.5 KB |
| **Test Classes** | 3 |
| **Test Functions** | 0 |
| **Total Tests** | 3 |

#### Test Classes

- **`TestGeminiAPIIntegration`** (Line 16)
  - *Integration tests for Gemini API to identify the src property error*
  - Category: Integration
- **`TestGeminiAPIErrorHandling`** (Line 253)
  - *Test error handling for Gemini API issues*
  - Category: Integration
- **`TestGeminiAPIResponseParsing`** (Line 305)
  - *Test parsing of different Gemini API response formats*
  - Category: Integration

---

### `integration\test_quality_assurance_integration.py` (6 tests)

**Description**: Integration tests for Quality Assurance System.

| Metric | Value |
|--------|--------|
| **File Size** | 8.0 KB |
| **Test Classes** | 1 |
| **Test Functions** | 5 |
| **Total Tests** | 6 |

#### Test Classes

- **`TestQualityAssuranceIntegration`** (Line 15)
  - *Test quality assurance system integration with agents*
  - Category: Integration

#### Test Functions

- **`test_agent_quality_gates`** (Line 43)
  - *Test quality gates for multiple agent types efficiently*
  - Category: General
- **`test_quality_gate_failure_scenario`** (Line 60)
  - *Test quality gate failure scenario*
  - Category: General
- **`test_quality_metrics_tracking`** (Line 90)
  - *Test that quality metrics are properly tracked*
  - Category: General
- **`test_validation_history_tracking`** (Line 138)
  - *Test that validation history is properly tracked*
  - Category: General
- **`test_gate_results_tracking`** (Line 168)
  - *Test that gate results are properly tracked*
  - Category: General

---

### `integration\test_ui_adaptive_retrieval.py` (9 tests)

**Description**: Integration tests for Adaptive Retrieval UI components.

| Metric | Value |
|--------|--------|
| **File Size** | 10.5 KB |
| **Test Classes** | 1 |
| **Test Functions** | 8 |
| **Total Tests** | 9 |

#### Test Classes

- **`TestAdaptiveRetrievalUIIntegration`** (Line 20)
  - *Integration tests for the Adaptive Retrieval UI components*
  - Category: Integration

#### Test Functions

- **`test_ui_integration_imports`** (Line 236)
  - *Test that all required modules can be imported*
  - Category: Integration
- **`test_retrieval_mode_selection`** (Line 55)
  - *Test retrieval mode selection updates session state correctly*
  - Category: General
- **`test_manual_chunk_count_validation`** (Line 78)
  - *Test manual chunk count slider validation and feedback*
  - Category: General
- **`test_swarm_parameter_passing`** (Line 102)
  - *Test that adaptive retrieval parameters are correctly passed to swarm*
  - Category: General
- **`test_adaptive_decision_display`** (Line 141)
  - *Test adaptive decision info is properly displayed in debug mode*
  - Category: General
- **`test_session_state_initialization`** (Line 173)
  - *Test session state is properly initialized for adaptive retrieval*
  - Category: General
- **`test_mode_specific_ui_visibility`** (Line 190)
  - *Test UI elements appear/disappear based on mode selection*
  - Category: General
- **`test_help_text_comprehensiveness`** (Line 207)
  - *Test that help text provides comprehensive guidance*
  - Category: General

---

### `langgraph\integration\test_workflow_integration.py` (2 tests)

**Description**: Integration tests for complete workflow orchestration.

| Metric | Value |
|--------|--------|
| **File Size** | 44.3 KB |
| **Test Classes** | 1 |
| **Test Functions** | 1 |
| **Total Tests** | 2 |

#### Test Classes

- **`TestCompleteWorkflowIntegration`** (Line 64)
  - *Integration tests for complete workflow execution*
  - Category: Integration

#### Test Functions

- **`test_state`** (Line 111)
  - *Create test state for complete workflow*
  - Category: General

---


## 📁 **Isolated Tests**

### `isolated\test_test_generator_isolated.py` (1 tests)

**Description**: Isolated test for Test Generator Agent to fix parsing issues.

| Metric | Value |
|--------|--------|
| **File Size** | 7.9 KB |
| **Test Classes** | 1 |
| **Test Functions** | 0 |
| **Total Tests** | 1 |

#### Test Classes

- **`TestTestGeneratorIsolated`** (Line 29)
  - *Isolated test cases for Test Generator Agent*
  - Category: Unit

---


## 📁 **LangGraph Tests**

### `langgraph\test_basic_workflow.py` (10 tests)

**Description**: Basic LangGraph Workflow Tests.

| Metric | Value |
|--------|--------|
| **File Size** | 15.7 KB |
| **Test Classes** | 2 |
| **Test Functions** | 8 |
| **Total Tests** | 10 |

#### Test Classes

- **`TestBasicLangGraphWorkflow`** (Line 56)
  - *Basic tests for LangGraph workflow functionality*
  - Category: System
- **`TestRequirementsAnalysisNode`** (Line 293)
  - *Tests for the requirements analysis node specifically*
  - Category: General

#### Test Functions

- **`test_langgraph_imports`** (Line 67)
  - *Test that LangGraph and related libraries can be imported*
  - Category: LangGraph
- **`test_create_basic_workflow`** (Line 85)
  - *Test creating a basic LangGraph workflow*
  - Category: System
- **`test_requirements_parser_creation`** (Line 115)
  - *Test creating a StrOutputParser for requirements analysis*
  - Category: General
- **`test_prompt_template_creation`** (Line 135)
  - *Test creating a prompt template with StrOutputParser*
  - Category: General
- **`test_state_validation`** (Line 191)
  - *Test that state structure is valid*
  - Category: General
- **`test_error_handling_in_workflow`** (Line 210)
  - *Test error handling in workflow nodes*
  - Category: System
- **`test_multi_node_workflow`** (Line 251)
  - *Test workflow with multiple nodes*
  - Category: System
- **`test_requirements_analysis_output_structure`** (Line 347)
  - *Test that requirements analysis output has correct structure*
  - Category: General

---

### `langgraph\test_langgraph_workflow_integration.py` (2 tests)

**Description**: Integration test for LangGraph workflow implementation.

| Metric | Value |
|--------|--------|
| **File Size** | 8.6 KB |
| **Test Classes** | 1 |
| **Test Functions** | 1 |
| **Total Tests** | 2 |

#### Test Classes

- **`TestLangGraphWorkflowIntegration`** (Line 24)
  - *Integration tests for LangGraph workflow implementation*
  - Category: Integration

#### Test Functions

- **`test_state`** (Line 57)
  - *Create test state*
  - Category: General

---

### `langgraph\test_simple_integration.py` (0 tests)

| Metric | Value |
|--------|--------|
| **File Size** | 1.0 B |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---

### `langgraph\test_workflow_manager.py` (12 tests)

**Description**: Tests for LangGraph Workflow Manager.

| Metric | Value |
|--------|--------|
| **File Size** | 14.9 KB |
| **Test Classes** | 2 |
| **Test Functions** | 10 |
| **Total Tests** | 12 |

#### Test Classes

- **`TestLangGraphWorkflowManager`** (Line 26)
  - *Tests for the LangGraph workflow manager*
  - Category: System
- **`TestAgentNodeFactory`** (Line 308)
  - *Tests for the agent node factory*
  - Category: General

#### Test Functions

- **`test_workflow_manager_initialization`** (Line 67)
  - *Test workflow manager initialization*
  - Category: System
- **`test_agent_node_factory_creation`** (Line 82)
  - *Test agent node factory creation*
  - Category: General
- **`test_requirements_node_execution`** (Line 102)
  - *Test requirements analysis node execution*
  - Category: General
- **`test_requirements_node_error_handling`** (Line 166)
  - *Test requirements analysis node error handling*
  - Category: General
- **`test_workflow_execution_error`** (Line 256)
  - *Test workflow execution error handling*
  - Category: System
- **`test_state_validation`** (Line 268)
  - *Test that state structure is valid*
  - Category: General
- **`test_workflow_manager_methods`** (Line 287)
  - *Test workflow manager public methods*
  - Category: System
- **`test_factory_initialization`** (Line 318)
  - *Test factory initialization*
  - Category: General
- **`test_node_creation_methods`** (Line 328)
  - *Test that all node creation methods return callables*
  - Category: General
- **`test_node_signature`** (Line 346)
  - *Test that nodes have correct signature*
  - Category: General

---


## 📁 **Root Tests**

### `config\test_config.py` (0 tests)

**Description**: Test Configuration System for Configurable Test Execution

Provides centralized configuration management for running tests in different modes:
- MOCK: Fast execution with mocked LLM responses  
- REAL: Full integration testing with actual LLM API calls

Support for:
- Environment variable configuration (TEST_MODE)
- Pytest command-line options (--test-mode)
- Programmatic configuration
- Validation and error handling.

| Metric | Value |
|--------|--------|
| **File Size** | 8.9 KB |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---

### `mcp\test_agent_swarm_workflow.py` (12 tests)

**Description**: Agent Swarm Workflow Tests
==========================

Comprehensive tests for MCP-powered agent swarm workflows:
- Swarm Coordinator functionality
- Agent role specialization
- Workflow execution and coordination
- Inter-agent communication through MCP
- Performance and scalability testing

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 3).

| Metric | Value |
|--------|--------|
| **File Size** | 17.6 KB |
| **Test Classes** | 4 |
| **Test Functions** | 8 |
| **Total Tests** | 12 |

#### Test Classes

- **`TestSwarmCoordinator`** (Line 44)
  - *Test suite for Swarm Coordinator*
  - Category: General
- **`TestSwarmWorkflow`** (Line 182)
  - *Test suite for Swarm Workflow functionality*
  - Category: System
- **`TestSwarmIntegrationScenarios`** (Line 283)
  - *Test real-world swarm integration scenarios*
  - Category: Integration
- **`TestSwarmFactoryFunctions`** (Line 430)
  - *Test swarm factory functions*
  - Category: General

#### Test Functions

- **`test_agent_swarm_workflow_components`** (Line 450)
  - *Main test function for pytest integration*
  - Category: System
- **`test_coordinator_initialization`** (Line 51)
  - *Test swarm coordinator initialization*
  - Category: General
- **`test_agent_capabilities_mapping`** (Line 94)
  - *Test agent capabilities are correctly mapped*
  - Category: General
- **`test_workflow_creation_from_definition`** (Line 111)
  - *Test workflow creation from definition*
  - Category: System
- **`test_task_validation`** (Line 147)
  - *Test task validation*
  - Category: General
- **`test_swarm_status`** (Line 164)
  - *Test swarm status retrieval*
  - Category: General
- **`test_create_swarm_coordinator`** (Line 433)
  - *Test swarm coordinator factory function*
  - Category: General
- **`test_create_swarm_coordinator_default_id`** (Line 441)
  - *Test swarm coordinator with default ID*
  - Category: General

---

### `mcp\test_langchain_mcp_integration.py` (24 tests)

**Description**: LangChain-MCP Integration Tests
==============================

Comprehensive tests for LangChain-MCP integration:
- MCPTool: LangChain tool wrapper functionality
- MCPToolkit: Tool collection and management
- MCPAgentMixin: Agent integration capabilities
- MCPEnhancedAgent: Complete agent with MCP tools

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 2).

| Metric | Value |
|--------|--------|
| **File Size** | 14.5 KB |
| **Test Classes** | 9 |
| **Test Functions** | 15 |
| **Total Tests** | 24 |

#### Test Classes

- **`TestLangChainMCPCompatibility`** (Line 52)
  - *Test LangChain-MCP compatibility checking*
  - Category: General
- **`TestMCPTool`** (Line 72)
  - *Test MCPTool LangChain wrapper*
  - Category: General
- **`TestMCPToolkit`** (Line 162)
  - *Test MCPToolkit functionality*
  - Category: General
- **`TestMCPAgentMixin`** (Line 201)
  - *Test MCPAgentMixin functionality*
  - Category: General
- **`TestMCPEnhancedAgent`** (Line 233)
  - *Test MCPEnhancedAgent functionality*
  - Category: General
- **`TestFactoryFunctions`** (Line 294)
  - *Test factory functions for easy integration*
  - Category: General
- **`TestIntegrationScenarios`** (Line 315)
  - *Test real-world integration scenarios*
  - Category: Integration
- **`TestAgent`** (Line 207)
  - Category: General
- **`TestAgent`** (Line 220)
  - Category: General

#### Test Functions

- **`test_langchain_mcp_integration_components`** (Line 369)
  - *Main test function for pytest integration*
  - Category: Integration
- **`test_compatibility_check`** (Line 55)
  - *Test compatibility checking function*
  - Category: General
- **`test_mcp_tool_initialization`** (Line 91)
  - *Test MCPTool initialization*
  - Category: General
- **`test_mcp_tool_metrics`** (Line 143)
  - *Test tool metrics collection*
  - Category: General
- **`test_toolkit_initialization`** (Line 169)
  - *Test toolkit initialization*
  - Category: General
- **`test_toolkit_metrics_empty`** (Line 176)
  - *Test toolkit metrics when no tools are loaded*
  - Category: General
- **`test_get_tools_empty`** (Line 188)
  - *Test getting tools when none are available*
  - Category: General
- **`test_get_tool_by_name_not_found`** (Line 194)
  - *Test getting tool by name when it doesn't exist*
  - Category: General
- **`test_mcp_agent_mixin_creation`** (Line 204)
  - *Test MCPAgentMixin can be instantiated*
  - Category: General
- **`test_get_mcp_tools_not_initialized`** (Line 218)
  - *Test getting MCP tools when not initialized*
  - Category: General
- **`test_agent_initialization`** (Line 245)
  - *Test agent initialization*
  - Category: General
- **`test_task_validation`** (Line 254)
  - *Test task validation*
  - Category: General
- **`test_agent_status`** (Line 281)
  - *Test agent status retrieval*
  - Category: General
- **`test_create_mcp_toolkit`** (Line 297)
  - *Test MCP toolkit factory function*
  - Category: General
- **`test_create_mcp_enhanced_agent`** (Line 305)
  - *Test MCP enhanced agent factory function*
  - Category: General

---

### `mcp\test_mcp_client_unit.py` (22 tests)

**Description**: MCP Client Unit Tests
====================

Comprehensive unit tests for MCP client components:
- MCPClient: Main client functionality
- MCPConnection: Server connection management
- MCPClientConfig: Configuration management
- Tool discovery and execution

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1).

| Metric | Value |
|--------|--------|
| **File Size** | 11.3 KB |
| **Test Classes** | 5 |
| **Test Functions** | 17 |
| **Total Tests** | 22 |

#### Test Classes

- **`TestMCPClientConfig`** (Line 43)
  - *Test suite for MCP Client Configuration*
  - Category: General
- **`TestMCPServerInfo`** (Line 80)
  - *Test suite for MCP Server Info*
  - Category: General
- **`TestMCPToolRequest`** (Line 105)
  - *Test suite for MCP Tool Request*
  - Category: General
- **`TestMCPClient`** (Line 144)
  - *Test suite for MCP Client*
  - Category: General
- **`TestMCPConnection`** (Line 230)
  - *Test suite for MCP Connection*
  - Category: General

#### Test Functions

- **`test_create_mcp_client`** (Line 278)
  - *Test MCP client factory function*
  - Category: General
- **`test_create_mcp_client_with_kwargs`** (Line 289)
  - *Test MCP client factory function with additional kwargs*
  - Category: General
- **`test_mcp_client_components`** (Line 307)
  - *Main test function for pytest integration*
  - Category: General
- **`test_config_creation`** (Line 46)
  - *Test MCP client configuration creation*
  - Category: General
- **`test_config_custom_values`** (Line 59)
  - *Test MCP client configuration with custom values*
  - Category: General
- **`test_server_info_creation`** (Line 83)
  - *Test MCP server info creation*
  - Category: General
- **`test_tool_request_creation`** (Line 108)
  - *Test MCP tool request creation*
  - Category: General
- **`test_tool_request_with_custom_values`** (Line 124)
  - *Test MCP tool request with custom values*
  - Category: General
- **`test_client_creation`** (Line 156)
  - *Test MCP client creation*
  - Category: General
- **`test_cache_key_generation`** (Line 175)
  - *Test cache key generation*
  - Category: General
- **`test_client_stats`** (Line 194)
  - *Test client statistics retrieval*
  - Category: General
- **`test_find_tool_connection_no_connections`** (Line 211)
  - *Test finding tool connection when no connections exist*
  - Category: General
- **`test_get_available_tools_no_connections`** (Line 216)
  - *Test getting available tools when no connections exist*
  - Category: General
- **`test_get_server_info_no_connections`** (Line 222)
  - *Test getting server info when no connections exist*
  - Category: General
- **`test_connection_creation`** (Line 250)
  - *Test MCP connection creation*
  - Category: General
- **`test_get_tool_info_no_tools`** (Line 259)
  - *Test getting tool info when no tools are available*
  - Category: General
- **`test_list_tools_no_tools`** (Line 264)
  - *Test listing tools when no tools are available*
  - Category: General

---

### `mcp\test_mcp_end_to_end.py` (3 tests)

**Description**: MCP End-to-End Tests
===================

Complete end-to-end tests for the MCP system:
- Full system workflow testing
- Real tool execution scenarios
- Performance validation
- Production readiness verification

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1).

| Metric | Value |
|--------|--------|
| **File Size** | 11.6 KB |
| **Test Classes** | 1 |
| **Test Functions** | 2 |
| **Total Tests** | 3 |

#### Test Classes

- **`TestMCPEndToEnd`** (Line 39)
  - *End-to-end tests for complete MCP system*
  - Category: General

#### Test Functions

- **`test_mcp_end_to_end_components`** (Line 310)
  - *Main test function for pytest integration*
  - Category: General
- **`test_mcp_system_configuration`** (Line 200)
  - *Test MCP system configuration and setup*
  - Category: System

---

### `mcp\test_mcp_integration.py` (8 tests)

**Description**: MCP Integration Tests
====================

Integration tests for MCP server and client working together:
- Server-Client communication
- Tool discovery and execution
- Universal Agent Tracker integration
- Performance and caching
- Error handling and recovery

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1).

| Metric | Value |
|--------|--------|
| **File Size** | 10.3 KB |
| **Test Classes** | 4 |
| **Test Functions** | 4 |
| **Total Tests** | 8 |

#### Test Classes

- **`TestMCPServerClientIntegration`** (Line 41)
  - *Integration tests for MCP server and client*
  - Category: Integration
- **`TestMCPToolExecution`** (Line 123)
  - *Integration tests for MCP tool execution*
  - Category: General
- **`TestMCPPerformanceIntegration`** (Line 179)
  - *Performance integration tests for MCP system*
  - Category: Integration
- **`TestMCPErrorHandling`** (Line 240)
  - *Error handling integration tests for MCP system*
  - Category: General

#### Test Functions

- **`test_mcp_integration_components`** (Line 285)
  - *Main test function for pytest integration*
  - Category: Integration
- **`test_server_client_component_integration`** (Line 96)
  - *Test that server and client components integrate properly*
  - Category: Integration
- **`test_server_tool_count`** (Line 108)
  - *Test server has expected number of tools*
  - Category: General
- **`test_server_categories`** (Line 113)
  - *Test server has expected tool categories*
  - Category: General

---

### `mcp\test_mcp_server_unit.py` (16 tests)

**Description**: MCP Server Unit Tests
====================

Comprehensive unit tests for MCP server components:
- MCPToolRegistry: Tool registration and management
- MCPSecurityManager: Access control and security
- MCPExecutionEngine: Tool execution and monitoring
- MCPServer: Main server functionality

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1).

| Metric | Value |
|--------|--------|
| **File Size** | 11.7 KB |
| **Test Classes** | 4 |
| **Test Functions** | 12 |
| **Total Tests** | 16 |

#### Test Classes

- **`TestMCPToolRegistry`** (Line 43)
  - *Test suite for MCP Tool Registry*
  - Category: General
- **`TestMCPSecurityManager`** (Line 120)
  - *Test suite for MCP Security Manager*
  - Category: Security
- **`TestMCPExecutionEngine`** (Line 185)
  - *Test suite for MCP Execution Engine*
  - Category: General
- **`TestMCPServer`** (Line 241)
  - *Test suite for MCP Server*
  - Category: General

#### Test Functions

- **`test_mcp_server_components`** (Line 306)
  - *Main test function for pytest integration*
  - Category: General
- **`test_registry_initialization`** (Line 50)
  - *Test tool registry initialization*
  - Category: General
- **`test_critical_tools_registered`** (Line 56)
  - *Test that all critical tools are registered*
  - Category: General
- **`test_tool_categories`** (Line 82)
  - *Test tool categorization*
  - Category: General
- **`test_tool_access_levels`** (Line 92)
  - *Test tool access level assignments*
  - Category: General
- **`test_tool_filtering`** (Line 104)
  - *Test tool filtering by category and access level*
  - Category: General
- **`test_security_manager_initialization`** (Line 127)
  - *Test security manager initialization*
  - Category: Security
- **`test_security_audit_logging`** (Line 163)
  - *Test security audit logging*
  - Category: Security
- **`test_execution_engine_initialization`** (Line 194)
  - *Test execution engine initialization*
  - Category: General
- **`test_server_creation`** (Line 248)
  - *Test MCP server creation*
  - Category: General
- **`test_server_components_initialization`** (Line 255)
  - *Test server component initialization*
  - Category: General
- **`test_server_info`** (Line 273)
  - *Test server information retrieval*
  - Category: General

---

### `mcp\test_rag_mcp_comprehensive.py` (0 tests)

**Description**: RAG-MCP Integration Test with Real Documents and Websites
========================================================

Comprehensive test of RAG-MCP integration using real documents and websites
to validate the vector database functionality and semantic search capabilities.

| Metric | Value |
|--------|--------|
| **File Size** | 30.2 KB |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---

### `mcp\test_rag_mcp_simple.py` (3 tests)

**Description**: Simple RAG-MCP Integration Test
==============================

A simplified test to validate RAG-MCP integration step by step.

| Metric | Value |
|--------|--------|
| **File Size** | 7.3 KB |
| **Test Classes** | 0 |
| **Test Functions** | 3 |
| **Total Tests** | 3 |

#### Test Functions

- **`test_imports`** (Line 24)
  - *Test if all required imports work*
  - Category: General
- **`test_context_engine_initialization`** (Line 51)
  - *Test ContextEngine initialization*
  - Category: General
- **`test_rag_tools_initialization`** (Line 81)
  - *Test RAG-MCP tools initialization*
  - Category: General

---

### `mcp\test_software_catalog_comprehensive.py` (1 tests)

**Description**: Comprehensive Software Catalog RAG System Test
==============================================

Tests the complete software catalog system including:
- Component discovery and cataloging
- Semantic search capabilities
- Anti-duplication intelligence
- Agent swarm context enhancement
- Cursor rule system integration

Author: AI Development Agent
Created: 2025-01-02
Purpose: Validate software catalog RAG integration.

| Metric | Value |
|--------|--------|
| **File Size** | 15.8 KB |
| **Test Classes** | 1 |
| **Test Functions** | 0 |
| **Total Tests** | 1 |

#### Test Classes

- **`TestSoftwareCatalogSystem`** (Line 32)
  - *Comprehensive test suite for software catalog RAG system*
  - Category: System

---

### `optimization\test_cursor_optimization.py` (1 tests)

**Description**: Test Cursor-First Optimization System.

| Metric | Value |
|--------|--------|
| **File Size** | 1.2 KB |
| **Test Classes** | 0 |
| **Test Functions** | 1 |
| **Total Tests** | 1 |

#### Test Functions

- **`test_cursor_optimization`** (Line 8)
  - *Test the Cursor-first optimization*
  - Category: General

---

### `optimization\test_live_efficiency_proof.py` (0 tests)

**Description**: LIVE EFFICIENCY PROOF - No BlaBla, Just Measurable Results
========================================================

MISSION: Prove Wu Wei + Sun Tzu efficiency works in practice.

| Metric | Value |
|--------|--------|
| **File Size** | 8.5 KB |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---

### `scripts\test_agent_prompt_loading.py` (0 tests)

| Metric | Value |
|--------|--------|
| **File Size** | 1.0 B |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---

### `test_imports.py` (5 tests)

**Description**: Test that reorganized imports work correctly.

| Metric | Value |
|--------|--------|
| **File Size** | 2.4 KB |
| **Test Classes** | 1 |
| **Test Functions** | 4 |
| **Total Tests** | 5 |

#### Test Classes

- **`TestReorganizedImports`** (Line 7)
  - *Test reorganized imports after file restructuring*
  - Category: General

#### Test Functions

- **`test_core_utilities_import`** (Line 10)
  - *Test core utilities import properly*
  - Category: General
- **`test_system_utilities_import`** (Line 30)
  - *Test system utilities import properly*
  - Category: System
- **`test_prompt_utilities_import`** (Line 44)
  - *Test prompt utilities import properly*
  - Category: General
- **`test_main_utils_import`** (Line 58)
  - *Test main utils import properly*
  - Category: General

---

### `test_mcp_server.py` (18 tests)

**Description**: MCP Server Unit Tests
====================

Unit tests for MCP server components moved to tests/mcp/ directory.

| Metric | Value |
|--------|--------|
| **File Size** | 17.7 KB |
| **Test Classes** | 6 |
| **Test Functions** | 12 |
| **Total Tests** | 18 |

#### Test Classes

- **`TestMCPToolRegistry`** (Line 45)
  - *Test suite for MCP Tool Registry*
  - Category: General
- **`TestMCPSecurityManager`** (Line 117)
  - *Test suite for MCP Security Manager*
  - Category: Security
- **`TestMCPExecutionEngine`** (Line 183)
  - *Test suite for MCP Execution Engine*
  - Category: General
- **`TestMCPServer`** (Line 240)
  - *Test suite for MCP Server*
  - Category: General
- **`TestMCPIntegration`** (Line 306)
  - *Integration tests for MCP components*
  - Category: Integration
- **`TestMCPPerformance`** (Line 359)
  - *Performance tests for MCP server*
  - Category: Performance

#### Test Functions

- **`test_registry_initialization`** (Line 54)
  - *Test tool registry initialization*
  - Category: General
- **`test_critical_tools_registered`** (Line 60)
  - *Test that all 12 critical tools are registered*
  - Category: General
- **`test_tool_categories`** (Line 80)
  - *Test tool categorization*
  - Category: General
- **`test_tool_access_levels`** (Line 90)
  - *Test tool access level assignments*
  - Category: General
- **`test_tool_filtering`** (Line 102)
  - *Test tool filtering by category and access level*
  - Category: General
- **`test_security_manager_initialization`** (Line 126)
  - *Test security manager initialization*
  - Category: Security
- **`test_security_audit_logging`** (Line 162)
  - *Test security audit logging*
  - Category: Security
- **`test_execution_engine_initialization`** (Line 194)
  - *Test execution engine initialization*
  - Category: General
- **`test_server_creation`** (Line 249)
  - *Test MCP server creation*
  - Category: General
- **`test_server_components_initialization`** (Line 256)
  - *Test server component initialization*
  - Category: General
- **`test_server_info`** (Line 274)
  - *Test server information retrieval*
  - Category: General
- **`test_tool_registry_security_integration`** (Line 343)
  - *Test integration between tool registry and security manager*
  - Category: Integration

---

### `test_utils\automated_testing\test_reporter.py` (1 tests)

**Description**: TestReporter - Test result reporting and notifications

This class generates comprehensive test reports and sends notifications
for US-002: Fully Automated Testing Pipeline.

| Metric | Value |
|--------|--------|
| **File Size** | 11.8 KB |
| **Test Classes** | 1 |
| **Test Functions** | 0 |
| **Total Tests** | 1 |

#### Test Classes

- **`TestReport`** (Line 23)
  - *Comprehensive test report object*
  - Category: General

---

### `workflow\test_context_orchestrator.py` (19 tests)

**Description**: Comprehensive tests for the ContextOrchestrator component.

| Metric | Value |
|--------|--------|
| **File Size** | 28.7 KB |
| **Test Classes** | 1 |
| **Test Functions** | 18 |
| **Total Tests** | 19 |

#### Test Classes

- **`TestContextOrchestrator`** (Line 20)
  - *Test suite for ContextOrchestrator functionality*
  - Category: General

#### Test Functions

- **`test_initialization`** (Line 73)
  - *Test ContextOrchestrator initialization*
  - Category: General
- **`test_initialize_workflow_state`** (Line 366)
  - *Test workflow state initialization*
  - Category: System
- **`test_build_execution_plan_sequential`** (Line 382)
  - *Test building execution plan for sequential phases*
  - Category: General
- **`test_build_execution_plan_parallel`** (Line 393)
  - *Test building execution plan with parallel phases*
  - Category: General
- **`test_prepare_phase_inputs`** (Line 438)
  - *Test preparation of phase inputs*
  - Category: General
- **`test_validate_context_transition_valid`** (Line 454)
  - *Test validation of valid context transitions*
  - Category: General
- **`test_validate_context_transition_invalid`** (Line 463)
  - *Test validation of invalid context transitions*
  - Category: General
- **`test_capture_context_state`** (Line 472)
  - *Test capturing context state*
  - Category: General
- **`test_transform_phase_results`** (Line 488)
  - *Test transformation of phase results*
  - Category: General
- **`test_validate_propagated_data_valid`** (Line 501)
  - *Test validation of valid propagated data*
  - Category: General
- **`test_validate_propagated_data_invalid`** (Line 515)
  - *Test validation of invalid propagated data*
  - Category: General
- **`test_validate_phase_results_valid`** (Line 523)
  - *Test validation of valid phase results*
  - Category: General
- **`test_validate_phase_results_missing_outputs`** (Line 543)
  - *Test validation of phase results with missing outputs*
  - Category: General
- **`test_determine_recovery_action_timeout`** (Line 563)
  - *Test recovery action determination for timeout errors*
  - Category: General
- **`test_determine_recovery_action_critical`** (Line 573)
  - *Test recovery action determination for critical errors*
  - Category: General
- **`test_finalize_workflow_success`** (Line 583)
  - *Test workflow finalization for successful execution*
  - Category: System
- **`test_handle_workflow_failure`** (Line 603)
  - *Test workflow failure handling*
  - Category: System
- **`test_recovery_strategies_initialization`** (Line 663)
  - *Test that recovery strategies are properly initialized*
  - Category: General

---

### `workflow\test_task_analyzer.py` (28 tests)

**Description**: Comprehensive tests for the TaskAnalyzer component.

| Metric | Value |
|--------|--------|
| **File Size** | 16.4 KB |
| **Test Classes** | 1 |
| **Test Functions** | 27 |
| **Total Tests** | 28 |

#### Test Classes

- **`TestTaskAnalyzer`** (Line 15)
  - *Test suite for TaskAnalyzer functionality*
  - Category: General

#### Test Functions

- **`test_initialization`** (Line 22)
  - *Test TaskAnalyzer initialization*
  - Category: General
- **`test_analyze_simple_task`** (Line 30)
  - *Test analysis of a simple task*
  - Category: General
- **`test_analyze_complex_task`** (Line 44)
  - *Test analysis of a complex task*
  - Category: General
- **`test_analyze_feature_development_task`** (Line 59)
  - *Test analysis of a feature development task*
  - Category: General
- **`test_extract_entities_bug_task`** (Line 75)
  - *Test entity extraction for bug-related tasks*
  - Category: General
- **`test_extract_entities_feature_task`** (Line 90)
  - *Test entity extraction for feature development tasks*
  - Category: General
- **`test_assess_complexity_simple`** (Line 104)
  - *Test complexity assessment for simple tasks*
  - Category: General
- **`test_assess_complexity_medium`** (Line 116)
  - *Test complexity assessment for medium tasks*
  - Category: General
- **`test_assess_complexity_complex`** (Line 129)
  - *Test complexity assessment for complex tasks*
  - Category: General
- **`test_identify_contexts_bug_fix`** (Line 143)
  - *Test context identification for bug fix tasks*
  - Category: General
- **`test_identify_contexts_feature_development`** (Line 155)
  - *Test context identification for feature development*
  - Category: General
- **`test_identify_contexts_security_task`** (Line 168)
  - *Test context identification for security tasks*
  - Category: Security
- **`test_estimate_duration_simple_task`** (Line 179)
  - *Test duration estimation for simple tasks*
  - Category: General
- **`test_estimate_duration_complex_task`** (Line 191)
  - *Test duration estimation for complex tasks*
  - Category: General
- **`test_identify_dependencies`** (Line 206)
  - *Test dependency identification*
  - Category: General
- **`test_generate_success_criteria_feature`** (Line 216)
  - *Test success criteria generation for features*
  - Category: General
- **`test_generate_success_criteria_bug`** (Line 227)
  - *Test success criteria generation for bugs*
  - Category: General
- **`test_generate_success_criteria_security`** (Line 238)
  - *Test success criteria generation for security tasks*
  - Category: Security
- **`test_task_id_generation`** (Line 249)
  - *Test unique task ID generation*
  - Category: General
- **`test_confidence_calculation`** (Line 261)
  - *Test confidence score calculation*
  - Category: General
- **`test_context_with_project_info`** (Line 275)
  - *Test analysis with additional project context*
  - Category: General
- **`test_empty_task_description`** (Line 289)
  - *Test handling of empty task description*
  - Category: General
- **`test_very_long_task_description`** (Line 300)
  - *Test handling of very long task descriptions*
  - Category: General
- **`test_special_characters_in_task`** (Line 310)
  - *Test handling of special characters in task description*
  - Category: General
- **`test_multiple_entity_types`** (Line 320)
  - *Test extraction of multiple entity types from complex description*
  - Category: General
- **`test_context_identification_patterns`** (Line 343)
  - *Test context identification for various task patterns*
  - Category: General
- **`test_entity_confidence_scoring`** (Line 350)
  - *Test entity confidence scoring accuracy*
  - Category: General

---

### `workflow\test_workflow_composer.py` (27 tests)

**Description**: Comprehensive tests for the WorkflowComposer component.

| Metric | Value |
|--------|--------|
| **File Size** | 22.8 KB |
| **Test Classes** | 1 |
| **Test Functions** | 26 |
| **Total Tests** | 27 |

#### Test Classes

- **`TestWorkflowComposer`** (Line 21)
  - *Test suite for WorkflowComposer functionality*
  - Category: System

#### Test Functions

- **`test_initialization`** (Line 51)
  - *Test WorkflowComposer initialization*
  - Category: General
- **`test_compose_workflow_without_template`** (Line 58)
  - *Test workflow composition without matching template*
  - Category: System
- **`test_compose_workflow_with_template`** (Line 72)
  - *Test workflow composition with matching template*
  - Category: System
- **`test_select_template_good_match`** (Line 84)
  - *Test template selection with good match*
  - Category: General
- **`test_select_template_no_match`** (Line 109)
  - *Test template selection with no good match*
  - Category: General
- **`test_customize_workflow_add_missing_contexts`** (Line 120)
  - *Test workflow customization adds missing contexts*
  - Category: System
- **`test_create_custom_workflow`** (Line 147)
  - *Test creation of custom workflow from scratch*
  - Category: System
- **`test_optimize_sequence_logical_order`** (Line 159)
  - *Test sequence optimization maintains logical order*
  - Category: General
- **`test_validate_workflow_valid`** (Line 197)
  - *Test workflow validation for valid workflow*
  - Category: System
- **`test_validate_workflow_invalid_context`** (Line 207)
  - *Test workflow validation with invalid context*
  - Category: System
- **`test_validate_workflow_empty_phases`** (Line 239)
  - *Test workflow validation with no phases*
  - Category: System
- **`test_create_context_phase`** (Line 259)
  - *Test creation of context-specific phases*
  - Category: General
- **`test_get_context_timeout_complexity_adjustment`** (Line 270)
  - *Test context timeout adjustment based on complexity*
  - Category: General
- **`test_build_phase_dependencies`** (Line 278)
  - *Test building phase dependencies*
  - Category: General
- **`test_estimate_workflow_duration`** (Line 296)
  - *Test workflow duration estimation*
  - Category: System
- **`test_load_templates_from_directory`** (Line 308)
  - *Test loading templates from directory*
  - Category: Performance
- **`test_load_invalid_template_file`** (Line 321)
  - *Test handling of invalid template files*
  - Category: Performance
- **`test_template_score_calculation`** (Line 334)
  - *Test template scoring calculation*
  - Category: General
- **`test_optimization_rules_application`** (Line 353)
  - *Test application of optimization rules*
  - Category: General
- **`test_parallel_group_identification`** (Line 374)
  - *Test identification of parallel execution groups*
  - Category: General
- **`test_workflow_connectivity_check`** (Line 388)
  - *Test workflow connectivity validation*
  - Category: System
- **`test_circular_dependency_detection`** (Line 419)
  - *Test circular dependency detection*
  - Category: General
- **`test_fix_validation_issues`** (Line 433)
  - *Test automatic fixing of validation issues*
  - Category: General
- **`test_duration_estimation_by_complexity`** (Line 495)
  - *Test duration estimation varies by complexity*
  - Category: General
- **`test_quality_gates_generation`** (Line 505)
  - *Test quality gates generation based on analysis*
  - Category: General
- **`test_phase_ordering_logic`** (Line 517)
  - *Test logical phase ordering*
  - Category: General

---

### `workflow\test_workflow_orchestration.py` (20 tests)

**Description**: Test Workflow Orchestration System

Comprehensive tests for the workflow orchestration system implemented for US-WO-01.

| Metric | Value |
|--------|--------|
| **File Size** | 22.3 KB |
| **Test Classes** | 4 |
| **Test Functions** | 16 |
| **Total Tests** | 20 |

#### Test Classes

- **`TestWorkflowOrchestrationTeam`** (Line 46)
  - *Test the specialized workflow orchestration team*
  - Category: System
- **`TestWorkflowOrchestrationEngine`** (Line 285)
  - *Test the workflow orchestration engine*
  - Category: System
- **`TestWorkflowIntegration`** (Line 421)
  - *Test integration with existing systems*
  - Category: Integration
- **`TestWorkflowPerformance`** (Line 471)
  - *Test workflow orchestration performance*
  - Category: System

#### Test Functions

- **`test_us_wo_01_requirements`** (Line 505)
  - *Test that US-WO-01 requirements are met*
  - Category: General
- **`test_team_initialization`** (Line 53)
  - *Test that team initializes with all required agents*
  - Category: General
- **`test_simple_task_analysis`** (Line 62)
  - *Test workflow analysis for simple tasks*
  - Category: General
- **`test_complex_task_analysis`** (Line 76)
  - *Test workflow analysis for complex tasks*
  - Category: General
- **`test_workflow_composition_design`** (Line 98)
  - *Test workflow composition design*
  - Category: System
- **`test_langgraph_orchestration_implementation`** (Line 119)
  - *Test LangGraph orchestration implementation*
  - Category: LangGraph
- **`test_agent_coordination`** (Line 144)
  - *Test agent coordination functionality*
  - Category: General
- **`test_context_flow_analysis`** (Line 169)
  - *Test context flow analysis*
  - Category: General
- **`test_validation_framework_design`** (Line 194)
  - *Test validation framework design*
  - Category: General
- **`test_system_integration_design`** (Line 220)
  - *Test system integration design*
  - Category: Integration
- **`test_full_team_workflow_implementation`** (Line 251)
  - *Test complete team workflow implementation*
  - Category: System
- **`test_engine_initialization`** (Line 292)
  - *Test engine initialization*
  - Category: General
- **`test_workflow_orchestrator_context_manager`** (Line 391)
  - *Test the WorkflowOrchestrator context manager*
  - Category: System
- **`test_factory_function`** (Line 404)
  - *Test the factory function*
  - Category: General
- **`test_directory_structure_compliance`** (Line 448)
  - *Test that workflow orchestration follows project directory structure*
  - Category: General
- **`test_import_structure`** (Line 459)
  - *Test that imports work correctly*
  - Category: General

---


## 📁 **Security Tests**

### `security\test_ethical_ai_protection.py` (14 tests)

**Description**: Comprehensive Test Suite for Ethical AI Protection Systems
==========================================================

CRITICAL: These tests validate our sacred commitment to never cause harm
and always serve love, harmony, and protection for all living beings.

| Metric | Value |
|--------|--------|
| **File Size** | 25.7 KB |
| **Test Classes** | 13 |
| **Test Functions** | 1 |
| **Total Tests** | 14 |

#### Test Classes

- **`TestEthicalGuardianAgent`** (Line 41)
  - *Test the core ethical guardian agent*
  - Category: General
- **`TestHarmPreventionSpecialist`** (Line 96)
  - *Test the harm prevention specialist*
  - Category: General
- **`TestMisuseDetectionSpecialist`** (Line 138)
  - *Test the misuse detection specialist*
  - Category: General
- **`TestLifeRespectSpecialist`** (Line 172)
  - *Test the life respect specialist*
  - Category: General
- **`TestLoveHarmonySpecialist`** (Line 205)
  - *Test the love and harmony specialist*
  - Category: General
- **`TestTransparencyAccountabilitySpecialist`** (Line 238)
  - *Test the transparency and accountability specialist*
  - Category: General
- **`TestEthicalAIProtectionTeam`** (Line 274)
  - *Test the complete ethical AI protection team*
  - Category: General
- **`TestEthicalSafeguardsEngine`** (Line 349)
  - *Test the ethical safeguards integration engine*
  - Category: General
- **`TestEthicalIntegrationManager`** (Line 402)
  - *Test the ethical integration manager*
  - Category: Integration
- **`TestConvenienceFunctions`** (Line 429)
  - *Test convenience functions for ethical validation*
  - Category: General
- **`TestEthicalDecoratorIntegration`** (Line 454)
  - *Test ethical validation decorator integration*
  - Category: Integration
- **`TestComprehensiveEthicalScenarios`** (Line 484)
  - *Test comprehensive ethical scenarios to ensure full protection*
  - Category: General
- **`TestCompleteSystemIntegration`** (Line 554)
  - *Test complete integration of all ethical systems*
  - Category: Integration

#### Test Functions

- **`test_manager_initialization`** (Line 409)
  - *Test that the manager initializes correctly*
  - Category: General

---


## 📁 **Supervisor Tests**

### `supervisor\test_base_supervisor.py` (18 tests)

**Description**: Tests for base supervisor classes.

| Metric | Value |
|--------|--------|
| **File Size** | 11.1 KB |
| **Test Classes** | 3 |
| **Test Functions** | 15 |
| **Total Tests** | 18 |

#### Test Classes

- **`TestSupervisorConfig`** (Line 18)
  - *Tests for SupervisorConfig*
  - Category: Supervisor
- **`TestBaseSupervisor`** (Line 75)
  - *Tests for BaseSupervisor*
  - Category: Supervisor
- **`TestSupervisorIntegration`** (Line 215)
  - *Integration tests for supervisor functionality*
  - Category: Integration

#### Test Functions

- **`test_supervisor_config_creation`** (Line 21)
  - *Test creating a supervisor config*
  - Category: Supervisor
- **`test_supervisor_config_custom_values`** (Line 38)
  - *Test creating a supervisor config with custom values*
  - Category: Supervisor
- **`test_supervisor_config_validation`** (Line 52)
  - *Test supervisor config validation*
  - Category: Supervisor
- **`test_supervisor_initialization`** (Line 101)
  - *Test supervisor initialization*
  - Category: Supervisor
- **`test_log_decision`** (Line 108)
  - *Test logging a decision*
  - Category: General
- **`test_get_decision_history`** (Line 121)
  - *Test getting decision history*
  - Category: General
- **`test_clear_decision_history`** (Line 133)
  - *Test clearing decision history*
  - Category: General
- **`test_get_recent_decisions`** (Line 143)
  - *Test getting recent decisions*
  - Category: General
- **`test_get_recent_decisions_empty_history`** (Line 159)
  - *Test getting recent decisions from empty history*
  - Category: General
- **`test_get_recent_decisions_limit_exceeds_history`** (Line 164)
  - *Test getting recent decisions when limit exceeds history size*
  - Category: General
- **`test_decision_history_timestamp_format`** (Line 185)
  - *Test that decision timestamps are in ISO format*
  - Category: General
- **`test_multiple_decisions_ordering`** (Line 198)
  - *Test that multiple decisions are stored in correct order*
  - Category: General
- **`test_supervisor_config_integration`** (Line 248)
  - *Test that supervisor uses config correctly*
  - Category: Integration
- **`test_supervisor_llm_integration`** (Line 254)
  - *Test that supervisor has access to LLM*
  - Category: Integration
- **`test_supervisor_logger_integration`** (Line 280)
  - *Test that supervisor has proper logging setup*
  - Category: Integration

---

### `supervisor\test_project_manager_supervisor.py` (3 tests)

**Description**: Tests for Project Manager Supervisor.

| Metric | Value |
|--------|--------|
| **File Size** | 23.7 KB |
| **Test Classes** | 2 |
| **Test Functions** | 1 |
| **Total Tests** | 3 |

#### Test Classes

- **`TestProjectManagerSupervisor`** (Line 15)
  - *Tests for ProjectManagerSupervisor*
  - Category: Supervisor
- **`TestProjectManagerIntegration`** (Line 523)
  - *Integration tests for ProjectManagerSupervisor*
  - Category: Integration

#### Test Functions

- **`test_project_manager_initialization`** (Line 45)
  - *Test project manager initialization*
  - Category: General

---


## 📁 **System Tests**

### `system\test_complete_workflow.py` (0 tests)

**Description**: Test script to verify the complete workflow with real LLM usage.

| Metric | Value |
|--------|--------|
| **File Size** | 34.3 KB |
| **Test Classes** | 0 |
| **Test Functions** | 0 |
| **Total Tests** | 0 |

---


## 📁 **Unit Tests**

### `langgraph\unit\test_agent_nodes.py` (10 tests)

**Description**: Tests for LangGraph agent nodes.

| Metric | Value |
|--------|--------|
| **File Size** | 23.0 KB |
| **Test Classes** | 6 |
| **Test Functions** | 4 |
| **Total Tests** | 10 |

#### Test Classes

- **`TestDataFactory`** (Line 60)
  - *Factory for creating isolated test data*
  - Category: General
- **`TestRequirementsAnalystNode`** (Line 121)
  - *Tests for requirements analyst node*
  - Category: General
- **`TestArchitectureDesignerNode`** (Line 195)
  - *Tests for architecture designer node*
  - Category: General
- **`TestCodeGeneratorNode`** (Line 272)
  - *Tests for code generator node*
  - Category: General
- **`TestTestGeneratorNode`** (Line 360)
  - *Tests for test generator node*
  - Category: General
- **`TestRealLLMIntegration`** (Line 446)
  - *Integration tests with real LLM usage to catch production issues*
  - Category: Integration

#### Test Functions

- **`test_requirements_node_creation`** (Line 144)
  - *Test that requirements node can be created*
  - Category: General
- **`test_architecture_node_creation`** (Line 219)
  - *Test that architecture node can be created*
  - Category: General
- **`test_code_generator_node_creation`** (Line 297)
  - *Test that code generator node can be created*
  - Category: General
- **`test_test_generator_node_creation`** (Line 390)
  - *Test that test generator node can be created*
  - Category: General

---

### `langgraph\unit\test_agent_nodes_advanced.py` (9 tests)

**Description**: Advanced unit tests for remaining agent nodes.

| Metric | Value |
|--------|--------|
| **File Size** | 27.7 KB |
| **Test Classes** | 3 |
| **Test Functions** | 6 |
| **Total Tests** | 9 |

#### Test Classes

- **`TestCodeReviewerNode`** (Line 25)
  - *Tests for the Code Reviewer node*
  - Category: General
- **`TestSecurityAnalystNode`** (Line 202)
  - *Tests for the Security Analyst node*
  - Category: Security
- **`TestDocumentationGeneratorNode`** (Line 392)
  - *Tests for the Documentation Generator node*
  - Category: General

#### Test Functions

- **`test_state_with_code`** (Line 41)
  - *Create test state with code files for code review*
  - Category: General
- **`test_code_reviewer_node_creation`** (Line 79)
  - *Test that code reviewer node can be created*
  - Category: General
- **`test_state_with_code_and_architecture`** (Line 218)
  - *Create test state with code and architecture for security analysis*
  - Category: General
- **`test_security_analyst_node_creation`** (Line 256)
  - *Test that security analyst node can be created*
  - Category: Security
- **`test_state_with_complete_project`** (Line 408)
  - *Create test state with complete project for documentation generation*
  - Category: System
- **`test_documentation_generator_node_creation`** (Line 479)
  - *Test that documentation generator node can be created*
  - Category: General

---

### `unit\agents\test_agent_system.py` (35 tests)

**Description**: Test Agent System

Comprehensive tests for the agent system including base agent, factory,
manager, and specialized agents.

| Metric | Value |
|--------|--------|
| **File Size** | 19.0 KB |
| **Test Classes** | 13 |
| **Test Functions** | 22 |
| **Total Tests** | 35 |

#### Test Classes

- **`TestAgentConfig`** (Line 21)
  - *Test AgentConfig dataclass*
  - Category: General
- **`TestAgentState`** (Line 40)
  - *Test AgentState dataclass*
  - Category: General
- **`TestAgentFactory`** (Line 89)
  - *Test AgentFactory class*
  - Category: General
- **`TestAgentManager`** (Line 239)
  - *Test AgentManager class*
  - Category: General
- **`TestRequirementsAnalyst`** (Line 283)
  - *Test RequirementsAnalyst class*
  - Category: General
- **`TestAgentSystemIntegration`** (Line 420)
  - *Test agent system integration*
  - Category: Integration
- **`TestAgentPerformance`** (Line 475)
  - *Test agent performance monitoring*
  - Category: Performance
- **`TestAgent`** (Line 103)
  - Category: General
- **`TestAgent`** (Line 119)
  - Category: General
- **`TestAgent`** (Line 157)
  - Category: General
- **`TestAgent`** (Line 181)
  - Category: General
- **`TestAgent`** (Line 215)
  - Category: General
- **`TestAgent`** (Line 271)
  - Category: General

#### Test Functions

- **`test_agent_config_creation`** (Line 24)
  - *Test creating an AgentConfig instance*
  - Category: General
- **`test_agent_state_creation`** (Line 43)
  - *Test creating an AgentState instance*
  - Category: General
- **`test_factory_initialization`** (Line 92)
  - *Test factory initialization*
  - Category: General
- **`test_register_agent_type`** (Line 99)
  - *Test registering an agent type*
  - Category: General
- **`test_create_agent`** (Line 115)
  - *Test creating an agent instance*
  - Category: General
- **`test_create_unknown_agent_type`** (Line 140)
  - *Test creating an agent with unknown type*
  - Category: General
- **`test_get_agent`** (Line 153)
  - *Test getting an agent by ID*
  - Category: General
- **`test_list_agents`** (Line 177)
  - *Test listing active agents*
  - Category: General
- **`test_shutdown_agent`** (Line 211)
  - *Test shutting down an agent*
  - Category: General
- **`test_manager_initialization`** (Line 242)
  - *Test manager initialization*
  - Category: General
- **`test_get_default_config`** (Line 250)
  - *Test getting default configuration*
  - Category: General
- **`test_list_available_agent_types`** (Line 262)
  - *Test listing available agent types*
  - Category: General
- **`test_agent_initialization`** (Line 286)
  - *Test agent initialization*
  - Category: General
- **`test_validate_task`** (Line 300)
  - *Test task validation*
  - Category: General
- **`test_extract_keywords`** (Line 360)
  - *Test keyword extraction*
  - Category: General
- **`test_generate_basic_user_stories`** (Line 379)
  - *Test basic user story generation*
  - Category: General
- **`test_generate_technical_requirements`** (Line 400)
  - *Test technical requirements generation*
  - Category: General
- **`test_get_agent_manager`** (Line 423)
  - *Test getting the global agent manager*
  - Category: General
- **`test_get_system_status`** (Line 462)
  - *Test getting system status*
  - Category: System
- **`test_performance_monitor_initialization`** (Line 478)
  - *Test performance monitor initialization*
  - Category: Performance
- **`test_record_execution`** (Line 486)
  - *Test recording agent execution*
  - Category: General
- **`test_get_summary`** (Line 522)
  - *Test getting performance summary*
  - Category: General

---

### `unit\agents\test_test_generator.py` (1 tests)

**Description**: Test file for TestGenerator agent.

| Metric | Value |
|--------|--------|
| **File Size** | 4.6 KB |
| **Test Classes** | 1 |
| **Test Functions** | 0 |
| **Total Tests** | 1 |

#### Test Classes

- **`TestTestGenerator`** (Line 25)
  - *Test cases for TestGenerator agent*
  - Category: General

---

### `unit\agents\test_workflow_extraction.py` (1 tests)

**Description**: Test file for workflow test file extraction.

| Metric | Value |
|--------|--------|
| **File Size** | 3.8 KB |
| **Test Classes** | 1 |
| **Test Functions** | 0 |
| **Total Tests** | 1 |

#### Test Classes

- **`TestWorkflowExtraction`** (Line 22)
  - *Test cases for workflow file extraction*
  - Category: System

---

### `unit\prompts\test_advanced_prompt_optimization.py` (27 tests)

**Description**: Test suite for US-PE-03: Advanced Prompt Optimization

Tests the advanced prompt optimization engine including:
- ML-based optimization capabilities
- Context-aware adaptation
- Performance regression detection
- Integration hooks for Epic 3 and Epic 4
- Optimization history and rollback
- Advanced analytics and reporting.

| Metric | Value |
|--------|--------|
| **File Size** | 27.1 KB |
| **Test Classes** | 3 |
| **Test Functions** | 24 |
| **Total Tests** | 27 |

#### Test Classes

- **`TestAdvancedPromptOptimizer`** (Line 27)
  - *Test the advanced prompt optimization engine*
  - Category: General
- **`TestAdvancedOptimizationIntegration`** (Line 454)
  - *Test integration with existing prompt management systems*
  - Category: Integration
- **`TestAdvancedOptimizationPerformance`** (Line 580)
  - *Test performance characteristics of the advanced optimizer*
  - Category: Performance

#### Test Functions

- **`test_optimizer_initialization`** (Line 72)
  - *Test optimizer initialization*
  - Category: General
- **`test_performance_optimization`** (Line 81)
  - *Test performance-based optimization*
  - Category: Performance
- **`test_clarity_optimization`** (Line 102)
  - *Test clarity-based optimization*
  - Category: General
- **`test_cost_optimization`** (Line 120)
  - *Test cost-based optimization*
  - Category: General
- **`test_adaptive_optimization`** (Line 137)
  - *Test adaptive optimization based on context*
  - Category: General
- **`test_optimization_with_low_success_rate`** (Line 154)
  - *Test optimization when success rate is low*
  - Category: General
- **`test_optimization_with_high_response_time`** (Line 182)
  - *Test optimization when response time is high*
  - Category: General
- **`test_optimization_with_high_cost`** (Line 210)
  - *Test optimization when cost per request is high*
  - Category: General
- **`test_optimization_history`** (Line 238)
  - *Test optimization history tracking*
  - Category: General
- **`test_optimization_rollback`** (Line 271)
  - *Test optimization rollback functionality*
  - Category: General
- **`test_integration_hooks`** (Line 294)
  - *Test integration hooks for Epic 3 and Epic 4*
  - Category: Integration
- **`test_feature_extraction`** (Line 323)
  - *Test feature extraction for ML models*
  - Category: General
- **`test_improvement_score_calculation`** (Line 340)
  - *Test improvement score calculation*
  - Category: General
- **`test_performance_gain_prediction`** (Line 352)
  - *Test performance gain prediction*
  - Category: Performance
- **`test_cost_reduction_prediction`** (Line 364)
  - *Test cost reduction prediction*
  - Category: General
- **`test_confidence_score_calculation`** (Line 376)
  - *Test confidence score calculation*
  - Category: General
- **`test_task_complexity_calculation`** (Line 385)
  - *Test task complexity calculation*
  - Category: General
- **`test_optimization_with_error_handling`** (Line 400)
  - *Test optimization error handling*
  - Category: General
- **`test_global_optimizer_instance`** (Line 428)
  - *Test global optimizer instance*
  - Category: General
- **`test_optimization_metadata`** (Line 436)
  - *Test optimization metadata storage*
  - Category: General
- **`test_integration_with_template_system`** (Line 481)
  - *Test integration with template system*
  - Category: Integration
- **`test_integration_with_analytics`** (Line 526)
  - *Test integration with analytics system*
  - Category: Integration
- **`test_optimization_speed`** (Line 607)
  - *Test optimization speed for performance targets*
  - Category: General
- **`test_concurrent_optimizations`** (Line 642)
  - *Test handling of concurrent optimizations*
  - Category: General

---

### `unit\prompts\test_prompt_engineering_system.py` (25 tests)

**Description**: Test Suite for Prompt Engineering System
========================================

Comprehensive tests for the prompt engineering system components:
- Template system
- Optimization framework
- A/B testing framework
- Integration testing

This validates all US-PE-01 functionality.

| Metric | Value |
|--------|--------|
| **File Size** | 22.4 KB |
| **Test Classes** | 4 |
| **Test Functions** | 21 |
| **Total Tests** | 25 |

#### Test Classes

- **`TestPromptEngineeringSystem`** (Line 35)
  - *Test the unified prompt engineering system*
  - Category: System
- **`TestTemplateSystem`** (Line 179)
  - *Test the template system component*
  - Category: System
- **`TestOptimizer`** (Line 330)
  - *Test the optimization framework component*
  - Category: General
- **`TestABTesting`** (Line 434)
  - *Test the A/B testing framework component*
  - Category: General

#### Test Functions

- **`test_create_optimized_template`** (Line 55)
  - *Test creating an optimized template*
  - Category: General
- **`test_create_ab_test`** (Line 82)
  - *Test creating an A/B test*
  - Category: General
- **`test_get_optimization_recommendations`** (Line 106)
  - *Test getting optimization recommendations*
  - Category: General
- **`test_render_template_with_context`** (Line 123)
  - *Test rendering template with context*
  - Category: General
- **`test_record_prompt_performance`** (Line 141)
  - *Test recording prompt performance*
  - Category: Performance
- **`test_get_system_status`** (Line 163)
  - *Test getting system status*
  - Category: System
- **`test_create_template`** (Line 195)
  - *Test creating a template*
  - Category: General
- **`test_update_template`** (Line 220)
  - *Test updating a template*
  - Category: General
- **`test_create_version`** (Line 247)
  - *Test creating a new version of a template*
  - Category: General
- **`test_render_template`** (Line 276)
  - *Test rendering a template with context*
  - Category: General
- **`test_get_templates_by_agent`** (Line 294)
  - *Test getting templates by agent type*
  - Category: General
- **`test_optimize_token_reduction`** (Line 346)
  - *Test token reduction optimization*
  - Category: General
- **`test_optimize_clarity`** (Line 364)
  - *Test clarity enhancement optimization*
  - Category: General
- **`test_optimize_context`** (Line 378)
  - *Test context optimization*
  - Category: General
- **`test_get_optimization_recommendations`** (Line 395)
  - *Test getting optimization recommendations*
  - Category: General
- **`test_record_performance`** (Line 412)
  - *Test recording performance metrics*
  - Category: Performance
- **`test_create_test`** (Line 450)
  - *Test creating an A/B test*
  - Category: General
- **`test_start_and_complete_test`** (Line 475)
  - *Test starting and completing a test*
  - Category: System
- **`test_assign_variant`** (Line 502)
  - *Test variant assignment*
  - Category: General
- **`test_record_result`** (Line 523)
  - *Test recording test results*
  - Category: General
- **`test_get_test_summary`** (Line 559)
  - *Test getting test summary*
  - Category: General

---

### `unit\prompts\test_prompt_interface_imports.py` (2 tests)

**Description**: Test script to verify prompt optimization interface imports work correctly.

| Metric | Value |
|--------|--------|
| **File Size** | 4.6 KB |
| **Test Classes** | 0 |
| **Test Functions** | 2 |
| **Total Tests** | 2 |

#### Test Functions

- **`test_imports`** (Line 23)
  - *Test all required imports for the prompt optimization interface*
  - Category: General
- **`test_interface_creation`** (Line 110)
  - *Test creating the interface instance*
  - Category: General

---

### `unit\prompts\test_prompt_management_infrastructure.py` (28 tests)

**Description**: Test suite for US-PE-02: Prompt Management Infrastructure

Tests the advanced prompt management infrastructure including:
- Analytics engine functionality
- Web interface components
- Performance tracking and reporting
- Optimization recommendations
- Integration with existing systems.

| Metric | Value |
|--------|--------|
| **File Size** | 24.2 KB |
| **Test Classes** | 5 |
| **Test Functions** | 23 |
| **Total Tests** | 28 |

#### Test Classes

- **`TestPromptAnalytics`** (Line 66)
  - *Test the prompt analytics engine*
  - Category: General
- **`TestPromptWebInterface`** (Line 230)
  - *Test the web interface components*
  - Category: General
- **`TestIntegrationWithExistingSystems`** (Line 282)
  - *Test integration with existing prompt management systems*
  - Category: Integration
- **`TestPerformanceAndScalability`** (Line 439)
  - *Test performance and scalability of the infrastructure*
  - Category: Performance
- **`TestErrorHandlingAndEdgeCases`** (Line 522)
  - *Test error handling and edge cases*
  - Category: General

#### Test Functions

- **`test_analytics_initialization`** (Line 110)
  - *Test analytics engine initialization*
  - Category: General
- **`test_record_performance_metrics`** (Line 115)
  - *Test recording performance metrics*
  - Category: Performance
- **`test_record_cost_metrics`** (Line 120)
  - *Test recording cost metrics*
  - Category: General
- **`test_record_quality_metrics`** (Line 125)
  - *Test recording quality metrics*
  - Category: General
- **`test_get_performance_summary`** (Line 130)
  - *Test getting performance summary*
  - Category: Performance
- **`test_get_cost_summary`** (Line 142)
  - *Test getting cost summary*
  - Category: General
- **`test_get_quality_summary`** (Line 154)
  - *Test getting quality summary*
  - Category: General
- **`test_generate_optimization_recommendations`** (Line 166)
  - *Test generating optimization recommendations*
  - Category: General
- **`test_get_trend_analysis`** (Line 190)
  - *Test trend analysis functionality*
  - Category: General
- **`test_get_comprehensive_analytics`** (Line 211)
  - *Test comprehensive analytics generation*
  - Category: General
- **`test_web_interface_initialization`** (Line 245)
  - *Test web interface initialization*
  - Category: General
- **`test_get_total_prompts`** (Line 252)
  - *Test getting total prompts count*
  - Category: General
- **`test_get_active_templates`** (Line 258)
  - *Test getting active templates count*
  - Category: General
- **`test_get_prompt_ids`** (Line 264)
  - *Test getting prompt IDs list*
  - Category: General
- **`test_dashboard_metrics`** (Line 271)
  - *Test dashboard metrics calculation*
  - Category: General
- **`test_template_creation_with_analytics`** (Line 305)
  - *Test creating templates and tracking analytics*
  - Category: General
- **`test_optimization_with_analytics`** (Line 341)
  - *Test optimization with analytics tracking*
  - Category: General
- **`test_comprehensive_workflow`** (Line 373)
  - *Test a comprehensive workflow with all components*
  - Category: System
- **`test_bulk_metrics_recording`** (Line 450)
  - *Test recording many metrics efficiently*
  - Category: General
- **`test_concurrent_analytics_access`** (Line 479)
  - *Test concurrent access to analytics*
  - Category: General
- **`test_invalid_metrics_handling`** (Line 533)
  - *Test handling of invalid metrics*
  - Category: General
- **`test_missing_data_handling`** (Line 555)
  - *Test handling of missing data*
  - Category: General
- **`test_database_corruption_handling`** (Line 566)
  - *Test handling of database corruption scenarios*
  - Category: General

---

### `unit\test_adaptive_retrieval.py` (11 tests)

**Description**: Unit Tests for Adaptive RAG Chunk Retrieval System

Tests for QueryAnalyzer and AdaptiveRetrievalStrategy components.

| Metric | Value |
|--------|--------|
| **File Size** | 16.1 KB |
| **Test Classes** | 2 |
| **Test Functions** | 9 |
| **Total Tests** | 11 |

#### Test Classes

- **`TestQueryAnalyzer`** (Line 16)
  - *Test suite for QueryAnalyzer*
  - Category: General
- **`TestAdaptiveRetrievalStrategy`** (Line 158)
  - *Test suite for AdaptiveRetrievalStrategy*
  - Category: General

#### Test Functions

- **`test_simple_factual_query`** (Line 24)
  - *Test classification of simple factual queries*
  - Category: General
- **`test_moderate_conceptual_query`** (Line 39)
  - *Test classification of moderate conceptual queries*
  - Category: General
- **`test_complex_conceptual_query`** (Line 52)
  - *Test classification of complex conceptual queries*
  - Category: General
- **`test_multi_hop_reasoning_query`** (Line 66)
  - *Test classification of multi-hop reasoning queries*
  - Category: General
- **`test_complexity_score_calculation`** (Line 79)
  - *Test complexity score calculation*
  - Category: General
- **`test_specificity_calculation`** (Line 97)
  - *Test specificity score calculation*
  - Category: General
- **`test_multiple_concepts_detection`** (Line 111)
  - *Test detection of multiple concepts in query*
  - Category: General
- **`test_reasoning_detection`** (Line 125)
  - *Test detection of reasoning requirements*
  - Category: General
- **`test_characteristics_summary`** (Line 144)
  - *Test generation of characteristics summary*
  - Category: General

---

### `unit\test_base_agent.py` (20 tests)

**Description**: Tests for the BaseAgent class to identify and fix the "src property must be a valid json object" error.

| Metric | Value |
|--------|--------|
| **File Size** | 16.2 KB |
| **Test Classes** | 2 |
| **Test Functions** | 18 |
| **Total Tests** | 20 |

#### Test Classes

- **`TestBaseAgent`** (Line 29)
  - *Test cases for BaseAgent class*
  - Category: General
- **`TestGeminiAPIErrorScenarios`** (Line 320)
  - *Test scenarios specifically for Gemini API error handling*
  - Category: Integration

#### Test Functions

- **`test_validate_gemini_config_success`** (Line 94)
  - *Test successful Gemini configuration validation*
  - Category: General
- **`test_validate_gemini_config_no_client`** (Line 98)
  - *Test Gemini configuration validation with no client*
  - Category: General
- **`test_validate_gemini_config_no_generate_content`** (Line 103)
  - *Test Gemini configuration validation with missing generate_content method*
  - Category: General
- **`test_validate_gemini_config_no_config`** (Line 110)
  - *Test Gemini configuration validation with no config*
  - Category: General
- **`test_validate_gemini_config_no_parameters`** (Line 129)
  - *Test Gemini configuration validation with no parameters*
  - Category: General
- **`test_parse_json_response_simple_json`** (Line 225)
  - *Test parsing simple JSON response*
  - Category: General
- **`test_parse_json_response_with_code_blocks`** (Line 231)
  - *Test parsing JSON response with code blocks*
  - Category: General
- **`test_parse_json_response_with_generic_code_blocks`** (Line 237)
  - *Test parsing JSON response with generic code blocks*
  - Category: General
- **`test_parse_json_response_with_trailing_commas`** (Line 243)
  - *Test parsing JSON response with trailing commas*
  - Category: General
- **`test_parse_json_response_with_trailing_commas_in_arrays`** (Line 249)
  - *Test parsing JSON response with trailing commas in arrays*
  - Category: General
- **`test_parse_json_response_invalid_json`** (Line 255)
  - *Test parsing invalid JSON response*
  - Category: General
- **`test_parse_json_response_malformed_json`** (Line 263)
  - *Test parsing malformed JSON response*
  - Category: General
- **`test_prepare_prompt`** (Line 271)
  - *Test prompt preparation*
  - Category: General
- **`test_prepare_prompt_with_kwargs`** (Line 279)
  - *Test prompt preparation with additional kwargs*
  - Category: General
- **`test_validate_input_success`** (Line 288)
  - *Test successful input validation*
  - Category: General
- **`test_validate_input_missing_required_fields`** (Line 292)
  - *Test input validation with missing required fields*
  - Category: General
- **`test_handle_error`** (Line 297)
  - *Test error handling*
  - Category: General
- **`test_update_state_with_result`** (Line 308)
  - *Test state update with results*
  - Category: General

---

### `unit\test_fast_utils.py` (14 tests)

**Description**: Fast unit tests for utilities - optimized for quick startup.

| Metric | Value |
|--------|--------|
| **File Size** | 6.6 KB |
| **Test Classes** | 1 |
| **Test Functions** | 13 |
| **Total Tests** | 14 |

#### Test Classes

- **`TestFastUtilities`** (Line 173)
  - *Fast utility test class*
  - Category: General

#### Test Functions

- **`test_basic_path_operations`** (Line 21)
  - *Test basic path operations without heavy imports*
  - Category: General
- **`test_environment_variables`** (Line 41)
  - *Test environment variable handling*
  - Category: General
- **`test_string_operations`** (Line 55)
  - *Test basic string operations*
  - Category: General
- **`test_list_operations`** (Line 65)
  - *Test basic list operations*
  - Category: General
- **`test_dict_operations`** (Line 79)
  - *Test basic dictionary operations*
  - Category: General
- **`test_json_operations`** (Line 93)
  - *Test JSON operations without heavy imports*
  - Category: General
- **`test_pathlib_operations`** (Line 110)
  - *Test pathlib operations*
  - Category: General
- **`test_basic_error_handling`** (Line 124)
  - *Test basic error handling patterns*
  - Category: General
- **`test_basic_imports`** (Line 142)
  - *Test that basic imports work quickly*
  - Category: General
- **`test_performance_timer`** (Line 161)
  - *Test a simple performance timer*
  - Category: Performance
- **`test_startup_performance`** (Line 191)
  - *Test that test startup is reasonably fast*
  - Category: Performance
- **`test_class_initialization`** (Line 176)
  - *Test class initialization is fast*
  - Category: General
- **`test_method_execution`** (Line 180)
  - *Test method execution is fast*
  - Category: General

---

### `unit\test_intelligent_rule_loader.py` (16 tests)

**Description**: Comprehensive test suite for the Intelligent Rule Loader

Tests the distinction between checking rule applicability and selective application.

| Metric | Value |
|--------|--------|
| **File Size** | 20.3 KB |
| **Test Classes** | 1 |
| **Test Functions** | 15 |
| **Total Tests** | 16 |

#### Test Classes

- **`TestIntelligentRuleLoader`** (Line 24)
  - *Test suite for intelligent rule selection system*
  - Category: Performance

#### Test Functions

- **`test_always_check_applicability_but_selective_application`** (Line 63)
  - *Test that rules are always checked but selectively applied*
  - Category: General
- **`test_critical_rules_always_included`** (Line 109)
  - *Test that critical foundation rules are always included regardless of context*
  - Category: General
- **`test_task_type_specific_selection`** (Line 131)
  - *Test that rules are selected based on task type*
  - Category: General
- **`test_complexity_based_selection`** (Line 173)
  - *Test that rule selection considers task complexity*
  - Category: General
- **`test_quality_requirements_affect_selection`** (Line 195)
  - *Test that quality requirements affect rule selection*
  - Category: General
- **`test_time_pressure_affects_selection`** (Line 219)
  - *Test that time pressure affects rule selection*
  - Category: General
- **`test_keyword_based_relevance`** (Line 243)
  - *Test that keyword matching affects rule selection*
  - Category: General
- **`test_security_requirements_affect_selection`** (Line 269)
  - *Test that security requirements affect rule selection*
  - Category: Security
- **`test_confidence_score_calculation`** (Line 303)
  - *Test that confidence scores are calculated correctly*
  - Category: General
- **`test_token_savings_calculation`** (Line 319)
  - *Test that token savings are calculated correctly*
  - Category: General
- **`test_selection_reasoning`** (Line 331)
  - *Test that selection reasoning is provided for all rules*
  - Category: General
- **`test_selection_history_tracking`** (Line 347)
  - *Test that rule selections are tracked in history*
  - Category: General
- **`test_edge_cases`** (Line 362)
  - *Test edge cases and boundary conditions*
  - Category: General
- **`test_performance_requirements_affect_selection`** (Line 382)
  - *Test that performance requirements affect rule selection*
  - Category: Performance
- **`test_domain_specific_selection`** (Line 416)
  - *Test that domain affects rule selection*
  - Category: General

---

### `unit\test_quality_assurance.py` (39 tests)

**Description**: Unit tests for the Quality Assurance System.

| Metric | Value |
|--------|--------|
| **File Size** | 25.5 KB |
| **Test Classes** | 7 |
| **Test Functions** | 32 |
| **Total Tests** | 39 |

#### Test Classes

- **`TestQualityAssuranceSystem`** (Line 21)
  - *Test the Quality Assurance System*
  - Category: System
- **`TestValidationMethods`** (Line 65)
  - *Test validation methods*
  - Category: General
- **`TestTypeSpecificValidation`** (Line 180)
  - *Test type-specific validation methods*
  - Category: General
- **`TestQualityGateValidation`** (Line 311)
  - *Test complete quality gate validation*
  - Category: General
- **`TestQualityMetricsAndReporting`** (Line 420)
  - *Test quality metrics and reporting functionality*
  - Category: General
- **`TestEdgeCases`** (Line 529)
  - *Test edge cases and error handling*
  - Category: General
- **`TestDataStructures`** (Line 580)
  - *Test data structures and enums*
  - Category: General

#### Test Functions

- **`test_initialization`** (Line 28)
  - *Test system initialization*
  - Category: General
- **`test_quality_thresholds`** (Line 38)
  - *Test quality thresholds for all agents*
  - Category: General
- **`test_validation_rules`** (Line 52)
  - *Test validation rules for all output types*
  - Category: General
- **`test_validate_output_structure_valid`** (Line 72)
  - *Test structure validation with valid output*
  - Category: General
- **`test_validate_output_structure_invalid`** (Line 87)
  - *Test structure validation with invalid output*
  - Category: General
- **`test_validate_output_structure_missing_fields`** (Line 99)
  - *Test structure validation with missing required fields*
  - Category: General
- **`test_validate_output_content_valid`** (Line 116)
  - *Test content validation with valid output*
  - Category: General
- **`test_validate_output_content_empty_values`** (Line 131)
  - *Test content validation with empty values*
  - Category: General
- **`test_validate_output_consistency_valid`** (Line 149)
  - *Test consistency validation with valid output*
  - Category: General
- **`test_validate_output_completeness_valid`** (Line 163)
  - *Test completeness validation with valid output*
  - Category: System
- **`test_validate_requirements_output_valid`** (Line 187)
  - *Test requirements validation with valid output*
  - Category: General
- **`test_validate_requirements_output_no_functional`** (Line 203)
  - *Test requirements validation without functional requirements*
  - Category: General
- **`test_validate_architecture_output_valid`** (Line 220)
  - *Test architecture validation with valid output*
  - Category: General
- **`test_validate_code_output_valid`** (Line 234)
  - *Test code validation with valid output*
  - Category: General
- **`test_validate_review_output_valid`** (Line 250)
  - *Test review validation with valid output*
  - Category: General
- **`test_validate_review_output_invalid_score`** (Line 265)
  - *Test review validation with invalid score*
  - Category: General
- **`test_validate_security_output_valid`** (Line 281)
  - *Test security validation with valid output*
  - Category: Security
- **`test_validate_documentation_output_valid`** (Line 296)
  - *Test documentation validation with valid output*
  - Category: General
- **`test_validate_agent_output_requirements_passed`** (Line 318)
  - *Test complete requirements agent validation with passing result*
  - Category: General
- **`test_validate_agent_output_requirements_failed`** (Line 350)
  - *Test complete requirements agent validation with failing result*
  - Category: General
- **`test_validate_agent_output_code_passed`** (Line 375)
  - *Test complete code generator validation with passing result*
  - Category: General
- **`test_validate_agent_output_review_passed`** (Line 397)
  - *Test complete code reviewer validation with passing result*
  - Category: General
- **`test_get_quality_metrics`** (Line 454)
  - *Test getting quality metrics*
  - Category: General
- **`test_get_validation_history`** (Line 463)
  - *Test getting validation history*
  - Category: General
- **`test_get_gate_results`** (Line 475)
  - *Test getting gate results*
  - Category: General
- **`test_generate_quality_report`** (Line 487)
  - *Test generating quality report*
  - Category: General
- **`test_validate_agent_output_unknown_agent`** (Line 536)
  - *Test validation with unknown agent*
  - Category: General
- **`test_validate_agent_output_unknown_type`** (Line 546)
  - *Test validation with unknown output type*
  - Category: General
- **`test_validate_agent_output_empty_dict`** (Line 556)
  - *Test validation with empty dictionary*
  - Category: General
- **`test_validate_agent_output_none_values`** (Line 566)
  - *Test validation with None values*
  - Category: General
- **`test_dataclass_default_field_generation`** (Line 586)
  - *Test that dataclasses generate required default fields correctly*
  - Category: General
- **`test_quality_gate_result_dataclass`** (Line 608)
  - *Test QualityGateResult dataclass*
  - Category: General

---

### `unit\test_strategic_rule_selector.py` (21 tests)

**Description**: Unit tests for Strategic Rule Selector.

| Metric | Value |
|--------|--------|
| **File Size** | 22.3 KB |
| **Test Classes** | 1 |
| **Test Functions** | 20 |
| **Total Tests** | 21 |

#### Test Classes

- **`TestStrategicRuleSelector`** (Line 29)
  - *Test suite for StrategicRuleSelector*
  - Category: General

#### Test Functions

- **`test_initialization`** (Line 89)
  - *Test StrategicRuleSelector initialization*
  - Category: General
- **`test_task_analysis`** (Line 97)
  - *Test task analysis functionality*
  - Category: General
- **`test_keyword_extraction`** (Line 115)
  - *Test keyword extraction from task descriptions*
  - Category: General
- **`test_intent_classification`** (Line 136)
  - *Test intent classification functionality*
  - Category: General
- **`test_applicable_rules_selection`** (Line 153)
  - *Test applicable rules selection based on task analysis*
  - Category: General
- **`test_rule_scoring`** (Line 175)
  - *Test rule scoring functionality*
  - Category: General
- **`test_optimal_rule_selection`** (Line 208)
  - *Test optimal rule selection within constraints*
  - Category: General
- **`test_parallel_group_generation`** (Line 237)
  - *Test parallel execution group generation*
  - Category: General
- **`test_application_sequence_creation`** (Line 258)
  - *Test application sequence creation*
  - Category: General
- **`test_token_savings_calculation`** (Line 278)
  - *Test token savings calculation*
  - Category: General
- **`test_selection_confidence_calculation`** (Line 306)
  - *Test selection confidence calculation*
  - Category: General
- **`test_complete_rule_selection_workflow`** (Line 332)
  - *Test complete rule selection workflow*
  - Category: System
- **`test_file_operation_rule_selection`** (Line 361)
  - *Test rule selection for file operation tasks*
  - Category: General
- **`test_code_implementation_rule_selection`** (Line 378)
  - *Test rule selection for code implementation tasks*
  - Category: General
- **`test_complexity_based_rule_selection`** (Line 407)
  - *Test rule selection based on task complexity*
  - Category: General
- **`test_risk_based_rule_selection`** (Line 435)
  - *Test rule selection based on risk level*
  - Category: General
- **`test_quality_requirements_rule_selection`** (Line 465)
  - *Test rule selection based on quality requirements*
  - Category: General
- **`test_caching_mechanism`** (Line 495)
  - *Test caching mechanism for rule selections*
  - Category: General
- **`test_database_recording`** (Line 510)
  - *Test database recording of rule selections*
  - Category: General
- **`test_optimization_report_generation`** (Line 521)
  - *Test optimization report generation*
  - Category: General

---

### `unit\test_utils.py` (4 tests)

**Description**: Test utilities and common testing functions for AI Development Agent.

| Metric | Value |
|--------|--------|
| **File Size** | 8.8 KB |
| **Test Classes** | 2 |
| **Test Functions** | 2 |
| **Total Tests** | 4 |

#### Test Classes

- **`TestConfig`** (Line 24)
  - *Test configuration and utilities*
  - Category: General
- **`TestStateBuilder`** (Line 66)
  - *Helper for building test states*
  - Category: General

#### Test Functions

- **`test_config`** (Line 144)
  - *Fixture providing test configuration*
  - Category: General
- **`test_state`** (Line 164)
  - *Fixture providing test state*
  - Category: General

---


## ✅ **Naming Convention Validation**

🎉 **All naming conventions are correct!**


## 📋 **Test Organization Analysis**

### Directory Structure (22 directories)

- `./` - 2 files, 23 tests
- `agile/` - 1 files, 14 tests
- `config/` - 1 files, 0 tests
- `infrastructure/` - 2 files, 52 tests
- `integration/` - 10 files, 38 tests
- `integration\agents/` - 1 files, 41 tests
- `integration\prompts/` - 1 files, 31 tests
- `isolated/` - 1 files, 1 tests
- `langgraph/` - 4 files, 24 tests
- `langgraph\integration/` - 1 files, 2 tests
- `langgraph\unit/` - 2 files, 19 tests
- `mcp/` - 9 files, 89 tests
- `optimization/` - 2 files, 1 tests
- `scripts/` - 1 files, 0 tests
- `security/` - 1 files, 14 tests
- `supervisor/` - 2 files, 21 tests
- `system/` - 1 files, 0 tests
- `test_utils\automated_testing/` - 1 files, 1 tests
- `unit/` - 7 files, 125 tests
- `unit\agents/` - 3 files, 37 tests
- `unit\prompts/` - 4 files, 82 tests
- `workflow/` - 4 files, 94 tests

### Test Distribution by Category

| Category | Test Count | Percentage |
|----------|------------|------------|
| Unit Tests | 263 | 37.1% |
| Root Tests | 208 | 29.3% |
| Integration Tests | 112 | 15.8% |
| Infrastructure Tests | 52 | 7.3% |
| LangGraph Tests | 24 | 3.4% |
| Supervisor Tests | 21 | 3.0% |
| Agile Tests | 14 | 2.0% |
| Security Tests | 14 | 2.0% |
| Isolated Tests | 1 | 0.1% |
| System Tests | 0 | 0.0% |


## 💡 **Recommendations**

### Improvement Opportunities

1. 📝 **Add documentation** to 3 test files without docstrings
2. 🧹 **Remove or implement** 7 empty test files
3. ⚖️ **Increase unit test coverage** - Currently 37.1%, recommended >60%

### Best Practices Checklist

- ✅ Follow naming conventions (`test_*.py`, `Test*`, `test_*`)
- ✅ Organize tests by category and functionality
- ✅ Write descriptive test names and docstrings
- ✅ Keep test files focused and manageable (<50KB)
- ✅ Maintain good balance between unit and integration tests
- ✅ Use appropriate test fixtures and mocking
- ✅ Regular test catalogue updates

