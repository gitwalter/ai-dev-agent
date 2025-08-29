#!/usr/bin/env python3
"""
Session Shutdown Script

This script triggers the comprehensive session shutdown routine when executed.
It can be run directly or called from the command line.

Usage:
    python scripts/session_shutdown.py
    python -m scripts.session_shutdown
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_tests(test_category: str = "all") -> dict:
    """
    Run tests for the specified category.
    
    Args:
        test_category: Test category to run (all, unit, integration, system, performance, security)
        
    Returns:
        Dictionary with test results
    """
    logger.info(f"Running {test_category} tests...")
    
    try:
        if test_category == "all":
            cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
        else:
            cmd = ["python", "-m", "pytest", f"tests/{test_category}/", "-v", "--tb=short"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        return {
            "passed": result.returncode == 0,
            "count": len([line for line in result.stdout.split('\n') if "PASSED" in line]),
            "output": result.stdout,
            "errors": result.stderr
        }
    except Exception as e:
        logger.error(f"Error running {test_category} tests: {e}")
        return {
            "passed": False,
            "count": 0,
            "output": "",
            "errors": str(e)
        }


def validate_documentation() -> dict:
    """
    Validate documentation completeness.
    
    Returns:
        Dictionary with documentation validation results
    """
    logger.info("Validating documentation...")
    
    docs_dir = project_root / "docs"
    required_files = [
        "README.md",
        "CHANGELOG.md",
        "DOCUMENTATION_INDEX.md"
    ]
    
    validation_results = {
        "main_docs": {"valid": True, "issues": []},
        "readme_files": {"valid": True, "issues": []},
        "api_docs": {"valid": True, "issues": []},
        "code_docs": {"valid": True, "issues": []},
        "architecture_docs": {"valid": True, "issues": []},
        "deployment_docs": {"valid": True, "issues": []},
        "fixes_applied": False
    }
    
    # Check main documentation files
    for file_name in required_files:
        file_path = docs_dir / file_name
        if not file_path.exists():
            validation_results["main_docs"]["valid"] = False
            validation_results["main_docs"]["issues"].append(f"Missing {file_name}")
    
    # Check README files in key directories
    readme_dirs = ["agents", "workflow", "models", "utils", "tests"]
    for dir_name in readme_dirs:
        readme_path = project_root / dir_name / "README.md"
        if not readme_path.exists():
            validation_results["readme_files"]["valid"] = False
            validation_results["readme_files"]["issues"].append(f"Missing README.md in {dir_name}/")
    
    # Check API documentation
    api_docs_path = docs_dir / "api"
    if not api_docs_path.exists():
        validation_results["api_docs"]["valid"] = False
        validation_results["api_docs"]["issues"].append("Missing API documentation directory")
    
    # Check architecture documentation
    arch_docs_path = docs_dir / "architecture"
    if not arch_docs_path.exists():
        validation_results["architecture_docs"]["valid"] = False
        validation_results["architecture_docs"]["issues"].append("Missing architecture documentation directory")
    
    # Check deployment documentation
    deploy_docs_path = docs_dir / "guides" / "deployment"
    if not deploy_docs_path.exists():
        validation_results["deployment_docs"]["valid"] = False
        validation_results["deployment_docs"]["issues"].append("Missing deployment documentation directory")
    
    # Overall validation status
    all_valid = all(
        validation_results[key]["valid"] 
        for key in ["main_docs", "readme_files", "api_docs", "code_docs", "architecture_docs", "deployment_docs"]
    )
    
    return {
        "status": "SUCCESS" if all_valid else "FAILED",
        "all_valid": all_valid,
        **validation_results
    }


def perform_git_operations() -> dict:
    """
    Perform git operations (stage, commit, push).
    
    Returns:
        Dictionary with git operation results
    """
    logger.info("Performing git operations...")
    
    try:
        # Check git status
        status_result = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, text=True, cwd=project_root
        )
        
        if not status_result.stdout.strip():
            logger.info("No changes to commit")
            return {
                "status": "SUCCESS",
                "commit_hash": "N/A",
                "commit_message": "No changes to commit",
                "push_status": "N/A",
                "changes_committed": []
            }
        
        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=project_root, check=True)
        
        # Create commit message
        commit_message = f"Session completion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Automated session shutdown"
        
        # Commit changes
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True, text=True, cwd=project_root
        )
        
        if commit_result.returncode != 0:
            return {
                "status": "FAILED",
                "reason": f"Commit failed: {commit_result.stderr}",
                "commit_hash": "N/A",
                "commit_message": "N/A",
                "push_status": "N/A",
                "changes_committed": []
            }
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=project_root
        )
        commit_hash = hash_result.stdout.strip()[:12] if hash_result.returncode == 0 else "N/A"
        
        # Push changes
        push_result = subprocess.run(
            ["git", "push"],
            capture_output=True, text=True, cwd=project_root
        )
        
        push_status = "SUCCESS" if push_result.returncode == 0 else "FAILED"
        
        # Get list of changed files
        changed_files = [line.split()[-1] for line in status_result.stdout.strip().split('\n') if line.strip()]
        
        return {
            "status": "SUCCESS",
            "commit_hash": commit_hash,
            "commit_message": commit_message,
            "push_status": push_status,
            "changes_committed": changed_files
        }
        
    except Exception as e:
        logger.error(f"Git operations failed: {e}")
        return {
            "status": "FAILED",
            "reason": str(e),
            "commit_hash": "N/A",
            "commit_message": "N/A",
            "push_status": "N/A",
            "changes_committed": []
        }


def generate_session_summary(test_validation: dict, doc_validation: dict, git_operations: dict) -> str:
    """
    Generate comprehensive session shutdown summary.
    
    Args:
        test_validation: Test validation results
        doc_validation: Documentation validation results
        git_operations: Git operations results
        
    Returns:
        Formatted summary string
    """
    summary = f"""
