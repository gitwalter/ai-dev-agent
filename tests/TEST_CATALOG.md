# AI-Dev-Agent Test Catalog
=============================

**Last Updated**: 2025-01-31  
**Status**: ✅ Organized and Up-to-Date  
**Total Test Files**: 32 test files across 8 categories  

## 📁 Test Directory Structure

### **🧪 Unit Tests** (`tests/unit/`)
Individual component testing with full isolation.

```
tests/unit/
├── agents/
│   ├── test_agent_system.py              # Core agent system functionality
│   ├── test_test_generator.py            # Test generation agent 
│   └── test_workflow_extraction.py       # Workflow extraction logic
├── prompts/
│   ├── test_advanced_prompt_optimization.py  # Advanced prompt optimization
│   ├── test_prompt_engineering_system.py     # Core prompt engineering
│   ├── test_prompt_interface_imports.py      # Prompt interface validation
│   └── test_prompt_management_infrastructure.py # Prompt infrastructure
├── test_base_agent.py                    # Base agent functionality
├── test_fast_utils.py                    # Fast utility functions
├── test_intelligent_rule_loader.py       # Rule loading system
├── test_quality_assurance.py             # QA system components
├── test_strategic_rule_selector.py       # Rule selection logic
└── test_utils.py                         # General utilities
```

### **🔗 Integration Tests** (`tests/integration/`)
Component interaction and workflow testing.

```
tests/integration/
├── agents/
│   └── test_specialized_subagent_team.py  # Agent team coordination
├── prompts/
│   └── test_prompt_management_system.py   # Prompt system integration
├── test_agent_execution.py               # Agent workflow execution
├── test_api_key_validation.py            # API key configuration
├── test_context_system_validation.py     # Context system validation
├── test_gemini_integration.py            # LLM provider integration
├── test_quality_assurance_integration.py # QA workflow integration
├── agent_tests_standalone.py             # Standalone agent tests
└── real_llm_test_standalone.py           # Real LLM testing
```

### **🔒 Security Tests** (`tests/security/`)
Security, safety, and ethical AI validation.

```
tests/security/
└── test_ethical_ai_protection.py         # Ethical AI protection and safety
```

### **🏗️ Infrastructure Tests** (`tests/infrastructure/`)
System infrastructure and automation testing.

```
tests/infrastructure/
├── test_automated_testing_pipeline.py   # Testing pipeline automation
└── test_git_hooks_automation.py         # Git hooks and automation
```

### **🌊 Workflow Tests** (`tests/workflow/`)
Workflow orchestration and composition testing.

```
tests/workflow/
├── test_context_orchestrator.py         # Context-aware orchestration
├── test_task_analyzer.py                # Task analysis and planning
├── test_workflow_composer.py            # Workflow composition
└── test_workflow_orchestration.py       # Complete workflow orchestration
```

### **🏢 System Tests** (`tests/system/`)
End-to-end system functionality testing.

```
tests/system/
├── agents/                               # System-level agent tests
└── test_complete_workflow.py            # Complete system workflow
```

### **⚡ Performance Tests** (`tests/performance/`)
Performance benchmarking and optimization testing.

```
tests/performance/
# (Directory structure for future performance tests)
```

### **📊 Specialized Test Categories**

#### **🧩 LangGraph Tests** (`tests/langgraph/`)
```
tests/langgraph/
├── integration/
│   └── test_workflow_integration.py     # LangGraph workflow integration
├── unit/
│   ├── test_agent_nodes_advanced.py     # Advanced agent node testing
│   └── test_agent_nodes.py              # Basic agent node testing
├── test_basic_workflow.py               # Basic workflow functionality
├── test_langgraph_workflow_integration.py # LangGraph integration
├── test_simple_integration.py           # Simple integration scenarios
└── test_workflow_manager.py             # Workflow management
```

#### **⚙️ Configuration Tests** (`tests/config/`)
```
tests/config/
└── test_config.py                       # System configuration testing
```

#### **📋 Agile Tests** (`tests/agile/`)
```
tests/agile/
└── test_agile_artifacts_automation.py   # Agile process automation
```

#### **👥 Supervisor Tests** (`tests/supervisor/`)
```
tests/supervisor/
├── test_base_supervisor.py              # Base supervisor functionality
└── test_project_manager_supervisor.py   # Project management supervision
```

#### **🔧 Utility Support**
```
tests/
├── isolated/
│   └── test_test_generator_isolated.py  # Isolated test generator testing
├── scripts/
│   ├── test_agent_prompt_loading.py     # Agent prompt loading
│   └── test_health_monitoring.py        # System health monitoring
├── utils/
│   └── automated_testing/
│       └── test_reporter.py             # Test reporting utilities
├── mocks/                                # Mock objects and utilities
├── fixtures/                             # Test fixtures and data
└── providers/                            # Test provider implementations
```

## 🎯 Test Execution Guide

### **Quick Commands**
```bash
# All tests
pytest tests/

# By category
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/security/      # Security tests only
pytest tests/workflow/      # Workflow tests only

# Specific areas
pytest tests/unit/agents/   # Agent unit tests
pytest tests/unit/prompts/  # Prompt unit tests
pytest tests/integration/agents/  # Agent integration tests

# With coverage
pytest tests/ --cov=agents --cov=utils --cov=workflow

# Fast tests only
pytest tests/unit/test_fast_utils.py -m fast
```

### **Test Environment Setup**
1. **API Keys**: Configure in `.streamlit/secrets.toml`
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **Database**: Initialize test databases as needed
4. **Permissions**: Ensure proper file permissions

## 📊 Test Statistics

- **Total Test Files**: 32
- **Unit Tests**: 13 files
- **Integration Tests**: 9 files  
- **Workflow Tests**: 4 files
- **Security Tests**: 1 file
- **Infrastructure Tests**: 2 files
- **Specialized Tests**: 3 files

## 🔄 Maintenance Guidelines

### **When Adding New Tests**
1. **Choose Correct Category**: Place in appropriate directory
2. **Update This Catalog**: Keep documentation current
3. **Follow Naming**: Use `test_*.py` convention
4. **Update README**: Update relevant directory README

### **When Moving Tests**
1. **Update All References**: Check imports and documentation
2. **Update Catalogs**: Update this file and README files
3. **Verify Paths**: Ensure all paths work correctly
4. **Test Execution**: Verify tests still run properly

## 📚 Documentation Links

- **[Unit Testing Guide](../docs/testing/unit_testing.md)**
- **[Integration Testing Guide](../docs/testing/integration_testing.md)**  
- **[Security Testing Guide](../docs/testing/security_testing.md)**
- **[Testing Best Practices](../docs/testing/README.md)**

---

**🎯 Goal**: 100% test pass rate with zero tolerance for failures  
**📈 Coverage Target**: 90%+ overall, 100% for critical paths  
**🔄 Update Frequency**: After every test reorganization or addition  
