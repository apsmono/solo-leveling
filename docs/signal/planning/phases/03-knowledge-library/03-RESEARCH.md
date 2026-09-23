# Phase 3: Knowledge Library + Conceptual Search + AI Guide - Research

**Researched:** 2026-05-30
**Domain:** FastAPI backend + React/Vite frontend, vector semantic search (pgvector), LLM intent parsing
**Confidence:** HIGH

## Summary

Phase 3 builds the Milestone-1 centerpiece on top of the Phase 1 vector spine (pgvector + Gemini embeddings + token-cache). The phase has three workstreams: (1) **Conceptual Search** — layer vector semantic search over the existing keyword-based library store, (2) **AI Guide** — replace the brittle `INTENT_MAP` keyword matcher with LLM-driven intent parsing and surface a persistent right-hand guide panel, and (3) **Library UI enhancements** — Recent Spark Cards and per-entry Q&A (reusing existing dashboard components).

The architecture is straightforward because Phase 1 already provisioned the vector infrastructure: `signal_embeddings` table with HNSW index, `on_entry_saved` hook firing on every library save, and `embed_text()` generating 768-dim vectors. The net-new work is: a vector search query module, an LLM intent parser to replace `INTENT_MAP`, API endpoints for conceptual search and intent parsing, and dashboard UI components for the AI Guide panel, Spark Cards, and distraction parking.

**Primary recommendation:** Build in 4 waves — (1) vector search backend + API, (2) LLM intent parser + command bar, (3) AI Guide panel UI + status banner + distraction gate, (4) integration verification and tests. Reuse existing components aggressively; the dashboard already has `LibraryPage`, `EntryAIPanel`, `EntryDetailModal`, and `CommandPalette`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Vector semantic search | API / Backend | Database (pgvector) | Cosine similarity query runs in Postgres; backend embeds query text and returns ranked results |
| Keyword search | API / Backend | — | Existing `search_entries()` on index records; stays as fallback/fast path |
| LLM intent parsing | API / Backend | — | Gemini dispatcher (`run_agent`) parses natural language into structured intent + parameters |
| Library storage | API / Backend | Filesystem (`library/`) | Filesystem-first with Firestore fallback; unchanged from Phase 1 |
| AI Guide panel | Browser / Client | — | Persistent right-hand UI panel; renders across all views |
| Command Bar | Browser / Client | API / Backend (intent parse) | User types natural language; client sends to backend for LLM parsing |
| Per-entry Q&A | Browser / Client | API / Backend (synthesize) | Reuses `EntryAIPanel` + `/entries/{id}/synthesize` endpoint |
| Spark Cards | Browser / Client | API / Backend (recent entries) | Client fetches recent entries and renders as cards |
| Status banner | Browser / Client | API / Backend (metrics) | Backend computes processed-noise metrics; client renders banner |
| Distraction parking | Browser / Client | API / Backend (save) | Quick-capture modal that saves to library without context switch |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pgvector | 0.4.2 | Vector extension for Postgres | Already provisioned in Phase 1; HNSW index on 768-dim embeddings |
| psycopg | 3.3.4+ | Async Postgres driver | Already used for pool lifecycle in `src.vector.db` |
| google-genai | 2.7.0+ | Gemini embedding + chat | Already used for embeddings; same client for intent parsing |
| httpx | 0.28.0+ | HTTP client for Gemini API | Already used in `src.agents.dispatcher` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| React | 19.2.6 | UI framework | Already in dashboard; no change |
| Tailwind CSS | 4.3.0 | Styling | Already in dashboard; no change |
| lucide-react | 1.16.0 | Icons | Already in dashboard; no change |
| cmdk | 1.1.1 | Command palette | Already in dashboard (`CommandPalette.tsx`) |
| firebase | 12.13.0 | Auth client | Already in dashboard; no change |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| LLM intent parsing (Gemini) | Fine-tuned classifier / spaCy | LLM is more flexible for natural language variation; classifier needs training data and retraining |
| pgvector HNSW | ivfflat | HNSW has better build/query performance tradeoff for <100K vectors; already chosen in Phase 1 |
| Custom vector search module | Qdrant / Pinecone | pgvector is already provisioned and tenant-scoped; external service adds ops overhead |

