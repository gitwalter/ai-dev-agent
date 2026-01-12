"""
Development MCP Server: dev_tests (FastMCP)
==========================================

Test execution helpers for development agents.

Transport:
- streamable-http (HTTP) at /mcp

Port:
- 8102

Tools (v1):
- tests.run_pytest (execution; use carefully)

Safety notes:
- This is an execution tool. In agent workflows it should be HITL-gated.
- For notebook/manual testing, this is intentionally exposed so you can validate
  the end-to-end MCP transport without an LLM.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from fastmcp import FastMCP


mcp = FastMCP("dev_tests")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@mcp.tool(name="tests.run_pytest")
def tests_run_pytest(
    target: str = "tests",
    k: str | None = None,
    maxfail: int = 1,
    timeout_sec: int = 300,
) -> dict:
    """
    Run pytest with a limited, safe set of parameters.

    Args:
        target: File/dir/test node id. Defaults to "tests".
        k: Optional -k expression.
        maxfail: Max failures before stopping (1-20).
        timeout_sec: Timeout in seconds (10-1800).
    """
    maxfail = max(1, min(maxfail, 20))
    timeout_sec = max(10, min(timeout_sec, 1800))

    args = [sys.executable, "-m", "pytest", target, f"--maxfail={maxfail}", "-q"]
    if k:
        args.extend(["-k", k])

    try:
        result = subprocess.run(
            args,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(args),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"pytest timed out after {timeout_sec}s"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8102)


