# 🤖 Manual UI Testing Guide

**Status**: DISABLED from automatic runs  
**Purpose**: Heavy UI tests that should be run manually only

## 🚫 **Why UI Tests are Disabled**

UI tests have been disabled from automatic pytest runs because they:
- Start browser instances and consume significant resources
- Take a long time to complete 
- Can cause interference with development workflow
- Are best run when specifically testing UI changes

## 🚀 **How to Run UI Tests Manually**

### **Full UI Test Suite**
```bash
python -m pytest tests/automated_ui/ -v
```

### **Specific UI Test**
```bash
python -m pytest tests/automated_ui/test_vibe_coding_ui_comprehensive.py -v
```

### **Quick UI Smoke Test**
```bash
python -m pytest tests/automated_ui/test_vibe_coding_ui_comprehensive.py::test_ui_page_load_performance -v
```

## 📋 **When to Run UI Tests**

- ✅ After making UI/UX changes
- ✅ Before major releases
- ✅ When debugging UI-specific issues
- ✅ During manual testing cycles
- ❌ NOT during regular development
- ❌ NOT in automated CI/CD (unless specifically configured)

## 🔧 **Re-enabling UI Tests**

If you need to re-enable UI tests in the automatic pytest runs:

1. **Remove from pytest.ini ignore list**:
   ```ini
   # Remove --ignore=tests/automated_ui from addopts
   ```

2. **Re-enable in cursor_auto_testing.py**:
   ```python
   # Uncomment the original _run_ui_tests implementation
   ```

## 📊 **UI Test Reports**

UI test reports are saved to:
```
tests/reports/ui_test_report_YYYYMMDD_HHMMSS.json
```

## 🎯 **UI Testing Best Practices**

- Run UI tests in a clean environment
- Ensure no other browser instances are running
- Use headless mode for faster execution
- Review generated reports for actionable insights
- Only run when actually needed

---

**Remember**: UI tests are powerful but resource-intensive. Use them wisely! 🎯
