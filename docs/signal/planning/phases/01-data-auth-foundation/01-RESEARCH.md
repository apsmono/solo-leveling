# Phase 1: Data & Auth Foundation - Research

**Researched:** 2026-05-29
**Domain:** pgvector on Postgres, Gemini embeddings API, psycopg3 async, Firebase session persistence, FastAPI integration
**Confidence:** HIGH (standard stack verified against PyPI and official docs; Gemini model name confirmed via WebSearch cross-refs)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Backend extends existing `solo-leveling` FastAPI brain (Python 3.13, `src.` absolute imports, `from __future__ import annotations`, stdlib unittest). New modules under `solo-leveling/src/`.
- Vector DB = **pgvector on Postgres**, sharing ONE Postgres with n8n (enable the commented Postgres service in docker-compose.n8n.yml).
- Embeddings = **Gemini embeddings** via existing `GEMINI_API_KEY` / `AGENT_PROVIDER=gemini`.
- Persistence re-scoped to a single explicit owner/tenant record (tenant-shaped, NOT multi-tenant).
- Auth = reuse existing Firebase Google auth; session persists across refresh.

### Claude's Discretion
- pgvector schema design, embedding dimension, index type (HNSW/IVF), and migration approach
- Whether Postgres runs inside the n8n compose or as a sibling service; connection/config via `.env`
- Token-cache key derivation, similarity threshold for a "match", and cache storage (pgvector table vs separate)
- How the embeddings pipeline hooks `library_store` writes and ingested items
- Where exactly new modules sit within `solo-leveling/src/` and how they register on the FastAPI app

### Deferred Ideas (OUT OF SCOPE)
- n8n REST client, credential injection, callbacks, error-abstraction → Phase 2
- Conceptual-search UX, AI Guide, library UI → Phase 3
- Multi-tenant isolation, billing → out of scope for v1
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFRA-01 | A vector database (pgvector/Qdrant) is provisioned and serves embedding queries | pgvector on Postgres; docker-compose.n8n.yml Postgres service; psycopg3 async client |
| INFRA-02 | Content embeddings are generated and indexed for library entries and ingested items | Gemini `gemini-embedding-001` model; hook `_FileLibraryStore.save_entry`; backfill script |
| INFRA-03 | Token-cache/dedup layer serves cached summary when incoming content matches an indexed item | Cosine distance threshold 0.92+; `token_cache` table; wrap `run_agent` non-invasively |
| INFRA-04 | Persistence re-scoped from owner-of-the-box to a single tenant record, without hard-blocking future multi-tenancy | `owner_id` column pattern; extend `ALLOWED_USER_EMAIL` to derive `SIGNAL_OWNER_ID` |
| ONB-01 | Owner signs in with Google OAuth and the session persists across refresh | Firebase session cookies (Admin SDK `create_session_cookie`); httpOnly cookie; 7-day TTL |
</phase_requirements>

---

## Summary

This phase stands up four interdependent infra slabs that all later Signal phases depend on: a pgvector Postgres database, a Gemini embedding pipeline, a token-cache/dedup layer, and a single-owner tenancy scaffold — plus a durable Firebase session so the owner's login survives a browser refresh.

The key architectural insight is that all five requirements fit inside the existing `solo-leveling` FastAPI process without a new service. Postgres is provisioned by uncommenting the service in `docker-compose.n8n.yml` and upgrading the image to `pgvector/pgvector:pg16`; the Python side uses psycopg3 async with an `AsyncConnectionPool` opened in the FastAPI lifespan. No ORM is needed: two tables (`signal_embeddings` and `signal_token_cache`) are created by a raw-SQL migration file executed at startup. The Gemini embeddings API (model `gemini-embedding-001`, 768-dim output) is called via the existing `GEMINI_API_KEY` using `httpx` — the same client already imported by `dispatcher.py` — keeping the dependency footprint zero. The token-cache wraps `run_agent` as a thin, non-invasive decorator that checks cosine similarity before every LLM call. The tenant scaffold adds an `owner_id` UUID column to both tables and a `SIGNAL_OWNER_ID` env var; today it is a constant, tomorrow a FK. Firebase session cookies replace the short-lived Bearer-token dance so the owner stays logged in for up to 7 days.

