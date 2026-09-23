# Phase 2: n8n Execution Layer - Pattern Map

**Mapped:** 2026-05-30
**Files analyzed:** 10
**Analogs found:** 10 / 10

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/n8n/__init__.py` | config | — | `src/integrations/github/__init__.py` | exact |
| `src/n8n/client.py` | service | request-response | `src/integrations/github/client.py` | exact |
| `src/n8n/credentials.py` | service | CRUD | `src/integrations/github/client.py` | role-match |
| `src/n8n/templates.py` | utility | transform | `src/integrations/telegram/webhook.py` | partial (JSON I/O) |
| `src/n8n/executor.py` | service | event-driven | `src/agents/dispatcher.py` + `src/autopilot/governor.py` | role-match |
| `src/n8n/errors.py` | utility | transform | `src/autopilot/governor.py` | role-match (enum) |
| `src/api/n8n_callback.py` | controller | request-response | `src/api/autopilot.py` | exact |
| `tests/test_n8n_execution.py` | test | — | `tests/test_autopilot.py` | exact |
| `src/core/config.py` | config | — | (existing file, add vars) | — |
| `src/api/v1_router.py` | route | — | (existing file, add import) | — |

## Pattern Assignments

### `src/n8n/__init__.py` (config, package init)

**Analog:** `src/integrations/github/__init__.py`

Empty init file. Just a docstring if any. Copy the pattern: a one-line module docstring or empty file.

---

### `src/n8n/client.py` (service, request-response)

**Analog:** `src/integrations/github/client.py` (exact match — httpx thin client, `_request` helper, env-gated auth)

**Imports pattern** (lines 1-17):
```python
"""n8n Public REST API client.

Requires N8N_BASE_URL and N8N_API_KEY environment variables.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.core.config import N8N_BASE_URL, N8N_API_KEY

logger = logging.getLogger(__name__)
```

**Auth header helper** (lines 22-28 of github/client.py):
```python
def _headers() -> dict[str, str]:
    return {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json",
    }
```
Note: n8n uses `X-N8N-API-KEY` header instead of GitHub's `Authorization: Bearer` pattern. Same structure, different header name.

**Core `_request` helper** (lines 31-48 of github/client.py) — copy this pattern exactly:
```python
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
```

**Domain functions** — follow the same one-function-per-API-endpoint pattern as github/client.py:
- `trigger_workflow(workflow_id, data)` → POST `/workflows/{id}/run`
- `get_execution(execution_id)` → GET `/executions/{id}`
- `list_executions(workflow_id, status, limit)` → GET `/executions`
- `create_credential(name, cred_type, data)` → POST `/credentials`
- `update_credential(cred_id, name, cred_type, data)` → PUT `/credentials/{id}`
- `delete_credential(cred_id)` → DELETE `/credentials/{id}`
- `list_credentials()` → GET `/credentials`
- `health_check()` → lightweight probe (copy github/client.py lines 126-134)

**Health check pattern** (lines 126-134 of github/client.py):
```python
def health_check() -> dict[str, Any]:
    """Return a lightweight health check result."""
    if not N8N_API_KEY:
        return {"ok": False, "error": "N8N_API_KEY not configured"}
    try:
        _request("GET", "/workflows", params={"limit": 1})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

---

### `src/n8n/credentials.py` (service, CRUD)

**Analog:** `src/integrations/github/client.py` (role-match — uses the n8n client for CRUD, adds mapping logic)

**Imports pattern:**
```python
from __future__ import annotations

import logging
from typing import Any

from src.n8n import client as n8n_client

logger = logging.getLogger(__name__)
```

**Core pattern** — upsert-by-name (check existing, then create or update):
```python
def sync_credential(integration: str, token_data: dict[str, Any],
                    owner_id: str = "default-owner") -> int:
    """Sync an integration's credentials into n8n's credential store."""
    cred_type = _CREDENTIAL_TYPE_MAP.get(integration)
    if not cred_type:
        raise ValueError(f"Unknown integration: {integration}")

    cred_name = f"signal-{owner_id}-{integration}"
    existing = _find_credential_by_name(cred_name)
    n8n_data = _map_token_to_n8n_credential(integration, token_data)

    if existing:
        result = n8n_client.update_credential(existing["id"], cred_name, cred_type, n8n_data)
        return result["id"]
    else:
        result = n8n_client.create_credential(cred_name, cred_type, n8n_data)
        return result["id"]
```

**Token mapping** — private helper `_map_token_to_n8n_credential(integration, token_data)` maps brain's heterogeneous token formats to n8n credential type schemas. Each integration branch is a simple dict construction.

**Error handling:** Let `httpx.HTTPStatusError` propagate from `n8n_client`; the caller (executor) catches and classifies via `errors.py`.

---

### `src/n8n/templates.py` (utility, transform)

**Analog:** `src/integrations/telegram/webhook.py` (partial — JSON file I/O pattern with `Path`, `json.loads`, rolling-window cap)

**Imports pattern:**
```python
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"
```

**JSON file loading pattern** (follows telegram/webhook.py `_load_processed_ids` lines 21-29):
```python
def _load_template(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to load template: %s", path)
        return None
```

**Core functions:**
- `load_all_templates() -> list[dict[str, Any]]` — scan `_TEMPLATES_DIR` for `.json` files
- `match_template(intent: str) -> dict[str, Any] | None` — fuzzy match intent to a template skeleton (keyword matching or simple scoring)
- `fill_parameters(skeleton: dict, params: dict) -> dict` — LLM-assisted parameter injection into skeleton

**No direct analog for the matching logic** — this is new domain logic. Use simple keyword/phrase matching for v1; the Gemini dispatcher (`run_agent`) can be called for more sophisticated matching if needed.

---

### `src/n8n/executor.py` (service, event-driven)

**Analog:** `src/agents/dispatcher.py` (orchestrator pattern — call multiple services, return structured result) + `src/autopilot/governor.py` (RL gate)

**Imports pattern:**
```python
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
```

**RL gate pattern** (governor.py lines 46-76) — import and use inline:
```python
from src.autopilot.governor import Governor, ResponsibilityLevel

governor = Governor(ResponsibilityLevel.LEAD_EXECUTOR)  # RL4 for cross-service writes
allowed, reason = governor.can_execute("n8n_workflow", {
    "workflow": skeleton["name"],
    "intent": intent,
})
if not allowed:
    return {"status": "needs_approval", "message": f"This action needs your approval: ..."}
```

**Core orchestrator `execute_intent`** — follows dispatcher.py's linear flow:
1. Match intent to template skeleton
2. LLM fills parameters
3. Check RL gate if side-effecting
4. Trigger n8n workflow
5. Poll for result (short workflows) or wait for callback
6. On failure: retry once, then classify error and return soft message

**Polling pattern** (new, simple):
```python
async def _poll_execution(execution_id: int | str, max_wait: int = 30) -> dict[str, Any]:
    for _ in range(max_wait):
        exec_data = n8n_client.get_execution(execution_id)
        status = exec_data.get("data", {}).get("status", "")
        if status in ("success", "error", "crashed", "waiting"):
            return exec_data.get("data", {})
        await asyncio.sleep(1)
    return {"status": "timeout"}
```

**Retry + soft error pattern** (D-10, D-11):
```python
async def _retry_and_report(workflow_id, workflow_json, first_result, intent):
    # Retry once
    try:
        result = n8n_client.trigger_workflow(workflow_id, data=workflow_json)
        # ... poll ...
        if success:
            return {"status": "ok", ...}
    except Exception:
        pass
    # Both failed — classify and return soft message
    error_class = classify_error(first_result)
    return {"status": "error", "message": soft_error_message(error_class, intent)}
```

**Unmet intent logging** (D-02) — follows telegram/webhook.py JSON append pattern:
```python
def _log_unmet_intent(intent: str, params: dict[str, Any]) -> None:
    log_path = Path("data/unmet_intents.json")
    existing = json.loads(log_path.read_text()) if log_path.exists() else []
    existing.append({"intent": intent, "params": params})
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(existing[-100:], indent=2))  # Cap at 100
```

---

### `src/n8n/errors.py` (utility, transform)

**Analog:** `src/autopilot/governor.py` (enum + lookup table pattern)

**Imports pattern:**
```python
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)
```

**Enum pattern** (governor.py lines 21-27):
```python
class ErrorClass(str, Enum):
    CREDENTIAL_EXPIRED = "credential_expired"
    CREDENTIAL_REVOKED = "credential_revoked"
    INTEGRATION_NOT_CONNECTED = "integration_not_connected"
    N8N_UNREACHABLE = "n8n_unreachable"
    WORKFLOW_NOT_FOUND = "workflow_not_found"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"
```

**Lookup table pattern** (governor.py lines 30-43 `_TOOL_RL_REQUIREMENTS`):
```python
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
```

**Core functions:**
- `classify_error(error_data: dict) -> ErrorClass` — string-match against patterns
- `soft_error_message(error_class, intent, integration) -> str` — template-based plain-language message

**Soft message templates** — owner-friendly, no stack traces, suggest action:
```python
_SOFT_MESSAGES: dict[ErrorClass, str] = {
    ErrorClass.CREDENTIAL_EXPIRED: "Your {integration} connection may have expired. Would you like to reconnect?",
    ErrorClass.N8N_UNREACHABLE: "The execution engine isn't responding right now. It may need a restart.",
    # ...
}
```

---

### `src/api/n8n_callback.py` (controller, request-response)

**Analog:** `src/api/autopilot.py` (exact — FastAPI router, `APIRouter()`, `Depends(require_auth)` pattern)

**Imports pattern** (autopilot.py lines 1-10):
```python
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter()
```

**Endpoint pattern** (autopilot.py uses `Depends(require_auth)` but n8n callbacks come from n8n itself, not the owner — use payload validation instead):
```python
@router.post("/webhook/n8n")
async def n8n_callback(request: Request) -> dict[str, str]:
    """Receive n8n execution completion callbacks."""
    try:
        payload = await request.json()
    except Exception:
        logger.warning("n8n callback received invalid JSON")
        return {"status": "error", "detail": "Invalid JSON"}

    execution_id = payload.get("executionId", "unknown")
    status = payload.get("status", "unknown")
    data = payload.get("data", {})

    logger.info("n8n callback: execution=%s status=%s", execution_id, status)
    _log_execution(execution_id, status, data)
    return {"status": "ok"}
```

**JSON persistence pattern** (telegram/webhook.py lines 32-41 `_save_processed_id`):
```python
_EXECUTION_LOG_PATH = Path("data/n8n_executions.json")

def _log_execution(execution_id: str, status: str, data: dict[str, Any]) -> None:
    existing = json.loads(_EXECUTION_LOG_PATH.read_text()) if _EXECUTION_LOG_PATH.exists() else []
    existing.append({
        "execution_id": execution_id,
        "status": status,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _EXECUTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _EXECUTION_LOG_PATH.write_text(json.dumps(existing[-500:], indent=2))
```

**Route registration** — add to `src/api/v1_router.py` (line 7-8 pattern):
```python
from src.api import n8n_callback
# ...
router.include_router(n8n_callback.router)
```

Note: The callback endpoint should NOT require auth (n8n sends the callback, not the owner). However, consider adding a shared secret header validation (like the Telegram webhook secret pattern in `app.py` lines 108-110) for production hardening.

---

### `tests/test_n8n_execution.py` (test)

**Analog:** `tests/test_autopilot.py` (exact — unittest.TestCase, mock patterns, TestClient)

**Imports pattern** (test_autopilot.py lines 1-18):
```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app
```

**Test class structure** — group by component:
```python
class N8NClientTests(unittest.TestCase):
    """Tests for src/n8n/client.py — mock httpx.Client."""

class CredentialTests(unittest.TestCase):
    """Tests for src/n8n/credentials.py — mock n8n_client functions."""

class TemplateTests(unittest.TestCase):
    """Tests for src/n8n/templates.py — use temp directory for JSON files."""

class ExecutorTests(unittest.TestCase):
    """Tests for src/n8n/executor.py — mock client, governor, templates."""

class ErrorTests(unittest.TestCase):
    """Tests for src/n8n/errors.py — pure function tests, no mocks needed."""

class CallbackTests(unittest.TestCase):
    """Tests for src/api/n8n_callback.py — use TestClient."""
```

**Mock pattern for httpx** (follow test_autopilot.py's `patch` usage):
```python
@patch("src.n8n.client.httpx.Client")
def test_trigger_workflow(self, mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"executionId": 42}}
    mock_response.raise_for_status = MagicMock()
    mock_client.request.return_value = mock_response
    # ... call and assert ...
```

**TestClient pattern** (test_autopilot.py uses `TestClient(app)` for endpoint tests):
```python
class CallbackTests(unittest.TestCase):
    def test_callback_logs_execution(self):
        client = TestClient(app)
        response = client.post("/api/v1/webhook/n8n", json={
            "executionId": "42", "status": "success", "data": {"result": "ok"}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
```

**Temp directory for JSON files** (test_autopilot.py lines 75-80):
```python
def setUp(self):
    self.tmpdir = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmpdir.cleanup)
    # Patch data paths to use tmpdir
```

---

### `src/core/config.py` (config, add env vars)

**Analog:** Existing file — add following the established pattern (lines 93-94 for GITHUB_PAT):

```python
# ---------------------------------------------------------------------------
# n8n Execution Engine
# ---------------------------------------------------------------------------
N8N_BASE_URL: str = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY: str = os.environ.get("N8N_API_KEY", "")
```

Place after the GitHub section (around line 95) to keep related integrations grouped.

---

### `src/api/v1_router.py` (route, register callback)

**Analog:** Existing file — add two lines following the established pattern (lines 7-8, 17-18):

```python
from src.api import n8n_callback  # add to import list (line 7)
# ...
router.include_router(n8n_callback.router)  # add after guide.router (line 19)
```

---

## Shared Patterns

### Auth / Environment Gating
**Source:** `src/integrations/github/client.py` lines 31-35
**Apply to:** `src/n8n/client.py`
```python
if not N8N_API_KEY:
    raise EnvironmentError("N8N_API_KEY is not set. Add it to your .env file.")
```
Pattern: Check env var at request time, raise `EnvironmentError` (not `ValueError`), message includes `.env` hint.

### JSON Local-First Persistence
**Source:** `src/integrations/telegram/webhook.py` lines 17-41
**Apply to:** `src/n8n/executor.py` (`_log_unmet_intent`), `src/api/n8n_callback.py` (`_log_execution`)
```python
path = Path("data/some_file.json")
existing = json.loads(path.read_text()) if path.exists() else []
existing.append(new_entry)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(existing[-CAP:], indent=2))
```
Pattern: Load-append-cap-write. Always `mkdir(parents=True, exist_ok=True)`. Always cap at a rolling window (100 or 500 entries).

### RL Governor Gate
**Source:** `src/autopilot/governor.py` lines 46-76
**Apply to:** `src/n8n/executor.py`
```python
from src.autopilot.governor import Governor, ResponsibilityLevel
governor = Governor(ResponsibilityLevel.LEAD_EXECUTOR)
allowed, reason = governor.can_execute("n8n_workflow", {"workflow": name, "intent": intent})
if not allowed:
    return {"status": "needs_approval", ...}
```
Pattern: Instantiate governor at RL4, call `can_execute`, branch on result. Use tool name `"n8n_workflow"` (new entry to add to `_TOOL_RL_REQUIREMENTS` in governor.py).

### FastAPI Router Registration
**Source:** `src/api/autopilot.py` + `src/api/v1_router.py`
**Apply to:** `src/api/n8n_callback.py`
```python
router = APIRouter()
@router.post("/webhook/n8n")
async def n8n_callback(request: Request) -> dict[str, str]:
    ...
```
Then in `v1_router.py`: `router.include_router(n8n_callback.router)`.

### Test Structure
**Source:** `tests/test_autopilot.py`
**Apply to:** `tests/test_n8n_execution.py`
```python
class SomeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
    # unittest.mock.patch for external deps
    # TestClient(app) for endpoint tests
```

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md patterns instead):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/n8n/templates.py` | utility | transform | No template-matching or skeleton-loading pattern exists yet. JSON I/O follows telegram/webhook.py but the matching logic is new domain code. |

## Metadata

**Analog search scope:** `solo-leveling/src/`, `solo-leveling/tests/`
**Files scanned:** 12 (app.py, config.py, v1_router.py, github/client.py, governor.py, dispatcher.py, telegram/webhook.py, autopilot.py, autopilot API, test_autopilot.py, plus directory listings)
**Pattern extraction date:** 2026-05-30
