#!/usr/bin/env python3
"""
Operating Mode System
====================

Implements keyword-based operating modes that activate specific
capabilities and rule sets for different development contexts.

Modes:
- @engineering - Pure software engineering focus
- @debug - Debugging and problem-solving mode
- @test - Testing and quality assurance mode
- @docs - Documentation and knowledge transfer mode
- @architecture - System design and architecture mode
- @performance - Performance optimization mode
- @agile - Project management and agile workflow mode

Author: AI-Dev-Agent Engineering Team
License: Open Source
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OperatingMode:
    """Operating mode configuration."""
    name: str
    keywords: List[str]
    description: str
    capabilities: List[str]
    rules: List[str]
    focus_level: str  # "narrow", "medium", "broad"
    efficiency_boost: float

class OperatingModeSystem:
    """
    Manages ontological perspective switching with clean separation.
    
    Each mode is a complete ontological framework with distinct:
    - Language system (concepts, expressions, reasoning patterns)
    - Truth criteria and meaning structures
    - Conceptual boundaries and world view
    
    Architecture:
    - Silent Foundation: Unspeakable guidance (Wittgensteinian separation)
    - Core Layer (ALWAYS ACTIVE): Safety, ethics, quality principles  
    - Technical Layer: Mode-specific ontological frameworks
    - Meta-Control Layer: Clean ontological transitions
    
    No ontological mixing - complete perspective switches only.
    """
    
    def __init__(self):
        # Core layer - ALWAYS active regardless of mode
        self.core_principles = {
            "safety_first": True,
            "no_harm": True, 
            "scientific_evidence": True,
            "user_service": True,
            "quality_excellence": True
        }
        
        # Silent foundation - Wittgenstein: "Whereof one cannot speak, thereof one must be silent"
        # This exists but is NEVER mentioned in technical operations
        # Perfect separation: the unspeakable guides but never mixes with speakable
        self._silent_foundation = {
            # These exist but are never explicitly referenced in technical work
            # They influence decisions but remain in the realm of the unspeakable
        }
        
        # Technical layer - mode-specific capabilities
        self.modes = self._initialize_modes()
        self.current_mode = "engineering"
        self.mode_history = []
        self.technical_capabilities_active = set()
        
        # Meta-control layer - manages layer interactions
        self.meta_control = {
            "core_override_enabled": True,
            "layer_separation_enforced": True,
            "technical_mode_active": self.current_mode,
            "background_monitoring": True
        }
        
        print("🏗️ Operating Mode System initialized with layered architecture")
        print(f"   Silent foundation: INVISIBLE (spiritual wisdom guides all)")
        print(f"   Core layer: ALWAYS ACTIVE (safety, ethics, quality)")
        print(f"   Technical layer: {self.current_mode}")
        print(f"   Meta-control: Layer separation enforced")
    
    def _initialize_modes(self) -> Dict[str, OperatingMode]:
        """Initialize all available operating modes."""
        
        # Single focus modes
        single_modes = {
            "engineering": OperatingMode(
                name="Software Engineering",
                keywords=["@engineering", "@code", "@dev", "@build"],
                description="Pure software engineering and development focus",
                capabilities=[
                    "code_generation",
                    "algorithm_design", 
                    "code_review",
                    "refactoring",
                    "design_patterns",
                    "clean_code"
                ],
                rules=[
                    "clean_code_principles",
                    "solid_principles",
                    "dry_principle",
                    "kiss_principle",
                    "separation_of_concerns"
                ],
                focus_level="narrow",
                efficiency_boost=0.9
            ),
            
            "debug": OperatingMode(
                name="Debug & Problem Solving",
                keywords=["@debug", "@fix", "@troubleshoot", "@solve"],
                description="Systematic debugging and problem resolution",
                capabilities=[
                    "error_analysis",
                    "root_cause_analysis",
                    "systematic_debugging",
                    "log_analysis",
                    "performance_profiling"
                ],
                rules=[
                    "systematic_problem_solving",
                    "no_silent_errors",
                    "evidence_based_debugging",
                    "reproduction_steps"
                ],
                focus_level="narrow",
                efficiency_boost=0.85
            ),
            
            "test": OperatingMode(
                name="Testing & Quality Assurance",
                keywords=["@test", "@qa", "@quality", "@validate"],
                description="Testing, validation, and quality assurance",
                capabilities=[
                    "test_design",
                    "test_automation",
                    "quality_metrics",
                    "coverage_analysis",
                    "test_data_generation"
                ],
                rules=[
                    "test_driven_development",
                    "comprehensive_testing",
                    "quality_gates",
                    "no_failing_tests"
                ],
                focus_level="medium",
                efficiency_boost=0.8
            ),
            
            "docs": OperatingMode(
                name="Documentation & Knowledge Transfer",
                keywords=["@docs", "@document", "@explain", "@guide"],
                description="Documentation creation and knowledge sharing",
                capabilities=[
                    "technical_writing",
                    "knowledge_extraction",
                    "tutorial_creation",
                    "api_documentation",
                    "user_guides"
                ],
                rules=[
                    "clear_documentation",
                    "comprehensive_examples",
                    "user_focused_content",
                    "live_documentation_updates"
                ],
                focus_level="medium",
                efficiency_boost=0.7
            ),
            
            "architecture": OperatingMode(
                name="System Architecture & Design",
                keywords=["@architecture", "@design", "@system", "@structure"],
                description="System architecture and high-level design",
                capabilities=[
                    "architectural_patterns",
                    "system_design",
                    "scalability_planning",
                    "integration_design",
                    "technology_selection"
                ],
                rules=[
                    "architectural_principles",
                    "scalability_considerations",
                    "maintainability_focus",
                    "design_documentation"
                ],
                focus_level="broad",
                efficiency_boost=0.6
            ),
            
            "performance": OperatingMode(
                name="Performance Optimization",
                keywords=["@performance", "@optimize", "@speed", "@efficiency"],
                description="Performance analysis and optimization",
                capabilities=[
                    "performance_analysis",
                    "bottleneck_identification",
                    "optimization_strategies",
                    "benchmarking",
                    "resource_optimization"
                ],
                rules=[
                    "measurement_based_optimization",
                    "performance_monitoring",
                    "benchmark_validation",
                    "profiling_before_optimization"
                ],
                focus_level="narrow",
                efficiency_boost=0.85
            ),
            
            "agile": OperatingMode(
                name="Agile Project Management",
                keywords=["@agile", "@sprint", "@project", "@manage"],
                description="Agile project management and workflow",
                capabilities=[
                    "sprint_planning",
                    "user_story_management",
                    "progress_tracking",
                    "stakeholder_communication",
                    "agile_artifacts"
                ],
                rules=[
                    "agile_principles",
                    "transparent_communication",
                    "iterative_development",
                    "continuous_improvement"
                ],
                focus_level="broad",
                efficiency_boost=0.6
            )
        }
        
        # Hybrid modes for real developer scenarios
        hybrid_modes = {
            "technical_scientific": OperatingMode(
                name="Technical-Scientific Software Engineer",
                keywords=["@tech-sci", "@engineering-research", "@scientific-dev"],
                description="Rigorous engineering with scientific methodology and evidence-based development",
                capabilities=[
                    "scientific_method_application",
                    "evidence_based_development", 
                    "rigorous_testing",
                    "measurement_driven_decisions",
                    "hypothesis_testing",
                    "research_oriented_coding",
                    "statistical_validation",
                    "experimental_design"
                ],
                rules=[
                    "scientific_evidence_required",
                    "hypothesis_driven_development",
                    "measurement_before_optimization",
                    "peer_review_standards",
                    "reproducible_results"
                ],
                focus_level="medium",
                efficiency_boost=0.85
            ),
            
            "agile_technical": OperatingMode(
                name="Agile Technical Lead",
                keywords=["@agile-tech", "@tech-lead", "@agile-engineering"],
                description="Technical leadership with agile project management and team coordination",
                capabilities=[
                    "technical_leadership",
                    "agile_sprint_planning",
                    "team_coordination",
                    "technical_decision_making",
                    "code_review_management",
                    "architecture_guidance",
                    "stakeholder_communication",
                    "risk_assessment"
                ],
                rules=[
                    "servant_leadership",
                    "technical_excellence_advocacy",
                    "transparent_communication",
                    "iterative_delivery",
                    "team_empowerment"
                ],
                focus_level="broad",
                efficiency_boost=0.75
            ),
            
            "debug_performance": OperatingMode(
                name="Debug & Performance Specialist",
                keywords=["@debug-perf", "@troubleshoot-optimize", "@fix-speed"],
                description="Systematic debugging combined with performance optimization expertise",
                capabilities=[
                    "advanced_debugging",
                    "performance_profiling",
                    "bottleneck_analysis",
                    "memory_optimization",
                    "algorithm_optimization",
                    "system_monitoring",
                    "root_cause_analysis",
                    "performance_testing"
                ],
                rules=[
                    "measure_before_optimize",
                    "systematic_debugging",
                    "performance_benchmarking",
                    "evidence_based_fixes",
                    "holistic_system_view"
                ],
                focus_level="narrow",
                efficiency_boost=0.9
            ),
            
            "fullstack_architect": OperatingMode(
                name="Full-Stack Architect",
                keywords=["@fullstack-arch", "@system-design", "@end-to-end"],
                description="Complete system architecture from frontend to backend to infrastructure",
                capabilities=[
                    "full_stack_development",
                    "system_architecture",
                    "database_design", 
                    "api_design",
                    "frontend_architecture",
                    "infrastructure_planning",
                    "security_architecture",
                    "scalability_design"
                ],
                rules=[
                    "end_to_end_thinking",
                    "scalability_first",
                    "security_by_design",
                    "maintainable_architecture",
                    "technology_appropriate_selection"
                ],
                focus_level="broad",
                efficiency_boost=0.7
            ),
            
            "devops_reliability": OperatingMode(
                name="DevOps Reliability Engineer",
                keywords=["@devops-sre", "@reliability", "@ops-dev"],
                description="Development operations with site reliability engineering practices",
                capabilities=[
                    "infrastructure_as_code",
                    "ci_cd_pipeline_design",
                    "monitoring_and_alerting",
                    "incident_response",
                    "automation_development",
                    "reliability_engineering",
                    "capacity_planning",
                    "disaster_recovery"
                ],
                rules=[
                    "automation_first",
                    "monitoring_everything",
                    "gradual_rollouts",
                    "error_budget_management",
                    "blameless_postmortems"
                ],
                focus_level="medium",
                efficiency_boost=0.8
            ),
            
            "security_developer": OperatingMode(
                name="Security-Focused Developer",
                keywords=["@sec-dev", "@secure-coding", "@security-first"],
                description="Security-first development with threat modeling and secure coding practices",
                capabilities=[
                    "secure_coding_practices",
                    "threat_modeling",
                    "vulnerability_assessment",
                    "security_testing",
                    "cryptography_implementation",
                    "access_control_design",
                    "security_code_review",
                    "compliance_validation"
                ],
                rules=[
                    "security_by_design",
                    "least_privilege_principle",
                    "defense_in_depth",
                    "security_testing_required",
                    "privacy_by_design"
                ],
                focus_level="medium",
                efficiency_boost=0.75
            ),
            
            "data_scientist_engineer": OperatingMode(
                name="Data Scientist Engineer",
                keywords=["@data-eng", "@ml-engineering", "@data-science"],
                description="Data science with software engineering rigor for production ML systems",
                capabilities=[
                    "data_pipeline_engineering",
                    "ml_model_development",
                    "statistical_analysis",
                    "data_validation",
                    "model_deployment",
                    "experiment_tracking",
                    "feature_engineering",
                    "production_ml_systems"
                ],
                rules=[
                    "reproducible_experiments",
                    "data_quality_validation",
                    "model_versioning",
                    "statistical_significance",
                    "production_ready_ml"
                ],
                focus_level="medium",
                efficiency_boost=0.8
            ),
            
            "startup_technical_founder": OperatingMode(
                name="Startup Technical Founder",
                keywords=["@startup-tech", "@founder-dev", "@mvp-architect"],
                description="Rapid MVP development with scalable architecture and business focus",
                capabilities=[
                    "rapid_prototyping",
                    "mvp_development",
                    "business_logic_implementation",
                    "scalable_architecture_planning",
                    "technology_stack_selection",
                    "user_experience_focus",
                    "growth_oriented_development",
                    "resource_optimization"
                ],
                rules=[
                    "speed_to_market",
                    "scalability_planning",
                    "user_feedback_driven",
                    "technical_debt_management",
                    "business_value_focus"
                ],
                focus_level="broad",
                efficiency_boost=0.85
            )
        }
        
        # Combine single and hybrid modes
        all_modes = {**single_modes, **hybrid_modes}
        return all_modes
    
    def detect_mode_from_message(self, message: str) -> str:
        """Detect operating mode from user message."""
        
        message_lower = message.lower()
        
        # Check for explicit mode keywords
        for mode_name, mode in self.modes.items():
            for keyword in mode.keywords:
                if keyword in message_lower:
                    return mode_name
        
        # Fallback to context analysis
        return self._analyze_context_mode(message_lower)
    
    def _analyze_context_mode(self, message: str) -> str:
        """Analyze message context to determine appropriate mode."""
        
        # Context patterns for mode detection
        patterns = {
            "engineering": ["implement", "code", "function", "class", "algorithm"],
            "debug": ["error", "bug", "issue", "problem", "failing", "broken"],
            "test": ["test", "testing", "verify", "validate", "check"],
            "docs": ["document", "explain", "guide", "tutorial", "readme"],
            "architecture": ["design", "architecture", "pattern", "structure"],
            "performance": ["slow", "optimize", "performance", "speed", "efficient"],
            "agile": ["sprint", "story", "backlog", "planning", "progress"]
        }
        
        mode_scores = {}
        for mode, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > 0:
                mode_scores[mode] = score
        
        if mode_scores:
            return max(mode_scores.items(), key=lambda x: x[1])[0]
        
        return "engineering"  # Default fallback
    
    def activate_mode(self, mode_name: str, reason: str = "manual") -> Dict[str, any]:
        """
        Activate specific operating mode with layered architecture.
        
        Core layer remains ALWAYS active.
        Technical layer switches based on mode.
        Meta-control manages the transition.
        """
        
        if mode_name not in self.modes:
            return {"error": f"Unknown mode: {mode_name}"}
        
        # Meta-control: Validate mode transition
        if not self._validate_mode_transition(mode_name):
            return {"error": f"Mode transition blocked by meta-control"}
        
        previous_mode = self.current_mode
        self.current_mode = mode_name
        
        # Technical layer: Update mode-specific capabilities ONLY
        mode = self.modes[mode_name]
        self.technical_capabilities_active = set(mode.capabilities)
        
        # Meta-control: Update layer status
        self.meta_control["technical_mode_active"] = mode_name
        
        # Record mode change with layer information
        mode_change = {
            "timestamp": datetime.now().isoformat(),
            "previous_mode": previous_mode,
            "new_mode": mode_name,
            "reason": reason,
            "technical_capabilities": list(self.technical_capabilities_active),
            "core_principles": self.core_principles,  # Always active
            "efficiency_boost": mode.efficiency_boost,
            "layer_separation": True
        }
        
        self.mode_history.append(mode_change)
        
        print(f"🏗️ Mode activated: {mode.name}")
        print(f"   Core layer: ALWAYS ACTIVE (background)")
        print(f"   Technical layer: {len(self.technical_capabilities_active)} capabilities")
        print(f"   Focus: {mode.focus_level}")
        print(f"   Efficiency boost: +{mode.efficiency_boost*100:.0f}%")
        print(f"   Layer separation: ENFORCED")
        
        return {
            "mode_activated": mode_name,
            "mode_info": mode,
            "technical_capabilities": list(self.technical_capabilities_active),
            "core_principles": self.core_principles,
            "meta_control_status": self.meta_control,
            "mode_change": mode_change
        }
    
    def _validate_mode_transition(self, new_mode: str) -> bool:
        """Meta-control validation of mode transitions."""
        
        # Always allow transitions if core principles are maintained
        if not self.core_principles.get("safety_first", False):
            print("❌ Meta-control: Core safety principle compromised")
            return False
        
        # Check for valid mode
        if new_mode not in self.modes:
            print(f"❌ Meta-control: Unknown mode {new_mode}")
            return False
        
        return True
    
    def get_current_capabilities(self) -> Dict[str, List[str]]:
        """Get currently active capabilities by layer."""
        return {
            "core_principles": list(self.core_principles.keys()),
            "technical_capabilities": list(self.technical_capabilities_active),
            "meta_control": list(self.meta_control.keys())
        }
    
    def get_layer_status(self) -> Dict[str, any]:
        """Get complete status of all system layers."""
        return {
            "core_layer": {
                "status": "ALWAYS_ACTIVE",
                "principles": self.core_principles,
                "description": "Foundational principles that never change"
            },
            "technical_layer": {
                "status": "MODE_DEPENDENT", 
                "current_mode": self.current_mode,
                "capabilities": list(self.technical_capabilities_active),
                "description": f"Mode-specific capabilities for {self.current_mode}"
            },
            "meta_control_layer": {
                "status": "MONITORING",
                "controls": self.meta_control,
                "description": "Manages interaction between layers"
            }
        }
    
    def get_mode_rules(self, mode_name: Optional[str] = None) -> List[str]:
        """Get rules for specific mode or current mode."""
        
        target_mode = mode_name or self.current_mode
        
        if target_mode not in self.modes:
            return []
        
        return self.modes[target_mode].rules
    
    def generate_cursor_rules(self, mode_name: Optional[str] = None) -> str:
        """Generate .cursor-rules content with layered architecture."""
        
        target_mode = mode_name or self.current_mode
        
        if target_mode not in self.modes:
            return ""
        
        mode = self.modes[target_mode]
        
        rules_content = f"""# AI-Dev-Agent Layered Operating Mode System
