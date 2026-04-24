"""
AI agent dispatcher.

Sends a prompt (with optional context) to a configured LLM and returns the response.
Supports Gemini, OpenAI, and Anthropic. Provider is selected by AGENT_PROVIDER env var.

Environment variables required:
    AGENT_PROVIDER      gemini | openai | anthropic  (default: gemini)
    GEMINI_API_KEY      (when AGENT_PROVIDER=gemini)
    GEMINI_MODEL        (optional, default: gemini-2.0-flash)
    OPENAI_API_KEY      (when AGENT_PROVIDER=openai)
    OPENAI_MODEL        (optional, default: gpt-4o)
    ANTHROPIC_API_KEY   (when AGENT_PROVIDER=anthropic)
    ANTHROPIC_MODEL     (optional, default: claude-3-5-sonnet-20241022)

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

    if PROVIDER == "gemini":
        return _run_gemini(sys_prompt, prompt)
    if PROVIDER == "anthropic":
        return _run_anthropic(sys_prompt, prompt)
    return _run_openai(sys_prompt, prompt)


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

def _run_openai(system: str, prompt: str) -> str:
    import openai  # type: ignore

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    result = response.choices[0].message.content or ""
    logger.info("OpenAI agent responded (%d chars).", len(result))
    return result.strip()


def _run_anthropic(system: str, prompt: str) -> str:
    import anthropic  # type: ignore

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set.")

    model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    result = message.content[0].text if message.content else ""
    logger.info("Anthropic agent responded (%d chars).", len(result))
    return result.strip()


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
