---
title: Reference: Book Research — AI Team Organization: Multiple AI agents working as a compan
section: reference
status: active
tags: [book, book-research, critical-knowledge]
captured_at: 2026-04-21T11:20
---

## Overview

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

## Why This Is Valuable

This topic was explicitly flagged for long-term development, so it should be captured with reasoning, traceability, and follow-up points.

## Research Notes

- Captured from explicit user request.
- Existing library entries were checked for overlap before writing.
- Further external verification may still be useful for factual topics.

## Open Questions

- What must be validated externally?
- What action should this knowledge change?

## Source Bundle

library/books/20260421-112049-book-research-ai-team-organization-multiple-ai-agents-working-as-a-compan

