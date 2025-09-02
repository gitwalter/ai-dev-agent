"""
Keyword-Driven Rule Attachment System with Strict Syntax & Semantics
===================================================================

Core Architecture:
- 7 Universal Rules (ALWAYS active)
- Specialized Rules attach to specific keywords (@agile, @code, @debug, etc.)
- Strict syntax and semantic validation
- Working implementation that maintains rule consistency

Principle: "Universal Foundation + Keyword-Specific Extensions"
"""

from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from pathlib import Path

class KeywordType(Enum):
    """Valid keyword types with strict definitions."""
    AGILE = "@agile"
    CODE = "@code" 
    DEBUG = "@debug"
    TEST = "@test"
    DOCS = "@docs"
    SECURITY = "@security"
    PERFORMANCE = "@performance"
    ARCHITECTURE = "@architecture"
    GIT = "@git"

@dataclass
class RuleAttachment:
    """Strict rule attachment specification."""
    keyword: KeywordType
    rule_id: str
    rule_title: str
    activation_condition: str
    deactivation_condition: str
    priority: int  # 1-10, higher = more important
    conflicts_with: List[str]  # Rule IDs that cannot be active simultaneously

@dataclass
class SyntaxValidation:
    """Strict syntax validation result."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    normalized_keyword: Optional[KeywordType]

class KeywordRuleAttachmentSystem:
    """
    Strict syntax and semantic system for keyword-driven rule attachment.
    Maintains the 7 Universal Rules + keyword-specific extensions.
    """
    
    def __init__(self):
        # The 7 Universal Rules (ALWAYS active)
        self.universal_rules = [
            "safety_first_principle",
            "scientific_verification_evidence_based_success", 
            "core_values_enforcement",
            "disaster_report_learning",
            "divine_harmony_integration_system",
            "keep_it_small_simple_kiss",
            "file_organization_cleanup"
        ]
        
        # Keyword-specific rule attachments
        self.keyword_rule_mappings = self._initialize_keyword_mappings()
        
        # Syntax validation patterns
        self.syntax_patterns = self._initialize_syntax_patterns()
        
    def _initialize_keyword_mappings(self) -> Dict[KeywordType, List[RuleAttachment]]:
        """Initialize strict keyword-to-rule mappings."""
        
        mappings = {
            KeywordType.AGILE: [
                RuleAttachment(
                    keyword=KeywordType.AGILE,
                    rule_id="agile_strategic_coordination_rule",
                    rule_title="Agile Strategic Coordination Rule",
                    activation_condition="@agile keyword detected in user message",
                    deactivation_condition="context switches away from agile coordination",
                    priority=9,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.AGILE,
                    rule_id="agile_artifacts_maintenance_rule",
                    rule_title="Agile Artifacts Maintenance Rule", 
                    activation_condition="@agile keyword + agile work detected",
                    deactivation_condition="agile work completed",
                    priority=8,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.AGILE,
                    rule_id="user_story_management_rule",
                    rule_title="User Story Management Rule",
                    activation_condition="@agile + user story work",
                    deactivation_condition="user story work completed",
                    priority=7,
                    conflicts_with=[]
                )
            ],
            
            KeywordType.CODE: [
                RuleAttachment(
                    keyword=KeywordType.CODE,
                    rule_id="development_core_principles_rule",
                    rule_title="Development Core Principles Rule",
                    activation_condition="@code keyword detected in user message",
                    deactivation_condition="coding context ends",
                    priority=9,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.CODE,
                    rule_id="test_driven_development_rule",
                    rule_title="Test-Driven Development Rule",
                    activation_condition="@code + implementation work",
                    deactivation_condition="implementation completed",
                    priority=8,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.CODE,
                    rule_id="clean_code_standards_rule",
                    rule_title="Clean Code Standards Rule",
                    activation_condition="@code + code quality focus",
                    deactivation_condition="code quality work completed",
                    priority=7,
                    conflicts_with=[]
                )
            ],
            
            KeywordType.DEBUG: [
                RuleAttachment(
                    keyword=KeywordType.DEBUG,
                    rule_id="systematic_problem_solving_rule",
                    rule_title="Systematic Problem Solving Rule",
                    activation_condition="@debug keyword or error indicators detected",
                    deactivation_condition="problem solved and verified",
                    priority=9,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.DEBUG,
                    rule_id="error_exposure_rule",
                    rule_title="Error Exposure Rule",
                    activation_condition="@debug + error handling focus",
                    deactivation_condition="errors resolved",
                    priority=8,
                    conflicts_with=[]
                )
            ],
            
            KeywordType.TEST: [
                RuleAttachment(
                    keyword=KeywordType.TEST,
                    rule_id="no_failing_tests_rule",
                    rule_title="No Failing Tests Rule",
                    activation_condition="@test keyword or testing context",
                    deactivation_condition="all tests passing",
                    priority=9,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.TEST,
                    rule_id="test_monitoring_rule",
                    rule_title="Test Monitoring Rule",
                    activation_condition="@test + test automation focus",
                    deactivation_condition="test monitoring established",
                    priority=7,
                    conflicts_with=[]
                )
            ],
            
            KeywordType.DOCS: [
                RuleAttachment(
                    keyword=KeywordType.DOCS,
                    rule_id="documentation_live_updates_rule",
                    rule_title="Documentation Live Updates Rule",
                    activation_condition="@docs keyword or documentation work",
                    deactivation_condition="documentation updated",
                    priority=8,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.DOCS,
                    rule_id="clear_communication_rule",
                    rule_title="Clear Communication Rule",
                    activation_condition="@docs + communication focus",
                    deactivation_condition="communication clarity achieved",
                    priority=7,
                    conflicts_with=[]
                )
            ],
            
            KeywordType.GIT: [
                RuleAttachment(
                    keyword=KeywordType.GIT,
                    rule_id="automated_git_workflow_enforcement_rule",
                    rule_title="Automated Git Workflow Enforcement Rule",
                    activation_condition="@git keyword or git operations",
                    deactivation_condition="git operations completed",
                    priority=9,
                    conflicts_with=[]
                ),
                RuleAttachment(
                    keyword=KeywordType.GIT,
                    rule_id="streamlined_git_operations_rule",
                    rule_title="Streamlined Git Operations Rule",
                    activation_condition="@git + workflow optimization",
                    deactivation_condition="git workflow optimized",
                    priority=7,
                    conflicts_with=[]
                )
            ]
        }
        
        return mappings
    
    def _initialize_syntax_patterns(self) -> Dict[str, str]:
        """Initialize strict syntax validation patterns."""
        
        return {
            "keyword_pattern": r"@(agile|code|debug|test|docs|security|performance|architecture|git)\\b",
            "multiple_keywords": r"@\\w+.*@\\w+",
            "invalid_keyword": r"@[a-zA-Z]+",
            "context_transition": r"@\\w+.*then.*@\\w+|@\\w+.*->.*@\\w+"
        }
    
    def validate_syntax(self, user_message: str) -> SyntaxValidation:
        """Validate syntax of user message with strict rules."""
        
        validation = SyntaxValidation(
            is_valid=True,
            errors=[],
            warnings=[],
            normalized_keyword=None
        )
        
        # Extract keywords from message
        keyword_matches = re.findall(self.syntax_patterns["keyword_pattern"], user_message.lower())
        
        if not keyword_matches:
            # No keywords - use Universal Seven only
            validation.warnings.append("No keywords detected - using Universal Seven rules only")
            return validation
        
        if len(keyword_matches) > 1:
            # Multiple keywords detected
            validation.warnings.append(f"Multiple keywords detected: {keyword_matches} - using first keyword")
            
        # Validate first keyword
        first_keyword = keyword_matches[0]
        try:
            normalized_keyword = KeywordType(f"@{first_keyword}")
            validation.normalized_keyword = normalized_keyword
        except ValueError:
            validation.is_valid = False
            validation.errors.append(f"Invalid keyword: @{first_keyword}")
            
        # Check for invalid keywords
        all_keywords = re.findall(r"@([a-zA-Z]+)", user_message.lower())
        valid_keywords = {kt.value[1:] for kt in KeywordType}  # Remove @ prefix
        
        for keyword in all_keywords:
            if keyword not in valid_keywords:
                validation.errors.append(f"Unknown keyword: @{keyword}")
                validation.is_valid = False
        
        return validation
    
    def generate_active_rules(self, user_message: str) -> Dict[str, Any]:
        """Generate active rule set based on user message with strict validation."""
        
        # Validate syntax first
        syntax_validation = self.validate_syntax(user_message)
        
        if not syntax_validation.is_valid:
            return {
                "status": "SYNTAX_ERROR",
                "errors": syntax_validation.errors,
                "active_rules": self.universal_rules,  # Fallback to Universal Seven
                "rule_count": len(self.universal_rules)
            }
        
        # Start with Universal Seven (always active)
        active_rules = self.universal_rules.copy()
        attached_rules = []
        
        # Add keyword-specific rules
        if syntax_validation.normalized_keyword:
            keyword = syntax_validation.normalized_keyword
            
            if keyword in self.keyword_rule_mappings:
                keyword_rules = self.keyword_rule_mappings[keyword]
                
                # Sort by priority (highest first)
                keyword_rules.sort(key=lambda r: r.priority, reverse=True)
                
                for rule_attachment in keyword_rules:
                    # Check for conflicts
                    if not any(conflict in active_rules for conflict in rule_attachment.conflicts_with):
                        active_rules.append(rule_attachment.rule_id)
                        attached_rules.append({
                            "rule_id": rule_attachment.rule_id,
                            "rule_title": rule_attachment.rule_title,
                            "keyword": keyword.value,
                            "priority": rule_attachment.priority,
                            "activation_condition": rule_attachment.activation_condition
                        })
        
        return {
            "status": "SUCCESS",
            "syntax_validation": syntax_validation,
            "universal_rules": self.universal_rules,
            "attached_rules": attached_rules,
            "active_rules": active_rules,
            "rule_count": len(active_rules),
            "efficiency_info": {
                "base_rules": len(self.universal_rules),
                "attached_rules": len(attached_rules),
                "total_active": len(active_rules),
                "keyword_used": syntax_validation.normalized_keyword.value if syntax_validation.normalized_keyword else None
            }
        }
    
    def generate_cursor_rules_content(self, active_rule_config: Dict[str, Any]) -> str:
        """Generate .cursor-rules content based on active rule configuration."""
        
        universal_rules_section = '''# THE UNIVERSAL SEVEN RULES + KEYWORD EXTENSIONS
# ===============================================
# 
# 7 Universal Rules (ALWAYS active) + Keyword-specific rule attachments
# Strict syntax: @keyword triggers additional specialized rules
# 
## Architecture: Universal Foundation + Keyword Extensions

### Core Principle
**"Seven Universal Rules + Keyword-Driven Specialized Extensions"**

The system maintains 7 Universal Rules that are ALWAYS active, plus specialized rules that attach when specific keywords are used.

## Universal Seven (Always Active)

### 1. Safety First Principle
**CRITICAL**: Always prioritize safety over speed, convenience, or automation.

### 2. Scientific Verification and Evidence-Based Success  
**CRITICAL**: All claims must be verified through systematic evidence collection.

### 3. Core Values Enforcement
**FOUNDATIONAL**: Maintain mathematical beauty, technical excellence, moral integrity.

### 4. Disaster Report Learning
**CRITICAL**: Convert every failure into comprehensive learning and improvement.

### 5. Divine Harmony Integration System
**FOUNDATIONAL**: Perfect integration of sensitivity, reflection, research, execution.

### 6. Keep It Small and Simple (KISS)
**CRITICAL**: Always prioritize simplicity, clarity, and minimalism.

### 7. File Organization and Cleanup
**CRITICAL**: Maintain clean, organized file structure automatically.

'''
        
        # Add keyword-specific rules if any are attached
        if active_rule_config.get("attached_rules"):
            keyword_section = f'''
## Keyword-Specific Extensions (Currently Active)

**Keyword**: {active_rule_config["efficiency_info"]["keyword_used"]}
**Additional Rules**: {len(active_rule_config["attached_rules"])}

'''
            for rule in active_rule_config["attached_rules"]:
                keyword_section += f'''
### {rule["rule_title"]}
**Priority**: {rule["priority"]}/10
**Activation**: {rule["activation_condition"]}
**Keyword**: {rule["keyword"]}

'''
        else:
            keyword_section = '''
## Keyword-Specific Extensions

**Status**: No keywords detected - using Universal Seven only
**Available Keywords**: @agile, @code, @debug, @test, @docs, @git, @security, @performance, @architecture

'''
        
        footer_section = f'''
## System Status

**Total Active Rules**: {active_rule_config["rule_count"]}
**Universal Rules**: {len(active_rule_config["universal_rules"])} (always active)
**Attached Rules**: {len(active_rule_config.get("attached_rules", []))} (keyword-specific)
**Syntax Status**: {active_rule_config["status"]}

## Keyword Syntax Reference

**Valid Keywords**: @agile, @code, @debug, @test, @docs, @git, @security, @performance, @architecture

**Usage Examples**:
- `@agile coordinate stakeholder communication` 
- `@code implement authentication system`
- `@debug fix the database connection error`
- `@test validate the user registration flow`
- `@docs update the API documentation`

**Strict Syntax Rules**:
1. Keywords must start with @ symbol
2. Only one primary keyword per message
3. Keywords must be from valid set
4. Invalid keywords generate syntax errors
'''
        
        return universal_rules_section + keyword_section + footer_section

def test_keyword_rule_system():
    """Test the keyword rule attachment system."""
    
    print("🎯 **TESTING KEYWORD RULE ATTACHMENT SYSTEM**")
    print("=" * 60)
    
    system = KeywordRuleAttachmentSystem()
    
    test_messages = [
        "@agile coordinate stakeholder communication for new feature",
        "@code implement user authentication with proper security",
        "@debug fix the database connection timeout error", 
        "@test validate the registration flow thoroughly",
        "@docs update the API documentation for v2.0",
        "regular message without any keywords",
        "@invalid unknown keyword test",
        "@agile work on user stories @code and implement features"  # Multiple keywords
    ]
    
    for message in test_messages:
        print(f"\\n--- Testing Message ---")
        print(f"Input: '{message}'")
        
        result = system.generate_active_rules(message)
        
        print(f"Status: {result['status']}")
        print(f"Active Rules: {result['rule_count']}")
        
        if result['status'] == 'SUCCESS':
            print(f"Universal: {len(result['universal_rules'])}")
            print(f"Attached: {len(result['attached_rules'])}")
            if result['attached_rules']:
                keyword = result['efficiency_info']['keyword_used']
                print(f"Keyword: {keyword}")
                for rule in result['attached_rules']:
                    print(f"  + {rule['rule_title']} (priority: {rule['priority']})")
        else:
            print(f"Errors: {result.get('errors', [])}")

def update_cursor_rules_with_keyword_system(user_message: str):
    """Update .cursor-rules with keyword-driven rule system."""
    
    print("🎯 **UPDATING CURSOR RULES WITH KEYWORD SYSTEM**")
    print("=" * 55)
    
    system = KeywordRuleAttachmentSystem()
    
    # Generate active rules based on current user message
    active_config = system.generate_active_rules(user_message)
    
    print(f"Status: {active_config['status']}")
    print(f"Active Rules: {active_config['rule_count']}")
    
    if active_config['status'] == 'SUCCESS':
        # Generate .cursor-rules content
        cursor_content = system.generate_cursor_rules_content(active_config)
        
        # Backup existing .cursor-rules
        if Path('.cursor-rules').exists():
            with open('.cursor-rules.backup.keyword', 'w', encoding='utf-8') as f:
                with open('.cursor-rules', 'r', encoding='utf-8') as original:
                    f.write(original.read())
            print("✅ Backup created: .cursor-rules.backup.keyword")
        
        # Write new .cursor-rules
        with open('.cursor-rules', 'w', encoding='utf-8') as f:
            f.write(cursor_content)
        
        print("✅ **KEYWORD RULE SYSTEM IMPLEMENTED**")
        print(f"   Universal Rules: {len(active_config['universal_rules'])} (always active)")
        print(f"   Attached Rules: {len(active_config.get('attached_rules', []))} (keyword-specific)")
        print(f"   Total Active: {active_config['rule_count']}")
        
        if active_config.get('attached_rules'):
            keyword = active_config['efficiency_info']['keyword_used']
            print(f"   Current Keyword: {keyword}")
        else:
            print(f"   Current Mode: Universal Seven only")
            
        return True
    else:
        print(f"❌ Syntax Error: {active_config.get('errors', [])}")
        return False

if __name__ == "__main__":
    print("🎯 **KEYWORD-DRIVEN RULE ATTACHMENT SYSTEM**")
    print("Testing strict syntax and semantic validation...")
    
    # Run tests
    test_keyword_rule_system()
    
    # Example usage with the current user message
    print("\\n" + "=" * 60)
    print("🎯 **IMPLEMENTING FOR CURRENT MESSAGE**")
    example_message = "@agile the other rules could be attached to keywords"
    result = update_cursor_rules_with_keyword_system(example_message)
    
    if result:
        print("\\n✅ **SUCCESS**: Keyword rule system implemented!")
        print("Restart Cursor IDE to see the Universal Seven + @agile extensions")
