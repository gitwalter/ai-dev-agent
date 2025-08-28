# Test Mocks

This directory contains mock objects and test isolation utilities for the AI Development Agent system.

## Quick Reference

For comprehensive mocking guidelines, see **[docs/testing/mocking_guide.md](../../docs/testing/mocking_guide.md)**.

## Mock Structure

This directory provides:
- Mock LLM services and responses
- Mock file system operations
- Mock database connections
- Mock external API calls
- Test isolation utilities

## Using Mocks

```python
from tests.mocks.mock_llm import MockLLM
from tests.mocks.mock_file_manager import MockFileManager

# Use in your tests
mock_llm = MockLLM()
mock_file_manager = MockFileManager()
```

## Mock Categories

- **LLM Mocks**: Mock language model responses
- **File System Mocks**: Mock file operations
- **Database Mocks**: Mock database interactions
- **API Mocks**: Mock external service calls
- **Agent Mocks**: Mock agent behaviors

---

**📖 For complete mocking strategies and examples, see [docs/testing/mocking_guide.md](../../docs/testing/mocking_guide.md)**

**🔗 For all testing documentation, see [docs/testing/](../../docs/testing/README.md)**