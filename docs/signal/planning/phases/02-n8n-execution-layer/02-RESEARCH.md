# Phase 2: n8n Execution Layer - Research

**Researched:** 2026-05-30
**Domain:** n8n Public REST API, workflow triggering, credential injection, execution status ingestion, error abstraction
**Confidence:** MEDIUM (n8n API endpoints verified via official docs references; credential encryption behavior based on community knowledge — needs live verification)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Hybrid strategy — Gemini dispatcher matches intent to vetted n8n workflow template skeleton, LLM fills parameters. Execution stays bounded to known-good skeletons.
- **D-02:** No template match → soft decline. Log unmet intent. Do NOT silently fall back to full LLM-generated JSON.
- **D-03:** Starter set intentionally small (one read-only, one side-effecting example). N8N-03 expands later.
- **D-04:** Brain populates n8n's own credential store via n8n API; workflows reference credentials by ID. Tokens live encrypted inside n8n.
- **D-05:** Sync at connect time. Re-sync on token refresh. First workflow run is instant — n8n already holds valid credential.
- **D-06:** Reuse existing integration client tokens (gmail, gdrive, github, notion, telegram, discord). No parallel credential store.
- **D-07:** Gate side-effecting actions through existing RL approval gate. Read-only runs execute freely.
- **D-08:** Approval prompts surface inline in AI Guide.
- **D-09:** Silent unless failure or needs owner input. No run-by-run progress noise.
- **D-10:** One automatic retry before surfacing to owner.
- **D-11:** Failure message informs + suggests likely fix (error→cause mapping).

### Claude's Discretion
- Exact n8n trigger/callback transport (sync REST trigger vs async webhook callback)
- Where template skeletons are stored and versioned; intent→skeleton matching mechanism
- RL level mapping for "side-effecting n8n run" within existing governor
- n8n REST auth mechanism (API key vs basic auth) and where base URL/API key live in `.env`
- Token-refresh detection and exact n8n credentials-API calls for create/update
- How to guarantee no partial side-effects on mid-run failure (pragmatic, not hard gate)

### Deferred Ideas (OUT OF SCOPE)
- N8N-03 — catalog of pre-built workflow templates for feed/draft pipelines → Phase 6/7
- Telegram (and other channels) as additional approval surfaces → possible later enhancement
- YOLO / Power Mode (raw n8n JSON editing, BYO keys, custom-JS nodes) → v1.1
- Multi-tenant credential broker / encrypted per-user vault → revisit when going commercial
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| N8N-01 | Brain translates user intent into n8n workflow JSON and triggers it via n8n API | n8n Public REST API `/api/v1/workflows/{id}/run` or webhook POST; hybrid template+LLM approach via dispatcher |
| N8N-02 | Owner's OAuth credentials injected into n8n nodes by backend (owner never handles raw keys) | n8n REST API `POST /api/v1/credentials` with server-side encryption; brain pulls tokens from existing integration clients |
| N8N-04 | n8n execution status and webhook callbacks ingested back into brain | n8n `GET /api/v1/executions/{id}` for polling; webhook callback node for push; FastAPI endpoint to receive |
| INFRA-05 | Error-abstraction layer converts technical backend/n8n errors into soft AI-Guide messages | Error→cause mapping table; retry logic; plain-language message formatter |
</phase_requirements>

---

## Summary

This phase wires the `solo-leveling` brain to n8n as the firm execution engine. The brain becomes the AI/control plane that translates owner intents into n8n workflow executions, injects the owner's OAuth credentials into n8n's credential store so the owner never sees raw keys, ingests execution results back, and wraps all failures in soft, actionable messages.

The n8n Public REST API (v1) provides the necessary endpoints: `POST /api/v1/workflows/{id}/run` for triggering executions, `POST /api/v1/credentials` for provisioning credentials (encryption is server-side — the API consumer sends plaintext, n8n encrypts with `N8N_ENCRYPTION_KEY` before storing), and `GET /api/v1/executions/{id}` for polling execution status. An alternative to polling is embedding a Webhook node at the end of n8n workflows that POSTs results back to a new FastAPI endpoint — this is the recommended approach for N8N-04 as it avoids polling overhead and provides near-real-time status updates.

The credential injection pattern (D-04, D-05) requires the brain to read OAuth tokens from the existing integration clients (`gmail/client.py`, `gdrive/client.py`, `github/client.py`, etc.) and push them into n8n's credential store via `POST /api/v1/credentials`. The key subtlety is that n8n credential types have specific schemas (e.g., `gmailOAuth2` expects `clientId`, `clientSecret`, `oauthTokenData` with `access_token`/`refresh_token`); the brain must map its existing token formats to the n8n credential type schemas. The existing clients use heterogeneous token storage: Gmail uses a JSON token file with `google.oauth2.credentials.Credentials`, GitHub uses a PAT string, Notion uses an API token string, Telegram uses a bot token string.

