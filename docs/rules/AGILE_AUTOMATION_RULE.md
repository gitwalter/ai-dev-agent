# Mandatory Agile Story Automation Rule

**CRITICAL**: All user stories, tasks, and agile work must be created and managed through the automated agile story system. Manual story creation is prohibited to ensure consistency and complete artifact integration.

## Description
This rule enforces the use of the automated agile story creation system for all development work, ensuring consistent documentation, proper estimation, complete artifact updates, and integrated progress tracking.

## Core Requirements

### 1. Mandatory Story Creation Process
**REQUIRED**: All development work must begin with automated story creation
```python
# CORRECT: Use automated story creation
from utils.agile.agile_story_automation import create_story

story = create_story(
    title="Fix Health Dashboard NumPy Error",
    description="Resolve NumPy 2.0 compatibility issues preventing health dashboard from loading...",
    business_justification="Critical system functionality blocked, preventing system health monitoring...",
    priority=Priority.CRITICAL
)

# FORBIDDEN: Manual story creation or starting work without stories
# Starting work without proper story documentation
```

### 2. Automatic Artifact Updates
**MANDATORY**: All agile artifacts must be updated automatically
- User Story Catalog updates automatically
- Task Catalog updates automatically  
- Sprint Backlog updates automatically
- Epic Overview updates automatically
- Progress tracking updates automatically

### 3. Work-in-Progress Tracking
**REQUIRED**: When starting work on any story, automatically mark as in progress
```python
# MANDATORY: Mark story in progress when work begins
from utils.agile.agile_story_automation import mark_in_progress

# When beginning work on US-022
mark_in_progress("US-022")  # Automatically updates all artifacts
```

## Automation System Components

### 1. Story Generation Features
**AUTOMATED GENERATION**:
- ✅ **Story ID Assignment**: Automatic sequential numbering
- ✅ **Task Breakdown**: Automatic task generation based on story type
- ✅ **Estimation**: Auto-estimation with manual override capability
- ✅ **Acceptance Criteria**: Default criteria with customization
- ✅ **Risk Assessment**: Automatic risk identification
- ✅ **Success Metrics**: Context-aware metrics generation

### 2. Artifact Integration
**AUTOMATIC UPDATES**:
- ✅ **User Story Catalog**: Real-time catalog updates
- ✅ **Task Catalog**: Task tracking and progress updates  
- ✅ **Sprint Backlog**: Sprint planning and capacity tracking
- ✅ **Epic Overview**: Epic progress and story distribution
- ✅ **Cross-Sprint Tracking**: Dependencies and milestone tracking

### 3. Quality Assurance
**BUILT-IN QUALITY**:
- ✅ **Consistent Formatting**: Standard markdown formatting
- ✅ **Complete Documentation**: All required sections included
- ✅ **Proper Estimation**: Evidence-based estimation algorithms
- ✅ **Dependency Tracking**: Automatic dependency validation
- ✅ **Progress Monitoring**: Real-time status updates

## Usage Patterns

### 1. Critical Bug Fixes
```python
# PATTERN: Critical bug fix story creation
story = create_story(
    title="Fix [Component] [Issue Type]",
    description="Detailed technical description of the issue and impact...",
    business_justification="Critical system impact explanation...",
    priority=Priority.CRITICAL,
    story_points=3  # Override auto-estimation if needed
)
# Result: Story automatically marked IN PROGRESS for critical issues
```

### 2. Feature Development
```python
# PATTERN: Feature development story creation
story = create_story(
    title="Implement [Feature Name]",
    description="Feature requirements and scope definition...",
    business_justification="Business value and user impact...",
    priority=Priority.HIGH,
    epic="Feature Development",
    dependencies=["US-001", "US-002"]  # Specify dependencies
)
```

### 3. Infrastructure Work
```python
# PATTERN: Infrastructure/automation story creation
story = create_story(
    title="Automate [Process/System]",
    description="Automation requirements and scope...",
    business_justification="Efficiency gains and operational improvements...",
    priority=Priority.MEDIUM,
    epic="Infrastructure"
)
```