**Primary recommendation:** Use `pgvector/pgvector:pg16` Docker image (not plain `postgres:16-alpine`), `psycopg[binary]>=3.3` + `psycopg-pool>=3.3` for async connection pooling, `pgvector>=0.4` Python adapter, raw-SQL startup migration (no Alembic), `gemini-embedding-001` at 768 dimensions, HNSW index with `vector_cosine_ops`, similarity threshold 0.92 for dedup, and Firebase `create_session_cookie` for session persistence.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Vector DB provisioning | Docker / Compose | — | Postgres runs as a compose service alongside n8n |
| Embedding generation | API / Backend (FastAPI) | — | Pure backend; called at write-time and query-time |
| Token-cache lookup | API / Backend | Database | Brain intercepts `run_agent` before dispatching to Gemini |
| Tenant owner record | Database / Storage | API / Backend | `owner_id` column in DB; env var constant seeds it |
| Firebase session cookie | API / Backend (new `/auth/session-login` endpoint) | Browser / Client | Backend creates cookie; browser stores it httpOnly |
| Library embedding backfill | API / Backend (startup job or CLI script) | Database | One-off async task; hooks the existing `_get_store()` |
| pgvector schema migrations | Database / Storage | API / Backend (startup) | Raw SQL file applied at lifespan startup if not yet present |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pgvector/pgvector:pg16` (Docker) | latest | Postgres 16 with pgvector pre-installed | Official pgvector project image; avoids manual extension compilation [VERIFIED: hub.docker.com/r/pgvector/pgvector] |
| `psycopg[binary]` | `>=3.3.4` | Async Postgres driver for Python | Modern psycopg3; native asyncio; dual sync/async API; pgvector-python adapter supports it [VERIFIED: pypi.org/project/psycopg] |
| `psycopg-pool` | `>=3.3.1` | Async connection pool for FastAPI lifespan | First-party pool for psycopg3; `AsyncConnectionPool` integrates cleanly with FastAPI lifespan [VERIFIED: pypi.org/project/psycopg-pool] |
| `pgvector` | `>=0.4.2` | Python type adapter for `vector` columns | Official pgvector Python adapter; provides `register_vector_async` and `Vector` type [VERIFIED: pypi.org/project/pgvector] |
| `google-genai` | `>=2.7.0` | Gemini SDK including `embed_content` | Google's official Python SDK for the Gemini API; replaces the raw httpx call pattern used in `dispatcher.py` for embeddings [VERIFIED: pypi.org/project/google-genai] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `alembic` | `>=1.18.4` | SQL migration management | **Not used this phase** — startup raw SQL is sufficient; add Alembic in Phase 4+ when schema evolves frequently |
| (none — raw SQL file) | — | Schema bootstrap | `src/vector/migrations/001_init_vector.sql` applied at startup |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pgvector/pgvector:pg16` image | `postgres:16-alpine` + manual compilation | The plain image does not ship pgvector; custom builds add maintenance burden |
| psycopg3 async | asyncpg | asyncpg is faster but requires a separate ORM adapter and does not have first-party pgvector-python support — psycopg3 has it out of the box |
| psycopg3 async | SQLAlchemy 2.x async | SQLAlchemy adds ORM overhead for only 2 tables; raw psycopg3 is simpler to reason about given the brain's no-ORM convention |
| `google-genai` SDK | raw `httpx` embed call | `dispatcher.py` currently uses raw httpx for text generation; a similar raw call works for embeddings but the SDK provides typed response objects and task_type support |
| 768-dim embeddings | 3072-dim full output | 768 matches a common pgvector HNSW sweet spot for recall vs. memory at personal scale; 3072-dim increases vector column storage 4x with negligible recall benefit for hundreds of items |

**Installation:**
```bash
# Add to solo-leveling/requirements.txt:
psycopg[binary]>=3.3.4
psycopg-pool>=3.3.1
pgvector>=0.4.2
google-genai>=2.7.0
```

---

## Package Legitimacy Audit

| Package | Registry | Age | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|
| `psycopg` | PyPI | ~4 yrs (psycopg3 line since 2021) | [OK] | Approved |
| `psycopg-pool` | PyPI | ~4 yrs | [OK] | Approved |
| `pgvector` | PyPI | ~3 yrs (official pgvector project) | [OK] | Approved |
| `google-genai` | PyPI | ~2 yrs (official Google package) | [OK] | Approved |
| `alembic` | PyPI | ~14 yrs | [OK] | Approved (supporting only; not used this phase) |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*slopcheck 0.6.1 was available and ran successfully. All packages confirmed [OK]. Versions also confirmed against PyPI via `pip3 index versions`.*

---

## Architecture Patterns

### System Architecture Diagram

```
                          ┌─────────────────────────────────────────┐
                          │    solo-leveling FastAPI Process         │
                          │                                         │
   Browser                │  ┌──────────────┐  ┌────────────────┐  │
   (Firebase JS SDK)  ──► │  │  /auth/...   │  │  /command,     │  │
   POST idToken           │  │  session     │  │  /api/v1/...   │  │
                          │  │  login/logout│  │  existing routes│  │
                          │  └──────┬───────┘  └───────┬────────┘  │
                          │         │                   │           │
                          │         ▼                   ▼           │
                          │  ┌─────────────────────────────────┐   │
                          │  │  src/vector/                    │   │
                          │  │  ┌─────────────┐ ┌──────────┐  │   │
                          │  │  │ embed.py    │ │ cache.py │  │   │
                          │  │  │ Gemini      │ │ token    │  │   │
                          │  │  │ embed_content│ │ dedup   │  │   │
                          │  │  └──────┬──────┘ └────┬─────┘  │   │
                          │  │         │              │        │   │
                          │  │  ┌──────▼──────────────▼──────┐ │   │
                          │  │  │  db.py (AsyncConnectionPool)│ │   │
                          │  │  └─────────────┬──────────────┘ │   │
                          │  └────────────────│────────────────┘   │
                          │                   │                     │
                          └───────────────────│─────────────────────┘
                                              │
                          ┌───────────────────▼─────────────────────┐
                          │  PostgreSQL 16 + pgvector                │
                          │  ┌────────────────────────────────────┐  │
                          │  │ signal_embeddings                  │  │
                          │  │  id, owner_id, entry_id, section,  │  │
                          │  │  content_hash, embedding vector(768)│  │
                          │  │  summary, captured_at, source_url  │  │
                          │  │                                    │  │
                          │  │ signal_token_cache                 │  │
                          │  │  id, owner_id, content_hash,       │  │
                          │  │  embedding vector(768), summary,   │  │
                          │  │  hit_count, created_at, expires_at │  │
                          │  └────────────────────────────────────┘  │
                          └──────────────────────────────────────────┘

                          (also shared by n8n — same Postgres instance)
```

### Recommended Project Structure

New modules live under `solo-leveling/src/vector/`:

