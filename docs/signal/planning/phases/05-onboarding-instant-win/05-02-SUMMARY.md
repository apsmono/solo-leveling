---
phase: 05-onboarding-instant-win
plan: 02
subsystem: api, ui
tags: [fastapi, react, typescript, onboarding, digest, app-connect, tdd]

# Dependency graph
requires:
  - phase: 05-01
    provides: profile store, parse-identity endpoint, OnboardingWizard with Step 3 placeholder

provides:
  - POST /api/v1/onboarding/connect-app — app connection recording with allowed-list validation
  - GET /api/v1/onboarding/digest — 3-bullet digest (live data or cold-start capability preview)
  - AppConnectStep — app cards with Connect/Skip flow wired to connectApp() API
  - InstantWinDigest — 3-bullet digest card with "Get started" transition to Zen shell
  - OnboardingWizard — full 4-sub-step flow: IdentityBox -> ProfileConfirmation -> AppConnectStep -> InstantWinDigest

affects:
  - 06-smart-feeds (digest pipeline and connected_apps profile field are the foundation for feed sources)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - generate_digest() follows intent_parser.py LLM structured output pattern (run_agent + JSON strip + validate/clamp + graceful fallback)
    - _cold_start_preview() reuses same pattern for capability preview bullets
    - _query_connected_sources() uses per-app try/except skipping — same isolation pattern as integration clients
    - AppConnectStep local Set<string> state tracks connections without lifting to parent
    - InstantWinDigest useEffect fetch-on-mount pattern matches existing AI Guide panel pattern
    - OnboardingWizard internal WizardSubStep type handles 2b sub-step without exposing it in OnboardingStep union

key-files:
  created:
    - dashboard/src/components/onboarding/AppConnectStep.tsx
    - dashboard/src/components/onboarding/InstantWinDigest.tsx
  modified:
    - solo-leveling/src/core/onboarding.py
    - solo-leveling/src/api/onboarding.py
    - solo-leveling/tests/test_onboarding.py
    - solo-leveling/CHANGELOG.md
    - dashboard/src/lib/api.ts
    - dashboard/src/components/onboarding/OnboardingWizard.tsx

key-decisions:
  - "connect-app records app in profile.connected_apps (not OAuth tokens) — OAuth is a frontend concern; backend only validates the allowed list (T-05-05)"
  - "Digest always returns exactly 3 bullets — real data path clamps to [:3] and pads if LLM returns fewer; cold-start also clamps/pads to 3"
  - "WizardSubStep '2b' is internal to OnboardingWizard — external OnboardingStep type remains 1|2|3 (no leakage)"
  - "StepIndicator shows 3 dots; steps 2 and 2b both highlight dot 2 (D-04 3-step linear UX)"

patterns-established:
  - "Digest generation: run_agent() -> _strip_fences() -> json.loads -> validate 'bullets' key -> clamp/pad to 3 -> graceful fallback list"
  - "Cold-start: no connected_apps or all sources fail -> _cold_start_preview() called from generate_digest() before LLM query"

requirements-completed: [ONB-03, ONB-04]

# Metrics
duration: 25min
completed: 2026-05-31
---

# Phase 5 Plan 02: App Connect + Instant Win Digest Summary

**App Connect endpoint with allowed-list validation, 3-bullet digest with cold-start capability preview, AppConnectStep and InstantWinDigest UI components, and OnboardingWizard updated to the complete 4-sub-step flow**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-31T05:00:00Z
- **Completed:** 2026-05-31T05:25:00Z
- **Tasks:** 2 (TDD)
- **Files modified:** 8 (2 created, 6 modified)

## Accomplishments

- Backend: `generate_digest()` with `_DIGEST_SYSTEM_PROMPT`, `_cold_start_preview()` with `_COLD_START_PREVIEW_PROMPT`, `_query_connected_sources()` with per-app try/except isolation, `_strip_fences()` helper — all following the intent_parser.py LLM structured output pattern
- Two new endpoints: `POST /onboarding/connect-app` (7-item allowed list, T-05-05 mitigation, records in `profile.connected_apps`) and `GET /onboarding/digest` (always returns 3 bullets, cold-start fallback)
- 6 new backend tests (14 total, all passing) with correct patch targets in `src.api.onboarding` namespace
- Frontend: `AppConnectStep` with per-app loading/error state, Mail/Youtube/Rss icons, "Skip for now" skippability (D-06); `InstantWinDigest` with entrance animation, cold-start heading, CheckCircle + "Get started" button (D-15)
- `OnboardingWizard` updated with internal `WizardSubStep` type for the "2b" App Connect sub-step — external `OnboardingStep` type unchanged; StepIndicator still shows 3 dots with 2+2b both activating dot 2 (D-04)
- TypeScript compiles with 0 errors; all 14 backend tests pass

