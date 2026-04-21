---
title: Thought: MCP Recommendation — What I Think You Should Do
section: thought
status: active
tags: [mcp, ai-protocol, recommendation, decision]
captured_at: 2026-04-21T11:02
---

## Recommendation

**Adopt MCP as the long-term integration standard for this brain. Start with a minimal proof of concept on library search, then expand.**

## Reasoning

This brain already routes structured commands to external tools. It is, architecturally, an MCP host without the protocol. Adding MCP does not change _what_ the brain does — it changes _how_ other AI assistants can access it.

The cost of adopting MCP is low:

- One new Python file (`src/mcp_server.py`) using the `mcp` SDK from Anthropic.
- No changes to existing webhook, router, or library handlers.
- Run alongside the existing FastAPI server.

The benefit is high:

- Any MCP-compatible AI assistant (Claude, Copilot, local LLMs) can talk to this brain without custom integration.
- Library knowledge becomes AI-readable without prompt engineering — just a resource endpoint.
- Sets the foundation for the brain to evolve into a personal AI platform rather than a WhatsApp-only tool.

## What Not To Do

- Do not rush to expose all integrations at once. Each tool exposed is a security surface. Start with read-only tools (library search, library summary) before write tools (add to library, send WhatsApp).
- Do not expose secrets through tool responses. If a tool needs credentials, it uses them internally — the model never sees them.
- Do not refactor the existing webhook until the standalone MCP server is proven stable.

## Conclusion

MCP is the right direction. The timing is right — the ecosystem is maturing and GitHub Copilot already supports it in VS Code. Capture this knowledge now, plan the proof of concept for next stage, and execute when the brain is stable enough to afford a new integration surface.

**Priority: Medium. Action: track, plan, execute in Stage 10.**
