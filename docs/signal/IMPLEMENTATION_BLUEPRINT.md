# Signal Implementation Blueprint

**Based on:** PRD v1.0 (2026-05-30)
**Target:** Telegram Mini App + solo-leveling backend ecosystem
**Timeline:** 8 phases over 6 months

---

## Executive Summary

This blueprint translates the PRD into actionable implementation steps. Each phase is self-contained, testable, and deployable. The approach is incremental — each phase builds on the previous one's working state.

**Core Principle:** Ship working software every 2 weeks. Never break what already works.

---

## Phase 1: Data & Auth Foundation (COMPLETE)

**Status:** Done
**Duration:** 2 weeks
**Goal:** Establish the data spine and authentication foundation.

### Deliverables

| Deliverable | Status | File |
|-------------|--------|------|
| PostgreSQL + pgvector vector database | Done | `src/vector/db.py` |
| Gemini embedding client (768-dim) | Done | `src/vector/embed.py` |
| Hybrid search (keyword + vector) | Done | `src/vector/search.py` |
| Firebase session cookie auth | Done | `src/api/auth_session.py` |
| Library entry auto-indexing | Done | `src/vector/hooks.py` |
| Token cache for embedding reuse | Done | `src/vector/cache.py` |

### Verification

```bash
# Run all vector tests
python -m unittest tests.test_vector_foundation tests.test_vector_search -v

# Verify vector DB connection
python -c "from src.vector.db import get_pool; print('Pool:', get_pool())"

# Verify embeddings
python -c "from src.vector.embed import embed_text; v = embed_text('test'); print('Dim:', len(v))"
```

---

## Phase 2: n8n Execution Layer (IN PROGRESS)

**Status:** In Progress
**Duration:** 3 weeks
**Goal:** Wire the brain to n8n as the firm execution engine.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    n8n Execution Layer                        │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ client.py   │  │ credentials │  │ templates   │          │
│  │ (REST API)  │  │ (OAuth→n8n) │  │ (skeletons) │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                 │                  │
│  ┌──────▼────────────────▼─────────────────▼──────────────┐ │
│  │ executor.py — Intent → Template → Execute → Result     │ │
│  └──────┬─────────────────────────────────────────────────┘ │
│         │                                                     │
│  ┌──────▼─────────────────────────────────────────────────┐ │
│  │ errors.py — Error → Cause → Soft Message               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Files to Create

| File | Purpose | Lines |
|------|---------|-------|
| `src/n8n/__init__.py` | Package marker | 1 |
| `src/n8n/client.py` | n8n REST API thin client | ~150 |
| `src/n8n/credentials.py` | OAuth → n8n credential injection | ~120 |
| `src/n8n/templates.py` | Template skeleton loader/validator | ~80 |
| `src/n8n/executor.py` | Intent → template → execute orchestrator | ~200 |
| `src/n8n/errors.py` | Error classification + soft messages | ~100 |
| `src/api/n8n_callback.py` | Webhook callback endpoint | ~60 |
| `tests/test_n8n_execution.py` | Unit tests | ~300 |
| `src/n8n/templates/*.json` | Starter skeletons | ~2 files |

### Implementation Steps

#### Step 1: n8n REST Client (`src/n8n/client.py`)

**Pattern:** Follow `src/integrations/github/client.py`

