# Agile Meeting Rules for AI-Dev-Agent System

**CRITICAL**: These rules ensure all agile meetings are conducted efficiently, effectively, and consistently to maximize team velocity and deliver value.

## 🎯 **Universal Meeting Principles**

### **Core Meeting Requirements**
**MANDATORY**: All agile meetings must follow these fundamental principles:

1. **Time-Boxed**: All meetings have strict time limits and must end on time
2. **Purpose-Driven**: Every meeting has clear objectives and desired outcomes
3. **Prepared**: All participants come prepared with necessary information
4. **Facilitated**: Every meeting has a designated facilitator
5. **Documented**: All decisions and action items are recorded and shared
6. **Action-Oriented**: Every meeting produces concrete action items
7. **Value-Focused**: All meetings focus on delivering user and business value

### **Meeting Quality Standards**
```python
# REQUIRED: Meeting effectiveness validation
def validate_meeting_effectiveness(meeting_data: dict) -> bool:
    """Validate that meeting meets agile standards."""
    required_criteria = [
        meeting_data.get("duration_minutes") <= meeting_data.get("timebox_minutes"),
        len(meeting_data.get("action_items", [])) > 0,
        meeting_data.get("facilitator") is not None,
        meeting_data.get("objectives_met", 0) >= 80,  # 80% objectives met
        meeting_data.get("participant_engagement", 0) >= 7  # 7/10 engagement
    ]
    return all(required_criteria)
```

---

## 📅 **1. DAILY STANDUP RULES**

### **Meeting Configuration**
- **Duration**: 15 minutes (STRICT)
- **Frequency**: Every working day
- **Time**: Same time daily (recommend 9:00 AM)
- **Facilitator**: Rotating team member or Scrum Master
- **Participants**: All sprint team members

### **Meeting Rules**
**MANDATORY**: Every daily standup must follow these rules:

1. **Three Questions Format**:
   - What did I complete yesterday?
   - What will I work on today?
   - What blockers or impediments do I have?

2. **Sprint Goal Focus**:
   - All updates must relate to sprint goal
   - Identify how today's work advances sprint goal
   - Flag any work not aligned with sprint goal

3. **No Problem Solving**:
   - Identify problems, don't solve them in standup
   - Schedule separate meetings for detailed discussions
   - Park detailed technical discussions

4. **Visual Management**:
   - Update sprint board during standup
   - Show burndown chart progress
   - Highlight blocked items visually

### **Pre-Meeting Automation**
```python
# REQUIRED: Automated standup preparation
def prepare_daily_standup():
    """Automate standup preparation."""
    preparation_data = {
        "burndown_update": update_burndown_chart(),
        "board_sync": synchronize_sprint_board(),
        "blocker_analysis": identify_potential_blockers(),
        "velocity_tracking": calculate_current_velocity(),
        "goal_progress": assess_sprint_goal_progress()
    }
    return preparation_data
```

### **Success Criteria**
- [ ] Meeting completed within 15 minutes
- [ ] All team members provide updates
- [ ] Sprint goal progress assessed
- [ ] Blockers identified and escalated
- [ ] Next day's work clarity achieved
- [ ] Team synchronization maintained

### **Post-Meeting Actions**
```python
# REQUIRED: Post-standup automation
def post_standup_actions(standup_data: dict):
    """Automate post-standup follow-up."""
    actions = [
        escalate_blockers(standup_data["blockers"]),
        update_stakeholder_dashboard(standup_data["progress"]),
        schedule_problem_solving_sessions(standup_data["parking_lot"]),
        send_daily_summary(standup_data["summary"]),
        update_velocity_projections(standup_data["velocity"])
    ]
    return execute_actions(actions)
```

---

## 🎯 **2. SPRINT PLANNING RULES**

### **Meeting Configuration**
- **Duration**: 4 hours (2-week sprint) / 2 hours (1-week sprint)
- **Frequency**: Start of every sprint
- **Facilitator**: Scrum Master or designated facilitator
- **Participants**: Entire scrum team + Product Owner

### **Two-Part Structure**
**MANDATORY**: Sprint planning must have two distinct parts:

#### **Part 1: What (2 hours)**
- Product Owner presents sprint goal
- Team examines product backlog
- Team commits to stories for sprint
- Sprint goal finalized and agreed

#### **Part 2: How (2 hours)**  
- Team breaks down stories into tasks
- Estimate tasks and validate capacity
- Identify dependencies and risks
- Create sprint backlog

