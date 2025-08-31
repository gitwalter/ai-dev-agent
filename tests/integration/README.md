# Integration Tests

This directory contains integration tests for the AI Development Agent system.

## Quick Reference

For comprehensive integration testing documentation, see **[docs/testing/integration_testing.md](../../docs/testing/integration_testing.md)**.

## Test Structure

```
tests/integration/
├── agents/
│   └── test_specialized_subagent_team.py  # Specialized agent team tests
├── prompts/
│   └── test_prompt_management_system.py   # Prompt system integration
├── test_agent_execution.py           # Agent workflow integration
├── test_api_key_validation.py        # API key configuration tests
├── test_context_system_validation.py # Context system validation
├── test_gemini_integration.py        # LLM integration testing
├── test_quality_assurance_integration.py # QA workflow tests
├── agent_tests_standalone.py         # Standalone agent tests
└── real_llm_test_standalone.py       # Real LLM integration tests
```

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run with coverage
pytest tests/integration/ --cov=src

# Run specific test
pytest tests/integration/test_agent_execution.py -v
```

## Test Environment

- Valid API keys required in `.streamlit/secrets.toml`
- Test database configuration
- See [docs/testing/](../../docs/testing/) for complete setup guide

## Key Testing Principles

1. **Component Interaction**: Test how components work together
2. **Data Flow**: Verify data flows correctly between agents
3. **Error Propagation**: Test error handling across components
4. **Real Functionality**: Tests assert working, productive code

---

**📖 For complete integration testing guidelines, best practices, and detailed examples, see [docs/testing/integration_testing.md](../../docs/testing/integration_testing.md)**

**🔗 For all testing documentation, see [docs/testing/](../../docs/testing/README.md)**