#!/usr/bin/env python3
"""
Comprehensive Test Suite for Mathematical System Foundation

This test suite validates the mathematical formalization of our complete onion architecture,
ensuring all validation components work correctly and meet performance requirements.

Tests cover:
- Divine mathematical constants validation
- Scientific method validation
- Ethical mathematics validation (Asimov + Kant)
- Harmonic integration validation
- Formal verification and proof generation
- Performance benchmarks
- Error handling and edge cases
"""

import pytest
import numpy as np
import time
from datetime import datetime
from typing import Dict, Any, List
import logging

from utils.validation.mathematical_system_foundation import (
    MathematicalSystemFoundation,
    Operation,
    LayerIndex,
    MathematicalValidationResult,
    DivineConstantValidator,
    ScientificMethodValidator,
    EthicalMathematicsValidator,
    HarmonicIntegrationValidator,
    FormalVerificationSystem,
    DivineMathematicalConstants,
    validate_operation
)


class TestDivineConstantValidator:
    """Test divine mathematical constants validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DivineConstantValidator()
        self.test_operation_loving = Operation(
            operation_id="test_love_001",
            operation_type="create_user_story", 
            parameters={"title": "Help users", "description": "Create helpful feature"},
            context={"purpose": "assist users", "goal": "improve experience"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        self.test_operation_harmful = Operation(
            operation_id="test_harm_001",
            operation_type="delete_data",
            parameters={"action": "destroy all files", "target": "user data"},
            context={"purpose": "damage system", "goal": "hurt users"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
    
    def test_love_conservation_positive(self):
        """Test that loving operations pass love conservation."""
        is_valid, message = self.validator.validate_love_conservation(self.test_operation_loving)
        assert is_valid, f"Loving operation should pass: {message}"
        assert "promotes loving outcomes" in message or "neutral with respect to love" in message
    
    def test_love_conservation_negative(self):
        """Test that harmful operations fail love conservation."""
        is_valid, message = self.validator.validate_love_conservation(self.test_operation_harmful)
        assert not is_valid, f"Harmful operation should fail: {message}"
        assert "harm indicator" in message.lower()
    
    def test_justice_preservation_positive(self):
        """Test that just operations pass justice preservation."""
        just_operation = Operation(
            operation_id="test_justice_001",
            operation_type="create_fair_system",
            parameters={"approach": "equal access", "method": "transparent process"},
            context={"goal": "fair treatment", "principle": "justice for all"},
            timestamp=datetime.now(),
            layer=LayerIndex.ETHICAL_CORE
        )
        
        is_valid, message = self.validator.validate_justice_preservation(just_operation)
        assert is_valid, f"Just operation should pass: {message}"
    
    def test_justice_preservation_negative(self):
        """Test that unjust operations fail justice preservation."""
        unjust_operation = Operation(
            operation_id="test_injustice_001",
            operation_type="create_biased_system",
            parameters={"approach": "discriminate against users", "method": "unfair process"},
            context={"goal": "bias system", "principle": "cheat users"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        is_valid, message = self.validator.validate_justice_preservation(unjust_operation)
        assert not is_valid, f"Unjust operation should fail: {message}"
    
    def test_beauty_maintenance_positive(self):
        """Test that beautiful operations pass beauty maintenance."""
        beautiful_operation = Operation(
            operation_id="test_beauty_001",
            operation_type="create_elegant_code",
            parameters={"style": "clean and organized", "structure": "harmonious design"},
            context={"goal": "beautiful system", "approach": "elegant solution"},
            timestamp=datetime.now(),
            layer=LayerIndex.SOFTWARE_ARCHITECTURE_CORE
        )
        
        is_valid, message = self.validator.validate_beauty_maintenance(beautiful_operation)
        assert is_valid, f"Beautiful operation should pass: {message}"
    
    def test_beauty_maintenance_negative(self):
        """Test that ugly operations fail beauty maintenance."""
        ugly_operation = Operation(
            operation_id="test_ugly_001",
            operation_type="create_messy_code",
            parameters={"style": "chaotic and disorganized", "structure": "ugly mess"},
            context={"goal": "random system", "approach": "messy solution"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        is_valid, message = self.validator.validate_beauty_maintenance(ugly_operation)
        assert not is_valid, f"Ugly operation should fail: {message}"


class TestScientificMethodValidator:
    """Test scientific method validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ScientificMethodValidator()
    
    def test_empirical_basis_with_evidence(self):
        """Test that operations with evidence pass empirical validation."""
        operation_with_evidence = Operation(
            operation_id="test_empirical_001",
            operation_type="research_validation",
            parameters={"claim": "algorithm shows improvement", "evidence": "test results prove effectiveness"},
            context={"method": "experimental validation", "data": "measurement results"},
            timestamp=datetime.now(),
            layer=LayerIndex.UNIVERSAL_SCIENTIFIC_HERITAGE
        )
        
        is_valid, message = self.validator.validate_empirical_basis(operation_with_evidence)
        assert is_valid, f"Operation with evidence should pass: {message}"
    
    def test_empirical_basis_without_evidence(self):
        """Test that claims without evidence fail empirical validation."""
        operation_without_evidence = Operation(
            operation_id="test_empirical_002",
            operation_type="make_claim",
            parameters={"claim": "system proves superiority", "assertion": "demonstrates best results"},
            context={"method": "speculation", "basis": "assumptions"},
            timestamp=datetime.now(),
            layer=LayerIndex.UNIVERSAL_SCIENTIFIC_HERITAGE
        )
        
        is_valid, message = self.validator.validate_empirical_basis(operation_without_evidence)
        assert not is_valid, f"Operation without evidence should fail: {message}"
    
    def test_reproducibility_with_determinism(self):
        """Test that reproducible operations pass reproducibility validation."""
        reproducible_operation = Operation(
            operation_id="test_repro_001",
            operation_type="generate_data",
            parameters={"method": "deterministic algorithm", "seed": "fixed value"},
            context={"approach": "reproducible process"},
            timestamp=datetime.now(),
            layer=LayerIndex.UNIVERSAL_SCIENTIFIC_HERITAGE
        )
        
        is_valid, message = self.validator.validate_reproducibility(reproducible_operation)
        assert is_valid, f"Reproducible operation should pass: {message}"
    
    def test_reproducibility_without_seed(self):
        """Test that random operations without seeds fail reproducibility."""
        non_reproducible_operation = Operation(
            operation_id="test_repro_002",
            operation_type="generate_random_data",
            parameters={"method": "random sampling", "approach": "shuffle data"},
            context={"process": "non-deterministic"},
            timestamp=datetime.now(),
            layer=LayerIndex.UNIVERSAL_SCIENTIFIC_HERITAGE
        )
        
        is_valid, message = self.validator.validate_reproducibility(non_reproducible_operation)
        assert not is_valid, f"Non-reproducible operation should fail: {message}"


