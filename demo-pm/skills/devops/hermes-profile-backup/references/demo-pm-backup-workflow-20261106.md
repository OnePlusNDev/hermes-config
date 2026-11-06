# demo-pm backup run — 2026-11-06

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `85592c49a1fe16120a72c848575c855e214fdbe2`
URL: https://github.com/OnePlusNDev/hermes-config/commit/85592c49a1fe16120a72c848575c855e214fdbe2
Diff: **7 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner, `permissions.push=true`; `GITHUB_TOKEN` / `GH_TOKEN` both
  unset) — **no switch needed**; the 11-04/11-05 keyring flip did not recur, and the account held through
  the whole run.
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
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
A  demo-pm/skills/devops/pm-triage-cron/references/assignee-query-verification.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py 9350d9a8e9cf` → exit 0,
`MODIFIED 7 / ADDED 1 / DELETED 0` (local 278 vs remote-at-PREV 277), output in `/tmp/bk-1106/char.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6483→6531,
  config-backup / memory-cleanup counters 136→137 ×2, `next_run_at` roll to 11-06/11-07,
  per-job `last_run_at`, `updated_at` 11-05T20:01:31 → 11-06T20:01:37; `memories/MEMORY.md` —
  header only, 最后更新 2026-11-04 → 2026-11-05 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-04 → 2026-11-05;
  `memories/archive/ARCHIVE.md` — new **2026-11-05 21:00-21:04 memory cleanup** row appended
  (daemon offline on first probe, `-p demo-pm daemon status` = not running, started via
  `start_hindsight_daemon.sh`, poll1/poll2 http=000 with the documented **stale-body false
  healthy** trap, poll3 http=200 healthy ~25-30 s; consolidation op `5a1383b6` +277 ms,
  counter 95→96, 48 nodes / 1228 links unchanged; reflect **188,865 / 7,446** primary,
  wording gate AFFIRMATIVE for the **15th consecutive** time on the perishability-reclassification
  shape, disambiguation **239,515 / 6,546** concluding 「无内容性过期事实」; new standing gap logged —
  bank still records the z.ai GLM key as current while MEMORY.md §3 says it 401'd on 2026-09-29 and
  the daemon moved to DeepSeek, so no superseding fact exists in the bank).
- **Benign carry-over doc lag, authored after the 11-05 follow-up push (3):**
  `hermes-profile-backup/references/index-and-table-append-recipe.md` (scoping correction:
  `$(date +%s)` does NOT expand in a `write_file` *path*, but DOES inside a `terminal()` shell
  command — `BK=/tmp/bk-$(date +%m%d)-$(date +%s)` is the tirith-safe scratch-dir idiom; plus the
  "items 2+3 in one helper script" recipe); `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md`
  (11-05 token row 188,865 / 7,446 + new「Bank-vs-flat-file drift: the LLM-key fact is a standing
  gap」section); `pm-triage-cron/SKILL.md` (one-line pointer to the new
  `assignee-query-verification.md`).
- **New file (1):** `pm-triage-cron/references/assignee-query-verification.md` — `GITHUB_`-prefixed
  token misread (404), sed-rewritten-legacy-script count contradiction (5 vs 7), PRs leaking into the
  issues endpoint, and the four-step evidence checklist before `[SILENT]`.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **278**; preflight read remote HEAD **`b72f09dbde16`** (296 blobs)
- Preflight diff: `Modified: 7, New: 1, Deleted: 0` — **no exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- A sibling **demo-dev** backup (`9350d9a8e9cf`, 2026-11-06T12:01:27Z) landed between the preflight
  read (`b72f09dbde16`) and the script's Step 2, which read `9350d9a8e9cf` / 296 blobs. Diff content
  identical (same **7 M / 1 A / 0 D**) and the commit was parented on the fresh HEAD → nothing lost,
  no 422 race. Baseline SHAs, stated plainly: preflight `b72f09db`, Step 2 `9350d9a8`.
- 8 blobs uploaded in one clean pass: `cron/jobs.json` `b4b0dcb72d3e`, `MEMORY.md` `e4d4258263e4`,
  `USER.md` `75f1e7d6d614`, `ARCHIVE.md` `73610c619f13`, `index-and-table-append-recipe.md`
  `6369443c3470`, `cleanup-run-endpoints-and-counts.md` `94056157257d`, `pm-triage-cron/SKILL.md`
  `5e8701ac35e6`, `assignee-query-verification.md` `fe2dc3468a5e`; subtree
  `ed9f3d0444dc17a16a8d5d987f1da0d6a0553a8a`, top tree `e03940303188a6e827e27c3e3479c593ca28b1dd`,
  commit + ref PATCH on the first attempt (`Remote HEAD now: 85592c49a1fe`).
- No network flakiness (no 443 timeout, no `unexpected EOF`). Follow-up cleanliness is asserted
  only by the closing-preflight `0/0/0` check below, not by the log.

## Post-push remote verification
- Remote HEAD `85592c49a1fe`; total blobs **297**, `demo-pm` blobs = **278**
  (== local file count 278); by top dir: demo-pm 278, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-05` → `2026-11-06` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
