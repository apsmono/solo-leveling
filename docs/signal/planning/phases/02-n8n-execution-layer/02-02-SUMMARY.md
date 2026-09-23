---
phase: 02-n8n-execution-layer
plan: 02
subsystem: api
tags: [n8n, executor, credentials, templates, rl-governor, dispatcher, router]

requires:
  - phase: 02-n8n-execution-layer (plan 01)
    provides: n8n REST client + error abstraction
  - phase: 01-data-auth-foundation
    provides: integration token sources, Firebase sign-in path, RL governor
provides:
  - intent executor (match → LLM param fill → RL gate → credential sync → trigger → retry)
  - owner-token → n8n credential injection (upsert by name)
  - versioned workflow template skeletons + keyword matcher
  - connect-time credential sync on sign-in
  - command-router n8n_workflow intent reaching execute_intent
affects: [02-03, onboarding, smart-feeds, smart-drafts, safety-recovery]

tech-stack:
  added: []
  patterns: ["hybrid template+LLM (keyword match + dispatcher param fill)", "RL gate instantiated at the owner's real RL from config", "credential upsert by deterministic name signal-{owner}-{integration}"]

key-files:
  created:
    - solo-leveling/src/n8n/templates.py
    - solo-leveling/src/n8n/credentials.py
    - solo-leveling/src/n8n/executor.py
    - solo-leveling/src/n8n/templates/gmail_read_summary.json
    - solo-leveling/src/n8n/templates/gmail_send_draft.json
  modified:
    - solo-leveling/src/autopilot/governor.py
    - solo-leveling/src/api/auth_session.py
    - solo-leveling/src/core/router.py

key-decisions:
  - "RL gate uses Governor(ResponsibilityLevel(AUTOPILOT_RL_LEVEL)) — the owner's real RL — so side-effecting workflows gate by default (default RL1), never auto-approved by a hardcoded RL4"
  - "Approval gate runs BEFORE credential sync/trigger; read-only workflows skip the gate"
  - "LLM parameter fill via dispatcher.run_agent with graceful fallback to schema defaults; explicit caller params always win"
  - "Connect-time credential sync is best-effort and never blocks sign-in"
  - "Router exposes an explicit-prefix n8n_workflow intent to avoid shadowing gmail/ask_ai keywords"

patterns-established:
  - "executor orchestration: match_template → _fill_with_llm → gate → sync_credential → trigger_workflow → _poll_execution → _retry_and_report"
  - "templates are version-controlled JSON skeletons in src/n8n/templates/ with an `integration` + `side_effecting` contract"

requirements-completed: [N8N-01, N8N-02]

duration: ~25min
completed: 2026-05-30
---

# Phase 2 / Plan 02: Intent Executor + Credential Injection Summary

**Intent executor that matches a vetted skeleton, fills its parameters with the LLM dispatcher, gates side-effecting runs at the owner's real RL, injects owner credentials into n8n, and is reachable from both the command router and the sign-in path.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3 (all TDD)
- **Files modified:** 8 (5 created, 3 modified)

## Accomplishments
- `executor.py` — `execute_intent` (D-01/D-02/D-07/D-09/D-10/D-11), `_fill_with_llm`, `_poll_execution`, `_retry_and_report`, `_load_integration_token`, `_log_unmet_intent`.
- `credentials.py` — `sync_credential` (upsert), `_map_token_to_n8n_credential` for gmail/gdrive/github/notion/telegram/discord.
- `templates.py` + 2 skeleton JSONs — `load_all_templates`, keyword `match_template`, `fill_parameters`.
- `governor.py` — `n8n_workflow` tool at RL4.
- `auth_session.py` — `_sync_connected_credentials` on sign-in (D-05, non-blocking).
- `router.py` — `n8n_workflow` intent + `_handle_n8n_workflow` + result formatter.

## Files Created/Modified
- `src/n8n/executor.py` - intent → n8n orchestrator
- `src/n8n/credentials.py` - brain token → n8n credential injection
- `src/n8n/templates.py` + `templates/*.json` - skeleton catalog + matcher
- `src/autopilot/governor.py` - n8n_workflow RL4 entry
- `src/api/auth_session.py` - connect-time credential sync
- `src/core/router.py` - n8n automation intent wiring

## Decisions Made
- Fixed the plan-review blocker: the RL gate is instantiated with the owner's real RL, not a hardcoded `LEAD_EXECUTOR`. Verified by a test that gets `needs_approval` at RL1 without mocking the governor.
- `execute_intent` calls `sync_credential` before `trigger_workflow` (call-order asserted in tests) so N8N-02 holds at runtime.

## Deviations from Plan
None - plan executed as written (the plan already incorporated the plan-checker revisions).

## Issues Encountered
- Offline LLM intent parser returns 403 (no API key); `route_command` correctly falls back to keyword detection, so the n8n route still resolves. Expected offline behavior.

## Next Phase Readiness
- Executor + credential + template + wiring ready; callback ingestion and full test completion happen in plan 02-03.

---
*Phase: 02-n8n-execution-layer*
*Completed: 2026-05-30*