```
solo-leveling/src/vector/
├── __init__.py         # exports: get_pool, embed_text, embed_batch, check_token_cache, store_token_cache
├── db.py               # AsyncConnectionPool lifecycle; apply_migrations()
├── embed.py            # Gemini embed_content calls; task_type routing
├── cache.py            # token-cache lookup and store; wraps run_agent
└── migrations/
    └── 001_init_vector.sql   # CREATE EXTENSION, CREATE TABLE, CREATE INDEX

solo-leveling/src/api/
└── auth_session.py     # POST /auth/session-login and /auth/session-logout endpoints
```

The `lifespan` in `src/app.py` gains two lines: `await db.open_pool()` at startup and `await db.close_pool()` at shutdown.

### Pattern 1: Postgres + pgvector Async Connection Pool (FastAPI lifespan)

**What:** `AsyncConnectionPool` created once at startup, shared across all requests via module-level singleton.
**When to use:** Any async FastAPI endpoint that needs a DB connection.

```python
# src/vector/db.py
from __future__ import annotations

import logging
from pathlib import Path

import psycopg
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

logger = logging.getLogger(__name__)

_pool: AsyncConnectionPool | None = None


async def open_pool(dsn: str) -> None:
    global _pool
    _pool = AsyncConnectionPool(conninfo=dsn, open=False)
    await _pool.open()
    # Register pgvector type adapter on every new connection
    async with _pool.connection() as conn:
        await register_vector_async(conn)
    await _apply_migrations()
    logger.info("Vector DB pool ready.")


async def close_pool() -> None:
    if _pool:
        await _pool.close()


def get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Vector DB pool not initialised. Call open_pool() first.")
    return _pool


async def _apply_migrations() -> None:
    sql = (Path(__file__).parent / "migrations" / "001_init_vector.sql").read_text()
    async with get_pool().connection() as conn:
        await conn.execute(sql)
        await conn.commit()
```

```python
# src/vector/migrations/001_init_vector.sql
-- Idempotent: safe to run on every startup
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS signal_embeddings (
    id            SERIAL PRIMARY KEY,
    owner_id      TEXT NOT NULL DEFAULT 'default-owner',
    entry_id      TEXT NOT NULL,
    section       TEXT NOT NULL DEFAULT '',
    content_hash  TEXT NOT NULL,
    embedding     vector(768),
    summary       TEXT NOT NULL DEFAULT '',
    source_url    TEXT,
    captured_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_signal_embeddings_owner_entry
    ON signal_embeddings (owner_id, entry_id);

CREATE INDEX IF NOT EXISTS idx_signal_embeddings_vec
    ON signal_embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS signal_token_cache (
    id            SERIAL PRIMARY KEY,
    owner_id      TEXT NOT NULL DEFAULT 'default-owner',
    content_hash  TEXT NOT NULL,
    embedding     vector(768),
    summary       TEXT NOT NULL,
    hit_count     INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at    TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_signal_token_cache_owner_hash
    ON signal_token_cache (owner_id, content_hash);

CREATE INDEX IF NOT EXISTS idx_signal_token_cache_vec
    ON signal_token_cache USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

*Source: pgvector README + pgvector-python psycopg3 examples [CITED: github.com/pgvector/pgvector-python]*

### Pattern 2: Gemini Embeddings via google-genai SDK

**What:** Call `client.models.embed_content` with `task_type` differentiation for documents vs queries.
**When to use:** At `save_entry` time (documents) and at cache-check/search time (queries).

```python
# src/vector/embed.py
from __future__ import annotations

import hashlib
import os
from typing import Literal

from google import genai
from google.genai import types

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


