# demo-pm backup run — 2026-09-17

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY, no aborted attempts.
Main commit: `1b9613870ffdd699bdb9245a93f836318af7ed0b`
URL: https://github.com/OnePlusNDev/hermes-config/commit/1b9613870ffdd699bdb9245a93f836318af7ed0b

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**, `admin` = true) — no switch needed
- `env | grep -E '^(GH|GITHUB)'` → only `GITHUB_EMAIL`, `GITHUB_USERNAME`
  → **no `GITHUB_TOKEN` / `GH_TOKEN`** in the cron env, so no auth-override risk
- config.yaml plaintext scan: `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  `(api_key|token|secret|password): '<6+ chars>'` → **NONE**; all **15** `api_key:` lines are `''`
  → **no plaintext key found, no key_env replacement needed**
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **6**, New **5**, Deleted **0**;
  token scan **CLEAN** → no exclude gaps, no `EXCLUDE_*` / rsync / gitignore changes needed
- `.env` (296 B; GITHUB_*, DEEPSEEK_API_KEY) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 5 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
A  demo-pm/skills/devops/hermes-profile-backup/references/network-flakiness-and-verify-tooling.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-16-baseline-noop.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-17-empty-assignee-and-script-packaging.md
A  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
A  demo-pm/skills/devops/pm-triage-cron/scripts/pm_parse.py
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one, so
there was nothing to re-upload. The 09-16 follow-up had already swept in the current config.

## Execution notes
- Remote HEAD was `7a2b4e395427` at start and **stayed there through commit time** → **no ref-PATCH 422
  race this run**; the ref PATCH succeeded on the first attempt (second such run in the 09-13 / 09-16
  / 09-17 set).
- **No network flakiness this run** — contrast with 09-16, which needed 3 attempts after two
  `dial tcp 20.205.243.168:443: i/o timeout` aborts. All 11 blobs uploaded and the commit pushed
  in a single clean run; `Done:` + exit 0 on attempt 1.
- `scripts/post-push-verify.py` ran green on the first execution — the 09-16 `jq=".content"` fix
  held (no repeat of the `config.yaml decodes: Incorrect padding` false FAIL).
- The 5 new files include the two `pm-triage-cron/scripts/` helpers (`pm_fetch.sh`, `pm_parse.py`)
  added by the PM triage cron — these live under the skill dir (not root), so they are NOT caught by
  the `get_token.sh` / `pm_health*` / `healthcheck_*` root-level diagnostics excludes and are
  correctly backed up. Their pre-upload token scan came back CLEAN.

## Post-push remote verification
- `scripts/post-push-verify.py` → **ALL CHECKS PASS**; remote HEAD `1b9613870ffd`
- Total blobs **646**; `demo-pm` blobs = **627** (== local file count 627); by top dir:
  demo-pm 627, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (script-reported `16835` is the **character** count — the file holds CJK comments; true byte
  length is **17021**, confirmed via `wc -c`)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-16` → `2026-09-17`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
