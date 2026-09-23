# Phase 6: Smart Feeds - Research

**Researched:** 2026-05-31
**Domain:** Feed ingestion, content compression, vector dedup, n8n templates
**Confidence:** HIGH

## Summary

Phase 6 builds on extensively reused assets from prior phases. The YouTube transcript fetch (`youtube.py`), LLM 3-bullet compression pattern (`generate_digest()` in `onboarding.py`), `_SOURCE_FETCHERS` registry, n8n template system (`templates.py` + `executor.py`), vector DB with cosine similarity (`vector/search.py`), and the Context Nest UI (`ContextNest.tsx` + `StreamCard.tsx`) are all production-ready and directly reusable. The primary new work is: (1) a feed compression backend module that extends the digest pattern to YouTube/news/email, (2) an n8n RSS polling workflow template, (3) vector-based news dedup logic, (4) a silent queue with `read` flag on library entries, and (5) dashboard UI extensions for `sources` on dedup cards and unread indicators.

**Primary recommendation:** Build a new `src/core/feeds.py` module that houses `compress_youtube()`, `compress_news()`, and `compress_email()` functions following the `generate_digest()` pattern. Wire it to the Command Bar intent parser and the `_SOURCE_FETCHERS` registry. Add a single n8n RSS template JSON. Extend `StreamCardData` with `sources?:` and `read?:` fields.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| YouTube URL detection + compression | API / Backend | — | Brain receives Command Bar input, fetches transcript, calls LLM, returns card |
| RSS feed polling + compression | n8n (execution) | API / Backend | n8n polls RSS on schedule, brain compresses and stores cards |
| Email compression | API / Backend | — | Brain fetches via Gmail client, compresses via LLM (reuses `inbox_summary()` + LLM pass) |
| News dedup (vector similarity) | Database / Storage | API / Backend | pgvector cosine similarity query determines merge eligibility |
| Silent queue (read flag) | Database / Storage | API / Backend | Library entries with `read: false` flag; flipped on view |
| Context Nest card rendering | Browser / Client | — | Dashboard renders StreamCards with sources and unread indicators |
| Feed URL management | API / Backend | Browser / Client | Command Bar intent parsed by brain; stored in profile/config |

## Standard Stack

### Core (all already installed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `youtube_transcript_api` | [ASSUMED] latest | YouTube transcript fetch | Already in requirements.txt, used by `youtube.py` |
| `httpx` | [ASSUMED] latest | RSS feed fetching + oEmbed | Already in requirements.txt, used by `web_fetch.py` |
| `feedparser` | [ASSUMED] latest | RSS/Atom parsing | Standard Python RSS library; needed for n8n-less RSS fetch fallback |
| `google-genai` | [ASSUMED] latest | Gemini embeddings for dedup | Already in use via `vector/embed.py` |
| `pgvector` (Postgres) | [ASSUMED] | Cosine similarity for dedup | Already provisioned in Phase 1 |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `lucide-react` | [ASSUMED] latest | Icon components for dedup sources UI | Already in use in StreamCard.tsx |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `feedparser` for RSS | n8n RSS node only | n8n is the execution engine (N8N-03), but a Python fallback lets the brain parse RSS when n8n is offline or for the "add feed" validation |
| Separate dedup service | Inline cosine check in `feeds.py` | Inline is simpler for personal-first; scales to separate service later |

**Installation:**
```bash
cd solo-leveling
pip install feedparser
```

**Version verification:** `feedparser` is a mature 15+ year library with 6.0.x as current stable. [ASSUMED]

## Package Legitimacy Audit

