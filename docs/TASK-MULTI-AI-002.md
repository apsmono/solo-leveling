# Task: Integration Smoke Suite - Next Multi-AI Task

**Task ID:** MULTI-AI-002
**Created:** 2026-04-21T13:04
**Status:** DONE
**Completed:** 2026-04-21 19:30
**Priority:** High
**Estimate:** 2 to 4 hours wall-clock time

---

## Task Definition

### Goal

Add credential-aware smoke coverage for the repo's highest-value integration paths so the project can validate core behavior without forcing every local run to have live secrets configured.

### Why This Task

1. It is the highest-leverage follow-up after MULTI-AI-001.
2. The repo already has strong Stage 9 local tests, but broader integration confidence is still missing.
3. Secrets are not always present on every device, so tests must degrade safely.
4. Deployment readiness depends on predictable verification steps for each service.

### Acceptance Criteria

- [x] Add at least one smoke path for each core area: Notion, Google Drive, Gmail, WhatsApp-facing router flow, and AI agent dispatch guardrails.
- [x] Smoke suite skips cleanly with clear messages when required credentials are missing.
- [x] Existing Stage 9 tests continue to pass unchanged.
- [x] Running the smoke suite is documented with exact commands and expectations.
- [x] `CHANGELOG.md` and `docs/ai-working-notes.md` are updated with the result.
- [x] Monitor AI validates the final suite before merge.

---

## Constraints

1. Do not commit secrets, tokens, or credential files.
2. Prefer small smoke checks over fragile end-to-end workflows.
3. Tests must be useful both with and without live credentials.
4. Keep public APIs and WhatsApp command behavior unchanged.

## Proposed Scope

### In Scope

1. Add smoke-test helpers for env detection and skip messaging.
2. Add one smoke check per major integration path where possible.
3. Validate router-level command dispatch for representative flows.
4. Document how to run smoke tests locally and what each result means.

### Out of Scope

1. Full Meta webhook end-to-end verification over public HTTPS.
2. Full production deployment automation.
3. Long-running or flaky external test orchestration.

## Smoke Test Runbook

Run from repository root after dependencies are installed.

### 1) Router and Guardrail Smoke (no credentials needed)

```bash
/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_integration_smoke.RouterSmokeTests -v
```

Expected result:

1. All router and helper tests pass.
2. No network calls are required because integrations are mocked.

### 2) Live Optional Smoke (credential-aware)

```bash
/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_integration_smoke.LiveIntegrationSmokeTests -v
```

Expected result:

1. Tests run only for integrations with available credentials.
2. Missing credentials produce explicit `skipped` messages.
3. Gmail OAuth browser flow is disabled by default unless `ALLOW_INTERACTIVE_OAUTH_SMOKE=true` is set.

### 3) Full Local Validation (Stage 9 + smoke)

```bash
/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v
```

Expected result:

1. Stage 9 regression suite remains green.
2. Smoke suite passes or skips clearly according to credential availability.

---

## Execution Flow

### Phase 1: Research (Research AI)

1. Audit current integration entry points in `src/integrations/` and `src/core/router.py`.
2. Map required env vars and identify what can be tested safely without secrets.
3. Recommend a smoke-test matrix and skip strategy.
4. Document findings in `docs/TASK-MULTI-AI-002-research.md`.

### Phase 2: Design (Monitor AI)

1. Define the smoke suite structure under `tests/`.
2. Decide how skipped tests should explain missing credentials.
3. Choose the minimum useful set of service checks.
4. Approve the exact implementation boundary.

### Phase 3: Implementation (Executor AI)

1. Add smoke tests and any lightweight helpers.
2. Preserve compatibility with current `unittest`-based test style unless a stronger reason exists.
3. Keep failures actionable and short.
4. Update docs with run commands.

### Phase 4: Validation (Quality AI)

1. Run existing Stage 9 regression suite.
2. Run the smoke suite in no-credential mode and confirm graceful skips.
3. Run available live checks if credentials exist.
4. Record what was actually validated.

### Phase 5: Monitor Approval (Monitor AI)

1. Review code, docs, and skip behavior.
2. Confirm changelog and working-notes updates.
3. Approve merge when the suite is stable and understandable.

---

## Suggested Branches

- Research: `agent/research/multi-ai-002-integration-smoke/research`
- Design: `agent/monitor/multi-ai-002-integration-smoke/design`
- Implementation: `agent/executor/multi-ai-002-integration-smoke/implementation`
- Validation: `agent/quality/multi-ai-002-integration-smoke/validation`

---

## Success Definition

This task is successful when a new AI or human can run one command, immediately understand which integrations are testable on the current machine, and get meaningful smoke validation without tripping over missing secrets.

## Validation Summary

- Command run:
  - `/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`
- Result:
  - `Ran 23 tests in 0.151s`
  - `OK (skipped=3)`
- Skip reasons:
  - Live Notion/Drive/Gmail tests skipped on missing credentials as designed.
- Notes:
  - Hardened Gmail live-smoke logic avoids unexpected interactive OAuth flow in headless environments unless explicitly enabled via `ALLOW_INTERACTIVE_OAUTH_SMOKE=true`.
