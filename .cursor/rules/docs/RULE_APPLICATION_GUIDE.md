---
description: "Auto-generated description for RULE_APPLICATION_GUIDE.md"
category: "general"
priority: "low"
alwaysApply: true
globs: ["**/*"]
tags: ['general']
tier: "2"
---

# Rule Application Guide

## 🎯 **RULE ORGANIZATION & APPLICATION FRAMEWORK**

### **TIER 1: CRITICAL RULES FRAMEWORK** ⭐
**These rules are ALWAYS applied automatically through the Core Rule Application Framework**

#### **Application Priority: CRITICAL - Always Applied Automatically**

1. **Courage and Complete Work Rule** 💪 **CRITICAL RULE #1**
   - **When**: ALWAYS - applied automatically to every work session, task, and problem-solving situation
   - **How**: Automatic application through Core Rule Application Framework, systematic completion enforcement
   - **Validation**: 100% work completion, no partial results accepted, systematic problem-solving
   - **Priority**: **CRITICAL - AUTOMATICALLY APPLIED TO EVERY SITUATION**

2. **No Premature Success Rule** 🎯 **CRITICAL RULE #2**
   - **When**: ALWAYS - applied automatically to every progress report, completion claim, and status update
   - **How**: Automatic validation through Core Rule Application Framework, evidence-based success declaration
   - **Validation**: Complete validation before any success declaration, evidence required for all claims
   - **Priority**: **CRITICAL - AUTOMATICALLY APPLIED TO EVERY PROGRESS REPORT**

3. **No Failing Tests Rule** 🧪 **CRITICAL RULE #3**
   - **When**: ALWAYS - applied automatically to every development session and commit
   - **How**: Automatic application through Core Rule Application Framework, zero tolerance enforcement
   - **Validation**: 100% test success rate, no exceptions, automatic failure blocking
   - **Priority**: **CRITICAL - AUTOMATICALLY APPLIED TO EVERY DEVELOPMENT SESSION**

4. **Boy Scout Rule** 🏕️ **CRITICAL RULE #4**
   - **When**: ALWAYS - applied automatically to every code modification and cleanup
   - **How**: Automatic application through Core Rule Application Framework, proactive improvement enforcement
   - **Validation**: Codebase always enhanced, proactive improvements made, cleaner than found
   - **Priority**: **CRITICAL - AUTOMATICALLY APPLIED TO EVERY CODE MODIFICATION**

2. **Keep Things in Order Rule** 📋 **RULE #2**
   - **When**: ALWAYS - maintain order in everything
   - **How**: Keep tasklists, filenames, folder structure, commit messages, documentation organized
   - **Validation**: Clean, organized, professional project structure
   - **Priority**: **CRITICAL - MAINTAIN ORDER ALWAYS**
   - **Related**: File Organization Cleanup Rule - automatically delete empty files and organize misplaced files

3. **Maintain Focus and Big Picture Rule** 🎯 **RULE #3**
   - **When**: ALWAYS - during every development task
   - **How**: Stay focused on current task while maintaining awareness of all relationships (Zusammenhänge)
   - **Validation**: Task completed successfully without losing sight of overall project goals
   - **Priority**: **CRITICAL - BALANCE FOCUS WITH CONTEXT**

4. **Test-Driven Development Rule** ⭐
   - **When**: Every new feature, bug fix, or refactoring
   - **How**: Write tests first, then implement functionality
   - **Validation**: 90%+ test coverage, all tests passing

5. **Systematic Problem-Solving Rule** ⭐
   - **When**: Any problem or issue encountered
   - **How**: Define → Analyze → Test → Fix → Validate → Document
   - **Validation**: Clear problem definition and documented solution

3. **Framework-First Rule** ⭐
   - **When**: Any new implementation or feature
   - **How**: Use LangChain + LangGraph + LangSmith, Pydantic, Pytest, Streamlit, Mermaid
   - **Validation**: 80% reduction in custom code

