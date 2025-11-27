"""
Website Test Tool for testing HTML pages and Streamlit apps.

This tool allows agents to:
- Test HTML file structure and validity
- Validate Streamlit apps
- Check for broken links
- Validate basic accessibility
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


class WebsiteTestTool:
    """
    Tool for testing HTML websites and Streamlit apps.
    
    Provides validation and testing capabilities for web applications.
    """
    
    def __init__(self, python_executable: Optional[str] = None):
        """
        Initialize website test tool.
        
        Args:
            python_executable: Path to Python executable (for Streamlit validation)
        """
        if python_executable is None:
            self.python_executable = r"C:\App\Anaconda\python.exe"
        else:
            self.python_executable = python_executable
        
        # Verify Python executable exists
        if not Path(self.python_executable).exists():
            logger.warning(f"Python executable not found: {self.python_executable}")
            self.python_executable = sys.executable
    
    def test_html_file(self, html_file: str) -> Dict[str, Any]:
        """
        Test HTML file for structure and validity.
        
        Args:
            html_file: Path to HTML file
            
        Returns:
            Test results with validation status, issues, broken links
        """
        try:
            html_path = Path(html_file)
            if not html_path.exists():
                return {
                    "success": False,
                    "error": f"HTML file not found: {html_file}",
                    "issues": [],
                    "broken_links": []
                }
            
            # Read and parse HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Basic validation
            issues = []
            
            # Check for required elements
            if not soup.find('html'):
                issues.append("Missing <html> tag")
            if not soup.find('head'):
                issues.append("Missing <head> tag")
            if not soup.find('body'):
                issues.append("Missing <body> tag")
            
            # Check for title
            title_tag = soup.find('title')
            has_title = title_tag is not None
            title_text = title_tag.get_text() if title_tag else ""
            
            # Check for meta charset
            has_meta_charset = soup.find('meta', charset=True) is not None
            
            # Check for broken links (if any)
            links = soup.find_all('a', href=True)
            broken_links = []
            for link in links:
                href = link['href']
                if href.startswith('http'):
                    try:
                        response = requests.head(href, timeout=5, allow_redirects=True)
                        if response.status_code >= 400:
                            broken_links.append({
                                "href": href,
                                "status_code": response.status_code,
                                "text": link.get_text()[:50]
                            })
                    except Exception as e:
                        broken_links.append({
                            "href": href,
                            "error": str(e),
                            "text": link.get_text()[:50]
                        })
            
            return {
                "success": len(issues) == 0,
                "issues": issues,
                "broken_links": broken_links,
                "link_count": len(links),
                "has_title": has_title,
                "title": title_text,
                "has_meta_charset": has_meta_charset,
                "file_size": len(html_content)
            }
        except Exception as e:
            logger.error(f"HTML file test error: {e}")
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "broken_links": []
            }
    
    def validate_streamlit_app(self, app_file: str) -> Dict[str, Any]:
        """
        Validate Streamlit app file structure.
        
        Args:
            app_file: Path to Streamlit app file
            
        Returns:
            Validation results
        """
        try:
            app_path = Path(app_file)
            if not app_path.exists():
                return {
                    "success": False,
                    "error": f"Streamlit app file not found: {app_file}",
                    "issues": []
                }
            
            # Read file and check for Streamlit imports
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            warnings = []
            
            # Check for Streamlit import
            has_streamlit_import = 'import streamlit' in content or 'from streamlit' in content
            if not has_streamlit_import:
                issues.append("Missing Streamlit import (should have 'import streamlit' or 'from streamlit')")
            
            # Check for basic Streamlit usage
            has_streamlit_usage = 'st.' in content
            if not has_streamlit_usage:
                issues.append("No Streamlit components found (should use st.*)")
            
            # Check for common Streamlit patterns
            has_title = 'st.title' in content or 'st.header' in content
            has_markdown = 'st.markdown' in content
            
            # Check for potential issues
            if 'if __name__' not in content and 'streamlit run' not in content:
                warnings.append("Consider adding 'if __name__ == \"__main__\":' guard")
            
            return {
                "success": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "file_size": len(content),
                "has_streamlit_import": has_streamlit_import,
                "has_streamlit_usage": has_streamlit_usage,
                "has_title": has_title,
                "has_markdown": has_markdown
            }
        except Exception as e:
            logger.error(f"Streamlit app validation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "issues": []
            }
    
    def check_accessibility_basic(self, html_file: str) -> Dict[str, Any]:
        """
        Basic accessibility checks for HTML file.
        
        Args:
            html_file: Path to HTML file
            
        Returns:
            Accessibility check results
        """
        try:
            html_path = Path(html_file)
            if not html_path.exists():
                return {
                    "success": False,
                    "error": f"HTML file not found: {html_file}",
                    "accessibility_issues": []
                }
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            issues = []
            
            # Check for alt text on images
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            if images_without_alt:
                issues.append(f"{len(images_without_alt)} image(s) without alt text")
            
            # Check for form labels
            inputs = soup.find_all(['input', 'textarea', 'select'])
            for inp in inputs:
                input_id = inp.get('id')
                if input_id:
                    label = soup.find('label', {'for': input_id})
                    if not label:
                        # Check if label wraps input
                        parent_label = inp.find_parent('label')
                        if not parent_label:
                            issues.append(f"Input without associated label (id: {input_id})")
            
            return {
                "success": len(issues) == 0,
                "accessibility_issues": issues,
                "image_count": len(images),
                "input_count": len(inputs)
            }
        except Exception as e:
            logger.error(f"Accessibility check error: {e}")
            return {
                "success": False,
                "error": str(e),
                "accessibility_issues": []
            }

