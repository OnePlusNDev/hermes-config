# demo-pm backup run — 2026-09-11

## Result
**Method B (standalone subtree, no clone)** — success.
Commit: `1cb42187ea8b12ee51fb60708bc2efffef10d1f9`
URL: https://github.com/OnePlusNDev/hermes-config/commit/1cb42187ea8b12ee51fb60708bc2efffef10d1f9

## Pre-flight
- `gh api user` → `OnePlusNTester` (NOT the repo owner; `permissions.push` = **false**)
  → `unset GITHUB_TOKEN; gh auth switch --user OnePlusNDev` → active user `OnePlusNDev`, push = **true**
- config.yaml plaintext scan: `sk-[A-Za-z0-9]{20,}` → no match; all **15** `api_key:` entries are `''` (empty)
  → no plaintext key found, no key_env replacement needed
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **7**, New **0**, Deleted **0**; token scan **CLEAN**

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/channel_directory.json
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
```

## Execution notes
- First script run hit **HTTP 422 non-fast-forward** on the ref PATCH (remote HEAD advanced
  `c40df19cc20b` → `163c7f57eca5` mid-run). The documented plain re-run absorbed it —
  blob uploads are idempotent (same 7 blob SHAs both passes), re-read of remote HEAD
  re-parented the commit. Second run succeeded on first attempt.
- The repeated 422 across recent runs (09-06, 09-07, 09-09, 09-11) points to a consistently
  concurrent sibling profile backup advancing `main` during the ~1–2 min blob phase.
  Budget for one re-run each session; no tree surgery needed.

## Post-push remote verification
- Remote `demo-pm/config.yaml`: `sk-` matches = **0**; non-empty `api_key` = **0**
- Total blobs **625**; `demo-pm` **606**; siblings intact — demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db`, `processes.json`,
  `bin/tirith`, `home/`, `.local/`) → **NONE**
- Temp/diagnostic script check (`pm_healthcheck`, `tmp_*.py`, `triage_*.py`,
  `cron_triage.py`) → **NONE**
