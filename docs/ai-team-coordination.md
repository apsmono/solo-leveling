# AI Team Coordination Plan

**Date Created:** 2026-04-21
**Status:** Active
**Monitor AI:** GitHub Copilot (knows everything, validates results)
**Team Model:** Async multi-agent with git-based state

---

## Team Roles & Responsibilities

### Monitor AI (Coordinator + Reviewer)

- **Owner:** GitHub Copilot (this agent)
- **Responsibility:** Orchestrate all tasks, track progress, validate quality, resolve blockers
- **Authority:** Approve merges, assign tasks, escalate conflicts
- **Tools:** GitHub Issues, git branches, session notes

### Task Execution AI (Executor)

- **Owner:** TBD (Claude, Copilot, or specialized agent)
- **Responsibility:** Implement assigned tasks, write code, create documentation
- **Input:** Clear task definition from Monitor
- **Output:** Code + handoff summary with what's done/pending/next
- **Communication:** Feature branch + pull request + comment with reasoning

### Research AI (Strategic Planner)

- **Owner:** TBD
- **Responsibility:** Deep research, analysis, architecture decisions
- **Input:** Research questions from Monitor
- **Output:** Documented findings, trade-offs, recommendations
- **Communication:** Markdown docs in `docs/` + PR comment

### Quality AI (Reviewer)

- **Owner:** TBD (could be Monitor initially)
- **Responsibility:** Code review, test validation, security check
- **Approval:** Must sign off before merge
- **Standards:** Follow AGENTS.md rules, formatting, test coverage

---

## Task Tracking System

### Task Status Lifecycle

```text
TODO → IN_PROGRESS → REVIEW → VALIDATED → DONE
       (Assigned)   (PR open)  (Approved)  (Merged)
```

### Task Template

Each task is tracked as:

1. **GitHub Issue** (centralized task board)
   - Title: Clear, actionable task name
   - Description: What, why, acceptance criteria
   - Labels: role (executor/planner/reviewer), stage (stage-9), priority
   - Assignee: Owning AI agent
   - Project: Track in the team board

2. **Feature Branch** (code location)
   - Branch name: `agent/<agent-name>/<task-slug>/<scope>`
   - Example: `agent/copilot-executor/stage9-library-search/optimization`

3. **PR + Handoff Summary** (transition point)
   - PR title: Same as task
   - PR description: What was done + what's pending + what next AI should do
   - Comments: Reasoning, design decisions, trade-offs

4. **Validation** (before merge)
   - Monitor AI runs all tests
   - Confirms CHANGELOG updated
   - Verifies docs are current
   - Checks git history is clean

---

## Communication Protocol

### Before Task Assignment

Monitor AI:

1. Reads all current issues and PRs
2. Checks `docs/ai-working-notes.md` for context
3. Verifies current branch state with `git status -sb`
4. Creates issue with clear definition

### During Task Execution

Executor AI:

1. Pulls latest from main: `git pull --ff-only origin main`
2. Creates feature branch: `git checkout -b agent/<name>/<task>/<scope>`
3. Implements task
4. Commits regularly with clear messages
5. On completion: opens PR with detailed handoff summary

### After Task Completion

Monitor AI:

1. Reads PR + handoff summary
2. Reviews code and tests
3. Checks CHANGELOG + docs updates
4. Runs validation: `python3 -m py_compile src/` + tests
5. Approves or requests changes
6. Merges to main: `git merge --no-ff` to preserve history
7. Pushes: `git push origin main`
8. Updates `docs/ai-working-notes.md` with results

---

## Active Task Board

### Current Tasks (Stage 9 Continuation)

| Task                           | Owner      | Status              | Branch | PR  | Notes                                                        |
| ------------------------------ | ---------- | ------------------- | ------ | --- | ------------------------------------------------------------ |
| Library retrieval optimization | Monitor AI | DONE                | main   | -   | Completed as MULTI-AI-001; cache shipped and validated       |
| Integration smoke suite        | Monitor AI | DONE                | main   | -   | Completed as MULTI-AI-002; credential-aware smoke suite live |
| Deployment readiness           | TBD        | TODO                | -      | -   | Choose hosting, validate webhook                             |
| MCP server proof-of-concept    | TBD        | TODO                | -      | -   | `library_search` as first MCP tool                           |

