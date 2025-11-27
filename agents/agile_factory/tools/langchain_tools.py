"""
LangChain tool wrappers for Agile Factory tools.

Uses LangChain's built-in Python REPL tool and custom website test tool.
"""

from langchain_core.tools import tool, Tool
try:
    from langchain_experimental.utilities import PythonREPL
    LANGCHAIN_EXPERIMENTAL_AVAILABLE = True
except ImportError:
    # Fallback if langchain_experimental not available
    PythonREPL = None
    LANGCHAIN_EXPERIMENTAL_AVAILABLE = False
from agents.agile_factory.tools.website_test_tool import WebsiteTestTool

# Initialize custom website test tool
_website_test = WebsiteTestTool()

# Initialize LangChain's Python REPL tool if available
if LANGCHAIN_EXPERIMENTAL_AVAILABLE:
    _python_repl = PythonREPL()
    # Create LangChain tool from PythonREPL
    python_repl_tool = Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
        func=_python_repl.run,
    )
else:
    # Fallback: create a placeholder tool
    python_repl_tool = None


# Use LangChain's Python REPL tool directly (python_repl_tool created above)
# Additional helper tools for specific use cases


@tool
def streamlit_validate_app(app_file: str) -> str:
    """
    Validate Streamlit app file structure and imports.
    
    Args:
        app_file: Path to Streamlit app file
        
    Returns:
        Validation result as formatted string
    """
    result = _website_test.validate_streamlit_app(app_file)
    
    if result["success"]:
        return f"Streamlit app validation passed:\n- Has Streamlit import: {result.get('has_streamlit_import')}\n- Has Streamlit usage: {result.get('has_streamlit_usage')}"
    else:
        issues = result.get("issues", [])
        error = result.get("error", "")
        issues_str = "\n".join(f"- {issue}" for issue in issues)
        return f"Streamlit app validation failed:\n{issues_str}\n{error}"


@tool
def streamlit_run_app(app_file: str, port: int = 8501) -> str:
    """
    Run Streamlit app and validate it starts successfully.
    
    Uses Python REPL to execute streamlit run command.
    
    Args:
        app_file: Path to Streamlit app file
        port: Port to run app on (default: 8501)
        
    Returns:
        Execution result as string
    """
    import subprocess
    import sys
    from pathlib import Path
    
    try:
        # Use Anaconda Python as per project standards
        python_executable = r"C:\App\Anaconda\python.exe"
        if not Path(python_executable).exists():
            python_executable = sys.executable
        
        app_path = Path(app_file)
        if not app_path.exists():
            return f"Streamlit app file not found: {app_file}"
        
        # Start Streamlit app in background
        process = subprocess.Popen(
            [python_executable, "-m", "streamlit", "run", str(app_path), 
             "--server.port", str(port), "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(app_path.parent)
        )
        
        # Wait briefly to check if it starts
        import time
        time.sleep(min(5, 5))  # Wait up to 5 seconds
        
        # Check if process is still running
        if process.poll() is None:
            # App started successfully
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return f"Streamlit app started successfully on port {port}"
        else:
            # App failed to start
            stdout, stderr = process.communicate()
            return f"Failed to start Streamlit app:\n{stderr or stdout or 'Unknown error'}"
    except Exception as e:
        return f"Failed to start Streamlit app:\n{str(e)}"


@tool
def html_test_file(html_file: str) -> str:
    """
    Test HTML file for structure, validity, and basic accessibility.
    
    Args:
        html_file: Path to HTML file
        
    Returns:
        Test results as formatted string
    """
    result = _website_test.test_html_file(html_file)
    
    if result["success"]:
        return f"HTML file validation passed:\n- Has title: {result.get('has_title')}\n- Links checked: {result.get('link_count')}"
    else:
        issues = result.get("issues", [])
        broken_links = result.get("broken_links", [])
        error = result.get("error", "")
        
        output = "HTML file validation failed:\n"
        if issues:
            output += "Issues:\n" + "\n".join(f"- {issue}" for issue in issues) + "\n"
        if broken_links:
            output += f"Broken links: {len(broken_links)}\n"
        if error:
            output += f"Error: {error}\n"
        
        return output


def get_agile_factory_tools() -> list:
    """
    Get all Agile Factory tools as LangChain tools.
    
    Uses LangChain's built-in Python REPL tool and custom website test tools.
    
    Returns:
        List of LangChain tool instances
    """
    tools = []
    
    # Add Python REPL tool if available
    if python_repl_tool is not None:
        tools.append(python_repl_tool)
    else:
        import logging
        logging.warning("langchain_experimental not available - Python REPL tool not included")
    
    # Add custom website test tools
    tools.extend([
        streamlit_validate_app,
        streamlit_run_app,
        html_test_file
    ])
    
    return tools