### **Pre-Planning Requirements**
**MANDATORY**: Before sprint planning meeting:
```python
# REQUIRED: Pre-planning validation
def validate_planning_readiness():
    """Validate readiness for sprint planning."""
    readiness_checks = {
        "backlog_groomed": validate_story_readiness(),
        "team_capacity_known": calculate_team_capacity(),
        "velocity_analyzed": analyze_historical_velocity(),
        "dependencies_mapped": identify_dependencies(),
        "definition_of_done_current": validate_dod_currency()
    }
    
    if not all(readiness_checks.values()):
        raise PlanningNotReadyException(f"Missing: {readiness_checks}")
    
    return readiness_checks
```

### **Sprint Goal Rules**
**MANDATORY**: Sprint goal must be:
- **Specific**: Clear and measurable objective
- **Achievable**: Realistic given team capacity
- **Valuable**: Delivers business or user value
- **Testable**: Success can be objectively measured
- **Singular**: One primary goal, not multiple goals

### **Story Commitment Rules**
**MANDATORY**: Story commitment must follow:
```python
# REQUIRED: Story commitment validation
def validate_story_commitment(stories: list, team_capacity: dict):
    """Validate story commitment against capacity."""
    validation_rules = [
        sum(story.points for story in stories) <= team_capacity["velocity"],
        all(story.meets_definition_of_ready() for story in stories),
        all(story.supports_sprint_goal() for story in stories),
        len([s for s in stories if s.priority == "HIGH"]) >= 1,
        story_dependencies_resolved(stories)
    ]
    return all(validation_rules)
```

### **Success Criteria**
- [ ] Sprint goal defined and agreed by all
- [ ] Stories committed based on team capacity
- [ ] All committed stories meet Definition of Ready
- [ ] Dependencies identified and mitigated
- [ ] Team confident in sprint success (8/10)
- [ ] Sprint backlog complete and detailed

---

## 🔍 **3. SPRINT REVIEW RULES**

### **Meeting Configuration**
- **Duration**: 1 hour (1-week sprint) / 2 hours (2-week sprint)
- **Frequency**: End of every sprint
- **Facilitator**: Product Owner or Scrum Master
- **Participants**: Scrum team + stakeholders + customers

### **Demo-Focused Structure**
**MANDATORY**: Sprint review must focus on demonstrations:

#### **Opening (10 minutes)**
- Sprint goal reminder
- Sprint summary overview
- Agenda and objectives

#### **Demonstrations (60-80%)**
- Live demo of completed stories
- Stakeholder interaction and feedback
- Business value showcase

#### **Metrics Review (10 minutes)**
- Velocity and burndown review
- Quality metrics presentation
- Performance indicators

#### **Next Sprint Preview (10 minutes)**
- Upcoming sprint goals
- Product backlog updates
- Stakeholder input collection

### **Demo Standards**
**MANDATORY**: Every demo must follow:
```python
# REQUIRED: Demo quality standards
def validate_demo_quality(demo_data: dict):
    """Validate demo meets quality standards."""
    demo_standards = [
        demo_data["shows_working_software"] == True,
        demo_data["demonstrates_user_value"] == True,
        demo_data["includes_acceptance_criteria"] == True,
        demo_data["duration_minutes"] <= demo_data["allocated_minutes"],
        demo_data["stakeholder_feedback_collected"] == True,
        demo_data["business_value_explained"] == True
    ]
    return all(demo_standards)
```

### **Feedback Collection Rules**
**MANDATORY**: Stakeholder feedback must be:
- **Recorded**: All feedback documented
- **Categorized**: Bugs, enhancements, new features
- **Prioritized**: Impact and effort assessed
- **Actionable**: Converted to backlog items
- **Acknowledged**: Feedback response provided

### **Success Criteria**
- [ ] All completed stories demonstrated
- [ ] Stakeholder feedback collected and recorded
- [ ] Business value clearly communicated
- [ ] Product backlog updated based on feedback
- [ ] Velocity and quality metrics shared
- [ ] Next sprint direction aligned

---

## 🔄 **4. SPRINT RETROSPECTIVE RULES**

### **Meeting Configuration**
- **Duration**: 1.5 hours (2-week sprint) / 45 minutes (1-week sprint)
- **Frequency**: End of every sprint (after review)
- **Facilitator**: Scrum Master
- **Participants**: Scrum team only (no stakeholders)

