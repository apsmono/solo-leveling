---
phase: 01-data-auth-foundation
plan: 03
type: execute
wave: 2
subsystem: vector
requirements:
  - INFRA-02
  - INFRA-03
tags: [vector, embedding, gemini, cache, dedup, hooks]
dependency_graph:
  requires: [01-02]
  provides: [01-04]
  affects: [src.vector, src.core.libraries]
tech_stack:
  added: [google-genai, pgvector, psycopg3]
  patterns: [lazy-singleton-client, fire-and-forget-async-hook, best-effort-cache-write]
key_files:
  created:
    - solo-leveling/src/vector/embed.py
    - solo-leveling/src/vector/hooks.py
    - solo-leveling/src/vector/cache.py
  modified:
    - solo-leveling/src/core/libraries.py
    - solo-leveling/tests/test_vector_foundation.py
decisions:
  - "embed_text is synchronous (Gemini SDK call is sync) — callers that need async wrap it"
  - "Hook fires via asyncio.get_running_loop().create_task() from _capture_entry, only when SIGNAL_POSTGRES_DSN is set and an event loop exists"
  - "Tests use MagicMock for pool.connection() context manager to match psycopg3 AsyncConnection API"
  - "Store cache uses ON CONFLICT DO UPDATE with hit_count increment for idempotent writes"
metrics:
  duration: "~25 minutes"
  completed_date: "2026-05-29"
  tasks: 3
  files_created: 3
  files_modified: 2
---

# Phase 01 Plan 03: Gemini Embedding Pipeline + Token Cache Summary

**One-liner:** Gemini embedding generation (768-dim), library save hooks, and cosine-similarity token cache for near-duplicate deduplication.

## What Was Built

### Task 1: embed.py + hooks.py
- `src/vector/embed.py` — Gemini embedding client with lazy singleton (`_get_client`), `embed_text()` returning 768-dim vectors, and `content_hash()` SHA-256 helper.
- `src/vector/hooks.py` — `on_entry_saved()` async fire-and-forget hook that upserts embeddings into `signal_embeddings` with `ON CONFLICT UPDATE`. Wrapped in try/except so embedding failures never break library saves.

### Task 2: cache.py
- `src/vector/cache.py` — `check_cache()` and `store_cache()` for token-level deduplication.
- Cosine distance threshold from `SIGNAL_COSINE_THRESHOLD` (default 0.08).
- `store_cache()` is best-effort: catches all exceptions, logs warning, never raises.
- All SQL uses `%s` parameterized queries; `owner_id` scopes every query.

### Task 3: Hook library saves + update tests
- `src/core/libraries.py` — added `_fire_embedding_hook()` helper called from `_capture_entry()` after every save. Only fires when `SIGNAL_POSTGRES_DSN` is set and an event loop is running (avoids breaking sync scripts/tests).
- `tests/test_vector_foundation.py` — updated all tests to match real module APIs:
  - `EmbedTests.test_embed_text_dimensions` — sync test (embed_text is sync, not async)
  - `EmbedTests.test_on_entry_saved_inserts_row` — imports from `src.vector.hooks`
  - `EmbedTests.test_on_entry_saved_never_raises` — new test verifying hook exception safety
  - `TokenCacheTests` — fixed mock pool/connection patterns for psycopg3 `connection()` context manager
  - `TenantTests` — fixed mock patterns

## Verification Results

| Test | Result |
|------|--------|
| `python -m py_compile src/vector/embed.py src/vector/hooks.py src/vector/cache.py` | PASS |
| `EmbedTests.test_embed_text_dimensions` | PASS |
| `TokenCacheTests.test_cache_miss_returns_none` | PASS |
| `TokenCacheTests.test_cache_hit_returns_summary` | PASS |
| `TokenCacheTests.test_cache_hit_logged` | PASS |
| `TokenCacheTests.test_store_cache_inserts_row` | PASS |
| `TokenCacheTests.test_store_cache_never_raises` | PASS |
| `EmbedTests.test_on_entry_saved_inserts_row` | PASS |
| `EmbedTests.test_on_entry_saved_never_raises` | PASS |
| `TenantTests.test_owner_id_written_correctly` | PASS |
| `TenantTests.test_config_owner_id_defaults_to_allowed_email` | PASS |
| Integration tests (gated behind `SIGNAL_POSTGRES_DSN_TEST`) | SKIP (expected) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] embed_text is synchronous, not async**
- **Found during:** Task 3 (test updates)
- **Issue:** The original test stubs treated `embed_text` as async (`await embed_text(...)`), but `google.genai.Client.models.embed_content()` is a synchronous call.
- **Fix:** Changed `test_embed_text_dimensions` to a synchronous test. All cache/hook tests that call `embed_text` now patch it with a sync return value.
- **Files modified:** `tests/test_vector_foundation.py`
- **Commit:** 68485b2

**2. [Rule 1 - Bug] Mock pool patterns didn't match psycopg3 AsyncConnection API**
- **Found during:** Task 3 (test execution)
- **Issue:** Original tests used `mock_pool.__aenter__` patterns, but psycopg3 uses `pool.connection()` as an async context manager (`async with pool.connection() as conn:`).
- **Fix:** Updated all mocks to use `mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)` pattern.
- **Files modified:** `tests/test_vector_foundation.py`
- **Commit:** 68485b2

**3. [Rule 2 - Missing critical functionality] Test for hook exception safety**
- **Found during:** Task 3 (test review)
- **Issue:** The original stubs had `test_on_entry_saved_inserts_row` but no test verifying the try/except guard in hooks.py (threat T-01-09 mitigation).
- **Fix:** Added `test_on_entry_saved_never_raises` that patches `get_pool` to raise RuntimeError and asserts no exception propagates.
- **Files modified:** `tests/test_vector_foundation.py`
- **Commit:** 68485b2

## Threat Surface Scan

No new threat surface outside the plan's threat model. All mitigations verified:

| Threat ID | Mitigation | Status |
|-----------|-----------|--------|
| T-01-09 | try/except in `on_entry_saved` — log warning, never raise | VERIFIED (test_on_entry_saved_never_raises) |
| T-01-10 | `_get_client` reads from env; never logs the key | VERIFIED (no key in logs) |
| T-01-11 | psycopg3 parameterized queries only; no f-string SQL | VERIFIED (all `%s` placeholders) |
| T-01-12 | Threshold is server-side constant from env | VERIFIED (`_COSINE_THRESHOLD` env-read) |
| T-01-13 | Every query filters by `owner_id` | VERIFIED (owner_id in WHERE clauses) |

## Known Stubs

None. All modules are fully wired with real data sources.

## Commits

| Hash | Message | Files |
|------|---------|-------|
| 701e043 | feat(01-03): create embed.py and hooks.py for Gemini vector indexing | `src/vector/embed.py`, `src/vector/hooks.py` |
| 2147087 | feat(01-03): create cache.py for token-level cosine deduplication | `src/vector/cache.py` |
| 68485b2 | feat(01-03): hook library saves to vector embedding + update tests | `src/core/libraries.py`, `tests/test_vector_foundation.py` |

## Self-Check: PASSED

- [x] `src/vector/embed.py` exists and compiles
- [x] `src/vector/hooks.py` exists and compiles
- [x] `src/vector/cache.py` exists and compiles
- [x] `src/core/libraries.py` compiles after edits
- [x] All 12 relevant unit tests pass
- [x] Integration tests skip when `SIGNAL_POSTGRES_DSN_TEST` is unset
- [x] All 3 commits exist on branch
