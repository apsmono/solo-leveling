---
phase: 05-onboarding-instant-win
plan: "03"
subsystem: onboarding-error-chain
tags: [bug-fix, error-handling, tdd, backend, frontend]
dependency_graph:
  requires: [05-01, 05-02]
  provides: [CR-01, CR-02, CR-05, WR-02]
  affects: [solo-leveling/src/api/onboarding.py, dashboard/src/components/onboarding/IdentityBox.tsx, dashboard/src/hooks/useOnboarding.ts]
tech_stack:
  added: []
  patterns: [try/finally for loading-state reset, HTTPException(502) for LLM failure, console.error for dropped-save observability]
key_files:
  created: []
  modified:
    - solo-leveling/src/api/onboarding.py
    - solo-leveling/tests/test_onboarding.py
    - dashboard/src/components/onboarding/IdentityBox.tsx
    - dashboard/src/components/onboarding/types.ts
    - dashboard/src/hooks/useOnboarding.ts
decisions:
  - "parse-identity uses HTTPException(502) not a bare dict return so clients can distinguish LLM failure from success"
  - "IdentityBox uses try/finally for loading reset — single exit point prevents stuck Analyzing button"
  - "handleComplete always calls setOnboardingState('complete') after if/else — both branches terminate cleanly"
metrics:
  duration: "~8 min"
  completed: "2026-05-31"
  tasks_completed: 3
  files_modified: 5
---

# Phase 05 Plan 03: Error-Handling Chain Gap Closure Summary

**One-liner:** Surgical four-gap fix closing CR-01/CR-02/CR-05/WR-02 — backend returns 502 on LLM failure, IdentityBox resets loading via finally and guards the response, handleComplete logs a dropped save, ProfileData typed with connected_apps.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | Failing test for parse-identity 502 | 535affa | solo-leveling/tests/test_onboarding.py |
| 1 (GREEN) | parse-identity raises HTTPException(502) | 138c452 | solo-leveling/src/api/onboarding.py |
| 2 | IdentityBox res.status guard + finally + error state | accd2eb | dashboard/src/components/onboarding/IdentityBox.tsx, types.ts |
| 3 | handleComplete logs when no profile to save | 8d2108d | dashboard/src/hooks/useOnboarding.ts |

## What Was Built

### CR-01 — Backend: parse-identity returns HTTP 502 on LLM failure

In `solo-leveling/src/api/onboarding.py`, the `except Exception:` block in `parse_identity_endpoint` previously returned `{"status": "error", ...}` with an implicit HTTP 200. Changed to `raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, ...) from None` while preserving `logger.exception("Failed to parse identity")`. The 400 guard for missing text and the 200 success path are unchanged.

### CR-01 frontend guard + CR-02 — IdentityBox resilient handleSubmit

In `dashboard/src/components/onboarding/IdentityBox.tsx`:
- Added `const [error, setError] = useState<string | null>(null)` error state
- Added `if (res.status !== "ok" || !res.profile)` guard before casting to `ProfileData` — wizard never advances with undefined profile
- Wrapped request in `try/catch/finally` — `finally` calls `setLoading(false)` on every exit path (success, follow-up, error), eliminating the stuck "Analyzing..." button
- Removed inline `setLoading(false)` from the follow-up branch and old catch (replaced by `finally`)
- Error message rendered above textarea: `{error && <p className="text-sm text-red-500 mb-4">{error}</p>}`

### WR-02 — ProfileData typed with connected_apps

In `dashboard/src/components/onboarding/types.ts`, added `connected_apps?: string[];` after `context_templates: string[];`. This removes the need for unsafe type casts in InstantWinDigest (addressed in 05-04).

### CR-05 — handleComplete logs dropped save

In `dashboard/src/hooks/useOnboarding.ts`, added `else` branch to `handleComplete` that calls `console.error("[onboarding] handleComplete called with no profile to save ...")`. The `setOnboardingState("complete")` call remains after the if/else so both branches terminate cleanly, preventing the silent re-onboarding loop.

## Verification

- `cd solo-leveling && python -m unittest tests.test_onboarding -v` — 15 tests, all OK, including new `test_parse_identity_llm_failure_returns_502`
- `cd dashboard && npx tsc --noEmit` — exit 0, no output

## TDD Gate Compliance

- RED gate commit: `535affa` — `test(05-03): add failing test for parse-identity 502 on LLM failure`
- GREEN gate commit: `138c452` — `feat(05-03): parse-identity raises HTTPException(502) on LLM failure (CR-01)`
- Test confirmed FAILING before GREEN implementation (AssertionError: 200 != 502)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all changes are functional fixes with no placeholder data flows.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes beyond the plan's `<threat_model>` scope.

## Self-Check: PASSED

- solo-leveling/src/api/onboarding.py — HTTP_502_BAD_GATEWAY present in except block
- solo-leveling/tests/test_onboarding.py — test_parse_identity_llm_failure_returns_502 present
- dashboard/src/components/onboarding/types.ts — connected_apps?: string[] present
- dashboard/src/components/onboarding/IdentityBox.tsx — finally block, res.status guard, error state all present
- dashboard/src/hooks/useOnboarding.ts — console.error present in else branch of handleComplete
- Commits 535affa, 138c452, accd2eb, 8d2108d all present in git log
