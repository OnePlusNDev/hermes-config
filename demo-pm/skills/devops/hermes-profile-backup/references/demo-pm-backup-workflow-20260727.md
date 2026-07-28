# Backup Workflow — 2026-07-27

## Summary
29-file backup (18 modified, 11 new) via gh API Git Data API (Method B). Active user `OnePlusNPM` pushed blobs to repo `OnePlusNDev/hermes-config` as a collaborator — no account switch needed. 6 files skipped by push protection (kept remote versions).

## Key discovery: collaborator-owner OWNER mismatch

The standalone script resolved `OWNER` dynamically via `gh api user --jq '.login'` → `OnePlusNPM`. But the repo is owned by `OnePlusNDev`. Since `OnePlusNPM` is a **collaborator** on `OnePlusNDev/hermes-config`:

- `gh api repos/OnePlusNDev/hermes-config/...` works (collaborator write access)
- `gh api repos/OnePlusNPM/hermes-config/...` would 404 (OnePlusNPM doesn't own the repo)

**Fix:** Script needed `OWNER = "OnePlusNDev"` hardcoded. The standalone script was patched to accept `REPO_OWNER` env var:

```bash
REPO_OWNER=OnePlusNDev python3 /tmp/gh-api-standalone-backup.py
```

This is a different pattern from the existing `gh auth switch --user` pitfall — no account switch needed, just use the correct owner in the API endpoint URL.

## Architecture

```
Active user:  OnePlusNPM (collaborator)
Repo owner:   OnePlusNDev
gh API:       repos/OnePlusNDev/hermes-config/...   ← works
              repos/OnePlusNPM/hermes-config/...    ← 404
Method:       gh API Git Data API (clone timed out on port 443)
Files:        560 total, 29 changed, 6 skipped (push protection)
```

## Backup details

| Metric | Value |
|--------|-------|
| Commit | `bd25578b38c01a0e40d86ea1c958821135f3d9d6` |
| Changed | 18 (modified) |
| New | 11 |
| Deleted | 0 |
| Skipped (push protection) | 6 |
| URL | https://github.com/OnePlusNDev/hermes-config/commit/bd25578b38c0 |

## Push-protected files (kept remote versions)

Same set as previous sessions:
- `hermes-profile-backup/SKILL.md`
- `hermes-profile-backup/references/2026-07-25-grep-truncation-hides-full-tokens.md`
- `pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md`
- `pm-triage-cron/references/2026-07-12-session-base64-token-extraction.md`
- `pm-triage-cron/references/2026-07-12-session-cat-heredoc-plus-python.md`
- `pm-triage-cron/references/2026-07-16-session-gh-repo-view-precheck.md`

## Lessons

1. **Script OWNER resolution must use repo owner, not active user.** Active user having collaborator access is sufficient for the gh API, but the endpoint URL must reference the repo owner. This is easy to miss because `gh api repos/OWNER/REPO` succeeds silently — you only notice the 404 when the script constructs the wrong URL.
2. **No plaintext API keys** in config.yaml — all `api_key` values were empty strings `''`. No action needed.
3. **`gh repo list <active_user>` does not show repos owned by other users** that the active user collaborates on. Use `gh api user/repos` instead.
