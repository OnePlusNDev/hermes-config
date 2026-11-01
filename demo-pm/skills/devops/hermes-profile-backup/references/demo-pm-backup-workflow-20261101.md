# demo-pm backup run — 2026-11-01

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts** (no account flip, no ref-PATCH 422 race).
Main commit: `17af9764fd2b6b4750c7c9d7f532c0c4d186d165`
URL: https://github.com/OnePlusNDev/hermes-config/commit/17af9764fd2b6b4750c7c9d7f532c0c4d186d165
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** with `permissions.push=true` — no `gh auth switch`
  needed (`GITHUB_TOKEN` unset). Repo root confirms the target carries `demo-pm/`:
  `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never
  uploaded; no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `characterize-diff-vs-prev-head.py --commit=17af9764fd2b6b4750c7c9d7f532c0c4d186d165`
(full 40-char SHA — the 12-char form 404s), derived PRE_PUSH `a1249babdc76`, one run,
exit 0, output sliced from `/tmp/bk-1101/char.txt`; it reported
**MODIFIED 6 / ADDED 0 / DELETED 0**, matching preflight exactly (local 272 vs
remote-at-PREV 272).

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6243→6291,
  config-backup and memory-cleanup counters 131→132, `next_run_at` 10-31→11-01 /
  11-01→11-02 / 10-31→11-01, `last_run_at` per job, `updated_at` roll-over;
  `memories/MEMORY.md` — header 最后更新 2026-10-30 → 2026-10-31 with a 30-day
  **re-check** (body byte-identical, no expired facts, reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — same re-check shape
  (header 2026-10-30 → 2026-10-31, reuses `archive/USER-20261011.snapshot.md`);
  `memories/archive/ARCHIVE.md` — new 2026-10-31 row (`:9178` offline at first probe,
  `lsof` showed only the global `:8888` daemon → started via
  `scripts/start_hindsight_daemon.sh`, healthy on the 2nd 10 s poll, ~10-20 s;
  consolidation op `0ec170de` +272 ms, completed 90→91; **no reflect crash — both
  calls succeeded on the first try**, first clean single-session run in days;
  reflect 151,379/5,516; wording gate fired on the date-condition/age-basis shape a
  **7th time / 11th consecutive**; disambig 266,832/7,350 → "no content-level expired
  facts", per-category table over AppID/chat_id/OpenID, ports 9177-9180, z.ai key and
  endpoint; 48 nodes / 1228 links / 18 observations / 0 pending; sessions 6528,
  >90d 2082, >30d 5082 — record only, no prune).
- **Benign carry-over lag, authored after the 10-31 follow-up push (2):**
  `references/run-note-diff-characterization.md` (the "pass the FULL 40-char SHA — a
  short SHA 404s and the 404 looks exactly like an account flip" section),
  diagnostics `references/cleanup-run-endpoints-and-counts.md` (10-31 token row +
  flat-file 30-day re-check header-wording pitfall + the 9th wording-gate shape).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local
one (16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **272**; first preflight read remote HEAD
  `33cb4f3c75ef` (291 blobs), then the script's Step 2 read **`a1249babdc76`** — a
  sibling profile landed in between. Both reads showed the **same 6 M / 0 A / 0 D**,
  and the script parented on the fresh HEAD → no lost work, no 422.
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- **Zero aborts.** The `gh api user` check at pre-flight and the script's own Step 2/4
  all ran against `OnePlusNDev` with `push=true`; the 10-29/10-30 keyring flip did not
  recur for a second day.
- 6 blobs uploaded in one pass: `cron/jobs.json` `7125d68ee877`, `MEMORY.md`
  `71ed9e20f221`, `USER.md` `feaa72d7b0dc`, `ARCHIVE.md` `c07c50f84b19`,
  `run-note-diff-characterization.md` `aca78354a8c6`,
  `cleanup-run-endpoints-and-counts.md` `a2f8874beac8`; subtree
  `b1121c4e13f19393684a9f92397d37abaa728074`, top tree
  `29bfe28e0958066b790ac1275b1e7b481912c416`, commit + ref PATCH on the first attempt.
- No network flakiness (no port-443 timeout, no `unexpected EOF`).

## Post-push remote verification
- Remote HEAD `17af9764fd2b`; total blobs **291**, `demo-pm` blobs = **272**
  (== local file count 272); by top dir: demo-pm 272, demo-dev 5, demo-tester 8,
  tester-01 5, `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row (today's clean
first-try run) + SKILL.md `latest:` `2026-10-31` → `2026-11-01` (same-length in-place
swap; SKILL.md is still over its 100 K cap, so no new prose goes in it). Pushed with
the same standalone-subtree script; the closing preflight re-run must report
`Modified: 0, New: 0, Deleted: 0`.
