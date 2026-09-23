# Roadmap: Signal

## Overview

Signal turns raw noise into a small number of trustworthy, actionable signals. We build it
**personal-first** on the existing `solo-leveling` brain (control/AI plane, heavily reused) plus
`dashboard`, with **n8n as the firm execution engine** (data/execution plane, built new). The
net-new foundation is split into two balanced phases so the differentiated value can land as
early as possible. **Phase 1 — Data & Auth Foundation** stands up the vector spine (vector DB +
embeddings + token-cache/dedup), persistence re-scoped to a single tenant record (built
tenant-ready, no multi-tenancy hard-blocks), and persistent Google OAuth. **Phase 2 — n8n
Execution Layer** wires the brain to n8n (REST client + owner-credential injection + intent→JSON
triggering + webhook/status callbacks) and adds the error-abstraction layer that softens
technical/n8n errors into AI-Guide messages. Splitting the foundation this way lets Milestone 1 —
the differentiated **Knowledge Library + conceptual vector search + the persistent AI Guide** —
build directly on the vector spine (Phase 1) without waiting on the n8n layer. The **Zen shell**
then gives those features their 70/30 home; **Onboarding** delivers the sub-2-minute Instant Win
(needs the n8n credential layer + a digest pipeline). **Smart Feeds**, **Smart Drafts (HITL)**,
and the **Routine Planner** broaden the value on top of n8n and the reused planning API. Finally,
**Safety & Recovery** (reset, panic) hardens the owner's trust in the credential and persistence
layers. Each post-foundation phase ships a usable end-to-end vertical slice.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Data & Auth Foundation** - Net-new vector spine: vector DB + embeddings + token-cache/dedup, tenant-ready single-record persistence, persistent Google OAuth
- [x] **Phase 2: n8n Execution Layer** - n8n REST client + owner-credential injection + intent→JSON triggering + webhook/status callback ingestion, plus the soft error-abstraction layer
- [x] **Phase 3: Knowledge Library + Conceptual Search + AI Guide** - Milestone-1 centerpiece: folderless vector-searchable library, Recent Spark Cards, per-entry Q&A, and the persistent LLM-driven AI Guide
- [x] **Phase 3.1: Library Table Enhancements** (INSERTED) - Thumbnail/image per table row, delete entry, date formatting, AI-summary endpoint audit, data-structure forward-compat review (completed 2026-05-30)
- [x] **Phase 4: Zen Shell + Clarity Board** - Asymmetric 70/30 split-screen with locked Panel B, Core Dashboard focus block, Context Nest, view switching, contextual actions
- [x] **Phase 5: Onboarding + Instant Win** - Guided sub-2-minute flow: Identity Box → AI-parsed profile → relevant-app connect → first live 24-hour digest (completed 2026-05-31)
- [ ] **Phase 6: Smart Feeds** - YouTube/email/news compression into 3-bullet Context Nest cards, vector-based news dedup, silent queue, n8n template pipelines
- [ ] **Phase 7: Smart Drafts + Human-in-the-Loop** - Context-aware style-matched reply drafts with one-click tone variants, gated by the reused RL governor / approval store
- [ ] **Phase 8: Routine & Milestone Planner** - Minimalist "Today's Rhythm" routines, low-prominence macro milestones, and AI-grouped Active Context Stacks
- [ ] **Phase 9: Safety, Trust & Recovery** - Zero-retention LLM endpoints, Layout & Memory Reset, single-user Panic Button (workflow delete + token revoke + profile flush)

## Phase Details

### Phase 1: Data & Auth Foundation

**Goal**: Stand up the net-new data spine and identity layer that the differentiated Milestone-1 slice builds on — a provisioned vector DB serving embedding queries, content embeddings generated and indexed, a token-cache/dedup layer that returns cached summaries for already-indexed content, persistence re-scoped from owner-of-the-box to a single tenant record (no design choices that hard-block future multi-tenancy), and persistent Google OAuth sign-in (reuses the Firebase auth foundation).
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, ONB-01
**Success Criteria** (what must be TRUE):

  1. Owner signs in with Google and the session survives a page refresh
  2. A plain-text query against the vector DB returns the nearest indexed embeddings (verified via a smoke query)
  3. Content embeddings are generated and indexed for library entries / ingested items
  4. Re-ingesting already-indexed content returns the cached summary instead of a fresh LLM call (token-cache hit observable in logs)
  5. State reads/writes route through a single tenant record rather than the owner-of-the-box assumption, with no multi-tenancy hard-blocks

**Plans**: 5 plans

Plans:

