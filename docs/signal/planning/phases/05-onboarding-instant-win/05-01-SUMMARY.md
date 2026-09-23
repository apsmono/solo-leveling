---
phase: 05-onboarding-instant-win
plan: 01
subsystem: api, ui
tags: [fastapi, react, typescript, onboarding, firebase-auth, llm-parsing]

# Dependency graph
requires:
  - phase: 04-zen-shell-clarity-board
    provides: DashboardPage panel A where OnboardingWizard is injected
  - phase: 03-knowledge-library
    provides: run_agent() dispatcher used by parse_identity()
  - phase: 01-data-auth-foundation
    provides: Firebase auth (require_auth), data/ local-first persistence pattern

provides:
  - GET /api/v1/profile — first-run detection (404 when no profile)
  - POST /api/v1/profile — profile CRUD
  - POST /api/v1/onboarding/parse-identity — LLM-based profile parsing from free text
  - POST /api/v1/profile/onboarding-step — D-10 step resume tracking
  - useOnboarding hook — first-run detection + D-10 resume + wizard state
  - OnboardingWizard — 3-step container rendering IdentityBox and ProfileConfirmation
  - IdentityBox — free text input with AI follow-up handling
  - ProfileConfirmation — parsed profile card with Edit and Confirm

affects:
  - 05-02 (app connect + instant win digest builds on this profile/step foundation)
  - 06-smart-feeds (uses profile.suggested_apps for relevant feed config)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - profile_store.py follows data/ local-first JSON pattern (same as reminders.py, scheduler.py)
    - parse_identity() follows intent_parser.py LLM structured output pattern (run_agent + JSON strip + validate/clamp)
    - useOnboarding follows useAuth.ts hook pattern (useState + useEffect for async init)
    - First-run detection: 404 on GET /profile is the canonical signal — no localStorage bypass (D-08)

key-files:
  created:
    - solo-leveling/src/core/profile_store.py
    - solo-leveling/src/core/onboarding.py
    - solo-leveling/src/api/profile.py
    - solo-leveling/src/api/onboarding.py
    - solo-leveling/tests/test_onboarding.py
    - dashboard/src/components/onboarding/types.ts
    - dashboard/src/hooks/useOnboarding.ts
    - dashboard/src/components/onboarding/StepIndicator.tsx
    - dashboard/src/components/onboarding/IdentityBox.tsx
    - dashboard/src/components/onboarding/ProfileConfirmation.tsx
    - dashboard/src/components/onboarding/OnboardingWizard.tsx
  modified:
    - solo-leveling/src/api/v1_router.py
    - solo-leveling/CHANGELOG.md
    - dashboard/src/lib/api.ts
    - dashboard/src/components/dashboard/DashboardPage.tsx

key-decisions:
  - "Backend 404 on GET /profile is the authoritative first-run signal — frontend follows backend (no localStorage-only bypass per D-08/T-05-03)"
  - "AI follow-up limited to 1 round per D-01 — second submit always parses regardless of needs_followup"
  - "handleComplete also calls saveProfile with onboarding_step=3 to mark completion atomically"
  - "Network error on profile fetch falls through to state=complete (non-blocking) — onboarding never blocks the user"

patterns-established:
  - "Profile local-first: data/profile.json, same mkdir(parents=True) + json.dumps pattern as reminders/scheduler"
  - "LLM structured output: run_agent() → strip markdown fences → json.loads → validate/clamp fields → graceful fallback dict"
  - "D-10 resume: onboarding_step stored in profile.json, checked on mount, persisted on every step change via /profile/onboarding-step"
  - "First-run guard: 404 = start at step 1; profile.onboarding_step < 3 = resume; >= 3 = complete"

requirements-completed: [ONB-02, ONB-03]

# Metrics
duration: 35min
completed: 2026-05-31
---

# Phase 5 Plan 01: Onboarding Backend + Wizard Steps 1-2 Summary

**Profile store + LLM identity parsing backend with Firebase auth, first-run detection hook, IdentityBox + ProfileConfirmation wizard steps wired into DashboardPage Panel A**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-05-31T04:00:00Z
- **Completed:** 2026-05-31T04:35:00Z
- **Tasks:** 2
- **Files modified:** 16 (11 created, 5 modified)

## Accomplishments

- Full onboarding backend: profile CRUD, LLM identity parsing with constrained system prompt, D-10 step resume tracking — all behind Firebase auth
- 8-test contract suite (all passing) covering 404 first-run detection, profile save, parse-identity happy/sad/followup paths, step save, auth requirement
- Frontend wizard: useOnboarding hook with D-10 resume, IdentityBox (free text + AI follow-up), ProfileConfirmation (bullets + Edit/Confirm), StepIndicator, OnboardingWizard container — conditionally rendered in DashboardPage Panel A
- TypeScript compiles clean (0 errors)

## Task Commits

