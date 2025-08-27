# System Architecture Diagram

```mermaid
graph TB
    %% User Interface Layer
    subgraph "User Interface"
        UI[Streamlit Web App]
        CLI[Command Line Interface]
    end
    
    %% Core System Layer
    subgraph "Core System"
        PM[Project Manager Agent]
        WF[Workflow Manager]
        EH[Error Handler]
        HA[Human Approval]
    end
    
    %% Agent Layer
    subgraph "AI Agents"
        RA[Requirements Analyst]
        AD[Architecture Designer]
        CG[Code Generator]
        TG[Test Generator]
        DG[Documentation Generator]
        CR[Code Reviewer]
        SA[Security Analyst]
    end
    
    %% Data Layer
    subgraph "Data & State"
        PS[Project State]
        CF[Configuration]
        LG[Logging]
        CT[Context Engine]
    end
    
    %% External Services
    subgraph "External Services"
        AI[Gemini AI API]
        FS[File System]
        DB[(Database)]
    end
    
    %% Connections
    UI --> PM
    CLI --> PM
    PM --> WF
    WF --> EH
    WF --> HA
    
    %% Agent Workflow
    PM --> RA
    PM --> AD
    PM --> CG
    PM --> TG
    PM --> DG
    PM --> CR
    PM --> SA
    
    %% Feedback Loops
    RA -.->|Feedback| AD
    AD -.->|Feedback| CG
    CG -.->|Feedback| CR
    CR -.->|Feedback| CG
    SA -.->|Feedback| CG
    TG -.->|Feedback| CR
    
    %% Data Flow
    RA --> PS
    AD --> PS
    CG --> PS
    TG --> PS
    DG --> PS
    CR --> PS
    SA --> PS
    
    %% External Integrations
    RA --> AI
    AD --> AI
    CG --> AI
    TG --> AI
    DG --> AI
    CR --> AI
    SA --> AI
    
    %% File Operations
    CG --> FS
    TG --> FS
    DG --> FS
    
    %% Configuration & Logging
    PM --> CF
    PM --> LG
    PM --> CT
    
    %% Styling
    classDef userInterface fill:#e1f5fe
    classDef coreSystem fill:#f3e5f5
    classDef agents fill:#e8f5e8
    classDef dataLayer fill:#fff3e0
    classDef external fill:#ffebee
    
    class UI,CLI userInterface
    class PM,WF,EH,HA coreSystem
    class RA,AD,CG,TG,DG,CR,SA agents
    class PS,CF,LG,CT dataLayer
    class AI,FS,DB external
```

## System Components

### User Interface Layer
- **Streamlit Web App**: Primary web interface for project creation and management
- **Command Line Interface**: Alternative interface for automation and scripting

### Core System Layer
- **Project Manager Agent**: Orchestrates the entire development workflow
- **Workflow Manager**: Manages the execution flow and agent coordination
- **Error Handler**: Handles errors and exceptions gracefully
- **Human Approval**: Manages points where human intervention is required

### AI Agents Layer
- **Requirements Analyst**: Analyzes project requirements and creates specifications
- **Architecture Designer**: Designs system architecture and technical decisions
- **Code Generator**: Generates source code based on requirements and architecture
- **Test Generator**: Creates comprehensive test suites
- **Documentation Generator**: Generates project documentation
- **Code Reviewer**: Reviews code quality and provides feedback
- **Security Analyst**: Analyzes security aspects and vulnerabilities

### Data & State Layer
- **Project State**: Maintains the current state of the project
- **Configuration**: Manages system configuration and settings
- **Logging**: Provides comprehensive logging and monitoring
- **Context Engine**: Manages context and knowledge sharing between agents

### External Services
- **Gemini AI API**: Provides AI capabilities for all agents
- **File System**: Stores generated project files
- **Database**: Stores project metadata and configurations

## Key Features

### Feedback Loops
The system implements sophisticated feedback loops where agents can provide feedback to each other:
- Requirements Analyst → Architecture Designer
- Architecture Designer → Code Generator
- Code Generator → Code Reviewer
- Code Reviewer → Code Generator (iterative improvement)
- Security Analyst → Code Generator
- Test Generator → Code Reviewer

### Decision Management
The Project Manager Agent can intervene when:
- Agents disagree on technical decisions
- Quality thresholds are not met
- Human approval is required for critical decisions
- Iteration limits are reached

### State Management
All agents work with a shared Project State that maintains:
- Current requirements and specifications
- Architecture decisions and diagrams
- Generated code and files
- Test results and coverage
- Documentation artifacts
- Review feedback and decisions