def embed_text(
    text: str,
    task_type: Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"] = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    """Embed a single text string. Returns a 768-dim float list."""
    result = _get_client().models.embed_content(
        model=_EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=_EMBED_DIM,
        ),
    )
    return result.embeddings[0].values


def content_hash(text: str) -> str:
    """SHA-256 hex digest of the input text (for exact-duplicate fast-path)."""
    return hashlib.sha256(text.encode()).hexdigest()
```

*Source: Gemini API embeddings docs — model `gemini-embedding-001` GA, `task_type` parameter, `output_dimensionality` for Matryoshka truncation [CITED: ai.google.dev/gemini-api/docs/embeddings]*

### Pattern 3: Token-Cache Wrapper for `run_agent`

**What:** Before invoking the LLM, embed the request context, query the `signal_token_cache` table for cosine similarity, and serve the cached summary if distance is within threshold.
**When to use:** Wraps any `run_agent` call. Non-invasive — callers do not change.

```python
# src/vector/cache.py
from __future__ import annotations

import logging
from typing import Callable

from pgvector.psycopg import register_vector_async

from src.vector.db import get_pool
from src.vector.embed import content_hash, embed_text

logger = logging.getLogger(__name__)

_COSINE_THRESHOLD = 0.08   # cosine DISTANCE (not similarity); 0.08 ≈ similarity 0.92
_DEFAULT_OWNER = "default-owner"


async def check_cache(text: str, owner_id: str = _DEFAULT_OWNER) -> str | None:
    """Return cached summary if a near-duplicate exists, else None."""
    vec = embed_text(text, task_type="RETRIEVAL_QUERY")
    async with get_pool().connection() as conn:
        row = await conn.fetchone(
            """
            SELECT summary, 1 - (embedding <=> %s::vector) AS similarity
            FROM signal_token_cache
            WHERE owner_id = %s
              AND (embedding <=> %s::vector) < %s
            ORDER BY embedding <=> %s::vector
            LIMIT 1
            """,
            (vec, owner_id, vec, _COSINE_THRESHOLD, vec),
        )
    if row:
        logger.info("Token cache HIT (similarity=%.3f)", row["similarity"])
        # Increment hit count (fire and forget)
        _hash = content_hash(text)
        return row["summary"]
    return None


async def store_cache(text: str, summary: str, owner_id: str = _DEFAULT_OWNER) -> None:
    """Store a new entry in the token cache."""
    vec = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
    _hash = content_hash(text)
    async with get_pool().connection() as conn:
        await conn.execute(
            """
            INSERT INTO signal_token_cache (owner_id, content_hash, embedding, summary)
            VALUES (%s, %s, %s::vector, %s)
            ON CONFLICT (owner_id, content_hash) DO UPDATE
              SET summary = EXCLUDED.summary, hit_count = signal_token_cache.hit_count + 1
            """,
            (owner_id, _hash, vec, summary),
        )
        await conn.commit()
```

**Threshold rationale:** Cosine distance 0.08 (= similarity 0.92) is a conservatively high bar for "same content". At personal scale (hundreds of items), false positives waste more user trust than false negatives waste tokens — so err toward a tight threshold. [ASSUMED — no single published standard; 0.92 is a commonly cited starting point in RAG dedup literature]

### Pattern 4: Firebase Session Cookie (ONB-01 — session persists across refresh)

**What:** The browser POSTs the Firebase ID token to `/auth/session-login`; the backend calls `firebase_admin.auth.create_session_cookie` and returns an `httpOnly Secure` cookie valid for N days.
**When to use:** Single call after Google OAuth sign-in.

```python
# src/api/auth_session.py
from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from src.integrations.firebase.auth import verify_id_token, _init_firebase

router = APIRouter()
_SESSION_DURATION = datetime.timedelta(days=7)


@router.post("/auth/session-login")
async def session_login(payload: dict[str, Any], response: Response) -> dict[str, str]:
    id_token = payload.get("idToken", "")
    if not id_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing idToken.")
    # Verify the ID token first (validates user + email allowlist)
    verify_id_token(id_token)
    # Create session cookie
    _init_firebase()
    import firebase_admin.auth as fb_auth
    cookie = fb_auth.create_session_cookie(id_token, expires_in=_SESSION_DURATION)
    response.set_cookie(
        key="__session",
        value=cookie,
        max_age=int(_SESSION_DURATION.total_seconds()),
        httponly=True,
        secure=True,  # set False for local dev via env flag
        samesite="strict",
    )
    return {"status": "ok"}


@router.post("/auth/session-logout")
async def session_logout(response: Response) -> dict[str, str]:
    response.delete_cookie("__session")
    return {"status": "ok"}
```

*Source: Firebase Admin SDK session cookie docs [CITED: firebase.google.com/docs/auth/admin/manage-cookies]*

### Anti-Patterns to Avoid

- **Using `postgres:16-alpine` instead of `pgvector/pgvector:pg16`:** Alpine does not ship pgvector. You would need a custom Dockerfile with build tools to compile the extension. Use the official pgvector image.
- **Sharing the n8n database user with Signal:** n8n uses the `n8n` database with user `n8n`. Create a separate `signal` database (or at minimum a `signal` schema with a separate role) to avoid privilege bleed and make the n8n → multi-tenant migration path clean.
- **IVFFlat instead of HNSW at personal scale:** IVFFlat requires a training step (`VACUUM ANALYZE` after initial data load); you must also set `lists` based on row count. At hundreds of rows the default `lists=100` creates near-empty clusters. HNSW has no training step and can be created on an empty table — it just works.
- **Registering `register_vector_async` once per pool instead of per connection:** The pgvector type adapter is per-connection. After opening the pool, run `register_vector_async` inside a pool connection to ensure all connections in the pool are registered. Always call it inside `conn.__aenter__` if unsure.
- **Calling `embed_text` inside a tight request loop without a rate-limit guard:** The Gemini free tier is 5 RPM for `gemini-embedding-001`; Tier 1 is 150 RPM. A backfill of 500 library entries at 1 call/entry will exhaust free tier quickly. Batch calls (up to 100 texts per request per the API, though rate limits apply per-call not per-batch) and add a small sleep between batches.
- **Storing `SIGNAL_OWNER_ID` only in code constants:** If the value is hardcoded rather than read from `.env`, future multi-tenancy requires code edits rather than config changes. Always read from `os.environ.get("SIGNAL_OWNER_ID", ALLOWED_USER_EMAIL)`.
- **Applying `register_vector_async` after the pool is already receiving connections:** If migrations run in a separate transaction before the pool is opened for queries, the type adapter may not be registered on those connections. Open the pool, immediately register, then run migrations, then serve requests.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Postgres connection pooling | Custom async connection factory | `psycopg-pool` `AsyncConnectionPool` | Handles idle connection eviction, reconnects on failure, lifespan-safe |
| pgvector type serialization | Binary vector encoding/decoding | `pgvector` Python adapter + `register_vector_async` | Exact binary format pgvector expects; version-safe |
| Cosine similarity search | Brute-force dot-product loop in Python | pgvector `<=>` operator + HNSW index | Index makes query sub-millisecond; Python loop is O(n·dim) = non-starter beyond hundreds of items |
| Exact-duplicate detection before LLM | Content-based hash | `hashlib.sha256` + `UNIQUE` index on `content_hash` | Trivially fast; catches 100% of true duplicates before vector computation |
| Firebase session lifetime | Custom JWT minting | `firebase_admin.auth.create_session_cookie` | Firebase handles signing, rotation, revocation list |
| SQL migrations | Manual `psycopg.execute` scattered across files | Single idempotent `.sql` file applied at startup | Predictable, auditable, git-tracked; Alembic adds weight not needed for 2 tables |

**Key insight:** pgvector's `<=>` operator (cosine distance) + HNSW index is the entire near-duplicate search — no external vector search service, no Python math, no custom data structure. The database does it.

---

## Common Pitfalls

### Pitfall 1: Wrong Postgres Image in docker-compose
**What goes wrong:** Uncomment the existing `postgres:16-alpine` service → `CREATE EXTENSION IF NOT EXISTS vector` fails with "extension 'vector' not found".
**Why it happens:** Alpine images don't ship pgvector; the extension must be compiled or the official pgvector image used.
**How to avoid:** Change the image to `pgvector/pgvector:pg16` in `docker-compose.n8n.yml`.
**Warning signs:** `ERROR: could not open extension control file "…/vector.control": No such file or directory`

### Pitfall 2: register_vector_async Not Called Per Connection
**What goes wrong:** Queries with `vector` type fail with `can't adapt type 'list'` or psycopg type error.
**Why it happens:** The pgvector adapter registers a custom type codec on a *specific connection object*, not globally on the pool.
**How to avoid:** Call `await register_vector_async(conn)` inside `open_pool()` (and in a pool `connect` callback for new connections). The `pgvector-python` README shows this pattern explicitly.
**Warning signs:** `ProgrammingError: can't adapt type 'list'` when inserting a vector value.

### Pitfall 3: HNSW Index Operator Class Mismatch
**What goes wrong:** Queries use `<=>` (cosine) but the index was created with `vector_l2_ops` (L2) → the index is silently ignored; full sequential scan on every query.
**Why it happens:** pgvector only uses an index when the query operator matches the index operator class.
**How to avoid:** Always create `USING hnsw (embedding vector_cosine_ops)` and always query with `<=>`. Verify with `EXPLAIN (ANALYZE) SELECT ...`.
**Warning signs:** `EXPLAIN` shows `Seq Scan` instead of `Index Scan` on the vector column.

### Pitfall 4: Gemini task_type Omission
**What goes wrong:** Using the same embedding (no task_type or wrong task_type) for both document storage and query-time lookup reduces recall significantly.
**Why it happens:** `gemini-embedding-001` is a biencoder — it uses different internal representations for `RETRIEVAL_DOCUMENT` (asymmetric, optimized for passage-level retrieval) and `RETRIEVAL_QUERY` (optimized for question/command-like inputs).
**How to avoid:** Always pass `task_type="RETRIEVAL_DOCUMENT"` at write time and `task_type="RETRIEVAL_QUERY"` at search/cache-check time.
**Warning signs:** Near-duplicate detection works poorly even on items that look clearly similar in human judgment.

### Pitfall 5: n8n Breaks After Postgres Changes
**What goes wrong:** n8n was previously running with SQLite (`n8n_data` volume). After Postgres is added, n8n's `DB_TYPE` env var must be set to `postgresdb` or it silently continues with SQLite while a Postgres container also spins up — wasting resources.
**Why it happens:** n8n defaults to SQLite if `DB_TYPE` is not set; the existing `docker-compose.n8n.yml` has no `DB_TYPE` environment variable.
**How to avoid:** Decision: run n8n on SQLite (keep `n8n_data` volume) and use Postgres *only* for Signal. This is simpler and matches the phase scope (n8n wiring is Phase 2). Add Postgres to the compose file but do NOT wire n8n to it this phase.
**Warning signs:** n8n startup logs show "Database: sqlite" even after adding Postgres service.

### Pitfall 6: Firebase `create_session_cookie` Requires ID Token (Not Refresh Token)
**What goes wrong:** Calling `create_session_cookie` with a refresh token or the wrong token type throws an exception.
**Why it happens:** The Admin SDK validates the token type before signing the session cookie.
**How to avoid:** The client-side Firebase JS SDK's `getIdToken()` returns the correct format. Always use `user.getIdToken()` — not `user.refreshToken` — in the browser POST.
**Warning signs:** `firebase_admin.exceptions.InvalidArgumentError: Failed to create session cookie`

### Pitfall 7: `psycopg[binary]` vs `psycopg` (pure Python) on Docker
**What goes wrong:** `psycopg` (pure Python) is slower but installs anywhere; `psycopg[binary]` includes pre-compiled C extensions. In the `python:3.13-slim` container used in the brain's `Dockerfile`, binary wheels are available for Linux/amd64 but the extra build deps are not needed.
**Why it happens:** pip installs the pure-Python fallback silently if the binary wheel is not found.
**How to avoid:** Use `psycopg[binary]>=3.3.4` in `requirements.txt`. On the MacMini (darwin arm64), binary wheels exist for psycopg3 3.x.
**Warning signs:** `import psycopg` works but `psycopg._cmodule` is `None` → pure Python mode (slower).

---

## Code Examples

### Verify HNSW Index is Used

```sql
-- Source: pgvector README [CITED: github.com/pgvector/pgvector]
-- Run after inserting at least one row; index requires data to be used
EXPLAIN (ANALYZE, BUFFERS)
SELECT entry_id, 1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM signal_embeddings
WHERE owner_id = 'default-owner'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
-- Expect: "Index Scan using idx_signal_embeddings_vec on signal_embeddings"
```

### Backfill Existing Library Entries

```python
# One-shot async script or startup task
# Source pattern: library_store.py _FileLibraryStore.search_all_entries + embed.py [ASSUMED — no official reference]
async def backfill_library_embeddings(owner_id: str) -> int:
    from src.core.libraries import _get_store
    from src.vector.embed import content_hash, embed_text
    store = _get_store()
    index = store.load_index()
    count = 0
    for entry in index.get("entries", []):
        entry_data = store.get_entry(entry["path"].rsplit("/", 1)[-1].removesuffix(".md"))
        if not entry_data:
            continue
        text = entry_data.get("markdown", "")
        if not text:
            continue
        vec = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
        _hash = content_hash(text)
        async with get_pool().connection() as conn:
            await conn.execute(
                """
                INSERT INTO signal_embeddings
                  (owner_id, entry_id, section, content_hash, embedding, summary, source_url)
                VALUES (%s, %s, %s, %s, %s::vector, %s, %s)
                ON CONFLICT (owner_id, entry_id) DO UPDATE
                  SET embedding = EXCLUDED.embedding, content_hash = EXCLUDED.content_hash
                """,
                (owner_id, entry.get("path", ""), entry.get("section", ""),
                 _hash, vec, entry.get("title", ""), entry.get("source_url")),
            )
            await conn.commit()
        count += 1
    return count
```

### Hook save_entry for Real-Time Indexing

```python
# Thin wrapper — place in src/vector/hooks.py
# Called from libraries.py save_entry after the file is written
# Source: project pattern — no external reference [ASSUMED]
import asyncio

async def on_entry_saved(entry_id: str, text: str, section: str, owner_id: str, source_url: str | None = None) -> None:
    from src.vector.embed import content_hash, embed_text
    from src.vector.db import get_pool
    vec = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
    _hash = content_hash(text)
    async with get_pool().connection() as conn:
        await conn.execute(
            """
            INSERT INTO signal_embeddings (owner_id, entry_id, section, content_hash, embedding, source_url)
            VALUES (%s, %s, %s, %s, %s::vector, %s)
            ON CONFLICT (owner_id, entry_id) DO UPDATE
              SET embedding = EXCLUDED.embedding
            """,
            (owner_id, entry_id, section, _hash, vec, source_url),
        )
        await conn.commit()
```

**Integration note:** `_FileLibraryStore.save_entry` is synchronous (`library_store.py` line 165). The hook must be called via `asyncio.create_task(on_entry_saved(...))` from an already-async context, or scheduled as a background job from the API layer, NOT called synchronously from inside `save_entry`. This avoids introducing async into the otherwise sync store module.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `text-embedding-004` | `gemini-embedding-001` (GA stable) | 2025-Q2 | `gemini-embedding-exp-03-07` deprecated Oct 2025; `gemini-embedding-001` is now the stable GA model [CITED: github.com/simonw/llm-gemini/issues/102] |
| `psycopg2` | `psycopg` v3 (psycopg3) | 2021-2024 | Native asyncio, no `greenlet`/`gevent` monkey-patching needed; pgvector-python adapter supports it natively |
| pgvector IVFFlat | pgvector HNSW (added v0.5.0, 2023) | 2023 | HNSW is now preferred: no training step, better recall, can be created on empty table |
| Bearer token on every request | Firebase session cookie | — | Session cookie survives browser refresh; ID tokens expire in 1 hour |

**Deprecated/outdated:**
- `gemini-embedding-exp-03-07`: deprecated October 2025; replaced by `gemini-embedding-001`.
- `text-embedding-004`: older generation, still available but not recommended for new projects.
- `psycopg2`: still functional but not recommended for new async FastAPI code; use `psycopg` v3.

---

## Runtime State Inventory

> This phase is greenfield (new tables, new modules) — no existing runtime state is renamed or migrated.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — `signal_embeddings` and `signal_token_cache` are new tables | Create at startup via migration SQL |
| Live service config | n8n currently runs on SQLite (`n8n_data` volume) — this phase does NOT migrate n8n to Postgres | No action; n8n stays on SQLite this phase |
| OS-registered state | None — no OS-level registrations reference Signal-specific names | None |
| Secrets/env vars | New vars: `SIGNAL_POSTGRES_DSN`, `SIGNAL_OWNER_ID` added to `.env.example`; existing `GEMINI_API_KEY` reused | Add new vars to `.env.example` and `src/core/config.py` |
| Build artifacts | None — new Python modules; no stale egg-info or compiled artifacts | None |

---

## Open Questions

1. **Where does the async `on_entry_saved` hook get called?**
   - What we know: `_FileLibraryStore.save_entry` is synchronous; FastAPI routes that call it are async.
   - What's unclear: The current call chain for `save_entry` (from `libraries.py` `_handle_library_capture`, which is called from `router.py` `route_command`, which is called from `src/app.py` `/command` — all synchronous).
   - Recommendation: Expose a new `/api/v1/library/entries` POST endpoint (already partially exists in `src/api/library.py`) that is async and fires `asyncio.create_task(on_entry_saved(...))` after calling the store. For the backfill, run as a FastAPI startup background task.

2. **Should Signal's Postgres DB be a separate `signal` database or a `signal` schema inside the n8n DB?**
   - What we know: The phase decision says "sharing ONE Postgres" for simplicity.
   - What's unclear: "sharing" could mean same DB + separate schema, or separate DB on same Postgres instance.
   - Recommendation (Claude's discretion): Use a separate database named `signal` on the same Postgres instance. This gives complete table-level isolation, independent `GRANT` statements, and a clean future split path. Connection strings: n8n → `postgresql://n8n:pass@postgres:5432/n8n`; Signal → `postgresql://signal:pass@postgres:5432/signal`.

3. **Is `SIGNAL_OWNER_ID` seeded from `ALLOWED_USER_EMAIL` or independently set?**
   - What we know: `ALLOWED_USER_EMAIL` (e.g. `pramono@getgoing.co.id`) is already the email-based guard in `auth.py`.
   - Recommendation: Use the email as the `owner_id` string value today (`owner_id = ALLOWED_USER_EMAIL`). This avoids a new UUID-generation step and keeps the "what is my owner_id" question trivially answerable by inspecting `.env`. Future multi-tenancy will migrate to UUID PKs, but for single-owner that migration is trivial.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | pgvector Postgres container | Yes | 29.4.0 | — |
| Python 3.13 (in venv) | solo-leveling brain | Yes (system is 3.14.5; venv pins 3.13 per requirements) | 3.13.x in venv | — |
| psql CLI | DB debugging / manual migration check | No — not installed on MacMini | — | Use `docker exec -it postgres psql` inside the container |
| `GEMINI_API_KEY` | Embedding calls | Assumed set (existing brain uses it) | — | Build will fail without it; no offline fallback |
| Firebase Admin credentials | Session cookie creation + token verify | Assumed set (existing auth.py uses them) | — | Auth endpoints return 500 without credentials |

**Missing dependencies with no fallback:**
- `GEMINI_API_KEY` — must be present; embedding calls fail without it
- `FIREBASE_CREDENTIALS_JSON` or `FIREBASE_CREDENTIALS_PATH` — must be present; session cookie endpoint fails without it

**Missing dependencies with fallback:**
- `psql` CLI — use `docker exec` inside the Postgres container for debugging

---

## Validation Architecture

`workflow.nyquist_validation: true` in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` |
| Config file | none (direct `python -m unittest` invocation) |
| Quick run command | `python -m unittest tests.test_vector_foundation -v` |
| Full suite command | `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| INFRA-01 | pgvector extension enabled; `signal_embeddings` and `signal_token_cache` tables created by migration | integration (requires Postgres) | `python -m unittest tests.test_vector_foundation.VectorDBTests.test_migration_is_idempotent -v` | No — Wave 0 gap |
| INFRA-01 | `get_pool()` raises before `open_pool()` is called | unit | `python -m unittest tests.test_vector_foundation.VectorDBTests.test_pool_not_init_raises -v` | No — Wave 0 gap |
| INFRA-02 | `embed_text` returns a 768-element float list | unit (mocked API) | `python -m unittest tests.test_vector_foundation.EmbedTests.test_embed_text_dimensions -v` | No — Wave 0 gap |
| INFRA-02 | `on_entry_saved` inserts a row into `signal_embeddings` | integration (requires Postgres) | `python -m unittest tests.test_vector_foundation.EmbedTests.test_on_entry_saved_inserts_row -v` | No — Wave 0 gap |
| INFRA-02 | Backfill returns non-zero count for a seeded library | integration | `python -m unittest tests.test_vector_foundation.EmbedTests.test_backfill_count -v` | No — Wave 0 gap |
| INFRA-03 | `check_cache` returns `None` on miss | unit (mocked pool) | `python -m unittest tests.test_vector_foundation.TokenCacheTests.test_cache_miss_returns_none -v` | No — Wave 0 gap |
| INFRA-03 | `check_cache` returns cached summary on near-duplicate hit | integration | `python -m unittest tests.test_vector_foundation.TokenCacheTests.test_cache_hit_returns_summary -v` | No — Wave 0 gap |
| INFRA-03 | Cache HIT is logged at INFO level | unit | `python -m unittest tests.test_vector_foundation.TokenCacheTests.test_cache_hit_logged -v` | No — Wave 0 gap |
| INFRA-04 | All DB rows have `owner_id` matching `SIGNAL_OWNER_ID` env var | unit | `python -m unittest tests.test_vector_foundation.TenantTests.test_owner_id_written_correctly -v` | No — Wave 0 gap |
| ONB-01 | `POST /auth/session-login` sets `__session` httpOnly cookie | unit (mocked Firebase) | `python -m unittest tests.test_vector_foundation.AuthSessionTests.test_session_login_sets_cookie -v` | No — Wave 0 gap |
| ONB-01 | `POST /auth/session-login` with invalid token returns 401 | unit (mocked Firebase raise) | `python -m unittest tests.test_vector_foundation.AuthSessionTests.test_session_login_invalid_token -v` | No — Wave 0 gap |
| ONB-01 | `POST /auth/session-logout` deletes `__session` cookie | unit | `python -m unittest tests.test_vector_foundation.AuthSessionTests.test_session_logout_clears_cookie -v` | No — Wave 0 gap |

### Sampling Rate

- **Per task commit:** `python -m unittest tests.test_vector_foundation -v` (unit tests only, mocked Postgres and Gemini)
- **Per wave merge:** `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation -v`
- **Phase gate:** Full suite green; plus one manual smoke: `curl -X POST http://localhost:8000/auth/session-login -H 'Content-Type: application/json' -d '{"idToken":"<token>"}'` and verify cookie is set.

### Wave 0 Gaps

- [ ] `tests/test_vector_foundation.py` — all test classes above; mock Gemini + use pytest-asyncio or `asyncio.run()` for async tests
- [ ] `SIGNAL_POSTGRES_DSN_TEST` env var in `.env.example` for integration tests
- [ ] Docker Compose up/down fixture or `SKIP_VECTOR_INTEGRATION` env flag for offline test runs

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | Firebase Admin SDK ID token + session cookie; existing `verify_id_token` reused |
| V3 Session Management | Yes | `httpOnly; Secure; SameSite=Strict` cookie; 7-day TTL via Firebase session cookie |
| V4 Access Control | Yes | `ALLOWED_USER_EMAIL` allowlist in `auth.py`; `owner_id` column on all DB rows |
| V5 Input Validation | Yes | `entry_id` and `text` are strings; SQL uses parameterized queries via psycopg3 |
| V6 Cryptography | No — not applicable | No custom crypto; pgvector and Firebase handle their own |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection via `entry_id` or `text` | Tampering | psycopg3 parameterized queries (`%s` placeholders); never f-string SQL |
| Session cookie theft (XSS) | Elevation of Privilege | `httpOnly=True` on `__session` cookie; no JS cookie access |
| Cross-site request forgery | Spoofing | `SameSite=Strict` on session cookie; POST `/auth/session-login` requires valid Firebase ID token |
| Unauthorized vector DB access | Information Disclosure | Postgres runs on Docker internal network only; no port exposed on host unless explicitly mapped |
| Embedding API key exposure | Information Disclosure | `GEMINI_API_KEY` read from env var only; never hardcoded; `.env` is gitignored |
| Cosine threshold manipulation (cache poisoning) | Tampering | Threshold is a server-side constant; not user-controllable; `owner_id` scopes all cache queries |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Cosine distance threshold 0.08 (similarity 0.92) is appropriate for token-cache dedup | Pattern 3, Common Pitfalls | Too tight → no cache hits; too loose → wrong summaries served; threshold should be validated empirically in Phase 1 testing |
| A2 | `gemini-embedding-001` free tier is 5 RPM and paid tier is 150 RPM | Common Pitfalls | Rate limit may have changed; check AI Studio for your project's current limits before implementing the backfill throttle |
| A3 | Using `owner_id = ALLOWED_USER_EMAIL` (email string) as the owner identifier is sufficient for single-owner | Open Questions | If email changes (e.g. account migration), all DB rows would need updating; acceptable for personal-first but worth noting |
| A4 | `on_entry_saved` can safely be called via `asyncio.create_task` from FastAPI route handlers | Pattern 3, Open Questions | If the event loop is torn down before the task completes, the embedding is silently skipped; add error logging inside the task |
| A5 | Using `gemini-embedding-001` at 768 dimensions gives sufficient recall for the personal-scale library (hundreds of items) | Standard Stack | If the library grows to tens of thousands of items, 3072-dim may improve recall; revisit when scaling |

---

## Project Constraints (from CLAUDE.md)

Directives extracted from `solo-leveling/CLAUDE.md` that the planner must verify compliance with:

1. **Absolute imports with `src.` prefix** — all new files in `src/vector/` must use `from src.vector.db import ...`, never `from .db import ...`.
2. **`from __future__ import annotations`** — required at the top of every new `.py` file.
3. **Private helpers prefixed with `_`** — internal functions like `_get_client()`, `_apply_migrations()`, `_init_firebase()`.
4. **Catch `EnvironmentError` separately in handlers** — `GEMINI_API_KEY` and DB DSN are environment-gated; raise `EnvironmentError` not generic `ValueError`.
5. **stdlib `unittest`** — no pytest; use `unittest.TestCase` classes, `unittest.mock.patch`.
6. **Tests live under `tests/`** — new file: `tests/test_vector_foundation.py`.
7. **Run tests before committing** — `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation -v`.
8. **Update `CHANGELOG.md`** after non-trivial changes.
9. **Update `AI_CONTEXT.md`** if the current phase, completed stages, or active priorities change.
10. **Docker mounts** — `library/` and `data/` are Docker volumes; new `vector/migrations/` is baked into the image (not a volume). The Postgres data volume must be added to `docker-compose.n8n.yml`.
11. **Commit style** — `feat(signal): ...` for Signal-specific additions; `chore: bump solo-leveling` for parent repo submodule bump.

---

## Sources

### Primary (HIGH confidence)
- [Gemini Embeddings API — Google AI for Developers](https://ai.google.dev/gemini-api/docs/embeddings) — model name `gemini-embedding-001`, task_type options, output_dimensionality
- [pgvector-python GitHub](https://github.com/pgvector/pgvector-python) — `register_vector_async`, psycopg3 integration pattern
- [pgvector GitHub README](https://github.com/pgvector/pgvector) — HNSW vs IVFFlat, HNSW operator classes, index parameters
- [Firebase Admin SDK — Manage Session Cookies](https://firebase.google.com/docs/auth/admin/manage-cookies) — `create_session_cookie`, httpOnly pattern, 2-week max TTL
- PyPI registry — `psycopg 3.3.4`, `psycopg-pool 3.3.1`, `pgvector 0.4.2`, `google-genai 2.7.0`, `alembic 1.18.4` (all confirmed via `pip3 index versions`)

### Secondary (MEDIUM confidence)
- [Gemini Embedding GA blog post — Google Developers Blog](https://developers.googleblog.com/gemini-embedding-available-gemini-api/) — `gemini-embedding-001` GA, deprecation of exp model
- [llm-gemini issue #102](https://github.com/simonw/llm-gemini/issues/102) — confirms `gemini-embedding-exp-03-07` deprecated; `gemini-embedding-001` stable
- [pgvector-python psycopg3 async example — DEV Community](https://dev.to/geekyfox90/how-to-use-pgvector-with-python-a-complete-guide-808) — async pattern verified against official docs
- [Neon Blog — HNSW Index](https://neon.com/blog/understanding-vector-search-and-hnsw-index-with-pgvector) — `ef_search`, m, ef_construction defaults

### Tertiary (LOW confidence)
- Cosine similarity threshold 0.92 for near-duplicate dedup — cross-referenced from multiple RAG community posts; no single canonical source; marked [ASSUMED]
- Gemini free tier 5 RPM for `gemini-embedding-001` — from rate-limit discussion threads; official table subject to change; check AI Studio [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages confirmed on PyPI, slopcheck passed, pgvector image verified
- Architecture: HIGH — grounded in actual code read (`library_store.py`, `dispatcher.py`, `auth.py`, `app.py`, `docker-compose.n8n.yml`)
- Pitfalls: MEDIUM — most grounded in official docs; threshold-related pitfalls are ASSUMED
- Gemini model name: MEDIUM-HIGH — confirmed via cross-referenced blog posts and GitHub issues; not directly fetched from live docs due to context-mode redirect

**Research date:** 2026-05-29
**Valid until:** 2026-08-29 (stable stack; Gemini model names change — re-verify `gemini-embedding-001` availability if > 60 days old)