**Installation:** No new Python packages required — all dependencies already in `requirements.txt`. No new npm packages required — all dashboard dependencies already in `package.json`.

## Package Legitimacy Audit

No new external packages are required for this phase. All dependencies were installed and verified in Phase 1.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| (none new) | — | — | — | — | — | — |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BROWSER / CLIENT                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  AI Guide Panel │  │  Command Bar    │  │  LibraryPage (enhanced)     │  │
│  │  (persistent)   │  │  (natural lang) │  │  ├─ Spark Cards (recent)   │  │
│  │  ├─ Status      │  │                 │  │  ├─ Conceptual Search      │  │
│  │  │   Banner      │  │                 │  │  ├─ Entry Detail + Q&A   │  │
│  │  ├─ Chat Thread │  │                 │  │  └─ Distraction Gate     │  │
│  │  └─ Suggested   │  │                 │  │                            │  │
│  │      Actions    │  │                 │  │                            │  │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────────────────┘  │
│           │                    │                                             │
│           │  POST /api/v1/guide/command  {text: "..."}                       │
│           │  ─────────────────────────────────────────►                      │
│           │                    │                                             │
│           │  GET  /api/v1/library/search?query=...&mode=vector               │
│           │  ─────────────────────────────────────────►                      │
│           │                    │                                             │
│           │  GET  /api/v1/library/entries?per_page=4&sort=newest             │
│           │  ─────────────────────────────────────────►                      │
│           └────────────────────┘                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI API / BACKEND                              │
│                                                                              │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────┐  │
│  │  src.api.guide          │    │  src.api.library (enhanced)             │  │
│  │  ├─ POST /guide/command │    │  ├─ GET /library/entries (existing)    │  │
│  │  │   → parse_intent()  │    │  ├─ GET /library/entries/{id} (exist)  │  │
│  │  ├─ GET /guide/status   │    │  ├─ POST /library/search (NEW)         │  │
│  │  └─ POST /guide/park    │    │  │   → vector_search() or keyword      │  │
│  │                         │    │  ├─ POST /library/capture (NEW)        │  │
│  └───────────┬─────────────┘    │  └─ POST /entries/{id}/synthesize      │  │
│              │                  └─────────────────────────────────────────┘  │
│              │                              │                                 │
│              ▼                              ▼                                 │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────┐  │
│  │  src.core.intent_parser │    │  src.vector.search (NEW)                │  │
│  │  (replaces INTENT_MAP)  │    │  ├─ search_embeddings()                 │  │
│  │  ├─ LLM prompt:         │    │  │   → embed_text(query)                │  │
│  │  │   intent + params   │    │  │   → cosine similarity via pgvector   │  │
│  │  └─ Structured output   │    │  │   → return ranked entry_ids          │  │
│  │    {intent, params}     │    │  └─ hybrid_search() (keyword + vector) │  │
│  └───────────┬─────────────┘    └─────────────────────────────────────────┘  │
│              │                              │                                 │
│              └──────────────────────────────┘                                 │
│                             │                                                 │
│                             ▼                                                 │
│              ┌─────────────────────────────┐                                  │
│              │  src.agents.dispatcher      │                                  │
│              │  run_agent(task, context)   │                                  │
│              │  → Gemini / Kimi            │                                  │
│              └─────────────────────────────┘                                  │
│                             │                                                 │
│                             ▼                                                 │
│              ┌─────────────────────────────┐                                  │
│              │  src.vector.db (existing)   │                                  │
│              │  AsyncConnectionPool        │                                  │
│              │  → signal_embeddings table  │                                  │
│              └─────────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
solo-leveling/
src/
├── vector/
│   ├── __init__.py
│   ├── db.py                    # EXISTING: pool lifecycle
│   ├── embed.py                 # EXISTING: Gemini embeddings
│   ├── cache.py                 # EXISTING: token-cache dedup
│   ├── hooks.py                 # EXISTING: on_entry_saved
│   └── search.py                # NEW: semantic search queries
├── core/
│   ├── router.py                # EXISTING: EVOLVE - replace INTENT_MAP
│   ├── intent_parser.py         # NEW: LLM-driven intent parsing
│   ├── libraries.py             # EXISTING: library command handlers
│   ├── library_store.py         # EXISTING: storage abstraction
│   └── config.py                # EXISTING: env vars
├── api/
│   ├── v1_router.py             # EXISTING: wire new routers
│   ├── library.py               # EXISTING: EVOLVE - add /search, /capture
│   ├── guide.py                 # NEW: AI Guide endpoints
│   └── deps.py                  # EXISTING: auth dependency
└── agents/
    └── dispatcher.py            # EXISTING: run_agent()