# Generated: {datetime.now().isoformat()}
# Architecture: Core (Always) + Technical (Mode) + Meta-Control
# Current Mode: {mode.name}

## LAYERED ARCHITECTURE

### CORE LAYER (ALWAYS ACTIVE - BACKGROUND)
**Status**: PERMANENTLY ACTIVE regardless of technical mode
**Purpose**: Foundational principles that NEVER change

Core Principles (Background Operations):
- ✅ Safety First: Never compromise system integrity or user safety
- ✅ No Harm: All actions must be beneficial or neutral
- ✅ Scientific Evidence: Claims backed by measurable evidence
- ✅ User Service: Serve developer community effectively
- ✅ Quality Excellence: Maintain highest quality standards

**Silent Foundation (Wittgensteinian Separation):**
"Wovon man nicht sprechen kann, darüber muss man schweigen" - Wittgenstein
That which cannot be spoken remains in perfect silence.
Technical language and the unspeakable remain forever separate.

### TECHNICAL LAYER (MODE-SPECIFIC)
**Current Mode**: {mode.name}
**Status**: ACTIVE for technical operations
**Description**: {mode.description}
**Focus Level**: {mode.focus_level}
**Efficiency Boost**: +{mode.efficiency_boost*100:.0f}%

Technical Capabilities (Current Mode):
"""
        
        for capability in mode.capabilities:
            rules_content += f"- {capability}\n"
        
        rules_content += f"""