### 4. Technical Debt
```python
# PATTERN: Technical debt story creation
story = create_story(
    title="Refactor [Component] for [Reason]",
    description="Technical debt description and refactoring plan...",
    business_justification="Long-term maintainability and quality improvements...",
    priority=Priority.LOW,
    epic="Technical Debt"
)
```

## Story Types and Auto-Generation

### 1. Bug Fix Stories
**AUTO-GENERATED TASKS**:
- Analyze root cause and impact (1h)
- Implement fix and solution (2h) 
- Test fix and verify resolution (1h)
- Update documentation and artifacts (0.5h)

### 2. Monitoring/Health Stories  
**AUTO-GENERATED TASKS**:
- Design monitoring architecture (2h)
- Implement monitoring endpoints (3h)
- Create monitoring dashboard (2.5h)
- Implement alerting system (1.5h)
- Integration testing and validation (2h)

### 3. Automation Stories
**AUTO-GENERATED TASKS**:
- Analyze automation requirements (1.5h)
- Design automation workflow (2h)
- Implement automation scripts (4h)
- Create automation testing (2h)
- Integration and deployment (1.5h)

### 4. Generic Feature Stories
**AUTO-GENERATED TASKS**:
- Requirements analysis and design (2h)
- Core implementation (4h)
- Testing and validation (2h)
- Documentation and integration (1h)

## Integration with Development Workflow

### 1. Before Starting Any Work
```python
# MANDATORY WORKFLOW
# 1. Create story first
story = create_story(title, description, justification)

# 2. System automatically:
#    - Assigns story ID
#    - Generates tasks  
#    - Updates all catalogs
#    - Creates story file
#    - Tracks in sprint backlog

# 3. Begin work (triggers in-progress status)
mark_in_progress(story.story_id)

# 4. System automatically:
#    - Updates status across all artifacts
#    - Tracks progress in catalogs
#    - Updates sprint metrics
```

### 2. During Development
- **Task Completion**: Mark tasks complete as they finish
- **Blocker Identification**: Add blockers to story automatically
- **Progress Updates**: Real-time progress tracking
- **Artifact Sync**: All changes reflected across project

### 3. Story Completion  
- **Verification**: All acceptance criteria met
- **Testing**: All tests passing
- **Documentation**: All artifacts updated
- **Closure**: Automatic story completion workflow

## Catalog Management

### 1. User Story Catalog Updates
**AUTOMATIC TRACKING**:
- Story creation immediately updates catalog
- Status changes reflected in real-time
- Progress percentages calculated automatically
- Dependencies tracked and validated

### 2. Task Catalog Updates
**AUTOMATIC TASK MANAGEMENT**:
- Tasks generated and tracked automatically
- Task completion updates sprint velocity
- Effort tracking for estimation improvements
- Dependency resolution monitoring

### 3. Sprint Integration
**SPRINT PLANNING AUTOMATION**:
- Stories automatically available for sprint planning
- Capacity calculations include auto-generated estimates
- Sprint backlog updates with story assignments
- Velocity tracking across sprint iterations

## Quality Gates

### 1. Story Creation Validation
**MANDATORY CHECKS**:
- [ ] Title follows naming conventions
- [ ] Description includes sufficient detail
- [ ] Business justification clearly stated
- [ ] Acceptance criteria comprehensive
- [ ] Tasks properly generated and estimated
- [ ] All artifacts updated successfully

### 2. Work-in-Progress Validation
**PROGRESS TRACKING**:
- [ ] Story marked in progress when work begins
- [ ] Task progress tracked accurately
- [ ] Blockers identified and documented
- [ ] Dependencies validated and current
- [ ] Artifacts synchronized across project

### 3. Completion Validation
**STORY CLOSURE**:
- [ ] All acceptance criteria met
- [ ] All tasks completed
- [ ] Tests passing and documented
- [ ] Documentation updated
- [ ] No regressions introduced
- [ ] Artifacts reflect completion

## Error Prevention

### 1. Common Violations to Avoid
- ❌ **Manual Story Creation**: Creating stories without automation
- ❌ **Incomplete Artifacts**: Missing catalog updates
- ❌ **Status Desync**: Manual status changes without artifact updates
- ❌ **Estimation Bypass**: Skipping proper estimation process
- ❌ **Documentation Gaps**: Incomplete story documentation

