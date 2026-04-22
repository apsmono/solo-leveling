# AI Employer Operating System

Created: 2026-04-22
Status: Active
Owner: Monitor AI / Project Manager / Main Brain

---

## Purpose

This document defines how the AI employer layer manages a multi-AI company model in this repository:

1. Git branch system for parallel work and safe review-before-merge
2. Employer role responsibilities to monitor AI employee delivery
3. OKR-based performance management and valuation
4. Responsibility-level testing and scoring before authority upgrades
5. Revenue-oriented policy adjustment based on measured results
6. Cascading task assignment from top-level AI to lower-level AI roles

---

## 1) Company Role, Branch, Authority Model

### Role hierarchy

1. Main Brain (Owner/Employer)
2. Monitor AI (Program Manager + Quality Gate)
3. Lead AI (Domain lead per workstream)
4. Specialist AI (Research, Executor, QA, Docs)

### Branch authority model

1. `main`
   - Authority: Main Brain + Monitor AI only
   - Rule: no direct task implementation; merge-only after validation
2. `program/<okr-cycle>/<initiative>`
   - Authority: Monitor AI
   - Purpose: integrate multiple approved task branches for one OKR initiative
3. `lead/<domain>/<initiative>`
   - Authority: Lead AI
   - Purpose: coordinate related task branches in one domain
4. `agent/<agent-name>/<task-slug>/<scope>`
   - Authority: assigned Specialist AI
   - Purpose: single-task execution branch with full traceability

### Merge policy

1. `agent/*` can merge only into `lead/*` or `program/*`
2. `lead/*` can merge only into `program/*`
3. `program/*` can merge into `main` after Monitor AI validation
4. Every merge requires:
   - acceptance criteria check
   - test evidence
   - docs/changelog update
   - handoff summary

---

## 2) Employer Jobs and Monitoring Tasks

## Monitor AI mandatory job list

1. Task intake and decomposition
2. Assignment by responsibility level
3. Workload balancing across active AIs
4. Review gate enforcement (test, docs, risk)
5. Weekly OKR scoring and authority recalibration
6. Revenue impact audit for all completed tasks

## Daily monitoring checklist

1. Check task board state: `TODO`, `IN_PROGRESS`, `REVIEW`, `VALIDATED`, `DONE`
2. Check branch hygiene: stale branches, ownership conflicts, unreviewed PRs
3. Check quality signals: test pass rate, rollback risk, docs completeness
4. Check delivery velocity: cycle time and blocked-time causes
5. Check business relevance: does current work map to active revenue OKRs?

## Escalation triggers

1. Two failed validations in a row for the same AI on same responsibility level
2. Missed handoff details that block next agent
3. Unauthorized changes outside branch scope
4. Repeated tasks with no measurable OKR contribution

---

## 3) Task Breakdown and Responsibility-Level System

## Unified task schema

Use this schema for every task card and branch assignment.

| Field | Meaning |
| --- | --- |
| Task ID | Unique ID (`MULTI-AI-XXX`) |
| Objective Link | Which objective this task supports |
| KR Link | Which key result it moves |
| Revenue Link | Direct, indirect, or none |
| Scope | Files/systems allowed |
| Risk Tier | Low, Medium, High |
| Responsibility Level | RL1 to RL5 |
| Owner AI | Assigned AI |
| Reviewer AI | Required reviewer |
| Test Protocol | Exact test commands/checks |
| Definition of Done | Observable completion criteria |
| Handoff Required | Yes/No (default Yes) |

## Responsibility levels (RL)

1. `RL1 - Assisted`:
   - Small, low-risk edits
   - Requires template-driven execution
   - Review required for every commit
2. `RL2 - Independent Task`:
   - Single-subsystem tasks
   - Must run required tests and provide evidence
3. `RL3 - Cross-Module Integrator`:
   - Multi-file and integration-impact tasks
   - Must include risk notes and rollback path
4. `RL4 - Lead Executor`:
   - Multi-task orchestration and design decisions
   - Can assign RL1-RL3 tasks to subordinate AIs
5. `RL5 - Program Lead`:
   - OKR program ownership
   - Can approve lead-branch merges into program branch (final gate still Monitor AI)

---

## 4) OKR System Definition

## Objective structure

Each cycle defines 3 to 5 objectives max.

Objective template:

- Objective statement: qualitative, directional, business-relevant
- Owner: Monitor AI or delegated Lead AI
- Horizon: monthly or quarterly
- Key results: 3 to 5 measurable KRs
- Revenue tag: direct or support

## Key result scoring model

KR score is normalized from 0.0 to 1.0 using actual vs target:

$$KR_{score} = \min\left(1, \max\left(0, \frac{actual - baseline}{target - baseline}\right)\right)$$

Weighted objective score:

$$Objective_{score} = \sum_{i=1}^{n}(KR_{score,i} \times weight_i)$$

Overall AI performance score for cycle:

$$AI_{cycle} = 0.40 \times Delivery + 0.25 \times Quality + 0.20 \times Collaboration + 0.15 \times RevenueImpact$$

All component scores are normalized to `[0, 1]`.

