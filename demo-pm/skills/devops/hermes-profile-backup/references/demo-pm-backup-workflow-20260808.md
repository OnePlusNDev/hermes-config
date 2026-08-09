# demo-pm backup workflow — 2026-08-08

Clean config + 6-file backup + legacy temp-script cleanup commit. No push protection blocks.

## Run summary

- **Config check:** no plaintext keys — all 14 `api_key:` values empty strings; no `sk-` matches. No key_env rewrite needed.
- **Changes committed (commit 1, `5330209e`):** cron/jobs.json (run counters), scripts/start_hindsight_daemon.sh (absolute → `~` paths), hermes-profile-backup SKILL.md (+13 doc lines incl. rsync DST pitfall), gh-api-git-data-incremental-push.py (Step 5 fix), pm-triage-cron SKILL.md (+10), new references/demo-pm-backup-workflow-20260807.md.
- **git push failed** (`Failed to connect to github.com port 443 after 75001 ms`), `gh api repos/... --jq '.id'` worked → Method B (gh API Git Data API) via the incremental-push script. Copied script to /tmp, patched hardcoded `WORKTREE` constant to the current clone path, ran it.
- **Post-push scan found legacy tracked temp scripts** `demo-pm/triage_fetch.py` and `demo-pm/triage_v5.py` in the remote tree (committed in prior backups before their exclude patterns existed). No secrets in content (they read GITHUB_TOKEN from .env at runtime).
- **Cleanup commit (commit 2, `88b26abd`):** `git rm --cached` both files, committed locally, re-ran the incremental-push script — it detected them as Deleted (2) and pushed the removal. Sibling profiles intact (demo-dev 5, demo-tester 8, tester-01 5).

## New exclude patterns added this run

- `**/pm_healthcheck_*.py` — dated one-off health-check scripts (`pm_healthcheck_0807b.py` reads GITHUB_TOKEN from .env; diagnostic artifact, not config). This file slipped past rsync on first pass — it was in `git status` as untracked; removed from clone + excluded.
- `**/triage_fetch.py`, `**/triage_v5.py` — triage script variants, now in rsync excludes + .gitignore docs so `git add -A` doesn't re-add them after the index removal.

## New pitfalls captured in SKILL.md

1. **Complex `--jq` regexes fail** — `test("\.env$|...")` in `--jq` errors with `invalid escape sequence "\." in string literal` (shell + jq double-parsing mangles backslashes). Fix: dump all blob paths to a temp file and grep (`gh api ... --jq '.tree[] | select(.type=="blob") | .path' > /tmp/remote_paths.txt`).
2. **Fuzzy matcher eats adjacent list lines** — patching a bullet into this skill's own exclude-list docs silently deleted the following `**/._*` bullet. Re-read the patched region after list edits.

## Verification commands that passed

- Remote config.yaml `sk-` grep count: 0
- Remote api_key values: all empty strings
- Sensitive-file path grep on remote tree: NONE
- Temp-script path grep on remote tree: NONE (after cleanup commit)
- Sibling dir distribution: demo-dev 5 / demo-tester 8 / tester-01 5 / demo-pm 569
