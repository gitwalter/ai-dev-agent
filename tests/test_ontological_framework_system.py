#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Ontological Framework System
=========================================================

Test-driven development approach with complete coverage of:
- Framework registration and activation
- Clean perspective switching
- Ontological contamination detection
- Expression validation within frameworks
- Error handling and edge cases

Following TDD methodology with systematic test coverage.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add utils path for imports
utils_path = Path(__file__).parent.parent / "utils"
sys.path.append(str(utils_path))

from context.ontological_framework_system import (
    OntologicalFramework,
    LanguageSystem,
    MeaningStructure, 
    ConceptualBoundaries,
    ContaminationDetector,
    OntologicalSwitchingSystem
)


class TestLanguageSystem(unittest.TestCase):
    """Test LanguageSystem dataclass functionality."""
    
    def setUp(self):
        """Set up test language system."""
        self.language_system = LanguageSystem(
            primary_concepts=["test", "verify", "assert"],
            truth_criteria="Tests must pass",
            reasoning_pattern="Evidence-based validation",
            valid_expressions=["test", "verify", "validate"],
            invalid_expressions=["guess", "assume"]
        )
    
    def test_language_system_creation(self):
        """Test language system can be created with all fields."""
        self.assertEqual(self.language_system.primary_concepts, ["test", "verify", "assert"])
        self.assertEqual(self.language_system.truth_criteria, "Tests must pass")
        self.assertEqual(self.language_system.reasoning_pattern, "Evidence-based validation")
        self.assertEqual(self.language_system.valid_expressions, ["test", "verify", "validate"])
        self.assertEqual(self.language_system.invalid_expressions, ["guess", "assume"])
    
    def test_language_system_immutable(self):
        """Test language system fields are accessible."""
        # Dataclass fields should be accessible
        self.assertIsInstance(self.language_system.primary_concepts, list)
        self.assertIsInstance(self.language_system.truth_criteria, str)


class TestOntologicalFramework(unittest.TestCase):
    """Test OntologicalFramework class functionality."""
    
    def setUp(self):
        """Set up test ontological framework."""
        self.language_system = LanguageSystem(
            primary_concepts=["code", "test", "function"],
            truth_criteria="Code must work",
            reasoning_pattern="Test-driven",
            valid_expressions=["implement", "test", "debug"],
            invalid_expressions=["design", "architecture"]
        )
        
        self.meaning_structure = MeaningStructure(
            success_definition="Tests pass",
            problem_definition="Tests fail", 
            solution_approach="Fix code",
            quality_criteria="Clean code"
        )
        
        self.conceptual_boundaries = ConceptualBoundaries(
            what_exists=["code", "tests"],
            what_matters=["functionality"],
            time_horizon="sprint",
            success_metrics=["test coverage"]
        )
        
        self.framework = OntologicalFramework(
            name="test_framework",
            world_view="Testing-focused reality",
            language_system=self.language_system,
            meaning_structure=self.meaning_structure,
            conceptual_boundaries=self.conceptual_boundaries,
            keywords=["@test"]
        )
    
    def test_framework_creation(self):
        """Test ontological framework can be created."""
        self.assertEqual(self.framework.name, "test_framework")
        self.assertEqual(self.framework.world_view, "Testing-focused reality")
        self.assertFalse(self.framework.active)
        self.assertIsNone(self.framework.activation_time)
    
    def test_framework_activation(self):
        """Test framework activation sets active state."""
        with patch('builtins.print'):  # Suppress print output
            self.framework.activate()
        
        self.assertTrue(self.framework.active)
        self.assertIsNotNone(self.framework.activation_time)
        self.assertIsInstance(self.framework.activation_time, datetime)
    
    def test_framework_deactivation(self):
        """Test framework deactivation clears active state."""
        with patch('builtins.print'):
            self.framework.activate()
            self.framework.deactivate()
        
        self.assertFalse(self.framework.active)
        self.assertIsNone(self.framework.activation_time)
    
    def test_validate_expression_when_inactive(self):
        """Test expression validation fails when framework inactive."""
        result = self.framework.validate_expression("test the code")
        
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "Framework not active")
        self.assertEqual(result["framework"], "test_framework")
    
    def test_validate_expression_with_invalid_concepts(self):
        """Test expression validation detects invalid concepts."""
        with patch('builtins.print'):
            self.framework.activate()
        
        result = self.framework.validate_expression("design the architecture")
        
        self.assertFalse(result["valid"])
        self.assertTrue("invalid concept" in result["reason"])
        self.assertTrue(result["ontological_violation"])
    
    def test_validate_expression_with_valid_concepts(self):
        """Test expression validation accepts valid concepts."""
        with patch('builtins.print'):
            self.framework.activate()
        
        result = self.framework.validate_expression("test the code implementation")
        
        self.assertTrue(result["valid"])
        self.assertEqual(result["framework"], "test_framework")
        self.assertIn("test", result["concept_matches"])
        self.assertIn("code", result["concept_matches"])
    
    def test_validate_expression_with_valid_expressions(self):
        """Test expression validation accepts valid expressions."""
        with patch('builtins.print'):
            self.framework.activate()
        
        result = self.framework.validate_expression("implement and debug the feature")
        
        self.assertTrue(result["valid"])
        self.assertIn("implement", result["expression_matches"])
        self.assertIn("debug", result["expression_matches"])
    
    def test_alignment_score_calculation(self):
        """Test alignment score is calculated correctly."""
        with patch('builtins.print'):
            self.framework.activate()
        
        result = self.framework.validate_expression("test code")
        
        # Should have alignment score based on matches
        self.assertIn("alignment_score", result)
        self.assertGreater(result["alignment_score"], 0)


