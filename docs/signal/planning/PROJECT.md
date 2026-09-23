# Signal

## What This Is

Signal is a "calm intelligence layer" that fights *infobesity* — it ingests a person's
unstructured streams (email, chat, news, YouTube, documents) and presents only compressed,
actionable signal inside a deliberately minimal "Zen" workspace, with a persistent
conversational **AI Guide** and a folderless, vector-searchable **Knowledge Library**.

**Built personal-first** (single user — the owner) on top of the existing `solo-leveling`
brain + `dashboard`, with **n8n as the execution engine** for automation/integration
workflows. Architected so it *can* become a multi-tenant SaaS later, but multi-tenancy,
billing, and the developer "YOLO" sandbox are explicitly deferred.

## Core Value

**Turn raw noise into a small number of trustworthy, actionable signals** — if everything
else fails, the conceptual Knowledge Library + AI Guide must still let the owner find and act
on what matters without managing ten tabs.

## Requirements

### Validated

<!-- Brownfield: reusable capabilities already shipped in solo-leveling / dashboard. -->

- ✓ **Planning API** (goals/projects/tasks/habits/reviews) — `solo-leveling/src/.../planning.py` (powers Routine/Milestone Planner)
- ✓ **Knowledge Library store** (folderless markdown + Firestore backends, 9-field metadata) — `libraries.py` / `library_store.py` (search is keyword-only today)
- ✓ **Library UI** (search, entry detail, per-entry AI Q&A, YouTube transcript fetch, link preview/dedup) — `dashboard` LibraryPage
- ✓ **Scheduler** (APScheduler daily digest jobs) and **Gmail/YouTube ingestion** — brain integrations
- ✓ **Gemini/Kimi LLM dispatcher** (`dispatcher.py`) — reusable as the intent→JSON translator
- ✓ **Autopilot approval store + RL governor (RL1–RL5)** — repurposable as the Human-In-The-Loop enforcement gate
- ✓ **Firebase Google auth** (brain Admin SDK verify + dashboard Bearer token) — single-owner auth foundation

### Active

<!-- Signal MVP (personal-first). Hypotheses until shipped. Detail in REQUIREMENTS.md. -->

- [ ] Vector DB foundation powering conceptual search + content dedup/token-cache
- [ ] Knowledge Library with conceptual (embedding) search — the Milestone-1 centerpiece
- [ ] Persistent AI Guide (natural-language Command Bar replacing the brittle keyword `INTENT_MAP`)
- [ ] n8n execution layer: brain translates intent → n8n workflow JSON, injects owner credentials, ingests callbacks
- [ ] "Zen" 70/30 split-screen shell with persistent Panel B and the three Clarity Board views
- [ ] Guided sub-2-minute onboarding: identity box → connect apps → first live 24-hr digest
- [ ] Smart Feeds (YouTube→3 bullets, email/news compression, news dedup, silent queue)
- [ ] Smart Drafts with one-click tone variants, gated by Human-In-The-Loop
- [ ] Routine & Milestone Planner (minimalist "Today's Rhythm")
- [ ] Single-user safety/recovery: Zero-Retention LLM, Layout/Memory Reset, Panic Button

### Out of Scope

<!-- Explicit boundaries with reasoning to prevent re-adding. -->

- **Multi-tenant SaaS isolation** — personal-first; foundation is built tenant-*ready* but not multi-tenant. (Biggest cost/risk; revisit when going commercial.)
- **Billing / subscription tiers / usage metering** ($0/$39/$99) — no external paying users yet.
- **YOLO / Power Mode** (BYO API keys, raw n8n JSON editing, custom-JS node injection, guardrail disable) — RCE/abuse surface; defer to v1.1 after the credential layer is hardened.
- **Apple OAuth** — Google OAuth is sufficient for a single owner in v1.
- **Per-user OAuth broker / encrypted multi-tenant vault** — collapses to the owner's single credential set in personal-first mode.

## Context

- **Workspace:** `apsmono/projects` is a submodule workspace ("personal operating system constellation"). Signal's planning lives in the parent repo's `.planning/`; its code will reuse `solo-leveling` (brain) + `dashboard` and a new n8n layer. Exact repo layout (new submodule vs. extend existing) is decided in Phase 1 planning.
- **Existing backend:** Python 3.13 / FastAPI brain — intent router, Gemini agent layer, autonomous Autopilot loop w/ RL governance, local-first markdown+JSON state with optional Firebase. **Hard single-tenant** today (`ALLOWED_USER_EMAIL`, one shared `_PROJECT_ROOT/library`, single-owner integration tokens).
- **Existing frontend:** static vanilla-JS dashboard, Firebase-auth'd, tab-based command center → GitHub Pages. The persistent 70/30 Zen layout is a structural rebuild, not a restyle.
- **n8n:** already present at repo root (`docker-compose.n8n.yml`); not yet wired to the brain.
- **Architecture analysis:** see `.planning/signal-prd.md` (source PRD) and the capability/reuse map produced during planning. Key finding — the hard foundation (vector DB, single→multi-tenant-ready persistence, credential injection) is net-new regardless of approach; reuse pays off in the feature layer.

## Constraints

- **Architecture**: n8n is the execution engine (firm, PRD §6) — brain becomes the AI/control plane + intent→JSON translator; user-defined integration workflows run as n8n nodes.
- **Tenancy**: Personal-first / single-tenant now, built tenant-*ready* (no design choices that hard-block multi-tenancy later).
- **Reuse**: Maximize reuse of the brain (planning, library, scheduler, dispatcher, RL/approval gate) and dashboard (auth, API patterns, library/Q&A components) before building new.
- **LLM**: Primary provider Gemini (`GEMINI_API_KEY`), per the brain's existing config.
- **Privacy**: Zero-data-retention LLM endpoints; personal data never trains public models.
- **Boundary discipline**: Hard, written ownership line — user-facing integration workflows run in n8n; only the platform's own internal automation runs in the autopilot loop (prevents dual-engine drift).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Personal-first, SaaS-ready later | Removes the largest cost/risk (multi-tenancy, OAuth vault, billing); brain is already single-tenant | — Pending |
| n8n is the firm execution engine | PRD §6 mandate; n8n's node catalog beats bespoke Python per integration | — Pending |
| Reuse-parts hybrid: brain = control/AI plane, n8n = data/execution plane | Foundation is net-new either way; only lever is reusing the mature, tested brain investment | — Pending |
| Milestone 1 = Knowledge Library + conceptual search + AI Guide | Most differentiated, most brain-reuse-heavy slice; proves the value before broadening | — Pending |
| Vector DB is the gating foundation item | Powers BOTH conceptual search and the token-cache/dedup layer; build once, use twice | — Pending |
| Defer YOLO mode + full multi-tenant Panic to v1.1 | RCE/abuse surface; should not ship before the credential layer is hardened | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-29 after initialization (PRD express path → architecture decision)*
