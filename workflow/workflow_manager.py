"""
Workflow Manager for AI Development Agent.
Manages workflow execution and state management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from models.state import AgentState
from models.responses import WorkflowResult, WorkflowStatus
from models.config import SystemConfig


class WorkflowManager:
    """
    Manages workflow execution and state management.
    """
    
    def __init__(self, config: SystemConfig):
        """
        Initialize the workflow manager.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.logger = logging.getLogger("workflow_manager")
        self.active_workflows: Dict[str, Any] = {}
        
    async def execute_workflow(
        self,
        workflow_graph: Any,
        initial_state: AgentState,
        session_id: str
    ) -> WorkflowResult:
        """
        Execute a workflow with the given initial state.
        
        Args:
            workflow_graph: Compiled LangGraph workflow
            initial_state: Initial workflow state
            session_id: Unique session identifier
            
        Returns:
            Workflow result
        """
        start_time = datetime.now()
        self.logger.info(f"Starting workflow execution for session: {session_id}")
        
        try:
            # Execute the workflow
            result_state = await workflow_graph.ainvoke(initial_state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Combine all file types for generated_files
            code_files = result_state.get("code_files", {})
            test_files = result_state.get("tests", {})
            documentation_files = result_state.get("documentation", {})
            configuration_files = result_state.get("configuration_files", {})
            
            # Merge all file types into generated_files
            generated_files = {}
            generated_files.update(code_files)
            generated_files.update(test_files)
            generated_files.update(documentation_files)
            generated_files.update(configuration_files)
            
            # Create workflow result
            workflow_result = WorkflowResult(
                workflow_id=session_id,
                session_id=session_id,
                status=WorkflowStatus.COMPLETED,
                project_name=result_state.get("project_name", ""),
                project_context=result_state.get("project_context", ""),
                agent_results=result_state.get("agent_outputs", {}),
                generated_files=generated_files,
                code_files=code_files,
                test_files=test_files,
                documentation_files=documentation_files,
                configuration_files=configuration_files,
                total_execution_time=execution_time,
                start_time=start_time,
                end_time=datetime.now(),
                human_approvals=result_state.get("approval_requests", []),
                errors=result_state.get("errors", []),
                warnings=result_state.get("warnings", [])
            )
            
            self.logger.info(f"Workflow completed successfully in {execution_time:.2f}s")
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create error result
            workflow_result = WorkflowResult(
                workflow_id=session_id,
                session_id=session_id,
                status=WorkflowStatus.FAILED,
                project_name=initial_state.get("project_name", ""),
                project_context=initial_state.get("project_context", ""),
                agent_results={},  # Empty agent results for failed workflow
                total_execution_time=execution_time,
                start_time=start_time,
                end_time=datetime.now(),
                errors=[{"error": str(e), "timestamp": datetime.now().isoformat()}]
            )
            
            return workflow_result
    
    def get_workflow_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Workflow status information
        """
        if session_id in self.active_workflows:
            return self.active_workflows[session_id]
        return None
    
    def cancel_workflow(self, session_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if workflow was cancelled successfully
        """
        if session_id in self.active_workflows:
            # Implementation would depend on the specific workflow execution mechanism
            self.logger.info(f"Cancelling workflow: {session_id}")
            return True
        return False
    
    def cleanup_workflow(self, session_id: str) -> None:
        """
        Clean up workflow resources.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.active_workflows:
            del self.active_workflows[session_id]
            self.logger.info(f"Cleaned up workflow: {session_id}")
    
    def get_active_workflows(self) -> Dict[str, Any]:
        """
        Get all active workflows.
        
        Returns:
            Dictionary of active workflows
        """
        return self.active_workflows.copy()
