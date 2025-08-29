# Velocity Tracking Guide

**Last Updated**: Current Session  
**Version**: 1.0  
**Status**: Active

## 📊 **Velocity Tracking Overview**

This document provides comprehensive guidelines for tracking team velocity in the AI-Dev-Agent project. Velocity tracking helps teams predict delivery capacity and improve estimation accuracy.

## 🎯 **What is Velocity?**

### **Definition**
Velocity is the average number of story points a team completes per sprint. It's a measure of team capacity and helps with sprint planning and release forecasting.

### **Key Concepts**
- **Story Points**: Relative measure of story complexity
- **Sprint Duration**: Fixed time period (typically 2 weeks)
- **Completed Stories**: Stories that meet the Definition of Done
- **Average Velocity**: Rolling average over multiple sprints

## 📈 **Velocity Calculation Methods**

### **Simple Average**
```
Velocity = Sum of completed story points / Number of sprints
```

### **Rolling Average (Recommended)**
```
Velocity = Average of last 3-5 sprints
```

### **Weighted Average**
```
Velocity = (Recent sprints weighted more heavily) / Total weight
```

## 📋 **Velocity Tracking Process**

### **Sprint Planning**
1. **Review Historical Velocity**: Use past velocity to guide planning
2. **Consider Team Capacity**: Account for team availability
3. **Plan Within Range**: Plan 80-100% of average velocity
4. **Account for Uncertainty**: Leave buffer for unknowns

### **Sprint Execution**
1. **Track Progress**: Monitor story completion daily
2. **Update Status**: Keep story status current
3. **Identify Blockers**: Address issues that slow progress
4. **Adjust Scope**: Modify sprint scope if needed

### **Sprint Review**
1. **Count Completed Points**: Only count stories that meet DoD
2. **Record Velocity**: Document actual velocity achieved
3. **Analyze Variance**: Compare planned vs actual
4. **Update Forecasts**: Adjust future sprint plans

## 📊 **Velocity Metrics**

### **Core Metrics**
- **Sprint Velocity**: Points completed in current sprint
- **Average Velocity**: Rolling average over 3-5 sprints
- **Velocity Range**: Min/max velocity for planning
- **Velocity Trend**: Direction of velocity over time
- **Velocity Stability**: Consistency of velocity

### **Derived Metrics**
- **Capacity Utilization**: Planned vs actual velocity
- **Forecast Accuracy**: Predicted vs actual completion
- **Scope Change Impact**: Effect of scope changes on velocity
- **Team Performance**: Velocity per team member

## 🎯 **Velocity Analysis**

### **Trend Analysis**
- **Increasing Velocity**: Team improving or scope creep
- **Decreasing Velocity**: Team issues or technical debt
- **Stable Velocity**: Predictable team performance
- **Volatile Velocity**: Unstable process or estimation

### **Pattern Recognition**
- **Seasonal Patterns**: Holidays, vacations, events
- **Technical Patterns**: Complex vs simple stories
- **Team Patterns**: New members, skill development
- **Process Patterns**: Process changes impact

### **Root Cause Analysis**
- **Estimation Issues**: Over/under estimation patterns
- **Process Issues**: Blockers, dependencies, coordination
- **Technical Issues**: Technical debt, complexity
- **Team Issues**: Availability, skills, communication

## 📈 **Velocity Forecasting**

### **Short-term Forecasting (Next Sprint)**
- **Conservative Estimate**: 80% of average velocity
- **Realistic Estimate**: 90% of average velocity
- **Optimistic Estimate**: 100% of average velocity
- **Range Planning**: Plan for velocity range

### **Long-term Forecasting (Release Planning)**
- **Trend Analysis**: Project velocity trend
- **Seasonal Adjustments**: Account for known patterns
- **Team Growth**: Consider skill development
- **Process Improvements**: Account for planned improvements

### **Release Planning Example**
```
Release Goal: 200 story points
Average Velocity: 45 points/sprint
Sprint Duration: 2 weeks
Estimated Duration: 200 / 45 = 4.4 sprints ≈ 9 weeks
Buffer (20%): 9 * 1.2 = 11 weeks
```

## ⚠️ **Velocity Anti-Patterns**

### **Common Mistakes**
- **Gaming Velocity**: Artificially inflating estimates
- **Ignoring Trends**: Not analyzing velocity patterns
- **Over-planning**: Planning more than team capacity
- **Scope Creep**: Adding stories during sprint
- **Incomplete Stories**: Counting partially done work

### **Red Flags**
- **Sudden Velocity Changes**: Indicates process issues
- **Consistent Over-estimation**: Estimation bias
- **Consistent Under-estimation**: Scope creep or quality issues
- **High Variance**: Unstable process or estimation
- **Zero Velocity**: Team blocked or process broken

## 📊 **Velocity Tracking Tools**

### **Manual Tracking**
- **Sprint Board**: Physical or digital Kanban board
- **Spreadsheet**: Excel/Google Sheets for calculations
- **Burndown Charts**: Visual progress tracking
- **Velocity Charts**: Historical velocity visualization

### **Automated Tracking**
- **Project Management Tools**: Jira, Azure DevOps, etc.
- **Agile Tools**: VersionOne, Rally, etc.
- **Custom Dashboards**: Team-specific tracking
- **CI/CD Integration**: Automated status updates

