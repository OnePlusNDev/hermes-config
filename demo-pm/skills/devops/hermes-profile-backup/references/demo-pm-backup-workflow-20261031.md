# demo-pm backup run — 2026-10-31

## Result
**Method B (standalone subtree, no clone)** — **first try, 0 aborts** (no account flip, no ref-PATCH 422 race).
Main commit: `6f1fca687f406494b16f15ffa6a02bc1b2c89d2f`
URL: https://github.com/OnePlusNDev/hermes-config/commit/6f1fca687f406494b16f15ffa6a02bc1b2c89d2f
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` -> **`OnePlusNDev`** with `permissions.push=true` — no `gh auth switch`
  needed (`GITHUB_TOKEN` unset). The pre-flight read also confirmed the target repo
  is the one actually carrying `demo-pm/` (root: `.gitignore`, `demo-dev`, `demo-pm`,
  `demo-tester`, `tester-01`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` -> **0** matches;
  `api_key: '<non-empty>'` -> **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  -> **no plaintext key found, no `key_env` replacement needed**
- `.env` / `auth.json` / `auth.lock` / `state.db*` present locally but excluded; remote
  tree stays clean (verified post-push).

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `characterize-diff-vs-prev-head.py --commit=6f1fca687f40...` (full SHA
required — a 12-char short SHA returns HTTP 404 from `/git/commits/{sha}`; derived PRE_PUSH
`a95e1c4dccf7`, one run, exit 0, output sliced from `/tmp/bk-1031/char.txt`); it reported
**MODIFIED 7 / ADDED 0 / DELETED 0**, matching preflight exactly (local 271 vs
remote-at-prev 271).

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6195->6243,
  config-backup and memory-cleanup counters 130->131, `next_run_at` 10-30->10-31 /
  10-31->11-01 / 10-30->10-31, `last_run_at` per job, `updated_at`
  2026-10-30T20:01:12 -> 2026-10-31T20:01:04; `memories/MEMORY.md` — header 最后更新
  2026-10-29 -> 2026-10-30 with a 30-day **re-check** (not a new archive: body byte-identical,
  no expired facts, reuses `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — same
  30-day re-check shape (header 2026-10-11 -> 2026-10-30, reuses
  `archive/USER-20261011.snapshot.md`, next window 2026-11-10); `memories/archive/ARCHIVE.md` —
  new 2026-10-30 row (daemon started from a stale-`:8888`-only state, healthy on the 2nd 10 s
  poll; consolidation op `ea9514ae` +388 ms, completed 89->90; **first reflect crashed**
  `Starting agentic reflect` -> `LinkExpansion` -> `ServerDisconnectedError` (daemon process
  gone), retry after launcher restart succeeded on the identical request; reflect
  216,498/9,363, wording gate fired on the date-conditional shape a **6th time / 10th
  consecutive**; disambig 244,920/7,093 -> "no content-level expired facts"; 16 facts checked,
  all within a 3-day span; `mentioned_at`-as-expiry named as the root cause).
- **Benign carry-over lag, authored after the 10-30 follow-up push (3):**
  `references/method-b-practice-notes.md` (the 2026-10-30 "tightest window yet" re-confirmation
  — 4 flips in 6 days, budget the abort rather than trying to prevent the flip),
  `references/run-note-diff-characterization.md` (MEMORY vs USER snapshot rollover guidance,
  in-skill `A` shape, and the local == remote-at-PREV + `New` arithmetic identity),
  diagnostics `references/cleanup-run-endpoints-and-counts.md` (10-30 token row + stale temp
  health-JSON caution + the transient first-reflect crash/retry note).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **271**; remote HEAD `a95e1c4dccf7a07a3f877359ec530b067a6f78ce`, 290 blobs
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Remote HEAD was stable at `a95e1c4dccf7` from preflight through commit time → **no
  ref-PATCH 422 race**, no sibling advance observed this run.

## Execution notes
- **Zero aborts.** No keyring flip this run: the `gh api user` check at pre-flight and the
  script's own Step 2/Step 4 all ran against `OnePlusNDev` with `push=true`. (Per the
  practice notes the flip is bursty, so this says nothing about tomorrow.)
- 7 blobs uploaded in one pass: `cron/jobs.json` `36794ca3a0f9`, `MEMORY.md` `8021b34126c4`,
  `USER.md` `e48ca3190b1d`, `ARCHIVE.md` `1feb2ffbf67e`, `method-b-practice-notes.md`
  `f62eb1d51243`, `run-note-diff-characterization.md` `5851df9a7744`,
  `cleanup-run-endpoints-and-counts.md` `35bec391fd51`; subtree
  `11d01b90ff7c832a427ba1ee0ea70628d40a6825`, top tree
  `dec76fc40717c34f64f7e6e1795cebe67d0b8258`, commit + ref PATCH on the first attempt.
- No network flakiness (no port-443 timeout, no `unexpected EOF`).

## Post-push remote verification
- Remote HEAD `6f1fca687f40`; total blobs **290**, `demo-pm` blobs = **271**
  (== local file count 271); by top dir: demo-pm 271, demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row (today's clean first-try
run) + SKILL.md `latest:` `2026-10-30` -> `2026-10-31` (same-length in-place swap; SKILL.md is
still over its 100 K cap, so no new prose goes in it). Pushed with the same standalone-subtree
script; the closing preflight re-run must report `Modified: 0, New: 0, Deleted: 0`.
