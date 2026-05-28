# Habit System

## Purpose

Define the recurring behaviors that support the self-development and financial systems.

## Habit Design Rules

- Each habit must support a specific objective.
- Each habit must have a clear trigger.
- Each habit must be measurable.
- Remove habits that create noise without meaningful payoff.

## Active Habits

| Habit | Objective Supported | Trigger | Frequency | Minimum Successful Version | Score Method |
| ----- | ------------------- | ------- | --------- | -------------------------- | ------------ |
| Morning priority check | Daily execution quality | Open laptop / start workday | Daily | Read `AI_CONTEXT.md`, note top 3 | Done or not done |
| Single commit rule | Consistent progress | Evening coding session | Daily | 1 meaningful commit to any project | Git log verification |
| Deep learning block | Capability building | Weekend morning | Weekly | 90 min focused learning | Timer + notes taken |
| Brain command test | System reliability | After any brain code change | Per change | Run `tests.test_stage9_libraries` + `tests.test_integration_smoke` | Pass/fail |
| Weekly review | Strategic alignment | Sunday evening | Weekly | Answer 3 review questions in `review-rhythm.md` | Notes exist |
| Content creation | Audience building | Wednesday evening | Weekly | 1 blog post, thread, or documentation update | Published/posted |
| Physical movement | Sustained energy | Morning or post-lunch | Daily | 20 min walk or workout | Done or not done |

## Anti-Habits

| Anti-Habit | Trigger | Cost | Countermeasure | Tracking Method |
| ---------- | ------- | ---- | -------------- | --------------- |
| Doom-scrolling Twitter/X | Boredom, waiting for builds | Time theft, mental fatigue | Use brain `/command` or read `library/` instead | Screen time audit weekly |
| Starting new repos | Seeing cool tech on HN/Reddit | Fragmented focus, abandoned work | 48-hour rule: must document why existing repo cannot host it | Repo creation log |
| Working past 10 PM | "Just one more thing" | Sleep debt, next-day fatigue | Hard stop at 10 PM — set phone alarm | Sleep tracking app |
| Manual repetition | "Faster to just do it" | Time debt, no automation gain | Ask: "Can the brain do this?" before any repeated task | Task audit weekly |

## Friction Design

- **How good habits are made easier:**
  - `AI_CONTEXT.md` is always open in the editor — lowest friction to check priorities.
  - Brain commands are accessible via Telegram — can trigger actions from anywhere.
  - Dashboard shows active priorities on login — visual reminder of focus.
  - VS Code workspace opens to the correct project automatically.
- **How bad habits are made harder:**
  - Social media apps removed from work device. Access only via separate device.
  - New repo creation requires writing a 1-page justification first.
  - Phone set to DND after 10 PM.
  - Browser blockers for Hacker News during deep-work hours.
- **Environment changes to support consistency:**
  - Dedicated workspace that signals "work mode."
  - Physical notebook for daily top-3 (reduces screen switching).
  - Brain reminder scheduled for morning priority check.

## Adjustment Rules

- If a habit fails 3 times in one week, review the trigger and scope.
- If a habit is completed consistently for 30 days, decide whether to increase difficulty, keep steady, or automate tracking.
- If a habit no longer serves a clear goal, remove or replace it.
