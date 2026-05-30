"""
Credential injection — brain → n8n (N8N-02, D-04/D-05/D-06).

The brain populates n8n's own credential store via the n8n API so workflows
reference credentials by ID and the owner never handles raw keys/webhooks.
Tokens are sourced from the brain's existing integration clients (D-06) and
synced at connect time / before each run (D-05). n8n encrypts the data at rest.
"""

from __future__ import annotations

import logging
from typing import Any

from src.n8n import client as n8n_client

logger = logging.getLogger(__name__)

# Brain integration name → n8n credential type name.
_CREDENTIAL_TYPE_MAP: dict[str, str] = {
    "gmail": "gmailOAuth2",
    "gdrive": "googleDriveOAuth2Api",
    "github": "githubApi",
    "notion": "notionApi",
    "telegram": "telegramApi",
    "discord": "discordBotApi",
}


def _map_token_to_n8n_credential(
    integration: str, token_data: dict[str, Any]
) -> dict[str, Any]:
    """Map a brain token payload to the n8n credential `data` schema."""
    if integration in ("gmail", "gdrive"):
        access = token_data.get("access_token") or token_data.get("token")
        return {
            "clientId": token_data.get("client_id", ""),
            "clientSecret": token_data.get("client_secret", ""),
            "oauthTokenData": {
                "access_token": access,
                "refresh_token": token_data.get("refresh_token", ""),
                "scope": token_data.get("scope", ""),
                "token_type": token_data.get("token_type", "Bearer"),
            },
        }
    if integration == "github":
        return {"accessToken": token_data.get("access_token") or token_data.get("token", "")}
    if integration == "notion":
        return {"apiKey": token_data.get("api_key") or token_data.get("token", "")}
    if integration == "telegram":
        return {"accessToken": token_data.get("access_token") or token_data.get("token", "")}
    if integration == "discord":
        return {"token": token_data.get("token", "")}
    raise ValueError(f"Unknown integration: {integration!r}")


def _find_credential_by_name(name: str) -> dict[str, Any] | None:
    """Return an existing n8n credential matching `name`, or None."""
    for cred in n8n_client.list_credentials():
        if cred.get("name") == name:
            return cred
    return None


def sync_credential(
    integration: str, token_data: dict[str, Any], owner_id: str = "default-owner"
) -> int:
    """
    Provision (or upsert) the owner's credential into n8n and return its ID.

    Per D-04 the brain populates n8n's credential store; per D-05 this is called
    at connect time and before each run so n8n already holds a valid credential.
    """
    if integration not in _CREDENTIAL_TYPE_MAP:
        raise ValueError(f"Unknown integration: {integration!r}")

    cred_type = _CREDENTIAL_TYPE_MAP[integration]
    name = f"signal-{owner_id}-{integration}"
    data = _map_token_to_n8n_credential(integration, token_data)

    existing = _find_credential_by_name(name)
    if existing:
        n8n_client.update_credential(existing["id"], name, cred_type, data)
        return existing["id"]

    result = n8n_client.create_credential(name, cred_type, data)
    return result.get("id")
