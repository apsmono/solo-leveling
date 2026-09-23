---
phase: 1
slug: data-auth-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-29
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Backend extends the `solo-leveling` brain (Python 3.13, stdlib `unittest`, offline-by-default).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | stdlib `unittest` (brain convention) |
| **Config file** | none — tests live under `solo-leveling/tests/` |
| **Quick run command** | `cd solo-leveling && python -m unittest tests.test_vector_store tests.test_token_cache -v` |
| **Full suite command** | `cd solo-leveling && python -m unittest discover tests` |
| **Estimated runtime** | ~30–60 seconds (offline; Postgres-backed tests gated behind a live flag) |

> Postgres/pgvector-dependent tests run only when a local pgvector instance is up; gate them behind an env flag (e.g. `ENABLE_PGVECTOR_TESTS=1`) so the default offline suite stays green — mirrors the brain's `ENABLE_LIVE_SMOKE_TESTS` pattern.

---

## Sampling Rate

- **After every task commit:** Run the quick command (the module(s) touched)
- **After every plan wave:** Run the full suite
- **Before `/gsd:verify-work`:** Full suite green; pgvector smoke (`ENABLE_PGVECTOR_TESTS=1`) green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

> Seeded from REQUIREMENTS + RESEARCH "## Validation Architecture". Planner refines task IDs/waves.

| Requirement | Validation intent | Test Type | Automated Command (indicative) | Status |
|-------------|-------------------|-----------|--------------------------------|--------|
| INFRA-01 | pgvector instance up; `<=>` query returns nearest rows via HNSW (not seq scan) | integration | `ENABLE_PGVECTOR_TESTS=1 python -m unittest tests.test_vector_store` | ⬜ pending |
| INFRA-02 | Library write generates + indexes a Gemini embedding (768-dim); backfill indexes existing entries | integration | `ENABLE_PGVECTOR_TESTS=1 python -m unittest tests.test_embeddings` | ⬜ pending |
| INFRA-03 | Re-ingesting near-duplicate content returns cached summary (cache-hit logged), no fresh LLM call | unit + integration | `python -m unittest tests.test_token_cache` (LLM call mocked) | ⬜ pending |
| INFRA-04 | All new rows carry `owner_id`; queries scoped by owner; default-owner constant resolvable | unit | `python -m unittest tests.test_owner_scoping` | ⬜ pending |
| ONB-01 | `POST /auth/session-login` sets httpOnly session cookie; protected route accepts it after "refresh" | unit | `python -m unittest tests.test_auth_session` (Firebase verify mocked) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `solo-leveling/tests/test_vector_store.py` — pgvector connect + nearest-neighbour stub (INFRA-01)
- [ ] `solo-leveling/tests/test_embeddings.py` — Gemini embedding generation/indexing stub (INFRA-02), embedding call mocked offline
- [ ] `solo-leveling/tests/test_token_cache.py` — cache-hit/miss stub with mocked dispatcher (INFRA-03)
- [ ] `solo-leveling/tests/test_owner_scoping.py` — owner_id presence/scoping stub (INFRA-04)
- [ ] `solo-leveling/tests/test_auth_session.py` — session-cookie login/verify stub with mocked Firebase (ONB-01)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 0.92 cosine dedup threshold is well-calibrated | INFRA-03 | Threshold is empirical (RESEARCH flagged LOW confidence) | After seeding real items, confirm true duplicates collapse and distinct items do not; tune the constant |
| Session cookie survives a real browser refresh | ONB-01 | End-to-end browser behavior | Sign in, refresh the page, confirm still authenticated against a protected endpoint |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter (after planner finalizes the map)

**Approval:** pending
