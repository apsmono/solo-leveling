---
title: Knowledge Intake — MCP (Model Context Protocol) is an open protocol for connect
category: research
storage_folder: research
item_type: knowledge-intake
tags: [research, knowledge-intake, critical-knowledge]
captured_at: 2026-04-21T08:23
research_mode: fallback-heuristic
---

## Conclusion

MCP (Model Context Protocol) is a strategically important protocol for this personal brain project. It standardizes how AI models discover and call external tools — exactly what this repo does today via custom Python handlers.

The immediate conclusion is: **the architecture is already MCP-compatible in intent; the next evolution is to make it formally MCP-compatible in protocol.**

MCP should be tracked as a long-term infrastructure decision. No code change is needed now, but every new handler should be written with a future `inputSchema` in mind to reduce migration friction later.

## Open Questions

- When should this project expose its first MCP server endpoint?
- Should the MCP server run alongside the existing FastAPI webhook or replace it over time?
- Which tools are safe to expose (read-only vs. write) at each stage?
- How does MCP handle authentication for remote server connections — what does that mean for the Gmail and Notion integrations?
- Does the Claude API support connecting to a custom MCP server, or only Claude Desktop?

## Validated Facts

- MCP is open source and not vendor-locked.
- GitHub Copilot (VS Code) already supports MCP in agent mode — confirmed during this research.
- `modelcontextprotocol/servers` on GitHub has a growing community registry.
- The protocol runs over stdio (local) or HTTP+SSE (remote) — the existing FastAPI server is a natural HTTP host.
