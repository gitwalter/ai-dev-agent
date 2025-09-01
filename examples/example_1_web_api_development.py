#!/usr/bin/env python3
"""
Example 1: Web API Development with Ontological Mode Switching
==============================================================

Practical demonstration of using different ontological frameworks
during real web API development workflow.

Shows clean perspective switching between:
- @architecture: Designing the API structure
- @engineering: Implementing the code
- @debug: Fixing issues that arise

This example builds a simple user management API.
"""

import sys
import os
from pathlib import Path

# Add utils to path for ontological framework system
utils_path = Path(__file__).parent.parent / "utils"
sys.path.append(str(utils_path))

from context.ontological_framework_system import OntologicalSwitchingSystem


class WebAPIExample:
    """
    Web API development example showing ontological mode switching.
    """
    
    def __init__(self):
        self.ontology_system = OntologicalSwitchingSystem()
        self.development_log = []
        self.api_components = {}
    
    def log_step(self, step: str, framework: str, action: str, result: str):
        """Log development steps with ontological framework context."""
        entry = {
            "step": step,
            "framework": framework,
            "action": action,
            "result": result,
            "validation": self.ontology_system.validate_expression(action)
        }
        self.development_log.append(entry)
        
        # Show real-time validation
        validation = entry["validation"]["validation"]
        contamination = entry["validation"]["contamination"]
        
        status = "✅" if validation["valid"] and not contamination["contamination_detected"] else "❌"
        print(f"{status} [{framework}] {action}")
        
        if not validation["valid"]:
            print(f"   ⚠️ Invalid for {framework}: {validation['reason']}")
        if contamination["contamination_detected"]:
            print(f"   ⚠️ Ontological contamination: {contamination['foreign_concepts']}")
        
        print(f"   Result: {result}\n")
    
    def run_development_workflow(self):
        """Run complete web API development workflow with mode switching."""
        
        print("🚀 WEB API DEVELOPMENT WORKFLOW")
        print("=" * 45)
        print("Building user management API with clean ontological switching\n")
        
        # Phase 1: Architecture Design
        print("📐 PHASE 1: ARCHITECTURAL DESIGN")
        print("-" * 35)
        
        self.ontology_system.switch_perspective("architecture", "Design user management API structure")
        
        self.log_step(
            "1.1", "architecture",
            "Design REST API endpoints for user operations",
            "Defined endpoints: POST /users, GET /users/{id}, PUT /users/{id}, DELETE /users/{id}"
        )
        
        self.log_step(
            "1.2", "architecture", 
            "Model user data structure with validation patterns",
            "User model: {id, email, name, created_at} with email validation pattern"
        )
        
        self.log_step(
            "1.3", "architecture",
            "Design authentication pattern for API security", 
            "JWT token authentication with role-based access control"
        )
        
        # Try invalid expression in architecture mode
        self.log_step(
            "1.4", "architecture",
            "Let's quickly implement the user validation function",  # Invalid in architecture
            "ERROR: Implementation details not valid in architecture mode"
        )
        
        # Phase 2: Engineering Implementation  
        print("\n🔧 PHASE 2: ENGINEERING IMPLEMENTATION")
        print("-" * 40)
        
        self.ontology_system.switch_perspective("engineering", "Implement the designed API")
        
        self.log_step(
            "2.1", "engineering",
            "Implement user model class with validation",
            "Created User class with email validation and data serialization"
        )
        
        self.log_step(
            "2.2", "engineering",
            "Build REST endpoints using Flask framework",
            "Implemented all CRUD endpoints with proper HTTP status codes"
        )
        
        self.log_step(
            "2.3", "engineering", 
            "Write comprehensive unit tests for all endpoints",
            "Created test suite: 15 tests covering all endpoints and edge cases"
        )
        
        # Try invalid expression in engineering mode
        self.log_step(
            "2.4", "engineering",
            "Consider the long-term architectural implications",  # Invalid in engineering
            "ERROR: Architectural concerns not valid in implementation mode"
        )
        
        # Phase 3: Debug Issues
        print("\n🐛 PHASE 3: DEBUGGING ISSUES")
        print("-" * 32)
        
        self.ontology_system.switch_perspective("debug", "Fix email validation failing in tests")
        
        self.log_step(
            "3.1", "debug",
            "Reproduce the email validation test failure",
            "Confirmed: Email regex fails for valid emails with plus signs"
        )
        
        self.log_step(
            "3.2", "debug",
            "Isolate the root cause in validation logic",
            "Root cause: Regex pattern doesn't include '+' character in email validation"
        )
        
        self.log_step(
            "3.3", "debug",
            "Verify fix resolves issue without breaking other cases",
            "Fix verified: Updated regex passes all email validation tests"
        )
        
        # Try invalid expression in debug mode
        self.log_step(
            "3.4", "debug",
            "Ship this fix quickly to production",  # Invalid in debug mode
            "ERROR: Shipping decisions not valid in debug mode - need verification first"
        )
        
        # Phase 4: Back to Engineering for Deployment
        print("\n🚀 PHASE 4: DEPLOYMENT PREPARATION")
        print("-" * 37)
        
        self.ontology_system.switch_perspective("engineering", "Prepare API for production deployment")
        
        self.log_step(
            "4.1", "engineering",
            "Deploy the validated fix to production environment",
            "Deployment successful: API running with fixed email validation"
        )
        
        self.log_step(
            "4.2", "engineering", 
            "Monitor API performance and error rates",
            "Monitoring active: 99.9% uptime, average response time 120ms"
        )
        
        print("\n📊 DEVELOPMENT WORKFLOW SUMMARY")
        print("=" * 40)
        
        # Analyze the workflow
        framework_usage = {}
        valid_expressions = 0
        invalid_expressions = 0
        contaminations = 0
        
        for entry in self.development_log:
            framework = entry["framework"]
            framework_usage[framework] = framework_usage.get(framework, 0) + 1
            
            if entry["validation"]["validation"]["valid"]:
                valid_expressions += 1
            else:
                invalid_expressions += 1
                
            if entry["validation"]["contamination"]["contamination_detected"]:
                contaminations += 1
        
        print(f"Total Steps: {len(self.development_log)}")
        print(f"Framework Usage: {framework_usage}")
        print(f"Valid Expressions: {valid_expressions}")
        print(f"Invalid Expressions: {invalid_expressions}")
        print(f"Ontological Contaminations: {contaminations}")
        
        print(f"\n✅ Web API successfully developed using clean ontological switching!")
        print("   Each phase used appropriate perspective with proper validation.")
        
        return {
            "workflow_completed": True,
            "total_steps": len(self.development_log),
            "framework_usage": framework_usage,
            "validation_results": {
                "valid_expressions": valid_expressions,
                "invalid_expressions": invalid_expressions,
                "contaminations": contaminations
            }
        }


def main():
    """Run the web API development example."""
    
    print("🌟 PRACTICAL EXAMPLE 1: WEB API DEVELOPMENT")
    print("=" * 50)
    print("Demonstrating ontological mode switching in real development workflow\n")
    
    example = WebAPIExample()
    results = example.run_development_workflow()
    
    print(f"\n💡 KEY INSIGHTS:")
    print("   🔧 Engineering mode: Focus on implementation and testing")
    print("   📐 Architecture mode: Focus on design patterns and structure")
    print("   🐛 Debug mode: Focus on systematic problem solving")
    print("   ⚠️ Invalid expressions rejected by ontological validation")
    print("   🧹 Clean perspective switching prevents confused thinking")
    
    print(f"\n🎯 DEVELOPER TAKEAWAY:")
    print("   Use @architecture for design decisions")
    print("   Use @engineering for implementation work") 
    print("   Use @debug for systematic problem solving")
    print("   Each mode has distinct language and focus - don't mix them!")
    
    return results


if __name__ == "__main__":
    main()
