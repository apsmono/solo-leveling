---
title: Why this Claude Code engineer uses HTML files as AI specs | Thariq Shihipar (Anthropic)
section: article
status: to-read
tags: [youtube, link, to-read]
captured_at: 2026-05-30T07:01
source_url: https://www.youtube.com/watch?v=Qrpm7E80wQ0
---

---
title: Why this Claude Code engineer uses HTML files as AI specs | Thariq Shihipar (Anthropic)
section: article
status: to-read
tags: [youtube, link, to-read]
captured_at: 2026-05-30T07:01
source_url: https://www.youtube.com/watch?v=Qrpm7E80wQ0
---

Source: https://www.youtube.com/watch?v=Qrpm7E80wQ0

Author: How I AI

Provider Name: YouTube

Type: video

Captured At: 2026-05-30T07:01

This video features Thariq Shihipar, an engineering lead on the Claude Code team at Anthropic, explaining his shift from using **Markdown** to **HTML** as the default format for AI-generated specifications, planning, and documentation.

### Summary

The core argument is that while Markdown has been the industry standard for LLM outputs due to its simplicity, it is becoming a bottleneck as AI agents handle increasingly complex tasks. Thariq argues that **HTML is a far superior medium for human-AI collaboration.** By treating HTML files as "living documents," developers can create richer, more readable, and interactive interfaces that prevent the "eye-glazing" effect caused by long, static Markdown files. This approach transforms developers from passive reviewers into active "compute allocators" who can better manage and verify the AI’s work.

---

### Key Points

* **The "100-Line Limit":** Thariq notes a personal and observable trend: humans rarely read Markdown files longer than 100 lines. Because Markdown lacks advanced formatting (like tabs, interactive elements, or collapsible sections), large project plans become unreadable and engagement drops.
* **Information Density & Visual Clarity:** HTML allows for much richer data representation, including:
* **SVG/Charts:** Replacing ASCII diagrams with native browser-rendered graphics.
* **Interactive Widgets:** Including sliders, buttons, and knobs to adjust variables or test design iterations.
* **Visual Organization:** Using CSS and browser-native features to create navigation tabs, sidebars, and responsive layouts.


* **Two-Way Interaction (Micro-apps):** HTML documents can act as small, disposable "micro-apps." For instance, an AI can generate an HTML interface where a user can toggle settings, which then allows the user to copy updated parameters back into the prompt for the AI to continue the work.
* **Living Design Systems:** Thariq maintains a "design system" HTML file that contains his project’s color palettes, typography, and component states. This file serves as a single, portable source of truth that keeps the AI consistent across different tasks.
* **Why Claude Code?** This workflow is uniquely powerful with **Claude Code** because the agent has deep access to the environment (filesystem, git history, MCP servers, and the browser). This allows the AI to ingest vast amounts of context and output it into an organized HTML artifact that is actually useful for human review.
* **Efficiency vs. Tokens:** While generating HTML consumes more tokens than Markdown, Thariq views this as a worthwhile investment. With modern large context windows (like 1M+ tokens), the cost is negligible compared to the value of a high-quality, readable, and actionable project spec.

---

### Suggested Use Cases

* **Project Planning:** Brainstorming options with mockups and risk assessments.
* **Code Review:** Rendering diffs, flowcharts, and technical diagrams directly within the document.
* **Reporting:** Drafting status updates or incident reports that are structured and easy to navigate.
* **Prototyping:** Sketching design systems or UI components that can be immediately visualized and adjusted.

---

Does this summary cover the specific workflow you were interested in, or would you like to know more about how to set up one of these HTML "micro-apps" for your own projects?

