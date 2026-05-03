"""
Autopilot tool registry.

Tools are plain Python functions registered by name. The loop executor
receives a tool name + args dict, looks up the callable, and returns
the result as a string observation.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

ToolFn = Callable[..., str]


class ToolRegistry:
    """Central registry for autopilot tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}
        self._register_defaults()

    def register(self, name: str, fn: ToolFn) -> None:
        self._tools[name] = fn

    def get(self, name: str) -> ToolFn | None:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def execute(self, name: str, args: dict[str, Any]) -> str:
        fn = self.get(name)
        if fn is None:
            return f"Error: unknown tool '{name}'. Available: {', '.join(self.list_tools())}"
        try:
            result = fn(**args)
            return str(result)
        except Exception as e:
            logger.exception("Tool '%s' failed with args %s", name, args)
            return f"Error executing tool '{name}': {type(e).__name__}: {e}"

    def _register_defaults(self) -> None:
        self.register("read", _tool_read)
        self.register("bash", _tool_bash)
        self.register("gmail_read", _tool_gmail_read)
        self.register("library_index", _tool_library_index)


def _tool_read(path: str, offset: int = 0, limit: int = 200) -> str:
    target = Path(path).resolve()
    repo_root = Path.cwd().resolve()
    # Disallow reading outside repo for safety
    if repo_root not in target.parents and target != repo_root:
        return f"Error: path '{path}' is outside the repository sandbox."
    if not target.exists():
        return f"Error: file not found: {path}"
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
        selected = lines[offset : offset + limit]
        header = f"--- {path} (lines {offset+1}-{offset+len(selected)}) ---\n"
        return header + "\n".join(selected)
    except Exception as e:
        return f"Error reading {path}: {e}"


def _tool_bash(command: str, timeout: int = 30) -> str:
    """Run a shell command in the repo root with a timeout."""
    logger.info("[bash] %s", command)
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd(),
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            output += f"\n[exit code {result.returncode}]\n{result.stderr.strip()}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def _tool_gmail_read(query: str = "", limit: int = 5) -> str:
    try:
        from src.integrations.gmail import client as gmail

        if query:
            return gmail.search(query, limit=limit)
        return gmail.inbox_summary(limit=limit)
    except EnvironmentError as e:
        return f"Gmail not configured: {e}"
    except Exception as e:
        return f"Error reading Gmail: {type(e).__name__}: {e}"


def _tool_library_index(rebuild: bool = True) -> str:
    try:
        from src.core.libraries import _build_library_index

        if rebuild:
            _build_library_index()
        return "Library index rebuilt."
    except Exception as e:
        return f"Error rebuilding library index: {type(e).__name__}: {e}"
