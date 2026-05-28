# 007 — Dependency Version Management Strategy

## Decision Title

- **Title:** Pin requirements.txt to tested versions with optional-install notes for inactive integrations
- **Date:** 2026-05-29
- **Status:** accepted
- **Scope:** solo-leveling Python dependencies, build reproducibility, integration activation workflow

## Context

The `requirements.txt` had drifted significantly from the actual virtual environment. Several packages were specified with very old minimum versions (`fastapi>=0.110.0` when `0.136.0` was installed, `uvicorn>=0.29.0` when `0.45.0` was installed). Two packages listed as dependencies (`python-telegram-bot`, `litellm`) were not installed at all because their integrations are not currently active. This creates three problems:

1. **Reproducibility risk:** A fresh install from `requirements.txt` would pull older, potentially incompatible versions.
2. **Wasted install time:** Dependencies for inactive integrations slow down fresh environment setup.
3. **Security exposure:** Old minimum versions may miss security patches.

## Decision

1. **Pin minimum versions to what is currently tested and running** in the `.venv`, not to what was originally added.
2. **Comment-out dependencies for inactive integrations** (`python-telegram-bot`, `litellm`) with clear activation instructions.
3. **Add a verification header** to `requirements.txt` with last-verified date and Python version.
4. **Adopt a quarterly dependency audit** as part of the review rhythm.

## Why

- **Known-good > latest:** The installed versions are proven to work with the test suite (59 tests pass). Bumping to absolute latest without testing risks breakage.
- **Lazy loading for integrations:** Telegram and Autopilot/litellm are not active paths. Installing them adds build time and attack surface for unused code.
- **Documentation as guardrails:** Comments in `requirements.txt` make the activation workflow explicit — future agents or humans know exactly when to uncomment.
- **Quarterly audit cadence:** Prevents drift from accumulating again. Ties into existing `review-rhythm.md` monthly/quarterly structure.

## Alternatives Considered

- **Alternative: Always use `==` exact pinning (e.g., `fastapi==0.136.0`)**
  - *Why not chosen:* Exact pinning is too rigid for a project in active development. We want security patches and compatible minor updates to flow in automatically.
- **Alternative: Use a separate `requirements-dev.txt` and `requirements-prod.txt`**
  - *Why not chosen:* Overkill for a single-service project. The brain has one deployment target (MacMini Docker). Splitting files adds complexity without benefit.
- **Alternative: Use Poetry or uv for dependency locking**
  - *Why not chosen:* The project already uses `pip` + `requirements.txt`. Migrating to Poetry/uv is a larger infrastructure change that should be its own decision record if needed.

## Consequences

- **Positive consequence:** Fresh installs now match the tested environment. Reduced risk of "works on my machine" issues.
- **Positive consequence:** Inactive integration dependencies are clearly marked, making the activation path obvious.
- **Positive consequence:** Quarterly audit creates a forcing function to stay current.
- **Negative consequence:** Security patches for pinned minimums won't auto-apply if they're below the new minimum. The quarterly audit mitigates this.
- **Follow-up required:**
  - [ ] When Telegram integration is activated, uncomment `python-telegram-bot` and verify `tests.test_integration_smoke` passes.
  - [ ] When Autopilot Phase 2 is activated, uncomment `litellm` and verify `tests.test_autopilot` passes.
  - [ ] Add dependency audit to `review-rhythm.md` quarterly checklist.

## Related Updates

- **Documents updated:**
  - `requirements.txt` — pinned to tested versions, added header, commented inactive deps.
  - `docs/decisions/007-dependency-version-management.md` — this file.
- **Changelog entry added:**
  - 2026-05-29 — `requirements.txt` synced to `.venv` versions; inactive integration deps commented with activation notes.
- **Next review date:** 2026-08-29 (quarterly dependency audit).
