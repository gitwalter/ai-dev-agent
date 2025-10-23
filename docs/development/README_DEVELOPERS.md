# AI-Dev-Agent: Developer Documentation
=====================================

**Fast, Free, Intelligent AI Development System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 🚀 **Quick Start (2 Minutes)**

### **Option 1: Docker (Recommended)**
```bash
# Clone and start
git clone https://github.com/ai-dev-agent/ai-dev-agent.git
cd ai-dev-agent

# One-command setup (Windows)
.\scripts\quick_start.ps1

# One-command setup (Linux/Mac)
./scripts/quick_start.sh
```

### **Option 2: Local Python**
```bash
# Setup
git clone https://github.com/ai-dev-agent/ai-dev-agent.git
cd ai-dev-agent
pip install -r requirements.txt

# Configure (create .streamlit/secrets.toml)
echo '[default]' > .streamlit/secrets.toml
echo 'GEMINI_API_KEY = "your-key-here"' >> .streamlit/secrets.toml

# Run
python run_demo.py
```

## 🎯 **What You Get**

### **Core Features**
- **🤖 Intelligent Agents**: Context-aware agents for coding, testing, debugging
- **📋 Agile Automation**: Automated user stories, sprint management, backlog tracking
- **🔍 Smart Research**: Automatic research and best practice application
- **🛡️ Safety First**: Built-in error handling and validation
- **📊 Real-time Monitoring**: System health and performance tracking

### **Developer Benefits**
- **Zero Setup Time**: Docker container with everything pre-configured
- **Free Forever**: No paid APIs required (uses free Google Gemini)
- **Production Ready**: Enterprise-grade architecture and patterns
- **Fully Tested**: Comprehensive test suite with >95% coverage
- **Well Documented**: Complete docs with examples and tutorials

## 🛠️ **System Architecture**

### **Onion Architecture (8 Layers)**
```
🧄 AI-Dev-Agent Architecture
├── 🌟 Silent Foundation (Spiritual/Philosophical Principles)
├── 🎯 Core Foundation (Safety, Ethics, Quality)
├── 🔧 Infrastructure (Databases, APIs, Monitoring)
├── 🏗️ Domain (Business Logic, Rules, Workflows)
├── 🎮 Application (Use Cases, Orchestration)
├── 📡 Interface (APIs, UIs, External Integration)
├── 🚀 Presentation (User Experience, Visualization)
└── 🌐 External (Third-party Services, Hardware)
```

### **Agent System**
```python
# Context-aware agent selection
@engineering  # For coding tasks
@debug        # For troubleshooting
@agile        # For project management
@research     # For knowledge gathering
@security     # For safety validation
```

### **Operating Modes**
- **Technical Mode**: Pure software engineering focus
- **Research Mode**: Deep investigation and analysis
- **Agile Mode**: Project management and tracking
- **Debug Mode**: Problem solving and optimization

## 📚 **Usage Examples**

### **1. Web API Development**
```python
# examples/example_1_web_api_development.py
from ai_dev_agent import TechnicalAgent

agent = TechnicalAgent(mode="@engineering")

# Automatically generates:
# - FastAPI application with proper structure
# - Comprehensive test suite
# - Documentation and OpenAPI spec
# - Docker configuration
# - CI/CD pipeline setup

result = agent.create_web_api(
    name="user_management_api",
    features=["authentication", "user_crud", "permissions"],
    database="postgresql"
)
```

### **2. Intelligent Test Generation**
```python
# examples/gem_2_intelligent_test_generator.py
from ai_dev_agent import TestingAgent

agent = TestingAgent(mode="@test")

# Generates comprehensive test suites
test_suite = agent.generate_tests(
    target_code="src/user_service.py",
    coverage_target=95,
    test_types=["unit", "integration", "edge_case"]
)

# Includes:
# - Unit tests with mocking
# - Integration tests with test data
# - Edge case and error condition tests
# - Performance and load tests
```

### **3. Smart API Gateway**
```python
# examples/community_gems/gem_04_smart_api_gateway.py
from ai_dev_agent import InfrastructureAgent

agent = InfrastructureAgent(mode="@infrastructure")

# Creates production-ready API gateway
gateway = agent.create_api_gateway(
    services=["user-service", "payment-service", "notification-service"],
    features=["rate_limiting", "authentication", "monitoring", "caching"]
)

# Includes:
# - Intelligent routing and load balancing
# - Security and rate limiting
# - Health checks and monitoring
# - Automatic documentation
```

## 🔧 **Configuration**

### **Environment Setup**
```bash
# .env file
GEMINI_API_KEY=your_free_google_api_key
LOG_LEVEL=INFO
DEVELOPMENT_MODE=true
AUTO_SAVE=true
```

