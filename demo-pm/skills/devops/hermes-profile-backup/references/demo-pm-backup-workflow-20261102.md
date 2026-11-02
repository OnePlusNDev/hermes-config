# demo-pm backup run — 2026-11-02

## Result
**Method B (standalone subtree, no clone)** — **ONE aborted attempt (account flip → blob HTTP 404, not a 422)**.
Main commit: `df4f29533df543e8ba89d76bcd0c6da17b5f55a9`
URL: https://github.com/OnePlusNDev/hermes-config/commit/df4f29533df543e8ba89d76bcd0c6da17b5f55a9
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) — the 10-29/10-30 keyring flip returned after
  two clean days → `gh auth switch --user OnePlusNDev` verified owner.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Aborted attempt (1)
The first script invocation (made to inspect `--help`, which this script does not implement —
it just RUNS) died at the first blob:
`FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`.
That 404 is the documented account-flip signature, not a missing repo: the switch had not held.
No blobs/commit/ref were produced by attempt 1. Second `gh auth switch --user OnePlusNDev`,
one plain re-run → Steps 1-7 clean.

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `characterize-diff-vs-prev-head.py --commit=df4f29533df543e8ba89d76bcd0c6da17b5f55a9`
(full 40-char SHA), derived PRE_PUSH `649c1e25bba0`, one run, exit 0, output sliced from
`/tmp/bk-1102/char.txt`; it reported **MODIFIED 6 / ADDED 0 / DELETED 0** (local 273 vs
remote-at-PREV 273).

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6291→6339,
  config-backup and memory-cleanup counters 132→133 ×2, `next_run_at` 11-01→11-02 /
  11-02→11-03, per-job `last_run_at`, `updated_at` roll-over;
  `memories/MEMORY.md` — header 最后更新 2026-10-31 → 2026-11-01 with the 30-day **re-check**
  (body byte-identical, no expired facts, reuses `archive/MEMORY-20261029.snapshot.md`);
  `memories/USER.md` — same re-check shape (header 2026-10-31 → 2026-11-01, reuses
  `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` — new 2026-11-01 row
  (`:9178` offline at first probe, only the global `:8888` daemon listening → launcher start,
  healthy on the 2nd 10 s poll, ~10-20 s; the `:8888` bank list held only
  demo-dev/active/hermes — **no `demo-pm-memory`**, so a sibling bypass is impossible for this
  bank and the profile launcher is mandatory; consolidation op `9c27af6d` +363 ms, completed
  91→92; **no reflect crash, both calls first-try**; reflect 189,432/7,374; disambig
  167,011/7,013 → 「无内容性过期事实」; wording gate fired on a **10th shape — perishability
  reclassification** (opened 「是，三类问题都存在」 and swapped the 30-day criterion for
  「是否属于状态快照」, listing 7 archive candidates), **12th consecutive** trigger;
  48 nodes / 1228 links / 18 observations / 0 pending; sessions 6578, >90d 2132, >30d 5102 —
  record only, no prune).
- **Benign carry-over lag, authored after the 11-01 follow-up push (2):**
  `references/skill-md-at-cap.md` (three new sections: practical paging — `read_file` with
  `limit=250` slices, because a single read of the ~100.9 KB file is rejected; the generic
  `patch` tool is refused in review/cron passes as non-whitelisted, so SKILL.md surgery must
  happen in the main run session; and a **known structural defect** — the Method Selection
  table is split in three with row C orphaned at ~line 99, to fix byte-neutrally with the next
  cap slim), diagnostics `references/cleanup-run-endpoints-and-counts.md` (11-01 token row +
  the 10th wording-gate shape section). The orphaned-row-C defect was confirmed in practice
  this run: paging the file showed A and B together and C below 17 lines of prose.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **273**; remote HEAD **stable at `649c1e25bba0`** (292 blobs total)
  from the preflight read through the script's Step 2 and commit time — no sibling advance,
  hence no ref-PATCH 422 race.
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- 6 blobs uploaded in one clean pass: `cron/jobs.json` `99e54b8ee5e7`, `MEMORY.md`
  `680045dc10c9`, `USER.md` `73f6836f4c07`, `ARCHIVE.md` `fd848efa86af`,
  `skill-md-at-cap.md` `08364ba2e817`, `cleanup-run-endpoints-and-counts.md` `6c67f8d2bfc7`;
  subtree `b2f8f9cd09a8a9086903c4c53a33c46a231f2e88`, top tree
  `a8e28d36473d8eb2f28666ec05cfd0f8898e6fd1`, commit + ref PATCH on the first attempt.
- No network flakiness (no port-443 timeout, no `unexpected EOF`).

## Post-push remote verification
- Remote HEAD `df4f29533df5`; total blobs **292**, `demo-pm` blobs = **273**
  (== local file count 273); by top dir: demo-pm 273, demo-dev 5, demo-tester 8,
  tester-01 5, `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row (the 11-02 account-flip
abort after two clean days) + SKILL.md `latest:` `2026-11-01` → `2026-11-02` (same-length
in-place swap; SKILL.md is still over its 100 K cap, so no new prose goes in it). Pushed with
the same standalone-subtree script; the closing preflight re-run must report
`Modified: 0, New: 0, Deleted: 0`.
