# demo-pm backup run — 2026-10-22

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY (0 aborted attempts, no ref-PATCH 422 race).
Main commit: `83e91837ceb34d2da5b7cf9e6832d926e5cc5c0b`
URL: https://github.com/OnePlusNDev/hermes-config/commit/83e91837ceb34d2da5b7cf9e6832d926e5cc5c0b
Diff: **7 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNTester` (`push=false`) → `gh auth switch --user OnePlusNDev`
  (`push=true` confirmed; `GITHUB_TOKEN` unset; switch held — no mid-run flip)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (7 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/network-flakiness-and-verify-tooling.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
A  demo-pm/skills/devops/pm-triage-cron/references/token-extraction-and-404-diagnosis.md
```
Characterized against PRE_PUSH HEAD `533503f33055`:

- **Routine runtime churn (2):** `cron/jobs.json` — `completed` 5763→5811 and 121→122 ×2,
  `next_run_at`/`last_run_at` advanced one day, `updated_at` refreshed;
  `memories/archive/ARCHIVE.md` — new 2026-10-21 Hindsight reflect+consolidation row
  (no 30+ day memory files to archive; MEMORY.md 22d / USER.md 10d still fresh).
- **Benign carry-over lag (3):** `network-flakiness-and-verify-tooling.md` (mtime 10-21
  20:05:56, 28 s after that day's follow-up push at 20:05:28), `hermes-profile-diagnostics/SKILL.md`
  (10-21 21:05:41) and `cleanup-run-endpoints-and-counts.md` (10-21 21:05:50) — all three
  were authored after the 10-21 follow-up commit landed, so 10-21's `0/0/0` assertion
  legitimately did not hold at that push time.
- **Same-day (today) work (3):** `pm-triage-cron/SKILL.md`, `pm-triage-cron/scripts/pm_fetch.sh`
  and the NEW `references/token-extraction-and-404-diagnosis.md` — the 2026-10-22 triage
  session's token-extraction / 404-misdiagnosis write-up (mtime 17:31 CST, well before this
  backup). The new doc was content-inspected: 2136 B, ASCII-only, no `ghp_`/`github_pat_`/
  `sk-`/hex/base64 token patterns → safe to upload (filename mentions "token-extraction" but
  it is a procedure doc, not a credential).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (16835 chars / 17021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **257**; remote HEAD `533503f33055`, 275 blobs
- Preflight diff: `Modified: 7, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `533503f33055` at blob-phase start and **stayed there through commit time**
  → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt. (That
  `533503f33055` is the sibling **demo-dev** backup of today 12:00:46Z — it landed *before*
  this run's Step 2, so it was absorbed as the commit parent, not as a race.)
- 8 blobs uploaded, subtree `b8c9d0ab60874544c4141e00fdf1e418957095d7`, top tree
  `5b3fc18597b3a475d9e4fc4f554f54272bc0fb86`, commit + ref in one clean pass.
- No network flakiness on the backup itself. Post-run, the optional
  `characterize-diff-vs-prev-head.py` died mid-way on a `net/http: TLS handshake timeout`
  fetching the ARCHIVE.md blob; the `cron/jobs.json` characterization it had already printed
  was kept and the remaining files were classified from local mtimes + commit timestamps.
  This is transport flakiness in the throwaway diagnostic, not a backup failure.

## Post-push remote verification
- Remote HEAD `83e91837ceb3`; total blobs **276**, `demo-pm` blobs = **257** (== local file count 257);
  by top dir: demo-pm 257, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-21` → `2026-10-22` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
