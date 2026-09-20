# demo-pm backup run — 2026-09-20

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY, no aborted attempts.
Main commit: `cf2cef128553b224a0a439bf529f469366cd4edb`
URL: https://github.com/OnePlusNDev/hermes-config/commit/cf2cef128553b224a0a439bf529f469366cd4edb
Diff: **6 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner) — no switch needed
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  all **15** `api_key:` lines are `''`; the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_*, DEEPSEEK_API_KEY) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
A  demo-pm/skills/devops/hermes-profile-backup/references/plaintext-key-scan-notes.md
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one.
The new file is a session-reference doc written under its skill's `references/` dir,
so it is legitimately inside the backup set (not caught by any root-level diagnostic exclude).

## Preflight
- Local files (after excludes): **401**; remote HEAD `4aaad6fc05a2`, 419 blobs
- First preflight run: `Modified: 6, New: 1, Deleted: 0` — **no new exclude gaps**
  (the 09-18 curator-archive churn stays settled; `.archive` / `.curator_suppressed`
  remain excluded as designed)
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `4aaad6fc05a2` at start and **stayed there through commit time** → **no ref-PATCH
  422 race**; the ref PATCH succeeded on the first attempt (fifth such run, after 09-13 / 09-16 /
  09-17 / 09-18 / 09-19).
- **No network flakiness** — 7 blobs uploaded, subtree `a5d7b6a84b47698e664523d7b4035e31136d570e`,
  top tree `23da57e15d2211bf12c386d8cb5a73bd4a040417`, commit + ref in one clean pass.
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Post-push remote verification
- Remote HEAD `cf2cef128553`; total blobs **420**, `demo-pm` blobs = **401** (== local file count 401);
  by top dir: demo-pm 401, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (`16835` chars vs `17021` bytes — the usual CJK-comment discrepancy)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `skills/.archive/` and `skills/.curator_suppressed` → **absent** from the remote tree (excluded as designed)

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-19` → `2026-09-20`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