**Primary recommendation:** Build `solo-leveling/src/integrations/n8n/client.py` following the existing `github/client.py` thin-client pattern (httpx-based, `_request` helper, env-gated). Use n8n API key auth (`X-N8N-API-KEY` header). Store n8n connection config in `.env` as `N8N_BASE_URL` and `N8N_API_KEY`. For execution status, use a hybrid: synchronous polling for short workflows (<30s) and a Webhook callback endpoint for longer ones. Gate side-effecting workflows through the existing RL governor at RL4 level.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Intent → template matching | API / Backend (dispatcher.py) | — | Gemini dispatcher already handles intent; extend to n8n template selection |
| Template skeleton storage | API / Backend (new module) | — | Versioned JSON files in `src/n8n/templates/` — brain owns the catalog |
| n8n workflow triggering | API / Backend (n8n client) | — | REST call to n8n; brain is the orchestrator |
| Credential injection | API / Backend (n8n client) | — | Brain reads existing tokens, pushes to n8n credential store |
| Execution status ingestion | API / Backend (webhook endpoint) | n8n (callback node) | n8n POSTs results to brain's FastAPI endpoint |
| Error abstraction | API / Backend (new module) | — | Translates raw errors to soft messages before AI Guide reply |
| RL approval gate | API / Backend (existing governor) | — | Reuse `governor.py` for side-effecting workflow approval |
| AI Guide approval surface | Frontend / Dashboard (future Phase 3) | — | Approval prompts display in AI Guide panel (Phase 3 delivery) |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `httpx` | (already installed) | HTTP client for n8n REST API calls | Already used by `dispatcher.py`, `github/client.py`; zero new dependency |
| n8n Public REST API v1 | n8n 1.x+ | Workflow CRUD, execution trigger, credential management, execution status | Official API; `/api/v1/` prefix; API key auth via `X-N8N-API-KEY` header [CITED: docs.n8n.io/api/] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pydantic` | (already available via FastAPI) | Template skeleton validation, error message models | Validate workflow JSON structure before sending to n8n |
| `json` (stdlib) | — | Template skeleton file loading, execution log persistence | No new dependency needed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| n8n Public REST API | n8n internal `/rest/` API | Internal API is undocumented, changes without notice; public API is stable and versioned |
| Webhook callback for status | Polling `GET /api/v1/executions` | Polling adds latency and load; webhook is event-driven but requires n8n workflow to include callback node |
| API key auth (`X-N8N-API-KEY`) | Basic auth (`N8N_BASIC_AUTH_USER/PASSWORD`) | API key is the officially recommended auth method; basic auth is for the n8n UI login |
| JSON template files in brain repo | n8n saved workflows | Brain repo templates are version-controlled, reviewable, and portable; n8n saved workflows live in n8n's DB and are harder to version |

**Installation:**
```bash
# No new packages needed — httpx and pydantic already in requirements.txt
# Add to solo-leveling/.env:
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=<generate-in-n8n-settings>
```

---

## Package Legitimacy Audit

No new external packages are installed in this phase. The n8n REST API is accessed via the existing `httpx` client. All template handling uses stdlib `json`.

| Package | Registry | Age | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|
| (none — zero new installs) | — | — | — | N/A |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    solo-leveling FastAPI Process                     │
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────┐ │
│  │ /command      │    │ dispatcher.py     │    │ n8n/              │ │
│  │ /api/v1/...   │───►│ (Gemini LLM)     │    │  client.py        │ │
│  │ (intent entry)│    │ intent→template   │    │  templates/       │ │
│  └──────────────┘    │ match + param fill│    │  errors.py        │ │
│                       └────────┬─────────┘    └────────┬──────────┘ │
│                                │                       │            │
│                                ▼                       ▼            │
│                       ┌─────────────────┐    ┌──────────────────┐  │
│                       │ governor.py      │    │ n8n REST API     │  │
│                       │ (RL approval     │    │ POST /workflows/ │  │
│                       │  gate for side-  │    │   {id}/run       │  │
│                       │  effecting only) │    │ POST /credentials│  │
│                       └────────┬─────────┘    │ GET /executions/ │  │
│                                │              └────────┬─────────┘  │
│                                ▼                       │            │
│                       ┌─────────────────┐              │            │
│                       │ AI Guide reply   │◄─────────────┘            │
│                       │ (soft messages,  │   webhook callback        │
│                       │  approval prompt)│   POST /webhook/n8n      │
│                       └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        n8n (Docker)            │
                    │  ┌──────────────────────────┐ │
                    │  │ Credential Store          │ │
                    │  │ (encrypted with           │ │
                    │  │  N8N_ENCRYPTION_KEY)      │ │
                    │  ├──────────────────────────┤ │
                    │  │ Workflow Engine           │ │
                    │  │ (Webhook trigger →        │ │
                    │  │  nodes → callback)        │ │
                    │  └──────────────────────────┘ │
                    └───────────────────────────────┘
```

### Recommended Project Structure

```
solo-leveling/src/n8n/
├── __init__.py
├── client.py           # n8n REST API thin client (httpx-based)
├── credentials.py      # Credential injection: pull from integration clients, push to n8n
├── templates.py        # Template skeleton loader, validator, intent→skeleton matcher
├── executor.py         # Orchestrator: match intent → fill params → check RL → trigger n8n
├── errors.py           # Error abstraction: n8n/backend errors → soft AI-Guide messages
└── templates/          # Versioned workflow skeleton JSON files
    ├── gmail_read_summary.json     # Read-only example
    └── gmail_send_draft.json       # Side-effecting example

solo-leveling/tests/
└── test_n8n_execution.py           # Unit + integration tests

solo-leveling/src/api/
└── n8n_callback.py     # POST /webhook/n8n endpoint for execution callbacks
```

### Pattern 1: n8n REST API Thin Client

**What:** An httpx-based client module following the `github/client.py` pattern — `_request` helper, env-gated auth, typed response dicts.
**When to use:** Every n8n API call goes through this module.

