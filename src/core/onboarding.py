"""
LLM-based profile parsing for Signal onboarding.

Uses run_agent() to parse free-text identity descriptions into structured profiles.
Follows the same pattern as intent_parser.py.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)

_PROFILE_SYSTEM_PROMPT = """You are a profile parser for a personal command center.
Given the owner's description of their work and pain points, extract a structured profile.

Respond with valid JSON only. No markdown, no explanations, no code blocks.

Format:
{
  "role": "short description of what they do",
  "pain_points": ["pain point 1", "pain point 2"],
  "suggested_apps": ["gmail", "youtube"],
  "context_templates": ["template description 1"],
  "needs_followup": false,
  "followup_question": ""
}

Rules:
- suggested_apps must be from: gmail, youtube, notion, gdrive, github, telegram, discord
- needs_followup: true ONLY if the input is genuinely vague (e.g., "I work in tech" -- no detail about apps or pain points)
- followup_question: a natural, conversational follow-up if needs_followup is true. Not clinical.
- Keep role to one sentence
- Max 3 pain points, max 3 suggested_apps
- If the user provides enough detail (mentions at least one app or pain point), set needs_followup to false
"""


def parse_identity(text: str) -> dict[str, Any]:
    """Parse free text into a structured profile using LLM.

    Args:
        text: The user's free-text identity description.

    Returns:
        A dict with keys: role, pain_points, suggested_apps, context_templates,
        needs_followup, followup_question. On failure, returns a graceful fallback
        with needs_followup=True.
    """
    try:
        response = run_agent(
            task=f"Parse this identity description: {text}",
            system=_PROFILE_SYSTEM_PROMPT,
        )

        # Strip markdown code fences if LLM wrapped JSON
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        parsed = json.loads(cleaned)

        # Validate and clamp fields
        result = {
            "role": str(parsed.get("role", "")),
            "pain_points": list(parsed.get("pain_points", []))[:3],
            "suggested_apps": list(parsed.get("suggested_apps", []))[:3],
            "context_templates": list(parsed.get("context_templates", [])),
            "needs_followup": bool(parsed.get("needs_followup", False)),
            "followup_question": str(parsed.get("followup_question", "")),
        }
        logger.info("Parsed identity: role=%s, apps=%s", result["role"], result["suggested_apps"])
        return result

    except Exception:
        logger.warning("Identity parser failed", exc_info=True)
        return {
            "role": "",
            "pain_points": [],
            "suggested_apps": [],
            "context_templates": [],
            "needs_followup": True,
            "followup_question": "Could you tell me a bit more about what you do and which apps you use most?",
        }
