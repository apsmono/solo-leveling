# Phase 1: Data & Auth Foundation - Pattern Map

**Mapped:** 2026-05-29
**Files analyzed:** 8 new/modified files
**Analogs found:** 7 / 8

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/vector/__init__.py` | module-init / export facade | — | `src/api/__init__.py` (empty) + `src/core/libraries.py` public surface | role-match |
| `src/vector/db.py` | store / client | CRUD (async pool lifecycle) | `src/core/library_store.py` — module-level singleton + lazy init pattern | role-match |
| `src/vector/embed.py` | client / utility | request-response (Gemini API) | `src/agents/dispatcher.py` — env-gated singleton client, `_get_*` lazy init, `EnvironmentError` on missing key | exact |
| `src/vector/cache.py` | service | CRUD + request-response | `src/core/library_store.py` `_FirestoreLibraryStore._save_to_firestore` — best-effort async write + `src/agents/dispatcher.py` — wraps `run_agent` | role-match |
| `src/vector/migrations/001_init_vector.sql` | migration | batch (startup) | `docker-compose.n8n.yml` patterns (no Python analog; raw SQL is greenfield) | no-analog |
| `src/api/auth_session.py` | route | request-response | `src/api/library.py` — `APIRouter`, `Depends(require_auth)`, `HTTPException`, `from src.integrations.firebase.auth import verify_id_token` | exact |
| `src/app.py` (modify lifespan) | config / wiring | — | `src/app.py` itself — `@asynccontextmanager async def lifespan` block | self-analog (modify) |
| `.env.example` + `src/core/config.py` (extend) | config | — | `.env.example` + `src/core/config.py` — `os.environ.get`, `_get_bool`, `require()` pattern | self-analog (extend) |

---

## Pattern Assignments

### `src/vector/db.py` (store, async CRUD)

**Analog:** `src/core/library_store.py` (module-level singleton + lazy init) and `src/agents/dispatcher.py` (env-gated init guard)

**Imports pattern** — follow `dispatcher.py` lines 1-8 and `library_store.py` lines 1-14:
```python
from __future__ import annotations

import logging
from pathlib import Path

import psycopg
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

logger = logging.getLogger(__name__)
```

**Module-level singleton pattern** — mirror `dispatcher.py` lines 30, 61-66 (`PROVIDER` constant + guard before use) and `library_store.py` `_FirestoreLibraryStore.__init__` (private `_pool` state):
```python
_pool: AsyncConnectionPool | None = None

async def open_pool(dsn: str) -> None:
    global _pool
    # ... open and register
    logger.info("Vector DB pool ready.")

def get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Vector DB pool not initialised. Call open_pool() first.")
    return _pool
```

**EnvironmentError on missing config** — mirror `dispatcher.py` lines 64-66:
```python
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY is not set.")
```
Apply same pattern for `SIGNAL_POSTGRES_DSN`:
```python
dsn = os.environ.get("SIGNAL_POSTGRES_DSN")
if not dsn:
    raise EnvironmentError("SIGNAL_POSTGRES_DSN is not set.")
```

**Migration helper** — private prefix `_apply_migrations`, reads SQL from `Path(__file__).parent / "migrations" / "001_init_vector.sql"`. The `Path(__file__).resolve().parents[N]` root-resolution idiom comes from `src/api/library.py` line 19: `_PROJECT_ROOT = Path(__file__).resolve().parents[2]`.

---

### `src/vector/embed.py` (client, request-response)

**Analog:** `src/agents/dispatcher.py` — this is the closest pattern in the entire codebase: env-gated singleton, lazy `_get_client()`, `EnvironmentError` on missing key, `logger.info` on success.

**Imports pattern** (mirror `dispatcher.py` lines 1-8, no `from __future__` in dispatcher — add it as required by CLAUDE.md):
```python
from __future__ import annotations

import hashlib
import logging
import os
from typing import Literal

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)
```

**Lazy singleton client** — mirror `dispatcher.py` lines 61-66 exactly:
```python
_EMBED_MODEL = "gemini-embedding-001"
_EMBED_DIM = 768
_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=api_key)
    return _client
