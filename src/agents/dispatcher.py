"""
AI agent dispatcher.

Sends a prompt (with optional context) to a configured LLM and returns the response.
Supports Gemini. Provider is selected by AGENT_PROVIDER env var.

Environment variables required:
    AGENT_PROVIDER      gemini  (default: gemini)
    GEMINI_API_KEY      (when AGENT_PROVIDER=gemini)
    GEMINI_MODEL        (optional, default: gemini-2.0-flash)

Usage:
    from src.agents.dispatcher import run_agent

    reply = run_agent(
        task="Summarise the following email",
        context="From: boss@example.com\\nSubject: Q1 Report\\n...",
    )
"""

import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

PROVIDER = os.environ.get("AGENT_PROVIDER", "gemini").lower()


def run_agent(task: str, context: str = "", system: str = "") -> str:
    """
    Run an AI agent with a task description and optional context.

    Args:
        task:    The instruction or question for the agent.
        context: Background text (e.g. email body, Notion page content) to reason over.
        system:  Custom system prompt. Defaults to the brain's standard system prompt.

    Returns:
        The agent's response as a plain string.
    """
    prompt = _build_prompt(task, context)
    sys_prompt = system or _default_system_prompt()

    if PROVIDER != "gemini":
        raise EnvironmentError("AGENT_PROVIDER must be set to 'gemini'.")
    return _run_gemini(sys_prompt, prompt)


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

def _run_gemini(system: str, prompt: str) -> str:
    import httpx  # type: ignore

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set.")

    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    payload = {
        "systemInstruction": {
            "parts": [{"text": system}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
    }

    response = httpx.post(url, params={"key": api_key}, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")
    parts = candidates[0].get("content", {}).get("parts", [])
    result = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
    logger.info("Gemini agent responded (%d chars).", len(result))
    return result

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_prompt(task: str, context: str) -> str:
    if context:
        return f"Context:\n{context}\n\nTask:\n{task}"
    return task


def _default_system_prompt() -> str:
    return (
        "You are the brain of a personal command center. "
        "You help the owner manage tasks, summarise information, and make decisions. "
        "Be concise, practical, and clear. "
        "Format responses for operational clarity (short paragraphs, no markdown tables)."
    )
