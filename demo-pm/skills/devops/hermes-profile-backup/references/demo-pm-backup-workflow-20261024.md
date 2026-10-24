# demo-pm backup run — 2026-10-24

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY (0 aborted attempts, no ref-PATCH 422 race).
Main commit: `3702d9a3853a7b7dc90426bc1d54c5848e0cafed`
URL: https://github.com/OnePlusNDev/hermes-config/commit/3702d9a3853a7b7dc90426bc1d54c5848e0cafed
Diff: **10 M, 1 A, 0 D**.

Notable: the remote copy of `RULES.md` was a **0-byte file**. The local file had been
restored (4537 B, copied from demo-tester) earlier today, so this run replaced the empty
blob on GitHub with the real 144-line collaboration charter — the first time the remote
has carried actual RULES content since the profile was created.

## Pre-flight
- `gh api user` → `OnePlusNDev`, but `permissions.push=false` — the keyring race had
  already flipped the active account. `gh auth status` showed **`OnePlusNTester`** active
  while `gh api user` still resolved `OnePlusNDev`. `gh auth switch --user OnePlusNDev`
  → re-verified `admin=true/push=true`; re-checked immediately pre-run and the switch held.
  (`GITHUB_TOKEN` unset throughout.)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (10 M, 1 A, 0 D)
```
M  demo-pm/RULES.md
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
A  demo-pm/skills/devops/pm-triage-cron/references/2026-10-24-rules-md-was-empty-and-restored.md
```
Characterized against PRE_PUSH HEAD `98c99937d351` (`characterize-diff-vs-prev-head.py`, one run, exit 0):

- **RULES.md — real content restore (1):** remote blob was empty, local is 144 lines /
  4537 B (restored from demo-tester at 01:02 today; recipe in the NEW reference file below).
  Diff is a pure `-0,0 +1,144` insertion — nothing lost, nothing rewritten.
- **Routine runtime churn (2):** `cron/jobs.json` — task-polling `completed` 5859→…,
  memory-cleanup and config-backup counters advanced one day, `updated_at`
  10-23T20:03:38 → 10-24T20:00:33; `memories/archive/ARCHIVE.md` — new 2026-10-23
  Hindsight reflect+consolidation row (no 30+ day memory files to archive; MEMORY.md 23d /
  USER.md 11d still fresh; reflect 241,749/11,595 tokens, first pass passed both gates).
- **Benign carry-over lag, authored after the 10-23 follow-up push (6):**
  `demo-pm-github-api/SKILL.md` (10-23 "5 bytes is not absolute proof" note),
  `hermes-profile-backup/SKILL.md` (the at-cap 100,543 B warning block),
  `hermes-profile-backup/templates/run-note-template.md` (jobs.json re-dirty rule +
  "never anchor on diff text" rule), `hermes-profile-diagnostics/SKILL.md` (emoji-in-heredoc
  + `include.facts: {}` pitfalls), `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md`
  (reflect request schema, 2026-10-23 token row, CLI-500-right-after-cold-start note),
  `pm-triage-cron/SKILL.md` (2026-09-12 baseline line now points at today's RULES restore).
- **Today's triage work (2):** `pm-triage-cron/scripts/pm_fetch.sh` (10-24 — adds
  `--max-time 20/25` to the retry legs plus a `sz=${sz:-0}` guard for failed connections;
  the credential is only ever the `$TOK` env var, no literal token), and the NEW
  `references/2026-10-24-rules-md-was-empty-and-restored.md` (10-24 01:02, 1834 B —
  diagnosis + `cp` restore recipe; content-scanned, no token patterns).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (16835 chars / 17021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **262**; remote HEAD `a9b19e4264e8`, 280 blobs total
  (261 under `demo-pm/`)
- Preflight diff: `Modified: 10, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `a9b19e4264e8` at blob-phase start and **stayed there through commit time**
  → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- 11 blobs uploaded, subtree `c799586921c1faf475b758be7023f4e602e53e87`, top tree
  `c3bc6d8c7a39698676726fae1ae3c0b69628dce7`, commit + ref in one clean pass.
- No network flakiness — neither the backup nor the characterization probe hit a transport error.

## Post-push remote verification
- Remote HEAD `3702d9a3853a`; total blobs **281**, `demo-pm` blobs = **262** (== local file count 262);
  by top dir: demo-pm 262, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-23` → `2026-10-24` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