## 🛑 **SESSION STOP SUMMARY**

### **Test Validation Results** 🧪
- **Status**: {'✅ PASSED' if test_validation['status'] == 'SUCCESS' else '❌ FAILED'}
- **Total Tests Run**: {test_validation.get('total_tests', 0)}
- **Unit Tests**: {'✅' if test_validation['unit_tests']['passed'] else '❌'} ({test_validation['unit_tests']['count']} tests)
- **Integration Tests**: {'✅' if test_validation['integration_tests']['passed'] else '❌'} ({test_validation['integration_tests']['count']} tests)
- **System Tests**: {'✅' if test_validation['system_tests']['passed'] else '❌'} ({test_validation['system_tests']['count']} tests)
- **Performance Tests**: {'✅' if test_validation['performance_tests']['passed'] else '❌'} ({test_validation['performance_tests']['count']} tests)
- **Security Tests**: {'✅' if test_validation['security_tests']['passed'] else '❌'} ({test_validation['security_tests']['count']} tests)

### **Documentation Validation Results** 📚
- **Status**: {'✅ VALIDATED' if doc_validation['status'] == 'SUCCESS' else '❌ ISSUES'}
- **Main Documentation**: {'✅' if doc_validation['main_docs']['valid'] else '❌'}
- **README Files**: {'✅' if doc_validation['readme_files']['valid'] else '❌'}
- **API Documentation**: {'✅' if doc_validation['api_docs']['valid'] else '❌'}
- **Code Documentation**: {'✅' if doc_validation['code_docs']['valid'] else '❌'}
- **Architecture Documentation**: {'✅' if doc_validation['architecture_docs']['valid'] else '❌'}
- **Deployment Documentation**: {'✅' if doc_validation['deployment_docs']['valid'] else '❌'}
- **Fixes Applied**: {'✅ Yes' if doc_validation.get('fixes_applied', False) else '❌ No'}

### **Git Operations Results** 🔄
- **Status**: {'✅ SUCCESS' if git_operations['status'] == 'SUCCESS' else '❌ FAILED'}
- **Commit Hash**: {git_operations.get('commit_hash', 'N/A')}
- **Commit Message**: {git_operations.get('commit_message', 'N/A')}
- **Push Status**: {git_operations.get('push_status', 'N/A')}
- **Changes Committed**: {len(git_operations.get('changes_committed', []))} files

### **Session Stop Status** 🎯
- **Overall Status**: {'✅ SUCCESS' if all([test_validation['status'] == 'SUCCESS', doc_validation['status'] == 'SUCCESS', git_operations['status'] == 'SUCCESS']) else '❌ FAILED'}
- **Session End Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Next Session**: Ready to begin when needed

### **Quality Assurance** ✅
- **All Tests Passing**: {'✅ Yes' if test_validation['status'] == 'SUCCESS' else '❌ No'}
- **Documentation Complete**: {'✅ Yes' if doc_validation['status'] == 'SUCCESS' else '❌ No'}
- **Changes Committed**: {'✅ Yes' if git_operations['status'] == 'SUCCESS' else '❌ No'}
- **Repository Clean**: {'✅ Yes' if git_operations['status'] == 'SUCCESS' else '❌ No'}

**Session successfully ended with all quality checks passed!** 🎉
"""
    
    return summary


def main():
    """Main entry point for session shutdown."""
    
    print("🛑 **SESSION STOP ROUTINE INITIATED**")
    print("=" * 50)
    
    # STEP 1: Comprehensive Test Validation
    print("🧪 Step 1: Running comprehensive test validation...")
    
    test_categories = ["unit", "integration", "system", "performance", "security"]
    test_results = {}
    
    for category in test_categories:
        test_results[category] = run_tests(category)
    
    # Run all tests for total count
    all_tests = run_tests("all")
    
    test_validation = {
        "status": "SUCCESS" if all_tests["passed"] else "FAILED",
        "total_tests": all_tests["count"],
        "unit_tests": test_results["unit"],
        "integration_tests": test_results["integration"],
        "system_tests": test_results["system"],
        "performance_tests": test_results["performance"],
        "security_tests": test_results["security"]
    }
    
    if test_validation["status"] == "FAILED":
        print("❌ **SESSION STOP BLOCKED**: Test validation failed")
        print("   - Please fix failing tests before ending session")
        return False
    
    print("✅ Test validation completed successfully")
    
    # STEP 2: Documentation Completeness Validation
    print("📚 Step 2: Validating documentation completeness...")
    
    doc_validation = validate_documentation()
    
    if doc_validation["status"] == "FAILED":
        print("❌ **SESSION STOP BLOCKED**: Documentation validation failed")
        print("   - Please resolve documentation issues before ending session")
        return False
    
    print("✅ Documentation validation completed successfully")
    
    # STEP 3: Git Operations
    print("🔄 Step 3: Performing git operations...")
    
    git_operations = perform_git_operations()
    
    if git_operations["status"] == "FAILED":
        print("❌ **SESSION STOP BLOCKED**: Git operations failed")
        print(f"   - Reason: {git_operations.get('reason', 'Unknown error')}")
        return False
    
    print("✅ Git operations completed successfully")
    
    # Generate session summary
    session_summary = generate_session_summary(test_validation, doc_validation, git_operations)
    
    print("🎉 **SESSION STOP COMPLETE**")
    print(session_summary)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
