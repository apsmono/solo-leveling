# Research: Deployable AI With Short Context + Specific Per-AI Tasks

Date: 2026-04-23

## Research question

How do we keep AI context short for deployment while still improving execution quality across multiple AIs?

## Short answer

Yes, your intuition is correct:

- Global context should be short and stable.
- Execution detail should move into task-specific briefs per AI role.

This gives better reliability than one long shared prompt.

## Evidence summary

### OpenAI prompt engineering guidance

Key findings from OpenAI docs (`developers.openai.com`):

- GPT-family models are more reliable with explicit instructions and clear output constraints.
- Split instructions by authority (developer/system rules vs user input) to reduce ambiguity.
- Structure prompts using clear sections (identity, instructions, examples, context).
- Include only relevant context and keep reusable/static context separate for caching and consistency.
- Use evals to measure prompt quality and iterate instead of growing prompts blindly.

Implication for this repo:

- Keep one short deployable base context and avoid embedding all project history.
- Pass execution specifics via task cards and role briefs.

### Anthropic guidance (Prompting best practices + Building effective agents)

Key findings from Anthropic docs (`platform.claude.com`, `anthropic.com/engineering`):

- Models follow instructions literally; underspecified prompts cause weak execution.
- Best results come from simple, composable workflows rather than over-complex orchestration.
- Use explicit output format and success criteria.
- For agentic tasks, clarify when to act, when to ask, and when to stop.
- Use structured tags/sections and examples to improve consistency.
- Routing and orchestrator-worker patterns are effective when tasks are decomposed clearly.

Implication for this repo:

- Define a concise shared mission + constraints.
- Assign each AI a narrow, concrete objective with acceptance criteria and evidence requirements.

## Recommended operating model for this repository

Use a 2-layer context model.

### Layer 1: Short deployable shared context (always-on)

Target size: 8-20 lines.

Include only:

1. Mission
2. Current stage and top priority
3. Hard constraints (security, branch/release policy, no secret leakage)
4. Definition of done

Exclude from Layer 1:

- Large historical notes
- Long examples
- Detailed implementation plans
- Full architecture narrative

### Layer 2: Per-task execution brief (assigned to each AI)

Each AI gets a focused brief with:

1. Objective (single sentence)
2. In scope / out of scope
3. Files allowed to edit
4. Required commands/tests
5. Acceptance criteria (binary checklist)
6. Evidence to return
7. Handoff format

This is where detail belongs.

## Copy-paste templates

### Template A: Short deployable shared context

```md
# Deployable AI Context (Short)

Mission: Keep this command center reliable for WhatsApp-driven personal OS automation.
Current stage: Stage 9 (library hardening + end-to-end readiness).
Top priority this cycle: finish credential-backed E2E validation and deployment reliability.

Hard constraints:
- Never expose or commit secrets.
- Follow branch flow: agent/* -> development -> main.
- Update CHANGELOG.md for notable changes with local timestamp format.
- Keep edits minimal and scoped; no speculative refactors.

Definition of done:
- Required tests/validation pass.
- Docs reflect behavior changes.
- Clear handoff notes with what changed and why.
```

### Template B: Per-AI execution brief

```md
# AI Task Brief

AI Role: <Research|Implementer|Validator|Release>
Objective: <single concrete outcome>

In scope:
- <bullet 1>
- <bullet 2>

Out of scope:
- <bullet 1>

Editable files:
- <path 1>
- <path 2>

Run/verify:
- <command 1>
- <command 2>

Acceptance criteria:
- [ ] <binary result 1>
- [ ] <binary result 2>
- [ ] <binary result 3>

Return evidence:
- changed files
- command outputs summary
- risks/assumptions

Handoff format:
1. What was done
2. What is pending
3. Exact next command for next AI
```

### Template C: Task decomposition for multi-AI

```md
Orchestrator AI:
- classify request
- split into 2-4 independent workstreams
- assign explicit deliverables and stop conditions

Worker AI (each):
- execute only assigned scope
- return evidence against checklist
- no policy changes without approval

Validator AI:
- verify outputs vs acceptance criteria
- reject if evidence missing

Release AI:
- update changelog/docs
- finalize commit/push/tag
```

## Practical prompt style rules (high-impact)

1. Use imperative, specific instructions: "Edit X, run Y, report Z".
2. State output format explicitly (e.g., checklist, JSON, numbered findings).
3. Put constraints before context.
4. Add 1-2 examples only when format compliance is poor.
5. Use stop conditions ("Stop after validation pass/fail report").
6. Prefer short context + referenced files over long narrative memory.

## Anti-patterns to avoid

- One giant prompt with mission, history, policy, and task mixed together.
- Role prompts without acceptance criteria.
- Ambiguous tasks like "improve this" without files/commands.
- Repeating global context in every task brief.
- Measuring success by "looks good" instead of binary checks.

## Suggested next step for this repo

Pilot this model in the next coordinated task:

1. Keep shared context under 20 lines in orchestrator prompt.
2. Create 3 role briefs (Implementer, Validator, Release).
3. Measure:
   - completion speed
   - number of clarification loops
   - rework count
   - merge readiness on first pass

If metrics improve for 2 cycles, adopt this as default multi-AI execution style.

## Source links used

- OpenAI Prompt Engineering Guide: https://developers.openai.com/api/docs/guides/prompt-engineering
- Anthropic Prompting Best Practices: https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents
