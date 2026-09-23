# Requirements: Signal

**Defined:** 2026-05-29
**Core Value:** Turn raw noise into a small number of trustworthy, actionable signals.

> **Scope mode:** Personal-first (single owner). n8n is the firm execution engine. Multi-tenancy,
> billing, and the YOLO developer sandbox are deferred (see Out of Scope). Source PRD:
> `.planning/signal-prd.md`.

## v1 Requirements

Requirements for the personal-first MVP. Each maps to exactly one roadmap phase.

### Foundation

- [ ] **INFRA-01**: A vector database (e.g. pgvector/Qdrant) is provisioned and serves embedding queries
- [ ] **INFRA-02**: Content embeddings are generated and indexed for library entries and ingested items
- [ ] **INFRA-03**: A token-cache/dedup layer serves a cached summary when incoming content matches an indexed item (saves LLM tokens)
- [ ] **INFRA-04**: Persistence is re-scoped from owner-of-the-box to a single tenant record, without design choices that hard-block future multi-tenancy
- [ ] **INFRA-05**: An error-abstraction layer converts technical backend/n8n errors into soft AI-Guide messages

### Authentication & Onboarding

- [ ] **ONB-01**: Owner signs in with Google OAuth and the session persists across refresh
- [x] **ONB-02**: An Identity Box captures free-text ("what you do / what overwhelms you") and the AI Guide parses it into a working profile/context templates
- [x] **ONB-03**: Guided integration — the Guide highlights and connects only the relevant apps (e.g. Gmail) via the brain's existing integrations
- [x] **ONB-04**: At the end of onboarding the system generates and displays a first live 24-hour mini-digest ("Instant Win"), targeting < 2 minutes total

### AI Guide

- [ ] **GUIDE-01**: A persistent right-hand AI Guide panel is present across every view
- [ ] **GUIDE-02**: A natural-language Command Bar executes operations via LLM intent parsing (replaces the brittle keyword `INTENT_MAP`)
- [ ] **GUIDE-03**: A status banner shows reassuring processed-noise metrics (e.g. "processed N items for you")
- [ ] **GUIDE-04**: Contextual action buttons adapt to the active view/card (e.g. "draft a reply" on an email card)
- [ ] **GUIDE-05**: A "Park a Distraction" gate captures a stray thought without leaving the current focus

### Knowledge Library

- [ ] **LIB-01**: A folderless library archives articles, notes, writings, and documents (reuses the existing store)
- [ ] **LIB-02**: A plain-text Conceptual Search returns semantically related entries via vector embeddings (no exact filename match required)
- [ ] **LIB-03**: Recent Spark Cards show the most recently dropped inputs (max 3–4)
- [ ] **LIB-04**: Active Context Stacks group entries automatically by active macro-milestone/topic
- [ ] **LIB-05**: Per-entry AI Q&A answers questions against a selected entry (reuses the dashboard component)

### Zen Interface

- [ ] **ZEN-01**: An asymmetric 70/30 split-screen shell renders Panel A (Clarity Board) + a locked Panel B (AI Guide)
- [ ] **ZEN-02**: The Core Dashboard view shows a Critical Focus Block of max 3–5 actionable tasks, with a calm "You are entirely caught up" empty state
- [ ] **ZEN-03**: A Context Nest renders compressed stream cards, each limited to 3 single-sentence bullets
- [ ] **ZEN-04**: The Clarity Board switches cleanly between Core Dashboard / Knowledge Library / Routine Planner views

### Smart Feeds

- [ ] **FEED-01**: A YouTube link is compressed into a 3-bullet takeaway card with reading-time metrics (reuses transcript fetch)
- [ ] **FEED-02**: Email and news streams are compressed into Context Nest cards
- [ ] **FEED-03**: News deduplication collates matching events into a single situational card (uses the vector layer)
- [ ] **FEED-04**: No push alerts — new content queues silently for designated reading routines

### Smart Drafts & Human-in-the-Loop

- [ ] **DRAFT-01**: The system generates a context-aware, style-matching reply draft for an urgent communication
- [ ] **DRAFT-02**: One-click draft actions are offered: Approve & Send, Make Friendlier, Make Firmer
- [ ] **DRAFT-03**: Human-In-The-Loop is enforced — no outbound communication sends without an explicit user click (reuses the RL governor / approval store)

### Routine & Milestone Planner

- [ ] **PLAN-01**: "Today's Rhythm" shows only 2–3 core micro-routine time blocks (reuses the planning API)
- [ ] **PLAN-02**: Macro Milestones are tracked in a low-prominence area without cluttering the daily focus
- [ ] **PLAN-03**: The AI groups context stacks automatically by active milestone

### n8n Execution Layer

- [ ] **N8N-01**: The brain translates a user intent into an n8n workflow JSON and triggers it via the n8n API
- [ ] **N8N-02**: The owner's OAuth credentials are injected into the corresponding n8n nodes by the backend (owner never handles raw keys/webhooks)
- [ ] **N8N-03**: Pre-built n8n workflow templates power the feed/draft pipelines
- [ ] **N8N-04**: n8n execution status and webhook callbacks are ingested back into the brain

### Safety, Trust & Recovery

