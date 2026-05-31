"""
Profile JSON persistence for Signal onboarding.

Stores profile data in data/profile.json following the brain's local-first pattern.
Same approach as scheduler.py and reminders.py.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PROFILE_PATH = Path("data/profile.json")


def load_profile() -> dict[str, Any] | None:
    """Load profile from JSON file. Returns None if file doesn't exist."""
    if not _PROFILE_PATH.exists():
        return None
    try:
        return json.loads(_PROFILE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to read profile from %s", _PROFILE_PATH)
        return None


def save_profile(profile: dict[str, Any]) -> None:
    """Save profile to JSON file."""
    _PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PROFILE_PATH.write_text(json.dumps(profile, indent=2))
    logger.info("Profile saved to %s", _PROFILE_PATH)


def load_onboarding_step() -> int:
    """Return the last completed onboarding step (1-3). Defaults to 1."""
    profile = load_profile()
    if not profile:
        return 1
    return profile.get("onboarding_step", 1)


def save_onboarding_step(step: int) -> None:
    """Persist the current onboarding step."""
    profile = load_profile() or {}
    profile["onboarding_step"] = step
    save_profile(profile)