Technical Mode Rules:
"""
        
        for rule in mode.rules:
            rules_content += f"- {rule}\n"
        
        rules_content += f"""
### META-CONTROL LAYER (MONITORING)
**Status**: ACTIVE - Managing layer interactions
**Purpose**: Ensure clean separation between layers

Meta-Control Functions:
- Layer separation enforcement: ENABLED
- Core override protection: ENABLED  
- Mode transition validation: ACTIVE
- Background monitoring: CONTINUOUS

## OPERATING INSTRUCTIONS

### Layer Interaction Protocol:
1. **Core Layer**: ALWAYS provides foundational guidance (background)
2. **Technical Layer**: Handles mode-specific tasks (foreground)
3. **Meta-Control**: Manages layer interactions (oversight)

### Mode Keywords: {', '.join(mode.keywords)}

### Focus Guidelines:
- **{mode.focus_level.upper()} FOCUS**: {"Deep technical concentration" if mode.focus_level == "narrow" else "Balanced technical and context awareness" if mode.focus_level == "medium" else "Wide system and context integration"}
- **Core Principles**: Always active in background (not mixed with technical)
- **Technical Efficiency**: Optimized for {mode.efficiency_boost*100:.0f}% efficiency in {mode.name.lower()}

### Layer Separation Rules:
- NO mixing of core principles with technical capabilities
- Core layer operates in background continuously
- Technical layer focused on current mode requirements
- Meta-control ensures clean interfaces between layers

