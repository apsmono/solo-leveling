---
phase: 05-onboarding-instant-win
reviewed: 2026-05-31T00:00:00Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - dashboard/src/components/dashboard/DashboardPage.tsx
  - dashboard/src/components/onboarding/AppConnectStep.tsx
  - dashboard/src/components/onboarding/IdentityBox.tsx
  - dashboard/src/components/onboarding/InstantWinDigest.tsx
  - dashboard/src/components/onboarding/OnboardingWizard.tsx
  - dashboard/src/components/onboarding/ProfileConfirmation.tsx
  - dashboard/src/components/onboarding/StepIndicator.tsx
  - dashboard/src/components/onboarding/types.ts
  - dashboard/src/hooks/useOnboarding.ts
  - dashboard/src/lib/api.ts
  - solo-leveling/src/api/onboarding.py
  - solo-leveling/src/api/profile.py
  - solo-leveling/src/api/v1_router.py
  - solo-leveling/src/core/onboarding.py
  - solo-leveling/src/core/profile_store.py
  - solo-leveling/tests/test_onboarding.py
findings:
  critical: 5
  warning: 7
  info: 4
  total: 16
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-05-31T00:00:00Z
**Depth:** standard
**Files Reviewed:** 16
**Status:** issues_found

## Summary

This phase implements the Signal onboarding wizard (3-step: IdentityBox → ProfileConfirmation + AppConnectStep → InstantWinDigest) plus the backend endpoints that support it. The overall structure is sound, but there are five blockers: the `parse-identity` endpoint silently swallows LLM failures and returns HTTP 200 with a stub profile instead of an error, creating an invisible bad state; the `handleSubmit` function in `IdentityBox` never resets the loading spinner on success; the `POST /profile` endpoint accepts and persists arbitrary user-supplied JSON without any field sanitization; `save_profile` uses a relative path that will resolve differently depending on the process CWD (inside Docker vs. locally vs. test runner); and `useOnboarding.handleComplete` silently skips saving when `profile` is null at completion time, permanently losing the user's parsed identity.

---

## Critical Issues

### CR-01: `parse-identity` returns HTTP 200 + error status on LLM failure — client treats it as a successful parse

**File:** `solo-leveling/src/api/onboarding.py:47-52`
**Issue:** When `parse_identity()` raises an exception the handler catches it and returns `{"status": "error", "message": "..."}` with HTTP **200**. The frontend `IdentityBox` checks nothing — it blindly reads `res.profile` from the 200 response. `res.profile` will be `undefined` for the error shape. `IdentityBox` then calls `onProfileParsed(undefined as ProfileData)` and `onNext()`, advancing the wizard to step 2 with a `null`/`undefined` profile. `OnboardingWizard` renders the `effectiveStep === 2 && !profile` fallback (IdentityBox again) but the step indicator has already moved to step 2, creating a confusing loop. The correct fix is to raise an `HTTPException` on failure.

**Fix:**
```python
# solo-leveling/src/api/onboarding.py
@router.post("/onboarding/parse-identity")
async def parse_identity_endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request payload.")

    try:
        parsed = parse_identity(text)
        return {"status": "ok", "profile": parsed}
    except Exception:
        logger.exception("Failed to parse identity")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to parse identity. Please try again.",
        )
```

---

### CR-02: `IdentityBox.handleSubmit` never resets `loading` on the success path — button stays permanently disabled

**File:** `dashboard/src/components/onboarding/IdentityBox.tsx:33-56`
**Issue:** On the happy path (no `needs_followup`, no exception) the code calls `onProfileParsed(parsed)` then `onNext()` at lines 50-51 and returns without ever calling `setLoading(false)`. The loading spinner persists for the life of the component. If `onNext` does not unmount the component immediately (e.g. when `OnboardingWizard` renders a sibling using the same mounted instance due to the step fallback), the button is stuck in the "Analyzing..." disabled state. The `catch` block at line 53 also omits `setLoading(false)` — the comment says "user can retry" but the button is disabled, making retry impossible.

**Fix:**
```typescript
// dashboard/src/components/onboarding/IdentityBox.tsx
  async function handleSubmit() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await parseIdentity(text.trim());
      const parsed = res.profile as ProfileData;
      if (parsed.needs_followup && !hasFollowup) {
        setFollowupQuestion(parsed.followup_question || "Could you tell me a bit more about what you do?");
        setHasFollowup(true);
        return;           // finally block will clear loading
      }
      onProfileParsed(parsed);
      onNext();
    } catch {
      // fall through to finally
    } finally {
      setLoading(false);  // always reset
    }
  }
```

---

### CR-03: `POST /profile` persists arbitrary user-supplied JSON without field validation — profile store can be poisoned

