"""
MCP Prompt Manager - Task 3.2 Implementation

This module implements the Model Context Protocol (MCP) server integration for advanced prompt management.
Following our systematic approach and rules for reliable, testable, and optimized prompt management.

Key Features:
- MCP server integration for prompt storage and versioning
- Advanced prompt lifecycle management
- Collaborative prompt development
- Version control and rollback capabilities
- Advanced analytics and monitoring
- Integration with existing testing and optimization frameworks
"""

import asyncio
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

from .prompt_engineering_framework import (
    PromptTestingFramework, 
    WorkflowMode, 
    OptimizedPrompt,
    PromptTestResults
)
from .prompt_optimizer import (
    PromptOptimizer,
    OptimizationResult,
    OptimizationConfig
)

# Configure logging
logger = logging.getLogger(__name__)

class PromptStatus(Enum):
    """Prompt status enumeration"""
    DRAFT = "draft"
    TESTING = "testing"
    OPTIMIZING = "optimizing"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"

class PromptVersion(Enum):
    """Prompt version types"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

@dataclass
class PromptMetadata:
    """Comprehensive prompt metadata"""
    prompt_id: str
    agent_type: str
    mode: WorkflowMode
    version: str
    status: PromptStatus
    created_at: datetime
    updated_at: datetime
    created_by: str
    tags: List[str] = field(default_factory=list)
    description: str = ""
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    test_results: Optional[PromptTestResults] = None
    dependencies: List[str] = field(default_factory=list)

@dataclass
class MCPPrompt:
    """MCP prompt with full metadata"""
    prompt: str
    metadata: PromptMetadata
    optimization_result: Optional[OptimizationResult] = None

class MCPPromptManager:
    """
    MCP server integration for advanced prompt management
    
    Implements comprehensive prompt lifecycle management:
    - MCP server integration for storage and versioning
    - Advanced prompt lifecycle management
    - Collaborative prompt development
    - Version control and rollback capabilities
    - Advanced analytics and monitoring
    - Integration with testing and optimization frameworks
    """
    
    def __init__(self, mcp_server_url: Optional[str] = None, db_path: str = "prompts/mcp_prompts.db"):
        self.mcp_server_url = mcp_server_url
        self.db_path = db_path
        self.testing_framework = PromptTestingFramework()
        self.optimizer = PromptOptimizer()
        
        # Initialize database
        self._init_database()
        
        logger.info("MCPPromptManager initialized with testing and optimization frameworks")
    
    def _init_database(self):
        """Initialize SQLite database for prompt storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create prompts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    prompt_id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    created_by TEXT NOT NULL,
                    tags TEXT,
                    description TEXT,
                    performance_metrics TEXT,
                    optimization_history TEXT,
                    test_results TEXT,
                    dependencies TEXT
                )
            ''')
            
            # Create versions table for version control
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompt_versions (
                    version_id TEXT PRIMARY KEY,
                    prompt_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    version_type TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT NOT NULL,
                    change_description TEXT,
                    performance_metrics TEXT,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (prompt_id)
                )
            ''')
            
            # Create analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompt_analytics (
                    analytics_id TEXT PRIMARY KEY,
                    prompt_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    context TEXT,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (prompt_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def create_prompt(
        self,
        prompt: str,
        agent_type: str,
        mode: WorkflowMode,
        created_by: str,
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> MCPPrompt:
        """
        Create a new prompt with comprehensive metadata
        
        Args:
            prompt: The prompt content
            agent_type: Type of agent
            mode: Workflow mode
            created_by: Creator identifier
            description: Prompt description
            tags: Prompt tags
            
        Returns:
            MCPPrompt: Created prompt with metadata
        """
        logger.info(f"Creating new prompt for {agent_type} in {mode.value} mode")
        
        try:
            # Generate unique prompt ID
            prompt_id = str(uuid.uuid4())
            
            # Create metadata
            metadata = PromptMetadata(
                prompt_id=prompt_id,
                agent_type=agent_type,
                mode=mode,
                version="1.0.0",
                status=PromptStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=created_by,
                tags=tags or [],
                description=description
            )
            
            # Create MCP prompt
            mcp_prompt = MCPPrompt(
                prompt=prompt,
                metadata=metadata
            )
            
            # Store in database
            await self._store_prompt(mcp_prompt)
            
            logger.info(f"Prompt created successfully with ID: {prompt_id}")
            return mcp_prompt
            
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            raise
    
    async def _store_prompt(self, mcp_prompt: MCPPrompt):
        """Store prompt in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO prompts 
                (prompt_id, prompt, agent_type, mode, version, status, created_at, updated_at, 
                 created_by, tags, description, performance_metrics, optimization_history, 
                 test_results, dependencies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                mcp_prompt.metadata.prompt_id,
                mcp_prompt.prompt,
                mcp_prompt.metadata.agent_type,
                mcp_prompt.metadata.mode.value,
                mcp_prompt.metadata.version,
                mcp_prompt.metadata.status.value,
                mcp_prompt.metadata.created_at.isoformat(),
                mcp_prompt.metadata.updated_at.isoformat(),
                mcp_prompt.metadata.created_by,
                json.dumps(mcp_prompt.metadata.tags),
                mcp_prompt.metadata.description,
                json.dumps(mcp_prompt.metadata.performance_metrics),
                json.dumps(mcp_prompt.metadata.optimization_history),
                json.dumps(mcp_prompt.metadata.test_results.__dict__) if mcp_prompt.metadata.test_results else None,
                json.dumps(mcp_prompt.metadata.dependencies)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store prompt: {e}")
            raise
    
    async def get_prompt(self, prompt_id: str) -> Optional[MCPPrompt]:
        """Retrieve prompt by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM prompts WHERE prompt_id = ?
            ''', (prompt_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return await self._row_to_mcp_prompt(row)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve prompt: {e}")
            return None
    
    async def _row_to_mcp_prompt(self, row: Tuple) -> MCPPrompt:
        """Convert database row to MCPPrompt"""
        metadata = PromptMetadata(
            prompt_id=row[0],
            agent_type=row[2],
            mode=WorkflowMode(row[3]),
            version=row[4],
            status=PromptStatus(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
            created_by=row[8],
            tags=json.loads(row[9]) if row[9] else [],
            description=row[10] or "",
            performance_metrics=json.loads(row[11]) if row[11] else {},
            optimization_history=json.loads(row[12]) if row[12] else [],
            test_results=None,  # Will be reconstructed if needed
            dependencies=json.loads(row[14]) if row[14] else []
        )
        
        return MCPPrompt(
            prompt=row[1],
            metadata=metadata
        )
    
    async def test_prompt(self, prompt_id: str) -> PromptTestResults:
        """Test prompt using the testing framework"""
        logger.info(f"Testing prompt: {prompt_id}")
        
        try:
            # Retrieve prompt
            mcp_prompt = await self.get_prompt(prompt_id)
            if not mcp_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Run comprehensive testing
            test_results = await self.testing_framework.comprehensive_test_prompt(
                mcp_prompt.prompt,
                mcp_prompt.metadata.agent_type,
                mcp_prompt.metadata.mode
            )
            
            # Update metadata
            mcp_prompt.metadata.test_results = test_results
            mcp_prompt.metadata.status = PromptStatus.TESTING
            mcp_prompt.metadata.updated_at = datetime.now()
            
            # Store updated prompt
            await self._store_prompt(mcp_prompt)
            
            logger.info(f"Prompt testing completed. Score: {test_results.overall_score:.3f}")
            return test_results
            
        except Exception as e:
            logger.error(f"Failed to test prompt: {e}")
            raise
    
    async def optimize_prompt(self, prompt_id: str, target_metrics: Optional[Dict[str, float]] = None) -> OptimizationResult:
        """Optimize prompt using the optimization framework"""
        logger.info(f"Optimizing prompt: {prompt_id}")
        
        try:
            # Retrieve prompt
            mcp_prompt = await self.get_prompt(prompt_id)
            if not mcp_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Run optimization
            optimization_result = await self.optimizer.optimize_prompt(
                mcp_prompt.prompt,
                mcp_prompt.metadata.agent_type,
                mcp_prompt.metadata.mode,
                target_metrics
            )
            
            # Update metadata
            mcp_prompt.optimization_result = optimization_result
            mcp_prompt.metadata.status = PromptStatus.OPTIMIZING
            mcp_prompt.metadata.updated_at = datetime.now()
            mcp_prompt.metadata.optimization_history.append({
                'timestamp': datetime.now().isoformat(),
                'strategy': optimization_result.strategy_used.value,
                'improvement': optimization_result.performance_improvement,
                'confidence': optimization_result.confidence_score
            })
            
            # Store updated prompt
            await self._store_prompt(mcp_prompt)
            
            logger.info(f"Prompt optimization completed. Improvement: {optimization_result.performance_improvement:.3f}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Failed to optimize prompt: {e}")
            raise
    
    async def update_prompt(
        self,
        prompt_id: str,
        new_prompt: str,
        updated_by: str,
        version_type: PromptVersion = PromptVersion.PATCH,
        change_description: str = ""
    ) -> MCPPrompt:
        """Update prompt with version control"""
        logger.info(f"Updating prompt: {prompt_id}")
        
        try:
            # Retrieve current prompt
            current_prompt = await self.get_prompt(prompt_id)
            if not current_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Create version record
            await self._create_version_record(
                current_prompt,
                version_type,
                updated_by,
                change_description
            )
            
            # Update prompt
            current_prompt.prompt = new_prompt
            current_prompt.metadata.updated_at = datetime.now()
            current_prompt.metadata.status = PromptStatus.DRAFT
            
            # Update version
            current_prompt.metadata.version = self._increment_version(
                current_prompt.metadata.version,
                version_type
            )
            
            # Store updated prompt
            await self._store_prompt(current_prompt)
            
            logger.info(f"Prompt updated successfully. New version: {current_prompt.metadata.version}")
            return current_prompt
            
        except Exception as e:
            logger.error(f"Failed to update prompt: {e}")
            raise
    
    async def _create_version_record(
        self,
        mcp_prompt: MCPPrompt,
        version_type: PromptVersion,
        updated_by: str,
        change_description: str
    ):
        """Create version record for prompt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            version_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO prompt_versions 
                (version_id, prompt_id, prompt, version_type, version_number, created_at, 
                 created_by, change_description, performance_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                version_id,
                mcp_prompt.metadata.prompt_id,
                mcp_prompt.prompt,
                version_type.value,
                mcp_prompt.metadata.version,
                datetime.now().isoformat(),
                updated_by,
                change_description,
                json.dumps(mcp_prompt.metadata.performance_metrics)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to create version record: {e}")
            raise
    
    def _increment_version(self, current_version: str, version_type: PromptVersion) -> str:
        """Increment version number"""
        try:
            major, minor, patch = map(int, current_version.split('.'))
            
            if version_type == PromptVersion.MAJOR:
                major += 1
                minor = 0
                patch = 0
            elif version_type == PromptVersion.MINOR:
                minor += 1
                patch = 0
            else:  # PATCH
                patch += 1
            
            return f"{major}.{minor}.{patch}"
            
        except Exception as e:
            logger.error(f"Failed to increment version: {e}")
            return current_version
    
    async def approve_prompt(self, prompt_id: str, approved_by: str) -> MCPPrompt:
        """Approve prompt for deployment"""
        logger.info(f"Approving prompt: {prompt_id}")
        
        try:
            mcp_prompt = await self.get_prompt(prompt_id)
            if not mcp_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Update status
            mcp_prompt.metadata.status = PromptStatus.APPROVED
            mcp_prompt.metadata.updated_at = datetime.now()
            
            # Store updated prompt
            await self._store_prompt(mcp_prompt)
            
            logger.info(f"Prompt approved successfully")
            return mcp_prompt
            
        except Exception as e:
            logger.error(f"Failed to approve prompt: {e}")
            raise
    
    async def deploy_prompt(self, prompt_id: str, deployed_by: str) -> MCPPrompt:
        """Deploy prompt to production"""
        logger.info(f"Deploying prompt: {prompt_id}")
        
        try:
            mcp_prompt = await self.get_prompt(prompt_id)
            if not mcp_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Verify prompt is approved
            if mcp_prompt.metadata.status != PromptStatus.APPROVED:
                raise ValueError(f"Prompt must be approved before deployment")
            
            # Update status
            mcp_prompt.metadata.status = PromptStatus.DEPLOYED
            mcp_prompt.metadata.updated_at = datetime.now()
            
            # Store updated prompt
            await self._store_prompt(mcp_prompt)
            
            logger.info(f"Prompt deployed successfully")
            return mcp_prompt
            
        except Exception as e:
            logger.error(f"Failed to deploy prompt: {e}")
            raise
    
    async def search_prompts(
        self,
        agent_type: Optional[str] = None,
        mode: Optional[WorkflowMode] = None,
        status: Optional[PromptStatus] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[MCPPrompt]:
        """Search prompts with filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM prompts WHERE 1=1"
            params = []
            
            if agent_type:
                query += " AND agent_type = ?"
                params.append(agent_type)
            
            if mode:
                query += " AND mode = ?"
                params.append(mode.value)
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if tags:
                # Search for prompts containing any of the tags
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
                query += f" AND ({' OR '.join(tag_conditions)})"
            
            query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to MCPPrompts
            prompts = []
            for row in rows:
                prompt = await self._row_to_mcp_prompt(row)
                prompts.append(prompt)
            
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to search prompts: {e}")
            return []
    
    async def get_prompt_analytics(self, prompt_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a prompt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get analytics data
            cursor.execute('''
                SELECT metric_type, metric_value, timestamp 
                FROM prompt_analytics 
                WHERE prompt_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (prompt_id, (datetime.now() - timedelta(days=days)).isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Process analytics data
            analytics = {
                'performance_trends': {},
                'usage_metrics': {},
                'optimization_impact': {}
            }
            
            for row in rows:
                metric_type, metric_value, timestamp = row
                if metric_type not in analytics:
                    analytics[metric_type] = []
                analytics[metric_type].append({
                    'value': metric_value,
                    'timestamp': timestamp
                })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get prompt analytics: {e}")
            return {}
    
    async def archive_prompt(self, prompt_id: str, archived_by: str) -> MCPPrompt:
        """Archive prompt"""
        logger.info(f"Archiving prompt: {prompt_id}")
        
        try:
            mcp_prompt = await self.get_prompt(prompt_id)
            if not mcp_prompt:
                raise ValueError(f"Prompt not found: {prompt_id}")
            
            # Update status
            mcp_prompt.metadata.status = PromptStatus.ARCHIVED
            mcp_prompt.metadata.updated_at = datetime.now()
            
            # Store updated prompt
            await self._store_prompt(mcp_prompt)
            
            logger.info(f"Prompt archived successfully")
            return mcp_prompt
            
        except Exception as e:
            logger.error(f"Failed to archive prompt: {e}")
            raise

# Main function for testing
async def main():
    """Test the MCP prompt manager"""
    logger.info("Testing MCP Prompt Manager")
    
    # Initialize manager
    manager = MCPPromptManager()
    
    # Create test prompt
    test_prompt = """
    You are a requirements analyst. Your task is to analyze the following requirements and extract functional and non-functional requirements.
    
    Output Format:
    - Functional Requirements: List of functional requirements
    - Non-Functional Requirements: List of non-functional requirements
    - Constraints: List of constraints
    
    Requirements: {requirements}
    """
    
    # Create prompt
    mcp_prompt = await manager.create_prompt(
        test_prompt,
        "requirements_analyst",
        WorkflowMode.WATERFALL,
        "test_user",
        "Test requirements analysis prompt",
        ["requirements", "analysis", "test"]
    )
    
    logger.info(f"Created prompt with ID: {mcp_prompt.metadata.prompt_id}")
    
    # Test prompt
    test_results = await manager.test_prompt(mcp_prompt.metadata.prompt_id)
    logger.info(f"Test results: {test_results.overall_score:.3f}")
    
    # Optimize prompt
    optimization_result = await manager.optimize_prompt(mcp_prompt.metadata.prompt_id)
    logger.info(f"Optimization result: {optimization_result.performance_improvement:.3f}")
    
    # Search prompts
    prompts = await manager.search_prompts(agent_type="requirements_analyst")
    logger.info(f"Found {len(prompts)} prompts")

if __name__ == "__main__":
    asyncio.run(main())
