# demo-pm backup run — 2026-10-18

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `f1062dbc9afe13581a615e6b33637b7c005c7cb2`
URL: https://github.com/OnePlusNDev/hermes-config/commit/f1062dbc9afe13581a615e6b33637b7c005c7cb2
Diff: **5 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (5 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
```
Characterized against the **pre-push** remote HEAD `853a428e3f37` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5571→5619 and 117→118 ×2;
  `next_run_at` / `last_run_at` / `updated_at` rolled 10-17 → 10-18).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-17 hindsight
  reflect+consolidation row, op `9860db7d`; bank `operations_by_status.completed` 76→77).
- `run-note-diff-characterization.md` — **benign carry-over lag**: the new category-3
  block ("A new doc authored by ANOTHER cron job between runs"), written after the
  10-17 follow-up push.
- `hermes-profile-diagnostics/SKILL.md` — **benign carry-over lag**: the "never launch the
  daemon script with `nohup … &` inside `terminal()`" bullet (verified 2026-10-17).
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over
  lag**: the 2026-10-17 recommendation-section gate variant + the "gate/token header lines
  live at the TOP and get cut off in a tail view" note.

All three doc edits were authored after the 10-17 follow-up push (ordering, not a lost
commit). Content inspected: no token values, no `.env` dumps.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **251**; remote HEAD `853a428e3f37`, 270 blobs
- Preflight diff: `Modified: 5, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `853a428e3f37` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 5 blobs uploaded, subtree `df73ab228d60fd5f105f9ed5b5497fb231da5f4f`, top tree
  `2d9a14001d15622b828ab6b4b63c9f5098efc320`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `f1062dbc9afe`; total blobs **270**, `demo-pm` blobs = **251** (== local file
  count 251); by top dir: demo-pm 251, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `response_store.db`, `bin/tirith`, `/home/`, `/.local/`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-17` → `2026-10-18` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
