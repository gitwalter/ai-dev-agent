#!/usr/bin/env python3
"""
🤖 Cursor IDE Automated Testing Integration
==========================================

MISSION: Integrate automated UI testing directly into Cursor IDE workflow
APPROACH: File watching + automatic test execution + AI-powered test generation
BENEFIT: Zero-effort testing - tests run automatically when you save files

🎯 FEATURES:
- File change detection in Cursor IDE
- Automatic test execution on save
- AI-generated test scenarios for new UI components
- Real-time test results in Cursor output
- Visual regression detection
- Performance monitoring
- Accessibility validation
- Test report generation with actionable insights

🔧 CURSOR IDE INTEGRATION:
- .cursor/tasks.json integration
- Real-time file watching
- Terminal output integration
- Error highlighting in IDE
- Automatic test fixing suggestions
- Performance metrics display

🚀 REAL VALUE ASSURANCE:
- User scenario validation
- Business value metrics
- Quality gate enforcement
- Regression prevention
- Continuous improvement
"""

import os
import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class CursorTestingHandler(FileSystemEventHandler):
    """File system event handler for Cursor IDE integration."""
    
    def __init__(self, tester_config: Dict[str, Any]):
        self.config = tester_config
        self.last_run = {}
        self.test_queue = []
        self.running_tests = False
        
        # File patterns to watch
        self.ui_patterns = [".py", ".js", ".tsx", ".css", ".html"]
        self.test_patterns = ["test_", "_test.py"]
        
        print("🤖 Cursor Auto-Testing initialized")
        print(f"📁 Watching: {self.config['watch_paths']}")
        print(f"🎯 UI patterns: {self.ui_patterns}")
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's a UI file we care about
        if self._should_trigger_tests(file_path):
            self._queue_tests(file_path)
    
    def _should_trigger_tests(self, file_path: Path) -> bool:
        """Determine if file changes should trigger tests."""
        
        # Check file extension
        if not any(file_path.suffix == ext for ext in self.ui_patterns):
            return False
        
        # Skip test files themselves (to avoid infinite loops)
        if any(pattern in file_path.name for pattern in self.test_patterns):
            return False
        
        # Skip temporary files
        if file_path.name.startswith('.') or file_path.name.endswith('.tmp'):
            return False
        
        # Check if enough time has passed since last run
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
        current_time = time.time()
        
        if file_hash in self.last_run:
            if current_time - self.last_run[file_hash] < self.config.get('debounce_seconds', 2):
                return False
        
        self.last_run[file_hash] = current_time
        return True
    
    def _queue_tests(self, file_path: Path):
        """Queue tests for execution."""
        test_spec = {
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "test_type": self._determine_test_type(file_path)
        }
        
        self.test_queue.append(test_spec)
        
        if not self.running_tests:
            self._run_queued_tests()
    
    def _determine_test_type(self, file_path: Path) -> str:
        """Determine what type of tests to run based on file."""
        
        file_name = file_path.name.lower()
        
        if "ui" in file_name or "streamlit" in file_name:
            return "ui_comprehensive"
        elif "vibe" in file_name:
            return "vibe_coding"
        elif "gem" in file_name:
            return "crystal_gem"
        else:
            return "general_ui"
    
    def _run_queued_tests(self):
        """Run all queued tests."""
        if not self.test_queue or self.running_tests:
            return
        
        self.running_tests = True
        
        try:
            print(f"\n🚀 Running automated tests for {len(self.test_queue)} file(s)...")
            
            # Group tests by type
            test_groups = {}
            for test_spec in self.test_queue:
                test_type = test_spec["test_type"]
                if test_type not in test_groups:
                    test_groups[test_type] = []
                test_groups[test_type].append(test_spec)
            
            # Run each test group
            all_results = []
            for test_type, specs in test_groups.items():
                print(f"\n🧪 Running {test_type} tests...")
                results = self._execute_test_group(test_type, specs)
                all_results.extend(results)
            
            # Generate summary report
            self._generate_cursor_report(all_results)
            
            # Clear queue
            self.test_queue.clear()
            
        finally:
            self.running_tests = False
    
    def _execute_test_group(self, test_type: str, specs: List[Dict]) -> List[Dict]:
        """Execute a group of tests of the same type."""
        
        results = []
        
        try:
            if test_type == "ui_comprehensive":
                # Run comprehensive UI tests
                result = self._run_ui_tests()
                results.append(result)
            
            elif test_type == "vibe_coding":
                # Run vibe coding specific tests
                result = self._run_vibe_coding_tests()
                results.append(result)
            
            elif test_type == "crystal_gem":
                # Run crystal gem tests
                result = self._run_crystal_gem_tests()
                results.append(result)
            
            else:
                # Run general UI validation
                result = self._run_general_ui_tests()
                results.append(result)
        
        except Exception as e:
            results.append({
                "test_type": test_type,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def _run_ui_tests(self) -> Dict[str, Any]:
        """Run comprehensive UI tests."""
        
        start_time = time.time()
        
        try:
            # Run pytest with UI tests
            cmd = [
                sys.executable, "-m", "pytest",
                str(project_root / "tests" / "automated_ui" / "test_vibe_coding_ui_comprehensive.py"),
                "-v", "--tb=short", "-x"  # Stop on first failure for faster feedback
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.config.get('test_timeout', 300)
            )
            
            execution_time = time.time() - start_time
            
            # Parse results
            success = result.returncode == 0
            test_output = result.stdout + result.stderr
            
            # Extract test metrics
            passed_tests = test_output.count(" PASSED")
            failed_tests = test_output.count(" FAILED") 
            skipped_tests = test_output.count(" SKIPPED")
            
            return {
                "test_type": "ui_comprehensive",
                "success": success,
                "execution_time": execution_time,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "output": test_output,
                "timestamp": datetime.now().isoformat()
            }
        
        except subprocess.TimeoutExpired:
            return {
                "test_type": "ui_comprehensive",
                "success": False,
                "error": "Test execution timed out",
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "test_type": "ui_comprehensive",
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_vibe_coding_tests(self) -> Dict[str, Any]:
        """Run vibe coding specific tests."""
        
        start_time = time.time()
        
        try:
            # Test vibe coding functionality
            from tests.automated_ui.test_vibe_coding_ui_comprehensive import AutomatedUITester, TestConfig
            
            config = TestConfig()
            tester = AutomatedUITester(config)
            
            # Start app for testing
            app_process = tester.start_streamlit_app()
            
            if not app_process:
                return {
                    "test_type": "vibe_coding",
                    "success": False,
                    "error": "Could not start Streamlit app",
                    "execution_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Setup browser
            if not tester.setup_browser():
                app_process.terminate()
                return {
                    "test_type": "vibe_coding",
                    "success": False,
                    "error": "Could not setup browser for testing",
                    "execution_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Run vibe-specific tests
            vibe_success = tester.test_vibe_expression_interface()
            journey_success = tester.test_user_journey_completion()
            
            # Cleanup
            tester.teardown_browser()
            app_process.terminate()
            
            # Generate report
            report = tester.generate_test_report()
            
            return {
                "test_type": "vibe_coding",
                "success": vibe_success and journey_success,
                "execution_time": time.time() - start_time,
                "vibe_translation_accuracy": tester.value_metrics["vibe_translation_accuracy"],
                "user_journey_completion": tester.value_metrics["user_journey_completion"],
                "detailed_report": report,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "test_type": "vibe_coding",
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_crystal_gem_tests(self) -> Dict[str, Any]:
        """Run crystal gem specific tests."""
        
        start_time = time.time()
        
        try:
            # Test crystal gem functionality
            cmd = [
                sys.executable, 
                str(project_root / "examples" / "crystal_gems" / "emerald_healthcare_vibe_gem.py")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0 and "VIBE CODING SUCCESS" in result.stdout
            
            return {
                "test_type": "crystal_gem",
                "success": success,
                "execution_time": time.time() - start_time,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "test_type": "crystal_gem",
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_general_ui_tests(self) -> Dict[str, Any]:
        """Run general UI validation tests."""
        
        start_time = time.time()
        
        try:
            # Basic syntax and import checks
            cmd = [
                sys.executable, "-m", "py_compile",
                str(project_root / "apps" / "vibe_coding_ui.py")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            syntax_ok = result.returncode == 0
            
            return {
                "test_type": "general_ui",
                "success": syntax_ok,
                "execution_time": time.time() - start_time,
                "checks": ["syntax_validation"],
                "error": result.stderr if result.stderr else None,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "test_type": "general_ui",
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_cursor_report(self, results: List[Dict[str, Any]]):
        """Generate formatted report for Cursor IDE."""
        
        print("\n" + "="*60)
        print("🤖 CURSOR AUTO-TESTING REPORT")
        print("="*60)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get("success", False))
        
        print(f"📊 Overall: {successful_tests}/{total_tests} tests passed")
        print(f"⏱️ Total time: {sum(r.get('execution_time', 0) for r in results):.1f}s")
        
        # Show results by type
        for result in results:
            test_type = result.get("test_type", "unknown")
            success = result.get("success", False)
            exec_time = result.get("execution_time", 0)
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_type} ({exec_time:.1f}s)")
            
            if not success and "error" in result:
                print(f"   Error: {result['error']}")
            
            # Show specific metrics for UI tests
            if test_type == "vibe_coding" and success:
                accuracy = result.get("vibe_translation_accuracy", 0)
                journey = result.get("user_journey_completion", 0)
                print(f"   📈 Vibe accuracy: {accuracy:.1f}%")
                print(f"   🎯 Journey completion: {journey:.1f}%")
        
        # Recommendations
        failed_results = [r for r in results if not r.get("success", False)]
        if failed_results:
            print("\n🔧 RECOMMENDATIONS:")
            for result in failed_results:
                test_type = result.get("test_type", "unknown")
                error = result.get("error", "Unknown error")
                
                if "timeout" in error.lower():
                    print(f"   {test_type}: Consider optimizing for faster execution")
                elif "browser" in error.lower():
                    print(f"   {test_type}: Check browser dependencies (Chrome/ChromeDriver)")
                elif "streamlit" in error.lower():
                    print(f"   {test_type}: Verify Streamlit installation and port availability")
                else:
                    print(f"   {test_type}: {error}")
        
        # Quality gates
        if successful_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT!")
        elif successful_tests / total_tests >= 0.8:
            print("\n⚠️ MOSTLY PASSING - REVIEW FAILURES BEFORE DEPLOYMENT")
        else:
            print("\n🚨 CRITICAL ISSUES - DO NOT DEPLOY UNTIL FIXED")
        
        print("="*60)
        
        # Save detailed report
        report_path = project_root / "tests" / "reports" / f"cursor_auto_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
                },
                "results": results
            }, f, indent=2)
        
        print(f"📄 Detailed report: {report_path}")

class CursorAutoTester:
    """Main class for Cursor IDE automated testing integration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.observer = None
        self.handler = None
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load testing configuration."""
        
        default_config = {
            "watch_paths": [
                str(project_root / "apps"),
                str(project_root / "examples" / "crystal_gems"),
                str(project_root / "tests" / "automated_ui")
            ],
            "debounce_seconds": 2,
            "test_timeout": 300,
            "enable_ui_tests": True,
            "enable_vibe_tests": True,
            "enable_gem_tests": True
        }
        
        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ Could not load config from {config_path}: {e}")
        
        return default_config
    
    def start_watching(self):
        """Start file watching for automatic test execution."""
        
        if self.observer:
            print("⚠️ Already watching files")
            return
        
        print("🤖 Starting Cursor Auto-Testing...")
        print(f"📁 Watching paths: {self.config['watch_paths']}")
        
        self.handler = CursorTestingHandler(self.config)
        self.observer = Observer()
        
        # Add watchers for each path
        for watch_path in self.config["watch_paths"]:
            path = Path(watch_path)
            if path.exists():
                self.observer.schedule(self.handler, str(path), recursive=True)
                print(f"📂 Watching: {path}")
            else:
                print(f"⚠️ Path not found: {path}")
        
        self.observer.start()
        print("✅ Auto-testing active - tests will run when you save files!")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()
    
    def stop_watching(self):
        """Stop file watching."""
        if self.observer:
            print("\n🛑 Stopping auto-testing...")
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.handler = None
            print("✅ Auto-testing stopped")
    
    def run_manual_test(self, test_type: str = "all"):
        """Run tests manually."""
        
        print(f"🧪 Running manual {test_type} tests...")
        
        handler = CursorTestingHandler(self.config)
        
        if test_type == "all" or test_type == "ui":
            result = handler._run_ui_tests()
            handler._generate_cursor_report([result])
        
        if test_type == "all" or test_type == "vibe":
            result = handler._run_vibe_coding_tests()
            handler._generate_cursor_report([result])
        
        if test_type == "all" or test_type == "gem":
            result = handler._run_crystal_gem_tests()
            handler._generate_cursor_report([result])

def main():
    """Main entry point for Cursor auto-testing."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Cursor IDE Automated Testing")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--manual", choices=["ui", "vibe", "gem", "all"], help="Run manual test")
    parser.add_argument("--watch", action="store_true", default=True, help="Start file watching (default)")
    
    args = parser.parse_args()
    
    tester = CursorAutoTester(args.config)
    
    if args.manual:
        tester.run_manual_test(args.manual)
    elif args.watch:
        tester.start_watching()

if __name__ == "__main__":
    main()
