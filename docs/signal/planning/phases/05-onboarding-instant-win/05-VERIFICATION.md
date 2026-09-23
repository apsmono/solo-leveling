---
phase: 05-onboarding-instant-win
verified: 2026-05-31T12:00:00Z
status: human_needed
score: 6/6 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 2/4
  gaps_closed:
    - "parse-identity returns HTTP 502 (not HTTP 200) when the LLM fails (CR-01)"
    - "IdentityBox does not advance the wizard or set a null profile when parse-identity errors (CR-01 frontend guard)"
    - "IdentityBox button does not stay permanently 'Analyzing...' after a successful AI parse (CR-02)"
    - "useOnboarding.handleComplete logs an error and still completes (no silent re-onboarding loop) when profile is null (CR-05)"
    - "ProfileData carries connected_apps without an unsafe type cast (WR-02)"
    - "The digest endpoint returns a mode flag distinguishing 'live' from 'preview' (SC-3/ONB-04 honest-labeling)"
    - "When no live connected data exists, the Instant Win card is honestly labeled as a preview (SC-3/ONB-04)"
    - "InstantWinDigest derives its preview/live state from the backend mode, not from an unsafe profile type cast (WR-02 closure)"
  gaps_remaining: []
  regressions: []
deferred:
  - truth: "Real OAuth flow wired to Connect button so live data can flow to digest"
    addressed_in: "Future milestone (new subsystem: OAuth client registration + redirect/callback endpoints + per-owner token storage)"
    evidence: "05-04-PLAN.md investigation confirms the brain has NO browser-triggerable OAuth authorization endpoint; Gmail uses InstalledAppFlow (desktop/CLI). Wiring real web-OAuth is a new subsystem beyond gap closure scope."
human_verification:
  - test: "Complete the onboarding flow end-to-end and verify the Instant Win digest labels are honest"
    expected: "On cold start (no OAuth), the digest card shows 'Preview' / 'What Signal will do for you' and NOT 'Your first digest' / 'Last 24 hours'. The intro text reads 'Here's what I'll do for you — connect an app to see your live 24-hour digest.'"
    why_human: "Visual inspection of rendered card labels; requires running the dashboard and completing the wizard flow"
  - test: "Trigger an LLM failure on parse-identity and verify the wizard stays on Step 1 with an error message"
    expected: "With GEMINI_API_KEY unset or invalid, submitting text in IdentityBox shows 'I couldn't analyze that right now. Please try again.' in red, the button resets from 'Analyzing...' to 'Continue', and the wizard does NOT advance to Step 2"
    why_human: "Requires live backend instance with intentionally broken LLM config; the code path is verified correct but runtime behavior (e.g. whether onNext() fires before catch) needs live test"
  - test: "Verify Panel B (AI Guide) remains visible and interactive during all onboarding steps"
    expected: "The AI Guide panel should be present and accessible in Panel B while the onboarding wizard occupies Panel A — at all three steps"
    why_human: "Visual layout check; Panel B is rendered in DashboardPage outside the onboarding conditional but may be obscured on narrow viewports"
---

# Phase 5: Onboarding + Instant Win Verification Report (Re-verification)

**Phase Goal:** Close all remaining Phase 5 verification gaps: error-handling chain (CR-01/CR-02/CR-05/WR-02), Instant Win OAuth honest-labeling (SC-3/ONB-03/ONB-04), and re-onboarding loop fix.
**Verified:** 2026-05-31T12:00:00Z
**Status:** human_needed
**Re-verification:** Yes — after gap closure via Plans 03 and 04

---

## Goal Achievement

