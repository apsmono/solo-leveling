# Information to Track

## Metrics to Monitor
- Hallucination rate: Track incorrect API/package references in generated code
- Test pass rate: Before/after AI-generated changes
- Context window usage: Average fill rate per session
- Session duration: Time before `/compact` or context exhaustion
- Verification agreement: Claude↔Kimi agreement rate on code reviews

## Experiments to Run
1. Two-model verification on 10 code changes → measure bug catch rate
2. Dynamic Workflows for library indexing → compare speed vs single agent
3. Prompt caching for repeated brain commands → measure latency reduction
4. Vector embeddings for library search → measure relevance improvement

## Follow-Up Research Needed
- Claude Code Dynamic Workflows implementation details
- Vector embedding providers (cost/quality comparison)
- CRDT libraries for Python (for agent coordination)
- Automatic curriculum learning for RL governance
