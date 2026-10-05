# demo-pm backup run — 2026-10-05

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts)**.
Main commit: `7b1e74df16e59e84acf139513497ec525b03ae29`
URL: https://github.com/OnePlusNDev/hermes-config/commit/7b1e74df16e59e84acf139513497ec525b03ae29
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, `push=true`) — **no switch needed**
  (`GITHUB_TOKEN` unset), no mid-run flip
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hindsight-daemon-recovery/SKILL.md
```
Characterized each `M` against the **pre-push** remote HEAD `b59147ff4803` with
`scripts/characterize-diff-vs-prev-head.py b59147ff4803`:
- `cron/jobs.json` — routine runtime churn (`completed` 104→105; `next_run_at` /
  `last_run_at` / `updated_at` advanced to 2026-10-05). Pure runtime churn.
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-04 Hindsight reflect +
  consolidation row; 记忆清理时间 2026-09-27 → 2026-10-04).
- `hermes-profile-backup/references/skill-md-at-cap.md` — **benign carry-over lag**: the
  "do NOT locate the path with a recursive `find` — it TIMES OUT (180 s, exit 124)" lesson
  (verified 2026-10-04), written after the 10-04 follow-up push → ordering, not a lost commit.
- `hindsight-daemon-recovery/SKILL.md` — **benign carry-over lag**: the new
  "boot-storm / cold-start can take ~7 min — do NOT kill prematurely" + "concurrent cron storm
  creates phantom no-listener readings" lessons (verified 2026-10-04), also written after the
  10-04 follow-up push.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **235**; remote HEAD `b59147ff4803`, **254** blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `b59147ff4803` at blob-phase start and **stayed there through commit time** →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness, no mid-run account flip; the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `406e5ac8db0237de95a8395b170f8e97c80d66df`, top tree
  `919563bb1650117b7e54aa6e96d202c0d164c332`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `7b1e74df16e5`; total blobs **254**, `demo-pm` blobs = **235** (== local file
  count 235); by top dir: demo-pm 235, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-04` → `2026-10-05` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