- [ ] **SAFE-01**: LLM processing uses zero-data-retention endpoints; personal data is never used to train public models
- [ ] **SAFE-02**: A Layout & Memory Reset flushes workspace cache + AI-Guide conversation loops while keeping connected app tokens alive
- [ ] **SAFE-03**: A Panic Button (single-user scope) deletes the owner's n8n workflows, revokes connected OAuth tokens, flushes the profile, and returns to onboarding

## v2 Requirements

Deferred to a future release. Tracked, not in the current roadmap.

### Shadow-Work Automation

- **DRAFT-04**: Keep-In-Touch Pulse proactively drafts relationship-maintenance touchpoints
- **DRAFT-05**: Automated Pipeline Routing extracts metrics from admin inputs (e.g. PDF invoices) into finance cards, alerting only on variance

### Platform / Commercial

- **SAAS-01**: Multi-tenant isolation (per-tenant data, credentials, and execution)
- **SAAS-02**: Subscription tiers + usage metering (Trial / Calm $39 / YOLO $99)
- **SAAS-03**: Per-user OAuth broker with an encrypted multi-tenant credential vault

### Power User

- **YOLO-01**: Custom LLM injection (user brings their own OpenAI/Anthropic API keys)
- **YOLO-02**: Direct node canvas / raw n8n JSON + custom JavaScript node injection
- **YOLO-03**: Guardrail disabling (bypass the default human-in-the-loop review)

## Out of Scope

Explicitly excluded for the personal-first MVP. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Multi-tenant SaaS isolation | Personal-first; foundation is built tenant-ready but not multi-tenant |
| Billing / subscription tiers / metering | No external paying users in v1 |
| YOLO mode (BYO keys, raw JSON, custom-JS, guardrail disable) | RCE/abuse surface — defer to v1.1 after credential layer is hardened |
| Apple OAuth | Google OAuth is sufficient for a single owner |
| Per-user OAuth broker / encrypted multi-tenant vault | Collapses to the owner's single credential set in personal-first mode |
| Bespoke Python per integration | n8n node catalog is the firm execution path (PRD §6) |

## Traceability

Each v1 requirement maps to exactly one phase. See `.planning/ROADMAP.md` for phase detail.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 — Data & Auth Foundation | Pending |
| INFRA-02 | Phase 1 — Data & Auth Foundation | Pending |
| INFRA-03 | Phase 1 — Data & Auth Foundation | Pending |
| INFRA-04 | Phase 1 — Data & Auth Foundation | Pending |
| ONB-01 | Phase 1 — Data & Auth Foundation | Pending |
| N8N-01 | Phase 2 — n8n Execution Layer | Pending |
| N8N-02 | Phase 2 — n8n Execution Layer | Pending |
| N8N-04 | Phase 2 — n8n Execution Layer | Pending |
| INFRA-05 | Phase 2 — n8n Execution Layer | Pending |
| LIB-01 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| LIB-02 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| LIB-03 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| LIB-05 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| GUIDE-01 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| GUIDE-02 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| GUIDE-03 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| GUIDE-05 | Phase 3 — Knowledge Library + Conceptual Search + AI Guide | Pending |
| ZEN-01 | Phase 4 — Zen Shell + Clarity Board | Pending |
| ZEN-02 | Phase 4 — Zen Shell + Clarity Board | Pending |
| ZEN-03 | Phase 4 — Zen Shell + Clarity Board | Pending |
| ZEN-04 | Phase 4 — Zen Shell + Clarity Board | Pending |
| GUIDE-04 | Phase 4 — Zen Shell + Clarity Board | Pending |
| ONB-02 | Phase 5 — Onboarding + Instant Win | Complete |
| ONB-03 | Phase 5 — Onboarding + Instant Win | Complete |
| ONB-04 | Phase 5 — Onboarding + Instant Win | Complete |
| FEED-01 | Phase 6 — Smart Feeds | Pending |
| FEED-02 | Phase 6 — Smart Feeds | Pending |
| FEED-03 | Phase 6 — Smart Feeds | Pending |
| FEED-04 | Phase 6 — Smart Feeds | Pending |
| N8N-03 | Phase 6 — Smart Feeds | Pending |
| DRAFT-01 | Phase 7 — Smart Drafts + Human-in-the-Loop | Pending |
| DRAFT-02 | Phase 7 — Smart Drafts + Human-in-the-Loop | Pending |
| DRAFT-03 | Phase 7 — Smart Drafts + Human-in-the-Loop | Pending |
| PLAN-01 | Phase 8 — Routine & Milestone Planner | Pending |
| PLAN-02 | Phase 8 — Routine & Milestone Planner | Pending |
| PLAN-03 | Phase 8 — Routine & Milestone Planner | Pending |
| LIB-04 | Phase 8 — Routine & Milestone Planner | Pending |
| SAFE-01 | Phase 9 — Safety, Trust & Recovery | Pending |
| SAFE-02 | Phase 9 — Safety, Trust & Recovery | Pending |
| SAFE-03 | Phase 9 — Safety, Trust & Recovery | Pending |

**Coverage:**
- v1 requirements: 40 total (across 10 categories — note: the prior "33 total" figure undercounted; the enumerated v1 set is 40)
- Mapped to phases: 40 ✓
- Unmapped: 0

---
*Requirements defined: 2026-05-29*
*Last updated: 2026-05-29 after roadmap revision (Foundation split into Phase 1 Data & Auth + Phase 2 n8n Execution Layer → 9 phases, 40/40 mapped)*
