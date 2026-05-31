"""
LLM-based profile parsing and digest generation for Signal onboarding.

Uses run_agent() to parse free-text identity descriptions into structured profiles
and to generate 24-hour digests from connected data sources.
Follows the same pattern as intent_parser.py.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)

_DIGEST_SYSTEM_PROMPT = """You are a personal digest generator for a command center.
Given the owner's profile and recent data from their connected apps, summarize the last 24 hours
into exactly 3 concise, actionable bullet points.

Respond with valid JSON only. No markdown, no explanations, no code blocks.

Format:
{
  "bullets": ["bullet 1", "bullet 2", "bullet 3"]
}

Rules:
- Exactly 3 bullets, no more, no fewer
- Each bullet is one sentence, under 100 characters
- Be specific to the data provided; do not invent details
- Prioritize actionable items (emails needing reply, deadlines, important updates)
"""

_COLD_START_PREVIEW_PROMPT = """You are a capability preview generator for a personal command center.
Given the owner's profile (role and pain points), generate 3 example bullets showing what Signal
will track and surface for them once their apps are connected. Be specific to their role.

Respond with valid JSON only. No markdown, no explanations, no code blocks.

Format:
{
  "bullets": ["bullet 1", "bullet 2", "bullet 3"]
}

Rules:
- Exactly 3 bullets, no more, no fewer
- Each bullet describes a concrete thing Signal will monitor or surface for this person
- Be specific to their stated role and pain points
- Use future tense: "Signal will..." or "You'll see..."
"""

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


def generate_digest(
    profile: dict[str, Any],
    connected_data: list[dict[str, Any]],
) -> list[str]:
    """Generate a 3-bullet digest from connected source data.

    If connected_data is empty, returns a cold-start capability preview instead.
    Always returns exactly 3 bullet strings.

    Args:
        profile: The owner's profile dict (role, pain_points, suggested_apps, …).
        connected_data: List of data dicts from connected integrations (may be empty).

    Returns:
        A list of exactly 3 bullet strings.
    """
    _FALLBACK = [
        "Your streams are being set up.",
        "Data will appear here once connected sources sync.",
        "Check back in a few minutes.",
    ]

    if not connected_data:
        return _cold_start_preview(profile)

    try:
        data_context = json.dumps(connected_data, ensure_ascii=False)[:4000]
        profile_context = f"Role: {profile.get('role', '')}\nPain points: {', '.join(profile.get('pain_points', []))}"
        response = run_agent(
            task=f"Generate a 24-hour digest from this data:\n{data_context}",
            context=profile_context,
            system=_DIGEST_SYSTEM_PROMPT,
        )

        cleaned = _strip_fences(response)
        parsed = json.loads(cleaned)
        bullets = list(parsed.get("bullets", []))[:3]

        # Ensure exactly 3 bullets; pad with fallback if LLM returned fewer
        while len(bullets) < 3:
            bullets.append(_FALLBACK[len(bullets)])

        logger.info("Digest generated: %d bullets", len(bullets))
        return bullets[:3]

    except Exception:
        logger.warning("Digest generation failed", exc_info=True)
        return _FALLBACK


def _cold_start_preview(profile: dict[str, Any]) -> list[str]:
    """Generate capability preview bullets for a cold-start (no connected apps) state.

    Uses the owner's role and pain points to show what Signal will do for them.

    Args:
        profile: The owner's profile dict.

    Returns:
        A list of exactly 3 preview bullet strings.
    """
    _FALLBACK = [
        "Signal will compress your streams into daily insights.",
        "Connected apps will be monitored for important updates.",
        "Your personalized digest will appear here.",
    ]

    try:
        profile_context = (
            f"Role: {profile.get('role', 'professional')}\n"
            f"Pain points: {', '.join(profile.get('pain_points', []))}\n"
            f"Suggested apps: {', '.join(profile.get('suggested_apps', []))}"
        )
        response = run_agent(
            task="Generate 3 capability preview bullets for this owner's profile.",
            context=profile_context,
            system=_COLD_START_PREVIEW_PROMPT,
        )

        cleaned = _strip_fences(response)
        parsed = json.loads(cleaned)
        bullets = list(parsed.get("bullets", []))[:3]

        while len(bullets) < 3:
            bullets.append(_FALLBACK[len(bullets)])

        logger.info("Cold-start preview generated: %d bullets", len(bullets))
        return bullets[:3]

    except Exception:
        logger.warning("Cold-start preview generation failed", exc_info=True)
        return _FALLBACK


def _gmail_fetcher() -> list[Any]:
    """Fetch recent Gmail messages using the file-based credentials client."""
    from src.integrations.gmail.client import list_messages  # type: ignore[import]
    return list_messages(max_results=5)


# Registry mapping app names to zero-arg fetcher callables.
# Adding a new integration is a one-line entry here — no structural changes needed.
_SOURCE_FETCHERS: dict[str, Callable[[], list[Any]]] = {
    "gmail": _gmail_fetcher,
}


def _query_connected_sources(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch recent data from connected integrations using a fetcher registry.

    Checks profile['connected_apps'] and dispatches to registered fetchers for each app.
    Apps with no registered fetcher are skipped (logged at debug).
    Returns an empty list when nothing is connected or all fetches fail.

    The registry-based dispatch makes adding future integrations (youtube, etc.)
    a one-line entry in _SOURCE_FETCHERS rather than a structural change.

    Args:
        profile: The owner's profile dict (must contain 'connected_apps' list).

    Returns:
        A list of data dicts with keys 'app' and 'items'. May be empty.
    """
    connected_apps: list[str] = profile.get("connected_apps", [])
    results: list[dict[str, Any]] = []

    for app in connected_apps:
        fetcher = _SOURCE_FETCHERS.get(app)
        if fetcher is None:
            logger.debug("No fetcher registered for app %s; skipping", app)
            continue
        try:
            items = fetcher()
            if items:
                results.append({"app": app, "items": items})
        except Exception:
            logger.debug("Could not fetch data from %s; skipping", app)

    return results


def _strip_fences(text: str) -> str:
    """Remove markdown code fences from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned
