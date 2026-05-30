"""
n8n error abstraction layer (INFRA-05).

Converts technical backend/n8n errors into soft, owner-facing messages that
inform and suggest a likely fix (D-11). Owner-facing strings NEVER contain
stack traces, exception class names, or raw API payloads (D-09/D-10).
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorClass(str, Enum):
    """Owner-actionable classification of a failure."""

    CREDENTIAL_EXPIRED = "credential_expired"
    CREDENTIAL_REVOKED = "credential_revoked"
    INTEGRATION_NOT_CONNECTED = "integration_not_connected"
    N8N_UNREACHABLE = "n8n_unreachable"
    WORKFLOW_NOT_FOUND = "workflow_not_found"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


# Ordered (substring, ErrorClass) — first match wins, so more specific /
# higher-priority patterns must come first (e.g. "revoked" before "expired").
_ERROR_PATTERNS: list[tuple[str, ErrorClass]] = [
    ("revoked", ErrorClass.CREDENTIAL_REVOKED),
    ("invalid_grant", ErrorClass.CREDENTIAL_EXPIRED),
    ("expired", ErrorClass.CREDENTIAL_EXPIRED),
    ("credential not found", ErrorClass.INTEGRATION_NOT_CONNECTED),
    ("no credential", ErrorClass.INTEGRATION_NOT_CONNECTED),
    ("not connected", ErrorClass.INTEGRATION_NOT_CONNECTED),
    ("econnrefused", ErrorClass.N8N_UNREACHABLE),
    ("connection refused", ErrorClass.N8N_UNREACHABLE),
    ("connection error", ErrorClass.N8N_UNREACHABLE),
    ("timed out", ErrorClass.N8N_UNREACHABLE),
    ("unreachable", ErrorClass.N8N_UNREACHABLE),
    ("workflow not found", ErrorClass.WORKFLOW_NOT_FOUND),
    ("no workflow", ErrorClass.WORKFLOW_NOT_FOUND),
    ("429", ErrorClass.RATE_LIMITED),
    ("too many requests", ErrorClass.RATE_LIMITED),
    ("rate limit", ErrorClass.RATE_LIMITED),
]


# Owner-friendly templates. `{integration}` is filled with a human label.
# Every message informs + suggests a likely fix (D-11) and stays calm (D-09).
_SOFT_MESSAGES: dict[ErrorClass, str] = {
    ErrorClass.CREDENTIAL_EXPIRED: (
        "Your {integration} connection may have expired. "
        "Would you like to reconnect {integration}?"
    ),
    ErrorClass.CREDENTIAL_REVOKED: (
        "Your {integration} connection was disconnected. "
        "Please reconnect {integration} and I'll try again."
    ),
    ErrorClass.INTEGRATION_NOT_CONNECTED: (
        "It looks like {integration} isn't connected yet. "
        "Connect it and I'll be able to do this."
    ),
    ErrorClass.N8N_UNREACHABLE: (
        "The automation engine isn't responding right now. "
        "I'll try again shortly — nothing was lost."
    ),
    ErrorClass.WORKFLOW_NOT_FOUND: (
        "I couldn't find that automation. It may not be set up yet — "
        "I've noted it so we can add it."
    ),
    ErrorClass.RATE_LIMITED: (
        "We're being rate-limited at the moment. "
        "I'll wait a beat and try again."
    ),
    ErrorClass.UNKNOWN: (
        "Something went wrong, but I've noted it. "
        "You can try again in a little while."
    ),
}


def _error_text(error_data: dict[str, Any]) -> str:
    """Flatten an error payload into a lowercase searchable string."""
    parts: list[str] = []
    for value in error_data.values():
        parts.append(str(value))
    # Fall back to the whole dict repr so nested shapes are still searchable.
    parts.append(str(error_data))
    return " ".join(parts).lower()


def classify_error(error_data: dict[str, Any]) -> ErrorClass:
    """Map a raw error payload to an owner-actionable ErrorClass."""
    text = _error_text(error_data)
    for needle, error_class in _ERROR_PATTERNS:
        if needle in text:
            return error_class
    return ErrorClass.UNKNOWN


def _integration_label(integration: str) -> str:
    cleaned = (integration or "").strip()
    if not cleaned:
        return "that service"
    return cleaned.capitalize()


def soft_error_message(
    error_class: ErrorClass,
    intent: str = "",
    integration: str = "",
) -> str:
    """
    Return a calm, plain-language message for the owner.

    Never includes stack traces or exception text. `intent` is accepted for
    future enrichment and call-site symmetry; the message stays generic so it
    is safe to surface directly in the AI Guide.
    """
    template = _SOFT_MESSAGES.get(error_class, _SOFT_MESSAGES[ErrorClass.UNKNOWN])
    return template.format(integration=_integration_label(integration))
