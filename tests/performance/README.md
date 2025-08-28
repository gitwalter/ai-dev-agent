# Performance Tests

This directory contains performance tests for the AI Development Agent system.

## Quick Reference

For comprehensive performance testing documentation, see **[docs/testing/performance_testing.md](../../docs/testing/performance_testing.md)**.

## Test Structure

Performance tests focus on:
- Response time validation
- Memory usage monitoring  
- Resource consumption testing
- Load and stress testing
- Scalability validation

## Running Performance Tests

```bash
# Run performance tests
pytest tests/performance/

# Run with detailed output
pytest tests/performance/ -v -s

# Run specific performance test
pytest tests/performance/test_agent_performance.py
```

## Performance Requirements

- **Unit Operations**: < 1 second
- **Integration Operations**: < 5 seconds  
- **End-to-end Workflows**: < 30 seconds
- **Memory Usage**: Within acceptable limits
- **Resource Cleanup**: Complete cleanup after tests

---

**📖 For complete performance testing guidelines and benchmarks, see [docs/testing/performance_testing.md](../../docs/testing/performance_testing.md)**

**🔗 For all testing documentation, see [docs/testing/](../../docs/testing/README.md)**