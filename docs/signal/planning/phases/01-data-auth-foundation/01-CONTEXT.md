# Phase 1: Data & Auth Foundation - Context

**Gathered:** 2026-05-29
**Status:** Ready for planning
**Source:** Phase discussion (3 locked tech decisions) + PRD express path

<domain>
## Phase Boundary

This phase stands up the **net-new backend substrate** that every later Signal phase depends on.
It is backend/infra only (no Signal UI — that begins Phase 3).

**In scope (REQs INFRA-01..04, ONB-01):**
- A provisioned **vector database** serving embedding similarity queries (INFRA-01)
- **Embeddings generated and indexed** for library entries and ingested items (INFRA-02)
- A **token-cache / dedup layer**: when incoming content matches an indexed item, serve the cached summary instead of a fresh LLM call (INFRA-03)
- **Persistence re-scoped** from owner-of-the-box to a single explicit **tenant/owner record**, with no design choices that hard-block future multi-tenancy (INFRA-04)
- **Persistent Google OAuth** sign-in that survives a page refresh (ONB-01)

**Explicitly NOT in this phase:**
- The n8n REST client, credential injection, callbacks, and error-abstraction → **Phase 2**
- Conceptual-search UX, AI Guide, library UI → **Phase 3**
- Multi-tenant isolation, billing → out of scope (see REQUIREMENTS.md)

</domain>

<decisions>
## Implementation Decisions

### Backend home (LOCKED)
- **Signal's backend extends the existing `solo-leveling` FastAPI brain** — new modules live inside `solo-leveling/src/`. This makes reuse of the brain's planning API, library store, Gemini dispatcher, and RL governor trivial (same repo/process), per the reuse-parts hybrid decision in PROJECT.md.
- New Phase-1 code (vector client, embeddings, token-cache, tenant-scoping) is added as new modules under `solo-leveling/src/core/` (or a new `src/vector/`), wired into the FastAPI app (`src/app.py`).

### Vector database (LOCKED)
- **pgvector on Postgres.** A single Postgres instance serves BOTH n8n (which already supports a Postgres backend — see commented section in `docker-compose.n8n.yml`) and Signal's vector search. SQL-native; per-row `owner_id` gives a clean path to multi-tenant later.
- Postgres is provisioned via the existing `docker-compose.n8n.yml` (uncomment/extend the Postgres service) or a sibling compose service — Claude's discretion on the exact compose wiring.

### Embeddings provider (LOCKED)
- **Gemini embeddings**, using the brain's existing `GEMINI_API_KEY` (consistent with `AGENT_PROVIDER=gemini`). No new provider/key.
- Embedding model variant and dimension are Claude's discretion (use a current Gemini text-embedding model; record the chosen dimension in the pgvector column definition).

### Tenancy / persistence (LOCKED shape, details discretionary)
- Re-scope the brain's currently single-owner, shared `_PROJECT_ROOT/library` and process-wide tokens to a **single explicit owner/tenant record** (e.g. an `owner_id` column/namespace defaulted to the sole owner). Do NOT build full multi-tenant isolation — just avoid choices that hard-block it.

### Auth (LOCKED reuse)
- **Reuse the existing Firebase Google auth**: backend verification in `solo-leveling/src/integrations/firebase/auth.py` + the dashboard Bearer-token pattern. Session must persist across refresh.

### Claude's Discretion
- pgvector schema design, embedding dimension, index type (HNSW/IVF), and migration approach
- Whether Postgres runs inside the n8n compose or as a sibling service; connection/config via `.env`
- Token-cache key derivation, similarity threshold for a "match", and cache storage (pgvector table vs separate)
- How the embeddings pipeline hooks `library_store` writes and ingested items
- Where exactly new modules sit within `solo-leveling/src/` and how they register on the FastAPI app

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project-level context
- `.planning/PROJECT.md` — Signal product context, reuse-parts hybrid decision, constraints
- `.planning/signal-prd.md` — source PRD (§6 Technical Architecture, §7 Safety, Token Caching Layer)
- `.planning/REQUIREMENTS.md` — REQ-IDs INFRA-01..04, ONB-01 (exact acceptance wording)

### Brain architecture (authoritative locators)
- `solo-leveling/ARCHITECTURE.md` — four-layer architecture; where new modules fit
- `solo-leveling/REPO_MAP.md` — directory map of the brain
- `solo-leveling/AI_CONTEXT.md` — current brain phase/priorities (source of truth)
- `solo-leveling/CLAUDE.md` — brain conventions (Python 3.13, `src.` imports, unittest)

### Reuse / modify targets (concrete files)
- `solo-leveling/src/app.py` — FastAPI app; where new routes/startup wiring register
- `solo-leveling/src/core/router.py` — intent router + keyword `INTENT_MAP` (evolved later, Phase 3)
- `solo-leveling/src/core/libraries.py`, `src/core/library_store.py`, `src/core/library_compression.py` — library store + its keyword search/LRU cache (embeddings index hooks here; token-cache relates here)
- `solo-leveling/src/agents/dispatcher.py` — Gemini/Kimi dispatcher (LLM + embedding calls; token-cache wraps `run_agent`)
- `solo-leveling/src/api/library.py`, `src/api/planning.py` — existing API endpoint patterns to follow
- `solo-leveling/src/integrations/firebase/auth.py` — Firebase Google auth verification (reuse for ONB-01)
- `solo-leveling/src/autopilot/governor.py` — RL governor (not modified this phase; context for later HITL reuse)
- `docker-compose.n8n.yml` — existing n8n stack with a commented Postgres service to enable for pgvector

</canonical_refs>

<specifics>
## Specific Ideas

- Consolidate infra: one Postgres for n8n + pgvector keeps the MacMini footprint small.
- Token-cache (INFRA-03) is the PRD's "Token Caching Layer" (§6): embed incoming content, check the vector index, and on a near-duplicate match serve the stored summary instead of calling the LLM — observable as a cache hit in logs.
- Embeddings (INFRA-02) must cover BOTH existing library entries (backfill via `library_store`) and newly ingested items (hook on write).
- Keep everything single-owner but tenant-shaped: an `owner_id` that today is a constant, tomorrow a FK.

</specifics>

<deferred>
## Deferred Ideas

- n8n REST client, owner-credential injection, intent→JSON triggering, webhook callbacks, error-abstraction layer → **Phase 2 (n8n Execution Layer)**
- Conceptual-search UI, AI Guide Command Bar, Recent Spark Cards, per-entry Q&A → **Phase 3**
- Multi-tenant isolation, per-user OAuth vault, billing/metering, YOLO mode → out of scope for v1 (REQUIREMENTS.md)

</deferred>

---

*Phase: 01-data-auth-foundation*
*Context gathered: 2026-05-29 via phase discussion (top-level)*
