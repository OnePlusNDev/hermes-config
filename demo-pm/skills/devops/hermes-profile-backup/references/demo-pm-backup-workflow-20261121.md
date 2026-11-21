# demo-pm backup run — 2026-11-21

## Result
**Method B (standalone subtree, no clone)** — **main commit FIRST-TRY, 0 aborts (no 422 race)**,
16th keyring flip caught at pre-flight, guard re-executed in the SAME shell call as the script.
Follow-up outcome is proven by the closing preflight assertion at the end of this note.
Main commit: `b261027bafda455bbb1125a7c5309064bd22d7c5`
URL: https://github.com/OnePlusNDev/hermes-config/commit/b261027bafda455bbb1125a7c5309064bd22d7c5
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **16th observed keyring
  flip** (11-20 logged the 15th). Guard form (switch → re-read login AND `permissions.push`) read
  `OnePlusNDev` / `push=true`; the pre-push guard was re-executed immediately before the script in
  the same shell call and printed `GUARD: login=OnePlusNDev push=true`. No blob 404, no mid-run flip.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; `GITHUB_USERNAME` / `GITHUB_EMAIL` / `GITHUB_TOKEN` / `GATEWAY_PORT` /
  `AGENT_NAME` / `AGENT_ROLE` / `DEEPSEEK_API_KEY` / `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in the remote tree.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+10/-10)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+15/-0)
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md                         (+1/-1)
M  demo-pm/skills/devops/hermes-profile-backup/references/tooling-gotchas-and-patch-anchoring.md (+31/-1)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+7/-0)
```
Counts and content from `scripts/characterize-diff-post-push.py 48f1f23def66` (prev blobs 319 /
new 319, identical 293; self-check 293 + 7 = 300 == preflight's 300 local files).

- **Routine runtime churn (4)** — task-polling `repeat.completed` 7203→**7251**, `next_run_at` →
  11-21T20:30, `last_run_at` → 11-21T20:00:49.041353; config-backup 151→**152**, next 11-22T20:00,
  last 11-20T20:05:58.339191; memory-cleanup 151→**152**, next 11-21T21:00, last
  11-20T21:04:10.786772. `memories/MEMORY.md` + `USER.md` — header date only, 2026-11-19 →
  **2026-11-20** (bodies identical; snapshots 20261029 / 20261011 reused).
  `memories/archive/ARCHIVE.md` — new **2026-11-20 21:0x memory cleanup** section: `:9178` offline
  at first probe, launcher start → poll1 **and** poll2 `000` (stale-body trap **11th consecutive**,
  fresh per-poll `/tmp/h9178_p<N>.json`), poll3 200 healthy at ~20-30 s; consolidation op
  `80d76f7f` **+446 ms**, counter **110→111**, `total_nodes=48` / `total_links=1228` (semantic 740 /
  temporal 469 / entity 19) / 2 documents / 18 observations, `mental-model list` + `directive list`
  both empty; two reflect passes — primary **170,607 / 7,876** (gate fired, **30th consecutive**,
  shape: opening 「30 天以上过期事实：无」 + heading 「一、过期事实（30 天以上）：无」 with the
  negation outside the 12-char pre-window + 06-17 date-conditional), disambig **395,237 / 8,395**
  = 「无内容性过期事实」 → 归档 0, keeping z.ai GLM → **drift day 16**; sessions **7,528 / 3,082
  (>90d) / 6,028 (>30d)** — the >90d count went UP vs 11-20's 3,032 (recorded as an anomaly, not
  treated as monotone).
- **Carry-over doc edits authored after the 11-20 follow-up push (3):**
  `demo-pm-github-api/SKILL.md` (+1/-1 on the long account-drift bullet: adds the 2026-11-20 复核
  note that the pre-check-and-switch is now standing practice, 15 consecutive flips, and that both
  pushes in a guarded run were 404-free);
  `tooling-gotchas-and-patch-anchoring.md` (+31/-1: "Eight traps" → "**Nine traps**", post-push
  variant of the characterize probe + the `identical + changed == blob count` self-consistency
  check, and new §9 on paging this skill's 100 K SKILL.md instead of reading it whole);
  `cleanup-run-endpoints-and-counts.md` (+7/-0: the 11-20 session-row anomaly note that `>90 d`
  must not be treated as a monotone counter, plus the 11-20 reflect row 170,607 / 7,876 /
  disambig 395,237 / 8,395).
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes / 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **300**; remote HEAD at preflight `bd9040701567`, 319 blobs
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- A sibling landed between preflight (`bd9040701567`, 319 blobs) and Step 2
  (`48f1f23def66`, 319 blobs) → the **identical 7 M / 0 A / 0 D** set, stable through Step 7 →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- 7 blobs uploaded, subtree `86b6df8bf513d20c5c268eaa0f33bf872c3bc237`, top tree
  `ea26d3f0874ca1a55cba0bd0baef81db23ab4204`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `b261027bafda`; total blobs **319**, `demo-pm` blobs = **300** (== local file count
  300); by top dir: demo-pm 300, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings
  intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_*`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-20` → `2026-11-21` (same-length swap), pushed with the same standalone-subtree script.
Bullet and row written by `scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
The closing preflight (`Modified: 0, New: 0, Deleted: 0`) is the proof that this follow-up's ref
PATCH landed.
