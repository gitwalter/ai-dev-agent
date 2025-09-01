#!/usr/bin/env python3
"""
Context-Aware Agent Factory

Revolutionary system for creating optimal agents based on context keywords and scope.
Integrates Foundation-Practical Onion Architecture with intelligent rule optimization.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Set
from enum import Enum


class AgentContext(Enum):
    """All supported agent contexts with their specialized purposes."""
    CODE = "code"
    DEBUG = "debug"
    TEST = "test"
    DOCS = "docs"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    AGILE = "agile"
    DEFAULT = "default"


class ContextScope(Enum):
    """Context scope sizes for optimal rule application."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class ContextConfiguration:
    """Configuration for a specific agent context and scope."""
    context: AgentContext
    scope: ContextScope
    active_rules: List[str]
    excluded_rules: List[str]
    optimization_level: str
    foundation_layers: List[str]
    practical_layers: List[str]
    speed_improvement: str


class ContextAwareAgentFactory:
    """
    Factory for creating optimally configured agents based on context and scope.
    
    Implements the unified context-aware system that actualizes our vision of
    intelligent rule application and Foundation-Practical integration.
    """
    
    def __init__(self):
        self.context_configurations = self._initialize_configurations()
        self.foundation_layers = self._get_foundation_layers()
        self.practical_layers = self._get_practical_layers()
    
    def _initialize_configurations(self) -> Dict[tuple, ContextConfiguration]:
        """Initialize all context-scope combinations with optimal configurations."""
        
        configs = {}
        
        # @code Context Configurations
        configs[(AgentContext.CODE, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.CODE,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "clean_code_principles",
                "basic_testing",
                "error_handling_essential"
            ],
            excluded_rules=[
                "agile_artifacts_maintenance",
                "complex_documentation",
                "architecture_validation",
                "comprehensive_testing"
            ],
            optimization_level="maximum",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["development_implementation"],
            speed_improvement="90%"
        )
        
        configs[(AgentContext.CODE, ContextScope.MEDIUM)] = ContextConfiguration(
            context=AgentContext.CODE,
            scope=ContextScope.MEDIUM,
            active_rules=[
                "safety_first_principle",
                "clean_code_principles", 
                "test_driven_development",
                "design_patterns",
                "performance_optimization",
                "documentation_essential"
            ],
            excluded_rules=[
                "agile_artifacts_comprehensive",
                "architecture_deep_validation",
                "philosophical_documentation"
            ],
            optimization_level="high",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["software_architecture", "development_implementation", "quality_testing"],
            speed_improvement="60%"
        )
        
        configs[(AgentContext.CODE, ContextScope.LARGE)] = ContextConfiguration(
            context=AgentContext.CODE,
            scope=ContextScope.LARGE,
            active_rules=[
                "all_development_rules",
                "architecture_validation",
                "comprehensive_testing",
                "documentation_complete",
                "agile_integration"
            ],
            excluded_rules=[],
            optimization_level="standard",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["software_architecture", "development_implementation", 
                           "operations_infrastructure", "quality_testing", "user_experience"],
            speed_improvement="20%"
        )
        
        # @debug Context Configurations
        configs[(AgentContext.DEBUG, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.DEBUG,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "error_handling_no_silent_errors",
                "scientific_verification_evidence_based",
                "systematic_problem_solving"
            ],
            excluded_rules=[
                "agile_artifacts_maintenance",
                "documentation_live_updates",
                "complex_architecture_validation",
                "philosophical_foundations"
            ],
            optimization_level="maximum",
            foundation_layers=["universal_foundation"],
            practical_layers=["development_implementation"],
            speed_improvement="90%"
        )
        
        configs[(AgentContext.DEBUG, ContextScope.MEDIUM)] = ContextConfiguration(
            context=AgentContext.DEBUG,
            scope=ContextScope.MEDIUM,
            active_rules=[
                "safety_first_principle",
                "no_failing_tests_rule",
                "development_core_principles",
                "performance_monitoring_optimization",
                "error_handling_comprehensive"
            ],
            excluded_rules=[
                "documentation_comprehensive",
                "agile_artifacts_full"
            ],
            optimization_level="high",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["development_implementation", "quality_testing"],
            speed_improvement="60%"
        )
        
        # @test Context Configurations
        configs[(AgentContext.TEST, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.TEST,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "test_driven_development",
                "no_failing_tests_rule",
                "test_coverage_basic"
            ],
            excluded_rules=[
                "agile_artifacts_maintenance",
                "documentation_comprehensive",
                "architecture_validation"
            ],
            optimization_level="maximum",
            foundation_layers=["universal_foundation"],
            practical_layers=["quality_testing"],
            speed_improvement="85%"
        )
        
        # @docs Context Configurations  
        configs[(AgentContext.DOCS, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.DOCS,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "documentation_excellence",
                "clear_communication",
                "user_experience_basic"
            ],
            excluded_rules=[
                "agile_artifacts_maintenance",
                "testing_comprehensive",
                "architecture_validation"
            ],
            optimization_level="maximum",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["user_experience"],
            speed_improvement="80%"
        )
        
        # @architecture Context Configurations
        configs[(AgentContext.ARCHITECTURE, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.ARCHITECTURE,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "solid_principles",
                "design_patterns",
                "architectural_consistency"
            ],
            excluded_rules=[
                "agile_artifacts_maintenance",
                "documentation_comprehensive",
                "testing_full_suite"
            ],
            optimization_level="high",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["software_architecture"],
            speed_improvement="70%"
        )
        
        # @security Context Configurations
        configs[(AgentContext.SECURITY, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.SECURITY,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "security_vulnerability_assessment",
                "ethical_ai_protection",
                "secure_coding_practices"
            ],
            excluded_rules=[
                "agile_artifacts_maintenance",
                "documentation_comprehensive",
                "architecture_non_security"
            ],
            optimization_level="high",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["security_infrastructure"],
            speed_improvement="75%"
        )
        
        # @agile Context Configurations
        configs[(AgentContext.AGILE, ContextScope.SMALL)] = ContextConfiguration(
            context=AgentContext.AGILE,
            scope=ContextScope.SMALL,
            active_rules=[
                "safety_first_principle",
                "agile_artifacts_maintenance",
                "user_story_management",
                "sprint_management_basic"
            ],
            excluded_rules=[
                "technical_implementation",
                "architecture_validation",
                "testing_comprehensive"
            ],
            optimization_level="high",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["project_management"],
            speed_improvement="65%"
        )
        
        return configs
    
    def _get_foundation_layers(self) -> Dict[str, Dict[str, str]]:
        """Get Foundation-Practical Onion Architecture foundation layers."""
        return {
            "universal_foundation": {
                "divine": "Create with infinite love and wisdom",
                "scientific": "Evidence-based methodology and validation",
                "ethical": "Absolute harm prevention and benefit maximization"
            },
            "philosophical_foundation": {
                "ontology": "Clean abstractions and proper categorization",
                "epistemology": "Testable knowledge and verifiable claims",
                "logic": "SOLID principles and systematic reasoning"
            }
        }
    
    def _get_practical_layers(self) -> Dict[str, Dict[str, str]]:
        """Get Foundation-Practical Onion Architecture practical layers."""
        return {
            "software_architecture": {
                "patterns": "Design patterns and architectural principles",
                "structure": "Clean architecture and modular design",
                "scalability": "Performance and scalability considerations"
            },
            "development_implementation": {
                "coding": "Clean code and best practices",
                "testing": "TDD and comprehensive testing",
                "refactoring": "Continuous improvement and optimization"
            },
            "operations_infrastructure": {
                "deployment": "CI/CD and deployment automation",
                "monitoring": "System monitoring and observability",
                "maintenance": "System maintenance and support"
            },
            "quality_testing": {
                "validation": "Comprehensive validation strategies",
                "coverage": "Test coverage and quality metrics",
                "automation": "Automated testing and validation"
            },
            "user_experience": {
                "interface": "User interface design and usability",
                "documentation": "User documentation and guides",
                "accessibility": "Accessibility and inclusivity"
            },
            "security_infrastructure": {
                "protection": "Security measures and protection",
                "compliance": "Compliance and regulatory requirements",
                "auditing": "Security auditing and monitoring"
            }
        }
    
    def detect_context_from_message(self, user_message: str) -> tuple[AgentContext, ContextScope]:
        """
        Detect agent context and scope from user message.
        
        Args:
            user_message: User's input message
            
        Returns:
            Tuple of (AgentContext, ContextScope)
        """
        message_lower = user_message.lower()
        
        # Detect explicit context keywords
        context = AgentContext.DEFAULT
        scope = ContextScope.MEDIUM  # Default
        
        # Context detection
        if "@code" in message_lower or "implement" in message_lower or "develop" in message_lower:
            context = AgentContext.CODE
        elif "@debug" in message_lower or "fix" in message_lower or "troubleshoot" in message_lower:
            context = AgentContext.DEBUG
        elif "@test" in message_lower or "testing" in message_lower or "validate" in message_lower:
            context = AgentContext.TEST
        elif "@docs" in message_lower or "document" in message_lower or "readme" in message_lower:
            context = AgentContext.DOCS
        elif "@architecture" in message_lower or "design" in message_lower or "structure" in message_lower:
            context = AgentContext.ARCHITECTURE
        elif "@security" in message_lower or "secure" in message_lower or "vulnerability" in message_lower:
            context = AgentContext.SECURITY
        elif "@agile" in message_lower or "sprint" in message_lower or "story" in message_lower:
            context = AgentContext.AGILE
        
        # Scope detection
        if "-small" in message_lower or "single" in message_lower or "simple" in message_lower:
            scope = ContextScope.SMALL
        elif "-large" in message_lower or "system" in message_lower or "comprehensive" in message_lower:
            scope = ContextScope.LARGE
        elif "-medium" in message_lower:
            scope = ContextScope.MEDIUM
        
        return context, scope
    
    def get_agent_configuration(self, context: AgentContext, scope: ContextScope) -> ContextConfiguration:
        """
        Get optimized configuration for specific context and scope.
        
        Args:
            context: Agent context type
            scope: Context scope size
            
        Returns:
            ContextConfiguration for the specified context and scope
        """
        config_key = (context, scope)
        
        if config_key in self.context_configurations:
            return self.context_configurations[config_key]
        
        # Fallback to medium scope if specific combination not found
        fallback_key = (context, ContextScope.MEDIUM)
        if fallback_key in self.context_configurations:
            return self.context_configurations[fallback_key]
        
        # Ultimate fallback to default configuration
        return self._get_default_configuration()
    
    def _get_default_configuration(self) -> ContextConfiguration:
        """Get default configuration for unknown contexts."""
        return ContextConfiguration(
            context=AgentContext.DEFAULT,
            scope=ContextScope.MEDIUM,
            active_rules=[
                "safety_first_principle",
                "development_core_principles",
                "basic_testing",
                "essential_documentation"
            ],
            excluded_rules=[],
            optimization_level="standard",
            foundation_layers=["universal_foundation", "philosophical_foundation"],
            practical_layers=["development_implementation", "quality_testing"],
            speed_improvement="30%"
        )
    
    def generate_agent_summary(self, config: ContextConfiguration) -> str:
        """Generate a summary of the agent configuration."""
        return f"""
🤖 **{config.context.value.title()} Agent - {config.scope.value.title()} Context**

**Foundation Layers**: {', '.join(config.foundation_layers)}
**Practical Layers**: {', '.join(config.practical_layers)}
**Speed Optimization**: {config.speed_improvement} faster execution
**Active Rules**: {len(config.active_rules)} rules loaded
**Excluded Rules**: {len(config.excluded_rules)} rules suspended

**Optimization**: {config.optimization_level.title()} efficiency mode
"""


# Usage example for current terminal issue
if __name__ == "__main__":
    factory = ContextAwareAgentFactory()
    
    # Example: @debug-small context for terminal hanging issue
    debug_context, debug_scope = AgentContext.DEBUG, ContextScope.SMALL
    config = factory.get_agent_configuration(debug_context, debug_scope)
    
    print("Current Context Configuration:")
    print(factory.generate_agent_summary(config))
    
    print("\nActive Rules for Terminal Issue:")
    for rule in config.active_rules:
        print(f"  ✅ {rule}")
    
    print("\nExcluded Rules (for maximum efficiency):")
    for rule in config.excluded_rules:
        print(f"  ⏸️ {rule}")
