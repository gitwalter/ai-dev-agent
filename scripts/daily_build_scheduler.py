#!/usr/bin/env python3
"""
Daily Build Scheduler

This script provides scheduling functionality for daily builds following
the Agile Daily Deployed Build Rule. It can be used with cron or Windows
Task Scheduler to ensure daily builds are executed automatically.

Usage:
    python scripts/daily_build_scheduler.py [options]
    
Options:
    --schedule: Set up scheduled task (requires admin privileges)
    --check: Check if daily build is needed
    --force: Force daily build execution
    --notify-only: Only send notifications without executing build
"""

import argparse
import datetime
import json
import platform
import subprocess
import sys
from pathlib import Path


class DailyBuildScheduler:
    """Scheduler for daily builds."""
    
    def __init__(self, project_root: Path):
        """Initialize scheduler."""
        self.project_root = project_root
        self.monitoring_dir = project_root / "monitoring"
        self.status_file = self.monitoring_dir / "daily_build_status.json"
        
    def check_build_needed(self) -> bool:
        """Check if daily build is needed."""
        
        today = datetime.date.today()
        
        # Check if build was already completed today
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    status_data = json.load(f)
                
                last_build = status_data.get("last_build", {})
                last_build_timestamp = last_build.get("timestamp")
                
                if last_build_timestamp:
                    # Parse the timestamp
                    last_build_date = datetime.datetime.fromisoformat(
                        last_build_timestamp.replace('Z', '+00:00')
                    ).date()
                    
                    if last_build_date >= today:
                        return False
                        
            except (json.JSONDecodeError, ValueError, KeyError):
                # If we can't parse the status, assume build is needed
                pass
        
        return True
    
    def execute_daily_build(self, force: bool = False) -> bool:
        """Execute daily build if needed."""
        
        if not force and not self.check_build_needed():
            print("✅ Daily build already completed today")
            return True
        
        print("🚀 Executing daily build...")
        
        try:
            # Execute daily build automation
            result = subprocess.run(
                [sys.executable, "scripts/daily_build_automation.py", "--trigger-type", "scheduled"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Daily build completed successfully")
                return True
            else:
                print(f"❌ Daily build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"💥 Daily build execution failed: {e}")
            return False
    
    def setup_scheduled_task(self) -> bool:
        """Set up scheduled task for daily builds."""
        
        system = platform.system()
        script_path = str(self.project_root / "scripts" / "daily_build_scheduler.py")
        
        if system == "Windows":
            return self._setup_windows_task(script_path)
        elif system in ["Linux", "Darwin"]:  # Darwin is macOS
            return self._setup_unix_cron(script_path)
        else:
            print(f"❌ Unsupported platform: {system}")
            return False
    
    def _setup_windows_task(self, script_path: str) -> bool:
        """Set up Windows scheduled task."""
        
        task_name = "DailyBuildAutomation"
        python_exe = sys.executable
        
        # Create task XML
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>AI-Dev-Agent Daily Build Automation</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2024-01-01T08:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>{script_path}</Arguments>
      <WorkingDirectory>{self.project_root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
        
        try:
            # Save task XML to temporary file
            temp_xml = self.project_root / "temp_task.xml"
            with open(temp_xml, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            # Create scheduled task
            result = subprocess.run([
                "schtasks", "/create", "/tn", task_name, "/xml", str(temp_xml), "/f"
            ], capture_output=True, text=True)
            
            # Clean up temp file
            temp_xml.unlink()
            
            if result.returncode == 0:
                print(f"✅ Windows scheduled task '{task_name}' created successfully")
                print("📅 Daily build will run at 8:00 AM every day")
                return True
            else:
                print(f"❌ Failed to create Windows scheduled task: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"💥 Windows task setup failed: {e}")
            return False
    
    def _setup_unix_cron(self, script_path: str) -> bool:
        """Set up Unix cron job."""
        
        python_exe = sys.executable
        cron_entry = f"0 8 * * 1-5 cd {self.project_root} && {python_exe} {script_path}\n"
        
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Check if entry already exists
            if "daily_build_scheduler.py" in current_crontab:
                print("✅ Cron job already exists")
                return True
            
            # Add new entry
            new_crontab = current_crontab + cron_entry
            
            # Install new crontab
            result = subprocess.run(
                ["crontab", "-"], 
                input=new_crontab, 
                text=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                print("✅ Cron job created successfully")
                print("📅 Daily build will run at 8:00 AM on weekdays")
                return True
            else:
                print(f"❌ Failed to create cron job: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"💥 Cron setup failed: {e}")
            return False
    
    def send_notification(self, message: str, status: str = "info") -> None:
        """Send notification about daily build status."""
        
        timestamp = datetime.datetime.utcnow().isoformat()
        
        notification = {
            "timestamp": timestamp,
            "status": status,
            "message": message,
            "source": "daily_build_scheduler"
        }
        
        # Store notification
        notifications_file = self.monitoring_dir / "notifications.json"
        notifications = []
        
        if notifications_file.exists():
            try:
                with open(notifications_file, 'r') as f:
                    notifications = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                notifications = []
        
        notifications.append(notification)
        
        # Keep only last 100 notifications
        notifications = notifications[-100:]
        
        # Save notifications
        self.monitoring_dir.mkdir(exist_ok=True)
        with open(notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)
        
        # Print notification
        status_emoji = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        print(f"{status_emoji.get(status, 'ℹ️')} {message}")


def main():
    """Main entry point for daily build scheduler."""
    
    parser = argparse.ArgumentParser(
        description="Daily build scheduler for agile development"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Set up scheduled task for daily builds"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if daily build is needed"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force daily build execution"
    )
    parser.add_argument(
        "--notify-only",
        action="store_true",
        help="Only send notifications without executing build"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    scheduler = DailyBuildScheduler(project_root)
    
    try:
        if args.schedule:
            print("🔧 Setting up scheduled daily builds...")
            success = scheduler.setup_scheduled_task()
            sys.exit(0 if success else 1)
            
        elif args.check:
            needed = scheduler.check_build_needed()
            if needed:
                print("🔍 Daily build is needed")
                scheduler.send_notification("Daily build is needed", "info")
            else:
                print("✅ Daily build already completed")
                scheduler.send_notification("Daily build already completed today", "success")
            sys.exit(0 if not needed else 1)
            
        elif args.notify_only:
            needed = scheduler.check_build_needed()
            if needed:
                scheduler.send_notification("Daily build required but not executed (notify-only mode)", "warning")
            else:
                scheduler.send_notification("Daily build up to date", "success")
            sys.exit(0)
            
        else:
            # Default: Execute daily build if needed
            success = scheduler.execute_daily_build(args.force)
            
            if success:
                scheduler.send_notification("Daily build completed successfully", "success")
                sys.exit(0)
            else:
                scheduler.send_notification("Daily build failed", "error")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("🛑 Daily build scheduler interrupted by user")
        scheduler.send_notification("Daily build scheduler interrupted", "warning")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Daily build scheduler failed: {e}")
        scheduler.send_notification(f"Daily build scheduler failed: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
