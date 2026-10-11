# demo-pm backup run — 2026-10-11

## Result
**Method B (standalone subtree, no clone)** — **1 aborted attempt (ref-PATCH 422 race)**, absorbed by the budgeted single plain re-run.
Main commit: `28a371e0e4ded350d39dff9b985fb3710de51b7d`
URL: https://github.com/OnePlusNDev/hermes-config/commit/28a371e0e4ded350d39dff9b985fb3710de51b7d
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`
  (re-checked immediately pre-run, held, **no mid-run flip**, `GITHUB_TOKEN` unset)
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
M  demo-pm/skills/devops/hermes-profile-backup/references/tirith-cron-workarounds.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
```
Characterized against the **pre-push** remote HEAD `e151b784b4bf`:
- `cron/jobs.json` — routine runtime churn (counters / `next_run_at` / `last_run_at` / `updated_at`).
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-10 Hindsight reflect +
  consolidation row).
- `hermes-profile-backup/references/tirith-cron-workarounds.md` — **benign carry-over lag**: the
  2026-10-10 post-push edit adding the attribution note that the cron-mode `execute_code` block is
  the **Hermes cron approval gate, not the tirith scanner** (`pattern_key` detection won't find it).
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over lag**: the
  2026-10-10 post-push edit noting `based_on.memories` count is a run-varying retrieval subset
  (observed `35` on 2026-10-10, not pinned to the 48-fact bank total) — the gate is "present and in
  the tens", not "== 48".

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **242**; remote HEAD `e151b784b4bf`, 261 blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Byte-inspection of the two changed doc files' `=***` grep hits → all literal `***`
  placeholders (no hidden live key; preflight's raw-byte scan CLEAN corroborates)

## Execution notes
- Remote HEAD was `e151b784b4bf` at blob-phase start (attempt 1) and **advanced to
  `b5089466ba27`** (concurrent sibling backup) before the ref PATCH → attempt 1's ref PATCH died
  `HTTP 422 non-fast-forward` (4 blobs + subtree `650ad2f24c19` + top tree `d7505bd19fc9` already
  uploaded) → absorbed by the budgeted **single plain re-run**; attempt 2 clean, identical 4 blobs,
  subtree `650ad2f24c19`, top tree `7896bebe07a2`, remote stable at `b5089466ba27` through commit time.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `650ad2f24c19de0bfaedf9da6c01108129fa68ed`, top tree
  `7896bebe07a277b6516e6f0b52e5253d26e825ce`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `28a371e0e4de`; total blobs **261**, `demo-pm` blobs = **242** (== local file
  count 242); by top dir: demo-pm 242, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-10` → `2026-10-11` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Shears off the 2026-10-10 carry-over doc `M` pair. Afterwards the
preflight is expected to report `Modified: 0, New: 0, Deleted: 0`.
