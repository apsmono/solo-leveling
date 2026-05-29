"""
Autopilot planner — break a high-level goal into executable steps.

For Phase 1 (MVP), the planner is a simple prompt-based JSON generator.
Future phases can use more sophisticated planning with Kimi/Claude Code.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)

_PLANNER_SYSTEM_PROMPT = (
    "You are an autopilot planner for a personal command center. "
    "Your job is to break a high-level goal into a short sequence of tool calls. "
    "You must respond with ONLY a JSON object in this exact format:\n"
    '{"steps": [{"tool": "<tool_name>", "args": {<arg_dict>}, "reason": "<why>"}]}\n'
    "Available tools and their args:\n"
    "- read: {path: string, offset?: int, limit?: int}\n"
    "- bash: {command: string, timeout?: int}\n"
    "- write: {path: string, content: string, mode?: 'write' | 'append'}\n"
    "- claude_code: {prompt: string, timeout?: int}\n"
    "- gmail_read: {query?: string, limit?: int}\n"
    "- library_index: {rebuild?: bool}\n"
    "Rules:\n"
    "1. Use the minimum number of steps to achieve the goal.\n"
    "2. Each step must use one of the available tools.\n"
    "3. Be specific with file paths and commands.\n"
    "4. Do not include markdown formatting — only raw JSON."
)


def plan_steps(goal: str, context: str = "") -> list[dict[str, Any]]:
    """
    Given a goal, return a list of step dicts.

    Each step dict has keys: tool, args, reason.
    """
    task = f"Goal: {goal}\n"
    if context:
        task += f"Context:\n{context}\n"
    task += "\nProduce the step plan as JSON."

    try:
        raw = run_agent(task=task, system=_PLANNER_SYSTEM_PROMPT)
    except Exception as e:
        logger.exception("Planner agent failed")
        return []

    # Extract JSON from the response (handle potential markdown fences)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("\n", 1)[0]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        steps = parsed.get("steps", [])
        if not isinstance(steps, list):
            logger.warning("Planner returned non-list steps: %s", type(steps))
            return []
        # Basic validation
        valid_steps = []
        for step in steps:
            if "tool" in step and "args" in step:
                valid_steps.append(step)
            else:
                logger.warning("Skipping malformed step: %s", step)
        logger.info("Planner produced %d steps for goal: %s", len(valid_steps), goal)
        return valid_steps
    except json.JSONDecodeError:
        logger.warning("Planner returned invalid JSON:\n%s", raw)
        return []