```python
# src/n8n/client.py
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


def _request(method: str, path: str, json: dict[str, Any] | None = None,
             params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute an authenticated n8n API request."""
    if not N8N_API_KEY:
        raise EnvironmentError("N8N_API_KEY is not set. Add it to your .env file.")

    url = f"{N8N_BASE_URL}/api/v1{path}"
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(method, url, headers=_headers(), json=json, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("n8n API error: %s %s — %s", method, path, e.response.text)
        raise
    except Exception:
        logger.exception("n8n API request failed: %s %s", method, path)
        raise


def trigger_workflow(workflow_id: int | str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Trigger an n8n workflow execution. Returns execution details."""
    payload = {"data": data or {}}
    return _request("POST", f"/workflows/{workflow_id}/run", json=payload)


def get_execution(execution_id: int | str) -> dict[str, Any]:
    """Get execution status and result."""
    return _request("GET", f"/executions/{execution_id}")


def list_executions(workflow_id: int | str | None = None, status: str | None = None,
                    limit: int = 20) -> list[dict[str, Any]]:
    """List executions with optional filters."""
    params: dict[str, Any] = {"limit": limit}
    if workflow_id:
        params["workflowId"] = workflow_id
    if status:
        params["status"] = status
    result = _request("GET", "/executions", params=params)
    return result.get("data", [])


def create_credential(name: str, cred_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Create a credential in n8n's store. n8n encrypts data server-side."""
    return _request("POST", "/credentials", json={
        "name": name,
        "type": cred_type,
        "data": data,
    })


def update_credential(cred_id: int | str, name: str, cred_type: str,
                      data: dict[str, Any]) -> dict[str, Any]:
    """Update an existing credential."""
    return _request("PUT", f"/credentials/{cred_id}", json={
        "name": name,
        "type": cred_type,
        "data": data,
    })


def delete_credential(cred_id: int | str) -> dict[str, Any]:
    """Delete a credential from n8n."""
    return _request("DELETE", f"/credentials/{cred_id}")


def list_credentials() -> list[dict[str, Any]]:
    """List all credentials (returns metadata, not secret data)."""
    result = _request("GET", "/credentials")
    return result.get("data", [])


def health_check() -> dict[str, Any]:
    """Lightweight health check — verify n8n is reachable."""
    if not N8N_API_KEY:
        return {"ok": False, "error": "N8N_API_KEY not configured"}
    try:
        # List workflows as a health probe
        _request("GET", "/workflows", params={"limit": 1})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

*Source: Pattern follows `solo-leveling/src/integrations/github/client.py` [VERIFIED: codebase read]. n8n API endpoints from [CITED: docs.n8n.io/api/].*

### Pattern 2: Credential Injection

**What:** Pull OAuth tokens from existing integration clients, map to n8n credential type schemas, push via `POST /api/v1/credentials`.
**When to use:** At connect time (onboarding/settings) and on token refresh (D-05).

```python
# src/n8n/credentials.py
from __future__ import annotations

import logging
from typing import Any

from src.n8n import client as n8n_client

logger = logging.getLogger(__name__)

# Mapping: brain integration name → n8n credential type
_CREDENTIAL_TYPE_MAP: dict[str, str] = {
    "gmail": "gmailOAuth2",
    "gdrive": "googleDriveOAuth2Api",
    "github": "githubApi",
    "notion": "notionApi",
    "telegram": "telegramApi",
    "discord": "discordBotApi",
}


def sync_credential(integration: str, token_data: dict[str, Any],
                    owner_id: str = "default-owner") -> int:
    """Sync an integration's credentials into n8n's credential store.
    
    Returns the n8n credential ID.
    """
    cred_type = _CREDENTIAL_TYPE_MAP.get(integration)
    if not cred_type:
        raise ValueError(f"Unknown integration: {integration}")

    cred_name = f"signal-{owner_id}-{integration}"

    # Check if credential already exists
    existing = _find_credential_by_name(cred_name)
    n8n_data = _map_token_to_n8n_credential(integration, token_data)

    if existing:
        result = n8n_client.update_credential(
            cred_id=existing["id"],
            name=cred_name,
            cred_type=cred_type,
            data=n8n_data,
        )
        logger.info("Updated n8n credential for %s (id=%s)", integration, existing["id"])
        return result["id"]
    else:
        result = n8n_client.create_credential(
            name=cred_name,
            cred_type=cred_type,
            data=n8n_data,
        )
        logger.info("Created n8n credential for %s (id=%s)", integration, result["id"])
        return result["id"]


def _find_credential_by_name(name: str) -> dict[str, Any] | None:
    """Find an existing n8n credential by name."""
    creds = n8n_client.list_credentials()
    for c in creds:
        if c.get("name") == name:
            return c
    return None


def _map_token_to_n8n_credential(integration: str, token_data: dict[str, Any]) -> dict[str, Any]:
    """Map brain's token format to n8n's expected credential data schema.
    
    Each integration has a different n8n credential schema.
    """
    if integration == "gmail":
        # n8n gmailOAuth2 expects: clientId, clientSecret, oauthTokenData
        return {
            "clientId": token_data.get("client_id", ""),
            "clientSecret": token_data.get("client_secret", ""),
            "oauthTokenData": {
                "access_token": token_data.get("access_token", ""),
                "refresh_token": token_data.get("refresh_token", ""),
                "token_type": "Bearer",
                "expiry_date": token_data.get("expiry_date"),
            },
        }
    elif integration == "github":
        # n8n githubApi expects: accessToken (personal access token)
        return {
            "accessToken": token_data.get("token", ""),
        }
    elif integration == "notion":
        # n8n notionApi expects: apiKey (internal integration token)
        return {
            "apiKey": token_data.get("token", ""),
        }
    elif integration == "telegram":
        # n8n telegramApi expects: accessToken (bot token)
        return {
            "accessToken": token_data.get("token", ""),
        }
    # Default: pass through as-is
    return token_data
```

*Source: n8n credential type schemas from n8n community docs and source code [ASSUMED — exact field names need live verification against n8n instance].*

### Pattern 3: Intent → Template Skeleton → n8n Execution

**What:** The orchestrator that ties intent detection, template matching, parameter filling, RL gating, and n8n triggering into one flow.
**When to use:** When an owner intent is resolved to an n8n-executable action.

```python
# src/n8n/executor.py
from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.n8n import client as n8n_client
from src.n8n import credentials as n8n_creds
from src.n8n import templates as n8n_templates
from src.n8n.errors import classify_error, soft_error_message

logger = logging.getLogger(__name__)

_MAX_RETRIES = 1  # D-10: one automatic retry


