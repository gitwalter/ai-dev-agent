# Agile Cursor Rules for AI-Dev-Agent System

## 🎯 **Agile Development Principles**

These Cursor rules are specifically designed to enforce agile principles, automate agile processes, and ensure the system operates with maximum agility and efficiency.

---

## 🚀 **TIER 1: CRITICAL AGILE RULES (Always Apply)**

### **Rule 1: Sprint-Focused Development**
**CRITICAL**: All development must align with current sprint goals and deliver working software incrementally.

#### **Core Requirements**
- **Sprint Goal Alignment**: Every task must contribute to the current sprint goal
- **Working Software Priority**: Focus on deliverable, functional increments over comprehensive documentation
- **User Story Completion**: Complete entire user stories, not just technical tasks
- **Sprint Boundary Respect**: No scope creep within sprint boundaries

#### **Implementation Guidelines**
```python
# CORRECT: Sprint-focused development
def implement_user_story(story_id: str, sprint_goal: str):
    """Implement complete user story aligned with sprint goal."""
    # 1. Validate story aligns with sprint goal
    # 2. Implement minimum viable functionality
    # 3. Ensure story meets definition of done
    # 4. Deliver working software increment
    pass

# INCORRECT: Task-focused development ignoring sprint goals
def implement_technical_task(task_id: str):
    """Implement isolated technical task."""
    # This violates sprint-focused development
    pass
```

#### **Agile Automation**
- Automatic sprint goal validation for all tasks
- Working software validation before task completion
- Sprint boundary enforcement through automated checks
- User story completion tracking and validation

---

### **Rule 2: Continuous Integration & Delivery**
**CRITICAL**: All code must be continuously integrated with automated testing and deployment pipelines.

#### **Core Requirements**
- **Immediate Integration**: Code integrates within minutes of commit
- **Automated Testing**: 100% automated testing with no manual intervention
- **Deployment Readiness**: Every commit is potentially deployable
- **Rapid Feedback**: Feedback loops under 10 minutes

#### **Implementation Guidelines**
```python
# CORRECT: CI/CD-ready development
def develop_feature(feature_spec: dict):
    """Develop feature with full CI/CD integration."""
    # 1. Write tests first (TDD)
    # 2. Implement minimal code to pass tests
    # 3. Automated integration testing
    # 4. Automated deployment validation
    pass

# INCORRECT: Manual integration development
def develop_feature_manual(feature_spec: dict):
    """Develop feature requiring manual testing."""
    # This violates continuous integration principles
    pass
```

#### **Automation Requirements**
- Automatic test execution on every commit
- Automated deployment pipeline with rollback capability
- Automated quality gates and validation
- Continuous monitoring and alerting

---

### **Rule 3: Customer Collaboration & Feedback**
**CRITICAL**: Prioritize customer collaboration, feedback integration, and user value delivery.

#### **Core Requirements**
- **User Story Driven**: All development based on user stories with clear acceptance criteria
- **Stakeholder Feedback**: Regular stakeholder demos and feedback collection
- **Value Delivery**: Measure and optimize for user value, not technical metrics
- **Adaptive Planning**: Adjust plans based on feedback and changing requirements

#### **Implementation Guidelines**
```python
# CORRECT: Customer-centric development
def implement_user_story(story: UserStory):
    """Implement user story with customer value focus."""
    # 1. Validate user value and acceptance criteria
    # 2. Implement user-facing functionality first
    # 3. Collect stakeholder feedback early
    # 4. Adapt based on feedback
    pass

# INCORRECT: Technology-centric development
def implement_technical_feature(tech_spec: dict):
    """Implement technology feature without user context."""
    # This violates customer collaboration principles
    pass
```

#### **Collaboration Automation**
- Automated stakeholder demo generation
- Feedback collection and integration pipelines
- User value metrics tracking and optimization
- Adaptive planning based on feedback analysis

---

## 🏃 **TIER 2: HIGH-PRIORITY AGILE RULES**

### **Rule 4: Test-Driven Development (TDD)**
**HIGH**: Use TDD cycles (Red-Green-Refactor) for all development with automated test validation.

#### **Core Requirements**
- **Red Phase**: Write failing tests first for all new functionality
- **Green Phase**: Implement minimal code to pass tests
- **Refactor Phase**: Improve code quality while maintaining test coverage
- **Automated Validation**: Automated enforcement of TDD cycles

#### **Implementation Guidelines**
```python
# CORRECT: TDD implementation
def implement_tdd_cycle(requirement: str):
    """Implement requirement using TDD cycle."""
    # RED: Write failing test
    test = create_failing_test(requirement)
    assert test.run() == False
    
    # GREEN: Implement minimal code
    code = implement_minimal_solution(requirement)
    assert test.run() == True
    
    # REFACTOR: Improve code quality
    refactored_code = refactor_for_quality(code)
    assert test.run() == True
    return refactored_code

# INCORRECT: Code-first development
def implement_code_first(requirement: str):
    """Implement code without tests first."""
    # This violates TDD principles
    pass
```

