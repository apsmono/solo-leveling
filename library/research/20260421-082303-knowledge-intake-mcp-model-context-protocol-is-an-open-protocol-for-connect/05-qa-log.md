---
title: Knowledge Intake — MCP (Model Context Protocol) is an open protocol for connect
category: research
storage_folder: research
item_type: knowledge-intake
tags: [research, knowledge-intake, critical-knowledge]
captured_at: 2026-04-21T08:23
research_mode: fallback-heuristic
---

## Question / Answer Log

### Q: What is MCP in one sentence?

**A:** MCP (Model Context Protocol) is an open protocol that lets AI models discover and call external tools, read resources, and use prompt templates through a standard schema-based interface — replacing ad-hoc custom integrations.

### Q: What are the three things a server can expose?

**A:** Tools (callable functions), Resources (readable data sources), and Prompts (reusable parameterized templates).

### Q: How does MCP handle transport?

**A:** Over stdio for local servers (subprocess), or HTTP + SSE for remote servers. The protocol is transport-agnostic — the same message format works over both.

### Q: Who created MCP and is it vendor-locked?

**A:** Anthropic created it, but it is open source and not vendor-locked. GitHub (Microsoft) and third-party contributors are already building MCP servers and hosts. The spec is open at modelcontextprotocol.io.

### Q: Why does this matter for this project specifically?

**A:** This brain already does what MCP enables — routing AI commands to external integrations. MCP would make those integrations discoverable and accessible to any AI assistant, not just this project's custom Python handlers. It is the upgrade path from a private automation to a personal AI platform.

### Q: Should MCP be adopted now?

**A:** No, not yet. The current Stages 1–9 implementation is stable and sufficient. MCP adoption is a Stage 10+ decision. The priority now is to track it, understand it, and write future handlers in a way that makes migration easy.
