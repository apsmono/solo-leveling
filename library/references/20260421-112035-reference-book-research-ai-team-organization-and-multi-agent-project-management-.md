---
title: Reference: Book Research — AI Team Organization and Multi-Agent Project Management

How
section: reference
status: active
tags: [book, book-research, critical-knowledge]
captured_at: 2026-04-21T11:20
---

## Overview

AI Team Organization and Multi-Agent Project Management

How should multiple AI agents work together as a team? What are their positions, roles, and tasks? How should a Project Manager AI orchestrate their work?

CORE ROLES:
1. Strategic Planner - research, long-term vision, decisions
2. Executor - implementation, code generation, deployment
3. Coordinator - task routing, state management, handoffs
4. Reviewer - quality assurance, security, consistency
5. Domain Expert - specialized knowledge in specific areas

WORK ALLOCATION:
- By specialization: assign to AI with best expertise
- By phase: research → planning → execution → review
- By risk: high-risk to most reliable AI
- By complexity: complex logic to reasoning-capable AI

MULTI-AI COORDINATION:
- Async message passing (no real-time blocking)
- Git-based state for code and documentation
- Handoff summaries: what done, pending, next steps
- Task ownership: one AI per task at a time
- Session memory: persistent notes on every session
- Clear escalation paths for conflicts

PROJECT MANAGER AI:
- Breaks work into stories and tasks
- Assigns to right specialization
- Tracks progress and state
- Facilitates communication
- Resolves blockers
- Ensures quality gates pass
- Maintains roadmap alignment

SCALING PATTERNS:
- 1 AI: knows everything, does everything
- 2 AIs: need handoff protocol, shared state
- 3+ AIs: need PM, task queue, conflict resolution
- 10+ AIs: need role hierarchy, escalation paths

KEY INSIGHT: Treat AI agents like team members with specializations. The glue is git/docs, handoff protocols, and PM-style orchestration.

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

library/books/20260421-112035-book-research-ai-team-organization-and-multi-agent-project-management-how

