# demo-pm backup run — 2026-10-17

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `3a5650ac379ae8f1f5122f4459130aa877fe3ebc`
URL: https://github.com/OnePlusNDev/hermes-config/commit/3a5650ac379ae8f1f5122f4459130aa877fe3ebc
Diff: **3 M, 1 A, 0 D**.

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

## Diff (3 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
A  demo-pm/skills/devops/pm-triage-cron/references/cron-run-pitfalls.md
```
Characterized against the **pre-push** remote HEAD `7ef238af2599` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counter 115→116 / 116→117 on the two
  daily jobs; `next_run_at` / `last_run_at` / `updated_at` rolled 10-16 → 10-17).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-16 hindsight
  reflect+consolidation row, op `8051e535`; bank `operations_by_status.completed` 75→76).
- `hermes-profile-backup/templates/run-note-template.md` — **benign carry-over lag**: the
  "Use a UNIQUE helper filename — never the generic `/tmp/append_index.py`" block, written
  after the 10-16 follow-up push.
- `pm-triage-cron/references/cron-run-pitfalls.md` — **new reference doc** (2,369 B) recording
  the `/tmp` fixed-filename sibling-subagent collision pitfall and the verified `COUNT:0`
  crosscheck recipe. Content inspected: no token, no `.env` value (names only).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **250**; remote HEAD `7ef238af2599`, 268 blobs
- Preflight diff: `Modified: 3, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `7ef238af2599` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness (`curl https://github.com` returns `000` as usual, but the `gh api`
  transport worked fine); the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `f2f99cf1202d14fd7090d94328b63b0a191042ba`, top tree
  `17be3a117898656c3992a2543df39cac1ecf579d`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `3a5650ac379a`; total blobs **269**, `demo-pm` blobs = **250** (== local file
  count 250); by top dir: demo-pm 250, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `response_store.db`, `bin/tirith`, `/home/`, `/.local/`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-16` → `2026-10-17` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
