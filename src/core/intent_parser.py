"""
LLM-driven intent parser for the command router.

Replaces the brittle keyword-based INTENT_MAP with structured LLM classification.
Every interface that calls route_command() (API, Telegram, scheduler) automatically
benefits from LLM intent parsing — no side async variant needed.

Fallback: if the LLM returns malformed JSON or raises an exception, the parser
falls back to the keyword-based _detect_intent() from router.py.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)

# Allowed intents — must stay in sync with router._dispatch handlers
_ALLOWED_INTENTS: set[str] = {
    "library_search",
    "library_capture",
    "library_qa",
    "status",
    "help",
    "park_distraction",
    "unknown",
}

_INTENT_SYSTEM_PROMPT = """You are an intent parser for a personal knowledge system.
Given a user's natural language command, classify it into one of these intents and extract parameters.

Allowed intents:
- library_search: User wants to search their personal knowledge library
- library_capture: User wants to save information to their library
- library_qa: User asks a question that can be answered from library entries
- status: User wants system status or health check
- help: User wants to see available commands
- park_distraction: User has a stray thought they want to save without context switching
- unknown: The command does not match any of the above intents

Respond with valid JSON only. No markdown, no explanations, no code blocks.

Format:
{
  "intent": "library_search",
  "params": {"query": "machine learning papers"},
  "confidence": 0.95
}

Rules:
- "intent" must be one of the allowed values listed above.
- "params" is a flat object with string values (e.g. {"query": "...", "text": "..."}).
- "confidence" is a float between 0.0 and 1.0.
- If unsure, use "unknown" with confidence below 0.5.

Examples:
- "find my notes on python" -> {"intent": "library_search", "params": {"query": "python"}, "confidence": 0.95}
- "save this: machine learning is cool" -> {"intent": "library_capture", "params": {"text": "machine learning is cool"}, "confidence": 0.92}
- "what do I know about docker?" -> {"intent": "library_qa", "params": {"query": "docker"}, "confidence": 0.88}
- "how is the system doing?" -> {"intent": "status", "params": {}, "confidence": 0.90}
- "what can you do?" -> {"intent": "help", "params": {}, "confidence": 0.95}
- "park this thought: buy milk later" -> {"intent": "park_distraction", "params": {"text": "buy milk later"}, "confidence": 0.91}
- "hello" -> {"intent": "unknown", "params": {"text": "hello"}, "confidence": 0.30}
"""


def parse_intent(text: str) -> dict[str, Any]:
    """
    Parse a natural language command into structured intent + params + confidence.

    Uses the LLM (via run_agent) for classification. On any failure (malformed
    JSON, LLM error, invalid intent), falls back to keyword-based detection.

    Args:
        text: The user's raw command string.

    Returns:
        A dict with keys: "intent" (str), "params" (dict), "confidence" (float).
    """
    try:
        response = run_agent(
            task=f"Parse this command: {text}",
            system=_INTENT_SYSTEM_PROMPT,
        )

        # Strip markdown code fences if the LLM wrapped JSON in them
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        parsed = json.loads(cleaned)

        intent = parsed.get("intent", "unknown")
        if intent not in _ALLOWED_INTENTS:
            logger.warning("LLM returned invalid intent '%s'; defaulting to unknown", intent)
            intent = "unknown"

        params = parsed.get("params", {})
        if not isinstance(params, dict):
            params = {"text": text}

        confidence = parsed.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)):
            confidence = 0.5
        confidence = float(confidence)

        logger.info("Parsed intent: %s (confidence=%.2f)", intent, confidence)
        return {
            "intent": intent,
            "params": params,
            "confidence": confidence,
        }

    except Exception:
        logger.warning("Intent parser fallback to keyword map", exc_info=True)
        from src.core.router import _detect_intent

        intent = _detect_intent(text)
        return {"intent": intent, "params": {"text": text}, "confidence": 0.3}
