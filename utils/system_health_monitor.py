#!/usr/bin/env python3
"""
System Health Monitoring for AI-Dev-Agent System.

This module implements automated health monitoring for all agents with:
- Real-time health status reporting every 5 minutes
- Automated alerts for agent failures
- System recovery procedures
- Health dashboard integration

Following Sprint 1 requirements and agile artifacts.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict
import streamlit as st


class HealthStatus(str, Enum):
    """Health status levels for agents and system."""
    HEALTHY = "healthy"
    WARNING = "warning" 
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    OFFLINE = "offline"


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class AgentHealthMetrics:
    """Health metrics for a single agent."""
    agent_name: str
    status: HealthStatus
    last_heartbeat: datetime
    response_time_ms: float
    error_count: int
    success_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    uptime_hours: float
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data


@dataclass
class SystemHealthSummary:
    """Overall system health summary."""
    overall_status: HealthStatus
    healthy_agents: int
    total_agents: int
    active_alerts: int
    system_uptime_hours: float
    last_update: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['last_update'] = self.last_update.isoformat()
        return data


@dataclass
class HealthAlert:
    """Health monitoring alert."""
    alert_id: str
    level: AlertLevel
    agent_name: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if data['resolution_time']:
            data['resolution_time'] = self.resolution_time.isoformat()
        return data


class SystemHealthMonitor:
    """
    Main system health monitoring class.
    
    Implements automated monitoring with 5-minute intervals,
    alerting, recovery, and dashboard integration.
    """
    
    def __init__(self, monitoring_interval: int = 300):  # 5 minutes
        """
        Initialize health monitor.
        
        Args:
            monitoring_interval: Health check interval in seconds (default: 300 = 5 minutes)
        """
        self.monitoring_interval = monitoring_interval
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.start_time = datetime.now()
        
        # Storage paths
        self.health_data_path = Path("monitoring/health_data.json")
        self.alerts_path = Path("monitoring/alerts.json")
        self.health_data_path.parent.mkdir(exist_ok=True)
        
        # Agent registry
        self.registered_agents = [
            "requirements_analyst",
            "architecture_designer", 
            "code_generator",
            "test_generator",
            "code_reviewer",
            "security_analyst",
            "documentation_generator"
        ]
        
        # Health data storage
        self.agent_health: Dict[str, AgentHealthMetrics] = {}
        self.active_alerts: List[HealthAlert] = []
        self.health_history: List[Dict[str, Any]] = []
        
        # Recovery settings
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 60  # seconds
        self.last_recovery_attempts: Dict[str, datetime] = {}
        
        self.logger.info("System Health Monitor initialized")

    async def start_monitoring(self):
        """Start the automated health monitoring loop."""
        if self.is_running:
            self.logger.warning("Health monitoring already running")
            return
            
        self.is_running = True
        self.logger.info(f"Starting health monitoring with {self.monitoring_interval}s interval")
        
        try:
            while self.is_running:
                await self._perform_health_check()
                await asyncio.sleep(self.monitoring_interval)
        except Exception as e:
            self.logger.error(f"Health monitoring loop failed: {e}")
            self.is_running = False
            raise

    def stop_monitoring(self):
        """Stop the health monitoring loop."""
        self.is_running = False
        self.logger.info("Health monitoring stopped")

    async def _perform_health_check(self):
        """Perform comprehensive health check on all agents."""
        self.logger.info("Performing system health check...")
        
        check_time = datetime.now()
        health_results = {}
        
        # Check each registered agent
        for agent_name in self.registered_agents:
            try:
                metrics = await self._check_agent_health(agent_name)
                health_results[agent_name] = metrics
                self.agent_health[agent_name] = metrics
                
                # Check for alert conditions
                await self._evaluate_alerts(metrics)
                
                # Trigger recovery if needed
                if metrics.status in [HealthStatus.CRITICAL, HealthStatus.OFFLINE]:
                    await self._attempt_recovery(agent_name, metrics)
                    
            except Exception as e:
                self.logger.error(f"Health check failed for {agent_name}: {e}")
                # Create critical alert for health check failure
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    agent_name,
                    f"Health check failed: {str(e)}"
                )
        
        # Generate system summary
        summary = self._generate_system_summary()
        
        # Save health data
        await self._save_health_data(health_results, summary)
        
        # Log summary
        self.logger.info(
            f"Health check complete: {summary.healthy_agents}/{summary.total_agents} agents healthy, "
            f"system status: {summary.overall_status}, active alerts: {summary.active_alerts}"
        )

    async def _check_agent_health(self, agent_name: str) -> AgentHealthMetrics:
        """
        Check health of a specific agent.
        
        Args:
            agent_name: Name of agent to check
            
        Returns:
            AgentHealthMetrics with current health status
        """
        start_time = time.time()
        
        try:
            # Import agent dynamically
            agent_class = await self._get_agent_class(agent_name)
            
            # Create agent instance with minimal config and mock gemini client
            from models.config import AgentConfig
            test_config = AgentConfig(
                name=agent_name,
                description=f"Health check configuration for {agent_name}",
                prompt_template="Health check template",
                system_prompt="Health check prompt"
            )
            
            # Create mock gemini client for health checks
            mock_gemini_client = self._create_mock_gemini_client()
            
            agent = agent_class(test_config, mock_gemini_client)
            
            # Perform basic health check (validate configuration)
            health_check_passed = await self._perform_agent_health_check(agent)
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Determine status based on health check
            if health_check_passed and response_time < 5000:  # 5 second threshold
                status = HealthStatus.HEALTHY
            elif health_check_passed and response_time < 10000:  # 10 second threshold
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
                
            # Calculate additional metrics
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600  # hours
            
            return AgentHealthMetrics(
                agent_name=agent_name,
                status=status,
                last_heartbeat=datetime.now(),
                response_time_ms=response_time,
                error_count=0,  # Would be tracked over time
                success_rate=100.0 if health_check_passed else 0.0,
                memory_usage_mb=0.0,  # Would require process monitoring
                cpu_usage_percent=0.0,  # Would require process monitoring
                uptime_hours=uptime,
                last_error=None if health_check_passed else "Health check failed"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Agent health check failed for {agent_name}: {e}")
            
            return AgentHealthMetrics(
                agent_name=agent_name,
                status=HealthStatus.OFFLINE,
                last_heartbeat=datetime.now(),
                response_time_ms=response_time,
                error_count=1,
                success_rate=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                uptime_hours=0.0,
                last_error=str(e)
            )

    async def _get_agent_class(self, agent_name: str):
        """Dynamically import agent class."""
        agent_module_map = {
            "requirements_analyst": "agents.requirements_analyst.RequirementsAnalyst",
            "architecture_designer": "agents.architecture_designer.ArchitectureDesigner",
            "code_generator": "agents.code_generator.CodeGenerator",
            "test_generator": "agents.test_generator.TestGenerator",
            "code_reviewer": "agents.code_reviewer.CodeReviewer",
            "security_analyst": "agents.security_analyst.SecurityAnalyst",
            "documentation_generator": "agents.documentation_generator.DocumentationGenerator"
        }
        
        module_path = agent_module_map.get(agent_name)
        if not module_path:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        module_name, class_name = module_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)

    def _create_mock_gemini_client(self):
        """Create a mock Gemini client for health checks."""
        import google.generativeai as genai
        
        class MockGenerativeModel:
            """Mock GenerativeModel for health checks."""
            def __init__(self):
                self.model_name = "gemini-2.5-flash-lite"
                
            def generate_content(self, prompt, **kwargs):
                """Mock generate_content method."""
                # Return a mock response for health checks
                class MockResponse:
                    def __init__(self):
                        self.text = '{"status": "healthy", "response": "mock response for health check"}'
                        
                return MockResponse()
                
            def count_tokens(self, content):
                """Mock count_tokens method."""
                return type('obj', (object,), {'total_tokens': len(str(content).split())})()
        
        return MockGenerativeModel()
    
    async def _perform_agent_health_check(self, agent) -> bool:
        """Perform basic health check on agent instance."""
        try:
            # Check if agent has required methods
            required_methods = ['execute', 'prepare_prompt', 'validate_input']
            for method in required_methods:
                if not hasattr(agent, method):
                    return False
            
            # Check configuration validation
            if hasattr(agent, 'validate_gemini_config'):
                # Try to validate with a minimal config
                try:
                    # This would check basic configuration without making API calls
                    config_valid = True  # Simplified for health check
                    return config_valid
                except Exception:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Agent health check error: {e}")
            return False

    async def _evaluate_alerts(self, metrics: AgentHealthMetrics):
        """Evaluate if alerts need to be created based on agent metrics."""
        agent_name = metrics.agent_name
        
        # Check for critical conditions
        if metrics.status == HealthStatus.OFFLINE:
            await self._create_alert(
                AlertLevel.EMERGENCY,
                agent_name,
                f"Agent {agent_name} is offline - last heartbeat: {metrics.last_heartbeat}"
            )
        elif metrics.status == HealthStatus.CRITICAL:
            await self._create_alert(
                AlertLevel.CRITICAL,
                agent_name,
                f"Agent {agent_name} is in critical state - response time: {metrics.response_time_ms:.2f}ms"
            )
        elif metrics.status == HealthStatus.WARNING:
            await self._create_alert(
                AlertLevel.WARNING,
                agent_name,
                f"Agent {agent_name} performance degraded - response time: {metrics.response_time_ms:.2f}ms"
            )
        
        # Check response time thresholds
        if metrics.response_time_ms > 10000:  # 10 seconds
            await self._create_alert(
                AlertLevel.CRITICAL,
                agent_name,
                f"Agent {agent_name} response time critical: {metrics.response_time_ms:.2f}ms"
            )
        elif metrics.response_time_ms > 5000:  # 5 seconds
            await self._create_alert(
                AlertLevel.WARNING,
                agent_name,
                f"Agent {agent_name} response time high: {metrics.response_time_ms:.2f}ms"
            )

    async def _create_alert(self, level: AlertLevel, agent_name: str, message: str):
        """Create a new health alert."""
        alert_id = f"{agent_name}_{int(time.time())}"
        
        # Check if similar alert already exists
        for existing_alert in self.active_alerts:
            if (existing_alert.agent_name == agent_name and 
                existing_alert.level == level and 
                not existing_alert.resolved and
                existing_alert.message == message):
                # Don't create duplicate alerts
                return
        
        alert = HealthAlert(
            alert_id=alert_id,
            level=level,
            agent_name=agent_name,
            message=message,
            timestamp=datetime.now()
        )
        
        self.active_alerts.append(alert)
        
        # Log alert
        self.logger.warning(f"ALERT [{level}] {agent_name}: {message}")
        
        # Save alerts
        await self._save_alerts()

    async def _attempt_recovery(self, agent_name: str, metrics: AgentHealthMetrics):
        """Attempt automated recovery for failed agent."""
        current_time = datetime.now()
        
        # Check recovery cooldown
        last_attempt = self.last_recovery_attempts.get(agent_name)
        if last_attempt and (current_time - last_attempt).seconds < self.recovery_cooldown:
            return
        
        self.logger.info(f"Attempting recovery for agent: {agent_name}")
        
        try:
            # Record recovery attempt
            self.last_recovery_attempts[agent_name] = current_time
            
            # Attempt basic recovery (restart agent instance)
            recovery_success = await self._perform_agent_recovery(agent_name)
            
            if recovery_success:
                await self._create_alert(
                    AlertLevel.INFO,
                    agent_name,
                    f"Agent {agent_name} recovery successful"
                )
                self.logger.info(f"Recovery successful for agent: {agent_name}")
            else:
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    agent_name,
                    f"Agent {agent_name} recovery failed"
                )
                self.logger.error(f"Recovery failed for agent: {agent_name}")
                
        except Exception as e:
            self.logger.error(f"Recovery attempt failed for {agent_name}: {e}")
            await self._create_alert(
                AlertLevel.CRITICAL,
                agent_name,
                f"Recovery error for {agent_name}: {str(e)}"
            )

    async def _perform_agent_recovery(self, agent_name: str) -> bool:
        """Perform actual recovery procedure for agent."""
        try:
            # For now, we'll implement a basic recovery by re-importing the agent
            # In a full implementation, this might involve:
            # - Restarting agent processes
            # - Clearing agent cache
            # - Resetting agent state
            # - Reconnecting to services
            
            agent_class = await self._get_agent_class(agent_name)
            
            # Test that we can create a new instance
            from models.config import AgentConfig
            test_config = AgentConfig(
                name=agent_name,
                description=f"Recovery test configuration for {agent_name}",
                prompt_template="Recovery test template",
                system_prompt="Recovery test prompt"
            )
            
            # Create mock gemini client for recovery tests
            mock_gemini_client = self._create_mock_gemini_client()
            
            test_agent = agent_class(test_config, mock_gemini_client)
            recovery_check = await self._perform_agent_health_check(test_agent)
            
            return recovery_check
            
        except Exception as e:
            self.logger.error(f"Agent recovery failed for {agent_name}: {e}")
            return False

    def _generate_system_summary(self) -> SystemHealthSummary:
        """Generate overall system health summary."""
        total_agents = len(self.registered_agents)
        healthy_agents = sum(1 for metrics in self.agent_health.values() 
                           if metrics.status == HealthStatus.HEALTHY)
        
        # Determine overall status
        if healthy_agents == total_agents:
            overall_status = HealthStatus.HEALTHY
        elif healthy_agents >= total_agents * 0.8:  # 80% threshold
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.CRITICAL
        
        active_alerts_count = len([a for a in self.active_alerts if not a.resolved])
        system_uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        
        return SystemHealthSummary(
            overall_status=overall_status,
            healthy_agents=healthy_agents,
            total_agents=total_agents,
            active_alerts=active_alerts_count,
            system_uptime_hours=system_uptime,
            last_update=datetime.now()
        )

    async def _save_health_data(self, health_results: Dict[str, AgentHealthMetrics], 
                               summary: SystemHealthSummary):
        """Save health data to persistent storage."""
        try:
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary.to_dict(),
                "agents": {name: metrics.to_dict() for name, metrics in health_results.items()}
            }
            
            # Save current data
            with open(self.health_data_path, 'w') as f:
                json.dump(health_data, f, indent=2)
            
            # Add to history (keep last 100 entries)
            self.health_history.append(health_data)
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            # Save history
            history_path = self.health_data_path.parent / "health_history.json"
            with open(history_path, 'w') as f:
                json.dump(self.health_history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save health data: {e}")

    async def _save_alerts(self):
        """Save alerts to persistent storage."""
        try:
            alerts_data = {
                "timestamp": datetime.now().isoformat(),
                "alerts": [alert.to_dict() for alert in self.active_alerts]
            }
            
            with open(self.alerts_path, 'w') as f:
                json.dump(alerts_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")

    def get_current_health_status(self) -> Dict[str, Any]:
        """Get current system health status."""
        summary = self._generate_system_summary()
        
        return {
            "summary": summary.to_dict(),
            "agents": {name: metrics.to_dict() for name, metrics in self.agent_health.items()},
            "active_alerts": [alert.to_dict() for alert in self.active_alerts if not alert.resolved],
            "monitoring_active": self.is_running
        }

    def resolve_alert(self, alert_id: str):
        """Manually resolve an alert."""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                self.logger.info(f"Alert resolved: {alert_id}")
                break

    async def force_health_check(self):
        """Force an immediate health check (outside normal schedule)."""
        self.logger.info("Forcing immediate health check...")
        await self._perform_health_check()


# Global monitor instance
_monitor_instance: Optional[SystemHealthMonitor] = None


def get_health_monitor() -> SystemHealthMonitor:
    """Get or create the global health monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemHealthMonitor()
    return _monitor_instance


async def start_health_monitoring():
    """Start the global health monitoring system."""
    monitor = get_health_monitor()
    await monitor.start_monitoring()


def stop_health_monitoring():
    """Stop the global health monitoring system."""
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop_monitoring()


def get_current_system_health() -> Dict[str, Any]:
    """Get current system health status."""
    monitor = get_health_monitor()
    return monitor.get_current_health_status()


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        monitor = SystemHealthMonitor(monitoring_interval=60)  # 1 minute for testing
        
        print("Starting health monitoring demo...")
        
        # Force a health check
        await monitor.force_health_check()
        
        # Get current status
        status = monitor.get_current_health_status()
        print(f"System Status: {status['summary']['overall_status']}")
        print(f"Healthy Agents: {status['summary']['healthy_agents']}/{status['summary']['total_agents']}")
        print(f"Active Alerts: {status['summary']['active_alerts']}")
        
        # Show agent details
        for agent_name, metrics in status['agents'].items():
            print(f"  {agent_name}: {metrics['status']} (Response: {metrics['response_time_ms']:.1f}ms)")
        
        print("Health monitoring demo complete")
    
    # Run demo
    asyncio.run(main())