```python
"""
n8n REST API client.

Requires N8N_BASE_URL and N8N_API_KEY environment variables.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

def _get_config() -> tuple[str, str]:
    base_url = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
    api_key = os.environ.get("N8N_API_KEY", "")
    if not api_key:
        raise EnvironmentError("N8N_API_KEY is not set.")
    return base_url, api_key

def _headers() -> dict[str, str]:
    _, api_key = _get_config()
    return {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
    }

def _request(method: str, path: str, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
    base_url, _ = _get_config()
    url = f"{base_url}/api/v1{path}"
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
    payload = {"data": data or {}}
    return _request("POST", f"/workflows/{workflow_id}/run", json=payload)

def get_execution(execution_id: int | str) -> dict[str, Any]:
    return _request("GET", f"/executions/{execution_id}")

def list_executions(workflow_id: int | str | None = None, status: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"limit": limit}
    if workflow_id:
        params["workflowId"] = workflow_id
    if status:
        params["status"] = status
    result = _request("GET", "/executions", params=params)
    return result.get("data", [])

def create_credential(name: str, cred_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/credentials", json={"name": name, "type": cred_type, "data": data})

def update_credential(cred_id: int | str, name: str, cred_type: str, data: dict[str, Any]) -> dict[str, Any]:
    return _request("PUT", f"/credentials/{cred_id}", json={"name": name, "type": cred_type, "data": data})

def list_credentials() -> list[dict[str, Any]]:
    result = _request("GET", "/credentials")
    return result.get("data", [])

def health_check() -> dict[str, Any]:
    try:
        _request("GET", "/workflows", params={"limit": 1})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

#### Step 2: Credential Injection (`src/n8n/credentials.py`)

**Purpose:** Pull OAuth tokens from existing integration clients, push into n8n credential store.

```python
"""
Credential injection: OAuth tokens → n8n credential store.

Syncs brain's integration tokens into n8n so workflows can use them
without the owner ever seeing raw keys.
"""

from __future__ import annotations

import logging
from typing import Any

from src.n8n import client as n8n_client

logger = logging.getLogger(__name__)

_CREDENTIAL_TYPE_MAP: dict[str, str] = {
    "gmail": "gmailOAuth2",
    "gdrive": "googleDriveOAuth2Api",
    "github": "githubApi",
    "notion": "notionApi",
    "telegram": "telegramApi",
    "discord": "discordBotApi",
}

def sync_credential(integration: str, token_data: dict[str, Any], owner_id: str = "default-owner") -> int:
    cred_type = _CREDENTIAL_TYPE_MAP.get(integration)
    if not cred_type:
        raise ValueError(f"Unknown integration: {integration}")

    cred_name = f"signal-{owner_id}-{integration}"
    existing = _find_credential_by_name(cred_name)
    n8n_data = _map_token_to_n8n_credential(integration, token_data)

    if existing:
        result = n8n_client.update_credential(existing["id"], cred_name, cred_type, n8n_data)
        logger.info("Updated n8n credential for %s (id=%s)", integration, existing["id"])
        return result["id"]
    else:
        result = n8n_client.create_credential(cred_name, cred_type, n8n_data)
        logger.info("Created n8n credential for %s (id=%s)", integration, result["id"])
        return result["id"]

def _find_credential_by_name(name: str) -> dict[str, Any] | None:
    creds = n8n_client.list_credentials()
    for c in creds:
        if c.get("name") == name:
            return c
    return None

def _map_token_to_n8n_credential(integration: str, token_data: dict[str, Any]) -> dict[str, Any]:
    if integration == "gmail":
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
        return {"accessToken": token_data.get("token", "")}
    elif integration == "notion":
        return {"apiKey": token_data.get("token", "")}
    elif integration == "telegram":
        return {"accessToken": token_data.get("token", "")}
    return token_data
```

#### Step 3: Template Skeletons (`src/n8n/templates.py`)

**Purpose:** Load, validate, and match template skeletons.

```python
"""
Template skeleton loader and matcher.

Templates are JSON files defining n8n workflow skeletons that the brain
can parameterize and execute.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"

def load_all_templates() -> list[dict[str, Any]]:
    templates = []
    for path in _TEMPLATES_DIR.glob("*.json"):
        try:
            template = json.loads(path.read_text(encoding="utf-8"))
            template["_path"] = str(path)
            templates.append(template)
        except Exception:
            logger.warning("Failed to load template: %s", path)
    return templates

def match_template(intent: str) -> dict[str, Any] | None:
    templates = load_all_templates()
    intent_lower = intent.lower()
    
    # Exact match first
    for t in templates:
        if t.get("intent") == intent:
            return t
    
    # Keyword match
    for t in templates:
        keywords = t.get("keywords", [])
        if any(kw.lower() in intent_lower for kw in keywords):
            return t
    
    return None

def fill_parameters(skeleton: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Fill template parameters into skeleton. Returns n8n workflow JSON."""
    workflow = skeleton.get("workflow", {})
    
    # Simple parameter substitution
    def _replace(obj: Any) -> Any:
        if isinstance(obj, str):
            for key, value in params.items():
                obj = obj.replace(f"{{{{{key}}}}}", str(value))
            return obj
        elif isinstance(obj, dict):
            return {k: _replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_replace(item) for item in obj]
        return obj
    
    return _replace(workflow)
