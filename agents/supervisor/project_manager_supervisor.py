#!/usr/bin/env python3
"""
Project Manager Supervisor for orchestrating the development workflow.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_supervisor import BaseSupervisor, SupervisorConfig
from models.supervisor_state import SupervisorSwarmState
from models.supervisor_state import Task, TaskResult, Escalation


class ProjectManagerSupervisor(BaseSupervisor):
    """Central coordinator for the development workflow."""
    
    def __init__(self, llm, config: SupervisorConfig):
        super().__init__(llm, config)
        self.worker_agents = {}
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
    
    async def orchestrate_workflow(self, project_context: str) -> Dict[str, Any]:
        """Orchestrate the entire development workflow."""
        self.logger.info("Starting project orchestration")
        
        # 1. Initialize project state
        initial_state = await self._initialize_project_state(project_context)
        
        # 2. Create task breakdown
        tasks = await self._create_task_breakdown(project_context)
        
        # 3. Prioritize and queue tasks
        self.task_queue = await self._prioritize_tasks(tasks)
        
        # 4. Execute workflow
        result = await self._execute_workflow(initial_state)
        
        return result
    
    async def delegate_task(self, task: Task, worker: str) -> TaskResult:
        """Delegate a specific task to a worker agent."""
        self.logger.info(f"Delegating task {task.id} to {worker}")
        
        # Create task prompt
        task_prompt = await self._create_task_prompt(task, worker)
        
        # Execute task
        result = await self.worker_agents[worker].execute_task(task_prompt)
        
        # Log delegation
        self.log_decision({
            "action": "task_delegation",
            "task_id": task.id,
            "worker": worker,
            "status": "completed"
        }, {"task": task.dict()})
        
        return TaskResult(
            task_id=task.id,
            worker=worker,
            result=result,
            timestamp=datetime.now()
        )
    
    async def handle_escalation(self, escalation: Escalation) -> Dict[str, Any]:
        """Handle escalations from worker agents."""
        self.logger.info(f"Handling escalation: {escalation.issue}")
        
        # Analyze escalation
        analysis = await self._analyze_escalation(escalation.dict())
        
        # Determine resolution strategy
        resolution = await self._determine_resolution_strategy(analysis)
        
        # Execute resolution
        result = await self._execute_resolution(resolution)
        
        # Log escalation handling
        self.log_decision({
            "action": "escalation_handling",
            "escalation_id": escalation.id,
            "resolution": resolution,
            "status": "resolved"
        }, {"escalation": escalation.dict()})
        
        return result
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a supervisory decision based on context."""
        decision_type = context.get("decision_type", "task_prioritization")
        
        if decision_type == "task_prioritization":
            return await self._prioritize_tasks_decision(context)
        elif decision_type == "resource_allocation":
            return await self._allocate_resources_decision(context)
        elif decision_type == "quality_gate":
            return await self._quality_gate_decision(context)
        elif decision_type == "escalation_handling":
            return await self._escalation_decision(context)
        else:
            return await self._default_decision(context)
    
    async def _assess_quality(self, output: Any, task_type: str) -> float:
        """Assess the quality of an output for project management tasks."""
        try:
            # Use LLM to assess quality
            prompt = f"""
            Assess the quality of this {task_type} output:
            
            OUTPUT:
            {str(output)[:1000]}
            
            Rate the quality from 0.0 to 1.0 based on:
            - Completeness (0.25 weight)
            - Accuracy (0.25 weight) 
            - Clarity (0.25 weight)
            - Feasibility (0.25 weight)
            
            Return only a number between 0.0 and 1.0.
            """
            
            response = await self.llm.ainvoke(prompt)
            quality_score = float(response.content.strip())
            
            # Ensure score is within valid range
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return 0.5  # Default to medium quality
    
    async def _initialize_project_state(self, project_context: str) -> SupervisorSwarmState:
        """Initialize the project state."""
        return SupervisorSwarmState(
            project_context=project_context,
            project_name="",
            session_id="",
            current_phase="planning",
            current_supervisor_task=None,
            active_agent=None,
            requirements=[],
            architecture={},
            code_files={},
            tests={},
            documentation={},
            agent_outputs={},
            supervisor_decisions=[],
            quality_validations=[],
            task_delegations=[],
            escalations=[],
            handoff_history=[],
            agent_collaborations=[],
            current_collaboration=None,
            errors=[],
            warnings=[],
            retry_count=0,
            execution_history=[],
            performance_metrics={}
        )
    
    async def _create_task_breakdown(self, project_context: str) -> List[Task]:
        """Create a breakdown of tasks from project context."""
        prompt = f"""
        Analyze this project context and create a comprehensive task breakdown:
        
        {project_context}
        
        Create tasks for:
        1. Requirements analysis
        2. Architecture design
        3. Code generation
        4. Test generation
        5. Code review
        6. Security analysis
        7. Documentation generation
        
        For each task, specify:
        - Task type
        - Description
        - Priority (low/medium/high/critical)
        - Estimated complexity (simple/moderate/complex)
        - Dependencies
        - Quality criteria
        """
        
        # Use LLM to create task breakdown
        response = await self.llm.ainvoke(prompt)
        
        # Parse response into Task objects
        tasks = self._parse_task_breakdown(response.content)
        
        return tasks
    
    def _parse_task_breakdown(self, response: str) -> List[Task]:
        """Parse LLM response into Task objects."""
        # This is a simplified parser - in practice, you'd use structured output parsing
        tasks = []
        
        # Default task breakdown for common development workflow
        default_tasks = [
            {
                "id": "task_1",
                "type": "requirements_analysis",
                "description": "Analyze project requirements and create detailed specifications",
                "priority": "high",
                "estimated_complexity": "moderate",
                "dependencies": [],
                "quality_criteria": {"completeness": 0.8, "clarity": 0.8}
            },
            {
                "id": "task_2", 
                "type": "architecture_design",
                "description": "Design system architecture based on requirements",
                "priority": "high",
                "estimated_complexity": "moderate",
                "dependencies": ["task_1"],
                "quality_criteria": {"scalability": 0.8, "maintainability": 0.8}
            },
            {
                "id": "task_3",
                "type": "code_generation", 
                "description": "Generate production-ready code based on architecture",
                "priority": "high",
                "estimated_complexity": "complex",
                "dependencies": ["task_2"],
                "quality_criteria": {"functionality": 0.9, "readability": 0.8}
            },
            {
                "id": "task_4",
                "type": "test_generation",
                "description": "Generate comprehensive tests for the code",
                "priority": "medium",
                "estimated_complexity": "moderate", 
                "dependencies": ["task_3"],
                "quality_criteria": {"coverage": 0.8, "effectiveness": 0.8}
            },
            {
                "id": "task_5",
                "type": "code_review",
                "description": "Review code for quality, security, and best practices",
                "priority": "medium",
                "estimated_complexity": "moderate",
                "dependencies": ["task_3"],
                "quality_criteria": {"thoroughness": 0.9, "actionability": 0.8}
            },
            {
                "id": "task_6",
                "type": "security_analysis",
                "description": "Analyze code and architecture for security vulnerabilities",
                "priority": "high",
                "estimated_complexity": "moderate",
                "dependencies": ["task_3", "task_2"],
                "quality_criteria": {"comprehensiveness": 0.9, "accuracy": 0.9}
            },
            {
                "id": "task_7",
                "type": "documentation_generation",
                "description": "Generate comprehensive documentation",
                "priority": "medium",
                "estimated_complexity": "moderate",
                "dependencies": ["task_3", "task_4"],
                "quality_criteria": {"completeness": 0.8, "clarity": 0.9}
            }
        ]
        
        for task_data in default_tasks:
            task = Task(
                id=task_data["id"],
                type=task_data["type"],
                description=task_data["description"],
                requirements={},
                priority=task_data["priority"],
                estimated_complexity=task_data["estimated_complexity"],
                dependencies=task_data["dependencies"],
                quality_criteria=task_data["quality_criteria"],
                created_at=datetime.now()
            )
            tasks.append(task)
        
        return tasks
    
    async def _prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Prioritize tasks based on dependencies and importance."""
        # Simple topological sort based on dependencies
        prioritized = []
        completed = set()
        
        while len(prioritized) < len(tasks):
            for task in tasks:
                if task.id not in completed:
                    # Check if all dependencies are completed
                    if all(dep in completed for dep in task.dependencies):
                        prioritized.append(task)
                        completed.add(task.id)
            
            # If no progress made, add remaining tasks
            if len(prioritized) == len(completed):
                for task in tasks:
                    if task.id not in completed:
                        prioritized.append(task)
                        completed.add(task.id)
                break
        
        return prioritized
    
    async def _execute_workflow(self, initial_state: SupervisorSwarmState) -> Dict[str, Any]:
        """Execute the workflow with the given tasks."""
        current_state = initial_state
        
        for task in self.task_queue:
            try:
                # Update state
                current_state["current_supervisor_task"] = task.id
                current_state["current_phase"] = f"executing_{task.type}"
                
                # Execute task (this would integrate with the actual workflow)
                task_result = await self._execute_task(task, current_state)
                
                # Update state with results
                current_state["task_delegations"].append(task_result.dict())
                current_state["execution_history"].append({
                    "task_id": task.id,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Task execution failed: {e}")
                current_state["errors"].append(f"Task {task.id} failed: {str(e)}")
                current_state["execution_history"].append({
                    "task_id": task.id,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        current_state["current_phase"] = "completed"
        return current_state
    
    async def _execute_task(self, task: Task, state: SupervisorSwarmState) -> TaskResult:
        """Execute a single task."""
        # This would integrate with the actual agent workflow
        # For now, return a mock result
        return TaskResult(
            task_id=task.id,
            worker=f"{task.type}_agent",
            result={"status": "completed", "output": f"Mock output for {task.type}"},
            timestamp=datetime.now()
        )
    
    async def _create_task_prompt(self, task: Task, worker: str) -> str:
        """Create a prompt for task execution."""
        return f"""
        TASK: {task.description}
        
        TASK TYPE: {task.type}
        PRIORITY: {task.priority}
        COMPLEXITY: {task.estimated_complexity}
        
        QUALITY CRITERIA:
        {task.quality_criteria}
        
        Please execute this task according to the quality criteria.
        """
    
    async def _prioritize_tasks_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision about task prioritization."""
        tasks = context.get("tasks", [])
        prioritized = await self._prioritize_tasks(tasks)
        
        return {
            "decision_type": "task_prioritization",
            "prioritized_tasks": [task.dict() for task in prioritized],
            "reasoning": "Tasks prioritized based on dependencies and critical path",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _allocate_resources_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision about resource allocation."""
        available_agents = context.get("available_agents", [])
        pending_tasks = context.get("pending_tasks", [])
        
        # Simple allocation strategy
        allocations = {}
        for i, task in enumerate(pending_tasks):
            agent = available_agents[i % len(available_agents)] if available_agents else "default_agent"
            allocations[task["id"]] = agent
        
        return {
            "decision_type": "resource_allocation",
            "allocations": allocations,
            "reasoning": "Round-robin allocation of tasks to available agents",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _quality_gate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision about quality gates."""
        output = context.get("output")
        task_type = context.get("task_type")
        
        validation_result = await self._assess_quality(output, task_type)
        
        return {
            "decision_type": "quality_gate",
            "validation_result": validation_result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _escalation_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision about escalations."""
        escalation = context.get("escalation", {})
        
        resolution = await self.handle_escalation(escalation)
        
        return {
            "decision_type": "escalation_handling",
            "resolution": resolution,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _default_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default decision for unknown decision types."""
        return {
            "decision_type": "default",
            "message": "No specific decision logic for this context",
            "timestamp": datetime.now().isoformat()
        }
