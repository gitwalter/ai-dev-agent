#!/usr/bin/env python3
"""
Health Monitoring REST API Endpoints for AI-Dev-Agent System.

Provides REST API endpoints for external monitoring systems, CI/CD integration,
and automated health checks. Supports health status reporting, alerts management,
and system metrics exposure.

Part of US-001: Automated System Health Monitoring implementation.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from utils.system_health_monitor import (
    get_health_monitor,
    SystemHealthMonitor,
    HealthStatus,
    AlertLevel,
    get_current_system_health
)


# Pydantic models for API responses
class HealthStatusResponse(BaseModel):
    """Health status API response model."""
    status: str = Field(description="Overall system health status")
    healthy_agents: int = Field(description="Number of healthy agents")
    total_agents: int = Field(description="Total number of agents")
    active_alerts: int = Field(description="Number of active alerts")
    system_uptime_hours: float = Field(description="System uptime in hours")
    last_update: str = Field(description="Last health check timestamp")
    monitoring_active: bool = Field(description="Whether monitoring is active")


class AgentHealthResponse(BaseModel):
    """Individual agent health response model."""
    agent_name: str = Field(description="Name of the agent")
    status: str = Field(description="Agent health status")
    last_heartbeat: str = Field(description="Last heartbeat timestamp")
    response_time_ms: float = Field(description="Response time in milliseconds")
    error_count: int = Field(description="Number of errors")
    success_rate: float = Field(description="Success rate percentage")
    uptime_hours: float = Field(description="Agent uptime in hours")
    last_error: Optional[str] = Field(description="Last error message")


class AlertResponse(BaseModel):
    """Alert API response model."""
    alert_id: str = Field(description="Unique alert identifier")
    level: str = Field(description="Alert severity level")
    agent_name: str = Field(description="Affected agent name")
    message: str = Field(description="Alert message")
    timestamp: str = Field(description="Alert timestamp")
    resolved: bool = Field(description="Whether alert is resolved")
    resolution_time: Optional[str] = Field(description="Resolution timestamp")


class SystemMetricsResponse(BaseModel):
    """System metrics API response model."""
    overall_health_score: float = Field(description="Overall health score (0-100)")
    average_response_time: float = Field(description="Average response time across agents")
    total_requests: int = Field(description="Total number of health checks performed")
    total_errors: int = Field(description="Total number of errors")
    uptime_percentage: float = Field(description="System uptime percentage")
    monitoring_interval: int = Field(description="Health check interval in seconds")


# Initialize FastAPI app
app = FastAPI(
    title="AI-Dev-Agent Health Monitor API",
    description="REST API for system health monitoring and alerting",
    version="1.0.0",
    docs_url="/health/docs",
    redoc_url="/health/redoc"
)

# Global logger
logger = logging.getLogger(__name__)


def get_monitor() -> SystemHealthMonitor:
    """Dependency to get health monitor instance."""
    return get_health_monitor()


@app.get("/health", response_model=HealthStatusResponse, tags=["Health"])
async def get_system_health(monitor: SystemHealthMonitor = Depends(get_monitor)):
    """
    Get overall system health status.
    
    Returns current system health summary including agent status,
    alerts, and uptime information.
    """
    try:
        health_data = monitor.get_current_health_status()
        summary = health_data.get('summary', {})
        
        return HealthStatusResponse(
            status=summary.get('overall_status', 'unknown'),
            healthy_agents=summary.get('healthy_agents', 0),
            total_agents=summary.get('total_agents', 0),
            active_alerts=summary.get('active_alerts', 0),
            system_uptime_hours=summary.get('system_uptime_hours', 0.0),
            last_update=summary.get('last_update', datetime.now().isoformat()),
            monitoring_active=health_data.get('monitoring_active', False)
        )
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/health/agents", response_model=List[AgentHealthResponse], tags=["Health"])
async def get_agents_health(monitor: SystemHealthMonitor = Depends(get_monitor)):
    """
    Get health status of all agents.
    
    Returns detailed health information for each agent including
    response times, error counts, and status.
    """
    try:
        health_data = monitor.get_current_health_status()
        agents = health_data.get('agents', {})
        
        agent_responses = []
        for agent_name, metrics in agents.items():
            agent_responses.append(AgentHealthResponse(
                agent_name=agent_name,
                status=metrics.get('status', 'unknown'),
                last_heartbeat=metrics.get('last_heartbeat', ''),
                response_time_ms=metrics.get('response_time_ms', 0.0),
                error_count=metrics.get('error_count', 0),
                success_rate=metrics.get('success_rate', 0.0),
                uptime_hours=metrics.get('uptime_hours', 0.0),
                last_error=metrics.get('last_error')
            ))
        
        return agent_responses
    except Exception as e:
        logger.error(f"Failed to get agents health: {e}")
        raise HTTPException(status_code=500, detail=f"Agents health check failed: {str(e)}")


@app.get("/health/agents/{agent_name}", response_model=AgentHealthResponse, tags=["Health"])
async def get_agent_health(agent_name: str, monitor: SystemHealthMonitor = Depends(get_monitor)):
    """
    Get health status of a specific agent.
    
    Args:
        agent_name: Name of the agent to check
        
    Returns detailed health information for the specified agent.
    """
    try:
        health_data = monitor.get_current_health_status()
        agents = health_data.get('agents', {})
        
        if agent_name not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        metrics = agents[agent_name]
        return AgentHealthResponse(
            agent_name=agent_name,
            status=metrics.get('status', 'unknown'),
            last_heartbeat=metrics.get('last_heartbeat', ''),
            response_time_ms=metrics.get('response_time_ms', 0.0),
            error_count=metrics.get('error_count', 0),
            success_rate=metrics.get('success_rate', 0.0),
            uptime_hours=metrics.get('uptime_hours', 0.0),
            last_error=metrics.get('last_error')
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent health for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent health check failed: {str(e)}")


@app.get("/health/alerts", response_model=List[AlertResponse], tags=["Alerts"])
async def get_active_alerts(monitor: SystemHealthMonitor = Depends(get_monitor)):
    """
    Get all active alerts.
    
    Returns list of all active system alerts with severity levels,
    affected agents, and timestamps.
    """
    try:
        health_data = monitor.get_current_health_status()
        alerts = health_data.get('active_alerts', [])
        
        alert_responses = []
        for alert in alerts:
            alert_responses.append(AlertResponse(
                alert_id=alert.get('alert_id', ''),
                level=alert.get('level', 'info'),
                agent_name=alert.get('agent_name', ''),
                message=alert.get('message', ''),
                timestamp=alert.get('timestamp', ''),
                resolved=alert.get('resolved', False),
                resolution_time=alert.get('resolution_time')
            ))
        
        return alert_responses
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts retrieval failed: {str(e)}")


@app.post("/health/alerts/{alert_id}/resolve", tags=["Alerts"])
async def resolve_alert(alert_id: str, monitor: SystemHealthMonitor = Depends(get_monitor)):
    """
    Resolve a specific alert.
    
    Args:
        alert_id: ID of the alert to resolve
        
    Marks the specified alert as resolved and records resolution time.
    """
    try:
        monitor.resolve_alert(alert_id)
        return JSONResponse(
            status_code=200,
            content={"message": f"Alert {alert_id} resolved successfully"}
        )
    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Alert resolution failed: {str(e)}")


@app.get("/health/metrics", response_model=SystemMetricsResponse, tags=["Metrics"])
async def get_system_metrics(monitor: SystemHealthMonitor = Depends(get_monitor)):
    """
    Get detailed system performance metrics.
    
    Returns comprehensive performance metrics including health scores,
    response times, error rates, and uptime statistics.
    """
    try:
        health_data = monitor.get_current_health_status()
        summary = health_data.get('summary', {})
        agents = health_data.get('agents', {})
        
        # Calculate metrics
        total_agents = summary.get('total_agents', 0)
        healthy_agents = summary.get('healthy_agents', 0)
        health_score = (healthy_agents / total_agents * 100) if total_agents > 0 else 0
        
        # Calculate average response time
        response_times = [agent.get('response_time_ms', 0) for agent in agents.values()]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate total errors
        total_errors = sum(agent.get('error_count', 0) for agent in agents.values())
        
        # Calculate uptime percentage (simplified)
        uptime_hours = summary.get('system_uptime_hours', 0)
        uptime_percentage = min(99.9, (uptime_hours / (uptime_hours + 0.1)) * 100) if uptime_hours > 0 else 100
        
        return SystemMetricsResponse(
            overall_health_score=health_score,
            average_response_time=avg_response_time,
            total_requests=0,  # Would be tracked over time
            total_errors=total_errors,
            uptime_percentage=uptime_percentage,
            monitoring_interval=monitor.monitoring_interval
        )
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@app.post("/health/check", tags=["Health"])
async def force_health_check(
    background_tasks: BackgroundTasks,
    monitor: SystemHealthMonitor = Depends(get_monitor)
):
    """
    Force an immediate health check.
    
    Triggers an immediate health check of all agents outside
    the normal monitoring schedule.
    """
    try:
        # Run health check in background
        background_tasks.add_task(monitor.force_health_check)
        
        return JSONResponse(
            status_code=202,
            content={"message": "Health check initiated", "status": "running"}
        )
    except Exception as e:
        logger.error(f"Failed to initiate health check: {e}")
        raise HTTPException(status_code=500, detail=f"Health check initiation failed: {str(e)}")


@app.get("/health/status/simple", tags=["Health"])
async def get_simple_status():
    """
    Get simple health status for basic monitoring.
    
    Returns simplified health status suitable for basic monitoring
    systems and uptime checks.
    """
    try:
        health_data = get_current_system_health()
        summary = health_data.get('summary', {})
        status = summary.get('overall_status', 'unknown')
        
        if status == 'healthy':
            return JSONResponse(status_code=200, content={"status": "ok", "message": "All systems healthy"})
        elif status == 'warning':
            return JSONResponse(status_code=200, content={"status": "warning", "message": "Some systems degraded"})
        else:
            return JSONResponse(status_code=503, content={"status": "error", "message": "System unhealthy"})
            
    except Exception as e:
        logger.error(f"Simple status check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "error", "message": "Health check failed"})


@app.get("/health/readiness", tags=["Health"])
async def readiness_probe():
    """
    Kubernetes/Docker readiness probe endpoint.
    
    Returns 200 if the system is ready to accept traffic,
    503 if not ready.
    """
    try:
        health_data = get_current_system_health()
        monitoring_active = health_data.get('monitoring_active', False)
        
        if monitoring_active:
            return JSONResponse(status_code=200, content={"ready": True})
        else:
            return JSONResponse(status_code=503, content={"ready": False, "reason": "Monitoring not active"})
            
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return JSONResponse(status_code=503, content={"ready": False, "reason": "Health check failed"})


@app.get("/health/liveness", tags=["Health"])
async def liveness_probe():
    """
    Kubernetes/Docker liveness probe endpoint.
    
    Returns 200 if the application is alive and running,
    regardless of health status.
    """
    return JSONResponse(status_code=200, content={"alive": True, "timestamp": datetime.now().isoformat()})


@app.on_event("startup")
async def startup_event():
    """Initialize health monitoring on startup."""
    logger.info("Health API starting up...")
    
    # Ensure monitoring directory exists
    Path("monitoring").mkdir(exist_ok=True)
    
    # Initialize health monitor
    monitor = get_health_monitor()
    
    # Start monitoring in background if not already running
    if not monitor.is_running:
        asyncio.create_task(monitor.start_monitoring())
        logger.info("Health monitoring started")
    
    logger.info("Health API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of health monitoring."""
    logger.info("Health API shutting down...")
    
    # Stop monitoring
    monitor = get_health_monitor()
    monitor.stop_monitoring()
    
    logger.info("Health API shutdown complete")


class HealthAPIServer:
    """
    Health monitoring API server manager.
    
    Provides easy startup and management of the health monitoring
    REST API server.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        """
        Initialize the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
    
    def start_server(self):
        """Start the health API server."""
        self.logger.info(f"Starting Health API server on {self.host}:{self.port}")
        
        uvicorn.run(
            app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
    
    async def start_server_async(self):
        """Start the health API server asynchronously."""
        self.logger.info(f"Starting Health API server (async) on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()


def start_health_api(host: str = "0.0.0.0", port: int = 8001):
    """
    Start the health monitoring API server.
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8001)
    """
    server = HealthAPIServer(host, port)
    server.start_server()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Start the API server
    start_health_api()
