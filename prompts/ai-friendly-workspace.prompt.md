Initiate this workspace to be AI-friendly.

Create a lightweight AI collaboration scaffold that includes:

- `README.md` updated with an AI workspace section
- `AGENTS.md` with repository-wide agent instructions
- `AI_CONTEXT.md` with project intent, current phase, source-of-truth files, growth conventions, and collaboration rules
- `CHANGELOG.md` with a human-readable changelog template
- `docs/AI_CHANGELOG_POLICY.md` defining scalable changelog rules and timestamp format
- `.github/copilot-instructions.md` with GitHub Copilot-specific guidance
- `.vscode/extensions.json` with minimal AI and documentation extension recommendations
- `.vscode/settings.json` with conservative workspace settings that help documentation and AI-assisted work
- `AI_INSTALLATION.md` explaining the setup and how to reproduce it later
- `prompts/ai-friendly-workspace.prompt.md` containing the reusable bootstrap prompt

Requirements:

- Keep the scaffold minimal and project-focused.
- Base all documentation on the actual purpose and current state of the repository.
- Avoid filler, speculative roadmap content, and unsupported technical assumptions.
- Make the AI-facing files work both now and as the project grows.
- Add instructions that AI must update changelog, documentation, and short descriptions whenever relevant changes are made.
- Use local device time in the format `YYYY-MM-DD HH-mm-ss` for changelog entries.
- Update existing files instead of replacing project intent.
- If the repository is early-stage, optimize for documentation-first collaboration.
