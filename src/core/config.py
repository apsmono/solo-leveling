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
# Firebase
# ---------------------------------------------------------------------------
FIREBASE_CREDENTIALS_PATH: str = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
FIREBASE_CREDENTIALS_JSON: str = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
FIREBASE_PROJECT_ID: str = os.environ.get("FIREBASE_PROJECT_ID", "")
ALLOWED_USER_EMAIL: str = os.environ.get("ALLOWED_USER_EMAIL", "")
USE_FIRESTORE_REMINDERS: bool = _get_bool("USE_FIRESTORE_REMINDERS", False)

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_SECRET: str = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")

# ---------------------------------------------------------------------------
# CORS / Deployment
# ---------------------------------------------------------------------------
FRONTEND_ORIGIN: str = os.environ.get("FRONTEND_ORIGIN", "")

# ---------------------------------------------------------------------------
# GitHub (cross-repo orchestration)
# ---------------------------------------------------------------------------
GITHUB_PAT: str = os.environ.get("GITHUB_PAT", "")

# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------
NOTION_WORKFLOW_PARENT_ID: str = os.environ.get("NOTION_WORKFLOW_PARENT_ID", "")

# ---------------------------------------------------------------------------
# Autopilot
# ---------------------------------------------------------------------------
AUTOPILOT_ENABLED: bool = _get_bool("AUTOPILOT_ENABLED", False)
AUTOPILOT_TICK_SECONDS: int = _get_int("AUTOPILOT_TICK_SECONDS", 60)
AUTOPILOT_RL_LEVEL: int = _get_int("AUTOPILOT_RL_LEVEL", 1)
AUTOPILOT_MAX_STEPS_PER_TASK: int = _get_int("AUTOPILOT_MAX_STEPS_PER_TASK", 50)
AUTOPILOT_TASK_STORE_PATH: str = os.environ.get("AUTOPILOT_TASK_STORE_PATH", "data/autopilot_tasks.json")
AUTOPILOT_STATE_PATH: str = os.environ.get("AUTOPILOT_STATE_PATH", "data/autopilot_state.json")
AUTOPILOT_APPROVALS_PATH: str = os.environ.get("AUTOPILOT_APPROVALS_PATH", "data/autopilot_approvals.json")
