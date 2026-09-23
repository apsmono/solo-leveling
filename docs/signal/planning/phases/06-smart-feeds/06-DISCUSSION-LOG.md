# Phase 6: Smart Feeds - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-31
**Phase:** 06-smart-feeds
**Areas discussed:** YouTube → 3-bullet flow, News source & ingestion, Reading routines & silent queue, News dedup card design

---

## YouTube → 3-Bullet Flow

### Q1: How does the owner trigger YouTube compression?

| Option | Description | Selected |
|--------|-------------|----------|
| Command Bar paste | Owner pastes a YouTube URL in the Command Bar → brain detects it → fetches transcript → compresses to 3 bullets → returns a StreamCard. Simplest, reuses existing intent parser. | ✓ |
| Universal paste handler | Owner pastes URL anywhere in Signal — Panel A, a dedicated input, or the Command Bar. A universal paste handler detects YouTube links. | |
| n8n auto-pipeline | An n8n workflow monitors a 'YouTube watch later' or bookmarks feed and auto-compresses new videos. No manual trigger needed. | |
| Both — paste + optional pipeline | Command Bar paste for immediate use, plus an optional n8n pipeline for auto-monitoring subscriptions later. | |

**User's choice:** Command Bar paste (Recommended)
**Notes:** Simplest approach. The intent parser detects a YouTube URL, triggers transcript fetch → LLM compression → StreamCard response.

### Q2: What are 'reading-time metrics'?

| Option | Description | Selected |
|--------|-------------|----------|
| Watch time vs. read time | Show 'X min watch → Y sec read' comparing estimated video duration to bullet reading time. Reinforces the 'compressed signal' value prop. | ✓ |
| Video duration only | Just show estimated video duration (e.g., '12 min video'). No read-time comparison. | |
| Read time only | Show reading time for the 3 bullets only (e.g., '15 sec read'). No video duration. | |
| No metrics | No time metrics at all — just the 3 bullets and source label. | |

**User's choice:** Watch time vs. read time (Recommended)
**Notes:** "12 min watch → 15 sec read" reinforces the value prop perfectly.

### Q3: Where does the YouTube takeaway card appear after compression?

| Option | Description | Selected |
|--------|-------------|----------|
| Inline in Guide response | The Command Bar returns the card inline in Panel B (the Guide). Owner can save it to the library or dismiss. Reuses the existing Guide response pattern. | |
| Auto-add to Context Nest | The card appears directly in the Context Nest in Panel A, alongside email/news cards. It's automatically part of the stream. | |
| Both — Guide + Context Nest | Card appears in the Guide AND gets auto-saved to the Context Nest simultaneously. | ✓ |

**User's choice:** Both — Guide + Context Nest
**Notes:** Card appears inline in the Guide as a response AND is auto-added to the Context Nest as a stream card.

### Q4: Should the YouTube takeaway also be saved to the Knowledge Library?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, save to library | Save the 3 bullets + metadata to the Knowledge Library as a new entry. Reuses existing library store. Enables conceptual search later. | ✓ |
| No, ephemeral only | Only in the Context Nest / Guide. Not persisted to the library. Stays ephemeral. | |
| On-demand save | Save to library only if the owner clicks 'Save' on the card. Otherwise ephemeral. | |

**User's choice:** Yes, save to library (Recommended)
**Notes:** Auto-save enables conceptual search and later retrieval.

---

## News Source & Ingestion

### Q1: What counts as 'news' for FEED-02?

| Option | Description | Selected |
|--------|-------------|----------|
| RSS feeds | Owner configures specific RSS feed URLs (e.g., TechCrunch, Hacker News, industry blogs). Brain or n8n polls them periodically. Simple, well-understood format. | ✓ |
| Topic-based news API | Owner provides news topics/keywords (e.g., 'AI regulation', 'pgvector updates'). An n8n workflow uses a news API (Google News, NewsAPI.org) to fetch matching articles. | |
| Manual paste only | Owner pastes news article URLs manually in the Command Bar (like YouTube). No auto-ingestion. | |
| RSS + topic API combo | RSS feeds for structured sources + topic-based API for broader coverage. n8n handles both. | |

**User's choice:** RSS feeds (Recommended)
**Notes:** Clean and simple. RSS is well-understood and widely supported.

### Q2: How do RSS feeds get ingested?

| Option | Description | Selected |
|--------|-------------|----------|
| n8n polls on schedule | An n8n workflow polls configured RSS feeds on a schedule (e.g., every hour), compresses new items into 3-bullet cards, and pushes them to the brain. Matches the 'n8n is the execution engine' mandate. | ✓ |
| Brain scheduler polls | The brain's scheduler (APScheduler) polls RSS feeds directly. Simpler, but doesn't use n8n as the execution engine. | |
| n8n scheduled + manual brain trigger | RSS feeds are polled by n8n, but the brain also has a manual 'refresh feeds' trigger for on-demand fetch. | |

**User's choice:** n8n polls on schedule (Recommended)
**Notes:** Follows the n8n-as-execution-engine mandate (N8N-03).

### Q3: How does the owner configure which RSS feeds to follow?

| Option | Description | Selected |
|--------|-------------|----------|
| Command Bar management | Owner adds/removes RSS feed URLs via the Command Bar (e.g., 'add feed: https://techcrunch.com/feed'). Brain stores them in profile/config. n8n reads from there. | ✓ |
| Settings page in Panel A | A dedicated Settings/Feeds page in Panel A where owner manages RSS sources. More structured but needs new UI. | |
| Natural language to Guide | Owner tells the AI Guide which feeds to follow in natural language. Guide parses and stores. Same as Identity Box pattern. | |

