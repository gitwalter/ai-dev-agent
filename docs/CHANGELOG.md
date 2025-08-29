# Changelog

## [Unreleased]

### Fixed
- **PromptManager missing methods**: Added `get_simplified_prompt`, `get_enhanced_prompt`, and `get_best_prompt` methods to support AgentPromptLoader
- **AgentResponse validation errors**: Fixed `create_agent_response` method to only pass fields defined in the AgentResponse model
- **Missing get_llm_model function**: Added function to utils/core/helpers.py with backward compatibility for task_type parameter
- **Import path issues**: Moved helpers.py to utils/core/ and updated utils/__init__.py imports
- **Model selection compatibility**: Updated get_llm_model to accept both task_complexity and task_type parameters

### Changed
- **File organization**: Moved utils/helpers.py to utils/core/helpers.py following project structure guidelines
- **Import patterns**: Updated imports to use organized paths (utils.core.helpers)

### Technical Debt
- **Test failures**: 90 tests passing, 93 failing - main issues resolved, remaining failures are in quality assurance and supervisor modules
- **Pydantic deprecation warnings**: Some deprecated methods still in use (dict() vs model_dump())

## [Previous Sessions]
