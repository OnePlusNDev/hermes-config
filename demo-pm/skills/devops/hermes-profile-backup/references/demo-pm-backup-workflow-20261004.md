# demo-pm backup run — 2026-10-04

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts)**.
Main commit: `208ac435e4d0e6a287b660d7a43f89bb81653a9f`
URL: https://github.com/OnePlusNDev/hermes-config/commit/208ac435e4d0e6a287b660d7a43f89bb81653a9f
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, `push=true`) — **no switch needed**
  (`GITHUB_TOKEN` unset), no mid-run flip
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/pm-triage-cron/references/sibling-collision-and-empty-result.md
```
Characterized each `M` against the **pre-push** remote HEAD `7f5418a4ef91` with
`scripts/characterize-diff-vs-prev-head.py 7f5418a4ef91`:
- `cron/jobs.json` — routine runtime churn (`completed` 4899→4947, 103→104; `next_run_at` /
  `last_run_at` / `updated_at` advanced to 2026-10-04). Pure runtime churn.
- `hermes-profile-backup/SKILL.md` — **benign carry-over lag**: the "same-day repeat run →
  `YYYYMMDDb.md`" addition to the `latest:` pointer line, written after the 10-03b run's
  follow-up push → ordering, not a lost commit.
- `templates/run-note-template.md` — **benign carry-over lag**: the new "Same-day repeat run"
  paragraph (also written after the 10-03b follow-up push).
- `pm-triage-cron/references/sibling-collision-and-empty-result.md` — a **2026-10-04 doc edit**
  (adding the output-path `$$` PID lesson): today's triage-recipe edit, part of the intended
  content set this run.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **234**; remote HEAD `7f5418a4ef91`, **253** blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `7f5418a4ef91` at blob-phase start and **stayed there through commit time** →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness, no mid-run account flip; the `mkdtemp` private-payload-dir fix held.
- 4 blobs uploaded, subtree `b3502ed58de202c92fbabb3cbc76e4bab157801d`, top tree
  `6c237a8753a4686911e47e32f55716a4af144960`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `208ac435e4d0`; total blobs **253**, `demo-pm` blobs = **234** (== local file
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
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-03` → `2026-10-04` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
