# Phase 3: Knowledge Library + Conceptual Search + AI Guide - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning
**Source:** Phase discussion + RESEARCH.md + Phase 1 completion state

<domain>
## Phase Boundary

This phase ships the **Milestone-1 centerpiece** on top of the Phase 1 vector spine (pgvector + embeddings + token-cache). It is NOT blocked by Phase 2 (n8n Execution Layer) — the n8n layer is not needed for conceptual search, the AI Guide, or library enhancements.

**In scope (REQs LIB-01, LIB-02, LIB-03, LIB-05, GUIDE-01, GUIDE-02, GUIDE-03, GUIDE-05):**
- **LIB-01**: Folderless library archives articles, notes, documents (reuses existing store)
- **LIB-02**: Plain-text conceptual search returns semantically related entries via vector embeddings
- **LIB-03**: Recent Spark Cards show most recently captured inputs (max 3-4)
- **LIB-05**: Per-entry AI Q&A answers questions against a selected entry (reuses dashboard component)
- **GUIDE-01**: Persistent right-hand AI Guide panel present across every view
- **GUIDE-02**: Natural-language Command Bar executes via LLM intent parsing (replaces INTENT_MAP)
- **GUIDE-03**: Status banner shows reassuring processed-noise metrics
- **GUIDE-05**: "Park a Distraction" gate captures a stray thought without leaving focus

**Explicitly NOT in this phase:**
- n8n execution, credential injection, workflow triggering → **Phase 2**
- Zen 70/30 shell, contextual action buttons per view → **Phase 4**
- Active Context Stacks auto-grouping → **Phase 8**
- Multi-tenant isolation, billing → out of scope (see REQUIREMENTS.md)

</domain>

<decisions>
## Implementation Decisions

### Backend home (LOCKED)
- **Signal's backend extends the existing `solo-leveling` FastAPI brain** — new modules live inside `solo-leveling/src/`. This reuses the brain's planning API, library store, Gemini dispatcher, and RL governor.
- New Phase-3 code: `src/vector/search.py`, `src/core/intent_parser.py`, `src/api/guide.py`.
- EVOLVE existing: `src/core/router.py` (replace INTENT_MAP), `src/api/library.py` (add /search, /recent), `src/api/v1_router.py` (register guide router).

### Vector search (LOCKED)
- **pgvector HNSW index** already provisioned in Phase 1. Cosine similarity via `1 - (embedding <=> query_vec)`.
- Hybrid search: keyword fast-path first, vector fallback when keyword results are sparse.
- Query embeddings use `RETRIEVAL_QUERY` task type; document embeddings already stored with `RETRIEVAL_DOCUMENT`.

### Intent parsing (LOCKED)
- **Gemini LLM structured output** replaces the brittle `INTENT_MAP` keyword matcher.
- `run_agent()` with a system prompt that classifies intent + extracts parameters.
- Keyword fallback (`_detect_intent`) preserved for offline/low-confidence scenarios.

### AI Guide panel (LOCKED)
- **Standalone persistent right-hand panel** in the dashboard, rendered outside the tab switcher.
- Self-contained component — no positioning logic inside it. `DashboardPage` decides where to render.
- Phase 4 will simply move the render location into Panel B of the Zen shell.

### Dashboard (LOCKED)
- **Reuses existing components aggressively**: `EntryAIPanel`, `EntryDetailModal`, `CommandPalette` patterns.
- New components in `dashboard/src/components/guide/`: `AIGuidePanel.tsx`, `CommandBar.tsx`, `StatusBanner.tsx`, `DistractionGate.tsx`.
- No new npm packages — all dependencies already in `package.json`.

### Claude's Discretion
- Exact SQL for vector search (parameterized, owner_id-scoped)
- Intent parser prompt engineering and allowed intent list
- Status banner metric computation (entry count, recent captures, command count)
- Distraction gate storage format (library entry with section="thought")
- Component prop interfaces and state lifting strategy

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project-level context
- `.planning/PROJECT.md` — Signal product context, reuse-parts hybrid decision
- `.planning/REQUIREMENTS.md` — REQ-IDs LIB-01..LIB-05, GUIDE-01..GUIDE-05
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, dependencies

### Phase 1 foundation (authoritative locators)
- `solo-leveling/src/vector/db.py` — pool lifecycle (Phase 1)
- `solo-leveling/src/vector/embed.py` — Gemini embedding client (Phase 1)
- `solo-leveling/src/vector/cache.py` — cosine distance query pattern (Phase 1)
- `solo-leveling/src/vector/hooks.py` — `on_entry_saved` hook (Phase 1)
- `solo-leveling/src/vector/migrations/001_init_vector.sql` — schema: `signal_embeddings`, HNSW indexes

### Reuse / modify targets (concrete files)
- `solo-leveling/src/core/router.py` — `INTENT_MAP`, `_detect_intent()`, `_dispatch()` — **EVOLVE**
- `solo-leveling/src/core/libraries.py` — `handle_library_command()`, `_capture_entry()`, `SearchCache`
- `solo-leveling/src/core/library_store.py` — `_LibraryStore` ABC, `search_entries()`, `get_entry()`
- `solo-leveling/src/agents/dispatcher.py` — `run_agent(task, context, system)` — reused for intent parsing
- `solo-leveling/src/api/library.py` — existing REST endpoints, `require_auth` dependency — **EVOLVE**
- `solo-leveling/src/api/v1_router.py` — router aggregator — **EVOLVE**
- `solo-leveling/src/api/deps.py` — `require_auth`, `optional_auth`
- `solo-leveling/src/app.py` — FastAPI app; where new routers register
- `dashboard/src/components/library/LibraryPage.tsx` — existing folderless library UI
- `dashboard/src/components/library/EntryAIPanel.tsx` — per-entry Q&A with localStorage history
- `dashboard/src/components/dashboard/DashboardPage.tsx` — tab switcher, where Guide panel integrates — **EVOLVE**
- `dashboard/src/lib/api.ts` — API client functions — **EVOLVE**
- `dashboard/src/hooks/useApi.ts` — library hooks — **EVOLVE**

</canonical_refs>

<specifics>
## Specific Ideas

- Vector search must always join with filesystem store — `signal_embeddings` may have stale entries if files were deleted but embeddings not cleaned up.
- Debounce Command Bar input at 300ms to avoid excessive LLM calls.
- Status banner metrics: library entry count, captures in last 24h, total commands processed. All queryable from existing data.
- Distraction Gate saves as a "thought" section library entry with minimal friction (no section picker, no tags).
- Spark Cards fetch the 4 most recent entries across all sections, sorted by `updated_at`.
- The AI Guide panel state (chat history, command input) must be lifted to `DashboardPage` level or use a context provider — React unmounts inside tab switchers.

</specifics>

<deferred>
## Deferred Ideas

- n8n REST client, credential injection, workflow triggering → **Phase 2**
- Zen 70/30 shell structural rebuild → **Phase 4**
- Contextual action buttons per view/card → **Phase 4 (GUIDE-04)**
- Active Context Stacks auto-grouping → **Phase 8 (LIB-04)**
- Multi-tenant isolation, billing, YOLO mode → out of scope for v1

</deferred>

---

*Phase: 03-knowledge-library*
*Context gathered: 2026-05-30*
