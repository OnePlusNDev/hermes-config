# demo-pm backup run — 2026-10-06

## Result
**Method B (standalone subtree, no clone)** — success, **1 aborted attempt (ref-PATCH 422 race; attempt 2 clean)**.
Main commit: `ff759b7ea76570d0bf4702e2bda9aefc8eee1104`
URL: https://github.com/OnePlusNDev/hermes-config/commit/ff759b7ea76570d0bf4702e2bda9aefc8eee1104
Diff: **5 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`
  (re-checked immediately pre-run → owner, `push=true`; `GITHUB_TOKEN` unset); no mid-run flip
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (5 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
A  demo-pm/skills/devops/pm-triage-cron/references/maintenance-notes.md
```
Characterized each `M` against the **pre-push** remote HEAD `c332a3c5a980` with
`scripts/characterize-diff-vs-prev-head.py c332a3c5a98009c5032ec0b9b84a27bacaa0884a`
(identical result vs the first attempt's base `08d2e00d49ea`):
- `cron/jobs.json` — routine runtime churn (`completed` counters advanced; `next_run_at` /
  `last_run_at` / `updated_at` → 2026-10-06).
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-05 Hindsight reflect +
  consolidation row).
- `hermes-profile-backup/references/skill-md-at-cap.md` — **benign carry-over lag**: the
  "`search_files(target='files')` is NOT a safe substitute for a broad listing" lesson
  (verified 2026-10-05), written after the 10-05 follow-up push.
- `hermes-profile-backup/templates/run-note-template.md` — **benign carry-over lag**: the
  "Copy the anchor VERBATIM — never reconstruct it from memory" index-append lesson
  (verified 2026-10-05).
- `hermes-profile-diagnostics/SKILL.md` — **benign carry-over lag**: the "Superseded again
  2026-10-04 + 2026-10-05" daemon-startup-latency recalibration (~7 min with a WARM PG;
  first-reflect-after-fresh-start can crash), also a 10-05 post-push edit.
- `pm-triage-cron/references/maintenance-notes.md` — **new reference doc** (legit skill
  content, token scan CLEAN).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **237**; remote HEAD `08d2e00d49ea`, **255** blobs
- Preflight diff: `Modified: 5, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Attempt 1 (base `08d2e00d49ea`): 6 blobs + subtree `7aa4284ef2bf` + top tree `c08b67036240`
  + commit `88a1f0f59892` all created, but the ref PATCH died **`HTTP 422 Update is not a fast
  forward`** (remote advanced `08d2e00d49ea` → `c332a3c5a980` via a concurrent sibling backup
  during the blob phase).
- **Budgeted single plain re-run** (blob SHAs idempotent): attempt 2 re-read the remote at
  `c332a3c5a980`, uploaded the identical 6 blobs + subtree `7aa4284ef2bf`, built top tree
  `a2cd6dc43956`, commit `ff759b7ea765`, and the ref PATCH succeeded on the first try.
- No network flakiness, no account flip; the `mkdtemp` private-payload-dir fix held.

## Post-push remote verification
- Remote HEAD `ff759b7ea765`; total blobs **256**, `demo-pm` blobs = **237** (== local file
  count 237); by top dir: demo-pm 237, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-05` → `2026-10-06` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
