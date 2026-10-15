# demo-pm backup run — 2026-10-15

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `7fc91dd67f9c5b93a795090254ff7611c19ada3c`
URL: https://github.com/OnePlusNDev/hermes-config/commit/7fc91dd67f9c5b93a795090254ff7611c19ada3c
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`;
  re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset)
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
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
```
Characterized against the **pre-push** remote HEAD `70e3c15e297c` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5427→5475 and 114→115 ×2
  on the daily jobs; `next_run_at` / `last_run_at` / `updated_at` rolled 10-14 → 10-15).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-14 hindsight
  reflect+consolidation row, op `cfe5c351`; bank `operations_by_status.completed` 73→74).
- `hermes-profile-backup/SKILL.md` — **benign carry-over lag**: the "Load THIS skill FIRST …
  DECOY" callout block at the top of the file, written after the 10-14 follow-up push.
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over lag**:
  the "Re-confirmed 2026-10-14 (variant heading)" sub-bullet under the 2026-10-06 gate
  false-positive entry, written after the 10-14 follow-up push.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **247**; remote HEAD `70e3c15e297c`, 266 blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `70e3c15e297c` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness (`curl https://github.com` returned `000` as usual, but the `gh api`
  transport worked fine); the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `3b9993fe0d9e4658c572411c2ca02f3ec17927fb`, top tree
  `d2c74ac00e695435c4fe182b5d4fb81b339f7d92`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `7fc91dd67f9c`; total blobs **266**, `demo-pm` blobs = **247** (== local file
  count 247); by top dir: demo-pm 247, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-14` → `2026-10-15` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
