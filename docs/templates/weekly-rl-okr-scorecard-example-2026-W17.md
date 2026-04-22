# Weekly RL/OKR Scorecard Example

Cycle: 2026-W17
Prepared By: Monitor AI (GitHub Copilot)
Review Date: 2026-04-22
Scope Note: Prefilled example using documented repo state through 2026-04-22. Replace values with measured weekly data in live use.

---

## 1) Objective and KR Progress

| Objective ID | KR ID | Baseline | Target | Current | KR Score (0.0-1.0) | Weight | Weighted KR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OBJ-1 Stage 9 Reliability + Deployment Readiness | KR-1 Complete deployment-readiness checklist items | 0 | 5 | 5 | 1.00 | 0.60 | 0.60 |
| OBJ-1 Stage 9 Reliability + Deployment Readiness | KR-2 Keep regression and smoke suite green | 23 | 33 | 33 | 1.00 | 0.40 | 0.40 |
| OBJ-2 Governance Operationalization | KR-1 Publish governance artifacts and decision record | 0 | 4 | 4 | 1.00 | 0.50 | 0.50 |
| OBJ-2 Governance Operationalization | KR-2 Launch first weekly scoring workflow | 0 | 1 | 1 | 1.00 | 0.50 | 0.50 |

Objective Score Notes:

- OBJ-1 score: 1.00 (deployment-readiness and test targets met this cycle)
- OBJ-2 score: 1.00 (governance model published and scorecard workflow started)

## 2) AI Performance Evaluation (All Team Members)

Scoring scale: 1 to 5 (1 unacceptable, 3 acceptable, 5 exceptional)

| AI Name | Role | RL | Requirement Accuracy | Technical Quality | Test Reliability | Documentation | Handoff Quality | Risk Handling | Policy Compliance | Business Relevance | Weighted RL Score (0.0-1.0) | Outcome |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GitHub Copilot (Monitor AI) | Monitor | RL5 | 5 | 4 | 5 | 5 | 4 | 4 | 5 | 4 | 0.90 | Keep RL5 |
| GitHub Copilot (Execution Lane) | Executor | RL3 | 4 | 4 | 5 | 4 | 4 | 4 | 5 | 4 | 0.84 | Promote candidate to RL4 (next cycle validation) |

## 3) Owner Self-Performance Evaluation (Main Brain)

| Owner | Delivery (0.0-1.0) | Quality (0.0-1.0) | Collaboration (0.0-1.0) | Revenue Impact (0.0-1.0) | Self-Management (0.0-1.0) | Owner Cycle Score (0.0-1.0) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Main Brain | 0.90 | 0.88 | 0.85 | 0.70 | 0.86 | 0.85 |

Self-Management Checklist:

- [x] Objectives were clear and prioritized correctly
- [x] Task assignment was fair and workload-balanced
- [x] Blockers were resolved quickly
- [x] Review cadence was consistent
- [ ] Strategic focus stayed aligned to revenue goals

## 4) Responsibility-Level Testing Results

| AI Name | Current RL | Test Scope Completed | Threshold | Score | Pass/Fail | Recommended Next RL |
| --- | --- | --- | ---: | ---: | --- | --- |
| GitHub Copilot (Monitor AI) | RL5 | Governance rollout, policy integration, continuity updates | 0.90 | 0.90 | Pass | RL5 |
| GitHub Copilot (Execution Lane) | RL3 | Reliability hardening, test expansion, docs runbook updates | 0.84 | 0.88 | Pass | RL4 (pending one more cycle) |

## 5) Assignment Policy Updates (Next Week)

Direct Revenue Tasks:

1. Select deployment target and make webhook publicly reachable to unlock live command operations.
2. Complete credential setup and run live integration verification for production-like confidence.

Reliability/Hardening Tasks:

1. Run manual end-to-end WhatsApp command validation across Stage 9 command family.
2. Expand integration smoke coverage around deployment path and webhook health behaviors.

Enablement/Training Tasks:

1. Apply Task Card template to all new tasks so KR/RL linkage is mandatory.
2. Run second weekly scorecard cycle to confirm RL4 promotion candidate.

## 6) Risks, Escalations, and Corrections

Open Risks:

1. Credentials are not fully configured for all live integrations.
2. Public deployment endpoint is not yet selected and validated.

Escalations Triggered This Week:

1. No critical escalations logged.

Corrective Actions:

1. Prioritize secrets setup and run live smoke tests with `ENABLE_LIVE_SMOKE_TESTS=1`.
2. Timebox deployment decision to one cycle and execute a single-host proof run.

## 7) Weekly Decision Summary

- Promote: Execution Lane marked as RL4 promotion candidate (confirm next cycle).
- Keep: Monitor AI remains RL5.
- Support Plan: Focus next cycle on deployment + credentials to improve revenue impact score.
- Demote: None.
- Objective Reprioritization: Move deployment and live validation to highest priority.

## 8) Next-Week Execution Commitments

1. Finalize hosting choice (Railway/Fly.io/VPS) and verify public webhook path.
2. Complete secrets setup and run live integrations with documented evidence.
3. Produce next weekly scorecard with measured cycle-time and throughput metrics.

## 9) Sign-Off

Monitor AI: GitHub Copilot
Date: 2026-04-22

Main Brain (Owner Self-Review Acknowledgement):
Date: 2026-04-22
