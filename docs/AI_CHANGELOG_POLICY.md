# AI Changelog Policy

## Goal

Maintain a changelog that scales with the project, remains easy for humans to scan, and stays reliable for AI-assisted work.

## Research Summary

This policy follows the useful parts of Keep a Changelog:

- Changelogs are for humans, not raw commit dumps.
- Notable changes should be grouped by type.
- The latest relevant information should appear first.
- Dates must be unambiguous and consistent.

This repository extends that baseline with per-entry timestamps using local device time so work can be traced more precisely during active development.

## Required Timestamp Format

Use local device time with this exact format:

- `YYYY-MM-DD HH-mm-ss`

Example:

- `2026-04-17 14-30-41`

## File Structure

Use a single top-level `CHANGELOG.md` as the primary human-readable log.

Recommended structure:

```md
# Changelog

## Unreleased

### Added

- 2026-04-17 14-30-41 Added a reusable prompt library for AI setup.

### Changed

- 2026-04-17 14-35-10 Refined agent rules to require documentation updates with implementation changes.

### Docs

- 2026-04-17 14-40-22 Expanded repository setup instructions for future contributors.
```

## Section Rules

Use only sections that have content. Prefer these headings:

- `Added` for new capabilities, files, or workflows
- `Changed` for behavior, structure, or process updates
- `Fixed` for bug fixes and corrections
- `Removed` for deleted capabilities or content
- `Docs` for meaningful documentation updates
- `Decisions` for project-level policy or direction changes

## Scalability Rules

- Keep a single `Unreleased` section during active development.
- Add entries at the top of the relevant subsection so the newest notes are seen first.
- Keep each entry to one line when possible.
- Describe impact, not implementation noise.
- Combine related low-level edits into one higher-value changelog entry.
- Do not log trivial formatting-only changes unless they affect understanding or workflow.
- If the project later adopts releases, move grouped `Unreleased` entries into dated release sections without changing the original entry timestamps.

## Human Readability Rules

- Write for someone scanning quickly.
- Start entries with a past-tense action such as `Added`, `Updated`, `Documented`, `Defined`, `Removed`, or `Fixed`.
- State why the change matters when the impact is not obvious.
- Avoid internal-only jargon unless the term already exists in repository documentation.
- Do not paste raw commit messages into the changelog.

## AI Maintenance Rules

AI assistants working in this repository should follow these rules on every notable change:

1. Update `CHANGELOG.md` in the same change.
2. Update any affected documentation, descriptions, setup steps, or usage notes in the same change.
3. If a file or workflow meaning changes, update the nearest source-of-truth document instead of leaving stale text behind.
4. If a change is too small for the changelog, still update documentation when meaning or usage changed.

## Planning Recommendation

As this repository grows, keep the changelog system simple:

1. Keep `CHANGELOG.md` as the main curated history.
2. Keep policy and examples in this document, not mixed into the changelog itself.
3. Add release sections later only when releases become real.
4. Revisit section names only when the current set stops serving human readers.
