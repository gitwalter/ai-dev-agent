# Automatic User Story Creation Rule

**CRITICAL**: Automatically detect when development work requires a user story and create it immediately with zero manual intervention. This rule integrates with our context-aware rule system to ensure all significant work is properly tracked.

## Description

This rule automatically triggers user story creation based on work complexity, context, and impact analysis. It prevents the common problem of doing substantial development work without proper agile tracking by proactively creating stories when needed.

## Core Requirements

### 1. **Automatic Detection Triggers**
**MANDATORY**: These conditions automatically trigger user story creation

```yaml
user_story_triggers:
  complexity_based:
    threshold: 5  # Work complexity score 1-10
    reasoning: "Complex work needs tracking and breakdown"
    
  context_based:
    coding_with_features: "New functionality or significant changes"
    architecture_work: "System design and major refactoring"
    integration_work: "Connecting systems or external services"
    ui_changes: "User interface modifications or improvements"
    
  impact_based:
    multi_file_changes: "Changes affecting multiple files/modules"
    user_facing_changes: "Changes visible to end users"
    breaking_changes: "Changes that might break existing functionality"
    infrastructure_changes: "Changes to build, deploy, or infrastructure"
    
  keyword_triggers:
    feature_keywords: ["implement", "create", "build", "add feature", "new functionality"]
    significant_keywords: ["refactor", "restructure", "overhaul", "major fix"]
    integration_keywords: ["integrate", "connect", "api", "service", "external"]
    ui_keywords: ["dashboard", "interface", "visualization", "user experience"]
```

### 2. **Work Complexity Assessment**
**MANDATORY**: Automatic complexity analysis to determine story requirement

```python
def assess_work_complexity(user_request: str, context: str, files_involved: List[str]) -> int:
    """
    Assess work complexity on a scale of 1-10.
    
    Args:
        user_request: User's development request
        context: Detected development context
        files_involved: List of files that might be affected
        
    Returns:
        Complexity score 1-10 (5+ triggers automatic story creation)
    """
    complexity_score = 0
    
    # Base complexity from request content
    complexity_indicators = {
        "implement": 3,
        "create": 2,
        "build": 4,
        "refactor": 5,
        "restructure": 6,
        "overhaul": 7,
        "integrate": 4,
        "connect": 3,
        "fix major": 4,
        "add feature": 5,
        "new functionality": 6
    }
    
    request_lower = user_request.lower()
    for indicator, score in complexity_indicators.items():
        if indicator in request_lower:
            complexity_score = max(complexity_score, score)
    
    # Adjust based on files involved
    if len(files_involved) > 3:
        complexity_score += 2
    elif len(files_involved) > 1:
        complexity_score += 1
    
    # Adjust based on context
    context_multipliers = {
        "ARCHITECTURE": 1.5,
        "CODING": 1.2,
        "INTEGRATION": 1.3,
        "DEBUGGING": 0.8,
        "TESTING": 0.9
    }
    
    multiplier = context_multipliers.get(context, 1.0)
    final_score = min(int(complexity_score * multiplier), 10)
    
    return final_score
```

### 3. **Automatic Story Creation Process**
**MANDATORY**: Seamless story creation with full automation

