# demo-pm backup run — 2026-11-04

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no account flip, no 422 race)**.
Main commit: `169326f5b055d03c1396ea014ed2641e8a3048a5`
URL: https://github.com/OnePlusNDev/hermes-config/commit/169326f5b055d03c1396ea014ed2641e8a3048a5
Diff: **9 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (not owner) — **switched** with `gh auth switch --user OnePlusNDev`
  (`GITHUB_TOKEN` unset first); re-check returned `OnePlusNDev`, `permissions.push=true`, and the
  account held through the whole run (no mid-run flip). The 10-29/10-30 burst pattern put the flip
  back on the board today; the pre-flight check caught it before any write.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Diff (9 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/scripts/reflect_quality_check.py
```
Characterized with `characterize-diff-vs-prev-head.py --commit=169326f5b055d03c1396ea014ed2641e8a3048a5`
(full 40-char SHA), derived PRE_PUSH `5276b169fea61b84eece019034c68ffb90b4c38f`, one run, exit 0,
output sliced from `/tmp/bk-1104/char.txt`; it reported **MODIFIED 9 / ADDED 0 / DELETED 0**
(local 275 vs remote-at-PREV 275).

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6387→6435,
  config-backup and memory-cleanup counters 134→135 ×2, `next_run_at` 11-03→11-04 /
  11-04→11-05, per-job `last_run_at`, `updated_at` roll-over;
  `memories/MEMORY.md` — header 最后更新 2026-11-02 → 2026-11-03 with the 30-day **re-check**
  (body byte-identical, no expired facts, reuses `archive/MEMORY-20261029.snapshot.md`);
  `memories/USER.md` — same re-check shape (header 2026-11-02 → 2026-11-03, reuses
  `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` — new 2026-11-03 row
  (`:9178` offline at first probe, only the global `:8888` daemon listening → launcher start,
  poll1/poll2 `http_code=000` then healthy on poll3 (~20-30 s); consolidation op
  `97a9d1cc-4e3b-4e76-a38a-aea8cdfd347e` +251 ms, completed 93→94 confirmed by post-reflect
  `/stats`; reflect 208,888/8,642 — **first primary in 14 runs to pass the wording gate clean**,
  disambiguation paid anyway at 166,518/6,318 `based_on=34` → 「无内容性过期事实」; 48 nodes /
  1228 links / 18 observations / 0 pending; the pass also recorded a **gate coverage gap**
  (「应优先归档」 slipped past the keyword list) which was fixed in the script below).
- **Benign carry-over lag, authored after the 11-03 follow-up push (5):**
  `hermes-profile-backup/references/method-b-practice-notes.md` (mtime 20:07:17, **38 s** after the
  11-03 follow-up `b86382ffee97` at 12:06:39Z = 20:06:39 CST — new ⚠️ section "The ref PATCH can
  fail SILENTLY — the log just stops at Step 7", the 11-03 follow-up 422 race, plus the
  ordering corollary for run notes) and `templates/run-note-template.md` (mtime 20:07:21, 42 s
  after — the same clarification folded into the template's closing-line guidance);
  `hermes-profile-diagnostics/SKILL.md`, `references/cleanup-run-endpoints-and-counts.md` and
  `scripts/reflect_quality_check.py` (mtime 21:03, i.e. written by the **21:00 memory-cleanup
  cron** — 11-03 token row, the keyword extension `应归档 / 应优先归档 / 建议归档` in `_KW`, and
  the startup-calibration note). All five are same-day work authored after the previous push,
  so 11-03's closing `0/0/0` legitimately did not hold — ordering, not a lost commit.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **275**; preflight read remote HEAD **`b86382ffee97`** (294 blobs).
  A sibling **demo-dev** backup (`5276b169fea6`, 2026-11-04T12:01:22Z) landed between that read and
  the script's Step 2, which read `5276b169fea6` / 294 blobs — **same 9 M / 0 A / 0 D**, and the
  commit was parented on the fresh HEAD, so nothing was lost (no 422 race, no aborted attempt).
- Preflight diff: `Modified: 9, New: 0, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- 9 blobs uploaded in one clean pass: `cron/jobs.json` `7edb559d8ede`, `MEMORY.md` `128b1a7da304`,
  `USER.md` `e0df9cef7e19`, `ARCHIVE.md` `1c9e5dd0c405`, `method-b-practice-notes.md`
  `4eb26d110f74`, `run-note-template.md` `86f341eb7f44`, diagnostics `SKILL.md` `70c4144a6ed0`,
  `cleanup-run-endpoints-and-counts.md` `9060ac3d9d8b`, `reflect_quality_check.py` `79946deae341`;
  subtree `80df6270afc6d8b51f22056e1202b0328e6477b1`, top tree
  `f97681d579c0f0072b3b12901cf2bdadd72c1c7a`, commit + ref PATCH on the first attempt
  (`Remote HEAD now: 169326f5b055`).
- No network flakiness (no 443 timeout, no `unexpected EOF`). Follow-up cleanliness is asserted
  only by the closing-preflight `0/0/0` check below, not by the log.

## Post-push remote verification
- Remote HEAD `169326f5b055`; total blobs **294**, `demo-pm` blobs = **275**
  (== local file count 275); by top dir: demo-pm 275, demo-dev 5, demo-tester 8,
  tester-01 5, `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row +
SKILL.md `latest:` `2026-11-03` → `2026-11-04` (same-length in-place swap; SKILL.md is still over
its 100 K cap, so no new prose goes in it). Pushed with the same standalone-subtree script; the
closing preflight must report `Modified: 0, New: 0, Deleted: 0`.
