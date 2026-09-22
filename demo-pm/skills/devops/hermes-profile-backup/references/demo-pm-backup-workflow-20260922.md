# demo-pm backup run — 2026-09-22

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY, no aborted attempts.
Main commit: `ca5146b41ac5a9261d19f7b5356bb8569721e37c`
URL: https://github.com/OnePlusNDev/hermes-config/commit/ca5146b41ac5a9261d19f7b5356bb8569721e37c
Diff: **3 M, 3 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner) — no switch needed
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (3 M, 3 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
A  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
A  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
A  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Carry-over note — the 09-21 slim artifacts landed today, not yesterday
The 3 `A` files are exactly the support files extracted from SKILL.md during the
**2026-09-21** slim (practice notes, cap notes, run-note template), and `SKILL.md` is
`M` — i.e. the remote still carried the pre-slim SKILL.md. So the 09-21 follow-up's
closing assertion (`Modified: 0, New: 0, Deleted: 0`) **did not hold**: the slim +
its extracted files were created *after* that session's follow-up commit, so the
next-morning preflight legitimately saw `3 M / 3 A`. Not a failed push, but a
reminder that the 0/0/0 assertion only proves sync for edits present at push time —
it cannot cover surgery done later in the same session. Nothing to hand-fix.

## Preflight
- Local files (after excludes): **406**; remote HEAD `cdefeb1d36b0`, 422 blobs
- Preflight diff: `Modified: 3, New: 3, Deleted: 0` — **no new exclude gaps**
  (the 09-18 curator-archive churn stays settled; `.archive` / `.curator_suppressed`
  remain excluded as designed)
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `cdefeb1d36b0` at blob-phase start and **stayed there through commit
  time** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- **No network flakiness** — 6 blobs uploaded, subtree `c95e1721c289`,
  top tree `82cdc5e994f8`, commit + ref in one clean pass.
- Trees are built hierarchically so every POST stays small (no flat-tree 422).

## Post-push remote verification
- Remote HEAD `ca5146b41ac5`; total blobs **425**, `demo-pm` blobs = **406** (== local file count 406);
  by top dir: demo-pm 406, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-21` → `2026-09-22`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
