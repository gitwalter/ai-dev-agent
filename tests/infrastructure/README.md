# Infrastructure Tests

This directory contains comprehensive tests for project infrastructure components that ensure the development environment and automation systems work correctly.

## Test Categories

### Git Hooks Automation (`test_git_hooks_automation.py`)

**Purpose**: Tests the complete git hooks automation system for database management during push/pull operations.

**Test Coverage**:
- ✅ Safe git operations initialization and configuration
- ✅ Git status checking and database file detection
- ✅ Command line interface for `safe_git_operations.py`
- ✅ Pre-merge and post-merge command functionality
- ✅ PowerShell hook execution (Windows)
- ✅ End-to-end push-pull cycle simulation
- ✅ Error handling and edge cases
- ✅ Documentation and compliance verification

**Key Test Classes**:
- `TestGitHooksInfrastructure` - Core functionality tests
- `TestGitHooksEndToEndScenarios` - Complete workflow tests  
- `TestGitHooksErrorScenarios` - Error handling tests
- `TestGitHooksDocumentationAndCompliance` - Quality assurance tests

## Running Infrastructure Tests

### Run All Infrastructure Tests
```bash
# Run all infrastructure tests
python -m pytest tests/infrastructure/ -v

# Run with detailed output
python -m pytest tests/infrastructure/ -v --tb=long

# Run specific test class
python -m pytest tests/infrastructure/test_git_hooks_automation.py::TestGitHooksInfrastructure -v
```

### Run Platform-Specific Tests
```bash
# Run PowerShell tests (Windows only)
python -m pytest tests/infrastructure/ -v -k "powershell"

# Skip PowerShell tests (non-Windows)
python -m pytest tests/infrastructure/ -v -k "not powershell"
```

### Run Individual Test Categories
```bash
# Test git hooks functionality
python -m pytest tests/infrastructure/test_git_hooks_automation.py::TestGitHooksInfrastructure -v

# Test end-to-end scenarios
python -m pytest tests/infrastructure/test_git_hooks_automation.py::TestGitHooksEndToEndScenarios -v

# Test error scenarios
python -m pytest tests/infrastructure/test_git_hooks_automation.py::TestGitHooksErrorScenarios -v
```

## Test Environment Requirements

### Prerequisites
- Git repository (tests skip if not in git repo)
- Python 3.8+ with pytest
- Windows PowerShell (for PowerShell hook tests)
- Project dependencies installed

### Test Dependencies
```bash
# Install test dependencies
pip install pytest pytest-mock

# Install project dependencies
pip install -r requirements.txt
```

## What These Tests Validate

### Critical Infrastructure Components
1. **Git Hooks Work Correctly**
   - Pre-push hooks prepare database for GitHub
   - Post-merge hooks restore development database
   - Both command line and IDE git operations work

2. **Database Automation Functions**
   - Safe git operations handle database conflicts
   - Stashing and unstaging work correctly
   - Error conditions are handled gracefully

3. **Cross-Platform Compatibility**
   - PowerShell hooks work on Windows
   - Python backend works on all platforms
   - Fallback mechanisms function properly

4. **Development Workflow Support**
   - IDE pull button integration works
   - Command line git operations work
   - Database preservation during operations

## Test Results Interpretation

### Expected Results
- ✅ All tests pass: Infrastructure is working correctly
- ⚠️ PowerShell tests skipped: Normal on non-Windows platforms
- ❌ Git hooks missing: Run setup script to install hooks

### Common Issues and Solutions

#### Git Hooks Not Found
```bash
# Install git hooks
python scripts/setup_git_hooks.py

# Verify hooks exist
ls .git/hooks/
```

#### PowerShell Execution Policy (Windows)
```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass (temporary)
powershell -ExecutionPolicy Bypass -File .git/hooks/post-merge.ps1
```

#### Test Database File Conflicts
```bash
# Clean up test artifacts
git checkout -- prompts/prompt_templates.db
git clean -fd
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Infrastructure Tests
on: [push, pull_request]

jobs:
  infrastructure-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pytest pytest-mock
          pip install -r requirements.txt
      - name: Run infrastructure tests
        run: |
          python -m pytest tests/infrastructure/ -v --tb=short
```

### Local Development Hooks
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
echo "Running infrastructure tests..."
python -m pytest tests/infrastructure/ -v --tb=short
if [ $? -ne 0 ]; then
    echo "Infrastructure tests failed. Please fix before committing."
    exit 1
fi
```

## Test Maintenance

### Adding New Infrastructure Tests
1. **Follow naming convention**: `test_[component]_[functionality].py`
2. **Use proper test classes**: Group related tests logically
3. **Include documentation tests**: Verify docstrings and comments
4. **Add error scenario tests**: Test failure conditions
5. **Update this README**: Document new test coverage

### Updating Existing Tests
1. **Maintain backward compatibility**: Don't break existing tests
2. **Update documentation**: Reflect changes in README
3. **Test on multiple platforms**: Verify Windows/Linux compatibility
4. **Follow excellence standards**: Comprehensive coverage, no silent failures

## Excellence Standards Applied

### Test Quality Requirements
- ✅ **100% functionality coverage**: All infrastructure components tested
- ✅ **Error exposure**: No silent failures, all errors properly raised
- ✅ **Evidence-based validation**: Tests execute actual commands and verify results
- ✅ **Platform compatibility**: Tests work on Windows and Unix-like systems
- ✅ **Documentation compliance**: All code properly documented and tested

### Test Organization Standards
- ✅ **Logical grouping**: Tests organized by functionality and scenario type
- ✅ **Clear naming**: Test names describe exactly what is being tested
- ✅ **Proper setup/teardown**: Each test has clean environment
- ✅ **Comprehensive coverage**: All code paths and error conditions tested
- ✅ **Performance consideration**: Tests run efficiently and don't interfere with each other

## Related Documentation

- [Git Pull Conflicts Solution](../../docs/troubleshooting/git_pull_conflicts.md)
- [Database Automation Guide](../../docs/guides/database/database_automation_guide.md)
- [Testing Guide](../README.md)
- [Development Setup](../../README.md)

## Support and Troubleshooting

### Getting Help
1. **Check test output**: Use `-v --tb=long` for detailed error information
2. **Review logs**: Check git hook logs in `.git/hooks.log`
3. **Verify setup**: Ensure all prerequisites are installed
4. **Check documentation**: Review related guides for setup instructions

### Reporting Issues
When reporting infrastructure test failures, include:
- Operating system and Python version
- Complete test output with `-v --tb=long`
- Git repository status (`git status`)
- Hook files content (if relevant)
- Steps to reproduce the issue

**Remember**: Infrastructure tests verify that your development environment works correctly. If tests fail, it indicates real issues that could affect your development workflow.
