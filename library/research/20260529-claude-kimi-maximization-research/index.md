# Research: Maximizing Claude Code + Kimi API for Coding Agents

**Research Date:** 2026-05-29
**Focus:** Prompt engineering, context optimization, anti-hallucination, multi-agent coordination
**Context:** Claude Code (primary IDE) + Kimi-for-Code API (secondary LLM) + solo-leveling brain
**Sources:** Anthropic official docs, Kimi official docs, Promptfoo, arXiv papers, community guides

---

## Executive Summary

This research synthesizes best practices for maximizing Claude Code's effectiveness when paired with the Kimi (Moonshot AI) coding API. The key insight: **Claude Code's orchestration layer + Kimi's coding model creates a powerful dual-AI system** where Claude handles context management, tool use, and coordination while Kimi provides deep coding reasoning.

Five critical areas covered:
1. Prompt engineering techniques for coding agents
2. Context window management and cache optimization
3. Tool use patterns that reduce hallucination
4. Multi-agent coordination strategies
5. Anti-hallucination layered defense

---

## 1. Prompt Engineering for Coding Agents

### Anthropic Official Best Practices

**Be Explicit and Clear**
- Lead with direct action verbs: "Write," "Analyze," "Generate," "Create"
- Skip preambles. Get straight to the request.
- State what you want the output to *include*, not just what to work on.
- Specify quality and depth expectations.

**Provide Context and Motivation**
- Explaining *why* something matters helps Claude make better decisions about related choices.
- Include purpose, audience, constraints, and how output will be used.

**Use Examples (Few-Shot Prompting)**
- Start with one example. Add more only if needed.
- Claude 4.x pays very close attention to details in examples.
- For coding: provide a small code snippet showing the desired style/pattern.

**Give Permission to Express Uncertainty**
- "If the data is insufficient to draw conclusions, say so rather than speculating."
- This is critical for preventing hallucinated code.

**Prefill the AI's Response**
- Start the assistant's response to guide format/tone.
- Useful for JSON/XML output, skipping preambles.
- Example: `<thinking>` tag to force step-by-step reasoning.

**Chain of Thought (CoT)**
- "Think step-by-step" for complex tasks.
- Three forms: basic, guided, and structured with tags.
- Complements Claude's "extended thinking" feature.

### Kimi Official Best Practices

**Three Operational Modes**

| Mode | Use Case | Prompt Strategy |
|------|----------|-----------------|
| **Instant** | Quick lookups, simple tasks | Keep prompts tight and direct |
| **Thinking** | Complex reasoning, math, verification | Request step-by-step reasoning; include constraints and edge cases |
| **Agent** | Multi-file refactors, end-to-end features | Name available tools, decompose tasks, define success criteria |

**Context Placement (Critical for Kimi)**
- Kimi excels at long-horizon coding with huge context windows (up to 262K tokens).
- **Paste full source material, docs, or diffs first — put instructions at the end.**
- For multi-file refactors, name repo structure and standards upfront.

**Coding-Specific Prompt Template for Kimi:**
```
Repo structure:
- src/api/ (REST endpoints)
- src/models/ (SQLAlchemy models)
- tests/ (pytest)

Standards:
- Use Pydantic v2 for validation
- All endpoints must have OpenAPI docs
- Write tests for every new endpoint

Task: Add a user management REST API with CRUD operations
Success criteria: All tests pass, coverage >90%
```

### Claude Code Tips (2026 Community)

**CLAUDE.md Files — "The single most impactful thing you can do"**
- Create project-root files with: overview, architecture, standards, commands, known issues, "do-not-touch" files.
- Supports layered hierarchy: `~/.claude/CLAUDE.md` for global, subdirectory files for focused context.
- Your existing `CLAUDE.md` in solo-leveling is excellent — continue evolving it.

**Key Slash Commands**
- `/plan` — Outline approach before coding; essential for multi-file changes.
- `/compact` — Compress conversation to save context window space.
- `/commit` — AI-generated commit messages following conventional formats.
- `/review` — Review recent changes via git diff.
- `/status` — Show session info and context usage.

**Hooks for Automation** (in `.claude/settings.json`)
- **PreCommit** — Run tests, lint; block commit on failure.
- **PostFileWrite** — Auto-formatting, import sorting.
- "Hooks transform Claude Code from a tool you have to babysit into a tool that enforces your standards automatically."

**Context Management**
- `.claudeignore` — Exclude `node_modules`, build outputs, large data files.
- **Multi-conversation workflows** — Separate sessions for backend, frontend, tests.
- **Piping** — `cat error.log | claude "What is causing these errors?"`

---

## 2. Context Window Management & Cache Optimization

### The Context Window Problem

