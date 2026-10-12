# demo-pm backup run — 2026-10-12

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY (no aborted attempts, no 422 race)**.
Main commit: `23180948b1a7390a3a94c794a4971a06bc975d5b`
URL: https://github.com/OnePlusNDev/hermes-config/commit/23180948b1a7390a3a94c794a4971a06bc975d5b
Diff: **7 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, `push=true`) — **no switch needed**, no mid-run flip
  (`GITHUB_TOKEN` unset)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695); `password`/`secret` empty
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (7 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/tirith-cron-workarounds.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/references/sibling-collision-and-empty-result.md
A  demo-pm/memories/archive/USER-20261011.snapshot.md
```
Characterized against the **pre-push** remote HEAD `478bbfe983c6`:
- `cron/jobs.json` — routine runtime churn (completed counters 5283→5331 + 111→112;
  `next_run_at` / `last_run_at` / `updated_at` rolled 10-11 → 10-12).
- `memories/USER.md` — routine runtime churn (最后更新 2026-09-11 → 2026-10-11; the 30-day archive
  ran, hence the new snapshot below).
- `memories/archive/ARCHIVE.md` — routine runtime churn (记忆清理时间 2026-10-04 → 2026-10-11) + the
  new `USER-20260911.snapshot.md` / `USER-20261011.snapshot.md` archive row.
- `hermes-profile-backup/references/tirith-cron-workarounds.md` — **benign carry-over lag**: the
  2026-10-11 edit adding the `mktemp -d` workaround for the `rm -rf && mkdir` approval-gate stall.
- `hermes-profile-diagnostics/SKILL.md` — **benign carry-over lag**: the 2026-10-11 edit adding the
  "never `curl | python3` inside terminal()" tirith `curl_pipe_shell` HIGH-severity rule.
- `hermes-profile-diagnostics/references/memory-maintenance.md` — **benign carry-over lag**: the
  2026-10-11 note that batch reads must not use `curl | python3` (pending_approval stalls a cron
  run) + the heredoc-`urllib` idiom to reuse.
- `pm-triage-cron/references/sibling-collision-and-empty-result.md` — **benign carry-over lag**: the
  2026-10-12 edit pointing readers at `references/maintenance-notes.md` / the packaged
  `scripts/pm_fetch.sh` (the hand-written two-snapshot form misses the step-3 sanity crosscheck)
  + the "SKILL.md at cap, write new lessons into `references/`" note.
- `A memories/archive/USER-20261011.snapshot.md` — intended new content (30-day USER.md archive
  snapshot; the `memories/archive/` snapshots are explicitly in the include list).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).
The `A` is a genuinely new local file (the new archive snapshot), not an exclude-set mismatch.

## Preflight
- Local files (after excludes): **244**; remote HEAD `478bbfe983c6`, 262 blobs (243 under `demo-pm/`)
- Preflight diff: `Modified: 7, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `478bbfe983c6` at blob-phase start (Step 2) and **stayed there through commit
  time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness; the `mkdtemp` private-payload-dir fix held.
- 8 blobs uploaded, subtree `53520d8b8021b162b821f85988bcf503cf47c984`, top tree
  `c217470be8392374fdfe1cb30e332f62ff18ee39`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `23180948b1a7`; total blobs **263**, `demo-pm` blobs = **244** (== local file count
  244); by top dir: demo-pm 244, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-11` → `2026-10-12` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
