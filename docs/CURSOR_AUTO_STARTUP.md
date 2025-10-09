# Cursor Auto-Startup System

## Overview

The Cursor Auto-Startup System ensures that Cursor AI integration is automatically initialized whenever you open the project in Cursor, providing seamless tracking and monitoring capabilities.

## How It Works

### 🔄 Automatic Startup Methods

1. **VS Code Tasks** (Primary Method)
   - File: `.vscode/tasks.json`
   - Triggers: When folder is opened (`runOn: "folderOpen"`)
   - Status: ✅ Configured

2. **Streamlit App Integration**
   - File: `apps/universal_composition_app.py`
   - Triggers: When Streamlit app starts
   - Status: ✅ Active

3. **Manual Startup Script**
   - File: `scripts/cursor_startup.py`
   - Usage: `python scripts/cursor_startup.py`
   - Status: ✅ Available

4. **Cursor Startup Hook**
   - File: `.cursor/startup.py`
   - Triggers: Cursor IDE startup (if supported)
   - Status: ✅ Configured

### 🎯 What Gets Started Automatically

When Cursor restarts, the integration will:

- ✅ **Initialize Tracking**: Connect to universal agent tracker
- ✅ **Monitor Rules**: Watch `.cursor/rules/*.mdc` files for changes
- ✅ **Detect Keywords**: Recognize `@agile`, `@debug`, `@test`, etc.
- ✅ **Track Context**: Monitor context switches and activity
- ✅ **Background Processing**: Run in daemon threads (non-blocking)

## Current Status

### ✅ What Works Now

- **Streamlit Integration**: Auto-starts when you run the Universal Composition App
- **Manual Startup**: Run `python scripts/cursor_startup.py` anytime
- **VS Code Tasks**: Should auto-run when folder opens (if VS Code tasks are supported)
- **Health Monitoring**: Check status with integration functions

### ⚠️ Limitations

- **Cursor-Specific Hooks**: Cursor may not support all VS Code auto-startup features
- **Session Persistence**: Integration runs per Python process, not globally
- **Manual Trigger**: May need manual startup in some cases

## Usage

### Check Current Status

```python
from utils.integration.cursor_auto_startup import get_initialization_status, is_cursor_integration_healthy

# Get detailed status
status = get_initialization_status()
print(f"Status: {status}")

# Quick health check
healthy = is_cursor_integration_healthy()
print(f"Healthy: {healthy}")
```

### Manual Startup

```bash
# Using the startup script
python scripts/cursor_startup.py

# Direct Python command
python -c "from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration; auto_initialize_cursor_integration()"
```

### Force Restart

```python
from utils.integration.cursor_auto_startup import force_reinitialize

# Force restart integration
success = force_reinitialize()
print(f"Restart successful: {success}")
```

## Troubleshooting

### Integration Not Starting

1. **Check Dependencies**:
   ```bash
   python -c "from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration"
   ```

2. **Manual Start**:
   ```bash
   python scripts/cursor_startup.py
   ```

3. **Check Status**:
   ```python
   from utils.integration.cursor_auto_startup import get_initialization_status
   print(get_initialization_status())
   ```

### Health Check Failed

If integration starts but health check fails:

1. **Check Universal Tracker**: Ensure database is accessible
2. **Check File Permissions**: Ensure `.cursor/rules/` is readable
3. **Check Background Threads**: Integration runs in daemon threads

### VS Code Tasks Not Running

If the folder-open task doesn't trigger:

1. **Check VS Code Version**: Ensure tasks are supported
2. **Manual Task**: Run "Start Cursor Integration" task from Command Palette
3. **Fallback**: Use manual startup script

## Files Overview

| File | Purpose | Auto-Run |
|------|---------|----------|
| `utils/integration/cursor_auto_startup.py` | Core auto-startup module | ❌ |
| `scripts/cursor_startup.py` | Manual startup script | ❌ |
| `.vscode/tasks.json` | VS Code auto-startup task | ✅ |
| `.cursor/startup.py` | Cursor IDE startup hook | ✅* |
| `apps/universal_composition_app.py` | Streamlit integration | ✅ |

*May depend on Cursor IDE support

## Next Steps

To ensure 100% automatic startup when Cursor restarts:

1. **Test VS Code Tasks**: Verify if Cursor supports `runOn: "folderOpen"`
2. **Cursor Extension**: Investigate Cursor-specific startup hooks
3. **Workspace Settings**: Configure Cursor to run startup commands
4. **Background Service**: Consider persistent service approach

## Summary

**Current State**: ✅ **Partially Automatic**
- Works automatically with Streamlit app
- Manual startup script available
- VS Code tasks configured (may work in Cursor)

**Recommendation**: Run `python scripts/cursor_startup.py` after opening the project to ensure integration is active, or start the Streamlit app which will auto-initialize the integration.