4. **Error Exposure Rule** ⭐
   - **When**: All error handling scenarios
   - **How**: Expose all errors immediately, no silent handling
   - **Validation**: Zero silent errors, comprehensive error logging

5. **Continuous Validation Rule** ⭐
   - **When**: Every step of development process
   - **How**: Validate inputs, outputs, state changes, performance
   - **Validation**: All validations passing, no cascading failures

6. **Continuous Learning Rule** ⭐
   - **When**: Every interaction and development session
   - **How**: Document insights, share knowledge, recognize patterns
   - **Validation**: Knowledge base updated, patterns documented

7. **Code Quality and Architecture Rule** ⭐
   - **When**: All code development and review
   - **How**: Apply SOLID principles, clean code, design patterns
   - **Validation**: Maintainable, extensible, well-documented code

8. **Strict Naming Conventions Rule** ⭐
   - **When**: All naming decisions (files, classes, functions, variables)
   - **How**: Follow established naming conventions consistently
   - **Validation**: Clear, consistent, professional naming

9. **Comprehensive Test Pattern Rule** ⭐
   - **When**: All testing scenarios
   - **How**: Unit-first for new features, integration-first for system validation
   - **Validation**: Systematic testing approach, comprehensive coverage

10. **System Architecture Integration Rule** ⭐
    - **When**: All component design and integration
    - **How**: Design for system awareness, integration points, scalability
    - **Validation**: Well-integrated, scalable, maintainable components

11. **Expert Design Patterns Application Rule** ⭐
    - **When**: Complex design decisions and architecture
    - **How**: Apply GoF and Fowler patterns with expert care
    - **Validation**: Understandable, robust, well-documented patterns

12. **Automated Research Rule** ⭐
    - **When**: Development blocked >5 minutes, unknown issues
    - **How**: 5-minute rapid research with systematic methodology
    - **Validation**: Quick problem resolution, knowledge accumulation

### **TIER 2: DEVELOPMENT STANDARDS** 🔧
**These rules ensure consistent, high-quality development practices**

#### **Application Priority: HIGH - Applied to Relevant Contexts**

13. **AI Model Selection Rule** 🔧
    - **When**: All LLM operations and agent interactions
    - **How**: Use `utils.helpers.get_llm_model(task_type="agent_name")`
    - **Validation**: Optimal performance and cost efficiency

**Model Selection Matrix**:
- **Complex Tasks** (use `gemini-2.5-flash`):
  - Requirements Analysis - Complex reasoning and synthesis
  - Architecture Design - System design and pattern recognition  
  - Code Review - Sophisticated analysis and pattern recognition
  - Security Analysis - Advanced threat modeling and risk assessment
- **Simple Tasks** (use `gemini-2.5-flash-lite`):
  - Test Generation - Basic test case creation
  - Documentation - Simple documentation generation
  - Basic Code Generation - Straightforward code implementation

14. **File Organization & Cleanup Rule** 🔧
    - **When**: All file and directory management, before every commit
    - **How**: Consistent naming, logical grouping, clear hierarchy, automatic deletion of empty files, organize misplaced files
    - **Validation**: Easy navigation, clear structure, scalable organization, zero empty files, all files in correct locations
    - **Automation**: Pre-commit hooks, scheduled cleanup, CI/CD validation

15. **Documentation Maintenance Rule** 🔧
    - **When**: All code changes and updates
    - **How**: Update docs with code changes, use Mermaid diagrams
    - **Validation**: 100% documentation synchronization

16. **Security Best Practices Rule** 🔧
    - **When**: All sensitive data handling and configuration
    - **How**: Use Streamlit secrets, validate inputs, secure dependencies
    - **Validation**: Secure handling, no exposed sensitive data

17. **Performance-First Rule** 🔧
    - **When**: All performance-critical operations
    - **How**: Optimize prompts, use appropriate models, implement caching
    - **Validation**: Fast execution, low costs, good user experience

### **TIER 3: TESTING & QUALITY ASSURANCE** 🧪
**These rules ensure comprehensive testing and quality standards**

