#!/usr/bin/env python3
"""
Database Inspector - Comprehensive Database Schema Analysis
==========================================================

This tool inspects the universal_agent_tracking.db to see all tables
and their schemas so we can use ALL of them in our logging system.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any

def inspect_database(db_path: str = "utils/universal_agent_tracking.db") -> Dict[str, Any]:
    """
    Inspect the database and return comprehensive schema information.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Dictionary with complete database schema information
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        return {"error": f"Database file {db_path} does not exist"}
    
    inspection_result = {
        "database_path": str(db_file.absolute()),
        "database_size_bytes": db_file.stat().st_size,
        "tables": {},
        "total_tables": 0,
        "total_records": 0
    }
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row[0] for row in cursor.fetchall()]
            
            inspection_result["total_tables"] = len(table_names)
            
            # Inspect each table
            for table_name in table_names:
                table_info = {
                    "name": table_name,
                    "columns": [],
                    "indexes": [],
                    "record_count": 0,
                    "sample_records": []
                }
                
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                for col in columns:
                    table_info["columns"].append({
                        "cid": col[0],
                        "name": col[1],
                        "type": col[2],
                        "not_null": col[3],
                        "default_value": col[4],
                        "primary_key": col[5]
                    })
                
                # Get indexes
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                for idx in indexes:
                    table_info["indexes"].append({
                        "name": idx[1],
                        "unique": idx[2],
                        "origin": idx[3]
                    })
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = cursor.fetchone()[0]
                table_info["record_count"] = record_count
                inspection_result["total_records"] += record_count
                
                # Get sample records (up to 3)
                if record_count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_rows = cursor.fetchall()
                    column_names = [col["name"] for col in table_info["columns"]]
                    
                    for row in sample_rows:
                        sample_record = {}
                        for i, value in enumerate(row):
                            if i < len(column_names):
                                sample_record[column_names[i]] = value
                        table_info["sample_records"].append(sample_record)
                
                inspection_result["tables"][table_name] = table_info
                
    except Exception as e:
        inspection_result["error"] = str(e)
    
    return inspection_result

def print_database_report(db_path: str = "utils/universal_agent_tracking.db"):
    """Print a comprehensive database report."""
    
    print("🔍 Universal Agent Tracking Database Inspector")
    print("=" * 60)
    
    inspection = inspect_database(db_path)
    
    if "error" in inspection:
        print(f"❌ Error: {inspection['error']}")
        return
    
    print(f"📄 Database: {inspection['database_path']}")
    print(f"📊 Size: {inspection['database_size_bytes']} bytes")
    print(f"📋 Tables: {inspection['total_tables']}")
    print(f"📈 Total Records: {inspection['total_records']}")
    print()
    
    # Print table details
    for table_name, table_info in inspection["tables"].items():
        print(f"📊 Table: {table_name}")
        print(f"   Records: {table_info['record_count']}")
        print(f"   Columns: {len(table_info['columns'])}")
        
        for col in table_info["columns"]:
            pk_indicator = " (PK)" if col["primary_key"] else ""
            not_null_indicator = " NOT NULL" if col["not_null"] else ""
            print(f"     - {col['name']}: {col['type']}{pk_indicator}{not_null_indicator}")
        
        if table_info["sample_records"]:
            print(f"   Sample Data:")
            for i, record in enumerate(table_info["sample_records"], 1):
                print(f"     {i}. {record}")
        
        print()
    
    return inspection

if __name__ == "__main__":
    # Run inspection
    inspection = print_database_report()
    
    # Also create a JSON report
    if inspection and "error" not in inspection:
        with open("database_inspection_report.json", "w") as f:
            json.dump(inspection, f, indent=2)
        print("📄 Full report saved to: database_inspection_report.json")
