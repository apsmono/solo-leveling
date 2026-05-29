"""
Autopilot governor — Responsibility Level (RL) safety gate.

Maps to docs/ai-employer-operating-system.md RL definitions:
- RL1 (Assisted): read-only tools, review required for every step
- RL2 (Independent Task): read + local file writes within scope, log only
- RL3 (Cross-Module Integrator): read + write + git commit, notify after
- RL4 (Lead Executor): cross-service writes, pre-approval queue
- RL5 (Program Lead): destructive ops, always require explicit human approve
"""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import Any

logger = logging.getLogger(__name__)


class ResponsibilityLevel(IntEnum):
    ASSISTED = 1
    INDEPENDENT = 2
    CROSS_MODULE = 3
    LEAD_EXECUTOR = 4
    PROGRAM_LEAD = 5


# Tool name → minimum RL required
_TOOL_RL_REQUIREMENTS: dict[str, ResponsibilityLevel] = {
    "read": ResponsibilityLevel.ASSISTED,
    "bash": ResponsibilityLevel.INDEPENDENT,
    "edit": ResponsibilityLevel.INDEPENDENT,
    "write": ResponsibilityLevel.INDEPENDENT,
    "claude_code": ResponsibilityLevel.CROSS_MODULE,
    "web_search": ResponsibilityLevel.ASSISTED,
    "gmail_read": ResponsibilityLevel.ASSISTED,
    "notion_create": ResponsibilityLevel.CROSS_MODULE,
    "gdrive_create": ResponsibilityLevel.CROSS_MODULE,
    "library_index": ResponsibilityLevel.ASSISTED,
    "git_commit": ResponsibilityLevel.CROSS_MODULE,
    "telegram_notify": ResponsibilityLevel.ASSISTED,
}


class Governor:
    """Intercept tool calls and enforce RL-based safety policies."""

    def __init__(self, current_rl: ResponsibilityLevel) -> None:
        self.current_rl = current_rl

    def can_execute(self, tool_name: str, tool_args: dict[str, Any]) -> tuple[bool, str]:
        """
        Return (allowed, reason).

        If allowed is False, the loop must pause the task and queue an approval request.
        """
        required = _TOOL_RL_REQUIREMENTS.get(tool_name)
        if required is None:
            logger.warning("Unknown tool '%s'; defaulting to require RL5.", tool_name)
            required = ResponsibilityLevel.PROGRAM_LEAD

        if self.current_rl < required:
            return False, (
                f"Tool '{tool_name}' requires RL{required.value} "
                f"but current RL is RL{self.current_rl.value}. "
                f"Approval required."
            )

        # Additional sandboxing for bash
        if tool_name == "bash":
            cmd = tool_args.get("command", "")
            if _is_dangerous_command(cmd):
                return False, f"Bash command blocked by sandbox policy: {cmd}"

        return True, ""


def _is_dangerous_command(command: str) -> bool:
    """Block obviously destructive or exfiltration-prone shell commands."""
    dangerous = [
        "rm -rf /",
        "sudo ",
        "> /dev/",
        "mkfs",
        "dd if=",
        ":(){ :|:",
        "curl >>",
        "wget >>",
    ]
    lower = command.lower()
    return any(d in lower for d in dangerous)