**File:** `solo-leveling/src/api/profile.py:34-46`
**Issue:** `create_profile` accepts any JSON dict and writes it verbatim to `data/profile.json`. There is no schema validation: a client can store `{"onboarding_step": 999, "connected_apps": ["../../etc/passwd"], "role": "<script>..."}` or any other content. While `connected_apps` is validated in `connect_app_endpoint`, the profile POST endpoint bypasses that guard entirely, letting an authenticated caller write arbitrary `connected_apps` values. `_query_connected_sources` in `onboarding.py` iterates `profile["connected_apps"]` and passes values to integration clients without a secondary allowlist check. This is an injection/data-integrity risk for the single-owner deployment.

**Fix:**
```python
# solo-leveling/src/api/profile.py
_ALLOWED_APPS = frozenset({"gmail", "youtube", "notion", "gdrive", "github", "telegram", "discord"})

PROFILE_SCHEMA_KEYS = {"role", "pain_points", "suggested_apps", "context_templates",
                       "needs_followup", "followup_question", "onboarding_step", "connected_apps"}

@router.post("/profile")
async def create_profile(
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=400, detail="Missing profile data.")

    # Whitelist keys and validate connected_apps
    sanitized: dict[str, Any] = {k: v for k, v in payload.items() if k in PROFILE_SCHEMA_KEYS}
    if "connected_apps" in sanitized:
        sanitized["connected_apps"] = [
            a for a in sanitized["connected_apps"] if a in _ALLOWED_APPS
        ]

    save_profile(sanitized)
    return {"status": "ok", "profile": sanitized}
```

---

### CR-04: `_PROFILE_PATH` is a relative path — resolves from process CWD, not from the project root

**File:** `solo-leveling/src/core/profile_store.py:17`
**Issue:** `_PROFILE_PATH = Path("data/profile.json")` is a relative path. In production this is fine because uvicorn runs from the project root. However, the test suite instantiates `TestClient(app)` from arbitrary working directories (e.g. the repo root via `python -m unittest`) and any test that hits the real `save_profile` or `load_profile` without mocking will create/read `data/profile.json` relative to wherever the test runner was invoked. If the tests run from the parent (`projects/`) directory, the profile lands in the wrong location. More critically, if `_PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)` runs in a CI container with a read-only filesystem it raises `OSError` that is not caught, crashing the process. The other data files in the brain (e.g. `reminders.py`) use the same pattern — but this is the only new addition in this phase.

**Fix:**
```python
# solo-leveling/src/core/profile_store.py
from pathlib import Path

# Resolve relative to this source file so it always points to
# <repo_root>/data/profile.json regardless of CWD.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]  # src/core -> src -> project root
_PROFILE_PATH = _PROJECT_ROOT / "data" / "profile.json"
```

---

### CR-05: `useOnboarding.handleComplete` silently skips the profile save when `profile` is null — onboarding completes without persisting data

**File:** `dashboard/src/hooks/useOnboarding.ts:77-90`
**Issue:** `handleComplete` is called from `InstantWinDigest` with no arguments (`onComplete()` at line 133 of `InstantWinDigest.tsx`). Inside the hook, `finalProfile ?? profile` is evaluated. If `profile` is `null` (possible when `handleProfileParsed` was never called — e.g. due to the CR-01 failure mode, or a race where the component unmounts mid-save), the `if (profileToSave)` guard at line 80 is false, so the profile is never saved to the backend. The hook then immediately calls `setOnboardingState("complete")`. On the next page load, `GET /profile` returns 404 (nothing was saved), the hook detects first-run, and the user is sent through onboarding again. This creates a silent re-onboarding loop.

**Fix:**
```typescript
// dashboard/src/hooks/useOnboarding.ts
const handleComplete = useCallback(
  async (finalProfile?: ProfileData) => {
    const profileToSave = finalProfile ?? profile;
    if (!profileToSave) {
      // Profile missing at completion — log and still mark complete to avoid loop,
      // but surface the issue clearly for debugging.
      console.error("[useOnboarding] handleComplete called with no profile — skipping save");
      setOnboardingState("complete");
      return;
    }
    try {
      await saveProfile({ ...profileToSave, onboarding_step: 3 });
    } catch {
      // Non-blocking — local state already updated
    }
    setOnboardingState("complete");
  },
  [profile]
);
```

Note: the `console.error` here is intentional for debugging a data-loss scenario. But the broader fix is ensuring CR-01 and CR-02 are resolved so that `profile` is never null at this call site.

---

## Warnings

### WR-01: `OnboardingWizard` local `subStep` state can permanently diverge from external `step` prop

