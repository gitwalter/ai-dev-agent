"""
Notebook MCP Server Launcher (LangGraph env)
===========================================

Purpose
-------
This module starts the local FastMCP servers required by
`tests/deep_agents/dev_mcp_tools_v1.ipynb` using the **langgraph**
conda environment Python:

- dev_repo  -> http://127.0.0.1:8100/mcp
- dev_search -> http://127.0.0.1:8101/mcp
- dev_docs -> http://127.0.0.1:8104/mcp

It is intentionally lightweight and uses only the Python standard library.

Usage (recommended from the notebook)
-------------------------------------
In a notebook cell:

    %run utils/mcp/fastmcp/start_notebook_mcp_servers.py
    procs = start_required_servers()
    # ... use the MCP tools ...
    stop_servers(procs)

CLI smoke test (safe; starts then stops)
----------------------------------------
From PowerShell:

    C:/App/Anaconda/envs/langgraph/python.exe utils/mcp/fastmcp/start_notebook_mcp_servers.py --smoke-test
"""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


LANGGRAPH_PYTHON = Path(r"C:\App\Anaconda\envs\langgraph\python.exe")


@dataclass(frozen=True)
class ServerSpec:
    """Definition of a FastMCP server required by the notebook."""

    name: str
    script_filename: str
    port: int

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/mcp"


REQUIRED_SERVERS: tuple[ServerSpec, ...] = (
    ServerSpec(name="dev_repo", script_filename="dev_repo_server.py", port=8100),
    ServerSpec(name="dev_search", script_filename="dev_search_server.py", port=8101),
    ServerSpec(name="dev_docs", script_filename="dev_docs_server.py", port=8104),
)


def _find_project_root(start: Optional[Path] = None) -> Path:
    """
    Locate the repository root (directory containing utils/mcp/fastmcp).

    Args:
        start: Optional start directory. Defaults to current working directory.

    Returns:
        Repository root path.

    Raises:
        RuntimeError: If the project root cannot be found.
    """
    cursor = (start or Path.cwd()).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / "utils" / "mcp" / "fastmcp").is_dir():
            return candidate
    raise RuntimeError(f"Could not detect project root from {cursor}")


def _can_connect(host: str, port: int, timeout_sec: float = 0.25) -> bool:
    """Return True if a TCP connection succeeds."""
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except OSError:
        return False


def _wait_port_open(host: str, port: int, timeout_sec: float = 10.0) -> bool:
    """
    Wait until a TCP port becomes reachable.

    Returns:
        True if reachable within timeout, else False.
    """
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if _can_connect(host, port, timeout_sec=0.25):
            return True
        time.sleep(0.2)
    return False


def _pick_python_executable(python_exe: Optional[Path]) -> Path:
    """
    Choose the Python executable to use for starting servers.

    Preference order:
    1) explicitly provided python_exe
    2) LANGGRAPH_PYTHON (absolute path required by project rule)
    3) sys.executable (fallback; warns)
    """
    if python_exe is not None:
        return python_exe

    if LANGGRAPH_PYTHON.exists():
        return LANGGRAPH_PYTHON

    # Fallback for portability if the hardcoded env path isn't present.
    # Keep the message ASCII-only (Windows console safe).
    print(
        "[WARNING] LANGGRAPH_PYTHON not found at expected path. "
        f"Falling back to sys.executable={sys.executable}"
    )
    return Path(sys.executable)


