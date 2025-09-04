# Getting Started with AI-Dev-Agent

**Complete implementation guide for setting up and using the multi-agent development framework.**

---

## 🎯 **Quick Start Overview**

The AI-Dev-Agent framework provides **intelligent automation** for software development workflows through **coordinated AI agents**. This guide will get you from installation to productive usage in **under 30 minutes**.

### **What You'll Achieve**
- **Complete system setup** with all dependencies configured
- **First working example** demonstrating agent coordination
- **Understanding of core concepts** for effective usage
- **Foundation for advanced customization** and integration

---

## ⚡ **5-Minute Quick Start**

### **Prerequisites Check**
```bash
# Verify Python installation (3.8+ required)
python --version

# Verify Anaconda installation (recommended)
conda --version

# Verify Git installation
git --version
```

### **Installation**
```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-dev-agent.git
cd ai-dev-agent

# 2. Create environment
conda env create -f environment.yml
conda activate ai-dev-agent

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import ai_dev_agent; print('Installation successful!')"
```

### **First Test Run**
```bash
# Launch the Vibe Coding interface
streamlit run apps/vibe_coding_ui.py

# In another terminal, test the agent system
python apps/main.py --test

# Run basic tests
pytest tests/unit/test_basic_functionality.py -v
```

**Expected Result**: All commands should complete without errors, and you should see the Streamlit interface in your browser.

---

## 🏗️ **System Architecture Overview**

### **Core Components**
```
AI-Dev-Agent Framework
├── Workflow Orchestration Engine    # Central coordination
├── Specialized Agents              # Requirements, Architecture, Code, Test
├── Context-Aware Rule System       # Intelligent behavior adaptation
├── Quality Assurance Pipeline      # Multi-layer validation
└── Integration APIs                # External tool integration
```

### **How Agents Work Together**
1. **Requirements Agent** → Analyzes and structures project requirements
2. **Architecture Agent** → Designs system architecture and tech stack
3. **Code Generation Agent** → Implements code based on architecture
4. **Testing Agent** → Generates comprehensive test suites
5. **Quality Review Agent** → Validates and optimizes deliverables

---

## 🚀 **Step-by-Step Implementation**

### **Step 1: Environment Configuration**

#### **Anaconda Setup (Recommended)**
```bash
# Create dedicated environment
conda create -n ai-dev-agent python=3.11
conda activate ai-dev-agent

# Install core dependencies
conda install -c conda-forge langchain streamlit pytest

# Install additional requirements
pip install -r requirements.txt
```

#### **Alternative: Virtual Environment**
```bash
# Create virtual environment
python -m venv ai-dev-agent-env

# Activate environment (Windows)
ai-dev-agent-env\Scripts\activate

# Activate environment (Linux/Mac)
source ai-dev-agent-env/bin/activate

# Install requirements
pip install -r requirements.txt
```

### **Step 2: Configuration Setup**

#### **API Configuration**
```bash
# Copy configuration template
cp config/config.template.yml config/config.yml

# Edit configuration file
# Add your API keys and preferences
```

#### **Example Configuration**
```yaml
# config/config.yml
api_config:
  gemini:
    api_key: "your-gemini-api-key"
    model: "gemini-pro"
  
agent_config:
  max_concurrent_agents: 4
  default_timeout: 300
  retry_attempts: 3

workflow_config:
  quality_gates_enabled: true
  automatic_validation: true
  progress_notifications: true
```

### **Step 3: First Project Creation**

#### **Using the Vibe Coding Interface**
```bash
# Launch the web interface
streamlit run apps/vibe_coding_ui.py
```

**In the interface:**
1. **Enter Project Description**: "Create a simple REST API for user management"
2. **Select Configuration**: Choose default settings for first run
3. **Start Workflow**: Click "Generate Project" 
4. **Monitor Progress**: Watch agents coordinate to build your project

#### **Using the Command Line Interface**
```bash
# Create project using CLI
python apps/main.py create-project \
    --description "Simple REST API for user management" \
    --output-dir ./generated_projects/user_api \
    --config config/config.yml
```

### **Step 4: Understanding the Output**

#### **Generated Project Structure**
```
generated_projects/user_api/
├── README.md                 # Project documentation
├── requirements.txt          # Dependencies
├── src/                     # Source code
│   ├── api/                 # API implementation
│   ├── models/              # Data models
│   └── tests/               # Test suite
├── docs/                    # Additional documentation
├── config/                  # Configuration files
└── scripts/                 # Utility scripts
```

#### **Quality Reports**
```
reports/
├── architecture_analysis.md    # Architecture decisions and rationale
├── code_quality_report.md     # Code quality metrics and analysis
├── test_coverage_report.html  # Comprehensive test coverage
└── performance_analysis.md    # Performance characteristics
```

---

## 🔧 **Core Usage Patterns**

### **Pattern 1: Single-Agent Task Execution**

