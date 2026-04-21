---
title: Term: MCP (Model Context Protocol)
section: term
status: active
tags: [mcp, ai-protocol, integration, interoperability, tooling]
captured_at: 2026-04-21T11:02
---

## Definition

**MCP = Model Context Protocol**

An open protocol that standardizes how AI models (called _hosts_ or _clients_) connect to external tools, data sources, and prompt libraries (called _servers_). MCP gives AI assistants a consistent, schema-first way to discover capabilities, request actions, and receive structured results — without each integration needing its own bespoke implementation.

## Core Components

| Component    | Role                                                                                         |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Host**     | The AI application (e.g. Claude Desktop, VS Code Copilot). Orchestrates one or more clients. |
| **Client**   | Lives inside the host. Manages the connection to a single MCP server.                        |
| **Server**   | Exposes tools, resources, and prompts over the protocol. Can be local or remote.             |
| **Tool**     | A callable function the AI can invoke (e.g. read a file, query a database).                  |
| **Resource** | A readable data source (e.g. a file, a URL, a database record).                              |
| **Prompt**   | A reusable prompt template the host can load and parameterize.                               |

## Key Properties

- **Schema-first**: every tool, resource, and prompt is described by a JSON Schema, so the model can self-discover capabilities at runtime.
- **Capability negotiation**: client and server handshake to declare what each supports before any tool is called.
- **Transport-agnostic**: runs over stdio (local) or HTTP+SSE (remote) — the protocol layer is independent of transport.
- **Secure by design**: servers declare their own boundaries; hosts enforce what each server is allowed to do.
- **Interoperable**: any MCP-compatible host can talk to any MCP-compatible server without custom glue code.

## Why It Matters

Before MCP, every AI tool integration was a one-off: a custom API wrapper, bespoke auth, ad-hoc output parsing. MCP turns that into a reusable, discoverable contract — similar to what USB did for device connectivity or what REST did for web APIs.

## Related Terms

- Model Context Protocol → this term
- AI Agent / AI Orchestration
- JSON Schema / schema-first contracts
- Tool Calling (OpenAI function calling, Anthropic tool use)
- LLM Context Window
- Agentic workflows

## Source

Anthropic MCP specification (2024). Personal knowledge capture 2026-04-21.
