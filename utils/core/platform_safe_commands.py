"""
Platform-Safe Command Validation System
Ensures correct commands are used for the target platform.
"""

import platform
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CommandValidation:
    """Result of command validation."""
    is_safe: bool
    corrected_command: str
    warnings: List[str]
    platform_detected: str


class PlatformSafeCommands:
    """
    Validates and corrects commands for platform safety.
    Implements safety_first_principle.mdc requirements.
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.python_exe = self._detect_python_executable()
        
        # Platform-specific command mappings
        self.command_mappings = {
            "Windows": {
                "list_files": "Get-ChildItem",
                "test_file": "Test-Path", 
                "read_file": "Get-Content",
                "search_text": "Select-String",
                "change_directory": "Set-Location",
                "python": self.python_exe,
                "path_separator": "\\",
                "command_separator": ";"
            },
            "Linux": {
                "list_files": "ls",
                "test_file": "test -f",
                "read_file": "cat",
                "search_text": "grep", 
                "change_directory": "cd",
                "python": "python3",
                "path_separator": "/",
                "command_separator": "&&"
            },
            "Darwin": {  # macOS
                "list_files": "ls",
                "test_file": "test -f", 
                "read_file": "cat",
                "search_text": "grep",
                "change_directory": "cd",
                "python": "python3",
                "path_separator": "/",
                "command_separator": "&&"
            }
        }
    
    def _detect_python_executable(self) -> str:
        """Detect the correct Python executable for this platform."""
        if platform.system() == "Windows":
            # Check for Anaconda installation first
            anaconda_python = r"C:\App\Anaconda\python.exe"
            if os.path.exists(anaconda_python):
                return anaconda_python
            return "python.exe"
        else:
            return "python3"
    
    def validate_command(self, command: str) -> CommandValidation:
        """
        Validate and correct a command for platform safety.
        
        Args:
            command: The command to validate
            
        Returns:
            CommandValidation with safety status and corrections
        """
        warnings = []
        corrected_command = command
        
        # Check for Unix-style commands on Windows
        if self.platform == "Windows":
            corrected_command, warnings = self._correct_windows_command(command)
        
        # Check for Windows commands on Unix
        elif self.platform in ["Linux", "Darwin"]:
            corrected_command, warnings = self._correct_unix_command(command)
        
        # Validate Python executable
        corrected_command = self._correct_python_executable(corrected_command)
        
        is_safe = len(warnings) == 0 or corrected_command != command
        
        return CommandValidation(
            is_safe=is_safe,
            corrected_command=corrected_command,
            warnings=warnings,
            platform_detected=self.platform
        )
    
    def _correct_windows_command(self, command: str) -> tuple[str, List[str]]:
        """Correct Unix-style commands for Windows."""
        warnings = []
        corrected = command
        
        # Fix command chaining (cd && command -> separate commands)
        if " && " in command:
            warnings.append("Unix-style command chaining detected - use separate commands on Windows")
            # For Windows, we should use separate commands or proper PowerShell syntax
            parts = command.split(" && ")
            if len(parts) == 2 and parts[0].startswith("cd "):
                directory = parts[0].replace("cd ", "").strip()
                second_command = parts[1].strip()
                corrected = f"Set-Location '{directory}'; {second_command}"
        
        # Fix ls -> Get-ChildItem
        if command.startswith("ls ") or command == "ls":
            warnings.append("Unix 'ls' command detected - use 'Get-ChildItem' on Windows")
            corrected = corrected.replace("ls ", "Get-ChildItem ")
            corrected = corrected.replace("ls", "Get-ChildItem")
        
        # Fix cat -> Get-Content
        if "cat " in command:
            warnings.append("Unix 'cat' command detected - use 'Get-Content' on Windows")
            corrected = corrected.replace("cat ", "Get-Content ")
        
        # Fix grep -> Select-String
        if "grep " in command:
            warnings.append("Unix 'grep' command detected - use 'Select-String' on Windows")
            corrected = corrected.replace("grep ", "Select-String ")
        
        # Fix test -f -> Test-Path
        if "test -f " in command:
            warnings.append("Unix 'test -f' command detected - use 'Test-Path' on Windows")
            corrected = corrected.replace("test -f ", "Test-Path ")
        
        return corrected, warnings
    
    def _correct_unix_command(self, command: str) -> tuple[str, List[str]]:
        """Correct Windows commands for Unix systems."""
        warnings = []
        corrected = command
        
        # Fix Get-ChildItem -> ls
        if "Get-ChildItem" in command:
            warnings.append("Windows 'Get-ChildItem' command detected - use 'ls' on Unix")
            corrected = corrected.replace("Get-ChildItem", "ls")
        
        # Fix Get-Content -> cat
        if "Get-Content" in command:
            warnings.append("Windows 'Get-Content' command detected - use 'cat' on Unix")
            corrected = corrected.replace("Get-Content", "cat")
        
        # Fix Select-String -> grep
        if "Select-String" in command:
            warnings.append("Windows 'Select-String' command detected - use 'grep' on Unix")
            corrected = corrected.replace("Select-String", "grep")
        
        # Fix Test-Path -> test -f
        if "Test-Path" in command:
            warnings.append("Windows 'Test-Path' command detected - use 'test -f' on Unix")
            corrected = corrected.replace("Test-Path", "test -f")
        
        return corrected, warnings
    
    def _correct_python_executable(self, command: str) -> str:
        """Ensure correct Python executable is used."""
        corrected = command
        
        # Replace generic python with platform-specific executable
        if self.platform == "Windows":
            corrected = corrected.replace("python ", f"{self.python_exe} ")
            corrected = corrected.replace("python3 ", f"{self.python_exe} ")
        else:
            corrected = corrected.replace("python ", "python3 ")
        
        return corrected
    
    def get_safe_command(self, operation: str) -> str:
        """Get a safe command for a specific operation."""
        mapping = self.command_mappings.get(self.platform, {})
        return mapping.get(operation, operation)
    
    def create_safe_test_command(self, test_path: str = "tests/", exclude_ui: bool = True) -> str:
        """Create a platform-safe test command."""
        exclude_clause = "--ignore=tests/automated_ui/" if exclude_ui else ""
        return f"{self.python_exe} -m pytest {test_path} --tb=short -x {exclude_clause} -q"


# Global instance for easy use
platform_safe = PlatformSafeCommands()


def validate_command_before_execution(command: str) -> CommandValidation:
    """
    Validate a command before execution.
    This should be called before every run_terminal_cmd.
    """
    return platform_safe.validate_command(command)


def get_safe_test_command(exclude_ui: bool = True) -> str:
    """Get a safe test command for the current platform."""
    return platform_safe.create_safe_test_command(exclude_ui=exclude_ui)


# Example usage and validation
if __name__ == "__main__":
    # Test command validation
    test_commands = [
        "cd tests && python -m pytest",
        "ls utils/*.py", 
        "cat file.txt",
        "grep pattern file.txt",
        "test -f file.txt"
    ]
    
    for cmd in test_commands:
        validation = validate_command_before_execution(cmd)
        print(f"Original: {cmd}")
        print(f"Platform: {validation.platform_detected}")
        print(f"Safe: {validation.is_safe}")
        print(f"Corrected: {validation.corrected_command}")
        if validation.warnings:
            print(f"Warnings: {validation.warnings}")
        print("-" * 50)
