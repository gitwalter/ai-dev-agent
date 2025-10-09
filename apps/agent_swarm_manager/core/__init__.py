"""
Core Infrastructure Components
=============================

Core components for the modular agent swarm management application:
- Event Bus: Inter-module communication
- App State: Centralized state management  
- Session Manager: Session lifecycle management

Author: AI Development Agent
Created: 2025-01-02
"""

from .event_bus import EventBus
from .app_state import AppState
from .session_manager import SessionManager

__all__ = ['EventBus', 'AppState', 'SessionManager']
