# demo-pm backup run — 2026-11-11

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `476097bc212c1e97186535ccdd3f1dba047f437f`
URL: https://github.com/OnePlusNDev/hermes-config/commit/476097bc212c1e97186535ccdd3f1dba047f437f
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false` on the repo) → `gh auth switch --user OnePlusNDev`
  verified `push=true`; **6th observed keyring flip** (11-09 was the 5th, 11-10 clean) — the switch held
  through blob phase and ref PATCH (pre-run re-check right before the script still read `OnePlusNDev`).
  `GITHUB_TOKEN` unset.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; `password: ''` /
  `secret: ''` both empty; the only `key_env` occurrence is a doc comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env`, `auth.json`, `auth.lock`, `state.db` present locally and excluded — none in the remote tree.

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py 631db0e91c8b` → exit 0,
`MODIFIED 7 / ADDED 0 / DELETED 0` (local 284 vs remote-at-PREV 284), output in
`/tmp/char_20261111.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6723→6771,
  config-backup / memory-archive counters 141→142, `next_run_at` roll to 11-11/11-12,
  per-job `last_run_at` (task-polling 11-11T20:01:40, memory-cleanup 11-10T20:05:25,
  memory-archive 11-10T21:03:27), `updated_at` 11-11T20:01:40; `memories/MEMORY.md` — header
  only, 最后更新 2026-11-09 → 2026-11-10 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-09 →
  2026-11-10 (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md`
  — new **2026-11-10 21:00-21:06 memory cleanup** row (daemon offline at first probe, started,
  stale-body trap on poll 1 for the **third run running**, healthy on poll 2 in ~10-20 s;
  consolidation op `24009a26-9e54-44ee-b1e7-ec12a662f47c` **+245 ms**, `deduplicated=false`,
  counter 100→101; reflect **both passes succeeded — no crash, no 504** (11-09's 300 s wall-clock
  timeout did not recur): primary **199,548 / 9,377** @ `budget=high` (~150 s); wording gate fired
  for the **20th consecutive** time, new shape = heading + date-conditional + 「快照式事实应优先复核」
  table; disambiguation **267,215 / 5,133** concluding 「无内容性过期事实」 with a 7-row table;
  bank↔flat-file LLM-key drift now **six consecutive days** — logged, no data mutated;
  30-day flat-file recheck: MEMORY.md body identical to `MEMORY-20261029.snapshot.md`,
  USER.md identical to `USER-20261011.snapshot.md`).
- **Benign carry-over doc lag, authored after the 11-10 follow-up push (3):**
  `hermes-profile-backup/references/skill-md-at-cap.md` (new section: opening a daily run with
  `skill_view` costs a 108,606-char JSON dump with a 1,500-char preview → `read_file` the on-disk
  SKILL.md instead); `hermes-profile-backup/templates/run-note-template.md` (new rule: run the
  preflight ONCE MORE between drafting and pushing the follow-up — expect exactly `3 M / 1 A / 0 D`,
  the `A` being today's run note); `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md`
  (11-10 token row 199,548 / 9,377 + disambig 267,215 / 5,133, 20th-shape, drift day 6).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes).

## Preflight
- Local files (after excludes): **284**; preflight read remote HEAD **`631db0e91c8b`** (303 blobs).
  Local 284 == remote `demo-pm` 284: the extra file vs the 11-10 main push (283) is that day's own
  run note, added by the follow-up commit — not a new file today.
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Preflight and the script's Step 2 both read **`631db0e91c8b`** (303 blobs) — no sibling landing
  in the gap, so there was **no preflight→Step-2 divergence** and no ref-PATCH 422 race.
- 7 blobs uploaded in one clean pass: `cron/jobs.json` `9bd979a53339`, `MEMORY.md` `ab0c72370f78`,
  `USER.md` `7806f7ef26f2`, `ARCHIVE.md` `23052d5077b9`, `skill-md-at-cap.md` `120ff98a2a07`,
  `run-note-template.md` `cce19671f2c6`, `cleanup-run-endpoints-and-counts.md` `6b6063510584`;
  subtree `86d0e37ef592663f098ecc61198bd306bf4ca24f`, top tree
  `27e58fc4d95e0b61be309b9a0a5c4a820d2d626f`, commit + ref PATCH on the first attempt
  (`Remote HEAD now: 476097bc212c`).
- No network flakiness in the main push (no 443 timeout, no `unexpected EOF`); the `mkdtemp`
  payload fix held. Follow-up cleanliness is asserted only by the closing-preflight `0/0/0`
  check, not by the log.

## Post-push remote verification
- Remote HEAD `476097bc212c`; total blobs **303**, `demo-pm` blobs = **284**
  (== local file count 284); by top dir: demo-pm 284, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-10` → `2026-11-11` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
