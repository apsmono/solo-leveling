# Task: Integration Smoke Suite - Next Multi-AI Task

**Task ID:** MULTI-AI-002
**Created:** 2026-04-21T13:04
**Status:** READY_FOR_ASSIGNMENT
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

- [ ] Add at least one smoke path for each core area: Notion, Google Drive, Gmail, WhatsApp-facing router flow, and AI agent dispatch guardrails.
- [ ] Smoke suite skips cleanly with clear messages when required credentials are missing.
- [ ] Existing Stage 9 tests continue to pass unchanged.
- [ ] Running the smoke suite is documented with exact commands and expectations.
- [ ] `CHANGELOG.md` and `docs/ai-working-notes.md` are updated with the result.
- [ ] Monitor AI validates the final suite before merge.

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