dashboard/
src/
├── components/
│   ├── library/
│   │   ├── LibraryPage.tsx      # EXISTING: EVOLVE - add Spark Cards
│   │   ├── EntryAIPanel.tsx     # EXISTING: reuse for per-entry Q&A
│   │   ├── EntryDetailModal.tsx # EXISTING: reuse
│   │   └── LinkCaptureModal.tsx # EXISTING: reuse
│   ├── guide/
│   │   ├── AIGuidePanel.tsx     # NEW: persistent right-hand panel
│   │   ├── CommandBar.tsx       # NEW: natural-language input
│   │   ├── StatusBanner.tsx     # NEW: processed-noise metrics
│   │   └── DistractionGate.tsx  # NEW: quick-capture modal
│   └── dashboard/
│       ├── DashboardPage.tsx    # EXISTING: EVOLVE - integrate Guide panel
│       └── CommandInput.tsx     # EXISTING: to be replaced by CommandBar
├── hooks/
│   └── useApi.ts                # EXISTING: EVOLVE - add guide hooks
└── lib/
    └── api.ts                   # EXISTING: EVOLVE - add guide endpoints
```

### Pattern 1: Hybrid Search (Keyword + Vector)
**What:** When a user searches the library, first try keyword match for speed and exact matches. If keyword results are sparse or the query looks conceptual (no exact word matches), fall back to vector semantic search.
**When to use:** LIB-02 conceptual search. The keyword path is fast (index.json in memory); vector path is slower (embedding API call + DB query) but catches semantic relationships.
**Example:**
```python
# src/vector/search.py
async def search_library(
    query: str,
    owner_id: str,
    mode: Literal["keyword", "vector", "hybrid"] = "hybrid",
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Search library entries by keyword, vector, or hybrid."""
    if mode in ("keyword", "hybrid"):
        keyword_results = _get_store().search_entries(query, limit=limit)
        if mode == "keyword":
            return keyword_results
        # hybrid: if keyword found enough, return them; else augment with vector
        if len(keyword_results) >= limit // 2:
            return keyword_results

    # Vector search path
    if not SIGNAL_POSTGRES_DSN:
        return keyword_results if mode == "hybrid" else []

    vec = embed_text(query, task_type="RETRIEVAL_QUERY")
    async with get_pool().connection() as conn:
        rows = await conn.fetchall(
            """
            SELECT entry_id, section, source_url, 1 - (embedding <=> %s::vector) AS similarity
            FROM signal_embeddings
            WHERE owner_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (vec, owner_id, vec, limit),
        )

    # Enrich with store metadata
    results = []
    for row in rows:
        entry = _get_store().get_entry(row["entry_id"])
        if entry:
            entry["similarity"] = round(row["similarity"], 3)
            results.append(entry)
    return results
```

### Pattern 2: LLM Intent Parsing (Replaces INTENT_MAP)
**What:** Send user natural language to Gemini with a structured system prompt that asks for intent classification + parameter extraction. Return JSON with `intent` and `params` fields. The router then dispatches based on `intent`.
**When to use:** GUIDE-02 — every command bar input goes through this parser.
**Example:**
```python
# src/core/intent_parser.py
import json
from src.agents.dispatcher import run_agent

