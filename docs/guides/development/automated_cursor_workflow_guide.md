# Automated Cursor Workflow Guide for Human Developers

**Last Updated**: 2024-01-15  
**Version**: 1.0  
**Audience**: Human developers working with the AI-Dev-Agent system

## 🎯 **Overview**

This guide provides comprehensive instructions for human developers working with the fully automated Cursor setup. The system implements a sophisticated 7-step session startup routine and 3-step session shutdown process that ensures systematic, efficient, and rule-compliant development sessions.

## 🚀 **Session Startup Process**

### **Triggering Session Startup**

#### **Method 1: Voice Command (Recommended)**
Simply say one of these phrases in Cursor:
- `"start our session"`
- `"start session"`
- `"begin session"`

#### **Method 2: Script Execution**
```bash
# Navigate to project root
cd /path/to/ai-dev-agent

# Run session startup script
python scripts/session_startup.py
```

#### **Method 3: Streamlit App**
1. Start the Streamlit application:
   ```bash
   streamlit run apps/streamlit_app.py
   ```
2. Navigate to the main app page
3. Click "Start Session" button

### **7-Step Session Startup Routine**

When you trigger session startup, the system automatically executes this comprehensive routine:

#### **Step 1: Agile Artifacts Analysis** 📊
- **Purpose**: Analyzes highest priority tasks from agile artifacts
- **Actions**:
  - Reads product backlog for current sprint priorities
  - Identifies high-priority user stories (CRITICAL/HIGH priority)
  - Checks for blocking issues or critical failures
  - Determines immediate next action
- **Output**: Priority-driven task list and sprint alignment

#### **Step 2: Rule Application Guide Loading** 📋
- **Purpose**: Loads and applies all relevant cursor rules systematically
- **Actions**:
  - Reads rule application guide (RULE_APPLICATION_GUIDE.md)
  - Loads Tier 1 (Critical) rules - ALWAYS APPLIED
  - Loads situation-specific rules based on current context
  - Loads task-specific rules based on identified next action
  - Applies rule priority and conflict resolution
- **Output**: Comprehensive rule compliance plan

