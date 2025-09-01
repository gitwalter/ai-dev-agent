# Agile Rules Index for AI-Dev-Agent System

## 📋 **Complete Agile Rules Organization**

This document serves as the central index for all agile rules and guidelines in the AI-Dev-Agent system, organized by category and priority.

---

## 🎯 **TIER 1: CRITICAL AGILE RULES (Always Apply)**

### **Foundational System Rules**
1. **[Formal Organization Rules](../../rules/core/formal_organization_rules.md)** - **CRITICAL** - Mathematical and philosophical foundation
   - Syntactical Rules (naming, organization, documentation)
   - Semantical Rules (meaning, purpose, consistency)
   - Agent Behavior Rules (validation, compliance, improvement)
   - Mathematical and Philosophical Foundation
2. **[Universal Naming Conventions](../../guides/development/universal_naming_conventions_reference.md)** - **MANDATORY** - Complete artifact naming system
   - ALL artifact type patterns (agile, code, tests, docs, config, data, infrastructure)
   - Fowler/Carnap/Quine philosophical foundation
   - Boy Scout Rule integration for continuous improvement

### **Development Rules**
3. **[Agile Cursor Rules](agile_cursor_rules.md)** - Core development principles
   - Sprint-Focused Development
   - Continuous Integration & Delivery
   - Customer Collaboration & Feedback
   - Test-Driven Development (TDD)
   - Retrospective-Driven Improvement
   - Minimal Viable Product (MVP) Focus

### **Meeting Rules**  
4. **[Agile Meeting Rules](agile_meeting_rules.md)** - Complete meeting governance
   - Daily Standup Rules
   - Sprint Planning Rules
   - Sprint Review Rules
   - Sprint Retrospective Rules
   - Backlog Refinement Rules
   - Release Planning Rules
   - Epic Planning Rules
   - Emergency Meeting Rules

### **Quality Rules**
5. **[Definition of Done](definition_of_done.md)** - Quality standards
6. **[Test Failure Tracking Rule](TEST_FAILURE_TRACKING_RULE.md)** - Test quality enforcement

---

## 🔄 **TIER 2: OPERATIONAL AGILE RULES**

### **Workflow Rules**
1. **[Agile Workflow](agile_workflow.md)** - Sprint cycle automation
2. **[Continuous Integration](../execution/continuous_integration.md)** - CI/CD processes
3. **[Velocity Tracking](../execution/velocity_tracking.md)** - Performance measurement

### **Planning Rules**
1. **[Product Backlog Management](../planning/product_backlog.md)** - Backlog governance
2. **[Epic Breakdown](../planning/epic-breakdown.md)** - Epic planning standards
3. **[User Story Guidelines](../planning/user_stories.md)** - Story creation rules
4. **[Story Estimation](../planning/story_estimation.md)** - Estimation standards

---

## 📊 **TIER 3: MEASUREMENT AND IMPROVEMENT RULES**

### **Metrics Rules**
1. **[Metrics Dashboard](../metrics/metrics_dashboard.md)** - KPI tracking
2. **[Performance Indicators](../metrics/performance_indicators.md)** - Performance rules
3. **[Quality Gates](../metrics/quality_gates.md)** - Quality enforcement

### **Automation Rules**
1. **[Automation Framework](../automation/automation_framework.md)** - Process automation
2. **[Sprint Automation](../templates/sprint_planning/README.md)** - Sprint tooling

---

## 🎯 **RULE APPLICATION MATRIX**

### **By Meeting Type**

| Meeting Type | Primary Rules | Secondary Rules | Automation Level |
|--------------|---------------|-----------------|------------------|
| **Daily Standup** | Meeting Rules § 1 | Cursor Rules § 7 | 90% Automated |
| **Sprint Planning** | Meeting Rules § 2 | Workflow, Backlog Rules | 70% Automated |
| **Sprint Review** | Meeting Rules § 3 | Quality Gates, Metrics | 60% Automated |
| **Retrospective** | Meeting Rules § 4 | Cursor Rules § 5 | 80% Automated |
| **Backlog Refinement** | Meeting Rules § 5 | Story, Epic Rules | 50% Automated |
| **Release Planning** | Meeting Rules § 6 | Epic, Velocity Rules | 40% Automated |

### **By Development Phase**

