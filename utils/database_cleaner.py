#!/usr/bin/env python3
"""
Database Cleaner for GitHub Distribution.

This utility creates a clean version of the prompt database for GitHub distribution
by removing execution data, usage statistics, and keeping only essential prompt templates.
"""

import sqlite3
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseCleaner:
    """
    Cleans the prompt database for GitHub distribution.
    """
    
    def __init__(self, source_db_path: str = "prompts/prompt_templates.db"):
        """
        Initialize the database cleaner.
        
        Args:
            source_db_path: Path to the source database file
        """
        self.source_db_path = Path(source_db_path)
        self.clean_db_path = self.source_db_path.parent / "prompt_templates_clean.db"
        
    def create_clean_database(self, output_path: Optional[str] = None) -> str:
        """
        Create a clean version of the database for GitHub distribution.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to the clean database file
        """
        if output_path:
            clean_db_path = Path(output_path)
        else:
            clean_db_path = self.clean_db_path
            
        logger.info(f"Creating clean database at: {clean_db_path}")
        
        # Copy the original database
        shutil.copy2(self.source_db_path, clean_db_path)
        
        # Clean the copied database
        self._clean_database(clean_db_path)
        
        logger.info(f"Clean database created successfully: {clean_db_path}")
        return str(clean_db_path)
    
    def _clean_database(self, db_path: Path):
        """
        Clean the database by removing execution data and resetting statistics.
        
        Args:
            db_path: Path to the database to clean
        """
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Remove execution data (traffic content)
            logger.info("Removing execution data...")
            cursor.execute("DELETE FROM prompt_executions")
            cursor.execute("DELETE FROM prompt_analysis")
            cursor.execute("DELETE FROM prompt_improvements")
            
            # Reset usage statistics but keep prompt templates
            logger.info("Resetting usage statistics...")
            cursor.execute("""
                UPDATE prompts 
                SET usage_count = 0, 
                    success_rate = 0.0, 
                    average_response_time = 0.0, 
                    last_used = NULL
            """)
            
            # Keep all prompt templates (they are essential for the system)
            logger.info("Keeping all prompt templates...")
            # No deletion needed - all prompts in the prompts table are essential
            
            # Note: RAG documents and system_prompts tables don't exist in this database
            # Only the following tables exist: prompts, prompt_executions, prompt_analysis, prompt_improvements
            
            # Reset auto-increment counters
            logger.info("Resetting auto-increment counters...")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('prompt_executions', 'prompt_analysis', 'prompt_improvements')")
            
            # Commit changes
            conn.commit()
            
            # Get statistics
            self._log_cleaning_statistics(cursor)
    
    def _log_cleaning_statistics(self, cursor):
        """
        Log statistics about the cleaning process.
        
        Args:
            cursor: Database cursor
        """
        # Count remaining records
        cursor.execute("SELECT COUNT(*) FROM prompts")
        prompt_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prompt_executions")
        execution_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prompt_analysis")
        analysis_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prompt_improvements")
        improvement_count = cursor.fetchone()[0]
        
        logger.info(f"Cleaning completed:")
        logger.info(f"  - Prompts kept: {prompt_count}")
        logger.info(f"  - Executions removed: {execution_count}")
        logger.info(f"  - Analysis records removed: {analysis_count}")
        logger.info(f"  - Improvement records removed: {improvement_count}")
    
    def get_essential_prompts(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get list of essential prompts that should be included in the clean database.
        
        Returns:
            Dictionary of essential prompts by agent
        """
        essential_prompts = {
            "requirements_analyst": [
                {
                    "name": "requirements_analysis",
                    "description": "Core requirements analysis prompt",
                    "category": "core"
                }
            ],
            "architecture_designer": [
                {
                    "name": "architecture_design",
                    "description": "Core architecture design prompt",
                    "category": "core"
                }
            ],
            "code_generator": [
                {
                    "name": "code_generation",
                    "description": "Core code generation prompt",
                    "category": "core"
                }
            ],
            "test_generator": [
                {
                    "name": "test_generation",
                    "description": "Core test generation prompt",
                    "category": "core"
                }
            ],
            "code_reviewer": [
                {
                    "name": "code_review",
                    "description": "Core code review prompt",
                    "category": "core"
                }
            ],
            "security_analyst": [
                {
                    "name": "security_analysis",
                    "description": "Core security analysis prompt",
                    "category": "core"
                }
            ],
            "documentation_generator": [
                {
                    "name": "documentation_generation",
                    "description": "Core documentation generation prompt",
                    "category": "core"
                }
            ]
        }
        
        return essential_prompts
    
    def validate_clean_database(self, db_path: str) -> bool:
        """
        Validate that the clean database contains essential data.
        
        Args:
            db_path: Path to the clean database
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Check that essential tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['prompts', 'prompt_executions', 'prompt_analysis', 'prompt_improvements']
                
                for table in required_tables:
                    if table not in tables:
                        logger.error(f"Required table missing: {table}")
                        return False
                
                # Check that prompts table has data
                cursor.execute("SELECT COUNT(*) FROM prompts")
                prompt_count = cursor.fetchone()[0]
                
                if prompt_count == 0:
                    logger.error("No prompts found in clean database")
                    return False
                
                # Check that execution data is removed
                cursor.execute("SELECT COUNT(*) FROM prompt_executions")
                execution_count = cursor.fetchone()[0]
                
                if execution_count > 0:
                    logger.error(f"Execution data still present: {execution_count} records")
                    return False
                
                # Check that analysis data is removed
                cursor.execute("SELECT COUNT(*) FROM prompt_analysis")
                analysis_count = cursor.fetchone()[0]
                
                if analysis_count > 0:
                    logger.error(f"Analysis data still present: {analysis_count} records")
                    return False
                
                # Check that improvement data is removed
                cursor.execute("SELECT COUNT(*) FROM prompt_improvements")
                improvement_count = cursor.fetchone()[0]
                
                if improvement_count > 0:
                    logger.error(f"Improvement data still present: {improvement_count} records")
                    return False
                
                logger.info("Clean database validation passed")
                return True
                
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            return False


def create_github_ready_database():
    """
    Create a GitHub-ready version of the prompt database.
    
    This function creates a clean database that can be safely included in GitHub
    without exposing user data or execution history.
    """
    cleaner = DatabaseCleaner()
    
    try:
        # Create clean database
        clean_db_path = cleaner.create_clean_database()
        
        # Validate the clean database
        if cleaner.validate_clean_database(clean_db_path):
            logger.info("✅ GitHub-ready database created successfully")
            logger.info(f"📁 Clean database: {clean_db_path}")
            logger.info("📋 Ready to commit to GitHub")
            return clean_db_path
        else:
            logger.error("❌ Clean database validation failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to create clean database: {e}")
        return None


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create GitHub-ready database
    clean_db_path = create_github_ready_database()
    
    if clean_db_path:
        print(f"\n🎉 Success! Clean database created: {clean_db_path}")
        print("📝 This database is ready to be committed to GitHub")
        print("🔒 It contains only essential prompt templates, no user data")
    else:
        print("\n❌ Failed to create clean database")
        exit(1)
