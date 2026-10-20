# demo-pm backup run — 2026-10-20

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `54e2ead3d6c56596394f03ced5c6a003629e0d97`
URL: https://github.com/OnePlusNDev/hermes-config/commit/54e2ead3d6c56596394f03ced5c6a003629e0d97
Diff: **8 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`;
  re-checked immediately pre-run (`push=true`) and the switch **held** (no mid-run flip,
  `GITHUB_TOKEN` unset)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a doc comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (8 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against the **pre-push** remote HEAD `1373e9ff9327` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5667→5715, 119→120 ×2;
  `next_run_at` / `last_run_at` / `updated_at` rolled 10-19 → 10-20).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-19 hindsight
  reflect+consolidation row, op `75425ba3-d35c-498f-ad31-0b2ae6a900e8`; bank
  `operations_by_status.completed` 78→79).
- `demo-pm-github-api/SKILL.md` — **benign carry-over lag**: the 2026-10-19
  `403 rate-limit-exceeded ≠ bad auth` bullet written after the 10-19 follow-up push.
- `hermes-profile-backup/SKILL.md` — **benign carry-over lag**: the inline
  "run the diff probe ONCE → file → slice" rule added at the probe pointer after the
  10-19 push.
- `method-b-practice-notes.md` — **benign carry-over lag**: new "Sibling advance BETWEEN
  the main and follow-up commit is harmless" section (10-19 lesson).
- `run-note-diff-characterization.md` — **benign carry-over lag**: the 10-19 repeat-offence
  note about running the probe twice.
- `hermes-profile-diagnostics/SKILL.md` — **benign carry-over lag**: the `execute_code is
  refused in cron mode` bullet + pointer to `cleanup-run-endpoints-and-counts.md`.
- `cleanup-run-endpoints-and-counts.md` — **benign carry-over lag**: `sqlite3` one-call
  counting, ARCHIVE.md row append pattern, 2026-10-19 reflect token row
  (402,985 / 9,297) and the widened ~112 K–403 K band.
  Content inspected: no token values, no `.env` dumps.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **254**; remote HEAD `1373e9ff9327`, 273 blobs
- Preflight diff: `Modified: 8, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `1373e9ff9327` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 8 blobs uploaded, subtree `09a1a69d6bc3ea485c73c5627c54192568d30c3f`, top tree
  `3a62971987e44ec3f7dd95504b7d1a7616f2abed`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `54e2ead3d6c5`; total blobs **273**, `demo-pm` blobs = **254** (== local file
  count 254); by top dir: demo-pm 254, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `response_store.db`, `bin/tirith`, `/home/`, `/.local/`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-19` → `2026-10-20` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