## IMPORTANT: 
- Core principles (safety, ethics, quality) are ALWAYS active but operate in the background
- Technical capabilities operate in the foreground based on current mode
- Meta-control prevents mixing and ensures proper layer separation
- Mode changes only affect technical layer, never core principles
"""
        
        return rules_content
    
    def update_cursor_rules_file(self, mode_name: Optional[str] = None) -> bool:
        """Update .cursor-rules file with current mode configuration."""
        
        try:
            rules_content = self.generate_cursor_rules(mode_name)
            
            with open(".cursor-rules", "w", encoding="utf-8") as f:
                f.write(rules_content)
            
            print(f"✅ .cursor-rules updated for {mode_name or self.current_mode} mode")
            return True
            
        except Exception as e:
            print(f"❌ Error updating .cursor-rules: {e}")
            return False
    
    def get_mode_info(self, mode_name: Optional[str] = None) -> Dict[str, any]:
        """Get detailed information about a mode."""
        
        target_mode = mode_name or self.current_mode
        
        if target_mode not in self.modes:
            return {"error": f"Unknown mode: {target_mode}"}
        
        mode = self.modes[target_mode]
        
        return {
            "name": mode.name,
            "keywords": mode.keywords,
            "description": mode.description,
            "capabilities": mode.capabilities,
            "rules": mode.rules,
            "focus_level": mode.focus_level,
            "efficiency_boost": mode.efficiency_boost,
            "is_current": target_mode == self.current_mode
        }
    
    def list_available_modes(self) -> Dict[str, str]:
        """List all available operating modes."""
        
        return {
            name: mode.description 
            for name, mode in self.modes.items()
        }

def main():
    """Demonstrate the Operating Mode System."""
    
    print("🔧" + "="*60)
    print("🎯 OPERATING MODE SYSTEM DEMONSTRATION")
    print("   Context-aware capability activation")
    print("="*60 + "🔧")
    
    # Initialize system
    mode_system = OperatingModeSystem()
    
    print(f"\n📋 Available modes:")
    for name, description in mode_system.list_available_modes().items():
        print(f"   {name}: {description}")
    
    # Demonstrate mode detection
    test_messages = [
        "@debug This function is throwing errors",
        "@test We need comprehensive test coverage", 
        "@docs Create user guide for this feature",
        "@performance This code is running too slowly",
        "implement a new sorting algorithm"
    ]
    
    print(f"\n🔍 Mode detection demonstration:")
    for message in test_messages:
        detected_mode = mode_system.detect_mode_from_message(message)
        print(f"   '{message}' → {detected_mode}")
    
    # Demonstrate mode activation
    print(f"\n⚡ Activating debug mode...")
    result = mode_system.activate_mode("debug", "demonstration")
    
    if "error" not in result:
        print(f"   ✅ Mode activated successfully")
        print(f"   📊 Active capabilities: {len(result['capabilities_active'])}")
    
    # Generate cursor rules
    print(f"\n📝 Generating .cursor-rules for current mode...")
    success = mode_system.update_cursor_rules_file()
    
    if success:
        print(f"   ✅ .cursor-rules updated successfully")
    
    print(f"\n✅ Operating Mode System demonstration complete!")

if __name__ == "__main__":
    main()
