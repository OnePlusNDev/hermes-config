# demo-pm backup run — 2026-10-07

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `dbc251d3ccf566d866f7ec2986b8a1b5d73fdd94`
URL: https://github.com/OnePlusNDev/hermes-config/commit/dbc251d3ccf566d866f7ec2986b8a1b5d73fdd94
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`JungleAssistant`** (`push=false`) → `gh auth switch --user OnePlusNDev`
  (re-checked immediately pre-run → owner, `push=true`; `GITHUB_TOKEN` unset); no mid-run flip.
  ⚠️ `JungleAssistant` is a **NEW flipper account**, not in the previously-recorded set
  (`OnePlusNTester`, `OnePlusNPM`, `zhangtbj`) — confirms the flipper set is open-ended.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; `auth.json` /
  `auth.lock` / `state.db*` exist locally but are all excluded → **not in the backed-up tree**
  (post-push-verify leak check confirms NONE)

## Diff (4 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
```
Characterized each `M` against the **pre-push** remote HEAD `79032de7d9e8` with
`scripts/characterize-diff-vs-prev-head.py 79032de7d9e8`:
- `cron/jobs.json` — routine runtime churn (`completed` counters 5043→5091 and 106→107;
  `next_run_at` / `last_run_at` / `updated_at` → 2026-10-07).
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-06 Hindsight reflect +
  consolidation row).
- `hermes-profile-backup/templates/run-note-template.md` — **benign carry-over lag**: the
  "`method-b-practice-notes.md` table ROWS share an identical tail" anchor-uniqueness lesson
  (verified 2026-10-06), a 10-06 post-push edit.
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over lag**: the
  "Gate false-positive on section headings (2026-10-06)" lesson, also a 10-06 post-push edit.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **238**; remote HEAD `4cbcf4355bf9`, 257 blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD at the script's Step 2 was `79032de7d9e8` (advanced from the preflight's
  `4cbcf4355bf9` by a concurrent sibling backup before the blob phase) and **stayed there
  through commit time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness, no account flip; the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `ef0a2e79644c86f692dd3328088b5fef1017855e`, top tree
  `9cb9d858a3fbc358c0394b6aad3f39e900c7a990`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `dbc251d3ccf5`; total blobs **257**, `demo-pm` blobs = **238** (== local file
  count 238); by top dir: demo-pm 238, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-06` → `2026-10-07` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
