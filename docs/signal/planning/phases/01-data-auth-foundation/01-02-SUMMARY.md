---
phase: 01-data-auth-foundation
plan: 02
subsystem: database
tags: [pgvector, postgres, psycopg, async, hnsw, docker-compose, fastapi, lifespan]

requires:
  - phase: 01-01
    provides: "SIGNAL_POSTGRES_DSN config export and .env.example entries"
provides:
  - "Docker Compose postgres service with pgvector/pgvector:pg16 image"
  - "Idempotent schema migration creating signal_embeddings and signal_token_cache tables"
  - "AsyncConnectionPool lifecycle module (open_pool, close_pool, get_pool)"
  - "FastAPI lifespan wiring: pool opens at startup, closes at shutdown"
affects:
  - "01-03 (embedding generation — depends on signal_embeddings table)"
  - "01-04 (token cache — depends on signal_token_cache table)"
  - "01-05 (search API — depends on HNSW indexes)"

tech-stack:
  added:
    - "pgvector>=0.4.2 (vector extension for Postgres)"
    - "psycopg[binary]>=3.3.4 (async Postgres driver)"
    - "psycopg-pool>=3.3.1 (async connection pool)"
    - "google-genai>=2.7.0 (Gemini SDK for embedding generation)"
  patterns:
    - "Module-level _pool singleton with get_pool() RuntimeError guard"
    - "Lifespan-before-yield for startup, after-yield for shutdown"
    - "Idempotent SQL migrations: CREATE EXTENSION IF NOT EXISTS, CREATE TABLE IF NOT EXISTS"
    - "EnvironmentError for missing config (empty DSN)"
    - "No host port exposure: internal Docker network only"

key-files:
  created:
    - "solo-leveling/src/vector/__init__.py — Public facade exporting get_pool, open_pool, close_pool"
    - "solo-leveling/src/vector/db.py — AsyncConnectionPool lifecycle + _apply_migrations()"
    - "solo-leveling/src/vector/migrations/001_init_vector.sql — Idempotent schema bootstrap"
  modified:
    - "docker-compose.n8n.yml — Added pgvector Postgres service with healthcheck"
    - "solo-leveling/src/app.py — Lifespan wiring: open_pool before yield, close_pool after yield"
    - "solo-leveling/requirements.txt — Added psycopg, psycopg-pool, pgvector, google-genai"

key-decisions:
  - "App starts even when SIGNAL_POSTGRES_DSN is empty (logs warning) — prevents hard failure in envs without Postgres"
  - "HNSW indexes use vector_cosine_ops (not vector_l2_ops) — matches SIGNAL_COSINE_THRESHOLD semantic search strategy"
  - "Separate signal database/user from n8n — prevents privilege bleed per threat model T-01-08"
  - "No host port mapping in compose — internal network only per threat model T-01-05"

patterns-established:
  - "Vector module pattern: src/vector/ with migrations/, db.py pool lifecycle, __init__.py facade"
  - "Config guard pattern: EnvironmentError on empty required DSN, graceful degradation on optional config"
  - "Threat-aware compose: internal networks, no host ports, dedicated DB credentials"

requirements-completed: [INFRA-01, INFRA-04]

duration: 8min
completed: 2026-05-29
---

# Phase 1 Plan 2: pgvector Postgres + Async Pool Lifewire Summary

**pgvector Postgres container with HNSW-indexed signal_embeddings and signal_token_cache tables, wired into FastAPI lifespan via async connection pool**

## Performance

- **Duration:** 8 min
- **Started:** 2026-05-29T14:20:00Z
- **Completed:** 2026-05-29T14:28:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Postgres service running pgvector:pg16 with dedicated signal DB, healthcheck, and persistent volume
- Idempotent migration SQL creating both tables with owner_id columns and HNSW cosine indexes
- AsyncConnectionPool module with open/close/get lifecycle and automatic migration application
- FastAPI lifespan hooks pool open before yield and close after yield, with graceful fallback when DSN is unset

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Postgres service to docker-compose.n8n.yml** — `5670fca` (feat)
2. **Task 2: Create vector module + migration + db.py** — `0deb2ca` (feat)
3. **Task 3: Wire pool into FastAPI lifespan and add requirements** — `efaffac` (feat)