### **Streamlit Configuration**
```toml
# .streamlit/secrets.toml
[default]
GEMINI_API_KEY = "your-key-here"
DATABASE_URL = "sqlite:///ai_dev_agent.db"
ENABLE_MONITORING = true
AUTO_BACKUP = true
```

### **Docker Configuration**
```yaml
# docker-compose.yml (included)
version: '3.8'
services:
  ai-dev-agent:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - "./workspace:/app/workspace"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

## 🧪 **Testing**

### **Run All Tests**
```bash
# Docker environment
docker-compose exec ai-dev-agent pytest tests/ -v

# Local environment
pytest tests/ -v --cov=src/ --cov-report=html
```

### **Test Categories**
- **Unit Tests**: Individual component testing
- **Integration Tests**: System interaction testing
- **LangGraph Tests**: Workflow and agent testing
- **System Tests**: End-to-end scenario testing
- **Performance Tests**: Load and stress testing

### **Test Coverage**
```bash
# Generate coverage report
pytest tests/ --cov=src/ --cov-report=html
open htmlcov/index.html  # View detailed coverage
```

## 📊 **Monitoring & Observability**

### **System Health**
```python
# Real-time system monitoring
from ai_dev_agent.monitoring import SystemMonitor

monitor = SystemMonitor()
health = monitor.get_system_health()

print(f"System Status: {health.status}")
print(f"Active Agents: {health.active_agents}")
print(f"Memory Usage: {health.memory_usage}%")
print(f"Response Time: {health.avg_response_time}ms")
```

### **Agent Performance**
```python
# Agent-specific metrics
agent_metrics = monitor.get_agent_metrics("engineering")
print(f"Success Rate: {agent_metrics.success_rate}%")
print(f"Avg Processing Time: {agent_metrics.avg_processing_time}ms")
print(f"Tasks Completed: {agent_metrics.tasks_completed}")
```

### **Built-in Dashboards**
- **System Dashboard**: Overall health and performance
- **Agent Dashboard**: Individual agent metrics and logs
- **Project Dashboard**: Agile tracking and progress
- **Quality Dashboard**: Code quality and test metrics

## 🔍 **Debugging & Troubleshooting**

### **Debug Mode**
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug agent
from ai_dev_agent import DebugAgent
debugger = DebugAgent(mode="@debug")
debugger.diagnose_system()
```

### **Common Issues**
| Issue | Solution |
|-------|----------|
| API Key Error | Set `GEMINI_API_KEY` in `.streamlit/secrets.toml` |
| Import Errors | Run `pip install -r requirements.txt` |
| Permission Errors | Check file permissions, run as appropriate user |
| Port Conflicts | Change port in `docker-compose.yml` or stop conflicting services |
| Memory Issues | Increase Docker memory allocation or use local Python |

### **Log Analysis**
```bash
# View system logs
docker-compose logs ai-dev-agent

# View specific agent logs
tail -f logs/agent_engineering.log

# Search for errors
grep "ERROR" logs/*.log
```

## 🚀 **Deployment**

### **Local Development**
```bash
# Development server
python run_demo.py

# With hot reload
streamlit run demo/technical_demo_system.py --server.runOnSave true
```

### **Production Docker**
```bash
# Build production image
docker build -t ai-dev-agent:prod .

# Run production container
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -v $(pwd)/workspace:/app/workspace \
  ai-dev-agent:prod
```

### **Cloud Deployment**
```bash
# Deploy to cloud (example: Google Cloud Run)
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-dev-agent
gcloud run deploy --image gcr.io/PROJECT-ID/ai-dev-agent --platform managed
```

## 🤝 **Contributing**

### **Development Workflow**
1. **Fork & Clone**: Fork the repository and clone locally
2. **Branch**: Create feature branch (`git checkout -b feature/amazing-feature`)
3. **Develop**: Write code following our standards
4. **Test**: Ensure all tests pass (`pytest tests/`)
5. **Document**: Update documentation as needed
6. **Pull Request**: Submit PR with clear description

### **Code Standards**
- **Python Style**: PEP 8 compliance with 120-character line limit
- **Type Hints**: All functions must have type annotations
- **Documentation**: Docstrings for all public functions and classes
- **Testing**: 95%+ test coverage required
- **Architecture**: Follow established onion architecture patterns

### **Development Setup**
```bash
# Development dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Run linting
flake8 src/ tests/
pylint src/ tests/

# Run type checking
mypy src/
```

## 📖 **Documentation**

### **Complete Documentation**
- **[Architecture Guide](docs/architecture/)** - System design and patterns
- **[API Reference](docs/api/)** - Complete API documentation
- **[User Guide](docs/guides/)** - Step-by-step tutorials
- **[Examples](examples/)** - Working code examples
- **[Agile Documentation](docs/agile/)** - Project management and tracking

