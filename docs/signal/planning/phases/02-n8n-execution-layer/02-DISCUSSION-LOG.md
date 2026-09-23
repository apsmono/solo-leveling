# Phase 2: n8n Execution Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-30
**Phase:** 02-n8n-execution-layer
**Areas discussed:** Workflow generation, Credential injection, Approval gate (HITL), Execution feedback

---

## Workflow generation

| Option | Description | Selected |
|--------|-------------|----------|
| Curated templates, brain fills | Brain keeps vetted n8n JSONs; dispatcher matches intent→template and fills params. Predictable/safe, no arbitrary nodes. | |
| Hybrid (template + LLM params) | Intent picks a template skeleton; LLM fills params/expressions. Flexible but bounded by vetted skeletons. | ✓ |
| LLM generates full JSON each time | Dispatcher emits a complete workflow JSON per intent. Most flexible, higher failure/abuse surface. | |

**User's choice:** Hybrid (template + LLM params)
**Notes:** Bounds execution to known-good skeletons while keeping flexibility. Consistent with deferring raw-JSON/YOLO mode.

### Follow-up: no template match

| Option | Description | Selected |
|--------|-------------|----------|
| Soft decline + note it | AI Guide says it can't do that yet; logs the unmet intent as a future-template candidate. | ✓ |
| Fall back to full LLM-generated JSON | Generate a workflow from scratch for the unmatched intent. Reintroduces unvalidated-JSON risk. | |
| Queue for owner confirmation | Draft a best-effort workflow, ask owner to confirm before running. | |

**User's choice:** Soft decline + note it

---

## Credential injection

| Option | Description | Selected |
|--------|-------------|----------|
| Brain populates n8n cred store via API | Brain pushes owner creds into n8n once; workflows reference by ID. Owner never sees keys. | ✓ |
| Ephemeral per-execution injection | Brain injects fresh tokens at trigger time; nothing persists in n8n. Smaller standing surface, more overhead. | |
| You decide | Let research/planner choose based on n8n API + token refresh. | |

**User's choice:** Brain populates n8n credential store via API

### Follow-up: credential sync timing

| Option | Description | Selected |
|--------|-------------|----------|
| At connect time | Provision the n8n credential when the owner connects an app; re-sync on token refresh. First run is instant. | ✓ |
| Lazily on first use | Provision when a workflow first needs it. Nothing in n8n until used; first run pays setup cost. | |
| You decide | Let research/planner pick. | |

**User's choice:** At connect time

---

## Approval gate (HITL)

| Option | Description | Selected |
|--------|-------------|----------|
| Gate side-effecting actions only | Reads run free; send/post/modify pass through the RL approval gate first. | ✓ |
| Gate every execution | Owner approves every run. Safest, but noisy and counter to the Zen identity. | |
| No gate in Phase 2 | Phase 2 just executes; defer all HITL to Phase 7. | |

**User's choice:** Gate side-effecting actions only

### Follow-up: approval surface

| Option | Description | Selected |
|--------|-------------|----------|
| AI Guide | Approval requests surface inline in the persistent AI Guide. | ✓ |
| Telegram | Reuse the brain's Telegram command channel for approvals. | |
| Both | Surface in AI Guide and push to Telegram. | |

**User's choice:** AI Guide

---

## Execution feedback

| Option | Description | Selected |
|--------|-------------|----------|
| Silent unless it needs me | No progress noise; only surface on failure/approval. Soft failure message, one auto-retry first. | ✓ |
| Lightweight progress in AI Guide | Small running/done indicator per run + soft errors. | |
| Verbose status feed | Full execution log visible. Counter to calm philosophy. | |

**User's choice:** Silent unless it needs me (one auto-retry)

### Follow-up: on failure (after auto-retry)

| Option | Description | Selected |
|--------|-------------|----------|
| Inform + one-tap retry | Plain-language message + single Retry affordance, no stack traces. | |
| Just inform | Soft message only, no action. | |
| Inform + suggest a fix | Soft message + likely cause/next step (e.g. reconnect Gmail). Needs error→cause mapping. | ✓ |

**User's choice:** Inform + suggest a fix

---

## Claude's Discretion

- n8n trigger/callback transport (sync REST vs async webhook) for status ingestion.
- Where template skeletons are stored/versioned and the intent→skeleton matching mechanism.
- RL level mapping for a "side-effecting n8n run" within the existing governor.
- n8n REST auth mechanism (API key vs basic auth) and `.env` placement.
- Token-refresh detection and the n8n credentials-API call shape.
- Whether/how to guarantee no partial side-effects on mid-run failure (pragmatic, not a hard gate this phase).

## Deferred Ideas

- N8N-03 catalog of pre-built workflow templates → Phases 6/7.
- Telegram (and other channels) as additional approval surfaces → later enhancement.
- YOLO / Power Mode → v1.1.
- Multi-tenant credential broker / encrypted vault → commercial milestone.
