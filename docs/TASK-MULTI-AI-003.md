# TASK-MULTI-AI-003 — GitHub Actions CI Pipeline

**Status:** IN_PROGRESS
**Assigned to:** Monitor AI (executor)
**Branch:** `agent/monitor-ai/ci-pipeline/setup`
**Created:** 2026-04-21 21-52-07

---

## Goal

Set up a GitHub Actions CI pipeline that automatically runs all unit and smoke tests on every push and pull request to `main`. This establishes a safety net that catches regressions before they land, without requiring live credentials.

---

## Acceptance Criteria

- [ ] `.github/workflows/ci.yml` exists and is valid YAML.
- [ ] Pipeline triggers on `push` and `pull_request` to `main`.
- [ ] Pipeline installs Python dependencies via `requirements.txt`.
- [ ] All 23 existing tests run; credential-gated tests are skipped (not failed).
- [ ] Pipeline passes green on a clean checkout with no `.env` present.
- [ ] Workflow file does not embed any secrets or credentials.

---

## Scope

Credential-free work only — no live service calls, no secret injection. The pipeline runs the same command validated locally:

```
python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v
```

Expected result: `Ran 23 tests … OK (skipped=3)`.

---

## Execution Plan

1. Create `.github/workflows/` directory.
2. Write `ci.yml` with:
   - Trigger: `push` and `pull_request` targeting `main`.
   - Runner: `ubuntu-latest`.
   - Steps: checkout → setup Python 3.11 → install deps → run tests.
3. Add `.venv` to `.gitignore` if not already present.
4. Validate the YAML is well-formed.
5. Update `CHANGELOG.md` and docs.
6. Commit and push.

---

## Handoff Notes

- Tests use `unittest` (no pytest dependency needed in CI).
- Live smoke tests self-skip via `unittest.skip` when env vars are absent — no special CI flags needed.
- Virtual env not needed in CI; direct `pip install -r requirements.txt` is sufficient.
