#!/usr/bin/env python3
"""
Reliable Context Integration System
Automatically switches context and forces rule reloading in Cursor
"""

import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Optional
import sys
sys.path.append('.')
from utils.system.context.working_context_system import switch_context_and_prove_it_works

class ReliableContextIntegration:
    """
    Reliable system for automatic context switching and rule reloading.
    """
    
    def __init__(self):
        self.cursor_rules_file = Path(".cursor-rules")
        self.last_context = None
        self.last_file_hash = None
        self.context_history = []
        
    def get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content for change detection (optimized)."""
        try:
            if file_path.exists():
                # Use faster hash for performance
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Use first 1KB + file size for faster hashing
                    if len(content) > 1024:
                        hash_content = content[:1024] + str(len(content)).encode()
                    else:
                        hash_content = content
                    return hashlib.md5(hash_content).hexdigest()
        except:
            pass
        return ""
    
    def force_cursor_reload(self) -> bool:
        """
        Force Cursor to reload rules by modifying file timestamp and content.
        This uses multiple techniques to ensure Cursor detects the change.
        """
        try:
            if not self.cursor_rules_file.exists():
                return False
            
            # Method 1: Update file timestamp
            current_time = time.time()
            os.utime(self.cursor_rules_file, (current_time, current_time))
            
            # Method 2: Add and remove a comment to trigger content change
            with open(self.cursor_rules_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add timestamp comment at the top
            timestamp_comment = f"# Auto-reload trigger: {int(current_time)}\n"
            
            # Remove old timestamp comments
            lines = content.split('\n')
            filtered_lines = [line for line in lines if not line.startswith("# Auto-reload trigger:")]
            
            # Add new timestamp comment
            new_content = timestamp_comment + '\n'.join(filtered_lines)
            
            with open(self.cursor_rules_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Method 3: Minimal pause for file system sync (optimized)
            time.sleep(0.05)
            
            return True
            
        except FileNotFoundError:
            print("Error: .cursor-rules file not found")
            return False
        except PermissionError:
            print("Error: Permission denied accessing .cursor-rules file")
            return False
        except UnicodeDecodeError:
            print("Error: Invalid encoding in .cursor-rules file")
            return False
        except Exception as e:
            print(f"Unexpected error during Cursor reload: {e}")
            return False
    
    def switch_context_with_reload(self, user_message: str) -> Dict:
        """
        Switch context and force Cursor to reload rules.
        This is the main method for reliable context switching.
        """
        try:
            # Step 1: Switch context and generate new rules
            result = switch_context_and_prove_it_works(user_message)
            
            if not result.get('success', True):
                return result
            
            # Step 2: Force Cursor to reload the rules
            reload_success = self.force_cursor_reload()
            
            # Step 3: Update tracking
            new_context = result['context']
            new_hash = self.get_file_hash(self.cursor_rules_file)
            
            context_changed = new_context != self.last_context
            file_changed = new_hash != self.last_file_hash
            
            # Step 4: Add reload information to result
            result.update({
                'reload_attempted': True,
                'reload_success': reload_success,
                'context_changed': context_changed,
                'file_changed': file_changed,
                'file_hash': new_hash,
                'timestamp': int(time.time())
            })
            
            # Step 5: Update state
            self.last_context = new_context
            self.last_file_hash = new_hash
            self.context_history.append({
                'context': new_context,
                'message': user_message[:50] + "...",
                'timestamp': int(time.time()),
                'rule_count': result['new_rule_count']
            })
            
            # Keep only last 10 context switches
            if len(self.context_history) > 10:
                self.context_history = self.context_history[-10:]
            
            return result
            
        except ImportError as e:
            return {
                'success': False,
                'error': f"Import error: {e}",
                'reload_attempted': False,
                'reload_success': False,
                'fallback': 'Check utils.system.context.working_context_system module'
            }
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f"File not found: {e}",
                'reload_attempted': False,
                'reload_success': False,
                'fallback': 'Ensure .cursor-rules directory exists'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Context switch failed: {e}",
                'reload_attempted': False,
                'reload_success': False,
                'fallback': 'Try manual context switch'
            }
    
    def verify_context_active(self, expected_context: str) -> Dict:
        """
        Verify that the expected context is actually active.
        This checks the .cursor-rules file content.
        """
        try:
            if not self.cursor_rules_file.exists():
                return {
                    'verified': False,
                    'reason': '.cursor-rules file not found',
                    'fallback': 'Run context switch to generate file'
                }
            
            with open(self.cursor_rules_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check context in header
            context_match = f"# Context: {expected_context}"
            context_found = context_match in content
            
            # Count rules
            rule_count = len([line for line in content.split('\n') if line.startswith('# === ') and line.endswith(' ===')])
            
            return {
                'verified': context_found,
                'expected_context': expected_context,
                'context_found': context_found,
                'rule_count': rule_count,
                'file_size': len(content),
                'file_hash': self.get_file_hash(self.cursor_rules_file)
            }
            
        except FileNotFoundError:
            return {
                'verified': False,
                'reason': '.cursor-rules file not found',
                'fallback': 'Run context switch to generate file'
            }
        except PermissionError:
            return {
                'verified': False,
                'reason': 'Permission denied reading .cursor-rules',
                'fallback': 'Check file permissions'
            }
        except Exception as e:
            return {
                'verified': False,
                'reason': f'Verification failed: {e}',
                'fallback': 'Manual verification required'
            }
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        return {
            'last_context': self.last_context,
            'cursor_rules_exists': self.cursor_rules_file.exists(),
            'cursor_rules_size': self.cursor_rules_file.stat().st_size if self.cursor_rules_file.exists() else 0,
            'last_file_hash': self.last_file_hash,
            'context_history_count': len(self.context_history),
            'recent_contexts': [h['context'] for h in self.context_history[-3:]]
        }

# Global instance for reliable context integration
_context_integration = None

def get_context_integration() -> ReliableContextIntegration:
    """Get global context integration instance."""
    global _context_integration
    if _context_integration is None:
        _context_integration = ReliableContextIntegration()
    return _context_integration

def auto_switch_context_reliable(user_message: str) -> Dict:
    """
    Main entry point for reliable automatic context switching.
    This function should be called whenever context needs to change.
    """
    integration = get_context_integration()
    return integration.switch_context_with_reload(user_message)

def verify_context_working(expected_context: str) -> Dict:
    """
    Verify that context switching is working correctly.
    """
    integration = get_context_integration()
    return integration.verify_context_active(expected_context)

def main():
    """Test the reliable context integration system."""
    print("Testing Reliable Context Integration System...")
    
    integration = ReliableContextIntegration()
    
    # Test context switches
    test_cases = [
        "@docs Update the documentation system",
        "@code Implement new features",
        "@debug Fix the system issues"
    ]
    
    for message in test_cases:
        print(f"\n--- Testing: {message} ---")
        
        # Switch context
        result = integration.switch_context_with_reload(message)
        
        if result.get('success', True):
            print(f"Context: {result['context']}")
            print(f"Rules: {result['new_rule_count']}")
            print(f"Reload Success: {result['reload_success']}")
            print(f"File Changed: {result['file_changed']}")
            
            # Verify context is active
            verification = integration.verify_context_active(result['context'])
            print(f"Verification: {verification['verified']}")
            print(f"Rule Count Verified: {verification['rule_count']}")
            
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")
    
    # System status
    status = integration.get_system_status()
    print(f"\nSystem Status:")
    print(f"Last Context: {status['last_context']}")
    print(f"Rules File Exists: {status['cursor_rules_exists']}")
    print(f"Rules File Size: {status['cursor_rules_size']} bytes")
    print(f"Recent Contexts: {status['recent_contexts']}")

if __name__ == "__main__":
    main()