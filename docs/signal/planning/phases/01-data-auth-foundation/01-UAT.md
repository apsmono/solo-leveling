---
status: testing
phase: 01-data-auth-foundation
source:
  - 01-01-SUMMARY.md
  - 01-02-SUMMARY.md
  - 01-03-SUMMARY.md
  - 01-04-SUMMARY.md
  - 01-05-SUMMARY.md
started: 2026-05-31T00:30:00.000Z
updated: 2026-05-31T00:30:00.000Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: 1
name: Cold Start Smoke Test
expected: |
  Kill any running server/service. Start the FastAPI app from scratch
  (uvicorn src.app:app --port 8000). Server boots without errors.
  GET /healthz returns 200. Vector pool warning appears if Postgres is
  not running (graceful degradation).
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server/service. Start the FastAPI app from scratch (uvicorn src.app:app --port 8000). Server boots without errors. GET /healthz returns 200. Vector pool warning appears if Postgres is not running (graceful degradation).
result: [pending]

### 2. Unit Test Suite Passes
expected: Run `python -m unittest tests.test_vector_foundation -v` from solo-leveling/. All tests pass (VectorDBTests, EmbedTests, TokenCacheTests, TenantTests, AuthSessionTests). Integration tests skip when SIGNAL_POSTGRES_DSN_TEST is unset.
result: [pending]

### 3. pgvector Postgres Provisioned
expected: Run `docker compose up -d postgres` (or equivalent). Postgres container starts healthy. `psql` or `docker exec` can connect and `SELECT extname FROM pg_extension WHERE extname='vector'` returns `vector`.
result: [pending]

### 4. Vector Tables Created
expected: With Postgres running and the app started once (triggers migration), connect to the signal database. Tables `signal_embeddings` and `signal_token_cache` exist. Both have `owner_id` column. HNSW indexes exist on the embedding columns.
result: [pending]

### 5. Embedding Generation Works
expected: With Postgres running and GEMINI_API_KEY set, saving a library entry triggers the embedding hook. A row appears in `signal_embeddings` with a 768-dim vector. Check via: `SELECT id, array_length(embedding::real[], 1) FROM signal_embeddings LIMIT 1` — should return 768.
result: [pending]

### 6. Token Cache Dedup Works
expected: Ingest the same content twice. The second ingest returns the cached summary (cache hit logged) instead of making a fresh LLM call. Check via: `SELECT * FROM signal_token_cache` — hit_count > 0 for the matching entry.
result: [pending]

### 7. Firebase Session Login Endpoint
expected: POST /auth/session-login with a valid Firebase ID token (from dashboard Google OAuth) returns 200 and sets an `__session` cookie. Cookie attributes: httpOnly=true, secure=true (or false if SESSION_COOKIE_SECURE=false), samesite=strict, max_age=604800 (7 days).
result: [pending]

### 8. Firebase Session Logout Endpoint
expected: POST /auth/session-logout clears the `__session` cookie. Subsequent requests with the old cookie are rejected.
result: [pending]

### 9. Tenant Scoping (owner_id)
expected: All vector queries are scoped by `owner_id`. Check that `signal_embeddings` and `signal_token_cache` rows have the correct `owner_id` value matching `SIGNAL_OWNER_ID` (or `ALLOWED_USER_EMAIL` default).
result: [pending]

### 10. Graceful Degradation Without Postgres
expected: Start the app with SIGNAL_POSTGRES_DSN empty or pointing to a stopped Postgres. App starts normally (logs warning). Non-vector features (library, planning, auth) work. Vector-dependent features (embedding hook, cache) silently skip without crashing.
result: [pending]

## Summary

total: 10
passed: 0
issues: 0
pending: 10
skipped: 0

## Gaps

[none yet]
