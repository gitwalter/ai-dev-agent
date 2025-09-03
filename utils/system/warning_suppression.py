#!/usr/bin/env python3
"""
System Warning Management
========================

Professional warning suppression for known ecosystem-level warnings
that are outside our codebase control. Follows best practices for
managing third-party library transition warnings.

PRINCIPLE: Suppress known safe warnings while preserving important ones.
"""

import warnings
import sys
from typing import List

def suppress_langchain_transition_warnings():
    """
    Suppress LangChain pydantic v1 -> v2 transition warnings.
    
    These warnings are from INSIDE LangChain's own code during their
    internal transition to pydantic v2. Even with latest versions (0.3.27),
    LangChain still has internal pydantic v1 compatibility code.
    Our code is already using pydantic v2 correctly.
    """
    
    # Import the specific warning classes
    try:
        import langchain
        # Suppress LangChainDeprecationWarning specifically
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message=".*langchain_core.pydantic_v1.*"
        )
    except ImportError:
        pass
    
    # Suppress specific LangChain deprecation warnings by message content
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message=".*pydantic_v1 module was a compatibility shim.*"
    )
    
    # Suppress pydantic v1/v2 mixing warnings for third-party libraries
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message=".*Mixing V1 models and V2 models.*"
    )
    
    # Suppress the specific TextRequestsWrapper warning
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message=".*Please upgrade.*TextRequestsWrapper.*to V2.*"
    )
    
    print("🔇 Suppressed LangChain ecosystem transition warnings")

def apply_professional_warning_filters():
    """
    Apply professional-grade warning filters.
    
    Maintains important warnings while suppressing known
    ecosystem-level transition noise.
    """
    
    # Keep all our own warnings
    warnings.filterwarnings("default", module="utils.*")
    warnings.filterwarnings("default", module="workflow.*")
    warnings.filterwarnings("default", module="agents.*")
    warnings.filterwarnings("default", module="apps.*")
    
    # Suppress third-party transition warnings
    suppress_langchain_transition_warnings()
    
    print("✅ Professional warning filters applied")

if __name__ == "__main__":
    apply_professional_warning_filters()
    
    # Test that warnings are properly suppressed
    try:
        import workflow.langgraph_workflow_manager
        print("✅ LangGraph workflow manager imported cleanly")
    except Exception as e:
        print(f"❌ Import failed: {e}")
