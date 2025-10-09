#!/usr/bin/env python3
"""
Cursor Auto-Startup Module
==========================

Provides automatic initialization functionality for Cursor AI integration.
This module handles the startup sequence for Cursor integration tracking
and ensures proper connection to the universal agent tracking system.

Created: 2024
Purpose: Automatic Cursor AI integration initialization
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global initialization state
_initialization_state = {
    'initialized': False,
    'hook_instance': None,
    'initialization_time': None,
    'error_count': 0,
    'last_error': None
}

def auto_initialize_cursor_integration() -> bool:
    """
    Automatically initialize Cursor AI integration with universal tracking.
    
    This function:
    1. Checks if integration is already initialized
    2. Creates and starts the Cursor integration hook
    3. Registers with the universal agent tracker
    4. Starts monitoring for rule activations and context switches
    5. Handles errors gracefully with fallback mechanisms
    
    Returns:
        bool: True if initialization successful, False otherwise
        
    Example:
        >>> from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration
        >>> success = auto_initialize_cursor_integration()
        >>> print(f"Integration started: {success}")
        Integration started: True
    """
    
    # Check if already initialized
    if _initialization_state['initialized']:
        logger.info("Cursor integration already initialized")
        return True
    
    try:
        logger.info("Starting Cursor AI integration auto-initialization...")
        
        # Import the cursor integration hook
        from utils.integration.cursor_integration_hook import get_cursor_hook, start_cursor_tracking
        
        # Initialize the hook
        hook = get_cursor_hook()
        
        # Start tracking in a separate thread to avoid blocking
        tracking_complete = threading.Event()
        
        def start_tracking_async():
            try:
                start_cursor_tracking()
                logger.info("Cursor tracking started successfully")
                tracking_complete.set()  # Signal completion
            except Exception as e:
                logger.error("Error starting cursor tracking: %s", e)
                _initialization_state['error_count'] += 1
                _initialization_state['last_error'] = str(e)
                tracking_complete.set()  # Signal completion even on error
        
        # Start tracking in background thread
        tracking_thread = threading.Thread(target=start_tracking_async, daemon=True)
        tracking_thread.start()
        
        # Wait briefly for tracking to start (with timeout)
        tracking_complete.wait(timeout=2.0)  # Wait up to 2 seconds
        
        # Update initialization state
        _initialization_state.update({
            'initialized': True,
            'hook_instance': hook,
            'initialization_time': datetime.now(),
            'error_count': 0,
            'last_error': None
        })
        
        logger.info("Cursor AI integration auto-initialization completed successfully")
        return True
        
    except ImportError as e:
        logger.warning("Cursor integration dependencies not available: %s", e)
        _initialization_state['error_count'] += 1
        _initialization_state['last_error'] = f"ImportError: {e}"
        return False
        
    except Exception as e:
        logger.error("Failed to auto-initialize Cursor integration: %s", e)
        _initialization_state['error_count'] += 1
        _initialization_state['last_error'] = str(e)
        return False

def get_initialization_status() -> Dict[str, Any]:
    """
    Get the current initialization status of Cursor integration.
    
    Returns:
        Dict containing initialization state information
        
    Example:
        >>> status = get_initialization_status()
        >>> print(f"Initialized: {status['initialized']}")
        Initialized: True
    """
    return {
        'initialized': _initialization_state['initialized'],
        'initialization_time': _initialization_state['initialization_time'].isoformat() if _initialization_state['initialization_time'] else None,
        'error_count': _initialization_state['error_count'],
        'last_error': _initialization_state['last_error'],
        'hook_available': _initialization_state['hook_instance'] is not None
    }

def force_reinitialize() -> bool:
    """
    Force re-initialization of Cursor integration.
    
    This will reset the initialization state and attempt to initialize again,
    even if it was previously initialized.
    
    Returns:
        bool: True if re-initialization successful, False otherwise
    """
    
    logger.info("Forcing Cursor integration re-initialization...")
    
    # Reset initialization state
    _initialization_state.update({
        'initialized': False,
        'hook_instance': None,
        'initialization_time': None,
        'error_count': 0,
        'last_error': None
    })
    
    # Attempt re-initialization
    return auto_initialize_cursor_integration()

def shutdown_cursor_integration():
    """
    Shutdown Cursor integration gracefully.
    
    This function stops all monitoring and cleans up resources.
    """
    
    try:
        if _initialization_state['hook_instance']:
            # Import stop function
            from utils.integration.cursor_integration_hook import stop_cursor_tracking
            
            # Stop tracking
            stop_cursor_tracking()
            logger.info("Cursor integration shutdown completed")
        
        # Reset state
        _initialization_state.update({
            'initialized': False,
            'hook_instance': None,
            'initialization_time': None
        })
        
    except Exception as e:
        logger.error("Error during Cursor integration shutdown: %s", e)

def is_cursor_integration_healthy() -> bool:
    """
    Check if Cursor integration is healthy and functioning.
    
    Returns:
        bool: True if integration is healthy, False otherwise
    """
    if not _initialization_state['initialized']:
        return False
    
    if _initialization_state['error_count'] > 5:
        logger.warning("Cursor integration has high error count")
        return False
    
    if _initialization_state['hook_instance'] is None:
        return False
    
    try:
        # Try to get status from hook
        status = _initialization_state['hook_instance'].get_session_status()
        return status.get('monitoring_active', False)
    except Exception:
        return False

def get_cursor_hook_instance():
    """
    Get the current Cursor hook instance if available.
    
    Returns:
        CursorIntegrationHook instance or None if not initialized
    """
    return _initialization_state.get('hook_instance')

# Convenience function for testing
def test_initialization():
    """
    Test the initialization process and print results.
    
    This function is useful for debugging and verification.
    """
    print("Testing Cursor Auto-Startup...")
    
    # Test initialization
    success = auto_initialize_cursor_integration()
    print(f"Initialization success: {success}")
    
    # Get status
    status = get_initialization_status()
    print(f"Status: {status}")
    
    # Check health
    healthy = is_cursor_integration_healthy()
    print(f"Health check: {healthy}")
    
    # Wait a moment for background processes
    time.sleep(2)
    
    # Get hook status if available
    hook = get_cursor_hook_instance()
    if hook:
        hook_status = hook.get_session_status()
        print(f"Hook status: {hook_status}")
    
    print("Test completed")

if __name__ == "__main__":
    # Run test if executed directly
    test_initialization()
