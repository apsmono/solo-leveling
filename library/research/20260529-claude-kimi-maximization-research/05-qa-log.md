# Q&A Log

## Q: Can Claude Code and Kimi API work together in the same session?
**A:** Yes. Claude Code handles IDE integration, tool use, and orchestration. Kimi API provides coding reasoning via the dispatcher module. The pattern is: Claude generates → Kimi verifies → tests confirm.

## Q: What is the most impactful single change for anti-hallucination?
**A:** Test-driven generation: generate tests first, then implementation, then verify. Your existing 37-test suite is your best defense.

## Q: How does Dynamic Workflows compare to my brain's orchestration?
**A:** Your brain's `router.py` IS an orchestrator-subagent pattern. Dynamic Workflows adds JavaScript scripting for scale (1,000 agents). You could migrate your orchestration to Claude Code workflows for massive parallel tasks.

## Q: Should I switch from pip to Poetry/uv for dependency management?
**A:** Not yet. Your current pip + requirements.txt is simple and works. The decision record (ADR-007) covers this. Switch only if you need lock files for reproducible deployments.
