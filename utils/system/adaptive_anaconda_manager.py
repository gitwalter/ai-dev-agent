#!/usr/bin/env python3
"""
Adaptive Anaconda Manager
========================

Automatically detects and adapts to different Anaconda installations
across workstations, solving the multi-environment development issue.

Author: AI-Dev-Agent Team
Created: 2024
License: Open Source - For seamless development everywhere
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import json

class AdaptiveAnacondaManager:
    """
    Automatically detects Anaconda installations and provides
    adaptive path management for cross-workstation development.
    """
    
    def __init__(self):
        self.system_type = platform.system().lower()
        self.detected_installations = {}
        self.active_installation = None
        self.config_file = Path.home() / ".ai_dev_agent" / "anaconda_config.json"
        
        # Common Anaconda installation patterns
        self.common_paths = self._get_common_installation_paths()
        
        print("🐍 Adaptive Anaconda Manager initialized")
        self._detect_and_configure()
    
    def _get_common_installation_paths(self) -> List[str]:
        """Get common Anaconda installation paths by platform."""
        
        if self.system_type == "windows":
            return [
                "C:\\App\\Anaconda",
                "C:\\Anaconda",
                "C:\\Users\\{username}\\Anaconda3",
                "C:\\Users\\{username}\\anaconda3",
                "C:\\ProgramData\\Anaconda3",
                "D:\\Anaconda",
                "D:\\App\\Anaconda"
            ]
        elif self.system_type == "darwin":  # macOS
            return [
                "/opt/anaconda3",
                "/usr/local/anaconda3",
                "~/anaconda3",
                "~/opt/anaconda3"
            ]
        else:  # Linux
            return [
                "/opt/anaconda3",
                "/usr/local/anaconda3",
                "~/anaconda3",
                "~/miniconda3"
            ]
    
    def _detect_and_configure(self) -> None:
        """Detect Anaconda installations and configure for current system."""
        
        print("🔍 Detecting Anaconda installations...")
        
        # 1. Try to load existing configuration
        if self._load_existing_config():
            print("📋 Loaded existing Anaconda configuration")
            return
        
        # 2. Auto-detect installations
        self._detect_installations()
        
        # 3. Select best installation
        self._select_best_installation()
        
        # 4. Save configuration
        self._save_configuration()
        
        print(f"✅ Anaconda configuration complete: {self.active_installation['base_path']}")
    
    def _load_existing_config(self) -> bool:
        """Try to load existing Anaconda configuration."""
        
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Verify the configured installation still exists
            if self._verify_installation(config.get('active_installation', {})):
                self.active_installation = config['active_installation']
                self.detected_installations = config.get('detected_installations', {})
                return True
            else:
                print("⚠️ Configured Anaconda installation no longer valid, re-detecting...")
                return False
                
        except Exception as e:
            print(f"⚠️ Error loading Anaconda configuration: {e}")
            return False
    
    def _detect_installations(self) -> None:
        """Detect all available Anaconda installations."""
        
        username = os.getenv('USERNAME') or os.getenv('USER') or 'user'
        
        for path_template in self.common_paths:
            # Expand username in path
            path = path_template.format(username=username)
            expanded_path = os.path.expanduser(path)
            
            if self._is_valid_anaconda_installation(expanded_path):
                installation_info = self._analyze_installation(expanded_path)
                if installation_info:
                    self.detected_installations[expanded_path] = installation_info
                    print(f"✅ Found Anaconda: {expanded_path}")
        
        # Also check conda command in PATH
        self._detect_path_conda()
    
    def _detect_path_conda(self) -> None:
        """Detect conda installation from PATH."""
        
        try:
            result = subprocess.run(['conda', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Try to find conda executable location
                result = subprocess.run(['where', 'conda'] if self.system_type == 'windows' else ['which', 'conda'],
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    conda_path = result.stdout.strip().split('\n')[0]
                    base_path = str(Path(conda_path).parent.parent)
                    
                    if self._is_valid_anaconda_installation(base_path):
                        installation_info = self._analyze_installation(base_path)
                        if installation_info:
                            self.detected_installations[base_path] = installation_info
                            print(f"✅ Found Anaconda in PATH: {base_path}")
        
        except Exception as e:
            print(f"ℹ️ Could not detect conda from PATH: {e}")
    
    def _is_valid_anaconda_installation(self, path: str) -> bool:
        """Check if path contains a valid Anaconda installation."""
        
        base_path = Path(path)
        
        # Check for essential Anaconda components
        required_components = []
        
        if self.system_type == "windows":
            required_components = [
                base_path / "python.exe",
                base_path / "Scripts" / "conda.exe",
                base_path / "Scripts" / "pip.exe"
            ]
        else:
            required_components = [
                base_path / "bin" / "python",
                base_path / "bin" / "conda",
                base_path / "bin" / "pip"
            ]
        
        return all(component.exists() for component in required_components)
    
    def _analyze_installation(self, path: str) -> Optional[Dict]:
        """Analyze an Anaconda installation and return info."""
        
        try:
            base_path = Path(path)
            
            # Get Python version
            python_exe = self._get_python_executable(path)
            result = subprocess.run([python_exe, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            python_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # Get conda version
            conda_exe = self._get_conda_executable(path)
            result = subprocess.run([conda_exe, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            conda_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            return {
                "base_path": path,
                "python_executable": str(python_exe),
                "conda_executable": str(conda_exe),
                "pip_executable": str(self._get_pip_executable(path)),
                "activate_script": str(self._get_activate_script(path)),
                "python_version": python_version,
                "conda_version": conda_version,
                "platform": self.system_type,
                "valid": True
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing installation {path}: {e}")
            return None
    
    def _select_best_installation(self) -> None:
        """Select the best Anaconda installation to use."""
        
        if not self.detected_installations:
            raise RuntimeError("No valid Anaconda installations found!")
        
        # Priority: prefer non-user directories, then most recent versions
        best_installation = None
        best_score = -1
        
        for path, info in self.detected_installations.items():
            score = 0
            
            # Prefer system-wide installations
            if not ("Users" in path or "user" in path.lower()):
                score += 10
            
            # Prefer shorter paths (usually more standard)
            score += max(0, 20 - len(path.split(os.sep)))
            
            # Prefer installations with "App" in path (likely managed)
            if "App" in path:
                score += 5
            
            if score > best_score:
                best_score = score
                best_installation = info
        
        self.active_installation = best_installation
    
    def _verify_installation(self, installation_info: Dict) -> bool:
        """Verify that an installation is still valid."""
        
        if not installation_info:
            return False
        
        required_files = [
            installation_info.get("python_executable"),
            installation_info.get("conda_executable"),
            installation_info.get("pip_executable")
        ]
        
        return all(Path(f).exists() for f in required_files if f)
    
    def _save_configuration(self) -> None:
        """Save current configuration to file."""
        
        config = {
            "active_installation": self.active_installation,
            "detected_installations": self.detected_installations,
            "last_updated": str(Path(__file__).stat().st_mtime),
            "system_type": self.system_type
        }
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _get_python_executable(self, base_path: str) -> Path:
        """Get Python executable path for installation."""
        base = Path(base_path)
        return base / "python.exe" if self.system_type == "windows" else base / "bin" / "python"
    
    def _get_conda_executable(self, base_path: str) -> Path:
        """Get conda executable path for installation."""
        base = Path(base_path)
        return base / "Scripts" / "conda.exe" if self.system_type == "windows" else base / "bin" / "conda"
    
    def _get_pip_executable(self, base_path: str) -> Path:
        """Get pip executable path for installation."""
        base = Path(base_path)
        return base / "Scripts" / "pip.exe" if self.system_type == "windows" else base / "bin" / "pip"
    
    def _get_activate_script(self, base_path: str) -> Path:
        """Get activate script path for installation."""
        base = Path(base_path)
        return base / "Scripts" / "activate.bat" if self.system_type == "windows" else base / "bin" / "activate"
    
    # Public API Methods
    
    def get_python_command(self) -> str:
        """Get the Python command to use."""
        return self.active_installation["python_executable"]
    
    def get_conda_command(self) -> str:
        """Get the conda command to use."""
        return self.active_installation["conda_executable"]
    
    def get_pip_command(self) -> str:
        """Get the pip command to use."""
        return self.active_installation["pip_executable"]
    
    def get_activate_command(self, env_name: str = None) -> str:
        """Get the activate command for an environment."""
        activate_script = self.active_installation["activate_script"]
        
        if env_name:
            return f'"{activate_script}" {env_name}'
        else:
            return f'"{activate_script}"'
    
    def run_python_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a Python command using the detected installation."""
        full_command = [self.get_python_command()] + command
        return subprocess.run(full_command, **kwargs)
    
    def run_conda_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a conda command using the detected installation."""
        full_command = [self.get_conda_command()] + command
        return subprocess.run(full_command, **kwargs)
    
    def run_pip_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a pip command using the detected installation."""
        full_command = [self.get_pip_command()] + command
        return subprocess.run(full_command, **kwargs)
    
    def create_environment(self, env_name: str, python_version: str = "3.11") -> bool:
        """Create a new conda environment."""
        try:
            result = self.run_conda_command([
                "create", "-n", env_name, f"python={python_version}", "-y"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created environment: {env_name}")
                return True
            else:
                print(f"❌ Failed to create environment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating environment: {e}")
            return False
    
    def install_package(self, package: str, env_name: str = None) -> bool:
        """Install a package using conda or pip."""
        try:
            # Try conda first
            conda_cmd = ["install", package, "-y"]
            if env_name:
                conda_cmd = ["-n", env_name] + conda_cmd
            
            result = self.run_conda_command(conda_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Installed {package} via conda")
                return True
            
            # Fall back to pip
            pip_cmd = ["install", package]
            result = self.run_pip_command(pip_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Installed {package} via pip")
                return True
            else:
                print(f"❌ Failed to install {package}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing package: {e}")
            return False
    
    def get_installation_info(self) -> Dict:
        """Get information about the active installation."""
        return self.active_installation.copy() if self.active_installation else {}
    
    def list_detected_installations(self) -> Dict:
        """Get all detected installations."""
        return self.detected_installations.copy()

# Global instance for easy access
anaconda_manager = None

def get_anaconda_manager() -> AdaptiveAnacondaManager:
    """Get the global Anaconda manager instance."""
    global anaconda_manager
    if anaconda_manager is None:
        anaconda_manager = AdaptiveAnacondaManager()
    return anaconda_manager

def get_python_command() -> str:
    """Quick access to Python command."""
    return get_anaconda_manager().get_python_command()

def get_conda_command() -> str:
    """Quick access to conda command."""
    return get_anaconda_manager().get_conda_command()

def get_pip_command() -> str:
    """Quick access to pip command."""
    return get_anaconda_manager().get_pip_command()

if __name__ == "__main__":
    # Demonstration
    print("🐍 " + "="*50)
    print("🔧 ADAPTIVE ANACONDA MANAGER DEMONSTRATION")
    print("="*50)
    
    manager = AdaptiveAnacondaManager()
    
    print(f"\n📊 ACTIVE INSTALLATION:")
    info = manager.get_installation_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 ALL DETECTED INSTALLATIONS:")
    for path, installation in manager.list_detected_installations().items():
        print(f"   {path}: {installation['python_version']}, {installation['conda_version']}")
    
    print(f"\n⚡ QUICK COMMANDS:")
    print(f"   Python: {manager.get_python_command()}")
    print(f"   Conda: {manager.get_conda_command()}")
    print(f"   Pip: {manager.get_pip_command()}")
    
    print(f"\n✨ Anaconda Manager ready for seamless cross-workstation development!")
    print("="*50)
