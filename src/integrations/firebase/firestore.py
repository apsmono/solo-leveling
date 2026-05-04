"""Firestore client wrappers for reminders and command logging."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.integrations.firebase.auth import _init_firebase

logger = logging.getLogger(__name__)

_firestore_client: Any | None = None


def _client() -> Any:
    global _firestore_client
    if _firestore_client is None:
        _init_firebase()
        from google.cloud import firestore
        _firestore_client = firestore.client()
    return _firestore_client


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

def create_reminder_doc(message: str, run_at: datetime, source: str = "api") -> str:
    doc_ref = _client().collection("reminders").document()
    doc_ref.set({
        "message": message,
        "run_at": run_at,
        "created_at": datetime.now(),
        "sent_at": None,
        "source": source,
    })
    return doc_ref.id


def list_pending_reminders() -> list[dict[str, Any]]:
    docs = (
        _client()
        .collection("reminders")
        .where("sent_at", "==", None)
        .order_by("run_at")
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def mark_reminder_sent(doc_id: str) -> None:
    _client().collection("reminders").document(doc_id).update({"sent_at": datetime.now()})


def delete_reminder_doc(doc_id: str) -> None:
    """Delete a reminder document by id (dashboard / API cancel)."""
    _client().collection("reminders").document(doc_id).delete()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def log_command(text: str, intent: str, reply: str, source: str = "api") -> None:
    _client().collection("commands").add({
        "text": text,
        "intent": intent,
        "reply": reply,
        "source": source,
        "created_at": datetime.now(),
    })


def list_recent_commands(limit: int = 50) -> list[dict[str, Any]]:
    from google.cloud.firestore import Query
    docs = (
        _client()
        .collection("commands")
        .order_by("created_at", direction=Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]