- [ ] 01-01-PLAN.md — Wave 0: Test stubs, env documentation, and config exports
- [ ] 01-02-PLAN.md — Wave 1: pgvector Postgres provisioned and wired into FastAPI lifespan
- [ ] 01-03-PLAN.md — Wave 2: Gemini embeddings pipeline and token-cache/dedup layer
- [ ] 01-04-PLAN.md — Wave 3: Persistent Google OAuth session via Firebase session cookies
- [ ] 01-05-PLAN.md — Wave 4: Integration verification, full test suite, docs update, phase close

### Phase 2: n8n Execution Layer

**Goal**: Wire the brain to n8n as the firm execution engine and make its failures owner-safe — build the n8n REST client, translate a user intent into an n8n workflow JSON and trigger it via the n8n API, inject the owner's OAuth credentials into the corresponding n8n nodes by the backend (owner never handles raw keys/webhooks), ingest n8n execution status and webhook callbacks back into the brain, and add the error-abstraction layer that converts technical backend/n8n errors into soft AI-Guide messages.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: N8N-01, N8N-02, N8N-04, INFRA-05
**Success Criteria** (what must be TRUE):

  1. The brain translates a user intent into an n8n workflow JSON and triggers it over the n8n REST API
  2. The owner's OAuth credentials are injected into the corresponding n8n nodes by the backend (owner never handles raw keys/webhooks)
  3. n8n execution status and webhook callbacks are ingested back into the brain
  4. A forced backend/n8n failure surfaces to the owner as a soft AI-Guide message, not a raw stack trace

**Plans**: 3 plans

Plans:

- [ ] 02-01-PLAN.md — Wave 1: n8n REST client + error abstraction + test stubs + config
- [ ] 02-02-PLAN.md — Wave 2: Intent executor (LLM param fill + RL gate) + credential injection + connect-time sync + router wiring + template skeletons
- [ ] 02-03-PLAN.md — Wave 3: Webhook callback endpoint + full test coverage + live n8n provisioning checkpoint

### Phase 3: Knowledge Library + Conceptual Search + AI Guide

**Goal**: Ship the differentiated Milestone-1 slice on top of the Phase 1 vector spine (this phase must not be blocked by the n8n execution layer). Reuse the existing folderless library store and dashboard Q&A component, layer vector search over the keyword store (EVOLVE), and replace the brittle keyword `INTENT_MAP` with the Gemini dispatcher driving an LLM intent-parsing Command Bar (EVOLVE). Deliver the persistent right-hand AI Guide as a standalone usable surface even before the full Zen shell exists.
**Mode:** mvp
**Depends on**: Phase 1 (the vector spine — not the n8n execution layer)
**Requirements**: LIB-01, LIB-02, LIB-03, LIB-05, GUIDE-01, GUIDE-02, GUIDE-03, GUIDE-05
**Success Criteria** (what must be TRUE):

  1. Owner can archive an article/note/document into the folderless library and find it later
  2. Owner can type a plain-text query and get semantically related entries back with no exact filename match required
  3. Owner can ask a question against a selected entry and get an answer grounded in that entry
  4. The persistent AI Guide panel accepts a natural-language command and executes the resolved intent via LLM parsing (not keyword matching)
  5. A status banner reports processed-noise metrics (e.g. "processed N items for you") and the owner can park a stray thought without leaving focus

**Plans**: 6 plans (+ 1 gap-closure)

Plans:

- [x] 03-01-PLAN.md — Wave 0: Test stubs + API contracts + dashboard scaffold
- [x] 03-02-PLAN.md — Wave 1: Vector search backend + library API enhancements
- [x] 03-03-PLAN.md — Wave 2: LLM intent parser + guide API
- [x] 03-04-PLAN.md — Wave 3: AI Guide panel UI (dashboard)
- [x] 03-05-PLAN.md — Wave 4: Integration verification + docs + phase close
- [x] 03-07-PLAN.md — Gap closure: fix #/library deep-link/refresh 404 (route dashboard paths to DashboardPage + hydrate tabs from hash) [UAT items 8–13]

### Phase 3.1: Library Table Enhancements (INSERTED)

**Goal**: Close UI/UX and data-layer gaps in the Knowledge Library table view after Phase 3 shipped — thumbnail/image display per row, delete entry capability (backend + UI), human-readable date formatting, audit and fix AI-summary endpoint URL/base, and verify `LibraryEntry` data format is forward-compatible with Phase 5/6.
**Depends on**: Phase 3
**Requirements**: (gap-closure — no new REQ-IDs)
**Success Criteria** (what must be TRUE):

  1. TableView shows a thumbnail (YouTube) or type icon for every row
  2. Owner can delete a library entry from the table; entry disappears from the list
  3. The "Date" column shows a formatted date (e.g., "May 28, 2026"), not a raw ISO string
  4. The AI-summary synthesize call succeeds against the production brain URL with no CORS/404 errors
  5. `LibraryEntry` type has optional forward-compat fields (`thumbnail_url?`, `og_image?`) that don't break existing renders