### Observable Truths (Plans 03 + 04 Must-Haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | parse-identity returns HTTP 502 (not HTTP 200) when the LLM fails (CR-01) | VERIFIED | `solo-leveling/src/api/onboarding.py:47-52`: `except Exception` raises `HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)`. Test `test_parse_identity_llm_failure_returns_502` passes. |
| 2 | IdentityBox does not advance the wizard or set a null profile when parse-identity errors (CR-01 frontend guard) | VERIFIED | `dashboard/src/components/onboarding/IdentityBox.tsx:43-46`: `if (res.status !== "ok" || !res.profile)` guard returns early with error message. `apiPost` throws on non-2xx (line 32: `if (!res.ok) throw`), so 502 triggers catch block which also sets error message. |
| 3 | IdentityBox button does not stay permanently 'Analyzing...' after a successful AI parse (CR-02) | VERIFIED | `IdentityBox.tsx:63-65`: `finally { setLoading(false) }` resets loading on every exit path (success, follow-up, error). |
| 4 | useOnboarding.handleComplete logs an error and still completes when profile is null (CR-05) | VERIFIED | `dashboard/src/hooks/useOnboarding.ts:86-91`: `else` branch calls `console.error("[onboarding] handleComplete called with no profile to save...")`. `setOnboardingState("complete")` executes after the if/else — both branches terminate cleanly. |
| 5 | ProfileData carries connected_apps without an unsafe type cast (WR-02) | VERIFIED | `dashboard/src/components/onboarding/types.ts:13`: `connected_apps?: string[]` field added to `ProfileData`. `InstantWinDigest.tsx` has zero `as unknown as` casts (confirmed by grep). |
| 6 | Digest endpoint returns mode flag and InstantWinDigest labels honestly (SC-3/ONB-04 honest-labeling) | VERIFIED | Backend: `onboarding.py:121`: `mode = "live" if connected_data else "preview"` — derived from actually-fetched data. Returns `{status, bullets, mode}`. Frontend: `InstantWinDigest.tsx:31`: `useState<"live" \| "preview">("preview")` (honest default). Line 44: `setMode(data.mode ?? "preview")`. Lines 111/114: labels switch on `isPreview` — "Preview" / "What Signal will do for you" vs "Your first digest" / "Last 24 hours". Line 92-96: intro text shown only on preview. |

**Score:** 6/6 truths verified

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | Real OAuth flow wired to Connect button so live data can flow to digest | Future milestone (new subsystem) | 05-04-PLAN.md investigation confirms brain has NO browser-triggerable OAuth endpoint; Gmail uses InstalledAppFlow (desktop/CLI). Honest labeling is the accepted gap closure per plan instructions. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `solo-leveling/src/api/onboarding.py` | HTTPException(502) on LLM failure + mode in digest response | VERIFIED | Lines 49-52: raises 502. Lines 121-123: returns mode flag. |
| `solo-leveling/tests/test_onboarding.py` | 17 tests including 502 and mode tests | VERIFIED | `test_parse_identity_llm_failure_returns_502` (line 115), `test_digest_mode_live_with_connected_data` (line 293), `test_digest_mode_preview_on_cold_start` (line 312). All 17 pass. |
| `dashboard/src/components/onboarding/IdentityBox.tsx` | Error guard + try/finally + error state | VERIFIED | Lines 27, 43-46, 60-66, 76-78. |
| `dashboard/src/components/onboarding/types.ts` | ProfileData with connected_apps | VERIFIED | Line 13: `connected_apps?: string[]`. |
| `dashboard/src/hooks/useOnboarding.ts` | console.error in else branch | VERIFIED | Lines 88-90. |
| `solo-leveling/src/core/onboarding.py` | _SOURCE_FETCHERS registry + mode derivation | VERIFIED | Lines 235-237: registry. Lines 240-271: `_query_connected_sources` uses registry. |
| `dashboard/src/components/onboarding/InstantWinDigest.tsx` | Honest preview/live labeling from backend mode | VERIFIED | Lines 31, 44, 75, 92-96, 111, 114. No unsafe casts. |
| `dashboard/src/lib/api.ts` | fetchDigest returns mode type | VERIFIED | Line 536: `mode: "live" | "preview"` in return type. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `IdentityBox.tsx` | `/api/v1/onboarding/parse-identity` | `parseIdentity()` with catch guard | VERIFIED | Line 40: await parseIdentity. Line 43: res.status guard. Line 60-62: catch sets error on 502 rejection. |
| `solo-leveling/src/api/onboarding.py` | `src.core.onboarding.parse_identity` | try/except raising HTTPException(502) | VERIFIED | Lines 44-52. |
| `InstantWinDigest.tsx` | `/api/v1/onboarding/digest` | `fetchDigest()` reading data.mode | VERIFIED | Line 41: await fetchDigest(). Line 44: setMode(data.mode). |
| `solo-leveling/src/api/onboarding.py` | `src.core.onboarding._query_connected_sources` | connected_data non-empty -> mode=live | VERIFIED | Lines 119-121. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `InstantWinDigest.tsx` | `mode` | `fetchDigest()` -> GET /onboarding/digest -> `mode = "live" if connected_data else "preview"` | N/A — mode is derived from actual fetch result | FLOWING — mode flag is honest (derived from real data presence, not profile intent) |
| `IdentityBox.tsx` | `error` | catch block on 502 rejection OR res.status guard | Yes — error message displayed to user | FLOWING |
| `useOnboarding.ts` | `profileToSave` | `finalProfile ?? profile` | Conditional — null when neither source has data | FLOWING — null case logged via console.error |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 17 backend contract tests pass | `solo-leveling/.venv/bin/python3.14 -m unittest tests.test_onboarding -v` | `Ran 17 tests in 0.017s OK` | PASS |
| TypeScript compiles with no errors | `cd dashboard && npx tsc --noEmit` | Exit 0, no output | PASS |
| parse-identity returns 502 on LLM exception | `grep -n HTTP_502_BAD_GATEWAY solo-leveling/src/api/onboarding.py` | Line 50: `status_code=status.HTTP_502_BAD_GATEWAY` | PASS |
| IdentityBox has finally block with setLoading(false) | `grep -n "finally" dashboard/src/components/onboarding/IdentityBox.tsx` | Line 63: `finally {` + Line 65: `setLoading(false)` | PASS |
| Digest endpoint returns mode flag | `grep -n "mode" solo-leveling/src/api/onboarding.py` | Line 121: `mode = "live" if connected_data else "preview"` + Line 123: `"mode": mode` | PASS |
| No unsafe type casts in InstantWinDigest | `grep "as unknown as" dashboard/src/components/onboarding/InstantWinDigest.tsx` | No matches | PASS |