**File:** `dashboard/src/components/onboarding/OnboardingWizard.tsx:44-49`
**Issue:** `subStep` is initialized from `step` in `useState(step)` and is only synced back when `step` changes to `1` or `3` (via the `effectiveStep` computation at line 48). If `step` changes from `2` → `2` (e.g. `handleStepChange(2)` is called twice), `subStep` is not reset. This means if a user navigates Edit → back to step 1 → re-submits → arrives at step 2, `subStep` may still hold `"2b"` from the previous pass, causing the wizard to skip `ProfileConfirmation` and jump directly to `AppConnectStep` with the freshly-parsed but unconfirmed profile.

**Fix:**
```typescript
// When step resets to 1 from outside, also reset subStep to 2 (not "2b")
// by making effectiveStep depend on the step change properly, or add a useEffect:
useEffect(() => {
  if (step === 1) setSubStep(1);
}, [step]);
```

---

### WR-02: `isColdStart` in `InstantWinDigest` casts through `unknown` to access `connected_apps` — type and `ProfileData` are out of sync

**File:** `dashboard/src/components/onboarding/InstantWinDigest.tsx:26-29`
**Issue:** `(profile as unknown as { connected_apps?: string[] }).connected_apps` is used because `ProfileData` in `types.ts` doesn't declare `connected_apps`. The field is present in the backend response (written by `connect_app_endpoint`) and in the `ParsedProfile` interface in `api.ts` (line 507 — also missing `connected_apps`). This cast is a symptom of an interface gap; if the backend adds or renames the field the TypeScript compiler will not catch it. The `ProfileData` type should be updated to include `connected_apps?: string[]`.

**Fix:**
```typescript
// dashboard/src/components/onboarding/types.ts
export interface ProfileData {
  role: string;
  pain_points: string[];
  suggested_apps: string[];
  context_templates: string[];
  needs_followup: boolean;
  followup_question: string;
  onboarding_step?: number;
  connected_apps?: string[];  // Add this field
}
```
Remove the cast in `InstantWinDigest.tsx:28`.

---

### WR-03: `AppConnectStep` — `canContinue` allows proceeding after skip but the `Continue` button only appears post-skip; user who skips immediately sees `Continue` without ever connecting anything

**File:** `dashboard/src/components/onboarding/AppConnectStep.tsx:59, 85-87, 163-172`
**Issue:** `canContinue = connectedApps.size > 0 || skipped`. When `handleSkip` sets `skipped = true`, the "Skip for now" text disappears and a "Continue" button appears in its place. This logic is correct but reveals a missing state: if `suggestedApps` is empty (the `!profile` fallback at `OnboardingWizard:135`), no app cards are rendered and `canContinue` starts as `false`. The user sees no apps, no "Skip for now" button is initially visible, and no "Continue" button — the wizard appears frozen. The "Skip for now" button should always be visible when apps haven't been connected, regardless of the `skipped` state, or `canContinue` should default to `true` when `apps.length === 0`.

**Fix:**
```typescript
// AppConnectStep.tsx — always allow continue when no apps are available
const canContinue = connectedApps.size > 0 || skipped || apps.length === 0;
```

---

### WR-04: `useOnboarding` resumes at `Math.max(step, 1)` — a profile with `onboarding_step: 0` restarts at step 1 even though step 0 is invalid per the backend validator

**File:** `dashboard/src/hooks/useOnboarding.ts:28-33`
**Issue:** The backend `onboarding_step_endpoint` validates `step >= 1`, so `onboarding_step: 0` should never be written by the normal flow. However, `save_profile` at `profile.py:45` writes the raw payload without validation, meaning a manual POST with `{"onboarding_step": 0}` is accepted. On next load, `step < 3` is true, `Math.max(0, 1)` returns `1`, and onboarding restarts — this is reasonable behavior. The more interesting edge case is `onboarding_step: 2`: the hook sets `setOnboardingStep(2)` but `OnboardingWizard` initializes `subStep` to `step=2`, so the user resumes at `ProfileConfirmation` (step 2), not `AppConnectStep` (step 2b). This is the intended D-10 behavior but is not tested. Not a crash, but should be validated in the test suite.

**Fix:** Add a test case to `test_onboarding.py` for the `onboarding_step: 2` resume path to document the expected behavior.

---

### WR-05: `_query_connected_sources` only handles `gmail` — other apps in `connected_apps` are silently ignored, making `generate_digest` misleadingly return a real digest

**File:** `solo-leveling/src/core/onboarding.py:240-250`
**Issue:** The loop iterates all `connected_apps` but only has a handler for `"gmail"`. Apps like `youtube`, `notion`, `github`, etc. produce no data. If the user connected `github` but not `gmail`, `connected_data` will be empty, causing `generate_digest` to take the cold-start path and return capability-preview bullets — despite the user having connected an app. This is misleading UX: the user connected an app, the app is confirmed as connected, but the digest acts as if nothing was connected.

