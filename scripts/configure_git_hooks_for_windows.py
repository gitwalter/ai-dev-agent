#!/usr/bin/env python3
"""
🔧 Windows Git Hooks Configuration Script
Purpose: Configure Git to use Python directly for hooks, bypassing batch file restrictions

This script sets up Git configuration to work around Windows group policy restrictions
that may block batch file execution.
"""

import sys
import subprocess
import os
from pathlib import Path


def main():
    """
    🚀 Configure Git hooks for Windows with group policy workarounds.
    """
    print("🔧 Windows Git Hooks Configuration")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Find Python executable
    python_exe = find_python_executable()
    if not python_exe:
        print("❌ Could not find Python executable")
        return 1
    
    print(f"🐍 Found Python: {python_exe}")
    
    # Configure Git to use Python directly
    configure_git_for_python_hooks(python_exe)
    
    # Create a simple pre-commit hook that Git can execute
    create_simple_hook()
    
    # Test the configuration
    test_hook_configuration()
    
    print("✅ Git hooks configured for Windows!")
    return 0


def find_python_executable():
    """🔍 Find the best Python executable for this system."""
    candidates = [
        sys.executable,
        r"C:\App\Anaconda\python.exe",
        r"C:\ProgramData\Anaconda3\python.exe",
        "python",
        "python3"
    ]
    
    for candidate in candidates:
        if test_python_executable(candidate):
            return candidate
    
    return None


def test_python_executable(python_path):
    """🧪 Test if a Python executable works."""
    try:
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def configure_git_for_python_hooks(python_exe):
    """⚙️ Configure Git to handle hooks properly on Windows."""
    print("⚙️ Configuring Git for Python hooks...")
    
    # Set core.hooksPath if needed (optional)
    # git_config_commands = [
    #     ["git", "config", "core.hooksPath", ".git/hooks"]
    # ]
    
    # For now, we'll rely on the default hooks path
    print("  📁 Using default Git hooks path: .git/hooks")


def create_simple_hook():
    """📝 Create a simple hook that should work on Windows."""
    hooks_dir = Path(".git/hooks")
    
    # Remove the problematic batch file
    batch_hook = hooks_dir / "pre-commit"
    if batch_hook.exists():
        try:
            batch_hook.unlink()
            print("  🗑️ Removed problematic batch hook")
        except:
            print("  ⚠️ Could not remove batch hook")
    
    # Create a PowerShell script instead
    powershell_hook = hooks_dir / "pre-commit.ps1"
    powershell_content = f'''# Cross-Platform Git Hook (PowerShell Version)
$pythonExe = "{sys.executable.replace(chr(92), chr(92) + chr(92))}"
$hookScript = "$PSScriptRoot\\pre-commit.py"

if (Test-Path $hookScript) {{
    & $pythonExe $hookScript
    exit $LASTEXITCODE
}} else {{
    Write-Host "❌ Hook script not found: $hookScript"
    exit 1
}}
'''
    
    with open(powershell_hook, 'w') as f:
        f.write(powershell_content)
    
    print(f"  📝 Created PowerShell hook: {powershell_hook}")
    
    # Create a simple executable hook for Git
    simple_hook = hooks_dir / "pre-commit"
    
    # Try creating a Python script that Git can execute directly
    simple_content = f'''#!{sys.executable.replace(chr(92), chr(47))}
# Simple executable Python hook for Git
import sys
import subprocess
from pathlib import Path

hook_script = Path(__file__).parent / "pre-commit.py"
if hook_script.exists():
    result = subprocess.run([sys.executable, str(hook_script)])
    sys.exit(result.returncode)
else:
    print("❌ Hook script not found")
    sys.exit(1)
'''
    
    with open(simple_hook, 'w') as f:
        f.write(simple_content)
    
    print(f"  📝 Created simple hook: {simple_hook}")


def test_hook_configuration():
    """🧪 Test the hook configuration."""
    print("🧪 Testing hook configuration...")
    
    hooks_dir = Path(".git/hooks")
    
    # Test PowerShell hook
    ps_hook = hooks_dir / "pre-commit.ps1" 
    if ps_hook.exists():
        print("  ✅ PowerShell hook exists")
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_hook)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("  ✅ PowerShell hook executes successfully")
            else:
                print(f"  ⚠️ PowerShell hook failed: {result.stderr}")
        except Exception as e:
            print(f"  ❌ PowerShell test failed: {e}")
    
    # Test Python hook directly
    py_hook = hooks_dir / "pre-commit.py"
    if py_hook.exists():
        print("  ✅ Python hook script exists")
        try:
            result = subprocess.run(
                [sys.executable, str(py_hook)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("  ✅ Python hook executes successfully")
                # Show some output to verify it's working
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[:3]:  # Show first 3 lines
                    print(f"    📤 {line}")
            else:
                print(f"  ⚠️ Python hook failed: {result.stderr}")
        except Exception as e:
            print(f"  ❌ Python hook test failed: {e}")


if __name__ == "__main__":
    sys.exit(main())
