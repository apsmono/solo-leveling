---
title: Thought: MCP Adoption Plan for This Brain — Phased Approach
section: thought
status: active
tags: [mcp, ai-protocol, plan, integration, roadmap]
captured_at: 2026-04-21T11:02
---

## Goal

Evolve this command-center brain into a full MCP-compatible server so that any AI assistant can connect to it, discover its capabilities, and use its integrations as tools — without needing custom code per assistant.

## Phase 1 — Learn and Track (now)

- [x] Understand MCP architecture (host, client, server, tool, resource, prompt)
- [x] Add MCP to the personal library with full term definition and reference
- [ ] Read the official MCP specification and the `modelcontextprotocol/servers` registry
- [ ] Identify which existing brain capabilities map cleanly to MCP tools vs. resources vs. prompts

**Outcome**: solid conceptual foundation, no code changes needed.

## Phase 2 — Proof of Concept (next)

Pick one small, self-contained capability to expose as a real MCP tool:

**Candidate: Library Search Tool**

```json
{
  "name": "library_search",
  "description": "Search the personal knowledge library by keyword. Returns matching entry titles and paths.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search keyword or phrase" },
      "limit": {
        "type": "integer",
        "default": 5,
        "description": "Max results to return"
      }
    },
    "required": ["query"]
  }
}
```

**Candidate: Add To Library Tool**

```json
{
  "name": "library_add",
  "description": "Add a new knowledge item to the personal library. Triggers full deep-capture workflow.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": { "type": "string", "description": "The knowledge to capture" }
    },
    "required": ["content"]
  }
}
```

**Outcome**: one working MCP server with 1-2 tools, testable with Claude Desktop.

## Phase 3 — Full Brain as MCP Server (future)

Map all current router intents to MCP tools:

| Current Intent    | MCP Tool Name         |
| ----------------- | --------------------- |
| `library_search`  | `library_search`      |
| `library_capture` | `library_add`         |
| `library_bundle`  | `library_get_bundle`  |
| `library_summary` | `library_summarize`   |
| `notion_search`   | `notion_search`       |
| `gdrive_list`     | `drive_list_files`    |
| `gmail_summary`   | `gmail_inbox_summary` |
| `reminder`        | `reminder_set`        |
| `ask_ai`          | `brain_ask`           |

**Outcome**: complete MCP-compatible personal brain server.

## Risks and Mitigations

| Risk                                              | Mitigation                                                                   |
| ------------------------------------------------- | ---------------------------------------------------------------------------- |
| MCP spec still evolving                           | Track spec version; pin to a stable release                                  |
| Secrets exposed via MCP tools                     | MCP server runs locally; all secrets stay in `.env`, never in tool responses |
| Performance — every tool call is a Python process | Cache index in memory; consider persistent FastAPI MCP endpoint              |

## Decision Point

Before Phase 2, decide: build a **standalone MCP server** (`mcp_server.py`) alongside the existing webhook, or **refactor the webhook itself** to speak MCP natively. Recommendation: standalone server first — lowest risk, keeps Stage 2–9 webhook stable.
