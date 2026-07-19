# 2026-07-16: GitHub Push Protection — Directory-Level Exclusion + gh API Fallback

## Context

Backing up `demo-pm` profile to `OnePlusNDev/hermes-config`. Initial commit included reference docs under `pm-triage-cron/references/` and `hermes-profile-backup/references/` that contained hex-encoded tokens from past session transcripts.

## Problem

Two blocking issues prevented a clean git push:

1. **SSH/HTTPS git push unavailable**: SSH key bound to `zhangtbj` account (no `OnePlusNDev` write access). HTTPS to `github.com:443` timed out even though `api.github.com:443` worked.

2. **GitHub push protection (GH013)**: Reference docs with hex-encoded tokens triggered secret scanning on blob upload via `gh api` Git Data API. Error: `HTTP 422 — Secret detected in content`.

## Solutions

### Issue 1: Multi-account SSH mismatch — switch to `gh api` Git Data API

```
SSH key (id_ed25519_jordanzt) → zhangtbj (read-only)
HTTPS port 443 → timeout
curl api.github.com:443 → works
```

**Workaround**: Use `gh api` Git Data API instead of `git push`:

1. `GET /repos/{owner}/{repo}/git/ref/heads/main` → get HEAD SHA
2. `GET /repos/{owner}/{repo}/git/commits/{sha}` → get tree SHA
3. For each changed file: `POST /repos/{owner}/{repo}/git/blobs` → create blob, get SHA
4. `POST /repos/{owner}/{repo}/git/trees` → create tree with all entries (unchanged files from remote + new blobs)
5. `POST /repos/{owner}/{repo}/git/commits` → create commit
6. `PATCH /repos/{owner}/{repo}/git/refs/heads/main` → update branch

**Key implementation detail**: After a local `git commit`, use `git ls-tree -r HEAD` (not `git status`) to enumerate local file tree. `git status --porcelain` returns empty because the commit is already done.

### Issue 2: Push protection on reference docs — directory-level .gitignore exclusion

**Detection**: The error appeared only after uploading all blobs and attempting tree creation. Individual blob uploads succeeded but the push failed at the ref update phase (all blobs scanned together).

**Fix**: Add entire reference doc directories to `.gitignore`:

```gitignore
# Reference docs with hex-encoded tokens (trigger GitHub push protection)
demo-pm/skills/devops/pm-triage-cron/references/
demo-pm/skills/devops/hermes-profile-backup/references/
```

Since these are in a repo subdirectory (`demo-pm/...`), the `.gitignore` needs the full relative path without `**/` prefix (it's scoped to the repo root).

**Note**: The existing backup script (`scripts/gh-api-standalone-backup.py`) already had these files in its exclusion list — but the `.gitignore` didn't, so `git status` kept showing them as untracked.

**Files excluded** (all under `references/` dirs):
- `pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md`
- `pm-triage-cron/references/2026-07-12-session-base64-token-extraction.md`
- `pm-triage-cron/references/2026-07-12-session-cat-heredoc-plus-python.md`
- `pm-triage-cron/references/2026-07-16-session-*-star-star-star*.md`
- `hermes-profile-backup/references/demo-pm-backup-workflow-*.md` (multiple dates)

## Final Push Result

**8 files committed and pushed** via `gh api` Git Data API:
- `.gitignore` — updated with demo-pm curator/reference exclusions
- `demo-pm/cron/jobs.json` — updated
- `demo-pm/cron_triage.py` — new
- `demo-pm/triage_check.py` — new
- `demo-pm/memories/archive/ARCHIVE.md` — updated
- `demo-pm/skills/devops/hermes-profile-backup/SKILL.md` — updated
- `demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-backup.py` — new
- `demo-pm/skills/devops/pm-triage-cron/SKILL.md` — updated

Push commit: `881c67e`

## Takeaway

For future backups of this profile: always exclude the `pm-triage-cron/references/` and `hermes-profile-backup/references/` directories before staging files. The `gh api` Git Data API push method is the reliable fallback when SSH/HTTPS git push fails.