**User's choice:** Command Bar management (Recommended)
**Notes:** Consistent with the Command Bar as the primary interaction surface.

---

## Reading Routines & Silent Queue

### Q1: What is a 'reading routine'?

| Option | Description | Selected |
|--------|-------------|----------|
| Manual 'show me new' on open | The owner opens Signal and sees a 'New since last visit' section in the Context Nest. Content accumulates silently; the owner reads when they choose. No time-based scheduling. | ✓ |
| Scheduled reading windows | Owner defines 2-3 reading times (e.g., 9am, 1pm, 6pm). At those times, queued content surfaces as a digest. Uses the brain's scheduler. | |
| Scheduled + on-open | Owner defines reading times, AND sees new content when they open Signal. Both scheduled and on-demand. | |

**User's choice:** Manual 'show me new' on open (Recommended)
**Notes:** Simple and calm — content waits for the owner, not the other way around.

### Q2: How does the owner distinguish new vs. seen content?

| Option | Description | Selected |
|--------|-------------|----------|
| Subtle visual indicator | New cards get a subtle accent border or dot indicator. Once the owner has seen them, the indicator fades. No explicit 'mark as read' action needed. | ✓ |
| Separate 'New' section | New cards appear in a 'New' section at the top of the Context Nest. After viewing, they move to the regular feed section. | |
| No distinction | No visual distinction between new and seen. The Context Nest just shows the most recent items regardless. | |

**User's choice:** Subtle visual indicator (Recommended)
**Notes:** Non-intrusive, Signal-calibrated.

### Q3: Where does the silent queue live?

| Option | Description | Selected |
|--------|-------------|----------|
| Library entries with read flag | Queued items are stored as library entries with a 'queued' or 'unread' flag. Reuses the existing library store. When viewed, the flag flips to 'read'. | ✓ |
| Separate queue store | A separate feed_queue table/collection in the database. Keeps feed items distinct from library entries. | |
| Ephemeral in-memory | Feed items are ephemeral — stored in memory/cache only. Disappear on server restart. Simpler but lossy. | |

**User's choice:** Library entries with read flag (Recommended)
**Notes:** Reuses existing library store. The `read` flag is a simple addition to the entry schema.

---

## News Dedup Card Design

### Q1: What does a dedup 'situational card' look like?

| Option | Description | Selected |
|--------|-------------|----------|
| Synthesized summary + expandable sources | A single synthesized summary bullet (e.g., 'Multiple sources report OpenAI raised $X'). Below it, expandable source list showing original titles. Clean, Signal-calibrated. | ✓ |
| All source titles as bullets | Show all source titles as separate bullets (up to the 3-bullet limit). If 4+ sources, show top 3 and '+N more'. | |
| Summary only, no sources | One synthesized card with no source attribution. Maximum compression, but loses provenance. | |

**User's choice:** Synthesized summary + expandable sources (Recommended)
**Notes:** Clean compression with provenance preserved.

### Q2: How does the system detect duplicate news?

| Option | Description | Selected |
|--------|-------------|----------|
| Vector similarity merge | Vector similarity threshold — when a new article's embedding is within X cosine distance of an existing card, merge it into that card. Uses the Phase 1 vector DB. | ✓ |
| LLM-based merge decision | LLM-based — send new + recent articles to the LLM and ask 'are these about the same event?' More accurate but more expensive. | |
| Vector filter + LLM confirm | Vector similarity as fast filter, LLM as confirmation for borderline cases. Best accuracy but more complex. | |

**User's choice:** Vector similarity merge (Recommended)
**Notes:** Fast, cheap, uses the existing Phase 1 vector DB infrastructure.

### Q3: Should a dedup card be a distinct card type?

| Option | Description | Selected |
|--------|-------------|----------|
| Same kind: 'news' | Use kind: 'news' — same as regular news cards. The dedup card just has more sources. Keeps the StreamCard type simple. | ✓ |
| New kind: 'situational' | Add a new kind: 'situational' or 'dedup'. The card gets a distinct icon (e.g., Layers instead of Newspaper). Visually signals 'this is aggregated'. | |
| 'news' + optional sources array | Kind stays 'news' but add an optional 'sources' array to StreamCardData for expandable source list. | |

**User's choice:** Same kind: 'news' (Recommended)
**Notes:** Keeps the type system simple. The `sources` array on StreamCardData handles the expandable list.

---

## Claude's Discretion

The following areas were left to Claude's discretion during planning:
- Exact RSS polling interval (e.g., 30 min vs. 1 hour)
- Vector similarity threshold for dedup (tunable parameter)
- Subtle indicator style for new/unread cards (accent border vs. dot vs. badge)
- Expandable sources UI pattern (accordion vs. tooltip vs. modal)
- n8n RSS workflow template JSON structure
- How YouTube video duration is estimated (from metadata or transcript length)
- Error handling when transcript fetch fails (fallback to title + description?)
- Whether email compression reuses the existing `inbox_summary()` or needs a new LLM compression pass

## Deferred Ideas

- Topic-based news API (Google News, NewsAPI.org) — future phase when RSS proves insufficient
- YouTube subscription auto-monitoring via n8n — future phase, manual paste only for v1
- Scheduled reading windows (e.g., 9am, 1pm, 6pm digest) — Phase 8 Routine Planner territory
- Push notifications for urgent feeds — explicitly out of scope (FEED-04: no push alerts)
- Feed analytics (most-read sources, reading patterns) — future phase