```

Note: `dispatcher.py` does NOT have `from __future__ import annotations` at the top (line 1 is the docstring, line 23 is `import os`). New files MUST add it per `solo-leveling/CLAUDE.md` conventions.

**Logging on success** — mirror `dispatcher.py` lines 92-93:
```python
logger.info("Gemini agent responded (%d chars).", len(result))
```
For embed: `logger.info("Embedded text (%d chars) → %d-dim vector.", len(text), len(values))`

---

### `src/vector/cache.py` (service, CRUD + request-response)

**Analog:** `src/core/library_store.py` `_FirestoreLibraryStore._save_to_firestore` (lines 455-493) — best-effort async write pattern; `src/agents/dispatcher.py` `run_agent` — the function being wrapped.

**Imports pattern**:
```python
from __future__ import annotations

import logging
from typing import Any

from src.vector.db import get_pool
from src.vector.embed import content_hash, embed_text

logger = logging.getLogger(__name__)
```

**Best-effort / never-raise pattern** — mirror `library_store.py` lines 467-493:
```python
def _save_to_firestore(self, ...) -> None:
    """Best-effort Firestore write. Never raises."""
    try:
        from src.integrations.firebase.firestore import save_library_entry
        save_library_entry(...)
    except Exception:
        logger.warning("Firestore library write failed", exc_info=True)
```
Apply to `store_cache`: catch `Exception`, log with `logger.warning(..., exc_info=True)`, never propagate.

**Owner-scoping pattern** — every DB query is scoped by `owner_id`. Read from `os.environ.get("SIGNAL_OWNER_ID", ALLOWED_USER_EMAIL)` (see config pattern below). Default constant `_DEFAULT_OWNER` follows the private-prefix convention from CLAUDE.md.

---

### `src/api/auth_session.py` (route, request-response)

**Analog:** `src/api/library.py` — this is the exact pattern to follow for all new route files.

**Imports pattern** — mirror `library.py` lines 1-17:
```python
from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status

from src.integrations.firebase.auth import verify_id_token, _init_firebase

router = APIRouter()
```

**Router definition** — `router = APIRouter()` (no prefix — prefix is added in `v1_router.py`). However, auth routes are NOT under `/api/v1/` prefix (they are top-level `/auth/...`). Register directly on `app` in `src/app.py` rather than via `v1_router.py`, following the same pattern as `app.include_router(v1_router)` at `app.py` line 69.

**Auth verification pattern** — mirror `auth.py` lines 43-67 (`verify_id_token` raises `HTTPException(401)` on bad token, `HTTPException(403)` on wrong email). The new endpoint calls `verify_id_token(id_token)` first, then `create_session_cookie`.

**HTTPException pattern** — mirror `library.py` lines 183-184:
```python
if not data:
    raise HTTPException(status_code=404, detail="Entry not found.")
```
For missing idToken:
```python
if not id_token:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing idToken.")
```

**Return shape** — all existing routes return `dict[str, Any]` or `dict[str, str]`. Mirror the simple `{"status": "ok"}` shape used in `app.py` line 74 and `app.py` line 88.

**Firebase lazy init guard** — mirror `auth.py` lines 22-40 (`_init_firebase()` is called inside the handler, not at import time). The session-login endpoint calls `_init_firebase()` before using `firebase_admin.auth`:
```python
# From auth.py lines 22-40 — call _init_firebase() before any firebase_admin usage
_init_firebase()
import firebase_admin.auth as fb_auth
cookie = fb_auth.create_session_cookie(id_token, expires_in=_SESSION_DURATION)
```

---

### `src/app.py` — lifespan modification (config / wiring)

**Analog:** `src/app.py` itself — extend the existing `lifespan` function at lines 36-43.

**Existing lifespan pattern** (lines 36-43):
```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    _startup_checks()
    start_scheduler()
    await start_discord_bot()
    yield
    await stop_discord_bot()
    shutdown_scheduler()
```

**Addition pattern** — add two lines mirroring the existing `start_scheduler()` / `shutdown_scheduler()` symmetry:
```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    _startup_checks()
    start_scheduler()
    await start_discord_bot()
    await db.open_pool(SIGNAL_POSTGRES_DSN)   # ADD — before yield
    yield
    await db.close_pool()                      # ADD — before other shutdowns
    await stop_discord_bot()
    shutdown_scheduler()