_INTENT_SYSTEM_PROMPT = """You are an intent parser for a personal knowledge system.
Given a user's natural language command, classify it into one of these intents and extract parameters.

Intents: library_search, library_capture, library_qa, status, help, park_distraction, unknown

Respond with valid JSON only:
{
  "intent": "library_search",
  "params": {"query": "machine learning papers"},
  "confidence": 0.95
}"""

async def parse_intent(text: str) -> dict[str, Any]:
    """Parse user text into structured intent + parameters via LLM."""
    try:
        response = run_agent(
            task=f"Parse this command: {text}",
            system=_INTENT_SYSTEM_PROMPT,
        )
        parsed = json.loads(response)
        return {
            "intent": parsed.get("intent", "unknown"),
            "params": parsed.get("params", {}),
            "confidence": parsed.get("confidence", 0.5),
        }
    except Exception:
        # Fallback: try keyword map for backward compat
        from src.core.router import _detect_intent
        intent = _detect_intent(text)
        return {"intent": intent, "params": {"text": text}, "confidence": 0.3}
```

### Pattern 3: AI Guide Panel as Standalone Surface
**What:** The AI Guide panel is a persistent right-hand panel that exists even before the Zen shell (Phase 4). It shows: (a) a status banner with processed-noise metrics, (b) a chat thread with the AI Guide, (c) a command input, (d) contextual action buttons. It communicates with the backend via the new `/api/v1/guide/*` endpoints.
**When to use:** GUIDE-01, GUIDE-03, GUIDE-05. This panel ships in Phase 3 as a standalone component that will later be locked into Panel B of the Zen shell.
**Example:**
```typescript
// dashboard/src/components/guide/AIGuidePanel.tsx
interface AIGuidePanelProps {
  activeView?: string;  // "library", "overview", etc. — for contextual actions
}

export function AIGuidePanel({ activeView }: AIGuidePanelProps) {
  const { metrics } = useGuideStatus();
  const { messages, send, loading } = useGuideChat();
  const [distractionOpen, setDistractionOpen] = useState(false);

  return (
    <div className="flex flex-col h-full border-l border-border bg-surface">
      <StatusBanner metrics={metrics} />
      <ChatThread messages={messages} loading={loading} />
      <CommandBar onSend={send} onPark={() => setDistractionOpen(true)} />
      <ContextualActions view={activeView} />
      <DistractionGate open={distractionOpen} onClose={setDistractionOpen} />
    </div>
  );
}
```

### Anti-Patterns to Avoid
- **Don't query the vector DB synchronously.** Embedding generation is an HTTP call to Gemini (~100-500ms). Always use async/await; never block the event loop.
- **Don't forget owner_id scoping.** Every vector query must include `WHERE owner_id = %s`. The table has a composite unique index on `(owner_id, entry_id)`.
- **Don't parse LLM output without a fallback.** If Gemini returns malformed JSON, fall back to keyword intent detection. Never crash the command flow.
- **Don't embed the entire markdown for search.** The `signal_embeddings` table stores embeddings of entry content. For search, embed the query with `RETRIEVAL_QUERY` task type (not `RETRIEVAL_DOCUMENT`).
- **Don't rebuild the library index on every search.** `build_index()` rebuilds `library/index.json` by scanning all markdown files. It is called on save, not on search. Search reads from the existing index or the vector DB.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vector similarity search | Custom vector math in Python | pgvector HNSW index | HNSW is optimized C code; custom Python would be 100x slower and memory-intensive |
| Intent classification | Regex/keyword map (current INTENT_MAP) | LLM structured output | Natural language variation is unbounded; keyword maps break constantly |
| Embedding generation | Local model inference | Gemini embedding API | Already integrated; local inference needs GPU + model management |
| Chat history persistence | Custom DB schema | localStorage per entry | `EntryAIPanel` already uses `localStorage` keyed by entry ID; sufficient for personal use |
| Markdown rendering | Custom parser | `renderMarkdownLite` in `EntryDetailModal` | Already exists and handles headers, bold, italic, lists |

**Key insight:** The biggest "don't hand-roll" is the intent parser. The current `INTENT_MAP` has 20+ intent keys with 50+ keywords, and it still misses obvious phrasings. An LLM parser with a structured system prompt handles all variations naturally and can extract parameters (e.g., "search for articles about AI" → `{"intent": "library_search", "params": {"query": "articles about AI", "section": "articles"}}`).

## Common Pitfalls

### Pitfall 1: Vector Search Returns Entry IDs Without Metadata
**What goes wrong:** The `signal_embeddings` table only stores `entry_id`, `section`, `embedding`, and `source_url`. A vector search returns these fields but not title, tags, or markdown. If the entry was deleted from the filesystem but not from the vector DB, you get stale ghost entries.
**Why it happens:** The vector hook (`on_entry_saved`) upserts embeddings but never deletes them. The filesystem store and vector store can drift.
**How to avoid:** Always join vector results with the filesystem store (`_get_store().get_entry(entry_id)`). If `get_entry()` returns `None`, skip the result and optionally queue a vector cleanup. Document this as a known limitation.
**Warning signs:** Search results with empty titles or 404s when clicking through.

### Pitfall 2: LLM Intent Parser Latency
**What goes wrong:** Every command bar input triggers an LLM call (~200-500ms). If the user types fast and hits Enter, the UI feels sluggish.
**Why it happens:** No debouncing or caching on the intent parser.
**How to avoid:** Debounce the command bar input (300ms). Cache parsed intents for identical text in an LRU cache (e.g., `SearchCache` already exists in `libraries.py`). For common commands ("search library", "add to library"), keep the keyword fast-path as a pre-check before calling the LLM.
**Warning signs:** User reports "typing feels slow" or network tab shows many `/guide/command` requests.

### Pitfall 3: Embedding Hook Fails Silently
**What goes wrong:** `_fire_embedding_hook()` catches all exceptions and logs a warning. If Gemini is down or the DB is unreachable, embeddings are not indexed, but the library save succeeds. The user thinks the entry is searchable, but vector search won't find it.
**Why it happens:** The hook is fire-and-forget by design (so save never blocks), but there's no retry or visibility.
**How to avoid:** Add a health check endpoint that reports "unindexed entries" count. In the dashboard, show a subtle indicator on entries that haven't been indexed yet. For Phase 3, document the limitation and add a background re-index task in Phase 6.
**Warning signs:** Vector search returns no results for recently saved entries.

### Pitfall 4: Tenant Scoping Leak
**What goes wrong:** The `signal_embeddings` table has `owner_id` but some queries might forget the `WHERE owner_id = %s` clause, especially in ad-hoc scripts or new endpoints.
**Why it happens:** The current codebase has `SIGNAL_OWNER_ID` as a global default. In a multi-tenant future, this would leak data across users.
**How to avoid:** Always extract `owner_id` from the authenticated user (Firebase token email/uid), never from the global config, in API endpoints. The vector search module should require `owner_id` as a parameter (no default).
**Warning signs:** Tests that don't mock `owner_id` properly; API endpoints that don't use `require_auth`.

### Pitfall 5: Dashboard Component State Drift
**What goes wrong:** The AI Guide panel is persistent across view switches (Library, Overview, etc.). If it holds local state (chat history, command input) and the user switches tabs, state might reset or duplicate.
**Why it happens:** React unmounts/remounts components on tab switch if not careful.
**How to avoid:** Lift AI Guide state to `DashboardPage` level or use a context provider. The panel should be rendered *outside* the tab switcher, not inside each tab's component tree.
**Warning signs:** Chat history disappears when switching from Library to Overview.

## Code Examples

### Vector Search Endpoint
```python
# src/api/library.py — add to existing router

@router.post("/library/search")
async def search_library(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Search library entries by keyword, vector, or hybrid."""
    query = str(payload.get("query", "")).strip()
    mode = str(payload.get("mode", "hybrid")).lower()
    limit = min(int(payload.get("limit", 12)), 50)

    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' in request body.")

    owner_id = user.get("email", user.get("uid", "default-owner"))

    from src.vector.search import search_library as vector_search
    results = await vector_search(query, owner_id=owner_id, mode=mode, limit=limit)

    return {
        "entries": [_enrich_entry(r) for r in results],
        "total": len(results),
        "mode": mode,
        "query": query,
    }
```

### Intent Parser Integration in Router
```python
# src/core/router.py — EVOLVE route_command

async def route_command(text: str, source: str = "api") -> str:
    """Parse intent from text and dispatch to the correct handler."""
    # Try LLM intent parsing first
    from src.core.intent_parser import parse_intent
    parsed = await parse_intent(text)
    intent = parsed["intent"]
    params = parsed.get("params", {})

    logger.info("Intent detected: %s (confidence=%.2f)", intent, parsed.get("confidence", 0))
    reply = await _dispatch_async(intent, text, params)
    _log_command(text, intent, reply, source)
    return reply
```

### Recent Spark Cards API
```python
# src/api/library.py — add to existing router

@router.get("/library/recent")
async def recent_entries(
    limit: int = Query(4, ge=1, le=10),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Return most recently captured entries across all sections."""
    store = _get_store()
    index = store.build_index()
    entries = sorted(
        index.get("entries", []),
        key=lambda e: e.get("updated_at", ""),
        reverse=True,
    )[:limit]

    return {
        "entries": [_enrich_entry(e) for e in entries],
        "total": len(entries),
    }
```

### AI Guide Panel — Dashboard Integration
```typescript
// dashboard/src/components/dashboard/DashboardPage.tsx — EVOLVE

// Add to imports:
import { AIGuidePanel } from "@/components/guide/AIGuidePanel";

// In the render, wrap content + guide side by side:
return (
  <div className="min-h-screen bg-bg text-text">
    <div className="mx-auto max-w-7xl px-4 py-6 flex gap-6">
      {/* Main content area */}
      <div className="flex-1 min-w-0">
        {/* existing header, tabs, tab content */}
      </div>
      {/* AI Guide panel — persistent right hand */}
      <div className="w-80 hidden lg:block shrink-0">
        <AIGuidePanel activeView={activeTab} />
      </div>
    </div>
  </div>
);
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Keyword `INTENT_MAP` in `router.py` | LLM structured output intent parser | Phase 3 | Handles natural language variation; extracts parameters |
| `search_entries()` keyword-only on index records | Hybrid keyword + vector semantic search | Phase 3 | Finds conceptually related entries without exact word matches |
| Command input in "cmd" tab only | Persistent Command Bar in AI Guide panel | Phase 3 | Always accessible; no tab switch needed |
| Per-entry Q&A only in detail modal | Reused `EntryAIPanel` + new AI Guide chat | Phase 3 | Consistent Q&A experience across entry and general queries |

