# demo-pm backup run — 2026-11-07

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `6f89f7a4de8237d8839800420e2900bdb1622448`
URL: https://github.com/OnePlusNDev/hermes-config/commit/6f89f7a4de8237d8839800420e2900bdb1622448
Diff: **7 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner, `permissions.push=true`; `GITHUB_TOKEN` / `GH_TOKEN`
  both unset) — **no switch needed**, and the account held through the whole run (second
  consecutive clean day after the 11-04/11-05 flip pair).
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695) → **no plaintext key found, no replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (7 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/index-and-table-append-recipe.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
A  demo-pm/skills/devops/hermes-profile-diagnostics/scripts/mem_cleanup_client.py
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py 0b405bb1c412` → exit 0,
`MODIFIED 7 / ADDED 1 / DELETED 0` (local 280 vs remote-at-PREV 279), output in `<scratch>/char.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6531→6579,
  config-backup / memory-cleanup counters 137→138 ×2, `next_run_at` roll to 11-07/11-08,
  per-job `last_run_at` (task-polling 11-07T20:00:48, memory-cleanup 11-06T20:05:44), `updated_at`;
  `memories/MEMORY.md` — header only, 最后更新 2026-11-05 → 2026-11-06 (body byte-identical, still
  reuses `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-05 →
  2026-11-06 (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md`
  — new **2026-11-06 21:00-21:05 memory cleanup** row appended (daemon offline on first probe, started
  via `start_hindsight_daemon.sh`, poll1 http=000 / **poll2 http=200 healthy in ~10-20 s** warm pg0;
  consolidation op `766c1f28-c2de-483a-ae03-126d4fb2ddc4` **+22 ms — fastest recorded**, counter
  96→97, 48 nodes / 1228 links unchanged; primary **176,961 / 7,246**, wording gate AFFIRMATIVE for
  the **16th consecutive** time on the 「字面上无，但需按当前日期复核」 date-conditional shape,
  disambiguation **309,656 / 7,796** concluding 「无内容性过期事实」; bank↔flat-file LLM-key drift
  now three consecutive days, still a missing-fact gap — logged, no data mutated).
- **Benign carry-over doc lag, authored after the 11-06 follow-up push (3):**
  `hermes-profile-backup/references/index-and-table-append-recipe.md` (new ⚠️ "the `next line starts
  with |` structural check only applies MID-TABLE" section + items 2+3+4 in one helper script);
  `hermes-profile-diagnostics/SKILL.md` (pointer row to the new `scripts/mem_cleanup_client.py`);
  `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (11-06 token row
  176,961 / 7,246 + disambig 309,656 / 7,796 and the new "twelfth shape" section + the drift-gap
  line extended to three days).
- **New file (1):** `hermes-profile-diagnostics/scripts/mem_cleanup_client.py` (3,438 B) — cron-safe
  Hindsight daemon client (`banks` / `stats` / `consolidate` / `op <id>` / `wait-op <id>`, urllib
  only, `--url` + `--bank` flags); content-inspected: **no `.env` read, no token reference**, so it
  is a documented helper, not a diagnostic artifact.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **280**; preflight read remote HEAD **`0b405bb1c412`** (298 blobs)
- Preflight diff: `Modified: 7, New: 1, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Preflight HEAD `0b405bb1c412` and the script's Step 2 read **`0b405bb1c412` / 298 blobs** — no
  sibling backup landed in between this run; no concurrent-advance rebase needed.
- 8 blobs uploaded in one clean pass: `cron/jobs.json` `e39e58fdbf40`, `MEMORY.md` `8c527b6ba9ef`,
  `USER.md` `8c5a06ba4afb`, `ARCHIVE.md` `3a232056b23e`, `index-and-table-append-recipe.md`
  `139e6ce1d631`, `diagnostics/SKILL.md` `2a0ece667ff9`, `cleanup-run-endpoints-and-counts.md`
  `0b81ed8f374b`, `mem_cleanup_client.py` `f16dfa465012`; subtree
  `32221fad0028de9c31ec5d2c380a56a9df88d971`, top tree `1a0d637210f805016bbdf5877bbfd75ce64a0f9b`,
  commit + ref PATCH on the first attempt (`Remote HEAD now: 6f89f7a4de82`).
- No network flakiness observed in the main push (no 443 timeout, no `unexpected EOF`). Follow-up
  cleanliness is asserted only by the closing-preflight `0/0/0` check below, not by the log.

## Post-push remote verification
- Remote HEAD `6f89f7a4de82`; total blobs **299**, `demo-pm` blobs = **280**
  (== local file count 280); by top dir: demo-pm 280, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-06` → `2026-11-07` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
