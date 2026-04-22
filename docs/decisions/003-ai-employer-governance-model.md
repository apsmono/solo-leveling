# Decision 003: Adopt AI Employer Governance Model

Date: 2026-04-22
Status: Approved
Owner: Monitor AI

## Context

The repository already supports multi-AI collaboration, but role authority, branch governance, responsibility-level advancement, and OKR-linked performance valuation were not formally codified in one enforceable model.

To scale safely and align execution to project earnings goals, the team needs a clear employer system for:

1. Branch-level authority and review-before-merge controls
2. Role-based delegation and task ownership
3. Responsibility-level testing and promotion policy
4. OKR scoring tied to delivery quality and revenue impact

## Decision

Adopt the AI employer governance model defined in `docs/ai-employer-operating-system.md` as the canonical policy for multi-AI operations.

This includes:

1. Role hierarchy (Main Brain -> Monitor AI -> Lead AI -> Specialist AI)
2. Branch authority model (`program/*`, `lead/*`, `agent/*`) with controlled merge flow to `main`
3. Unified task schema with KR and revenue linkage
4. Responsibility-level testing system (`RL1` to `RL5`) with weighted scoring and thresholds
5. OKR valuation formula and cycle-based assignment adjustments

## Why

1. Improves traceability and control for concurrent AI execution
2. Reduces merge conflicts and unauthorized scope drift
3. Creates measurable basis for assigning higher-stakes tasks
4. Aligns AI allocation with outcomes that influence revenue and reliability

## Consequences

Positive:

1. More predictable assignment and review flow
2. Better quality gates and clearer escalation path
3. Evidence-based promotion/demotion and workload balancing

Costs / risks:

1. Slightly higher coordination overhead per task
2. Requires consistent weekly scoring discipline from Monitor AI

## Implementation Notes

1. `docs/ai-team-coordination.md` remains operational guidance and now references the employer model.
2. Future task docs should include responsibility level and KR linkage fields.
3. Policy tuning should occur after the first full weekly scoring cycle.
