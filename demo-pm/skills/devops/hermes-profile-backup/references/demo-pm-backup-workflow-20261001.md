# demo-pm backup run — 2026-10-01

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts)**.
Main commit: `5480e52cad4271c09271aab071ec0ca6a5c48e8d`
URL: https://github.com/OnePlusNDev/hermes-config/commit/5480e52cad4271c09271aab071ec0ca6a5c48e8d
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false` on the repo) → **`gh auth switch --user OnePlusNDev`
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

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
```
Characterized each `M` against the **pre-push** remote HEAD `1fcd2063e654` with
`scripts/characterize-diff-vs-prev-head.py` (the anchor this run = the preflight SHA, because the
script's Step-2 HEAD equalled it — `main` did not move between preflight and the blob phase):
- `cron/jobs.json` — routine cron counters/timestamps (`completed` 4809→4857, 100→101 x2,
  `next_run_at`/`last_run_at` advanced to 2026-10-01, `updated_at` 2026-10-01T20:01:13+08:00).
  Pure runtime churn.
- `memories/archive/ARCHIVE.md` — routine hindsight reflect + consolidation cron row for **2026-09-30**
  (op `665b8182-9318-4475-a4e5-bd8bb7265327`, bank 48 nodes / 1228 links, `>90d sessions = 533`,
  `auto_prune=false`); reflect returned a real itemized analysis (112,767 in / 4,814 out tokens,
  ~25s). Runtime churn.
- `skills/devops/hermes-profile-backup/references/method-b-practice-notes.md` — the **09-30** doc edit:
  the "Observed on recent runs" table rows for 09-29 + 09-30 and the "maintain this table with one row
  per run" note. Written *after* the 09-30 follow-up push → **benign carry-over lag**, not a lost commit.
- `skills/devops/hermes-profile-backup/templates/run-note-template.md` — **09-30** edit: the follow-up
  section now names the method-b-practice-notes table row as part of the follow-up, and the `.env`
  line instructs listing **var names only**. Carry-over lag.
- `skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md` — **09-30** edit: the
  deepseek-v4-flash reflect baseline is reframed as an order-of-magnitude band (~100K–150K), re-verified
  at 112,767 input tokens. Carry-over lag.
- `skills/devops/pm-triage-cron/SKILL.md` — **09-30** edit: added the tirith `rm -f /tmp/pm_*.json`
  mass-file-deletion lesson to the 禁用清单. Carry-over lag.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **232**; remote HEAD `1fcd2063e654`, **251** blobs (demo-pm **232**)
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Remote HEAD was **stable** from preflight through commit time (no sibling advance this run)

## Execution notes
- **No account flip mid-run** (pre-flight switch `OnePlusNTester` → `OnePlusNDev` held), **no ref-PATCH
  422 race** (remote stable at `1fcd2063e654` through commit time), no network flakiness.
- 6 blobs uploaded, subtree `06db308902a5243ec4900e321f6868ecd4525186`, top tree
  `fac92ca2ab39c6535f6ec3f44058a0beda80b6f8`, commit + ref in **one clean pass**.
- The 09-23 `mkdtemp` private-payload-dir fix held (no shared-`/tmp` deletion).

## Post-push remote verification
- Remote HEAD `5480e52cad42`; total blobs **251**, `demo-pm` blobs = **232** (== local file count 232);
  by top dir: demo-pm 232, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-30` → `2026-10-01` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
