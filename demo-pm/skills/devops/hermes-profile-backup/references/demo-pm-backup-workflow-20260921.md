# demo-pm backup run — 2026-09-21

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY, no aborted attempts.
Main commit: `d005c7a2b323eaeea276ed1fd34fe0f1b2dc5ffe`
URL: https://github.com/OnePlusNDev/hermes-config/commit/d005c7a2b323eaeea276ed1fd34fe0f1b2dc5ffe
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner) — no switch needed
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_*, DEEPSEEK_API_KEY) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_parse.py
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **402**; remote HEAD `c82057b2f14b` (advanced from the
  09-20 run's `cf2cef128553` by concurrent sibling-profile backups), 421 blobs
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
  (the 09-18 curator-archive churn stays settled; `.archive` / `.curator_suppressed`
  remain excluded as designed)
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `07eea1c358f6` at blob-phase start (it had moved again between the
  preflight and the backup script) and **stayed there through commit time** → **no
  ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- **No network flakiness** — 6 blobs uploaded, subtree `17fbed6d3d05`,
  top tree `c14c71ded0d2`, commit + ref in one clean pass.
- Trees are built hierarchically so every POST stays small (no flat-tree 422).

## Post-push remote verification
- Remote HEAD `d005c7a2b323`; total blobs **421**, `demo-pm` blobs = **402** (== local file count 402);
  by top dir: demo-pm 402, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `skills/.archive/` and `skills/.curator_suppressed` → **absent** from the remote tree (excluded as designed)
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-20` → `2026-09-21`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
