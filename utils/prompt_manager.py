"""
Prompt Management System for AI Development Agent.
Stores, analyzes, and improves agent prompts using SQLite database.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Manages prompt templates, stores usage data, and provides analysis tools.
    """
    
    def __init__(self, db_path: str = "prompts/prompt_templates.db"):
        """
        Initialize the prompt manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create prompts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    prompt_hash TEXT UNIQUE NOT NULL,
                    prompt_template TEXT NOT NULL,
                    prompt_variables TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    average_response_time REAL DEFAULT 0.0,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create prompt_executions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    execution_hash TEXT UNIQUE NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id)
                )
            """)
            
            # Create prompt_analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    analysis_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id)
                )
            """)
            
            # Create prompt_improvements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_prompt_id INTEGER NOT NULL,
                    improved_prompt_id INTEGER NOT NULL,
                    improvement_type TEXT NOT NULL,
                    improvement_reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (original_prompt_id) REFERENCES prompts (id),
                    FOREIGN KEY (improved_prompt_id) REFERENCES prompts (id)
                )
            """)
            
            conn.commit()
    
    def store_prompt(self, agent_name: str, prompt_template: str, 
                    prompt_variables: Dict[str, Any]) -> int:
        """
        Store a new prompt template in the database.
        
        Args:
            agent_name: Name of the agent using this prompt
            prompt_template: The prompt template string
            prompt_variables: Variables used in the prompt
            
        Returns:
            Prompt ID
        """
        prompt_hash = self._generate_prompt_hash(prompt_template)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if prompt already exists
            cursor.execute(
                "SELECT id FROM prompts WHERE prompt_hash = ?",
                (prompt_hash,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing prompt
                cursor.execute("""
                    UPDATE prompts 
                    SET updated_at = CURRENT_TIMESTAMP, is_active = 1
                    WHERE id = ?
                """, (existing[0],))
                return existing[0]
            else:
                # Insert new prompt
                cursor.execute("""
                    INSERT INTO prompts (agent_name, prompt_hash, prompt_template, 
                                       prompt_variables, created_at, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    agent_name,
                    prompt_hash,
                    prompt_template,
                    json.dumps(prompt_variables)
                ))
                return cursor.lastrowid
    
    def record_execution(self, prompt_id: int, input_data: Dict[str, Any],
                        output_data: Optional[Dict[str, Any]] = None,
                        execution_time: Optional[float] = None,
                        success: bool = True,
                        error_message: Optional[str] = None) -> str:
        """
        Record a prompt execution.
        
        Args:
            prompt_id: ID of the prompt used
            input_data: Input data provided to the prompt
            output_data: Output data received from the model
            execution_time: Time taken for execution
            success: Whether the execution was successful
            error_message: Error message if execution failed
            
        Returns:
            Execution hash
        """
        execution_hash = self._generate_execution_hash(prompt_id, input_data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert execution record
            cursor.execute("""
                INSERT INTO prompt_executions 
                (prompt_id, execution_hash, input_data, output_data, 
                 execution_time, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id,
                execution_hash,
                json.dumps(input_data),
                json.dumps(output_data) if output_data else None,
                execution_time,
                success,
                error_message
            ))
            
            # Update prompt usage statistics
            cursor.execute("""
                UPDATE prompts 
                SET usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (prompt_id,))
            
            # Update success rate
            if success:
                cursor.execute("""
                    UPDATE prompts 
                    SET success_rate = (
                        SELECT CAST(COUNT(CASE WHEN success = 1 THEN 1 END) AS FLOAT) / COUNT(*) * 100
                        FROM prompt_executions 
                        WHERE prompt_id = ?
                    )
                    WHERE id = ?
                """, (prompt_id, prompt_id))
            
            # Update average response time
            if execution_time:
                cursor.execute("""
                    UPDATE prompts 
                    SET average_response_time = (
                        SELECT AVG(execution_time)
                        FROM prompt_executions 
                        WHERE prompt_id = ? AND execution_time IS NOT NULL
                    )
                    WHERE id = ?
                """, (prompt_id, prompt_id))
            
            conn.commit()
        
        return execution_hash
    
    def get_prompt_statistics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for prompts.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            Dictionary with prompt statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if agent_name:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_prompts,
                        AVG(success_rate) as avg_success_rate,
                        AVG(average_response_time) as avg_response_time,
                        SUM(usage_count) as total_usage,
                        COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_prompts
                    FROM prompts 
                    WHERE agent_name = ?
                """, (agent_name,))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_prompts,
                        AVG(success_rate) as avg_success_rate,
                        AVG(average_response_time) as avg_response_time,
                        SUM(usage_count) as total_usage,
                        COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_prompts
                    FROM prompts
                """)
            
            row = cursor.fetchone()
            return {
                "total_prompts": row[0],
                "avg_success_rate": row[1] or 0.0,
                "avg_response_time": row[2] or 0.0,
                "total_usage": row[3] or 0,
                "active_prompts": row[4]
            }
    
    def analyze_prompt_performance(self, prompt_id: int) -> Dict[str, Any]:
        """
        Analyze performance of a specific prompt.
        
        Args:
            prompt_id: ID of the prompt to analyze
            
        Returns:
            Analysis results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get prompt details
            cursor.execute("""
                SELECT agent_name, prompt_template, usage_count, success_rate, 
                       average_response_time, created_at, last_used
                FROM prompts WHERE id = ?
            """, (prompt_id,))
            
            prompt_data = cursor.fetchone()
            if not prompt_data:
                return {"error": "Prompt not found"}
            
            # Get execution history
            cursor.execute("""
                SELECT success, execution_time, error_message, created_at
                FROM prompt_executions 
                WHERE prompt_id = ?
                ORDER BY created_at DESC
                LIMIT 100
            """, (prompt_id,))
            
            executions = cursor.fetchall()
            
            # Analyze patterns
            success_count = sum(1 for e in executions if e[0])
            total_executions = len(executions)
            recent_success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
            
            # Common error patterns
            cursor.execute("""
                SELECT error_message, COUNT(*) as count
                FROM prompt_executions 
                WHERE prompt_id = ? AND error_message IS NOT NULL
                GROUP BY error_message
                ORDER BY count DESC
                LIMIT 5
            """, (prompt_id,))
            
            error_patterns = cursor.fetchall()
            
            return {
                "prompt_id": prompt_id,
                "agent_name": prompt_data[0],
                "usage_count": prompt_data[2],
                "overall_success_rate": prompt_data[3] or 0.0,
                "recent_success_rate": recent_success_rate,
                "average_response_time": prompt_data[4] or 0.0,
                "created_at": prompt_data[5],
                "last_used": prompt_data[6],
                "total_executions": total_executions,
                "error_patterns": [{"error": e[0], "count": e[1]} for e in error_patterns],
                "performance_trend": self._calculate_performance_trend(executions)
            }
    
    def get_prompt_improvements(self, prompt_id: int) -> List[Dict[str, Any]]:
        """
        Get improvement suggestions for a prompt.
        
        Args:
            prompt_id: ID of the prompt to improve
            
        Returns:
            List of improvement suggestions
        """
        analysis = self.analyze_prompt_performance(prompt_id)
        improvements = []
        
        # Analyze success rate
        if analysis.get("overall_success_rate", 0) < 80:
            improvements.append({
                "type": "success_rate",
                "priority": "high",
                "suggestion": "Consider adding more specific instructions or examples to improve success rate",
                "current_value": analysis.get("overall_success_rate", 0),
                "target_value": 90
            })
        
        # Analyze response time
        if analysis.get("average_response_time", 0) > 30:
            improvements.append({
                "type": "response_time",
                "priority": "medium",
                "suggestion": "Consider simplifying the prompt or breaking it into smaller parts",
                "current_value": analysis.get("average_response_time", 0),
                "target_value": 15
            })
        
        # Analyze error patterns
        error_patterns = analysis.get("error_patterns", [])
        for pattern in error_patterns:
            if pattern["count"] > 3:
                improvements.append({
                    "type": "error_pattern",
                    "priority": "high",
                    "suggestion": f"Address recurring error: {pattern['error']}",
                    "error": pattern["error"],
                    "occurrence_count": pattern["count"]
                })
        
        return improvements
    
    def export_prompts(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Export all prompts and their statistics.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            Dictionary with exported prompt data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if agent_name:
                cursor.execute("""
                    SELECT id, agent_name, prompt_template, prompt_variables,
                           usage_count, success_rate, average_response_time,
                           created_at, last_used, is_active
                    FROM prompts 
                    WHERE agent_name = ?
                    ORDER BY usage_count DESC
                """, (agent_name,))
            else:
                cursor.execute("""
                    SELECT id, agent_name, prompt_template, prompt_variables,
                           usage_count, success_rate, average_response_time,
                           created_at, last_used, is_active
                    FROM prompts 
                    ORDER BY usage_count DESC
                """)
            
            prompts = cursor.fetchall()
            
            return {
                "export_date": datetime.now().isoformat(),
                "total_prompts": len(prompts),
                "prompts": [
                    {
                        "id": p[0],
                        "agent_name": p[1],
                        "prompt_template": p[2],
                        "prompt_variables": json.loads(p[3]),
                        "usage_count": p[4],
                        "success_rate": p[5],
                        "average_response_time": p[6],
                        "created_at": p[7],
                        "last_used": p[8],
                        "is_active": bool(p[9])
                    }
                    for p in prompts
                ]
            }
    
    def _generate_prompt_hash(self, prompt_template: str) -> str:
        """Generate a hash for the prompt template."""
        return hashlib.sha256(prompt_template.encode()).hexdigest()
    
    def _generate_execution_hash(self, prompt_id: int, input_data: Dict[str, Any]) -> str:
        """Generate a hash for the execution."""
        data_str = f"{prompt_id}:{json.dumps(input_data, sort_keys=True)}"
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _calculate_performance_trend(self, executions: List[Tuple]) -> str:
        """Calculate performance trend from recent executions."""
        if len(executions) < 10:
            return "insufficient_data"
        
        recent = executions[:10]
        older = executions[10:20] if len(executions) >= 20 else executions[10:]
        
        recent_success = sum(1 for e in recent if e[0]) / len(recent)
        older_success = sum(1 for e in older if e[0]) / len(older) if older else recent_success
        
        if recent_success > older_success + 0.1:
            return "improving"
        elif recent_success < older_success - 0.1:
            return "declining"
        else:
            return "stable"
    
    def get_simplified_prompt(self, agent_name: str) -> Optional[str]:
        """Get the simplified prompt for an agent if available."""
        prompts = self.get_agent_prompts(agent_name)
        
        # Look for prompts marked as simplified
        simplified_prompts = [p for p in prompts if p.get('variables', {}).get('simplified')]
        
        if simplified_prompts:
            # Return the most recent simplified prompt
            simplified_prompts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return simplified_prompts[0]['template']
        
        return None

    def get_enhanced_prompt(self, agent_name: str) -> Optional[str]:
        """Get the enhanced prompt for an agent if available."""
        # First try to get enhanced prompt from database
        prompts = self.get_agent_prompts(agent_name)
        
        # Look for prompts marked as enhanced
        enhanced_prompts = [p for p in prompts if p.get('variables', {}).get('enhanced')]
        
        if enhanced_prompts:
            # Return the most recent enhanced prompt
            enhanced_prompts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return enhanced_prompts[0]['template']
        
        # Fallback to file-based enhanced prompts (legacy)
        enhanced_path = Path("prompts/enhanced") / agent_name / "enhanced_system_prompt.py"
        
        if enhanced_path.exists():
            # Import the enhanced prompt
            import importlib.util
            spec = importlib.util.spec_from_file_location("enhanced_prompt", enhanced_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the prompt from the EnhancedSystemPrompt class
            if hasattr(module, 'EnhancedSystemPrompt'):
                return module.EnhancedSystemPrompt.get_prompt()
        
        return None
    
    def get_agent_prompts(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all prompts for a specific agent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, prompt_template, prompt_variables, created_at, 
                       updated_at, usage_count, success_rate, is_active
                FROM prompts 
                WHERE agent_name = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (agent_name,))
            
            prompts = []
            for row in cursor.fetchall():
                try:
                    variables = json.loads(row[2]) if row[2] else {}
                except:
                    variables = {}
                    
                prompts.append({
                    'id': row[0],
                    'template': row[1],
                    'variables': variables,
                    'created_at': row[3],
                    'updated_at': row[4],
                    'usage_count': row[5],
                    'success_rate': row[6],
                    'is_active': row[7]
                })
            
            return prompts
    
    def get_best_prompt(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the best performing prompt for an agent."""
        prompts = self.get_agent_prompts(agent_name)
        
        if not prompts:
            return None
        
        # Sort by success rate and usage count
        sorted_prompts = sorted(
            prompts, 
            key=lambda x: (x.get('success_rate', 0) or 0, x.get('usage_count', 0) or 0),
            reverse=True
        )
        
        return sorted_prompts[0]
    
    def format_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """Format a prompt template with variables."""
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable {e} in prompt template")
            return template


# Global prompt manager instance
_prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def store_agent_prompt(agent_name: str, prompt_template: str, 
                      prompt_variables: Dict[str, Any]) -> int:
    """
    Store an agent's prompt template.
    
    Args:
        agent_name: Name of the agent
        prompt_template: The prompt template
        prompt_variables: Variables used in the prompt
        
    Returns:
        Prompt ID
    """
    manager = get_prompt_manager()
    return manager.store_prompt(agent_name, prompt_template, prompt_variables)


def record_prompt_execution(prompt_id: int, input_data: Dict[str, Any],
                           output_data: Optional[Dict[str, Any]] = None,
                           execution_time: Optional[float] = None,
                           success: bool = True,
                           error_message: Optional[str] = None) -> str:
    """
    Record a prompt execution.
    
    Args:
        prompt_id: ID of the prompt used
        input_data: Input data provided to the prompt
        output_data: Output data received from the model
        execution_time: Time taken for execution
        success: Whether the execution was successful
        error_message: Error message if execution failed
        
    Returns:
        Execution hash
    """
    manager = get_prompt_manager()
    return manager.record_execution(
        prompt_id, input_data, output_data, execution_time, success, error_message
    )