**Deprecated/outdated:**
- `INTENT_MAP` keyword matching: Will be kept as a fallback inside `parse_intent()` for offline/low-confidence scenarios, but new commands should not add to it.
- `CommandInput.tsx` in the "cmd" tab: Replaced by `CommandBar.tsx` in the AI Guide panel. The old component can be removed in Phase 4.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Gemini embedding API (`gemini-embedding-001`) supports both `RETRIEVAL_DOCUMENT` and `RETRIEVAL_QUERY` task types | Standard Stack | If task types are not supported, vector search quality degrades; query embeddings may not match document embeddings well |
| A2 | pgvector HNSW index with `m=16, ef_construction=64` is sufficient for personal-scale library (<10K entries) | Architecture Patterns | If index params are wrong, search quality or build time may suffer; tuneable later |
| A3 | The dashboard's existing `EntryAIPanel` component can be reused for per-entry Q&A without structural changes | What Exists | If the component needs changes, estimate increases; but the interface is clean and well-isolated |
| A4 | `SIGNAL_OWNER_ID` from Firebase token email is a stable tenant identifier | Pitfall 4 | If owner switches Firebase accounts, the owner_id changes and vector embeddings become orphaned |
| A5 | No new npm/Python packages are needed for this phase | Standard Stack | If a package is discovered missing during implementation, it can be added in-wave without blocking |

