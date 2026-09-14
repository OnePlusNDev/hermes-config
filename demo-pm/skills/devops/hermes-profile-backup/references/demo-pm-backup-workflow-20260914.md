# demo-pm backup run — 2026-09-14

## Result
**Method B (standalone subtree, no clone)** — success.
Main commit: `674df1f2eab6aaddd884c7d2df67397756876e7a` (second attempt — first ref PATCH hit HTTP 422)
URL: https://github.com/OnePlusNDev/hermes-config/commit/674df1f2eab6aaddd884c7d2df67397756876e7a

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**) — no account switch needed
- No `GITHUB_TOKEN` / `GH_TOKEN` in the cron env (`env | grep ^GH` = 0) → no auth-override risk
- config.yaml plaintext scan: `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  all **15** `api_key:` lines are `''` (empty; `grep -cE "api_key: ''"` = 15, non-empty = 0)
  → **no plaintext key found, no key_env replacement needed**
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **6**, New **1**, Deleted **0**; token scan **CLEAN**
- `.env` (GITHUB_USERNAME/EMAIL/TOKEN, GATEWAY_PORT, AGENT_NAME/ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV)
  excluded, never uploaded; no `auth.json`/`auth.lock`/`state.db*` in tree

## Diff (6 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/references/2026-09-12-variable-key-baseline.md
M  demo-pm/skills/devops/pm-triage-cron/references/2026-09-13-silent-noop-sibling-tmp-collision.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-14-session-clean-noop-and-skill-size-cap.md
```

## Execution notes
- Remote HEAD was `3cd29d91e1ec` at start. First run uploaded all 7 blobs, built subtree
  `72c4c429269545b57ae82b544fb623fd6b9b7759`, top tree `e76ab930974e` and commit `1583aadf5ae5`,
  then Step 7 ref PATCH failed: `Update is not a fast forward (HTTP 422)` — remote had advanced
  to `78f16d84a359` during the ~1–2 min blob phase (concurrent sibling-profile backup).
- Budgeted ONE plain re-run per the documented rule: blob SHAs are idempotent, so the re-run
  re-uploaded the same 7 blobs and re-parented the identical content on the fresh HEAD
  → subtree `72c4c429269545b57ae82b544fb623fd6b9b7759` (same), top tree `ae01ce23ea5f`,
  commit `674df1f2eab6` — ref PATCH succeeded, `Remote HEAD now: 674df1f2eab6`.
- No tree surgery, no rebase, no manual re-parent. The 422 is the documented 09-06→09-12
  pattern (09-13 was the exception with a first-try success); it is NOT a partial failure.
- No exclude gaps found this run; no `EXCLUDE_*` / rsync / gitignore changes required.

## Post-push remote verification
- Remote `demo-pm/config.yaml`: **17021** bytes; `sk-` matches = **0**; `api_key` lines = 15,
  non-empty = **0**
- Total blobs **633**; `demo-pm` blobs = **614** (== local file count 614); entries by top dir:
  demo-pm 794, demo-tester 11, demo-dev 7, tester-01 6, .gitignore 1
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `home/`, `.local/`, `response_store.db`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`) → **NONE**
- Remote HEAD after push: `674df1f2eab6aaddd884c7d2df67397756876e7a` (verified)