```python
def auto_create_user_story(user_request: str, 
                          complexity: int,
                          context: str,
                          story_type: str) -> UserStory:
    """
    Automatically create a complete user story from development request.
    
    Args:
        user_request: Original development request
        complexity: Assessed complexity score
        context: Development context
        story_type: Type of story (feature, technical, bug)
        
    Returns:
        Complete UserStory object with all fields populated
    """
    
    # Generate story components
    story_components = extract_story_components(user_request, context)
    
    # Create story object
    story = UserStory(
        title=story_components["title"],
        user_type=story_components["user_type"],
        goal=story_components["goal"],
        benefit=story_components["benefit"]
    )
    
    # Auto-estimate story points based on complexity
    story_points = complexity_to_story_points(complexity)
    story.estimate_story_points(story_points, "auto-generated")
    
    # Generate acceptance criteria
    acceptance_criteria = generate_acceptance_criteria(user_request, story_type)
    for criterion in acceptance_criteria:
        test_scenario = generate_test_scenario(criterion)
        story.add_acceptance_criterion(criterion, test_scenario)
    
    # Set story metadata
    story.priority = determine_priority(complexity, story_type)
    story.epic = determine_epic(context, story_type)
    story.sprint = assign_to_sprint(story_points)
    story.status = "ready"
    story.created_date = datetime.now()
    story.created_by = "automatic_system"
    
    # Create story documentation
    create_story_documentation(story)
    
    # Update all agile artifacts
    update_agile_artifacts_with_new_story(story)
    
    return story

def extract_story_components(user_request: str, context: str) -> Dict[str, str]:
    """Extract user story components from development request."""
    
    # Determine user type based on context
    user_type_mapping = {
        "CODING": "developer",
        "ARCHITECTURE": "system architect", 
        "DEBUGGING": "developer",
        "TESTING": "QA engineer",
        "AGILE": "product owner",
        "DOCUMENTATION": "team member"
    }
    
    user_type = user_type_mapping.get(context, "user")
    
    # Extract goal from request
    goal = extract_goal_from_request(user_request)
    
    # Generate benefit statement
    benefit = generate_benefit_statement(goal, context)
    
    # Generate title
    title = generate_story_title(goal, context)
    
    return {
        "title": title,
        "user_type": user_type,
        "goal": goal,
        "benefit": benefit
    }

def complexity_to_story_points(complexity: int) -> int:
    """Convert complexity score to Fibonacci story points."""
    complexity_to_points = {
        1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 
        6: 5, 7: 8, 8: 8, 9: 13, 10: 13
    }
    return complexity_to_points.get(complexity, 5)
```

### 4. **Integration with Context-Aware Rule System**
**MANDATORY**: Seamless integration with existing rule system

```python
def enhanced_context_detection_with_stories(user_message, open_files, current_directory):
    """
    Enhanced context detection that includes user story automation.
    """
    
    # Step 1: Standard context detection
    context_result = detect_context(user_message, open_files, current_directory)
    
    # Step 2: Assess if user story is needed
    complexity = assess_work_complexity(user_message, context_result.context, open_files)
    story_needed = should_create_user_story(user_message, context_result.context, complexity)
    
    # Step 3: Auto-create story if needed
    story = None
    if story_needed:
        story_type = determine_story_type(user_message, context_result.context)
        story = auto_create_user_story(user_message, complexity, context_result.context, story_type)
        
        print(f"📋 **Auto-Created User Story**: {story.id}")
        print(f"🎯 **Title**: {story.title}")
        print(f"⚡ **Story Points**: {story.story_points}")
        print(f"🔄 **Status**: {story.status}")
        print(f"📅 **Sprint**: {story.sprint}")
    
    # Step 4: Enhanced rule application with story context
    rule_result = apply_context_aware_rules(context_result)
    
    # Step 5: Add story tracking to active session
    if story:
        rule_result.active_story = story
        rule_result.track_story_progress = True
    
    return rule_result

def should_create_user_story(user_message: str, context: str, complexity: int) -> bool:
    """Determine if user story creation is required."""
    
    # Rule 1: Complexity threshold
    if complexity >= 5:
        return True
    
    # Rule 2: Context-specific triggers
    story_required_contexts = ["CODING", "ARCHITECTURE", "AGILE"]
    if context in story_required_contexts:
        # Check for specific trigger words
        trigger_words = [
            "implement", "create", "build", "add feature", "new functionality",
            "refactor", "restructure", "overhaul", "integrate", "connect"
        ]
        if any(word in user_message.lower() for word in trigger_words):
            return True
    
    # Rule 3: Multi-file or user-facing changes
    if detect_multi_file_impact(user_message) or detect_user_facing_changes(user_message):
        return True
    
    return False
```

### 5. **Story Progress Tracking Integration**
**MANDATORY**: Automatic progress tracking for created stories

