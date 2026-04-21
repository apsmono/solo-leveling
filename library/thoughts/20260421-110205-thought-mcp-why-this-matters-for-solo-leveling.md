---
title: Thought: Why MCP Matters for This Brain and What To Do About It
section: thought
status: draft
tags: [mcp, ai-protocol, strategy, integration, solo-leveling]
captured_at: 2026-04-21T11:02
---

## The Core Observation

This repo is already doing what MCP was designed to enable — routing AI commands to external tools (Notion, Drive, Gmail, WhatsApp) and returning structured results. The difference is that today all of that is hardwired custom code. MCP would make it a discoverable, interoperable protocol layer.

## Why This Changes The Picture

Right now, if I want to connect a different AI assistant (say GPT-4o instead of Claude) to this brain, I have to rewrite or re-expose all the integration code. With MCP, any MCP-compatible host can connect and immediately discover what this brain can do. The capabilities become **self-describing**.

This is strategically important because:

1. The AI assistant ecosystem is fragmenting — Claude, Copilot, GPT, Gemini, local models. MCP is the protocol that could unify how all of them access this brain.
2. Once this brain is MCP-compatible, it can be controlled by whichever AI is best for a given task, not locked to one vendor.
3. The library (`library/`) itself could become an MCP resource server — any AI can query it, search it, and add to it using the protocol.

## Reasoning

The current implementation is correct for Stage 9, but it is tightly coupled to the Python codebase. That is fine for now. The question is where MCP fits in the evolution:

- **Short term (now)**: learn MCP deeply, add it to the library and terms so the concept is tracked.
- **Medium term (next stage)**: refactor at least one integration (e.g. library search) as a proper MCP tool with a JSON Schema definition.
- **Long term (future stage)**: expose the full brain as an MCP server so any AI assistant can connect to it.

## What Should Change Today

Nothing in the code needs to change right now. But the mental model should shift: think of every handler function in `src/core/` as a _future MCP tool definition_. When writing new handlers, write them as if they already need a JSON Schema `inputSchema`. This makes the eventual MCP migration much easier.

## Status

Draft — to be revisited when planning the next major integration stage.
