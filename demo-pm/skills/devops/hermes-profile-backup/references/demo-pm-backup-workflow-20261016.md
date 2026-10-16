# demo-pm backup run — 2026-10-16

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `2bba43566f800821c9c267b844c280207b1acf87`
URL: https://github.com/OnePlusNDev/hermes-config/commit/2bba43566f800821c9c267b844c280207b1acf87
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
```
Characterized against the **pre-push** remote HEAD `4ad2bdfe0e85` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5475→5523 and 115→116 ×2
  on the daily jobs; `next_run_at` / `last_run_at` / `updated_at` rolled 10-15 → 10-16).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-15 hindsight
  reflect+consolidation row, op `a2d3e694`; bank `operations_by_status.completed` 74→75).
- `hermes-profile-backup/templates/run-note-template.md` — **benign carry-over lag**: the
  "The Python append is now the DEFAULT for the index bullet" block plus the `patch`-vs-Python
  route reclassification, written after the 10-15 follow-up push.
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over lag**:
  the "Re-confirmed 2026-10-15 (colon + ✅ variant)" sub-bullet under the 2026-10-06 gate
  false-positive entry, written after the 10-15 follow-up push.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **248**; remote HEAD `4ad2bdfe0e85`, 267 blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `4ad2bdfe0e85` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness (`curl https://github.com` returned `000` as usual, but the `gh api`
  transport worked fine); the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `735e6829e1c48541437c9c93bcbdc9aeda60649a`, top tree
  `6267aa4b8f4348e8cef94cd8abb1ef267d07693e`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `2bba43566f80`; total blobs **267**, `demo-pm` blobs = **248** (== local file
  count 248); by top dir: demo-pm 248, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-15` → `2026-10-16` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
