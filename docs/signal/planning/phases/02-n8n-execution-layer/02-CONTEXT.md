# Phase 2: n8n Execution Layer - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire the brain to n8n as the firm execution engine and make its failures owner-safe.
This phase delivers, for the single owner:

- **N8N-01** — translate a user intent into an n8n workflow and trigger it via the n8n REST API
- **N8N-02** — inject the owner's OAuth credentials into the corresponding n8n nodes from the backend (owner never handles raw keys/webhooks)
- **N8N-04** — ingest n8n execution status and webhook callbacks back into the brain
- **INFRA-05** — an error-abstraction layer that converts technical backend/n8n errors into soft AI-Guide messages

**Explicitly NOT in this phase:**
- **N8N-03** (pre-built n8n workflow templates that power the feed/draft pipelines) — belongs to the Smart Feeds / Smart Drafts phases (6/7).
- YOLO / Power Mode (BYO API keys, raw n8n JSON editing, custom-JS nodes, guardrail disable) — deferred to v1.1 per PROJECT.md Out of Scope.
- Multi-tenant credential broker / encrypted per-user vault — personal-first collapses to the owner's single credential set.

</domain>

<decisions>
## Implementation Decisions

### Workflow generation (intent → n8n workflow)
- **D-01:** Use a **hybrid** strategy. The Gemini dispatcher matches an owner intent to a **vetted n8n workflow template skeleton**, then the LLM fills the parameters/expressions for that skeleton. Execution stays bounded to known-good skeletons — no fully unvalidated, LLM-authored workflow JSON runs in v1. (Consistent with deferring raw-JSON editing / YOLO mode.)
- **D-02:** **No template match → soft decline.** When an intent matches no skeleton, the AI Guide tells the owner it can't do that one *yet* and **logs the unmet intent** as a candidate for a future template. Do NOT silently fall back to full LLM-generated JSON, and do NOT auto-run a best-effort workflow.
- **D-03:** The starter set of template skeletons is intentionally small in this phase — just enough to satisfy the N8N-01/N8N-04 success criteria end-to-end (e.g. at least one read-only and one side-effecting example). N8N-03 expands the catalog later.

### Credential injection (N8N-02)
- **D-04:** The brain **populates n8n's own credential store via the n8n API** and workflows reference credentials **by ID**. The owner never sees or pastes keys/webhooks. Tokens live (encrypted at rest) inside n8n rather than being re-injected inline on every run.
- **D-05:** **Sync at connect time.** When the owner connects/authorizes an app (onboarding or settings), the brain immediately provisions the matching n8n credential, and **re-syncs on token refresh**. First workflow run for an integration is instant — n8n already holds a valid credential.
- **D-06:** The owner OAuth tokens being injected are the ones already held by the brain's existing integration clients (`gmail`, `gdrive`, `github`, `notion`, `telegram`, `discord`). Reuse those token sources — do not introduce a parallel credential store in the brain.

### Approval gate — Human-In-The-Loop (reuses RL governor)
- **D-07:** **Gate side-effecting actions only.** Read-only runs (fetch, summarize, dedup, status) execute freely. Any workflow that **sends, posts, or modifies** the owner's data/accounts must pass through the **existing RL approval gate** before n8n runs it.
- **D-08:** **Approval prompts surface inline in the AI Guide** (the persistent Phase-3 surface). One calm place for approvals — not a separate channel in v1. (Telegram as an additional channel is a possible later enhancement, not required here.)

### Execution feedback & failure handling (N8N-04, INFRA-05)
- **D-09:** **Silent unless it needs the owner.** No run-by-run progress noise (Zen/calm identity). The owner is only surfaced to when a run **fails** or **needs approval/input**. Successful runs are ingested quietly.
- **D-10:** **One automatic retry** on failure before bothering the owner. If the retry also fails, surface a **soft AI-Guide message** — plain language, **no stack traces**.
- **D-11:** The failure message **informs + suggests a likely fix** (e.g. "your Gmail connection may have expired — reconnect?"). This implies an error→cause mapping in the abstraction layer (INFRA-05), at least for the common, owner-actionable cases (expired/revoked credential, integration not connected, n8n unreachable).

