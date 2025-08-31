#!/usr/bin/env python3
"""
Demo script for Intelligent Context-Aware Rule System
Implementation of US-E0-010
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.rule_system.intelligent_context_detector import detect_and_apply_context


def main():
    """Demo the intelligent context detection system."""
    
    print("🚀 **Intelligent Context-Aware Rule System Demo**")
    print("Implementation of US-E0-010\n")
    
    # Test scenarios
    scenarios = [
        ("@code Let's implement authentication", ["src/auth.py"], "src/"),
        ("@debug The tests are failing", ["test_auth.py"], "tests/"),
        ("@agile Update sprint backlog", ["sprint.md"], "docs/agile/"),
        ("Help me with the project", [], "")
    ]
    
    for i, (message, files, directory) in enumerate(scenarios, 1):
        print(f"**Test {i}:** {message}")
        context_result, rule_result = detect_and_apply_context(message, files, directory)
        print(f"Future Agent: {context_result.agent_future}\n")
    
    print("✅ **Demo Complete!** System ready for deployment.")


if __name__ == "__main__":
    main()
