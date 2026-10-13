# demo-pm backup run — 2026-10-13

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `4075d061125a6a3f1154cad667a4fc653c7492eb`
URL: https://github.com/OnePlusNDev/hermes-config/commit/4075d061125a6a3f1154cad667a4fc653c7492eb
Diff: **5 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`JungleAssistant`** (`push=false`, a known flipper since 2026-10-07)
  → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch
  **held** (no mid-run flip, `GITHUB_TOKEN` unset)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695); `password`/`secret` both empty
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (5 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-backup/scripts/characterize-diff-vs-prev-head.py
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
```
Characterized against the **pre-push** remote HEAD `68e7f0a1c6b8` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5331→5379 and 112→113;
  `next_run_at` / `last_run_at` / `updated_at` rolled 10-12 → 10-13).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-12 hindsight
  reflect+consolidation row).
- `hermes-profile-backup/references/run-note-diff-characterization.md` — **benign
  carry-over lag**: the 2026-10-12 edit expanding the `ADDED 0` section into the
  two-causes (exclude drift vs a legitimately new include-list file) explanation.
- `hermes-profile-backup/scripts/characterize-diff-vs-prev-head.py` — **benign
  carry-over lag**: the matched 2026-10-12 edit to the `ADDED` hint text.
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over
  lag**: the 2026-10-12 edit adding the "Bank↔flat-file drift — `demo-pm-memory` bank is
  a frozen 2026-06 snapshot" section.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **245**; remote HEAD `68e7f0a1c6b8`, 264 blobs
- Preflight diff: `Modified: 5, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `68e7f0a1c6b8` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 5 blobs uploaded, subtree `f208acfb11402f1c44714bb30b161fbd0585b64a`, top tree
  `f9e3947c047faa7c42a26049367c936ac4726325`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `4075d061125a`; total blobs **264**, `demo-pm` blobs = **245** (== local file
  count 245); by top dir: demo-pm 245, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-12` → `2026-10-13` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
