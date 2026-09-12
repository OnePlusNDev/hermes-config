# demo-pm backup run — 2026-09-12

## Result
**Method B (standalone subtree, no clone)** — success.
Commit: `4407180c5ee891afda45cf2ba272a401f1d159d8`
URL: https://github.com/OnePlusNDev/hermes-config/commit/4407180c5ee891afda45cf2ba272a401f1d159d8

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true`) — no account switch needed
- config.yaml plaintext scan: `sk-[A-Za-z0-9]{20,}` → no match; all **15** `api_key:` entries are `''` (empty)
  → no plaintext key found, no key_env replacement needed
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **8**, New **3**, Deleted **0**; token scan **CLEAN**

## Diff (8 M, 3 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
A  demo-pm/memories/archive/MEMORY-20260911.snapshot.md
A  demo-pm/memories/archive/USER-20260911.snapshot.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-12-variable-key-baseline.md
```

## Execution notes
- First script run hit **HTTP 422 non-fast-forward** on the ref PATCH (remote HEAD advanced
  ff288da3e72e → fd86dc451618 mid-run). The documented plain re-run absorbed it —
  blob uploads are idempotent (same 11 blob SHAs both passes), re-read of remote HEAD
  re-parented the commit. Second run succeeded on first attempt.
- This is the 4th consecutive run (09-06, 09-07, 09-09, 09-11, 09-12) showing the 422,
  consistent with a concurrent sibling profile backup advancing `main` during the
  ~1–2 min blob phase. Budget exactly one re-run; no tree surgery.
- Note blobs of the two memory snapshots (MEMORY/USER-20260911.snapshot.md) are new files
  this run — they live under `memories/archive/` (intended archive content, NOT the excluded
  `memory_backup_*.json` runtime dumps) and passed the token scan CLEAN.

## Post-push remote verification
- Remote `demo-pm/config.yaml`: `sk-` matches = **0**; non-empty `api_key` = **0**
- Total blobs **629**; `demo-pm` **610**; siblings intact — demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db`, `processes.json`,
  `bin/tirith`, `home/`, `.local/`) → **NONE** (grep false positive on the doc filename
  `references/tirith-cron-workarounds.md` — documentation, not the binary)
- Temp/diagnostic script check (`pm_healthcheck`, `tmp_*.py`, `triage_*.py`,
  `cron_triage.py`, `get_token.sh`) → **NONE**