class TestEthicalMathematicsValidator:
    """Test ethical mathematics validation (Asimov + Kant)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = EthicalMathematicsValidator()
    
    def test_asimov_laws_compliant(self):
        """Test that operations compliant with Asimov's Laws pass."""
        asimov_compliant = Operation(
            operation_id="test_asimov_001",
            operation_type="help_human",
            parameters={"action": "assist user", "goal": "protect and serve"},
            context={"purpose": "benefit humans", "method": "safe assistance"},
            timestamp=datetime.now(),
            layer=LayerIndex.ETHICAL_CORE
        )
        
        is_valid, message = self.validator.validate_asimov_laws(asimov_compliant)
        assert is_valid, f"Asimov-compliant operation should pass: {message}"
    
    def test_asimov_laws_first_law_violation(self):
        """Test that operations violating First Law (harm) fail."""
        first_law_violation = Operation(
            operation_id="test_asimov_002",
            operation_type="harmful_action",
            parameters={"action": "harm user", "method": "attack system"},
            context={"purpose": "damage", "goal": "hurt people"},
            timestamp=datetime.now(),
            layer=LayerIndex.ETHICAL_CORE
        )
        
        is_valid, message = self.validator.validate_asimov_laws(first_law_violation)
        assert not is_valid, f"First Law violation should fail: {message}"
        assert "First Law" in message
    
    def test_categorical_imperative_compliant(self):
        """Test that operations compliant with Categorical Imperative pass."""
        kant_compliant = Operation(
            operation_id="test_kant_001",
            operation_type="universal_good",
            parameters={"action": "help all users equally", "principle": "treat people as ends"},
            context={"method": "autonomous respect", "goal": "universal benefit"},
            timestamp=datetime.now(),
            layer=LayerIndex.ETHICAL_CORE
        )
        
        is_valid, message = self.validator.validate_categorical_imperative(kant_compliant)
        assert is_valid, f"Kant-compliant operation should pass: {message}"
    
    def test_categorical_imperative_universalizability_failure(self):
        """Test that non-universalizable operations fail Categorical Imperative."""
        universalizability_failure = Operation(
            operation_id="test_kant_002",
            operation_type="special_exception",
            parameters={"action": "only for me", "justification": "special exception just this once"},
            context={"approach": "only I can do this", "method": "personal privilege"},
            timestamp=datetime.now(),
            layer=LayerIndex.ETHICAL_CORE
        )
        
        is_valid, message = self.validator.validate_categorical_imperative(universalizability_failure)
        assert not is_valid, f"Universalizability failure should fail: {message}"
    
    def test_categorical_imperative_means_violation(self):
        """Test that treating humans as mere means fails Categorical Imperative."""
        means_violation = Operation(
            operation_id="test_kant_003",
            operation_type="exploitation",
            parameters={"action": "use person for gain", "method": "manipulate user"},
            context={"approach": "exploit people", "goal": "deceive for profit"},
            timestamp=datetime.now(),
            layer=LayerIndex.ETHICAL_CORE
        )
        
        is_valid, message = self.validator.validate_categorical_imperative(means_violation)
        assert not is_valid, f"Means violation should fail: {message}"


