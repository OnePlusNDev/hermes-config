# demo-pm backup run — 2026-11-12

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `39ce322c4a74a24e07d76f19b0d276ca0397a7ba`
URL: https://github.com/OnePlusNDev/hermes-config/commit/39ce322c4a74a24e07d76f19b0d276ca0397a7ba
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, repo `permissions.push=true`, `admin=true`, `GITHUB_TOKEN` unset)
  with **no switch needed** — the 11-11 flip (6th observed) did not recur. A re-check immediately before
  the script still read `OnePlusNDev`; no mid-run re-flip, no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  `password: ''` / `secret: ''` both empty → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py e69ffed97a2e` → exit 0,
`MODIFIED 6 / ADDED 0 / DELETED 0` (local 285 vs remote-at-PREV 285), output in `/tmp/char_20261112.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6771→**6819**,
  `next_run_at` → 11-12T20:30, `last_run_at` 11-12T20:01:23; config-backup `completed` 142→143,
  next 11-13T20:00, last 11-11T20:05:23; memory-archive 142→143, next 11-12T21:00,
  last 11-11T21:02:53; `updated_at` → 11-12T20:01:23. `memories/MEMORY.md` — header only,
  最后更新 2026-11-10 → 2026-11-11 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-10 →
  2026-11-11 (body identical, reuses `archive/USER-20261011.snapshot.md`);
  `memories/archive/ARCHIVE.md` — new **2026-11-11 21:00-21:06 memory cleanup** row (daemon offline at
  first probe, started; stale-body trap on poll 1 for the **fourth run running**, and this time poll 2 was
  ALSO `http_code=000` with healthy only at poll 3, ~20-30 s warm pg0; consolidation op
  `29546377-c264-4146-a240-e80fde731d6f` **+175 ms**, `deduplicated=false`, counter **101→102**;
  nodes 48 / 1228 links / 2 documents stable; reflect both passes succeeded, no crash, no 504 — primary
  **174,613 / 6,627** @ `budget=high`, wording gate **21st consecutive** on the
  「过期事实（30天以上）」 heading + 「若当前日期晚于 2026-07-17 则全部事实均已超过 30 天」 +
  4-item 「最优先需要重验或归档」 shape; disambiguation **238,590 / 7,028** concluding
  「无内容性过期事实」 with a 9-row table; bank↔flat-file LLM-key drift now **seven consecutive days**
  — logged, no data mutated).
- **Benign carry-over doc lag, authored after the 11-11 follow-up push (2):**
  `hermes-profile-backup/references/skill-md-at-cap.md` (new section: the `patch` restriction is a property of
  the *turn type* — background skill-review turns are whitelisted down to memory+skill tools, but a scheduled
  cron RUN turn has the full toolset; verified 2026-11-11 with three `patch` calls and a byte-identical
  100,859 B SKILL.md); `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md`
  (11-11 token row 174,613 / 6,627 + disambig 238,590 / 7,028, gate shape 21, drift day 7; plus two new
  pitfalls — `patch` after a `terminal cat` read emits a bogus sibling-write warning, and two consecutive
  `http_code=000` polls are not a failed daemon start).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes).

## Preflight
- Local files (after excludes): **285**; preflight read remote HEAD **`e69ffed97a2e`** (304 blobs).
  Local 285 == remote `demo-pm` 285.
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- **Sibling landed mid-prep:** the preflight read `e69ffed97a2e`, then a sibling **demo-dev** backup
  (`065dc96e4192`, 12:01:26Z) landed before the script's Step 2, which read `065dc96e4192`
  (304 blobs, same 6 M / 0 A / 0 D set). Nothing failed and no second preflight was needed —
  a sibling touches only its own subtree — but both SHAs are recorded here so tomorrow's reader
  does not see a phantom "lost commit".

## Execution notes
- 6 blobs uploaded in one clean pass: `cron/jobs.json` `4a5aaec75a05`, `MEMORY.md` `012264a9db6f`,
  `USER.md` `47fb098560e4`, `ARCHIVE.md` `aa33440b3a76`, `skill-md-at-cap.md` `f8b7d3825506`,
  `cleanup-run-endpoints-and-counts.md` `32dc8bbc8164`; subtree `82486609ba87f5e35a01961777ec85734ce1acd6`,
  top tree `7198b8fa939a6fb340323bdb03738149632c4c19`, commit + ref PATCH on the first attempt
  (`Remote HEAD now: 39ce322c4a74`).
- Step 2 → commit time the remote HEAD stayed `065dc96e4192` → **no ref-PATCH 422 race**.
- No network flakiness in the main push; the `mkdtemp` payload fix held. Follow-up cleanliness is
  asserted only by the closing-preflight `0/0/0` check, not by the log.

## Post-push remote verification
- Remote HEAD `39ce322c4a74`; total blobs **304**, `demo-pm` blobs = **285** (== local file count 285);
  by top dir: demo-pm 285, demo-dev 5, demo-tester 8, tester-01 5, `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-11` → `2026-11-12` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
