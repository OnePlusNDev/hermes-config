# demo-pm backup workflow — 2026-09-03

## Result
CLEAN Method B (standalone-subtree) run. Main commit `dfc1dcc` (8M+2A+0D).
Final HEAD after run-note follow-up: `b312dc70` (1M+1A, re-pushed over a
concurrent demo-dev commit — see "Follow-up divergence" below).

## Follow-up divergence (concurrent demo-dev push raced the ref)
Run-note follow-up commit `16b71845` (parent `dfc1dcc`) was created and the
script exited 0, but a concurrent demo-dev backup (`b104d084`, ALSO parented on
`dfc1dcc`) won the ref PATCH race — `main` pointed at `b104d084`, not at my
commit. Detection: `gh api repos/OnePlusNDev/hermes-config/git/refs/heads/main
--jq '.object.sha'` differed from the printed commit SHA, and
`gh api .../compare/<current-head>...<my-sha> --jq '.status, .ahead_by, .behind_by'`
returned `diverged 1 1` (my commit was a divergent orphan, not on main).
Recovery: re-ran the standalone-subtree script — blob uploads are idempotent
(same content -> same SHA), and it re-parents onto the CURRENT remote HEAD, so
the re-run produced `b312dc70` with parent `b104d084`. Verified linear chain:
b312dc70 -> b104d084 -> dfc1dcc. Lesson: after ANY Method B push (including a
same-session run-note follow-up), verify the remote ref before declaring
success — exit 0 + "Remote HEAD now: X" is not a guarantee X is still main
seconds later on this multi-profile shared repo.

## Security check (pre-backup)
- config.yaml scanned: **NO plaintext keys** — all 15 `api_key:` values are
  empty strings (`''`), zero `sk-`/`ghp_`/`gho_`/hex/base64 matches. No
  `key_env` replacement needed.
- Preflight scan: CLEAN (no full token patterns in upload candidates).

## New exclude gap found + fixed this run
Preflight showed `A demo-pm/skills/devops/pm-triage-cron/scripts/__pycache__/
full_triage.cpython-313.pyc` — a Python bytecode cache (runtime artifact, not
config) that matched NO existing exclude. Fixed by adding `__pycache__` to
EXCLUDE_DIRS in all three backup scripts
(`gh-api-standalone-subtree-backup.py`, `gh-api-standalone-backup.py`,
`preflight-backup-scan.py`), plus `--exclude '__pycache__/'` + `*.pyc` in the
SKILL.md rsync list and `**/__pycache__/` + `**/*.pyc` in
`templates/gitignore-template.txt`. Re-ran preflight: pyc gone (New 3 -> 2).

## Files backed up (8 M + 2 A)
- M cron/jobs.json
- M memories/archive/ARCHIVE.md
- M skills/devops/hermes-profile-backup/SKILL.md (exclude docs + rsync list)
- M skills/devops/hermes-profile-backup/scripts/gh-api-standalone-backup.py
- M skills/devops/hermes-profile-backup/scripts/gh-api-standalone-subtree-backup.py
- M skills/devops/hermes-profile-backup/scripts/preflight-backup-scan.py
- M skills/devops/hermes-profile-backup/templates/gitignore-template.txt
- M skills/devops/pm-triage-cron/SKILL.md
- A skills/devops/hermes-profile-backup/references/dated-runs-index.md
- A skills/devops/pm-triage-cron/references/2026-09-03-session-script-plus-list-endpoint-crosscheck.md

## Auth / method
- Active gh user at start and before push: OnePlusNDev (repo owner,
  `permissions.push=true`); no account flip observed this run.
- Method B standalone-subtree (no clone needed; remote HEAD absorbed
  automatically). Blob uploads: 10, no push-protection skips.

## Post-push remote verification (all passed)
- remote config.yaml `sk-` count: 0
- sensitive files in tree (.env, auth.*, home/, .local/, bin/tirith,
  __pycache__, *.pyc): NONE
- top-level distribution: .gitignore 1, demo-dev 5, demo-pm 597 (was 595,
  +2 new), demo-tester 8, tester-01 5 — siblings intact
- new files confirmed present in remote tree
