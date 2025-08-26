#!/usr/bin/env python3
"""
Base supervisor classes for the hybrid supervisor-swarm architecture.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel


class SupervisorConfig(BaseModel):
    """Configuration for supervisor agents."""
    quality_thresholds: Dict[str, float]
    max_retries: int = 3
    escalation_threshold: float = 0.7
    enable_parallel_execution: bool = True


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
    
    def log_decision(self, decision: Dict[str, Any], context: Dict[str, Any]):
        """Log a supervisory decision."""
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": context
        })
        self.logger.info(f"Supervisor decision: {decision}")
    
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
