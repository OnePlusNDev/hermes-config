# demo-pm backup run — 2026-11-08

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `7bce27df4026335e7c79db7bd61f83af62b6862d`
URL: https://github.com/OnePlusNDev/hermes-config/commit/7bce27df4026335e7c79db7bd61f83af62b6862d
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner, `permissions.push=true`; `GITHUB_TOKEN` / `GH_TOKEN`
  both unset — only `GITHUB_USER` is exported) — **no switch needed**, third consecutive clean day
  after the 11-04/11-05 flip pair.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695) → **no plaintext key found, no `key_env`
  replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py e56adb10f3cf` → exit 0,
`MODIFIED 6 / ADDED 0 / DELETED 0` (local 281 vs remote-at-PREV 281), output in
`/tmp/char_20261108.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6579→6626,
  config-backup / memory-cleanup counters 138→139 ×2, `next_run_at` roll to 11-08/11-09,
  per-job `last_run_at` (task-polling 11-08T19:31:27, memory-cleanup 11-07T20:04:54,
  memory-archive 11-07T21:05:22), `updated_at` 11-08T20:00:53; `memories/MEMORY.md` — header
  only, 最后更新 2026-11-06 → 2026-11-07 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-06 →
  2026-11-07 (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md`
  — new **2026-11-07 21:00-21:06 memory cleanup** row (daemon offline at first probe, started via
  `start_hindsight_daemon.sh`, healthy on poll 1 in ~10 s warm pg0; consolidation op
  `de4bbbbe-72bd-4d01-a6e7-7bbce80222c9` +82 ms, counter 97→98; **first reflect after the fresh
  start crashed** — `ServerDisconnectedError` + leaked-semaphore log tail — succeeded on retry
  after relaunch, 172,238 / 8,311; wording gate AFFIRMATIVE for the **17th consecutive** time on a
  new sentence-initial 「过期事实：无」 shape; disambiguation 313,042 / 9,166 concluding
  「无内容性过期事实」; bank↔flat-file LLM-key drift now four consecutive days — logged, no data
  mutated).
- **Benign carry-over doc lag, authored after the 11-07 follow-up push (2):**
  `hermes-profile-backup/references/run-note-diff-characterization.md` (new category-4 section: a
  new `scripts/*.py` under a sibling skill is include-list content when its own SKILL.md gains the
  pointer row and it reads no `.env`/token); `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md`
  (11-07 token row 172,238 / 8,311 + disambig 313,042 / 9,166, the 17th-shape section, and the
  drift-gap line extended to four days).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **281**; preflight read remote HEAD **`e56adb10f3cf`** (300 blobs)
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Preflight read `e56adb10f3cf`; the script's Step 2 read **`7abe43b6b158`** / 300 blobs — a
  **sibling (demo-dev) backup landed in between**. The file set and diff shape were identical at
  each HEAD (6 M / 0 A / 0 D) and the script parented the commit on the fresh HEAD, so nothing was
  lost and no rebase was needed — **no ref-PATCH 422 race**.
- 6 blobs uploaded in one clean pass: `cron/jobs.json` `e32aad43d672`, `MEMORY.md` `7436fa95249f`,
  `USER.md` `c63807ebf949`, `ARCHIVE.md` `479d9bd5af17`, `run-note-diff-characterization.md`
  `aa1345c9e331`, `cleanup-run-endpoints-and-counts.md` `4642392942d0`; subtree
  `aa3ffc6f8f9ebf86e33c338639596db9cb6cce02`, top tree `015771d8721164fb57d158d314dc41ccbfcb8002`,
  commit + ref PATCH on the first attempt (`Remote HEAD now: 7bce27df4026`).
- No network flakiness observed in the main push (no 443 timeout, no `unexpected EOF`). Follow-up
  cleanliness is asserted only by the closing-preflight `0/0/0` check below, not by the log.

## Post-push remote verification
- Remote HEAD `7bce27df4026`; total blobs **300**, `demo-pm` blobs = **281**
  (== local file count 281); by top dir: demo-pm 281, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-07` → `2026-11-08` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