Claude Code sessions can run for hours (as you've experienced). Context window exhaustion is the primary failure mode for long sessions.

**Strategies:**

1. **Proactive Compaction**
   - Use `/compact` before context fills (Claude Code shows context usage).
   - Compress conversation by summarizing completed work and removing intermediate reasoning.

2. **Multi-Conversation Workflows**
   - Separate sessions for: backend API, frontend UI, tests/infrastructure.
   - More effective than a single overloaded session.
   - Use git commits as boundaries between sessions.

3. **CLAUDE.md as Persistent Context**
   - Store non-ephemeral context in `CLAUDE.md`, not in conversation history.
   - Update `CLAUDE.md` with discoveries so next session starts informed.
   - Your `docs/ai-knowledge/` folder serves this purpose well.

4. **Library Index as RAG**
   - Use `library/index.json` as a curated knowledge base.
   - Agents can search it before generating code, grounding responses in actual project context.

5. **Kimi's Massive Context Advantage**
   - Kimi-for-coding supports 262K tokens.
   - Use Kimi for tasks requiring full codebase context (refactors, architecture reviews).
   - Use Claude for orchestration, tool use, and coordination.

### Cache Optimization

- **Prompt caching in Claude API**: Reuse system prompts and context across requests.
- **Static analysis integration**: Cache ASTs, dependency graphs, type information.
- **Library index caching**: Your `library/index.json` with LRU cache is a good pattern — extend it to cache search results.

---

## 3. Tool Use Patterns That Reduce Hallucination

### The Core Principle

Hallucinations in code generation often stem from:
- Invented APIs/packages
- Outdated library versions
- Incorrect assumptions about codebase structure
- Missing edge cases

### Tool-Based Defense Patterns

**Pattern 1: Read-Before-Write**
- Always read the file before editing it.
- Always read related files before proposing changes.
- Your brain's `router.py` already enforces this — extend it to all agents.

**Pattern 2: Test-Driven Generation**
- Generate tests first, then implementation.
- Run tests after every change.
- Your existing test suite (37 tests) is the best anti-hallucination tool.

**Pattern 3: Static Analysis Verification**
- Run `mypy`, `ruff`, or `pylint` on generated code.
- Use AST parsing to verify imports exist.
- Your `test_integration_smoke.py` serves this role.

**Pattern 4: Execution-Based Validation**
- Actually run generated code in a sandbox.
- For APIs: hit the endpoint and verify response.
- For UIs: build and visually inspect.

**Pattern 5: Two-Model Verification (Claude + Kimi)**
- Claude proposes the code.
- Kimi reviews it for correctness, edge cases, and style.
- Disagreements flag areas needing human review.
- This is your most powerful anti-hallucination tool given your dual-AI setup.

### Specific Tool Configuration

**In `.claude/settings.json`:**
```json
{
  "hooks": {
    "PreCommit": ["python -m unittest tests.test_stage9_libraries tests.test_integration_smoke"],
    "PostFileWrite": ["ruff check $FILE", "ruff format $FILE"]
  }
}
```

**In `solo-leveling/src/core/router.py`:**
- Add a `verify` intent that runs tests before executing commands.
- Add a `review` intent that uses Kimi to review Claude-generated code.

---

## 4. Multi-Agent Coordination Strategies

### Claude Code Dynamic Workflows (May 2026)

Anthropic introduced **Dynamic Workflows** enabling orchestration of up to **1,000 subagents** with **16 concurrent**:

| Feature | Traditional | Dynamic Workflows |
|--------|-------------|-------------------|
| Plan holder | Claude decides turn-by-turn | JavaScript orchestration script |
| Context management | Intermediate results fill context | State lives in script variables |
| Scale | Limited by context window | Up to 1,000 agents, 16 concurrent |
| Repeatability | Ad-hoc | Saveable as `.claude/workflows/` |

**Key insight for your setup:** Your `solo-leveling` brain IS an orchestrator. The dashboard + Telegram + API endpoints are the coordination layer. You're already building what Anthropic calls "orchestrator-subagent" pattern.

### Five Coordination Patterns

**1. Generator-Verifier**
- One agent generates, another verifies.
- **Best for:** Code generation with explicit quality standards.
- **Your use:** Claude generates, Kimi verifies.

**2. Orchestrator-Subagent** ⭐ *Your current pattern*
- Hierarchical: lead agent plans, delegates, synthesizes.
- **Your brain's `router.py` is this pattern.**
- Enhance it with explicit task cards and handoff checklists.

**3. Agent Teams**
- Parallel, independent subtasks.
- **Best for:** Embarrassingly parallel workloads.
- **Your use:** Multiple library articles processed in parallel.

**4. Message Bus**
- Event-driven communication.
- **Best for:** Flexible, decoupled interactions.
- **Your use:** Telegram bot commands → brain → integrations.

**5. Shared-State**
- Collaborative work on central data.
- **Best for:** Iterative refinement.
- **Your use:** `library/index.json` + `data/` as shared state.

### Recommendations for Your Multi-AI Team

From `docs/ai-employer-operating-system.md`:
- **Role-based protocols:** Each agent has a clear role (executor, researcher, reviewer).
- **Responsibility Levels (RL1-RL5):** Your RL governance is sound. Extend it to require two-model verification for RL4+ tasks.
- **Task cards:** Your template in `docs/templates/` is good. Add a "verification agent" field.
- **Branch authority:** Continue using `agent/<name>/<slug>/<scope>` naming.

---

## 5. Anti-Hallucination Layered Defense

### The Six-Layer Stack

Research from 2024–2026 shows combining techniques maximizes effect:

```
Layer 1: RAG with curated knowledge base + semantic search
    ↓
Layer 2: Constrained decoding / grammar enforcement (for code)
    ↓
Layer 3: Chain-of-thought prompting + citation requirements
    ↓
Layer 4: Static analysis + execution verification
    ↓
Layer 5: Faithfulness checking / LLM-as-judge (Claude ↔ Kimi)
    ↓
Layer 6: Human-in-the-loop for flagged/high-stakes outputs
```

**Combined impact:** RAG + verification + guardrails can reduce hallucinations by up to 96%.

### Layer 1: RAG (Your Library System)

Your `library/` folder IS a RAG system:
- `library/index.json` — semantic search index.
- `library/research/` — curated knowledge bundles.
- `library/references/` — canonical definitions.

**Enhancement:** Add vector embeddings to `library/index.json` for semantic similarity search. Use the embedding API from your Kimi or Gemini provider.

### Layer 2: Constrained Decoding

For code generation:
- Restrict imports to packages in `requirements.txt`.
- Validate API endpoints against `API_CONTRACT.md`.
- Use Pydantic models to enforce request/response shapes.

### Layer 3: Chain of Thought + Citations

**Prompt template:**
```
Before writing code:
1. List the files you need to read
2. Identify the key functions/classes to modify
3. Note any dependencies or side effects
4. Write the code
5. Verify: does this match the existing patterns in the codebase?

Cite specific files and line numbers for every claim.
```

### Layer 4: Static Analysis + Execution

**Your existing tests are this layer.** Expand:
- Add type checking with `mypy`.
- Add import validation (ensure no phantom packages).
- Add API contract tests (verify endpoints match spec).

### Layer 5: Two-Model Verification (Claude ↔ Kimi)

**Implementation:**
```python
# In src/agents/dispatcher.py or a new verifier module
def verify_code_with_kimi(code: str, context: str) -> str:
    """Have Kimi review Claude-generated code."""
    prompt = f"""
    Review this code for correctness, edge cases, and style consistency.
    
    Context: {context}
    Code: {code}
    
    Report any issues. If correct, say 'VERIFIED'.
    """
    return run_agent(task=prompt, provider="kimi")
```

### Layer 6: Human-in-the-Loop

Your existing `autopilot approve` command is this layer.
- RL1-RL3: Auto-approve.
- RL4: Require Kimi verification.
- RL5: Require human approval.

---

## Specific Recommendations for Your Setup

### Immediate Actions (This Week)

1. **Add `.claude/settings.json` hooks** for auto-test and auto-format.
2. **Implement two-model verification** in the brain: Claude generates, Kimi reviews.
3. **Add `mypy` to your test suite** for type-checking as anti-hallucination.
4. **Create a `verify` intent** in `router.py` that runs full test suite before executing.

### Short-Term (This Month)

5. **Add vector embeddings to `library/index.json`** for semantic search.
6. **Implement prompt caching** in your Kimi/Gemini dispatcher for repeated context.
7. **Create a `review` intent** that uses the generator-verifier pattern on code changes.
8. **Add API contract tests** to verify dashboard ↔ brain API compatibility.

### Medium-Term (This Quarter)

9. **Explore Claude Code Dynamic Workflows** for your agent orchestration.
10. **Add CRDT-based coordination** for parallel agent file editing (prevents merge conflicts).
11. **Implement automatic curriculum learning** for your autopilot system.
12. **Build a feedback loop** where human corrections train the RL governance model.

---

## Sources

- [Anthropic: Best Practices for Prompt Engineering](https://claude.com/blog/best-practices-for-prompt-engineering)
- [Claude Code Tips 2026](https://spunk.codes/blog/claude-code-tips-2026)
- [Kimi API Prompt Best Practices](https://platform.moonshot.ai/docs/guide/prompt-best-practice)
- [Promptfoo: How to Measure and Prevent LLM Hallucinations](https://www.promptfoo.dev/docs/guides/prevent-llm-hallucinations/)
- [Claude Code Dynamic Workflows](https://pasqualepillitteri.it/en/news/3663/claude-code-dynamic-workflows-anthropic-research-preview)
- [Multi-Agent Coordination Patterns](https://www.aiarainia.com/en/news/tools/multi-agent-coordination-patterns)
- [Claude Code Subagents Guide](https://turion.ai/blog/claude-code-multi-agents-subagents-guide/)
- [Kimi Code K2.6 Developer Guide](https://effloow.com/articles/kimi-code-k26-coding-model-developer-guide-2026)
- [LLM Grounding: How to Prevent AI Hallucinations in 2026](https://webcite.co/blog/llm-grounding-hallucination-prevention/)