| Development Phase | Applicable Rules | Enforcement Level | Success Metrics |
|-------------------|------------------|-------------------|-----------------|
| **Planning** | Meeting Rules §2,5,6,7 + Planning Rules | Mandatory | 95% Compliance |
| **Development** | Cursor Rules §1,2,4 + Quality Rules | Mandatory | 100% Compliance |
| **Testing** | Cursor Rules §4 + Quality Rules | Mandatory | 90% Coverage |
| **Review** | Meeting Rules §3 + Quality Gates | Mandatory | 80% Satisfaction |
| **Deployment** | Cursor Rules §2 + CI/CD Rules | Mandatory | 100% Automation |
| **Retrospection** | Meeting Rules §4 + Improvement Rules | Mandatory | 3+ Actions/Sprint |

### **By Team Role**

| Team Role | Primary Rules Focus | Meeting Responsibilities |
|-----------|-------------------|------------------------|
| **Scrum Master** | All Meeting Rules + Cursor Rules §5,7 | Facilitate all agile meetings |
| **Product Owner** | Meeting Rules §2,3,5,6 + Planning Rules | Lead planning and review meetings |
| **Developer** | Cursor Rules §1,2,4,6 + Meeting Rules §1 | Participate in all meetings, lead standups |
| **QA Engineer** | Quality Rules + Cursor Rules §4 | Support review and validation |
| **Architect** | Meeting Rules §6,7 + Cursor Rules §2 | Technical planning guidance |

---

## ⚡ **RULE ACTIVATION TRIGGERS**

### **Automatic Rule Activation**
```python
# REQUIRED: Rule activation automation
class AgileRuleActivation:
    def __init__(self):
        self.rule_engine = AgileRuleEngine()
        self.meeting_scheduler = MeetingScheduler()
        self.compliance_monitor = ComplianceMonitor()
    
    def activate_rules_for_event(self, event_type: str):
        """Automatically activate relevant rules for agile events."""
        activation_map = {
            "sprint_start": [
                "daily_standup_rules",
                "sprint_planning_rules", 
                "development_rules"
            ],
            "sprint_mid": [
                "daily_standup_rules",
                "backlog_refinement_rules",
                "development_rules"
            ],
            "sprint_end": [
                "sprint_review_rules",
                "retrospective_rules",
                "improvement_rules"
            ],
            "release_planning": [
                "release_planning_rules",
                "epic_planning_rules",
                "capacity_planning_rules"
            ]
        }
        return self.rule_engine.activate(activation_map.get(event_type, []))
```

### **Manual Rule Triggers**
- **Meeting Conflicts**: Emergency meeting rules activate
- **Quality Issues**: Enhanced quality rules activate  
- **Velocity Problems**: Performance improvement rules activate
- **Team Changes**: Onboarding and collaboration rules activate

---

## 📈 **RULE EFFECTIVENESS MONITORING**

### **Compliance Metrics**
```python
# REQUIRED: Rule compliance tracking
def track_rule_compliance():
    """Monitor and report rule compliance across all categories."""
    compliance_metrics = {
        "meeting_rules": {
            "daily_standup": calculate_standup_compliance(),
            "sprint_planning": calculate_planning_compliance(), 
            "sprint_review": calculate_review_compliance(),
            "retrospective": calculate_retro_compliance()
        },
        "development_rules": {
            "tdd_compliance": calculate_tdd_compliance(),
            "ci_cd_compliance": calculate_cicd_compliance(),
            "quality_compliance": calculate_quality_compliance()
        },
        "overall_compliance": calculate_overall_compliance()
    }
    return compliance_metrics
```

### **Target Compliance Levels**
- **Meeting Rules**: 95%+ compliance across all meeting types
- **Development Rules**: 100% compliance for critical rules
- **Quality Rules**: 90%+ compliance with continuous improvement
- **Process Rules**: 85%+ compliance with monthly review

### **Improvement Actions**
- **Weekly**: Review compliance metrics and identify issues
- **Sprint End**: Retrospective on rule effectiveness
- **Monthly**: Update rules based on effectiveness data
- **Quarterly**: Major rule review and optimization

---

## 🔄 **RULE EVOLUTION PROCESS**

