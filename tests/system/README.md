# System Tests

This directory contains system tests for the AI Development Agent system.

## Quick Reference

For comprehensive system testing documentation, see **[docs/testing/system_testing.md](../../docs/testing/system_testing.md)**.

## Test Structure

System tests validate:
- Complete end-to-end workflows
- Multi-agent collaboration
- Real LLM integration
- Full system functionality
- User scenarios and use cases

## Running System Tests

```bash
# Run system tests  
pytest tests/system/

# Run with detailed output
pytest tests/system/ -v -s

# Run specific system test
pytest tests/system/test_complete_workflow.py
```

## System Test Categories

- **End-to-End Workflows**: Complete project generation flows
- **Multi-Agent Scenarios**: Agent collaboration and handoffs
- **Real LLM Integration**: Testing with actual LLM services
- **User Scenarios**: Real-world usage patterns
- **System Integration**: Full system functionality validation

---

**📖 For complete system testing guidelines and scenarios, see [docs/testing/system_testing.md](../../docs/testing/system_testing.md)**

**🔗 For all testing documentation, see [docs/testing/](../../docs/testing/README.md)**