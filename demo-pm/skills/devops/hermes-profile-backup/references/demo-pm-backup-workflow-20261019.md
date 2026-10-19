# demo-pm backup run — 2026-10-19

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `8f60c15fd3bd6c08e02cd9b5439cfc7e9bc7b410`
URL: https://github.com/OnePlusNDev/hermes-config/commit/8f60c15fd3bd6c08e02cd9b5439cfc7e9bc7b410
Diff: **4 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`;
  re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  `token|secret|password|bearer:` long-value scan → **no matches**
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B) excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
A  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against the **pre-push** remote HEAD `d1454b937e52` (preflight and the
script's Step 2 agreed — no anchor divergence):
- `cron/jobs.json` — routine runtime churn (completed counters 5619→5667 and 118→119 ×2;
  `next_run_at` / `last_run_at` / `updated_at` rolled 10-18 → 10-19).
- `memories/archive/ARCHIVE.md` — routine runtime churn (one new 2026-10-18 hindsight
  reflect+consolidation row, op `e86783d6-ba56-433b-9ac6-c76328dbac13`; bank
  `operations_by_status.completed` 77→78).
- `run-note-diff-characterization.md` — **benign carry-over lag**: the "Run it ONCE — write
  the diff to a file, then slice it" section, written after the 10-18 follow-up push.
- `hermes-profile-diagnostics/SKILL.md` — **benign carry-over lag**: the pointer to
  `references/cleanup-run-endpoints-and-counts.md` (added after the 10-18 push, now
  required because `memory-maintenance.md` is at the 100 K char cap).
- `cleanup-run-endpoints-and-counts.md` — **legitimately NEW include-list doc** (not
  EXCLUDE drift): consolidate/operation-status URLs, bank-list pre-flight, epoch-float
  `started_at` retention counting, `process(log)` offset quirk, deepseek reflect token band.
  Content inspected: no token values, no `.env` dumps.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **253**; remote HEAD `d1454b937e52`, 271 blobs
- Preflight diff: `Modified: 4, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `d1454b937e52` at blob-phase start (Step 2) and **stayed there through
  commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 5 blobs uploaded, subtree `ca3c3ccb91007aa26549cf1b5f4f2b93ff9203fc`, top tree
  `da91d032ea8e925c5771dd5a84305b1cc47c96fa`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `8f60c15fd3bd`; total blobs **272**, `demo-pm` blobs = **253** (== local file
  count 253); by top dir: demo-pm 253, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `response_store.db`, `bin/tirith`, `/home/`, `/.local/`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-18` → `2026-10-19` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