def start_required_servers(
    *,
    project_root: Optional[Path] = None,
    python_exe: Optional[Path] = None,
    transport: str = "streamable-http",
    startup_timeout_sec: float = 12.0,
) -> Dict[str, subprocess.Popen]:
    """
    Start the MCP servers required by `dev_mcp_tools_v1.ipynb`.

    This starts each server as a child process using the specified Python
    executable (preferably `C:\\App\\Anaconda\\envs\\langgraph\\python.exe`).

    Args:
        project_root: Repository root; auto-detected if not provided.
        python_exe: Python executable to use (defaults to LANGGRAPH_PYTHON).
        transport: FastMCP transport ("streamable-http" or "stdio").
        startup_timeout_sec: Timeout per server for port to become reachable.

    Returns:
        Dict mapping server name -> subprocess.Popen object.

    Raises:
        RuntimeError: If a server process exits early or fails to become reachable.
    """
    root = (project_root or _find_project_root()).resolve()
    python_path = _pick_python_executable(python_exe)

    fastmcp_dir = root / "utils" / "mcp" / "fastmcp"
    procs: Dict[str, subprocess.Popen] = {}

    for spec in REQUIRED_SERVERS:
        # If already running, don't start another copy.
        if _can_connect("127.0.0.1", spec.port, timeout_sec=0.25):
            print(f"[INFO] {spec.name} already reachable at {spec.url} (skipping start)")
            continue

        script_path = fastmcp_dir / spec.script_filename
        if not script_path.exists():
            raise RuntimeError(f"Missing server script: {script_path}")

        cmd = [
            str(python_path),
            str(script_path),
            "--transport",
            transport,
            "--port",
            str(spec.port),
        ]

        # Note: use cwd=root so relative paths resolve as expected.
        proc = subprocess.Popen(
            cmd,
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
        procs[spec.name] = proc
        print(f"[INFO] Starting {spec.name} (pid={proc.pid}) on {spec.url}")

        if transport == "streamable-http":
            if not _wait_port_open("127.0.0.1", spec.port, timeout_sec=startup_timeout_sec):
                # Try to include some output for debugging.
                snippet = ""
                try:
                    if proc.stdout:
                        snippet = proc.stdout.read(2000) or ""
                except (OSError, ValueError):
                    snippet = ""
                stop_servers({spec.name: proc}, timeout_sec=3.0)
                raise RuntimeError(
                    f"{spec.name} did not become reachable on port {spec.port} within "
                    f"{startup_timeout_sec}s.\nOutput (first 2000 chars):\n{snippet}"
                )

        # If the process already died, surface its output.
        if proc.poll() is not None:
            output = ""
            try:
                if proc.stdout:
                    output = proc.stdout.read() or ""
            except (OSError, ValueError):
                output = ""
            raise RuntimeError(f"{spec.name} exited early with code {proc.returncode}.\n{output}")

    return procs


def stop_servers(procs: Dict[str, subprocess.Popen], *, timeout_sec: float = 5.0) -> None:
    """
    Stop previously started servers.

    Args:
        procs: Mapping of server name -> subprocess.Popen.
        timeout_sec: Time to wait for graceful termination before killing.
    """
    for name, proc in procs.items():
        if proc.poll() is not None:
            print(f"[INFO] {name} already stopped (exit={proc.returncode})")
            continue

        print(f"[INFO] Stopping {name} (pid={proc.pid}) ...")
        proc.terminate()
        try:
            proc.wait(timeout=timeout_sec)
            print(f"[INFO] {name} stopped (exit={proc.returncode})")
        except subprocess.TimeoutExpired:
            print(f"[WARNING] {name} did not stop in {timeout_sec}s; killing (pid={proc.pid})")
            proc.kill()
            proc.wait(timeout=timeout_sec)
            print(f"[INFO] {name} killed (exit={proc.returncode})")


def _smoke_test() -> int:
    """
    Start servers, verify ports open, then stop them.

    Returns:
        Process exit code (0=success).
    """
    procs: Dict[str, subprocess.Popen] = {}
    try:
        procs = start_required_servers()
        print("[OK] All required servers started (or were already running).")
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        print(f"[ERROR] Smoke test failed: {e}")
        return 1
    finally:
        if procs:
            stop_servers(procs)


def _main() -> int:
    parser = argparse.ArgumentParser(description="Start MCP servers required by dev_mcp_tools_v1.ipynb")
    parser.add_argument("--smoke-test", action="store_true", help="Start then stop servers (safe).")
    args = parser.parse_args()

    if args.smoke_test:
        return _smoke_test()

    print("[INFO] Loaded MCP notebook launcher.")
    print("[INFO] Call: procs = start_required_servers()")
    print("[INFO] Then: stop_servers(procs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

