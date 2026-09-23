# Phase 6: Smart Feeds - Pattern Map

**Mapped:** 2026-05-31
**Files analyzed:** 12 (5 new, 7 modified)
**Analogs found:** 10 / 12

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `solo-leveling/src/core/feeds.py` (NEW) | service | transform (LLM compression) | `solo-leveling/src/core/onboarding.py` | exact |
| `solo-leveling/src/api/feeds.py` (NEW) | controller | request-response | `solo-leveling/src/api/onboarding.py` | exact |
| `solo-leveling/src/n8n/templates/rss_poll_compress.json` (NEW) | config | event-driven | `solo-leveling/src/n8n/templates/gmail_read_summary.json` | exact |
| `dashboard/src/components/zen/FeedSources.tsx` (NEW) | component | request-response | `dashboard/src/components/zen/StreamCard.tsx` | role-match |
| `tests/test_feeds.py` (NEW) | test | request-response | `solo-leveling/tests/test_onboarding.py` | exact |
| `solo-leveling/src/core/onboarding.py` (MOD) | service | transform | — | modification |
| `solo-leveling/src/core/library_store.py` (MOD) | store | CRUD | — | modification |
| `solo-leveling/src/api/library.py` (MOD) | controller | CRUD | — | modification |
| `solo-leveling/src/api/v1_router.py` (MOD) | route | request-response | — | modification |
| `dashboard/src/components/zen/types.ts` (MOD) | model | — | — | modification |
| `dashboard/src/components/zen/StreamCard.tsx` (MOD) | component | request-response | — | modification |
| `dashboard/src/components/zen/ContextNest.tsx` (MOD) | component | request-response | — | modification |

## Pattern Assignments

### `solo-leveling/src/core/feeds.py` (service, transform)

**Analog:** `solo-leveling/src/core/onboarding.py`

**Imports pattern** (lines 1-18 of onboarding.py):
```python
"""
Feed compression: YouTube, news, email -> 3-bullet StreamCards.

Follows the generate_digest() pattern from onboarding.py.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)
```

**Core compression pattern** — adapt `generate_digest()` (lines 133-180 of onboarding.py):
```python
# Key pattern: run_agent() with system prompt -> _strip_fences() -> json.loads() -> clamp to 3 bullets
def generate_digest(
    profile: dict[str, Any],
    connected_data: list[dict[str, Any]],
) -> list[str]:
    # ...
    data_context = json.dumps(connected_data, ensure_ascii=False)[:4000]
    response = run_agent(
        task=f"Generate a 24-hour digest from this data:\n{data_context}",
        context=profile_context,
        system=_DIGEST_SYSTEM_PROMPT,
    )
    cleaned = _strip_fences(response)
    parsed = json.loads(cleaned)
    bullets = list(parsed.get("bullets", []))[:3]
    while len(bullets) < 3:
        bullets.append(_FALLBACK[len(bullets)])
    return bullets[:3]
```

**LLM prompt pattern** — follow the `_DIGEST_SYSTEM_PROMPT` structure (lines 20-36 of onboarding.py):
```python
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
```

**Error handling pattern** — graceful fallback (lines 148-180 of onboarding.py):
```python
_FALLBACK = [
    "Your streams are being set up.",
    "Data will appear here once connected sources sync.",
    "Check back in a few minutes.",
]
try:
    # ... LLM call ...
except Exception:
    logger.warning("Digest generation failed", exc_info=True)
    return _FALLBACK
```

**Code fence stripping** — reuse `_strip_fences()` directly (lines 274-283 of onboarding.py):
```python
def _strip_fences(text: str) -> str:
    """Remove markdown code fences from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned
```

**YouTube integration** — use existing `youtube.py` (lines 21-59 of youtube.py):
```python
from src.integrations.youtube import extract_video_id, fetch_transcript
from src.integrations.web_fetch import fetch_url_metadata

# extract_video_id(url) -> Optional[str]  (supports watch/shorts/embed/youtu.be)
# fetch_transcript(video_id) -> Optional[str]  (graceful None on failure)
# fetch_url_metadata(url) -> dict with title, author, platform, extra.thumbnail_url
```

