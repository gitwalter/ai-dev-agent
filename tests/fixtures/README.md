# Test Fixtures

This directory contains test fixtures and shared test data for the AI Development Agent system.

## Quick Reference

For comprehensive test fixtures documentation, see **[docs/testing/test_fixtures.md](../../docs/testing/test_fixtures.md)**.

## Fixture Structure

This directory provides:
- Sample project data
- Test state configurations
- Mock responses and data
- Shared test utilities
- Common test setup code

## Using Fixtures

```python
import pytest
from tests.fixtures.sample_data import sample_project_state

@pytest.fixture
def project_state():
    """Sample project state for testing."""
    return sample_project_state()
```

## Fixture Categories

- **Project Fixtures**: Sample project configurations
- **State Fixtures**: Workflow state data
- **Response Fixtures**: Mock LLM responses
- **Data Fixtures**: Test input and output data
- **Setup Fixtures**: Common test setup utilities

---

**📖 For complete fixtures usage and examples, see [docs/testing/test_fixtures.md](../../docs/testing/test_fixtures.md)**

**🔗 For all testing documentation, see [docs/testing/](../../docs/testing/README.md)**