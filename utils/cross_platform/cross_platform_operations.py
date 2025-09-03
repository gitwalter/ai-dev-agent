#!/usr/bin/env python3
"""
🌍 Cross-Platform Operations Implementation

Provides concrete implementation of cross-platform system operations.
Automatically detects OS and provides appropriate commands and paths.
"""

import platform
import os
import sys
from typing import Dict, Any, Optional


class CrossPlatformOperations:
    """Systematic cross-platform operation handler."""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type == 'linux'
        self.is_macos = self.os_type == 'darwin'
        
    def detect_environment(self) -> Dict[str, Any]:
        """Detect and return current OS environment."""
        return {
            'os': self.os_type,
            'is_windows': self.is_windows,
            'is_linux': self.is_linux,
            'is_macos': self.is_macos,
            'shell': self._detect_shell(),
            'path_separator': os.sep,
            'line_ending': os.linesep,
            'python_executable': self._get_python_executable()
        }
    
    def _detect_shell(self) -> str:
        """Detect the current shell environment."""
        if self.is_windows:
            return 'powershell' if 'powershell' in os.environ.get('PSModulePath', '').lower() else 'cmd'
        else:
            shell = os.environ.get('SHELL', '/bin/bash')
            return os.path.basename(shell)
    
    def _get_python_executable(self) -> str:
        """Get the current Python executable path."""
        return sys.executable


class CrossPlatformCommands:
    """OS-appropriate command generation."""
    
    def __init__(self):
        self.ops = CrossPlatformOperations()
        
    def list_files(self, directory: str = ".") -> str:
        """Generate OS-appropriate file listing command."""
        if self.ops.is_windows:
            return f"dir \"{directory}\""
        else:
            return f"ls -la \"{directory}\""
    
    def check_file_exists(self, filepath: str) -> str:
        """Generate OS-appropriate file existence check."""
        if self.ops.is_windows:
            return f"if exist \"{filepath}\" echo EXISTS"
        else:
            return f"[ -f \"{filepath}\" ] && echo EXISTS"
    
    def copy_file(self, source: str, dest: str) -> str:
        """Generate OS-appropriate file copy command."""
        if self.ops.is_windows:
            return f"copy \"{source}\" \"{dest}\""
        else:
            return f"cp \"{source}\" \"{dest}\""
    
    def delete_file(self, filepath: str) -> str:
        """Generate OS-appropriate file deletion command."""
        if self.ops.is_windows:
            return f"del \"{filepath}\""
        else:
            return f"rm \"{filepath}\""
    
    def make_directory(self, dirpath: str) -> str:
        """Generate OS-appropriate directory creation command."""
        if self.ops.is_windows:
            return f"mkdir \"{dirpath}\""
        else:
            return f"mkdir -p \"{dirpath}\""
    
    def python_command(self, script_path: str, args: str = "") -> str:
        """Generate OS-appropriate Python execution command."""
        python_exe = self.ops._get_python_executable()
        if args:
            return f"\"{python_exe}\" \"{script_path}\" {args}"
        else:
            return f"\"{python_exe}\" \"{script_path}\""
    
    def get_environment_info(self) -> str:
        """Generate command to display environment information."""
        if self.ops.is_windows:
            return "echo OS: %OS% & echo User: %USERNAME% & echo Path: %PATH%"
        else:
            return "echo OS: $(uname -s) && echo User: $USER && echo Path: $PATH"


class CrossPlatformPaths:
    """OS-appropriate path handling."""
    
    def __init__(self):
        self.ops = CrossPlatformOperations()
    
    def normalize_path(self, path: str) -> str:
        """Convert path to OS-appropriate format."""
        return os.path.normpath(path)
    
    def join_paths(self, *args) -> str:
        """Join paths using OS-appropriate separator."""
        return os.path.join(*args)
    
    def get_executable_path(self, program: str) -> str:
        """Get OS-appropriate executable path."""
        if self.ops.is_windows and not program.endswith('.exe'):
            return f"{program}.exe"
        return program
    
    def get_python_executable(self) -> str:
        """Get OS-appropriate Python executable."""
        return self.ops._get_python_executable()
    
    def convert_to_platform_path(self, unix_path: str) -> str:
        """Convert Unix-style path to current platform format."""
        if self.ops.is_windows:
            return unix_path.replace('/', '\\')
        return unix_path
    
    def get_home_directory(self) -> str:
        """Get user home directory path."""
        return os.path.expanduser("~")
    
    def get_temp_directory(self) -> str:
        """Get system temporary directory path."""
        return os.path.tmpdir if hasattr(os, 'tmpdir') else '/tmp' if not self.ops.is_windows else 'C:\\temp'


class CrossPlatformAgent:
    """Base class ensuring all agents are cross-platform compliant."""
    
    def __init__(self):
        self.platform_ops = CrossPlatformOperations()
        self.platform_cmds = CrossPlatformCommands()
        self.platform_paths = CrossPlatformPaths()
        
        # Validate cross-platform compliance
        self._validate_platform_support()
    
    def execute_command(self, intent: str, **kwargs) -> str:
        """Execute command with OS-appropriate syntax."""
        command_map = {
            'list_files': self.platform_cmds.list_files,
            'check_file': self.platform_cmds.check_file_exists,
            'copy_file': self.platform_cmds.copy_file,
            'delete_file': self.platform_cmds.delete_file,
            'make_directory': self.platform_cmds.make_directory,
            'python_command': self.platform_cmds.python_command,
            'environment_info': self.platform_cmds.get_environment_info
        }
        
        if intent not in command_map:
            raise ValueError(f"Unknown command intent: {intent}")
        
        return command_map[intent](**kwargs)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get comprehensive platform information."""
        return self.platform_ops.detect_environment()
    
    def log_platform_info(self):
        """Log platform information for debugging."""
        info = self.get_platform_info()
        print(f"🌍 Platform: {info['os']} ({platform.machine()})")
        print(f"🐍 Python: {info['python_executable']}")
        print(f"🔧 Shell: {info['shell']}")
    
    def _validate_platform_support(self):
        """Ensure agent can operate on current platform."""
        env = self.platform_ops.detect_environment()
        
        if not any([env['is_windows'], env['is_linux'], env['is_macos']]):
            raise RuntimeError(f"Unsupported platform: {env['os']}")
        
        # Silent validation - only log in debug mode
        if os.environ.get('DEBUG_PLATFORM'):
            print(f"🌍 Agent initialized for {env['os']} platform")


# Convenience functions for direct use
def get_platform_command(intent: str, **kwargs) -> str:
    """Get platform-appropriate command without creating agent instance."""
    agent = CrossPlatformAgent()
    return agent.execute_command(intent, **kwargs)


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system().lower() == 'windows'


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system().lower() == 'linux'


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system().lower() == 'darwin'


def get_current_platform() -> str:
    """Get current platform name."""
    return platform.system().lower()


if __name__ == "__main__":
    # Demo the cross-platform operations
    print("🌍 Cross-Platform Operations Demo")
    print("=" * 50)
    
    agent = CrossPlatformAgent()
    agent.log_platform_info()
    
    print("\n📋 Commands for current platform:")
    commands = [
        ("list_files", {"directory": "."}),
        ("check_file", {"filepath": "README.md"}),
        ("python_command", {"script_path": "test.py"})
    ]
    
    for intent, kwargs in commands:
        cmd = agent.execute_command(intent, **kwargs)
        print(f"  {intent}: {cmd}")
    
    print("\n✅ Cross-platform operations demo complete!")
