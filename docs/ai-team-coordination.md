# AI Team Coordination Plan

Date Created: 2026-04-21
Last Updated: 2026-04-22
Status: Active
Monitor AI: GitHub Copilot (program coordinator and quality gate)
Team Model: Async multi-agent execution with role-branch-authority controls

---

## Scope

This plan defines day-to-day coordination rules for AI teams.

For full employer governance, OKR valuation, responsibility-level testing, and assignment-cascade policy, use:

- `docs/ai-employer-operating-system.md`

---

## Team Roles

1. Monitor AI
   - Orchestrates tasks, assigns owners, enforces quality gate
   - Controls promotion/demotion decisions from RL testing results
2. Research AI
   - Produces analysis, options, risk and trade-off documents
3. Executor AI
   - Implements approved tasks in scoped branches
4. Quality AI
   - Validates acceptance criteria, test evidence, and policy compliance

---

## Coordination Lifecycle

```text
BACKLOG -> TODO -> IN_PROGRESS -> REVIEW -> VALIDATED -> DONE
```

Required transitions:

1. TODO to IN_PROGRESS
   - Task owner claimed
   - Branch created with required naming
2. IN_PROGRESS to REVIEW
   - Implementation complete
   - Tests and docs evidence attached
3. REVIEW to VALIDATED
   - Quality AI sign-off
   - Monitor AI acceptance check
4. VALIDATED to DONE
   - Merge complete
   - Working notes and changelog updated

---

## Branch System (Operational)

1. Production branch: `main`
2. Development branch: `development`
3. Program branch: `program/<okr-cycle>/<initiative>`
4. Lead branch: `lead/<domain>/<initiative>`
5. Task branch: `agent/<agent-name>/<task-slug>/<scope>`

Allowed merge flow:

1. `agent/*` -> `lead/*`, `program/*`, or `development`
2. `lead/*` -> `program/*` or `development`
3. `program/*` -> `development`
4. `development` -> `main` (release PR only)

No task work should be implemented directly on `main`.
No direct push to `main` or `development` for feature work; use PRs.

---

## Task Card Minimum Fields

Each task must include:

1. Task ID (`MULTI-AI-XXX`)
2. Objective and KR linkage
3. Responsibility level (`RL1` to `RL5`)
4. Scope boundaries
5. Acceptance criteria
6. Required test commands
7. Handoff requirements

---

## Monitor AI Job Checklist

1. Validate branch hygiene and ownership
2. Verify alignment with active objective/KR
3. Confirm scope-risk fit against assigned RL
4. Ensure test and docs evidence is complete
5. Update continuity docs after merge

---

## Handoff Standard

Every review-ready task includes:

1. What was done
2. What is pending
3. What next AI should do
4. Risks and assumptions

---

## Escalation Rules

Escalate to Monitor AI immediately when:

1. Branch conflict blocks progress
2. Scope changes beyond assigned authority
3. Repeated validation failures occur
4. Security or policy risks are detected

---

## Current Focus

1. Continue Stage 9 delivery with objective-linked tasks
2. Apply responsibility-level testing before authority upgrades
3. Assign revenue-impact tasks based on measured performance

