# User Story: US-UKD-001 - Unified Keyword Detection System Implementation

**Epic**: Agent Context Management and Monitoring  
**Sprint**: Sprint 4  
**Story Points**: 8  
**Priority**: HIGH  
**Created**: 2025-09-26  
**Status**: 🔄 REOPENED - Critical Missing: Real Cursor Conversation Monitoring  

## Story Description

**As a** developer using the AI-Dev-Agent system  
**I want** a unified, YAML-based keyword detection system that triggers context switches and shows real-time agent activity  
**So that** I can see transparent, accurate monitoring of all agent activities and context changes in the live dashboard  

## Background

The current system has scattered, incomplete keyword detection implementations that:
- Use hardcoded keyword mappings instead of the comprehensive YAML configuration
- Show outdated or incorrect "last keyword" information (e.g., showing `@code` when `@agile` was used)
- Don't properly integrate with the agent monitoring dashboard
- Missing critical keywords like `@analyze`
- Have inconsistent behavior across different components

We have a comprehensive `optimized_context_rule_mappings.yaml` configuration that defines all contexts, keywords, and rules, but it's not being used by the detection systems.

## Acceptance Criteria

### ✅ Primary Acceptance Criteria

1. **YAML-Based Configuration Loading**
   - [x] Create unified keyword detector that loads from `optimized_context_rule_mappings.yaml`
   - [x] Support all contexts defined in YAML (CODING, TESTING, AGILE, DEBUGGING, etc.)
   - [x] Load complete keyword mappings with rules and agent types
   - [x] Handle missing or malformed YAML gracefully

2. **Complete Keyword Coverage**
   - [x] Support all keywords from YAML config (`@agile`, `@code`, `@test`, `@debug`, etc.)
   - [x] Add missing critical keywords (`@analyze`, `@monitor`, `@deploy`)
   - [x] Map each keyword to correct context and rule set
   - [x] Ensure consistent keyword detection across all components

3. **Real-Time Context Switching**
   - [x] Trigger actual context switches when keywords detected
   - [x] Update universal agent tracker with context changes
   - [x] Record rule activations for each context switch
   - [ ] Show context switches immediately in live monitor
   - [ ] **🎯 CRITICAL: Capture actual Cursor conversation keywords in real-time**

4. **Agent Monitor Integration**
   - [x] Replace old detection systems with unified detector in main app
   - [ ] Display context switches in "Complete Agent Activity History"
   - [ ] Show rule loading changes when contexts switch
   - [ ] Update metrics to reflect real keyword usage

### 🎯 Secondary Acceptance Criteria

5. **Professional Agent Lifecycle Management**
   - [ ] Fix "121 active agents" issue (implement proper deactivation)
   - [ ] Implement proper agent status tracking (active/inactive/completed/error)
   - [ ] Clean up stale agent sessions automatically
   - [ ] Provide accurate agent count metrics

6. **Remove Fake Data and Inconsistencies**
   - [ ] Remove all simulated/fake data from agent monitoring displays
   - [ ] Ensure all displayed data comes from real database queries
   - [ ] Fix inconsistent "last keyword" reporting
   - [ ] Validate all metrics show actual system state

7. **Professional Dashboard**
   - [ ] Create clean, professional agent activity dashboard
   - [ ] Show only real, measured data (no placeholder values)
   - [ ] Implement proper error handling and fallback displays
   - [ ] Ensure consistent UI/UX across monitoring components

## Technical Implementation

### 📋 Tasks Breakdown

1. **Unified Detector Creation** (3 points) ✅ COMPLETED
   - [x] Create `utils/unified_keyword_detector.py`
   - [x] Load configuration from YAML file
   - [x] Build comprehensive keyword mapping
   - [x] Implement context switching logic

2. **Main App Integration** (2 points) ✅ COMPLETED
   - [x] Replace old keyword detection initialization
   - [x] Update conversation processing functions
   - [x] Add real-time keyword detection
   - [x] Integrate with universal agent tracker

3. **Monitor Visibility Validation** (1 point) 🔄 IN PROGRESS
   - [ ] Verify `@agile` keyword triggers visible context switches
   - [ ] Test that different rules load for different contexts
   - [ ] Confirm real-time updates in agent monitor
   - [ ] Validate accurate "last keyword" reporting

**🚨 CRITICAL MISSING TASK:**

6. **Real Cursor Conversation Integration** (2 points) ⚠️ CRITICAL GAP
   - [ ] **Hook into actual Cursor AI chat conversation interface**
   - [ ] **Capture keywords typed in this conversation in real-time**
   - [ ] **Log actual user messages (@agile test message) to database**
   - [ ] **Show TODAY'S actual keyword usage in agent monitor**
   - [ ] **Replace old simulated data with real conversation data**