### **Recommended Tools for AI-Dev-Agent**
- **GitHub Projects**: Integration with code repository
- **Custom Dashboard**: Built-in velocity tracking
- **Automated Reports**: Sprint automation scripts
- **Real-time Updates**: Live velocity tracking

## 📋 **Velocity Tracking Checklist**

### **Sprint Planning**
- [ ] Review historical velocity data
- [ ] Consider team capacity and availability
- [ ] Plan within velocity range (80-100%)
- [ ] Account for known blockers or events
- [ ] Document planning assumptions

### **Sprint Execution**
- [ ] Track story progress daily
- [ ] Update story status promptly
- [ ] Identify and address blockers
- [ ] Monitor velocity against plan
- [ ] Adjust scope if necessary

### **Sprint Review**
- [ ] Count only completed story points
- [ ] Verify Definition of Done met
- [ ] Record actual velocity achieved
- [ ] Analyze variance from plan
- [ ] Update velocity history

### **Retrospective**
- [ ] Discuss velocity performance
- [ ] Identify factors affecting velocity
- [ ] Plan improvements for next sprint
- [ ] Update velocity forecasts
- [ ] Document lessons learned

## 📈 **Velocity Improvement Strategies**

### **Estimation Improvement**
- **Reference Stories**: Use consistent reference points
- **Team Consensus**: Involve all team members
- **Historical Data**: Learn from past estimates
- **Regular Review**: Continuously improve estimation
- **Training**: Improve team estimation skills

### **Process Improvement**
- **Remove Blockers**: Address process impediments
- **Reduce Dependencies**: Minimize coordination overhead
- **Improve Communication**: Better team collaboration
- **Streamline Workflow**: Optimize development process
- **Automate Tasks**: Reduce manual overhead

### **Technical Improvement**
- **Reduce Technical Debt**: Address code quality issues
- **Improve Tooling**: Better development tools
- **Optimize Environment**: Faster builds and tests
- **Enhance Testing**: More efficient testing process
- **Better Architecture**: Reduce complexity

### **Team Improvement**
- **Skill Development**: Training and learning
- **Team Stability**: Reduce turnover
- **Cross-training**: Improve team flexibility
- **Better Collaboration**: Improve team dynamics
- **Clear Roles**: Reduce confusion and overlap

## 📊 **Velocity Reporting**

### **Sprint Reports**
- **Sprint Summary**: Completed points, velocity, variance
- **Story Breakdown**: Points by story type/category
- **Blocker Analysis**: Issues affecting velocity
- **Team Performance**: Individual contributions
- **Quality Metrics**: Bugs, technical debt impact

### **Release Reports**
- **Release Progress**: Points completed vs planned
- **Velocity Trends**: Historical velocity analysis
- **Forecast Accuracy**: Predicted vs actual
- **Risk Assessment**: Velocity-based risks
- **Recommendations**: Improvement suggestions

### **Executive Reports**
- **High-level Metrics**: Velocity trends and forecasts
- **Team Performance**: Overall team capacity
- **Project Health**: Velocity-based project status
- **Resource Planning**: Capacity for new work
- **Strategic Insights**: Long-term velocity patterns

## 🎯 **Velocity Goals and Targets**

### **Team Goals**
- **Stable Velocity**: Consistent performance
- **Improving Velocity**: Gradual capacity increase
- **Predictable Delivery**: Reliable forecasts
- **Quality Velocity**: High-quality deliverables
- **Sustainable Velocity**: Maintainable pace

### **Target Setting**
- **Realistic Targets**: Based on historical data
- **Incremental Improvement**: Small, achievable goals
- **Quality Focus**: Maintain quality while improving speed
- **Team Agreement**: Consensus on targets
- **Regular Review**: Adjust targets based on performance

## 📈 **Velocity Examples**

### **Example 1: Stable Team**
```
Sprint 1: 42 points
Sprint 2: 45 points
Sprint 3: 43 points
Sprint 4: 44 points
Average Velocity: 43.5 points
Planning Range: 35-44 points
```

### **Example 2: Improving Team**
```
Sprint 1: 35 points
Sprint 2: 38 points
Sprint 3: 42 points
Sprint 4: 45 points
Trend: Increasing
Forecast: 47-50 points next sprint
```

### **Example 3: Volatile Team**
```
Sprint 1: 50 points
Sprint 2: 30 points
Sprint 3: 55 points
Sprint 4: 35 points
Issue: High variance
Action: Investigate root causes
```

## 🔄 **Continuous Improvement**

### **Regular Review**
- **Sprint Retrospectives**: Discuss velocity performance
- **Monthly Analysis**: Review velocity trends
- **Quarterly Planning**: Adjust forecasts and targets
- **Annual Review**: Long-term velocity analysis

### **Improvement Actions**
- **Process Changes**: Implement process improvements
- **Tool Improvements**: Enhance tracking tools
- **Team Development**: Invest in team skills
- **Technical Improvements**: Address technical issues
- **Communication**: Improve team collaboration

---

**Last Updated**: Current Session  
**Next Review**: End of current sprint  
**Document Owner**: Scrum Master
