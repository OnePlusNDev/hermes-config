# demo-pm backup run — 2026-09-24

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY** (no aborted attempts).
Main commit: `0da99942c4cc1984fb0614004abff590f49452a6`
URL: https://github.com/OnePlusNDev/hermes-config/commit/0da99942c4cc1984fb0614004abff590f49452a6
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner) — **no switch needed** (09-23 was the odd day out;
  09-24 is back to owner-active, and the pre-push re-check held as well)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **409**; remote HEAD `6c156eb1e2c4`, 428 blobs
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- **Carry-over lag, benign:** the local `SKILL.md` differed from the remote in exactly two
  doc hunks — the shared-`/tmp` payload-collision note in the `method-b-practice-notes`
  pointer paragraph, and the "re-measure with `wc -c`" headroom caveat. Both were written
  *after* the 09-23 follow-up push, so they legitimately surfaced as today's `M` and were
  pushed as part of today's main commit (ordering, not a lost commit — the 09-23 closing
  `0/0/0` assertion only covers edits present at push time).
- File count 407 → **409** since 09-23: the +2 are the 09-23 follow-up artifacts
  (`references/demo-pm-backup-workflow-20260923.md`, `references/method-a-rsync-excludes.md`).

## Execution notes
- Remote HEAD was `6c156eb1e2c4` at preflight and advanced to `46c22a23e2e5` (a concurrent
  sibling `demo-dev` backup, 2026-09-24T12:00:45Z) **before** the script's own Step 2 —
  the script re-read the ref, so this was absorbed silently (harmless; only means the diff
  was recomputed against the newer HEAD).
- **No ref-PATCH 422 race:** remote was stable at `46c22a23e2e5` through the blob phase, and
  the ref PATCH succeeded on the **first** attempt.
- No network flakiness, no shared-`/tmp` payload deletion (the 09-23 `mkdtemp` fix held).
- 6 blobs uploaded, subtree `487714750df008277540bb1389a245ac53c8ba66`, top tree
  `1aece6e84fbb76d5de2b1f1f7b0e267fbee5b46c`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `0da99942c4cc`; total blobs **428**, `demo-pm` blobs = **409** (== local file count 409);
  by top dir: demo-pm 409, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-23` → `2026-09-24`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