### **Rule Lifecycle Management**
```python
# REQUIRED: Rule lifecycle automation
class AgileRuleLifecycle:
    def __init__(self):
        self.rule_repository = AgileRuleRepository()
        self.effectiveness_analyzer = RuleEffectivenessAnalyzer()
        self.change_manager = RuleChangeManager()
    
    def manage_rule_evolution(self):
        """Continuously evolve rules based on effectiveness data."""
        evolution_cycle = [
            self.measure_rule_effectiveness(),
            self.identify_improvement_opportunities(),
            self.propose_rule_changes(),
            self.validate_rule_changes(),
            self.implement_rule_updates(),
            self.monitor_change_impact()
        ]
        return self.execute_evolution_cycle(evolution_cycle)
```

### **Rule Change Process**
1. **Identify Need**: Performance data or team feedback indicates improvement opportunity
2. **Propose Change**: Draft new or modified rule with rationale
3. **Team Review**: Team validates proposed change and impact
4. **Pilot Test**: Test rule change in controlled environment
5. **Measure Impact**: Assess effectiveness of rule change
6. **Full Implementation**: Roll out successful rule changes
7. **Documentation Update**: Update all relevant documentation

### **Change Approval Matrix**
| Change Type | Approval Required | Testing Required | Documentation Update |
|-------------|------------------|------------------|-------------------- |
| **Minor Update** | Team Consensus | 1 Sprint Pilot | Rule Doc Update |
| **Major Change** | Stakeholder + Team | 2 Sprint Pilot | Full Doc Review |
| **New Rule** | All Stakeholders | 3 Sprint Pilot | Complete Integration |
| **Rule Removal** | All Stakeholders | Impact Assessment | Archive Documentation |

---

## 📚 **RULE DOCUMENTATION STANDARDS**

### **Documentation Requirements**
Every agile rule must include:
- **Purpose**: Why the rule exists and what problem it solves
- **Scope**: When and where the rule applies
- **Implementation**: How to follow the rule with examples
- **Validation**: How compliance is measured and verified
- **Automation**: What parts can be automated
- **Success Criteria**: Measurable outcomes and targets

### **Template Structure**
```markdown
# Rule Name

## Purpose and Rationale
[Why this rule exists]

## Scope and Applicability  
[When and where rule applies]

## Implementation Guidelines
[How to follow the rule]

## Automation Requirements
[Automated enforcement and support]

## Success Criteria and Metrics
[How to measure compliance and effectiveness]

## Integration with Other Rules
[How this rule relates to other rules]
```

### **Cross-Reference Requirements**
- All rules must reference related rules
- Dependencies clearly documented
- Integration points identified
- Conflict resolution procedures defined

---

## ✅ **RULE ADOPTION CHECKLIST**

### **For New Team Members**
- [ ] Read all Tier 1 critical rules
- [ ] Understand meeting rules and responsibilities
- [ ] Practice rule application in safe environment
- [ ] Demonstrate rule compliance in real situations
- [ ] Provide feedback on rule clarity and usability

### **For New Projects**
- [ ] Identify applicable rules for project context
- [ ] Customize rules for project-specific needs
- [ ] Set up automation and compliance monitoring
- [ ] Train team on project-specific rule applications
- [ ] Establish rule compliance measurement and improvement

### **For Ongoing Operations**
- [ ] Regular rule compliance monitoring
- [ ] Continuous rule effectiveness measurement
- [ ] Team feedback collection and incorporation
- [ ] Rule optimization and improvement
- [ ] Documentation maintenance and updates

---

## 🎯 **QUICK REFERENCE GUIDE**

### **Emergency Rule Reference**
| Situation | Primary Rules | Quick Actions |
|-----------|---------------|--------------|
| **Sprint in Jeopardy** | Meeting Rules §8 + Cursor Rules §1 | Emergency meeting, sprint replanning |
| **Quality Issues** | Quality Rules + Cursor Rules §4 | Enhanced testing, definition of done review |
| **Team Conflict** | Meeting Rules §4 + Collaboration | Retrospective, conflict resolution session |
| **Scope Creep** | Cursor Rules §1 + Meeting Rules §2 | Sprint goal reminder, scope management |
| **Technical Debt** | Cursor Rules §5 + Quality Rules | Technical retrospective, improvement sprint |

### **Daily Rule Reminders**
- **Every Day**: Daily standup rules, development rules compliance
- **Every Sprint**: All meeting rules, quality gates, velocity tracking
- **Every Release**: Release planning rules, epic planning, stakeholder alignment
- **Every Quarter**: Rule effectiveness review, process optimization

---

**Last Updated**: Current Session  
**Document Owner**: Agile Coach / Scrum Master  
**Next Review**: End of Sprint 1  
**Version**: 1.0
