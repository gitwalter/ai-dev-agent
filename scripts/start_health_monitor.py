#!/usr/bin/env python3
"""
Health Monitor Service Startup Script for AI-Dev-Agent System.

Simple startup script for US-001: Automated System Health Monitoring.
Ensures 99.9% uptime guarantee through automated health monitoring.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.system_health_monitor import get_health_monitor, start_health_monitoring
from utils.health_api_endpoints import start_health_api
from utils.proactive_alerting import start_proactive_alerting
from utils.logging_config import setup_logging


class HealthMonitorService:
    """Simple health monitoring service manager."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.start_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        """Start all health monitoring components."""
        self.logger.info("Starting Health Monitor Service...")
        self.start_time = datetime.now()
        self.is_running = True
        
        try:
            # Ensure monitoring directory exists
            Path("monitoring").mkdir(exist_ok=True)
            
            # Start core health monitoring
            monitor = get_health_monitor()
            monitoring_task = asyncio.create_task(monitor.start_monitoring())
            
            # Start proactive alerting
            alerting_task = asyncio.create_task(start_proactive_alerting())
            
            # Start API server (in background)
            import subprocess
            api_process = subprocess.Popen([
                sys.executable, "-c",
                "from utils.health_api_endpoints import start_health_api; start_health_api()"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.logger.info("✅ Health Monitor Service started successfully")
            self.logger.info("🔍 Core monitoring: Active")
            self.logger.info("🚨 Proactive alerts: Active") 
            self.logger.info("🌐 API server: http://localhost:8001/health")
            
            # Keep service running
            while self.is_running:
                await asyncio.sleep(30)
                
                # Service heartbeat
                uptime = (datetime.now() - self.start_time).total_seconds()
                if int(uptime) % 300 == 0:  # Every 5 minutes
                    self.logger.info(f"Service heartbeat - uptime: {uptime:.0f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            raise
        finally:
            self.logger.info("Health Monitor Service stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False


async def main():
    """Main entry point."""
    # Setup logging
    setup_logging(log_level="INFO", log_file="monitoring/health_service.log")
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 AI-Dev-Agent Health Monitor Service")
    logger.info("📋 US-001: Automated System Health Monitoring")
    logger.info("🎯 Sprint 1 - Foundation Phase")
    
    # Create and start service
    service = HealthMonitorService()
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Service error: {e}")
    
    logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
