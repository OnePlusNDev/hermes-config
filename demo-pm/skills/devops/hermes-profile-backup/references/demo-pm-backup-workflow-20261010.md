# demo-pm backup run — 2026-10-10

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `f6000012ab0972f32e613463d44a054862c12cfd`
URL: https://github.com/OnePlusNDev/hermes-config/commit/f6000012ab0972f32e613463d44a054862c12cfd
Diff: **3 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`
  (re-checked immediately pre-run, held, **no mid-run flip**, `GITHUB_TOKEN` unset)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; `auth.json` (164 B) /
  `auth.lock` / `state.db` (1.8 GB) exist locally but are all excluded → **not in the backed-up
  tree** (post-push-verify leak check confirms NONE)

## Diff (3 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
```
Characterized each `M` against the **pre-push** remote HEAD `ee1d16446a25` with
`scripts/characterize-diff-vs-prev-head.py ee1d16446a25`:
- `cron/jobs.json` — routine runtime churn (`completed` counters 109→110; `next_run_at` /
  `last_run_at` / `updated_at` → 2026-10-10).
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-09 Hindsight reflect +
  consolidation row).
- `hermes-profile-backup/references/method-b-practice-notes.md` — **benign carry-over lag**: the
  2026-10-09 rewrite of the ref-PATCH 422-race explanation (intermittent, "any sibling advances
  main", observed siblings demo-tester/demo-dev), a 10-09 post-push edit.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **241**; remote HEAD `ee1d16446a25`, 260 blobs
- Preflight diff: `Modified: 3, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `ee1d16446a25` at blob-phase start and **stayed there through commit time** →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 3 blobs uploaded, subtree `856f8a32170ace223faaef2c30bf5e80260e51be`, top tree
  `5df4b9aefe3d8a1fde7b4893a611c82f0a385b24`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `f6000012ab09`; total blobs **260**, `demo-pm` blobs = **241** (== local file
  count 241); by top dir: demo-pm 241, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-09` → `2026-10-10` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