### **Safe Environment Rules**
**MANDATORY**: Retrospective must maintain:
- **Psychological Safety**: Open, honest discussion
- **Focus on Process**: Improve systems, not blame people
- **Confidentiality**: What's discussed stays in the room
- **Action-Oriented**: Generate concrete improvements
- **Data-Driven**: Use metrics and evidence

### **Structured Format**
**MANDATORY**: Use proven retrospective formats:

#### **Start-Stop-Continue (Recommended)**
- **Start**: What should we start doing?
- **Stop**: What should we stop doing?
- **Continue**: What should we continue doing?

#### **Alternative Formats**
- **What Went Well/What Could Improve/Action Items**
- **Sailboat (Wind/Anchors/Rocks/Island)**
- **4 Ls (Liked/Learned/Lacked/Longed For)**

### **Improvement Action Rules**
**MANDATORY**: Every retrospective must produce:
```python
# REQUIRED: Action item validation
def validate_retrospective_actions(actions: list):
    """Validate retrospective action items."""
    action_criteria = [
        len(actions) >= 1 and len(actions) <= 3,  # 1-3 actions max
        all(action.has_owner() for action in actions),
        all(action.has_due_date() for action in actions),
        all(action.is_measurable() for action in actions),
        all(action.is_achievable() for action in actions)
    ]
    return all(action_criteria)
```

### **Metrics-Driven Insights**
**MANDATORY**: Use sprint metrics for insights:
- **Velocity trends**: Increasing, stable, or decreasing
- **Quality metrics**: Defect rates, test coverage
- **Cycle time**: Story completion time
- **Team satisfaction**: Morale and engagement scores
- **Process effectiveness**: Meeting efficiency, collaboration

### **Success Criteria**
- [ ] Team reflects honestly on sprint process
- [ ] Process improvements identified
- [ ] 1-3 concrete action items defined
- [ ] Action items have owners and due dates
- [ ] Team commitment to improvement actions
- [ ] Next sprint process adjustments agreed

---

## 📚 **5. BACKLOG REFINEMENT RULES**

### **Meeting Configuration**
- **Duration**: 1 hour per week
- **Frequency**: Weekly (mid-sprint)
- **Facilitator**: Product Owner
- **Participants**: Scrum team + domain experts (as needed)

### **Refinement Activities**
**MANDATORY**: Every refinement session must:

#### **Story Preparation**
- Review upcoming stories (2-3 sprints ahead)
- Add missing acceptance criteria
- Break down large stories (epics)
- Estimate story points
- Identify dependencies

#### **Story Quality Validation**
**MANDATORY**: Stories must meet INVEST criteria:
```python
# REQUIRED: Story quality validation
def validate_story_invest(story: UserStory):
    """Validate story meets INVEST criteria."""
    invest_criteria = {
        "Independent": story.has_minimal_dependencies(),
        "Negotiable": story.allows_implementation_flexibility(),
        "Valuable": story.delivers_user_or_business_value(),
        "Estimable": story.can_be_estimated_reliably(),
        "Small": story.fits_within_single_sprint(),
        "Testable": story.has_clear_acceptance_criteria()
    }
    return all(invest_criteria.values())
```

### **Definition of Ready**
**MANDATORY**: Stories must meet Definition of Ready:
- [ ] Clear user story format ("As a... I want... So that...")
- [ ] Detailed acceptance criteria defined
- [ ] Story points estimated by team
- [ ] Dependencies identified and documented
- [ ] UI/UX mockups available (if applicable)
- [ ] Technical approach discussed
- [ ] Testable and demonstrable

### **Success Criteria**
- [ ] Next 2-3 sprints have ready stories
- [ ] All refined stories meet INVEST criteria
- [ ] Story estimates are team consensus
- [ ] Dependencies identified and tracked
- [ ] Product backlog ordered by priority
- [ ] Team understands upcoming work

---

## 🗓️ **6. RELEASE PLANNING RULES**

### **Meeting Configuration**
- **Duration**: 4-8 hours (quarterly)
- **Frequency**: Every 3 months or major release
- **Facilitator**: Product Owner or Product Manager
- **Participants**: Scrum teams + stakeholders + leadership

### **Release Objectives**
**MANDATORY**: Release planning must define:
- **Release Goal**: Clear business objective
- **Release Scope**: Features and stories included
- **Release Timeline**: Target dates and milestones
- **Success Metrics**: Measurable success criteria
- **Risk Assessment**: Major risks and mitigation