#### **Requirements Analysis**
```python
from ai_dev_agent.agents import RequirementsAgent

# Initialize agent
req_agent = RequirementsAgent()

# Analyze requirements
requirements = req_agent.analyze(
    description="Build a task management system",
    context={"domain": "productivity", "users": "small teams"}
)

print(f"Generated {len(requirements.use_cases)} use cases")
print(f"Identified {len(requirements.acceptance_criteria)} acceptance criteria")
```

#### **Architecture Design**
```python
from ai_dev_agent.agents import ArchitectureAgent

# Initialize agent
arch_agent = ArchitectureAgent()

# Design architecture
architecture = arch_agent.design(
    requirements=requirements,
    constraints={"technology": "Python", "deployment": "cloud"}
)

print(f"Recommended technology stack: {architecture.tech_stack}")
print(f"Architecture pattern: {architecture.pattern}")
```

### **Pattern 2: Multi-Agent Workflow**

#### **Coordinated Development Workflow**
```python
from ai_dev_agent import WorkflowOrchestrator

# Initialize orchestrator
orchestrator = WorkflowOrchestrator()

# Add agents to workflow
orchestrator.add_agent("requirements", RequirementsAgent())
orchestrator.add_agent("architecture", ArchitectureAgent())
orchestrator.add_agent("code_gen", CodeGenerationAgent())
orchestrator.add_agent("testing", TestingAgent())

# Execute coordinated workflow
result = orchestrator.execute(
    project_description="E-commerce product catalog API",
    config={"quality_level": "production", "testing": "comprehensive"}
)

# Access results
print(f"Project status: {result.status}")
print(f"Generated files: {len(result.generated_files)}")
print(f"Test coverage: {result.test_coverage}%")
```

### **Pattern 3: Custom Agent Integration**

#### **Creating Custom Domain Agent**
```python
from ai_dev_agent.base import BaseAgent

class DataScienceAgent(BaseAgent):
    """Specialized agent for data science projects."""
    
    def __init__(self):
        super().__init__()
        self.specialization = "data_science"
        
    def analyze_data_requirements(self, project_spec):
        """Analyze data science specific requirements."""
        return {
            "data_sources": self.identify_data_sources(project_spec),
            "analysis_methods": self.recommend_methods(project_spec),
            "visualization_needs": self.assess_visualization(project_spec)
        }
        
    def generate_pipeline(self, requirements):
        """Generate data processing pipeline."""
        pipeline_config = self.design_pipeline(requirements)
        return self.implement_pipeline(pipeline_config)

# Use custom agent
ds_agent = DataScienceAgent()
data_requirements = ds_agent.analyze_data_requirements(project_description)
```

---

## 📊 **Monitoring and Optimization**

### **Performance Monitoring**

#### **Real-Time Metrics**
```python
from ai_dev_agent.monitoring import PerformanceMonitor

# Initialize monitoring
monitor = PerformanceMonitor()

# Track workflow execution
with monitor.track_workflow("project_generation"):
    result = orchestrator.execute(project_description)

# View performance metrics
metrics = monitor.get_metrics()
print(f"Execution time: {metrics.execution_time}")
print(f"Resource usage: {metrics.resource_usage}")
print(f"Quality score: {metrics.quality_score}")
```

#### **Quality Metrics Dashboard**
```bash
# Launch monitoring dashboard
streamlit run apps/monitoring_dashboard.py

# View metrics in browser
# http://localhost:8501
```

### **System Optimization**

#### **Configuration Tuning**
```yaml
# config/optimization.yml
performance_tuning:
  agent_pool_size: 6           # Adjust based on available resources
  concurrent_workflows: 2      # Number of parallel workflows
  cache_size: 1000            # Cache size for common patterns
  timeout_settings:
    default: 300              # 5 minutes default timeout
    code_generation: 600      # 10 minutes for code generation
    testing: 900             # 15 minutes for comprehensive testing
```

#### **Resource Management**
```python
from ai_dev_agent.optimization import ResourceOptimizer

# Initialize optimizer
optimizer = ResourceOptimizer()

# Optimize resource allocation
optimal_config = optimizer.optimize_for_workload(
    expected_projects_per_hour=10,
    complexity_distribution={"simple": 0.4, "medium": 0.4, "complex": 0.2},
    resource_constraints={"max_memory": "8GB", "max_cpu": "4 cores"}
)

# Apply optimization
orchestrator.update_config(optimal_config)
```

---

## 🔗 **Integration Examples**

### **IDE Integration**

#### **VS Code Extension**
```json
{
  "name": "ai-dev-agent-integration",
  "version": "1.0.0",
  "contributes": {
    "commands": [
      {
        "command": "aiDevAgent.generateCode",
        "title": "Generate Code with AI-Dev-Agent"
      },
      {
        "command": "aiDevAgent.analyzeRequirements", 
        "title": "Analyze Requirements"
      }
    ]
  }
}
```