```

#### Step 4: Error Abstraction (`src/n8n/errors.py`)

**Purpose:** Translate technical errors into soft, owner-friendly messages.

```python
"""
Error abstraction layer.

Translates technical n8n/backend errors into soft, actionable messages
for the AI Guide to present to the owner.
"""

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

_SOFT_MESSAGES: dict[ErrorClass, str] = {
    ErrorClass.CREDENTIAL_EXPIRED: "Your {integration} connection may have expired. Would you like to reconnect?",
    ErrorClass.CREDENTIAL_REVOKED: "Your {integration} access was revoked. You'll need to reconnect to continue.",
    ErrorClass.INTEGRATION_NOT_CONNECTED: "You haven't connected {integration} yet. Let's set that up first.",
    ErrorClass.N8N_UNREACHABLE: "The execution engine isn't responding right now. It may need a restart.",
    ErrorClass.WORKFLOW_NOT_FOUND: "I couldn't find that workflow — it may have been removed.",
    ErrorClass.RATE_LIMITED: "Too many requests at once. Let's wait a moment and try again.",
    ErrorClass.UNKNOWN: "Something went wrong with that action. I've logged it — try again in a bit.",
}

def classify_error(error_data: dict[str, Any]) -> ErrorClass:
    error_str = str(error_data).lower()
    for pattern, error_class in _ERROR_PATTERNS:
        if pattern.lower() in error_str:
            return error_class
    return ErrorClass.UNKNOWN

def soft_error_message(error_class: ErrorClass, intent: str = "", integration: str = "") -> str:
    template = _SOFT_MESSAGES.get(error_class, _SOFT_MESSAGES[ErrorClass.UNKNOWN])
    return template.format(integration=integration or "that app")
```

#### Step 5: Orchestrator (`src/n8n/executor.py`)

**Purpose:** Tie everything together — intent → template → RL gate → execute → result.

```python
"""
n8n execution orchestrator.

Coordinates: intent detection → template matching → parameter filling →
RL approval gate → n8n triggering → result handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from src.n8n import client as n8n_client
from src.n8n import credentials as n8n_creds
from src.n8n import templates as n8n_templates
from src.n8n.errors import classify_error, soft_error_message

logger = logging.getLogger(__name__)

_MAX_RETRIES = 1

async def execute_intent(intent: str, params: dict[str, Any], owner_id: str = "default-owner") -> dict[str, Any]:
    # 1. Match intent to template
    skeleton = n8n_templates.match_template(intent)
    if not skeleton:
        _log_unmet_intent(intent, params)
        return {"status": "declined", "message": "I can't do that yet — but I've noted it for a future update."}

    # 2. Fill parameters
    workflow_json = n8n_templates.fill_parameters(skeleton, params)

    # 3. Check if side-effecting → RL gate
    if skeleton.get("side_effecting", False):
        from src.autopilot.governor import Governor, ResponsibilityLevel
        governor = Governor(ResponsibilityLevel.LEAD_EXECUTOR)
        allowed, reason = governor.can_execute("n8n_workflow", {"workflow": skeleton["name"], "intent": intent})
        if not allowed:
            return {"status": "needs_approval", "message": f"This action needs your approval: {skeleton.get('description', intent)}", "approval_context": {"intent": intent, "skeleton": skeleton["id"]}}

    # 4. Trigger n8n workflow
    workflow_id = skeleton["n8n_workflow_id"]
    try:
        result = n8n_client.trigger_workflow(workflow_id, data=workflow_json)
        execution_id = result.get("data", {}).get("executionId")
        logger.info("n8n workflow %s triggered, execution=%s", workflow_id, execution_id)

        # 5. Wait for completion
        if execution_id:
            exec_result = await _poll_execution(execution_id)
            if exec_result.get("status") == "success":
                return {"status": "ok", "result": exec_result.get("data")}
            else:
                return await _retry_and_report(workflow_id, workflow_json, exec_result, intent)

        return {"status": "ok", "result": result}

    except Exception as e:
        logger.exception("n8n execution failed for intent=%s", intent)
        return await _retry_and_report(workflow_id, workflow_json, {"error": str(e)}, intent)

async def _poll_execution(execution_id: int | str, max_wait: int = 30) -> dict[str, Any]:
    for _ in range(max_wait):
        exec_data = n8n_client.get_execution(execution_id)
        status = exec_data.get("data", {}).get("status", "")
        if status in ("success", "error", "crashed", "waiting"):
            return exec_data.get("data", {})
        await asyncio.sleep(1)
    return {"status": "timeout"}

async def _retry_and_report(workflow_id: int | str, workflow_json: dict, first_result: dict, intent: str) -> dict[str, Any]:
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

    error_class = classify_error(first_result)
    return {"status": "error", "message": soft_error_message(error_class, intent)}

def _log_unmet_intent(intent: str, params: dict[str, Any]) -> None:
    log_path = Path("data/unmet_intents.json")
    try:
        existing = json.loads(log_path.read_text()) if log_path.exists() else []
    except (json.JSONDecodeError, OSError):
        existing = []
    existing.append({"intent": intent, "params": params})
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(existing[-100:], indent=2))
```

#### Step 6: Webhook Callback (`src/api/n8n_callback.py`)

**Purpose:** Receive n8n execution results via webhook.

```python
"""
n8n execution callback endpoint.