> All packages are either already installed or mature/standard. No new exotic dependencies.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| `feedparser` | PyPI | ~20 yrs | millions/mo | github.com/kurtmckee/feedparser | [ASSUMED] | Approved |
| `youtube_transcript_api` | PyPI | ~6 yrs | high | jdepoix/youtube-transcript-api | Already installed | Approved |
| `httpx` | PyPI | ~6 yrs | very high | encode/httpx | Already installed | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*If slopcheck was unavailable at research time, all packages above are tagged `[ASSUMED]`.*

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │              Command Bar (Dashboard)             │
                    │  "paste YouTube URL"  │  "add feed: <url>"      │
                    └──────────┬────────────┴──────────┬──────────────┘
                               │                       │
                               ▼                       ▼
                    ┌──────────────────────────────────────────────────┐
                    │           Brain Core (router.py)                 │
                    │  intent parser → YouTube URL detect / RSS cmd    │
                    └──────────┬───────────────────────┬──────────────┘
                               │                       │
                    ┌──────────▼──────────┐  ┌────────▼───────────────┐
                    │  feeds.py           │  │  profile_store.py      │
                    │  compress_youtube() │  │  save/remove RSS URLs  │
                    │  compress_news()    │  │  in profile config     │
                    │  compress_email()   │  └────────────────────────┘
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
    ┌─────────────┐  ┌──────────────┐  ┌───────────────┐
    │ youtube.py  │  │ gmail/client │  │ feedparser    │
    │ fetch_      │  │ list_unread()│  │ RSS parse     │
    │ transcript()│  │ inbox_summary│  │               │
    └──────┬──────┘  └──────┬───────┘  └───────┬───────┘
           │                │                   │
           └────────────────┼───────────────────┘
                            ▼
                    ┌──────────────────┐
                    │   LLM (Gemini)   │
                    │  3-bullet compress│
                    └──────────┬───────┘
                               │
                    ┌──────────▼──────────┐
                    │  Vector Dedup       │
                    │  cosine similarity  │
                    │  merge or create    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Library Store      │
                    │  save_entry() with  │
                    │  read: false flag   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Context Nest (UI)  │
                    │  StreamCard +       │
                    │  sources + unread   │
                    └─────────────────────┘

    n8n Layer (parallel path for RSS polling):
    ┌──────────────────────────────────────────────────┐
    │  n8n RSS Poll Workflow (scheduled trigger)        │
    │  → fetch RSS → POST /feeds/ingest-rss to brain   │
    │  → brain compresses + dedupes + stores            │
    └──────────────────────────────────────────────────┘
```

### Recommended Project Structure
```
solo-leveling/src/
├── core/
│   ├── feeds.py              # NEW: compress_youtube(), compress_news(), compress_email()
│   └── onboarding.py         # EXTEND: add youtube + rss to _SOURCE_FETCHERS
├── api/
│   ├── feeds.py              # NEW: /feeds/youtube, /feeds/rss, /feeds/manage
│   └── library.py            # EXTEND: /library/recent with read flag filter
├── n8n/
│   └── templates/
│       ├── gmail_read_summary.json   # existing
│       └── rss_poll_compress.json    # NEW: RSS polling workflow template
└── integrations/
    └── youtube.py            # EXISTING: no changes needed

dashboard/src/components/zen/
├── types.ts                  # EXTEND: add sources?, read? to StreamCardData
├── StreamCard.tsx            # EXTEND: sources expandable, unread indicator
├── ContextNest.tsx           # EXTEND: pull from feed queue (read:false entries)
└── FeedSources.tsx           # NEW: expandable sources sub-component for dedup cards
```

### Pattern 1: Feed Compression (extending generate_digest pattern)
**What:** LLM compresses raw content into exactly 3 bullets, following the `generate_digest()` pattern in `onboarding.py`.
**When to use:** Every feed type (YouTube, news, email) goes through the same compression pipeline.
**Example:**
```python
# Source: solo-leveling/src/core/onboarding.py (existing pattern, adapted)
_YOUTUBE_COMPRESS_PROMPT = """You are a content compressor for a personal command center.
Given a YouTube video transcript, summarize it into exactly 3 concise, actionable bullet points.

Respond with valid JSON only. No markdown, no explanations, no code blocks.

Format:
{
  "bullets": ["bullet 1", "bullet 2", "bullet 3"],
  "watch_minutes": 12,
  "read_seconds": 15
}

Rules:
- Exactly 3 bullets, no more, no fewer
- Each bullet is one sentence, under 100 characters
- watch_minutes: estimated video duration from transcript length
- read_seconds: estimated time to read the 3 bullets (~3 seconds per bullet)
"""