### Probe Execution

No probes declared in Plans 03/04 and no conventional probes found for this phase. Step 7c: SKIPPED.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| ONB-02 | 05-01-PLAN.md | Identity Box captures free-text and AI Guide parses it into a working profile/context templates | SATISFIED | `parse_identity()` + `IdentityBox` + `ProfileConfirmation` wired end-to-end. 17 backend tests pass. CR-01/CR-02 fixes ensure error path is handled. |
| ONB-03 | 05-01, 05-02, 05-03, 05-04 PLAN.md | Guided integration highlights and connects only relevant apps via existing integrations | SATISFIED (partial) | App highlighting works (suggestedApps). Connect records intent. No real OAuth — honest labeling makes this transparent. Plan explicitly accepts honest-labeling as gap closure. |
| ONB-04 | 05-02, 05-03, 05-04 PLAN.md | First live 24-hour mini-digest as Instant Win, targeting < 2 minutes | SATISFIED (honest-labeling) | Digest endpoint returns mode="preview" on cold start (honest). Card labels truthfully. Real live digest requires OAuth subsystem (deferred). Timing under 2 min needs human verification. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | All 8 modified files are clean: no TBD, FIXME, XXX, TODO, HACK, or PLACEHOLDER markers found. |

### Human Verification Required

### 1. Instant Win Digest — honest labeling on cold start

**Test:** Complete the onboarding flow with no OAuth configured (cold start). Observe the digest card labels.
**Expected:** Card shows "Preview" / "What Signal will do for you" and intro text "Here's what I'll do for you — connect an app to see your live 24-hour digest." NOT "Your first digest" / "Last 24 hours".
**Why human:** Visual inspection of rendered card; requires running the dashboard.

### 2. LLM failure graceful degradation (CR-01 runtime)

**Test:** With GEMINI_API_KEY unset or invalid, submit text in IdentityBox Step 1. Observe wizard behavior.
**Expected:** Error message "I couldn't analyze that right now. Please try again." appears in red. Button resets to "Continue". Wizard stays on Step 1 — does NOT advance to Step 2.
**Why human:** Requires live backend with broken LLM config to verify the full error-handling chain at runtime.

### 3. Panel B (AI Guide) visibility during onboarding

**Test:** Walk through all onboarding steps (1, 2, 2b, 3). At each step, verify the AI Guide panel is visible in Panel B.
**Expected:** Panel B is always present and accessible alongside the onboarding wizard in Panel A.
**Why human:** Visual layout check; may be obscured on narrow viewports.

---

## Gaps Summary

**All previous gaps are closed.** The error-handling chain (CR-01/CR-02/CR-05/WR-02) is fully fixed with backend 502, frontend error guard + try/finally, console.error on dropped save, and proper typing. The Instant Win honest-labeling (SC-3/ONB-04) is addressed via the mode flag approach: the digest endpoint returns `mode="live"|"preview"` derived from actually-fetched data, and the frontend labels truthfully.

**One item is deferred, not a gap:** Real OAuth flow for live data is a new subsystem (OAuth client registration + redirect/callback + per-owner token storage) beyond gap closure scope. The honest-labeling approach transparently communicates to the owner that the digest is a preview until apps are connected.

**Three items require human verification** (visual inspection and runtime behavior that cannot be verified statically).

---

_Verified: 2026-05-31T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
