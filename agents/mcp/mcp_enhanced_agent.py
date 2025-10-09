#!/usr/bin/env python3
"""
MCP-Enhanced Agent
=================

Demonstration agent that showcases LangChain-MCP integration.
This agent has access to all MCP tools through the LangChain interface.

Features:
- Full MCP tool integration
- LangChain agent framework compatibility
- Universal Agent Tracker integration
- Performance monitoring and metrics
- Automatic tool discovery and registration

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 2)
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import base agent
try:
    from agents.core.enhanced_base_agent import EnhancedBaseAgent
    from agents.core.base_agent import AgentConfig
    BASE_AGENT_AVAILABLE = True
except ImportError:
    # Fallback if base agent not available
    class EnhancedBaseAgent:
        def __init__(self, config, gemini_client=None):
            self.config = config
            self.gemini_client = gemini_client
            self.logger = logging.getLogger(f"agent.{config.agent_id}")
    
    class AgentConfig:
        def __init__(self, agent_id, agent_type, prompt_template_id, **kwargs):
            self.agent_id = agent_id
            self.agent_type = agent_type
            self.prompt_template_id = prompt_template_id
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    BASE_AGENT_AVAILABLE = False

# Import MCP integration
try:
    from utils.mcp.langchain_integration import MCPAgentMixin, MCPToolkit, create_mcp_toolkit
    from utils.mcp.server import ToolCategory
    MCP_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MCP integration not available: {e}")
    MCP_INTEGRATION_AVAILABLE = False

# LangChain imports
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.schema import AgentAction, AgentFinish
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class MCPEnhancedAgent(EnhancedBaseAgent, MCPAgentMixin if MCP_INTEGRATION_AVAILABLE else object):
    """
    Enhanced agent with full MCP tool integration.
    
    Combines the enhanced base agent capabilities with MCP tool access,
    providing a powerful agent that can use all available MCP tools
    through the LangChain interface.
    """
    
    def __init__(self, config: AgentConfig, gemini_client=None):
        """
        Initialize MCP-enhanced agent.
        
        Args:
            config: Agent configuration
            gemini_client: Gemini client instance
        """
        super().__init__(config, gemini_client)
        
        # MCP-specific initialization
        self.mcp_tools_loaded = False
        self.available_tool_categories = []
        self.tool_execution_history = []
        self.mcp_metrics = {}
        
        logger.info(f"🤖 MCP-Enhanced Agent '{config.agent_id}' initialized")
        
        if MCP_INTEGRATION_AVAILABLE:
            logger.info(f"🔌 MCP integration active for agent '{config.agent_id}'")
        else:
            logger.warning(f"⚠️ MCP integration not available for agent '{config.agent_id}'")
    
    async def initialize_agent(self, auto_discover_tools: bool = True) -> bool:
        """
        Initialize the agent with MCP capabilities.
        
        Args:
            auto_discover_tools: Automatically discover and load MCP tools
            
        Returns:
            True if initialization successful
        """
        try:
            logger.info(f"🚀 Initializing MCP-Enhanced Agent '{self.config.agent_id}'...")
            
            # Initialize MCP toolkit if available
            if MCP_INTEGRATION_AVAILABLE:
                success = await self.initialize_mcp(auto_discover_tools)
                if success:
                    self.mcp_tools_loaded = True
                    self._analyze_available_tools()
                    logger.info(f"✅ MCP tools loaded: {len(self.get_mcp_tools())} tools available")
                else:
                    logger.warning("⚠️ MCP initialization failed, continuing without MCP tools")
            
            # Initialize other agent components
            await self._initialize_agent_components()
            
            logger.info(f"🎯 Agent '{self.config.agent_id}' initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            return False
    
    def _analyze_available_tools(self):
        """Analyze available MCP tools and categorize them."""
        if not self.mcp_tools_loaded:
            return
        
        tools = self.get_mcp_tools()
        categories = set()
        
        for tool in tools:
            if hasattr(tool.tool_definition, 'category'):
                categories.add(tool.tool_definition.category)
        
        self.available_tool_categories = list(categories)
        
        logger.info(f"📊 Available tool categories: {[str(cat) for cat in self.available_tool_categories]}")
    
    async def _initialize_agent_components(self):
        """Initialize additional agent components."""
        # Initialize prompt system
        self.prompt_system = self._initialize_prompt_system()
        
        # Initialize performance monitoring
        self.performance_monitor = {
            'start_time': datetime.now(),
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'tool_executions': 0
        }
        
        logger.info("🔧 Agent components initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using available tools and capabilities.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🎯 Executing task: {task.get('description', 'Unknown task')}")
            
            # Update performance metrics
            self.performance_monitor['total_tasks'] += 1
            
            # Analyze task requirements
            task_analysis = await self._analyze_task_requirements(task)
            
            # Select appropriate tools
            selected_tools = await self._select_tools_for_task(task_analysis)
            
            # Execute task with selected tools
            result = await self._execute_task_with_tools(task, selected_tools)
            
            # Update metrics
            self.performance_monitor['successful_tasks'] += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Task completed in {execution_time:.2f}s")
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time,
                'tools_used': [tool.name for tool in selected_tools],
                'task_analysis': task_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.performance_monitor['failed_tasks'] += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"❌ Task execution failed after {execution_time:.2f}s: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_task_requirements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze task to determine tool requirements.
        
        Args:
            task: Task to analyze
            
        Returns:
            Task analysis results
        """
        task_type = task.get('type', 'general')
        task_description = task.get('description', '')
        task_data = task.get('data', {})
        
        # Determine required tool categories based on task
        required_categories = []
        
        if 'agile' in task_description.lower() or 'story' in task_description.lower():
            required_categories.append(ToolCategory.AGILE)
        
        if 'file' in task_description.lower() or 'create' in task_description.lower():
            required_categories.append(ToolCategory.FILE_SYSTEM)
        
        if 'git' in task_description.lower() or 'commit' in task_description.lower():
            required_categories.append(ToolCategory.GIT)
        
        if 'test' in task_description.lower():
            required_categories.append(ToolCategory.TESTING)
        
        if 'database' in task_description.lower() or 'track' in task_description.lower():
            required_categories.append(ToolCategory.DATABASE)
        
        if 'prompt' in task_description.lower() or 'ai' in task_description.lower():
            required_categories.append(ToolCategory.AI)
        
        return {
            'task_type': task_type,
            'description': task_description,
            'required_categories': required_categories,
            'complexity': len(required_categories),
            'data_provided': bool(task_data)
        }
    
    async def _select_tools_for_task(self, task_analysis: Dict[str, Any]) -> List[Any]:
        """
        Select appropriate tools for the task.
        
        Args:
            task_analysis: Task analysis results
            
        Returns:
            List of selected tools
        """
        selected_tools = []
        
        if not self.mcp_tools_loaded:
            logger.warning("⚠️ No MCP tools available for task execution")
            return selected_tools
        
        # Get tools by required categories
        for category in task_analysis['required_categories']:
            category_tools = self.get_mcp_tools(category)
            selected_tools.extend(category_tools)
        
        # If no specific categories, get some general tools
        if not selected_tools:
            all_tools = self.get_mcp_tools()
            # Select first few tools as fallback
            selected_tools = all_tools[:3] if len(all_tools) >= 3 else all_tools
        
        logger.info(f"🔧 Selected {len(selected_tools)} tools for task execution")
        return selected_tools
    
    async def _execute_task_with_tools(self, task: Dict[str, Any], tools: List[Any]) -> Dict[str, Any]:
        """
        Execute task using selected tools.
        
        Args:
            task: Task to execute
            tools: Selected tools
            
        Returns:
            Task execution results
        """
        results = {}
        
        # For demonstration, we'll execute a simple tool if available
        if tools:
            # Try to execute the first available tool with task data
            tool = tools[0]
            
            try:
                # Prepare parameters for tool execution
                parameters = task.get('data', {})
                if not parameters:
                    # Provide default parameters based on task
                    parameters = {
                        'agent_id': self.config.agent_id,
                        'task_description': task.get('description', ''),
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Execute tool
                tool_result = await tool._arun(parameters)
                
                results['tool_execution'] = {
                    'tool_name': tool.name,
                    'result': tool_result,
                    'success': True
                }
                
                # Update metrics
                self.performance_monitor['tool_executions'] += 1
                
                logger.info(f"🔧 Tool '{tool.name}' executed successfully")
                
            except Exception as e:
                logger.error(f"❌ Tool execution failed: {e}")
                results['tool_execution'] = {
                    'tool_name': tool.name,
                    'error': str(e),
                    'success': False
                }
        
        # Add task completion information
        results['task_completed'] = True
        results['tools_available'] = len(tools)
        results['agent_id'] = self.config.agent_id
        
        return results
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate task structure and requirements.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid
        """
        required_fields = ['description']
        
        for field in required_fields:
            if field not in task:
                logger.error(f"❌ Task missing required field: {field}")
                return False
        
        return True
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        status = {
            'agent_id': self.config.agent_id,
            'agent_type': self.config.agent_type,
            'mcp_integration': MCP_INTEGRATION_AVAILABLE,
            'mcp_tools_loaded': self.mcp_tools_loaded,
            'available_tool_categories': [str(cat) for cat in self.available_tool_categories],
            'performance_metrics': self.performance_monitor.copy(),
            'initialization_time': getattr(self, 'initialization_time', None)
        }
        
        # Add MCP toolkit metrics if available
        if self.mcp_tools_loaded and hasattr(self, 'mcp_toolkit'):
            status['mcp_metrics'] = self.mcp_toolkit.get_toolkit_metrics()
        
        return status
    
    async def shutdown(self):
        """Shutdown agent and cleanup resources."""
        logger.info(f"🛑 Shutting down MCP-Enhanced Agent '{self.config.agent_id}'")
        
        # Shutdown MCP toolkit
        if MCP_INTEGRATION_AVAILABLE and hasattr(self, 'mcp_toolkit'):
            await self.shutdown_mcp()
        
        # Log final metrics
        final_status = self.get_agent_status()
        logger.info(f"📊 Final agent metrics: {final_status['performance_metrics']}")


# Factory function for easy agent creation
def create_mcp_enhanced_agent(agent_id: str, agent_type: str = "mcp_enhanced", 
                            prompt_template_id: str = "default") -> MCPEnhancedAgent:
    """
    Create MCP-enhanced agent instance.
    
    Args:
        agent_id: Unique agent identifier
        agent_type: Agent type
        prompt_template_id: Prompt template to use
        
    Returns:
        Configured MCP-enhanced agent
    """
    config = AgentConfig(
        agent_id=agent_id,
        agent_type=agent_type,
        prompt_template_id=prompt_template_id,
        optimization_enabled=True,
        performance_monitoring=True
    )
    
    return MCPEnhancedAgent(config)


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test MCP-enhanced agent."""
        print("🤖 Testing MCP-Enhanced Agent...")
        
        # Create agent
        agent = create_mcp_enhanced_agent("test_mcp_agent", "test_agent")
        
        try:
            # Initialize agent
            success = await agent.initialize_agent()
            if not success:
                print("❌ Agent initialization failed")
                return
            
            print("✅ Agent initialized successfully")
            
            # Show agent status
            status = agent.get_agent_status()
            print(f"📊 Agent status: {status}")
            
            # Test task execution
            test_task = {
                'description': 'Test MCP tool integration',
                'type': 'integration_test',
                'data': {
                    'test_parameter': 'test_value',
                    'agent_id': 'test_mcp_agent'
                }
            }
            
            print("🎯 Executing test task...")
            result = await agent.execute(test_task)
            print(f"📋 Task result: {result}")
            
        finally:
            # Cleanup
            await agent.shutdown()
            print("🛑 Agent shutdown complete")
    
    # Run test
    asyncio.run(main())
