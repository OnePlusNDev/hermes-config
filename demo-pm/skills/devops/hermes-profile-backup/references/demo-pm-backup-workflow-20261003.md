# demo-pm backup run — 2026-10-03

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts)**.
Main commit: `c61866ac8a22b12d6dddd7d19681336365c4d846`
URL: https://github.com/OnePlusNDev/hermes-config/commit/c61866ac8a22b12d6dddd7d19681336365c4d846
Diff: **7 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner, `push=true`) — **no switch needed**;
  `GITHUB_TOKEN` unset. Active account re-checked immediately before the blob phase, held.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{16,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a
  comment (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (7 M, 1 A, 0 D)
```
M  demo-pm/channel_directory.json
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/scripts/characterize-diff-vs-prev-head.py
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/scripts/reflect_quality_check.py
A  demo-pm/skills/productivity/ocr-and-documents/DESCRIPTION.md
```
Characterized each `M` against the **pre-push** remote HEAD `5b541e866d54` with
`scripts/characterize-diff-vs-prev-head.py 5b541e866d54`:
- `channel_directory.json` — routine runtime churn (`updated_at` 2026-09-11 → 2026-10-03).
- `cron/jobs.json` — routine cron counters/timestamps (`completed` 4857→4880, 101→102, 101→103;
  `next_run_at`/`last_run_at`/`updated_at` advanced to 2026-10-03). Pure runtime churn.
- `memories/archive/ARCHIVE.md` — routine hindsight reflect + consolidation cron rows for
  **2026-10-01** (op `ef1219f5-5827-456a-b702-57e58f7864ea`) and **2026-10-03**
  (op `b57d217c-8de2-4872-98a2-82a079596660`), both `deduplicated=false`, 1-poll completed.
  Runtime churn.
- `scripts/characterize-diff-vs-prev-head.py` — the **2026-10-01** doc edit adding the
  "Timing is NOT load-bearing" section. Written *after* the 10-01 follow-up push →
  **benign carry-over lag**, not a lost commit.
- `hermes-profile-diagnostics/SKILL.md` — **carry-over lag**: reflect two-gate rewording
  (10-01) + the 2026-10-03 cold-start recalibration (~20s full cold start, 1-3+ min is an
  upper bound).
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **carry-over lag**: the
  broadened deepseek band (~112K–273K, 10-01), the new "creation-age false positive can hide
  INSIDE a full itemized analysis" section, the facts-included payload recipe, and the
  2026-10-03 cold-start recalibration.
- `hermes-profile-diagnostics/scripts/reflect_quality_check.py` — **carry-over lag**: the
  two-gate probe (`--baseline 50000` for deepseek, wording gate + forced-distinction
  DISAMBIG) added 10-01.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **234**; remote HEAD `5b541e866d54`, **252** blobs
- Preflight diff: `Modified: 7, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `5b541e866d54` at blob-phase start and **stayed there through commit time**
  → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness, no mid-run account flip; the `mkdtemp` private-payload-dir fix held.
- 8 blobs uploaded, subtree `874cf6a84a11a860694b807a45ab9af83abab144`, top tree
  `102a5bd05ee7ec65d1e03d1f6905a0f3c5f225ef`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `c61866ac8a22`; total blobs **253**, `demo-pm` blobs = **234** (== local file
  count 234); by top dir: demo-pm 234, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-01` → `2026-10-03` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
