# demo-pm backup run — 2026-11-24

## Result
**Method B (standalone subtree, no clone)** — main commit FIRST-TRY, 0 aborts (no 422 race).
Main commit: `1f50ae58bf055d68ff90e561855dfc6cd979a785`
URL: https://github.com/OnePlusNDev/hermes-config/commit/1f50ae58bf055d68ff90e561855dfc6cd979a785
Diff: **8 M, 0 A, 0 D**.

Scheduler has recovered from the 11-22 outage: `cron/jobs.json` now carries
`last_status: ok` / `last_error: null` for BOTH config-backup (11-23T20:07:52.041845) and
memory-cleanup (11-23T21:04:35.451921). **The open item left by the 11-23 run is closed** —
no missed tick, no catch-up this time.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`,
  re-read `permissions.push=true` — **17th observed keyring flip** (11-21 logged the 16th;
  11-23 was a no-flip day). Guard re-executed before the script in the same flow → no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; names only: `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in tree.

## Diff (8 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `scripts/characterize-diff-post-push.py 57811017fc94` (the push had already
landed, so the pre-push HEAD `57811017fc94` was used, not `main`). Per-file: `jobs.json` +14/-14,
`MEMORY.md` +1/-1, `USER.md` +1/-1, `ARCHIVE.md` +10/-0, `demo-pm-github-api/SKILL.md` +3/-0,
`run-note-diff-characterization.md` +32/-0, `skill-md-at-cap.md` +16/-0,
`cleanup-run-endpoints-and-counts.md` +2/-0. Summary `MODIFIED 8 / ADDED 0 / DELETED 0`,
matching the preflight exactly.

- **4 routine runtime churn** — task-polling `completed` 7347→**7395**, config-backup
  154→**155** (`last_run_at` 11-23T20:07:52.041845), memory-cleanup 154→**155**
  (`last_run_at` 11-23T21:04:35.451921), `updated_at` 11-24T20:01:39.692545; `MEMORY.md` /
  `USER.md` header 2026-11-21 → **2026-11-23**; `ARCHIVE.md` = the 11-23 21:0x cleanup
  (+10 lines) — op `8cf12f77-674b-49f3-ab1a-af02246eca9a` +270 ms, counter
  `operations_by_status.completed` 112→**113**, `total_nodes 48 / total_links 1228` unchanged
  (no-op dedupe), primary **227,610 / 9,895** with the wording gate 32nd consecutive,
  disambig **102,787 / 5,068** → 「无内容性过期事实」; the blob records
  `stale-body 陷阱第 11 次` (poll 1 `000` with the previous healthy body still in
  `/tmp/h9178_p1.json`, healthy poll 2); sessions **7,678 / 3,232 / 6,178** vs
  7,578 / 3,132 / 6,076 last round (all three ~+100 — record, do not read as monotone).
- **4 carry-over doc edits** made since the 11-23 push: `demo-pm-github-api/SKILL.md`
  (+3: `/rate_limit` does not consume core quota and Search has its own bucket — a `200` on
  `/search/issues` is NOT proof core recovered; 403/5-byte interleaving means the 5-byte
  `200` is not evidence; date+HH:MM `/tmp` names still collide across sibling cron runs, use
  `$$`), `run-note-diff-characterization.md` (+32: a diff base older than yesterday's run note
  is a MISSED TICK, not a sibling), `skill-md-at-cap.md` (+16: 5th occurrence of the
  skill-read reflex — start at the grep), `cleanup-run-endpoints-and-counts.md` (+2: the
  11-23 reflect row).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **302**; preflight remote HEAD `34be5ba8bd32`, 321 blobs
- Preflight diff: `Modified: 8, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- **Sibling landed between preflight and Step 2** (verified benign): preflight read
  `34be5ba8bd32` (321 blobs), Step 2 read `57811017fc94` (321 blobs), same **8 M / 0 A / 0 D**
  at each, stable through Step 7 → **no ref-PATCH 422 race**; the ref PATCH succeeded on the
  first attempt. Sibling subtree untouched (demo-dev 5, demo-tester 8, tester-01 5 all intact
  after the push).
- 8 blobs uploaded, subtree `adaf56dbb2de7a0a80033387878135a2a5ac5934`, top tree
  `8904b35793d500df5d24008aa91ccd397eff7a6d`, commit + ref in one clean pass.
- No network flakiness; the `mkdtemp` payload fix held.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `1f50ae58bf05`; total blobs **321**, `demo-pm` blobs = **302** (== local file
  count 302); by top dir: demo-pm 302, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 →
  siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-23` → `2026-11-24` (same-length swap; SKILL.md measured 100,901 B, at cap),
pushed with the same standalone-subtree script. Bullet and row written by
`scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
The closing preflight (`Modified: 0, New: 0, Deleted: 0`) is the proof that this follow-up's
ref PATCH landed.