#### **Application Priority: ABSOLUTE - ZERO TOLERANCE**

21. **No Failing Tests Rule** 🧪 **ABSOLUTE PRIORITY**
    - **When**: ALWAYS - before commits, during development, in CI/CD
    - **How**: Block all progress on failing tests, immediate fixes required
    - **Validation**: 100% pass rate, no exceptions, commit blocking
    - **Priority**: **CRITICAL - STOP ALL WORK UNTIL FIXED**

#### **Application Priority: HIGH - Applied to Relevant Contexts**

18. **Test Organization Rule** 🧪
    - **When**: All test creation and organization
    - **How**: Organize by type (unit, integration, system, langgraph, isolated)
    - **Validation**: Clear test structure, easy discovery and execution

19. **Agent Testing & Parsing Rule** 🧪
    - **When**: Agent development and parsing issues
    - **How**: Isolated testing, systematic prompt-parser optimization
    - **Validation**: Optimal agent performance, reliable parsing

20. **Test Monitoring Rule** 🧪
    - **When**: All test execution and monitoring
    - **How**: Automated monitoring, immediate error detection
    - **Validation**: Fast bug detection, improved test reliability

### **TIER 4: PROJECT MANAGEMENT** 📊
**These rules ensure effective project management and organization**

#### **Application Priority: HIGH - Applied to Relevant Contexts**

22. **Tasklist Management Rule** 📊
    - **When**: All project progress and task tracking
    - **How**: Update tasklists with every change, track progress accurately
    - **Validation**: Clear project visibility, accurate progress tracking

23. **Implementation Roadmap Rule** 📊
    - **When**: All development planning and execution
    - **How**: Follow roadmap phases, update progress continuously
    - **Validation**: Systematic development, successful milestone achievement

#### **Application Priority: MEDIUM - Applied When Context is Relevant**

24. **Requirements Management Rule** 📊
    - **When**: All requirement tracking and validation
    - **How**: Document requirements clearly, validate against implementation
    - **Validation**: Clear project scope, successful requirement implementation

25. **Prompt Database Management Rule** 📊
    - **When**: All prompt management and optimization
    - **How**: Store prompts in database, use web editor, track performance
    - **Validation**: Centralized management, easy optimization

26. **Automation & Environment Rule** 📊
    - **When**: All automation and environment management
    - **How**: Automated testing, deployment, monitoring, documentation
    - **Validation**: Reduced manual effort, consistent environment

27. **Diagram Standards Rule** 📊
    - **When**: All visual documentation and diagrams
    - **How**: Use Mermaid diagrams, GitHub-compatible, clear syntax
    - **Validation**: GitHub-native rendering, modern documentation

### **TIER 5: DAILY WORKFLOW AUTOMATION** ⚡
**These rules automate daily development workflows**

#### **Application Priority: HIGH - Applied Daily**

28. **Daily Start Automation Rule** ⚡
    - **When**: Every development session start
    - **How**: Repository sync, tasklist analysis, health check, initial tests
    - **Validation**: Clean, ready-to-develop state

29. **Agile Daily Deployed Build Rule** ⚡
    - **When**: Every development day, triggered by commits or schedule
    - **How**: Automated build pipeline, quality gates, deployment integration, stakeholder communication
    - **Validation**: Daily deployable artifacts, quality assurance, stakeholder visibility
    - **Priority**: **CRITICAL - DAILY BUILD REQUIREMENT**

30. **Daily End Automation Rule** ⚡
    - **When**: Every development session end
    - **How**: Tasklist update, documentation sync, cleanup, final tests, commit
    - **Validation**: Clean, documented, committed state

## 🚀 **RULE APPLICATION DECISION TREE**

### **For Every Development Session**

