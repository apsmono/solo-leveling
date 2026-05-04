# Subproject Linking Workflow

Subprojects live as actual files inside `subprojects/` so the monorepo remains the source of truth. On every push to `main`, `.github/workflows/sync-subprojects.yml` copies each subproject to its standalone external repository and pushes to `main`.

## Current Mapping

| Monorepo Path | External Repo | Local Clone | Deploy Target |
|---------------|---------------|-------------|---------------|
| `subprojects/dashboard` | `apsmono/dashboard` | `../projects/dashboard` | GitHub Pages |
| `subprojects/wedding-invitation` | `apsmono/wedding-invitation` | `../projects/wedding-invitation` | Cloudflare Pages |
| `subprojects/koperasi-landing` | `apsmono/koperasi` | `../projects/koperasi` | Cloudflare Pages |

## How Sync Works

### CI (GitHub Actions)

`.github/workflows/sync-subprojects.yml` triggers on push to `main`:

1. Checks out `solo-leveling`
2. Checks out each external repo using `SYNC_PAT`
3. Copies deployable files to the external repo
4. Commits and pushes to the external repo's `main`

**Wedding invitation is special:** the workflow runs `npm ci` + `npm run build` in `subprojects/wedding-invitation/` and copies **`dist/*`** to `apsmono/wedding-invitation` (static output at the repo root). The monorepo path still holds the **full Vite/React source**. Do not expect the external repo’s `main` tree to match a source checkout line-for-line.

**Dashboard and Koperasi:** synced as project files from `subprojects/` (see the workflow for exact copy rules).

### Local Development

Edit files directly in `subprojects/` inside the monorepo, then commit and push to `solo-leveling`. To copy **monorepo source** into your local clones (paths are hard-coded in the script; includes `../projects/wedding-invitation` on this machine):

```bash
./scripts/sync-subprojects.sh
```

The script uses `rsync --delete` so the clone’s tracked app files match the monorepo folder; extra top-level files from an older clone layout (for example legacy `.github/` or `AGENTS.md` beside the app) can be removed—intentional if that clone is only a mirror of `subprojects/<name>/`. It skips `node_modules`, `dist`, and `.claude`; after sync, run `npm ci` (and `npm run build` if you need `dist/`) inside `wedding-invitation`.

To align a clone with **GitHub `main` on the external repo** (for `wedding-invitation`, that is the **built** site from CI, not the React source), use `git pull --ff-only` in that clone instead of the script.

Or manually copy files to `../projects/dashboard`, `../projects/wedding-invitation`, or `../projects/koperasi`.

## Why This Approach

- **Source of truth in monorepo**: all subproject code is tracked in `solo-leveling`
- **Auto-sync on release**: merging `development -> main` pushes subprojects automatically
- **External repos stay lean**: each repo contains only its own deployable files
- **Local clones for convenience**: you can still develop in `../projects/X` and copy back to `subprojects/` when done
