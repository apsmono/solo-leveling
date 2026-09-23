---
phase: 05-onboarding-instant-win
plan: "04"
subsystem: onboarding
tags: [honest-labeling, digest, mode-flag, sc-3, onb-03, onb-04, wr-02, tdd]
dependency_graph:
  requires: [05-01, 05-02, 05-03]
  provides: [SC-3-closure, ONB-03-closure, ONB-04-closure, WR-02-closure]
  affects: [solo-leveling/src/core/onboarding.py, solo-leveling/src/api/onboarding.py, dashboard/src/components/onboarding/InstantWinDigest.tsx, dashboard/src/lib/api.ts]
tech_stack:
  added: []
  patterns: [fetcher-registry, backend-mode-flag, honest-labeling]
key_files:
  created: []
  modified:
    - solo-leveling/src/core/onboarding.py
    - solo-leveling/src/api/onboarding.py
    - solo-leveling/tests/test_onboarding.py
    - dashboard/src/components/onboarding/InstantWinDigest.tsx
    - dashboard/src/lib/api.ts
    - solo-leveling/CHANGELOG.md
decisions:
  - "mode flag sourced from actually-fetched data (not profile.connected_apps) — this is what closes the false-labeling gap"
  - "_SOURCE_FETCHERS registry replaces gmail-only literal branch — future integrations are one-line additions"
  - "Frontend defaults mode state to 'preview' — the honest non-overclaiming default before backend responds"
metrics:
  duration: ~20 min
  completed: "2026-05-31"
  tasks_completed: 2
  tasks_total: 2
---

# Phase 05 Plan 04: Instant Win Honest Labeling (SC-3/ONB-03/ONB-04/WR-02) Summary

**One-liner:** Backend digest endpoint now returns `mode="live"|"preview"` derived from actually-fetched integration data; InstantWinDigest card labels truthfully as "Preview"/"What Signal will do for you" on cold start and "Your first digest"/"Last 24 hours" only when real data is live.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | TDD failing tests for mode flag | 704f290 | tests/test_onboarding.py |
| 1 (GREEN) | Backend mode flag + fetcher registry | e1aea1b | src/core/onboarding.py, src/api/onboarding.py |
| 1 (docs) | CHANGELOG update | 5466d5e | CHANGELOG.md |
| 2 | Frontend honest labeling + WR-02 fix | 9e9f889 (dashboard) | InstantWinDigest.tsx, api.ts |

## What Was Built

### Task 1: Backend (TDD — solo-leveling)

**`_query_connected_sources()` — fetcher registry pattern:**
- Replaced the single `if app == "gmail"` literal branch with `_SOURCE_FETCHERS: dict[str, Callable[[], list[Any]]]`
- `_gmail_fetcher()` is a named function (not an inline lambda) registered at module level
- For each app in `profile.connected_apps`, looks up its fetcher; apps with no registered fetcher are skipped (logged at debug)
- Adding future integrations (youtube, notion, etc.) is one line in `_SOURCE_FETCHERS`
- `from collections.abc import Callable` added to imports

**`digest_endpoint()` — mode flag:**
- `mode = "live" if connected_data else "preview"` — derived from actual fetched data, not the profile's `connected_apps` list
- Returns `{"status": "ok", "bullets": bullets[:3], "mode": mode}`
- This is the single source of truth: live only when real integration data was fetched

**Tests (17 total, all green):**
- `test_digest_mode_live_with_connected_data` — patches `_query_connected_sources` to return data; asserts `mode="live"`
- `test_digest_mode_preview_on_cold_start` — patches `_query_connected_sources` to return `[]`; asserts `mode="preview"`
- All 15 pre-existing tests continue to pass

### Task 2: Frontend (dashboard)

**`api.ts` — `fetchDigest()` return type:**
- Updated to `Promise<{ status: string; bullets: string[]; mode: "live" | "preview" }>`

**`InstantWinDigest.tsx` — honest labeling:**
- `isColdStart()` helper and its `(profile as unknown as { ... }).connected_apps` cast removed entirely (WR-02 closed)
- `const [mode, setMode] = useState<"live" | "preview">("preview")` — defaults to the honest non-overclaiming value
- `setMode(data.mode ?? "preview")` in the `load()` success path; catch block leaves mode at `"preview"`
- `const isPreview = mode === "preview"` replaces `const coldStart = isColdStart(profile)`
- Card labels driven by `isPreview`:
  - Sparkles span: `isPreview ? "Preview" : "Your first digest"`
  - Right span: `isPreview ? "What Signal will do for you" : "Last 24 hours"`
  - Intro text: `isPreview && <p>Here's what I'll do for you — connect an app to see your live 24-hour digest.</p>`
- `profile` prop renamed `_profile` to avoid unused-var lint (prop kept in interface — OnboardingWizard call site unchanged)
- TypeScript check exits 0 with no output

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| mode flag derived from `bool(connected_data)` not `bool(profile.connected_apps)` | `connected_apps` records intent; `connected_data` records reality — only the latter can honestly label the card |
| Registry pattern for `_SOURCE_FETCHERS` | Generalization that makes the function honest (any registered fetcher can contribute) and extensible (one-line additions) |
| Frontend defaults mode to `"preview"` | Non-overclaiming before backend responds; error path also stays at preview since fallback bullets are not live data |
| Kept `profile` prop in component interface | Avoids breaking OnboardingWizard call site; prefixed `_profile` to suppress unused-var lint without structural change |

## Deviations from Plan

None — plan executed exactly as written. TDD RED/GREEN cycle followed for Task 1.

## TDD Gate Compliance

- RED commit `704f290` (`test(05-04): add failing tests...`) — 2 new tests failing with `KeyError: 'mode'`
- GREEN commit `e1aea1b` (`feat(05-04): digest endpoint returns mode flag...`) — all 17 tests pass

## Known Stubs

None — all behavior is fully implemented and wired.

## Threat Flags

None — no new trust boundaries introduced beyond those described in the plan's threat model.

## Self-Check: PASSED

- `solo-leveling/src/api/onboarding.py` exists and contains `"mode"` and `mode = "live" if connected_data else "preview"`
- `solo-leveling/src/core/onboarding.py` exists and contains `_SOURCE_FETCHERS` (no `if app == "gmail"` literal branch)
- `solo-leveling/tests/test_onboarding.py` contains both new mode tests; all 17 pass
- `dashboard/src/components/onboarding/InstantWinDigest.tsx` has no `as unknown as` cast, no `isColdStart`, has `mode` state
- `dashboard/src/lib/api.ts` fetchDigest return type includes `mode: "live" | "preview"`
- `npx tsc --noEmit` exits 0 with no output
- Commits: 704f290 (RED), e1aea1b (GREEN), 5466d5e (docs), 9e9f889 (dashboard)
