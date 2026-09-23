---
phase: 02-n8n-execution-layer
plan: 01
subsystem: infra
tags: [n8n, httpx, rest-client, error-abstraction, config]

requires:
  - phase: 01-data-auth-foundation
    provides: backend home in solo-leveling, shared Postgres, config patterns
provides:
  - n8n Public REST API client (trigger/execution/credential endpoints)
  - 7-class error abstraction with soft owner-facing messages (INFRA-05)
  - N8N_BASE_URL / N8N_API_KEY config + .env.example documentation
  - tests/test_n8n_execution.py scaffold (N8NClientTests + ErrorTests green)
affects: [02-02, 02-03, smart-feeds, smart-drafts, safety-recovery]

tech-stack:
  added: []
  patterns: ["thin httpx client with env-gated _request (github/client.py analog)", "str-Enum + ordered pattern table for classification (governor.py analog)"]

key-files:
  created:
    - solo-leveling/src/n8n/__init__.py
    - solo-leveling/src/n8n/client.py
    - solo-leveling/src/n8n/errors.py
    - solo-leveling/tests/test_n8n_execution.py
  modified:
    - solo-leveling/src/core/config.py
    - solo-leveling/.env.example

key-decisions:
  - "n8n auth via X-N8N-API-KEY header (vs basic auth) — Public REST API v1 standard"
  - "N8N_BASE_URL defaults to http://localhost:5678 (bundled docker-compose); API key empty by default"
  - "Error messages are owner-friendly templates only — raw exception text never reaches the AI Guide"

patterns-established:
  - "n8n client mirrors src/integrations/github/client.py exactly (httpx, _request, health_check)"
  - "classify_error scans a flattened lowercased payload against an ordered (substring, ErrorClass) table"

requirements-completed: [N8N-01, INFRA-05]

duration: ~10min
completed: 2026-05-30
---

# Phase 2 / Plan 01: n8n REST Client + Error Abstraction Summary

**httpx n8n Public REST client (workflow/execution/credential endpoints) plus a 7-class error→soft-message abstraction, env config, and a 21-test offline scaffold.**

## Performance

- **Duration:** ~10 min
- **Tasks:** 2 (both TDD)
- **Files modified:** 6 (4 created, 2 modified)

## Accomplishments
- `src/n8n/client.py` — `trigger_workflow`, `get_execution`, `list_executions`, `create/update/delete/list_credential(s)`, `health_check`, env-gated `_request`.
- `src/n8n/errors.py` — `ErrorClass` (7 members), `classify_error`, `soft_error_message` (no stack traces, suggests a fix per D-11).
- `N8N_BASE_URL` / `N8N_API_KEY` added to `config.py` + `.env.example` with API-key generation notes.
- `tests/test_n8n_execution.py` — `N8NClientTests` (12) + `ErrorTests` (9) green; 4 classes stubbed for later waves.

## Files Created/Modified
- `src/n8n/client.py` - n8n Public REST API client
- `src/n8n/errors.py` - error classification + soft messages
- `src/n8n/__init__.py` - package init
- `tests/test_n8n_execution.py` - test scaffold (6 classes)
- `src/core/config.py` - N8N_BASE_URL, N8N_API_KEY
- `.env.example` - n8n env documentation

## Decisions Made
- Followed the `github/client.py` thin-client pattern verbatim, swapping the auth header to `X-N8N-API-KEY` and prefixing `/api/v1`.

## Deviations from Plan
None - plan executed as written.

## Issues Encountered
None.

## Next Phase Readiness
- Client + error layer ready for the executor, credential injection, and callback (plans 02-02, 02-03).

---
*Phase: 02-n8n-execution-layer*
*Completed: 2026-05-30*