**News dedup pattern** — adapt `search_library()` from `vector/search.py` (lines 66-83):
```python
from src.vector.db import get_pool
from src.vector.embed import embed_text

_DEDUP_THRESHOLD = 0.85

async def find_dedup_candidate(summary_text: str, owner_id: str) -> dict[str, Any] | None:
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

**Library persistence** — use existing `library_store.save_entry()` (lines 177-207 of library_store.py):
```python
from src.core.libraries import _get_store as _get_library_store

store = _get_library_store()
path = store.save_entry(
    section="article",  # or "news" for RSS items
    title=card_title,
    body=card_body,
    status="captured",
    tags=["youtube", "feed"],
    source_url=url,
)
```

---

### `solo-leveling/src/api/feeds.py` (controller, request-response)

**Analog:** `solo-leveling/src/api/onboarding.py`

**Imports pattern** (lines 1-26 of onboarding.py):
```python
"""
Feed REST endpoints.

Provides:
  - POST /feeds/youtube       — compress YouTube URL into 3-bullet card
  - POST /feeds/rss           — ingest RSS item (called by n8n callback)
  - GET  /feeds/queue         — get unread feed entries
  - POST /feeds/manage        — add/remove RSS feed URLs

All endpoints require Firebase authentication.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth

logger = logging.getLogger(__name__)

router = APIRouter()
```

**Endpoint pattern** — POST handler with validation + service call + error handling (lines 31-52 of onboarding.py):
```python
@router.post("/feeds/youtube")
async def compress_youtube_endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Compress a YouTube URL into a 3-bullet takeaway card."""
    url = str(payload.get("url", "")).strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'url' in request payload.",
        )

    try:
        card = compress_youtube(url)
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not process this YouTube URL.",
            )
        return {"status": "ok", "card": card}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to compress YouTube URL")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to compress video. Please try again.",
        ) from None
