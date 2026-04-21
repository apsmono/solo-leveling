---
title: Reference: MCP (Model Context Protocol) — Architecture and Usage Guide
section: reference
status: active
tags: [mcp, ai-protocol, integration, architecture, reference]
captured_at: 2026-04-21T11:02
---

## What Is MCP

Model Context Protocol (MCP) is an open standard introduced by Anthropic that defines how AI models communicate with external tools, data sources, and reusable prompt libraries. It replaces the patchwork of custom integrations that each AI tool previously required with a single, schema-validated, capability-negotiated protocol.

Think of MCP as the **USB-C of AI integrations**: one protocol, many compatible devices.

---

## Architecture

```
┌─────────────────────────────────────┐
│              Host                   │
│  (Claude Desktop, VS Code, app)     │
│                                     │
│   ┌──────────┐   ┌──────────┐      │
│   │ Client 1 │   │ Client 2 │      │
│   └────┬─────┘   └────┬─────┘      │
└────────┼──────────────┼────────────┘
         │              │
    MCP Protocol   MCP Protocol
         │              │
   ┌─────▼──────┐  ┌───▼──────────┐
   │  Server A  │  │   Server B   │
   │ (local fs) │  │ (remote API) │
   └────────────┘  └──────────────┘
```

- **Host**: orchestrates everything. Decides which servers to connect to, manages lifecycle.
- **Client**: one per server connection. Handles handshake, capability listing, tool invocations.
- **Server**: exposes tools, resources, and prompts. Can run locally (stdio) or remotely (HTTP + SSE).

---

## Protocol Lifecycle

1. **Initialization**: client connects to server; they exchange `initialize` messages declaring protocol version and capabilities.
2. **Capability negotiation**: server returns its tool list, resource list, and prompt list. Client stores this.
3. **Tool discovery**: host/model reads the schema of each tool to understand inputs, outputs, and descriptions.
4. **Tool invocation**: model decides to call a tool; client sends `tools/call` to server with validated arguments.
5. **Result delivery**: server returns structured result; client passes it back to the model's context.
6. **Session teardown**: client closes connection cleanly.

---

## Tool Definition Example

```json
{
  "name": "read_file",
  "description": "Read the contents of a local file by path.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": { "type": "string", "description": "Absolute file path" }
    },
    "required": ["path"]
  }
}
```

The model uses `description` to decide when to call the tool, and `inputSchema` to construct valid arguments.

---

## Transport Options

| Transport      | Use case                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| **stdio**      | Local server running as a subprocess. Lowest latency. Used for file system, local databases, CLI tools. |
| **HTTP + SSE** | Remote server over network. Supports streaming. Used for cloud APIs, web services.                      |

---

## MCP vs. Alternative Approaches

| Approach                | Problem MCP Solves                                       |
| ----------------------- | -------------------------------------------------------- |
| Custom API wrappers     | Every integration is bespoke; no reuse, no discovery     |
| OpenAI function calling | Tightly coupled to one provider's schema and runtime     |
| LangChain tools         | Framework-dependent; not a neutral open standard         |
| **MCP**                 | Open, provider-agnostic, schema-first, self-discoverable |

---

## Security Model

- Servers declare their own capability scope — they cannot self-expand it.
- Hosts control which servers a client connects to.
- Tool arguments are schema-validated before execution.
- No ambient authority: tools only do what their schema says they do.
- Sensitive outputs should be sanitized server-side before returning to the model context.

---

## Practical Use Cases

1. **AI code assistant** reads and writes local files through an MCP filesystem server.
2. **AI personal brain** (this repo) routes WhatsApp commands through MCP-exposed tools for Notion, Drive, Gmail.
3. **AI research agent** fetches web content, searches databases, saves summaries via MCP servers.
4. **AI financial advisor** reads portfolio data from a brokerage API exposed as an MCP resource.

---

## Adoption Status (as of 2026-04)

- Anthropic: native MCP support in Claude Desktop and Claude API.
- GitHub Copilot: MCP support added in VS Code agent mode.
- OpenAI: exploring compatibility.
- Community: growing open-source MCP server registry (filesystem, GitHub, Slack, databases, etc.).

---

## Relationship To This Repo

This command-center brain (`solo-leveling`) is a natural MCP candidate:

- Each integration (Notion, Drive, Gmail, WhatsApp) could be exposed as an MCP server.
- The router becomes an MCP host, dispatching tool calls rather than raw function calls.
- Library captures, search, and retrieval could be MCP resources and tools.
- This would make the brain interoperable with any MCP-compatible AI assistant.

---

## Key References

- Anthropic MCP specification: https://spec.modelcontextprotocol.io
- MCP server registry: https://github.com/modelcontextprotocol/servers
- VS Code MCP extension docs
