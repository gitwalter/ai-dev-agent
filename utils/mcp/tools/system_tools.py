#!/usr/bin/env python3
"""
System Tools for MCP Server
===========================

Tool wrapper implementations for system operation functionality.
These wrappers connect MCP tool definitions to existing system utilities.

Tools Implemented:
- system.platform_commands: Platform-safe command execution
- system.configure_logging: Logging configuration management
- system.manage_toml_config: TOML configuration management

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1)
"""

import logging
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


async def platform_commands(command: str, args: Optional[List[str]] = None, 
                          safe_mode: bool = True, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute platform-safe commands with proper validation.
    
    Args:
        command: Command to execute
        args: Command arguments
        safe_mode: Enable safety checks and validation
        timeout: Command timeout in seconds
        
    Returns:
        Dictionary with command execution results
    """
    try:
        # Import platform safe commands
        from utils.core.platform_safe_commands import PlatformSafeCommands
        
        # Create platform commands instance
        platform_cmd = PlatformSafeCommands()
        
        # Validate command in safe mode
        if safe_mode:
            validation_result = platform_cmd.validate_command(command, args or [])
            if not validation_result.get("safe", False):
                return {
                    "success": False,
                    "error": f"Command not safe: {validation_result.get('reason', 'Unknown')}",
                    "command": command,
                    "safe_mode": True
                }
        
        # Execute command with platform-specific handling
        current_platform = platform.system()
        
        if current_platform == "Windows":
            result = platform_cmd.execute_windows_command(command, args, timeout)
        else:
            result = platform_cmd.execute_unix_command(command, args, timeout)
        
        logger.info(f"✅ Executed platform command: {command}")
        
        return {
            "success": True,
            "command": command,
            "args": args or [],
            "platform": current_platform,
            "exit_code": result.get("exit_code", 0),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "execution_time": result.get("execution_time", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError as e:
        logger.error(f"❌ Platform commands not available: {e}")
        
        # Fallback to basic subprocess execution
        try:
            full_command = [command] + (args or [])
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            return {
                "success": True,
                "command": command,
                "args": args or [],
                "platform": platform.system(),
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "fallback_mode": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timeout after {timeout} seconds",
                "command": command
            }
        except Exception as fallback_error:
            return {
                "success": False,
                "error": f"Platform commands not available and fallback failed: {fallback_error}",
                "command": command
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to execute platform command: {e}")
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "args": args
        }


async def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None,
                          format_type: str = "standard") -> Dict[str, Any]:
    """
    Configure system logging with specified parameters.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_type: Log format type (standard, detailed, json)
        
    Returns:
        Dictionary with logging configuration results
    """
    try:
        # Import logging configuration
        from utils.core.logging_config import setup_logging, LoggingConfig
        
        # Create logging configuration
        config = LoggingConfig(
            level=log_level.upper(),
            log_file=log_file,
            format_type=format_type
        )
        
        # Setup logging with new configuration
        logger_instance = setup_logging("mcp_system", config)
        
        # Test logging configuration
        test_message = f"Logging configured at {datetime.now().isoformat()}"
        logger_instance.info(test_message)
        
        logger.info(f"✅ Configured logging: {log_level} level")
        
        return {
            "success": True,
            "log_level": log_level.upper(),
            "log_file": log_file,
            "format_type": format_type,
            "logger_name": "mcp_system",
            "test_message": test_message,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError as e:
        logger.error(f"❌ Logging configuration not available: {e}")
        
        # Fallback to basic logging configuration
        try:
            import logging
            
            # Set basic logging level
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            logging.basicConfig(
                level=numeric_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                filename=log_file
            )
            
            return {
                "success": True,
                "log_level": log_level.upper(),
                "log_file": log_file,
                "fallback_mode": True,
                "message": "Basic logging configuration applied",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as fallback_error:
            return {
                "success": False,
                "error": f"Logging configuration not available and fallback failed: {fallback_error}",
                "requested_level": log_level
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to configure logging: {e}")
        return {
            "success": False,
            "error": str(e),
            "log_level": log_level,
            "log_file": log_file
        }


async def manage_toml_config(action: str, config_file: str, 
                           section: Optional[str] = None, 
                           key: Optional[str] = None, 
                           value: Any = None) -> Dict[str, Any]:
    """
    Manage TOML configuration files with read/write operations.
    
    Args:
        action: Action to perform (read, write, update, delete)
        config_file: Path to TOML configuration file
        section: Configuration section
        key: Configuration key
        value: Configuration value (for write/update operations)
        
    Returns:
        Dictionary with configuration management results
    """
    try:
        # Import TOML configuration management
        from utils.core.toml_config import TOMLConfig
        
        # Create TOML config instance
        config = TOMLConfig(config_file)
        
        result = {"success": True, "action": action, "config_file": config_file}
        
        if action == "read":
            if section and key:
                # Read specific key
                config_value = config.get(section, key)
                result.update({
                    "section": section,
                    "key": key,
                    "value": config_value
                })
            elif section:
                # Read entire section
                section_data = config.get_section(section)
                result.update({
                    "section": section,
                    "data": section_data
                })
            else:
                # Read entire config
                all_data = config.get_all()
                result.update({"data": all_data})
                
        elif action == "write" or action == "update":
            if not section or not key:
                return {
                    "success": False,
                    "error": "Section and key required for write/update operations",
                    "action": action
                }
            
            # Write/update configuration value
            config.set(section, key, value)
            config.save()
            
            result.update({
                "section": section,
                "key": key,
                "value": value,
                "saved": True
            })
            
        elif action == "delete":
            if not section:
                return {
                    "success": False,
                    "error": "Section required for delete operation",
                    "action": action
                }
            
            if key:
                # Delete specific key
                config.delete_key(section, key)
                result.update({
                    "section": section,
                    "key": key,
                    "deleted": "key"
                })
            else:
                # Delete entire section
                config.delete_section(section)
                result.update({
                    "section": section,
                    "deleted": "section"
                })
            
            config.save()
            result["saved"] = True
            
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "valid_actions": ["read", "write", "update", "delete"]
            }
        
        logger.info(f"✅ TOML config {action}: {config_file}")
        result["timestamp"] = datetime.now().isoformat()
        
        return result
        
    except ImportError as e:
        logger.error(f"❌ TOML configuration not available: {e}")
        return {
            "success": False,
            "error": f"TOML configuration module not available: {e}",
            "fallback_action": "Manual configuration required"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Configuration file not found: {config_file}",
            "action": action
        }
    except Exception as e:
        logger.error(f"❌ Failed to manage TOML config: {e}")
        return {
            "success": False,
            "error": str(e),
            "action": action,
            "config_file": config_file
        }