**Plans**: 4 plans

Plans:

- [x] 03.1-01-PLAN.md — Wave 1→2: DELETE endpoint + LibraryEntry type extension
- [x] 03.1-02-PLAN.md — Wave 2: Dashboard UI — thumbnail column, delete button, formatted date, synthesize audit
- [x] 03.1-03-PLAN.md — Wave 1: Store-level delete_entry() implementation (prerequisite for Plan 01)
- [x] 03.1-04-PLAN.md — Wave 3: CardView menu, TableView row expand, relative time tooltip, LibraryPage wiring

### Phase 4: Zen Shell + Clarity Board

**Goal**: Build the structural 70/30 Zen workspace (BUILD-NEW — a rebuild of the static dashboard, not a restyle): Panel A Clarity Board + locked Panel B (the AI Guide from Phase 3), the Core Dashboard Critical Focus Block with its "You are entirely caught up" empty state, the Context Nest of compressed 3-bullet cards, clean switching between Core Dashboard / Knowledge Library / Routine Planner views, and view-adaptive contextual action buttons.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: ZEN-01, ZEN-02, ZEN-03, ZEN-04, GUIDE-04
**Success Criteria** (what must be TRUE):

  1. The app renders an asymmetric 70/30 split-screen with Panel A content and a locked, always-present Panel B AI Guide
  2. The Core Dashboard shows at most 3-5 actionable tasks and renders the calm "You are entirely caught up" state when empty
  3. The Context Nest renders stream cards each limited to exactly 3 single-sentence bullets
  4. The owner can switch cleanly between Core Dashboard, Knowledge Library, and Routine Planner views
  5. Contextual action buttons change to match the active view/card (e.g. "draft a reply" on an email card)

**Plans**: 1 plan

Plans:

- [x] 04-01-PLAN.md — Wave 1: Zen shell scaffold (ZenShell, ClarityBoard, Critical Focus, Context Nest, contextual actions)

**UI hint**: yes

### Phase 5: Onboarding + Instant Win

**Goal**: Deliver the guided sub-2-minute first run. The Identity Box captures free text and the AI Guide (Phase 3) parses it into a working profile / context templates; guided integration highlights and connects only the relevant apps via the brain's existing integrations through the n8n credential layer (Phase 2); onboarding ends by generating and displaying a first live 24-hour mini-digest as the Instant Win.
**Mode:** mvp
**Depends on**: Phase 4 and Phase 2 (needs the n8n credential layer + a digest pipeline)
**Requirements**: ONB-02, ONB-03, ONB-04
**Success Criteria** (what must be TRUE):

  1. Owner enters free text in the Identity Box and the AI Guide produces a working profile / context templates from it
  2. The Guide highlights only the relevant apps (e.g. Gmail) and the owner connects them via OAuth without handling raw keys
  3. At the end of onboarding the system displays a live 24-hour mini-digest generated from real connected data
  4. A first-run owner reaches the Instant Win in under 2 minutes

**Plans**: 4 plans (2 + 2 gap-closure)

Plans:
**Wave 1**

- [x] 05-01-PLAN.md — Wave 1: Backend profile store + onboarding endpoints + Identity Box + Profile Confirmation UI

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 05-02-PLAN.md — Wave 2: App Connect + Instant Win digest + wizard completion

**Wave 3 — gap closure** *(error-handling chain; depends on 05-01, 05-02)*

- [x] 05-03-PLAN.md — Gap closure: parse-identity 502 on LLM failure (CR-01) + IdentityBox response guard / loading reset (CR-01/CR-02) + handleComplete null-profile safety (CR-05) + ProfileData.connected_apps (WR-02)

**Wave 4 — gap closure** *(honest digest labeling; depends on 05-03 — shares api/onboarding.py)*

- [x] 05-04-PLAN.md — Gap closure: digest endpoint `mode` (live/preview) + generalized `_query_connected_sources` + honest InstantWinDigest labeling (SC-3/ONB-03/ONB-04 honest-labeling; WR-02 cast removal)

**UI hint**: yes

### Phase 6: Smart Feeds

