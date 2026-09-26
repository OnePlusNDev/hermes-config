# demo-pm backup run — 2026-09-26

## Result
**Method B (standalone subtree, no clone)** — success, **1 aborted attempt** (account flip, see below).
Main commit: `3734ef8ff71bcb80675a6331014487736ab06430`
URL: https://github.com/OnePlusNDev/hermes-config/commit/3734ef8ff71bcb80675a6331014487736ab06430
Diff: **6 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`zhangtbj`** (a *fifth* gh account on this keyring; the repo owner is
  `OnePlusNDev`) with `permissions.push = false` → `gh auth switch --user OnePlusNDev` →
  `push=true` confirmed before any blob POST
- ⚠️ **The flip recurred MID-RUN**: attempt 1 died at the first blob with
  `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`; a re-check of
  `gh api user` showed `zhangtbj` active *again* — the keyring race re-flipped the active
  account between the pre-flight switch and the blob POST (~1 min). Second switch → clean
  re-run. This is the documented "check the active account TWICE" rule; the first account
  observed this run was **not** one of the previously-recorded candidates
  (OnePlusNDev / OnePlusNTester / OnePlusNPM / JungleAssistant)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695); `password:`/`secret:` both `''`
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/curator-archive-churn-triage.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
A  demo-pm/skills/devops/hermes-profile-backup/scripts/verify-curator-archive-churn.py
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).
3 of the `M` (SKILL.md hunks, `curator-archive-churn-triage.md` Recurrence log,
`run-note-template.md`) are **benign carry-over lag** — doc edits written *after* the
09-25 follow-up push, so that run's `0/0/0` closing assertion legitimately did not hold.

## Preflight
- Local files (after excludes): **225**; remote HEAD `5f8e78cf1073`, **243** blobs
- Preflight diff: `Modified: 6, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `5f8e78cf1073` at preflight and had advanced to `03b61c6a6c89` (concurrent
  sibling backup) by the script's own Step 2 — absorbed silently by the re-read (243 blobs
  both times, i.e. the sibling was outside `demo-pm/`).
- Attempt 1 aborted on the **account flip** (404, above); attempt 2 clean.
- **No ref-PATCH 422 race:** remote was stable at `03b61c6a6c89` through the blob phase, and
  the ref PATCH succeeded on the **first** attempt.
- No network flakiness, no shared-`/tmp` payload deletion (the 09-23 `mkdtemp` fix held).
- 7 blobs uploaded, subtree `7b528200e686`, top tree `d443235fcd57`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `3734ef8ff71b`; total blobs **244**, `demo-pm` blobs = **225** (== local file count 225);
  by top dir: demo-pm 225, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-25` → `2026-09-26` + a
`method-b-practice-notes.md` table row for this run's abort, pushed with the same
standalone-subtree script. Afterwards the preflight reports `Modified: 0, New: 0, Deleted: 0`.