Each task was committed atomically:

**Task 1: Backend profile store + onboarding endpoints + tests (TDD)**
1. `3e8bf71` — `test(05-01)`: add failing tests for onboarding profile endpoints (RED)
2. `92a6cc5` — `feat(05-01)`: implement onboarding backend (profile store, endpoints, v1 router) (GREEN)
3. `5e4f7bc` — `docs(05-01)`: update CHANGELOG with Phase 5 onboarding backend

**Task 2: First-run detection hook + Identity Box + Profile Confirmation UI**
4. `115a60f` — `feat(05-01)`: add onboarding wizard, first-run detection, identity box, profile confirmation

## Files Created/Modified

**solo-leveling (backend):**
- `src/core/profile_store.py` — load_profile / save_profile / load_onboarding_step / save_onboarding_step
- `src/core/onboarding.py` — parse_identity() via run_agent() with _PROFILE_SYSTEM_PROMPT; graceful fallback on parse failure
- `src/api/profile.py` — GET /profile (404 first-run) + POST /profile; require_auth
- `src/api/onboarding.py` — POST /onboarding/parse-identity + POST /profile/onboarding-step; require_auth
- `src/api/v1_router.py` — registered onboarding and profile routers (modified)
- `CHANGELOG.md` — added Phase 5 entry under Unreleased/Added (modified)
- `tests/test_onboarding.py` — 8 contract tests (OnboardingAPITests class)

**dashboard (frontend):**
- `src/components/onboarding/types.ts` — ProfileData, OnboardingStep, OnboardingState
- `src/hooks/useOnboarding.ts` — first-run detection, D-10 resume, step/profile state management
- `src/components/onboarding/StepIndicator.tsx` — dot row with accent/success/border states
- `src/components/onboarding/IdentityBox.tsx` — free text textarea + parseIdentity() + AI follow-up (1 round)
- `src/components/onboarding/ProfileConfirmation.tsx` — profile bullets + Edit + Confirm buttons
- `src/components/onboarding/OnboardingWizard.tsx` — 3-step container with StepIndicator
- `src/lib/api.ts` — parseIdentity, fetchProfile, saveProfile, saveOnboardingStep API functions (modified)
- `src/components/dashboard/DashboardPage.tsx` — useOnboarding hook, onboarding loading guard, conditional OnboardingWizard in Panel A (modified)

## Decisions Made

- **404 as first-run signal:** Backend GET /profile returning 404 is authoritative — no localStorage bypass path (enforces T-05-03 threat mitigation).
- **1-round follow-up (D-01):** IdentityBox sends a second submit directly to parseIdentity regardless of needs_followup flag; second response always produces a profile.
- **handleComplete saves profile with onboarding_step=3:** Atomically marks onboarding complete when user confirms profile, preventing step resume after completion.
- **Network error = non-blocking:** If profile fetch fails (not 404), onboardingState defaults to "complete" so users are never blocked from the dashboard.

## Deviations from Plan

None - plan executed exactly as written. All backend files existed in untracked state from a previous partial execution; committed with proper TDD RED/GREEN sequence as specified.

## Issues Encountered

- `python3` on the system resolved to Python 3.9 (venv symlink points to 3.14 but system `python3` was 3.9). Used `.venv/bin/python3.14` explicitly to run tests — all 8 passed.

## Known Stubs

- `OnboardingWizard` Step 3 renders a placeholder div: "Step 3: App Connect + Digest" — intentional per plan spec. Plan 05-02 will replace this with the App Connect + Instant Win digest flow.

## Threat Surface Scan

No new threat surface beyond what was documented in the plan's `<threat_model>`. All T-05-01 through T-05-03 mitigations are implemented:
- T-05-01/02: parse_identity() constrains LLM output to JSON schema, clamps suggested_apps to allowed list, validated/clamped fields, graceful fallback on malformed JSON
- T-05-03: Backend /profile is authoritative; no localStorage-only bypass path exists
- T-05-SC: No new packages installed

## Next Phase Readiness

- 05-02 (App Connect + Instant Win) can proceed: profile store, parse-identity endpoint, and step tracking are all in place
- Wizard Step 3 placeholder is ready for replacement
- useOnboarding hook exports handleComplete — ready to wire to digest generation in 05-02

## Self-Check: PASSED

All files verified:
- solo-leveling backend: profile_store.py, core/onboarding.py, api/profile.py, api/onboarding.py, tests/test_onboarding.py
- dashboard frontend: types.ts, useOnboarding.ts, OnboardingWizard.tsx, IdentityBox.tsx, ProfileConfirmation.tsx, StepIndicator.tsx
- Commits: 3e8bf71 (test RED), 92a6cc5 (feat GREEN), 5e4f7bc (docs changelog), 115a60f (feat frontend)

---
*Phase: 05-onboarding-instant-win*
*Completed: 2026-05-31*