def compress_youtube(url: str) -> dict[str, Any] | None:
    """Compress a YouTube video into a 3-bullet takeaway card."""
    video_id = extract_video_id(url)
    if not video_id:
        return None
    transcript = fetch_transcript(video_id)
    if not transcript:
        # Fallback: use oEmbed metadata only
        metadata = fetch_url_metadata(url)
        return _compress_from_metadata(metadata)

    metadata = fetch_url_metadata(url)
    truncated = transcript[:4000]
    response = run_agent(
        task=f"Compress this transcript:\n{truncated}",
        context=f"Title: {metadata.get('title', '')}\nAuthor: {metadata.get('author', '')}",
        system=_YOUTUBE_COMPRESS_PROMPT,
    )
    parsed = json.loads(_strip_fences(response))
    bullets = list(parsed.get("bullets", []))[:3]
    # ... clamp to 3 bullets, compute read_seconds
    return {
        "bullets": bullets,
        "kind": "library",
        "source": "YouTube",
        "source_url": url,
        "watch_minutes": parsed.get("watch_minutes", 0),
        "read_seconds": parsed.get("read_seconds", 9),
        "thumbnail_url": metadata.get("extra", {}).get("thumbnail_url"),
    }
```

### Pattern 2: News Dedup via Vector Similarity
**What:** When a new article arrives, embed its summary and query pgvector for similar existing cards. If cosine distance < threshold, merge sources into existing card instead of creating new one.
**When to use:** Every RSS news item processed by the feed pipeline.
**Example:**
```python
# Source: solo-leveling/src/vector/search.py (existing pattern, adapted)
from src.vector.db import get_pool
from src.vector.embed import embed_text

_DEDUP_THRESHOLD = 0.85  # cosine similarity threshold (Claude's discretion)

async def find_dedup_candidate(summary_text: str, owner_id: str) -> dict[str, Any] | None:
    """Find an existing news card that matches this summary closely enough to merge."""
    vec = embed_text(summary_text, task_type="RETRIEVAL_QUERY")
    async with get_pool().connection() as conn:
        rows = await conn.fetchall(
            """
            SELECT entry_id, 1 - (embedding <=> %s::vector) AS similarity
            FROM signal_embeddings
            WHERE owner_id = %s AND section = 'news'
            ORDER BY embedding <=> %s::vector
            LIMIT 1
            """,
            (vec, owner_id, vec),
        )
    if rows and float(rows[0]["similarity"]) >= _DEDUP_THRESHOLD:
        return {"entry_id": rows[0]["entry_id"], "similarity": rows[0]["similarity"]}
    return None
