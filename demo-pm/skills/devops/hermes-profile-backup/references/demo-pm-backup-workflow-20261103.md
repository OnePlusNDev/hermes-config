# demo-pm backup run — 2026-11-03

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no account flip, no 422 race)**.
Main commit: `8d8f2898649f3ff51a5932ce4fd38eed434b3c8f`
URL: https://github.com/OnePlusNDev/hermes-config/commit/8d8f2898649f3ff51a5932ce4fd38eed434b3c8f
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner) — no switch needed; the 10-29/10-30 keyring flip
  stayed away for a third consecutive day.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `characterize-diff-vs-prev-head.py --commit=8d8f2898649f3ff51a5932ce4fd38eed434b3c8f`
(full 40-char SHA), derived PRE_PUSH `cbf50d45831a`, one run, exit 0, output sliced from
`/tmp/bk-1103/char.txt`; it reported **MODIFIED 7 / ADDED 0 / DELETED 0** (local 274 vs
remote-at-PREV 274).

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6339→6387,
  config-backup and memory-cleanup counters 133→134 ×2, `next_run_at` 11-02→11-03 /
  11-03→11-04, per-job `last_run_at`, `updated_at` roll-over;
  `memories/MEMORY.md` — header 最后更新 2026-11-01 → 2026-11-02 with the 30-day **re-check**
  (body byte-identical, no expired facts, reuses `archive/MEMORY-20261029.snapshot.md`);
  `memories/USER.md` — same re-check shape (header 2026-11-01 → 2026-11-02, reuses
  `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` — new 2026-11-02 row
  (`:9178` offline at first probe, only the global `:8888` daemon listening → launcher start,
  poll1/poll2 `http_code=000` then healthy on the 3rd 10 s poll (~20-30 s; stale
  `/tmp/h9178_p*.json` bodies from a previous run are a known trap — trust the code, not the
  body; the `:8888` bank list holds no `demo-pm-memory`, so no sibling bypass);
  consolidation op `29902e48` +190 ms, completed 92→93; **no reflect crash, both calls
  first-try**; reflect 174,494/6,225; disambig 357,543/4,775 → 「无内容性过期事实」; wording
  gate fired on an **11th shape — 「未发现（有前提）」 conditional** (opened 「没有发现超过 30
  天的过期事实」 then added an if-today-is-past-2026-06-17 clause + a perishable-config list),
  **13th consecutive**; 48 nodes / 1228 links / 18 observations / 0 pending; sessions 6578,
  >90d 2132, >30d 5102 — record only, no prune).
- **Benign carry-over lag, authored after the 11-02 follow-up push (3):**
  `references/method-b-practice-notes.md` (rewrote the 11-02 row to point at the
  "budget the abort" rule instead of a third pre-flight read, plus a new ⚠️ section: NEVER
  pass `--help` to `gh-api-standalone-subtree-backup.py` — no arg parser, it immediately runs
  a real backup — and a note that only `preflight-backup-scan.py` /
  `characterize-diff-vs-prev-head.py` are safe read-only probes), diagnostics `SKILL.md`
  (wording-gate shape count "eight so far" → "eleven so far"), diagnostics
  `references/cleanup-run-endpoints-and-counts.md` (11-02 token row 174,494/6,225 + disambig
  357,543/4,775 + the 11th-shape section and the stale-temp-health-JSON caution).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **274**; remote HEAD **stable at `cbf50d45831a`** (293 blobs
  total) from the preflight read through the script's Step 2 and commit time — no sibling
  advance, hence no ref-PATCH 422 race.
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- 7 blobs uploaded in one clean pass: `cron/jobs.json` `4a7f1b9aa81e`, `MEMORY.md`
  `18f6ea2c32ad`, `USER.md` `457d0fbacd91`, `ARCHIVE.md` `e4879325a31c`,
  `method-b-practice-notes.md` `c291956c0c86`, diagnostics `SKILL.md` `d017161c264c`,
  `cleanup-run-endpoints-and-counts.md` `66dc62da52f2`; subtree
  `efec8c5fe385c726d97bc97e80356debacd7dc25`, top tree
  `69974658aa70b7169c8c48710682e067fa35c2cc`, commit + ref PATCH on the first attempt.
- No network flakiness (no port-443 timeout, no `unexpected EOF`).

## Post-push remote verification
- Remote HEAD `8d8f2898649f`; total blobs **293**, `demo-pm` blobs = **274**
  (== local file count 274); by top dir: demo-pm 274, demo-dev 5, demo-tester 8,
  tester-01 5, `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row (the 11-03 first-try
run, third clean day after the flip) + SKILL.md `latest:` `2026-11-02` → `2026-11-03`
(same-length in-place swap; SKILL.md is still over its 100 K cap, so no new prose goes in it).
Pushed with the same standalone-subtree script; the closing preflight re-run must report
`Modified: 0, New: 0, Deleted: 0`.

**Follow-up hit the ref-PATCH 422 race (first occurrence since 2026-11-01).** Attempt 1 built
commit `6606dc9d2c85` on parent `8d8f2898649f`, but a sibling **demo-dev** backup
(`96c48574a7af`, 12:03:54Z) advanced `main` in the window between Step 6 and Step 7, so the ref
PATCH was rejected (the script stops at `=== Step 7: updating ref ===` with no `Remote HEAD now`
/ `Done:` line — a silent non-fast-forward, easily misread as a hang). Nothing was lost: the
blob SHAs are idempotent, so the one plain re-run rebuilt the same 4-file tree on the fresh
HEAD `96c48574a7af`. Note the asymmetry with the main commit: `main` really was race-free
(HEAD stable `cbf50d45831a` from preflight through Step 7), so this is the documented
late-window race, not a baseline misread.
