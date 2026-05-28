# Review Rhythm

## Purpose

Define how progress is reviewed so plans stay current and drift is corrected early.

## Review Cadence

| Review Level | Frequency | Main Focus | Output |
| ------------ | --------- | ---------- | ------ |
| Daily | Every day | Execution quality and focus | Updated priorities |
| Weekly | Once per week | Progress, blockers, and habit performance | Weekly reset |
| Monthly | Once per month | Trend analysis and strategy adjustment | Monthly decisions |
| Quarterly | Every 3 months | Direction, resource allocation, and major tradeoffs | Strategic reset |

## Daily Review

**When:** End of work session (or before sleep).
**Where:** Brain command `/log daily` or voice note to Telegram bot.
**Time:** 5 minutes.

- What mattered most today?
- What slipped and why?
- What are the top priorities for tomorrow?
- Did I make at least one commit? (Git log check)
- Did I avoid anti-habits? (Quick mental check)

**Output:** Single sentence summary logged to `library/thoughts/` or brain daily log.

## Weekly Review

**When:** Sunday evening, 30–45 minutes.
**Where:** This document + `AI_CONTEXT.md` + GitHub contributions graph.

- What results were produced?
  - Commits made, features shipped, bugs fixed.
  - Documentation updated, tests added.
- Which habits held and which failed?
  - Review habit tracker (if automated) or memory.
  - Identify patterns: which habits fail together?
- What needs to be simplified, escalated, or removed?
  - Any active priorities that should be deprioritized?
  - Any blocked tasks that need help or a different approach?
- Financial check: Did I stick to spending rules? Any unexpected costs?
- Content check: Did I publish this week? If not, why?

**Output:** Update `self-development-system.md` capability areas if progress warrants. Log decisions in `docs/decisions/` if direction changes.

## Monthly Review

**When:** Last day of month, 1–2 hours.
**Where:** All planning docs + Git history + financial records.

- Which metrics moved in the right direction?
  - Code output (commits, PRs, tests).
  - Product metrics (if any product has users).
  - Financial metrics (income, expenses, runway).
  - Learning metrics (new skills applied, certifications, content published).
- Which system produced the most leverage?
  - Did the brain save time? Did autopilot work? Did the dashboard improve decisions?
- What strategic correction is needed next month?
  - Is the current priority still correct?
  - Should a new capability area be added or removed?
  - Are constraints still valid?

**Output:** Update `AI_CONTEXT.md` priorities if needed. Add decision record if strategy shifts.

## Quarterly Review

**When:** End of March, June, September, December. Full half-day.
**Where:** All docs + financial statements + project retrospectives.

- Are the current goals still correct?
  - Does the 12-month objective still feel right?
  - Has the market or personal situation changed?
- What has changed in constraints, opportunity, or risk?
  - New tools or APIs that change the game?
  - Personal life changes that affect time/energy?
- Which decisions should be logged because they change direction or operating rules?
  - Any "we've always done it this way" assumptions to challenge?
  - Any projects to sunset or pivot?

**Output:** Major update to `self-development-system.md`, `financial-freedom-strategy.md`, and `AI_CONTEXT.md`. Create new decision records for any directional changes. Set next quarter's single most important objective.

## Review Automation

- **Brain reminder:** Weekly review reminder via scheduler (Sunday 6 PM).
- **Monthly trigger:** Calendar event with link to this doc.
- **Quarterly trigger:** Physical reminder (e.g., change of season) + calendar block.
- **Auto-data:** Git contributions, brain command history, and financial logs should feed into reviews automatically where possible.