## Files Created/Modified

- `docker-compose.n8n.yml` — Added `postgres` service using `pgvector/pgvector:pg16`, signal DB credentials, internal network, healthcheck
- `solo-leveling/src/vector/migrations/001_init_vector.sql` — Idempotent schema: vector extension, signal_embeddings, signal_token_cache, HNSW cosine indexes
- `solo-leveling/src/vector/db.py` — AsyncConnectionPool lifecycle: `open_pool()`, `close_pool()`, `get_pool()`, `_apply_migrations()`
- `solo-leveling/src/vector/__init__.py` — Public facade exporting `get_pool`, `open_pool`, `close_pool`
- `solo-leveling/src/app.py` — Lifespan wiring: `vector_db.open_pool()` before yield, `vector_db.close_pool()` after yield
- `solo-leveling/requirements.txt` — Added `psycopg[binary]>=3.3.4`, `psycopg-pool>=3.3.1`, `pgvector>=0.4.2`, `google-genai>=2.7.0`

## Decisions Made

- App starts even when `SIGNAL_POSTGRES_DSN` is empty (logs warning) — prevents hard failure in environments without Postgres configured yet
- HNSW indexes use `vector_cosine_ops` (not `vector_l2_ops`) — aligns with `SIGNAL_COSINE_THRESHOLD` semantic search strategy from Wave 0
- Separate `signal` database/user from n8n — prevents privilege bleed per threat model T-01-08
- No host port mapping in compose — internal Docker network only per threat model T-01-05

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing psycopg-binary for libpq support**
- **Found during:** Task 3 verification
- **Issue:** `psycopg` installed but `libpq` library not found on macOS; `from pgvector.psycopg import register_vector_async` failed with "no pq wrapper available"
- **Fix:** Installed `psycopg-binary` package which bundles libpq
- **Files modified:** None (runtime dependency install, not source change)
- **Verification:** `python -c "from src.app import app"` passes cleanly
- **Committed in:** `efaffac` (Task 3 commit — requirements.txt already had `psycopg[binary]`)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minor runtime dependency issue. No source code changes required beyond what was planned.

## Issues Encountered

- `psycopg` pure-Python wheel failed to find system `libpq` on macOS. Resolved by installing `psycopg-binary` which bundles its own libpq. The `requirements.txt` already specified `psycopg[binary]` which should handle this on fresh installs.

## User Setup Required

None — no external service configuration required. The Postgres container is self-contained in Docker Compose.

**Note:** To start the Postgres container locally:
```bash
docker compose -f docker-compose.n8n.yml up -d postgres
```

## Next Phase Readiness

- Vector DB foundation is complete and ready for embedding generation (Plan 03)
- Pool lifecycle is wired into FastAPI — embeddings and cache tables will be available on startup
- HNSW indexes are pre-created for cosine similarity search
- No blockers

## Self-Check: PASSED

- [x] `docker-compose.n8n.yml` contains pgvector service — verified via `docker compose config`
- [x] `src/vector/migrations/001_init_vector.sql` contains both tables with HNSW cosine indexes — verified by Read
- [x] `src/vector/db.py` compiles — verified via `python -m py_compile`
- [x] `src/vector/__init__.py` compiles — verified via `python -m py_compile`
- [x] `src/app.py` imports cleanly — verified via `python -c "from src.app import app"`
- [x] All three task commits exist in solo-leveling: `0deb2ca`, `efaffac`
- [x] Parent repo commit exists: `5670fca`

---
*Phase: 01-data-auth-foundation*
*Completed: 2026-05-29*