```

### Pattern 3: Silent Queue with read Flag
**What:** Library entries get a `read: false` frontmatter field. The Context Nest queries entries with `read: false` and shows them as "new." When the owner views a card, the flag flips to `true`.
**When to use:** All feed-sourced entries (YouTube, news, email).
**Example:**
```python
# In library_store.py save_entry() — add read field to frontmatter
content = (
    f"---\n"
    f"title: {title}\n"
    f"section: {section}\n"
    f"status: {status}\n"
    f"read: false\n"       # NEW: silent queue flag
    f"tags: [{metadata_tags}]\n"
    f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
    f"{source_url_line}"
    f"---\n\n"
    f"{body}\n"
)
```

### Anti-Patterns to Avoid
- **Custom RSS parser:** Use `feedparser` — RSS/Atom has dozens of edge cases (CDATA, namespaces, enclosures) that a hand-rolled parser will miss.
- **Pushing new content to the owner:** FEED-04 explicitly forbids push alerts. Content must queue silently and only surface when the owner opens Signal.
- **Separate "feeds" table:** Reuse the existing library store with `section: "news"` or `section: "feed"`. The library is already the unified store.
- **Blocking on transcript fetch:** YouTube transcript fetch can fail (private video, disabled captions). Always have a fallback to oEmbed metadata + title-only card.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RSS/Atom parsing | Custom XML parser | `feedparser` library | RSS has 20+ edge cases (Atom, RSS 1.0/2.0, Dublin Core, enclosures) |
| YouTube transcript fetch | Direct YouTube API | `youtube_transcript_api` (already installed) | Handles auto-captions, language fallback, rate limits |
| Content embedding | Custom embedding model | `embed_text()` from `vector/embed.py` | Gemini embeddings already provisioned, 768-dim |
| Cosine similarity search | Manual vector math | pgvector `<=>` operator via `vector/db.py` | Index-optimized, already working in Phase 1 |
| LLM 3-bullet compression | Custom prompt per feed type | `run_agent()` with structured prompt (extend `generate_digest` pattern) | Consistent output format, code fence stripping, fallback handling |
| n8n workflow triggering | Direct HTTP to n8n | `execute_intent()` from `n8n/executor.py` | Already handles credential sync, error classification, retry |

**Key insight:** Almost everything needed for Phase 6 is already built. The phase is primarily about wiring existing components together with a thin new `feeds.py` module and one n8n template.

## Common Pitfalls

### Pitfall 1: YouTube transcript failure silently breaks the card
**What goes wrong:** `fetch_transcript()` returns `None` for private videos, disabled captions, or region-blocked content. If the code assumes a transcript always exists, the card never appears.
**Why it happens:** Many YouTube videos have auto-captions disabled or are members-only.
**How to avoid:** Always check for `None` and fall back to oEmbed metadata (title + author + thumbnail). The card can show "Transcript unavailable — title-only summary" as the third bullet.
**Warning signs:** Unit tests only test with videos that have transcripts.

### Pitfall 2: RSS feed URL validation missing
**What goes wrong:** Owner pastes a non-RSS URL as a feed (e.g., `https://techcrunch.com` instead of `https://techcrunch.com/feed`). The n8n workflow silently fails or the feedparser throws.
**Why it happens:** RSS URLs are not obvious to non-technical users.
**How to avoid:** Validate the URL by fetching it with `feedparser.parse()` before saving. Return a clear error if it's not valid RSS/Atom.
**Warning signs:** "add feed" succeeds but no cards ever appear.