```

**Router registration pattern** — mirror `app.py` lines 67-69 (`from src.api.v1_router import router as v1_router` + `app.include_router(v1_router)`). Auth session router registers at top-level (not under `/api/v1`):
```python
from src.api.auth_session import router as auth_router
app.include_router(auth_router)
```
Place this import block next to the existing `from src.api.v1_router import router as v1_router` at lines 67-69.

---

### `src/core/config.py` — extension (config)

**Analog:** `src/core/config.py` itself — extend the existing pattern.

**Existing env-var pattern** (lines 47-105) — all vars use `os.environ.get(KEY, default)` or `_get_bool`/`_get_int` helpers. New vars follow the same grouping-by-section layout:
```python
# ---------------------------------------------------------------------------
# Signal / Vector DB
# ---------------------------------------------------------------------------
SIGNAL_POSTGRES_DSN: str = os.environ.get("SIGNAL_POSTGRES_DSN", "")
SIGNAL_OWNER_ID: str = os.environ.get("SIGNAL_OWNER_ID", ALLOWED_USER_EMAIL)
SIGNAL_COSINE_THRESHOLD: float = float(os.environ.get("SIGNAL_COSINE_THRESHOLD", "0.08"))
```

Note: `SIGNAL_OWNER_ID` defaults to `ALLOWED_USER_EMAIL` (already loaded at line 66), which is the RESEARCH.md recommendation (Open Question 3 resolution: use email as owner_id string today).

**`require()` function** (lines 36-44) — use for any variable that must be set for the process to function. `SIGNAL_POSTGRES_DSN` should be a soft fail (empty string allows the process to start without vector DB when not yet provisioned); raise at `open_pool()` call time instead.

---

### `.env.example` — extension (config)

**Analog:** `.env.example` itself — extend with a new section.

**Existing section pattern** (lines 61-76):
```
# Firebase
# Path to service account JSON or inline JSON for Admin SDK
FIREBASE_CREDENTIALS_PATH=./.credentials/firebase/service_account.json
FIREBASE_CREDENTIALS_JSON=
...
```

**New section to append**:
```
# Signal / Vector DB (Phase 1)
# Postgres connection string for pgvector (use pgvector/pgvector:pg16 image)
SIGNAL_POSTGRES_DSN=postgresql://signal:changeme@localhost:5432/signal
# Owner identifier — defaults to ALLOWED_USER_EMAIL if not set
SIGNAL_OWNER_ID=
# Cosine distance threshold for token-cache dedup (0.08 ≈ similarity 0.92)
SIGNAL_COSINE_THRESHOLD=0.08
# Test DSN for integration tests (skipped if not set)
SIGNAL_POSTGRES_DSN_TEST=
```

---

### `tests/test_vector_foundation.py` (test)

**Analog:** `tests/test_stage9_libraries.py` and `tests/test_integration_smoke.py` — both use stdlib `unittest.TestCase`, `from __future__ import annotations`, `unittest.mock.patch`, and `patch.dict(os.environ, {...}, clear=True)` for env isolation.

**File header pattern** — mirror `test_integration_smoke.py` lines 1-18:
```python
from __future__ import annotations

import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from dotenv import load_dotenv
load_dotenv()
```

**TestCase class pattern** — mirror `test_stage9_libraries.py` lines 12-33:
```python
class VectorDBTests(unittest.TestCase):
    def setUp(self) -> None:
        # patch module-level _pool to None for isolation
        ...
    def tearDown(self) -> None:
        ...
```

**Env isolation pattern** — mirror `test_integration_smoke.py` lines 62-74:
```python
with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
    result = embed_text("hello")
```

**Async test pattern** — `unittest` does not natively support `async def test_*`. Use `asyncio.run()` wrapper inside synchronous test methods (no pytest-asyncio needed):
```python
import asyncio

class TokenCacheTests(unittest.TestCase):
    def test_cache_miss_returns_none(self) -> None:
        async def _run():
            with patch("src.vector.cache.get_pool") as mock_pool:
                mock_pool.return_value.__aenter__ = AsyncMock(...)
                result = await check_cache("text", owner_id="test-owner")
                self.assertIsNone(result)
        asyncio.run(_run())
