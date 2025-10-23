#!/usr/bin/env python3
"""
Base supervisor classes for the hybrid supervisor-swarm architecture.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


# LangGraph integration check
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available - agent will work in legacy mode only")

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel


class SupervisorConfig(BaseModel):
    """Configuration for supervisor agents."""
    quality_thresholds: Dict[str, float]
    max_retries: int = 3
    escalation_threshold: float = 0.7
    enable_parallel_execution: bool = True




class BaseSupervisorState(BaseModel):
    """State for BaseSupervisor LangGraph workflow using Pydantic BaseModel."""
    
    # Input fields
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    
    # Output fields
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    
    # Control fields
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Execution metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

class BaseSupervisor(ABC):
    """Base class for all supervisor agents."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, config: SupervisorConfig):
        self.llm = llm
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.decision_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a supervisory decision based on context."""
        pass
    
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            self.logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            self.logger.info("⚠️ LangGraph not available - using legacy mode")

    def log_decision(self, decision: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Log a supervisory decision."""
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": context
        }
        self.decision_history.append(decision_record)
        self.logger.info(f"Supervisor decision: {decision}")
        return decision_record
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decisions from history."""
        return self.decision_history[-limit:] if self.decision_history else []
    
    async def validate_quality(self, output: Any, task_type: str) -> Dict[str, Any]:
        """Validate output quality against configured thresholds."""
        try:
            # Get quality threshold for this task type
            threshold = self.config.quality_thresholds.get(task_type, 0.7)
            
            # Perform quality assessment (to be implemented by subclasses)
            quality_score = await self._assess_quality(output, task_type)
            
            # Determine if quality meets threshold
            is_approved = quality_score >= threshold
            
            result = {
                "task_type": task_type,
                "quality_score": quality_score,
                "threshold": threshold,
                "is_approved": is_approved,
                "timestamp": datetime.now().isoformat(),
                "supervisor": self.__class__.__name__
            }
            
            # Log the validation decision
            self.log_decision({
                "action": "quality_validation",
                "task_type": task_type,
                "quality_score": quality_score,
                "is_approved": is_approved
            }, {"output": str(output)[:200]})  # Truncate for logging
            
            return result
            
        except Exception as e:
            self.logger.error(f"Quality validation failed: {e}")
            return {
                "task_type": task_type,
                "quality_score": 0.0,
                "threshold": 0.7,
                "is_approved": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "supervisor": self.__class__.__name__
            }
    
    @abstractmethod
    async def _assess_quality(self, output: Any, task_type: str) -> float:
        """Assess the quality of an output (to be implemented by subclasses)."""
        pass
    
    async def handle_escalation(self, escalation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalations from worker agents."""
        try:
            self.logger.info(f"Handling escalation: {escalation.get('issue', 'Unknown issue')}")
            
            # Analyze escalation
            analysis = await self._analyze_escalation(escalation)
            
            # Determine resolution strategy
            resolution = await self._determine_resolution_strategy(analysis)
            
            # Execute resolution
            result = await self._execute_resolution(resolution)
            
            # Log escalation handling
            self.log_decision({
                "action": "escalation_handling",
                "escalation_id": escalation.get("id", "unknown"),
                "resolution": resolution,
                "status": "resolved"
            }, {"escalation": escalation})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Escalation handling failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "supervisor": self.__class__.__name__
            }
    
    async def _analyze_escalation(self, escalation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an escalation to understand the issue."""
        # Default implementation - subclasses can override
        return {
            "issue_type": escalation.get("issue_type", "unknown"),
            "severity": escalation.get("severity", "medium"),
            "affected_components": escalation.get("affected_components", []),
            "recommended_actions": escalation.get("recommended_actions", [])
        }
    
    async def _determine_resolution_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best resolution strategy for an escalation."""
        # Default implementation - subclasses can override
        return {
            "strategy": "manual_intervention",
            "priority": "medium",
            "estimated_time": "1-2 hours",
            "required_resources": ["human_review", "code_analysis"]
        }
    
    async def _execute_resolution(self, resolution: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a resolution strategy."""
        # Default implementation - subclasses can override
        return {
            "status": "resolved",
            "resolution_applied": resolution.get("strategy", "unknown"),
            "resolution_time": datetime.now().isoformat(),
            "notes": "Resolution executed successfully"
        }
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get the decision history for this supervisor."""
        return self.decision_history.copy()
    
    def clear_decision_history(self):
        """Clear the decision history."""
        self.decision_history.clear()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this supervisor."""
        if not self.decision_history:
            return {
                "total_decisions": 0,
                "approval_rate": 0.0,
                "average_quality_score": 0.0,
                "escalations_handled": 0
            }
        
        total_decisions = len(self.decision_history)
        quality_validations = [d for d in self.decision_history if d.get("decision", {}).get("action") == "quality_validation"]
        escalations = [d for d in self.decision_history if d.get("decision", {}).get("action") == "escalation_handling"]
        
        approval_rate = 0.0
        if quality_validations:
            approved = sum(1 for v in quality_validations if v.get("decision", {}).get("is_approved", False))
            approval_rate = approved / len(quality_validations)
        
        average_quality_score = 0.0
        if quality_validations:
            scores = [v.get("decision", {}).get("quality_score", 0.0) for v in quality_validations]
            average_quality_score = sum(scores) / len(scores)
        
        return {
            "total_decisions": total_decisions,
            "approval_rate": approval_rate,
            "average_quality_score": average_quality_score,
            "escalations_handled": len(escalations),
            "last_decision": self.decision_history[-1]["timestamp"] if self.decision_history else None
        }

    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for BaseSupervisor."""
        workflow = StateGraph(BaseSupervisorState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: BaseSupervisorState) -> BaseSupervisorState:
        """Execute agent in LangGraph workflow."""
        import time
        start = time.time()
        
        try:
            # Call the agent's execute method
            result = await self.execute(state.input_data)
            
            # Update state with results
            state.output_data = result
            state.status = "completed"
            state.metrics["execution_time"] = time.time() - start
            
        except Exception as e:
            self.logger.error(f"LangGraph execution failed: {e}")
            state.errors.append(str(e))
            state.status = "failed"
            state.metrics["execution_time"] = time.time() - start
        
        return state


# Export for LangGraph Studio
# Note: BaseSupervisor is an abstract class and cannot be instantiated directly
# Concrete implementations should provide their own graph exports
graph = None