### Pitfall 3: Dedup threshold too aggressive or too lenient
**What goes wrong:** Threshold too low (e.g., 0.7) merges unrelated articles. Threshold too high (0.95) never deduplicates.
**Why it happens:** Cosine similarity for news headlines is naturally lower than for full documents because headlines are short.
**How to avoid:** Start with 0.85 threshold. Log similarity scores during development. Make it a config parameter (Claude's discretion). Consider embedding the headline + first paragraph rather than just the headline.
**Warning signs:** Dedup cards merge Apple earnings with Apple product launches.

### Pitfall 4: read flag not flipped on view
**What goes wrong:** Cards stay permanently marked as "new" because the `read: true` update never fires.
**Why it happens:** The Context Nest renders cards but doesn't call an API to mark them as read.
**How to avoid:** Add a `PATCH /library/entries/{id}` call when a card is first rendered in the Context Nest (or when the owner clicks/selects it). Use a debounce to avoid hammering the API on scroll.
**Warning signs:** Every card always has the unread indicator.

### Pitfall 5: n8n RSS template missing credential sync
**What goes wrong:** The RSS polling workflow triggers but can't access the feed URLs because they're stored in the brain's profile, not in n8n's credential store.
**Why it happens:** RSS feeds are URLs, not OAuth tokens — the credential sync pattern (N8N-02) doesn't apply directly.
**How to avoid:** Pass feed URLs as workflow parameters (not credentials). The n8n template should accept `feed_urls` as an array parameter. The brain fills this from `profile['rss_feeds']` using `fill_parameters()`.
**Warning signs:** n8n workflow runs successfully but processes zero items.

### Pitfall 6: Email compression duplicates existing inbox_summary()
**What goes wrong:** Building a separate email compression path that fetches the same messages as `inbox_summary()` but with different formatting.
**Why it happens:** `inbox_summary()` returns plain text; Phase 6 needs 3-bullet cards.
**How to avoid:** Reuse `list_unread()` from `gmail/client.py` to fetch messages, then pass them through the LLM compression prompt (same as `generate_digest()` but with the email-specific prompt). Do not re-implement the Gmail fetch.
**Warning signs:** Two different code paths fetching Gmail with slightly different queries.

## Code Examples

### YouTube → 3-Bullet Card (full flow)
```python
# Source: adapted from onboarding.py generate_digest() + youtube.py + web_fetch.py
from src.integrations.youtube import extract_video_id, fetch_transcript
from src.integrations.web_fetch import fetch_url_metadata
from src.agents.dispatcher import run_agent
import json

def compress_youtube(url: str) -> dict[str, Any] | None:
    """Compress a YouTube URL into a 3-bullet takeaway card with reading-time metrics."""
    video_id = extract_video_id(url)
    if not video_id:
        return None

    # Fetch transcript (may be None)
    transcript = fetch_transcript(video_id)
    # Fetch metadata (title, author, thumbnail via oEmbed)
    metadata = fetch_url_metadata(url)

    if transcript:
        truncated = transcript[:4000]
        response = run_agent(
            task=f"Compress this video transcript into 3 bullets:\n{truncated}",
            context=f"Title: {metadata.get('title', '')}",
            system=_YOUTUBE_COMPRESS_PROMPT,
        )
        parsed = json.loads(_strip_fences(response))
    else:
        # Fallback: compress from title + description only
        parsed = {"bullets": [
            f"Video: {metadata.get('title', 'Unknown')}",
            f"By: {metadata.get('author', 'Unknown')}",
            "Transcript unavailable — open to watch.",
        ], "watch_minutes": 0, "read_seconds": 9}

    bullets = list(parsed.get("bullets", []))[:3]
    while len(bullets) < 3:
        bullets.append("...")
    watch_min = parsed.get("watch_minutes", 0)
    read_sec = len(bullets) * 3  # ~3 seconds per bullet
    return {
        "bullets": bullets,
        "kind": "library",
        "source": "YouTube",
        "source_url": url,
        "watch_minutes": watch_min,
        "read_seconds": read_sec,
        "thumbnail_url": metadata.get("extra", {}).get("thumbnail_url"),
    }
```

### RSS Feed Template JSON (n8n)
```json
{
  "id": "rss_poll_compress",
  "name": "RSS Feed Poll & Compress",
  "description": "Poll configured RSS feeds, compress new items into 3-bullet cards",
  "integration": null,
  "n8n_workflow_id": 0,
  "keywords": ["rss", "feed", "news", "poll", "subscribe"],
  "side_effecting": false,
  "parameter_schema": {
    "feed_urls": {
      "type": "array",
      "description": "List of RSS feed URLs to poll",
      "default": []
    },
    "max_items_per_feed": {
      "type": "integer",
      "description": "Max items to process per feed per poll",
      "default": 5
    }
  }
}
```

### StreamCardData Extension (TypeScript)
```typescript
// Source: dashboard/src/components/zen/types.ts
export interface StreamCardData {
  id: string;
  source: string;
  timeLabel: string;
  bullets: [string, string, string];
  kind?: "email" | "news" | "library" | "generic";
  // NEW for Phase 6:
  sources?: { title: string; url: string }[];  // dedup expandable source list
  read?: boolean;                               // silent queue flag (default true for existing)
  watchMinutes?: number;                        // YouTube watch time
  readSeconds?: number;                         // bullet reading time
  thumbnailUrl?: string;                        // YouTube thumbnail
}
```

### ContextNest Feed Queue Integration
```typescript
// Source: dashboard/src/components/zen/ContextNest.tsx (extension)
// Add feed queue entries (read: false) alongside library recent
useEffect(() => {
  Promise.all([
    fetchLibraryRecent(4),
    fetchFeedQueue(),  // NEW: GET /feeds/queue returns entries with read: false
  ]).then(([libRes, feedRes]) => {
    const libCards = (libRes.entries ?? []).slice(0, 4).map(entryToCard);
    const feedCards = (feedRes.entries ?? []).slice(0, 6).map(feedEntryToCard);
    setLibraryCards([...feedCards, ...libCards]);
  }).catch(() => setLibraryCards([]));
}, []);
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `inbox_summary()` plain text | LLM 3-bullet compression | Phase 6 (new) | Structured cards instead of plain text |
| Manual library entries | Auto-ingested feed cards | Phase 6 (new) | Zero-effort content capture |
| No dedup | Vector similarity merge | Phase 6 (new) | One card per news event, not 5 duplicates |
| All content treated equal | Silent queue with read flag | Phase 6 (new) | Content waits for the owner, not vice versa |

**Deprecated/outdated:**
- None — Phase 6 extends, not replaces, existing patterns.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `feedparser` package name and API | Standard Stack | Low — it is the de facto Python RSS library, but not verified against PyPI in this session |
| A2 | `_DEDUP_THRESHOLD = 0.85` is a good starting point | Architecture / Pattern 2 | Medium — may need tuning; marked as Claude's discretion |
| A3 | YouTube video duration can be estimated from transcript snippet count | Code Examples | Low — transcript snippets have timing data in the API response |
| A4 | RSS polling interval (e.g., 1 hour) | Claude's Discretion | Low — tunable, no hard dependency |
| A5 | `read` field can be added to library entry frontmatter without breaking existing reads | Architecture / Pattern 3 | Low — frontmatter is parsed with regex; unknown fields are ignored |

## Open Questions

1. **How does the n8n RSS workflow call back to the brain?**
   - What we know: Phase 2 built webhook callback ingestion (`N8N-04`). The n8n workflow can POST results to a brain endpoint.
   - What's unclear: The exact webhook URL and payload format for the RSS compress callback.
   - Recommendation: Reuse the existing `/n8n/callback` endpoint pattern from Phase 2. The RSS workflow POSTs compressed items back; the brain stores them.

2. **Should email compression run on a schedule or on-demand?**
   - What we know: FEED-02 says "email streams compress into Context Nest cards." FEED-04 says no push alerts.
   - What's unclear: Whether email cards appear on a timer (like RSS) or only when the owner opens Signal.
   - Recommendation: On-demand — when the owner opens Signal, the brain fetches recent unread and compresses. No background polling for email (RSS gets the scheduled path).

3. **What section name for feed entries in the library?**
   - What we know: Existing sections are `profile`, `term`, `book`, `article`, `thought`, `reference`, `research`.
   - What's unclear: Whether to use `news`, `feed`, or reuse `article`.
   - Recommendation: Use `news` for RSS items and `article` for YouTube (since it's knowledge content). This lets the Context Nest filter by section.

## Environment Availability

> All dependencies are internal to the existing codebase. No external tools needed beyond what Phase 1-5 already provisioned.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.13 | All backend | ✓ | 3.13 | — |
| PostgreSQL + pgvector | Vector dedup | ✓ | Phase 1 provisioned | Skip dedup, create plain cards |
| Gemini API key | Embeddings + LLM | ✓ | Phase 1 provisioned | — |
| n8n instance | RSS polling workflow | [ASSUMED] ✓ | Phase 2 provisioned | Poll RSS directly from brain (fallback) |
| Node.js + npm | Dashboard build | ✓ | — | — |

**Missing dependencies with no fallback:** none identified
**Missing dependencies with fallback:** n8n (brain can poll RSS directly if n8n is unavailable)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `unittest` (stdlib) |
| Config file | `tests/` directory |
| Quick run command | `python -m unittest tests.test_feeds -v` |
| Full suite command | `python -m unittest discover tests -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FEED-01 | YouTube URL → 3-bullet card | unit | `python -m unittest tests.test_feeds::test_compress_youtube -v` | Wave 0 |
| FEED-02 | Email/news → compressed cards | unit | `python -m unittest tests.test_feeds::test_compress_email -v` | Wave 0 |
| FEED-03 | News dedup via vector similarity | unit | `python -m unittest tests.test_feeds::test_dedup_merge -v` | Wave 0 |
| FEED-04 | Silent queue, no push alerts | integration | `python -m unittest tests.test_feeds::test_silent_queue -v` | Wave 0 |
| N8N-03 | n8n RSS template exists + matches | unit | `python -m unittest tests.test_feeds::test_rss_template -v` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m unittest tests.test_feeds -v`
- **Per wave merge:** `python -m unittest discover tests -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_feeds.py` — covers FEED-01, FEED-02, FEED-03, FEED-04, N8N-03
- [ ] `tests/conftest.py` — shared fixtures (mock transcript, mock RSS feed)
- [ ] `feedparser` install: `pip install feedparser`

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Firebase auth (existing `require_auth` dependency) |
| V3 Session Management | no | — |
| V4 Access Control | yes | Owner-scoped entries (`owner_id` on embeddings) |
| V5 Input Validation | yes | RSS URL validation, YouTube URL validation (already in `extract_video_id`) |
| V6 Cryptography | no | — |

### Known Threat Patterns for Feed Ingestion

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SSRF via RSS feed URL | Information Disclosure | Validate RSS URL scheme (https only), resolve DNS, block internal IPs |
| Malicious RSS content (XSS in titles) | Tampering | Sanitize all RSS content before storage; render as plain text in cards |
| LLM prompt injection via RSS content | Tampering | Truncate content to 4000 chars before LLM; system prompt constrains output format |
| Transcript API rate limiting | Denial of Service | Cache transcripts; don't re-fetch for same video_id within 24h |

## Sources

### Primary (HIGH confidence)
- `solo-leveling/src/core/onboarding.py` — `generate_digest()` pattern, `_SOURCE_FETCHERS` registry, `_query_connected_sources()`
- `solo-leveling/src/integrations/youtube.py` — `extract_video_id()`, `fetch_transcript()`
- `solo-leveling/src/vector/search.py` — `search_library()` with cosine similarity via pgvector
- `solo-leveling/src/vector/embed.py` — `embed_text()` with Gemini, 768-dim
- `solo-leveling/src/n8n/templates.py` — `match_template()`, `fill_parameters()`, template loading
- `solo-leveling/src/n8n/executor.py` — `execute_intent()`, credential sync, retry logic
- `solo-leveling/src/n8n/templates/gmail_read_summary.json` — n8n template JSON pattern
- `dashboard/src/components/zen/ContextNest.tsx` — Context Nest component
- `dashboard/src/components/zen/StreamCard.tsx` — StreamCard rendering with kind-based icons
- `dashboard/src/components/zen/types.ts` — `StreamCardData` type definition
- `solo-leveling/src/core/library_store.py` — `save_entry()`, frontmatter format, `_FileLibraryStore`

### Secondary (MEDIUM confidence)
- `feedparser` library — standard Python RSS parser [ASSUMED — not verified via PyPI in this session]

### Tertiary (LOW confidence)
- None — all findings grounded in codebase inspection

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — all core libraries already in codebase, only `feedparser` is new
- Architecture: HIGH — patterns directly observable in existing code
- Pitfalls: HIGH — derived from code inspection and known integration failure modes

**Research date:** 2026-05-31
**Valid until:** 2026-06-30 (stable — builds on completed Phase 1-5 infrastructure)