async def execute_intent(intent: str, params: dict[str, Any],
                         owner_id: str = "default-owner") -> dict[str, Any]:
    """Execute an owner intent via n8n.
    
    Returns: {"status": "ok"|"error"|"needs_approval", "message": "...", ...}
    """
    # 1. Match intent to template skeleton
    skeleton = n8n_templates.match_template(intent)
    if not skeleton:
        # D-02: No template match → soft decline + log
        _log_unmet_intent(intent, params)
        return {
            "status": "declined",
            "message": "I can't do that yet — but I've noted it for a future update.",
        }

    # 2. LLM fills parameters for the skeleton
    workflow_json = n8n_templates.fill_parameters(skeleton, params)

    # 3. Check if side-effecting → RL approval gate (D-07)
    if skeleton.get("side_effecting", False):
        from src.autopilot.governor import Governor, ResponsibilityLevel
        governor = Governor(ResponsibilityLevel.LEAD_EXECUTOR)  # RL4 for cross-service writes
        allowed, reason = governor.can_execute("n8n_workflow", {
            "workflow": skeleton["name"],
            "intent": intent,
        })
        if not allowed:
            return {
                "status": "needs_approval",
                "message": f"This action needs your approval: {skeleton.get('description', intent)}",
                "approval_context": {"intent": intent, "skeleton": skeleton["id"]},
            }

    # 4. Trigger n8n workflow
    workflow_id = skeleton["n8n_workflow_id"]
    try:
        result = n8n_client.trigger_workflow(workflow_id, data=workflow_json)
        execution_id = result.get("data", {}).get("executionId")
        logger.info("n8n workflow %s triggered, execution=%s", workflow_id, execution_id)

        # 5. Wait for completion (polling for short workflows)
        if execution_id:
            exec_result = await _poll_execution(execution_id)
            if exec_result.get("status") == "success":
                return {"status": "ok", "result": exec_result.get("data")}
            else:
                # Retry once (D-10)
                return await _retry_and_report(workflow_id, workflow_json, exec_result, intent)

        return {"status": "ok", "result": result}

    except Exception as e:
        logger.exception("n8n execution failed for intent=%s", intent)
        return await _retry_and_report(workflow_id, workflow_json, {"error": str(e)}, intent)


async def _poll_execution(execution_id: int | str, max_wait: int = 30) -> dict[str, Any]:
    """Poll n8n execution status until complete or timeout."""
    import asyncio
    for _ in range(max_wait):
        exec_data = n8n_client.get_execution(execution_id)
        status = exec_data.get("data", {}).get("status", "")
        if status in ("success", "error", "crashed", "waiting"):
            return exec_data.get("data", {})
        await asyncio.sleep(1)
    return {"status": "timeout"}


async def _retry_and_report(workflow_id: int | str, workflow_json: dict,
                            first_result: dict, intent: str) -> dict[str, Any]:
    """Retry once, then surface soft error message (D-10, D-11)."""
    logger.warning("First execution failed for workflow %s, retrying...", workflow_id)
    try:
        result = n8n_client.trigger_workflow(workflow_id, data=workflow_json)
        execution_id = result.get("data", {}).get("executionId")
        if execution_id:
            exec_result = await _poll_execution(execution_id)
            if exec_result.get("status") == "success":
                return {"status": "ok", "result": exec_result.get("data")}
    except Exception:
        logger.exception("Retry also failed for workflow %s", workflow_id)

    # Both attempts failed — surface soft message (D-11)
    error_class = classify_error(first_result)
    return {
        "status": "error",
        "message": soft_error_message(error_class, intent),
    }


def _log_unmet_intent(intent: str, params: dict[str, Any]) -> None:
    """Log unmet intent for future template development (D-02)."""
    import json
    from pathlib import Path
    log_path = Path("data/unmet_intents.json")
    try:
        existing = json.loads(log_path.read_text()) if log_path.exists() else []
    except (json.JSONDecodeError, OSError):
        existing = []
    existing.append({"intent": intent, "params": params, "count": 1})
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(existing[-100:], indent=2))  # Keep last 100
```

*Source: Pattern derived from existing brain architecture (dispatcher.py, governor.py, router.py) [VERIFIED: codebase read].*

### Pattern 4: Error Abstraction Layer

**What:** Maps raw n8n/backend errors to plain-language, owner-actionable messages.
**When to use:** After any n8n execution failure, before surfacing to the AI Guide.

```python
# src/n8n/errors.py
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorClass(str, Enum):
    CREDENTIAL_EXPIRED = "credential_expired"
    CREDENTIAL_REVOKED = "credential_revoked"
    INTEGRATION_NOT_CONNECTED = "integration_not_connected"
    N8N_UNREACHABLE = "n8n_unreachable"
    WORKFLOW_NOT_FOUND = "workflow_not_found"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


# Error patterns → classification
_ERROR_PATTERNS: list[tuple[str, ErrorClass]] = [
    ("token expired", ErrorClass.CREDENTIAL_EXPIRED),
    ("token has been revoked", ErrorClass.CREDENTIAL_REVOKED),
    ("invalid_grant", ErrorClass.CREDENTIAL_EXPIRED),
    ("401", ErrorClass.CREDENTIAL_EXPIRED),
    ("403", ErrorClass.CREDENTIAL_REVOKED),
    ("not connected", ErrorClass.INTEGRATION_NOT_CONNECTED),
    ("ECONNREFUSED", ErrorClass.N8N_UNREACHABLE),
    ("workflow not found", ErrorClass.WORKFLOW_NOT_FOUND),
    ("429", ErrorClass.RATE_LIMITED),
]


def classify_error(error_data: dict[str, Any]) -> ErrorClass:
    """Classify a raw error into an owner-actionable category."""
    error_str = str(error_data).lower()
    for pattern, error_class in _ERROR_PATTERNS:
        if pattern.lower() in error_str:
            return error_class
    return ErrorClass.UNKNOWN