#### **Step 3: Rule Compliance Enforcement** ⚡
- **Purpose**: Applies all rules with zero exceptions
- **Actions**:
  - Applies No Failing Tests Rule (RULE #1) - ABSOLUTE PRIORITY
  - Applies Keep Things in Order Rule (RULE #2)
  - Applies Maintain Focus and Big Picture Rule (RULE #3)
  - Applies all other Tier 1 rules
  - Applies situation and task specific rules
- **Output**: Rule compliance status and any blocking issues

#### **Step 4: Redundancy Cleanup Application** 🧹
- **Purpose**: Applies redundancy cleanup rule radically but safely
- **Actions**:
  - Identifies and removes duplicate code
  - Consolidates similar functions and classes
  - Eliminates redundant configuration
  - Cleans up temporary files and artifacts
- **Output**: Clean, optimized codebase

#### **Step 5: Test-Driven Development Work** 🧪
- **Purpose**: Works test-driven on open task
- **Actions**:
  - Identifies current highest priority task
  - Writes tests first (TDD approach)
  - Implements minimum code to pass tests
  - Refactors while keeping tests passing
- **Output**: Working, tested code

#### **Step 6: Agile Artifacts Update** 📝
- **Purpose**: Updates all agile artifacts and documentation
- **Actions**:
  - Updates product backlog with progress
  - Updates sprint backlog with completed work
  - Updates user story status and progress
  - Updates documentation per Live Documentation Updates rule
  - Applies file organization and boyscout rules
- **Output**: Current, accurate project artifacts

#### **Step 7: Autonomous Work Execution** 🤖
- **Purpose**: Executes work autonomously with minimal chat output
- **Actions**:
  - Sets autonomous mode with focused problem-solving
  - Executes work with systematic approach
  - Maintains focus on solving the problem
  - Applies all rules throughout execution
- **Output**: Completed work with quality assurance

### **Session Startup Summary**

After completing all 7 steps, you'll receive a comprehensive summary:

```
## 🎯 **SESSION SUMMARY**

### **Agile Progress**
- Current Sprint: Sprint 1
- Sprint Goal: Implement core agent system
- High Priority Stories: 3 active
- Blocking Issues: 0 resolved

### **Rule Compliance**
- Tier 1 Rules: 6 applied
- Situation Rules: 3 applied
- Task Rules: 2 applied
- Compliance Status: COMPLIANT

### **Work Completed**
- Redundancy Cleanup: COMPLETE
- TDD Work: COMPLETE
- Artifact Updates: COMPLETE
- Autonomous Execution: COMPLETE

### **Quality Assurance**
- Tests Passing: 127/127
- Documentation Updated: ✅ Yes
- Repository Clean: ✅ Yes
- Git Status: SUCCESS

### **Next Actions**
- Continue with next high-priority story
- Review generated code and tests
- Update sprint progress
```

## 🔄 **During Session Activities**

### **Working with the Automated System**

#### **Autonomous Mode**
- The system works autonomously with minimal chat output
- Focus is on systematic problem-solving
- All rules are applied automatically throughout execution
- Quality gates prevent substandard work

#### **Human Interaction Points**
- **Approval Requests**: System may request human approval for critical decisions
- **Error Resolution**: Human intervention may be needed for complex errors
- **Priority Changes**: You can redirect focus to different tasks
- **Quality Reviews**: Review generated code and provide feedback

#### **Monitoring Progress**
- Check the session summary for current status
- Monitor test results and quality metrics
- Review generated artifacts and documentation
- Track agile progress and sprint alignment

### **Common Commands During Session**

#### **Status Check**
```bash
# Check current session status
python scripts/health_monitor_service.py --check
```

#### **Test Execution**
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/system/ -v
```

#### **Documentation Update**
```bash
# Update documentation index
python scripts/update_documentation_index.py

# Generate API documentation
python scripts/generate_api_docs.py
```

#### **Quality Checks**
```bash
# Run linting
python -m pylint src/ --errors-only

# Run code formatting
python -m black src/

# Run security checks
python -m bandit src/ -r
```

## 🛑 **Session Shutdown Process**

### **Triggering Session Shutdown**

#### **Method 1: Voice Command (Recommended)**
Say one of these phrases in Cursor:
- `"end session"`
- `"stop session"`
- `"end our session"`
- `"stop our session"`
- `"session complete"`
- `"done for today"`
- `"finish session"`
- `"complete session"`

#### **Method 2: Script Execution**
```bash
# Run session shutdown script
python scripts/session_shutdown.py
```

### **3-Step Session Shutdown Routine**

When you trigger session shutdown, the system automatically executes this comprehensive routine:

#### **Step 1: Comprehensive Test Validation** 🧪
- **Purpose**: Runs all tests and validates no errors exist
- **Actions**:
  - Runs all unit tests
  - Runs all integration tests
  - Runs all system tests
  - Runs all performance tests
  - Runs all security tests
  - Validates test results
- **Output**: Complete test validation report

#### **Step 2: Documentation Completeness Validation** 📚
- **Purpose**: Validates all documentation is complete and current
- **Actions**:
  - Validates main documentation files
  - Validates README files
  - Validates API documentation
  - Validates code documentation
  - Validates architecture documentation
  - Validates deployment documentation
  - Applies fixes if needed
- **Output**: Documentation validation report

#### **Step 3: Git Operations** 🔄
- **Purpose**: Performs proper git operations to maintain repository integrity
- **Actions**:
  - Stages all changes
  - Creates comprehensive commit message
  - Commits all changes
  - Pushes to remote repository
  - Validates git operations success
- **Output**: Git operations report

### **Session Shutdown Summary**

After completing all 3 steps, you'll receive a comprehensive summary:

```
## 🛑 **SESSION STOP SUMMARY**

### **Test Validation Results** 🧪
- Status: ✅ PASSED
- Total Tests Run: 127
- Unit Tests: ✅ (45 tests)
- Integration Tests: ✅ (32 tests)
- System Tests: ✅ (25 tests)
- Performance Tests: ✅ (15 tests)
- Security Tests: ✅ (10 tests)

### **Documentation Validation Results** 📚
- Status: ✅ VALIDATED
- Main Documentation: ✅
- README Files: ✅
- API Documentation: ✅
- Code Documentation: ✅
- Architecture Documentation: ✅
- Deployment Documentation: ✅
- Fixes Applied: ✅ Yes

### **Git Operations Results** 🔄
- Status: ✅ SUCCESS
- Commit Hash: a1b2c3d4e5f6
- Commit Message: Session completion: Implemented user authentication system
- Push Status: ✅ SUCCESS
- Changes Committed: 15 files

### **Session Stop Status** 🎯
- Overall Status: ✅ SUCCESS
- Session End Time: 2024-01-15 17:30:00
- Next Session: Ready to begin when needed

### **Quality Assurance** ✅
- All Tests Passing: ✅ Yes
- Documentation Complete: ✅ Yes
- Changes Committed: ✅ Yes
- Repository Clean: ✅ Yes

Session successfully ended with all quality checks passed! 🎉
```

## 🔧 **Configuration and Setup**

### **Prerequisites**

#### **Required Software**
- Python 3.8+
- Git
- Cursor IDE
- Google Gemini API key

#### **Environment Setup**
```bash
# Clone the repository
git clone <repository-url>
cd ai-dev-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **API Key Configuration**
1. Create `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key-here"
   ```
2. Ensure `.streamlit/secrets.toml` is in `.gitignore`

### **System Configuration**

#### **Cursor Rules**
The system uses comprehensive cursor rules located in `.cursor/rules/`:
- **Session Startup Rule**: `.cursor/rules/session_startup_routine_rule.mdc`
- **Session Stop Rule**: `.cursor/rules/session_stop_routine_rule.mdc`
- **Rule Application Guide**: `.cursor/rules/RULE_APPLICATION_GUIDE.md`

#### **Automation Status**
All rules are configured with `alwaysApply: true` for full automation:
- **Critical Rules**: Always applied
- **High Priority Rules**: Applied daily
- **Medium Priority Rules**: Applied as needed
- **Low Priority Rules**: Applied on demand

## 📊 **Monitoring and Troubleshooting**

### **Health Monitoring**

#### **System Health Check**
```bash
# Run comprehensive health check
python scripts/health_monitor_service.py --check

# Monitor health in real-time
python scripts/health_monitor_service.py --monitor
```

#### **Log Monitoring**
```bash
# View agent logs
tail -f logs/agent.log

# View workflow logs
tail -f logs/langchain/workflow.log

# View system logs
tail -f logs/system.log
```

### **Common Issues and Solutions**

#### **Session Startup Issues**

**Problem**: Session startup fails with "BLOCKED" status
**Solution**:
1. Check for failing tests: `python -m pytest tests/ -v`
2. Fix any failing tests
3. Ensure all dependencies are installed
4. Verify API key configuration

**Problem**: Rule compliance enforcement fails
**Solution**:
1. Check rule files in `.cursor/rules/`
2. Verify rule syntax and structure
3. Check for conflicting rules
4. Review rule application guide

#### **Session Shutdown Issues**

**Problem**: Test validation fails during shutdown
**Solution**:
1. Fix failing tests before ending session
2. Run tests manually: `python -m pytest tests/ -v`
3. Check for test environment issues
4. Review test configuration

**Problem**: Git operations fail during shutdown
**Solution**:
1. Check git status: `git status`
2. Resolve any merge conflicts
3. Ensure remote repository is accessible
4. Check git credentials and permissions

#### **General Issues**

**Problem**: System becomes unresponsive
**Solution**:
1. Check system resources (CPU, memory)
2. Restart Cursor IDE
3. Kill any hanging processes
4. Check for infinite loops in automation

**Problem**: Generated code quality issues
**Solution**:
1. Review generated code manually
2. Run linting: `python -m pylint src/`
3. Run security checks: `python -m bandit src/ -r`
4. Provide feedback to improve generation

## 🎯 **Best Practices**

### **Session Management**

#### **Start of Day**
1. **Trigger session startup** with "start our session"
2. **Review session summary** to understand current priorities
3. **Set clear goals** for the session
4. **Monitor progress** throughout the day

#### **During Session**
1. **Trust the automation** - let the system work autonomously
2. **Provide feedback** when requested
3. **Monitor quality** of generated artifacts
4. **Stay focused** on high-priority tasks

#### **End of Day**
1. **Trigger session shutdown** with "end session"
2. **Review shutdown summary** to ensure quality
3. **Plan next session** based on progress
4. **Document any issues** for follow-up

### **Quality Assurance**

#### **Code Quality**
- Always review generated code before committing
- Run tests after any significant changes
- Monitor linting and security scan results
- Maintain documentation standards

#### **Process Quality**
- Follow the systematic approach
- Trust the rule-based automation
- Provide feedback for process improvement
- Maintain agile artifacts accuracy

### **Collaboration**

#### **Team Communication**
- Share session summaries with team
- Document any process improvements
- Provide feedback on automation effectiveness
- Collaborate on rule improvements

#### **Knowledge Sharing**
- Document lessons learned
- Share best practices
- Contribute to rule development
- Help improve automation

## 📚 **Additional Resources**

### **Documentation**
- [System Architecture](architecture/overview/system_diagram.md)
- [Development Roadmap](guides/implementation/roadmap.md)
- [Testing Guide](testing/README.md)
- [API Documentation](docs/api/README.md)

### **Scripts and Tools**
- [Session Startup Script](scripts/session_startup.py)
- [Health Monitor Service](scripts/health_monitor_service.py)
- [Git Hooks Setup](scripts/setup_git_hooks.py)

### **Configuration Files**
- [Cursor Rules](.cursor/rules/)
- [Test Configuration](tests/pytest.ini)
- [System Configuration](models/config.py)

## 🎉 **Success Metrics**

### **Session Success Indicators**
- ✅ All tests passing
- ✅ Documentation complete and current
- ✅ Code quality standards met
- ✅ Agile artifacts updated
- ✅ Repository clean and committed
- ✅ No blocking issues

### **Process Improvement**
- 📈 Reduced manual intervention
- 📈 Increased development velocity
- 📈 Improved code quality
- 📈 Better documentation coverage
- 📈 Enhanced team collaboration

### **Automation Benefits**
- 🤖 Systematic, consistent approach
- 🤖 Reduced human error
- 🤖 Improved productivity
- 🤖 Better quality assurance
- 🤖 Enhanced project visibility

---

**Remember**: The fully automated Cursor setup is designed to maximize your productivity while maintaining high quality standards. Trust the automation, provide feedback when needed, and focus on the creative aspects of development while the system handles the systematic tasks.

**For support**: Check the troubleshooting section above or review the comprehensive documentation in the `docs/` directory.