#### **TDD Automation**
- Automatic TDD cycle enforcement
- Test-first validation for all commits
- Automated refactoring suggestions and validation
- TDD metrics tracking and optimization

---

### **Rule 5: Retrospective-Driven Improvement**
**HIGH**: Continuously improve processes through automated retrospectives and action implementation.

#### **Core Requirements**
- **Data-Driven Retrospectives**: Use metrics and data for improvement identification
- **Action Implementation**: Automatically implement improvement actions
- **Process Optimization**: Continuously optimize development processes
- **Learning Culture**: Learn from both successes and failures

#### **Implementation Guidelines**
```python
# CORRECT: Retrospective-driven improvement
def conduct_automated_retrospective(sprint_data: dict):
    """Conduct automated retrospective with action implementation."""
    # 1. Analyze sprint metrics and feedback
    # 2. Identify improvement opportunities
    # 3. Generate improvement actions
    # 4. Automatically implement actions
    # 5. Track improvement effectiveness
    pass

# INCORRECT: Manual retrospective without follow-up
def manual_retrospective(feedback: list):
    """Manual retrospective without automated improvement."""
    # This violates continuous improvement principles
    pass
```

#### **Improvement Automation**
- Automated retrospective data collection
- AI-powered improvement opportunity identification
- Automatic implementation of process improvements
- Effectiveness tracking and optimization

---

### **Rule 6: Minimal Viable Product (MVP) Focus**
**HIGH**: Deliver minimal viable functionality that provides user value, then iterate based on feedback.

#### **Core Requirements**
- **Essential Features Only**: Implement only features essential for user value
- **Rapid Delivery**: Deliver working software in days, not weeks
- **Feedback-Driven Iteration**: Use feedback to guide next iterations
- **Value Optimization**: Optimize for user value, not feature completeness

#### **Implementation Guidelines**
```python
# CORRECT: MVP-focused development
def build_mvp(user_need: str, constraints: dict):
    """Build minimal viable product for user need."""
    # 1. Identify core value proposition
    # 2. Implement minimal essential features
    # 3. Deliver working software quickly
    # 4. Collect user feedback
    # 5. Iterate based on feedback
    pass

# INCORRECT: Feature-complete development
def build_complete_product(all_features: list):
    """Build product with all possible features."""
    # This violates MVP principles
    pass
```

#### **MVP Automation**
- Automatic feature prioritization based on user value
- Rapid delivery pipeline optimization
- Feedback collection and analysis automation
- Value-driven iteration planning

---

## 🔄 **TIER 3: OPERATIONAL AGILE RULES**

### **Rule 7: Daily Standup Automation**
**MEDIUM**: Automate daily progress tracking, blocker identification, and next-day planning.

#### **Core Requirements**
- **Daily Progress Collection**: Automatically collect progress from all agents
- **Blocker Identification**: Automatically identify and escalate blockers
- **Next-Day Planning**: Automatically plan next day's work based on progress
- **Team Synchronization**: Ensure all team members are synchronized

#### **Implementation Guidelines**
```python
# CORRECT: Automated daily standup
def conduct_daily_standup():
    """Conduct automated daily standup."""
    # 1. Collect progress from all agents
    # 2. Identify blockers and impediments
    # 3. Update sprint progress and burndown
    # 4. Plan next day's work
    # 5. Communicate updates to stakeholders
    pass
```

#### **Standup Automation**
- Automated progress collection from all agents
- AI-powered blocker identification and resolution
- Automatic next-day planning and task assignment
- Real-time team synchronization and communication

---

### **Rule 8: Definition of Done Enforcement**
**MEDIUM**: Automatically enforce definition of done criteria for all work items.

#### **Core Requirements**
- **Quality Gates**: Automated quality gates for all deliverables
- **Acceptance Criteria**: Automatic validation of acceptance criteria
- **Documentation Standards**: Automated documentation validation
- **Release Readiness**: Automatic release readiness validation

#### **Implementation Guidelines**
```python
# CORRECT: Definition of done enforcement
def validate_definition_of_done(work_item: WorkItem):
    """Validate work item meets definition of done."""
    # 1. Check all acceptance criteria are met
    # 2. Validate code quality standards
    # 3. Ensure test coverage requirements
    # 4. Validate documentation completeness
    # 5. Confirm release readiness
    return all_criteria_met

# INCORRECT: Manual definition of done checking
def manual_done_check(work_item: WorkItem):
    """Manual checking of done criteria."""
    # This violates automated quality assurance
    pass
```

#### **Done Automation**
- Automated acceptance criteria validation
- Quality gate enforcement for all deliverables
- Documentation completeness validation
- Release readiness automation

---

## 📊 **AGILE METRICS & AUTOMATION**

