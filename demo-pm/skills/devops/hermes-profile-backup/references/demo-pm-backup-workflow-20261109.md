# demo-pm backup run — 2026-11-09

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `d1fdc0098ff0c361cda9f5f05ee5b2eac8814787`
URL: https://github.com/OnePlusNDev/hermes-config/commit/d1fdc0098ff0c361cda9f5f05ee5b2eac8814787
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** with `permissions.push=false` → **switch REQUIRED**:
  `gh auth switch --user OnePlusNDev` → `gh api user` = `OnePlusNDev`, `permissions.push=true`.
  This breaks the 11-06/11-07/11-08 three-day clean streak and is the 5th observed flip
  (10-25 ×2, 10-27, 10-29, 10-30, 11-04, 11-05 patterns — the keyring race is still live).
  The switch **held** through the whole run (no mid-run re-flip, no blob 404).
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; `auth.json` (164 B),
  `auth.lock` (0 B), `state.db` (2.25 GB) present locally and excluded — none in the remote tree.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695) → **no plaintext key found, no `key_env`
  replacement needed**.

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py 33fec41e9fc6` → exit 0,
`MODIFIED 6 / ADDED 0 / DELETED 0` (local 282 vs remote-at-PREV 282), output in
`/tmp/char_20261109.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6627→6675,
  config-backup / memory-cleanup counters 139→140 ×2, `next_run_at` roll to 11-09/11-10,
  per-job `last_run_at` (task-polling 11-09T20:01:05, memory-cleanup 11-08T20:04:56,
  memory-archive 11-08T21:05:20), `updated_at` 11-09T20:01:05; `memories/MEMORY.md` — header
  only, 最后更新 2026-11-07 → 2026-11-08 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-07 →
  2026-11-08 (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md`
  — new **2026-11-08 21:00-21:05 memory cleanup** row (daemon offline at first probe, started via
  `scripts/start_hindsight_daemon.sh`, poll 1 `http_code=000` stale-body trap then healthy on poll 2
  in ~10-20 s warm pg0; consolidation op `5b6f7972-8df5-4c60-b614-f73faef48b2b` +506 ms,
  `deduplicated=false`, counter 98→99; both reflect calls first-try, no crash;
  primary **174,375 / 6,448** — wording gate AFFIRMATIVE for the **18th consecutive** time on the
  heading-negation + date-conditional pair; disambiguation **264,557 / 6,002** concluding
  「无内容性过期事实」; bank↔flat-file LLM-key drift now five consecutive days — logged, no data
  mutated).
- **Benign carry-over doc lag, authored after the 11-08 follow-up push (2):**
  `hermes-profile-backup/references/run-note-diff-characterization.md` (new reconciliation section:
  if the probe already ran with the preflight SHA, do NOT re-run it for a sibling-advanced Step-2
  HEAD — disclose both SHAs in one line instead; sibling backups touch no `demo-pm/` blob);
  `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (11-08 token row
  174,375 / 6,448 + disambig 264,557 / 6,002, the 18th-shape section, drift-gap line extended to
  five days, plus the `hindsight -p demo-pm` named-profile form working directly).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **282**; preflight read remote HEAD **`33fec41e9fc6`** (301 blobs).
  Local 282 == remote `demo-pm` 282: the extra file vs the 11-08 main push (281) is that day's own
  run note, added by the follow-up commit — not a new file today.
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- An ad-hoc `gh api .../git/refs/heads/main` read at the very start returned `5e1f4d75022c`; the
  preflight (a minute later) read **`33fec41e9fc6`** — a sibling backup commit landed in between,
  before any of our own reads. Preflight and the script's Step 2 then both read `33fec41e9fc6`
  (301 blobs), so there was **no preflight→Step-2 divergence** and no ref-PATCH 422 race.
- 6 blobs uploaded in one clean pass: `cron/jobs.json` `a4095ec015fa`, `MEMORY.md` `7ecc74777250`,
  `USER.md` `b223aa606f27`, `ARCHIVE.md` `13d184b0eca5`, `run-note-diff-characterization.md`
  `d0783aa7e52f`, `cleanup-run-endpoints-and-counts.md` `099fe47c45d7`; subtree
  `44c66e18fdb352dc06ee3aa6b97d7efb46c8a34e`, top tree `5ebd7790ca0f08b3d09e241cc3c6b6177adbed5a`,
  commit + ref PATCH on the first attempt (`Remote HEAD now: d1fdc0098ff0`).
- No network flakiness in the main push (no 443 timeout, no `unexpected EOF`). Follow-up
  cleanliness is asserted only by the closing-preflight `0/0/0` check, not by the log.

## Post-push remote verification
- Remote HEAD `d1fdc0098ff0`; total blobs **301**, `demo-pm` blobs = **282**
  (== local file count 282); by top dir: demo-pm 282, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-08` → `2026-11-09` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
