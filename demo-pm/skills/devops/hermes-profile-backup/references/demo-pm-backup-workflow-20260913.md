# demo-pm backup run — 2026-09-13

## Result
**Method B (standalone subtree, no clone)** — success, first attempt (no 422).
Commit: `67d204819bc34e738d6b60f33a4633d58aef144b`
URL: https://github.com/OnePlusNDev/hermes-config/commit/67d204819bc34e738d6b60f33a4633d58aef144b

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**, `admin` = true) — no account switch needed
- No `GITHUB_TOKEN` / `GH_TOKEN` in the cron env → no override risk
- config.yaml plaintext scan: `sk-[A-Za-z0-9]{20,}` → **0** matches; all **15** `api_key:` entries are `''` (empty)
  → **no plaintext key found, no key_env replacement needed**
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **6**, New **1**, Deleted **0**; token scan **CLEAN**
- `.env` holds GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME, AGENT_ROLE,
  DEEPSEEK_API_KEY, TERMINAL_ENV — excluded, never uploaded

## Diff (6 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/hindsight-daemon-recovery/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-13-silent-noop-sibling-tmp-collision.md
```

## Execution notes
- Remote HEAD was `a71121b57290` at start; ref PATCH succeeded on the **first** run — remote HEAD
  was stable through the blob phase this time (breaks a 09-06→09-12 streak of HTTP 422
  non-fast-forward races from a concurrent sibling-profile backup). No re-run needed.
- 7 blobs uploaded, all idempotent SHAs; `demo-pm` subtree `a2a9eec0`, top tree `da46ecf5`.
- Local SKILL.md/edit churn noted at diff time was unrelated to this run's script (no exclude
  gaps found this run; no EXCLUDE_* changes required).

## Post-push remote verification
- Remote `demo-pm/config.yaml`: 17021 bytes, `sk-` matches = **0**; `api_key` lines = 15, all empty (**0** non-empty)
- Total blobs **631**; `demo-pm` **612**; siblings intact — demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `home/`, `.local/`, `response_store.db`) → **NONE**
- Temp/diagnostic script check (`pm_health*`, `tmp_*`, `triage_*`, `cron_triage`, `get_token`) → **NONE**
- Remote HEAD after push: `67d204819bc34e738d6b60f33a4633d58aef144b` (verified)