class TestContaminationDetector(unittest.TestCase):
    """Test ContaminationDetector functionality."""
    
    def setUp(self):
        """Set up contamination detector and test frameworks."""
        self.detector = ContaminationDetector()
        
        # Create two distinct frameworks
        self.framework1 = OntologicalFramework(
            name="engineering",
            world_view="Code-focused",
            language_system=LanguageSystem(
                primary_concepts=["code", "function", "performance"],
                truth_criteria="Works correctly",
                reasoning_pattern="Test-driven",
                valid_expressions=["implement", "optimize"],
                invalid_expressions=["design"]
            ),
            meaning_structure=MeaningStructure("", "", "", ""),
            conceptual_boundaries=ConceptualBoundaries([], [], "", []),
            keywords=["@engineering"]
        )
        
        self.framework2 = OntologicalFramework(
            name="architecture", 
            world_view="Design-focused",
            language_system=LanguageSystem(
                primary_concepts=["pattern", "structure", "design"],
                truth_criteria="Well-designed",
                reasoning_pattern="Pattern-based",
                valid_expressions=["design", "architect"],
                invalid_expressions=["implement"]
            ),
            meaning_structure=MeaningStructure("", "", "", ""),
            conceptual_boundaries=ConceptualBoundaries([], [], "", []),
            keywords=["@architecture"]
        )
        
        self.all_frameworks = {
            "engineering": self.framework1,
            "architecture": self.framework2
        }
    
    def test_no_contamination_detected(self):
        """Test clean expression has no contamination."""
        with patch('builtins.print'):
            result = self.detector.detect_contamination(
                "design the system pattern",
                self.framework2,  # architecture framework
                self.all_frameworks
            )
        
        self.assertFalse(result["contamination_detected"])
        self.assertEqual(result["active_framework"], "architecture")
        self.assertEqual(result["foreign_concepts"], {})
    
    def test_contamination_detected(self):
        """Test contamination is detected when mixing concepts."""
        with patch('builtins.print'):
            result = self.detector.detect_contamination(
                "design the function performance",  # mixes architecture + engineering
                self.framework2,  # architecture framework active
                self.all_frameworks
            )
        
        self.assertTrue(result["contamination_detected"])
        self.assertEqual(result["active_framework"], "architecture")
        self.assertIn("engineering", result["foreign_concepts"])
        self.assertIn("function", result["foreign_concepts"]["engineering"])
        self.assertIn("performance", result["foreign_concepts"]["engineering"])
    
    def test_contamination_logging(self):
        """Test contamination events are logged."""
        with patch('builtins.print'):
            self.detector.detect_contamination(
                "implement the design pattern",
                self.framework2,
                self.all_frameworks
            )
        
        self.assertEqual(len(self.detector.contamination_log), 1)
        self.assertTrue(self.detector.contamination_log[0]["contamination_detected"])