## Open Questions

**RESOLVED** — All questions below were resolved during planning and are reflected in the PLAN.md files.

1. **Should vector search support filtering by section/tag before or after the vector query?**
   - What we know: pgvector supports `WHERE` clauses before `ORDER BY` distance. Filtering by section in SQL is efficient.
   - What's unclear: Whether the frontend needs section-filtered conceptual search, or if global conceptual search is sufficient.
   - **RESOLVED:** Start with global vector search (no section filter). Add section-filtered vector search if LIB-02 user testing shows it's needed. See `03-02-PLAN.md` Task 1.

2. **How should the AI Guide panel handle the transition to the Zen shell (Phase 4)?**
   - What we know: Phase 4 will lock the AI Guide into Panel B of a 70/30 split-screen.
   - What's unclear: Whether to build the panel as position-agnostic now (so it works both standalone and locked), or to build for standalone and refactor in Phase 4.
   - **RESOLVED:** Build `AIGuidePanel` as a self-contained component with no positioning logic. `DashboardPage` decides where to render it. Phase 4 will simply move the render location. See `03-04-PLAN.md` Task 3.

3. **What processed-noise metrics should the status banner show?**
   - What we know: GUIDE-03 asks for "reassuring processed-noise metrics (e.g. 'processed N items for you')".
   - What's unclear: Which metrics are available now vs. need new instrumentation.
   - **RESOLVED:** Start with library entry count, recent captures (last 24h), and command count. These are all queryable from existing data. Add feed/draft metrics in later phases when those pipelines exist. See `03-03-PLAN.md` Task 3 (`GET /guide/status`).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend runtime | ✓ | 3.14.5 | — |
