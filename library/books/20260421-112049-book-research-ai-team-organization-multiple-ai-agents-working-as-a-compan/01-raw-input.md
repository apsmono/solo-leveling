---
title: Book Research — AI Team Organization: Multiple AI agents working as a compan
category: book
storage_folder: books
item_type: book-research
tags: [book, book-research, critical-knowledge]
captured_at: 2026-04-21T11:20
research_mode: fallback-heuristic
---

## Raw Input

AI Team Organization: Multiple AI agents working as a company team

CORE ROLES:
- Strategic Planner: research, long-term vision, decisions
- Executor: implementation, code generation, deployment
- Coordinator: task routing, state tracking, handoffs
- Reviewer: quality assurance, security, consistency
- Domain Expert: specialized knowledge in specific areas

TASK ALLOCATION:
- By specialization: assign to AI with best expertise
- By phase: research → planning → execution → review
- By risk: high-risk tasks to most reliable AI
- By complexity: complex logic to reasoning-capable AI

MULTI-AI COORDINATION:
- Async handoff protocol (no real-time blocking needed)
- Git-based state management for code/docs
- Handoff summaries: what done, what pending, what next
- Task ownership: one AI per task at a time
- Session memory: persistent notes via git
- Clear escalation for conflicts

PROJECT MANAGER AI:
- Breaks work into stories and tasks
- Assigns to right specialization
- Tracks progress and state
- Facilitates communication
- Resolves blockers
- Maintains quality gates
- Aligns with roadmap

SCALING:
- 1 AI: knows everything, does everything
- 2 AIs: need handoff protocol and shared state
- 3+ AIs: need project manager and task queue
- 10+ AIs: need role hierarchy and escalation paths

KEY INSIGHT: Treat AI agents like team members with specializations. Coordination happens through git/docs, handoff protocols, and PM-style orchestration.