```

**GET endpoint pattern** (lines 108-123 of onboarding.py):
```python
@router.get("/feeds/queue")
async def feed_queue_endpoint(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Return unread feed entries for the Context Nest."""
    # Query library entries with read: false
    store = _get_library_store()
    entries = store.list_entries(section="news", ...)  # filter for unread
    return {"status": "ok", "entries": entries}
```

**Router registration** — add to `v1_router.py` (line 7 of v1_router.py):
```python
# In src/api/v1_router.py, add 'feeds' to the import and include_router:
from src.api import ..., feeds
router.include_router(feeds.router)
```

---

### `solo-leveling/src/n8n/templates/rss_poll_compress.json` (config, event-driven)

**Analog:** `solo-leveling/src/n8n/templates/gmail_read_summary.json`

**Full template pattern** (entire file, 16 lines):
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

Key differences from `gmail_read_summary.json`:
- `integration: null` (RSS is not an OAuth integration; feed URLs are passed as parameters)
- `side_effecting: false` (read-only polling)
- `keywords` include "rss", "feed", "news", "poll", "subscribe" for intent matching

---

### `dashboard/src/components/zen/FeedSources.tsx` (component, request-response)

**Analog:** `dashboard/src/components/zen/StreamCard.tsx`

**Imports pattern** (lines 1-3 of StreamCard.tsx):
```tsx
import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import type { StreamCardData } from "./types";
```

**Component structure** — follow StreamCard's props pattern (lines 5-9 of StreamCard.tsx):
```tsx
interface FeedSourcesProps {
  sources: { title: string; url: string }[];
}

export function FeedSources({ sources }: FeedSourcesProps) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-1">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs text-muted hover:text-text transition-colors"
      >
        {expanded ? <ChevronDown size={12} /> : <ChevronUp size={12} />}
        {sources.length} source{sources.length !== 1 ? "s" : ""}
      </button>
      {expanded && (
        <ul className="mt-1 space-y-0.5 pl-3">
          {sources.map((src, i) => (
            <li key={i} className="truncate text-xs text-muted">
              <a href={src.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                {src.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

### `tests/test_feeds.py` (test, request-response)

**Analog:** `solo-leveling/tests/test_onboarding.py`

**Test structure** (lines 1-28 of test_onboarding.py):
```python
"""
Tests for Phase 6: Smart Feeds — compression, dedup, and queue endpoints.

Endpoints tested:
- POST /api/v1/feeds/youtube    — YouTube URL -> 3-bullet card
- POST /api/v1/feeds/rss        — RSS item ingestion
- GET  /api/v1/feeds/queue      — unread feed entries
- POST /api/v1/feeds/manage     — add/remove RSS feed URLs

All tests run offline (mocked auth + dependencies).
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class FeedCompressionTests(unittest.TestCase):
    """Unit tests for feed compression functions."""

    def test_compress_youtube_returns_3_bullets(self) -> None:
        """compress_youtube() returns dict with exactly 3 bullets."""
        from src.core.feeds import compress_youtube

        mock_transcript = "This is a test transcript about AI."
        mock_metadata = {"title": "Test Video", "author": "Test", "extra": {"thumbnail_url": ""}}

        with patch("src.core.feeds.fetch_transcript", return_value=mock_transcript), \
             patch("src.core.feeds.fetch_url_metadata", return_value=mock_metadata), \
             patch("src.core.feeds.run_agent", return_value='{"bullets": ["a", "b", "c"], "watch_minutes": 10, "read_seconds": 9}'):
            result = compress_youtube("https://youtube.com/watch?v=abc123")

        self.assertIsNotNone(result)
        self.assertEqual(len(result["bullets"]), 3)
        self.assertEqual(result["kind"], "library")
        self.assertEqual(result["source"], "YouTube")

    def test_compress_youtube_none_on_invalid_url(self) -> None:
        """compress_youtube() returns None for non-YouTube URLs."""
        from src.core.feeds import compress_youtube
        result = compress_youtube("https://example.com")
        self.assertIsNone(result)

    def test_compress_youtube_fallback_on_no_transcript(self) -> None:
        """compress_youtube() falls back to metadata when transcript is None."""
        from src.core.feeds import compress_youtube

        mock_metadata = {"title": "Test Video", "author": "Test", "extra": {"thumbnail_url": ""}}

        with patch("src.core.feeds.fetch_transcript", return_value=None), \
             patch("src.core.feeds.fetch_url_metadata", return_value=mock_metadata):
            result = compress_youtube("https://youtube.com/watch?v=abc123")

        self.assertIsNotNone(result)
        self.assertIn("Transcript unavailable", result["bullets"][2])


class FeedAPITests(unittest.TestCase):
    """Contract tests for feed API endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_youtube_endpoint_returns_card(self, mock_verify: MagicMock) -> None:
        """POST /feeds/youtube with valid URL returns 200 + card."""
        mock_verify.return_value = self.mock_user
        mock_card = {"bullets": ["a", "b", "c"], "kind": "library", "source": "YouTube"}

        with patch("src.api.feeds.compress_youtube", return_value=mock_card):
            response = self.client.post(
                "/api/v1/feeds/youtube",
                json={"url": "https://youtube.com/watch?v=abc123"},
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("card", data)

    @patch("src.api.deps.verify_id_token")
    def test_youtube_endpoint_missing_url_returns_400(self, mock_verify: MagicMock) -> None:
        """POST /feeds/youtube with empty body returns 400."""
        mock_verify.return_value = self.mock_user
        response = self.client.post(
            "/api/v1/feeds/youtube",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )
        self.assertEqual(response.status_code, 400)

    @patch("src.api.deps.verify_id_token")
    def test_queue_endpoint_returns_entries(self, mock_verify: MagicMock) -> None:
        """GET /feeds/queue returns 200 with entries list."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.feeds._get_feed_queue", return_value=[]):
            response = self.client.get(
                "/api/v1/feeds/queue",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("entries", data)

    @patch("src.api.deps.verify_id_token")
    def test_all_endpoints_require_auth(self, mock_verify: MagicMock) -> None:
        """All feed endpoints return 401 when no Authorization header is provided."""
        mock_verify.side_effect = Exception("No token")
        endpoints = [
            ("POST", "/api/v1/feeds/youtube"),
            ("GET", "/api/v1/feeds/queue"),
        ]
        for method, path in endpoints:
            if method == "GET":
                resp = self.client.get(path)
            else:
                resp = self.client.post(path, json={"url": "test"})
            self.assertIn(
                resp.status_code,
                (401, 403),
                f"{method} {path} should require auth, got {resp.status_code}",
            )


if __name__ == "__main__":
    unittest.main()
```

**Auth mock pattern** (lines 32-34 of test_onboarding.py):
```python
# Every test class:
def setUp(self) -> None:
    self.client = TestClient(app)
    self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

# Every test method:
@patch("src.api.deps.verify_id_token")
def test_something(self, mock_verify: MagicMock) -> None:
    mock_verify.return_value = self.mock_user
    # ...
```

---

### `solo-leveling/src/core/onboarding.py` (MOD — extend _SOURCE_FETCHERS)

**Modification:** Add youtube and rss fetchers to the registry (lines 233-237 of onboarding.py).

Current:
```python
_SOURCE_FETCHERS: dict[str, Callable[[], list[Any]]] = {
    "gmail": _gmail_fetcher,
}
```

Add:
```python
def _youtube_fetcher() -> list[Any]:
    """Placeholder — YouTube is triggered by paste, not polling."""
    return []


def _rss_fetcher() -> list[Any]:
    """Fetch latest RSS items from configured feeds."""
    from src.core.feeds import fetch_rss_items
    return fetch_rss_items()


_SOURCE_FETCHERS: dict[str, Callable[[], list[Any]]] = {
    "gmail": _gmail_fetcher,
    "youtube": _youtube_fetcher,
    "rss": _rss_fetcher,
}
```

---

### `solo-leveling/src/core/library_store.py` (MOD — add read field)

**Modification:** Add `read` field to frontmatter in `save_entry()` (lines 194-204 of library_store.py).

Current frontmatter template:
```python
content = (
    f"---\n"
    f"title: {title}\n"
    f"section: {section}\n"
    f"status: {status}\n"
    f"tags: [{metadata_tags}]\n"
    f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
    f"{source_url_line}"
    f"---\n\n"
    f"{body}\n"
)
```

Add `read` field after `status`:
```python
content = (
    f"---\n"
    f"title: {title}\n"
    f"section: {section}\n"
    f"status: {status}\n"
    f"read: false\n"
    f"tags: [{metadata_tags}]\n"
    f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
    f"{source_url_line}"
    f"---\n\n"
    f"{body}\n"
)
```

Also update `build_index()` (line 393-404) to parse the `read` field:
```python
read_match = re.search(r"^read:\s*(.+)$", text, flags=re.MULTILINE)
read_flag = read_match.group(1).strip().lower() == "true" if read_match else True
# Add to record dict:
record["read"] = read_flag
```

Also add a `mark_read()` method or update `update_entry()` to flip the read flag.

---

### `solo-leveling/src/api/library.py` (MOD — add read filter)

**Modification:** Extend `list_entries` query to support `read=false` filter. The existing `list_entries()` in `library_store.py` already supports section/status/tag filtering (lines 324-364). Add `read` parameter:

In `library_store.py` `list_entries()`:
```python
def list_entries(
    self,
    section: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    source_url: Optional[str] = None,
    read: Optional[bool] = None,  # NEW
    page: int = 1,
    per_page: int = 20,
    sort: Optional[str] = None,
    order: Optional[str] = None,
) -> dict[str, Any]:
    # ... existing filters ...
    if read is not None:
        entries = [e for e in entries if e.get("read", True) == read]
```

---

### `solo-leveling/src/api/v1_router.py` (MOD — register feeds router)

**Modification:** Add feeds import and router registration (line 7-8 of v1_router.py).

Current:
```python
from src.api import dashboard, commands, reminders, library, graph, timeline, analysis, planning, autopilot, guide, n8n_callback, onboarding, profile
```

Add:
```python
from src.api import dashboard, commands, reminders, library, graph, timeline, analysis, planning, autopilot, guide, n8n_callback, onboarding, profile, feeds
```

And add:
```python
router.include_router(feeds.router)
```

---

### `dashboard/src/components/zen/types.ts` (MOD — extend StreamCardData)

**Modification:** Add new fields to `StreamCardData` (lines 10-16 of types.ts).

Current:
```typescript
export interface StreamCardData {
  id: string;
  source: string;
  timeLabel: string;
  bullets: [string, string, string];
  kind?: "email" | "news" | "library" | "generic";
}
```

Extended:
```typescript
export interface StreamCardData {
  id: string;
  source: string;
  timeLabel: string;
  bullets: [string, string, string];
  kind?: "email" | "news" | "library" | "generic";
  // Phase 6: Smart Feeds
  sources?: { title: string; url: string }[];
  read?: boolean;
  watchMinutes?: number;
  readSeconds?: number;
  thumbnailUrl?: string;
}
```

---

### `dashboard/src/components/zen/StreamCard.tsx` (MOD — sources + unread)

**Modification 1:** Import and render `FeedSources` for dedup cards (after bullet list, before actions):
```tsx
import { FeedSources } from "./FeedSources";

// In the JSX, after the <ul> bullet list:
{card.sources && card.sources.length > 0 && (
  <FeedSources sources={card.sources} />
)}
```

**Modification 2:** Add unread indicator — subtle accent border when `read === false`:
```tsx
// Change the article className (line 45):
className={`flex max-h-[140px] flex-col rounded-lg border bg-card p-3 shadow-sm transition-shadow hover:shadow-md ${
  selected ? "border-accent ring-1 ring-accent/30" :
  card.read === false ? "border-accent/50" : "border-border"
}`}
```

**Modification 3:** Add watch/read time metrics for YouTube cards:
```tsx
// After the timeLabel span, add:
{card.watchMinutes && card.readSeconds && (
  <span className="text-xs text-muted">
    {card.watchMinutes} min watch → {card.readSeconds}s read
  </span>
)}
```

---

### `dashboard/src/components/zen/ContextNest.tsx` (MOD — feed queue)

**Modification:** Fetch feed queue alongside library recent (lines 59-66 of ContextNest.tsx).

Current:
```tsx
useEffect(() => {
  fetchLibraryRecent(4)
    .then((res) => {
      const cards = (res.entries ?? []).slice(0, 4).map(entryToCard);
      setLibraryCards(cards);
    })
    .catch(() => setLibraryCards([]));
}, []);
```

Extended:
```tsx
useEffect(() => {
  Promise.all([
    fetchLibraryRecent(4),
    fetch("/api/v1/feeds/queue", {
      headers: { "Authorization": `Bearer ${getToken()}` },
    }).then(r => r.json()).catch(() => ({ entries: [] })),
  ]).then(([libRes, feedRes]) => {
    const libCards = (libRes.entries ?? []).slice(0, 4).map(entryToCard);
    const feedCards = (feedRes.entries ?? []).slice(0, 6).map(feedEntryToCard);
    setLibraryCards([...feedCards, ...libCards]);
  }).catch(() => setLibraryCards([]));
}, []);
```

Add `feedEntryToCard` mapper (similar to `entryToCard` at lines 31-48):
```tsx
function feedEntryToCard(entry: {
  id: string;
  title?: string;
  section?: string;
  tags?: string[];
  updated_at?: string;
  source_url?: string;
  read?: boolean;
  sources?: { title: string; url: string }[];
}): StreamCardData {
  const title = entry.title ?? "Untitled feed item";
  const section = entry.section ?? "news";
  return {
    id: entry.id,
    source: section.charAt(0).toUpperCase() + section.slice(1),
    timeLabel: entry.updated_at ? new Date(entry.updated_at).toLocaleDateString() : "Recent",
    kind: section === "news" ? "news" : "library",
    bullets: [title, "From your feed.", "Open to read the full summary."],
    read: entry.read ?? true,
    sources: entry.sources,
  };
}
```

---

## Shared Patterns

### LLM 3-Bullet Compression
**Source:** `solo-leveling/src/core/onboarding.py` lines 133-180 (`generate_digest()`)
**Apply to:** `feeds.py` `compress_youtube()`, `compress_news()`, `compress_email()`
```python
# Pattern: run_agent(task, context, system=prompt) -> _strip_fences() -> json.loads() -> clamp to 3 bullets
response = run_agent(
    task=f"Compress this content:\n{truncated_content}",
    context=f"Title: {title}",
    system=_COMPRESSION_PROMPT,
)
cleaned = _strip_fences(response)
parsed = json.loads(cleaned)
bullets = list(parsed.get("bullets", []))[:3]
while len(bullets) < 3:
    bullets.append(_FALLBACK[len(bullets)])
```

### Auth Middleware
**Source:** `solo-leveling/src/api/deps.py` lines 12-20 (`require_auth`)
**Apply to:** All feed API endpoints
```python
from src.api.deps import require_auth

@router.post("/feeds/youtube")
async def endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    # user is guaranteed authenticated
```

### Error Handling
**Source:** `solo-leveling/src/api/onboarding.py` lines 39-52
**Apply to:** All feed API endpoints
```python
try:
    result = service_function(args)
    return {"status": "ok", "data": result}
except Exception:
    logger.exception("Failed to do thing")
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Failed to do thing. Please try again.",
    ) from None