**Fix:** The `for app in connected_apps` loop should collect data from all supported integrations (even as stub `{"app": app, "items": []}` entries) so `connected_data` is non-empty whenever at least one app is connected. The cold-start path (`not connected_data`) should be replaced with a check against `connected_apps` directly:

```python
# onboarding.py digest_endpoint
connected_data = _query_connected_sources(profile)
is_cold_start = not profile.get("connected_apps")  # check intent, not fetched data
bullets = generate_digest(profile, connected_data, cold_start=is_cold_start)
```

---

### WR-06: `handleDraftReply` in `DashboardPage.tsx` swallows the error entirely — if `sendGuideCommand` throws, `guideLoading` stays `true` permanently

**File:** `dashboard/src/components/dashboard/DashboardPage.tsx:153-166`
**Issue:** The `try/finally` block in `handleDraftReply` correctly calls `setGuideLoading(false)` in `finally`. However, if `sendGuideCommand` throws, `setGuideMessages` is never called, and the error is completely silent — no toast, no message added to the guide, no user feedback. This is pre-existing code but is a quality issue that ships in this phase's `DashboardPage.tsx`.

**Fix:**
```typescript
} catch (err) {
  setGuideMessages((prev) => [
    ...prev,
    { role: "user", content: "Draft a friendly reply" },
    { role: "assistant", content: "Could not reach the guide. Please try again." },
  ]);
}
```

---

### WR-07: `digest_endpoint` calls `_query_connected_sources` synchronously in an async FastAPI handler — blocks the event loop

**File:** `solo-leveling/src/api/onboarding.py:118`
**Issue:** `_query_connected_sources` calls `list_messages()` from the Gmail client synchronously inside an `async def` endpoint without `await` or `run_in_executor`. This blocks the entire FastAPI/uvicorn async event loop while the Gmail HTTP call is in flight. For a single-owner deployment the practical impact is minimal, but it is architecturally incorrect and will cause visible latency on the digest endpoint.

**Fix:**
```python
import asyncio
# In digest_endpoint:
connected_data = await asyncio.get_event_loop().run_in_executor(
    None, _query_connected_sources, profile
)
```

---

## Info

### IN-01: `api.ts` — `ParsedProfile` and `ProfileData` (types.ts) are parallel interfaces that are not shared

**File:** `dashboard/src/lib/api.ts:506-514`
**Issue:** `ParsedProfile` in `api.ts` duplicates every field of `ProfileData` in `types.ts`. They differ only in that `ParsedProfile` is not imported by the wizard components (which use `ProfileData`). This creates a silent type divergence: if a field is added to one but not the other the compiler will not catch misuse at the API boundary. `api.ts` functions return `ParsedProfile` but callers cast to `ProfileData` (e.g. `IdentityBox.tsx:39`).

**Fix:** Import and re-export `ProfileData` from `types.ts` in `api.ts`, or extend one from the other to keep a single source of truth. Remove the `ParsedProfile` duplicate.

---

### IN-02: `StepIndicator` uses array index as React `key` for step dots

**File:** `dashboard/src/components/onboarding/StepIndicator.tsx:24`
**Issue:** `key={step}` where `step = i + 1` is equivalent to using the index. Since the `total` prop never changes during the wizard's lifetime this is safe, but it is a code smell. Use a descriptive key like `key={`step-${step}`}`.

---

### IN-03: Commented-style transition block in `OnboardingWizard` does nothing — opacity/transform are hardcoded to final values

**File:** `dashboard/src/components/onboarding/OnboardingWizard.tsx:81-86`
**Issue:** The inline `style` on the step container has `opacity: 1` and `transform: "translateY(0)"` hardcoded. The comment block implies an animation was intended (see `InstantWinDigest` which implements the pattern correctly with a `visible` state). This dead code adds confusion without adding value.

**Fix:** Either implement the step-transition animation (using a `visible` state toggled on step change) or remove the `style` block and keep only the Tailwind `transition-all` class.

---

### IN-04: `test_onboarding.py` — `test_all_endpoints_require_auth` does not include `connect-app` and `digest` endpoints

**File:** `solo-leveling/tests/test_onboarding.py:156-175`
**Issue:** The auth-gate test in `OnboardingAPITests` was written before `AppConnectDigestAPITests` was added. The new `POST /onboarding/connect-app` and `GET /onboarding/digest` endpoints are only indirectly tested for auth in `test_digest_requires_auth`. The `connect-app` endpoint has no dedicated no-auth test. The `test_all_endpoints_require_auth` helper should be extended or a new test added to `AppConnectDigestAPITests`.

**Fix:** Add `/api/v1/onboarding/connect-app` (POST) and `/api/v1/onboarding/digest` (GET) to the auth check loop, or add a dedicated `test_connect_app_requires_auth` method.

---

_Reviewed: 2026-05-31T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
