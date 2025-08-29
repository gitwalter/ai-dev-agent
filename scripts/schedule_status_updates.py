#!/usr/bin/env python3
"""
Scheduled User Story Status Updates
=================================

Runs the automation every 5 minutes during development hours.
This provides continuous, real-time updates to user story status
and agile artifacts throughout the development day.

Usage:
    python scripts/schedule_status_updates.py
    
    # With custom schedule
    python scripts/schedule_status_updates.py --interval 10  # Every 10 minutes
    
    # Development hours only (default: 8 AM - 6 PM)
    python scripts/schedule_status_updates.py --start-hour 9 --end-hour 17

Author: AI Development Agent
Version: 1.0.0
Last Updated: 2025-08-29
"""

import schedule
import time
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

class StatusUpdateScheduler:
    """Scheduler for automated user story status updates."""
    
    def __init__(self, interval_minutes: int = 5, start_hour: int = 8, end_hour: int = 18):
        self.interval_minutes = interval_minutes
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.script_path = Path(__file__).parent / "automate_user_story_updates.py"
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        
    def run_status_update(self):
        """Execute the status update automation."""
        
        self.execution_count += 1
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            print(f"🔄 [{current_time}] Executing status update (#{self.execution_count})...")
            
            result = subprocess.run([
                sys.executable, str(self.script_path)
            ], capture_output=True, text=True, timeout=180)  # 3 minute timeout
            
            if result.returncode == 0:
                self.success_count += 1
                print(f"✅ [{current_time}] Status update completed successfully")
                
                # Parse output for key metrics
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "Test Success Rate:" in line:
                        print(f"   📊 {line.strip()}")
                    elif "Health Monitoring:" in line:
                        print(f"   🏥 {line.strip()}")
                    elif "Stories Updated:" in line:
                        print(f"   📝 {line.strip()}")
                        
            else:
                self.failure_count += 1
                print(f"❌ [{current_time}] Status update failed (exit code: {result.returncode})")
                
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            self.failure_count += 1
            print(f"⏰ [{current_time}] Status update timed out after 3 minutes")
            
        except Exception as e:
            self.failure_count += 1
            print(f"🚨 [{current_time}] Exception during status update: {e}")
        
        # Print statistics every 10 executions
        if self.execution_count % 10 == 0:
            self.print_statistics()
    
    def print_statistics(self):
        """Print execution statistics."""
        
        success_rate = (self.success_count / self.execution_count * 100) if self.execution_count > 0 else 0
        
        print(f"\n📊 Scheduler Statistics (Last {self.execution_count} executions):")
        print(f"   ✅ Successful: {self.success_count}")
        print(f"   ❌ Failed: {self.failure_count}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Next update in {self.interval_minutes} minutes\n")
    
    def is_development_hours(self) -> bool:
        """Check if current time is within development hours."""
        
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour <= self.end_hour
    
    def start_scheduler(self):
        """Start the scheduled automation."""
        
        print("🕐 Starting scheduled user story status updates...")
        print(f"📅 Running every {self.interval_minutes} minutes during development hours ({self.start_hour}:00 - {self.end_hour}:00)")
        print(f"💻 Script: {self.script_path}")
        print(f"🚀 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚡ Press Ctrl+C to stop\n")
        
        # Schedule the updates
        schedule.every(self.interval_minutes).minutes.do(self.run_status_update)
        
        # Run initial update if in development hours
        if self.is_development_hours():
            print("🔄 Running initial status update...")
            self.run_status_update()
        
        try:
            while True:
                # Only run during development hours
                if self.is_development_hours():
                    schedule.run_pending()
                else:
                    # Print status during off-hours (once per hour)
                    if datetime.now().minute == 0:
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"💤 [{current_time}] Outside development hours, sleeping...")
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print(f"\n🛑 Scheduler stopped by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.print_statistics()
            print("👋 Thank you for using the automated status update system!")


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="Scheduled User Story Status Updates")
    parser.add_argument("--interval", type=int, default=5, 
                       help="Update interval in minutes (default: 5)")
    parser.add_argument("--start-hour", type=int, default=8,
                       help="Development start hour (default: 8)")
    parser.add_argument("--end-hour", type=int, default=18,
                       help="Development end hour (default: 18)")
    parser.add_argument("--run-once", action="store_true",
                       help="Run once immediately and exit")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not (0 <= args.start_hour <= 23 and 0 <= args.end_hour <= 23):
        print("❌ Error: Hours must be between 0 and 23")
        sys.exit(1)
        
    if args.start_hour >= args.end_hour:
        print("❌ Error: Start hour must be less than end hour")
        sys.exit(1)
        
    if args.interval < 1:
        print("❌ Error: Interval must be at least 1 minute")
        sys.exit(1)
    
    # Create and start scheduler
    scheduler = StatusUpdateScheduler(
        interval_minutes=args.interval,
        start_hour=args.start_hour,
        end_hour=args.end_hour
    )
    
    if args.run_once:
        print("🔄 Running status update once...")
        scheduler.run_status_update()
    else:
        scheduler.start_scheduler()


if __name__ == "__main__":
    main()