```python
def track_story_progress_automatically(story: UserStory, session_context: dict):
    """
    Automatically track story progress during development session.
    """
    
    # Monitor code changes
    code_changes = monitor_code_changes(story.id)
    
    # Monitor test execution
    test_results = monitor_test_results(story.id)
    
    # Monitor documentation updates
    doc_updates = monitor_documentation_updates(story.id)
    
    # Update story progress
    progress_percentage = calculate_story_progress(code_changes, test_results, doc_updates)
    story.progress_percentage = progress_percentage
    
    # Update story status based on progress
    if progress_percentage == 100 and all_acceptance_criteria_met(story):
        story.status = "completed"
        story.completion_date = datetime.now()
        mark_story_completed(story)
    elif progress_percentage > 0:
        story.status = "in_progress"
    
    # Update agile artifacts
    update_story_progress_in_artifacts(story)
```

### 6. **Artifact Auto-Update System**
**MANDATORY**: All agile artifacts automatically updated with new stories

```python
def update_agile_artifacts_with_new_story(story: UserStory):
    """Update all agile artifacts when new story is created."""
    
    artifacts_to_update = [
        "docs/agile/catalogs/USER_STORY_CATALOG.md",
        "docs/agile/sprints/sprint_2/backlog.md", 
        "docs/agile/sprints/sprint_2/progress.md",
        "docs/agile/daily_standup.md",
        "docs/agile/velocity_tracking_current.md"
    ]
    
    for artifact_path in artifacts_to_update:
        update_artifact_with_story(artifact_path, story)
    
    # Create individual story file
    create_story_file(story)
    
    # Update epic overview
    update_epic_overview_with_story(story)
    
    print(f"✅ Updated {len(artifacts_to_update)} agile artifacts with new story")
```

## Implementation Guidelines

### 1. **Trigger Configuration**
```yaml
automation_config:
  complexity_threshold: 5
  contexts_requiring_stories: ["CODING", "ARCHITECTURE", "AGILE"]
  auto_update_artifacts: true
  notify_story_creation: true
  track_progress_automatically: true
```

### 2. **Quality Assurance**
```yaml
quality_checks:
  story_validation:
    - "INVEST criteria automatically validated"
    - "Acceptance criteria generated and reviewed"
    - "Story points estimated using proven algorithms"
    - "Story assigned to appropriate sprint"
  
  artifact_consistency:
    - "All agile artifacts updated simultaneously" 
    - "No orphaned or inconsistent story references"
    - "Catalog automatically synchronized"
    - "Progress tracking activated immediately"
```

### 3. **User Feedback Integration**
```yaml
feedback_system:
  story_creation_notification:
    message: "📋 Auto-created User Story: {story_id} - {title}"
    details: "Story Points: {points}, Sprint: {sprint}, Type: {type}"
    
  manual_override:
    enabled: true
    user_can_modify: "All story attributes after creation"
    user_can_cancel: "Story creation within 5 minutes"
    
  learning_system:
    track_accuracy: "Monitor if auto-created stories were appropriate"
    improve_triggers: "Learn from user feedback to improve detection"
```

## Benefits

### **Immediate Benefits**
- **Zero Missed Stories**: All significant work automatically tracked
- **Consistent Agile Practice**: Enforces proper story management
- **Real-Time Visibility**: Immediate project status updates
- **Reduced Manual Work**: No manual story creation needed

### **Long-Term Benefits**
- **Perfect Traceability**: Every change linked to business value
- **Accurate Velocity**: Proper story tracking improves velocity calculations
- **Better Planning**: Historical data improves future estimation
- **Stakeholder Confidence**: Always current project status

### **Integration Benefits**
- **Seamless Workflow**: No interruption to development flow
- **Context Awareness**: Stories created with proper context
- **Rule System Synergy**: Leverages existing intelligent rule system
- **Future-Proof**: Ready for agent swarm coordination

## Enforcement

This rule is **CONDITIONALLY APPLIED** based on context and work complexity.

**The system automatically creates user stories when detection criteria are met.**

## Configuration

```yaml
# Enable automatic user story creation
automatic_user_story_creation:
  enabled: true
  complexity_threshold: 5
  contexts: ["CODING", "ARCHITECTURE", "AGILE"]
  notification: true
  artifact_updates: true
  progress_tracking: true
```

## Remember

**"If work is worth doing, it's worth tracking."**

**"Automatic detection prevents manual oversight."**

**"Stories created automatically are stories created correctly."**

**"Context-aware automation serves developers, not bureaucracy."**

This rule ensures that our agile practice becomes truly automatic, preventing the common problem of untracked development work while maintaining development velocity and focus.
