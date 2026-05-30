"""
n8n workflow template skeletons (D-01, D-03).

Templates are version-controlled JSON skeletons stored in `templates/`. The
brain owns this small starter catalog. Intent → skeleton matching uses keyword
overlap as a fast pre-filter; the executor then fills the skeleton's parameters
via the LLM dispatcher (the hybrid approach in D-01).
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_WORD_RE = re.compile(r"[a-z0-9]+")


def load_all_templates() -> list[dict[str, Any]]:
    """Load every template skeleton from the templates directory."""
    templates: list[dict[str, Any]] = []
    if not _TEMPLATES_DIR.exists():
        return templates
    for path in sorted(_TEMPLATES_DIR.glob("*.json")):
        try:
            templates.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            logger.warning("Skipping unreadable template: %s", path.name)
    return templates


def match_template(intent: str) -> dict[str, Any] | None:
    """Return the best-matching skeleton by keyword overlap, or None."""
    tokens = set(_WORD_RE.findall(intent.lower()))
    if not tokens:
        return None

    best: dict[str, Any] | None = None
    best_score = 0
    for template in load_all_templates():
        keywords = template.get("keywords", [])
        score = 0
        for kw in keywords:
            kw_tokens = set(_WORD_RE.findall(kw.lower()))
            if kw_tokens and kw_tokens.issubset(tokens):
                score += 1
        if score > best_score:
            best_score = score
            best = template
    return best if best_score > 0 else None


def fill_parameters(skeleton: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Merge explicit params over the skeleton's schema defaults."""
    schema = skeleton.get("parameter_schema", {})
    result: dict[str, Any] = {}
    for key, spec in schema.items():
        if isinstance(spec, dict) and "default" in spec:
            result[key] = spec["default"]
    result.update(params or {})
    return result
