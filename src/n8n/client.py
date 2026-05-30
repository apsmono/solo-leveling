"""n8n Public REST API client.

Requires N8N_BASE_URL and N8N_API_KEY environment variables.

Thin httpx client following the src/integrations/github/client.py pattern:
an env-gated `_request` helper, typed response dicts, and a lightweight
`health_check`. Authentication uses the `X-N8N-API-KEY` header.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.core.config import N8N_BASE_URL, N8N_API_KEY

logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    return {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json",
    }


def _request(
    method: str,
    path: str,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute an authenticated n8n API request against the /api/v1 surface."""
    if not N8N_API_KEY:
        raise EnvironmentError("N8N_API_KEY is not set. Add it to your .env file.")

    url = f"{N8N_BASE_URL}/api/v1{path}"
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method, url, headers=_headers(), json=json, params=params
            )
            response.raise_for_status()
            if not response.content:
                return {}
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("n8n API error: %s %s — %s", method, path, e.response.text)
        raise
    except Exception:
        logger.exception("n8n API request failed: %s %s", method, path)
        raise


# ---------------------------------------------------------------------------
# Workflows / executions
# ---------------------------------------------------------------------------

def trigger_workflow(
    workflow_id: int | str, data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Trigger a workflow run, passing optional input data."""
    return _request("POST", f"/workflows/{workflow_id}/run", json={"data": data or {}})


def get_execution(execution_id: int | str) -> dict[str, Any]:
    """Fetch a single execution by ID."""
    return _request("GET", f"/executions/{execution_id}")


def list_executions(
    workflow_id: int | str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List executions, optionally filtered by workflow and status."""
    params: dict[str, Any] = {"limit": limit}
    if workflow_id is not None:
        params["workflowId"] = workflow_id
    if status is not None:
        params["status"] = status
    result = _request("GET", "/executions", params=params)
    return result.get("data", [])


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def create_credential(
    name: str, cred_type: str, data: dict[str, Any]
) -> dict[str, Any]:
    """Create an n8n credential. n8n encrypts `data` server-side at rest."""
    return _request(
        "POST", "/credentials", json={"name": name, "type": cred_type, "data": data}
    )


def update_credential(
    cred_id: int | str, name: str, cred_type: str, data: dict[str, Any]
) -> dict[str, Any]:
    """Update an existing n8n credential by ID."""
    return _request(
        "PUT",
        f"/credentials/{cred_id}",
        json={"name": name, "type": cred_type, "data": data},
    )


def delete_credential(cred_id: int | str) -> dict[str, Any]:
    """Delete an n8n credential by ID."""
    return _request("DELETE", f"/credentials/{cred_id}")


def list_credentials() -> list[dict[str, Any]]:
    """List all credentials known to n8n."""
    result = _request("GET", "/credentials")
    return result.get("data", [])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def health_check() -> dict[str, Any]:
    """Return a lightweight health check result against the live n8n instance."""
    if not N8N_API_KEY:
        return {"ok": False, "error": "N8N_API_KEY not configured"}
    try:
        _request("GET", "/workflows", params={"limit": 1})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
