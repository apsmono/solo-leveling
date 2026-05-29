# Research Notes

## Key Findings

### Claude Code Maximization
- CLAUDE.md is the single most impactful configuration file
- Dynamic Workflows (May 2026) enable 1,000 subagents with 16 concurrent
- Hooks in .claude/settings.json transform Claude from tool to automation
- Multi-conversation workflows beat single overloaded sessions

### Kimi API Integration
- Three modes: Instant, Thinking, Agent
- Context placement: source material FIRST, instructions LAST
- 262K token context window for kimi-for-coding
- OpenAI-compatible API with base_url change

### Anti-Hallucination
- Six-layer defense stack reduces hallucinations up to 96%
- RAG most impactful single technique (40-70% reduction)
- Two-model verification (Claude + Kimi) is production-ready
- Test-driven generation is the best practical defense

### Multi-Agent Coordination
- Orchestrator-Subagent pattern matches current brain architecture
- Generator-Verifier pattern perfect for Claude+Kimi dual-AI setup
- Dynamic Workflows use JavaScript orchestration scripts
- CRDT-based coordination prevents merge conflicts

## Surprises
- Anthropic's Dynamic Workflows launched May 2026 — very recent
- Bun rewrite achieved 750K lines in 11 days using parallel agents
- Kimi's context window (262K) significantly larger than Claude's
- Promptfoo shows explicit uncertainty permission improves accuracy 55%→94%
