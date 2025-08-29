# Automated Workflow Quick Reference

**Last Updated**: 2024-01-15  
**Version**: 1.0

## 🚀 **Session Startup Commands**

### **Voice Commands (Recommended)**
```
"start our session"
"start session"
"begin session"
```

### **Script Commands**
```bash
# Session startup
python scripts/session_startup.py

# Session shutdown
python scripts/session_shutdown.py
```

### **Streamlit App**
```bash
streamlit run apps/streamlit_app.py
```

## 🛑 **Session Shutdown Commands**

### **Voice Commands (Recommended)**
```
"end session"
"stop session"
"end our session"
"stop our session"
"session complete"
"done for today"
"finish session"
"complete session"
```

## 📊 **7-Step Session Startup Routine**

1. **📊 Agile Artifacts Analysis** - Analyzes highest priority tasks
2. **📋 Rule Application Guide Loading** - Loads and applies cursor rules
3. **⚡ Rule Compliance Enforcement** - Applies all rules with zero exceptions
4. **🧹 Redundancy Cleanup Application** - Removes duplicates and optimizes
5. **🧪 Test-Driven Development Work** - Works test-driven on open task
6. **📝 Agile Artifacts Update** - Updates all artifacts and documentation
7. **🤖 Autonomous Work Execution** - Executes work autonomously

## 🛑 **3-Step Session Shutdown Routine**

1. **🧪 Comprehensive Test Validation** - Runs all tests and validates
2. **📚 Documentation Completeness Validation** - Validates all documentation
3. **🔄 Git Operations** - Stages, commits, and pushes changes

## 🔧 **Common Commands During Session**

### **Status Check**
```bash
python scripts/health_monitor_service.py --check
```

### **Test Execution**
```bash
# All tests
python -m pytest tests/ -v

# Specific categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/system/ -v
```

### **Quality Checks**
```bash
# Linting
python -m pylint src/ --errors-only

# Code formatting
python -m black src/

# Security checks
python -m bandit src/ -r
```

### **Log Monitoring**
```bash
# Agent logs
tail -f logs/agent.log

# Workflow logs
tail -f logs/langchain/workflow.log
```

## 🚀 **VS Code Launch Configurations**

### **Available Launch Configurations**

The project includes pre-configured VS Code launch configurations in `.vscode/launch.json`:

#### **Streamlit Applications**
1. **🚀 Main Streamlit App** - Launches main web interface (Port 8501)
2. **🤖 Prompt Manager App** - Launches prompt management interface (Port 8502)
3. **🔍 System Health Monitor Dashboard** - Real-time system health monitoring (Port 8505)
4. **🚀 Main Streamlit App (Debug Port 8503)** - Debug version with detailed logging
5. **🤖 Prompt Manager App (Debug Port 8504)** - Debug version for prompt manager
6. **🔍 System Health Monitor (Debug Port 8506)** - Debug version for health monitoring

#### **CLI Applications**
7. **🔧 Main CLI App (Debug)** - Debug CLI entry point with console integration

### **Quick Start with Launch Configurations**

1. **Open VS Code** in the project root directory
2. **Press F5** or **Ctrl+Shift+D** to open Run and Debug panel
3. **Select configuration** from dropdown (e.g., "🚀 Main Streamlit App")
4. **Click Play button** or **Press F5** to launch

### **Configuration Details**

#### **Anaconda Python Integration**
- All configurations use: `D:\Anaconda\python.exe`
- Automatic PYTHONPATH configuration
- Integrated terminal support

#### **Port Assignments**
| Application | Standard Port | Debug Port |
|-------------|---------------|------------|
| Main Streamlit App | 8501 | 8503 |
| Prompt Manager App | 8502 | 8504 |
| System Health Monitor | 8505 | 8506 |

#### **Debug Features**
- Integrated terminal console
- Breakpoint support
- Auto-reload for Streamlit apps
- Enhanced logging in debug versions

### **Troubleshooting Launch Configurations**

#### **Common Issues**
1. **Python not found**: Verify Anaconda installation at `D:\Anaconda\`
2. **Module not found**: Ensure working directory is project root
3. **Port conflicts**: Use debug configurations with alternative ports

#### **Manual Launch (Alternative)**
```bash
# Main Streamlit App
D:\Anaconda\python.exe -m streamlit run apps/streamlit_app.py --server.port 8501

# Prompt Manager App  
D:\Anaconda\python.exe -m streamlit run apps/prompt_manager_app.py --server.port 8502

# System Health Monitor Dashboard
D:\Anaconda\python.exe -m streamlit run utils/health_dashboard.py --server.port 8505

# CLI App Debug
D:\Anaconda\python.exe apps/main.py
```

## 📁 **Key Files and Directories**

### **Session Management**
- `.cursor/rules/session_startup_routine_rule.mdc` - Session startup rules
- `.cursor/rules/session_stop_routine_rule.mdc` - Session shutdown rules
- `scripts/session_startup.py` - Session startup script
- `scripts/session_shutdown.py` - Session shutdown script

### **Configuration**
- `.streamlit/secrets.toml` - API keys and secrets
- `.cursor/rules/RULE_APPLICATION_GUIDE.md` - Rule application guide
- `models/config.py` - System configuration

### **Documentation**
- `docs/guides/development/automated_cursor_workflow_guide.md` - Complete guide
- `docs/DOCUMENTATION_INDEX.md` - Documentation index
- `README.md` - Project overview

## 🎯 **Success Indicators**

### **Session Startup Success**
- ✅ All tests passing
- ✅ Rule compliance enforced
- ✅ Redundancy cleanup complete
- ✅ Agile artifacts updated
- ✅ Autonomous work executing

### **Session Shutdown Success**
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Changes committed
- ✅ Repository clean

## ⚠️ **Troubleshooting**

### **Session Startup Issues**
```bash
# Check for failing tests
python -m pytest tests/ -v

# Verify API key
cat .streamlit/secrets.toml

# Check rule files
ls .cursor/rules/
```

### **Session Shutdown Issues**
```bash
# Fix failing tests first
python -m pytest tests/ -v

# Check git status
git status

# Verify documentation
ls docs/
```

### **General Issues**
```bash
# Health check
python scripts/health_monitor_service.py --check

# Restart Cursor IDE
# Kill hanging processes
# Check system resources
```

## 📞 **Support Resources**

### **Documentation**
- [Complete Guide](guides/development/automated_cursor_workflow_guide.md)
- [System Architecture](architecture/overview/system_diagram.md)
- [Testing Guide](testing/README.md)

### **Scripts**
- [Session Startup](scripts/session_startup.py)
- [Session Shutdown](scripts/session_shutdown.py)
- [Health Monitor](scripts/health_monitor_service.py)

### **Rules**
- [Session Startup Rules](.cursor/rules/session_startup_routine_rule.mdc)
- [Session Stop Rules](.cursor/rules/session_stop_routine_rule.mdc)
- [Rule Application Guide](.cursor/rules/RULE_APPLICATION_GUIDE.md)

---

**Remember**: Trust the automation, provide feedback when needed, and focus on creative development while the system handles systematic tasks.