### **Automated Metrics Collection**
```python
class AgileMetrics:
    def __init__(self):
        self.velocity_tracker = VelocityTracker()
        self.burndown_generator = BurndownGenerator()
        self.quality_monitor = QualityMonitor()
        self.feedback_analyzer = FeedbackAnalyzer()
    
    def collect_sprint_metrics(self, sprint_id: str):
        """Automatically collect comprehensive sprint metrics."""
        return {
            "velocity": self.velocity_tracker.get_velocity(sprint_id),
            "burndown": self.burndown_generator.generate_burndown(sprint_id),
            "quality": self.quality_monitor.get_quality_metrics(sprint_id),
            "feedback": self.feedback_analyzer.analyze_feedback(sprint_id)
        }
```

### **Key Agile Metrics**
- **Velocity**: Story points completed per sprint (Target: 40-60 SP)
- **Burndown**: Daily progress toward sprint goal (Target: Linear burndown)
- **Cycle Time**: Time from story start to completion (Target: <3 days)
- **Quality**: Defect rate and test coverage (Target: <5% defects, >90% coverage)
- **Satisfaction**: Stakeholder and team satisfaction (Target: >8/10)

---

## 🤖 **AGILE AUTOMATION FRAMEWORK**

### **Sprint Automation Engine**
```python
class SprintAutomationEngine:
    def __init__(self):
        self.sprint_planner = AutomatedSprintPlanner()
        self.daily_coordinator = DailyStandupCoordinator()
        self.review_generator = SprintReviewGenerator()
        self.retrospective_analyzer = RetrospectiveAnalyzer()
    
    async def automate_sprint_cycle(self, sprint_config: dict):
        """Fully automate sprint cycle from planning to retrospective."""
        # Sprint Planning
        sprint_plan = await self.sprint_planner.plan_sprint(sprint_config)
        
        # Daily Operations
        for day in range(sprint_config["duration_days"]):
            await self.daily_coordinator.conduct_daily_standup()
        
        # Sprint Review
        review_results = await self.review_generator.generate_review()
        
        # Sprint Retrospective
        improvements = await self.retrospective_analyzer.analyze_and_improve()
        
        return {
            "plan": sprint_plan,
            "review": review_results,
            "improvements": improvements
        }
```

### **Agile Quality Gates**
```python
class AgileQualityGates:
    def __init__(self):
        self.story_validator = UserStoryValidator()
        self.code_quality_gate = CodeQualityGate()
        self.test_coverage_gate = TestCoverageGate()
        self.deployment_gate = DeploymentReadinessGate()
    
    def validate_story_ready_for_sprint(self, story: UserStory) -> bool:
        """Validate story meets INVEST criteria and is ready for sprint."""
        return self.story_validator.validate_invest_criteria(story)
    
    def validate_code_ready_for_merge(self, code: str) -> bool:
        """Validate code meets quality standards."""
        return self.code_quality_gate.validate(code)
    
    def validate_ready_for_deployment(self, build: Build) -> bool:
        """Validate build is ready for deployment."""
        return all([
            self.test_coverage_gate.validate(build),
            self.deployment_gate.validate(build)
        ])
```

---

## 🎯 **AGILE RULE ENFORCEMENT**

### **Automatic Rule Validation**
- All rules are automatically validated through CI/CD pipeline
- Rule violations block commits and deployments
- Automated feedback and coaching for rule compliance
- Continuous rule effectiveness monitoring and optimization

### **Rule Compliance Metrics**
- **Sprint Goal Alignment**: 95%+ of tasks align with sprint goals
- **TDD Compliance**: 100% of code follows TDD cycles
- **CI/CD Automation**: 100% automated testing and deployment
- **Definition of Done**: 95%+ compliance with quality criteria

### **Rule Evolution**
- Rules are continuously improved based on retrospective feedback
- New rules added based on process improvement opportunities
- Deprecated rules removed when no longer relevant
- Rule effectiveness measured and optimized

---

## 📋 **AGILE RULE CHECKLIST**

### **Before Starting Development**
- [ ] Current sprint goal clearly defined and understood
- [ ] User stories meet INVEST criteria
- [ ] Acceptance criteria are clear and testable
- [ ] Definition of done is understood and achievable
- [ ] TDD approach planned for implementation

### **During Development**
- [ ] Following TDD cycles (Red-Green-Refactor)
- [ ] Code integrates continuously with automated testing
- [ ] Progress tracked and blockers identified daily
- [ ] Stakeholder feedback sought early and often
- [ ] MVP approach maintained with minimal viable features

### **Before Completion**
- [ ] All acceptance criteria met and validated
- [ ] Definition of done criteria satisfied
- [ ] Code quality gates passed
- [ ] Deployment readiness confirmed
- [ ] User value delivered and validated

### **After Sprint**
- [ ] Sprint retrospective conducted with improvement actions
- [ ] Process improvements implemented automatically
- [ ] Lessons learned captured and shared
- [ ] Next sprint planning informed by current sprint results

---

**Last Updated**: Current Session  
**Rule Owner**: Agile Development Team  
**Next Review**: End of Sprint 1  
**Compliance Target**: 95%+ across all rules