```

**Skip pattern for integration tests** — mirror `test_integration_smoke.py` `@unittest.skipUnless(os.environ.get("ENABLE_LIVE_SMOKE_TESTS"), ...)`:
```python
@unittest.skipUnless(
    os.environ.get("SIGNAL_POSTGRES_DSN_TEST"),
    "SIGNAL_POSTGRES_DSN_TEST not set — skipping vector integration tests",
)
class VectorDBIntegrationTests(unittest.TestCase):
    ...
```

---

## Shared Patterns

### `from __future__ import annotations` (all new `.py` files)
**Source:** Every existing file in `src/` that has it — `library_store.py` line 3, `auth.py` line 3, `library.py` line 3, `deps.py` line 3.
**Apply to:** All new files: `db.py`, `embed.py`, `cache.py`, `auth_session.py`, `test_vector_foundation.py`.
**Note:** `dispatcher.py` is the one exception — it is missing `from __future__ import annotations`. Do not copy that omission.

### `logger = logging.getLogger(__name__)` (all new `.py` files)
**Source:** `auth.py` line 17, `dispatcher.py` line 28, `library_store.py` (imported inline per method in `_FirestoreLibraryStore`).
**Apply to:** All new files. Always module-level, after imports.

### Private helper prefix `_`
**Source:** `auth.py` `_init_firebase`, `_FIREBASE_APP`; `library_store.py` `_ensure_library_dirs`, `_slugify`; `library.py` `_load_index`, `_entry_id_from_path`.
**Apply to:** `db.py` → `_pool`, `_apply_migrations`; `embed.py` → `_client`, `_get_client`, `_EMBED_MODEL`, `_EMBED_DIM`; `cache.py` → `_DEFAULT_OWNER`, `_COSINE_THRESHOLD`.

### `EnvironmentError` for missing env vars
**Source:** `dispatcher.py` lines 52-54, 64-66, 100-101; `auth.py` lines 37-39.
**Apply to:** `db.py` `open_pool` (missing `SIGNAL_POSTGRES_DSN`), `embed.py` `_get_client` (missing `GEMINI_API_KEY`).
```python
# From dispatcher.py lines 64-66
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY is not set.")
```

### `logger.warning(..., exc_info=True)` for best-effort operations
**Source:** `library_store.py` lines 491-493, 570-572, 585-587 (all `_FirestoreLibraryStore` fallback blocks).
**Apply to:** `cache.py` `store_cache` (never raise on cache write failure); any async background task in `src/vector/`.
```python
except Exception:
    logger.warning("Token cache write failed", exc_info=True)
```

### `require_auth` dependency injection
**Source:** `src/api/deps.py` lines 12-20; used in every existing `library.py` route handler via `Depends(require_auth)`.
**Apply to:** `auth_session.py` does NOT use `require_auth` (it is the auth endpoint itself). Future Signal routes under `/api/v1/signal/` WILL use `Depends(require_auth)`.

### Absolute `src.` imports, never relative
**Source:** `library.py` line 14 `from src.api.deps import require_auth`; `library.py` line 15 `from src.agents.dispatcher import run_agent`; `deps.py` line 9 `from src.integrations.firebase.auth import verify_id_token`.
**Apply to:** All new files. `from src.vector.db import get_pool` not `from .db import get_pool`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/vector/migrations/001_init_vector.sql` | migration | batch (startup, idempotent) | No existing SQL migration files anywhere in `solo-leveling/src/`. Use RESEARCH.md Pattern 1 SQL directly. |

---

## Metadata

**Analog search scope:** `solo-leveling/src/` — all subdirectories (`core/`, `agents/`, `api/`, `integrations/firebase/`)
**Files read:** `src/app.py`, `src/integrations/firebase/auth.py`, `src/agents/dispatcher.py`, `src/core/library_store.py`, `src/api/library.py`, `src/api/deps.py`, `src/api/v1_router.py`, `src/core/config.py`, `.env.example`, `tests/test_integration_smoke.py`, `tests/test_stage9_libraries.py`
**Pattern extraction date:** 2026-05-29
