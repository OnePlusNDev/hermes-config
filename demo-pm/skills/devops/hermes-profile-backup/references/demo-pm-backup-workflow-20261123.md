# demo-pm backup run — 2026-11-23

## Result
**Method B (standalone subtree, no clone)** — **main commit FIRST-TRY, 0 aborts (no 422 race)**,
no keyring flip at pre-flight (first run since 11-15 to read the owner directly).
This run is also the **catch-up for the failed 2026-11-22 tick** (see Pre-flight).
Main commit: `1b645c1495981aa2a17e1e2f6cec216398e5c2d3`
URL: https://github.com/OnePlusNDev/hermes-config/commit/1b645c1495981aa2a17e1e2f6cec216398e5c2d3
Diff: **8 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (`permissions.push=true`) on the FIRST probe — **no flip, no
  switch needed** (record stays at 16 accumulated flips; 11-21 logged the 16th). The pre-push guard
  was still re-executed in the SAME shell call as the script and printed
  `GUARD: login=OnePlusNDev push=true`. No blob 404, no mid-run flip.
- **Gap detected: the 2026-11-22 run never happened.** `cron/jobs.json` at the pre-push HEAD
  records `last_status: "error"` / `last_error: "RuntimeError: Connection error."` for BOTH the
  config-backup job (`last_run_at` 2026-11-22T20:02:45.840119) and the memory-cleanup job
  (`last_run_at` 2026-11-22T21:03:18.960666). Corroborating evidence: no
  `references/demo-pm-backup-workflow-20261122.md` exists, the pre-push diff base was still the
  11-21 post-follow-up state, and `memories/archive/ARCHIVE.md` has no 11-22 section. Today's run
  therefore carries **two days** of runtime churn (task-polling +96 ticks, config/memory counters
  +2 each) in one commit.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{10,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; `GITHUB_USERNAME` / `GITHUB_EMAIL` / `GITHUB_TOKEN` / `GATEWAY_PORT` /
  `AGENT_NAME` / `AGENT_ROLE` / `DEEPSEEK_API_KEY` / `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in the remote tree.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.

## Diff (8 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+14/-14)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+10/-0)
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md                         (+1/-1)
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md (+33/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md (+14/-1)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+9/-1)
```
Counts from `scripts/characterize-diff-post-push.py 35c6d6b6ba6f` (MODIFIED 8 / ADDED 0 /
DELETED 0), cross-checked against `scripts/characterize-diff-vs-prev-head.py 35c6d6b6ba6f`
(pre-push, same set). Self-check: identical 293 + changed 8 = 301 == preflight's 301 local files.

- **Routine runtime churn (4)** — task-polling `repeat.completed` 7251→**7347** (two days of
  48/day ticks), `next_run_at` → 11-23T20:30, `last_run_at` → 11-23T20:02:11.176766;
  config-backup 152→**154**, next 11-24T20:00, last 11-22T20:02:45.840119 (**error**);
  memory-cleanup 152→**154**, next 11-23T21:00, last 11-22T21:03:18.960666 (**error**).
  `memories/MEMORY.md` + `USER.md` — header date only, 2026-11-20 → **2026-11-21** (bodies
  identical; snapshots 20261029 / 20261011 reused). `memories/archive/ARCHIVE.md` — new
  **2026-11-21 21:0x memory cleanup** section: `:9178` offline at first probe, launcher start →
  **poll 1 healthy** (~10 s, warm pg0, no stale-body trap), consolidation op `0c30126e` **+216 ms**,
  counter **111→112**, 48 nodes / 1228 links unchanged (no-op dedupe), primary **99,453 / 5,294**
  (gate fired, **31st consecutive**; table-cell ``| 30天以上过期事实 | **未发现** |`` shape +
  06-17 date-conditional), disambig **351,465 / 5,934** = 「无内容性过期事实」 → 归档 0, keeping
  z.ai GLM → **drift day 17**; sessions **7,578 / 3,132 (>90d) / 6,076 (>30d)** — all three ~+50
  over 11-21 again, not treated as monotone.
- **Carry-over doc edits authored after the 11-21 follow-up push (4):**
  `demo-pm-github-api/SKILL.md` (+1/-1: the long account-drift bullet's 复核 clause moves from
  "至 11-21 已第 16 次" — the 11-21 session's own self-referential edit);
  `run-note-diff-characterization.md` (+33/-0: new §"A `(+1/-1)` hunk whose two lines look
  IDENTICAL — the edit is past the 300-char clip", with the `?ref=<PREV_SHA>` difflib probe);
  `skill-md-at-cap.md` (+14/-1: "Fourth occurrence, 2026-11-21 — the fix is a *starting order*,
  not a reminder", i.e. order the run so no skill read is needed first);
  `cleanup-run-endpoints-and-counts.md` (+9/-1: `GET /banks` is not a route — `/v1/default/`
  prefix mandatory; the 11-21 reflect row appended to the run table).
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes / 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **301**; remote HEAD at preflight `35c6d6b6ba6f`, 320 blobs
- Preflight diff: `Modified: 8, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD **stable at `35c6d6b6ba6f`** (320 blobs) from preflight through Step 7 (Step 2 read
  the same SHA) → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- 8 blobs uploaded, subtree `372a417bfc317f6f8852a2bb4e904864aa1cc854`, top tree
  `fdd3502e7370844bc647ea2a2acb5c65abbfe9af`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `1b645c149598`; total blobs **320**, `demo-pm` blobs = **301** (== local file count
  301); by top dir: demo-pm 301, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings
  intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_*`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-21` → `2026-11-23` (same-length swap), pushed with the same standalone-subtree script.
Bullet and row written by `scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
The closing preflight (`Modified: 0, New: 0, Deleted: 0`) is the proof that this follow-up's ref
PATCH landed.

**Open item for the next run:** if `cron/jobs.json` again shows `last_status: "error"` with
`RuntimeError: Connection error.` for 11-23/11-24, the scheduler's own outbound connectivity is
intermittent (not the backup script) — this run proves the same push path works when executed
manually at the same hour.
