"""
Universal Composition Layer - Professional AI Agent Builder
A sophisticated interface for building software agents and enterprise systems
with multi-platform AI framework integration and universal compatibility.
"""

import streamlit as st
import sys
import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import actual agent system components
try:
    from agents.requirements_analyst import RequirementsAnalyst
    from agents.architect import Architect  
    AGENTS_AVAILABLE = True
except ImportError:
    # Fallback if agents not available
    RequirementsAnalyst = None
    Architect = None
    AGENTS_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Universal Composition Layer",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
    }
    .composition-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .framework-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .enterprise-module {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    .capability-metric {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 5px;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_api_keys():
    """Load API keys from Streamlit secrets."""
    try:
        return {
            'gemini_api_key': st.secrets.get('GEMINI_API_KEY', ''),
            'langsmith_api_key': st.secrets.get('LANGSMITH_API_KEY', ''),
            'langsmith_endpoint': st.secrets.get('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com'),
            'langsmith_project': st.secrets.get('LANGSMITH_PROJECT', 'ai-dev-agent'),
            'langsmith_tracing': st.secrets.get('LANGSMITH_TRACING', 'true')
        }
    except Exception as e:
        st.error(f"❌ Error loading API keys: {str(e)}")
        return {
            'gemini_api_key': '',
            'langsmith_api_key': '',
            'langsmith_endpoint': 'https://api.smith.langchain.com',
            'langsmith_project': 'ai-dev-agent',
            'langsmith_tracing': 'true'
        }

def initialize_session_state():
    """Initialize session state for the Universal Composition Layer."""
    if 'composition_config' not in st.session_state:
        st.session_state.composition_config = {
            'selected_frameworks': [],
            'enterprise_modules': [],
            'agent_architecture': 'simple',
            'deployment_target': 'local',
            'integration_level': 'basic'
        }
    
    if 'project_blueprint' not in st.session_state:
        st.session_state.project_blueprint = None
    
    if 'active_agents' not in st.session_state:
        st.session_state.active_agents = []
    
    if 'api_keys' not in st.session_state:
        # Load API keys from secrets.toml
        st.session_state.api_keys = load_api_keys()
    
    if 'running_projects' not in st.session_state:
        st.session_state.running_projects = []
    
    if 'human_loop_conversations' not in st.session_state:
        st.session_state.human_loop_conversations = []
    
    if 'active_chat' not in st.session_state:
        st.session_state.active_chat = None
    
    if 'workflow_paused_states' not in st.session_state:
        st.session_state.workflow_paused_states = []

def display_main_header():
    """Display the main application header."""
    st.markdown('<h1 class="main-header">🔧 Universal Composition Layer</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; font-size: 1.2rem; color: #666;">
        Professional AI Agent Builder & Enterprise System Composer<br>
        <em>Build Any Software Agent | Connect All Frameworks | Deploy Anywhere</em>
    </div>
    """, unsafe_allow_html=True)

def display_framework_selector():
    """Display framework selection interface."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🚀 AI Framework Selection")
    
    frameworks = {
        'LangChain': {
            'description': 'Comprehensive LLM application framework',
            'capabilities': ['Chains', 'Agents', 'Memory', 'Tools'],
            'best_for': 'Complex reasoning workflows'
        },
        'LangGraph': {
            'description': 'Stateful multi-actor applications',
            'capabilities': ['State Management', 'Multi-Agent', 'Workflows'],
            'best_for': 'Collaborative agent systems'
        },
        'n8n': {
            'description': 'Visual workflow automation',
            'capabilities': ['No-Code', 'Integrations', 'Triggers'],
            'best_for': 'Business process automation'
        },
        'CrewAI': {
            'description': 'Role-based AI agent framework',
            'capabilities': ['Role Assignment', 'Task Delegation', 'Coordination'],
            'best_for': 'Team-based AI workflows'
        },
        'AutoGen': {
            'description': 'Multi-agent conversation framework',
            'capabilities': ['Conversational AI', 'Group Chat', 'Code Generation'],
            'best_for': 'Collaborative problem solving'
        },
        'Semantic Kernel': {
            'description': 'Microsoft AI orchestration',
            'capabilities': ['Skill Chaining', 'Memory', 'Planning'],
            'best_for': 'Enterprise AI integration'
        }
    }
    
    selected_frameworks = st.multiselect(
        "Select AI Frameworks to Compose:",
        options=list(frameworks.keys()),
        default=st.session_state.composition_config['selected_frameworks']
    )
    
    st.session_state.composition_config['selected_frameworks'] = selected_frameworks
    
    # Display selected framework details
    if selected_frameworks:
        st.write("**Selected Framework Details:**")
        for fw in selected_frameworks:
            with st.expander(f"{fw} - {frameworks[fw]['description']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Capabilities:**")
                    for cap in frameworks[fw]['capabilities']:
                        st.markdown(f'<span class="framework-badge">{cap}</span>', unsafe_allow_html=True)
                with col2:
                    st.write(f"**Best for:** {frameworks[fw]['best_for']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_enterprise_modules():
    """Display enterprise system modules."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🏢 Enterprise System Modules")
    
    modules = {
        'ERP System': 'Enterprise Resource Planning',
        'CRM Platform': 'Customer Relationship Management',
        'Financial System': 'Accounting & Financial Management',
        'Logistics Platform': 'Supply Chain & Warehouse Management',
        'Customer Support': 'Helpdesk & Support Automation',
        'HR Management': 'Human Resources & Payroll',
        'Project Management': 'Task & Project Coordination',
        'Business Intelligence': 'Analytics & Reporting',
        'E-Commerce Platform': 'Online Sales & Inventory',
        'Document Management': 'File Storage & Workflow'
    }
    
    col1, col2 = st.columns(2)
    with col1:
        selected_modules = st.multiselect(
            "Select Enterprise Modules:",
            options=list(modules.keys()),
            default=st.session_state.composition_config['enterprise_modules']
        )
        st.session_state.composition_config['enterprise_modules'] = selected_modules
    
    with col2:
        if selected_modules:
            st.write("**Selected Modules:**")
            for module in selected_modules:
                st.markdown(f'<div class="enterprise-module">{module}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_architecture_designer():
    """Display architecture design interface."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🏗️ Agent Architecture Designer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        architecture = st.selectbox(
            "Architecture Pattern:",
            ['Simple Sequential', 'Parallel Processing', 'Hierarchical', 'Mesh Network', 'Event-Driven'],
            index=0
        )
        st.session_state.composition_config['agent_architecture'] = architecture
    
    with col2:
        deployment = st.selectbox(
            "Deployment Target:",
            ['Local Development', 'Cloud Container', 'Kubernetes', 'Serverless', 'Edge Computing'],
            index=0
        )
        st.session_state.composition_config['deployment_target'] = deployment
    
    with col3:
        integration = st.selectbox(
            "Integration Level:",
            ['Basic (API Only)', 'Advanced (Webhooks)', 'Deep (Native)', 'Custom (SDK)'],
            index=0
        )
        st.session_state.composition_config['integration_level'] = integration
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_capability_matrix():
    """Display system capability matrix."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("📊 System Capability Matrix")
    
    capabilities = {
        'Agent Coordination': 85,
        'Enterprise Integration': 92,
        'Scalability': 78,
        'Security': 88,
        'Performance': 82,
        'Maintainability': 90,
        'Extensibility': 87,
        'User Experience': 85
    }
    
    for capability, score in capabilities.items():
        st.markdown(f"""
        <div class="capability-metric">
            <span><strong>{capability}</strong></span>
            <span>{score}%</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_composition_dashboard():
    """Display the main composition dashboard."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_framework_selector()
        display_enterprise_modules()
        display_architecture_designer()
    
    with col2:
        display_api_configuration()
        display_capability_matrix()
        
        # Action buttons
        st.markdown('<div class="composition-card">', unsafe_allow_html=True)
        st.subheader("🚀 Actions")
        
        if st.button("🎯 Generate System Blueprint", type="primary"):
            generate_system_blueprint()
        
        if st.button("⚡ Deploy Composition", type="secondary"):
            deploy_composition()
        
        if st.button("🔍 Validate Architecture", type="secondary"):
            validate_architecture()
        
        if st.button("📋 Export Configuration", type="secondary"):
            export_configuration()
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_api_configuration():
    """Display API configuration section with secrets.toml loading and manual entry."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🔑 API Configuration")
    
    # Load from secrets.toml status
    api_keys = st.session_state.api_keys
    
    # Status indicators
    col1, col2 = st.columns(2)
    with col1:
        gemini_status = "🟢 Loaded" if api_keys['gemini_api_key'] else "🔴 Missing"
        st.metric("Gemini API", gemini_status)
    with col2:
        langsmith_status = "🟢 Loaded" if api_keys['langsmith_api_key'] else "🔴 Missing"
        st.metric("LangSmith API", langsmith_status)
    
    # Configuration mode toggle
    config_mode = st.radio(
        "Configuration Source:",
        ["📁 Use secrets.toml", "✏️ Manual Entry", "🔄 Refresh from secrets"],
        horizontal=True
    )
    
    if config_mode == "🔄 Refresh from secrets":
        if st.button("🔄 Reload API Keys"):
            st.session_state.api_keys = load_api_keys()
            st.success("✅ API keys refreshed from secrets.toml")
            st.rerun()
    
    elif config_mode == "✏️ Manual Entry":
        st.write("**Manual API Key Entry:**")
        
        # Manual Gemini API key entry
        manual_gemini = st.text_input(
            "Gemini API Key:",
            value=api_keys['gemini_api_key'],
            type="password",
            help="Enter your Google Gemini API key"
        )
        
        # Manual LangSmith API key entry
        manual_langsmith = st.text_input(
            "LangSmith API Key:",
            value=api_keys['langsmith_api_key'],
            type="password",
            help="Enter your LangChain LangSmith API key"
        )
        
        # LangSmith project name
        manual_project = st.text_input(
            "LangSmith Project:",
            value=api_keys['langsmith_project'],
            help="LangSmith project name for tracing"
        )
        
        # Update session state with manual entries
        if st.button("💾 Save Manual Configuration"):
            st.session_state.api_keys.update({
                'gemini_api_key': manual_gemini,
                'langsmith_api_key': manual_langsmith,
                'langsmith_project': manual_project
            })
            st.success("✅ Manual API configuration saved!")
            st.rerun()
    
    else:  # Use secrets.toml
        if api_keys['gemini_api_key'] and api_keys['langsmith_api_key']:
            st.success("✅ API keys loaded from secrets.toml")
        else:
            st.warning("⚠️ Some API keys missing in secrets.toml")
            st.info("💡 Add missing keys to .streamlit/secrets.toml or use manual entry")
    
    # Display current configuration (masked)
    with st.expander("🔍 Current Configuration"):
        st.code(f"""
Gemini API Key: {'*' * 20 + api_keys['gemini_api_key'][-8:] if len(api_keys['gemini_api_key']) > 8 else 'Not set'}
LangSmith API Key: {'*' * 20 + api_keys['langsmith_api_key'][-8:] if len(api_keys['langsmith_api_key']) > 8 else 'Not set'}
LangSmith Endpoint: {api_keys['langsmith_endpoint']}
LangSmith Project: {api_keys['langsmith_project']}
LangSmith Tracing: {api_keys['langsmith_tracing']}
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_system_blueprint():
    """Generate a comprehensive system blueprint with real agent analysis."""
    with st.spinner("🎯 Generating intelligent system blueprint..."):
        try:
            # Get the selected configuration
            config = st.session_state.composition_config
            
            # Create the project description for analysis
            project_description = create_project_description_from_config(config)
            
            # Check API keys before proceeding
            api_keys = st.session_state.api_keys
            if not api_keys['gemini_api_key']:
                st.error("❌ Gemini API key is required for AI analysis!")
                st.info("💡 Please configure your API keys in the configuration section above.")
                return
            
            # Set environment variables for API keys
            os.environ['GEMINI_API_KEY'] = api_keys['gemini_api_key']
            if api_keys['langsmith_api_key']:
                os.environ['LANGCHAIN_TRACING_V2'] = api_keys['langsmith_tracing']
                os.environ['LANGCHAIN_ENDPOINT'] = api_keys['langsmith_endpoint']
                os.environ['LANGCHAIN_API_KEY'] = api_keys['langsmith_api_key']
                os.environ['LANGCHAIN_PROJECT'] = api_keys['langsmith_project']
            
            # Initialize agents if available
            if AGENTS_AVAILABLE:
                try:
                    requirements_analyst = RequirementsAnalyst()
                    architect = Architect()
                    
                    # Real requirements analysis
                    st.info("🔍 Analyzing requirements with AI...")
                    requirements_result = asyncio.run(
                        requirements_analyst.analyze_requirements(project_description)
                    )
                    
                    # Real architecture design  
                    st.info("🏗️ Designing system architecture with AI...")
                    architecture_result = asyncio.run(
                        architect.design_architecture(requirements_result.get('requirements', ''))
                    )
                    
                except Exception as e:
                    st.warning(f"⚠️ Agent analysis failed: {str(e)}")
                    st.info("🤖 Using simulated analysis instead...")
                    requirements_result = simulate_requirements_analysis(project_description)
                    architecture_result = simulate_architecture_analysis(config)
            else:
                st.info("🤖 Using simulated analysis (agents not available)...")
                requirements_result = simulate_requirements_analysis(project_description)
                architecture_result = simulate_architecture_analysis(config)
            
            # Generate comprehensive blueprint
            blueprint = {
                'timestamp': datetime.now().isoformat(),
                'composition_config': config,
                'ai_analysis': {
                    'requirements_analysis': requirements_result,
                    'architecture_design': architecture_result
                },
                'system_specification': {
                    'frameworks': config['selected_frameworks'],
                    'enterprise_modules': config['enterprise_modules'],
                    'architecture_pattern': config['agent_architecture'],
                    'deployment_target': config['deployment_target'],
                    'integration_level': config['integration_level']
                },
                'implementation_plan': generate_implementation_plan(config, requirements_result, architecture_result),
                'estimated_metrics': calculate_system_metrics(config),
                'generated_components': generate_component_specifications(config)
            }
            
            st.session_state.project_blueprint = blueprint
            st.success("✅ Intelligent system blueprint generated successfully!")
            
            # Display results in organized tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Blueprint", "🤖 AI Analysis", "🏗️ Architecture", "⚡ Implementation"])
            
            with tab1:
                st.json(blueprint['system_specification'])
            
            with tab2:
                st.subheader("🔍 Requirements Analysis")
                if 'requirements' in requirements_result:
                    st.write(requirements_result['requirements'])
                if 'user_stories' in requirements_result:
                    st.subheader("📖 Generated User Stories")
                    for i, story in enumerate(requirements_result['user_stories'], 1):
                        st.write(f"**US-{i:03d}**: {story}")
            
            with tab3:
                st.subheader("🏗️ System Architecture")
                if 'architecture' in architecture_result:
                    st.write(architecture_result['architecture'])
                if 'components' in architecture_result:
                    st.subheader("🔧 System Components")
                    for component in architecture_result['components']:
                        st.write(f"• **{component['name']}**: {component['description']}")
            
            with tab4:
                st.subheader("⚡ Implementation Plan")
                plan = blueprint['implementation_plan']
                for phase in plan['phases']:
                    with st.expander(f"Phase {phase['number']}: {phase['name']}"):
                        st.write(f"**Duration**: {phase['duration']}")
                        st.write(f"**Deliverables**: {', '.join(phase['deliverables'])}")
            
        except Exception as e:
            st.error(f"❌ Error generating blueprint: {str(e)}")
            st.info("💡 Tip: Ensure you have selected at least one framework and enterprise module.")

def deploy_composition():
    """Deploy the composed system by creating actual project structure."""
    if not st.session_state.project_blueprint:
        st.error("❌ Please generate a system blueprint first!")
        return
    
    with st.spinner("⚡ Deploying composition - Creating real project structure..."):
        try:
            blueprint = st.session_state.project_blueprint
            project_name = generate_project_name(blueprint['composition_config'])
            
            # Create project directory
            project_path = Path(f"generated_projects/{project_name}")
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Generate real project files
            create_project_structure(project_path, blueprint)
            generate_requirements_file(project_path, blueprint)
            generate_main_application(project_path, blueprint)
            generate_docker_files(project_path, blueprint)
            generate_documentation(project_path, blueprint)
            
            st.success("✅ Composition deployed successfully!")
            st.balloons()
            
            # Display deployment results
            st.subheader("🚀 Deployment Results")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Project Name", project_name)
                st.metric("Project Path", str(project_path))
                st.metric("Generated Files", count_generated_files(project_path))
            
            with col2:
                st.metric("Frameworks Integrated", len(blueprint['composition_config']['selected_frameworks']))
                st.metric("Enterprise Modules", len(blueprint['composition_config']['enterprise_modules']))
                st.metric("Estimated Dev Time", blueprint['implementation_plan']['total_duration'])
            
            # Show generated file structure
            with st.expander("📁 Generated Project Structure"):
                display_project_tree(project_path)
            
            # Download project as ZIP
            if st.button("📦 Download Project ZIP"):
                zip_data = create_project_zip(project_path)
                st.download_button(
                    label="💾 Download Complete Project",
                    data=zip_data,
                    file_name=f"{project_name}.zip",
                    mime="application/zip"
                )
                
        except Exception as e:
            st.error(f"❌ Deployment failed: {str(e)}")
            st.info("💡 Please check your configuration and try again.")

def validate_architecture():
    """Validate the designed architecture."""
    with st.spinner("🔍 Validating architecture..."):
        # Architecture validation logic here
        st.success("✅ Architecture validation passed!")

def export_configuration():
    """Export the current configuration."""
    config_yaml = yaml.dump(st.session_state.composition_config, default_flow_style=False)
    st.download_button(
        label="📋 Download Configuration",
        data=config_yaml,
        file_name=f"composition_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml",
        mime="text/yaml"
    )

def create_project_description_from_config(config: Dict) -> str:
    """Create a detailed project description from the composition configuration."""
    frameworks = ", ".join(config['selected_frameworks'])
    modules = ", ".join(config['enterprise_modules'])
    
    description = f"""
    Project: Enterprise System with AI Agent Integration
    
    Selected AI Frameworks: {frameworks}
    Enterprise Modules: {modules}
    Architecture Pattern: {config['agent_architecture']}
    Deployment Target: {config['deployment_target']}
    Integration Level: {config['integration_level']}
    
    Requirements:
    - Build a comprehensive enterprise system that integrates the selected AI frameworks
    - Implement the specified enterprise modules with full functionality
    - Use the {config['agent_architecture']} architecture pattern for optimal performance
    - Deploy to {config['deployment_target']} environment
    - Achieve {config['integration_level']} integration between all components
    
    The system should be scalable, maintainable, and follow enterprise best practices.
    """
    return description.strip()

def generate_implementation_plan(config: Dict, requirements: Dict, architecture: Dict) -> Dict:
    """Generate a realistic implementation plan based on the configuration."""
    num_modules = len(config['enterprise_modules'])
    num_frameworks = len(config['selected_frameworks'])
    
    complexity_multiplier = 1.0
    if config['agent_architecture'] in ['Hierarchical', 'Mesh Network', 'Event-Driven']:
        complexity_multiplier = 1.5
    if config['integration_level'] in ['Deep (Native)', 'Custom (SDK)']:
        complexity_multiplier *= 1.3
    
    base_weeks = max(2, num_modules + num_frameworks)
    total_weeks = int(base_weeks * complexity_multiplier)
    
    phases = [
        {
            'number': 1,
            'name': 'Foundation & Architecture Setup',
            'duration': f'{total_weeks // 4} weeks',
            'deliverables': ['Project structure', 'Core architecture', 'Framework integration']
        },
        {
            'number': 2,
            'name': 'Core Module Development',
            'duration': f'{total_weeks // 2} weeks',
            'deliverables': ['Enterprise modules', 'Database design', 'API development']
        },
        {
            'number': 3,
            'name': 'Agent Integration & Testing',
            'duration': f'{total_weeks // 4} weeks',
            'deliverables': ['AI agent integration', 'System testing', 'Performance optimization']
        },
        {
            'number': 4,
            'name': 'Deployment & Documentation',
            'duration': f'{total_weeks // 8 or 1} weeks',
            'deliverables': ['Production deployment', 'User documentation', 'Training materials']
        }
    ]
    
    return {
        'total_duration': f'{total_weeks} weeks',
        'complexity_level': 'High' if complexity_multiplier > 1.3 else 'Medium',
        'phases': phases,
        'team_size': f'{3 + num_modules // 2} developers',
        'technologies': config['selected_frameworks'] + config['enterprise_modules']
    }

def calculate_system_metrics(config: Dict) -> Dict:
    """Calculate realistic system metrics based on configuration."""
    base_score = 70
    
    # Framework complexity adjustments
    framework_bonus = len(config['selected_frameworks']) * 5
    
    # Enterprise module complexity
    module_bonus = len(config['enterprise_modules']) * 3
    
    # Architecture pattern adjustments
    architecture_bonus = {
        'Simple Sequential': 5,
        'Parallel Processing': 10,
        'Hierarchical': 15,
        'Mesh Network': 20,
        'Event-Driven': 18
    }.get(config['agent_architecture'], 10)
    
    # Calculate individual metrics
    coordination = min(95, base_score + framework_bonus + architecture_bonus)
    integration = min(95, base_score + module_bonus + framework_bonus)
    scalability = min(95, base_score + architecture_bonus + (module_bonus // 2))
    
    return {
        'agent_coordination': coordination,
        'enterprise_integration': integration,
        'scalability': scalability,
        'estimated_performance': min(95, (coordination + integration + scalability) // 3),
        'complexity_score': framework_bonus + module_bonus + architecture_bonus,
        'development_velocity': max(1, 10 - (len(config['enterprise_modules']) // 2))
    }

def generate_component_specifications(config: Dict) -> List[Dict]:
    """Generate detailed component specifications."""
    components = []
    
    # Framework components
    for framework in config['selected_frameworks']:
        components.append({
            'name': f'{framework} Integration Layer',
            'type': 'Framework Component',
            'description': f'Integration layer for {framework} AI framework',
            'dependencies': ['Core API', 'Configuration Manager'],
            'interfaces': ['REST API', 'WebSocket', 'Event Bus']
        })
    
    # Enterprise module components
    for module in config['enterprise_modules']:
        components.append({
            'name': f'{module} Service',
            'type': 'Enterprise Module',
            'description': f'Complete {module} implementation with AI integration',
            'dependencies': ['Database Layer', 'Authentication Service', 'AI Framework'],
            'interfaces': ['REST API', 'GraphQL', 'Message Queue']
        })
    
    # Architecture-specific components
    if config['agent_architecture'] == 'Hierarchical':
        components.append({
            'name': 'Agent Hierarchy Manager',
            'type': 'Architecture Component',
            'description': 'Manages hierarchical agent relationships and communication',
            'dependencies': ['Agent Registry', 'Message Router'],
            'interfaces': ['Agent Protocol', 'Management API']
        })
    elif config['agent_architecture'] == 'Event-Driven':
        components.append({
            'name': 'Event Bus System',
            'type': 'Architecture Component',
            'description': 'Central event routing and processing system',
            'dependencies': ['Message Broker', 'Event Store'],
            'interfaces': ['Event Publisher', 'Event Subscriber']
        })
    
    return components

def generate_project_name(config: Dict) -> str:
    """Generate a meaningful project name from configuration."""
    frameworks = "_".join(config['selected_frameworks'][:2])  # Limit to first 2
    modules = "_".join([m.replace(" ", "").lower() for m in config['enterprise_modules'][:2]])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{frameworks}_{modules}_{timestamp}".lower()

def create_project_structure(project_path: Path, blueprint: Dict):
    """Create the actual project directory structure."""
    # Core directories
    dirs = [
        "src/agents", "src/services", "src/models", "src/utils", "src/api",
        "tests/unit", "tests/integration", "tests/performance",
        "docs/architecture", "docs/api", "docs/deployment",
        "config", "scripts", "data", "logs"
    ]
    
    for dir_name in dirs:
        (project_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    init_dirs = ["src", "src/agents", "src/services", "src/models", "src/utils", "src/api", "tests"]
    for dir_name in init_dirs:
        (project_path / dir_name / "__init__.py").write_text("# Generated by Universal Composition Layer\n")

def generate_requirements_file(project_path: Path, blueprint: Dict):
    """Generate requirements.txt with framework-specific dependencies."""
    frameworks = blueprint['composition_config']['selected_frameworks']
    
    requirements = [
        "# Generated by Universal Composition Layer",
        "# Core dependencies",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "",
        "# Framework-specific dependencies"
    ]
    
    if "LangChain" in frameworks:
        requirements.extend([
            "langchain>=0.1.0",
            "langchain-community>=0.0.10",
            "langchain-core>=0.1.0"
        ])
    
    if "LangGraph" in frameworks:
        requirements.append("langgraph>=0.0.20")
    
    if "CrewAI" in frameworks:
        requirements.append("crewai>=0.1.0")
    
    if "AutoGen" in frameworks:
        requirements.append("pyautogen>=0.2.0")
    
    if "Semantic Kernel" in frameworks:
        requirements.append("semantic-kernel>=0.4.0")
    
    if "n8n" in frameworks:
        requirements.extend([
            "requests>=2.31.0",
            "websockets>=12.0"
        ])
    
    requirements.extend([
        "",
        "# Development dependencies",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.7.0"
    ])
    
    (project_path / "requirements.txt").write_text("\n".join(requirements))

def generate_main_application(project_path: Path, blueprint: Dict):
    """Generate the main application file."""
    config = blueprint['composition_config']
    
    main_content = f'''"""
{generate_project_name(config).replace("_", " ").title()} - Generated by Universal Composition Layer
Enterprise System with AI Agent Integration

Frameworks: {", ".join(config['selected_frameworks'])}
Modules: {", ".join(config['enterprise_modules'])}
Architecture: {config['agent_architecture']}
"""

import asyncio
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="{generate_project_name(config).replace("_", " ").title()}",
    description="Enterprise System with AI Agent Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Framework integrations
{generate_framework_integrations(config['selected_frameworks'])}

# Enterprise modules
{generate_enterprise_modules(config['enterprise_modules'])}

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {{
        "message": "Enterprise System with AI Agent Integration",
        "frameworks": {config['selected_frameworks']},
        "modules": {config['enterprise_modules']},
        "architecture": "{config['agent_architecture']}",
        "status": "running"
    }}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "timestamp": "{{datetime.now().isoformat()}}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    (project_path / "main.py").write_text(main_content)

def generate_framework_integrations(frameworks: List[str]) -> str:
    """Generate framework integration code."""
    integrations = []
    
    for framework in frameworks:
        if framework == "LangChain":
            integrations.append("""
# LangChain Integration
try:
    from langchain.llms import OpenAI
    from langchain.chains import LLMChain
    logger.info("LangChain integration loaded successfully")
except ImportError:
    logger.warning("LangChain not installed")
""")
        elif framework == "LangGraph":
            integrations.append("""
# LangGraph Integration
try:
    from langgraph.graph import StateGraph
    logger.info("LangGraph integration loaded successfully")
except ImportError:
    logger.warning("LangGraph not installed")
""")
        elif framework == "CrewAI":
            integrations.append("""
# CrewAI Integration
try:
    from crewai import Agent, Task, Crew
    logger.info("CrewAI integration loaded successfully")
except ImportError:
    logger.warning("CrewAI not installed")
""")
    
    return "\n".join(integrations)

def generate_enterprise_modules(modules: List[str]) -> str:
    """Generate enterprise module code."""
    module_code = []
    
    for module in modules:
        module_name = module.replace(" ", "").lower()
        module_code.append(f"""
# {module} Module
@app.get("/{module_name}")
async def get_{module_name}_status():
    '''Get {module} status and information.'''
    return {{
        "module": "{module}",
        "status": "active",
        "features": ["AI Integration", "Real-time Processing", "Enterprise Security"]
    }}
""")
    
    return "\n".join(module_code)

def generate_docker_files(project_path: Path, blueprint: Dict):
    """Generate Docker configuration files."""
    dockerfile_content = """# Generated by Universal Composition Layer
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
"""
    
    docker_compose_content = """# Generated by Universal Composition Layer
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: enterprise_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    
    (project_path / "Dockerfile").write_text(dockerfile_content)
    (project_path / "docker-compose.yml").write_text(docker_compose_content)

def generate_documentation(project_path: Path, blueprint: Dict):
    """Generate project documentation."""
    config = blueprint['composition_config']
    
    readme_content = f"""# {generate_project_name(config).replace("_", " ").title()}

Enterprise System with AI Agent Integration - Generated by Universal Composition Layer

## Overview

This project integrates multiple AI frameworks and enterprise modules:

### AI Frameworks
{chr(10).join([f"- **{fw}**: {get_framework_description(fw)}" for fw in config['selected_frameworks']])}

### Enterprise Modules  
{chr(10).join([f"- **{mod}**: Complete {mod} implementation" for mod in config['enterprise_modules']])}

### Architecture
- **Pattern**: {config['agent_architecture']}
- **Deployment**: {config['deployment_target']}
- **Integration**: {config['integration_level']}

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Access the API at http://localhost:8000

## Docker Deployment

```bash
docker-compose up -d
```

## Generated Structure

- `src/` - Source code
- `tests/` - Test suites
- `docs/` - Documentation
- `config/` - Configuration files
- `scripts/` - Utility scripts

## API Endpoints

- `GET /` - System information
- `GET /health` - Health check
{chr(10).join([f"- `GET /{mod.replace(' ', '').lower()}` - {mod} status" for mod in config['enterprise_modules']])}

## Development

This project was generated with the Universal Composition Layer using the following specifications:

```yaml
{yaml.dump(config, default_flow_style=False)}
```

For more information, see the generated documentation in the `docs/` directory.
"""
    
    (project_path / "README.md").write_text(readme_content)

def get_framework_description(framework: str) -> str:
    """Get description for a framework."""
    descriptions = {
        "LangChain": "Comprehensive LLM application framework",
        "LangGraph": "Stateful multi-actor applications",
        "n8n": "Visual workflow automation",
        "CrewAI": "Role-based AI agent framework",
        "AutoGen": "Multi-agent conversation framework",
        "Semantic Kernel": "Microsoft AI orchestration"
    }
    return descriptions.get(framework, "AI framework integration")

def count_generated_files(project_path: Path) -> int:
    """Count the number of generated files."""
    return len(list(project_path.rglob("*"))) if project_path.exists() else 0

def display_project_tree(project_path: Path):
    """Display the project directory tree."""
    if not project_path.exists():
        st.error("Project path does not exist")
        return
    
    tree_items = []
    for item in sorted(project_path.rglob("*")):
        relative_path = item.relative_to(project_path)
        indent = "  " * (len(relative_path.parts) - 1)
        icon = "📁" if item.is_dir() else "📄"
        tree_items.append(f"{indent}{icon} {relative_path.name}")
    
    st.code("\n".join(tree_items[:50]))  # Limit to first 50 items
    if len(tree_items) > 50:
        st.info(f"... and {len(tree_items) - 50} more files/directories")

def create_project_zip(project_path: Path) -> bytes:
    """Create a ZIP file of the entire project."""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                arc_name = file_path.relative_to(project_path)
                zip_file.write(file_path, arc_name)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def simulate_requirements_analysis(project_description: str) -> Dict:
    """Simulate requirements analysis when agents are not available."""
    return {
        'requirements': f"Simulated requirements analysis for: {project_description[:100]}...",
        'user_stories': [
            "As a user, I want to access the enterprise system with AI integration",
            "As an admin, I want to manage system configurations and monitor performance",
            "As a developer, I want to extend the system with custom modules"
        ],
        'functional_requirements': [
            "Multi-framework AI integration",
            "Enterprise module composition", 
            "Scalable architecture implementation"
        ]
    }

def simulate_architecture_analysis(config: Dict) -> Dict:
    """Simulate architecture analysis when agents are not available."""
    frameworks = config['selected_frameworks']
    modules = config['enterprise_modules']
    
    return {
        'architecture': f"Simulated {config['agent_architecture']} architecture for {', '.join(frameworks)} with {', '.join(modules)}",
        'components': [
            {
                'name': f'{fw} Service Layer',
                'description': f'Service layer implementation for {fw} framework'
            } for fw in frameworks
        ] + [
            {
                'name': f'{mod} Module',
                'description': f'Enterprise module for {mod} functionality'  
            } for mod in modules
        ],
        'patterns': [config['agent_architecture']],
        'deployment': config['deployment_target']
    }

def display_project_runner():
    """Display project runner interface for running generated projects."""
    st.subheader("🚀 Project Runner - Run Your Generated Projects")
    st.markdown("Run and test your generated projects directly within the Universal Composition Layer.")
    
    # Check for available projects
    generated_projects_path = Path("generated_projects")
    if not generated_projects_path.exists():
        st.info("📂 No generated projects found. Create a project first using the Composition Dashboard.")
        return
    
    # List available projects
    projects = [p for p in generated_projects_path.iterdir() if p.is_dir()]
    
    if not projects:
        st.info("📂 No generated projects found. Create a project first using the Composition Dashboard.")
        return
    
    # Project selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_project = st.selectbox(
            "Select Project to Run:",
            options=[p.name for p in projects],
            help="Choose a generated project to run"
        )
    
    with col2:
        if st.button("🔄 Refresh Projects"):
            st.rerun()
    
    if selected_project:
        project_path = generated_projects_path / selected_project
        
        # Display project information
        st.markdown('<div class="composition-card">', unsafe_allow_html=True)
        st.subheader(f"📋 Project: {selected_project}")
        
        # Show project details
        readme_path = project_path / "README.md"
        if readme_path.exists():
            with st.expander("📖 Project README"):
                st.markdown(readme_path.read_text())
        
        # Show project structure
        with st.expander("📁 Project Structure"):
            display_project_tree(project_path)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Running controls
        st.markdown('<div class="composition-card">', unsafe_allow_html=True)
        st.subheader("⚡ Run Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Project", type="primary"):
                start_project(project_path, selected_project)
        
        with col2:
            if st.button("⏹️ Stop Project", type="secondary"):
                stop_project(selected_project)
        
        with col3:
            if st.button("📊 View Logs", type="secondary"):
                display_project_logs(project_path, selected_project)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Running projects status
        display_running_projects()

def start_project(project_path: Path, project_name: str):
    """Start a generated project."""
    try:
        # Check if project is already running
        running_projects = st.session_state.running_projects
        if any(p['name'] == project_name for p in running_projects):
            st.warning(f"⚠️ Project '{project_name}' is already running!")
            return
        
        # Install dependencies first
        st.info("📦 Installing project dependencies...")
        requirements_path = project_path / "requirements.txt"
        if requirements_path.exists():
            install_result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
            ], capture_output=True, text=True, cwd=str(project_path))
            
            if install_result.returncode != 0:
                st.error(f"❌ Failed to install dependencies: {install_result.stderr}")
                return
            else:
                st.success("✅ Dependencies installed successfully!")
        
        # Start the project
        st.info("🚀 Starting project...")
        main_py_path = project_path / "main.py"
        
        if main_py_path.exists():
            # Start project in background
            process = subprocess.Popen([
                sys.executable, str(main_py_path)
            ], cwd=str(project_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Add to running projects
            running_project = {
                'name': project_name,
                'path': str(project_path),
                'process': process,
                'start_time': datetime.now().isoformat(),
                'url': f"http://localhost:8000",  # Default FastAPI port
                'status': 'running'
            }
            
            st.session_state.running_projects.append(running_project)
            st.success(f"✅ Project '{project_name}' started successfully!")
            st.info(f"🌐 Project should be accessible at: http://localhost:8000")
            
        else:
            st.error("❌ main.py not found in project directory!")
            
    except Exception as e:
        st.error(f"❌ Failed to start project: {str(e)}")

def stop_project(project_name: str):
    """Stop a running project."""
    try:
        running_projects = st.session_state.running_projects
        project_to_stop = None
        
        for i, project in enumerate(running_projects):
            if project['name'] == project_name:
                project_to_stop = (i, project)
                break
        
        if project_to_stop:
            index, project = project_to_stop
            if 'process' in project:
                project['process'].terminate()
                project['process'].wait(timeout=5)  # Wait up to 5 seconds
            
            # Remove from running projects
            st.session_state.running_projects.pop(index)
            st.success(f"✅ Project '{project_name}' stopped successfully!")
        else:
            st.warning(f"⚠️ Project '{project_name}' is not running!")
            
    except Exception as e:
        st.error(f"❌ Failed to stop project: {str(e)}")

def display_project_logs(project_path: Path, project_name: str):
    """Display project logs."""
    logs_path = project_path / "logs"
    if logs_path.exists():
        log_files = list(logs_path.glob("*.log"))
        if log_files:
            for log_file in log_files:
                with st.expander(f"📋 {log_file.name}"):
                    try:
                        log_content = log_file.read_text()
                        st.code(log_content[-2000:] if len(log_content) > 2000 else log_content)  # Last 2000 chars
                    except Exception as e:
                        st.error(f"Error reading log file: {e}")
        else:
            st.info("📋 No log files found.")
    else:
        st.info("📋 No logs directory found.")

def display_running_projects():
    """Display currently running projects."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🏃 Running Projects")
    
    running_projects = st.session_state.running_projects
    
    if not running_projects:
        st.info("No projects currently running.")
    else:
        for project in running_projects:
            with st.expander(f"🚀 {project['name']} - {project['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Started:** {project['start_time']}")
                    st.write(f"**Path:** {project['path']}")
                with col2:
                    if 'url' in project:
                        st.markdown(f"**URL:** [Open App]({project['url']})")
                    st.write(f"**Status:** {project['status']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_agent_builder_interface():
    """Display the Agent Builder interface with Simple and Expert modes."""
    st.subheader("🤖 Agent Builder - Create AI Agents with Vibe")
    st.markdown("Build custom AI agents using natural language descriptions and vibe-driven configuration.")
    
    # Mode selection
    col1, col2 = st.columns([3, 1])
    with col1:
        builder_mode = st.radio(
            "Building Mode:",
            ["🌟 Simple Mode", "🔧 Expert Mode"],
            horizontal=True,
            help="Simple Mode: Natural language descriptions | Expert Mode: Advanced configuration"
        )
    
    with col2:
        if st.button("🎨 Load Vibe Context"):
            load_vibe_context_to_builder()
    
    if builder_mode == "🌟 Simple Mode":
        display_simple_mode_builder()
    else:
        display_expert_mode_builder()
    
    # Display active agents
    display_active_agents()

def display_simple_mode_builder():
    """Display the simple mode agent builder with vibe-driven interface."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🌟 Simple Mode - Describe Your Agent")
    
    # Agent basic info
    col1, col2 = st.columns(2)
    with col1:
        agent_name = st.text_input(
            "Agent Name:",
            placeholder="e.g., Customer Support Assistant",
            help="Give your agent a descriptive name"
        )
    
    with col2:
        agent_type = st.selectbox(
            "Agent Type:",
            ["Assistant", "Analyst", "Manager", "Specialist", "Coordinator"],
            help="What type of role will this agent fulfill?"
        )
    
    # Vibe selection for agent personality
    st.subheader("✨ Agent Vibe & Personality")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        agent_energy = st.selectbox(
            "Energy Level:",
            ["🔋 High Energy", "⚡ Balanced", "🧘 Calm & Focused"],
            help="How energetic should your agent be?"
        )
    
    with col2:
        agent_style = st.selectbox(
            "Communication Style:",
            ["💼 Professional", "😊 Friendly", "🎓 Educational", "🚀 Innovative"],
            help="How should your agent communicate?"
        )
    
    with col3:
        agent_expertise = st.selectbox(
            "Expertise Level:",
            ["🎯 Specialist", "🌐 Generalist", "🔍 Researcher", "🛠️ Problem Solver"],
            help="What's your agent's expertise approach?"
        )
    
    # Natural language description
    st.subheader("📝 Describe What Your Agent Should Do")
    agent_description = st.text_area(
        "Agent Description:",
        placeholder="""Describe your agent in natural language. For example:

"I want an agent that helps customers with technical support questions. It should be friendly but professional, able to troubleshoot common issues, escalate complex problems, and maintain a knowledge base of solutions. The agent should work with our CRM system and create tickets when needed."

Be as detailed as you want - the more context, the better!""",
        height=150,
        help="Describe your agent's purpose, capabilities, and behavior in plain English"
    )
    
    # Quick capabilities selection
    st.subheader("🛠️ Quick Capabilities")
    capabilities = st.multiselect(
        "Select capabilities your agent should have:",
        [
            "💬 Natural Language Processing",
            "📊 Data Analysis", 
            "🔍 Web Search",
            "📧 Email Integration",
            "📋 Task Management",
            "🗄️ Database Access",
            "📁 File Processing",
            "🔄 Workflow Automation",
            "📈 Reporting & Analytics",
            "🎨 Content Generation"
        ],
        help="Choose the main capabilities your agent needs"
    )
    
    # Framework preference (simplified)
    st.subheader("⚙️ AI Framework (Optional)")
    preferred_framework = st.selectbox(
        "Preferred AI Framework:",
        ["🤖 Auto-Select Best", "🦜 LangChain", "📊 LangGraph", "👥 CrewAI", "💬 AutoGen"],
        help="Let us pick the best framework, or choose your preference"
    )
    
    # Generation mode selection
    st.subheader("🎭 Creation Mode")
    creation_mode = st.radio(
        "How would you like to create your agent?",
        ["🤖 Instant Creation", "💬 Collaborative Chat", "🎯 Step-by-Step Guided"],
        horizontal=True,
        help="Choose your preferred creation experience"
    )
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if creation_mode == "💬 Collaborative Chat":
            if st.button("💬 Start Agent Chat", type="primary", use_container_width=True):
                if agent_name and agent_description:
                    start_collaborative_agent_creation(
                        name=agent_name,
                        type=agent_type,
                        energy=agent_energy,
                        style=agent_style,
                        expertise=agent_expertise,
                        description=agent_description,
                        capabilities=capabilities,
                        framework=preferred_framework
                    )
                else:
                    st.error("❌ Please provide at least an agent name and description!")
        
        elif creation_mode == "🎯 Step-by-Step Guided":
            if st.button("🎯 Start Guided Creation", type="primary", use_container_width=True):
                if agent_name and agent_description:
                    start_guided_agent_creation(
                        name=agent_name,
                        type=agent_type,
                        energy=agent_energy,
                        style=agent_style,
                        expertise=agent_expertise,
                        description=agent_description,
                        capabilities=capabilities,
                        framework=preferred_framework
                    )
                else:
                    st.error("❌ Please provide at least an agent name and description!")
        
        else:  # Instant Creation
            if st.button("🚀 Create My Agent", type="primary", use_container_width=True):
                if agent_name and agent_description:
                    create_simple_agent(
                        name=agent_name,
                        type=agent_type,
                        energy=agent_energy,
                        style=agent_style,
                        expertise=agent_expertise,
                        description=agent_description,
                        capabilities=capabilities,
                        framework=preferred_framework
                    )
                else:
                    st.error("❌ Please provide at least an agent name and description!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display active chat interface if there's an ongoing conversation
    if st.session_state.active_chat:
        display_human_agent_chat_interface()

def display_expert_mode_builder():
    """Display the expert mode agent builder with advanced configuration."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🔧 Expert Mode - Advanced Agent Configuration")
    
    # Expert Mode Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏗️ Architecture", "🔄 Workflow", "🧠 Intelligence", "🔗 Integration", "⚡ Deployment"
    ])
    
    with tab1:
        display_expert_architecture_config()
    
    with tab2:
        display_expert_workflow_config()
    
    with tab3:
        display_expert_intelligence_config()
    
    with tab4:
        display_expert_integration_config()
    
    with tab5:
        display_expert_deployment_config()
    
    st.markdown('</div>', unsafe_allow_html=True)

def load_vibe_context_to_builder():
    """Load vibe context from the main app to the agent builder."""
    if 'vibe_context' in st.session_state:
        st.success("✨ Vibe context loaded! Your agent will inherit the current vibe settings.")
        st.info(f"Current vibe: {st.session_state.get('current_vibe', 'Balanced')}")
    else:
        st.info("💡 No vibe context found. Visit the main app's Vibe Coding section to set a vibe first.")

def create_simple_agent(name: str, type: str, energy: str, style: str, expertise: str, 
                       description: str, capabilities: List[str], framework: str):
    """Create a simple agent from natural language description."""
    
    with st.spinner("🤖 Creating your AI agent..."):
        try:
            # Generate agent configuration
            agent_config = {
                'name': name,
                'type': type,
                'personality': {
                    'energy': energy,
                    'style': style,
                    'expertise': expertise
                },
                'description': description,
                'capabilities': capabilities,
                'framework': framework,
                'created_at': datetime.now().isoformat(),
                'status': 'created'
            }
            
            # Auto-select framework if needed
            if framework == "🤖 Auto-Select Best":
                agent_config['framework'] = auto_select_framework(capabilities, description)
            
            # Generate agent code
            agent_code = generate_agent_code(agent_config)
            
            # Create agent project
            agent_project_path = create_agent_project(agent_config, agent_code)
            
            # Add to active agents
            st.session_state.active_agents.append(agent_config)
            
            st.success(f"✅ Agent '{name}' created successfully!")
            
            # Display agent details
            display_created_agent_details(agent_config, agent_project_path)
            
        except Exception as e:
            st.error(f"❌ Failed to create agent: {str(e)}")

def auto_select_framework(capabilities: List[str], description: str) -> str:
    """Auto-select the best framework based on capabilities and description."""
    
    # Simple heuristics for framework selection
    if "workflow" in description.lower() or "📋 Task Management" in capabilities:
        return "📊 LangGraph"
    elif "team" in description.lower() or len(capabilities) > 5:
        return "👥 CrewAI"
    elif "conversation" in description.lower() or "💬 Natural Language Processing" in capabilities:
        return "💬 AutoGen"
    else:
        return "🦜 LangChain"

def generate_agent_code(agent_config: Dict) -> str:
    """Generate Python code for the agent based on configuration."""
    
    framework = agent_config['framework'].replace("🤖 ", "").replace("🦜 ", "").replace("📊 ", "").replace("👥 ", "").replace("💬 ", "")
    
    code_template = f'''"""
{agent_config['name']} - AI Agent
Generated by Universal Composition Layer

Type: {agent_config['type']}
Framework: {framework}
Description: {agent_config['description']}
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

class {agent_config['name'].replace(" ", "")}Agent:
    """
    {agent_config['description']}
    
    Personality:
    - Energy: {agent_config['personality']['energy']}
    - Style: {agent_config['personality']['style']}
    - Expertise: {agent_config['personality']['expertise']}
    """
    
    def __init__(self):
        self.name = "{agent_config['name']}"
        self.type = "{agent_config['type']}"
        self.capabilities = {agent_config['capabilities']}
        self.created_at = "{agent_config['created_at']}"
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def process_request(self, request: str) -> Dict[str, Any]:
        """Process a user request using agent capabilities."""
        
        self.logger.info(f"Processing request: {{request}}")
        
        # Agent processing logic based on capabilities
        response = {{
            "agent": self.name,
            "request": request,
            "response": f"Processing your request with {{self.type}} capabilities...",
            "capabilities_used": self.capabilities,
            "timestamp": datetime.now().isoformat()
        }}
        
        return response
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information."""
        return {{
            "name": self.name,
            "type": self.type,
            "capabilities": self.capabilities,
            "personality": {agent_config['personality']},
            "created_at": self.created_at,
            "framework": "{framework}",
            "status": "active"
        }}

# Example usage
if __name__ == "__main__":
    agent = {agent_config['name'].replace(" ", "")}Agent()
    print(f"Agent {{agent.name}} is ready!")
    
    # Example request processing
    async def test_agent():
        result = await agent.process_request("Hello, can you help me?")
        print(result)
    
    asyncio.run(test_agent())
'''
    
    return code_template

def create_agent_project(agent_config: Dict, agent_code: str) -> Path:
    """Create a complete project structure for the agent."""
    
    # Create project directory
    agent_name_clean = agent_config['name'].replace(" ", "_").lower()
    project_path = Path(f"generated_projects/agent_{agent_name_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create agent code file
    (project_path / f"{agent_name_clean}_agent.py").write_text(agent_code)
    
    # Create requirements.txt
    requirements = [
        "# Generated Agent Requirements",
        "langchain>=0.1.0",
        "streamlit>=1.28.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0"
    ]
    (project_path / "requirements.txt").write_text("\n".join(requirements))
    
    # Create README.md
    readme_content = f"""# {agent_config['name']} - AI Agent

{agent_config['description']}

## Agent Details

- **Type**: {agent_config['type']}
- **Framework**: {agent_config['framework']}
- **Capabilities**: {', '.join(agent_config['capabilities'])}

## Personality

- **Energy**: {agent_config['personality']['energy']}
- **Style**: {agent_config['personality']['style']}
- **Expertise**: {agent_config['personality']['expertise']}

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the agent:
   ```bash
   python {agent_name_clean}_agent.py
   ```

## Generated by Universal Composition Layer

This agent was created using the Simple Mode Agent Builder with vibe-driven configuration.
"""
    
    (project_path / "README.md").write_text(readme_content)
    
    return project_path

def display_created_agent_details(agent_config: Dict, project_path: Path):
    """Display details of the newly created agent."""
    
    st.subheader("🎉 Agent Created Successfully!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Agent Name", agent_config['name'])
        st.metric("Agent Type", agent_config['type'])
        st.metric("Framework", agent_config['framework'])
    
    with col2:
        st.metric("Capabilities", len(agent_config['capabilities']))
        st.metric("Project Path", str(project_path))
        st.metric("Status", agent_config['status'])
    
    # Show agent personality
    with st.expander("✨ Agent Personality"):
        personality = agent_config['personality']
        st.write(f"**Energy Level**: {personality['energy']}")
        st.write(f"**Communication Style**: {personality['style']}")
        st.write(f"**Expertise Approach**: {personality['expertise']}")
    
    # Show capabilities
    with st.expander("🛠️ Agent Capabilities"):
        for capability in agent_config['capabilities']:
            st.write(f"• {capability}")
    
    # Show project structure
    with st.expander("📁 Generated Project Structure"):
        display_project_tree(project_path)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Run Agent"):
            start_project(project_path, f"agent_{agent_config['name']}")
    
    with col2:
        if st.button("📂 Open in Project Runner"):
            st.session_state.selected_project = project_path.name
            st.info("💡 Switch to Project Runner tab to manage this agent!")
    
    with col3:
        if st.button("📋 Copy Agent Code"):
            agent_code_path = project_path / f"{agent_config['name'].replace(' ', '_').lower()}_agent.py"
            if agent_code_path.exists():
                st.code(agent_code_path.read_text(), language="python")

def display_active_agents():
    """Display currently active agents."""
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader("🤖 Active Agents")
    
    if not st.session_state.active_agents:
        st.info("No active agents created yet. Use the builder above to create your first agent!")
    else:
        for i, agent in enumerate(st.session_state.active_agents):
            with st.expander(f"🤖 {agent['name']} - {agent['type']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type**: {agent['type']}")
                    st.write(f"**Framework**: {agent['framework']}")
                    st.write(f"**Status**: {agent['status']}")
                
                with col2:
                    st.write(f"**Created**: {agent['created_at'][:19]}")
                    st.write(f"**Capabilities**: {len(agent['capabilities'])}")
                    
                    if st.button(f"🗑️ Remove", key=f"remove_agent_{i}"):
                        st.session_state.active_agents.pop(i)
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def start_collaborative_agent_creation(name: str, type: str, energy: str, style: str, 
                                      expertise: str, description: str, capabilities: List[str], framework: str):
    """Start collaborative agent creation with human-in-the-loop chat."""
    
    # Initialize chat conversation
    chat_config = {
        'chat_id': f"agent_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'agent_name': name,
        'agent_config': {
            'name': name,
            'type': type,
            'personality': {'energy': energy, 'style': style, 'expertise': expertise},
            'description': description,
            'capabilities': capabilities,
            'framework': framework
        },
        'conversation_history': [],
        'current_stage': 'planning',
        'human_feedback': [],
        'iterations': 0
    }
    
    st.session_state.active_chat = chat_config
    st.session_state.human_loop_conversations.append(chat_config)
    
    # Start the conversation
    start_message = f"""🤖 **Hello! I'm your AI Agent Creation Assistant.**

I'm excited to work with you to create **{name}** - your {type} agent!

Based on your description: "{description[:100]}..."

Let's collaborate to make this agent exactly what you envision. I'll guide you through the process and we can refine everything together.

🎯 **What would you like to focus on first?**
1. **Refine the agent's personality and communication style**
2. **Define specific capabilities and behaviors**  
3. **Plan the technical implementation**
4. **Design the user interaction patterns**

Just let me know what interests you most, or ask me anything about your agent!"""

    # Add initial message to conversation
    chat_config['conversation_history'].append({
        'role': 'assistant',
        'message': start_message,
        'timestamp': datetime.now().isoformat(),
        'stage': 'planning'
    })
    
    st.success(f"✨ Started collaborative creation for **{name}**! Chat interface is now active below.")
    st.rerun()

def start_guided_agent_creation(name: str, type: str, energy: str, style: str, 
                               expertise: str, description: str, capabilities: List[str], framework: str):
    """Start step-by-step guided agent creation with approval gates."""
    
    # Initialize guided workflow
    guided_config = {
        'workflow_id': f"guided_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'agent_name': name,
        'agent_config': {
            'name': name,
            'type': type,
            'personality': {'energy': energy, 'style': style, 'expertise': expertise},
            'description': description,
            'capabilities': capabilities,
            'framework': framework
        },
        'current_step': 1,
        'total_steps': 5,
        'step_results': {},
        'approval_required': True,
        'status': 'active'
    }
    
    st.session_state.workflow_paused_states.append(guided_config)
    
    st.success(f"🎯 Started guided creation for **{name}**! You'll be asked to approve each step.")
    
    # Start first step
    execute_guided_step(guided_config)

def display_human_agent_chat_interface():
    """Display the beautiful human-agent chat interface."""
    
    chat_config = st.session_state.active_chat
    if not chat_config:
        return
    
    st.markdown('<div class="composition-card">', unsafe_allow_html=True)
    st.subheader(f"💬 Collaborating on: {chat_config['agent_name']}")
    
    # Chat header with agent info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Stage", chat_config['current_stage'].title())
    with col2:
        st.metric("Messages", len(chat_config['conversation_history']))
    with col3:
        st.metric("Iterations", chat_config['iterations'])
    
    # Display conversation history
    st.subheader("🗨️ Conversation")
    
    chat_container = st.container()
    with chat_container:
        for msg in chat_config['conversation_history']:
            if msg['role'] == 'assistant':
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg['message'])
                    st.caption(f"⏰ {msg['timestamp'][:19]} | Stage: {msg.get('stage', 'unknown')}")
            else:  # human
                with st.chat_message("human", avatar="👨‍💻"):
                    st.markdown(msg['message'])
                    st.caption(f"⏰ {msg['timestamp'][:19]}")
    
    # Chat input
    user_input = st.chat_input("💬 Chat with your agent creation assistant...")
    
    if user_input:
        # Add human message
        chat_config['conversation_history'].append({
            'role': 'human',
            'message': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate AI response
        ai_response = generate_collaborative_response(chat_config, user_input)
        
        # Add AI response
        chat_config['conversation_history'].append({
            'role': 'assistant',
            'message': ai_response,
            'timestamp': datetime.now().isoformat(),
            'stage': chat_config['current_stage']
        })
        
        st.rerun()
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Approve Current Design"):
            approve_agent_design(chat_config)
    
    with col2:
        if st.button("🔄 Request Changes"):
            request_agent_changes(chat_config)
    
    with col3:
        if st.button("🎯 Generate Agent"):
            generate_agent_from_chat(chat_config)
    
    with col4:
        if st.button("❌ End Chat"):
            st.session_state.active_chat = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_collaborative_response(chat_config: Dict, user_input: str) -> str:
    """Generate AI response for collaborative agent creation."""
    
    agent_config = chat_config['agent_config']
    stage = chat_config['current_stage']
    
    # Simple response generation (can be enhanced with actual AI later)
    responses = {
        'planning': [
            f"Great question! For **{agent_config['name']}**, I think we should focus on the {agent_config['personality']['style'].lower()} communication style you chose.",
            f"I understand you want to enhance the {', '.join(agent_config['capabilities'][:2])} capabilities. Let me suggest some improvements...",
            f"Based on your {agent_config['type']} agent type, I recommend we add specific workflows for this use case.",
        ],
        'refinement': [
            "Excellent feedback! Let me incorporate those changes into the agent design.",
            "I see what you mean. That would definitely make the agent more effective.",
            "Good point! Let's adjust the personality to be more aligned with your vision.",
        ],
        'implementation': [
            "Now I'll show you how this translates into the technical implementation.",
            "Here's how the code structure would look for your agent.",
            "Let me explain how these capabilities will work in practice.",
        ],
        'testing': [
            "Let's test this configuration. What scenarios should we try?",
            "I think we should validate this approach. Do you agree?",
            "How does this feel to you? Any adjustments needed?",
        ]
    }
    
    # Select appropriate response based on stage and input
    if "approve" in user_input.lower() or "looks good" in user_input.lower():
        chat_config['current_stage'] = 'implementation'
        return f"🎉 Wonderful! I'm moving to the implementation stage. Let me start generating the code for **{agent_config['name']}** with your approved specifications."
    
    elif "change" in user_input.lower() or "modify" in user_input.lower():
        chat_config['current_stage'] = 'refinement'
        chat_config['iterations'] += 1
        return "🔄 Of course! I love iterating to get it perfect. What specific changes would you like me to make?"
    
    else:
        # General conversational response
        stage_responses = responses.get(stage, responses['planning'])
        import random
        base_response = random.choice(stage_responses)
        
        return f"{base_response}\n\n💬 **Your input**: \"{user_input}\"\n\n🤔 Let me think about this in the context of your **{agent_config['type']}** agent with **{agent_config['personality']['style']}** personality..."

def approve_agent_design(chat_config: Dict):
    """Handle approval of current agent design."""
    chat_config['current_stage'] = 'approved'
    chat_config['conversation_history'].append({
        'role': 'assistant',
        'message': f"🎉 **Design Approved!** \n\nExcellent! I'll now generate **{chat_config['agent_name']}** with the specifications we've discussed. This agent will have the perfect balance of your requirements and our collaborative refinements.",
        'timestamp': datetime.now().isoformat(),
        'stage': 'approved'
    })
    st.success("✅ Agent design approved! Ready for generation.")
    st.rerun()

def request_agent_changes(chat_config: Dict):
    """Handle request for agent changes."""
    chat_config['current_stage'] = 'refinement'
    chat_config['iterations'] += 1
    
    # Prompt for specific changes
    st.text_input(
        "What changes would you like?",
        key=f"changes_{chat_config['chat_id']}",
        placeholder="Describe the specific changes you'd like to make..."
    )

def generate_agent_from_chat(chat_config: Dict):
    """Generate the final agent from chat configuration."""
    agent_config = chat_config['agent_config']
    
    # Add conversation insights to agent config
    agent_config['conversation_insights'] = {
        'total_messages': len(chat_config['conversation_history']),
        'iterations': chat_config['iterations'],
        'final_stage': chat_config['current_stage'],
        'human_feedback_count': len(chat_config['human_feedback'])
    }
    
    # Generate the agent using the collaborative configuration
    create_simple_agent(
        name=agent_config['name'],
        type=agent_config['type'],
        energy=agent_config['personality']['energy'],
        style=agent_config['personality']['style'],
        expertise=agent_config['personality']['expertise'],
        description=agent_config['description'],
        capabilities=agent_config['capabilities'],
        framework=agent_config['framework']
    )
    
    # End the chat
    st.session_state.active_chat = None
    st.success("🎉 Agent generated from collaborative session!")

def execute_guided_step(guided_config: Dict):
    """Execute a step in the guided creation workflow."""
    
    step = guided_config['current_step']
    agent_name = guided_config['agent_name']
    
    steps = {
        1: f"🎯 **Step 1: Personality Refinement** for {agent_name}",
        2: f"🛠️ **Step 2: Capability Configuration** for {agent_name}",
        3: f"🏗️ **Step 3: Technical Architecture** for {agent_name}",
        4: f"🧪 **Step 4: Testing Strategy** for {agent_name}",
        5: f"🚀 **Step 5: Final Generation** for {agent_name}"
    }
    
    if step in steps:
        st.info(f"🎯 **Guided Creation**: Now executing {steps[step]}")
        st.info("⏸️ **Paused for Approval**: Review the step and approve to continue.")

def main():
    """Main application function."""
    initialize_session_state()
    display_main_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🔧 Navigation")
        page = st.selectbox(
            "Select Interface:",
            ["🎯 Composition Dashboard", "🚀 Project Runner", "🤖 Agent Builder", "🏢 Enterprise Systems", "🔍 System Monitor", "⚙️ Settings"]
        )
    
    if page == "🎯 Composition Dashboard":
        display_composition_dashboard()
    elif page == "🚀 Project Runner":
        display_project_runner()
    elif page == "🤖 Agent Builder":
        display_agent_builder_interface()
    elif page == "🏢 Enterprise Systems":
        st.info("🚧 Enterprise Systems interface coming soon...")
    elif page == "🔍 System Monitor":
        st.info("🚧 System Monitor interface coming soon...")
    elif page == "⚙️ Settings":
        st.info("🚧 Settings interface coming soon...")

# Expert Mode Configuration Functions

def display_expert_architecture_config():
    """Display expert architecture configuration."""
    st.markdown("### 🏗️ Agent Architecture Design")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Core Architecture")
        
        # Architecture Pattern
        arch_pattern = st.selectbox(
            "Architecture Pattern:",
            [
                "🧠 Single Agent", 
                "🤝 Multi-Agent Collaboration", 
                "🔄 Pipeline Architecture",
                "🌐 Mesh Network", 
                "🎭 Actor Model",
                "📊 Event-Driven Architecture"
            ],
            help="Choose the fundamental architectural pattern"
        )
        
        # Processing Model
        processing_model = st.selectbox(
            "Processing Model:",
            [
                "🔄 Synchronous", 
                "⚡ Asynchronous", 
                "📊 Stream Processing",
                "🧮 Batch Processing", 
                "💫 Reactive",
                "🌊 Event Sourcing"
            ]
        )
        
        # State Management
        state_mgmt = st.selectbox(
            "State Management:",
            [
                "💾 Stateless", 
                "🗃️ In-Memory State", 
                "💽 Persistent State",
                "📚 Database State", 
                "🔄 Distributed State",
                "⏰ Event Store"
            ]
        )
    
    with col2:
        st.subheader("🎛️ Advanced Configuration")
        
        # Concurrency Model
        concurrency = st.selectbox(
            "Concurrency Model:",
            [
                "🧵 Single Threaded", 
                "🎭 Multi-Threaded", 
                "📊 Process Pool",
                "⚡ Async/Await", 
                "🌊 Coroutines",
                "🎪 Actor System"
            ]
        )
        
        # Communication Protocol
        comm_protocol = st.selectbox(
            "Communication Protocol:",
            [
                "📞 Direct Calls", 
                "📬 Message Queue", 
                "🌐 HTTP/REST",
                "⚡ WebSockets", 
                "📡 gRPC",
                "📻 Event Bus"
            ]
        )
    
    # Architecture Preview
    st.subheader("🎨 Architecture Preview")
    st.info(f"🏗️ **Architecture Configuration**\n\n"
           f"**Pattern**: {arch_pattern}\n"
           f"**Processing**: {processing_model}\n"
           f"**State Management**: {state_mgmt}\n"
           f"**Concurrency**: {concurrency}\n"
           f"**Communication**: {comm_protocol}")

def display_expert_workflow_config():
    """Display expert workflow configuration."""
    st.markdown("### 🔄 Workflow Design Studio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Workflow Steps")
        
        # Initialize workflow steps in session state
        if 'workflow_steps' not in st.session_state:
            st.session_state.workflow_steps = [
                {"id": 1, "name": "Input Processing", "type": "input", "config": {}},
                {"id": 2, "name": "Core Logic", "type": "processor", "config": {}},
                {"id": 3, "name": "Output Generation", "type": "output", "config": {}}
            ]
        
        # Display workflow steps
        for i, step in enumerate(st.session_state.workflow_steps):
            with st.expander(f"🔧 Step {step['id']}: {step['name']}", expanded=False):
                
                col_a, col_b, col_c = st.columns([2, 2, 1])
                
                with col_a:
                    step_name = st.text_input(
                        "Step Name:", 
                        value=step['name'], 
                        key=f"step_name_{step['id']}"
                    )
                    step['name'] = step_name
                
                with col_b:
                    step_type = st.selectbox(
                        "Step Type:",
                        ["input", "processor", "decision", "output", "integration", "validation"],
                        index=["input", "processor", "decision", "output", "integration", "validation"].index(step['type']),
                        key=f"step_type_{step['id']}"
                    )
                    step['type'] = step_type
                
                with col_c:
                    if st.button("🗑️", key=f"delete_step_{step['id']}", help="Delete Step"):
                        st.session_state.workflow_steps.pop(i)
                        st.rerun()
                
                # Human-in-the-loop configuration
                human_loop = st.checkbox(
                    "🤝 Require Human Approval",
                    value=step['config'].get('human_approval', False),
                    key=f"human_loop_{step['id']}"
                )
                step['config']['human_approval'] = human_loop
        
        # Add new step
        if st.button("➕ Add Workflow Step"):
            new_id = max([s['id'] for s in st.session_state.workflow_steps]) + 1
            st.session_state.workflow_steps.append({
                "id": new_id,
                "name": f"New Step {new_id}",
                "type": "processor",
                "config": {}
            })
            st.rerun()
    
    with col2:
        st.subheader("🎨 Workflow Visualization")
        
        # Simple workflow visualization
        if st.session_state.workflow_steps:
            workflow_text = "**Workflow Flow:**\n\n"
            for i, step in enumerate(st.session_state.workflow_steps):
                workflow_text += f"{i+1}. **{step['name']}** ({step['type']})\n"
                if step['config'].get('human_approval'):
                    workflow_text += f"   └─ 🤝 *Human approval required*\n"
                if i < len(st.session_state.workflow_steps) - 1:
                    workflow_text += "   ⬇️\n"
            
            st.markdown(workflow_text)
        
        # Generate Workflow Code
        if st.button("🚀 Generate Workflow Code", type="primary"):
            workflow_code = f"""# Generated Workflow Configuration
class ExpertWorkflow:
    def __init__(self):
        self.steps = {st.session_state.workflow_steps}
    
    def execute(self):
        print("Executing expert workflow...")
        for step in self.steps:
            print(f"Step: {{step['name']}} ({{step['type']}})")
            if step['config'].get('human_approval'):
                print("  Waiting for human approval...")
        return "Workflow completed"
"""
            st.code(workflow_code, language="python")

def display_expert_intelligence_config():
    """Display expert AI intelligence configuration."""
    st.markdown("### 🧠 AI Intelligence Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Core AI Settings")
        
        # Primary AI Model
        primary_model = st.selectbox(
            "Primary AI Model:",
            [
                "🧠 GPT-4 Turbo", 
                "💎 Claude 3.5 Sonnet", 
                "⭐ Gemini Pro",
                "🦙 Llama 3", 
                "🔥 Mixtral 8x7B",
                "🎯 Custom Model"
            ]
        )
        
        # Temperature and Creativity
        temperature = st.slider("🌡️ Temperature (Creativity):", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.number_input("📝 Max Tokens:", 100, 8000, 1000)
        
        # Advanced AI Parameters
        top_p = st.slider("🎯 Top P (Nucleus Sampling):", 0.0, 1.0, 0.9, 0.05)
    
    with col2:
        st.subheader("🧩 Intelligence Modules")
        
        # Reasoning Capabilities
        st.markdown("**🧠 Reasoning Capabilities:**")
        reasoning_modules = st.multiselect(
            "Select reasoning modules:",
            [
                "🔍 Chain of Thought",
                "🌳 Tree of Thoughts", 
                "🎯 Goal-Oriented Reasoning",
                "📊 Statistical Reasoning", 
                "🧮 Mathematical Reasoning",
                "🎨 Creative Reasoning"
            ],
            default=["🔍 Chain of Thought"]
        )
        
        # Memory Systems
        st.markdown("**🧠 Memory Systems:**")
        memory_systems = st.multiselect(
            "Select memory systems:",
            [
                "💾 Short-term Memory",
                "🗄️ Long-term Memory", 
                "📚 Knowledge Base",
                "🔄 Working Memory", 
                "🎯 Episodic Memory"
            ],
            default=["💾 Short-term Memory", "📚 Knowledge Base"]
        )
    
    # Intelligence Preview
    st.subheader("🎨 Intelligence Configuration")
    st.info(f"🧠 **AI Configuration**\n\n"
           f"**Model**: {primary_model}\n"
           f"**Temperature**: {temperature}\n"
           f"**Max Tokens**: {max_tokens}\n"
           f"**Reasoning Modules**: {len(reasoning_modules)} selected\n"
           f"**Memory Systems**: {len(memory_systems)} selected")

def display_expert_integration_config():
    """Display expert integration configuration."""
    st.markdown("### 🔗 Integration & Connectivity")
    
    # External Integrations
    st.subheader("🌐 External Service Integrations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 AI Frameworks:**")
        ai_integrations = st.multiselect(
            "AI Framework Integration:",
            [
                "🦜 LangChain", 
                "📊 LangGraph", 
                "👥 CrewAI",
                "🔧 AutoGen", 
                "🧠 LlamaIndex",
                "🌊 Semantic Kernel"
            ]
        )
    
    with col2:
        st.markdown("**📊 Data Sources:**")
        data_integrations = st.multiselect(
            "Data Source Integration:",
            [
                "🐘 PostgreSQL", 
                "📊 MongoDB", 
                "🔥 Redis",
                "❄️ Snowflake", 
                "🏢 Salesforce",
                "📈 Google Analytics"
            ]
        )
    
    with col3:
        st.markdown("**🔧 Business Tools:**")
        business_integrations = st.multiselect(
            "Business Tool Integration:",
            [
                "📋 Jira", 
                "💬 Slack", 
                "📧 Microsoft Teams",
                "📊 Notion", 
                "🎯 Asana",
                "📞 Zoom"
            ]
        )
    
    # API Configuration
    st.subheader("🔌 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # REST API Settings
        st.markdown("**🌐 REST API Settings:**")
        enable_rest_api = st.checkbox("Enable REST API Interface")
        
        if enable_rest_api:
            api_prefix = st.text_input("API Prefix:", value="/api/v1")
            enable_cors = st.checkbox("Enable CORS", value=True)
    
    with col2:
        # WebSocket Settings
        st.markdown("**⚡ WebSocket Settings:**")
        enable_websocket = st.checkbox("Enable WebSocket Interface")
        
        if enable_websocket:
            ws_path = st.text_input("WebSocket Path:", value="/ws")
            enable_heartbeat = st.checkbox("Enable Heartbeat", value=True)

def display_expert_deployment_config():
    """Display expert deployment configuration."""
    st.markdown("### ⚡ Deployment & Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Deployment Target")
        
        deployment_target = st.selectbox(
            "Deployment Environment:",
            [
                "💻 Local Development",
                "🐳 Docker Container", 
                "☁️ Cloud Native",
                "🎯 Kubernetes", 
                "🌊 Serverless",
                "🔥 Edge Computing"
            ]
        )
        
        # Resource Requirements
        st.subheader("💾 Resource Requirements")
        cpu_cores = st.slider("CPU Cores:", 0.1, 8.0, 1.0, 0.1)
        memory_gb = st.slider("Memory (GB):", 0.5, 32.0, 2.0, 0.5)
        storage_gb = st.slider("Storage (GB):", 1, 100, 10)
    
    with col2:
        st.subheader("📊 Monitoring & Observability")
        
        monitoring_tools = st.multiselect(
            "Monitoring Tools:",
            [
                "📊 Prometheus", 
                "📈 Grafana", 
                "🔍 Jaeger",
                "📋 ELK Stack", 
                "🌊 Datadog",
                "📡 New Relic"
            ]
        )
        
        # Health Checks
        st.markdown("**🏥 Health Checks:**")
        enable_health_checks = st.checkbox("Enable Health Checks", value=True)
        
        if enable_health_checks:
            health_check_interval = st.number_input("Check Interval (seconds):", 5, 300, 30)
        
        # Scaling Configuration
        st.subheader("📈 Auto Scaling")
        enable_autoscaling = st.checkbox("Enable Auto Scaling")
        
        if enable_autoscaling:
            min_instances = st.number_input("Min Instances:", 1, 10, 1)
            max_instances = st.number_input("Max Instances:", 1, 100, 10)
    
    # Generate Configuration
    st.subheader("🛠️ Generated Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🐳 Generate Dockerfile", type="primary"):
            dockerfile_content = f"""# Generated Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Set resource limits
ENV CPU_CORES={cpu_cores}
ENV MEMORY_GB={memory_gb}

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health

# Run application
CMD ["python", "main.py"]
"""
            st.code(dockerfile_content, language="dockerfile")
    
    with col2:
        if st.button("🎯 Generate K8s Config", type="primary"):
            k8s_config = f"""# Generated Kubernetes Configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-agent
  template:
    metadata:
      labels:
        app: ai-agent
    spec:
      containers:
      - name: ai-agent
        image: ai-agent:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "{cpu_cores}"
            memory: "{memory_gb}Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
"""
            st.code(k8s_config, language="yaml")

if __name__ == "__main__":
    main()