#### **Integration Code**
```python
# VS Code extension integration
import vscode
from ai_dev_agent import WorkflowOrchestrator

def generate_code_command():
    """VS Code command for code generation."""
    # Get selected text or current file
    selection = vscode.window.active_text_editor.selection
    text = vscode.window.active_text_editor.document.get_text(selection)
    
    # Initialize AI-Dev-Agent
    orchestrator = WorkflowOrchestrator()
    
    # Generate code
    result = orchestrator.execute(text)
    
    # Insert generated code
    vscode.window.active_text_editor.edit(lambda edit: 
        edit.replace(selection, result.generated_code)
    )
```

### **CI/CD Pipeline Integration**

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/ai-dev-agent.yml
name: AI-Dev-Agent Integration
on: [push, pull_request]

jobs:
  ai-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup AI-Dev-Agent
        run: |
          pip install ai-dev-agent
          
      - name: Analyze Code Quality
        run: |
          python -m ai_dev_agent analyze \
            --path ./src \
            --output ./reports/quality_analysis.json
            
      - name: Generate Tests
        run: |
          python -m ai_dev_agent generate-tests \
            --path ./src \
            --output ./tests/generated
            
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: ai-analysis-reports
          path: ./reports/
```

### **API Integration**

#### **RESTful API Usage**
```python
import requests

# API endpoint
api_base = "http://localhost:8000/api/v1"

# Create project via API
response = requests.post(f"{api_base}/projects", json={
    "description": "Social media analytics dashboard",
    "requirements": {
        "technology": "React + Python",
        "deployment": "AWS",
        "timeline": "2 weeks"
    }
})

project_id = response.json()["project_id"]

# Monitor progress
status_response = requests.get(f"{api_base}/projects/{project_id}/status")
print(f"Project status: {status_response.json()['status']}")

# Download results
results = requests.get(f"{api_base}/projects/{project_id}/results")
```

---

## 🔍 **Troubleshooting Guide**

### **Common Issues and Solutions**

#### **Installation Issues**
```bash
# Issue: Dependency conflicts
# Solution: Use clean environment
conda create -n ai-dev-agent-clean python=3.11
conda activate ai-dev-agent-clean
pip install --no-cache-dir -r requirements.txt

# Issue: API key not found
# Solution: Check environment variables
echo $GEMINI_API_KEY
# Or check config file
cat config/config.yml | grep api_key
```

#### **Performance Issues**
```python
# Issue: Slow execution
# Solution: Enable performance profiling
from ai_dev_agent.profiling import ProfileManager

with ProfileManager() as profiler:
    result = orchestrator.execute(description)

# View performance bottlenecks
profiler.print_stats()
```

#### **Memory Issues**
```yaml
# Issue: Out of memory
# Solution: Adjust configuration
resource_limits:
  max_memory_per_agent: "2GB"
  enable_memory_monitoring: true
  cleanup_interval: 300  # 5 minutes
```

### **Debug Mode**

#### **Enable Detailed Logging**
```python
import logging
from ai_dev_agent import configure_logging

# Enable debug logging
configure_logging(level=logging.DEBUG, 
                 output_file="debug.log",
                 include_timestamps=True)

# Execute with detailed logs
result = orchestrator.execute(description)
```

#### **Agent Execution Tracing**
```python
from ai_dev_agent.debug import ExecutionTracer

# Enable execution tracing
tracer = ExecutionTracer()
orchestrator.add_tracer(tracer)

# Execute and analyze trace
result = orchestrator.execute(description)
trace_report = tracer.generate_report()

print(f"Total execution steps: {trace_report.step_count}")
print(f"Agent interactions: {len(trace_report.agent_interactions)}")
```

---

## 📚 **Next Steps**

### **Learn More**
- **[Architecture Guide](../architecture/system_overview.md)** - Deep dive into system architecture
- **[API Reference](../api/)** - Complete API documentation
- **[Advanced Configuration](../advanced/configuration.md)** - Advanced configuration options
- **[Custom Agent Development](../advanced/agents.md)** - Building custom agents

### **Community and Support**
- **[GitHub Issues](https://github.com/your-username/ai-dev-agent/issues)** - Report bugs and request features
- **[Discussions](https://github.com/your-username/ai-dev-agent/discussions)** - Community discussion and help
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[FAQ](../FAQ.md)** - Frequently asked questions

### **Advanced Usage**
- **[Performance Optimization](../advanced/performance.md)** - Optimizing for production use
- **[Enterprise Integration](../enterprise/)** - Enterprise-grade deployment
- **[Custom Workflows](../advanced/workflows.md)** - Creating custom workflows
- **[Plugin Development](../advanced/plugins.md)** - Extending functionality

---

**You're now ready to use AI-Dev-Agent for automated software development. Start with simple projects and gradually explore advanced features as you become more familiar with the system.**
