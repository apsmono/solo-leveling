---
phase: 6
slug: smart-feeds
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-31
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `unittest` (stdlib) |
| **Config file** | `tests/` directory |
| **Quick run command** | `python -m unittest tests.test_feeds -v` |
| **Full suite command** | `python -m unittest discover tests -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests.test_feeds -v`
- **After every plan wave:** Run `python -m unittest discover tests -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | FEED-01 | T-06-01 | YouTube URL validation via `extract_video_id()` | unit | `python -m unittest tests.test_feeds::test_compress_youtube -v` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | FEED-02 | T-06-02 | Email/news compression to 3-bullet cards | unit | `python -m unittest tests.test_feeds::test_compress_email -v` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | FEED-03 | T-06-03 | News dedup via cosine similarity (threshold 0.85) | unit | `python -m unittest tests.test_feeds::test_dedup_merge -v` | ❌ W0 | ⬜ pending |
| 06-01-04 | 01 | 1 | FEED-04 | T-06-04 | Silent queue — no push alerts, `read: false` flag | integration | `python -m unittest tests.test_feeds::test_silent_queue -v` | ❌ W0 | ⬜ pending |
| 06-01-05 | 01 | 1 | N8N-03 | T-06-05 | RSS n8n template exists + matches pattern | unit | `python -m unittest tests.test_feeds::test_rss_template -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_feeds.py` — stubs for FEED-01, FEED-02, FEED-03, FEED-04, N8N-03
- [ ] `tests/conftest.py` — shared fixtures (mock transcript, mock RSS feed)
- [ ] `feedparser` install: `pip install feedparser`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| YouTube card appears in Context Nest after paste | FEED-01 | Requires live Command Bar + Guide integration | Paste a YouTube URL in Command Bar, verify card appears in Context Nest with 3 bullets + reading-time metric |
| RSS feed cards appear after n8n poll | FEED-02 | Requires live n8n instance + RSS feed | Add RSS feed via Command Bar, wait for n8n poll cycle, verify cards appear |
| Dedup card shows expandable sources | FEED-03 | Requires multiple articles about same event | Ingest 2+ similar news articles, verify they merge into one card with expandable sources |
| No push notification on new content | FEED-04 | Negative test — absence of notification | Add feed, wait for new content, verify no browser push/notification appears |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
