# AI-Dev-Agent: Practical AI Development Toolkit

**A pedagogical toolkit for building AI agent systems with practical software development techniques.**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Research%20Foundation-orange?style=flat-square)

---

## What This Is

This is a **foundational research project** that teaches how to build AI agent systems using practical software development techniques. It's designed for learning and extracting production-ready components.

**Not a production system** - Use this to learn patterns and extract clean software artifacts.

---

## Key Features

### 🤖 **Agent Framework**
- LangChain/LangGraph-based agent coordination
- Specialized agent roles (architect, developer, tester)
- Context-aware rule loading system

### 🌈 **Vibe Coding UI**
- Streamlit interface for intuitive development
- Emotion-to-code translation for non-technical users
- Enhanced prompt generation for agent workflows

### 💾 **Prompt Management System**
- SQLite database for prompt storage and versioning
- A/B testing and optimization framework
- Template system with quality assessment

### 🔧 **Development Tools**
- Cross-platform git hooks and automation
- File organization enforcement
- Agile artifact management

---

## 🚀 **Quick Start**

### **📖 Essential Reading: Complete Cursor Practical Guide**
**[→ Complete Cursor Practical Guide](docs/guides/development/cursor-practical-guide.md)** 🎯

**THE definitive guide for developers using our revolutionary AI development system:**
- Full development workflows (coding, debugging, testing, deployment)
- Complete agile management with automation
- @keyword mastery for instant context switching  
- Advanced features and troubleshooting

### Prerequisites
- **Python**: Use Anaconda installation at `C:\App\Anaconda\` (Windows)
- **Free APIs**: Google Gemini (no paid services required)
- **Git**: For version control

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/ai-dev-agent.git
cd ai-dev-agent

# Create conda environment
conda env create -f environment.yml
conda activate ai-dev-agent

# Install dependencies
pip install -r requirements.txt
```

### Try Vibe Coding
```bash
# Launch the UI
streamlit run apps/vibe_coding_ui.py
```

### Run Agent System
```bash
# Start the main agent interface
python apps/main.py
```

---

## Project Structure

```
ai-dev-agent/
├── agents/           # Specialized AI agents
├── apps/            # User interfaces (Vibe Coding, etc.)
├── utils/           # Core utilities and frameworks
├── tests/           # Comprehensive test suite
├── docs/            # Documentation and guides
├── enforcement/     # Rules and principles
└── scripts/         # Automation and setup tools
```

---

## Core Components

### Agent System
- **Context-aware agents** that adapt behavior based on development context
- **Rule-based coordination** using practical software patterns
- **Wu Wei principles** for natural, non-forcing system design

### Vibe Coding Interface
- **Intuitive development** through emotion and metaphor
- **Enhanced prompts** that improve agent communication
- **Working implementation** - not just a concept

### Prompt Engineering
- **Database-driven** prompt storage and optimization
- **Scientific A/B testing** for prompt effectiveness
- **Template system** for consistent, reusable patterns

---

## Learning Focus

This project teaches practical techniques for:

1. **AI Agent Coordination** - How to build multi-agent systems that work together
2. **Context-Aware Systems** - Loading different behaviors based on development context
3. **Prompt Engineering** - Scientific approach to optimizing LLM communication
4. **Ethical AI Development** - Building safeguards and value alignment
5. **Clean Architecture** - Organizing AI systems for maintainability

---

## Production Extraction

To generate clean, production-ready software from this research:

```bash
# Extract specific components
python scripts/extract.py --type agent-toolkit --output ./my-agents
python scripts/extract.py --type vibe-ui --output ./my-vibe-app
python scripts/extract.py --type prompt-manager --output ./my-prompts
```

See [PROJECT_STRUCTURE_STRATEGY.md](./docs/PROJECT_STRUCTURE_STRATEGY.md) for details.

---

## Testing

```bash
# Run full test suite
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

---

## Development Principles

- **Test-driven development** - Write tests first
- **Clean code practices** - Readable, maintainable implementations  
- **Evidence-based validation** - No claims without proof
- **Practical focus** - Every concept must improve actual software
- **No bullshit** - Clear, honest documentation and implementation

---

## Contributing

1. **Follow the development principles** - practical, tested, clean code
2. **Write comprehensive tests** for all new functionality
3. **Document clearly** - focus on practical usage
4. **No philosophical abstractions** - keep it practical and teachable

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

---

## Technology Stack

- **Python 3.8+** with Anaconda package management
- **LangChain/LangGraph** for agent orchestration
- **Streamlit** for user interfaces
- **SQLite** for data persistence
- **Pytest** for testing framework
- **Google Gemini** for LLM capabilities

---

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

## Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - Agent orchestration framework
- [Streamlit](https://streamlit.io/) - Beautiful Python web apps
- [Google Gemini](https://ai.google.dev/) - LLM capabilities

Standing on the shoulders of software engineering giants:
- Donald Knuth, Robert C. Martin, Martin Fowler, Kent Beck
- Gang of Four, Steve McConnell, and the Python community

---

**Focus**: Learn practical AI development techniques. Extract clean software. Build useful tools.

**Mission**: Teach how philosophy can improve software engineering when applied practically.
