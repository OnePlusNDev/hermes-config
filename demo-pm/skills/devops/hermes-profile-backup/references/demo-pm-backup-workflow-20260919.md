# demo-pm backup run — 2026-09-19

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY, no aborted attempts.
Main commit: `4b85dff48c20e3f36f4e3cb77a8d237325ce34a2`
URL: https://github.com/OnePlusNDev/hermes-config/commit/4b85dff48c20e3f36f4e3cb77a8d237325ce34a2
Diff: **4 M, 2 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**, `admin` = true) — no switch needed
- `env | grep -E '^(GH|GITHUB)'` → only `GITHUB_EMAIL`, `GITHUB_USERNAME`
  → **no `GITHUB_TOKEN` / `GH_TOKEN`** in the cron env, so no auth-override risk
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  all **15** `api_key:` lines are `''`; the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_*, DEEPSEEK_API_KEY) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
A  demo-pm/skills/devops/hermes-profile-backup/references/curator-archive-churn-triage.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-19-filter-sanity-crosscheck.md
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one.
Both new files are session-reference docs written under their skills' `references/` dirs,
so they are legitimately inside the backup set (not caught by any root-level diagnostic exclude).

## Preflight
- Local files (after excludes): **399**; remote HEAD `e18164653ec6`, 416 blobs
- First preflight run: `Modified: 4, New: 2, Deleted: 0` — **no new exclude gaps** (the
  curator-archive churn from the 09-18 run has settled; `.archive` / `.curator_suppressed`
  stay excluded as designed)
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `e18164653ec6` at start and **stayed there through commit time** → **no ref-PATCH
  422 race**; the ref PATCH succeeded on the first attempt (fourth such run, after 09-13 / 09-16 / 09-17 / 09-18).
- **No network flakiness** — 6 blobs uploaded, subtree `513e1a519cd666ed2bd231e663c6f5b86bb4ac00`,
  top tree `9033526cc0a238135492631d042b572f0b4c191a`, commit + ref in one clean pass.
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Post-push remote verification
- Remote HEAD `4b85dff48c20`; total blobs **418**, `demo-pm` blobs = **399** (== local file count 399);
  by top dir: demo-pm 399, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (`16835` chars vs `17021` bytes — the usual CJK-comment discrepancy)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `skills/.archive/` and `skills/.curator_suppressed` → **absent** from the remote tree (excluded as designed)

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-18` → `2026-09-19`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
