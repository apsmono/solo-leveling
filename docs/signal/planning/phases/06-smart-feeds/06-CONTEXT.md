# Phase 6: Smart Feeds - Context

**Gathered:** 2026-05-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Compress real streams into Context Nest 3-bullet cards using n8n template pipelines and the reused YouTube transcript fetch + Gmail summary building blocks. A YouTube link pasted in the Command Bar becomes a 3-bullet takeaway card with watch-vs-read time metrics; RSS news feeds are polled by n8n on a schedule and compressed into cards; the vector layer collates duplicate news events into a single situational card; and new content queues silently (no push alerts) until the owner opens Signal.

**In scope (FEED-01, FEED-02, FEED-03, FEED-04, N8N-03):**
- **FEED-01** — YouTube link → 3-bullet takeaway card with reading-time metrics (reuses transcript fetch)
- **FEED-02** — Email and news streams compress into Context Nest cards
- **FEED-03** — News deduplication via vector layer — collates matching events into single situational card
- **FEED-04** — No push alerts — new content queues silently until owner opens Signal
- **N8N-03** — Pre-built n8n workflow templates power the feed/dedup pipelines

**Explicitly NOT in this phase:**
- Smart Drafts / reply generation → Phase 7
- Routine Planner / reading schedule UI → Phase 8
- Safety/Recovery (Panic Button, Reset) → Phase 9
- News API / topic-based news (deferred — RSS only for v1)
- YouTube subscription auto-monitoring (deferred — manual paste only for v1)

</domain>

<decisions>
## Implementation Decisions

### YouTube → 3-Bullet Flow (FEED-01)
- **D-01:** Trigger: **Command Bar paste** — owner pastes a YouTube URL in the Command Bar. The intent parser detects it as a YouTube link, fetches the transcript, compresses to 3 bullets via LLM, and returns a StreamCard.
- **D-02:** Reading-time metrics: **"X min watch → Y sec read"** — estimated video duration compared to bullet reading time. Reinforces the "compressed signal" value prop.
- **D-03:** Card destination: **both Guide response AND Context Nest** — the card appears inline in the Guide (Panel B) as a response AND is auto-added to the Context Nest (Panel A) as a stream card.
- **D-04:** Library persistence: **auto-save to Knowledge Library** — the 3 bullets + metadata are saved as a new library entry. Enables conceptual search and later retrieval.

### News Source & Ingestion (FEED-02, N8N-03)
- **D-05:** News source type: **RSS feeds only** for v1. Owner configures specific RSS feed URLs (e.g., TechCrunch, Hacker News, industry blogs). No topic-based news API.
- **D-06:** Ingestion mechanism: **n8n polls on schedule** — an n8n workflow polls configured RSS feeds periodically (e.g., every hour), compresses new items into 3-bullet cards, and pushes them to the brain. Matches the "n8n is the execution engine" mandate (N8N-03).
- **D-07:** Feed management: **Command Bar** — owner adds/removes RSS feed URLs via the Command Bar (e.g., "add feed: https://techcrunch.com/feed"). Brain stores them in profile/config. n8n reads from there.

### Reading Routines & Silent Queue (FEED-04)
- **D-08:** Queue behavior: **manual "show me new" on open** — content accumulates silently; the owner sees new items when they open Signal. No time-based scheduling, no push alerts.
- **D-09:** New-vs-seen indicator: **subtle visual indicator** — new cards get a subtle accent border or dot indicator. Once the owner has seen them, the indicator fades. No explicit "mark as read" action.
- **D-10:** Queue storage: **library entries with read flag** — queued items are stored as library entries with a `read: false` flag. When viewed, the flag flips to `true`. Reuses the existing library store.

### News Dedup (FEED-03)
- **D-11:** Card format: **synthesized summary + expandable sources** — a single synthesized summary bullet (e.g., "Multiple sources report OpenAI raised $X"). Below it, an expandable source list showing original titles.
- **D-12:** Merge detection: **vector similarity** — when a new article's embedding is within a cosine similarity threshold of an existing card, merge it into that card. Uses the Phase 1 vector DB.
- **D-13:** Card kind: **reuse `kind: "news"`** — dedup cards are the same kind as regular news cards. The `StreamCardData` type gets an optional `sources` array for the expandable source list.

### Claude's Discretion
- Exact RSS polling interval (e.g., 30 min vs. 1 hour)
- Vector similarity threshold for dedup (tunable parameter)
- Subtle indicator style for new/unread cards (accent border vs. dot vs. badge)
- Expandable sources UI pattern (accordion vs. tooltip vs. modal)
- n8n RSS workflow template JSON structure
- How YouTube video duration is estimated (from metadata or transcript length)
- Error handling when transcript fetch fails (fallback to title + description?)
- Whether email compression reuses the existing `inbox_summary()` or needs a new LLM compression pass

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project-level context
- `.planning/PROJECT.md` — Signal product context, personal-first constraint
- `.planning/REQUIREMENTS.md` — REQ-IDs FEED-01, FEED-02, FEED-03, FEED-04, N8N-03
- `.planning/ROADMAP.md` — Phase 6 goal, success criteria, dependencies

