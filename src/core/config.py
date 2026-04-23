"""
Environment variable loader for the brain core.

All secrets must be set in the environment (or a .env file loaded by the caller).
This module reads them and exposes typed constants for use across the codebase.

Never hardcode secrets here or anywhere else in this repository.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_int(key: str, default: int) -> int:
    value = os.environ.get(key)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def require(key: str) -> str:
    """Return the value of an environment variable; raise if missing."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            "Copy .env.example to .env and fill in the value."
        )
    return value


# ---------------------------------------------------------------------------
# WhatsApp
# ---------------------------------------------------------------------------
WHATSAPP_PROVIDER: str = os.environ.get("WHATSAPP_PROVIDER", "meta").lower()
WHATSAPP_OWNER_NUMBER: str = os.environ.get("WHATSAPP_OWNER_NUMBER", "")

# ---------------------------------------------------------------------------
# Meta Cloud API
# ---------------------------------------------------------------------------
META_PHONE_NUMBER_ID: str = os.environ.get("META_PHONE_NUMBER_ID", "")
META_ACCESS_TOKEN: str = os.environ.get("META_ACCESS_TOKEN", "")
META_VERIFY_TOKEN: str = os.environ.get("META_VERIFY_TOKEN", "")

# ---------------------------------------------------------------------------
# Twilio (fallback)
# ---------------------------------------------------------------------------
TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER: str = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")

# ---------------------------------------------------------------------------
# Notifications / scheduler
# ---------------------------------------------------------------------------
REMINDER_STORE_PATH: str = os.environ.get("REMINDER_STORE_PATH", "data/reminders.json")
SCHEDULER_POLL_SECONDS: int = _get_int("SCHEDULER_POLL_SECONDS", 30)
DAILY_GMAIL_DIGEST_ENABLED: bool = _get_bool("DAILY_GMAIL_DIGEST_ENABLED", False)
DAILY_GMAIL_DIGEST_HOUR: int = _get_int("DAILY_GMAIL_DIGEST_HOUR", 8)
DAILY_GMAIL_DIGEST_MINUTE: int = _get_int("DAILY_GMAIL_DIGEST_MINUTE", 0)
LIBRARY_MAINTENANCE_ENABLED: bool = _get_bool("LIBRARY_MAINTENANCE_ENABLED", False)
LIBRARY_MAINTENANCE_DAY: str = os.environ.get("LIBRARY_MAINTENANCE_DAY", "sun").strip().lower() or "sun"
LIBRARY_MAINTENANCE_HOUR: int = _get_int("LIBRARY_MAINTENANCE_HOUR", 9)
LIBRARY_MAINTENANCE_MINUTE: int = _get_int("LIBRARY_MAINTENANCE_MINUTE", 0)

# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------
NOTION_WORKFLOW_PARENT_ID: str = os.environ.get("NOTION_WORKFLOW_PARENT_ID", "")
