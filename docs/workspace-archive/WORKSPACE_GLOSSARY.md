# Glossary

Shared terminology across the workspace. Project-specific deep definitions live in each submodule's own `GLOSSARY.md` (notably `solo-leveling/GLOSSARY.md`).

## Workspace structure

- **Parent repo / workspace** — `apsmono/projects`; the container repository that pins each project as a submodule.
- **Submodule** — An independent git repository nested inside the parent at a fixed commit SHA. Each has its own history, CI/CD, and deploy target.
- **Pin / SHA bump** — Recording a submodule's new commit in the parent (`git add <submodule>` then commit). The parent always points at one specific commit per submodule.
- **Scaffolding directory** — `scrapers/` and `microservices/`; tracked directly in the parent repo (not submodules), containing templates/stubs for future work.

## The brain (solo-leveling)

- **Brain** — The `solo-leveling` FastAPI backend; the central command center that receives commands, routes them, and orchestrates integrations and AI.
- **Command** — A natural-language string sent to `POST /command` (or via Telegram), e.g. `"add to library: Model Context Protocol"`.
- **Intent** — The classified meaning of a command. Detected by keyword matching against the **Intent Map** in `core/router.py`, then dispatched to a handler.
- **Intent Map** — `INTENT_MAP` in `router.py`: ~25 intents (help, status, library_capture, library_search, workflow, ask_ai, autopilot, reminder, github_issue, …) mapped to keyword triggers.
- **Stage** — A numbered build phase of the brain (Stages 1–9). Stages 1–8 are complete; **Stage 9** (Personal Knowledge Libraries) is the active phase. Source of truth: `solo-leveling/AI_CONTEXT.md`.
- **Library** — The local-first markdown knowledge store under `library/`, organized into sections: `profile`, `terms`, `books`, `articles`, `thoughts`, `references`, `research`. Indexed by `library/index.json`.
- **Deep Capture** — Stage-9 flow that turns `"add to library: <topic>"` into a 7-file research bundle via Gemini analysis (after a sensitive-content check).
- **Research Bundle** — The 7-file structure produced by Deep Capture: `index.md`, `01-raw-input`, `02-search-history`, `03-research-notes`, `04-information-to-track`, `05-qa-log`, `06-logic-trail`, `07-conclusion`.
- **Workflow** — A Stage-8 multi-step chain composing several integrations (e.g. summarize Gmail inbox → save to Notion). Defined in `core/workflows.py`.

## AI & agents

- **Agent (LLM agent)** — A program that uses an LLM to plan and/or act. In this workspace the primary agent runtime is **Autopilot**; the primary LLM is **Gemini**.
- **Dispatcher** — `agents/dispatcher.py`; the Gemini REST wrapper (`run_agent(task, context, system)`).
- **Autopilot** — The brain's autonomous task subsystem: plan a goal into steps, execute them via a tool registry, record observations, and advance — gated by RL governance.
- **Responsibility Level (RL1–RL5)** — The autonomy/safety tier governing what Autopilot may do without human approval (RL1 read-only/review-each-step → RL5 destructive/always-approve). Enforced by `autopilot/governor.py`.
- **Tool registry** — The set of callable actions Autopilot can invoke (read, bash, gmail_read, library_index, …) in `autopilot/tools.py`.
- **Task card / task record** — A persisted Autopilot task (goal, plan, current step, observations) stored as JSON under `data/`.
- **ADR (Architecture Decision Record)** — A numbered decision document under `solo-leveling/docs/decisions/` (e.g. the Gemini-primary pivot, the RL governance model).

## Coding-agent guidance

- **AI agent (here: Claude Code)** — An assistant editing this workspace. Operating rules live in `AI_AGENTS.md`, `AGENTS.md`, and `CLAUDE.md`.
