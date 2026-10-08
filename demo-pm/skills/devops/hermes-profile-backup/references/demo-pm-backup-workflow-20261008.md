# demo-pm backup run — 2026-10-08

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `73b97f8daeb0a384447f264b5aa6f702913af73b`
URL: https://github.com/OnePlusNDev/hermes-config/commit/73b97f8daeb0a384447f264b5aa6f702913af73b
Diff: **3 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`zhangtbj`** (`push=false`, a known flipper) → `gh auth switch --user OnePlusNDev`
  (re-checked immediately pre-run → owner, `GITHUB_TOKEN` unset); no mid-run flip.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
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
Characterized each `M` against the **pre-push** remote HEAD `292113d1acc2` with
`scripts/characterize-diff-vs-prev-head.py 292113d1acc2`:
- `cron/jobs.json` — routine runtime churn (`completed` counters 5091→5139 and 107→108;
  `next_run_at` / `last_run_at` / `updated_at` → 2026-10-08).
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-07 Hindsight reflect +
  consolidation row, op `556c6e21`).
- `hermes-profile-backup/references/method-b-practice-notes.md` — **benign carry-over lag**: the
  new "Known gh keyring accounts — the flipper set is OPEN" section (six keyring accounts; the
  flipper set is open-ended), a 10-07 post-push edit.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **239**; remote HEAD `292113d1acc2`, 258 blobs
- Preflight diff: `Modified: 3, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `292113d1acc2` at the script's Step 2 and **stayed there through commit time**
  → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness, no account flip; the `mkdtemp` private-payload-dir fix held.
- 3 blobs uploaded, subtree `8f40df208898fa6582d20f886018cad7b72127ba`, top tree
  `559f668c43526022a36719e7a8078329b85b02ef`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `73b97f8daeb0`; total blobs **258**, `demo-pm` blobs = **239** (== local file
  count 239); by top dir: demo-pm 239, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-07` → `2026-10-08` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