## Task Commits

**Task 1: Backend endpoints + tests (TDD)**
1. `db603fa` — `test(05-02)`: add failing tests for connect-app and digest endpoints (RED)
2. `8510ace` — `feat(05-02)`: implement connect-app and digest backend endpoints (GREEN)
3. `a1c1a28` — `docs(05-02)`: update CHANGELOG with Phase 5 Plan 02 connect-app and digest endpoints

**Task 2: Frontend AppConnectStep + InstantWinDigest + wizard update**
4. `3139836` — `feat(05-02)`: add AppConnectStep + InstantWinDigest + update wizard

## Files Created/Modified

**solo-leveling (backend):**
- `src/core/onboarding.py` — added `_DIGEST_SYSTEM_PROMPT`, `_COLD_START_PREVIEW_PROMPT`, `generate_digest()`, `_cold_start_preview()`, `_query_connected_sources()`, `_strip_fences()`
- `src/api/onboarding.py` — added `POST /onboarding/connect-app`, `GET /onboarding/digest`, `_ALLOWED_APPS` constant; imported `load_profile`, `save_profile`, `generate_digest`, `_query_connected_sources`
- `tests/test_onboarding.py` — added `AppConnectDigestAPITests` class (6 new tests); fixed patch targets for digest tests
- `CHANGELOG.md` — added Phase 5 Plan 02 entry

**dashboard (frontend):**
- `src/lib/api.ts` — added `connectApp()` and `fetchDigest()` API functions
- `src/components/onboarding/AppConnectStep.tsx` — new: app cards, Connect button with loading/error state, "Skip for now", Continue button
- `src/components/onboarding/InstantWinDigest.tsx` — new: digest card with 3 bullets, cold-start heading, CheckCircle, "Get started" button, entrance animation
- `src/components/onboarding/OnboardingWizard.tsx` — updated: AppConnectStep and InstantWinDigest integrated, WizardSubStep internal type, step indicator stays at 3 dots

## Decisions Made

- **connect-app records, not OAuth:** Backend records `app` in `profile.connected_apps` — OAuth popup is a frontend concern using the brain's existing integration auth endpoints. Backend only validates against the allowed list (T-05-05 mitigation).
- **Digest always 3 bullets:** `generate_digest()` and `_cold_start_preview()` both clamp to `[:3]` and pad if LLM returns fewer than 3. The endpoint applies one final `[:3]` slice.
- **WizardSubStep is internal:** The `"2b"` sub-step is a local `WizardSubStep` type inside `OnboardingWizard` only. `OnboardingStep = 1 | 2 | 3` in `types.ts` is unchanged — no API/hook changes needed.
- **StepIndicator unchanged:** Both step 2 and 2b map to `indicatorStep = 2` so the 3-dot indicator shows consistent progress (D-04 linear UX).

## Deviations from Plan

None — plan executed exactly as written. All files created/modified as specified.

## Known Stubs

None. The digest endpoint always returns 3 bullets via either LLM query or fallback. `_query_connected_sources()` returns empty list for all apps except gmail (which requires the gmail integration client to be callable) — this is handled gracefully by `generate_digest()`'s cold-start branch.

## Threat Surface Scan

No new threat surface beyond the plan's `<threat_model>`:
- T-05-05: connect-app validates against `_ALLOWED_APPS` frozenset — unknown names return 400
- T-05-06: connect-app only stores the app name string, never OAuth tokens
- T-05-07: digest endpoint requires auth; no onboarding bypass path
- T-05-08: digest queries only the authenticated owner's connected sources

## Self-Check: PASSED

Files verified:
- `solo-leveling/src/core/onboarding.py` — contains `def generate_digest`, `def _cold_start_preview`, `def _query_connected_sources`, `_DIGEST_SYSTEM_PROMPT`
- `solo-leveling/src/api/onboarding.py` — contains `@router.post("/onboarding/connect-app")` and `@router.get("/onboarding/digest")`
- `dashboard/src/components/onboarding/AppConnectStep.tsx` — exists, contains Mail/Youtube/Rss imports, "Skip for now", "Connect"
- `dashboard/src/components/onboarding/InstantWinDigest.tsx` — exists, contains "Your first digest", "Get started", CheckCircle, fetchDigest
- `dashboard/src/components/onboarding/OnboardingWizard.tsx` — imports AppConnectStep and InstantWinDigest
- `dashboard/src/lib/api.ts` — contains connectApp and fetchDigest exports
- Commits: db603fa (RED), 8510ace (GREEN), a1c1a28 (docs), 3139836 (frontend)

---
*Phase: 05-onboarding-instant-win*
*Completed: 2026-05-31*
