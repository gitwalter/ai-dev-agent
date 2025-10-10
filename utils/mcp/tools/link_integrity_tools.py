#!/usr/bin/env python3
"""
MCP Tools for Link Integrity Management
========================================

Exposes link healing and validation functionality as MCP tools for intelligent
agent access and automation.

Features:
- Link discovery and scanning
- Link validation and broken link detection
- Automatic link healing during file operations
- Integration with file organization tools

MCP Tool IDs:
- link.scan_all: Scan project for all links
- link.validate: Validate all discovered links
- link.heal: Heal links after file renames
- link.generate_report: Generate link analysis report

Author: AI Development Agent
Created: 2025-10-10
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.link_healing_system import LinkHealingSystem


def scan_all_links(target_directory: str = ".") -> Dict[str, Any]:
    """
    Scan project for all links in documentation.
    
    MCP Tool: link.scan_all
    Access Level: PUBLIC
    Category: FILE_SYSTEM
    
    Args:
        target_directory: Root directory to scan (default: current directory)
        
    Returns:
        Dictionary with link discovery results:
        - markdown_files: List of markdown files with links
        - python_files: List of Python files with doc references
        - config_files: List of config files with doc references
        - discovered_links: Complete list of all discovered links
        - summary: Summary statistics
    """
    try:
        healer = LinkHealingSystem(project_root=target_directory)
        all_links = healer.scan_all_links()
        
        # Add summary statistics
        summary = {
            "total_links": len(all_links.get("discovered_links", [])),
            "markdown_files_count": len(all_links.get("markdown_files", [])),
            "python_files_count": len(all_links.get("python_files", [])),
            "config_files_count": len(all_links.get("config_files", []))
        }
        
        return {
            "success": True,
            "data": {
                "markdown_files": all_links.get("markdown_files", []),
                "python_files": all_links.get("python_files", []),
                "config_files": all_links.get("config_files", []),
                "discovered_links": all_links.get("discovered_links", []),
                "summary": summary
            },
            "message": f"Scanned {summary['total_links']} links across {summary['markdown_files_count']} markdown files"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to scan links: {e}"
        }


def validate_all_links(target_directory: str = ".") -> Dict[str, Any]:
    """
    Validate all discovered links in the project.
    
    MCP Tool: link.validate
    Access Level: PUBLIC
    Category: FILE_SYSTEM
    
    Args:
        target_directory: Root directory to validate (default: current directory)
        
    Returns:
        Dictionary with validation results:
        - valid_links: List of valid, working links
        - broken_links: List of broken links that need attention
        - external_links: List of external (http/https) links
        - suspicious_links: List of links with unusual patterns
        - summary: Summary statistics
    """
    try:
        healer = LinkHealingSystem(project_root=target_directory)
        
        # First scan for links
        healer.scan_all_links()
        
        # Then validate them
        validation_results = healer.validate_all_links()
        
        # Add summary statistics
        summary = {
            "total_links": sum([
                len(validation_results.get("valid_links", [])),
                len(validation_results.get("broken_links", [])),
                len(validation_results.get("external_links", []))
            ]),
            "valid_count": len(validation_results.get("valid_links", [])),
            "broken_count": len(validation_results.get("broken_links", [])),
            "external_count": len(validation_results.get("external_links", [])),
            "validation_rate": round(
                len(validation_results.get("valid_links", [])) / 
                max(1, sum([
                    len(validation_results.get("valid_links", [])),
                    len(validation_results.get("broken_links", []))
                ])) * 100, 2
            )
        }
        
        return {
            "success": True,
            "data": {
                "valid_links": validation_results.get("valid_links", []),
                "broken_links": validation_results.get("broken_links", []),
                "external_links": validation_results.get("external_links", []),
                "suspicious_links": validation_results.get("suspicious_links", []),
                "summary": summary
            },
            "message": f"Validated {summary['total_links']} links: {summary['valid_count']} valid, {summary['broken_count']} broken"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to validate links: {e}"
        }


def heal_links_after_rename(rename_mapping: Dict[str, str], target_directory: str = ".") -> Dict[str, Any]:
    """
    Heal all links after file renames or moves.
    
    MCP Tool: link.heal
    Access Level: RESTRICTED
    Category: FILE_SYSTEM
    Requires Confirmation: True
    
    Args:
        rename_mapping: Dictionary of {old_path: new_path} for renamed files
        target_directory: Root directory to heal (default: current directory)
        
    Returns:
        Dictionary with healing results:
        - files_updated: Number of files updated
        - links_healed: Number of links successfully healed
        - files_processed: Total files processed
        - backups_created: List of backup files created
    """
    try:
        healer = LinkHealingSystem(project_root=target_directory)
        
        # First scan for links
        healer.scan_all_links()
        
        # Create rename mapping
        mapping = healer.create_rename_mapping(rename_mapping)
        
        # Heal all links
        healing_stats = healer.heal_all_links(mapping)
        
        return {
            "success": True,
            "data": {
                "files_updated": healing_stats.get("files_updated", 0),
                "links_healed": healing_stats.get("links_healed", 0),
                "files_processed": healing_stats.get("files_processed", 0)
            },
            "message": f"Healed {healing_stats.get('links_healed', 0)} links across {healing_stats.get('files_updated', 0)} files"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to heal links: {e}"
        }


def generate_link_report(target_directory: str = ".", output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate comprehensive link analysis report.
    
    MCP Tool: link.generate_report
    Access Level: PUBLIC
    Category: FILE_SYSTEM
    
    Args:
        target_directory: Root directory to analyze (default: current directory)
        output_path: Optional path to save report (default: docs/agile/analysis/LINK_ANALYSIS_REPORT.md)
        
    Returns:
        Dictionary with report generation results:
        - report_path: Path where report was saved
        - report_content: Full report content
        - summary: Summary statistics from the report
    """
    try:
        healer = LinkHealingSystem(project_root=target_directory)
        
        # Scan and validate links
        healer.scan_all_links()
        healer.validate_all_links()
        
        # Generate report
        report_content = healer.generate_link_report()
        
        # Determine output path
        if output_path is None:
            output_path = Path(target_directory) / "docs/agile/analysis/LINK_ANALYSIS_REPORT.md"
        else:
            output_path = Path(output_path)
        
        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content, encoding='utf-8')
        
        # Extract summary from report
        total_links = len(healer.all_links.get("discovered_links", []))
        broken_count = len(healer.broken_links)
        valid_count = total_links - broken_count
        
        summary = {
            "total_links": total_links,
            "valid_links": valid_count,
            "broken_links": broken_count,
            "files_with_links": len(healer.all_links.get("markdown_files", []))
        }
        
        return {
            "success": True,
            "data": {
                "report_path": str(output_path),
                "report_content": report_content,
                "summary": summary
            },
            "message": f"Link analysis report generated: {output_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate link report: {e}"
        }


