# Phase 4: Zen Shell + Clarity Board - Context

**Gathered:** 2026-05-30
**Status:** Executing (Wave 1 — shell scaffold)

<domain>
## Phase Boundary

Build the structural 70/30 Zen workspace on top of Phase 3's AI Guide panel and Knowledge Library.

**In scope (ZEN-01..04, GUIDE-04):**
- **ZEN-01** — asymmetric 70/30 split: Panel A Clarity Board + locked Panel B AI Guide
- **ZEN-02** — Core Dashboard Critical Focus Block (max 5 tasks, calm empty state)
- **ZEN-03** — Context Nest stream cards with exactly 3 single-sentence bullets
- **ZEN-04** — clean switching between Core Dashboard / Knowledge Library / Routine Planner
- **GUIDE-04** — contextual action buttons adapt to active view / selected card

**NOT in this phase:**
- Live Smart Feeds pipelines (email/news/YouTube) → Phase 6
- Onboarding / Instant Win → Phase 5
- Full Telegram Mini App layout → later polish

</domain>

<decisions>
## Implementation Decisions

- **D-01:** Reuse Phase 3 `AIGuidePanel` as locked Panel B — no rewrite, only reposition into `ZenShell`.
- **D-02:** Primary navigation collapses to 3 Clarity Board views; legacy tabs (graph, timeline, …) move to **More tools** overlay.
- **D-03:** Context Nest uses `/library/recent` when available; demo cards fill gaps until Phase 6 feeds land.
- **D-04:** Contextual actions render inside the Guide panel (GUIDE-04), driven by `useZenContextualActions` hook.

</decisions>
