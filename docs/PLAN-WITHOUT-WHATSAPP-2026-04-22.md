# Recommended Execution Plan (Skipping WhatsApp for now)

Status: WhatsApp integration paused intentionally.

Goal: Continue shipping meaningful progress with low dependency on external approvals and secrets.

## Phase A - Core Stability (1-2 days)

1. Keep CI green and strict
- Keep running: `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`
- Treat skipped live tests as expected when credentials are absent.

2. Expand Stage 9 local-library test depth
- Add cases for larger corpus search behavior.
- Add malformed input cases for deep-capture commands.
- Add deterministic tests for summary retrieval and bundle indexing edge cases.

3. Improve local reliability guards
- Add safer error messages for missing env vars and invalid command shapes.
- Ensure handlers fail gracefully with actionable output.

Exit criteria:
- Test suite remains green.
- New edge-case tests merged.

## Phase B - Deployment Readiness Without Webhook (2-3 days)

1. Container verification locally
- Build and run container repeatedly.
- Verify write persistence for `library/` and `data/` mounts.

2. Runtime hardening
- Add startup checks for required directories and optional secrets.
- Confirm scheduler behavior in container restarts.

3. Documentation hardening
- Add a single "runbook" section for local/container run modes and expected outcomes.

Exit criteria:
- Containerized app boots cleanly with no WhatsApp calls required.
- Local runbook is reproducible from clean checkout.

## Phase C - Integrations Behind Feature Gates (2-4 days)

1. Notion/Drive/Gmail dry-mode checks
- Keep mocked and skip-safe smoke tests as default.
- Add explicit env-driven toggles for live checks.

2. Add one command-health report
- Provide a lightweight status command that reports:
  - enabled integrations
  - missing credentials
  - suggested next setup step

3. Prepare handoff checklist
- What to fill in `.env`
- Which tests to run after each secret is added
- What success output should look like

Exit criteria:
- Any collaborator can see readiness state without digging through code.

## Phase D - Parallel Legal/Meta Track (background)

This runs in parallel while engineering continues.

1. Prepare legal verification packet
- legal entity docs
- exact name/address matching across docs and Business Manager
- representative details

2. Submit and monitor verification
- resolve any mismatch feedback quickly
- track status daily

Exit criteria:
- business verification approved or clear blockers documented.

## Priority order

1. Phase A (quality)
2. Phase B (runtime confidence)
3. Phase C (integration readiness)
4. Re-open WhatsApp implementation only when Phase A-C are stable or legal track is approved

## First command set to execute today

1. `source .venv/bin/activate`
2. `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`
3. `docker build -t solo-leveling .`
4. `docker run --rm -p 8000:8000 --env-file .env -v "$(pwd)/library:/app/library" -v "$(pwd)/data:/app/data" solo-leveling`

If command 4 is not yet desired, complete all Phase A tasks first.
