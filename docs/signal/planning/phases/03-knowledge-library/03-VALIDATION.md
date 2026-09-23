---
phase: 3
slug: knowledge-library
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-30
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Backend extends the `solo-leveling` brain (Python 3.13, stdlib `unittest`, offline-by-default).
> Dashboard is static React/Vite — manual browser verification for UI.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | stdlib `unittest` (brain convention) |
| **Config file** | none — tests live under `solo-leveling/tests/` |
| **Quick run command** | `cd solo-leveling && python -m unittest tests.test_vector_search tests.test_intent_parser tests.test_guide_api -v` |
| **Full suite command** | `cd solo-leveling && python -m unittest discover tests -v` |
| **Estimated runtime** | ~30–60 seconds (offline; Postgres-backed tests gated behind `SIGNAL_POSTGRES_DSN_TEST`) |

> Postgres/pgvector-dependent tests run only when a local pgvector instance is up; gate them behind `SIGNAL_POSTGRES_DSN_TEST` so the default offline suite stays green.

---

## Sampling Rate

- **After every task commit:** Run the quick command (the module(s) touched)
- **After every plan wave:** Run the full suite
- **Before `/gsd:verify-work`:** Full suite green; pgvector smoke (`SIGNAL_POSTGRES_DSN_TEST` set) green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

> Seeded from REQUIREMENTS + RESEARCH "## Validation Architecture". Planner refines task IDs/waves.

| Requirement | Validation intent | Test Type | Automated Command (indicative) | Status |
|-------------|-------------------|-----------|--------------------------------|--------|
| LIB-01 | Archive article/note/document into library | integration | `python -m unittest tests.test_library_api -v` | ✅ existing |
| LIB-02 | Plain-text conceptual search returns semantically related entries | unit + integration | `python -m unittest tests.test_vector_search -v` | ❌ Wave 0 |
| LIB-03 | Recent Spark Cards show most recent inputs | unit | `python -m unittest tests.test_library_api -v` | ✅ (needs new test) |
| LIB-05 | Per-entry AI Q&A answers questions | integration | `python -m unittest tests.test_library_api -v` | ✅ existing |
| GUIDE-01 | Persistent AI Guide panel present | e2e / manual | Browser verification | ❌ Wave 0 |
| GUIDE-02 | Natural-language Command Bar executes via LLM intent | unit + integration | `python -m unittest tests.test_intent_parser -v` | ❌ Wave 0 |
| GUIDE-03 | Status banner shows processed-noise metrics | unit | `python -m unittest tests.test_guide_api -v` | ❌ Wave 0 |
| GUIDE-05 | "Park a Distraction" captures stray thought | integration | `python -m unittest tests.test_guide_api -v` | ❌ Wave 0 |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_vector_search.py` — covers LIB-02 (vector search contract)
- [ ] `tests/test_intent_parser.py` — covers GUIDE-02 (LLM intent parsing)
- [ ] `tests/test_guide_api.py` — covers GUIDE-01, GUIDE-03, GUIDE-05 (guide endpoints)
- [ ] Dashboard: `src/components/guide/` directory with component stubs

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| AI Guide panel renders persistently across tab switches | GUIDE-01 | UI layout / visual | Open dashboard, verify panel visible on Overview, Library, Planning tabs |
| Command Bar parses natural language and shows intent | GUIDE-02 | LLM integration + UX flow | Type "search for machine learning papers", verify response shows search results |
| Status banner shows live metrics | GUIDE-03 | Metrics computation + visual | Verify banner shows entry count, recent captures count |
| Distraction Gate captures and saves thought | GUIDE-05 | End-to-end flow | Click "Park", type thought, verify it appears in library as "thought" section |
| Spark Cards show recent entries | LIB-03 | Visual layout | Verify 3-4 most recent entries shown as cards in Library page |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter (after planner finalizes the map)

**Approval:** pending
