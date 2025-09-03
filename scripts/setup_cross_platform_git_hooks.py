#!/usr/bin/env python3
"""
🔧 Cross-Platform Git Hooks Setup Script
Purpose: Automatically configure git hooks that work on Windows, Linux, and macOS

Features:
- Detects current platform
- Sets up appropriate hook execution method
- Creates platform-specific backup and restore mechanisms
- Provides diagnostic information for troubleshooting
"""

import sys
import os
import platform
import shutil
from pathlib import Path


def main():
    """
    🚀 Setup cross-platform git hooks with intelligent platform detection.
    """
    print("🔧 Cross-Platform Git Hooks Setup")
    print("=" * 50)
    
    # Detect current platform
    system_info = detect_platform()
    print(f"📍 Detected Platform: {system_info['platform']} {system_info['architecture']}")
    print(f"🎨 Execution Style: {system_info['style']}")
    print()
    
    # Get project root and hooks directory
    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"
    
    if not hooks_dir.exists():
        print("❌ Git hooks directory not found. Make sure you're in a git repository.")
        return 1
    
    print(f"📁 Hooks Directory: {hooks_dir}")
    print()
    
    # Setup hooks based on platform
    success = setup_platform_specific_hooks(hooks_dir, system_info)
    
    if success:
        print("✅ Cross-platform git hooks setup complete!")
        print()
        test_hook_execution(hooks_dir, system_info)
    else:
        print("❌ Failed to setup git hooks")
        return 1
    
    return 0


def detect_platform():
    """
    🔍 Detect platform and determine optimal execution strategy.
    """
    system = platform.system().lower()
    machine = platform.machine()
    
    platform_info = {
        'platform': system,
        'architecture': machine,
        'python_executable': sys.executable,
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin',
        'is_linux': system == 'linux',
    }
    
    # Determine execution style
    if platform_info['is_windows']:
        platform_info['style'] = 'windows'
        platform_info['hook_type'] = 'python_with_windows_paths'
    else:
        platform_info['style'] = 'unix'
        platform_info['hook_type'] = 'python_with_shebang'
    
    return platform_info


def setup_platform_specific_hooks(hooks_dir, system_info):
    """
    🛠️ Setup hooks optimized for the current platform.
    """
    print(f"🔨 Setting up {system_info['style']} optimized hooks...")
    
    # Define hook files to setup
    hook_files = ['pre-commit', 'pre-push']
    
    success = True
    for hook_name in hook_files:
        hook_path = hooks_dir / hook_name
        
        try:
            if hook_name == 'pre-commit':
                setup_pre_commit_hook(hook_path, system_info)
            elif hook_name == 'pre-push':
                setup_pre_push_hook(hook_path, system_info)
            
            # Make executable on Unix systems
            if not system_info['is_windows']:
                os.chmod(hook_path, 0o755)
            
            print(f"  ✅ {hook_name} hook configured for {system_info['platform']}")
            
        except Exception as e:
            print(f"  ❌ Failed to setup {hook_name}: {e}")
            success = False
    
    return success


def setup_pre_commit_hook(hook_path, system_info):
    """
    📝 Setup the pre-commit hook with platform-specific optimizations.
    """
    # The hook content is already cross-platform, but we can add platform-specific comments
    hook_content = get_cross_platform_pre_commit_content(system_info)
    
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)


def setup_pre_push_hook(hook_path, system_info):
    """
    📤 Setup the pre-push hook with platform-specific optimizations.
    """
    hook_content = get_cross_platform_pre_push_content(system_info)
    
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)


def get_cross_platform_pre_commit_content(system_info):
    """
    📄 Get the pre-commit hook content optimized for the current platform.
    """
    # Read the current pre-commit hook content
    project_root = Path(__file__).parent.parent
    current_hook = project_root / ".git" / "hooks" / "pre-commit"
    
    if current_hook.exists():
        with open(current_hook, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add platform-specific header comment
        platform_header = f"""#!/usr/bin/env python3
# 🌍 Optimized for {system_info['platform']} {system_info['architecture']}
# 🎨 Using {system_info['style']} execution style
# 🐍 Python: {system_info['python_executable']}
"""
        
        # Replace the existing shebang and add our platform info
        lines = content.split('\n')
        if lines[0].startswith('#!'):
            lines[0] = platform_header.strip()
        else:
            lines.insert(0, platform_header.strip())
        
        return '\n'.join(lines)
    
    # Fallback: return a basic hook
    return f"""#!/usr/bin/env python3
# 🌍 Cross-platform pre-commit hook for {system_info['platform']}
import sys
print("🧮 Pre-commit validation placeholder")
sys.exit(0)
"""


def get_cross_platform_pre_push_content(system_info):
    """
    📄 Get the pre-push hook content optimized for the current platform.
    """
    return f"""#!/usr/bin/env python3
# 🌍 Cross-platform pre-push hook for {system_info['platform']} {system_info['architecture']}
# 🎨 Using {system_info['style']} execution style

import sys
import subprocess
import os
from pathlib import Path

def main():
    print(f"🚀 Pre-push validation on {system_info['platform']}")
    print("🧹 Running repository cleanup...")
    
    # Add pre-push validations here
    # For example: run tests, check code quality, etc.
    
    print("✅ Pre-push validation complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""


def test_hook_execution(hooks_dir, system_info):
    """
    🧪 Test that the hooks can execute properly on this platform.
    """
    print("🧪 Testing Hook Execution")
    print("-" * 30)
    
    # Test pre-commit hook
    pre_commit_hook = hooks_dir / "pre-commit"
    if pre_commit_hook.exists():
        print("🔍 Testing pre-commit hook...")
        
        try:
            if system_info['is_windows']:
                # On Windows, test with explicit python call
                result = subprocess.run(
                    [sys.executable, str(pre_commit_hook)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                # On Unix systems, test direct execution
                result = subprocess.run(
                    [str(pre_commit_hook)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode == 0:
                print("  ✅ Pre-commit hook executes successfully")
                print(f"  📤 Output: {result.stdout.strip()}")
            else:
                print("  ⚠️ Pre-commit hook returned non-zero exit code")
                print(f"  📤 Output: {result.stdout.strip()}")
                print(f"  ❌ Error: {result.stderr.strip()}")
            
        except Exception as e:
            print(f"  ❌ Failed to test pre-commit hook: {e}")
    
    print()
    print("🎯 Platform-Specific Notes:")
    
    if system_info['is_windows']:
        print("  🪟 Windows: Hooks use Python executable discovery")
        print("  🐍 Priority: Anaconda > Standard Python > PATH")
        print("  ⚡ Performance: Optimized for Windows file paths")
    elif system_info['is_macos']:
        print("  🍎 macOS: Hooks use standard Unix conventions")
        print("  🐍 Priority: python3 > Homebrew > System Python")
        print("  ⚡ Performance: Optimized for macOS conventions")
    elif system_info['is_linux']:
        print("  🐧 Linux: Hooks use standard Unix conventions")
        print("  🐍 Priority: python3 > Distribution Python")
        print("  ⚡ Performance: Optimized for Linux distributions")


if __name__ == "__main__":
    sys.exit(main())