### 2. Required Workflow Patterns
- ✅ **Automation First**: Always use automated story creation
- ✅ **Complete Integration**: All artifacts updated automatically
- ✅ **Progress Tracking**: Real-time status across all documents
- ✅ **Quality Assurance**: Built-in validation and verification
- ✅ **Consistency**: Standard formatting and documentation

## Tool Integration

### 1. Command Line Usage
```bash
# Create story from command line
python -m utils.agile.agile_story_automation \
  --title "Fix Health Dashboard" \
  --description "NumPy compatibility fix..." \
  --justification "Critical system restoration..." \
  --priority critical
```

### 2. Script Integration
```python
# Import and use in scripts
from utils.agile.agile_story_automation import create_story, mark_in_progress

# Automatically create stories during development
story = create_story(
    title="Automated Story Creation",
    description="System-generated story...",
    business_justification="Automation efficiency..."
)

# Track progress programmatically
mark_in_progress(story.story_id)
```

### 3. IDE Integration
- **Code Actions**: Create stories from code comments
- **Task Tracking**: Integrate with IDE task management
- **Status Updates**: Real-time status in development environment

## Monitoring and Metrics

### 1. Story Creation Metrics
- **Creation Rate**: Stories created per day/sprint
- **Estimation Accuracy**: Actual vs estimated effort
- **Completion Rate**: Stories completed vs planned
- **Quality Score**: Artifact completeness and accuracy

### 2. Automation Effectiveness
- **Time Savings**: Manual vs automated story creation time
- **Consistency Score**: Documentation quality and completeness
- **Error Reduction**: Fewer missing artifacts and status issues
- **Team Adoption**: Usage rate across development activities

### 3. Process Improvements
- **Template Refinement**: Continuous improvement of auto-generation
- **Integration Enhancement**: Better tool and workflow integration
- **Quality Enhancement**: Improved validation and verification
- **User Experience**: Streamlined creation and management workflows

## Benefits

### **Development Efficiency**
- **Time Savings**: 80% reduction in story creation time
- **Consistency**: 100% consistent story formatting and documentation
- **Quality**: Built-in quality gates and validation
- **Integration**: Seamless artifact management

### **Project Visibility**
- **Real-time Tracking**: Immediate updates across all artifacts
- **Complete Documentation**: No missing or outdated information
- **Dependency Management**: Automatic dependency tracking and validation
- **Progress Monitoring**: Clear visibility into sprint and epic progress

### **Quality Assurance**
- **Standardization**: Consistent approach across all development work
- **Validation**: Built-in checks for completeness and accuracy
- **Traceability**: Clear audit trail from story creation to completion
- **Integration**: Seamless connection between planning and execution

## Enforcement

This rule is **ALWAYS APPLIED** and must be followed for all:
- User story creation and management
- Task breakdown and tracking
- Sprint planning and execution
- Progress monitoring and reporting
- Artifact updates and maintenance
- Development workflow integration

**Violations of this rule require immediate remediation and adoption of the automated agile system.**

## Implementation Checklist

### **For New Work**
- [ ] Create story using automated system before starting work
- [ ] Verify all artifacts updated automatically
- [ ] Mark story in progress when beginning work
- [ ] Track task completion throughout development
- [ ] Validate story completion with all criteria met

### **For Existing Work**
- [ ] Retroactively create stories for ongoing work
- [ ] Update all artifacts to current state
- [ ] Integrate existing progress with automation system
- [ ] Document any manual work in automated stories
- [ ] Transition to automated workflow for future updates

### **For Team Adoption**
- [ ] Train team on automation system usage
- [ ] Establish automation-first development culture
- [ ] Monitor adoption and effectiveness metrics
- [ ] Continuously improve automation based on feedback
- [ ] Enforce automation requirements in code reviews

---

**Remember**: "Manual story management is technical debt. Automation ensures quality, consistency, and complete project visibility."

**This rule ensures every piece of development work is properly planned, tracked, and integrated into the project's agile management system.**