## Owner self-performance evaluation

The Main Brain (owner/employer) is also evaluated each cycle using the same score components plus a self-management score.

Owner cycle score:

$$Owner_{cycle} = 0.30 \times Delivery + 0.20 \times Quality + 0.15 \times Collaboration + 0.15 \times RevenueImpact + 0.20 \times SelfManagement$$

`SelfManagement` measures:

1. Objective clarity and prioritization quality
2. Assignment fairness and workload realism
3. Decision speed on blockers and escalations
4. Consistency of review cadence and follow-through

This enables explicit self-review by the owner and keeps leadership performance measurable.

---

## 5) Responsibility-Level Testing System

## Evaluation keys

Every AI is tested against these keys:

1. Requirement accuracy
2. Technical quality
3. Test reliability
4. Documentation traceability
5. Handoff quality
6. Risk handling
7. Policy compliance (branch, authority, security)
8. Business relevance to OKR/revenue
9. Self-management quality (owner role only)

## Test protocol by level

1. RL1 test:
   - 3 small scoped tasks
   - pass threshold `>= 0.75`
2. RL2 test:
   - 2 medium tasks in one module
   - pass threshold `>= 0.80`
3. RL3 test:
   - 2 cross-module tasks + 1 incident simulation
   - pass threshold `>= 0.84`
4. RL4 test:
   - lead one initiative with at least 2 subordinate handoffs
   - pass threshold `>= 0.88`
5. RL5 test:
   - own one OKR cycle segment and recover one blocker
   - pass threshold `>= 0.90`

## Scoring rubric

Each evaluation key is scored 1 to 5.

- 1 = unacceptable
- 2 = inconsistent
- 3 = acceptable
- 4 = strong
- 5 = exceptional

Responsibility-level test score:

$$RL_{score} = \frac{\sum(score_i \times weight_i)}{5}$$

`weight_i` sum must equal `1.0`.

Recommended default weights:

- Requirement accuracy: 0.15
- Technical quality: 0.20
- Test reliability: 0.15
- Documentation traceability: 0.10
- Handoff quality: 0.10
- Risk handling: 0.10
- Policy compliance: 0.10
- Business relevance: 0.10

Owner-specific weight profile:

- Requirement accuracy: 0.10
- Technical quality: 0.15
- Test reliability: 0.10
- Documentation traceability: 0.10
- Handoff quality: 0.10
- Risk handling: 0.10
- Policy compliance: 0.10
- Business relevance: 0.10
- Self-management quality: 0.15

---

## 6) Evaluation Outcomes and Policy Adjustment

## Promotion and demotion rules

1. Promote one responsibility level when:
   - current RL test score is above threshold for two consecutive cycles
   - no critical policy violation in same period
2. Freeze level when:
   - score is within 0.03 below threshold
   - corrective plan exists and is tracked
3. Demote one level when:
   - score is below threshold by more than 0.05
   - or a critical policy violation occurs

## Revenue-priority policy update

When cycle evaluation is complete:

1. AIs with highest `RevenueImpact` and `Delivery` are assigned direct revenue tasks first
2. AIs with weaker `RevenueImpact` but strong `Quality` are assigned reliability and hardening tracks
3. AIs below threshold are routed to bounded-scope enablement tasks until retested

This ensures task assignment is evidence-based and tied to project earnings goals.

---

## 7) Assignment Cascade Policy (Top-Down Delegation)

## Main Brain to Monitor AI

1. Set strategic objective and revenue direction
2. Approve OKR set and target ranges
3. Authorize program branches for each initiative

## Monitor AI to Lead AI

1. Decompose objectives into initiative bundles
2. Assign each bundle to a lead with clear KR ownership
3. Define branch scope and authority limits

## Lead AI to Specialist AI

1. Break bundles into executable tasks using unified schema
2. Assign task to AI based on validated RL score
3. Enforce branch naming and review chain
4. Collect handoff and pass to reviewer

## Reviewer AI back to Monitor AI

1. Approve, request changes, or reject with reasons
2. Report risk and policy compliance score
3. Return validation status for merge gate decision

---

## 8) Workload Policy

1. Maximum active tasks per AI:
   - RL1 to RL2: 1 active task
   - RL3: 2 active tasks
   - RL4 to RL5: 3 active tasks
2. No AI can accept a new task while carrying one blocked task older than 24h without Monitor override
3. Priority order for assignment:
   - P1 revenue blockers
   - P1 reliability/security blockers
   - P2 feature delivery tied to active KR
   - P3 optimization/documentation

---

## 9) Operating Cadence

1. Daily: branch + progress + blocker review
2. Weekly: KR score update and RL evaluation
   - Includes explicit owner self-review score entry
3. Monthly: authority adjustments and workload rebalance
4. Quarterly: objective reset and policy tuning

---

## 10) Immediate Adoption Checklist

- [ ] Add this system to active coordination workflow
- [ ] Tag each active task with RL and KR links
- [ ] Start weekly RL testing for all active AIs
- [ ] Start cycle scoring dashboard in task docs
- [ ] Review and adjust assignment policy based on first cycle results
