---
phase: 05
slug: onboarding-instant-win
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-31
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (backend) + none detected (frontend) |
| **Config file** | none — tests run via `python -m unittest` |
| **Quick run command** | `cd solo-leveling && python -m unittest tests.test_onboarding -v` |
| **Full suite command** | `cd solo-leveling && python -m unittest discover tests -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd solo-leveling && python -m unittest tests.test_onboarding -v`
- **After every plan wave:** Run `cd solo-leveling && python -m unittest discover tests -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | ONB-02 | T-05-01 | Profile JSON validated on save | unit | `python -m unittest tests.test_onboarding -v` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | ONB-02 | T-05-02 | LLM output parsed to structured JSON | unit | `python -m unittest tests.test_onboarding -v` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 1 | ONB-03 | T-05-03 | OAuth tokens not exposed in profile | unit | `python -m unittest tests.test_onboarding -v` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 2 | ONB-03 | — | App connect triggers OAuth flow | integration | `python -m unittest tests.test_onboarding -v` | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 2 | ONB-04 | — | Digest returns 3 bullets | unit | `python -m unittest tests.test_onboarding -v` | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 2 | ONB-04 | — | Cold-start fallback returns capability preview | unit | `python -m unittest tests.test_onboarding -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `solo-leveling/tests/test_onboarding.py` — stubs for ONB-02, ONB-03, ONB-04
- [ ] `solo-leveling/src/core/profile_store.py` — profile persistence module
- [ ] `solo-leveling/src/api/onboarding.py` — onboarding endpoints
- [ ] `solo-leveling/src/api/profile.py` — profile CRUD endpoints
- [ ] `dashboard/src/components/onboarding/` — all wizard components
- [ ] `dashboard/src/hooks/useOnboarding.ts` — onboarding state hook
- [ ] Frontend API functions in `dashboard/src/lib/api.ts` for onboarding endpoints

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| First-run owner reaches Instant Win in under 2 min | ONB-04 | Timing is user-perceived, not programmatic | Manual stopclock test: fresh account → onboarding → digest displayed |
| OAuth popup completes without blocking wizard | ONB-03 | Browser popup behavior varies | Manual test: click Connect → authorize → return to wizard |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
