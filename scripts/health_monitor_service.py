#!/usr/bin/env python3
"""
Health Monitoring Service for AI-Dev-Agent System.

This script runs the health monitoring service as a background process,
providing automated health checks every 5 minutes, alerting, and recovery.

Usage:
    python scripts/health_monitor_service.py [--interval=300] [--daemon]

Following Sprint 1 requirements for US-001: System Health Monitoring.
"""

import asyncio
import argparse
import logging
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.system_health_monitor import SystemHealthMonitor, start_health_monitoring


class HealthMonitorService:
    """
    Health monitoring service that runs as a background process.
    """
    
    def __init__(self, interval: int = 300):
        """
        Initialize health monitor service.
        
        Args:
            interval: Monitoring interval in seconds (default: 300 = 5 minutes)
        """
        self.interval = interval
        self.monitor = SystemHealthMonitor(monitoring_interval=interval)
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("monitoring/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "health_monitor.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    async def start(self):
        """Start the health monitoring service."""
        self.logger.info(f"Starting health monitoring service with {self.interval}s interval")
        self.running = True
        
        try:
            await self.monitor.start_monitoring()
        except Exception as e:
            self.logger.error(f"Health monitoring service failed: {e}")
            raise
    
    def stop(self):
        """Stop the health monitoring service."""
        self.logger.info("Stopping health monitoring service...")
        self.running = False
        self.monitor.stop_monitoring()
    
    async def status(self):
        """Get current service status."""
        status = self.monitor.get_current_health_status()
        
        print("=== Health Monitor Service Status ===")
        print(f"Service Running: {self.running}")
        print(f"Monitoring Interval: {self.interval}s")
        print(f"System Status: {status['summary']['overall_status'].upper()}")
        print(f"Healthy Agents: {status['summary']['healthy_agents']}/{status['summary']['total_agents']}")
        print(f"Active Alerts: {status['summary']['active_alerts']}")
        print(f"System Uptime: {status['summary']['system_uptime_hours']:.1f} hours")
        
        if status['active_alerts']:
            print("\nActive Alerts:")
            for alert in status['active_alerts']:
                print(f"  - [{alert['level'].upper()}] {alert['agent_name']}: {alert['message']}")
        
        print("\nAgent Status:")
        for agent_name, metrics in status['agents'].items():
            print(f"  - {agent_name}: {metrics['status'].upper()} "
                  f"({metrics['response_time_ms']:.1f}ms)")
    
    async def force_check(self):
        """Force an immediate health check."""
        self.logger.info("Forcing immediate health check...")
        await self.monitor.force_health_check()
        await self.status()


async def main():
    """Main service entry point."""
    parser = argparse.ArgumentParser(description="AI-Dev-Agent Health Monitoring Service")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=300, 
        help="Monitoring interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--daemon", 
        action="store_true", 
        help="Run as daemon (background process)"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="Show current status and exit"
    )
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="Force health check and show status"
    )
    
    args = parser.parse_args()
    
    service = HealthMonitorService(interval=args.interval)
    
    if args.status:
        await service.status()
        return
    
    if args.check:
        await service.force_check()
        return
    
    if args.daemon:
        # TODO: Implement proper daemon mode with pid file
        print("Daemon mode not fully implemented. Running in foreground.")
    
    try:
        print(f"Starting AI-Dev-Agent Health Monitoring Service")
        print(f"Monitoring interval: {args.interval} seconds")
        print("Press Ctrl+C to stop")
        
        await service.start()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Service failed: {e}")
        sys.exit(1)
    finally:
        service.stop()
        print("Health monitoring service stopped")


if __name__ == "__main__":
    asyncio.run(main())
