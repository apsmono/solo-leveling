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
3. Copies files from `subprojects/<name>/` to the external repo
4. Commits and pushes to the external repo's `main`

### Local Development

Edit files directly in `subprojects/` inside the monorepo, then commit and push to `solo-leveling`. To sync locally to your external clones before CI runs:

```bash
./scripts/sync-subprojects.sh
```

Or manually copy files to `../projects/dashboard`, `../projects/wedding-invitation`, or `../projects/koperasi`.

## Why This Approach

- **Source of truth in monorepo**: all subproject code is tracked in `solo-leveling`
- **Auto-sync on release**: merging `development -> main` pushes subprojects automatically
- **External repos stay lean**: each repo contains only its own deployable files
- **Local clones for convenience**: you can still develop in `../projects/X` and copy back to `subprojects/` when done