4. **Legacy System Cleanup** (1 point) 🔄 IN PROGRESS
   - [ ] Remove old hardcoded keyword detection systems
   - [ ] Clean up unused detection modules
   - [ ] Update all references to use unified system
   - [ ] Remove duplicate/conflicting implementations

5. **Professional Dashboard Implementation** (1 point) 📋 PENDING
   - [ ] Create professional agent monitor (rename from "professional")
   - [ ] Implement proper agent lifecycle management
   - [ ] Add agent cleanup and status tracking
   - [ ] Remove all fake/simulated data displays

### 🔧 Technical Details

**YAML Configuration Structure:**
```yaml
contexts:
  AGILE:
    detection_patterns:
      keywords: ["@agile", "@sprint", "@story", "@backlog"]
    rules:
      foundation: ["ethical_dna_core", "safety_first_principle", ...]
      context: ["agile_coordination"]
      tools: ["project_management_patterns"]
    agent_future: "ScrumMasterAgent"
```

**Key Components:**
- `utils/unified_keyword_detector.py` - Main detection system
- `utils/yaml_based_keyword_detector.py` - YAML loader (deprecated by unified)
- `utils/comprehensive_keyword_detector.py` - Extended mappings (deprecated by unified)
- Integration points in `apps/universal_composition_app.py`

**Expected Context Switches:**
- `@agile` → AGILE context → 5 agile rules activated
- `@code` → CODING context → 5 development rules activated  
- `@analyze` → ANALYSIS context → 5 analysis rules activated
- `@test` → TESTING context → 5 testing rules activated

## Definition of Done

- [x] **YAML configuration loaded** - Unified detector reads from optimized_context_rule_mappings.yaml
- [x] **Complete keyword coverage** - All keywords from YAML config supported
- [x] **Unified system integration** - Old detection systems replaced with unified detector
- [ ] **Visible context switches** - Keywords trigger visible changes in agent monitor
- [ ] **Accurate monitoring** - All displayed data reflects real system state
- [ ] **Professional UI** - Clean dashboard with no fake data or placeholder values
- [ ] **Proper agent lifecycle** - Correct agent counts and status management

## Testing Strategy

### 🧪 Manual Testing Scenarios

1. **Keyword Detection Test**
   ```
   GIVEN: User types "@agile now the system should show context switch"
   WHEN: Message is processed by unified detector
   THEN: Context switches from DEFAULT to AGILE
   AND: 5 agile rules are activated
   AND: Change is visible in agent monitor immediately
   ```

2. **Multiple Keyword Test**
   ```
   GIVEN: User types "@agile @code @test multiple keywords"
   WHEN: Message is processed
   THEN: All keywords are detected and processed
   AND: Context switches follow priority order
   AND: All rule activations are logged
   ```

3. **Monitor Accuracy Test**
   ```
   GIVEN: Keywords have been used throughout the day
   WHEN: User checks "Complete Agent Activity History"
   THEN: All context switches from today are shown
   AND: No fake or placeholder data is displayed
   AND: "Last keyword" shows the actual last keyword used
   ```

### 🔬 Automated Testing

- [ ] Unit tests for unified keyword detector
- [ ] Integration tests for YAML configuration loading
- [ ] UI tests for agent monitor display
- [ ] Database tests for context switch logging

## Notes and Considerations

### 🎯 Context Detection Impact
This story itself was created in response to `@agile` keyword usage, demonstrating the workflow integration working correctly.

### 🔗 Dependencies
- Requires `optimized_context_rule_mappings.yaml` configuration file
- Depends on universal agent tracker system
- Integrates with main Streamlit application
- Connected to US-TST-002 (test suite fixes)

### 🚨 Risks
- YAML configuration changes could break detection
- Multiple keyword detection might create conflicts
- Agent lifecycle cleanup could affect active sessions
- Performance impact of real-time processing

### 📊 Success Metrics
- Keyword detection accuracy: 100%
- Context switch latency: < 1 second
- Agent monitor refresh time: < 3 seconds
- False positive rate: 0%
- Fake data instances: 0

## Sprint Integration

This story is central to Sprint 4's objectives of improving system transparency and agent monitoring. It directly supports:

- Enhanced developer experience through accurate monitoring
- Improved system reliability through unified detection
- Better agile workflow integration through context awareness
- Foundation for future agent swarm coordination

The completion of this story enables reliable keyword-driven context switching and provides the transparency needed for effective agent system development.

---

**Story Owner**: Development Team  
**Technical Lead**: AI Assistant  
**Stakeholders**: Product Team, DevOps Team, End Users  
**Estimated Completion**: Sprint 4 (Current Sprint)  
**Related Stories**: US-TST-002 (Test Suite Fixes), US-MON-001 (Agent Monitoring)
