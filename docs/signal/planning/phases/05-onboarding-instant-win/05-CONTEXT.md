# Phase 5: Onboarding + Instant Win - Context

**Gathered:** 2026-05-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the guided sub-2-minute first-run experience. The Identity Box captures free text → AI Guide parses it into a working profile → guided app connection via n8n credential layer → first live 24-hour mini-digest as the "Instant Win."

**In scope (ONB-02, ONB-03, ONB-04):**
- **ONB-02** — Identity Box captures free text; AI Guide parses into working profile / context templates
- **ONB-03** — Guided integration: Guide highlights and connects relevant apps via brain's existing integrations
- **ONB-04** — End of onboarding: generate and display first live 24-hour mini-digest (< 2 min total)

**Explicitly NOT in this phase:**
- n8n credential layer itself → Phase 2 (dependency — must exist before this phase)
- Full Smart Feeds pipelines → Phase 6
- Safety/Recovery (Panic Button, Reset) → Phase 9
- Multi-tenant profile isolation → out of scope
- Profile settings page → future phase

</domain>

<decisions>
## Implementation Decisions

### Identity Box & Profile
- **D-01:** Input format: **1 initial prompt + AI follow-up** — conversational, the AI asks a follow-up if it needs more detail. Not a multi-field form.
- **D-02:** Profile output: **Structured JSON** (role, pain_points, connected_apps, context_templates) stored in the brain. The Guide shows a **confirmation card in Panel A** with bullet points summarizing what it understood.
- **D-03:** Profile confirmation card: owner can **edit or confirm** before proceeding. After confirming, profile changes require Guide chat.

### Onboarding Flow
- **D-04:** Step sequence: **3-step linear wizard** rendered in Panel A: Identity Box → Confirmation + App Connect → Instant Win digest.
- **D-05:** App connect shows **only the 2-3 most relevant apps** based on the parsed profile. Each gets a Connect button. Not all supported apps.
- **D-06:** App connection is **skippable** — "Skip for now" link. Digest works with whatever data is available.
- **D-07:** Progress indicator: **step indicator at top of Panel A** ("Step 1 of 3" or dots).

### First-Run Detection & Re-entry
- **D-08:** Detection: **backend profile check** — no profile exists → onboarding. Profile exists → Zen shell. No localStorage flag.
- **D-09:** Return visits: **skip straight to Zen shell**. Onboarding is one-time.
- **D-10:** Interruption handling: **resume from last completed step**. Backend tracks onboarding progress per step.
- **D-11:** Profile editing post-onboarding: **Guide chat only** for now. No settings page.

### Instant Win Digest
- **D-12:** Digest format: **Context Nest card** — same pattern as Phase 4 stream cards, 3 bullets summarizing the last 24 hours.
- **D-13:** Cold-start fallback: **capability preview** — "Here's what I'll do for you" with example bullets based on the profile. Honest, sets expectations.
- **D-14:** Data sources: **connected sources only** (Gmail if connected, YouTube if connected, library entries, news). No public API fallback.
- **D-15:** Completion: Guide says **"You're all set. Signal is now watching your streams."** + subtle "Get started" button transitions to full Zen shell.

### Claude's Discretion
- Exact Identity Box placeholder text and AI follow-up prompt wording
- Profile JSON schema field names and structure
- Step indicator animation style
- Context Nest card styling for the digest (reuse Phase 4 card pattern)
- OAuth flow error handling during app connect step
- Capability preview content generation from profile data

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project-level context
- `.planning/PROJECT.md` — Signal product context, personal-first constraint
- `.planning/REQUIREMENTS.md` — REQ-IDs ONB-02, ONB-03, ONB-04
- `.planning/ROADMAP.md` — Phase 5 goal, success criteria, dependencies

### Phase 3 — AI Guide foundation (authoritative)
- `.planning/phases/03-knowledge-library/03-CONTEXT.md` — AI Guide panel architecture, intent parsing via Gemini, Guide chat state lifted to DashboardPage
- `dashboard/src/components/guide/AIGuidePanel.tsx` — persistent Guide panel (locked Panel B)
- `solo-leveling/src/agents/dispatcher.py` — `run_agent()` reused for profile parsing
- `solo-leveling/src/core/intent_parser.py` — LLM structured output pattern (reuse for profile extraction)

### Phase 4 — Zen shell foundation (authoritative)
- `.planning/phases/04-zen-shell/04-CONTEXT.md` — Zen shell architecture, Context Nest pattern, Clarity Board views
- `dashboard/src/components/zen/ZenShell.tsx` — 70/30 shell (onboarding renders in Panel A)
- `dashboard/src/components/zen/ContextNest.tsx` — stream card pattern (reuse for digest card)

### Phase 1 — Auth foundation
- `.planning/phases/01-data-auth-foundation/` — Firebase Google OAuth session persistence

### Phase 2 — n8n credential layer (dependency)
- `.planning/phases/02-n8n-execution-layer/` — credential injection, app connect flow (must exist before Phase 5 executes)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AIGuidePanel.tsx` — locked Panel B; onboarding UI must render in Panel A or overlay, not replace the Guide
- `DashboardPage.tsx` — owns Guide chat state; onboarding wizard state should live here too
- `ZenShell.tsx` — 70/30 layout; onboarding replaces Panel A content temporarily
- `ContextNest.tsx` — stream card pattern (3 bullets); reuse for the digest card
- `run_agent()` in `dispatcher.py` — Gemini structured output; reuse for profile parsing from free text
- `intent_parser.py` — LLM JSON output pattern; adapt for profile extraction prompt

### Established Patterns
- Firebase Google OAuth — Phase 1 session persistence; app connect reuses the same OAuth flow
- `require_auth` FastAPI dependency — onboarding endpoints must follow same auth pattern
- Clarity Board view switching (Phase 4) — onboarding is a temporary "view" that replaces Panel A content

### Integration Points
- Onboarding wizard state: lifted to `DashboardPage` level (same pattern as Guide chat state)
- Profile storage: brain backend (new endpoint `/api/v1/profile` or extend existing user store)
- Onboarding progress tracking: brain backend (new field or endpoint for step tracking)
- App connect: triggers OAuth flows via brain's existing integration layer
- Digest generation: brain backend queries connected data sources, returns compressed summary

</code_context>

<specifics>
## Specific Ideas

- The Identity Box initial prompt should be warm and inviting: "Tell me what you do and what overwhelms you" — not clinical
- The AI follow-up should feel natural, not like a form validation error: "That's helpful — could you also tell me which apps you spend the most time in?"
- Profile confirmation card in Panel A should use the same card styling as Context Nest stream cards for visual consistency
- The "Get started" button at the end of onboarding should feel like a natural conclusion, not a hard cutoff
- If the owner connects Gmail during onboarding, the digest should include a real email summary — that's the "wow" moment

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-onboarding-instant-win*
*Context gathered: 2026-05-31*