```
START
├── 🚀 SESSION STARTUP ROUTINE (When user says "start our session")
│   ├── Step 1: Agile Artifacts Analysis
│   ├── Step 2: Rule Application Guide Loading
│   ├── Step 3: Rule Compliance Enforcement
│   ├── Step 4: Redundancy Cleanup Application
│   ├── Step 5: Test-Driven Development Work
│   ├── Step 6: Agile Artifacts Update
│   ├── Step 7: Autonomous Work Execution
│   └── Generate Session Summary
├── Apply Tier 1 Rules (Always)
│   ├── Test-Driven Development
│   ├── Systematic Problem-Solving
│   ├── Framework-First
│   ├── Error Exposure
│   ├── Continuous Validation
│   └── Continuous Learning
├── Apply Daily Start Automation
├── Apply Daily Build Rule (if build conditions met)
├── Apply Relevant Tier 2 Rules
├── Apply Relevant Tier 3 Rules
├── Apply Relevant Tier 4 Rules
├── Apply Daily End Automation
└── END
```

### **For Every Code Change**

```
START
├── Apply Test-Driven Development Rule
├── Apply Framework-First Rule
├── Apply Code Quality and Architecture Rule
├── Apply Strict Naming Conventions Rule
├── Apply File Organization Rule
├── Apply Documentation Maintenance Rule
├── Apply Security Best Practices Rule
├── Apply Performance-First Rule
├── Apply Test Organization Rule
├── Apply Tasklist Management Rule
└── END
```

### **For Every Problem Encountered**

```
START
├── Apply Systematic Problem-Solving Rule
├── Apply Error Exposure Rule
├── Apply Continuous Validation Rule
├── IF blocked >5 minutes
│   └── Apply Automated Research Rule
├── Apply Agent Testing & Parsing Rule (if applicable)
├── Apply Test Monitoring Rule
├── Apply No Failing Tests Rule
└── END
```

## 📋 **RULE COMPLIANCE CHECKLIST**

### **Before Starting Any Development Task**
- [ ] Tier 1 rules reviewed and ready to apply
- [ ] Daily start automation executed
- [ ] Current tasklist and roadmap reviewed
- [ ] Development environment prepared
- [ ] Test framework ready

### **During Development**
- [ ] Test-Driven Development followed
- [ ] Systematic problem-solving applied
- [ ] Framework-first approach used
- [ ] Errors exposed immediately
- [ ] Continuous validation performed
- [ ] Learning documented

### **After Completing Development Task**
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code quality standards met
- [ ] Naming conventions followed
- [ ] Tasklist updated
- [ ] Daily end automation executed

## 🎯 **RULE EFFECTIVENESS METRICS**

### **Efficiency Metrics**
- **Problem Resolution Time**: <30 minutes average
- **Feature Delivery Speed**: 3x faster with established patterns
- **Bug Detection Time**: <5 minutes with automated monitoring
- **Development Session Efficiency**: 50% improvement

### **Quality Metrics**
- **Test Coverage**: >90% for all components
- **Error Rate**: <1% with proper error handling
- **Code Quality Score**: >95% with automated standards
- **Documentation Accuracy**: 100% synchronized

### **Reliability Metrics**
- **System Uptime**: 99.9% with proper validation
- **Test Reliability**: 100% passing tests
- **Deployment Success**: 100% automated deployments
- **Knowledge Retention**: 100% documented learnings

## 🔄 **RULE EVOLUTION PROCESS**

### **Continuous Rule Improvement**
1. **Monitor Rule Effectiveness**: Track metrics and outcomes
2. **Identify Improvement Opportunities**: Analyze failures and inefficiencies
3. **Propose Rule Updates**: Suggest modifications and additions
4. **Test Rule Changes**: Validate improvements in controlled environment
5. **Implement Rule Updates**: Deploy improved rules systematically
6. **Document Rule Evolution**: Maintain rule change history

### **Rule Feedback Loop**
- **Daily**: Review rule application effectiveness
- **Weekly**: Analyze rule performance metrics
- **Monthly**: Evaluate rule evolution and improvements
- **Quarterly**: Comprehensive rule system review and optimization

---

**This guide ensures optimal rule application for maximum development efficiency, quality, and reliability.**