### Phase 4 — Zen shell & Context Nest (authoritative)
- `.planning/phases/04-zen-shell/04-CONTEXT.md` — Context Nest pattern, StreamCardData type, Clarity Board views
- `dashboard/src/components/zen/ContextNest.tsx` — Context Nest component (receives feed cards)
- `dashboard/src/components/zen/StreamCard.tsx` — StreamCard rendering (3 bullets, kind icon, actions)
- `dashboard/src/components/zen/types.ts` — `StreamCardData` type definition (extend with `sources?`)

### Phase 5 — Onboarding & digest (authoritative)
- `.planning/phases/05-onboarding-instant-win/05-CONTEXT.md` — digest generation pattern, `_query_connected_sources` registry
- `solo-leveling/src/core/onboarding.py` — `generate_digest()`, `_SOURCE_FETCHERS` registry, `_query_connected_sources()`
- `solo-leveling/src/api/onboarding.py` — digest endpoint pattern (reuse for feed compression)

### Phase 2 — n8n execution layer (authoritative)
- `solo-leveling/src/n8n/executor.py` — `execute_intent()`, template matching, credential sync
- `solo-leveling/src/n8n/templates.py` — `match_template()`, `fill_parameters()`, template loading
- `solo-leveling/src/n8n/templates/gmail_read_summary.json` — existing n8n template (pattern for RSS template)

### Phase 1 — Vector DB foundation
- `.planning/phases/01-data-auth-foundation/` — pgvector embeddings, cosine similarity search

### YouTube integration
- `solo-leveling/src/integrations/youtube.py` — `extract_video_id()`, `fetch_transcript()`
- `solo-leveling/src/integrations/web_fetch.py` — `fetch_url_metadata()`, platform detection

### Gmail integration
- `solo-leveling/src/integrations/gmail/client.py` — `list_unread()`, `search_messages()`, `inbox_summary()`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ContextNest.tsx` — renders StreamCards from library entries; extend to pull from feed queue
- `StreamCard.tsx` — 3-bullet card with kind-based icons (email/news/library/generic); extend with `sources` for dedup cards
- `StreamCardData` type — add optional `sources?: {title: string; url: string}[]` for dedup expandable list
- `generate_digest()` in `onboarding.py` — LLM-based 3-bullet compression; reuse pattern for YouTube/news compression
- `_SOURCE_FETCHERS` registry in `onboarding.py` — add `youtube` and `rss` fetchers
- `_query_connected_sources()` in `onboarding.py` — dispatches to registered fetchers; extend for feed ingestion
- `fetch_transcript()` in `youtube.py` — YouTube transcript fetch; directly reusable
- `extract_video_id()` in `youtube.py` — YouTube URL parsing; directly reusable
- `inbox_summary()` in `gmail/client.py` — email summary; reuse or extend for email feed cards
- `match_template()` in `n8n/templates.py` — keyword-based template matching; add RSS feed template
- `execute_intent()` in `n8n/executor.py` — full n8n execution pipeline; reuse for RSS polling workflow

### Established Patterns
- StreamCard kind-based icon dispatch (`kindIcon` map) — add handling for dedup sources display
- Library entry creation via `/api/v1/library/entries` — reuse for saving YouTube takeaways
- `_SOURCE_FETCHERS` registry pattern — one-line entry per new integration
- n8n template JSON structure (see `gmail_read_summary.json`) — follow same pattern for RSS template
- `run_agent()` for LLM compression — same pattern as `generate_digest()`

### Integration Points
- Command Bar intent parser — needs YouTube URL detection + RSS feed add/remove commands
- Context Nest — needs to pull from feed queue (library entries with `read: false`) in addition to `/library/recent`
- n8n — needs RSS polling workflow template + credential sync for RSS feed URLs
- Library store — needs `read` flag field on entries for queue tracking
- Vector DB — needs cosine similarity query for news dedup merging

</code_context>

<specifics>
## Specific Ideas

- The "X min watch → Y sec read" metric should feel like a small win — "12 min video, you just saved 11 min 45 sec"
- RSS feed management via Command Bar should feel natural: "add feed: techcrunch.com/feed" or "remove feed: TechCrunch"
- The dedup card's expandable sources should be lightweight — a chevron that reveals 2-3 source titles, not a full modal
- Email compression should reuse the existing `inbox_summary()` but add LLM compression to 3 bullets (currently returns plain text summary)
- When the owner opens Signal after being away, the "New since last visit" indicator should be immediately visible but not alarming

</specifics>

<deferred>
## Deferred Ideas

- Topic-based news API (Google News, NewsAPI.org) — future phase when RSS proves insufficient
- YouTube subscription auto-monitoring via n8n — future phase, manual paste only for v1
- Scheduled reading windows (e.g., 9am, 1pm, 6pm digest) — Phase 8 Routine Planner territory
- Push notifications for urgent feeds — explicitly out of scope (FEED-04: no push alerts)
- Feed analytics (most-read sources, reading patterns) — future phase

</deferred>

---

*Phase: 06-smart-feeds*
*Context gathered: 2026-05-31*
