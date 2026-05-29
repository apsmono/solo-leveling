---
title: I Tried 100+ Claude Code Skills. These 6 Are The Best
section: article
status: to-read
tags: [youtube, link, to-read]
captured_at: 2026-05-28T02:26
source_url: https://www.youtube.com/watch?v=eRS3CmvrOvA
---

---
title: I Tried 100+ Claude Code Skills. These 6 Are The Best
section: article
status: to-read
tags: [youtube, link, to-read]
captured_at: 2026-05-28T02:26
source_url: https://www.youtube.com/watch?v=eRS3CmvrOvA
---

Source: https://www.youtube.com/watch?v=eRS3CmvrOvA

Author: Nate Herk | AI Automation

The video **"I Tried 100+ Claude Code Skills. These 6 Are The Best"** by Nate Herk focuses on practical, effective Claude Code skills and plugins that deliver real business value (saving time, reducing costs, and eliminating errors) rather than just looking "flashy" in videos [[00:00](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=0)].

---

### Executive Summary

After spending over 400 hours working with Claude Code across various industries (real estate, HVAC, marketing, coaching), Nate identifies the common pitfalls of AI development—mainly **rushed code** and **context rot** [[00:00](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=0), [02:20](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=140)]. He breaks down 6 core tools (plus a bonus design skill) that elevate Claude's performance to that of a senior developer, optimize token usage, and retain long-term memory [[02:56](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=176), [05:05](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=305), [09:49](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=589)]. Finally, he explains how to position and sell these AI automations to businesses by focusing on outcomes rather than the underlying tech stack [[12:25](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=745)].

---

### Key Details & The 6 Best Skills

#### 1. Skill Creator [[00:44](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=44)]

* **What it does:** An official Anthropic skill that acts as a "factory" to build other skills. You describe what you want in plain English or drop in a Standard Operating Procedure (SOP), and Claude automatically drafts, tests, and packages it [[00:48](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=48)].
* **Problem solved:** Eliminates the frustration and flakiness of manually writing and formatting `skill.md` files [[01:15](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=75)].
* **How to install:** `/pluginstall skill creator` (Recommended to install globally on a user scope) [[02:06](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=126)].

#### 2. Superpowers [[02:56](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=176)]

* **What it does:** Forces Claude to approach coding like a senior engineer. Before writing any code, it steps back, plans out the architecture, writes tests, and runs a two-stage review process (spec matching and code quality) in an isolated environment [[03:01](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=181)].
* **Problem solved:** Prevents Claude from writing rushed, sloppy, or fragile code that falls apart under edge-case scenarios [[03:20](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=200)].
* **Impact:** Increases first-pass accuracy to around 80% (up from ~60%), meaning fewer debugging cycles and lower token costs [[04:06](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=246)].

#### 3. GSD (Get Shit Done) [[04:34](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=274)]

* **What it does:** Manages context engineering. Instead of using one massive conversation that degrades over time, GSD automatically spawns fresh "sub-agents" with clean context windows dedicated to individual sub-tasks [[05:05](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=305)]. It features automated quality gates, security enforcement, and an autonomous mode [[05:21](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=321), [05:38](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=338)].
* **Problem solved:** Fixes "context rot," where Claude starts cutting corners or forgetting initial project rules halfway through a long session [[04:45](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=285)].

#### 4. Code Review Commands (`/re` & `/ultrareview`) [[06:14](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=374)]

* **`/re`:** Runs a fast, local structured review of your code to flag bugs and structural issues immediately at no extra token cost [[06:24](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=384)].
* **`/ultrareview`:** (Launched with Opus 4.7) Uploads your branch to a cloud sandbox and deploys a fleet of specialized parallel agents to aggressively test logic, security, and performance. Bugs must be independently reproduced before making the report, eliminating false positives [[06:39](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=399), [06:56](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=416)].
* **Note:** Requires Claude Code v2.1.86 or later and a paid Claude account. `/ultrareview` takes 10–20 minutes and costs roughly $5 to $20 per run [[07:16](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=436), [07:49](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=469)].

#### 5. Context Mode [[08:04](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=484)]

* **What it does:** Intercepts massive tool outputs (like a 56KB Playwright screenshot or 46KB access logs) by routing them through an isolated subprocess, stripping out the garbage data, and passing only the essential text (compressing thousands of bytes into a few hundred) [[08:36](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=516)]. It also logs every key decision and file edit into a local SQLite database [[09:10](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=550)].
* **Problem solved:** Prevents Claude from running out of space and wiping out session history [[08:20](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=500)]. It stretches 30-minute breaking-point sessions into stable 3-hour workflows [[09:31](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=571)].

#### 6. Claude Mem [[09:49](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=589)]

* **What it does:** Tracks project history locally across multiple separate sessions using vector search [[09:55](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=595), [10:35](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=635)]. It automatically documents decisions, bug fixes, and file changes into folder-level `claude.md` files [[10:30](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=630), [10:46](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=646)].
* **Problem solved:** Eliminates the "startup tax" of re-explaining a project context to Claude every time you open a new terminal window [[10:00](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=600)]. It yields roughly a 10x token savings on retrieval [[11:14](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=674)].

#### 🌟 Bonus: Front-End Design Skill [[11:56](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=716)]

* An official Anthropic skill that helps Claude Code generate UI layouts and decks that look far less generic or "AI-generated" [[12:02](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=722)].

---

### Nate's Business Strategy for 2026 [[12:25](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=745)]

* **Sell the Outcome, Not the Tech:** Business owners do not care about the workflow, how many lines of code were written, or the underlying AI tools. They care about saving 10 hours a week, minimizing costly human mistakes, and boosting profit margins [[12:29](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=749), [12:37](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=757)].
* **Start Small:** If you want to make money selling AI automation, don't try to learn all 6 tools at once. Master one, build a clean, working demo, and show its direct value to a business owner [[12:50](https://www.youtube.com/watch?v=eRS3CmvrOvA&t=770)].

You can watch the full breakdown and see the exact terminal commands demonstrated in the video here: **[I Tried 100+ Claude Code Skills. These 6 Are The Best](http://www.youtube.com/watch?v=eRS3CmvrOvA)**.

Provider Name: YouTube

Type: video

Captured At: 2026-05-28T02:26