**Goal**: Compress real streams into the Context Nest using n8n template pipelines (N8N-03) and the reused YouTube transcript fetch + Gmail summary building blocks. A YouTube link becomes a 3-bullet takeaway card with reading-time metrics; email and news streams compress into cards; the vector layer collates duplicate news events into a single situational card; and new content queues silently (no push alerts) for designated reading routines.
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: FEED-01, FEED-02, FEED-03, FEED-04, N8N-03
**Success Criteria** (what must be TRUE):

  1. Pasting a YouTube link yields a 3-bullet takeaway card with reading-time metrics
  2. Connected email and news streams appear as compressed Context Nest cards
  3. Multiple reports of the same news event collapse into one situational card via the vector layer
  4. New content never triggers a push alert — it queues silently until the owner opens a reading routine
  5. Feed and dedup pipelines run as pre-built n8n workflow templates triggered by the brain

**Plans**: 2 plans

Plans:
**Wave 1**

- [ ] 06-01-PLAN.md — Wave 1: Backend feeds module (YouTube/news/email compression, RSS fetch, vector dedup) + library store read flag + n8n RSS template + tests

**Wave 2** *(blocked on Wave 1 — needs backend endpoints)*

- [ ] 06-02-PLAN.md — Wave 2: Frontend StreamCard YouTube/dedup/unread extensions + ContextNest feed queue integration + FeedSources component

### Phase 7: Smart Drafts + Human-in-the-Loop

**Goal**: Generate context-aware, style-matching reply drafts for urgent communications, offer one-click tone variants, and enforce Human-In-The-Loop by reusing the autopilot RL governor + approval store (EVOLVE) so nothing sends without an explicit owner click.
**Mode:** mvp
**Depends on**: Phase 6
**Requirements**: DRAFT-01, DRAFT-02, DRAFT-03
**Success Criteria** (what must be TRUE):

  1. The owner can ask for a reply to an urgent message and get a context-aware, style-matching draft
  2. The owner sees one-click actions on the draft: Approve & Send, Make Friendlier, Make Firmer
  3. No outbound communication is sent without an explicit owner click (enforced by the reused approval gate)
  4. Choosing a tone variant regenerates the draft in the requested tone before any send

**Plans**: TBD

### Phase 8: Routine & Milestone Planner

**Goal**: Deliver the minimalist planning view by reusing the existing planning API (`planning.py`). "Today's Rhythm" shows only 2-3 core micro-routine time blocks; macro milestones are tracked in a low-prominence area that never clutters daily focus; and the AI automatically groups library Active Context Stacks by the active macro-milestone/topic.
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: PLAN-01, PLAN-02, PLAN-03, LIB-04
**Success Criteria** (what must be TRUE):

  1. "Today's Rhythm" shows only 2-3 core micro-routine time blocks
  2. Macro milestones are visible in a low-prominence area without crowding the daily focus
  3. Library entries auto-group into Active Context Stacks by active macro-milestone/topic
  4. The owner can move between the planner view and the rest of the Clarity Board without losing focus

**Plans**: TBD
**UI hint**: yes

### Phase 9: Safety, Trust & Recovery

**Goal**: Harden owner trust in the credential and persistence layers (downstream of the n8n credential layer and tenant-ready persistence — not polish). Route LLM processing through zero-data-retention endpoints; provide a Layout & Memory Reset that flushes workspace cache + AI-Guide conversation loops while keeping app tokens alive; and a single-user Panic Button that deletes the owner's n8n workflows, revokes connected OAuth tokens, flushes the profile, and returns to onboarding.
**Mode:** mvp
**Depends on**: Phase 8
**Requirements**: SAFE-01, SAFE-02, SAFE-03
**Success Criteria** (what must be TRUE):

  1. LLM calls use zero-data-retention endpoints and personal data is never sent to training-eligible paths (verifiable in config/logs)
  2. Layout & Memory Reset flushes workspace cache + AI-Guide conversation loops while connected app tokens stay alive
  3. Panic Button deletes the owner's n8n workflows, revokes connected OAuth tokens, flushes the profile, and returns the owner to onboarding

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data & Auth Foundation | 5/5 | Complete | 2026-05-31 |
| 2. n8n Execution Layer | 3/3 | Executed | - |
| 3. Knowledge Library + Conceptual Search + AI Guide | 7/7 | Complete | 2026-05-30 |
| 3.1. Library Table Enhancements | 4/4 | Complete   | 2026-05-30 |
| 4. Zen Shell + Clarity Board | 1/1 | Complete | 2026-05-30 |
| 5. Onboarding + Instant Win | 4/4 | Complete   | 2026-05-31 |
| 6. Smart Feeds | 0/2 | Not started | - |
| 7. Smart Drafts + Human-in-the-Loop | 0/TBD | Not started | - |
| 8. Routine & Milestone Planner | 0/TBD | Not started | - |
| 9. Safety, Trust & Recovery | 0/TBD | Not started | - |