def check_before_file_move(old_path: str, new_path: str, target_directory: str = ".") -> Dict[str, Any]:
    """
    Check what links would be affected by a file move before performing it.
    
    MCP Tool: link.check_before_move
    Access Level: PUBLIC
    Category: FILE_SYSTEM
    
    Args:
        old_path: Current file path
        new_path: Proposed new file path
        target_directory: Root directory to check (default: current directory)
        
    Returns:
        Dictionary with impact analysis:
        - affected_files: List of files that link to this file
        - link_count: Number of links that would need updating
        - safe_to_move: Boolean indicating if move is safe
        - recommendations: List of recommended actions
    """
    try:
        healer = LinkHealingSystem(project_root=target_directory)
        
        # Scan for all links
        healer.scan_all_links()
        
        # Find links pointing to the old path
        affected_links = []
        affected_files = set()
        
        for file_info in healer.all_links.get("markdown_files", []):
            for link in file_info.get("links", []):
                if old_path in link.get("path", ""):
                    affected_links.append(link)
                    affected_files.add(file_info["file"])
        
        # Generate recommendations
        recommendations = []
        if affected_links:
            recommendations.append(f"Update {len(affected_links)} links across {len(affected_files)} files")
            recommendations.append(f"Use link.heal with mapping: {{'{old_path}': '{new_path}'}}")
        else:
            recommendations.append("No links affected - safe to move directly")
        
        return {
            "success": True,
            "data": {
                "affected_files": list(affected_files),
                "link_count": len(affected_links),
                "affected_links": affected_links,
                "safe_to_move": len(affected_links) == 0,
                "recommendations": recommendations
            },
            "message": f"Found {len(affected_links)} links that would be affected by moving {old_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to check file move impact: {e}"
        }


# MCP Tool Definitions for Registration
MCP_TOOL_DEFINITIONS = [
    {
        "tool_id": "link.scan_all",
        "name": "Scan All Links",
        "description": "Scan project for all documentation links",
        "category": "file_system",
        "access_level": "public",
        "function": scan_all_links,
        "parameters_schema": {
            "target_directory": {"type": "string", "default": "."}
        },
        "returns_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "message": {"type": "string"}
            }
        }
    },
    {
        "tool_id": "link.validate",
        "name": "Validate All Links",
        "description": "Validate all discovered links and find broken ones",
        "category": "file_system",
        "access_level": "public",
        "function": validate_all_links,
        "parameters_schema": {
            "target_directory": {"type": "string", "default": "."}
        },
        "returns_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "message": {"type": "string"}
            }
        }
    },
    {
        "tool_id": "link.heal",
        "name": "Heal Links After Rename",
        "description": "Automatically heal all links after file renames or moves",
        "category": "file_system",
        "access_level": "restricted",
        "function": heal_links_after_rename,
        "requires_confirmation": True,
        "parameters_schema": {
            "rename_mapping": {"type": "object", "required": True},
            "target_directory": {"type": "string", "default": "."}
        },
        "returns_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "message": {"type": "string"}
            }
        }
    },
    {
        "tool_id": "link.generate_report",
        "name": "Generate Link Analysis Report",
        "description": "Generate comprehensive link analysis and health report",
        "category": "file_system",
        "access_level": "public",
        "function": generate_link_report,
        "parameters_schema": {
            "target_directory": {"type": "string", "default": "."},
            "output_path": {"type": "string", "required": False}
        },
        "returns_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "message": {"type": "string"}
            }
        }
    },
    {
        "tool_id": "link.check_before_move",
        "name": "Check File Move Impact",
        "description": "Check what links would be affected before moving a file",
        "category": "file_system",
        "access_level": "public",
        "function": check_before_file_move,
        "parameters_schema": {
            "old_path": {"type": "string", "required": True},
            "new_path": {"type": "string", "required": True},
            "target_directory": {"type": "string", "default": "."}
        },
        "returns_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "message": {"type": "string"}
            }
        }
    }
]


if __name__ == "__main__":
    # Demonstration of MCP tools
    print("Link Integrity MCP Tools - Demonstration")
    print("=" * 60)
    
    # Test scan
    print("\n1. Scanning all links...")
    result = scan_all_links()
    print(f"   Result: {result['message']}")
    
    # Test validate
    print("\n2. Validating links...")
    result = validate_all_links()
    print(f"   Result: {result['message']}")
    
    # Test report generation
    print("\n3. Generating report...")
    result = generate_link_report()
    print(f"   Result: {result['message']}")
    
    print("\nAll MCP link integrity tools tested successfully!")