### How to Claim a Task

1. Comment in issue: "I'll take this" or "Assign to me"
2. Monitor AI updates here + assigns
3. Create feature branch immediately
4. Push first commit within 1 hour to signal progress
5. Keep Monitor AI updated via PR comments

---

## Git Discipline (Critical for Multi-AI)

### Before Starting Work

```bash
git fetch --all --prune
git status -sb
# If behind: git pull --ff-only
```

### While Working

```bash
git add <specific files>
git commit -m "clear message describing what changed"
# Commit frequently; push at least daily
```

### Handoff Summary (in PR)

```markdown
## What Was Done
- List each change clearly
- Link to relevant docs/tests

## What's Pending
- What was out of scope
- What needs follow-up
- Known issues

## What Next AI Should Do
- Exact next steps
- Where to start reading
- Any blockers to be aware of
```

### Merge & Cleanup

```bash
# After Monitor approval:
git merge --no-ff <feature-branch>
git push origin main
git branch -d <feature-branch>
git push origin --delete <feature-branch>
```

---

## Session Memory Flow

**Every AI agent, after finishing work:**

1. **Update `docs/ai-working-notes.md`**

   ```markdown
   ### Session: [Date] [Agent Name]

   - What I did
   - What I discovered
   - What the next AI should know
   - Any blockers or dependencies
   ```

2. **Update `CHANGELOG.md`** (human-readable changes only)
   - Use `date "+%Y-%m-%d %H-%M-%S"` for timestamp
   - Clear description of impact

3. **Update `AI_CONTEXT.md`** (if priorities changed)
   - New current priorities
   - Completed stages
   - Active planning updates

4. **Commit all doc updates** in the same PR or final commit

---

## Escalation Path

### For Blockers

1. Document clearly in PR comments
2. Tag Monitor AI
3. Monitor AI investigates and proposes solution

### For Conflicts (two AIs modifying same file)

1. First AI completes and merges
2. Second AI rebases: `git pull --ff-only origin main` + resolve conflicts
3. Monitor AI validates merged result

### For Architecture Decisions

1. Create `docs/decisions/NNN-*.md` with rationale
2. Link in PR and commit message
3. Monitor AI approves or requests changes

---

## Success Metrics

- **Task throughput:** Issues closed / week
- **Merge cycle time:** Time from task start → main merge
- **Code quality:** All tests passing, no lint errors
- **Documentation:** 100% of changes have doc updates
- **Handoff quality:** Next AI can start work without asking questions

---

## Getting Started: Next Coordinated Task

**Pilot status:** MULTI-AI-001 and MULTI-AI-002 are complete and validated.

**Next proposed task for multi-AI coordination:**

### Task: Deployment Readiness

**Goal:** Choose deployment target and validate webhook/runtime behavior end-to-end.

**Subtasks:**

1. Research: Compare Railway, Fly.io, and VPS setup requirements for this repo (Research AI)
2. Design: Define deployment checklist, env strategy, and webhook validation plan (Monitor AI + Research AI)
3. Implement: Add deployment runbook and minimal automation scaffolding (Executor AI)
4. Test: Validate container run + webhook reachability with safe checks (Quality AI)
5. Validate: Ensure docs and continuity notes capture the final deployment choice (Monitor AI)

**Timeline:** 2 to 4 hours of wall-clock time, async execution

**Success:** The repo has a documented, validated path to run publicly reachable webhook runtime.

---

## Rules Summary

1. **Always read before starting.** Check issue, PR, docs, main branch.
2. **Claim task explicitly.** Update board, create branch immediately.
3. **Commit frequently.** No surprise 1000-line commits.
4. **Handoff clearly.** What done + what pending + what next.
5. **Document as you go.** Code + tests + docstrings + markdown.
6. **Push daily.** Keep remote in sync, signal progress.
7. **Session memory always.** Update working notes before signing off.
8. **Monitor validates.** All merges go through review + validation.
9. **No direct main commits.** Feature branches + PR only.
10. **Escalate early.** Don't block; ask Monitor for help.

---

**Next Step:** Assign MULTI-AI-003 (deployment readiness) and create the first research branch. Monitor AI is ready to coordinate.
