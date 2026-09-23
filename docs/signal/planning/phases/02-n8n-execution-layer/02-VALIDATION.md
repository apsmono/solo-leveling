---
phase: 2
slug: n8n-execution-layer
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-30
updated: 2026-05-30
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Regenerated to match the actual 3-plan / 8-task structure (02-01, 02-02, 02-03).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` |
| **Config file** | none (direct `python -m unittest` invocation) |
| **Quick run command** | `python -m unittest tests.test_n8n_execution -v` |
| **Full suite command** | `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation tests.test_n8n_execution -v` |
| **Estimated runtime** | ~15 seconds |

The single test file `tests/test_n8n_execution.py` is created in **plan 02-01 (wave 1, Task 2)** with `N8NClientTests` and `ErrorTests` green and the remaining four classes stubbed (`skipTest`). The stubs are completed to green in **plan 02-03 (wave 3, Task 2)**. This file is the Wave 0 test artifact for the phase.

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests.test_n8n_execution -v`
- **After every plan wave:** Run `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke tests.test_vector_foundation tests.test_n8n_execution -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|--------|
| 02-01-01 | 01 | 1 | N8N-01, INFRA-05 | T-02-01, T-02-02 | n8n config read from env only; error messages carry no stack traces | unit | `python -c "from src.n8n.errors import ErrorClass, classify_error, soft_error_message; assert classify_error({'error':'token expired'})==ErrorClass.CREDENTIAL_EXPIRED; assert 'reconnect' in soft_error_message(ErrorClass.CREDENTIAL_EXPIRED, integration='gmail').lower()"` | ⬜ pending |
| 02-01-02 | 01 | 1 | N8N-01 | T-02-01 | trigger_workflow sends correct payload; missing API key raises | unit | `python -m unittest tests.test_n8n_execution.N8NClientTests tests.test_n8n_execution.ErrorTests -v` | ⬜ pending |
| 02-02-01 | 02 | 2 | N8N-01, N8N-02 | T-02-03, T-02-05 | template skeletons version-controlled; credential schema mapped; governor RL entry added | unit | `python -c "from src.n8n.templates import load_all_templates, match_template; assert len(load_all_templates())==2; assert match_template('summarize my gmail')['id']=='gmail_read_summary'; assert match_template('xyzzy')is None" && python -c "from src.autopilot.governor import _TOOL_RL_REQUIREMENTS; assert 'n8n_workflow' in _TOOL_RL_REQUIREMENTS"` | ⬜ pending |
| 02-02-02 | 02 | 2 | N8N-01, N8N-02 | T-02-03, T-02-04 | side-effecting gated at owner's REAL RL (not hardcoded RL4); credential synced before trigger; LLM fills params | unit | `python -c "import asyncio; from unittest.mock import patch; from src.n8n.executor import execute_intent; skel={'id':'t','name':'t','integration':'gmail','side_effecting':True,'description':'d','n8n_workflow_id':1,'parameter_schema':{}};\nimport src.n8n.executor as ex;\np1=patch('src.n8n.executor.n8n_templates.match_template',return_value=skel);p2=patch('src.n8n.executor._fill_with_llm',return_value={});p3=patch('src.n8n.executor.AUTOPILOT_RL_LEVEL',1);\np1.start();p2.start();p3.start();r=asyncio.run(execute_intent('send email',{}));assert r['status']=='needs_approval', r"` | ⬜ pending |
| 02-02-03 | 02 | 2 | N8N-01, N8N-02 | T-02-05 | connect-time sync best-effort (non-blocking); command router reaches executor | unit | `python -c "import src.core.router as r; assert 'n8n_workflow' in r.INTENT_MAP and hasattr(r,'_handle_n8n_workflow')" && python -c "import src.api.auth_session as a; assert hasattr(a,'_sync_connected_credentials')"` | ⬜ pending |
| 02-03-01 | 03 | 3 | N8N-04 | T-02-06, T-02-07 | callback endpoint logs execution; unauthenticated by design; log capped | unit | `python -c "from fastapi.testclient import TestClient; from src.app import app; c=TestClient(app); assert c.post('/api/v1/webhook/n8n', json={'executionId':'42','status':'success','data':{}}).json()['status']=='ok'; assert c.post('/api/v1/webhook/n8n', content='x', headers={'Content-Type':'application/json'}).json()['status']=='error'"` | ⬜ pending |
| 02-03-02 | 03 | 3 | N8N-04, INFRA-05 | — | all 6 test classes green incl. RL1 regression guard, LLM-fill, credential-order assertions | unit | `python -m unittest tests.test_n8n_execution -v` | ⬜ pending |
| 02-03-03 | 03 | 3 | N8N-01, N8N-02, N8N-04 | T-02-01 | live workflows provisioned; real IDs recorded; credential usable in n8n UI | manual | `python -c "from src.n8n.client import health_check; print(health_check())"` + live read-only trigger via brain (see Manual-Only Verifications) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Folded into **plan 02-01 (wave 1)** — there is no separate Wave 0 plan:

- [x] `tests/test_n8n_execution.py` created in 02-01 Task 2 (`N8NClientTests` + `ErrorTests` green; `CredentialTests`, `TemplateTests`, `ExecutorTests`, `CallbackTests` stubbed). Completed to full green in 02-03 Task 2.
- [x] `N8N_BASE_URL` and `N8N_API_KEY` added to `.env.example` with setup comments (02-01 Task 1).
- [ ] Docker Compose n8n service running with API key generated — **manual gate, 02-03 Task 3**.
- [ ] Two starter workflow skeletons created in n8n and IDs recorded in template JSON files — **manual gate, 02-03 Task 3** (template JSONs ship with `n8n_workflow_id: 0` until then).

---

## Manual-Only Verifications

| Behavior | Requirement | Task | Why Manual | Test Instructions |
|----------|-------------|------|------------|-------------------|
| Trigger read-only n8n workflow end-to-end via brain | N8N-01 | 02-03-03 | Requires live n8n instance + real workflow | Start n8n via `docker compose -f docker-compose.n8n.yml up -d`, create API key, set `.env`, record workflow IDs in template JSONs, then `route_command("summarize my gmail")`; verify executor returns a result and `data/n8n_executions.json` logs the run |
| Credential injection creates usable n8n credential | N8N-02 | 02-03-03 | Requires live n8n + real OAuth token | Sync a Gmail credential via `sync_credential`, open n8n UI, verify the credential exists and is usable in a workflow node (owner never pasted the raw key) |
| Connect-time credential sync on sign-in | N8N-02, D-05 | 02-02-03 / 02-03-03 | Requires live n8n + real sign-in | Sign in / connect an app; confirm the matching n8n credential is provisioned and that sign-in still succeeds even if n8n is down |
| Side-effecting workflow approval prompt in AI Guide | N8N-01, D-07 | 02-03-03 | Requires Phase 3 AI Guide surface | Trigger side-effecting workflow; the executor returns `needs_approval` (backend contract); the inline AI-Guide prompt rendering is delivered by Phase 3 |

---

## Validation Sign-Off

- [x] All implementation tasks have an `<automated>` verify (02-03-03 is an explicit manual checkpoint)
- [x] Sampling continuity: no 3 consecutive implementation tasks without automated verify (wave 2 = 3/3 automated; wave 3 = 2/3 automated)
- [x] Wave 0 test artifact created in plan 02-01; live-instance requirements gated by the 02-03 Task 3 manual checkpoint
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** ready for re-check