### **Video Tutorials**
- **Getting Started** (5 minutes): Basic setup and first agent
- **Advanced Features** (15 minutes): Custom agents and workflows
- **Production Deployment** (10 minutes): Docker and cloud deployment
- **Contributing Guide** (8 minutes): Development workflow

### **Community Resources**
- **[Discord Server](https://discord.gg/ai-dev-agent)** - Community chat and support
- **[GitHub Discussions](https://github.com/ai-dev-agent/ai-dev-agent/discussions)** - Technical discussions
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/ai-dev-agent)** - Q&A and troubleshooting

## 🔒 **Security**

### **Security Features**
- **Input Validation**: All user inputs validated and sanitized
- **API Key Protection**: Secure storage and transmission of API keys
- **Code Execution Safety**: Sandboxed execution environment
- **Audit Logging**: Comprehensive logging of all system operations

### **Security Best Practices**
```python
# Secure API key handling
import streamlit as st
api_key = st.secrets["GEMINI_API_KEY"]  # Never hardcode keys

# Input validation
from ai_dev_agent.security import validate_input
user_input = validate_input(raw_input, max_length=1000, allow_code=False)

# Sandboxed execution
from ai_dev_agent.execution import SafeExecutor
executor = SafeExecutor(timeout=30, memory_limit="256MB")
result = executor.run(code, sandbox=True)
```

### **Vulnerability Reporting**
- **Security Issues**: Email security@ai-dev-agent.org
- **Bug Bounty**: Responsible disclosure with recognition
- **Response Time**: Security issues addressed within 24 hours

## 📊 **Performance**

### **Benchmarks**
- **Startup Time**: < 3 seconds (Docker), < 1 second (local)
- **Response Time**: < 100ms for simple tasks, < 5s for complex tasks
- **Memory Usage**: < 512MB base, scales with complexity
- **Throughput**: 100+ requests/minute per agent

### **Optimization Tips**
```python
# Enable caching for better performance
from ai_dev_agent.caching import enable_cache
enable_cache(redis_url="redis://localhost:6379")

# Use async for better concurrency
import asyncio
from ai_dev_agent import AsyncAgent

async def process_multiple_tasks(tasks):
    agent = AsyncAgent()
    results = await asyncio.gather(
        *[agent.process(task) for task in tasks]
    )
    return results
```

## 🎯 **Roadmap**

### **Current Version (v1.0)**
- ✅ Core agent system with context awareness
- ✅ Docker containerization and easy deployment
- ✅ Comprehensive test suite and documentation
- ✅ Agile automation and project tracking

### **Next Release (v1.1)**
- 🔄 Multi-language support (JavaScript, Go, Rust)
- 🔄 Advanced agent swarm coordination
- 🔄 Enhanced monitoring and observability
- 🔄 Visual workflow builder

### **Future Releases (v2.0+)**
- 📋 Cloud-native deployment with auto-scaling
- 📋 Advanced AI model integration (local LLMs)
- 📋 Plugin ecosystem and marketplace
- 📋 Enterprise features and support

## 📞 **Support**

### **Community Support**
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time community help
- **Stack Overflow**: Technical Q&A
- **Documentation**: Comprehensive guides and examples

### **Professional Support**
- **Enterprise Support**: 24/7 support with SLA
- **Custom Development**: Tailored solutions for specific needs
- **Training & Consulting**: Team training and best practices
- **Integration Services**: Help with complex integrations

### **Contact**
- **Email**: support@ai-dev-agent.org
- **Documentation**: https://docs.ai-dev-agent.org
- **Community**: https://community.ai-dev-agent.org

---

## 🏆 **Why Choose AI-Dev-Agent?**

### **Unique Advantages**
1. **🆓 Completely Free**: No paid APIs or subscriptions required
2. **⚡ Production Ready**: Enterprise-grade architecture from day one
3. **🧠 Intelligent**: Context-aware agents that learn and adapt
4. **🛡️ Safe & Secure**: Built-in safety measures and validation
5. **📈 Scalable**: From single developer to enterprise teams
6. **🌍 Open Source**: Full transparency and community-driven

### **Perfect For**
- **Startups**: Rapid prototyping and MVP development
- **Enterprises**: Scalable automation and quality assurance
- **Individual Developers**: Productivity enhancement and learning
- **Teams**: Collaboration and agile project management
- **Educators**: Teaching modern development practices

**Start building intelligent software systems today!** 🚀

```bash
git clone https://github.com/ai-dev-agent/ai-dev-agent.git
cd ai-dev-agent && ./scripts/quick_start.ps1
```