### Claude's Discretion
- Exact n8n trigger/callback transport (synchronous REST trigger vs async webhook callback) for ingesting execution status (N8N-04) — choose based on the n8n API and latency/UX; the *owner-visible* behavior (silent success, soft failure) is fixed by D-09/D-10.
- Where template skeletons are stored and versioned (brain repo as versioned JSON vs n8n saved workflows), and the intent→skeleton matching mechanism inside the dispatcher.
- RL level mapping (which RL1–RL5 level a "side-effecting n8n run" maps to) within the existing governor.
- n8n REST authentication mechanism (n8n public API key vs basic auth) and where its base URL / API key live in `.env`.
- Token-refresh detection and the exact n8n credentials-API calls used to create/update credentials.
- How (and whether) to guarantee no partial side-effects when a side-effecting workflow fails mid-run — handle pragmatically; not a hard gate for this phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product & architecture mandate
- `.planning/PROJECT.md` — n8n = firm execution engine; brain = control/AI plane; boundary discipline (user-facing integration workflows run in n8n, only internal automation in the autopilot loop); owner never handles raw keys; YOLO/multi-tenant deferred.
- `.planning/signal-prd.md` §6 — the n8n-as-execution-engine mandate and the credential-injection requirement.
- `.planning/ROADMAP.md` → "Phase 2: n8n Execution Layer" — goal, success criteria, `Depends on: Phase 1`, `Mode: mvp`.
- `.planning/REQUIREMENTS.md` — N8N-01, N8N-02, N8N-04, INFRA-05 (and N8N-03 marked as a later phase).

### Locked decisions inherited from Phase 1
- `.planning/phases/01-data-auth-foundation/01-CONTEXT.md` — backend extends `solo-leveling`; **shared Postgres** serves both n8n and pgvector; single `owner_id` tenancy; Firebase Google auth reuse.

### Infrastructure
- `docker-compose.n8n.yml` (repo root) — n8n service (`n8nio/n8n:latest`, basic auth, `WEBHOOK_URL`/`N8N_PORT=5678`, `N8N_AI_ENABLED=true`) and the shared `pgvector/pgvector:pg16` Postgres. This is the n8n the brain wires to.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `solo-leveling/src/agents/dispatcher.py` — the Gemini/Kimi LLM dispatcher; reuse as the intent→template-match + parameter-fill translator (D-01).
- `solo-leveling/src/core/router.py` — intent detection/dispatch; the entry point where an owner intent is routed toward the n8n execution path.
- `solo-leveling/src/autopilot/governor.py` + `solo-leveling/src/api/autopilot.py` — RL governor (RL1–RL5) and approval surface; reuse as the HITL gate for side-effecting workflows (D-07).
- `solo-leveling/src/integrations/{gmail,gdrive,github,notion,telegram,discord}/client.py` — hold the owner's OAuth tokens; these are the credential sources synced into n8n (D-04, D-06).
- `solo-leveling/src/integrations/telegram/webhook.py` — existing inbound webhook pattern; analog for ingesting n8n callbacks (N8N-04).

### Established Patterns
- Brain is a single FastAPI process; new n8n-client / execution modules live under `solo-leveling/src/` and register on `src/app.py` (per Phase 1's "backend home" lock).
- Local-first state (markdown `library/` + JSON in `data/`) with optional Firebase — execution status/log persistence should follow the same local-first shape.
- Integration clients are thin per-service `client.py` modules — a new `integrations/n8n/client.py` (REST + credentials API) fits this convention.

### Integration Points
- New n8n REST client → triggers workflows and reads execution status (N8N-01, N8N-04).
- n8n credentials API ← brain pushes owner tokens at connect time (N8N-02, D-05).
- Inbound n8n webhook/callback endpoint on the FastAPI app → ingests execution results (N8N-04).
- Error-abstraction layer sits between raw n8n/backend errors and the AI Guide reply path (INFRA-05, D-10/D-11).
- Shared Postgres (from Phase 1) is available if execution records need SQL persistence.

</code_context>

<specifics>
## Specific Ideas

- Soft-failure message example the owner should experience: *"That didn't work — your Gmail connection may have expired. Reconnect?"* with a one-tap retry, never a stack trace (D-10/D-11).
- Phase must prove the success criteria end-to-end with at least one **read-only** workflow (runs free) and one **side-effecting** workflow (passes the approval gate), so both D-07 branches are exercised.

</specifics>

<deferred>
## Deferred Ideas

- **N8N-03 — catalog of pre-built workflow templates** for the feed/draft pipelines → Smart Feeds (Phase 6) / Smart Drafts (Phase 7). Phase 2 builds only the minimal skeleton set needed to prove the pipeline.
- **Telegram (and other channels) as additional approval surfaces** → possible enhancement; v1 approvals are AI-Guide-only (D-08).
- **YOLO / Power Mode** (raw n8n JSON editing, BYO keys, custom-JS nodes) → v1.1, after the credential layer is hardened (PROJECT.md Out of Scope).
- **Multi-tenant credential broker / encrypted per-user vault** → revisit when going commercial; personal-first uses the owner's single credential set.

</deferred>

---

*Phase: 02-n8n-execution-layer*
*Context gathered: 2026-05-30*
