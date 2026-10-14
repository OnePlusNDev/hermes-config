# demo-pm backup run — 2026-10-14

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `2b1846aa3131ab51e5732a03446b263e5cad57e7`
URL: https://github.com/OnePlusNDev/hermes-config/commit/2b1846aa3131ab51e5732a03446b263e5cad57e7
Diff: **3 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`zhangtbj`** (`push=false`, a known flipper since 2026-09-26)
  → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch
  **held** (no mid-run flip, `GITHUB_TOKEN` unset)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (3 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
```
Characterized against the **pre-push** remote HEAD `aa1e15833e0e` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5379→5427 and 113→114
  on the two daily jobs; `next_run_at` / `last_run_at` / `updated_at` rolled 10-13 → 10-14).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-13 hindsight
  reflect+consolidation row).
- `hermes-profile-backup/templates/run-note-template.md` — **benign carry-over lag**:
  the 2026-10-13 edit adding the "Fallback: Python append when the last bullet is too
  long to transcribe" section.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **246**; remote HEAD `aa1e15833e0e`, 265 blobs
- Preflight diff: `Modified: 3, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `aa1e15833e0e` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 3 blobs uploaded, subtree `68fa7c6fbd9946cc7b8329f3134e36b50f779ade`, top tree
  `aef6413691735db8508be3b7d47d00c0ddc1eaed`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `2b1846aa3131`; total blobs **265**, `demo-pm` blobs = **246** (== local file
  count 246); by top dir: demo-pm 246, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-13` → `2026-10-14` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
