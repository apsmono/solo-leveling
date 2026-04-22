"""
Gmail integration client.

Read-only access to the Gmail inbox: list messages, read content,
search by query, and produce a plain-text summary of recent unread mail.

Write access (drafts, send) is intentionally excluded from this client.
Add it only when explicitly required and log the decision in docs/decisions/.

Environment variables required:
    GMAIL_CREDENTIALS_PATH   — path to OAuth2 credentials JSON
                               (service accounts do not work for Gmail; OAuth2 required)
    GOOGLE_CREDENTIALS_PATH  — legacy fallback path

Usage:
    from src.integrations.gmail.client import list_unread, get_message, search_messages
"""

from __future__ import annotations

import os
import base64
import logging
from email import message_from_bytes
from typing import Any

from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from google.auth.transport.requests import Request  # type: ignore
from googleapiclient.discovery import build  # type: ignore

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
_TOKEN_PATH = os.environ.get("GMAIL_TOKEN_PATH", ".gmail_token.json")


def _service():
    """Build and return an authenticated Gmail API service using OAuth2."""
    creds: Credentials | None = None

    if os.path.exists(_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_path = (
                os.environ.get("GMAIL_CREDENTIALS_PATH")
                or os.environ.get("GOOGLE_CREDENTIALS_PATH")
            )
            if not creds_path:
                raise EnvironmentError(
                    "GMAIL_CREDENTIALS_PATH is not set. "
                    "Download OAuth2 credentials from Google Cloud Console and set the path in .env. "
                    "GOOGLE_CREDENTIALS_PATH is still supported as a legacy fallback."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save refreshed token for next run
        with open(_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_unread(limit: int = 5) -> list[dict[str, Any]]:
    """
    Return up to `limit` unread messages as simplified dicts:
    {id, subject, sender, snippet, date}.
    """
    return search_messages(query="is:unread", limit=limit)


def search_messages(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Search the inbox using a Gmail query string (e.g. 'is:unread from:boss@example.com').
    Returns simplified message summaries: {id, subject, sender, snippet, date}.
    """
    service = _service()
    result = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
    messages = result.get("messages", [])
    summaries = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        summaries.append({
            "id": msg["id"],
            "subject": headers.get("Subject", "(no subject)"),
            "sender": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": detail.get("snippet", ""),
        })
    logger.info("Gmail search '%s' returned %d messages.", query, len(summaries))
    return summaries


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_message(message_id: str) -> dict[str, Any]:
    """
    Return the full decoded content of a message.
    Returns {id, subject, sender, date, body}.
    """
    service = _service()
    detail = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
    body = _decode_body(detail.get("payload", {}))
    return {
        "id": message_id,
        "subject": headers.get("Subject", "(no subject)"),
        "sender": headers.get("From", ""),
        "date": headers.get("Date", ""),
        "body": body,
    }


# ---------------------------------------------------------------------------
# Summary helper (used by the router)
# ---------------------------------------------------------------------------

def inbox_summary(limit: int = 5) -> str:
    """
    Return a plain-text summary of the most recent unread emails.
    Suitable for sending back as a WhatsApp message.
    """
    messages = list_unread(limit=limit)
    if not messages:
        return "No unread emails."

    lines = [f"You have {len(messages)} unread email(s):\n"]
    for i, msg in enumerate(messages, 1):
        lines.append(f"{i}. {msg['subject']}")
        lines.append(f"   From: {msg['sender']}")
        lines.append(f"   {msg['snippet'][:100]}...\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_body(payload: dict) -> str:
    """Recursively decode the body of a Gmail message payload."""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")

    if mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            text = _decode_body(part)
            if text:
                return text

    return ""