_SOFT_MESSAGES: dict[ErrorClass, str] = {
    ErrorClass.CREDENTIAL_EXPIRED: (
        "Your {integration} connection may have expired. "
        "Would you like to reconnect?"
    ),
    ErrorClass.CREDENTIAL_REVOKED: (
        "Your {integration} access was revoked. "
        "You'll need to reconnect to continue."
    ),
    ErrorClass.INTEGRATION_NOT_CONNECTED: (
        "You haven't connected {integration} yet. "
        "Let's set that up first."
    ),
    ErrorClass.N8N_UNREACHABLE: (
        "The execution engine isn't responding right now. "
        "It may need a restart."
    ),
    ErrorClass.WORKFLOW_NOT_FOUND: (
        "I couldn't find that workflow — it may have been removed. "
        "Let me know if you'd like to set it up again."
    ),
    ErrorClass.RATE_LIMITED: (
        "Too many requests at once. "
        "Let's wait a moment and try again."
    ),
    ErrorClass.UNKNOWN: (
        "Something went wrong with that action. "
        "I've logged it — try again in a bit."
    ),
}


def soft_error_message(error_class: ErrorClass, intent: str = "",
                       integration: str = "") -> str:
    """Return a plain-language error message for the owner."""
    template = _SOFT_MESSAGES.get(error_class, _SOFT_MESSAGES[ErrorClass.UNKNOWN])
    return template.format(integration=integration or "that app")
```

### Pattern 5: Webhook Callback Endpoint

**What:** A FastAPI endpoint that receives n8n execution completion callbacks.
**When to use:** Registered on the FastAPI app; n8n workflows include a callback node that POSTs results here.

```python
# src/api/n8n_callback.py
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter()

_EXECUTION_LOG_PATH = Path("data/n8n_executions.json")


@router.post("/webhook/n8n")
async def n8n_callback(request: Request) -> dict[str, str]:
    """Receive n8n execution completion callbacks.
    
    n8n workflows should include a Webhook node at the end that POSTs
    execution results to this endpoint.
    """
    try:
        payload = await request.json()
    except Exception:
        logger.warning("n8n callback received invalid JSON")
        return {"status": "error", "detail": "Invalid JSON"}

    execution_id = payload.get("executionId", "unknown")
    status = payload.get("status", "unknown")
    data = payload.get("data", {})

    logger.info("n8n callback: execution=%s status=%s", execution_id, status)

    # Persist execution result
    _log_execution(execution_id, status, data)

    # If failed, could trigger soft error message to owner here
    # (integration with AI Guide reply path — Phase 3 surface)

    return {"status": "ok"}


