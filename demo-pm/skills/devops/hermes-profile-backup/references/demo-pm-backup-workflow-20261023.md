# demo-pm backup run — 2026-10-23

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY (0 aborted attempts, no ref-PATCH 422 race).
Main commit: `5d5e084b8c85cf5727b09eb7eb5b95ba1396cf5b`
URL: https://github.com/OnePlusNDev/hermes-config/commit/5d5e084b8c85cf5727b09eb7eb5b95ba1396cf5b
Diff: **7 M, 2 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner, `push=true`/`admin=true`) — no switch needed;
  `GITHUB_TOKEN` unset; no mid-run flip (re-checked implicitly by the clean blob phase)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (7 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
A  demo-pm/skills/devops/pm-triage-cron/references/2026-10-22-http2-false-empty.md
A  demo-pm/skills/devops/pm-triage-cron/references/2026-10-23-skill-view-oversize-and-sibling-script-collision.md
```
Characterized against PRE_PUSH HEAD `befc945f97e8` (`characterize-diff-vs-prev-head.py`, one run, exit 0):

- **Routine runtime churn (2):** `cron/jobs.json` — task-polling `completed` 5811→5859,
  memory-cleanup and config-backup `completed` 122→123 each, all `next_run_at`/`last_run_at`
  advanced one day, `updated_at` 10-22T20:03 → 10-23T20:03; `memories/archive/ARCHIVE.md` —
  new 2026-10-22 Hindsight reflect+consolidation row (no 30+ day memory files to archive;
  MEMORY.md 23d / USER.md 11d still fresh).
- **Benign carry-over lag, authored after the 10-22 follow-up push (4):**
  `run-note-diff-characterization.md` (mtime 10-22 20:22:57),
  `cleanup-run-endpoints-and-counts.md` (10-22 21:03:36, written by the 21:00 memory-cleanup cron),
  `demo-pm-github-api/SKILL.md` (10-23 00:03:02),
  NEW `references/2026-10-22-http2-false-empty.md` (10-22 23:07:59 — doc for the triage
  HTTP/2 false-empty diagnosis; content-scanned, no token patterns).
- **Today's triage work (3):** `pm-triage-cron/SKILL.md` (10-23 17:33:20),
  `pm-triage-cron/scripts/pm_fetch.sh` (10-23 07:31:30 — diff inspected: adds a
  `fetch_best()` retry-N-take-largest-bytes helper + a Search-API cross-check leg; the API
  token is only ever referenced as the `$TOK` env var, no literal credential), and the NEW
  `references/2026-10-23-skill-view-oversize-and-sibling-script-collision.md` (10-23 17:32:49,
  4179 B, no `ghp_`/`github_pat_`/`sk-`/hex token patterns).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (16835 chars / 17021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **260**; remote HEAD `befc945f97e8`, 277 blobs total
  (258 under `demo-pm/`)
- Preflight diff: `Modified: 7, New: 2, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `befc945f97e8` at blob-phase start and **stayed there through commit time**
  → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- 9 blobs uploaded, subtree `d5ebd2ce879a0741fb1ba9dc6ea64acb200dbfa5`, top tree
  `8649f37cffcbf633fde41fcccbea35da21f75159`, commit + ref in one clean pass.
- No network flakiness — neither the backup nor the characterization probe hit a transport error.

## Post-push remote verification
- Remote HEAD `5d5e084b8c85`; total blobs **279**, `demo-pm` blobs = **260** (== local file count 260);
  by top dir: demo-pm 260, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-22` → `2026-10-23` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