### **Multi-Sprint Planning**
**MANDATORY**: Plan 3-6 sprints ahead:
```python
# REQUIRED: Release planning validation
def validate_release_plan(release_plan: dict):
    """Validate release plan feasibility."""
    validation_criteria = [
        release_plan["total_story_points"] <= release_plan["team_capacity"],
        release_plan["critical_path_identified"] == True,
        release_plan["dependencies_mapped"] == True,
        release_plan["risk_mitigation_planned"] == True,
        len(release_plan["success_metrics"]) >= 3
    ]
    return all(validation_criteria)
```

### **Success Criteria**
- [ ] Release goal clearly defined and agreed
- [ ] Feature roadmap mapped to sprints
- [ ] Team capacity vs. scope validated
- [ ] Dependencies and risks identified
- [ ] Success metrics defined and measurable
- [ ] Stakeholder alignment achieved

---

## 🎯 **7. EPIC PLANNING RULES**

### **Meeting Configuration**
- **Duration**: 2-4 hours (as needed)
- **Frequency**: When new epics are identified
- **Facilitator**: Product Owner or Architect
- **Participants**: Scrum team + subject matter experts

### **Epic Breakdown Process**
**MANDATORY**: Epic planning must include:

#### **Epic Definition**
- **Epic Goal**: Clear business outcome
- **User Personas**: Who benefits from epic
- **Success Criteria**: Measurable success metrics
- **Business Value**: ROI and impact assessment

#### **Story Mapping**
- Break epic into user stories
- Map user journey and workflow
- Identify MVP vs. enhancement features
- Sequence stories by priority and dependency

### **Epic Sizing**
**MANDATORY**: Epic estimation must consider:
```python
# REQUIRED: Epic sizing validation
def validate_epic_sizing(epic: Epic):
    """Validate epic is properly sized and planned."""
    sizing_criteria = [
        epic.total_story_points <= 100,  # Max 100 SP per epic
        epic.estimated_sprints <= 6,    # Max 6 sprints per epic
        len(epic.stories) >= 3,         # Min 3 stories per epic
        epic.has_mvp_identified() == True,
        epic.dependencies_mapped() == True
    ]
    return all(sizing_criteria)
```

### **Success Criteria**
- [ ] Epic goal and value clearly defined
- [ ] Epic broken down into implementable stories
- [ ] Story sequence and priorities established
- [ ] MVP identified and scoped
- [ ] Epic fits within release timeline
- [ ] Technical approach validated

---

## ⚡ **8. EMERGENCY MEETING RULES**

### **Unplanned Meeting Guidelines**
**MANDATORY**: When urgent issues require immediate attention:

#### **Meeting Triggers**
- Production outages or critical bugs
- Sprint goal jeopardy situations
- Blocker escalation needs
- Stakeholder urgent changes
- Team conflict resolution

#### **Emergency Meeting Rules**
```python
# REQUIRED: Emergency meeting validation
def validate_emergency_meeting(issue: dict):
    """Validate if emergency meeting is justified."""
    emergency_criteria = [
        issue["severity"] in ["CRITICAL", "HIGH"],
        issue["impact"] == "SPRINT_GOAL_JEOPARDY" or issue["impact"] == "PRODUCTION",
        issue["cannot_wait_until_next_planned_meeting"] == True,
        issue["resolution_time_critical"] == True
    ]
    return any(emergency_criteria)  # At least one must be true
```

#### **Meeting Structure**
- **Duration**: 30 minutes maximum
- **Focus**: Problem identification and solution
- **Outcome**: Clear action plan with owners
- **Follow-up**: Status update within 24 hours

### **Success Criteria**
- [ ] Issue severity justified emergency meeting
- [ ] Problem clearly identified and scoped
- [ ] Solution approach agreed upon
- [ ] Action items with owners and timelines
- [ ] Sprint impact assessed and communicated
- [ ] Regular meeting schedule maintained

---

## 📊 **MEETING EFFECTIVENESS AUTOMATION**

