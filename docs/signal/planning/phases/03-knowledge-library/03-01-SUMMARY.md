---
phase: 03-knowledge-library
plan: 01
type: execute
wave: 0
subsystem: solo-leveling + dashboard
tags: [tdd, test-stubs, contracts, vector-search, intent-parser, guide-api]
dependencies:
  requires: [phase-01-complete]
  provides: [03-02-implementation-contracts]
  affects: [solo-leveling/tests, dashboard/src/components/guide, solo-leveling/.env.example]
tech-stack:
  added: []
  patterns: [unittest, conditional-import, skipUnless, AsyncMock, TestClient]
key-files:
  created:
    - solo-leveling/tests/test_vector_search.py
    - solo-leveling/tests/test_intent_parser.py
    - solo-leveling/tests/test_guide_api.py
    - dashboard/src/components/guide/.gitkeep
  modified:
    - solo-leveling/.env.example
decisions:
  - "Conditional import pattern: try/except ImportError at module level + @unittest.skipUnless for graceful skipping when target modules don't exist yet"
  - "Hybrid search contract: keyword-first with vector fallback when keyword results < limit//2"
  - "Intent parser contract: LLM-first with keyword fallback on malformed JSON or exception"
  - "Guide API contract: POST /command (intent parsing), GET /status (metrics), POST /park (distraction capture)"
metrics:
  duration: "~12 minutes"
  completed_date: "2026-05-30"
  tasks: 3
  files_created: 4
  files_modified: 1
  tests_written: 18
  tests_skipped: 18
  commits: 5
---

# Phase 03 Plan 01: Wave 0 — Test Stubs & API Contracts Summary

**One-liner:** Created 18 TDD contract tests across three modules (vector search, intent parser, guide API) that skip gracefully until Wave 1-4 implementations land, plus scaffolded the dashboard guide component directory and documented Phase 3 environment variables.

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Vector search contract tests | `2930942` (solo-leveling) | `tests/test_vector_search.py` |
| 2 | Intent parser contract tests | `c96c7fb` (solo-leveling) | `tests/test_intent_parser.py` |
| 3 | Guide API contract tests + env vars + dashboard scaffold | `666a61e` (solo-leveling), `c0ccb82` (dashboard), `33b637d` (parent) | `tests/test_guide_api.py`, `.env.example`, `dashboard/src/components/guide/.gitkeep` |

## Test Inventory

### `test_vector_search.py` (7 tests)

| Test Class | Count | Gating | Coverage |
|-----------|-------|--------|----------|
| `VectorSearchTests` | 6 | `@unittest.skipUnless` (module exists) | keyword mode, vector mode, hybrid prefers keyword, hybrid falls back to vector, owner_id scoping, empty query |
| `VectorSearchIntegrationTests` | 1 | `SIGNAL_POSTGRES_DSN_TEST` env + module exists | Live vector search with Gemini embedding |

### `test_intent_parser.py` (6 tests)

| Test Class | Count | Gating | Coverage |
|-----------|-------|--------|----------|
| `IntentParserTests` | 6 | `@unittest.skipUnless` (module exists) | structured dict return, library_search intent, park_distraction intent, malformed JSON fallback, exception fallback, original text preservation |

### `test_guide_api.py` (5 tests)

| Test Class | Count | Gating | Coverage |
|-----------|-------|--------|----------|
| `GuideAPITests` | 5 | `@unittest.skipUnless` (module exists) | POST /command parses intent, POST /command missing text 400, GET /status returns metrics, POST /park creates entry, POST /park missing text 400 |

## Environment Variables Added

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIGNAL_INTENT_LLM_MODEL` | (empty = same as GEMINI_MODEL) | Gemini model for intent parsing |
| `SIGNAL_INTENT_KEYWORD_FALLBACK` | `true` | Enable/disable keyword fallback when LLM parsing fails |

## Deviations from Plan

None — plan executed exactly as written.

## Auth Gates

None.

## Known Stubs

None — this is a Wave 0 test-stub plan; all "stubs" are intentional contract definitions that will be satisfied by Wave 1-4 implementations.

## Threat Flags

None — all tests use mocked external dependencies. Integration tests are gated behind `SIGNAL_POSTGRES_DSN_TEST`. No new security surface introduced.

## Self-Check: PASSED

- [x] `solo-leveling/tests/test_vector_search.py` exists and compiles
- [x] `solo-leveling/tests/test_intent_parser.py` exists and compiles
- [x] `solo-leveling/tests/test_guide_api.py` exists and compiles
- [x] `dashboard/src/components/guide/.gitkeep` exists
- [x] `solo-leveling/.env.example` contains `SIGNAL_INTENT_LLM_MODEL`
- [x] `solo-leveling/.env.example` contains `SIGNAL_INTENT_KEYWORD_FALLBACK`
- [x] All 18 tests run (skipped=18) — graceful skip when modules not yet implemented
- [x] Commit `2930942` exists in solo-leveling
- [x] Commit `c96c7fb` exists in solo-leveling
- [x] Commit `666a61e` exists in solo-leveling
- [x] Commit `c0ccb82` exists in dashboard
- [x] Commit `33b637d` exists in parent repo