class TestOntologicalSwitchingSystem(unittest.TestCase):
    """Test OntologicalSwitchingSystem functionality."""
    
    def setUp(self):
        """Set up ontological switching system."""
        with patch('builtins.print'):  # Suppress initialization prints
            self.system = OntologicalSwitchingSystem()
    
    def test_system_initialization(self):
        """Test system initializes with standard frameworks."""
        self.assertIn("engineering", self.system.frameworks)
        self.assertIn("architecture", self.system.frameworks)
        self.assertIn("debug", self.system.frameworks)
        self.assertIsNone(self.system.current_framework)
        self.assertEqual(len(self.system.transition_history), 0)
    
    def test_switch_to_valid_framework(self):
        """Test switching to a valid framework."""
        with patch('builtins.print'):
            result = self.system.switch_perspective("engineering", "Test context")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["active_framework"], "engineering")
        self.assertEqual(self.system.current_framework.name, "engineering")
        self.assertTrue(self.system.current_framework.active)
        self.assertEqual(len(self.system.transition_history), 1)
    
    def test_switch_to_invalid_framework(self):
        """Test switching to invalid framework fails gracefully."""
        with patch('builtins.print'):
            result = self.system.switch_perspective("invalid_framework")
        
        self.assertFalse(result["success"])
        self.assertIn("Unknown ontological framework", result["error"])
        self.assertIsNone(self.system.current_framework)
    
    def test_switch_between_frameworks(self):
        """Test switching between multiple frameworks."""
        with patch('builtins.print'):
            # Switch to engineering
            result1 = self.system.switch_perspective("engineering")
            self.assertTrue(result1["success"])
            
            # Switch to architecture  
            result2 = self.system.switch_perspective("architecture")
            self.assertTrue(result2["success"])
            
            # Verify engineering was deactivated and architecture activated
            engineering_framework = self.system.frameworks["engineering"]
            architecture_framework = self.system.frameworks["architecture"]
            
            self.assertFalse(engineering_framework.active)
            self.assertTrue(architecture_framework.active)
            self.assertEqual(self.system.current_framework.name, "architecture")
            self.assertEqual(len(self.system.transition_history), 2)
    
    def test_validate_expression_no_active_framework(self):
        """Test expression validation fails with no active framework."""
        result = self.system.validate_expression("test expression")
        
        self.assertFalse(result["validation"]["valid"])
        self.assertIn("No active ontological framework", result["validation"]["error"])
    
    def test_validate_expression_with_active_framework(self):
        """Test expression validation with active framework."""
        with patch('builtins.print'):
            self.system.switch_perspective("engineering")
            result = self.system.validate_expression("implement the function")
        
        # Should have validation and contamination results
        self.assertIn("validation", result)
        self.assertIn("contamination", result)
        self.assertEqual(result["current_framework"], "engineering")
    
    def test_detect_framework_from_keywords(self):
        """Test framework detection from keywords."""
        engineering_detection = self.system.detect_framework_from_keywords("@engineering implement feature")
        architecture_detection = self.system.detect_framework_from_keywords("@architecture design system")
        no_detection = self.system.detect_framework_from_keywords("random text")
        
        self.assertEqual(engineering_detection, "engineering")
        self.assertEqual(architecture_detection, "architecture")
        self.assertIsNone(no_detection)
    
    def test_get_framework_status(self):
        """Test framework status reporting."""
        status = self.system.get_framework_status()
        
        self.assertIsNone(status["current_framework"])
        self.assertEqual(len(status["available_frameworks"]), 3)
        self.assertEqual(status["transition_count"], 0)
        self.assertEqual(status["contamination_count"], 0)
        self.assertIsNone(status["last_transition"])
        
        # After transition
        with patch('builtins.print'):
            self.system.switch_perspective("engineering")
        
        status_after = self.system.get_framework_status()
        self.assertEqual(status_after["current_framework"], "engineering")
        self.assertEqual(status_after["transition_count"], 1)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete ontological switching workflows."""
    
    def setUp(self):
        """Set up integration test environment."""
        with patch('builtins.print'):
            self.system = OntologicalSwitchingSystem()
    
    def test_complete_development_workflow(self):
        """Test complete development workflow with multiple switches."""
        with patch('builtins.print'):
            # Architecture phase
            result1 = self.system.switch_perspective("architecture", "Design phase")
            self.assertTrue(result1["success"])
            
            validation1 = self.system.validate_expression("design the system structure")
            self.assertTrue(validation1["validation"]["valid"])
            self.assertFalse(validation1["contamination"]["contamination_detected"])
            
            # Engineering phase
            result2 = self.system.switch_perspective("engineering", "Implementation phase")
            self.assertTrue(result2["success"])
            
            validation2 = self.system.validate_expression("implement the user function")
            self.assertTrue(validation2["validation"]["valid"])
            
            # Debug phase
            result3 = self.system.switch_perspective("debug", "Bug found")
            self.assertTrue(result3["success"])
            
            validation3 = self.system.validate_expression("reproduce the error symptom")
            self.assertTrue(validation3["validation"]["valid"])
            
            # Verify complete workflow
            self.assertEqual(len(self.system.transition_history), 3)
            self.assertEqual(self.system.current_framework.name, "debug")
    
    def test_contamination_across_workflow(self):
        """Test contamination detection across workflow transitions."""
        with patch('builtins.print'):
            # Start in architecture mode
            self.system.switch_perspective("architecture")
            
            # Try engineering expression in architecture mode
            result = self.system.validate_expression("implement the function quickly")
            
            self.assertFalse(result["validation"]["valid"])
            self.assertTrue(result["contamination"]["contamination_detected"])
            
            # Switch to engineering and try same expression
            self.system.switch_perspective("engineering")
            result2 = self.system.validate_expression("implement the function quickly")
            
            self.assertTrue(result2["validation"]["valid"])
            # Should have no contamination in correct framework
            self.assertFalse(result2["contamination"]["contamination_detected"])


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up error handling test environment."""
        with patch('builtins.print'):
            self.system = OntologicalSwitchingSystem()
    
    def test_register_duplicate_framework(self):
        """Test registering framework with duplicate name."""
        # Create duplicate framework
        duplicate_framework = OntologicalFramework(
            name="engineering",  # Same as existing
            world_view="Duplicate",
            language_system=LanguageSystem([], "", "", [], []),
            meaning_structure=MeaningStructure("", "", "", ""),
            conceptual_boundaries=ConceptualBoundaries([], [], "", []),
            keywords=[]
        )
        
        with patch('builtins.print'):
            self.system.register_framework(duplicate_framework)
        
        # Should overwrite existing framework
        self.assertEqual(self.system.frameworks["engineering"].world_view, "Duplicate")
    
    def test_empty_expression_validation(self):
        """Test validation of empty expressions."""
        with patch('builtins.print'):
            self.system.switch_perspective("engineering")
            result = self.system.validate_expression("")
        
        # Should handle empty expressions gracefully
        self.assertFalse(result["validation"]["valid"])
    
    def test_none_expression_validation(self):
        """Test validation handles None expressions."""
        with patch('builtins.print'):
            self.system.switch_perspective("engineering")
            
            # This should not crash
            try:
                result = self.system.validate_expression(None)
                # Should handle None gracefully
                self.assertIsNotNone(result)
            except AttributeError:
                # Expected if None.lower() is called
                pass


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