### **Automated Meeting Management**
```python
# REQUIRED: Meeting automation framework
class AgileMeetingAutomation:
    def __init__(self):
        self.meeting_scheduler = MeetingScheduler()
        self.metrics_collector = MeetingMetricsCollector()
        self.action_tracker = ActionItemTracker()
        self.feedback_analyzer = MeetingFeedbackAnalyzer()
    
    def automate_meeting_lifecycle(self, meeting_type: str):
        """Fully automate meeting preparation and follow-up."""
        # Pre-meeting preparation
        preparation = self.prepare_meeting(meeting_type)
        
        # Meeting execution support
        execution_support = self.support_meeting_execution(meeting_type)
        
        # Post-meeting follow-up
        follow_up = self.execute_post_meeting_actions(meeting_type)
        
        # Effectiveness measurement
        effectiveness = self.measure_meeting_effectiveness(meeting_type)
        
        return {
            "preparation": preparation,
            "execution": execution_support,
            "follow_up": follow_up,
            "effectiveness": effectiveness
        }
    
    def prepare_meeting(self, meeting_type: str):
        """Automate meeting preparation based on type."""
        preparation_templates = {
            "daily_standup": self.prepare_standup(),
            "sprint_planning": self.prepare_sprint_planning(),
            "sprint_review": self.prepare_sprint_review(),
            "retrospective": self.prepare_retrospective(),
            "backlog_refinement": self.prepare_backlog_refinement()
        }
        return preparation_templates.get(meeting_type)
```

### **Meeting Quality Metrics**
**MANDATORY**: Track these effectiveness metrics:

#### **Efficiency Metrics**
- **On-Time Start**: 95%+ meetings start on time
- **Time-Boxing**: 95%+ meetings end within timebox
- **Preparation**: 100% meetings have pre-work completed
- **Attendance**: 95%+ required participants present

#### **Effectiveness Metrics**
- **Objective Achievement**: 90%+ objectives met
- **Action Item Generation**: 100% meetings produce actions
- **Participant Engagement**: 8/10 average engagement score
- **Follow-Through**: 95%+ action items completed on time

#### **Value Metrics**
- **Decision Quality**: 8/10 average decision quality
- **Problem Resolution**: 90%+ problems resolved
- **Innovation Generation**: Ideas and improvements per meeting
- **Team Satisfaction**: 8/10 average meeting satisfaction

### **Continuous Improvement**
```python
# REQUIRED: Meeting improvement automation
def improve_meeting_effectiveness():
    """Continuously improve meeting effectiveness."""
    improvement_actions = [
        analyze_meeting_patterns(),
        identify_improvement_opportunities(),
        implement_process_optimizations(),
        measure_improvement_impact(),
        share_best_practices()
    ]
    return execute_improvement_cycle(improvement_actions)
```

---

## ✅ **MEETING RULE COMPLIANCE CHECKLIST**

### **Pre-Meeting Checklist**
- [ ] Meeting purpose and objectives clearly defined
- [ ] Agenda prepared and shared in advance
- [ ] Required participants confirmed and available
- [ ] Pre-work completed by all participants
- [ ] Meeting materials and tools prepared
- [ ] Facilitator identified and prepared

### **During Meeting Checklist**
- [ ] Meeting starts and ends on time
- [ ] Agenda followed and objectives addressed
- [ ] All participants actively engaged
- [ ] Decisions documented and action items captured
- [ ] Parking lot used for off-topic discussions
- [ ] Meeting stays focused on defined purpose

### **Post-Meeting Checklist**
- [ ] Meeting notes and decisions documented
- [ ] Action items assigned with owners and due dates
- [ ] Next steps and follow-up meetings scheduled
- [ ] Meeting effectiveness measured and recorded
- [ ] Action items tracked and monitored
- [ ] Stakeholder communication completed as needed

---

## 🎯 **RULE ENFORCEMENT AND COMPLIANCE**

### **Automatic Rule Validation**
- All meeting rules automatically validated through meeting management system
- Rule violations flagged and coaching provided
- Meeting effectiveness continuously monitored and optimized
- Best practices shared across teams

### **Compliance Targets**
- **Meeting Efficiency**: 95%+ meetings complete within timebox
- **Action Item Completion**: 90%+ action items completed on time
- **Participant Satisfaction**: 8/10+ average meeting satisfaction
- **Objective Achievement**: 90%+ meeting objectives achieved

### **Rule Evolution**
- Rules continuously improved based on retrospective feedback
- New meeting types added as process evolves
- Deprecated rules removed when no longer relevant
- Rule effectiveness measured and optimized

---

**Last Updated**: Current Session  
**Rule Owner**: Agile Coach / Scrum Master  
**Next Review**: End of Sprint 1  
**Compliance Target**: 95%+ across all meeting rules
