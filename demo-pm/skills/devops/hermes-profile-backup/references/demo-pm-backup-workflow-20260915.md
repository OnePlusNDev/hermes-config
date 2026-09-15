# demo-pm backup run — 2026-09-15

## Result
**Method B (standalone subtree, no clone)** — success.
Main commit: `3704ae6fc209a5d008dc6370899ca0742ec255a3` (second attempt — first ref PATCH hit HTTP 422)
URL: https://github.com/OnePlusNDev/hermes-config/commit/3704ae6fc209a5d008dc6370899ca0742ec255a3

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**, `admin` = true) — no account switch needed
- No `GITHUB_TOKEN` / `GH_TOKEN` in the cron env (`env | grep -E '^(GH|GITHUB)'` → only `GITHUB_EMAIL`, `GITHUB_USERNAME`)
  → no auth-override risk
- config.yaml plaintext scan: `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  all **15** `api_key:` lines are `''` (empty; non-empty count = 0)
  → **no plaintext key found, no key_env replacement needed**
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **7**, New **3**, Deleted **0**; token scan **CLEAN**
- `.env` (GITHUB_USERNAME/EMAIL/TOKEN, GATEWAY_PORT, AGENT_NAME/ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV)
  excluded, never uploaded; no `auth.json`/`auth.lock`/`state.db*` in tree

## Diff (7 M, 3 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
A  demo-pm/skills/devops/hermes-profile-diagnostics/scripts/reflect_quality_check.py
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-14-cron-empty-assignee-and-mass-deletion-guard.md
A  demo-pm/skills/devops/pm-triage-cron/references/sibling-collision-and-empty-result.md
```
(The two new `pm-triage-cron/references/*.md` files and
`hermes-profile-diagnostics/scripts/reflect_quality_check.py` are new session docs/scripts
written since the 09-14 backup.)

## Execution notes
- Remote HEAD was `4b071bfa6ca0` at start. First run uploaded all 10 blobs, built subtree
  `2c7c3a7448d482d4b3c6d201ca06baff0f68fb5b`, top tree `15d304afd879` and commit `5b878cd883ad`,
  then Step 7 ref PATCH failed: `Update is not a fast forward (HTTP 422)` — remote had advanced
  to `be591abd16d8` during the ~1–2 min blob phase (concurrent sibling-profile backup).
- Budgeted ONE plain re-run per the documented rule: blob SHAs are idempotent, so the re-run
  re-uploaded the same 10 blobs and re-parented the identical content on the fresh HEAD
  → subtree `2c7c3a7448d482d4b3c6d201ca06baff0f68fb5b` (same), top tree `6f3d25fba161`,
  commit `3704ae6fc209` — ref PATCH succeeded, `Remote HEAD now: 3704ae6fc209`.
- No tree surgery, no rebase, no manual re-parent. This is the documented 09-06→09-12 /
  09-14 pattern (09-13 was the exception with a first-try success), NOT a partial failure.
- No exclude gaps found this run; no `EXCLUDE_*` / rsync / gitignore changes required.

## Post-push remote verification
- Remote `demo-pm/config.yaml`: **16835** bytes; `sk-` matches = **0**; `api_key` lines = 15,
  non-empty = **0**
- Total blobs **637**; `demo-pm` blobs = **618** (== local file count 618); entries by top dir:
  demo-pm 618, demo-tester 8, demo-dev 5, tester-01 5, .gitignore 1
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `home/`, `.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- Remote HEAD after push: `3704ae6fc209a5d008dc6370899ca0742ec255a3` (verified)