Receives execution results from n8n webhook nodes.
"""

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

def _log_execution(execution_id: str, status: str, data: dict[str, Any]) -> None:
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
    _EXECUTION_LOG_PATH.write_text(json.dumps(existing[-500:], indent=2))
```

#### Step 7: Template Skeletons

Create starter templates in `src/n8n/templates/`:

**`gmail_read_summary.json`** (read-only):
```json
{
  "id": "gmail-read-summary",
  "name": "Gmail Read & Summarize",
  "description": "Read recent emails and summarize them",
  "intent": "gmail_summary",
  "keywords": ["email", "gmail", "inbox", "unread"],
  "side_effecting": false,
  "n8n_workflow_id": "PLACEHOLDER",
  "workflow": {
    "nodes": [
      {"name": "Gmail", "type": "n8n-nodes-base.gmail", "parameters": {"operation": "getAll", "limit": 10}},
      {"name": "Summarize", "type": "n8n-nodes-base.code", "parameters": {"jsCode": "return items.map(item => ({json: {subject: item.json.subject, snippet: item.json.snippet}}));"}}
    ]
  }
}
```

**`gmail_send_draft.json`** (side-effecting):
```json
{
  "id": "gmail-send-draft",
  "name": "Gmail Send Draft",
  "description": "Send a drafted email reply",
  "intent": "gmail_send",
  "keywords": ["send", "reply", "draft"],
  "side_effecting": true,
  "n8n_workflow_id": "PLACEHOLDER",
  "workflow": {
    "nodes": [
      {"name": "Gmail", "type": "n8n-nodes-base.gmail", "parameters": {"operation": "send"}}
    ]
  }
}
```

#### Step 8: Configuration

Add to `.env.example`:
```bash
# n8n Execution Engine
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=
```

#### Step 9: Route Registration

Add to `src/app.py`:
```python
from src.api.n8n_callback import router as n8n_callback_router
app.include_router(n8n_callback_router)
```

#### Step 10: Unit Tests

Create `tests/test_n8n_execution.py` with test classes for:
- `N8NClientTests` — mock httpx.Client, verify API calls
- `CredentialTests` — mock n8n_client, verify token mapping
- `TemplateTests` — test template loading and parameter filling
- `ExecutorTests` — mock all dependencies, verify orchestration flow
- `ErrorTests` — test error classification and soft messages
- `CallbackTests` — use TestClient, verify webhook handling

### Verification

```bash
# Run n8n tests
python -m unittest tests.test_n8n_execution -v

# Verify n8n connectivity (requires running n8n)
python -c "from src.n8n.client import health_check; print(health_check())"

# Verify credential sync (requires running n8n + Gmail token)
python -c "from src.n8n.credentials import sync_credential; print('Sync OK')"
```

---

## Phase 3: Knowledge Library + Conceptual Search + AI Guide

**Status:** Not Started
**Duration:** 3 weeks
**Goal:** Transform the library from file-based to AI-powered knowledge system.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Guide Layer                            │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Conversational│  │ Contextual  │  │ Synthesis   │          │
│  │ Interface   │  │ Actions     │  │ Engine      │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                 │                  │
│  ┌──────▼────────────────▼─────────────────▼──────────────┐ │
│  │ Enhanced Vector Search (re-ranking, semantic chunks)   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| Enhanced vector search | Re-ranking with cross-encoder, semantic chunking |
| AI Guide conversational | Persistent chat context, memory, personality |
| Contextual actions | Suggest actions based on current view/content |
| Library synthesis | Multi-entry Q&A with source citations |
| Graph enhancements | Interactive filtering, clustering, path finding |

### Files to Modify

| File | Changes |
|------|---------|
| `src/vector/search.py` | Add re-ranking, semantic chunking |
| `src/api/guide.py` | Add conversational context, memory |
| `src/api/library.py` | Add synthesis improvements |
| `dashboard/src/components/graph/` | Add interactivity |

---

## Phase 4: Telegram Mini App

**Status:** Not Started
**Duration:** 4 weeks
**Goal:** Make Signal available as a Telegram Mini App.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Mini App                          │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ React App   │  │ Telegram    │  │ Auth Flow   │          │
│  │ (Vite)      │  │ WebApp API  │  │ (Firebase)  │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                 │                  │
│  ┌──────▼────────────────▼─────────────────▼──────────────┐ │
│  │ Mobile-Optimized Layout (bottom nav, swipe gestures)   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| Telegram Mini App frontend | React + Telegram WebApp API |
| Mobile-optimized layout | Bottom nav, swipe gestures, pull-to-refresh |
| Telegram auth flow | Telegram Login Widget → Firebase custom token |
| Push notifications | Telegram bot for alerts and approvals |
| Inline keyboard | Quick actions directly in Telegram |

### New Repository

Create `signal-miniapp/` as a new submodule:
- React 19 + TypeScript + Vite
- Telegram WebApp SDK
- Shared API client with dashboard
- Mobile-first design system

### Key Files

```
signal-miniapp/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── Home.tsx
│   │   ├── Library.tsx
│   │   ├── Planner.tsx
│   │   ├── Chat.tsx
│   │   └── Settings.tsx
│   ├── hooks/
│   │   ├── useTelegram.ts
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── telegram.ts
│   │   └── firebase.ts
│   └── styles/
│       └── globals.css
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### Telegram-Specific Features

1. **Haptic Feedback:** `Telegram.WebApp.HapticFeedback` for action confirmations
2. **Main Button:** `Telegram.WebApp.MainButton` for primary actions
3. **Back Button:** `Telegram.WebApp.BackButton` for navigation
4. **Swipe Gestures:** Custom touch handlers for card actions
5. **Safe Areas:** `env(safe-area-inset-*)` for notch/home indicator

---

## Phase 5: Digest Engine

**Status:** Not Started
**Duration:** 3 weeks
**Goal:** Automated daily digest generation and delivery.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Digest Engine                              │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Collector   │  │ Processor   │  │ Assembler   │          │
│  │ (Gmail, RSS)│  │ (LLM, PII)  │  │ (Cards)     │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                 │                  │
│  ┌──────▼────────────────▼─────────────────▼──────────────┐ │
│  │ Scheduler (APScheduler, 6 AM user TZ)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| Gmail inbox summarization | Last 24h, unread + flagged, max 50 |
| Priority scoring | Critical Focus Block ranking algorithm |
| PII redaction | Regex + NER, token replacement |
| LLM summarization | 3 bullets max, 1 sentence each |
| Digest assembly | Critical Focus Block + Context Nest cards |
| Scheduled delivery | APScheduler, 6 AM user TZ |
| Engagement tracking | Open time, dwell time, actions taken |

### Files to Create

| File | Purpose |
|------|---------|
| `src/digest/collector.py` | Collect data from sources |
| `src/digest/processor.py` | Filter, deduplicate, summarize |
| `src/digest/assembler.py` | Assemble digest cards |
| `src/digest/redactor.py` | PII redaction pipeline |
| `src/digest/scheduler.py` | Scheduled delivery |
| `src/api/digest.py` | REST endpoints |

---

## Phase 6: Smart Feeds

**Status:** Not Started
**Duration:** 3 weeks
**Goal:** Noise-free content consumption.

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| YouTube transcript abstraction | Pull transcripts, compress to 3-bullet cards |
| RSS feed subscription | Configurable feed management |
| News deduplication | Vector similarity >0.85 → merge |
| Feed item compression | LLM-powered 3-bullet summaries |
| Silent queueing | Queue for reading routines |

### Files to Create

| File | Purpose |
|------|---------|
| `src/feeds/youtube.py` | YouTube transcript abstraction |
| `src/feeds/rss.py` | RSS feed processing |
| `src/feeds/dedup.py` | News deduplication |
| `src/feeds/compressor.py` | Feed item compression |
| `src/api/feeds.py` | REST endpoints |

---

## Phase 7: Smart Drafts

**Status:** Not Started
**Duration:** 3 weeks
**Goal:** Context-aware reply generation.

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| Email thread context | Fetch full history, last 10 messages |
| User style profile | Analyze last 10 sent emails |
| Relationship context | Last interaction date, topic history |
| Draft generation | Subject line, body, suggested send time |
| Tone variants | Approve, Friendlier, Firmer, Shorter, Longer |
| Draft scheduling | Queue for optimal send time |

### Files to Create

| File | Purpose |
|------|---------|
| `src/drafts/context.py` | Context gathering |
| `src/drafts/style.py` | Style profile analysis |
| `src/drafts/generator.py` | Draft generation |
| `src/drafts/scheduler.py` | Draft scheduling |
| `src/api/drafts.py` | REST endpoints |

---

## Phase 8: Polish & Launch

**Status:** Not Started
**Duration:** 4 weeks
**Goal:** Production hardening and public launch.

### Deliverables

| Deliverable | Description |
|-------------|-------------|
| Security audit | STRIDE review, penetration testing |
| Performance testing | k6 load tests, Lighthouse CI |
| E2E test suite | Playwright, critical user journeys |
| Error monitoring | Sentry or similar |
| Status page | status.signal.app |
| Landing page | Marketing site |
| Billing integration | Stripe, subscription management |
| GDPR compliance | Data export, deletion, consent |

### Testing Strategy

```bash
# Unit tests (80% coverage target)
python -m unittest discover -s tests -v

# Integration tests
python -m unittest tests.test_integration_smoke -v

# E2E tests
npx playwright test

# Performance tests
k6 run tests/performance/load.js

# Security scan
trivy fs --security-checks vuln .
```

---

## Dependencies & Setup

### Python Dependencies

Add to `requirements.txt`:
```bash
# Existing
fastapi
uvicorn
httpx
python-dotenv
google-genai
psycopg[binary]
pgvector
litellm

# New (Phase 2+)
pydantic>=2.0
python-telegram-bot>=20.0
```

### Frontend Dependencies

Add to `dashboard/package.json`:
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tailwindcss": "^4.0.0",
    "firebase": "^10.0.0",
    "lucide-react": "^0.400.0"
  }
}
```

### Environment Variables

Add to `.env.example`:
```bash
# n8n Execution Engine
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=

# Digest Engine
DIGEST_ENABLED=false
DIGEST_HOUR=6
DIGEST_TIMEZONE=Asia/Jakarta

# Smart Feeds
FEED_YOUTUBE_ENABLED=false
FEED_RSS_ENABLED=false

# Smart Drafts
DRAFT_ENABLED=false
DRAFT_MAX_CONTEXT_EMAILS=10
```

---

## Deployment Strategy

### Development

```bash
# Backend
cd solo-leveling
source .venv/bin/activate
uvicorn src.app:app --port 8000 --reload

# Frontend
cd dashboard
bun run dev

# n8n
docker compose -f docker-compose.n8n.yml up -d
```

### Staging

```bash
# Backend (Docker)
cd solo-leveling
docker compose up -d

# Frontend (GitHub Pages)
cd dashboard
bun run build
# Auto-deployed via GitHub Actions

# n8n (Docker)
docker compose -f docker-compose.n8n.yml up -d
```

### Production

```bash
# Backend (MacMini Docker)
cd solo-leveling
docker compose up -d

# Frontend (GitHub Pages)
# Auto-deployed via GitHub Actions

# n8n (MacMini Docker)
docker compose -f docker-compose.n8n.yml up -d
```

---

## Success Metrics

### Phase 2 (n8n)

- [ ] n8n REST client passes all unit tests
- [ ] Credential injection works for Gmail, GitHub, Notion
- [ ] Template matching returns correct skeleton for 5 test intents
- [ ] Error abstraction produces soft messages for 7 error classes
- [ ] Webhook callback logs execution results

### Phase 3 (Library + AI Guide)

- [ ] Vector search re-ranking improves relevance by 20%
- [ ] AI Guide maintains conversation context across 10 messages
- [ ] Contextual actions suggest relevant actions for 5 view types
- [ ] Library synthesis answers questions with source citations

### Phase 4 (Telegram Mini App)

- [ ] Mini App loads in <2s on 3G
- [ ] All 5 primary views work on mobile
- [ ] Telegram auth flow completes in <3 taps
- [ ] Push notifications deliver within 30s

### Phase 5 (Digest)

- [ ] Digest generates in <60s for 50 emails
- [ ] PII redaction catches 99% of emails, phones, names
- [ ] Priority scoring ranks urgent emails in top 3
- [ ] Scheduled delivery triggers at 6 AM user TZ

### Phase 6 (Smart Feeds)

- [ ] YouTube transcript abstracted in <10s
- [ ] Deduplication merges 90% of similar articles
- [ ] Feed compression produces 3-bullet cards
- [ ] Silent queueing delivers at reading routine time

### Phase 7 (Smart Drafts)

- [ ] Draft generation completes in <10s
- [ ] Style profile matches 80% of user's tone
- [ ] Tone variants produce distinct drafts
- [ ] Draft scheduling respects calendar availability

### Phase 8 (Polish)

- [ ] Security audit passes with 0 critical findings
- [ ] Performance budgets met (FCP <1.2s, LCP <2.5s)
- [ ] E2E tests cover 100% of P0 flows
- [ ] GDPR compliance verified by legal review

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| n8n API instability | Pin n8n version, maintain Signal-native schema fallback |
| LLM cost spike | Implement cost caps, caching, fallback to cheaper models |
| OAuth token expiry | Auto-refresh, graceful degradation, user notification |
| Vector DB performance | Connection pooling, query optimization, caching |
| Telegram Mini App limits | Progressive enhancement, offline-first, graceful degradation |

---

## Timeline

| Phase | Duration | Start | End | Dependencies |
|-------|----------|-------|-----|--------------|
| Phase 1 | 2 weeks | Done | Done | — |
| Phase 2 | 3 weeks | Week 3 | Week 5 | Phase 1 |
| Phase 3 | 3 weeks | Week 6 | Week 8 | Phase 2 |
| Phase 4 | 4 weeks | Week 9 | Week 12 | Phase 3 |
| Phase 5 | 3 weeks | Week 13 | Week 15 | Phase 4 |
| Phase 6 | 3 weeks | Week 16 | Week 18 | Phase 5 |
| Phase 7 | 3 weeks | Week 19 | Week 21 | Phase 6 |
| Phase 8 | 4 weeks | Week 22 | Week 25 | Phase 7 |

**Total:** 25 weeks (6 months)

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-30 | Signal Team | Initial implementation blueprint |

**Next Review Date:** 2026-06-15
**Distribution:** Core team, engineering leads