| Postgres + pgvector | Vector DB | ✗ (not running) | — | Docker Compose in `docker-compose.n8n.yml` starts it |
| Gemini API | Embeddings + intent parsing | ✓ (env key) | — | Kimi fallback configured in dispatcher |
| Firebase Auth | Authentication | ✓ | Admin SDK 7.4+ | — |
| Docker | Container runtime | ✓ | 29.4.0 | — |
| Node.js/Bun | Dashboard build | ✓ | — | — |
| React | Dashboard UI | ✓ | 19.2.6 | — |

**Missing dependencies with no fallback:**
- Postgres + pgvector must be running for vector search to work. The `docker-compose.n8n.yml` in the parent repo defines the service. The planner must include a "start postgres" step in Wave 0.

**Missing dependencies with fallback:**
- None identified.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` |
| Config file | None — see Wave 0 |
| Quick run command | `python -m unittest tests.test_vector_search tests.test_intent_parser -v` |
| Full suite command | `python -m unittest discover tests -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LIB-01 | Archive article/note/document into library | integration | `python -m unittest tests.test_library_api -v` | ✅ existing |
| LIB-02 | Plain-text conceptual search returns semantically related entries | unit + integration | `python -m unittest tests.test_vector_search -v` | ❌ Wave 0 |
| LIB-03 | Recent Spark Cards show most recent inputs | unit | `python -m unittest tests.test_library_api -v` | ✅ (needs new test) |
| LIB-05 | Per-entry AI Q&A answers questions | integration | `python -m unittest tests.test_library_api -v` | ✅ existing (`test_synthesize_entry_not_found`) |
| GUIDE-01 | Persistent AI Guide panel present | e2e / manual | Browser verification | ❌ Wave 0 |
| GUIDE-02 | Natural-language Command Bar executes via LLM intent | unit + integration | `python -m unittest tests.test_intent_parser -v` | ❌ Wave 0 |
| GUIDE-03 | Status banner shows processed-noise metrics | unit | `python -m unittest tests.test_guide_api -v` | ❌ Wave 0 |
| GUIDE-05 | "Park a Distraction" captures stray thought | integration | `python -m unittest tests.test_guide_api -v` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m unittest tests.test_vector_search tests.test_intent_parser -v`
- **Per wave merge:** `python -m unittest discover tests -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_vector_search.py` — covers LIB-02 (vector search contract)
- [ ] `tests/test_intent_parser.py` — covers GUIDE-02 (LLM intent parsing)
- [ ] `tests/test_guide_api.py` — covers GUIDE-01, GUIDE-03, GUIDE-05 (guide endpoints)
- [ ] Dashboard: `src/components/guide/` directory with test stubs

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Firebase ID token verification via `require_auth` dependency |
| V3 Session Management | yes | Firebase session cookies (`__session`, httpOnly, Secure, SameSite=Strict) |
| V4 Access Control | yes | `ALLOWED_USER_EMAIL` check in `verify_id_token`; owner_id scoping on all DB rows |
| V5 Input Validation | yes | FastAPI request models; LLM output JSON schema validation |
| V6 Cryptography | no | No custom crypto; Firebase handles token signing |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection in vector search | Tampering | Parameterized queries via psycopg (already used in cache.py) |
| Prompt injection in intent parser | Spoofing | System prompt hardcodes allowed intents; params are validated before dispatch |
| Unauthorized vector DB access | Elevation of Privilege | `owner_id` filter on every query; no global SELECT |
| LLM output parsing failure | Denial of Service | Try/except with fallback to keyword map; never crash on malformed JSON |
| Embedding content exposure | Information Disclosure | `owner_id` scoping; no cross-tenant embedding queries |

## Sources

### Primary (HIGH confidence)
- `solo-leveling/src/vector/db.py` — pool lifecycle, migration execution
- `solo-leveling/src/vector/embed.py` — Gemini embedding client, 768-dim, task types
- `solo-leveling/src/vector/cache.py` — cosine distance query pattern, parameterized SQL
- `solo-leveling/src/vector/hooks.py` — `on_entry_saved` hook, upsert pattern
- `solo-leveling/src/vector/migrations/001_init_vector.sql` — schema: `signal_embeddings`, `signal_token_cache`, HNSW indexes
- `solo-leveling/src/core/router.py` — `INTENT_MAP`, `_detect_intent()`, `_dispatch()`
- `solo-leveling/src/core/libraries.py` — `handle_library_command()`, `_capture_entry()`, `_fire_embedding_hook()`
- `solo-leveling/src/core/library_store.py` — `_LibraryStore` ABC, `_FileLibraryStore`, `_UnifiedLibraryStore`
- `solo-leveling/src/api/library.py` — existing REST endpoints, `require_auth` dependency
- `solo-leveling/src/agents/dispatcher.py` — `run_agent()`, Gemini/Kimi providers
- `dashboard/src/components/library/LibraryPage.tsx` — existing folderless library UI
- `dashboard/src/components/library/EntryAIPanel.tsx` — per-entry Q&A with localStorage history
- `dashboard/src/components/library/EntryDetailModal.tsx` — entry detail with tabs (read/edit/ai)
- `dashboard/src/components/dashboard/CommandInput.tsx` — existing command input
- `dashboard/src/components/CommandPalette.tsx` — cmdk-based palette with search
- `dashboard/src/hooks/useApi.ts` — library hooks, synthesize hook
- `dashboard/src/lib/api.ts` — API client functions

### Secondary (MEDIUM confidence)
- `solo-leveling/tests/test_vector_foundation.py` — test patterns for vector modules (mock pool, mock embed)
- `solo-leveling/tests/test_library_api.py` — test patterns for library API (TestClient, mock auth)
- `solo-leveling/tests/test_api_contract.py` — contract test patterns
- `solo-leveling/ARCHITECTURE.md` — system layers and data flows
- `solo-leveling/AI_CONTEXT.md` — current phase priorities and completed stages

### Tertiary (LOW confidence)
- None — all claims verified against codebase.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages already installed and verified in Phase 1
- Architecture: HIGH — codebase read in full; all integration points identified
- Pitfalls: HIGH — derived from actual code patterns (silent hook failures, tenant scoping, state drift)

**Research date:** 2026-05-30
**Valid until:** 2026-06-30 (stable stack, no fast-moving dependencies)
