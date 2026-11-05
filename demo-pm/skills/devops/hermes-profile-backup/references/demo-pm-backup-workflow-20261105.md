# demo-pm backup run — 2026-11-05

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `4c86521c7d7a19de85211f6bc8884e49795b77ef`
URL: https://github.com/OnePlusNDev/hermes-config/commit/4c86521c7d7a19de85211f6bc8884e49795b77ef
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (not owner, repo `permissions.push=false`) — **switched** with
  `gh auth switch --user OnePlusNDev` (`GITHUB_TOKEN` / `GH_TOKEN` both unset first); re-check
  returned `OnePlusNDev` with `push=true`, and the account held through the whole run.
  Second consecutive day of the keyring flip (11-04 same shape).
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695) → **no plaintext key found, no replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/index-and-table-append-recipe.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py 9623ded95915` → exit 0,
`MODIFIED 7 / ADDED 0 / DELETED 0` (local 276 vs remote-at-PREV 276), sliced from `/tmp/bk-1105-*/char.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6435→6483,
  config-backup and memory-cleanup counters 135→136 ×2, `next_run_at` 11-04→11-05,
  per-job `last_run_at`, `updated_at` roll-over; `memories/MEMORY.md` — header only,
  最后更新 2026-11-03 → 2026-11-04 (body byte-identical, reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-03 → 2026-11-04
  (reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` — new 2026-11-04
  memory-cleanup row (launcher start → `/health` 200 on **poll 1** ~10 s warm pg0, fastest yet;
  consolidation `67d0219d` completed +30 ms, counter 94→95; primary reflect 169,983 / 9,021,
  wording gate fired on the perishability-reclassification shape; disambiguation 316,341 / 10,375
  → 「无内容性过期事实」, `based_on` full-bank; 48 nodes / 1228 links / 18 observations / 0 pending).
- **Benign carry-over doc lag, authored after the 11-04 follow-up push (3):**
  `hermes-profile-backup/references/index-and-table-append-recipe.md` (new ⚠️ note: `write_file`
  does NOT expand `$(date +%s)` in a path — use a literal suffix); `hermes-profile-diagnostics/SKILL.md`
  (two rows corrected: Python `hindsight_client` DOES accept `include_facts=True`, the 422 caveat is
  raw-HTTP only; `hindsight -p demo-pm` named-profile route); and
  `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (cron-safe
  `write_file`→venv-python helper pattern, 11-04 token row, perishability note, `-p` CLI forms).
  All three were written by the **11-04 21:01–21:03 memory-cleanup cron**, i.e. after yesterday's
  follow-up push — ordering, not a lost commit.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **276**; preflight read remote HEAD **`9623ded95915`** (295 blobs)
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- A sibling **demo-dev** backup (`6b4cb804764a`, 2026-11-05T12:01:29Z) landed between the preflight
  read (`9623ded95915`) and the script's Step 2, which read `6b4cb804764a` / 295 blobs. Diff content
  unchanged (**same 7 M / 0 A / 0 D**) and the commit was parented on the fresh HEAD → nothing lost,
  no 422 race. Baseline SHAs, stated plainly: preflight `9623ded9`, Step 2 `6b4cb804`.
- 7 blobs uploaded in one clean pass: `cron/jobs.json` `423e64027cd0`, `MEMORY.md` `b5793b176302`,
  `USER.md` `339c66ed51ed`, `ARCHIVE.md` `651867c7ade2`, `index-and-table-append-recipe.md`
  `b9d7563129f9`, diagnostics `SKILL.md` `312ec144d572`, `cleanup-run-endpoints-and-counts.md`
  `519e278b587c`; subtree `9ad565f65a40`, top tree `8ae009f41b57`, commit + ref PATCH on the
  first attempt (`Remote HEAD now: 4c86521c7d7a`).
- No network flakiness (no 443 timeout, no `unexpected EOF`). Follow-up cleanliness is asserted
  only by the closing-preflight `0/0/0` check below, not by the log.

## Post-push remote verification
- Remote HEAD `4c86521c7d7a`; total blobs **295**, `demo-pm` blobs = **276**
  (== local file count 276); by top dir: demo-pm 276, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-04` → `2026-11-05` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
