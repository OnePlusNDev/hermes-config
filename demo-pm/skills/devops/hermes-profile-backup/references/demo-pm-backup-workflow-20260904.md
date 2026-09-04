# demo-pm backup workflow — 2026-09-04

## Result
CLEAN Method B (standalone-subtree) run. Main commit `5fb64c58` (6M+0A+0D).
Follow-up run-note commit (same session): this note + dated-runs-index bullet +
exclude syncs (`gh-api-standalone-backup.py`, `gitignore-template.txt`,
SKILL.md rsync list).

## Security check (pre-backup)
- config.yaml scanned: **NO plaintext keys** — all `api_key:`/`secret:` values
  are empty strings (`''`), zero `sk-`/`ghp_`/`gho_`/hex/base64 matches. No
  `key_env` replacement needed.
- Preflight scan: CLEAN (no full token patterns in upload candidates).

## New exclude gap found + fixed this run
Preflight showed 3 `A` files under root-level temp dirs, all PM-triage
diagnostic crosscheck scripts that read `.env` for `GITHUB_TOKEN`:
- `demo-pm/tmp/pm_crosscheck_20260904.py` (opens `~/.hermes/profiles/demo-pm/.env`)
- `demo-pm/tmp/triage_crosscheck_0904.py` (reads env GITHUB_TOKEN)
- `demo-pm/tmp_pm/crosscheck_triage.py` (opens `.env`)

Same diagnostic-artifact family as `tmp_triage/`, `pm_triage_*.py`,
`query_issues.py` etc. Fixed with a **root-scoped** rule in all three backup
scripts (`if parts[0] in ("tmp", "tmp_pm"): return True` in should_exclude) —
scoped to root deliberately, since a blanket `tmp` dir exclude could swallow
legit nested dirs (health_ lesson, 2026-08-28). Also synced:
`templates/gitignore-template.txt` (`demo-pm/tmp/`, `demo-pm/tmp_pm/` anchored
patterns) and the SKILL.md Method A rsync list (`--exclude '/tmp/'` +
`--exclude '/tmp_pm/'`, root-anchored). Re-ran preflight: New 3 -> 0, scan CLEAN.

## Files backed up (main commit: 6 M)
- M cron/jobs.json
- M memories/archive/ARCHIVE.md
- M skills/devops/hermes-profile-backup/references/dated-runs-index.md
  (local carried the final 09-03 bullet with the follow-up/divergence lesson —
  an uncommitted last-session edit, same pattern as 09-01 -> 09-02)
- M skills/devops/hermes-profile-backup/references/demo-pm-backup-workflow-20260903.md
  (same uncommitted final-edit pickup)
- M skills/devops/hermes-profile-backup/scripts/gh-api-standalone-subtree-backup.py
  (tmp/tmp_pm root-scoped exclude)
- M skills/devops/hermes-profile-backup/scripts/preflight-backup-scan.py
  (tmp/tmp_pm root-scoped exclude)

Follow-up commit: run note (this file) + index bullet +
`gh-api-standalone-backup.py` + `gitignore-template.txt` + SKILL.md rsync list
syncs.

## Auth / method
- Active gh user at start: OnePlusNTester (read-only, `permissions.push=false`)
  -> switched to OnePlusNDev (repo owner, `permissions.push=true`) before
  anything; no account flip after that.
- Remote HEAD advanced between first ref check (b312dc70) and preflight
  (f6810d72 = demo-dev's concurrent 2026-09-04 backup) — expected on this
  shared multi-profile repo; standalone-subtree re-parents onto current HEAD.
- Method B standalone-subtree (no clone needed). Blob uploads: 6, no
  push-protection skips.

## Post-push remote verification (all passed)
- remote config.yaml `sk-` count: 0
- sensitive files in tree (.env, auth.*, home/, .local/, bin/tirith, state.db):
  NONE
- temp/diag files under demo-pm (tmp_*.py, /tmp/, /tmp_pm/, triage_*,
  pm_health*): NONE
- top-level distribution: demo-pm 598, demo-dev 5, demo-tester 8, tester-01 5
  (siblings intact), + .gitignore
- ref check after push: main = 5fb64c58 (no concurrent race this time)