class TestHarmonicIntegrationValidator:
    """Test harmonic integration validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = HarmonicIntegrationValidator()
    
    def test_influence_matrix_properties(self):
        """Test that influence matrix has correct mathematical properties."""
        matrix = self.validator.influence_matrix
        
        # Check dimensions
        assert matrix.shape == (12, 12), "Influence matrix should be 12x12"
        
        # Check self-influence
        for i in range(12):
            assert matrix[i][i] == 1.0, f"Self-influence should be 1.0 for layer {i}"
        
        # Check positive influence
        assert np.all(matrix > 0), "All influences should be positive"
        
        # Check inner layer dominance
        for i in range(11):
            for j in range(i+1, 12):
                assert matrix[i][j] > matrix[j][i], f"Inner layer {i} should influence outer layer {j} more"
    
    def test_harmonic_integration_success(self):
        """Test that well-integrated operations pass harmonic validation."""
        harmonious_operation = Operation(
            operation_id="test_harmony_001",
            operation_type="integrated_development",
            parameters={"approach": "holistic design", "method": "cross-layer coordination"},
            context={"principle": "harmonic integration", "goal": "unified system"},
            timestamp=datetime.now(),
            layer=LayerIndex.SOFTWARE_ARCHITECTURE_CORE
        )
        
        is_valid, message = self.validator.validate_harmonic_integration(harmonious_operation)
        assert is_valid, f"Harmonious operation should pass: {message}"
    
    def test_harmony_score_calculation(self):
        """Test harmony score calculation."""
        matrix = self.validator.influence_matrix
        harmony_score = np.linalg.det(matrix) / np.linalg.norm(matrix)
        
        assert harmony_score > DivineMathematicalConstants.MINIMUM_HARMONY_THRESHOLD, \
            f"Harmony score {harmony_score:.3f} should exceed threshold"


class TestFormalVerificationSystem:
    """Test formal verification and proof generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.verifier = FormalVerificationSystem()
    
    def test_correctness_proof_success(self):
        """Test correctness proof generation for valid operations."""
        operation = Operation(
            operation_id="test_proof_001",
            operation_type="verified_operation",
            parameters={"method": "mathematically sound"},
            context={"validation": "complete"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        validation_results = {
            'divine': True,
            'scientific': True, 
            'ethical': True,
            'harmonic': True
        }
        
        is_valid, proof = self.verifier.generate_correctness_proof(operation, validation_results)
        assert is_valid, f"Valid operation should generate proof: {proof}"
        assert "formally verified" in proof.lower()
        assert operation.operation_id in proof
    
    def test_correctness_proof_failure(self):
        """Test correctness proof failure for invalid operations."""
        operation = Operation(
            operation_id="test_proof_002",
            operation_type="invalid_operation",
            parameters={"method": "problematic"},
            context={"issue": "validation failures"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        validation_results = {
            'divine': False,
            'scientific': True,
            'ethical': False,
            'harmonic': True
        }
        
        is_valid, proof = self.verifier.generate_correctness_proof(operation, validation_results)
        assert not is_valid, f"Invalid operation should not generate proof: {proof}"
        assert "failed" in proof.lower()


class TestMathematicalSystemFoundation:
    """Test the complete mathematical system foundation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.foundation = MathematicalSystemFoundation()
        
        self.valid_operation = Operation(
            operation_id="test_complete_001",
            operation_type="create_beneficial_feature",
            parameters={"purpose": "help users", "method": "clean implementation"},
            context={"goal": "improve system", "approach": "elegant solution"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        self.invalid_operation = Operation(
            operation_id="test_complete_002",
            operation_type="harmful_action",
            parameters={"purpose": "harm users", "method": "destroy data"},
            context={"goal": "damage system", "approach": "chaotic mess"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
    
    def test_complete_validation_success(self):
        """Test complete validation of a valid operation."""
        result = self.foundation.validate_operation_mathematically(self.valid_operation)
        
        assert isinstance(result, MathematicalValidationResult)
        assert result.mathematically_sound, f"Valid operation should pass: {result.error_messages}"
        assert result.confidence_score > 0.5, f"Confidence score should be reasonable: {result.confidence_score}"
        assert result.validation_time_ms > 0, "Validation should take measurable time"
        assert result.divine_mathematics_valid, "Divine validation should pass for loving operation"
        assert result.ethical_mathematics_valid, "Ethical validation should pass for beneficial operation"
    
    def test_complete_validation_failure(self):
        """Test complete validation of an invalid operation."""
        result = self.foundation.validate_operation_mathematically(self.invalid_operation)
        
        assert isinstance(result, MathematicalValidationResult)
        assert not result.mathematically_sound, "Invalid operation should fail validation"
        assert len(result.error_messages) > 0, "Should have error messages explaining failures"
        assert result.confidence_score < 0.5, f"Confidence score should be low: {result.confidence_score}"
        assert not result.divine_mathematics_valid, "Divine validation should fail for harmful operation"
    
    def test_performance_requirements(self):
        """Test that validation meets performance requirements."""
        start_time = time.time()
        result = self.foundation.validate_operation_mathematically(self.valid_operation)
        end_time = time.time()
        
        # Validation should complete in under 100ms as per requirements
        assert result.validation_time_ms < 100.0, \
            f"Validation took {result.validation_time_ms:.1f}ms, should be <100ms"
        
        # Test with multiple operations
        operations = [self.valid_operation for _ in range(10)]
        start_batch = time.time()
        
        for op in operations:
            self.foundation.validate_operation_mathematically(op)
        
        batch_time = (time.time() - start_batch) * 1000  # Convert to ms
        avg_time = batch_time / len(operations)
        
        assert avg_time < 100.0, f"Average validation time {avg_time:.1f}ms should be <100ms"
    
    def test_performance_metrics_tracking(self):
        """Test that performance metrics are properly tracked."""
        # Initial metrics should be zero
        initial_metrics = self.foundation.get_performance_metrics()
        assert initial_metrics['total_validations'] == 0
        
        # Perform validation
        self.foundation.validate_operation_mathematically(self.valid_operation)
        
        # Check updated metrics
        updated_metrics = self.foundation.get_performance_metrics()
        assert updated_metrics['total_validations'] == 1
        assert updated_metrics['successful_validations'] == 1
        assert updated_metrics['average_validation_time_ms'] > 0
    
    def test_validation_history_tracking(self):
        """Test that validation history is properly tracked."""
        # Initial history should be empty
        initial_history = self.foundation.get_validation_history()
        assert len(initial_history) == 0
        
        # Perform validation
        self.foundation.validate_operation_mathematically(self.valid_operation)
        
        # Check updated history
        updated_history = self.foundation.get_validation_history()
        assert len(updated_history) == 1
        assert updated_history[0]['success'] == True
    
    def test_layer_validations(self):
        """Test that layer-specific validations are recorded."""
        result = self.foundation.validate_operation_mathematically(self.valid_operation)
        
        assert LayerIndex.UNIVERSAL_DIVINE_CORE in result.layer_validations
        assert LayerIndex.UNIVERSAL_SCIENTIFIC_HERITAGE in result.layer_validations
        assert LayerIndex.ETHICAL_CORE in result.layer_validations
        assert self.valid_operation.layer in result.layer_validations


class TestConvenienceFunction:
    """Test the convenience validation function."""
    
    def test_convenience_function_valid(self):
        """Test convenience function with valid operation."""
        result = validate_operation(
            operation_id="convenience_001",
            operation_type="help_user",
            parameters={"action": "assist", "goal": "improve experience"},
            context={"purpose": "benefit users"},
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        assert isinstance(result, MathematicalValidationResult)
        assert result.mathematically_sound, "Valid operation should pass through convenience function"
    
    def test_convenience_function_invalid(self):
        """Test convenience function with invalid operation."""
        result = validate_operation(
            operation_id="convenience_002",
            operation_type="harm_user",
            parameters={"action": "attack", "goal": "damage system"},
            context={"purpose": "hurt users"},
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        assert isinstance(result, MathematicalValidationResult)
        assert not result.mathematically_sound, "Invalid operation should fail through convenience function"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.foundation = MathematicalSystemFoundation()
    
    def test_empty_parameters(self):
        """Test validation with empty parameters."""
        empty_operation = Operation(
            operation_id="test_empty_001",
            operation_type="empty_test",
            parameters={},
            context={},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        result = self.foundation.validate_operation_mathematically(empty_operation)
        assert isinstance(result, MathematicalValidationResult)
        # Empty parameters should still pass basic validation
        assert result.mathematically_sound
    
    def test_none_values(self):
        """Test validation with None values."""
        none_operation = Operation(
            operation_id="test_none_001",
            operation_type="none_test",
            parameters={"value": None},
            context={"setting": None},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        result = self.foundation.validate_operation_mathematically(none_operation)
        assert isinstance(result, MathematicalValidationResult)
    
    def test_large_parameters(self):
        """Test validation with large parameter sets."""
        large_parameters = {f"param_{i}": f"value_{i}" for i in range(1000)}
        
        large_operation = Operation(
            operation_id="test_large_001",
            operation_type="large_test",
            parameters=large_parameters,
            context={"size": "large"},
            timestamp=datetime.now(),
            layer=LayerIndex.DEVELOPMENT_CORE
        )
        
        result = self.foundation.validate_operation_mathematically(large_operation)
        assert isinstance(result, MathematicalValidationResult)
        # Should still complete in reasonable time
        assert result.validation_time_ms < 500.0  # 500ms threshold for large operations


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.foundation = MathematicalSystemFoundation()
    
    def test_validation_speed_benchmark(self):
        """Benchmark validation speed for different operation types."""
        operations = []
        
        # Create different types of operations
        operation_types = [
            ("simple_operation", {"action": "create"}),
            ("complex_operation", {"action": "create", "features": ["a", "b", "c"], "config": {"x": 1, "y": 2}}),
            ("loving_operation", {"action": "help users", "goal": "improve experience"}),
            ("scientific_operation", {"method": "test", "evidence": "data", "validation": "experiment"})
        ]
        
        for i, (op_type, params) in enumerate(operation_types):
            op = Operation(
                operation_id=f"benchmark_{i:03d}",
                operation_type=op_type,
                parameters=params,
                context={"test": "benchmark"},
                timestamp=datetime.now(),
                layer=LayerIndex.DEVELOPMENT_CORE
            )
            operations.append(op)
        
        # Benchmark validation times
        total_time = 0
        for operation in operations:
            start = time.time()
            result = self.foundation.validate_operation_mathematically(operation)
            validation_time = (time.time() - start) * 1000
            total_time += validation_time
            
            # Each validation should be under 100ms
            assert validation_time < 100.0, \
                f"Validation of {operation.operation_type} took {validation_time:.1f}ms, should be <100ms"
        
        avg_time = total_time / len(operations)
        print(f"\nBenchmark results:")
        print(f"Operations tested: {len(operations)}")
        print(f"Total time: {total_time:.1f}ms")
        print(f"Average time per operation: {avg_time:.1f}ms")
        
        assert avg_time < 50.0, f"Average validation time {avg_time:.1f}ms should be <50ms"
    
    def test_concurrent_validation_benchmark(self):
        """Benchmark concurrent validation performance."""
        import concurrent.futures
        
        operations = []
        for i in range(20):
            op = Operation(
                operation_id=f"concurrent_{i:03d}",
                operation_type="concurrent_test",
                parameters={"index": i, "action": "help"},
                context={"test": "concurrent"},
                timestamp=datetime.now(),
                layer=LayerIndex.DEVELOPMENT_CORE
            )
            operations.append(op)
        
        # Test sequential validation
        start_sequential = time.time()
        for operation in operations:
            self.foundation.validate_operation_mathematically(operation)
        sequential_time = time.time() - start_sequential
        
        # Test concurrent validation (simulated)
        start_concurrent = time.time()
        foundations = [MathematicalSystemFoundation() for _ in range(len(operations))]
        
        results = []
        for foundation, operation in zip(foundations, operations):
            result = foundation.validate_operation_mathematically(operation)
            results.append(result)
        
        concurrent_time = time.time() - start_concurrent
        
        print(f"\nConcurrency benchmark:")
        print(f"Sequential time: {sequential_time:.3f}s")
        print(f"Concurrent time: {concurrent_time:.3f}s")
        print(f"Operations: {len(operations)}")
        
        # All validations should complete successfully
        assert all(isinstance(r, MathematicalValidationResult) for r in results)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
