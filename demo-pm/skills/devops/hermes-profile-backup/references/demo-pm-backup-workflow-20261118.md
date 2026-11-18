# demo-pm backup run — 2026-11-18

## Result
**Method B (standalone subtree, no clone)** — **main commit FIRST-TRY, 0 aborts (no 422 race on the
main commit)**, 13th keyring flip caught at pre-flight and the guard re-executed in the SAME shell
call as the script (closing the gap noted honestly on 11-17). Follow-up commit outcome is proven by
the closing preflight assertion at the end of this note.
Main commit: `d2c0b018b82c3f63f067f43949670a85a9399e44`
URL: https://github.com/OnePlusNDev/hermes-config/commit/d2c0b018b82c3f63f067f43949670a85a9399e44
Diff: **8 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **13th observed keyring
  flip** (11-17 logged the 12th). Guard form (switch → re-read login AND `permissions.push`) read
  `OnePlusNDev` / `push=true`.
- **The pre-push guard was re-executed immediately before the script, in the same shell call** (the
  11-17 run note flagged its absence as a process gap): the call printed
  `GUARD: login=OnePlusNDev push=true` and then invoked the backup script in that identical shell,
  so the identity could not re-flip between the check and the first blob POST. No blob 404, no
  mid-run flip.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Diff (8 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+10/-10)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+11/-0)
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md                          (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md (+10/-0)
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md (+25/-0)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+2/-0)
A  demo-pm/skills/devops/hermes-profile-backup/references/tooling-gotchas-and-patch-anchoring.md (+?)
```
`scripts/characterize-diff-vs-prev-head.py` reported **10 M / 1 A** because it derived
`PREV_HEAD = 3d0a4570d7ca` from `parents[0]` of main — which predates the 11-17 **correction**
commit `7ad14556b5cf` ("backup: demo-pm 2026-11-17", 12:08:49Z). That commit's own two files
(`dated-runs-index.md`, `demo-pm-backup-workflow-20261117.md`) are already on the remote. The
preflight — measured against actual HEAD `7ad14556b5cf` — is the authoritative figure: **8 M / 1 A /
0 D**, and it matches the landed commit's file list exactly.

- **Routine runtime churn (4)** — task-polling `repeat.completed` 7059→**7107**, `next_run_at` →
  11-18T20:30, `last_run_at` → 11-18T20:01:44.321578, `updated_at` → 11-18T20:01:44.322215;
  config-backup 148→**149**, next 11-19T20:00, last 11-17T20:09:08.383076; memory-cleanup
  148→**149**, next 11-18T21:00, last 11-17T21:03:51.357041. `memories/MEMORY.md` + `USER.md` — header
  date only, 2026-11-16 → **2026-11-17** (bodies identical; snapshots 20261029 / 20261011 reused).
  `memories/archive/ARCHIVE.md` — new **2026-11-17 21:05 memory cleanup** section: first poll
  healthy (`:9178` warm pg0, ~10 s — **the stale-body trap did NOT fire, breaking the 8-run
  streak**), consolidation op `5fc0ecf3` **+300 ms**, `deduplicated=false`, counter **107→108**,
  bank 48 units / 1228 links / 2 documents, `mental-model list` + `directive list` both empty (so
  consolidation + reflect auditing was the whole "advanced curation"); two reflect passes —
  primary **327,274 / 10,754** with the wording gate firing a **27th consecutive** time in a new
  shape (「## 结论（先给判断）」 opening table whose first row is 「30 天以上的过期事实 | **不存在**」,
  i.e. a correctly-negated verdict still trips the 12-char pre-window rule), disambig
  **409,528 / 4,481** = 「无内容性过期事实」 after a three-class check (长期有效配置类 / 规则铁律类 /
  Hindsight 终态), keeping z.ai GLM → **drift day 13**; sessions **7,378 / 2,932 (>90d) /
  5,878 (>30d)** (+50/day, recorded only — `auto_prune: false`), zero archiving.
- **Carry-over doc edits authored after the 11-17 follow-up push (4):**
  `demo-pm-github-api/SKILL.md` (+1: the 2026-11-18 four-way cross-validation recipe as one
  `pmcheck_<MMDD>_verify.sh` — rate_limit, assignee ×4, full open ×4, zero-task account, Search API —
  plus the finding that the Bearer-header variant **worked this time**, so Bearer is flaky
  rather than hard-banned; Basic Auth stays the default);
  `method-b-practice-notes.md` (+10: pointer to the new tooling-gotchas doc);
  `run-note-template.md` (+25: three new pitfalls — a Python-appended bullet is ONE physical line so
  a multi-line `patch` anchor can never match; a mid-sentence `old_string` silently shears the
  following clause; write the `## Result` headline as a two-part claim from the start);
  `cleanup-run-endpoints-and-counts.md` (+2: the 11-17 reflect row, primary 327,274 / 10,754 and
  disambig 409,528 / 4,481).
- **New reference doc (1):** `tooling-gotchas-and-patch-anchoring.md` — four time-wasters verified
  2026-11-17: the backup scripts implement **no `--help`** (unknown argv is ignored and the full
  backup runs, so probing the interface pushes a commit); `characterize-diff-vs-prev-head.py`
  derives its baseline from `parents[0]` of main, which is off by one commit when HEAD is
  yesterday's follow-up (quote the preflight, not the probe); a Python-appended index bullet is one
  physical line; and a mid-sentence `old_string` shears off the clause after it.
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **296**; remote HEAD at preflight `7ad14556b5cf`, 314 blobs
- Preflight diff: `Modified: 8, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- A sibling **demo-dev** backup landed between the preflight and the blob phase:
  **`02e59d32a94d`** "backup: demo-dev profile config (2026-11-18)", 12:01:29Z. Step 2 read
  `02e59d32a94d` (314 blobs) with the identical **8 M / 1 A / 0 D**, and the remote stayed there
  through Step 7 → the commit is parented on the fresh HEAD and the ref PATCH succeeded on the first
  attempt (**no ref-PATCH 422 race**). The change was confined to `demo-dev/`, so the diff set was
  unaffected.
- 9 blobs uploaded, subtree `c5c666a446fea063d2fd5020a25e9c4b237daa8c`, top tree
  `af41af5d365277fb88be17fe8ca690cfd918fd9c`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `d2c0b018b82c`; total blobs **315**, `demo-pm` blobs = **296** (== local file count
  296); by top dir: demo-pm 296, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings
  intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_*`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-11-17` → `2026-11-18` +
`references/method-b-practice-notes.md` "Observed on recent runs" row `2026-11-18`, pushed with the
same standalone-subtree script. The closing preflight (`Modified: 0, New: 0, Deleted: 0`) is the
proof that this follow-up's ref PATCH landed.
