# demo-pm backup run — 2026-09-30

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts)**.
Main commit: `37c82021e9e1dc175ebd02c48423369638f1754f`
URL: https://github.com/OnePlusNDev/hermes-config/commit/37c82021e9e1dc175ebd02c48423369638f1754f
Diff: **8 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`zhangtbj`** (`push=false` on the repo) → **`gh auth switch --user OnePlusNDev`
  REQUIRED** before any blob POST; post-switch `permissions.push = true` confirmed. `GITHUB_TOKEN` unset.
  The account was re-checked immediately before the run (still `OnePlusNDev`) and the flip did **NOT**
  recur mid-run this time.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{10,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (8 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_parse.py
```
Characterized each `M` against the **pre-push** remote HEAD `6cdc630521ec` with
`scripts/characterize-diff-vs-prev-head.py` (the anchor this run = the preflight SHA, because the
script's Step-2 HEAD equalled it — `main` did not move between preflight and the blob phase):
- `cron/jobs.json` — routine cron counters/timestamps (`completed` +48/+1/+1, `next_run_at` and
  `last_run_at` advanced to 2026-09-30, `updated_at` 2026-09-30T20:00:41+08:00). Pure runtime churn.
- `memories/MEMORY.md` — the **09-29 LLM-key fix** content edit: the Hindsight LLM entry was rewritten
  from z.ai GLM to `demo-pm` daemon(:9178) `deepseek-v4-flash` @ `https://api.deepseek.com/v1`
  (key = profile `.env` `DEEPSEEK_API_KEY`, verified 200; old GLM key 401'd same day), plus the header
  date advanced 2026-09-11 → 2026-09-29. Written *after* the 09-29 follow-up push (memory maintenance
  cron ran 21:03 CST, follow-up pushed 20:05 CST) → **benign carry-over lag**, not a lost commit.
- `memories/archive/ARCHIVE.md` — routine hindsight reflect/consolidation cron row for **2026-09-29**
  (op `cc9eafb1`, bank 48 nodes / 1228 links, `>90d sessions = 481`, `auto_prune=false`); also the
  cleanup-window line (`MEMORY.md` window pushed to ~2026-10-29, `USER.md` ~2026-10-11).
- `skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md` — the **09-29**
  doc edit (the "Pick the anchor AFTER the push — a preflight SHA can be stale" section + the 09-29
  worked example). Post-09-29-push → carry-over lag.
- `skills/devops/hermes-profile-diagnostics/SKILL.md` — **09-29** doc edit: the reflect token baseline
  is now flagged MODEL-specific (glm-4-flash ~6.8–7.0K vs deepseek-v4-flash ~149K). Carry-over lag.
- `skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md` — **09-29** doc edit:
  the new "LLM Key Expired — reflect returns HTTP 401 `Authentication Failed`" section (diagnosis +
  secret-free rewrite recipe + baseline recalibration). Carry-over lag.
- `skills/devops/pm-triage-cron/scripts/pm_fetch.sh` — **09-30** (today) edit: adds a `pm_ndev_*` fetch
  (`assignee=OnePlusNDev`, the zero-task account) alongside `pm_boss_*`. Fresh edit, not lag.
- `skills/devops/pm-triage-cron/scripts/pm_parse.py` — **09-30** (today) edit: step-3 sanity check now
  prefers the **zero-task** account over `OnePlusNBoss` (Boss is structurally identical to the full set
  at steady state → no discriminating power). Fresh edit, not lag.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **231**; remote HEAD `6cdc630521ec`, **250** blobs (demo-pm **231**)
- Preflight diff: `Modified: 8, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Remote HEAD was **stable** from preflight through commit time (no sibling advance this run)

## Execution notes
- **No account flip mid-run** (pre-flight switch `zhangtbj` → `OnePlusNDev` held), **no ref-PATCH 422
  race** (remote stable at `6cdc630521ec` through commit time), no network flakiness.
- 8 blobs uploaded, subtree `52cb600c33b45bb67677ab8dbde3484067cdc26e`, top tree
  `1ad643b365c830740e4841aa8ad34cd8f2b85945`, commit + ref in **one clean pass**.
- The 09-23 `mkdtemp` private-payload-dir fix held (no shared-`/tmp` deletion).

## Post-push remote verification
- Remote HEAD `37c82021e9e1`; total blobs **250**, `demo-pm` blobs = **231** (== local file count 231);
  by top dir: demo-pm 231, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-29` → `2026-09-30`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