```

### Vector Cosine Similarity
**Source:** `solo-leveling/src/vector/search.py` lines 66-83
**Apply to:** News dedup in `feeds.py`
```python
from src.vector.db import get_pool
from src.vector.embed import embed_text

vec = embed_text(text, task_type="RETRIEVAL_QUERY")
async with get_pool().connection() as conn:
    rows = await conn.fetchall(
        "SELECT entry_id, 1 - (embedding <=> %s::vector) AS similarity "
        "FROM signal_embeddings WHERE owner_id = %s ORDER BY embedding <=> %s::vector LIMIT 1",
        (vec, owner_id, vec),
    )
```

### n8n Template JSON
**Source:** `solo-leveling/src/n8n/templates/gmail_read_summary.json`
**Apply to:** `rss_poll_compress.json`
```json
{
  "id": "template_id",
  "name": "Human Name",
  "description": "What it does",
  "integration": null,
  "n8n_workflow_id": 0,
  "keywords": ["word1", "word2"],
  "side_effecting": false,
  "parameter_schema": { ... }
}
```

### Test Auth Mock
**Source:** `solo-leveling/tests/test_onboarding.py` lines 23-34
**Apply to:** `tests/test_feeds.py`
```python
class TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_endpoint(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        # ...
```

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md patterns instead):

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `solo-leveling/src/integrations/rss.py` (if created) | integration | file-I/O | No RSS integration exists yet; use `feedparser` library directly in `feeds.py` instead |

## Metadata

**Analog search scope:** `solo-leveling/src/core/`, `solo-leveling/src/api/`, `solo-leveling/src/n8n/`, `solo-leveling/src/vector/`, `solo-leveling/src/integrations/`, `solo-leveling/tests/`, `dashboard/src/components/zen/`
**Files scanned:** 18
**Pattern extraction date:** 2026-05-31