def _log_execution(execution_id: str, status: str, data: dict[str, Any]) -> None:
    """Log execution result to local JSON store (local-first pattern)."""
    try:
        existing = json.loads(_EXECUTION_LOG_PATH.read_text()) if _EXECUTION_LOG_PATH.exists() else []
    except (json.JSONDecodeError, OSError):
        existing = []

    existing.append({
        "execution_id": execution_id,
        "status": status,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    _EXECUTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _EXECUTION_LOG_PATH.write_text(json.dumps(existing[-500:], indent=2))  # Keep last 500
```

### Anti-Patterns to Avoid

- **Sending raw n8n stack traces to the owner:** The error abstraction layer (Pattern 4) MUST wrap every n8n failure before it reaches the AI Guide reply path. Never pass `httpx.HTTPStatusError.response.text` directly to the user.
- **Polling n8n executions indefinitely:** Set a max wait (30s for short workflows). For long-running workflows, use the webhook callback pattern instead.
- **Storing n8n API key in code:** Always read from `N8N_API_KEY` env var via `config.py`. Never hardcode.
- **Creating n8n credentials without checking for existing ones:** Always `list_credentials` + name-match first, then create or update. Duplicate credentials cause confusion.
- **Assuming n8n credential field names without verification:** n8n credential type schemas are not formally documented in the public API. The field names in Pattern 2 are based on community knowledge [ASSUMED] and MUST be verified against a live n8n instance before implementation.
- **Bypassing the RL gate for "read-only" workflows that actually have side effects:** Classify templates as `side_effecting: true/false` explicitly in the template JSON. When in doubt, treat as side-effecting.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| n8n API authentication | Custom auth header logic | `X-N8N-API-KEY` header per n8n docs | Standard API key auth; n8n validates server-side |
| Credential encryption for n8n | AES encryption with `N8N_ENCRYPTION_KEY` | n8n REST API `POST /credentials` (server-side encryption) | n8n encrypts credential data automatically when received via the API; the client sends plaintext |
| Execution status tracking | Custom polling loop with backoff | `GET /api/v1/executions/{id}` + simple 1s interval poll | n8n provides execution status directly; custom backoff adds complexity with no benefit at personal scale |
| Error classification | Free-text error matching | Structured `ErrorClass` enum + pattern table | Deterministic; extensible; prevents error message drift |
| Workflow template storage | Database table for templates | JSON files in `src/n8n/templates/` | Version-controlled, reviewable, portable; matches brain's local-first pattern |

**Key insight:** The n8n Public REST API handles credential encryption server-side — the brain sends plaintext token data to `POST /api/v1/credentials` and n8n encrypts it with its `N8N_ENCRYPTION_KEY` before storing. The brain does NOT need access to n8n's encryption key. This simplifies D-04 significantly. [ASSUMED — needs live verification against n8n instance]

---

## Common Pitfalls

### Pitfall 1: n8n Credential Type Schema Mismatch
**What goes wrong:** `POST /api/v1/credentials` returns 400 or the credential is created but n8n nodes cannot use it.
**Why it happens:** n8n credential types have specific expected field names (e.g., `gmailOAuth2` expects `clientId`, `clientSecret`, `oauthTokenData`). Using wrong field names silently creates a broken credential.
**How to avoid:** Verify credential type schemas against a live n8n instance. Create a credential manually in the n8n UI, then `GET /api/v1/credentials/{id}` to see the structure. Use that as the reference.
**Warning signs:** n8n workflow fails with "credential not found" or "invalid credential" even though the credential exists.

### Pitfall 2: n8n API Key Not Generated
**What goes wrong:** All n8n API calls return 401 Unauthorized.
**Why it happens:** The n8n API key must be generated manually in the n8n UI (Settings → API → Create API Key). It is NOT set via environment variables.
**How to avoid:** Document the API key generation step in the setup guide. Add `N8N_API_KEY` to `.env.example` with a comment explaining where to get it.
**Warning signs:** `httpx.HTTPStatusError` with 401 status on every n8n API call.

### Pitfall 3: n8n Workflow Not Activated
**What goes wrong:** `POST /api/v1/workflows/{id}/run` returns 400 or "workflow not active".
**Why it happens:** n8n requires workflows to be activated before they can be triggered via the API or webhooks. Deactivated workflows only work in the test editor.
**How to include:** After creating/importing a workflow, always `PATCH /api/v1/workflows/{id}` with `{"active": true}` or use the activate endpoint.
**Warning signs:** "Workflow is not active" error message from n8n API.

### Pitfall 4: Webhook URL Mismatch
**What goes wrong:** n8n callback node POSTs to wrong URL; brain never receives execution results.
**Why it happens:** The `WEBHOOK_URL` in `docker-compose.n8n.yml` must match the brain's externally reachable URL. For local dev, this is `http://host.docker.internal:8000` (not `localhost`).
**How to avoid:** Set `WEBHOOK_URL` in the n8n compose service to the brain's actual URL. For production, use the deployed URL.
**Warning signs:** No callback received; execution stays in "running" state in n8n.

### Pitfall 5: Token Refresh Race Condition
**What goes wrong:** Brain pushes an OAuth token to n8n, but the token expires before the workflow runs.
**Why it happens:** OAuth tokens have short TTLs (typically 1 hour). If the brain syncs a token that is already near-expiry, n8n will use an expired token.
**How to avoid:** Before syncing to n8n, check `creds.expired` and call `creds.refresh(Request())` if needed. Only push freshly-refreshed tokens.
**Warning signs:** n8n workflow fails with "token expired" immediately after credential sync.

### Pitfall 6: Execution Log Bloat
**What goes wrong:** `data/n8n_executions.json` grows unbounded.
**Why it happens:** Every callback appends to the file; no rotation.
**How to avoid:** Cap at 500 entries (rolling window). Same pattern used in `telegram/webhook.py` (`_MAX_PROCESSED_SIZE = 1000`).
**Warning signs:** File grows past 1MB; slow JSON parse on startup.

---

## Code Examples

### Verify n8n is Reachable

```python
# Health check — mirrors github/client.py health_check pattern
from src.n8n.client import health_check

result = health_check()
# {"ok": True} or {"ok": False, "error": "N8N_API_KEY not configured"}
```

### Trigger a Workflow and Poll for Result

```python
from src.n8n.client import trigger_workflow, get_execution
import asyncio

# Trigger
result = trigger_workflow(workflow_id=123, data={"to": "user@example.com", "subject": "Test"})
execution_id = result["data"]["executionId"]

# Poll
for _ in range(30):
    exec_data = get_execution(execution_id)
    status = exec_data["data"]["status"]
    if status in ("success", "error", "crashed"):
        break
    await asyncio.sleep(1)
```

### Sync Gmail Credentials to n8n

```python
from src.n8n.credentials import sync_credential

# Pull from existing gmail client token file
import json
token_path = ".gmail_token.json"
with open(token_path) as f:
    token_data = json.load(f)

cred_id = sync_credential("gmail", token_data, owner_id="pramono@getgoing.co.id")
# cred_id = 42 (n8n credential ID to reference in workflow nodes)
```

*Source: Gmail token format from `solo-leveling/src/integrations/gmail/client.py` [VERIFIED: codebase read].*

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| n8n internal `/rest/` API | n8n Public REST API `/api/v1/` | n8n v1.0 (2023) | Stable, versioned, documented API; API key auth instead of session cookies |
| n8n basic auth for API | n8n API key (`X-N8N-API-KEY`) | n8n v1.0+ | API keys are per-user, revocable, don't expire with sessions |
| Manual credential entry in n8n UI | Programmatic credential creation via REST API | n8n v1.0+ | Brain can provision credentials automatically at connect time |

**Deprecated/outdated:**
- n8n internal `/rest/` endpoints: undocumented, change without notice, use session auth. Use `/api/v1/` instead.
- n8n basic auth for API access: still works for the UI login but API keys are the recommended auth method for programmatic access.

---

## Runtime State Inventory

> This phase is greenfield (new n8n client module, new templates, new callback endpoint) — no existing runtime state is renamed or migrated. However, n8n's own runtime state is relevant.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None in brain — new `data/n8n_executions.json` and `data/unmet_intents.json` are created fresh | Create at runtime |
| Live service config | n8n running via `docker-compose.n8n.yml` with basic auth (`admin/changeme-strong-password`), `WEBHOOK_URL=http://localhost:5677/` | Add `N8N_API_KEY` env var; update `WEBHOOK_URL` if brain callback endpoint is on different port |
| OS-registered state | None — no OS-level registrations | None |
| Secrets/env vars | New: `N8N_BASE_URL`, `N8N_API_KEY`. Existing reused: `GMAIL_TOKEN_PATH`, `GITHUB_PAT`, `NOTION_API_TOKEN`, `TELEGRAM_BOT_TOKEN` | Add new vars to `.env.example` and `config.py` |
| Build artifacts | None | None |

---

## Open Questions (RESOLVED)

1. **Does n8n's `POST /api/v1/credentials` handle encryption server-side?** — RESOLVED: Proceed with assumption that n8n encrypts server-side (brain sends plaintext). Verify during live integration test in Wave 0. If pre-encryption is needed, add AES crypto with `N8N_ENCRYPTION_KEY` — but this is unlikely for the public API.

2. **What are the exact n8n credential type names and field schemas for Gmail OAuth2, GitHub, Notion, Telegram?** — RESOLVED: Proceed with documented type names (`gmailOAuth2`, `githubApi`, `notionApi`, `telegramApi`). Verify field schemas by creating credentials manually in n8n UI then `GET /api/v1/credentials/{id}` during Wave 0 setup.

3. **Should the brain use `POST /api/v1/workflows/{id}/run` (manual execution) or trigger via webhook URL?** — RESOLVED: Use `POST /api/v1/workflows/{id}/run` for this phase (simpler, synchronous for short workflows). Webhook triggering is a possible production enhancement but not required to prove the pipeline.

4. **How does the brain discover n8n workflow IDs for its templates?** — RESOLVED: Pre-create starter workflows in n8n via the API during Wave 0 setup. Record returned IDs in template JSON files. This is a one-time setup step documented in the plan.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| n8n (Docker) | All n8n API calls | Yes (via `docker-compose.n8n.yml`) | n8nio/n8n:latest | — |
| n8n API Key | API authentication | Needs generation in n8n UI | — | Basic auth as fallback (less secure) |
| Python 3.13 (venv) | Brain process | Yes | 3.13.x | — |
| httpx | n8n REST client | Yes (already installed) | — | — |
| `GMAIL_TOKEN_PATH` (.gmail_token.json) | Gmail credential sync | Assumed exists (Phase 1 setup) | — | Skip Gmail credential sync |
| `GITHUB_PAT` | GitHub credential sync | Assumed set | — | Skip GitHub credential sync |
| `NOTION_API_TOKEN` | Notion credential sync | Assumed set | — | Skip Notion credential sync |

**Missing dependencies with no fallback:**
- `N8N_API_KEY` — must be generated in n8n UI and added to `.env`; all n8n API calls fail without it

**Missing dependencies with fallback:**
- Individual integration tokens (Gmail, GitHub, etc.) — if not configured, skip credential sync for that integration; the n8n execution layer still works for workflows that don't need those credentials

---

## Validation Architecture

`workflow.nyquist_validation: true` in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` |
| Config file | none (direct `python -m unittest` invocation) |
| Quick run command | `python -m unittest tests.test_n8n_execution -v` |
| Full suite command | `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation tests.test_n8n_execution -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| N8N-01 | `trigger_workflow` sends POST to n8n API with correct payload | unit (mocked httpx) | `python -m unittest tests.test_n8n_execution.N8NClientTests.test_trigger_workflow -v` | No — Wave 0 gap |
| N8N-01 | `execute_intent` matches intent to template and triggers n8n | unit (mocked client) | `python -m unittest tests.test_n8n_execution.ExecutorTests.test_execute_intent_readonly -v` | No — Wave 0 gap |
| N8N-01 | No template match returns soft decline (D-02) | unit | `python -m unittest tests.test_n8n_execution.ExecutorTests.test_no_template_match_declines -v` | No — Wave 0 gap |
| N8N-02 | `sync_credential` creates credential in n8n | unit (mocked API) | `python -m unittest tests.test_n8n_execution.CredentialTests.test_sync_creates_credential -v` | No — Wave 0 gap |
| N8N-02 | `sync_credential` updates existing credential (no duplicate) | unit (mocked API) | `python -m unittest tests.test_n8n_execution.CredentialTests.test_sync_updates_existing -v` | No — Wave 0 gap |
| N8N-02 | Token data mapped correctly for Gmail OAuth2 | unit | `python -m unittest tests.test_n8n_execution.CredentialTests.test_gmail_token_mapping -v` | No — Wave 0 gap |
| N8N-04 | Webhook callback endpoint receives and logs execution | unit (TestClient) | `python -m unittest tests.test_n8n_execution.CallbackTests.test_callback_logs_execution -v` | No — Wave 0 gap |
| N8N-04 | `_poll_execution` returns result when execution completes | unit (mocked API) | `python -m unittest tests.test_n8n_execution.ExecutorTests.test_poll_execution_success -v` | No — Wave 0 gap |
| INFRA-05 | `classify_error` maps "token expired" to CREDENTIAL_EXPIRED | unit | `python -m unittest tests.test_n8n_execution.ErrorTests.test_classify_credential_expired -v` | No — Wave 0 gap |
| INFRA-05 | `soft_error_message` returns owner-friendly text | unit | `python -m unittest tests.test_n8n_execution.ErrorTests.test_soft_message_no_stack_trace -v` | No — Wave 0 gap |
| INFRA-05 | Side-effecting workflow goes through RL approval gate | unit (mocked governor) | `python -m unittest tests.test_n8n_execution.ExecutorTests.test_side_effecting_needs_approval -v` | No — Wave 0 gap |
| D-10 | Failed execution triggers one retry before surfacing error | unit (mocked API) | `python -m unittest tests.test_n8n_execution.ExecutorTests.test_retry_once_on_failure -v` | No — Wave 0 gap |

### Sampling Rate

- **Per task commit:** `python -m unittest tests.test_n8n_execution -v` (unit tests, mocked n8n API)
- **Per wave merge:** `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation tests.test_n8n_execution -v`
- **Phase gate:** Full suite green; plus one manual smoke: trigger a read-only n8n workflow via the brain and verify the AI Guide receives a success or soft-error message

### Wave 0 Gaps

- [ ] `tests/test_n8n_execution.py` — all test classes above; mock `httpx.Client` for n8n API calls
- [ ] `N8N_BASE_URL` and `N8N_API_KEY` in `.env.example` with setup comments
- [ ] Docker Compose n8n service running with API key generated
- [ ] Two starter workflow skeletons created in n8n and IDs recorded in template JSON files

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | n8n API key auth (`X-N8N-API-KEY`); stored in `.env`, never hardcoded |
| V3 Session Management | No | n8n API keys don't have sessions; stateless per-request auth |
| V4 Access Control | Yes | RL governor gates side-effecting workflows (D-07); `owner_id` scopes all operations |
| V5 Input Validation | Yes | Template parameters validated before passing to n8n; webhook callback payload validated |
| V6 Cryptography | Yes | n8n handles credential encryption server-side; brain does NOT handle `N8N_ENCRYPTION_KEY` |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| n8n API key exposure | Information Disclosure | Read from env var only; `.env` is gitlogged; never in code or logs |
| Credential data in transit (brain → n8n) | Information Disclosure | n8n runs on Docker internal network; use HTTPS in production |
| Malicious workflow JSON injection | Tampering | Templates are version-controlled JSON files; LLM only fills parameters, not node definitions (D-01) |
| Unauthorized workflow execution | Elevation of Privilege | n8n API key required; brain is the only caller; webhook callback endpoint validates payload structure |
| Credential sync race condition | Denial of Service | Sync is idempotent (upsert by name); concurrent syncs are safe |
| Unmet intent log bloat | Denial of Service | Capped at 100 entries (rolling window) |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | n8n `POST /api/v1/credentials` encrypts data server-side (brain sends plaintext) | Don't Hand-Roll, Open Q1 | If pre-encryption required, brain needs `N8N_ENCRYPTION_KEY` + AES crypto — adds complexity |
| A2 | n8n credential type names are `gmailOAuth2`, `githubApi`, `notionApi`, `telegramApi`, `discordBotApi` | Pattern 2 (Credentials) | Wrong type names → credentials created but n8n nodes can't use them |
| A3 | n8n credential data field names for Gmail OAuth2 are `clientId`, `clientSecret`, `oauthTokenData` | Pattern 2 (Credentials) | Wrong field names → broken credential; must verify against live n8n |
| A4 | `POST /api/v1/workflows/{id}/run` accepts a `data` payload and returns `executionId` | Pattern 1 (Client) | If endpoint doesn't exist or has different shape, trigger mechanism changes |
| A5 | Webhook callback from n8n includes `executionId`, `status`, and `data` fields | Pattern 5 (Callback) | If payload shape differs, callback parsing breaks |
| A6 | n8n workflows must be activated before API triggering works | Pitfall 3 | If wrong, unnecessary activation step; if right, forgetting it causes 400 errors |
| A7 | RL4 (Lead Executor) is the correct level for side-effecting n8n workflows | Pattern 3 (Executor) | Too low → insufficient safety; too high → excessive approval friction |

---

## Project Constraints (from CLAUDE.md)

Directives extracted from `solo-leveling/CLAUDE.md` that the planner must verify compliance with:

1. **Absolute imports with `src.` prefix** — all new files in `src/n8n/` must use `from src.n8n.client import ...`, never `from .client import ...`.
2. **`from __future__ import annotations`** — required at the top of every new `.py` file.
3. **Private helpers prefixed with `_`** — internal functions like `_headers()`, `_map_token_to_n8n_credential()`, `_log_unmet_intent()`.
4. **Catch `EnvironmentError` separately in handlers** — `N8N_API_KEY` is environment-gated; raise `EnvironmentError` not generic `ValueError`.
5. **stdlib `unittest`** — no pytest; use `unittest.TestCase` classes, `unittest.mock.patch`.
6. **Tests live under `tests/`** — new file: `tests/test_n8n_execution.py`.
7. **Run tests before committing** — `python -m unittest tests.test_n8n_execution -v`.
8. **Update `CHANGELOG.md`** after non-trivial changes.
9. **Update `AI_CONTEXT.md`** if the current phase, completed stages, or active priorities change.
10. **Commit style** — `feat(n8n): ...` for n8n execution layer additions.
11. **Follow existing integration client pattern** — `github/client.py` is the template: thin httpx client, `_request` helper, env-gated auth, typed response dicts.

---

## Sources

### Primary (HIGH confidence)
- [n8n Public REST API docs](https://docs.n8n.io/api/) — endpoint reference for workflows, credentials, executions
- [n8n Webhook node docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/) — webhook trigger pattern, production vs test URLs
- `solo-leveling/src/integrations/github/client.py` — thin client pattern (httpx, `_request`, env-gated) [VERIFIED: codebase read]
- `solo-leveling/src/autopilot/governor.py` — RL governor, `can_execute` interface [VERIFIED: codebase read]
- `solo-leveling/src/agents/dispatcher.py` — Gemini dispatcher, `run_agent` interface [VERIFIED: codebase read]
- `docker-compose.n8n.yml` — n8n service config (basic auth, ports, volumes) [VERIFIED: file read]

### Secondary (MEDIUM confidence)
- n8n credential type schemas (`gmailOAuth2`, `githubApi`, etc.) — from n8n community forums and source code references [ASSUMED — needs live verification]
- n8n `POST /api/v1/credentials` server-side encryption — from community discussions [ASSUMED — needs live verification]
- `POST /api/v1/workflows/{id}/run` endpoint existence and payload shape — from n8n API docs references [ASSUMED — endpoint may have changed]

### Tertiary (LOW confidence)
- Exact field names within n8n credential `data` objects — not formally documented; derived from community examples [ASSUMED]
- n8n execution callback payload shape — assumed based on webhook node documentation; needs live verification [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — httpx already installed; no new dependencies; n8n API is official
- Architecture: HIGH — grounded in existing codebase patterns (github/client.py, governor.py, dispatcher.py)
- Pitfalls: MEDIUM — most grounded in n8n docs; credential schema pitfalls are ASSUMED
- Credential injection: LOW-MEDIUM — n8n credential type schemas need live verification against n8n instance

**Research date:** 2026-05-30
**Valid until:** 2026-06-30 (n8n API is stable but credential schemas and endpoint details need live verification)
